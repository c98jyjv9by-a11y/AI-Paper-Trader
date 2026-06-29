"""Positions + queued-orders report across the broker accounts, each ticker ENRICHED with the same
per-ticker analytics added to `intraday-check`: composite score + cross-sectional rank, trailing
1/5/20/60d AVG composite score, a trend type, and trailing 1/5/20/60d price return.

For every account it shows: a CURRENT POSITIONS table and the QUEUED ORDERS the live reconcile would
send right now (dry-run, latest prices) with each order's clarified reason. The open-positions table
carries the stats TWICE — once **@Entry** (the same trailing scores/returns + trend tag as they stood
on the session the position was opened, reconstructed via `_build_enrichment(as_of=entry_date)`) and
once **Now** — so you can see how each name's momentum picture has shifted since you bought it. The
entry session is reconstructed from each account's fill history (start of the current holding streak).
Renders reports/positions_report_<date>.pdf.

    python run.py positions-report [--accounts a b c] [--end YYYY-MM-DD] [--out FILE]
"""
import sys
import warnings
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["text.parse_math"] = False   # '$' is currency here, not a mathtext toggle (two $ on
                                                  # one line — e.g. the equity/cash subtitle — else vanish)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

sys.path.insert(0, str(Path(__file__).resolve().parent))
warnings.filterwarnings("ignore")

from broker_adapter import AlpacaPaper
import broker_sync as bs
from intraday_check import _build_enrichment, _WINDOWS, _pct, _sc

ROOT = Path(__file__).resolve().parent.parent
GREEN, RED, GREY, HEAD = "#1a7f37", "#c0392b", "#888", "#34495e"
ENTRY_HEAD = "#6b5b95"          # @Entry header band — a muted purple, distinct from the slate "Now" band
DEFAULT_ACCOUNTS = ["topten", "copymodel", "rampup", "monthly10", "weekly10", "combo20",
                    "zscore10d_biweekly", "zscore5d_weekly", "zscore1d_daily"]


def _money(x):
    if x is None:
        return "—"
    return ("-$%s" % f"{abs(x):,.0f}") if x < 0 else ("$%s" % f"{x:,.0f}")


def _entry_dates(cli, held_syms):
    """{symbol: 'YYYY-MM-DD'} entry session for each currently-held name = the date the CURRENT continuous
    holding streak OPENED. Walks the account's FILLED orders oldest-first tracking running signed qty; each
    time a name crosses from flat (≈0) to non-zero it stamps a fresh entry date, and a return to flat clears
    it — so a name sold out and re-bought reports the LATEST open, not the original. None if no fill covers it
    (e.g. seeded position with no recorded fill)."""
    from collections import defaultdict
    try:
        fills = [o for o in (cli.orders(status="all", limit=500) or [])
                 if o.get("status") == "filled" and o.get("filled_at")]
    except Exception:
        return {s: None for s in held_syms}
    fills.sort(key=lambda o: o["filled_at"])
    run, start = defaultdict(float), {}
    for o in fills:
        s = o.get("symbol")
        q = float(o.get("filled_qty") or 0) * (1 if o.get("side") == "buy" else -1)
        if abs(run[s]) < 1e-9 and q != 0:                  # flat -> open: a new holding streak begins
            start[s] = o["filled_at"][:10]
        run[s] += q
        if abs(run[s]) < 1e-9:                             # back to flat: streak closed
            start.pop(s, None)
    return {s: start.get(s) for s in held_syms}


def _pct0(x):
    """Compact whole-percent (the four-window return quad is too wide at 2 decimals — it overran the
    neighbouring column in the dense positions table)."""
    return "—" if x is None else f"{x * 100:+.0f}%"


def _avg_quad(e):
    return "/".join(_sc(e["avg"][w]) for w in _WINDOWS)


def _ret_quad(e):
    return "/".join(_pct0(e["ret"][w]) for w in _WINDOWS)


def _entry_stat_cells(e):
    """The 4 @Entry analytics cells (score, trend, avg 1/5/20/60, ret 1/5/20/60) — no rank (a past
    cross-sectional rank is less useful than the trajectory it sat in). '—' when unavailable."""
    if not e:
        return ["—", "—", "—", "—"]
    return [_sc(e.get("score")), e.get("trend", "—"), _avg_quad(e), _ret_quad(e)]


