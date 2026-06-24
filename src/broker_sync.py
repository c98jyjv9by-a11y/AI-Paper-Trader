"""
broker_sync.py — reconciliation, realized-slippage logging, broker→ledger sync, and the
daily session orchestrator that sits on top of broker_adapter (Alpaca paper).

This is the layer that replaces *assumed* fills with the broker's *actual* fills:
  • submit_session()    — build the day's queue, save the decision reference prices, and
                          (optionally, guarded) submit the orders to the paper account.
  • reconcile_session() — pull the broker's actual fills + positions, compute realized
                          slippage vs the saved references, log it, and rewrite the
                          account ledger from the broker (broker = source of truth).
  • slippage_summary()  — aggregate the fills log vs the model's assumed cost.

Pure cores (compute_slippage / ledger_from_broker) are unit-testable without a broker.
Broker calls go through broker_adapter, which is paper-only and submit-guarded.

CLI:
    python src/broker_sync.py --submit-plan --account tracker [--submit]
    python src/broker_sync.py --reconcile  --account tracker
    python src/broker_sync.py --slippage   --account tracker
"""
from __future__ import annotations

import json
import argparse
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

ROOT = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(ROOT / "src"))
import broker_adapter as ba
from account import _append_csv, _sha256, _manifest_path, load_manifest, load_ledger, _acct_dir
ASSUMED_COST_BPS = 10.0    # the flat round-trip cost the backtest assumes (for comparison)
HEDGE_SYM = "SQQQ"         # the default hedge instrument (-3x inverse QQQ; long only, never shorted)
REBOUND_SYM = "TQQQ"       # the 1-day rebound overlay instrument (+3x QQQ); managed by rebound_overlay,
                           # excluded from the model decision and added to the target only when it fires
COLLAR_CACHE = ROOT / "backtests" / "collars.csv"


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _broker_dir(name: str) -> Path:
    d = _acct_dir(name) / "broker"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ── pure cores (unit-testable, no broker) ──────────────────────────────────────────
def compute_slippage(fills: List[Dict[str, Any]], refs: Dict[str, float]) -> pd.DataFrame:
    """Realized slippage per fill vs its decision reference price.
    fills: [{client_order_id, symbol, side, filled_qty, fill_price}]; refs: {client_order_id: ref_mid}.
    slippage_bps > 0 means WORSE than the reference (paid up on a buy / sold low on a sell)."""
    rows = []
    for f in fills:
        ref = refs.get(f.get("client_order_id"))
        fp, qty = f.get("fill_price"), f.get("filled_qty") or 0
        if not (ref and fp and qty):
            continue
        sign = 1.0 if f["side"].lower() == "buy" else -1.0
        bps = sign * (fp - ref) / ref * 1e4
        rows.append({"client_order_id": f["client_order_id"], "symbol": f["symbol"],
                     "side": f["side"], "qty": qty, "ref_price": round(ref, 4),
                     "fill_price": round(fp, 4), "slippage_bps": round(bps, 2),
                     "slippage_$": round(sign * (fp - ref) * qty, 2),
                     "filled_at": f.get("filled_at")})
    return pd.DataFrame(rows)


def ledger_from_broker(positions: List[Dict[str, Any]], cash: float, equity: float, asof: str,
                       prior_entry_dates: Optional[Dict[str, str]] = None) -> Dict[str, pd.DataFrame]:
    """Build continuation positions + an equity row from a broker snapshot (broker = truth)."""
    ped = prior_entry_dates or {}
    _pcols = ["ticker", "shares", "entry_price", "entry_date", "current_price",
              "highest_price", "lowest_price"]
    pos = pd.DataFrame([{
        "ticker": p["ticker"], "shares": p["qty"], "entry_price": p["avg_entry"],
        "entry_date": ped.get(p["ticker"], asof), "current_price": p["price"],
        "highest_price": p["price"], "lowest_price": p["price"]} for p in positions],
        columns=_pcols)   # keep the header even when the broker book is empty (fresh account)
    open_val = float(sum(p["market_value"] for p in positions))
    eq = pd.DataFrame([{"date": asof, "cash": cash, "open_positions_value": open_val,
                        "total_portfolio_value": equity, "realized_pnl_to_date": 0.0,
                        "unrealized_pnl": 0.0, "daily_return": "", "cumulative_return": "",
                        "spy_cumulative_return": 0.0, "qqq_cumulative_return": 0.0,
                        "equal_weight_cumulative_return": 0.0, "forecast_vol": "", "exposure_mult": 1.0}])
    return {"positions": pos, "equity": eq}


# ── data-driven execution collars (per-instrument limit tolerance) ──────────────────
def collars_from_gaps(gaps: Dict[str, "pd.Series"], p_base: float = 0.85, p_retry: float = 0.95,
                      floor: float = 0.0015, cap: float = 0.20) -> Dict[str, Dict[str, float]]:
    """PURE. Map {symbol: overnight-gap series (open/prevclose-1)} -> per-symbol collars.
      collar = clamp(P85(|gap|), floor, cap)   retry = clamp(P95(|gap|), floor, cap)
    A buy-limit at ref*(1+collar) fills on ~85% of normal opens and deliberately skips the worst
    ~15% (the adverse gaps we don't want to chase). `floor` covers the bid-ask on calm names."""
    out: Dict[str, Dict[str, float]] = {}
    for s, g in gaps.items():
        if getattr(g, "ndim", 1) > 1:         # yfinance returned duplicate columns for this symbol
            g = g.iloc[:, 0]
        g = g.dropna().abs()
        if len(g) < 50:                       # not enough history -> safe default
            out[s] = {"collar": 0.02, "retry": 0.04, "n": int(len(g)), "src": "default"}
            continue
        out[s] = {"collar": round(float(min(max(g.quantile(p_base), floor), cap)), 4),
                  "retry": round(float(min(max(g.quantile(p_retry), floor), cap)), 4),
                  "n": int(len(g)), "src": "data"}
    return out


def compute_collars(symbols: List[str], cache_day: Optional[str] = None) -> Dict[str, Dict[str, float]]:
    """Fetch ~2y of opens/closes, derive per-symbol collars, and cache to backtests/collars.csv.
    Re-uses today's cache if present (one refresh per day) so submit/retry stay consistent."""
    symbols = sorted(set(symbols))
    if not symbols:
        return {}
    today = cache_day or _utcnow()[:10]
    if COLLAR_CACHE.exists():                 # same-day cache hit (covering all requested syms)
        c = pd.read_csv(COLLAR_CACHE)
        if str(c.get("asof", pd.Series([""])).iloc[0]) == today and set(symbols) <= set(c["symbol"]):
            c = c[c["symbol"].isin(symbols)].set_index("symbol")
            return {s: {"collar": float(r["collar"]), "retry": float(r["retry"]),
                        "n": int(r["n"]), "src": r["src"]} for s, r in c.iterrows()}
    import yfinance as yf
    px = yf.download(symbols, period="2y", auto_adjust=True, progress=False)
    op, cl = px["Open"], px["Close"]
    gaps = {s: (op[s] / cl[s].shift(1) - 1) for s in symbols
            if isinstance(op, pd.DataFrame) and s in op.columns}
    if len(symbols) == 1 and not isinstance(op, pd.DataFrame):  # old yfinance: flat frame for one symbol
        gaps = {symbols[0]: (op / cl.shift(1) - 1)}
    cols = collars_from_gaps(gaps)
    df = pd.DataFrame([{"asof": today, "symbol": s, **v} for s, v in cols.items()])
    COLLAR_CACHE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(COLLAR_CACHE, index=False)
    return cols


