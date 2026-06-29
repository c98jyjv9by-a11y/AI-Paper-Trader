"""Positions + ALL ORDERS PLACED TODAY report across the broker accounts — a sibling of
positions_report, but the per-account orders section shows the day's ACTUAL orders (from the broker)
instead of the queued/likely-next reconcile plan.

Every ticker is enriched with the same analytics as positions_report (composite score + rank, trailing
1/5/20/60d avg score, trailing 1/5/20/60d return) — EXCEPT the trend column, which uses the ORDER-HISTORY
report's classifier (account_orders_report._score_pattern: Surging / Dropping / Climbing / Fading /
Stable, from the 60d->20d->5d->1d score trajectory) so the trend label matches that report exactly.

Order reasons come from accounts/<name>/broker/decisions.csv via account_orders_report._order_reason —
the same logged reason the order-history report shows. Renders reports/orders_today_<date>.pdf.

    python run.py orders-today-report [--accounts a b c] [--end YYYY-MM-DD] [--out FILE]
"""
import sys
import warnings
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["text.parse_math"] = False
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

sys.path.insert(0, str(Path(__file__).resolve().parent))
warnings.filterwarnings("ignore")

from broker_adapter import AlpacaPaper
import broker_sync as bs
import positions_report as pr
from positions_report import _money, _draw_table, _avg_quad, _ret_quad, _entry_dates
from intraday_check import _build_enrichment, _pct, _sc
from account_orders_report import (_score_pattern, _et_date, _load_decision_log, _order_reason,
                                   _annotate_trade_pnl)
from eod_accounts import disp

ROOT = Path(__file__).resolve().parent.parent
GREEN, RED, GREY, HEAD, ENTRY_HEAD = pr.GREEN, pr.RED, pr.GREY, pr.HEAD, pr.ENTRY_HEAD
DEFAULT_ACCOUNTS = pr.DEFAULT_ACCOUNTS


def _trend(e):
    """Order-history trend classification (account_orders_report._score_pattern) from the trailing
    avg-composite trajectory the enrichment already computes: avg[1]=cur, avg[5], avg[20], avg[60]."""
    if not e or not e.get("avg"):
        return "—"
    a = e["avg"]
    return _score_pattern(a.get(1), a.get(5), a.get(20), a.get(60))


def _stat_cells(e):
    """score, rank, trend (order-history pattern), avg 1/5/20/60, ret 1/5/20/60."""
    if not e:
        return ["—", "—", "—", "—", "—"]
    rank = f"#{e['rank']}/{e['n_uni']}" if e.get("rank") else "—"
    return [_sc(e.get("score")), rank, _trend(e), _avg_quad(e), _ret_quad(e)]


def _entry_stat_cells(e):
    """The 4 @Entry cells: score, trend (pattern), avg quad, ret quad (no past rank)."""
    if not e:
        return ["—", "—", "—", "—"]
    return [_sc(e.get("score")), _trend(e), _avg_quad(e), _ret_quad(e)]


def _collect(name, today):
    """Live positions + the account's orders PLACED TODAY (ET date), with logged reasons."""
    try:
        cli = AlpacaPaper(account=name)
        acct = cli.account()
        pos = cli.positions() or []
        kind = (bs.load_manifest(name) or {}).get("target_mode", {}).get("kind")
        allord = cli.orders(status="all", limit=500) or []
        price_now = {p["ticker"]: float(p["price"]) for p in pos}
        _annotate_trade_pnl(allord, price_now=price_now, today=today)   # adds rlz (sells) / unrlz (buys)
        todays = [o for o in allord
                  if _et_date(o.get("filled_at") or o.get("submitted_at")) == today]
        dec = _load_decision_log(name)
        entry = _entry_dates(cli, [p["ticker"] for p in pos])
        return {"name": name, "eq": float(acct.get("equity") or 0.0),
                "cash": float(acct.get("cash") or 0.0), "pos": pos, "orders": todays,
                "kind": kind, "dec": dec, "entry": entry, "err": None}
    except Exception as exc:
        return {"name": name, "err": str(exc)[:90]}


