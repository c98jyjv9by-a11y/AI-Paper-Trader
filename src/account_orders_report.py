"""Per-account ORDER HISTORY + P&L report, combined for every broker account into ONE PDF.

For each Alpaca paper account it pulls the LIVE broker state and renders:
  • a P&L summary (equity / cash / starting; total, unrealized, and realized-estimate P&L),
  • the current positions with per-name unrealized P&L,
  • the full order history submitted to Alpaca (time, side, symbol, qty, status, fill price, value),
paginated as needed. A cover page rolls every account's P&L into one table.

P&L sourcing (broker = truth):
  • unrealized $ per position = (current_price - avg_entry) * qty   (% = Alpaca unrealized_plpc),
  • total P&L = equity - starting_value (manifest); realized P&L ≈ total - Σ unrealized
    (exact for a paper account funded once with no deposits/withdrawals).

    python run.py order-history [--accounts a b c] [--status all|closed|open] [--end YYYY-MM-DD] [--out FILE]
"""
import glob
import json
import textwrap
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["text.parse_math"] = False     # treat '$' / '%' literally everywhere (money strings)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from broker_adapter import AlpacaPaper
from eod_accounts import BLURBS, DEFAULT_ACCOUNTS, _blurb, _money, _pct

ROOT = Path(__file__).resolve().parent.parent
GREEN, RED, GREY = "#1a7f37", "#c0392b", "#777"
ORDERS_PER_PAGE = 34          # order rows per page (+ header + TOTAL row); wraps to more pages beyond this


_CT = ZoneInfo("America/Chicago")
_ET = ZoneInfo("America/New_York")
_UTC = ZoneInfo("UTC")


def _ts(s):
    """ISO (UTC) timestamp -> 'MM-DD HH:MM' in Chicago Central time, or '—'."""
    if not s:
        return "—"
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        dt = (dt.replace(tzinfo=_UTC) if dt.tzinfo is None else dt).astimezone(_CT)
        return dt.strftime("%m-%d %H:%M")
    except Exception:
        return s[:16] if len(s) >= 16 else "—"


def _annotate_trade_pnl(orders, price_now=None):
    """Per-order P&L via running AVERAGE-COST accounting (matches Alpaca's avg_entry_price). Walks FILLED
    orders oldest->newest, maintaining {qty, cost} per symbol:
      • a SELL realizes (fill_px - avg_entry) x qty -> `rlz`,
      • a BUY of a STILL-HELD symbol marks to market (current_px - fill_px) x qty -> `unrlz`
        (a BUY of a name no longer held gets no `unrlz` — its outcome shows on the SELL rows).
    `ret` is the single return that pairs with whichever applies (realized return for sells, unrealized
    return for held buys). Annotates each order dict in place with `rlz` / `unrlz` / `ret` (None when N/A).
    `price_now` = {symbol: current price} for currently-held names. Accurate when the full opening history
    is within the pulled window (true for these young books)."""
    price_now = price_now or {}
    books = {}
    for o in orders:
        o["rlz"] = o["unrlz"] = o["ret"] = None
    # Any order with a filled qty + price counts — INCLUDING partial fills that ended 'expired'/'canceled'
    # (filled_qty is the actually-executed share count; realize on that, not on the terminal status).
    fills = [o for o in orders if o.get("fill_price") and o.get("filled_qty")]
    for o in sorted(fills, key=lambda x: (x.get("filled_at") or x.get("submitted_at") or "")):
        sym, q, px = o["symbol"], o["filled_qty"], o["fill_price"]
        b = books.setdefault(sym, {"qty": 0.0, "cost": 0.0})
        if (o.get("side") or "").lower() == "buy":
            b["qty"] += q; b["cost"] += q * px
            cur = price_now.get(sym)
            if cur:                                            # mark the buy to market only if still held
                o["unrlz"] = (cur - px) * q
                o["ret"] = (cur / px - 1) if px > 0 else None
        else:                                                  # sell -> realize vs running average cost
            avg = (b["cost"] / b["qty"]) if b["qty"] > 1e-9 else px
            o["rlz"] = (px - avg) * q
            o["ret"] = (px / avg - 1) if avg > 0 else None
            b["qty"] -= q; b["cost"] -= avg * q
            if b["qty"] <= 1e-9:                               # flat (or rounding) -> reset the book
                b["qty"], b["cost"] = 0.0, 0.0
    return orders


# Overlay sleeves are identified by symbol (excluded from the model decision, managed standalone).
_OVERLAY_REASON = {"TQQQ": ("rebound overlay buy", "rebound 1-day exit"),
                   "SQQQ": ("hedge overlay buy", "hedge exit")}
# Per-strategy (buy_reason, sell_reason) — the RULE that governs that order, by the account's target_mode.
_KIND_REASON = {
    "model_v4":          ("model entry (gate/persist)", "model exit (stop/rotate/hold)"),
    "score_gate_rampup": ("ramp-up buy (score>0.90)",   "model exit (stop/rotate/hold)"),
    "score_rebalance":   ("rebalance add (top-N score)", "rebalance drop (out of book)"),
    "zscore_reversal":   ("z-reversal entry (low-z)",    "z-reversal rebalance / to-cash"),
}


def _reason(side, sym, kind):
    """Brief GOVERNING-RULE label for an order, derived from the account strategy + side + symbol —
    the FALLBACK used for orders placed before per-order decision logging existed. Each book is a
    deterministic rule, so the rule that produced a buy/sell is well-defined. Overlays flagged by symbol."""
    is_buy = (side or "").lower() == "buy"
    if sym in _OVERLAY_REASON:
        return _OVERLAY_REASON[sym][0 if is_buy else 1]
    b, s = _KIND_REASON.get(kind, ("buy", "sell"))
    return b if is_buy else s


def _et_date(s):
    """ET calendar date (YYYY-MM-DD) of an ISO timestamp — matches the broker plan's `asof` (ET)."""
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return (dt.replace(tzinfo=_UTC) if dt.tzinfo is None else dt).astimezone(_ET).strftime("%Y-%m-%d")
    except Exception:
        return None


_PHASE_ORDER = {"open": 0, "intraday": 1, "close": 2}


def _ct_date(s):
    """Chicago (Central) calendar date (YYYY-MM-DD) of an ISO timestamp."""
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return (dt.replace(tzinfo=_UTC) if dt.tzinfo is None else dt).astimezone(_CT).strftime("%Y-%m-%d")
    except Exception:
        return None