def submit_window(clk: Dict[str, Any], prequeue: bool = False, far_hours: float = 20.0) -> Dict[str, Any]:
    """Decide whether it's a sensible moment to SEND the day's first-attempt reconcile orders.
    Pure & testable. Returns {ok, reason}. The first attempt is LIMIT-ON-OPEN/CLOSE (opg/cls),
    which targets the next auction, so the clean window is "market closed and the next open is on
    the SAME ET calendar day" (the pre-open window). Blocks when the market is OPEN (on-open/close
    orders belong to the auctions; intraday top-ups go through the retry path's day orders) and
    when today is NOT a trading day (weekend/holiday — an on-open order *may* not survive until the
    next session). Both blocks are overridable with prequeue (e.g. deliberate weekend pre-staging)."""
    from datetime import datetime as _dt
    try:
        now = _dt.fromisoformat(clk["timestamp"]); nopen = _dt.fromisoformat(clk["next_open"])
        hrs = (nopen - now).total_seconds() / 3600.0
        same_session_day = now.date() == nopen.date()
    except Exception:
        hrs, same_session_day = None, True   # can't parse clock -> don't hard-block on the date check
    if clk.get("is_open"):
        return {"ok": bool(prequeue), "reason": "market is OPEN — on-open/close orders are for the "
                "auctions; submit pre-open, or use the retry path for intraday day orders "
                "(or --prequeue to send anyway)."}
    if not same_session_day or (hrs is not None and hrs > far_hours):
        return {"ok": bool(prequeue), "reason": "next open is %s (~%s away) — today is NOT a trading "
                "session, so an on-open order may not survive until then; submit during the pre-open "
                "window on a trading day, or use --prequeue to pre-stage for the next open deliberately."
                % (clk.get("next_open"), "%.0fh" % hrs if hrs is not None else "?")}
    return {"ok": True, "reason": "market closed, today's open imminent — valid pre-open window."}


# ── target book (reconcile-to-target) ───────────────────────────────────────────────
def topn_targets(intended: List[Dict[str, Any]], equity: float, current: Dict[str, float],
                 size_pct: float) -> "tuple[Dict[str,int], Dict[str,float]]":
    """PURE. Top-N intended names -> TARGET book {symbol: shares}, each sized at `size_pct` of live
    `equity` (whole shares via its latest mark). ACCUMULATE: never trims a held name below its
    current shares (lets winners run); a held name absent from `intended` (fell out of the top N)
    is simply not in the target, so reconcile sells it to 0. `intended`: [{ticker, price}]."""
    targets: Dict[str, int] = {}
    refs: Dict[str, float] = {}
    for it in intended:
        sym, px = it["ticker"], it.get("price")
        if not px or float(px) <= 0:
            continue
        refs[sym] = float(px)
        want = int(equity * size_pct / float(px))
        targets[sym] = max(int(round(current.get(sym, 0))), want)
    return targets, refs


def equal_weight_targets(prices: Dict[str, float], equity: float, current: Dict[str, float],
                         gross: float = 1.0) -> "tuple[Dict[str,int], Dict[str,float]]":
    """PURE. Equal-weight a fixed set of names: each gets gross/N of live `equity` (whole shares
    via its latest mark). ACCUMULATE: never trims a held name below its current shares; a name
    absent from `prices` (dropped from the source book) is left out, so reconcile sells it to 0.
    `prices`: {ticker: mark}."""
    names = [s for s, p in prices.items() if p and float(p) > 0]
    n = len(names)
    targets: Dict[str, int] = {}
    refs: Dict[str, float] = {}
    if not n:
        return targets, refs
    per = (equity * gross) / n
    for s in names:
        p = float(prices[s])
        refs[s] = p
        targets[s] = max(int(round(current.get(s, 0))), int(per / p))
    return targets, refs


def _source_book_names(source: str) -> List[str]:
    """Current NON-hedge holdings of a source account ledger (e.g. 'primary' = the live model_v4
    book) — the names this account replicates. Frozen+continuation merged; latest book wins."""
    pos = load_ledger(source)["positions"]
    if pos is None or not len(pos) or "ticker" not in pos.columns:
        return []
    seen, out = set(), []
    for t in pos["ticker"].tolist():
        s = str(t).strip()
        if s and s != HEDGE_SYM and s not in seen:
            seen.add(s); out.append(s)
    return out


def _model_v4_decision(name: str, cli: ba.AlpacaPaper) -> Dict[str, Any]:
    """model_v4's next-session decision {buys, sells} computed SEEDED with the account's LIVE broker
    book + cash — so exits, the exposure cap, and ROTATION FUNDING (sell the weakest holding to fund a
    persistence buy) all reflect the real positions and cash, not a from-inception simulation."""
    sys.path.insert(0, str(ROOT / "src"))
    from datetime import date as _date, timedelta as _td
    from scenarios import build_config, load_scenario
    from backtest import load_config, fetch_backtest_data, next_session_decision
    man = load_manifest(name) or {}
    cfg = build_config(load_config(ROOT / "config"), load_scenario(man.get("scenario", "model_v4")))
    acct = cli.account()
    led = load_ledger(name).get("positions")               # ledger entry dates (for max-hold / days)
    led_dates = ({str(r["ticker"]).strip(): r.get("entry_date") for _, r in led.iterrows()}
                 if (led is not None and len(led) and "entry_date" in led.columns) else {})
    inception = man.get("inception")
    rows = []
    for p in cli.positions():                              # seed from the live broker book (avg_entry = cost)
        t = p["ticker"]
        if t in (HEDGE_SYM, REBOUND_SYM):                  # overlays are not model positions
            continue
        now = float(p["price"])
        rows.append({"ticker": t, "shares": int(p["qty"]), "entry_price": float(p["avg_entry"]),
                     "entry_date": led_dates.get(t) or inception, "current_price": now,
                     "highest_price": now, "lowest_price": now})
    init_pos = pd.DataFrame(rows, columns=["ticker", "shares", "entry_price", "entry_date",
                                           "current_price", "highest_price", "lowest_price"])
    init_cash = float(acct.get("cash") or 0.0)
    end = _date.today()
    pdata = fetch_backtest_data(cfg["tickers"], end - _td(days=220), end)   # >= 60 trading days
    return next_session_decision(cfg, pdata, initial_positions=init_pos, initial_cash=init_cash)


def _model_v4_targets(name: str, current: Dict[str, float], cli: ba.AlpacaPaper,
                      include_hedge: bool = False) -> "tuple[Dict[str,int], Dict[str,float]]":
    """Follow model_v4's OWN buy/sell rules on THIS account's book: hold the current positions and
    apply model_v4's next-session ENTRIES (gate >0.70 + persistence, model-sized) and EXITS
    (score-gated 15% stop / max-hold / rotation funding) — computed SEEDED with the live broker book
    so the funding/exposure-cap math is real. Buys ADD; exits + rotation sells → 0. No hedge for
    accounts unless include_hedge=True."""
    ns = _model_v4_decision(name, cli)
    targets: Dict[str, int] = {t: int(round(s)) for t, s in current.items()
                               if t not in (HEDGE_SYM, REBOUND_SYM)}
    refs: Dict[str, float] = {}
    for b in (ns.get("buys") or []):
        sym, px = b["ticker"], b.get("price")
        sh = int(round(b.get("shares") or 0))
        if sym == HEDGE_SYM:
            if include_hedge:
                targets[HEDGE_SYM] = sh
            continue
        if px:
            refs[sym] = px
        targets[sym] = int(round(current.get(sym, 0))) + sh
    for s in (ns.get("sells") or []):                      # model exits + rotation-funding sells → flatten
        sym = s["ticker"]
        if sym == HEDGE_SYM:
            continue
        targets[sym] = 0
        if s.get("price"):
            refs[sym] = s["price"]
    if not include_hedge:
        targets.pop(HEDGE_SYM, None)
    return targets, refs


