"""snapshot.py — daily SNAPSHOT report across every broker account.

Two parts (replaces the old performance-snapshot):

  • PAGE 1 — a summary table (the order-history report's cover, re-cut): per account, the CURRENT DAY's
    P&L so far + Day %, then SINCE-INCEPTION P&L + % vs the QQQ/SPY benchmark over each account's own
    inception→today window, plus #positions, #orders, and #days trading. A TOTAL row aggregates, and below
    it three BENCHMARK ROWS — QQQ, SPY, and the equal-weight model_v4 Universe average — each showing the
    daily return and the since-inception return (starting-weighted across the fleet).

  • PAGE 2 — "Orders Today, totals by account": a per-account roll-up (counts + traded $ + realized /
    unrealized) of the orders in the current session window — no per-ticker detail.

  • PAGE 3+ — "Orders Today" per-account detail: every order whose submission falls in the CURRENT session
    window — from the PRIOR trading day's market close (16:00 ET) through now (so the post-close EOD-agent
    fills and the pre-open auction orders that set up today's book are included) — with the SAME per-order
    stats columns as the account order-history report (Score@sub / Trail / Pattern / Rlz / Unrlz / Ret /
    Held / Reason — reused verbatim from account_orders_report so the two always agree).

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
    ORDER_COLS, ORDER_RAW, _money, _pct, DEFAULT_ACCOUNTS, GREEN, RED, GREY, disp,
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


def _universe_panel(today, start):
    """Close panel for the model_v4 universe (the ~83 names) from `start` through `today` — the source for
    the equal-weight UNIVERSE-AVERAGE benchmark row. None on failure."""
    try:
        import datetime as _dt
        from backtest import load_config, fetch_backtest_data
        from scenarios import load_scenario, build_config
        cfg = build_config(load_config(ROOT / "config"), load_scenario("model_v4"))
        s = _dt.date.fromisoformat(start) - _dt.timedelta(days=10)
        cl = fetch_backtest_data(cfg["tickers"], s, _dt.date.fromisoformat(today))["Close"]
        return cl if hasattr(cl, "columns") else None
    except Exception:
        return None


def _avg_ret(panel, base_date):
    """Equal-weight mean across columns of (latest bar / close on-or-before `base_date` − 1) — the universe
    avg return from `base_date` to now. base_date = prior close → daily; = inception → since-inception.
    None when the base date isn't covered."""
    if panel is None or not base_date:
        return None
    try:
        base = panel.loc[:base_date]
        if base.empty:
            return None
        b0, b1 = base.iloc[-1], panel.iloc[-1]
        rets = [float(b1[c]) / float(b0[c]) - 1 for c in panel.columns
                if float(b0[c]) > 0 and b0[c] == b0[c] and b1[c] == b1[c]]
        return (sum(rets) / len(rets)) if rets else None
    except Exception:
        return None