def _account_page(pdf, d, enrich, entry_enrich, today):
    name = d["name"]
    fig = plt.figure(figsize=(11, 8.5))
    if d.get("err"):
        fig.suptitle("%s — broker error" % disp(name), fontsize=13, weight="bold")
        fig.text(0.5, 0.5, d["err"], ha="center", color=RED, fontsize=10)
        pdf.savefig(fig); plt.close(fig); return

    nfilled = sum(1 for o in d["orders"] if float(o.get("filled_qty") or 0) > 0)
    fig.suptitle("%s   —   positions & orders placed today   (%s)" % (disp(name), today),
                 fontsize=13, weight="bold")
    fig.text(0.5, 0.945, "equity %s · cash %s · %d position(s) · %d order(s) today (%d filled)"
             % (_money(d["eq"]), _money(d["cash"]), len(d["pos"]), len(d["orders"]), nfilled),
             ha="center", fontsize=9, color="#333")

    # ── current positions — stats @ENTRY (purple) and NOW (slate), trend = order-history pattern ──
    fig.text(0.04, 0.905, "CURRENT POSITIONS   —   trailing scores/returns + trend (pattern) @ entry vs now",
             fontsize=10, weight="bold")
    pcols = ["Ticker", "Qty", "Entry$", "Last$", "Mkt Val", "Unreal P&L", "Entry\nDate",
             "@Ent\nScore", "@Ent\nTrend", "@Ent Avg\n1/5/20/60d", "@Ent Ret\n1/5/20/60d",
             "Now\nScore", "Now\nRank", "Now\nTrend", "Now Avg\n1/5/20/60d", "Now Ret\n1/5/20/60d"]
    praw = [6, 3, 6, 6, 7, 10, 5, 5, 7, 14, 16, 5, 6, 7, 14, 16]
    pcolw = [w / sum(praw) for w in praw]
    ptint = {j: ENTRY_HEAD for j in (6, 7, 8, 9, 10)}
    pcells, prules = [], []
    for i, p in enumerate(sorted(d["pos"], key=lambda x: -x.get("market_value", 0))):
        sym = p["ticker"]
        upl = p["market_value"] - p["qty"] * p["avg_entry"]
        plpc = p.get("unrealized_plpc", 0.0)
        ed = (d.get("entry") or {}).get(sym)
        ee = (entry_enrich.get(ed) or {}).get(sym) if ed else None
        pcells.append([sym, f"{p['qty']:.0f}", f"${p['avg_entry']:,.2f}", f"${p['price']:,.2f}",
                       _money(p["market_value"]), "%s (%s)" % (_money(upl), _pct(plpc)),
                       (ed[5:] if ed else "—"), *_entry_stat_cells(ee), *_stat_cells(enrich.get(sym))])
        prules.append((i, 5, GREEN if upl >= 0 else RED))
    nrow = max(len(pcells), 1)
    ph = min(0.52, 0.05 + 0.027 * nrow)
    axp = fig.add_axes([0.02, 0.885 - ph, 0.96, ph])
    _draw_table(axp, pcols, pcells, pcolw, prules, fontsize=6.0, head_tints=ptint)

    # ── ORDERS PLACED TODAY (actual broker orders, reasons from decisions.csv) ──────────────
    oy = 0.885 - ph - 0.04
    fig.text(0.04, oy, "ORDERS PLACED TODAY   —   actual broker fills; reason from the decision log",
             fontsize=10, weight="bold")
    ocols = ["Side", "Ticker", "Qty", "Fill $", "Value $", "Score", "Rank", "Trend",
             "Avg 1/5/20/60d", "Ret 1/5/20/60d", "Reason"]
    oraw = [5, 7, 4, 8, 9, 6, 7, 9, 15, 17, 34]
    ocolw = [w / sum(oraw) for w in oraw]
    rows = sorted(d["orders"], key=lambda o: -(float(o.get("filled_qty") or 0) * float(o.get("fill_price") or 0)))
    ocells, orules, tot = [], [], 0.0
    for i, o in enumerate(rows):
        sym = o.get("symbol", ""); side = (o.get("side") or "").upper()
        fq = float(o.get("filled_qty") or 0); fp = o.get("fill_price")
        val = fq * float(fp) if (fq and fp) else 0.0; tot += val
        reason = _order_reason(o, d.get("kind"), d.get("dec"))
        if o.get("status") != "filled":
            reason = "[%s] %s" % (o.get("status"), reason)
        reason = (reason[:50] + "…") if len(reason) > 51 else reason   # keep cell from overflowing
        ocells.append([side, sym, "%g" % fq if fq else "—",
                       ("$%.2f" % float(fp)) if fp else "—", _money(val) if val else "—",
                       *_stat_cells(enrich.get(sym)), reason])
        orules.append((i, 0, GREEN if side == "BUY" else RED))
    if rows:
        ocells.append(["TOTAL", "", "", "", _money(tot), "", "", "", "", "", ""])
    oh = min(0.32, 0.04 + 0.026 * max(len(ocells), 1))
    axo = fig.add_axes([0.04, max(0.03, oy - 0.02 - oh), 0.92, oh])
    _draw_table(axo, ocols, ocells, ocolw, orules, fontsize=6.3)

    pdf.savefig(fig); plt.close(fig)