def _deployed_frac(name: str, cli: ba.AlpacaPaper = None) -> float:
    """Cumulative BUY notional ÷ starting cash for `name` — the 'funded' fraction used to graduate a
    ramp-up account to full model_v4 (Σ buys / starting_value). Sourced from the BROKER's filled buy
    orders (the broker is the source of truth; the ledger trades.csv isn't populated for fills)."""
    man = load_manifest(name) or {}
    starting = float(man.get("starting_value", 100000.0)) or 1.0
    cli = cli or ba.AlpacaPaper(account=name)
    spent = 0.0
    try:
        for o in cli.orders(status="closed"):
            if o.get("side") == "buy" and o.get("status") == "filled" and o.get("fill_price"):
                spent += float(o.get("filled_qty") or 0) * float(o["fill_price"])
    except Exception:
        return 0.0
    return spent / starting


def _avg_scores(scenario: str = "model_v4", n: int = 5) -> Dict[str, float]:
    """{ticker: composite score averaged over the last n ranking snapshots} — the trailing 5-day MEAN
    score (each snapshot scores ALL universe names every day, whether held or not), used to choose the
    rotation exits (lowest-conviction names by recent average, not just today)."""
    import glob
    snaps = sorted(glob.glob(str(ROOT / "backtests" / f"rankings_{scenario}_*.csv")))[-n:]
    if not snaps:
        return {}
    cols = [pd.read_csv(s).assign(ticker=lambda d: d["ticker"].astype(str).str.strip())
            .set_index("ticker")["score"] for s in snaps]
    avg = pd.concat(cols, axis=1).mean(axis=1)
    return {str(t): float(v) for t, v in avg.items()}


def _rebound_target(name: str, cli: ba.AlpacaPaper, targets: Dict[str, int],
                    refs: Dict[str, float]) -> "tuple[Dict[str,int], Dict[str,float]]":
    """Overlay the standalone 1-day REBOUND sleeve onto the account's model target. If the LIVE rebound
    fires (QQQ down-shock + momentum signal<0 + vol-up; see rebound_overlay), ADD a TQQQ buy at the full
    weight x book size. Funding (`rebound_funding`, default 'trim'): cash first, then ROTATE — exit AT MOST
    `rebound_trim_max` (default 2) holdings, the lowest by 5-DAY AVG score, to raise the shortfall; the rest
    stays in cash (overlay capped if cash + those 2 exits fall short). Bounds turnover to 2 names. Set
    'cash' to instead cap at available cash (no book sale). If it does NOT fire, TQQQ is absent so the reconcile flattens any
    held rebound position next session (the 1-day exit; the trimmed names also come back into the model
    target and are rebought). The model decision never sees TQQQ. Opt out with manifest `rebound: false`."""
    man = load_manifest(name) or {}
    if not man.get("rebound", True):
        return targets, refs
    try:
        import rebound_overlay as _ro
        acct = cli.account()
        cash = max(float(acct.get("cash") or 0.0), 0.0)
        bmv = max(float(acct.get("equity") or 0.0) - cash, 0.0)
        rec = _ro.recommend(market_value=bmv, live=True)          # latest close -> act now if it fires
        if not rec.get("fires"):
            return targets, refs
        q = (cli.latest_prices([REBOUND_SYM]) or {}).get(REBOUND_SYM) or {}
        px = q.get("mid") or q.get("last") or q.get("price")
        if not (px and float(px) > 0):
            return targets, refs
        want = float(rec["rebound_dollars"])                      # full weight x book
        avail = cash * 0.95                                       # fund from cash first (5% buffer)
        if want > avail and man.get("rebound_funding", "trim") == "trim":
            # ROTATE: fund the shortfall by exiting AT MOST `rebound_trim_max` (default 2) holdings, the
            # lowest by 5-DAY AVG score; the rest stays unfunded (overlay capped). Keeps turnover bounded.
            shortfall = want - avail
            max_exits = int(man.get("rebound_trim_max", 2))
            scores = _avg_scores(man.get("scenario", "model_v4"), 5)
            held = [(t, int(qv)) for t, qv in targets.items()
                    if int(qv) > 0 and t not in (HEDGE_SYM, REBOUND_SYM)]
            held.sort(key=lambda tqv: scores.get(tqv[0], 0.5))   # lowest 5d-avg score first
            weakest = held[:max(max_exits, 0)]
            hp = cli.latest_prices([t for t, _ in weakest]) or {}
            raised = 0.0
            for t, qv in weakest:                                # cap at `max_exits` ticker exits
                if raised >= shortfall:
                    break
                p = (hp.get(t) or {}).get("mid") or (hp.get(t) or {}).get("last")
                if not p or float(p) <= 0:
                    continue
                sell = min(qv, int((shortfall - raised) / float(p)) + 1)
                targets[t] = qv - sell                            # trim this holding
                refs[t] = float(p)
                raised += sell * float(p)
            avail += raised                                       # cash + up-to-2 exits; rest unfunded
        qty = int(min(want, avail) / float(px))
        if qty > 0:
            targets[REBOUND_SYM] = qty
            refs[REBOUND_SYM] = float(px)
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning("rebound overlay skipped for %s: %s", name, exc)
    return targets, refs


def _recent_trading_days(n: int = 12):
    """The most recent ~n trading days (DatetimeIndex), cheaply (one small QQQ fetch) — for the
    rebalance-day gate without recomputing scores."""
    import datetime as _dt
    from backtest import fetch_backtest_data
    end = _dt.date.today()
    px = fetch_backtest_data(["QQQ"], end - _dt.timedelta(days=n * 3 + 12), end)["Close"]
    return px.index


def _is_rebalance_day(freq: str, cal) -> bool:
    """Is the latest trading day the FIRST of its week / month? (stateless, calendar-based)."""
    if freq == "daily" or len(cal) < 2:
        return True
    cur, prev = cal[-1], cal[-2]
    if freq == "weekly":
        return tuple(cur.isocalendar())[:2] != tuple(prev.isocalendar())[:2]
    if freq == "monthly":
        return (cur.year, cur.month) != (prev.year, prev.month)
    return True


def _lookback_avg_scores(scenario: str, lookback_days: int = 60, as_of=None):
    """{ticker: trailing N-day AVG composite score} computed LIVE, ending at `as_of` (default today).
    `as_of` lets the top sleeve be anchored to the first-of-month while the bottom uses today (the
    staggered-refresh combo). A daily cross-sectional score averaged over `lookback_days`."""
    import datetime as _dt
    from backtest import load_config, fetch_backtest_data
    from scenarios import load_scenario, build_config
    from signals import calculate_signals, rank_candidates
    from rank_report import _build_ticker_weights, _SIGNAL_WINDOW
    cfg = build_config(load_config(ROOT / "config"), load_scenario(scenario))
    uni, w = cfg["tickers"], cfg["signals"].get("weights")
    tw = _build_ticker_weights(cfg) or None
    end = (as_of.date() if hasattr(as_of, "date") else as_of) or _dt.date.today()
    pdata = fetch_backtest_data(uni, end - _dt.timedelta(days=lookback_days * 2 + 420), end)
    rows = [dict(zip(rf["ticker"], rf["composite_score"]))
            for ts in pdata["Close"].index[-lookback_days:]
            for rf in [rank_candidates(calculate_signals(pdata.loc[:ts].iloc[-_SIGNAL_WINDOW:], uni),
                                       top_n=len(uni), weights=w, ticker_weights=tw)]]
    return pd.DataFrame(rows).mean().to_dict()


def _period_anchor(cal, refresh: str):
    """First trading day of the current week/month in `cal` (for staggered refresh — so the top sleeve
    is computed as-of the period start and stays fixed between refreshes)."""
    if len(cal) == 0:
        return None
    last = cal[-1]
    if refresh == "monthly":
        same = [d for d in cal if (d.year, d.month) == (last.year, last.month)]
    elif refresh == "weekly":
        same = [d for d in cal if tuple(d.isocalendar())[:2] == tuple(last.isocalendar())[:2]]
    else:
        return last
    return same[0] if same else last


