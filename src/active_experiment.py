"""
active_experiment.py — Ticker-level active-vs-buy-and-hold, with a fixed grid.

For each ticker we grid-search a SMALL predefined rule set (entry filter + stop /
take-profit / trailing / max-hold), compare the best rule to buy-and-hold of that
same ticker, decide "active eligibility", then build a portfolio from only the
eligible tickers (each trading its own selected rule). Everything is reported in-
sample on a TRAIN window and out-of-sample on a disjoint TEST window.

No unlimited per-ticker optimisation — only the predefined grid. All TRAIN numbers
are in-sample; the TEST block is the out-of-sample validation. Live paper state
(data/) is never touched; outputs go to reports/ and backtests/.

    python run.py active --train-start 2021-06-12 --train-end 2024-06-12 \
                         --test-start 2024-06-12 --test-end 2026-06-12
"""
import argparse
import logging
import sys
from datetime import date
from itertools import product
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from backtest import fetch_backtest_data, load_config
from logger import setup_logging
from risk import resolve_max_position_pct
from signals import calculate_signals, rank_candidates
from signal_calibration import _hold_return, _max_drawdown, _sharpe

log = logging.getLogger(__name__)

# ─── Predefined grid (NOT expanded — this is the whole search space) ──────────
GRID_STOP: List[float] = [0.075, 0.10]
GRID_TP: List[Optional[float]] = [None, 0.15, 0.20]
GRID_TRAIL: List[Optional[float]] = [None, 0.10, 0.15]
GRID_HOLD: List[int] = [30, 60]
ENTRY_FILTERS: List[str] = ["composite", "above_50ma", "ret20_pos", "qqq_above_50ma"]

_MIN_TRADES = 20
_MIN_PF = 1.2
_DD_RETURN_EDGE = 0.10   # "meaningfully higher" return …
_DD_SLACK = 0.05         # … allowed with at most this much extra drawdown


# ─── Entry signals (precomputed per ticker, once) ─────────────────────────────


def compute_entry_signals(price_data: pd.DataFrame, config: Dict[str, Any], tickers: List[str],
                          win_first: int, win_last: int) -> Dict[str, Dict[str, np.ndarray]]:
    """Boolean long-eligibility per (filter, ticker), aligned to the price index."""
    close = price_data["Close"]
    n = len(close.index)
    sig: Dict[str, Dict[str, np.ndarray]] = {f: {} for f in ENTRY_FILTERS}

    # QQQ regime (same array for every ticker)
    if "QQQ" in close.columns:
        q = close["QQQ"].to_numpy()
        qma = close["QQQ"].rolling(50).mean().to_numpy()
        qqq_ok = q > qma
    else:
        qqq_ok = np.ones(n, dtype=bool)

    for t in tickers:
        if t not in close.columns:
            continue
        c = close[t]
        carr = c.to_numpy()
        sma50 = c.rolling(50).mean().to_numpy()
        ret20 = np.full(n, np.nan)
        ret20[20:] = carr[20:] / carr[:-20] - 1.0
        sig["above_50ma"][t] = carr > sma50            # NaN compares False → no entry until valid
        sig["ret20_pos"][t] = ret20 > 0
        sig["qqq_above_50ma"][t] = qqq_ok.copy()

    # composite-score trigger: enter when the ticker's cross-sectional composite
    # clears min_composite_score on that bar (computed with no look-ahead).
    min_score = config.get("signals", {}).get("min_composite_score") or 0.6
    weights = config.get("signals", {}).get("weights")
    comp = {t: np.zeros(n, dtype=bool) for t in tickers if t in close.columns}
    for bar_idx in range(win_first, win_last + 1):
        data_slice = price_data.iloc[max(0, bar_idx + 1 - 60): bar_idx + 1]
        s = calculate_signals(data_slice, tickers)
        if s.empty:
            continue
        ranked = rank_candidates(s, top_n=len(s), weights=weights)
        for _, row in ranked.iterrows():
            tk = row["ticker"]
            if tk in comp and row["composite_score"] >= min_score:
                comp[tk][bar_idx] = True
    for t, arr in comp.items():
        sig["composite"][t] = arr
    return sig