def _summary_page(pdf, data, accts, enrich, today, side):
    """Cross-account summary of today's BUYS (Unrealized P&L) or SELLS (Realized P&L). One row per
    filled order: account, ticker analytics, 1-day return, P&L, reason — with a TOTAL row."""
    is_buy = (side == "buy")
    pnl_lbl = "Unrlzd P&L" if is_buy else "Rlzd P&L"
    title = "Orders Placed Today — %s (all accounts)" % ("BUYS" if is_buy else "SELLS")
    sub = ("Every BUY filled today, marked to current price → Unrealized P&L." if is_buy
           else "Every SELL filled today → Realized P&L vs average cost.")
    rows = []
    for n in accts:
        d = data[n]
        if d.get("err"):
            continue
        for ordr in d.get("orders", []):
            if (ordr.get("side") or "").lower() != side or not (ordr.get("fill_price") and ordr.get("filled_qty")):
                continue
            sym = ordr["symbol"]; e = enrich.get(sym)
            rows.append({"acct": disp(n), "sym": sym, "val": ordr["filled_qty"] * ordr["fill_price"],
                         "pnl": (ordr.get("unrlz") if is_buy else ordr.get("rlz")), "e": e,
                         "oneD": (e["ret"].get(1) if (e and e.get("ret")) else None),
                         "reason": _order_reason(ordr, d.get("kind"), d.get("dec"))})
    rows.sort(key=lambda r: (r["pnl"] is not None, r["pnl"] if r["pnl"] is not None else 0.0), reverse=True)

    fig = plt.figure(figsize=(11, 8.5))
    fig.suptitle(title + "   (%s)" % today, fontsize=14, weight="bold")
    fig.text(0.5, 0.95, sub, ha="center", fontsize=8.5, color="#555")
    cols = ["Account", "Ticker", "Value $", "Score", "Rank", "Trend", "Avg 1/5/20/60d", "1D Ret", pnl_lbl, "Reason"]
    raw = [16, 7, 9, 6, 7, 9, 16, 8, 11, 30]
    colw = [w / sum(raw) for w in raw]
    cells, rules, tv, tp = [], [], 0.0, 0.0
    for i, r in enumerate(rows):
        e = r["e"]; pnl = r["pnl"]
        score = _sc(e.get("score")) if e else "—"
        rank = f"#{e['rank']}/{e['n_uni']}" if (e and e.get("rank")) else "—"
        avgq = _avg_quad(e) if e else "—"
        oneD = _pct(r["oneD"]) if r["oneD"] is not None else "—"
        tv += r["val"]; tp += (pnl or 0.0)
        reason = r["reason"]; reason = (reason[:46] + "…") if len(reason) > 47 else reason
        cells.append([r["acct"], r["sym"], _money(r["val"]), score, rank, _trend(e), avgq, oneD,
                      _money(pnl) if pnl is not None else "—", reason])
        if pnl is not None:
            rules.append((i, 8, GREEN if pnl >= 0 else RED))
    if rows:
        cells.append(["TOTAL", "", _money(tv), "", "", "", "", "", _money(tp), ""])
        tr = len(rows)
        rules += [(tr, 0, HEAD), (tr, 2, HEAD), (tr, 8, GREEN if tp >= 0 else RED)]
    h = min(0.84, 0.06 + 0.029 * max(len(cells), 1))
    ax = fig.add_axes([0.03, max(0.05, 0.90 - h), 0.94, h])
    _draw_table(ax, cols, cells, colw, rules, fontsize=6.6)
    pdf.savefig(fig); plt.close(fig)