def _phase(ts):
    """Classify a submission into a session phase by its CHICAGO (Central) time of day: open (< 9:00 CT =
    < 10:00 ET, incl. the on-open auction + pre-market), close (>= 14:30 CT = >= 15:30 ET, incl. the
    on-close auction + post-market/EOD), else intraday."""
    if not ts:
        return "intraday"
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        dt = (dt.replace(tzinfo=_UTC) if dt.tzinfo is None else dt).astimezone(_CT)
        m = dt.hour * 60 + dt.minute
        return "open" if m < 540 else ("close" if m >= 870 else "intraday")
    except Exception:
        return "intraday"


def _sess(r):
    """Display label for a (date, phase) batch row, e.g. '06-26 close'."""
    ed = r.get("edate") or ""
    return ("%s %s" % (ed[5:], r.get("phase", ""))) if ed else r.get("phase", "")


def _load_rank_snapshots(scenario="model_v4"):
    """Ascending [(date, {ticker: (score, rank)})] from backtests/rankings_<scenario>_<date>.csv — the
    close-based composite score + rank the model recorded each day. Each order is matched to the snapshot
    EFFECTIVE at its submission time (latest snapshot on/before the order's ET submit date), so the score
    shown is the one the batch was actually generated under."""
    import glob, re
    out = []
    for f in sorted(glob.glob(str(ROOT / "backtests" / ("rankings_%s_*.csv" % scenario)))):
        m = re.search(r"_(\d{4}-\d{2}-\d{2})\.csv$", f)
        if not m:
            continue
        try:
            df = pd.read_csv(f)
            tbl = {str(r["ticker"]).strip(): (float(r["score"]), int(r["rank"]))
                   for _, r in df.iterrows() if pd.notna(r.get("score"))}
            out.append((m.group(1), tbl))
        except Exception:
            continue
    return out


def _entry_score(o, snapshots):
    """(score, rank) for an order's symbol from the ranking snapshot effective at its SUBMISSION time —
    the latest snapshot dated on/before the order's ET submit date (carry-forward over gap days). Returns
    (None, None) for overlay/unscored names or when no snapshot covers the date."""
    if not snapshots:
        return None, None
    d = _et_date(o.get("submitted_at") or o.get("filled_at"))
    if not d:
        return None, None
    tbl = None
    for date_str, t in snapshots:                              # ascending -> keep the last on/before d
        if date_str <= d:
            tbl = t
        else:
            break
    return (tbl or {}).get(o.get("symbol", ""), (None, None))


def _asof_signal(d, as_of, cache):
    """{ticker: (value, rank)} for the account's OWN selection metric, recomputed AS-OF `as_of`:
      • zscore_reversal -> the avg-window z-signal, ranked ASCENDING (lowest z = #1, the pick),
      • score_rebalance -> the trailing-lookback avg composite, ranked DESCENDING (highest = #1).
    Deterministic from price history; cached per (kind, params, date) since a whole batch shares a date.
    Heavy (recomputes daily cross-sectional scores) so it's only invoked for these two book types."""
    kind, tm, scen = d.get("kind"), d.get("tm") or {}, d.get("scenario", "model_v4")
    if kind == "zscore_reversal":
        key = ("z", scen, int(tm.get("zscore_lookback", 60)), int(tm.get("avg_window", 10)), as_of)
    elif kind == "score_rebalance":
        key = ("s", scen, int(tm.get("lookback_days", 60)), as_of)
    else:
        return {}
    if key in cache:
        return cache[key]
    out = {}
    try:
        import broker_sync as bs
        import datetime as _dt
        dt = _dt.date.fromisoformat(as_of)
        if kind == "zscore_reversal":
            sig = bs._zscore_reversal_signal(scen, int(tm.get("zscore_lookback", 60)),
                                             int(tm.get("avg_window", 10)), as_of=dt)
            ranked = sorted((t for t in sig if sig[t] == sig[t]), key=lambda t: sig[t])   # asc, NaN-safe
            out = {t: (sig[t], i + 1) for i, t in enumerate(ranked)}
        else:
            avg = bs._lookback_avg_scores(scen, int(tm.get("lookback_days", 60)), as_of=dt)
            ranked = sorted((t for t in avg if avg[t] == avg[t]), key=lambda t: avg[t], reverse=True)
            out = {t: (avg[t], i + 1) for i, t in enumerate(ranked)}
    except Exception:
        out = {}
    cache[key] = out
    return out


def _score_pattern(cur, a5, a20, a60):
    """Classify a score profile (from the 2018-2026 forward-return study, where the 60-DAY-avg dominates):
      Top      — 60d-avg >= .70: SUSTAINED top-ranking, the durable sweet spot (+5.7%/20d excess, t=14.6),
      Emerging — current > .85 with a 60d base >= .55: high now + 60d building (+1.0%/20d, t=5.3),
      Flash    — current > .85 but 60d < .55: a spike with NO 60d base = head-fake (~0 edge, t=0.9),
      Chase    — mid .40-.85 with a RISING current score: chasing late momentum = the trap (-0.3%/20d),
      Reversal — current < .40: beaten-down (z-reversal zone; weak edge),
      Neutral  — the dead middle."""
    if cur is None:
        return "—"
    a60 = a60 if a60 is not None else cur
    if a60 >= 0.70:
        return "Top"
    if cur > 0.85:
        return "Emerging" if a60 >= 0.55 else "Flash"
    if cur < 0.40:
        return "Reversal"
    trend = (a5 if a5 is not None else cur) - (a20 if a20 is not None else cur)
    return "Chase" if trend > 0.05 else "Neutral"


def _trail_avg(scenario, as_of, cache):
    """{ticker: (cur, avg5, avg10, avg20, avg60)} — the 1-DAY (current-close) composite score plus its
    trailing 5/10/20/60-TRADING-DAY averages, ending at `as_of`. Recomputes the daily cross-sectional
    composite (the rankings snapshots are too sparse), then rolls. Cached per (scenario, date)."""
    key = (scenario, as_of)
    if key in cache:
        return cache[key]
    out = {}
    try:
        import datetime as _dt
        from backtest import load_config, fetch_backtest_data
        from scenarios import load_scenario, build_config
        from signals import calculate_signals, rank_candidates
        from rank_report import _build_ticker_weights, _SIGNAL_WINDOW
        cfg = build_config(load_config(ROOT / "config"), load_scenario(scenario))
        uni, w = cfg["tickers"], cfg["signals"].get("weights")
        tw = _build_ticker_weights(cfg) or None
        end = _dt.date.fromisoformat(as_of)
        pdata = fetch_backtest_data(uni, end - _dt.timedelta(days=60 * 2 + 420), end)
        pdata = pdata[pdata.index <= pd.Timestamp(end)]
        rows = [dict(zip(rf["ticker"], rf["composite_score"]))
                for ts in pdata["Close"].index[-60:]
                for rf in [rank_candidates(calculate_signals(pdata.loc[:ts].iloc[-_SIGNAL_WINDOW:], uni),
                                           top_n=len(uni), weights=w, ticker_weights=tw)]]
        sdf = pd.DataFrame(rows)
        cur = sdf.iloc[-1]
        a5, a10, a20, a60 = (sdf.tail(n).mean() for n in (5, 10, 20, 60))
        out = {t: (cur.get(t), a5.get(t), a10.get(t), a20.get(t), a60.get(t)) for t in sdf.columns}
    except Exception:
        out = {}
    cache[key] = out
    return out