# ─── Single-name active simulator ─────────────────────────────────────────────


def _simulate_active(close: np.ndarray, entry_ok: np.ndarray, a: int, b: int,
                     stop: Optional[float], tp: Optional[float], trail: Optional[float],
                     hold: Optional[int], slippage: float) -> Dict[str, Any]:
    """One ticker, in/out by entry_ok + stop/tp/trailing/hold. Decide at t, fill t+1."""
    cash, shares, in_pos = 1.0, 0.0, False
    peak = entry_price = 0.0
    entry_idx = 0
    n_entries = 0
    bars_long = 0
    slip_paid = 0.0
    equity = np.empty(b - a + 1)
    trade_rets: List[float] = []
    pending: Optional[str] = None

    for t in range(a, b + 1):
        px = close[t]
        if pending == "buy" and not in_pos and not np.isnan(px):
            fill = px * (1 + slippage)
            shares, in_pos, peak, entry_price, entry_idx = cash / fill, True, px, fill, t
            slip_paid += cash * slippage / (1 + slippage)
            cash, n_entries = 0.0, n_entries + 1
        elif pending == "sell" and in_pos and not np.isnan(px):
            fill = px * (1 - slippage)
            trade_rets.append(fill / entry_price - 1.0)
            slip_paid += shares * px * slippage
            cash, shares, in_pos = shares * fill, 0.0, False
        pending = None

        if in_pos:
            peak = max(peak, px)
            bars_long += 1
        equity[t - a] = cash + (shares * px if in_pos else 0.0)

        if t < b:
            if not in_pos:
                if entry_ok[t]:
                    pending = "buy"
            else:
                ret = px / entry_price - 1.0
                hit = ((stop is not None and ret <= -stop)
                       or (tp is not None and ret >= tp)
                       or (trail is not None and peak > 0 and px <= peak * (1 - trail))
                       or (hold is not None and (t - entry_idx) >= hold))
                if hit:
                    pending = "sell"

    daily = equity[1:] / equity[:-1] - 1.0 if len(equity) > 1 else np.array([])
    wins = [r for r in trade_rets if r > 0]
    losses = [r for r in trade_rets if r <= 0]
    if losses and sum(losses) != 0:
        pf: Optional[float] = sum(wins) / abs(sum(losses))
    else:
        pf = float("inf") if wins else None
    return {
        "total_return": float(equity[-1] - 1.0),
        "daily": daily,
        "total_trades": n_entries,
        "win_rate": (len(wins) / len(trade_rets)) if trade_rets else 0.0,
        "profit_factor": pf,
        "slippage_cost": slip_paid,
        "frac_long": bars_long / max(1, b - a + 1),
        "max_drawdown": _max_drawdown(daily),
        "sharpe": _sharpe(daily),
    }


def _eligible(active: Dict[str, Any], hold_ret: float, hold_sharpe: Optional[float],
              hold_dd: Optional[float]) -> bool:
    """Active eligibility gate (all conditions)."""
    ar, asharpe, add = active["total_return"], active["sharpe"], active["max_drawdown"]
    pf, trades = active["profit_factor"], active["total_trades"]
    if hold_sharpe is None or asharpe is None or add is None or hold_dd is None:
        return False
    if not (ar > hold_ret and asharpe > hold_sharpe and trades >= _MIN_TRADES):
        return False
    if not (pf is not None and pf > _MIN_PF):
        return False
    add_mag, hold_mag = abs(add), abs(hold_dd)
    dd_ok = (add_mag <= hold_mag) or (ar >= hold_ret + _DD_RETURN_EDGE and add_mag <= hold_mag + _DD_SLACK)
    return dd_ok