def run(accounts=None, end=None, out=None):
    today = end or date.today().isoformat()
    accts = accounts or DEFAULT_ACCOUNTS
    data = {n: _collect(n, today) for n in accts}

    syms = sorted({p["ticker"] for d in data.values() for p in (d.get("pos") or [])}
                  | {o.get("symbol") for d in data.values() for o in (d.get("orders") or []) if o.get("symbol")})
    enrich = {}
    if syms:
        try:
            enrich = _build_enrichment(syms)
        except Exception as exc:
            print("warning: per-ticker analytics unavailable (%s)" % exc)

    entry_dates = sorted({ed for d in data.values() for ed in (d.get("entry") or {}).values() if ed})
    entry_enrich = {}
    for ed in entry_dates:
        try:
            entry_enrich[ed] = _build_enrichment(syms, as_of=date.fromisoformat(ed))
        except Exception as exc:
            print("warning: @entry analytics unavailable for %s (%s)" % (ed, exc))

    out = Path(out) if out else ROOT / "reports" / f"orders_today_{today}.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(out) as pdf:
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle("Positions & Orders Placed Today — all accounts   %s" % today, fontsize=15, weight="bold")
        ax = fig.add_axes([0.06, 0.08, 0.88, 0.80]); ax.axis("off")
        ax.text(0, 1.0, "One page per account: current positions and every order PLACED TODAY (actual broker "
                "fills, reasons from the decision log),", fontsize=9.5, va="top", color="#333")
        ax.text(0, 0.965, "each ticker enriched with score + rank, trailing 1/5/20/60d avg score & return, and "
                "the order-history TREND pattern (Surging/Dropping/Climbing/Fading/Stable).",
                fontsize=9.5, va="top", color="#333")
        y = 0.90
        for n in accts:
            d = data[n]
            nf = 0 if d.get("err") else sum(1 for o in d["orders"] if float(o.get("filled_qty") or 0) > 0)
            line = ("broker error" if d.get("err")
                    else "equity %s · cash %s · %d positions · %d order(s) today (%d filled)"
                    % (_money(d["eq"]), _money(d["cash"]), len(d["pos"]), len(d["orders"]), nf))
            ax.text(0.0, y, disp(n), fontsize=9.5, weight="bold", va="top")
            ax.text(0.30, y, line, fontsize=9, va="top", color=(RED if d.get("err") else "#333"))
            y -= 0.038
        ax.text(0, y - 0.02, "Trend = account_orders_report._score_pattern (same as the order-history report). "
                "Overlay names (TQQQ/SQQQ) sit outside the universe so score/rank/avg show '—'.",
                fontsize=7.5, va="top", color="#666")
        pdf.savefig(fig); plt.close(fig)

        _summary_page(pdf, data, accts, enrich, today, "buy")    # buys across all accounts (unrealized)
        _summary_page(pdf, data, accts, enrich, today, "sell")   # sells across all accounts (realized)

        for n in accts:
            _account_page(pdf, data[n], enrich, entry_enrich, today)

    return {"pdf": str(out), "data": data}


if __name__ == "__main__":
    print(run()["pdf"])