def _order_reason(o, kind, dec_log):
    """The REAL logged reason + supporting data for an order (matched by ET date + symbol + side in
    decisions.csv), e.g. 'zscore weekly entry: most-fallen #1 (5d-avg z) · z-1.71'. Falls back to the
    derived rule label when no decision was logged (orders predating the decision-logging feature)."""
    sym, side = o.get("symbol", ""), (o.get("side") or "").lower()
    d = dec_log.get((_et_date(o.get("submitted_at") or o.get("filled_at")), sym, side))
    if not d or not d.get("reason"):
        return _reason(side, sym, kind)
    extra = []
    if d.get("score") is not None:
        extra.append("score %.2f" % float(d["score"]))
    if d.get("z") is not None:
        extra.append("z%+.2f" % float(d["z"]))
    return str(d["reason"]) + ((" · " + " ".join(extra)) if extra else "")


def _collect(name, today, status="all", limit=500):
    """LIVE broker pull for one account: account, positions (+unrealized $), full order history, P&L."""
    try:
        cli = AlpacaPaper(account=name)
        a = cli.account()
        eq, cash = float(a.get("equity") or 0.0), float(a.get("cash") or 0.0)
        pos = cli.positions() or []
        for p in pos:                                          # derive unrealized $ from the broker fields
            p["unrealized_pl"] = (p["price"] - p["avg_entry"]) * p["qty"]
            p["cost_basis"] = p["avg_entry"] * p["qty"]
        orders = _annotate_trade_pnl(cli.orders(status=status, limit=limit) or [],   # newest-first; +per-trade P&L
                                     price_now={p["ticker"]: p["price"] for p in pos})
        man = json.load(open(glob.glob(str(ROOT / "accounts" / name / "*.json"))[0]))
        start = float(man.get("starting_value") or eq)
        unreal = sum(p["unrealized_pl"] for p in pos)
        total = eq - start
        cost = sum(p["cost_basis"] for p in pos)               # open-book return = Σ mkt / Σ cost - 1
        mv = sum(p["market_value"] for p in pos)
        realized = sum(o["rlz"] for o in orders if o.get("rlz") is not None)   # fills-derived (avg-cost),
        return {"name": name, "eq": eq, "cash": cash, "start": start, "pos": pos, "orders": orders,   # same as
                "kind": (man.get("target_mode") or {}).get("kind"), "tm": (man.get("target_mode") or {}),  # order
                "scenario": man.get("scenario", "model_v4"), "inception": man.get("inception"),   # table & summary
                "dec_log": _load_decision_log(name),
                "book_cost": cost, "book_mv": mv, "book_ret": (mv / cost - 1) if cost > 0 else None,
                "unreal": unreal, "total_pnl": total, "realized_est": realized,
                "tot_ret": (eq / start - 1 if start else 0.0), "err": None}
    except Exception as exc:
        return {"name": name, "err": str(exc)[:80]}


def _load_decision_log(name):
    """{(asof, symbol, side): {reason, score, rank, z, pnl}} from accounts/<name>/broker/decisions.csv —
    the REAL reason + supporting data logged when each order was created. {} if the log doesn't exist yet
    (orders placed before decision-logging was added fall back to the derived rule label)."""
    f = ROOT / "accounts" / name / "broker" / "decisions.csv"
    if not f.exists():
        return {}
    try:
        df = pd.read_csv(f)
        out = {}
        for _, r in df.iterrows():
            out[(str(r["asof"]), str(r["symbol"]), str(r["side"]).lower())] = {
                k: (None if pd.isna(r.get(k)) else r.get(k)) for k in ("reason", "score", "rank", "z", "pnl")}
        return out
    except Exception:
        return {}


# ── benchmarks (aligned PER ACCOUNT to its own inception window) ──────────────────
def _bench_panel(today, start):
    """QQQ/SPY close panel from `start` (earliest inception) through `today`. {} on failure."""
    try:
        import datetime as _dt
        from backtest import fetch_backtest_data
        s = _dt.date.fromisoformat(start) - _dt.timedelta(days=10)
        cl = fetch_backtest_data(["QQQ", "SPY"], s, _dt.date.fromisoformat(today))["Close"]
        return cl if hasattr(cl, "columns") else None
    except Exception:
        return None


def _bench(panel, inception, ext=None):
    """{QQQ,SPY} total return from the close ON/BEFORE the account's inception to the latest mark —
    so each account is compared to the benchmark over ITS OWN holding window (timelines aligned).
    When `ext` (extended-hours {SPY,QQQ} prices) is given, the latest endpoint uses that print, so
    an EH-marked book is compared to an EH-marked benchmark (consistent marks)."""
    if panel is None or not inception:
        return {}
    try:
        base = panel.loc[:inception]
        if base.empty:
            return {}
        b0, b1 = base.iloc[-1], panel.iloc[-1]
        ext = ext or {}
        out = {}
        for s in ("QQQ", "SPY"):
            if s not in panel.columns or float(b0[s]) <= 0:
                continue
            end_px = ext.get(s) or float(b1[s])
            out[s] = float(end_px) / float(b0[s]) - 1
        return out
    except Exception:
        return {}