def grid_search_ticker(close: np.ndarray, entry_for_ticker: Dict[str, np.ndarray],
                       a: int, b: int, slippage: float) -> Optional[Dict[str, Any]]:
    """Search the fixed grid for one ticker; return the chosen rule + metrics + eligibility."""
    hold_ret = _hold_return(close, a, b)
    if hold_ret is None or np.isnan(hold_ret):
        return None
    hc = close[a: b + 1]
    hold_daily = hc[1:] / hc[:-1] - 1.0 if len(hc) > 1 else np.array([])
    hold_sharpe, hold_dd = _sharpe(hold_daily), _max_drawdown(hold_daily)

    scored: List[Tuple[Dict[str, Any], Dict[str, Any], bool]] = []
    for filt in ENTRY_FILTERS:
        eok = entry_for_ticker.get(filt)
        if eok is None:
            continue
        for stop, tp, trail, hold in product(GRID_STOP, GRID_TP, GRID_TRAIL, GRID_HOLD):
            res = _simulate_active(close, eok, a, b, stop, tp, trail, hold, slippage)
            rule = {"filter": filt, "stop": stop, "tp": tp, "trail": trail, "hold": hold}
            scored.append((rule, res, _eligible(res, hold_ret, hold_sharpe, hold_dd)))
    if not scored:
        return None

    passing = [(r, m) for r, m, ok in scored if ok]
    if passing:
        rule, res = max(passing, key=lambda rm: (rm[1]["sharpe"] or -9))
        eligible = True
    else:
        rule, res = max(scored, key=lambda rm: rm[1]["total_return"] - hold_ret)[:2]
        eligible = False

    return {
        "rule": rule, "eligible": eligible,
        "active_return": res["total_return"], "hold_return": hold_ret,
        "excess": res["total_return"] - hold_ret,
        "active_dd": res["max_drawdown"], "hold_dd": hold_dd,
        "active_sharpe": res["sharpe"], "hold_sharpe": hold_sharpe,
        "total_trades": res["total_trades"], "win_rate": res["win_rate"],
        "profit_factor": res["profit_factor"], "slippage_cost": res["slippage_cost"],
        "frac_long": res["frac_long"],
    }


def evaluate_ticker_rule(close: np.ndarray, entry_ok: np.ndarray, a: int, b: int,
                         rule: Dict[str, Any], slippage: float) -> Dict[str, Any]:
    """Apply ONE fixed rule to a ticker over [a, b] (used on the OOS test window)."""
    res = _simulate_active(close, entry_ok, a, b, rule["stop"], rule["tp"], rule["trail"],
                           rule["hold"], slippage)
    hold_ret = _hold_return(close, a, b)
    hc = close[a: b + 1]
    hold_daily = hc[1:] / hc[:-1] - 1.0 if len(hc) > 1 else np.array([])
    return {
        "rule": rule, "active_return": res["total_return"],
        "hold_return": hold_ret, "excess": (res["total_return"] - hold_ret) if hold_ret is not None else None,
        "active_dd": res["max_drawdown"], "hold_dd": _max_drawdown(hold_daily),
        "active_sharpe": res["sharpe"], "hold_sharpe": _sharpe(hold_daily),
        "total_trades": res["total_trades"], "win_rate": res["win_rate"],
        "profit_factor": res["profit_factor"], "slippage_cost": res["slippage_cost"],
        "frac_long": res["frac_long"],
    }


# ─── Portfolio of per-ticker rules ────────────────────────────────────────────