def _cadence(name):
    """(human cadence label, is-this-a-rebalance-day-now). model_v4/ramp-up + daily books trade every
    session; the calendar-gated books only rebalance on their own first-of-period day."""
    tm = (bs.load_manifest(name) or {}).get("target_mode") or {}
    if tm.get("kind") in ("model_v4", "score_gate_rampup"):
        return ("every session", True)
    freq = (tm.get("rebalance") or "daily").lower()
    if freq == "daily":
        return ("daily", True)
    return (freq, bs._is_rebalance_day(freq, bs._recent_trading_days()))


def _forced_preview(name, cli):
    """The plan the book WOULD send at its next rebalance, computed off the latest data (forces the
    calendar gate open via BROKER_REBALANCE_FORCE_TODAY). Read-only; restores the env afterward."""
    import os
    prev = os.environ.get("BROKER_REBALANCE_FORCE_TODAY")
    os.environ["BROKER_REBALANCE_FORCE_TODAY"] = "1"
    try:
        return bs.submit_session(name, cli=cli, submit=False, extended=True, log=False)
    finally:
        if prev is None:
            os.environ.pop("BROKER_REBALANCE_FORCE_TODAY", None)
        else:
            os.environ["BROKER_REBALANCE_FORCE_TODAY"] = prev


def _collect(name):
    """Live positions + the queued reconcile plan. On a rebalance day that's the real gated plan; off a
    rebalance day it's the LIKELY-NEXT plan (forced rebalance off latest data), flagged preview=True."""
    try:
        cli = AlpacaPaper(account=name)
        acct = cli.account()
        pos = cli.positions() or []
        cadence, due = _cadence(name)
        entry = _entry_dates(cli, [p["ticker"] for p in pos])    # entry session per held name (from fills)
        res = (bs.submit_session(name, cli=cli, submit=False, extended=True, log=False) if due
               else _forced_preview(name, cli))                  # read-only previews (no audit-log writes)
        return {"name": name, "eq": float(acct.get("equity") or 0.0),
                "cash": float(acct.get("cash") or 0.0), "pos": pos, "cadence": cadence, "preview": not due,
                "entry": entry,
                "orders": res.get("orders", []), "suppressed": res.get("suppressed", []), "err": None}
    except Exception as exc:
        return {"name": name, "err": str(exc)[:90]}


def _stat_cells(e):
    """The 5 shared analytics cells (score, rank, trend, avg 1/5/20/60, ret 1/5/20/60) for a ticker."""
    if not e:
        return ["—", "—", "—", "—", "—"]
    rank = f"#{e['rank']}/{e['n_uni']}" if e.get("rank") else "—"
    return [_sc(e.get("score")), rank, e.get("trend", "—"), _avg_quad(e), _ret_quad(e)]


def _draw_table(ax, cols, cells, colw, color_rules, fontsize=7.0, head_tints=None):
    """Banded table filling `ax`; color_rules = list of (row_idx0based_in_cells, col_idx, color).
    `head_tints` = optional {col_idx: facecolor} to band a header-column group a custom colour."""
    head_tints = head_tints or {}
    ax.axis("off")
    if not cells:
        ax.text(0.0, 0.95, "— none —", fontsize=8, color=GREY, va="top")
        return
    t = ax.table(cellText=cells, colLabels=cols, colWidths=colw, loc="upper center",
                 cellLoc="center", bbox=[0, 0, 1, 1])
    t.auto_set_font_size(False)
    t.set_fontsize(fontsize)
    for j in range(len(cols)):
        c = t[0, j]; c.set_facecolor(head_tints.get(j, HEAD))
        c.set_text_props(color="white", weight="bold"); c.set_fontsize(fontsize - 0.2)
    for i in range(len(cells)):                         # zebra banding
        if i % 2:
            for j in range(len(cols)):
                t[i + 1, j].set_facecolor("#f2f4f6")
    for (i, j, color) in color_rules:
        t[i + 1, j].set_text_props(color=color, weight="bold")