def _session_window(today, prior_day):
    """(win_start, win_end, label) for the CURRENT session: the prior trading-day close (16:00 ET) → now.
    Orders submitted in this window are 'today's' (incl. post-close EOD fills + pre-open auction orders)."""
    win_end = datetime.combine(date.fromisoformat(today), time(23, 59, 59), tzinfo=_ET)
    win_start = (datetime.combine(date.fromisoformat(prior_day), time(16, 0), tzinfo=_ET)
                 if prior_day else win_end - timedelta(days=1))
    lbl = ("since the prior close (%s 16:00 ET) through now" % prior_day) if prior_day else "today"
    return win_start, win_end, lbl


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
def _render_summary(pdf, data, accts, today, panel, ibench, dbench, prior_day, bench_rows):
    fig = plt.figure(figsize=(11, 8.5))
    fig.suptitle("Snapshot — daily & since-inception P&L vs benchmarks   %s" % today,
                 fontsize=14, weight="bold")
    sub = ("Account returns are on INVESTED capital (equity − cash; cash excluded)   ·   Day = vs the prior "
           "close (%s)   ·   benchmark rows below TOTAL" % (prior_day or "—"))
    fig.text(0.5, 0.945, sub, ha="center", fontsize=8, color="#555")

    ax = fig.add_axes([0.05, 0.34, 0.90, 0.55]); ax.axis("off")
    cols = ["Account", "Equity", "Day\nP&L", "Day\n%", "Incep\nP&L", "Incep\n%", "Incep\nQQQ", "Incep\nSPY",
            "Pos", "Ord", "Days"]
    raw = [16, 12, 10, 8, 11, 8, 8, 8, 5, 5, 6]
    DAYCOL, INCCOL = 3, 5                              # the columns the benchmark rows write into

    def _b(v):
        return _pct(v) if v is not None else "—"

    cells, ok = [], []
    for n in accts:
        d = data[n]
        if d.get("err"):
            cells.append([disp(n), "—", "—", "—", "ERR", "—", "—", "—", "—", "—", "—"])
            continue
        ok.append(d)
        ib = ibench.get(n) or {}
        days = _days_trading(panel, d.get("inception"))
        inv = max(d["eq"] - d["cash"], 0.0)               # invested capital — cash EXCLUDED from the denominator
        dret = (d["day_pnl"] / inv) if (inv > 0 and d.get("day_pnl") is not None) else None
        tret = (d["total_pnl"] / inv) if inv > 0 else None
        cells.append([disp(n), _money(d["eq"]),
                      _money(d["day_pnl"]) if d.get("day_pnl") is not None else "—", _b(dret),
                      _money(d["total_pnl"]), _b(tret), _b(ib.get("QQQ")), _b(ib.get("SPY")),
                      str(len(d["pos"])), str(len(d["orders"])), str(days) if days is not None else "—"])
    if ok:
        agg = {k: sum(d[k] for d in ok) for k in ("eq", "total_pnl", "start")}
        day_ok = [d for d in ok if d.get("day_pnl") is not None]
        day_pnl = sum(d["day_pnl"] for d in day_ok)
        inv_day = sum(max(d["eq"] - d["cash"], 0.0) for d in day_ok)   # invested base (cash excluded)
        inv_all = sum(max(d["eq"] - d["cash"], 0.0) for d in ok)

        def _blend(sym):
            num = sum(d["start"] * ibench[d["name"]][sym] for d in ok
                      if (ibench.get(d["name"]) or {}).get(sym) is not None)
            den = sum(d["start"] for d in ok if (ibench.get(d["name"]) or {}).get(sym) is not None)
            return (num / den) if den else None
        cells.append(["TOTAL", _money(agg["eq"]),
                      (_money(day_pnl) if day_ok else "—"), (_b(day_pnl / inv_day) if inv_day else "—"),
                      _money(agg["total_pnl"]), _b(agg["total_pnl"] / inv_all if inv_all else None),
                      _b(_blend("QQQ")), _b(_blend("SPY")),
                      str(sum(len(d["pos"]) for d in ok)), str(sum(len(d["orders"]) for d in ok)), "—"])
    # benchmark reference rows below TOTAL — daily return in the Day-% column, since-inception in the Incep-% column
    bench_start = len(cells)
    for label, dayret, incret in bench_rows:
        row = [label] + ["—"] * (len(cols) - 1)
        row[DAYCOL], row[INCCOL] = _b(dayret), _b(incret)
        cells.append(row)

    t = ax.table(cellText=cells, colLabels=cols, colWidths=[w / sum(raw) for w in raw],
                 loc="upper center", cellLoc="center")
    t.auto_set_font_size(False); t.set_fontsize(7.6); t.scale(1, 1.7)
    for j in range(len(cols)):
        t[0, j].set_facecolor(HEAD); t[0, j].set_text_props(color="white", weight="bold"); t[0, j].set_fontsize(7.0)
    # per-account sign coloring on the P&L / return / benchmark cells (cols 2,3,4,5,6,7)
    for i, n in enumerate(accts):
        d = data[n]
        if d.get("err"):
            t[i + 1, 4].set_text_props(color=RED, weight="bold")
            continue
        ib = ibench.get(n) or {}
        inv = max(d["eq"] - d["cash"], 0.0)
        dret = (d["day_pnl"] / inv) if (inv > 0 and d.get("day_pnl") is not None) else None
        tret = (d["total_pnl"] / inv) if inv > 0 else None
        for j, v in [(2, d.get("day_pnl")), (3, dret), (4, d["total_pnl"]), (5, tret),
                     (6, ib.get("QQQ")), (7, ib.get("SPY"))]:
            if v is not None:
                t[i + 1, j].set_text_props(color=(GREEN if v >= 0 else RED), weight="bold")
    if ok:                                                    # shade + bold the TOTAL row
        tr = len(accts) + 1
        for j in range(len(cols)):
            t[tr, j].set_facecolor("#dfe6e9"); t[tr, j].set_text_props(weight="bold")
    for k, (label, dayret, incret) in enumerate(bench_rows):  # tint + sign-color the benchmark rows
        r = bench_start + 1 + k
        for j in range(len(cols)):
            t[r, j].set_facecolor("#eef2f7")
        t[r, 0].set_text_props(style="italic", color="#333")
        for j, v in [(DAYCOL, dayret), (INCCOL, incret)]:
            if v is not None:
                t[r, j].set_text_props(color=(GREEN if v >= 0 else RED))

    n1 = ("Day P&L = equity − prior-close equity (today's intraday change SO FAR); Incep P&L = equity − starting.  "
          "Day % and Incep % are on INVESTED capital — P&L ÷ (equity − cash) — so idle cash is EXCLUDED from the "
          "denominator and the figures are comparable to the fully-invested benchmark rows (TOTAL = Σ P&L ÷ Σ invested).  "
          "Incep QQQ / SPY columns = each account's benchmark over its own inception→today window.")
    n2 = ("Benchmark rows (below TOTAL): QQQ / SPY = the index move; Universe avg = equal-weight mean of the "
          "model_v4 universe.  Day column = the prior-close→now move; Incep column = the same metric over the "
          "fleet's inception window (starting-weighted).  Days = trading sessions since inception.")
    fig.text(0.05, 0.27, n1, fontsize=7.4, color="#555", wrap=True)
    fig.text(0.05, 0.215, n2, fontsize=7.4, color="#555", wrap=True)
    pdf.savefig(fig); plt.close(fig)