def _remark_prepost(d, ext, label):
    """Re-mark a collected account to the latest EXTENDED-HOURS print (`ext` = {symbol: price}).
    Updates each position's price/MV/unrealized, the book aggregates, the EH-marked equity, and the
    held-BUY order marks. Realized P&L is price-invariant so it's unchanged. Falls back to the close
    for any symbol without an EH bar. Records how many names were EH-marked + the as-of label."""
    if d.get("err"):
        return d
    marked = 0
    for p in d["pos"]:
        px = ext.get(p["ticker"])
        if px and px > 0:
            p["price"] = float(px); marked += 1
        p["cost_basis"] = p["avg_entry"] * p["qty"]
        p["market_value"] = p["price"] * p["qty"]
        p["unrealized_pl"] = (p["price"] - p["avg_entry"]) * p["qty"]
        p["unrealized_plpc"] = (p["price"] / p["avg_entry"] - 1) if p["avg_entry"] else 0.0
    d["unreal"] = sum(p["unrealized_pl"] for p in d["pos"])
    d["book_cost"] = sum(p["cost_basis"] for p in d["pos"])
    d["book_mv"] = sum(p["market_value"] for p in d["pos"])
    d["book_ret"] = (d["book_mv"] / d["book_cost"] - 1) if d["book_cost"] > 0 else None
    d["eq"] = d["cash"] + d["book_mv"]                          # EH-marked equity = cash + EH market value
    d["total_pnl"] = d["eq"] - d["start"]
    d["tot_ret"] = (d["eq"] / d["start"] - 1) if d["start"] else 0.0
    # realized_est is fills-derived (price-invariant) — do NOT recompute from total-unreal here
    _annotate_trade_pnl(d["orders"], price_now={p["ticker"]: p["price"] for p in d["pos"]})
    d["mark_label"], d["marked_ext"] = label, marked
    return d


# ── rendering ───────────────────────────────────────────────────────────────────
def _new_page(pdf, title, sub=None):
    fig = plt.figure(figsize=(11, 8.5))
    fig.suptitle(title, fontsize=13, weight="bold")
    if sub:
        fig.text(0.5, 0.945, sub, ha="center", fontsize=8.5, color="#555")
    return fig


def _table(fig, rect, cols, cells, colw, fontsize=7.5):
    ax = fig.add_axes(rect); ax.axis("off")
    if not cells:
        ax.text(0.0, 0.95, "— none —", fontsize=8, color=GREY, va="top")
        return ax, None
    t = ax.table(cellText=cells, colLabels=cols, colWidths=colw, loc="upper center", cellLoc="center")
    t.auto_set_font_size(False); t.set_fontsize(fontsize); t.scale(1, 1.4)
    for j in range(len(cols)):
        t[0, j].set_facecolor("#34495e"); t[0, j].set_text_props(color="white", weight="bold")
    return ax, t


