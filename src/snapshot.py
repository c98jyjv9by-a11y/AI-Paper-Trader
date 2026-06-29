"""snapshot.py — daily SNAPSHOT report across every broker account.

Two parts (replaces the old performance-snapshot):

  • PAGE 1 — a summary table (the order-history report's cover, re-cut): per account, the CURRENT DAY's
    P&L so far vs the daily QQQ/SPY benchmark move, then SINCE-INCEPTION P&L vs the QQQ/SPY benchmark over
    that same inception→today window, plus #positions, #orders, and #days trading. A TOTAL row aggregates.

  • PAGE 2+ — "Orders Today": every order whose submission falls in the CURRENT session window — from the
    PRIOR trading day's market close (16:00 ET) through now (so the post-close EOD-agent fills and the
    pre-open auction orders that set up today's book are included). One page per account that traded,
    with the SAME per-order stats columns as the account order-history report (Score@sub / Trail / Pattern
    / Rlz / Unrlz / Ret / Reason — reused verbatim from account_orders_report so the two always agree).

    python run.py snapshot [--end YYYY-MM-DD] [--accounts a b c] [--out FILE]
"""
from __future__ import annotations

import sys
import warnings
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["text.parse_math"] = False     # '$' is currency here, not a mathtext toggle
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import account_orders_report as AO
from account_orders_report import (
    _collect, _bench_panel, _bench, _load_rank_snapshots,
    _order_builders, _order_total_row, _color_orders, _table, _new_page,
    ORDER_COLS, ORDER_RAW, _money, _pct, DEFAULT_ACCOUNTS, GREEN, RED, GREY,
)
from broker_adapter import AlpacaPaper

_ET = ZoneInfo("America/New_York")
_UTC = ZoneInfo("UTC")
HEAD = "#34495e"
ORDERS_PER_PAGE = 30


# ── benchmark + calendar helpers ─────────────────────────────────────────────────
def _live_bench_px(accts, data) -> Dict[str, float]:
    """Current QQQ/SPY mid from the first working broker client (market-wide — one quote serves all)."""
    for n in accts:
        if data[n].get("err"):
            continue
        try:
            q = AlpacaPaper(account=n).latest_prices(["QQQ", "SPY"]) or {}
            out = {s: float(q[s]["mid"]) for s in ("QQQ", "SPY") if q.get(s) and q[s].get("mid")}
            if out:
                return out
        except Exception:
            continue
    return {}


def _prior_trading_day(panel, today: str) -> Optional[str]:
    """The most recent trading-session date STRICTLY before `today` (YYYY-MM-DD), off the QQQ/SPY price
    calendar — the close that the current day's P&L and the Orders-Today window are measured from."""
    if panel is None:
        return None
    try:
        dts = [d.strftime("%Y-%m-%d") for d in panel.index]
        prior = [x for x in dts if x < today]
        return prior[-1] if prior else None
    except Exception:
        return None


def _daily_bench(panel, prior_day, live_px) -> Dict[str, float]:
    """{QQQ,SPY} return from the PRIOR trading-day close to NOW — the same daily window as each account's
    intraday day-P&L. Endpoint is the live broker quote when available, else the panel's latest close."""
    out: Dict[str, float] = {}
    if panel is None or not prior_day:
        return out
    try:
        base = panel.loc[:prior_day]
        if base.empty:
            return out
        b0 = base.iloc[-1]
        for s in ("QQQ", "SPY"):
            if s not in panel.columns or float(b0[s]) <= 0:
                continue
            end_px = live_px.get(s) or float(panel.iloc[-1][s])
            out[s] = float(end_px) / float(b0[s]) - 1
    except Exception:
        pass
    return out


def _days_trading(panel, inception) -> Optional[int]:
    """# trading sessions from inception (inclusive) through today, off the price calendar."""
    if panel is None or not inception:
        return None
    try:
        return int(len(panel.loc[inception:]))
    except Exception:
        return None


def _et_dt(ts):
    """ISO timestamp → tz-aware Eastern datetime, or None."""
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return (dt.replace(tzinfo=_UTC) if dt.tzinfo is None else dt).astimezone(_ET)
    except Exception:
        return None


def _today_orders(orders, win_start, win_end):
    """Orders submitted within (prior-close, today] — newest first (the order list already is)."""
    out = []
    for o in orders:
        dt = _et_dt(o.get("submitted_at") or o.get("filled_at"))
        if dt is not None and win_start < dt <= win_end:
            out.append(o)
    return out