def _account_page(pdf, d, enrich, entry_enrich, today):
    name = d["name"]
    fig = plt.figure(figsize=(11, 8.5))
    if d.get("err"):
        fig.suptitle("%s — broker error" % name, fontsize=13, weight="bold")
        fig.text(0.5, 0.5, d["err"], ha="center", color=RED, fontsize=10)
        pdf.savefig(fig); plt.close(fig); return

    fig.suptitle("%s   —   positions & %s   (%s)"
                 % (name, "likely-next orders" if d.get("preview") else "queued orders", today),
                 fontsize=13, weight="bold")
    fig.text(0.5, 0.945, "equity %s · cash %s · %d position(s) · cadence: %s%s · %d order(s)%s"
             % (_money(d["eq"]), _money(d["cash"]), len(d["pos"]), d.get("cadence", "—"),
                ("  (NOT due today — showing likely next)" if d.get("preview") else "  (rebalances today)"),
                len(d["orders"]),
                ("" if not d["suppressed"] else " · %d trim(s) suppressed" % len(d["suppressed"]))),
             ha="center", fontsize=9, color="#333")

    # ── current positions — stats shown @ENTRY (purple band) and NOW (slate band) ─────────────
    fig.text(0.04, 0.905, "CURRENT POSITIONS   —   trailing scores/returns + trend tag @ entry vs now",
             fontsize=10, weight="bold")
    pcols = ["Ticker", "Qty", "Entry$", "Last$", "Mkt Val", "Unreal P&L", "Entry\nDate",
             "@Ent\nScore", "@Ent\nTrend", "@Ent Avg\n1/5/20/60d", "@Ent Ret\n1/5/20/60d",
             "Now\nScore", "Now\nRank", "Now\nTrend", "Now Avg\n1/5/20/60d", "Now Ret\n1/5/20/60d"]
    praw = [6, 3, 6, 6, 7, 10, 5, 5, 7, 14, 16, 5, 6, 7, 14, 16]
    pcolw = [w / sum(praw) for w in praw]
    ptint = {j: ENTRY_HEAD for j in (6, 7, 8, 9, 10)}  # Entry-Date + the 4 @Entry stat columns
    pcells, prules = [], []
    for i, p in enumerate(sorted(d["pos"], key=lambda x: -x.get("market_value", 0))):
        sym = p["ticker"]
        upl = p["market_value"] - p["qty"] * p["avg_entry"]
        plpc = p.get("unrealized_plpc", 0.0)
        ed = (d.get("entry") or {}).get(sym)               # entry session 'YYYY-MM-DD' (or None)
        ee = (entry_enrich.get(ed) or {}).get(sym) if ed else None   # enrichment as-of that session
        pcells.append([sym, f"{p['qty']:.0f}", f"${p['avg_entry']:,.2f}", f"${p['price']:,.2f}",
                       _money(p["market_value"]), "%s (%s)" % (_money(upl), _pct(plpc)),
                       (ed[5:] if ed else "—"), *_entry_stat_cells(ee), *_stat_cells(enrich.get(sym))])
        prules.append((i, 5, GREEN if upl >= 0 else RED))
    nrow = max(len(pcells), 1)
    ph = min(0.58, 0.05 + 0.027 * nrow)                # height grows with row count, capped
    axp = fig.add_axes([0.02, 0.885 - ph, 0.96, ph])
    _draw_table(axp, pcols, pcells, pcolw, prules, fontsize=6.0, head_tints=ptint)

    # ── queued orders (dry-run reconcile, latest prices) ─────────────────────
    qy = 0.885 - ph - 0.04
    qtitle = ("WHAT'S LIKELY NEXT — %s rebalance (preview off latest data; not due today, sends nothing)"
              % d.get("cadence", "next") if d.get("preview")
              else "QUEUED ORDERS  (dry-run reconcile, latest prices — sends nothing)")
    fig.text(0.04, qy, qtitle, fontsize=10, weight="bold")
    qcols = ["Side", "Ticker", "Qty", "Limit", "Est $", "Score", "Rank", "Trend",
             "Avg 1/5/20/60d", "Ret 1/5/20/60d", "Reason"]
    qraw = [5, 7, 4, 7, 8, 6, 7, 9, 16, 20, 30]
    qcolw = [w / sum(qraw) for w in qraw]
    qcells, qrules = [], []
    for i, o in enumerate(d["orders"]):
        sym = o["symbol"]; pl = o["_plan"]; dec = o.get("_decision") or {}
        side = o["side"].upper()
        reason = dec.get("reason", "")
        if dec.get("z") is not None:
            reason += "  [z %+.2f]" % dec["z"]
        qcells.append([side, sym, str(o["qty"]), "$%.2f" % o["limit_price"],
                       _money(pl.get("est_value")), *_stat_cells(enrich.get(sym)), reason])
        qrules.append((i, 0, GREEN if side == "BUY" else RED))
    for sup in d["suppressed"]:                          # show churn-suppressed trims too
        qcells.append(["HOLD", sup["symbol"], "%+d" % sup["delta"], "—", "—",
                       *_stat_cells(enrich.get(sup["symbol"])), "trim suppressed (churn deadband)"])
    qh = min(0.30, 0.04 + 0.026 * max(len(qcells), 1))
    axq = fig.add_axes([0.04, max(0.03, qy - 0.02 - qh), 0.92, qh])
    _draw_table(axq, qcols, qcells, qcolw, qrules)

    pdf.savefig(fig); plt.close(fig)