def _render_account(pdf, d, bench=None, snapshots=None, sig_cache=None, trail_cache=None):
    bench = bench or {}
    snapshots = snapshots or []
    sig_cache = sig_cache if sig_cache is not None else {}
    trail_cache = trail_cache if trail_cache is not None else {}
    name = d["name"]
    label, blurb = _blurb(name)
    title = "%s  —  %s" % (name, label)

    # ── broker error -> a single explanatory page (e.g. placeholder/unset keys) ──
    if d.get("err"):
        fig = _new_page(pdf, title)
        ax = fig.add_axes([0.06, 0.1, 0.88, 0.78]); ax.axis("off")
        ax.text(0.0, 1.0, "Broker unavailable for this account.", fontsize=11, weight="bold",
                color=RED, va="top")
        ax.text(0.0, 0.93, textwrap.fill("Alpaca call failed: %s" % d["err"], 90), fontsize=9,
                color="#333", va="top")
        ax.text(0.0, 0.80, textwrap.fill("This usually means the account's API keys are not set in .env "
                "(several research books ship with placeholder keys). Set real Alpaca paper keys to "
                "populate its order history and P&L.", 95), fontsize=8.5, color=GREY, va="top")
        pdf.savefig(fig); plt.close(fig)
        return

    # ── page 1: P&L summary + positions ──
    fig = _new_page(pdf, title)
    # P&L summary band
    ax = fig.add_axes([0.06, 0.74, 0.88, 0.16]); ax.axis("off")
    pnl_color = GREEN if d["total_pnl"] >= 0 else RED
    line1 = ("Equity %s    Cash %s    Starting %s    Positions %d    Orders %d"
             % (_money(d["eq"]), _money(d["cash"]), _money(d["start"]), len(d["pos"]), len(d["orders"])))
    ax.text(0.0, 1.0, line1, fontsize=9.5, family="monospace", va="top")
    if d.get("mark_label"):
        ax.text(0.0, 0.82, "Marked to extended-hours print (%s) — %d/%d names; rest at close."
                % (d["mark_label"], d.get("marked_ext", 0), len(d["pos"])),
                fontsize=7.5, color="#0b3d91", style="italic", va="top")
    ax.text(0.0, 0.60, "Total P&L  %s (%s)" % (_money(d["total_pnl"]), _pct(d["tot_ret"])),
            fontsize=11, weight="bold", color=pnl_color, va="top")
    ax.text(0.34, 0.60, "Unrealized  %s" % _money(d["unreal"]),
            fontsize=10, color=(GREEN if d["unreal"] >= 0 else RED), va="top")
    ax.text(0.60, 0.60, "Realized  %s" % _money(d["realized_est"]),
            fontsize=10, color=(GREEN if d["realized_est"] >= 0 else RED), va="top")
    # benchmark + open-book return, aligned to THIS account's inception window
    def _bpct(sym):
        v = bench.get(sym)
        return ("%s %s" % (sym, _pct(v))) if v is not None else ("%s —" % sym)
    bookret = (" · Open book %s (cost %s → mkt %s)"
               % (_pct(d["book_ret"]), _money(d["book_cost"]), _money(d["book_mv"]))) if d.get("book_ret") is not None else ""
    ax.text(0.0, 0.34, "Since inception %s:  Total %s   vs   %s   %s%s"
            % (d.get("inception") or "—", _pct(d["tot_ret"]), _bpct("QQQ"), _bpct("SPY"), bookret),
            fontsize=8.5, va="top", color="#333")
    ax.text(0.0, 0.18, textwrap.fill(blurb, 120), fontsize=7.5, color="#444", va="top")

    # positions table — gets the rest of page 1 (holds up to ~24 rows comfortably; combo20 has 20)
    fig.text(0.06, 0.70, "Open positions (%d)" % len(d["pos"]), fontsize=10, weight="bold")
    pcols = ["Symbol", "Qty", "Avg entry", "Price", "Mkt value", "Cost", "Unreal $", "Unreal %"]
    psorted = sorted(d["pos"], key=lambda x: -x["market_value"])
    pcells = [[p["ticker"], "%g" % p["qty"], "$%.2f" % p["avg_entry"], "$%.2f" % p["price"],
               _money(p["market_value"]), _money(p["cost_basis"]), _money(p["unrealized_pl"]),
               _pct(p["unrealized_plpc"])] for p in psorted]
    praw = [10, 7, 10, 9, 11, 10, 10, 9]
    _, pt = _table(fig, [0.06, 0.05, 0.88, 0.62], pcols, pcells, [w / sum(praw) for w in praw])
    if pt is not None:
        for i, p in enumerate(psorted):
            for j in (6, 7):
                pt[i + 1, j].set_text_props(color=(GREEN if p["unrealized_pl"] >= 0 else RED), weight="bold")
    pdf.savefig(fig); plt.close(fig)

    # ── order history — its own page(s), paginated; never shares a page with positions ──
    orders = d["orders"]
    kind = d.get("kind")
    dec_log = d.get("dec_log") or {}
    ocols = ["Filled (CT)", "Side", "Symbol", "FillQty", "Fill px", "Value", "Rlz $", "Unrlz $", "Ret %",
             "Score@sub", "Trail 1/5/10/20/60d", "Pattern", "Status", "Reason"]
    oraw = [10, 4, 6, 5, 7, 7, 7, 7, 6, 8, 16, 9, 7, 11]
    ow = [w / sum(oraw) for w in oraw]
    realized_sum = sum(o["rlz"] for o in orders if o.get("rlz") is not None)
    unrlz_sum = sum(o["unrlz"] for o in orders if o.get("unrlz") is not None)
    value_sum = sum(o["filled_qty"] * o["fill_price"] for o in orders
                    if o.get("fill_price") and o.get("filled_qty"))
    # account-wide TOTAL row (shown atop every page of this history): gross filled value + Σ Rlz/Unrlz
    total_row = ["TOTAL", "", "", "", "", _money(value_sum), _money(realized_sum), _money(unrlz_sum), "", "", "", "", "", ""]

    def _scorecell(o):                                       # the book's OWN selection metric the batch was submitted under
        sym, side = o.get("symbol", ""), (o.get("side") or "").lower()
        dt = _et_date(o.get("submitted_at") or o.get("filled_at"))
        # 1) exact, from the decision log (going forward): z for zscore books, score otherwise
        dl = dec_log.get((dt, sym, side))
        if dl:
            rk = (" #%d" % int(dl["rank"])) if dl.get("rank") is not None else ""
            if dl.get("z") is not None and dl["z"] == dl["z"]:
                return "z%+.2f%s" % (float(dl["z"]), rk)
            if dl.get("score") is not None and dl["score"] == dl["score"]:
                return "%.2f%s" % (float(dl["score"]), rk)
        # 2) recompute the book's own metric as-of the submission date (zscore / score_rebalance)
        if kind in ("zscore_reversal", "score_rebalance") and dt:
            v, rk = _asof_signal(d, dt, sig_cache).get(sym, (None, None))
            if v is not None:
                return ("z%+.2f #%d" % (v, rk)) if kind == "zscore_reversal" else ("%.2f #%d" % (v, rk))
            return "—"                                       # don't fall back to composite (wrong metric)
        # 3) model_v4 / ramp-up / seed books -> composite score #rank from the daily snapshot
        sc, rk = _entry_score(o, snapshots)
        if sc is None:
            return "—"
        return ("%.2f #%d" % (sc, rk)) if rk else ("%.2f" % sc)

    def _trail(o):                                          # (cur, a5, a10, a20) composite scores at order date
        dt = _et_date(o.get("submitted_at") or o.get("filled_at"))
        return _trail_avg(d.get("scenario", "model_v4"), dt, trail_cache).get(o.get("symbol", "")) if dt else None

    def _trailcell(o):                                      # 1/5/10/20-day trailing close composite scores
        a = _trail(o)
        if not a or a[0] is None:
            return "—"
        return "/".join(("%.2f" % v).lstrip("0") if v is not None else "—" for v in a)   # e.g. .81/.80/.86/.76

    def _patterncell(o):                                    # pattern category from score level + trend + 60d base
        a = _trail(o)
        return _score_pattern(a[0], a[1], a[3], a[4]) if a else "—"

    def _orow(o):
        fp = o.get("fill_price")
        val = (o["filled_qty"] * fp) if (fp and o["filled_qty"]) else None
        rlz, unrlz, ret = o.get("rlz"), o.get("unrlz"), o.get("ret")
        return [_ts(o.get("filled_at") or o.get("submitted_at")), (o.get("side") or "").upper(),
                o.get("symbol", ""), "%g" % o["filled_qty"], ("$%.2f" % fp) if fp else "—",
                _money(val) if val is not None else "—",
                _money(rlz) if rlz is not None else "—",
                _money(unrlz) if unrlz is not None else "—",
                _pct(ret) if ret is not None else "—",
                _scorecell(o), _trailcell(o), _patterncell(o), o.get("status", ""), _order_reason(o, kind, dec_log)]

    def _color_orders(tbl, chunk, offset):                   # `offset` = table row of the first order
        # style the TOTAL header-data row (always at table row 1) once
        for j in range(len(ocols)):
            tbl[1, j].set_facecolor("#dfe6e9"); tbl[1, j].set_text_props(weight="bold")
        tbl[1, 6].set_text_props(color=(GREEN if realized_sum >= 0 else RED), weight="bold")
        tbl[1, 7].set_text_props(color=(GREEN if unrlz_sum >= 0 else RED), weight="bold")
        for i, o in enumerate(chunk):
            r = i + offset
            side = (o.get("side") or "").upper()
            tbl[r, 1].set_text_props(color=(GREEN if side == "BUY" else RED), weight="bold")
            if o.get("rlz") is not None:                       # realized SELL
                tbl[r, 6].set_text_props(color=(GREEN if o["rlz"] >= 0 else RED), weight="bold")
            if o.get("unrlz") is not None:                     # mark-to-market of a held BUY
                tbl[r, 7].set_text_props(color=(GREEN if o["unrlz"] >= 0 else RED), weight="bold")
            if o.get("ret") is not None:
                tbl[r, 8].set_text_props(color=(GREEN if o["ret"] >= 0 else RED), weight="bold")
            tbl[r, 10].set_text_props(color="#555")            # trailing avgs (muted)
            pat = _patterncell(o)                              # color the pattern by the study's read
            tbl[r, 11].set_text_props(weight="bold", color=(GREEN if pat in ("Top", "Emerging")
                                      else RED if pat in ("Chase", "Flash") else "#555"))
            if o.get("status") != "filled":
                tbl[r, 12].set_text_props(color=GREY, style="italic")
            tbl[r, 13].set_text_props(color="#555", style="italic")

    rest, page, npages = orders, 1, max(1, (len(orders) + ORDERS_PER_PAGE - 1) // ORDERS_PER_PAGE)
    while rest or page == 1:                                  # always emit at least one (possibly empty) page
        chunk, rest = rest[:ORDERS_PER_PAGE], rest[ORDERS_PER_PAGE:]
        sub = "order history (newest first)" + ("" if npages == 1 else " — page %d/%d" % (page, npages))
        fig = _new_page(pdf, title, sub=sub)
        cells = ([total_row] + [_orow(o) for o in chunk]) if orders else []   # TOTAL row pinned at the top
        _, ot = _table(fig, [0.02, 0.05, 0.96, 0.84], ocols, cells, ow, fontsize=5.5)
        if ot is not None:
            _color_orders(ot, chunk, offset=2)               # order rows start after header(0)+TOTAL(1)
        fig.text(0.02, 0.93, "Score@sub = the book's OWN selection metric #rank as-of the order's date (zscore: z, "
                 "lowest=#1; score-rebalance: 60d-avg score; model_v4: composite).  Trail 1/5/10/20/60d = the 1-day "
                 "(current) close composite score + its trailing 5/10/20/60-day averages (0.xx shown as .xx).",
                 fontsize=6.3, color="#555")
        fig.text(0.02, 0.915, "Pattern (2018-26 fwd-return study; the 60d-avg dominates): Top (60d>=.70 sustained "
                 "leader = sweet spot, green) · Emerging (cur>.85 + 60d>=.55, green) · Flash (cur>.85 but 60d<.55 = "
                 "head-fake, red) · Chase (mid + rising = trap, red) · Reversal (<.40) · Neutral.  Times in CT.",
                 fontsize=6.3, color="#555")
        pdf.savefig(fig); plt.close(fig)
        if not rest:
            break
        page += 1


def _render_cover(pdf, data, accts, today, bench, mark_note=None):
    fig = plt.figure(figsize=(11, 8.5))
    fig.suptitle("Account Order History & P&L — all accounts   %s" % today, fontsize=14, weight="bold")
    if mark_note:
        fig.text(0.5, 0.945, mark_note, ha="center", fontsize=8, color="#0b3d91", style="italic")
    ax = fig.add_axes([0.03, 0.30, 0.94, 0.55]); ax.axis("off")
    cols = ["Account", "Equity", "Cash", "Starting", "Total P&L", "Total %", "QQQ %", "SPY %",
            "Unreal $", "Realized", "Pos", "Orders"]

    def _bp(n, sym):                                          # account-aligned benchmark % (or "—")
        v = (bench.get(n) or {}).get(sym)
        return _pct(v) if v is not None else "—"
    cells, ok = [], []
    for n in accts:
        d = data[n]
        if d.get("err"):
            cells.append([n, "—", "—", "—", "ERR", "—", "—", "—", "—", "—", "—", "—"])
            continue
        ok.append(d)
        cells.append([n, _money(d["eq"]), _money(d["cash"]), _money(d["start"]), _money(d["total_pnl"]),
                      _pct(d["tot_ret"]), _bp(n, "QQQ"), _bp(n, "SPY"), _money(d["unreal"]),
                      _money(d["realized_est"]), str(len(d["pos"])), str(len(d["orders"]))])
    if ok:
        agg = {k: sum(d[k] for d in ok) for k in ("eq", "cash", "start", "total_pnl", "unreal", "realized_est")}
        # blended benchmark = starting-value-weighted mean of each account's inception-aligned return
        def _blend(sym):
            num = sum(d["start"] * bench[d["name"]][sym] for d in ok
                      if bench.get(d["name"], {}).get(sym) is not None)
            den = sum(d["start"] for d in ok if bench.get(d["name"], {}).get(sym) is not None)
            return _pct(num / den) if den else "—"
        cells.append(["TOTAL", _money(agg["eq"]), _money(agg["cash"]), _money(agg["start"]),
                      _money(agg["total_pnl"]), _pct(agg["eq"] / agg["start"] - 1 if agg["start"] else 0.0),
                      _blend("QQQ"), _blend("SPY"), _money(agg["unreal"]), _money(agg["realized_est"]),
                      str(sum(len(d["pos"]) for d in ok)), str(sum(len(d["orders"]) for d in ok))])
    raw = [15, 10, 9, 9, 10, 7, 7, 7, 9, 11, 5, 7]
    t = ax.table(cellText=cells, colLabels=cols, colWidths=[w / sum(raw) for w in raw],
                 loc="upper center", cellLoc="center")
    t.auto_set_font_size(False); t.set_fontsize(7.5); t.scale(1, 1.5)
    for j in range(len(cols)):
        t[0, j].set_facecolor("#34495e"); t[0, j].set_text_props(color="white", weight="bold")
    for i, n in enumerate(accts):
        d = data[n]
        if d.get("err"):
            t[i + 1, 4].set_text_props(color=RED, weight="bold")
            continue
        for j, v in [(4, d["total_pnl"]), (5, d["tot_ret"]), (8, d["unreal"]), (9, d["realized_est"])]:
            t[i + 1, j].set_text_props(color=(GREEN if v >= 0 else RED), weight="bold")
        for j, sym in [(6, "QQQ"), (7, "SPY")]:               # color benchmark cells too
            bv = (bench.get(n) or {}).get(sym)
            if bv is not None:
                t[i + 1, j].set_text_props(color=(GREEN if bv >= 0 else RED))
    if ok:                                                    # shade + bold the TOTAL row
        tr = len(accts) + 1
        for j in range(len(cols)):
            t[tr, j].set_facecolor("#dfe6e9"); t[tr, j].set_text_props(weight="bold")
    fig.text(0.03, 0.24, "Total P&L = equity - starting (broker).  Unrealized = Σ (price - avg entry) x qty over open "
             "positions (broker).  Realized = Σ realized P&L on sells (fills, avg-cost) — the SAME figure shown by the "
             "order-history TOTAL and the Trade Summary (Total may differ from Realized+Unrealized by a small "
             "broker-vs-fills residual).", fontsize=7.5, color="#555", wrap=True)
    fig.text(0.03, 0.205, "QQQ %% / SPY %% = benchmark total return measured over EACH account's own inception->today "
             "window (timelines aligned per account; TOTAL = starting-weighted blend).", fontsize=7.5, color="#555")
    fig.text(0.03, 0.17, "ERR rows = the account's Alpaca keys are unset/placeholder; see its page for detail.",
             fontsize=7.5, color="#555")
    pdf.savefig(fig); plt.close(fig)


def _buy_pnl(orders, price_now, pos_unreal=None):
    """Per-BUY-entry P&L, CONSISTENT with the order-history table / cover (which use AVERAGE-COST and the
    broker's positions). Each sale's realized P&L uses the AVERAGE-COST magnitude (sell_px - running avg) x
    qty — identical to the order table — and FIFO lot consumption is used only to decide WHICH buy batch it
    is credited back to. Unrealized is the broker's actual per-position P&L (`pos_unreal`, avg-cost),
    distributed across the still-open lots by quantity. So the trade-summary totals reconcile exactly with
    the cover and order-history table (realized + unrealized + grand total all match). Returns
    {buy_oid: {edate, phase, notional, realized, unrealized}}; SELLS are not entries."""
    import collections
    fills = [o for o in orders if o.get("fill_price") and o.get("filled_qty")]
    fills.sort(key=lambda o: (o.get("filled_at") or o.get("submitted_at") or ""))
    books = collections.defaultdict(lambda: {"qty": 0.0, "cost": 0.0, "lots": collections.deque()})
    res, seq = {}, 0
    for o in fills:
        sym, q, px = o["symbol"], o["filled_qty"], o["fill_price"]
        b = books[sym]
        if (o.get("side") or "").lower() == "buy":
            src = o.get("submitted_at") or o.get("filled_at") or ""
            oid = "%s#%d" % (o.get("id") or "b", seq); seq += 1
            res[oid] = {"edate": _ct_date(src) or "", "phase": _phase(src),
                        "notional": q * px, "realized": 0.0, "unrealized": 0.0}
            b["qty"] += q; b["cost"] += q * px
            b["lots"].append([oid, q])
        else:                                                          # sell: avg-cost magnitude, FIFO attribution
            avg = (b["cost"] / b["qty"]) if b["qty"] > 1e-9 else px
            sq = q
            while sq > 1e-9 and b["lots"]:
                lot = b["lots"][0]
                take = min(lot[1], sq)
                res[lot[0]]["realized"] += (px - avg) * take          # avg-cost $, credited to this buy batch
                lot[1] -= take; sq -= take
                if lot[1] <= 1e-9:
                    b["lots"].popleft()
            b["qty"] -= q; b["cost"] -= avg * q
            if b["qty"] <= 1e-9:
                b["qty"], b["cost"] = 0.0, 0.0
    pos_unreal = pos_unreal or {}
    for sym, b in books.items():                                       # unrealized -> broker per-position P&L
        leftover = sum(l[1] for l in b["lots"])
        if leftover <= 1e-9:
            continue
        bu = pos_unreal.get(sym)
        if bu is None:                                                 # fallback: mark at current price vs avg cost
            cur = price_now.get(sym); avg = (b["cost"] / b["qty"]) if b["qty"] > 1e-9 else None
            bu = (cur - avg) * leftover if (cur and avg) else 0.0
        for oid, lq in b["lots"]:
            res[oid]["unrealized"] += bu * (lq / leftover)             # distribute across open lots by qty
    return res


def _agg_buys(rows):
    """Aggregate BUY entries (sells excluded): #entries, hit rate, invested (notional), realized $ (FIFO-
    attributed back to these buys), unrealized $, avg winner/loser. Per-entry P&L = realized + unrealized."""
    pnls = [r["realized"] + r["unrealized"] for r in rows]
    wins, losses = [p for p in pnls if p > 0], [p for p in pnls if p < 0]
    return {"n": len(rows), "invested": sum(r["notional"] for r in rows),
            "realized": sum(r["realized"] for r in rows), "unreal": sum(r["unrealized"] for r in rows),
            "hit": (len(wins) / len(pnls)) if pnls else None,
            "avgwin": (sum(wins) / len(wins)) if wins else None,
            "avglose": (sum(losses) / len(losses)) if losses else None}


def _batch_summaries(data, accts):
    """BUY entries summarized two ways, BOTH ascending (oldest->newest); realized P&L is credited to the
    originating buy batch (FIFO) and sells are excluded from the stats:
      • acct_rows  — one row per (account, buy-batch minute),
      • ts_rows    — one row per buy-batch minute ACROSS portfolios, with the #portfolios it spanned.
    Plus a grand TOTAL."""
    buyrows = []
    for n in accts:
        d = data[n]
        if d.get("err"):
            continue
        price_now = {p["ticker"]: p["price"] for p in d["pos"]}
        pos_unreal = {p["ticker"]: p["unrealized_pl"] for p in d["pos"]}   # broker avg-cost P&L (the cover's)
        for v in _buy_pnl(d["orders"], price_now, pos_unreal).values():
            buyrows.append({"account": n, **v})
    g_acct, g_ts = {}, {}
    for r in buyrows:
        g_acct.setdefault((r["account"], r["edate"], r["phase"]), []).append(r)
        tk = (r["edate"], r["phase"])
        g_ts.setdefault(tk, {"rows": [], "ports": set()})
        g_ts[tk]["rows"].append(r); g_ts[tk]["ports"].add(r["account"])
    acct_rows = [{"account": n, "edate": ed, "phase": ph, **_agg_buys(rs)}
                 for (n, ed, ph), rs in g_acct.items()]
    acct_rows.sort(key=lambda r: (r["edate"], _PHASE_ORDER.get(r["phase"], 1), r["account"]))   # ascending
    ts_rows = [{"edate": ed, "phase": ph, "nport": len(v["ports"]), **_agg_buys(v["rows"])}
               for (ed, ph), v in g_ts.items()]
    ts_rows.sort(key=lambda r: (r["edate"], _PHASE_ORDER.get(r["phase"], 1)))                   # ascending
    total = {**_agg_buys(buyrows), "nport": len({r["account"] for r in buyrows})} if buyrows else None
    return acct_rows, ts_rows, total


_SUM_FOOT = ("One row per BUY batch grouped by day + session phase (CT): open <9:00, intraday, close >=14:30, "
             "oldest->newest.  Sells excluded from the stats; each sale's realized P&L is credited back to the "
             "buy phase it came from (FIFO).  #Buys = entries.  Entry P&L = realized (shares since sold) + "
             "unrealized (still held).  Hit% = entries with P&L>0.  Invested = buy notional.  AvgWin/AvgLose = "
             "mean entry P&L.  Rows shaded green/red: GOOD = hit>=50% AND avg win > avg loss; BAD = neither.")
# very light, nonchalant row tints by batch rating
_RATE_TINT = {"good": "#eef6ee", "bad": "#f8efef", "neutral": None}


def _rate(r):
    """Batch rating: GOOD if hit>=50% AND avg winner beats avg loser (magnitude); BAD if neither; else
    NEUTRAL. None hit (no P&L'd trades) -> neutral."""
    hit = r.get("hit")
    if hit is None:
        return "neutral"
    aw, al = r.get("avgwin"), r.get("avglose")
    c1 = hit >= 0.5
    c2 = (aw is not None) and (aw > (abs(al) if al is not None else 0.0))
    return "good" if (c1 and c2) else ("neutral" if (c1 or c2) else "bad")


def _render_summary_table(pdf, title, today, cols, raw, rows, total, cells_fn, per=20):
    """Paginated metric table (money cols 5..8 colored by sign; shaded TOTAL on the last page)."""
    chunks = [rows[i:i + per] for i in range(0, max(len(rows), 1), per)] or [[]]
    for pi, chunk in enumerate(chunks):
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle(title + ("   %s" % today) + ("" if len(chunks) == 1 else "  (%d/%d)" % (pi + 1, len(chunks))),
                     fontsize=13, weight="bold")
        ax = fig.add_axes([0.04, 0.07, 0.92, 0.83]); ax.axis("off")
        body = [cells_fn(r, False) for r in chunk]
        last = pi == len(chunks) - 1
        if last and total:
            body.append(cells_fn(total, True))
        t = ax.table(cellText=body or [["—"] * len(cols)], colLabels=cols,
                     colWidths=[w / sum(raw) for w in raw], loc="upper center", cellLoc="center")
        t.auto_set_font_size(False); t.set_fontsize(8); t.scale(1, 1.4)
        for j in range(len(cols)):
            t[0, j].set_facecolor("#34495e"); t[0, j].set_text_props(color="white", weight="bold")
        money = [(4, "realized"), (5, "unreal"), (6, "avgwin"), (7, "avglose")]
        for i, r in enumerate(chunk):
            tint = _RATE_TINT.get(_rate(r))                          # nonchalant good/bad row shade
            if tint:
                for j in range(len(cols)):
                    t[i + 1, j].set_facecolor(tint)
            for j, key in money:
                v = r.get(key)
                if v is not None:
                    t[i + 1, j].set_text_props(color=(GREEN if v >= 0 else RED), weight="bold")
        if last and total:
            tr = len(chunk) + 1
            for j in range(len(cols)):
                t[tr, j].set_facecolor("#dfe6e9"); t[tr, j].set_text_props(weight="bold")
            for j, key in money:
                v = total.get(key)
                if v is not None:
                    t[tr, j].set_text_props(color=(GREEN if v >= 0 else RED), weight="bold")
        fig.text(0.04, 0.035, _SUM_FOOT, fontsize=7, color="#555")
        pdf.savefig(fig); plt.close(fig)


def _render_batch_summary(pdf, data, accts, today):
    acct_rows, ts_rows, total = _batch_summaries(data, accts)

    def _hit(r):
        return ("%.0f%%" % (r["hit"] * 100)) if r["hit"] is not None else "—"

    def _m(r, k):
        return _money(r[k]) if r.get(k) is not None else "—"

    # Table 1: ACROSS session phases (all portfolios), with the #portfolios each phase spanned
    tcols = ["Session (CT)", "#Port", "#Buys", "Invested", "Realized", "Unreal", "AvgWin", "AvgLose", "Hit%"]
    traw = [13, 6, 5, 11, 10, 10, 9, 9, 6]

    def _tcells(r, is_total):
        return [("TOTAL" if is_total else _sess(r)), str(r.get("nport", "")), str(r["n"]),
                _m(r, "invested"), _m(r, "realized"), _m(r, "unreal"), _m(r, "avgwin"), _m(r, "avglose"), _hit(r)]
    _render_summary_table(pdf, "Trade Summary — by session phase (all portfolios)", today,
                          tcols, traw, ts_rows, total, _tcells)

    # Table 2: per ACCOUNT & session phase
    acols = ["Account", "Session (CT)", "#Buys", "Invested", "Realized", "Unreal", "AvgWin", "AvgLose", "Hit%"]
    araw = [16, 12, 5, 11, 10, 10, 9, 9, 6]

    def _acells(r, is_total):
        return [("TOTAL" if is_total else r["account"]), ("" if is_total else _sess(r)), str(r["n"]),
                _m(r, "invested"), _m(r, "realized"), _m(r, "unreal"), _m(r, "avgwin"), _m(r, "avglose"), _hit(r)]
    _render_summary_table(pdf, "Trade Summary — by account & session phase", today,
                          acols, araw, acct_rows, total, _acells)


def run(accounts=None, end=None, out=None, status="all", limit=500, prepost=False):
    today = end or date.today().isoformat()
    accts = accounts or DEFAULT_ACCOUNTS
    data = {n: _collect(n, today, status=status, limit=limit) for n in accts}

    # Extended-hours marking: re-mark held positions (and the QQQ/SPY benchmark endpoint) to the
    # latest pre/post-market print so the report reflects the freshest price after the close.
    ext = {}
    mark_note = None
    if prepost:
        from rank_report import extended_hours_prices
        syms = sorted({p["ticker"] for n in accts if not data[n].get("err") for p in data[n]["pos"]}
                      | {"SPY", "QQQ"})
        ext, label, _ = extended_hours_prices(syms)
        if ext:
            for n in accts:
                _remark_prepost(data[n], ext, label)
            mark_note = "Marked to latest extended-hours print (%s); names without an AH bar stay at the close." % label
        else:
            mark_note = "Extended-hours marking requested but no pre/post-market bars were available — showing the close."

    # QQQ/SPY benchmark return aligned to EACH account's own inception window (timelines per account)
    incs = [data[n]["inception"] for n in accts if not data[n].get("err") and data[n].get("inception")]
    panel = _bench_panel(today, min(incs)) if incs else None
    bench = {n: _bench(panel, data[n].get("inception"), ext) for n in accts if not data[n].get("err")}
    snapshots = _load_rank_snapshots()                         # close-based composite score+rank per day
    sig_cache, trail_cache = {}, {}                            # memoize as-of z/avg-score and trailing-avg recomputes
    out = Path(out) if out else ROOT / "reports" / f"account_orders_{today}.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(out) as pdf:
        _render_cover(pdf, data, accts, today, bench, mark_note)
        _render_batch_summary(pdf, data, accts, today)         # page 2: submissions by batch & account
        for n in accts:
            _render_account(pdf, data[n], bench.get(n, {}), snapshots, sig_cache, trail_cache)
    return {"pdf": str(out), "data": data}


if __name__ == "__main__":
    print(run()["pdf"])