# ── buys tables — every BUY in a window, by account & ticker, sorted by current unrealized P&L ───
def _render_buys(pdf, data, accts, win_start, win_end, title, sub):
    rows = []
    for n in accts:
        d = data[n]
        if d.get("err"):
            continue
        for o in d["orders"]:
            if (o.get("side") or "").lower() != "buy" or not (o.get("fill_price") and o.get("filled_qty")):
                continue
            dt = _et_dt(o.get("submitted_at") or o.get("filled_at"))
            if dt is None or not (win_start < dt <= win_end):
                continue
            qty, px = o["filled_qty"], o["fill_price"]
            rows.append({"acct": disp(n), "sym": o.get("symbol", ""), "qty": qty, "px": px,
                         "cost": qty * px, "unrlz": o.get("unrlz"), "ret": o.get("ret"),
                         "held": o.get("days_held")})
    # descending by current unrealized P&L; buys no longer held (unrlz None) sort to the bottom
    rows.sort(key=lambda r: (r["unrlz"] is not None, r["unrlz"] if r["unrlz"] is not None else 0.0), reverse=True)
    cols = ["Account", "Ticker", "Qty", "Buy px", "Cost $", "Unreal $", "Unreal %", "Held"]
    raw = [18, 8, 6, 8, 10, 10, 8, 6]
    tot_cost = sum(r["cost"] for r in rows)
    tot_unrlz = sum(r["unrlz"] for r in rows if r["unrlz"] is not None)
    PER = 32
    chunks = [rows[i:i + PER] for i in range(0, len(rows), PER)] or [[]]
    for pi, chunk in enumerate(chunks):
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle(title + ("" if len(chunks) == 1 else "  (%d/%d)" % (pi + 1, len(chunks))),
                     fontsize=14, weight="bold")
        fig.text(0.5, 0.945, sub, ha="center", fontsize=8, color="#555")
        ax = fig.add_axes([0.06, 0.09, 0.88, 0.82]); ax.axis("off")
        cells = [[r["acct"], r["sym"], "%g" % r["qty"], "$%.2f" % r["px"], _money(r["cost"]),
                  (_money(r["unrlz"]) if r["unrlz"] is not None else "—"),
                  (_pct(r["ret"]) if r["ret"] is not None else "—"),
                  ("%dd" % r["held"] if r["held"] is not None else "—")] for r in chunk]
        last = pi == len(chunks) - 1
        if last and rows:
            cells.append(["TOTAL", "", "", "", _money(tot_cost), _money(tot_unrlz), "", ""])
        if not rows:
            cells = [["— no buys in this window —"] + [""] * (len(cols) - 1)]
        # bbox-constrained so the table always fits the axes (compresses rows) instead of overflowing
        bh = min(1.0, 0.04 + 0.03 * len(cells))
        t = ax.table(cellText=cells, colLabels=cols, colWidths=[w / sum(raw) for w in raw],
                     cellLoc="center", bbox=[0, 1 - bh, 1, bh])
        t.auto_set_font_size(False); t.set_fontsize(7.5)
        for j in range(len(cols)):
            t[0, j].set_facecolor(HEAD); t[0, j].set_text_props(color="white", weight="bold")
        for i, r in enumerate(chunk):
            if r["unrlz"] is not None:
                t[i + 1, 5].set_text_props(color=(GREEN if r["unrlz"] >= 0 else RED), weight="bold")
            if r["ret"] is not None:
                t[i + 1, 6].set_text_props(color=(GREEN if r["ret"] >= 0 else RED))
        if last and rows:
            tr = len(chunk) + 1
            for j in range(len(cols)):
                t[tr, j].set_facecolor("#dfe6e9"); t[tr, j].set_text_props(weight="bold")
            if tot_unrlz:
                t[tr, 5].set_text_props(color=(GREEN if tot_unrlz >= 0 else RED), weight="bold")
        fig.text(0.06, 0.035, "Every BUY filled in the window, by account & ticker, marked to current prices and "
                 "sorted by unrealized P&L (descending).  Unreal $ / % = mark-to-market vs the buy fill; Held = "
                 "days since the buy.  Buys already sold out show '—' and sort last.", fontsize=7.2, color="#555", wrap=True)
        pdf.savefig(fig); plt.close(fig)