# ── page 1: summary table ────────────────────────────────────────────────────────
def _render_summary(pdf, data, accts, today, panel, ibench, dbench, prior_day):
    fig = plt.figure(figsize=(11, 8.5))
    fig.suptitle("Snapshot — daily & since-inception P&L vs benchmarks   %s" % today,
                 fontsize=14, weight="bold")
    dq, ds = dbench.get("QQQ"), dbench.get("SPY")
    sub = ("Day = today's change so far vs the prior close (%s)   ·   Since inception = each account's "
           "own start→today window" % (prior_day or "—"))
    fig.text(0.5, 0.945, sub, ha="center", fontsize=8, color="#555")

    ax = fig.add_axes([0.03, 0.34, 0.94, 0.55]); ax.axis("off")
    cols = ["Account", "Equity", "Day\nP&L", "Day\n%", "Day\nQQQ", "Day\nSPY",
            "Incep\nP&L", "Incep\n%", "Incep\nQQQ", "Incep\nSPY", "Pos", "Ord", "Days"]
    raw = [15, 11, 9, 7, 7, 7, 10, 8, 7, 7, 5, 5, 6]

    def _b(v):
        return _pct(v) if v is not None else "—"

    cells, ok = [], []
    for n in accts:
        d = data[n]
        if d.get("err"):
            cells.append([n, "—", "—", "—", _b(dq), _b(ds), "ERR", "—", "—", "—", "—", "—", "—"])
            continue
        ok.append(d)
        ib = ibench.get(n) or {}
        days = _days_trading(panel, d.get("inception"))
        cells.append([n, _money(d["eq"]),
                      _money(d["day_pnl"]) if d.get("day_pnl") is not None else "—", _b(d.get("day_ret")),
                      _b(dq), _b(ds),
                      _money(d["total_pnl"]), _b(d["tot_ret"]), _b(ib.get("QQQ")), _b(ib.get("SPY")),
                      str(len(d["pos"])), str(len(d["orders"])),
                      str(days) if days is not None else "—"])
    if ok:
        agg = {k: sum(d[k] for d in ok) for k in ("eq", "total_pnl", "start")}
        day_ok = [d for d in ok if d.get("day_pnl") is not None]
        day_pnl = sum(d["day_pnl"] for d in day_ok)
        day_last = sum(d["last_eq"] for d in day_ok)

        def _blend(sym):
            num = sum(d["start"] * ibench[d["name"]][sym] for d in ok
                      if (ibench.get(d["name"]) or {}).get(sym) is not None)
            den = sum(d["start"] for d in ok if (ibench.get(d["name"]) or {}).get(sym) is not None)
            return (num / den) if den else None
        cells.append(["TOTAL", _money(agg["eq"]),
                      (_money(day_pnl) if day_ok else "—"), (_b(day_pnl / day_last) if day_last else "—"),
                      _b(dq), _b(ds),
                      _money(agg["total_pnl"]), _b(agg["eq"] / agg["start"] - 1 if agg["start"] else 0.0),
                      _b(_blend("QQQ")), _b(_blend("SPY")),
                      str(sum(len(d["pos"]) for d in ok)), str(sum(len(d["orders"]) for d in ok)), "—"])

    t = ax.table(cellText=cells, colLabels=cols, colWidths=[w / sum(raw) for w in raw],
                 loc="upper center", cellLoc="center")
    t.auto_set_font_size(False); t.set_fontsize(7.6); t.scale(1, 1.7)
    for j in range(len(cols)):
        t[0, j].set_facecolor(HEAD); t[0, j].set_text_props(color="white", weight="bold"); t[0, j].set_fontsize(7.0)
    # per-row sign coloring on the 8 P&L / return / benchmark cells (cols 2..9)
    for i, n in enumerate(accts):
        d = data[n]
        if d.get("err"):
            t[i + 1, 6].set_text_props(color=RED, weight="bold")
            for j, v in [(4, dq), (5, ds)]:
                if v is not None:
                    t[i + 1, j].set_text_props(color=(GREEN if v >= 0 else RED))
            continue
        ib = ibench.get(n) or {}
        for j, v in [(2, d.get("day_pnl")), (3, d.get("day_ret")), (4, dq), (5, ds),
                     (6, d["total_pnl"]), (7, d["tot_ret"]), (8, ib.get("QQQ")), (9, ib.get("SPY"))]:
            if v is not None:
                t[i + 1, j].set_text_props(color=(GREEN if v >= 0 else RED), weight="bold")
    if ok:                                                    # shade + bold the TOTAL row
        tr = len(accts) + 1
        for j in range(len(cols)):
            t[tr, j].set_facecolor("#dfe6e9"); t[tr, j].set_text_props(weight="bold")

    n1 = ("Day P&L = equity − prior-close equity (today's intraday change SO FAR); Day % = that ÷ prior-close "
          "equity.  Day QQQ / SPY = the benchmark's move over the SAME prior-close→now window (one market-wide "
          "number; TOTAL Day % = Σ day P&L ÷ Σ prior-close equity).")
    n2 = ("Incep P&L = equity − starting (broker).  Incep % / QQQ / SPY = total return over EACH account's own "
          "inception→today window (timelines aligned per account; TOTAL benchmark = starting-weighted blend).  "
          "Days = trading sessions since inception.  ERR = the account's Alpaca keys are unset/placeholder.")
    fig.text(0.03, 0.27, n1, fontsize=7.4, color="#555", wrap=True)
    fig.text(0.03, 0.215, n2, fontsize=7.4, color="#555", wrap=True)
    pdf.savefig(fig); plt.close(fig)