def _combo_targets(scenario: str, cli: ba.AlpacaPaper, current: Dict[str, float],
                   tm: Dict[str, Any], cal, has_book: bool) -> "tuple[Dict[str,int], Dict[str,float]]":
    """STAGGERED split book (two independent sleeves, each rebalanced on its OWN cadence):
      • TOP sleeve — top_n by `top_lookback_days`-avg score anchored to the first trading day of the month
        (so the names match the monthly book). RE-SIZED only on the month's first weekly rebalance; on every
        other weekly rebalance the top positions are LEFT UNTOUCHED (kept at current shares — they just drift).
      • BOTTOM sleeve — bottom_n by `bottom_lookback_days`-avg score as-of today, RE-SIZED every (weekly)
        rebalance. Each name targets gross/(top_n+bottom_n) of equity (top uses month-start equity via its
        held shares, bottom uses current equity). Overlap -> top sleeve keeps the name."""
    import os
    force = os.environ.get("BROKER_REBALANCE_FORCE_TODAY", "").lower() in ("1", "yes", "true")
    top_n, bot_n = int(tm.get("top_n", 10)), int(tm.get("bottom_n", 10))
    equity = float(cli.account().get("equity") or 0.0)
    per = float(tm.get("gross", 0.90)) * equity / max(top_n + bot_n, 1)
    # special "fire today": anchor the top sleeve to TODAY's intraday bar (not the month start) and re-size it
    anchor = cal[-1] if force else _period_anchor(cal, tm.get("top_refresh", "monthly"))
    ta = _lookback_avg_scores(scenario, int(tm.get("top_lookback_days", 60)), as_of=anchor)
    top = [t for t in sorted(ta, key=lambda k: ta[k], reverse=True) if pd.notna(ta[t])][:top_n]
    ba = _lookback_avg_scores(scenario, int(tm.get("bottom_lookback_days", 5)))
    bottom = [t for t in sorted(ba, key=lambda k: ba[k]) if pd.notna(ba[t])][:bot_n]
    # refresh the top sleeve only on the month's FIRST weekly rebalance (or when forced / first deploy)
    do_top = force or (not has_book) or (tuple(cal[-1].isocalendar())[:2] == tuple(anchor.isocalendar())[:2])
    quotes = cli.latest_prices(list(dict.fromkeys(top + bottom))) or {}
    cur = current or {}
    targets: Dict[str, int] = {}
    refs: Dict[str, float] = {}
    for t in top:
        px = (quotes.get(t) or {}).get("mid") or (quotes.get(t) or {}).get("last")
        if not px or float(px) <= 0:
            continue
        refs[t] = float(px)
        targets[t] = int(per / float(px)) if do_top else int(round(cur.get(t, 0)))   # monthly re-size, else hold
    for t in bottom:
        if t in targets:                                           # overlap -> top sleeve keeps it
            continue
        px = (quotes.get(t) or {}).get("mid") or (quotes.get(t) or {}).get("last")
        if not px or float(px) <= 0:
            continue
        refs[t] = float(px)
        targets[t] = int(per / float(px))                          # bottom re-sizes every (weekly) rebalance
    return targets, refs


def _score_rebalance_targets(name: str, cli: ba.AlpacaPaper, current: Dict[str, float],
                             tm: Dict[str, Any]) -> "tuple[Dict[str,int], Dict[str,float]]":
    """Periodically-rebalanced score book (`target_mode: {kind: score_rebalance, ...}`). SINGLE-lookback
    (`lookback_days, top_n, bottom_n`): rank by trailing-avg score, hold top_n (+ bottom_n) equal-weight,
    rebalance on the first trading day of each week/month. STAGGERED split (`top_lookback_days/top_refresh`
    + `bottom_lookback_days` present): see `_combo_targets` — top sleeve rebalanced monthly, bottom weekly.
    Off-rebalance days hold. No model_v4 rules, no hedge/rebound; dropped names are flattened by reconcile."""
    import os
    force = os.environ.get("BROKER_REBALANCE_FORCE_TODAY", "").lower() in ("1", "yes", "true")
    held = {t: int(round(s)) for t, s in (current or {}).items()
            if int(round(s)) > 0 and t not in (HEDGE_SYM, REBOUND_SYM)}
    cal = _recent_trading_days()
    if held and not force and not _is_rebalance_day(tm.get("rebalance", "monthly"), cal):
        return held, {}                                            # not a rebalance day -> hold (unless forced)
    scenario = (load_manifest(name) or {}).get("scenario", "model_v4")
    if tm.get("top_lookback_days") or tm.get("bottom_lookback_days"):
        return _combo_targets(scenario, cli, current, tm, cal, bool(held))
    avg = _lookback_avg_scores(scenario, int(tm.get("lookback_days", 60)))
    ranked = [t for t in sorted(avg, key=lambda k: avg[k], reverse=True) if pd.notna(avg[t])]
    top_n, bot_n = int(tm.get("top_n", 10)), int(tm.get("bottom_n", 0))
    picks = list(dict.fromkeys(ranked[:top_n] + (ranked[-bot_n:] if bot_n else [])))
    if not picks:
        return held, {}
    equity = float(cli.account().get("equity") or 0.0)
    per = float(tm.get("gross", 0.90)) * equity / len(picks)       # equal-weight to gross exposure
    quotes = cli.latest_prices(picks) or {}
    targets: Dict[str, int] = {}
    refs: Dict[str, float] = {}
    for t in picks:
        px = (quotes.get(t) or {}).get("mid") or (quotes.get(t) or {}).get("last")
        if px and float(px) > 0:
            refs[t] = float(px)
            targets[t] = int(per / float(px))
    return targets, refs                                           # picks only -> the rest flattens