# ── page: orders today — totals by account (no per-ticker detail) ────────────────
def _render_orders_by_account(pdf, data, accts, today, win_start, win_end, win_lbl):
    fig = plt.figure(figsize=(11, 8.5))
    fig.suptitle("Orders Today — totals by account   %s" % today, fontsize=14, weight="bold")
    fig.text(0.5, 0.945, "Per-account roll-up of orders %s (no per-ticker detail — see the following pages)"
             % win_lbl, ha="center", fontsize=8, color="#555")
    ax = fig.add_axes([0.08, 0.30, 0.84, 0.58]); ax.axis("off")
    cols = ["Account", "Orders", "Buys", "Sells", "Filled", "Traded $", "Realized $", "Unreal $"]
    raw = [18, 7, 6, 6, 7, 11, 11, 11]
    cells = []
    tot = dict(orders=0, buys=0, sells=0, filled=0, value=0.0, rlz=0.0, unrlz=0.0)
    meta = []                                                # (rlz, unrlz) per row for coloring; None for ERR/TOTAL
    for n in accts:
        d = data[n]
        if d.get("err"):
            cells.append([disp(n), "—", "—", "—", "—", "—", "—", "—"]); meta.append(None); continue
        td = _today_orders(d["orders"], win_start, win_end)
        nb = sum(1 for o in td if (o.get("side") or "").lower() == "buy")
        ns = sum(1 for o in td if (o.get("side") or "").lower() == "sell")
        nf = sum(1 for o in td if o.get("status") == "filled")
        val = sum(o["filled_qty"] * o["fill_price"] for o in td if o.get("fill_price") and o.get("filled_qty"))
        rlz = sum(o["rlz"] for o in td if o.get("rlz") is not None)
        unrlz = sum(o["unrlz"] for o in td if o.get("unrlz") is not None)
        cells.append([disp(n), str(len(td)), str(nb), str(ns), str(nf), _money(val), _money(rlz), _money(unrlz)])
        meta.append((rlz, unrlz))
        for k, v in (("orders", len(td)), ("buys", nb), ("sells", ns), ("filled", nf),
                     ("value", val), ("rlz", rlz), ("unrlz", unrlz)):
            tot[k] += v
    cells.append(["TOTAL", str(tot["orders"]), str(tot["buys"]), str(tot["sells"]), str(tot["filled"]),
                  _money(tot["value"]), _money(tot["rlz"]), _money(tot["unrlz"])])
    t = ax.table(cellText=cells, colLabels=cols, colWidths=[w / sum(raw) for w in raw],
                 loc="upper center", cellLoc="center")
    t.auto_set_font_size(False); t.set_fontsize(8.0); t.scale(1, 1.7)
    for j in range(len(cols)):
        t[0, j].set_facecolor(HEAD); t[0, j].set_text_props(color="white", weight="bold")
    for i, m in enumerate(meta):
        if m is None:
            continue
        for j, v in ((6, m[0]), (7, m[1])):
            if v:
                t[i + 1, j].set_text_props(color=(GREEN if v >= 0 else RED), weight="bold")
    tr = len(accts) + 1                                       # TOTAL row
    for j in range(len(cols)):
        t[tr, j].set_facecolor("#dfe6e9"); t[tr, j].set_text_props(weight="bold")
    for j, v in ((6, tot["rlz"]), (7, tot["unrlz"])):
        if v:
            t[tr, j].set_text_props(color=(GREEN if v >= 0 else RED), weight="bold")
    fig.text(0.08, 0.24, "Counts and dollar totals of the orders each account placed in the current session "
             "window (%s).  Traded $ = Σ filled qty × fill price.  Realized / Unreal = Σ per-order realized "
             "(sells) / mark-to-market (held buys) P&L — same figures the per-account detail pages total."
             % win_lbl, fontsize=7.6, color="#555", wrap=True)
    pdf.savefig(fig); plt.close(fig)