def simulate_portfolio(price_data: pd.DataFrame, rules: Dict[str, Dict[str, Any]],
                       entry_signals: Dict[str, Dict[str, np.ndarray]],
                       a: int, b: int, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Each eligible ticker trades its own selected rule. Respects max_total_exposure
    and max_position_pct; holds cash when nothing is active. Decide at t, fill t+1.
    """
    close = price_data["Close"]
    starting = float(config["portfolio"]["starting_value"])
    max_exp = float(config["portfolio"]["max_total_exposure"])
    max_pos = resolve_max_position_pct(config)
    slip = float(config["risk"]["slippage"])
    arrs = {t: close[t].to_numpy() for t in rules if t in close.columns}

    cash = starting
    positions: Dict[str, Dict[str, Any]] = {}
    pending_buys: List[Tuple[str, int]] = []
    pending_sells: List[str] = []
    equity = np.empty(b - a + 1)
    exposure_series = np.empty(b - a + 1)

    for t in range(a, b + 1):
        for tk in pending_sells:
            if tk in positions and not np.isnan(arrs[tk][t]):
                cash += positions[tk]["shares"] * arrs[tk][t] * (1 - slip)
                del positions[tk]
        for tk, shares in pending_buys:
            px = arrs[tk][t]
            if tk not in positions and not np.isnan(px):
                cost = shares * px * (1 + slip)
                if shares > 0 and cost <= cash:
                    cash -= cost
                    positions[tk] = {"shares": shares, "entry_price": px * (1 + slip),
                                     "entry_idx": t, "peak": px, "rule": rules[tk]}
        pending_buys, pending_sells = [], []

        invested = 0.0
        for tk, p in positions.items():
            px = arrs[tk][t]
            if not np.isnan(px):
                p["peak"] = max(p["peak"], px)
                invested += p["shares"] * px
        port_val = cash + invested
        equity[t - a] = port_val
        exposure_series[t - a] = invested / port_val if port_val > 0 else 0.0

        if t < b:
            # exits
            for tk, p in list(positions.items()):
                px = arrs[tk][t]
                if np.isnan(px):
                    continue
                r = p["rule"]
                ret = px / p["entry_price"] - 1.0
                if ((r["stop"] is not None and ret <= -r["stop"])
                        or (r["tp"] is not None and ret >= r["tp"])
                        or (r["trail"] is not None and p["peak"] > 0 and px <= p["peak"] * (1 - r["trail"]))
                        or (r["hold"] is not None and (t - p["entry_idx"]) >= r["hold"])):
                    pending_sells.append(tk)
            # entries (capacity-limited)
            reserved = invested
            for tk, rule in rules.items():
                if tk in positions or tk in pending_sells:
                    continue
                eok = entry_signals[rule["filter"]].get(tk)
                px = arrs[tk][t] if tk in arrs else np.nan
                if eok is None or np.isnan(px) or px <= 0 or not eok[t]:
                    continue
                if port_val <= 0 or reserved / port_val >= max_exp:
                    continue
                shares = int((port_val * max_pos) / px)
                if shares <= 0:
                    continue
                if (reserved + shares * px) / port_val > max_exp or shares * px * (1 + slip) > cash:
                    continue
                pending_buys.append((tk, shares))
                reserved += shares * px

    daily = equity[1:] / equity[:-1] - 1.0 if len(equity) > 1 else np.array([])
    return {
        "total_return": float(equity[-1] / starting - 1.0),
        "daily": daily, "max_drawdown": _max_drawdown(daily), "sharpe": _sharpe(daily),
        "avg_exposure": float(np.mean(exposure_series)), "max_exposure": float(np.max(exposure_series)),
        "ending_value": float(equity[-1]),
    }


# ─── Benchmarks ───────────────────────────────────────────────────────────────


def _ew_daily(close: pd.DataFrame, tickers: List[str], a: int, b: int) -> np.ndarray:
    """Daily-rebalanced equal-weight daily returns for a ticker set over [a, b]."""
    rows = []
    for t in tickers:
        if t not in close.columns:
            continue
        arr = close[t].to_numpy()[a: b + 1]
        if len(arr) > 1:
            rows.append(arr[1:] / arr[:-1] - 1.0)
    if not rows:
        return np.array([])
    return np.nanmean(np.vstack(rows), axis=0)


def _series_metrics(daily: np.ndarray) -> Dict[str, Optional[float]]:
    if daily.size == 0:
        return {"total_return": None, "max_drawdown": None, "sharpe": None}
    return {"total_return": float(np.prod(1 + daily) - 1.0),
            "max_drawdown": _max_drawdown(daily), "sharpe": _sharpe(daily)}


def _bench_block(close: pd.DataFrame, universe: List[str], eligible: List[str],
                 a: int, b: int, avg_exposure: float) -> Dict[str, Dict[str, Optional[float]]]:
    out: Dict[str, Dict[str, Optional[float]]] = {}
    for label, tks in [("SPY", ["SPY"]), ("QQQ", ["QQQ"])]:
        out[label] = _series_metrics(_ew_daily(close, tks, a, b))
    out["EW_universe"] = _series_metrics(_ew_daily(close, universe, a, b))
    ew_elig = _ew_daily(close, eligible, a, b) if eligible else np.array([])
    out["EW_eligible"] = _series_metrics(ew_elig)
    # capital-matched: own the eligible EW basket at avg_exposure, rest cash
    if ew_elig.size and not np.isnan(avg_exposure):
        ew_level = np.cumprod(1 + ew_elig)
        cm_level = 1.0 + avg_exposure * (ew_level - 1.0)
        cm_daily = cm_level[1:] / cm_level[:-1] - 1.0 if len(cm_level) > 1 else np.array([])
        out["EW_eligible_capital_matched"] = {
            "total_return": float(cm_level[-1] - 1.0),
            "max_drawdown": _max_drawdown(cm_daily), "sharpe": _sharpe(cm_daily)}
    else:
        out["EW_eligible_capital_matched"] = {"total_return": None, "max_drawdown": None, "sharpe": None}
    return out


# ─── Orchestration ────────────────────────────────────────────────────────────


def _idx_window(close: pd.DataFrame, start: date, end: date) -> Optional[Tuple[int, int]]:
    in_win = [i for i, ts in enumerate(close.index) if start <= ts.date() <= end]
    return (in_win[0], in_win[-1]) if in_win else None


def run_active_experiment(config: Dict[str, Any], price_data: pd.DataFrame,
                          train: Tuple[date, date], test: Tuple[date, date]) -> Dict[str, Any]:
    close = price_data["Close"]
    tickers = config["tickers"]
    slippage = config["risk"]["slippage"]
    full = _idx_window(close, train[0], test[1])
    tr = _idx_window(close, train[0], train[1])
    te = _idx_window(close, test[0], test[1])
    if not (full and tr and te):
        raise ValueError("Train/test windows not found in the data.")

    # Precompute entry signals across the full span (so MAs/composite have history).
    log.info("Precomputing entry signals…")
    signals = compute_entry_signals(price_data, config, tickers, full[0], full[1])

    # Per-ticker grid search on TRAIN, then evaluate the chosen rule on TEST.
    per_ticker: List[Dict[str, Any]] = []
    for t in tickers:
        if t not in close.columns:
            continue
        carr = close[t].to_numpy()
        entry_t = {f: signals[f][t] for f in ENTRY_FILTERS if t in signals[f]}
        gs = grid_search_ticker(carr, entry_t, tr[0], tr[1], slippage)
        if gs is None:
            continue
        gs["ticker"] = t
        if gs["eligible"]:
            gs["test"] = evaluate_ticker_rule(carr, entry_t[gs["rule"]["filter"]], te[0], te[1],
                                              gs["rule"], slippage)
        per_ticker.append(gs)

    eligible = [r["ticker"] for r in per_ticker if r["eligible"]]
    rules = {r["ticker"]: r["rule"] for r in per_ticker if r["eligible"]}

    # Portfolio of eligible rules, on TRAIN (in-sample) and TEST (out-of-sample).
    port_train = simulate_portfolio(price_data, rules, signals, tr[0], tr[1], config) if rules else None
    port_test = simulate_portfolio(price_data, rules, signals, te[0], te[1], config) if rules else None
    bench_train = _bench_block(close, tickers, eligible, tr[0], tr[1],
                               port_train["avg_exposure"] if port_train else float("nan"))
    bench_test = _bench_block(close, tickers, eligible, te[0], te[1],
                              port_test["avg_exposure"] if port_test else float("nan"))

    return {"per_ticker": per_ticker, "eligible": eligible, "rules": rules,
            "port_train": port_train, "port_test": port_test,
            "bench_train": bench_train, "bench_test": bench_test,
            "train": train, "test": test}


# ─── Reporting ────────────────────────────────────────────────────────────────


def _pct(v: Optional[float], d: str = "—") -> str:
    return d if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v * 100:+.2f}%"


def _num(v: Optional[float], d: str = "—") -> str:
    if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))):
        return "∞" if isinstance(v, float) and np.isinf(v) else d
    return f"{v:.2f}"


def _rule_str(rule: Dict[str, Any]) -> str:
    tp = "null" if rule["tp"] is None else f"{rule['tp']:.0%}"
    tr = "null" if rule["trail"] is None else f"{rule['trail']:.0%}"
    return f"{rule['filter']} | sl {rule['stop']:.1%} | tp {tp} | trail {tr} | hold {rule['hold']}d"


def _pass_fail(port: Optional[Dict[str, Any]], bench: Dict[str, Dict[str, Optional[float]]]) -> List[Tuple[str, bool, str]]:
    ew = bench.get("EW_eligible", {})
    rows: List[Tuple[str, bool, str]] = []
    if not port or ew.get("total_return") is None:
        return [("portfolio vs EW-eligible", False, "no eligible tickers / portfolio")]
    rows.append(("Portfolio beat EW-eligible BH",
                 port["total_return"] > (ew["total_return"] or 9),
                 f"{_pct(port['total_return'])} vs {_pct(ew.get('total_return'))}"))
    rows.append(("Portfolio improved Sharpe vs EW-eligible",
                 (port["sharpe"] or -9) > (ew.get("sharpe") or 9),
                 f"{_num(port['sharpe'])} vs {_num(ew.get('sharpe'))}"))
    rows.append(("Portfolio reduced drawdown vs EW-eligible",
                 abs(port["max_drawdown"] or 9) < abs(ew.get("max_drawdown") or 0),
                 f"{_pct(port['max_drawdown'])} vs {_pct(ew.get('max_drawdown'))}"))
    return rows


def render_report(res: Dict[str, Any], run_date: date) -> str:
    pt = res["per_ticker"]
    n_elig = len(res["eligible"])
    n_beat = sum(1 for r in pt if r["excess"] is not None and r["excess"] > 0)
    train, test = res["train"], res["test"]

    lines: List[str] = [
        "# Ticker-Level Active vs Buy-and-Hold",
        f"**Train (in-sample):** {train[0]} → {train[1]}  |  "
        f"**Test (out-of-sample):** {test[0]} → {test[1]}  |  **Generated:** {run_date.isoformat()}",
        "",
        "> Per ticker, the best rule from a **fixed grid** "
        f"(stop×tp×trail×hold×entry-filter = {len(GRID_STOP)*len(GRID_TP)*len(GRID_TRAIL)*len(GRID_HOLD)*len(ENTRY_FILTERS)} "
        "combos) is chosen on TRAIN and compared to buy-and-hold of that ticker. Eligible tickers "
        "form a portfolio, validated on the disjoint TEST window. No unlimited optimisation.",
        "",
        "---",
        "",
        "## Pass / Fail",
        "",
        "| Test | Result | Detail |",
        "|------|--------|--------|",
        f"| Ticker active rules beat ticker BH (TRAIN) | {'✅' if n_beat else '❌'} {n_beat}/{len(pt)} | excess > 0 in-sample |",
        f"| Tickers passing active eligibility | {'✅' if n_elig else '❌'} {n_elig}/{len(pt)} | full eligibility gate |",
    ]
    for label, ok, detail in _pass_fail(res["port_train"], res["bench_train"]):
        lines.append(f"| {label} (TRAIN) | {'✅' if ok else '❌'} | {detail} |")
    for label, ok, detail in _pass_fail(res["port_test"], res["bench_test"]):
        lines.append(f"| {label} (TEST/OOS) | {'✅' if ok else '❌'} | {detail} |")
    # survive OOS = portfolio beat EW-eligible on TEST
    pf_test = _pass_fail(res["port_test"], res["bench_test"])
    survive = bool(pf_test) and pf_test[0][1]
    lines.append(f"| **Performance survived out-of-sample** | {'✅' if survive else '❌'} | TEST portfolio vs EW-eligible BH |")
    lines.append("")

    # Per-ticker (TRAIN)
    lines += [
        "## Per-Ticker Active vs Buy-and-Hold (TRAIN, in-sample)",
        "",
        "| Ticker | Eligible | Best Rule | Active Ret | BH Ret | Excess | Active DD | BH DD | Active Sharpe | BH Sharpe | Trades | Win% | PF | Slippage |",
        "|--------|----------|-----------|-----------|--------|--------|-----------|-------|---------------|-----------|--------|------|----|----------|",
    ]
    for r in sorted(pt, key=lambda x: (x["eligible"], x["excess"] or -9), reverse=True):
        lines.append(
            f"| {r['ticker']} | {'✅' if r['eligible'] else '❌'} | {_rule_str(r['rule'])} "
            f"| {_pct(r['active_return'])} | {_pct(r['hold_return'])} | {_pct(r['excess'])} "
            f"| {_pct(r['active_dd'])} | {_pct(r['hold_dd'])} | {_num(r['active_sharpe'])} "
            f"| {_num(r['hold_sharpe'])} | {r['total_trades']} | {_pct(r['win_rate'])} "
            f"| {_num(r['profit_factor'])} | {_pct(r['slippage_cost'])} |"
        )
    lines.append("")

    # Portfolio vs benchmarks
    for tag, port, bench in [("TRAIN (in-sample)", res["port_train"], res["bench_train"]),
                             ("TEST (out-of-sample)", res["port_test"], res["bench_test"])]:
        lines += [f"## Portfolio vs Benchmarks — {tag}", "",
                  "| Strategy | Total Return | Max DD | Sharpe |",
                  "|----------|--------------|--------|--------|"]
        if port:
            lines.append(f"| **Active portfolio** ({_pct(port['avg_exposure'])} avg exp) "
                         f"| {_pct(port['total_return'])} | {_pct(port['max_drawdown'])} | {_num(port['sharpe'])} |")
        else:
            lines.append("| **Active portfolio** | _no eligible tickers_ | — | — |")
        for key, label in [("SPY", "SPY"), ("QQQ", "QQQ"), ("EW_universe", "EW buy-hold (full universe)"),
                           ("EW_eligible", "EW buy-hold (eligible only)"),
                           ("EW_eligible_capital_matched", "EW eligible, capital-matched")]:
            m = bench.get(key, {})
            lines.append(f"| {label} | {_pct(m.get('total_return'))} | {_pct(m.get('max_drawdown'))} | {_num(m.get('sharpe'))} |")
        lines.append("")

    lines += [
        "## Interpretation",
        "",
        f"- {n_elig}/{len(pt)} tickers cleared the full active-eligibility gate in-sample. "
        + ("Eligible names then form the portfolio." if n_elig else
           "With none eligible, there is no active edge over holding these names on this window."),
        "- **The TEST block is the verdict.** If the portfolio's TEST row does not beat EW-eligible "
        "buy-and-hold, the in-sample eligibility did not generalise — i.e. it was grid-search luck.",
        "- All TRAIN numbers are in-sample by construction (best-of-grid). Re-run with the second split "
        "to confirm; a real edge survives both.",
        "",
    ]
    return "\n".join(lines)


def results_csv(res: Dict[str, Any]) -> pd.DataFrame:
    rows = []
    for r in res["per_ticker"]:
        rule = r["rule"]
        row = {"ticker": r["ticker"], "eligible": r["eligible"],
               "entry_filter": rule["filter"], "stop_loss": rule["stop"], "take_profit": rule["tp"],
               "trailing_stop": rule["trail"], "max_holding_days": rule["hold"],
               "active_return": r["active_return"], "hold_return": r["hold_return"], "excess": r["excess"],
               "active_dd": r["active_dd"], "hold_dd": r["hold_dd"],
               "active_sharpe": r["active_sharpe"], "hold_sharpe": r["hold_sharpe"],
               "total_trades": r["total_trades"], "win_rate": r["win_rate"],
               "profit_factor": (None if r["profit_factor"] in (None,) else
                                 (1e9 if r["profit_factor"] == float("inf") else r["profit_factor"])),
               "slippage_cost": r["slippage_cost"]}
        t = r.get("test")
        if t:
            row.update({"oos_active_return": t["active_return"], "oos_hold_return": t["hold_return"],
                        "oos_excess": t["excess"], "oos_active_sharpe": t["active_sharpe"]})
        rows.append(row)
    return pd.DataFrame(rows)


# ─── CLI ──────────────────────────────────────────────────────────────────────


def run(train_start: date, train_end: date, test_start: date, test_end: date) -> Dict[str, str]:
    setup_logging()
    run_date = date.today()
    root = Path(__file__).parent.parent
    config = load_config(root / "config")

    log.info("=== Ticker-Level Active vs Buy-and-Hold ===")
    price_data = fetch_backtest_data(config["tickers"], train_start, test_end)
    res = run_active_experiment(config, price_data, (train_start, train_end), (test_start, test_end))
    report = render_report(res, run_date)
    csv_df = results_csv(res)

    (root / "reports").mkdir(parents=True, exist_ok=True)
    (root / "backtests").mkdir(parents=True, exist_ok=True)
    tag = run_date.isoformat()
    md = root / "reports" / f"active_experiment_{tag}.md"
    md.write_text(report)
    csv = root / "backtests" / f"active_experiment_{tag}.csv"
    csv_df.to_csv(csv, index=False)

    print()
    print(f"  Eligible tickers : {len(res['eligible'])}/{len(res['per_ticker'])}")
    if res["port_test"] and res["bench_test"].get("EW_eligible", {}).get("total_return") is not None:
        pv, bv = res["port_test"]["total_return"], res["bench_test"]["EW_eligible"]["total_return"]
        print(f"  OOS portfolio    : {_pct(pv)}  vs EW-eligible {_pct(bv)}  "
              f"({'BEATS' if pv > bv else 'trails'})")
    print()
    print(f"  Report : {md}")
    print(f"  CSV    : {csv}")
    print("  NOTE: TRAIN is in-sample; TEST is the OOS verdict. Re-run with the 2nd split to confirm.")
    print()
    return {"report": str(md), "csv": str(csv)}


def main() -> None:
    p = argparse.ArgumentParser(description="AI Paper Trader — Ticker-Level Active vs Buy-and-Hold")
    p.add_argument("--train-start", required=True, metavar="YYYY-MM-DD")
    p.add_argument("--train-end", required=True, metavar="YYYY-MM-DD")
    p.add_argument("--test-start", required=True, metavar="YYYY-MM-DD")
    p.add_argument("--test-end", required=True, metavar="YYYY-MM-DD")
    args = p.parse_args()
    try:
        ts, te = date.fromisoformat(args.train_start), date.fromisoformat(args.train_end)
        vs, ve = date.fromisoformat(args.test_start), date.fromisoformat(args.test_end)
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)
    run(ts, te, vs, ve)


if __name__ == "__main__":
    main()