def compute_targets(name: str, cli: ba.AlpacaPaper,
                    current: Optional[Dict[str, float]] = None) -> "tuple[Dict[str,int], Dict[str,float]]":
    """TARGET book {symbol: shares} for the next session, computed from the broker's actual book.

    Default (ramp-up) mode:
        • hold every current NON-hedge position (ramp-up is accumulate-only),
        • add ramp-up entries (>0.9 names not yet held) at their queued size,
        • set the hedge to its recommended size (0 if the signal isn't firing).
    Top-N mode (manifest `target_mode: {kind: top_n, n, size_pct}`): the target IS the N
    highest current-composite-score names, each sized at size_pct of live equity (accumulate;
    names that drop out of the top N are reconciled to 0). No hedge in this mode.
    Model-equal mode (manifest `target_mode: {kind: model_equal, source, gross}`): replicate the
    NAMES held by a source account (default 'primary' = the live model_v4 book), EQUAL-weighted at
    gross/N of live equity each (accumulate; names the source drops are reconciled to 0). No hedge.
    Score-gate mode (manifest `target_mode: {kind: score_gate, min_score, size_pct}`): hold exactly
    the names whose CURRENT composite score >= min_score (default 0.9) at current ranks, each sized
    at size_pct of live equity (accumulate; names that fall below the gate are reconciled to 0). A
    threshold, not a fixed count — the book grows/shrinks with how many clear the gate. No hedge.
    Model-v4 mode (`target_mode: {kind: model_v4}`): follow model_v4's OWN buy/sell rules on this
    account's book (next_session_decision — gate/persistence entries, score-gated/max-hold/rotation
    exits). The seed persists; the book evolves by the model's daily decisions. No hedge. (top_n /
    model_equal / score_gate were the INITIAL SEED modes; this is the post-seed steady state.)
    Score-gate ramp-up mode (`{kind: score_gate_rampup, min_score, size_pct, graduate_at}`): BUY only
    names scoring > min_score (size_pct each) but SELL only per model_v4's exit rules, UNTIL
    `graduate_at` of starting cash has been deployed (Σ broker buys / starting), then full model_v4.

    Diffing this vs the broker's current positions rolls the 1-day hedge and never re-buys held
    names. Returns (targets, ref_prices)."""
    current = current if current is not None else {p["ticker"]: p["qty"] for p in cli.positions()}
    tm = (load_manifest(name) or {}).get("target_mode") or {}
    if tm.get("kind") == "score_rebalance":
        # trailing-N-day-avg-score top_n (+bottom_n) equal-weight, rebalanced weekly/monthly. No overlay.
        return _score_rebalance_targets(name, cli, current or {}, tm)
    if tm.get("kind") == "model_v4":
        # Follow model_v4's own entry/exit rules on this account's book (post-seed). No hedge.
        # Then overlay the 1-day rebound sleeve (TQQQ on a confirmed momentum-crash sell-off).
        return _rebound_target(name, cli, *_model_v4_targets(name, current, cli,
                                                             include_hedge=bool(tm.get("hedge", False))))
    if tm.get("kind") == "score_gate_rampup":
        # Ramp-up: BUY only names scoring > min_score (size_pct each), but SELL only per model_v4's
        # exit rules — until `graduate_at` of starting cash has been deployed, then full model_v4.
        equity = float(cli.account().get("equity") or 0.0)
        if _deployed_frac(name, cli) >= float(tm.get("graduate_at", 0.75)):
            return _rebound_target(name, cli, *_model_v4_targets(name, current, cli,
                                                                 include_hedge=bool(tm.get("hedge", False))))
        model_sells = {s["ticker"] for s in (_model_v4_decision(name, cli).get("sells") or [])}
        # keep current names EXCEPT those model_v4 is exiting (sell only per model_v4 rules)
        targets: Dict[str, int] = {s: int(round(sh)) for s, sh in current.items()
                                   if s not in (HEDGE_SYM, REBOUND_SYM) and s not in model_sells}
        refs: Dict[str, float] = {}
        size_pct = float(tm.get("size_pct", 0.085))
        for it in ba.score_gate_from_account(name, min_score=float(tm.get("min_score", 0.9))):
            s, px = it["ticker"], it.get("price")              # add the >0.9 names at size_pct
            if not px or float(px) <= 0:
                continue
            refs[s] = float(px)
            targets[s] = max(int(round(current.get(s, 0))), int(equity * size_pct / float(px)))
        return _rebound_target(name, cli, targets, refs)
    if tm.get("kind") == "top_n":
        equity = float(cli.account().get("equity") or 0.0)
        intended = ba.topn_from_account(name, top_n=int(tm.get("n", 10)))
        return topn_targets(intended, equity, current, float(tm.get("size_pct", 0.085)))
    if tm.get("kind") == "score_gate":
        equity = float(cli.account().get("equity") or 0.0)
        intended = ba.score_gate_from_account(name, min_score=float(tm.get("min_score", 0.9)))
        return topn_targets(intended, equity, current, float(tm.get("size_pct", 0.085)))
    if tm.get("kind") == "model_equal":
        equity = float(cli.account().get("equity") or 0.0)
        names = _source_book_names(tm.get("source", "primary"))
        quotes = cli.latest_prices(names) if names else {}
        prices = {s: (quotes.get(s) or {}).get("mid") for s in names}
        return equal_weight_targets(prices, equity, current, float(tm.get("gross", 1.0)))
    q = ba.queue_from_account(name)
    targets: Dict[str, int] = {t: int(round(s)) for t, s in current.items() if t != HEDGE_SYM}
    refs: Dict[str, float] = {}
    hedge_seen = False
    for it in q:
        sym, px = it["ticker"], it.get("price")
        sh = int(round(it.get("shares") or 0))
        if px:
            refs[sym] = px
        if sym == HEDGE_SYM:
            targets[HEDGE_SYM] = sh; hedge_seen = True
        elif it.get("action", "BUY").upper() == "BUY":
            targets[sym] = int(round(current.get(sym, 0))) + sh    # held -> add; new -> shares
        else:                                                       # SELL / model exit
            targets[sym] = 0
    if not hedge_seen:
        targets[HEDGE_SYM] = 0                                      # hedge off -> flatten any hedge
    return targets, refs


# ── session steps ──────────────────────────────────────────────────────────────────
_LIVE_STATUSES = {"new", "accepted", "pending_new", "partially_filled",
                  "accepted_for_bidding", "held", "calculated"}