# ── page 3+: orders today — per-account ticker detail ────────────────────────────
def _render_orders_today(pdf, data, accts, today, win_start, win_end, win_lbl, snapshots, sig_cache, trail_cache):
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
            fig = _new_page(pdf, "Orders Today — %s  (%d)" % (disp(n), len(todays)), sub=sub)
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
    win_start, win_end, win_lbl = _session_window(today, prior_day)
    # prior session = between the close-before-last and the last close (for the prior-day buys table)
    pb_day = _prior_trading_day(panel, prior_day) if prior_day else None
    if prior_day:
        winB_end = datetime.combine(date.fromisoformat(prior_day), time(16, 0), tzinfo=_ET)
        winB_start = (datetime.combine(date.fromisoformat(pb_day), time(16, 0), tzinfo=_ET)
                      if pb_day else winB_end - timedelta(days=1))
        winB_lbl = "the prior session (%s 16:00 ET → %s 16:00 ET)" % (pb_day or "?", prior_day)
    else:
        winB_start, winB_end = win_start - timedelta(days=1), win_start
        winB_lbl = "the prior session"
    snapshots = _load_rank_snapshots()
    sig_cache, trail_cache = {}, {}

    # benchmark rows (QQQ / SPY / equal-weight universe): (label, daily return, since-inception return).
    # Since-inception is the starting-weighted blend across accounts so it tracks the live fleet's timeline.
    upanel = _universe_panel(today, min(incs)) if incs else None
    ok = [data[n] for n in accts if not data[n].get("err")]

    def _blend(fn):
        num = sum(d["start"] * fn(d) for d in ok if fn(d) is not None)
        den = sum(d["start"] for d in ok if fn(d) is not None)
        return (num / den) if den else None
    _uinc = {}

    def _univ_inc(d):
        inc = d.get("inception")
        if inc not in _uinc:
            _uinc[inc] = _avg_ret(upanel, inc)
        return _uinc[inc]
    bench_rows = [
        ("QQQ", dbench.get("QQQ"), _blend(lambda d: (ibench.get(d["name"]) or {}).get("QQQ"))),
        ("SPY", dbench.get("SPY"), _blend(lambda d: (ibench.get(d["name"]) or {}).get("SPY"))),
        ("Universe avg", _avg_ret(upanel, prior_day), _blend(_univ_inc)),
    ]

    out = Path(output) if output else ROOT / "reports" / f"snapshot_{today}.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(out) as pdf:
        _render_summary(pdf, data, accts, today, panel, ibench, dbench, prior_day, bench_rows)
        _render_buys(pdf, data, accts, win_start, win_end, "Buys Today — by account & ticker",
                     "All buys %s, marked to current prices, sorted by unrealized P&L" % win_lbl)
        _render_buys(pdf, data, accts, winB_start, winB_end, "Prior-Day Buys — current P&L",
                     "Buys placed in %s, marked to NOW, sorted by current unrealized P&L" % winB_lbl)
        _render_orders_by_account(pdf, data, accts, today, win_start, win_end, win_lbl)
        _render_orders_today(pdf, data, accts, today, win_start, win_end, win_lbl, snapshots, sig_cache, trail_cache)

    rows = [{"label": n, "error": data[n].get("err")} for n in accts]
    return out, rows


if __name__ == "__main__":
    out, rows = run()
    ok = sum(1 for r in rows if not r.get("error"))
    print("Wrote %s  (%d/%d accounts)" % (out, ok, len(rows)))