def run(accounts=None, end=None, out=None):
    today = end or date.today().isoformat()
    accts = accounts or DEFAULT_ACCOUNTS
    data = {n: _collect(n) for n in accts}

    syms = sorted({p["ticker"] for d in data.values() for p in (d.get("pos") or [])}
                  | {o["symbol"] for d in data.values() for o in (d.get("orders") or [])})
    enrich = {}
    if syms:
        try:
            enrich = _build_enrichment(syms)                       # current (as-of today)
        except Exception as exc:
            print("warning: per-ticker analytics unavailable (%s) — rendering without stats" % exc)

    # one @Entry enrichment per DISTINCT entry session across the fleet (deduped — a weekly rebalance
    # opens many names on the same day), so the as-of panel is rebuilt only a handful of times.
    entry_dates = sorted({ed for d in data.values() for ed in (d.get("entry") or {}).values() if ed})
    entry_enrich = {}
    for ed in entry_dates:
        try:
            entry_enrich[ed] = _build_enrichment(syms, as_of=date.fromisoformat(ed))
        except Exception as exc:
            print("warning: @entry analytics unavailable for %s (%s)" % (ed, exc))

    out = Path(out) if out else ROOT / "reports" / f"positions_report_{today}.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(out) as pdf:
        # cover
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle("Positions & Queued Orders — all accounts   %s" % today, fontsize=15, weight="bold")
        ax = fig.add_axes([0.06, 0.08, 0.88, 0.80]); ax.axis("off")
        ax.text(0, 1.0, "One page per account: current positions and the orders the live reconcile would "
                "send now (dry-run), each", fontsize=9.5, va="top", color="#333")
        ax.text(0, 0.965, "ticker enriched with composite score + rank, trailing 1/5/20/60d avg score, "
                "trend type, and trailing 1/5/20/60d return — shown @ENTRY (when opened) and NOW.",
                fontsize=9.5, va="top", color="#333")
        y = 0.90
        for n in accts:
            d = data[n]
            line = ("broker error" if d.get("err")
                    else "equity %s · cash %s · %d positions · %d %s · %s"
                    % (_money(d["eq"]), _money(d["cash"]), len(d["pos"]), len(d["orders"]),
                       "likely-next" if d.get("preview") else "queued",
                       ("%s (not due today)" % d.get("cadence") if d.get("preview")
                        else "%s — due today" % d.get("cadence"))))
            ax.text(0.0, y, n, fontsize=9.5, weight="bold", va="top")
            ax.text(0.28, y, line, fontsize=9, va="top", color=(RED if d.get("err") else "#333"))
            y -= 0.038
        ax.text(0, y - 0.02, "Stats use the model_v4 score panel; overlay names (TQQQ/SQQQ) sit outside the "
                "universe so their score/rank/avg show '—'.", fontsize=7.5, va="top", color="#666")
        pdf.savefig(fig); plt.close(fig)

        for n in accts:
            _account_page(pdf, data[n], enrich, entry_enrich, today)

    return {"pdf": str(out), "data": data}


if __name__ == "__main__":
    print(run()["pdf"])