def _dedupe_order_ids(cli: ba.AlpacaPaper, asof: str, orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Alpaca requires client_order_id to be globally unique (forever — even vs canceled orders).
    So: (1) if a LIVE order for this symbol/side already exists today, drop the new one (idempotent —
    re-running won't duplicate); (2) otherwise suffix the id with the next attempt index so a fresh
    submit after a cancel/reject doesn't collide. Read-only; degrades gracefully if the lookup fails."""
    prior: Dict[tuple, list] = {}
    try:
        for st in ("open", "closed"):
            for o in cli.orders(status=st):
                coid = o.get("client_order_id") or ""
                if coid.startswith(f"mv4-{asof}-"):
                    prior.setdefault((o["symbol"], o["side"]), []).append(o)
    except Exception:
        return orders                                   # no broker view -> leave base ids as-is
    out = []
    for o in orders:
        hits = prior.get((o["symbol"], o["side"].lower()), [])
        if any(h.get("status") in _LIVE_STATUSES for h in hits):
            continue                                    # already working -> don't re-submit
        if hits:
            o["client_order_id"] = f"{o['client_order_id']}-{len(hits) + 1}"
        out.append(o)
    return out


def submit_session(name: str, cli: ba.AlpacaPaper = None, submit: bool = False,
                   prequeue: bool = False, retry: bool = False, extended: bool = False) -> Dict[str, Any]:
    """Build the day's RECONCILE-TO-TARGET plan (limit orders with data-driven per-symbol collars),
    persist the decision references + collars (for slippage & the retry pass), and optionally submit
    — guarded by a clock/calendar window. `retry=True` rebuilds unfilled deltas at the wider collar.
    `extended=True` sends FILL-NOW marketable-limit `extended_hours` day orders for the current
    pre/post-market session (bypasses the auction window guard)."""
    cli = cli or ba.AlpacaPaper(account=name)
    clk = cli.clock()
    asof = clk.get("timestamp", _utcnow())[:10]
    current = {p["ticker"]: p["qty"] for p in cli.positions()}
    targets, _refpx = compute_targets(name, cli, current)
    delta_syms = sorted({s for s in set(targets) | set(current)
                         if int(round(targets.get(s, 0))) != int(round(current.get(s, 0)))})
    prices = cli.latest_prices(delta_syms) if delta_syms else {}
    collars = compute_collars(delta_syms, cache_day=asof)
    orders = ba.build_reconcile_orders(targets, current, prices, collars, asof, retry=retry, extended=extended)
    for o in orders:                                # the REBOUND overlay EXIT is a 1-day hold sold AT THE
        if o["symbol"] == REBOUND_SYM and o["side"] == "sell":   # CLOSE — force market/limit-on-close even
            o["time_in_force"] = "cls"; o.pop("extended_hours", None)   # in retry / extended-hours mode
            o["_plan"]["tif"] = "cls"
    orders = _dedupe_order_ids(cli, asof, orders)   # idempotent: skip live dupes, make ids unique
    refs = {o["client_order_id"]: o["_plan"]["ref_mid"] for o in orders}
    (_broker_dir(name) / f"plan_{asof}.json").write_text(json.dumps(
        {"asof": asof, "retry": retry, "refs": refs,
         "collars": {s: collars.get(s, {}) for s in delta_syms},
         "orders": [{k: v for k, v in o.items() if not k.startswith("_")} for o in orders],
         "detail": [dict(symbol=o["symbol"], side=o["side"], qty=o["qty"],
                         limit_price=o["limit_price"], **o["_plan"]) for o in orders]}, indent=2))
    # retry orders are intraday DAY limits (submitted while the market is open), so they bypass the
    # pre-open/on-open window guard that governs the first (opg/cls) attempt.
    win = submit_window(clk, prequeue=prequeue or retry or extended)
    if submit and not win["ok"]:
        return {"asof": asof, "n_orders": len(orders), "submitted": 0, "dry_run": True,
                "blocked": True, "reason": win["reason"], "orders": orders}
    results = [cli.submit({k: v for k, v in o.items() if not k.startswith("_")}, confirm=submit)
               for o in orders]
    sent = sum(1 for r in results if not r.get("dry_run"))
    return {"asof": asof, "n_orders": len(orders), "submitted": sent,
            "dry_run": sent == 0, "window": win["reason"], "orders": orders}


def retry_unfilled(name: str, cli: ba.AlpacaPaper = None) -> Dict[str, Any]:
    """RETRY-ONCE-WIDER: cancel any still-open limit orders from today's plan and resubmit the
    remaining delta at each symbol's wider retry collar; anything still unfilled after this is
    SKIPPED (logged). Call once, after the first plan has had time to work."""
    cli = cli or ba.AlpacaPaper(account=name)
    asof = cli.clock().get("timestamp", _utcnow())[:10]
    open_orders = [o for o in cli.orders(status="open")]
    todays = [o for o in open_orders if (o.get("client_order_id") or "").startswith(f"mv4-{asof}-")]
    for o in todays:                                   # cancel the unfilled first attempt
        cli.cancel(o["id"]) if hasattr(cli, "cancel") else None
    res = submit_session(name, cli=cli, submit=True, prequeue=False, retry=True)
    # record what got skipped (still no position vs target) for honesty
    targets, _ = compute_targets(name, cli)
    current = {p["ticker"]: p["qty"] for p in cli.positions()}
    skipped = [{"asof": asof, "symbol": s, "target": int(round(targets.get(s, 0))),
                "current": int(round(current.get(s, 0)))}
               for s in sorted(set(targets) | set(current))
               if int(round(targets.get(s, 0))) != int(round(current.get(s, 0)))]
    if skipped:
        _append_csv(_broker_dir(name) / "skips.csv", pd.DataFrame(skipped))
    return {"asof": asof, "canceled": len(todays), "resubmitted": res["n_orders"],
            "still_unfilled": len(skipped)}


def flatten_overlay(name: str, cli: ba.AlpacaPaper = None, submit: bool = False,
                    sym: str = REBOUND_SYM) -> Dict[str, Any]:
    """Force-exit any REMAINING overlay position (`sym`, default TQQQ) — for when the scheduled
    close-of-day (`cls`) exit didn't fully fill (submitted after the LOC cutoff, partial, or rejected).
    CANCELS any working order for `sym` first (so we don't double-sell a still-pending exit), then
    submits a MARKETABLE day-ext sell for the actual live position. Guarded: dry-run unless submit=True
    AND env BROKER_ADAPTER_ALLOW_SUBMIT=yes."""
    cli = cli or ba.AlpacaPaper(account=name)
    canceled = 0
    for o in (cli.orders(status="open") or []):           # cancel working orders -> avoid double-sell
        if o.get("symbol") == sym:
            cli.cancel(o["id"], confirm=submit)
            canceled += 1
    pos = next((p for p in (cli.positions() or []) if p.get("ticker") == sym), None)
    qty = int(round(float(pos["qty"]))) if pos else 0
    if qty <= 0:                                           # already flat -> nothing to do
        return {"account": name, "sym": sym, "qty": 0, "canceled": canceled, "submitted": False, "order": None}
    q = (cli.latest_prices([sym]) or {}).get(sym) or {}
    px = q.get("bid") or q.get("mid") or pos.get("price")
    lim = round(float(px) * 0.97, 2) if px else None       # 3% through the bid -> crosses now
    ts = _utcnow().replace(":", "").replace("-", "").replace("T", "")
    order = {"symbol": sym, "qty": str(qty), "side": "sell", "type": "limit", "limit_price": lim,
             "time_in_force": "day", "extended_hours": True, "client_order_id": f"flat-{sym}-{name}-{ts[:14]}"}
    res = cli.submit(order, confirm=submit)
    return {"account": name, "sym": sym, "qty": qty, "limit": lim, "canceled": canceled,
            "submitted": bool(submit and isinstance(res, dict) and res.get("id")), "order": res}


def create_broker_account(name: str, scenario: str = "model_v4", starting: float = 100000.0,
                          ramp_up: Optional[Dict[str, Any]] = None, asof: Optional[str] = None,
                          broker_keys: Optional[Dict[str, str]] = None,
                          target_mode: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a fresh broker-driven account: an empty frozen ledger (cash only, no positions) that
    reconcile_session() then drives forward from the real Alpaca fills (broker = source of truth).
    `broker_keys` = {"key_env": "...", "secret_env": "..."} names the .env vars holding THIS
    account's Alpaca paper keys, so multiple accounts can each use their own credentials."""
    d = _acct_dir(name); d.mkdir(parents=True, exist_ok=True)
    asof = asof or _utcnow()[:10]
    pd.DataFrame(columns=["date", "action", "ticker", "shares", "price", "trade_value", "reason",
                          "realized_pnl", "holding_days", "entry_price", "highest_price",
                          "lowest_price"]).to_csv(d / "trades.csv", index=False)
    pd.DataFrame([{"date": asof, "cash": starting, "open_positions_value": 0.0,
                   "total_portfolio_value": starting, "realized_pnl_to_date": 0.0,
                   "unrealized_pnl": 0.0, "daily_return": 0.0, "cumulative_return": 0.0,
                   "spy_cumulative_return": 0.0, "qqq_cumulative_return": 0.0,
                   "equal_weight_cumulative_return": 0.0, "forecast_vol": "",
                   "exposure_mult": 1.0}]).to_csv(d / "equity.csv", index=False)
    pd.DataFrame(columns=["ticker", "shares", "entry_price", "entry_date", "current_price",
                          "highest_price", "lowest_price"]).to_csv(d / "positions.csv", index=False)
    man = {"name": name, "scenario": scenario, "status": "frozen", "inception": asof,
           "frozen_through": asof, "live_through": asof, "starting_value": starting,
           "ending_value": starting, "total_return": 0.0, "n_trades": 0, "n_positions": 0,
           "broker": "alpaca_paper",
           "broker_keys": broker_keys or {"key_env": "APCA_API_KEY_ID_FIRST",
                                          "secret_env": "APCA_API_SECRET_KEY_FIRST"},
           "ramp_up": ramp_up or {"entry_score": 0.9, "entry_size_pct": 0.085, "hedge": True},
           "hashes": {}}
    if target_mode:
        man["target_mode"] = target_mode
    for f in ["trades.csv", "equity.csv", "positions.csv"]:
        man["hashes"][f] = _sha256(d / f)
    _manifest_path(name).write_text(json.dumps(man, indent=2))
    return man


def reconcile_session(name: str, cli: ba.AlpacaPaper = None) -> Dict[str, Any]:
    """Pull the broker's actual fills + positions; log realized slippage vs the saved plan
    references; rewrite the account's continuation ledger from the broker (source of truth)."""
    cli = cli or ba.AlpacaPaper(account=name)
    asof = cli.clock().get("timestamp", datetime.utcnow().isoformat())[:10]
    bdir = _broker_dir(name)

    # merge all saved plan refs (so fills match their decision prices)
    refs: Dict[str, float] = {}
    for pf in bdir.glob("plan_*.json"):
        refs.update(json.loads(pf.read_text()).get("refs", {}))

    fills = [o for o in cli.orders(status="closed") if o["status"] == "filled" and o["fill_price"]]
    slip = compute_slippage(fills, refs)
    if not slip.empty:
        _append_csv(bdir / "fills.csv", slip)

    # rewrite the ledger from the broker snapshot
    acct = cli.account()
    prior = {p["ticker"]: p.get("entry_date") for _, p in load_ledger(name)["positions"].iterrows()} \
        if len(load_ledger(name)["positions"]) else {}
    snap = ledger_from_broker(cli.positions(), acct["cash"], acct["equity"], asof, prior)
    cont = _acct_dir(name) / "continuation"; cont.mkdir(exist_ok=True)
    _append_csv(cont / "equity.csv", snap["equity"])
    snap["positions"].to_csv(cont / "positions.csv", index=False)

    man = load_manifest(name)
    man["live_through"] = asof; man["live_value"] = acct["equity"]; man["status"] = "living"
    man["n_positions"] = len(snap["positions"]); man["broker"] = "alpaca_paper"
    man.setdefault("hashes", {})
    for f in sorted(cont.glob("*.csv")):
        man["hashes"][f"continuation/{f.name}"] = _sha256(f)
    _manifest_path(name).write_text(json.dumps(man, indent=2))

    return {"asof": asof, "fills": int(len(slip)),
            "avg_slippage_bps": float(slip["slippage_bps"].mean()) if not slip.empty else None,
            "equity": acct["equity"], "positions": len(snap["positions"])}


def apply_live_broker_marks(d: Dict[str, Any], account: str, cli: ba.AlpacaPaper = None) -> bool:
    """Overlay the LIVE Alpaca book onto a rank_report.build_report dict `d` (in place) so an
    account's intraday returns reflect REAL fills + live prices instead of the (possibly 1-day-old)
    ledger:
      • each held position's entry_price ← Alpaca avg_entry_price (what was actually paid),
        current_price ← Alpaca current_price (live) → the holdings table's unrealized %/value are real;
      • pv/cash ← the live account; portfolio 1-day return ← equity / last_equity - 1 (real, and
        defined even when the ledger only has today's equity row).
    Returns True if marks were applied; False (no-op) if `account` isn't broker-backed. Raises only
    if the broker call itself fails — callers guard with try/except and fall back to the ledger."""
    man = load_manifest(account) or {}
    if not (man.get("broker_keys") or man.get("broker") == "alpaca_paper"):
        return False
    cli = cli or ba.AlpacaPaper(account=account)
    acct = cli.account()
    bpos = cli.positions()
    # Rebuild the held book from the BROKER (source of truth) so positions held at the broker but not
    # yet in the ledger (e.g. submitted-but-not-reconciled) still show. Enrich each from the ledger
    # where the ticker exists (entry_date for "days", running peaks); fall back to broker values else.
    led = d.get("positions")
    led_by = {}
    if led is not None and not led.empty:
        led_by = {r["ticker"]: r for _, r in led.iterrows()}
    cols = ["ticker", "shares", "entry_price", "entry_date", "current_price",
            "highest_price", "lowest_price"]
    rows = []
    for p in bpos:
        t = p["ticker"]; lr = led_by.get(t); now = float(p["price"])
        rows.append({"ticker": t, "shares": int(p["qty"]), "entry_price": float(p["avg_entry"]),
                     "entry_date": (lr["entry_date"] if lr is not None else d.get("mark")),
                     "current_price": now,
                     "highest_price": float(lr["highest_price"]) if lr is not None else now,
                     "lowest_price": float(lr["lowest_price"]) if lr is not None else now})
    d["positions"] = pd.DataFrame(rows, columns=cols)
    eq = float(acct.get("equity") or 0) or d.get("pv")
    if eq:
        d["pv"] = eq
    d["cash"] = float(acct.get("cash") or d.get("cash") or 0)
    # held-book dollar-weighted move today (recomputed for the broker book, vs prior close)
    retf = d.get("ret")
    if retf and rows:
        num = den = 0.0
        for r in rows:
            rr = retf(r["ticker"]); val = r["shares"] * r["current_price"]
            if rr is not None:
                num += val * rr; den += val
        d["held_dw"] = (num / den) if den else d.get("held_dw")
        # equal-weight held return from the REAL broker positions (no synthetic hedge line)
        eqr = [retf(r["ticker"]) for r in rows if retf(r["ticker"]) is not None]
        d["held_avg"] = (sum(eqr) / len(eqr)) if eqr else d.get("held_avg")
    # A broker account does NOT trade the model_v4 overlay hedge — for accounts it's synthetic. The
    # held book / pv / cash / returns above already reflect ONLY the real Alpaca book; strip the rest
    # of the hedge artifacts so nothing imaginary shows: clear the hedge dict, tie the book-only $-wt
    # to held_dw, and drop the synthetic hedge BUY/SELL the report injected.
    d["hedge"] = None
    d["held_dw_book"] = d.get("held_dw")
    for _k in ("today_trades", "recent_trades"):
        if d.get(_k):
            d[_k] = [t for t in d[_k] if "hedge" not in str(t.get("reason", "")).lower()]
    le = float(acct.get("last_equity") or 0)
    if le > 0 and eq:
        day = eq / le - 1
        d.setdefault("stats", {}).setdefault("1D", {})["port"] = day   # real intraday portfolio return
        d["broker_day_return"] = day
    return True


def slippage_summary(name: str) -> Dict[str, Any]:
    """Aggregate the realized-slippage fills log and compare to the model's assumed cost."""
    f = _broker_dir(name) / "fills.csv"
    if not f.exists():
        return {"note": "no fills logged yet"}
    df = pd.read_csv(f)
    by_sym = df.groupby("symbol")["slippage_bps"].mean().round(1).to_dict()
    return {"n_fills": len(df), "avg_slippage_bps": round(df["slippage_bps"].mean(), 2),
            "median_bps": round(df["slippage_bps"].median(), 2),
            "total_slippage_$": round(df["slippage_$"].sum(), 2),
            "assumed_bps": ASSUMED_COST_BPS, "by_symbol": by_sym}


# ── CLI ─────────────────────────────────────────────────────────────────────────────
def _cli(argv=None):
    p = argparse.ArgumentParser(description="Broker reconciliation / slippage / ledger sync")
    p.add_argument("--account", required=True)
    p.add_argument("--submit-plan", action="store_true", help="build + save the order plan")
    p.add_argument("--submit", action="store_true", help="actually send (needs BROKER_ADAPTER_ALLOW_SUBMIT=yes)")
    p.add_argument("--prequeue", action="store_true", help="allow submitting outside the pre-open window (weekend/holiday)")
    p.add_argument("--extended-hours", action="store_true",
                   help="(now the DEFAULT) FILL-NOW marketable-limit extended_hours day orders for the "
                        "current regular/pre/post-market session")
    p.add_argument("--auction", action="store_true",
                   help="opt OUT of fill-now: use next-open/close AUCTION orders (opg buys / cls sells) "
                        "instead of the default marketable fill-ASAP path")
    p.add_argument("--reconcile", action="store_true", help="pull fills, log slippage, sync ledger from broker")
    p.add_argument("--slippage", action="store_true", help="print realized-slippage summary")
    p.add_argument("--retry", action="store_true", help="cancel unfilled orders + resubmit at the wider retry collar")
    p.add_argument("--flatten-overlay", action="store_true",
                   help="force-exit any REMAINING TQQQ overlay position MARKETABLE (cancels working "
                        "orders first) — for when the scheduled cls exit didn't fully fill; with --submit to send")
    p.add_argument("--create-account", action="store_true", help="create a fresh broker-driven ramp-up account")
    p.add_argument("--key-env", help="env-var NAME holding this account's APCA key id (e.g. APCA_API_KEY_ID_NEW)")
    p.add_argument("--secret-env", help="env-var NAME holding this account's APCA secret key")
    p.add_argument("--target-mode",
                   choices=["ramp_up", "top_n", "model_equal", "score_gate", "model_v4",
                            "score_gate_rampup", "score_rebalance"],
                   default="ramp_up",
                   help="SEED modes: top_n / model_equal / score_gate. STEADY-STATE: model_v4 (follow "
                        "model_v4's own buy/sell rules on the account's book). score_gate_rampup (buy "
                        ">--min-score, sell per model_v4, until --graduate-at of starting cash deployed). "
                        "score_rebalance (trailing --lookback-days-avg-score top-N [+ --bottom-n] "
                        "equal-weight, rebalanced --rebalance weekly/monthly).")
    p.add_argument("--graduate-at", type=float, default=0.75,
                   help="fraction of starting cash deployed before a score_gate_rampup account goes full model_v4")
    p.add_argument("--top-n", type=int, default=10, help="N for --target-mode top_n / score_rebalance (default 10)")
    p.add_argument("--bottom-n", type=int, default=0,
                   help="also hold N lowest-scored names for score_rebalance (the 20-name version; default 0)")
    p.add_argument("--lookback-days", type=int, default=60,
                   help="trailing score-average window for score_rebalance (default 60)")
    p.add_argument("--rebalance", choices=["daily", "weekly", "monthly"], default="monthly",
                   help="rebalance frequency for score_rebalance (default monthly)")
    p.add_argument("--min-score", type=float, default=0.9,
                   help="score threshold for --target-mode score_gate (default 0.9)")
    p.add_argument("--size-pct", type=float, default=0.085,
                   help="per-name size as a fraction of equity for top_n / score_gate (default 0.085)")
    p.add_argument("--source", default="primary",
                   help="source account whose holdings to replicate for --target-mode model_equal (default primary)")
    p.add_argument("--gross", type=float, default=1.0,
                   help="total invested fraction split equally across the source's names for model_equal (default 1.0)")
    a = p.parse_args(argv)
    if a.create_account:
        bk = {"key_env": a.key_env, "secret_env": a.secret_env} if (a.key_env and a.secret_env) else None
        if a.target_mode == "top_n":
            tm = {"kind": "top_n", "n": a.top_n, "size_pct": a.size_pct}
        elif a.target_mode == "model_equal":
            tm = {"kind": "model_equal", "source": a.source, "gross": a.gross}
        elif a.target_mode == "score_gate":
            tm = {"kind": "score_gate", "min_score": a.min_score, "size_pct": a.size_pct}
        elif a.target_mode == "model_v4":
            tm = {"kind": "model_v4"}
        elif a.target_mode == "score_gate_rampup":
            tm = {"kind": "score_gate_rampup", "min_score": a.min_score,
                  "size_pct": a.size_pct, "graduate_at": a.graduate_at}
        elif a.target_mode == "score_rebalance":
            tm = {"kind": "score_rebalance", "lookback_days": a.lookback_days, "top_n": a.top_n,
                  "bottom_n": a.bottom_n, "rebalance": a.rebalance, "gross": 0.90}
        else:
            tm = None
        man = create_broker_account(a.account, broker_keys=bk, target_mode=tm)
        # these modes don't ramp up via next_session_decision → the manifest must carry NO ramp_up
        if tm and tm["kind"] in ("model_v4", "score_gate_rampup", "score_rebalance"):
            man.pop("ramp_up", None)
            _manifest_path(a.account).write_text(json.dumps(man, indent=2))
        if tm and tm["kind"] == "top_n":
            tmdesc = "top-%d @ %.1f%%" % (tm["n"], tm["size_pct"] * 100)
        elif tm and tm["kind"] == "model_equal":
            tmdesc = "model_equal (replicate %s @ %.0f%% gross, equal-weight)" % (tm["source"], tm["gross"] * 100)
        elif tm and tm["kind"] == "score_gate":
            tmdesc = "score_gate (current score >= %.2f @ %.1f%% each)" % (tm["min_score"], tm["size_pct"] * 100)
        elif tm and tm["kind"] == "model_v4":
            tmdesc = "model_v4 (follow the model's own buy/sell rules on this book)"
        elif tm and tm["kind"] == "score_gate_rampup":
            tmdesc = "score_gate_rampup (buy >%.2f, sell per model_v4, until %.0f%% deployed)" % (
                tm["min_score"], tm["graduate_at"] * 100)
        elif tm and tm["kind"] == "score_rebalance":
            tmdesc = "score_rebalance (%s rebal, top-%d%s, %dD-avg score, equal-wt)" % (
                tm["rebalance"], tm["top_n"],
                ("+bottom-%d" % tm["bottom_n"]) if tm["bottom_n"] else "", tm["lookback_days"])
        else:
            tmdesc = "ramp_up entry>=%.2f" % (man.get("ramp_up") or {}).get("entry_score", 0.9)
        print("CREATED broker account '%s' (scenario=%s, $%s cash, %s, keys=%s). "
              "Broker now drives the ledger via --reconcile." % (
              man["name"], man["scenario"], format(int(man["starting_value"]), ","),
              tmdesc, man["broker_keys"]["key_env"]))
    if a.submit_plan:
        # fill-ASAP is the default now; --auction opts back into next-open/close auction orders
        r = submit_session(a.account, submit=a.submit, prequeue=a.prequeue,
                           extended=(a.extended_hours or not a.auction))
        if r.get("blocked"):
            print("PLAN %s: %d orders — NOT submitted. %s" % (r["asof"], r["n_orders"], r["reason"]))
        else:
            print("PLAN %s: %d orders, %s" % (r["asof"], r["n_orders"],
                  "DRY-RUN (nothing sent)" if r["dry_run"] else f"{r['submitted']} submitted"))
        for o in r.get("orders", []):
            pl = o["_plan"]
            print("  %-4s %-6s qty %-5s  %-3s limit $%-8.2f  collar %.1f%%  (tgt %d / now %d)  ~$%-8.0f" % (
                o["side"].upper(), o["symbol"], o["qty"], pl.get("tif", o["time_in_force"]),
                o["limit_price"], pl["collar"] * 100, pl["target"], pl["current"], pl["est_value"]))
    if a.retry:
        r = retry_unfilled(a.account)
        print("RETRY %s: canceled %d, resubmitted %d, still unfilled %d" % (
            r["asof"], r["canceled"], r["resubmitted"], r["still_unfilled"]))
    if a.flatten_overlay:
        r = flatten_overlay(a.account, submit=a.submit)
        if r["qty"] == 0:
            print("FLATTEN-OVERLAY %s: no %s position (canceled %d working order(s))"
                  % (a.account, r["sym"], r["canceled"]))
        else:
            tag = "SUBMITTED" if r["submitted"] else "DRY-RUN (nothing sent)"
            print("FLATTEN-OVERLAY %s: SELL %s %d @ <=%.2f marketable day-ext — %s (canceled %d working order(s))"
                  % (a.account, r["sym"], r["qty"], r["limit"] or 0, tag, r["canceled"]))
    if a.reconcile:
        r = reconcile_session(a.account)
        print(f"RECONCILED {r['asof']}: {r['fills']} fills, avg slippage {r['avg_slippage_bps']} bps, "
              f"equity ${r['equity']:,.0f}, {r['positions']} positions")
    if a.slippage:
        print("SLIPPAGE SUMMARY:", json.dumps(slippage_summary(a.account), indent=2))


if __name__ == "__main__":
    _cli()