# ── page 2+: orders today ────────────────────────────────────────────────────────
def _render_orders_today(pdf, data, accts, today, prior_day, snapshots, sig_cache, trail_cache):
    win_end = datetime.combine(date.fromisoformat(today), time(23, 59, 59), tzinfo=_ET)
    win_start = (datetime.combine(date.fromisoformat(prior_day), time(16, 0), tzinfo=_ET)
                 if prior_day else win_end - timedelta(days=1))
    win_lbl = ("since the prior close (%s 16:00 ET) through now" % prior_day) if prior_day else "today"
    ow = [w / sum(ORDER_RAW) for w in ORDER_RAW]

    any_today = False
    for n in accts:
        d = data[n]
        if d.get("err"):
            continue
        todays = _today_orders(d["orders"], win_start, win_end)
        if not todays:
            continue
        any_today = True
        _orow, _patterncell = _order_builders(d, snapshots, sig_cache, trail_cache)
        total_row, realized_sum, unrlz_sum = _order_total_row(todays)
        rest, page = todays, 1
        npages = max(1, (len(todays) + ORDERS_PER_PAGE - 1) // ORDERS_PER_PAGE)
        while rest:
            chunk, rest = rest[:ORDERS_PER_PAGE], rest[ORDERS_PER_PAGE:]
            sub = "Orders Today — %s%s" % (win_lbl, "" if npages == 1 else "  (page %d/%d)" % (page, npages))
            fig = _new_page(pdf, "Orders Today — %s  (%d)" % (n, len(todays)), sub=sub)
            cells = [total_row] + [_orow(o) for o in chunk]
            _, ot = _table(fig, [0.02, 0.05, 0.96, 0.84], ORDER_COLS, cells, ow, fontsize=5.5)
            if ot is not None:
                _color_orders(ot, chunk, 2, _patterncell, realized_sum, unrlz_sum)
            fig.text(0.02, 0.93, "Same per-order stats as the order-history report.  Score@sub = the book's OWN "
                     "selection metric #rank as-of the order date.  Trail 1/5/10/20/60d = current close composite "
                     "score + its trailing averages.  Pattern = score TRAJECTORY (Surging/Climbing/Stable/Fading/"
                     "Dropping).  Times in CT.", fontsize=6.3, color="#555")
            pdf.savefig(fig); plt.close(fig)
            page += 1

    if not any_today:
        fig = _new_page(pdf, "Orders Today", sub="Orders Today — %s" % win_lbl)
        ax = fig.add_axes([0.06, 0.1, 0.88, 0.78]); ax.axis("off")
        ax.text(0.0, 1.0, "No orders in the current session window across any account.", fontsize=11,
                weight="bold", color="#333", va="top")
        ax.text(0.0, 0.93, "Window: %s." % win_lbl, fontsize=9, color=GREY, va="top")
        pdf.savefig(fig); plt.close(fig)


def run(end: Optional[date] = None, output: Optional[Path] = None,
        accounts: Optional[List[str]] = None, window=None) -> "tuple[Path, List[Dict[str, Any]]]":
    today = (end.isoformat() if hasattr(end, "isoformat") else end) or date.today().isoformat()
    accts = accounts or DEFAULT_ACCOUNTS
    data = {n: _collect(n, today, status="all") for n in accts}

    incs = [data[n]["inception"] for n in accts if not data[n].get("err") and data[n].get("inception")]
    panel = _bench_panel(today, min(incs)) if incs else None
    ibench = {n: _bench(panel, data[n].get("inception")) for n in accts if not data[n].get("err")}
    live_px = _live_bench_px(accts, data)
    prior_day = _prior_trading_day(panel, today)
    dbench = _daily_bench(panel, prior_day, live_px)
    snapshots = _load_rank_snapshots()
    sig_cache, trail_cache = {}, {}

    out = Path(output) if output else ROOT / "reports" / f"snapshot_{today}.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(out) as pdf:
        _render_summary(pdf, data, accts, today, panel, ibench, dbench, prior_day)
        _render_orders_today(pdf, data, accts, today, prior_day, snapshots, sig_cache, trail_cache)

    rows = [{"label": n, "error": data[n].get("err")} for n in accts]
    return out, rows


if __name__ == "__main__":
    out, rows = run()
    ok = sum(1 for r in rows if not r.get("error"))
    print("Wrote %s  (%d/%d accounts)" % (out, ok, len(rows)))
