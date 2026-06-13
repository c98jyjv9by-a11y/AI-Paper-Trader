"""
signal_calibration.py — Per-ticker single-name timing, walk-forward calibrated.

Goal: for each ticker INDEPENDENTLY, decide whether an absolute buy/sell signal on
that ticker's own history beats simply buying and holding the same ticker over the
same period — out-of-sample.

Why this module (vs the portfolio backtester):
  * Single-name standalone: fully in or out of ONE ticker, no cross-sectional
    ranking, no daily-trade/exposure caps. Timing skill is not entangled with
    portfolio capacity, so "timing X vs holding X" is a clean comparison.
  * Absolute rules: entry/exit depend only on the ticker's own price history
    (moving averages + trailing stop), not on how it ranks against other names.
  * Walk-forward: parameters are grid-searched on a TRAIN window, then applied to
    the immediately following TEST window. Only TEST (out-of-sample) results are
    reported. This is the disciplined way to "calibrate optimal criteria" without
    the curve-fitting that fitting one full period would produce.

Honesty caveats baked into the report:
  * Few trades per ticker → high variance; a couple of OOS wins can be luck.
  * Multiple testing: scanning ~25 tickers, some beat hold by chance alone.
  * Parameter instability across folds is a red flag that the "optimal" criteria
    are noise, not signal.

Look-ahead: SMAs at bar t use only close[..t]; decisions at close t fill at t+1;
the TEST window is never seen while calibrating. Live paper state (data/) is never
touched — outputs go to reports/ and backtests/ only.

Usage:
    python src/signal_calibration.py --start 2021-06-12 --end 2026-06-12
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
import yaml

sys.path.insert(0, str(Path(__file__).parent))

from backtest import fetch_backtest_data, load_config
from logger import setup_logging

log = logging.getLogger(__name__)

# Walk-forward geometry (trading days).
TRAIN_BARS = 252      # ~1 year calibration window
TEST_BARS = 63        # ~1 quarter out-of-sample
STEP_BARS = 63        # advance one quarter per fold

# Parameter grid for the absolute single-name rule (kept small on purpose).
FAST_WINDOWS = [10, 20]
SLOW_WINDOWS = [50, 100]
TRAILING_STOPS: List[Optional[float]] = [None, 0.10, 0.15]
_ALL_WINDOWS = sorted(set(FAST_WINDOWS + SLOW_WINDOWS))


# ─── Single-name simulator ────────────────────────────────────────────────────


def _simulate(close: np.ndarray, a: int, b: int, sma: Dict[int, np.ndarray],
              fast: int, slow: int, trailing: Optional[float], slippage: float) -> Dict[str, float]:
    """
    Simulate the absolute rule on close[a..b] (decisions at close t, fill at t+1).

    Rule: long when close > SMA(fast) and close > SMA(slow); exit when close < SMA(fast)
    or price falls `trailing` below its peak-since-entry. Starts flat, ends marked to
    market. Returns total_return (vs $1), trade count, and fraction of bars invested.
    """
    sf, ss = sma[fast], sma[slow]
    cash, shares, in_pos, peak = 1.0, 0.0, False, 0.0
    bars_long, trades = 0, 0
    pending: Optional[str] = None
    equity = np.empty(b - a + 1)

    for t in range(a, b + 1):
        # execute pending order at this bar's close
        if pending == "buy" and not in_pos:
            fill = close[t] * (1 + slippage)
            shares, cash, in_pos, peak = cash / fill, 0.0, True, close[t]
            trades += 1
        elif pending == "sell" and in_pos:
            fill = close[t] * (1 - slippage)
            cash, shares, in_pos = shares * fill, 0.0, False
            trades += 1
        pending = None

        if in_pos:
            peak = max(peak, close[t])
            bars_long += 1
        equity[t - a] = cash + (shares * close[t] if in_pos else 0.0)

        if t < b:  # decide for next bar using only data up to t
            trend_ok = (not np.isnan(ss[t]) and not np.isnan(sf[t])
                        and close[t] > sf[t] and close[t] > ss[t])
            if not in_pos and trend_ok:
                pending = "buy"
            elif in_pos:
                broke = (not np.isnan(sf[t])) and close[t] < sf[t]
                trail = trailing is not None and peak > 0 and close[t] <= peak * (1 - trailing)
                if broke or trail:
                    pending = "sell"

    n = max(1, b - a + 1)
    daily = equity[1:] / equity[:-1] - 1.0 if len(equity) > 1 else np.array([])
    return {"total_return": equity[-1] - 1.0, "n_trades": trades,
            "frac_long": bars_long / n, "daily_returns": daily}


# ─── Risk metrics on a daily-return series ────────────────────────────────────


def _sharpe(daily: np.ndarray) -> Optional[float]:
    d = daily[~np.isnan(daily)]
    if len(d) < 2 or d.std() == 0:
        return None
    return float(d.mean() / d.std() * np.sqrt(252))


def _max_drawdown(daily: np.ndarray) -> Optional[float]:
    d = daily[~np.isnan(daily)]
    if len(d) == 0:
        return None
    level = np.cumprod(1.0 + d)
    peak = np.maximum.accumulate(level)
    return float(((level - peak) / peak).min())


def _annualized(total_return: float, n_bars: int) -> Optional[float]:
    if total_return is None or n_bars <= 0:
        return None
    base = 1.0 + total_return
    if base <= 0:
        return -1.0
    return base ** (252.0 / n_bars) - 1.0


def _calmar(total_return: float, n_bars: int, max_dd: Optional[float]) -> Optional[float]:
    ann = _annualized(total_return, n_bars)
    if ann is None or max_dd is None or max_dd == 0:
        return None
    return ann / abs(max_dd)


def _hold_return(close: np.ndarray, a: int, b: int) -> float:
    p0, pb = close[a], close[b]
    if p0 <= 0 or np.isnan(p0) or np.isnan(pb):
        return float("nan")
    return float(pb / p0 - 1.0)


# ─── Walk-forward per ticker ──────────────────────────────────────────────────


OBJECTIVES = ("total_return", "sharpe", "calmar")


def _objective_value(res: Dict[str, float], objective: str) -> float:
    """Score a single train-window simulation by the chosen calibration objective."""
    daily = res["daily_returns"]
    if objective == "sharpe":
        v = _sharpe(daily)
        return v if v is not None else -np.inf
    if objective == "calmar":
        v = _calmar(res["total_return"], len(daily) + 1, _max_drawdown(daily))
        return v if v is not None else -np.inf
    return res["total_return"]


def _build_folds(first: int, last: int) -> List[Tuple[int, int, int, int]]:
    """(train_a, train_b, test_a, test_b) folds within [first, last]."""
    folds = []
    train_a = first
    while True:
        train_b = train_a + TRAIN_BARS - 1
        test_a = train_b + 1
        test_b = test_a + TEST_BARS - 1
        if test_b > last:
            break
        folds.append((train_a, train_b, test_a, test_b))
        train_a += STEP_BARS
    return folds


def walk_forward_ticker(close: np.ndarray, sma: Dict[int, np.ndarray],
                        first_valid: int, last: int, slippage: float,
                        objective: str = "total_return") -> Optional[Dict[str, Any]]:
    """
    Calibrate the rule on each train window (maximising `objective`), apply to the
    next (OOS) test window, and compound the OOS test returns. Compare to
    buy-and-hold over the same OOS span. objective ∈ OBJECTIVES.
    """
    grid = [(f, s, t) for f, s, t in product(FAST_WINDOWS, SLOW_WINDOWS, TRAILING_STOPS)]
    # need slow-window warmup before the first decision
    start = max(first_valid, max(SLOW_WINDOWS))
    folds = _build_folds(start, last)
    if not folds:
        return None

    chosen: List[Tuple[int, int, Optional[float]]] = []
    n_trades_oos = 0
    frac_long_oos: List[float] = []
    test_wins = 0
    oos_daily_parts: List[np.ndarray] = []

    for (tr_a, tr_b, te_a, te_b) in folds:
        # grid search on TRAIN only, maximising the chosen objective
        best, best_score = None, -np.inf
        for (f, s, ts) in grid:
            r = _simulate(close, tr_a, tr_b, sma, f, s, ts, slippage)
            score = _objective_value(r, objective)
            if score > best_score:
                best, best_score = (f, s, ts), score
        # apply best params to TEST (out-of-sample)
        res = _simulate(close, te_a, te_b, sma, best[0], best[1], best[2], slippage)
        chosen.append(best)
        n_trades_oos += int(res["n_trades"])
        frac_long_oos.append(res["frac_long"])
        oos_daily_parts.append(res["daily_returns"])
        if res["total_return"] > _hold_return(close, te_a, te_b):
            test_wins += 1

    oos_first, oos_last = folds[0][2], folds[-1][3]
    timed_daily = np.concatenate(oos_daily_parts) if oos_daily_parts else np.array([])
    timed_total = float(np.prod(1.0 + timed_daily) - 1.0) if timed_daily.size else 0.0
    hold_total = _hold_return(close, oos_first, oos_last)

    # buy-and-hold daily series over the OOS span (for risk-adjusted comparison)
    hold_close = close[oos_first: oos_last + 1]
    hold_daily = hold_close[1:] / hold_close[:-1] - 1.0 if len(hold_close) > 1 else np.array([])
    avg_frac_long = float(np.mean(frac_long_oos)) if frac_long_oos else 0.0
    n_oos = len(timed_daily) + 1

    # parameter stability: how often the single most-common param set was chosen
    from collections import Counter
    counts = Counter(chosen)
    mode_params, mode_n = counts.most_common(1)[0]
    stability = mode_n / len(chosen)

    timed_dd = _max_drawdown(timed_daily)
    hold_dd = _max_drawdown(hold_daily)
    exposure_matched_return = (avg_frac_long * hold_total) if hold_total is not None and not np.isnan(hold_total) else None

    return {
        "n_folds": len(folds),
        "timed_return": timed_total,
        "hold_return": hold_total,
        "outperformance": (timed_total - hold_total) if not np.isnan(hold_total) else None,
        "test_win_rate": test_wins / len(folds),
        "oos_trades": n_trades_oos,
        "avg_frac_long": avg_frac_long,
        "param_stability": stability,
        "modal_params": {"fast": mode_params[0], "slow": mode_params[1], "trailing": mode_params[2]},
        # risk-adjusted + exposure-matched
        "timed_sharpe": _sharpe(timed_daily),
        "hold_sharpe": _sharpe(hold_daily),
        "timed_max_drawdown": timed_dd,
        "hold_max_drawdown": hold_dd,
        "timed_calmar": _calmar(timed_total, n_oos, timed_dd),
        "hold_calmar": _calmar(hold_total, n_oos, hold_dd) if hold_total is not None else None,
        "exposure_matched_return": exposure_matched_return,
        "beats_exposure_matched": (exposure_matched_return is not None and timed_total > exposure_matched_return),
    }


# ─── Universe driver ──────────────────────────────────────────────────────────


def calibrate_universe(price_data: pd.DataFrame, tickers: List[str],
                       start_date: date, end_date: date, slippage: float,
                       objective: str = "total_return") -> List[Dict[str, Any]]:
    close_panel = price_data["Close"]
    all_ts = close_panel.index
    # restrict decisions to the requested [start, end] window
    in_window = [(i, ts) for i, ts in enumerate(all_ts) if start_date <= ts.date() <= end_date]
    if not in_window:
        return []
    win_first, win_last = in_window[0][0], in_window[-1][0]

    results: List[Dict[str, Any]] = []
    for ticker in tickers:
        if ticker not in close_panel.columns:
            continue
        series = close_panel[ticker]
        close = series.to_numpy()
        # precompute SMAs over the full history (so warmup is available)
        sma = {w: series.rolling(w).mean().to_numpy() for w in _ALL_WINDOWS}
        # first bar with a real price at/after window start
        valid = np.where(~np.isnan(close[: win_last + 1]))[0]
        valid = valid[valid >= 0]
        if valid.size == 0:
            continue
        first_valid = max(win_first, int(valid[0]))
        res = walk_forward_ticker(close, sma, first_valid, win_last, slippage, objective)
        if res is None:
            log.info("%s: not enough history for walk-forward — skipped", ticker)
            continue
        res["ticker"] = ticker
        results.append(res)
    return results


# ─── Evaluate fixed criteria (no re-fitting) ──────────────────────────────────


def evaluate_criteria(price_data: pd.DataFrame, criteria: Dict[str, Tuple[int, int, Optional[float]]],
                      start_date: date, end_date: date, slippage: float) -> List[Dict[str, Any]]:
    """
    Apply a FIXED per-ticker rule (fast, slow, trailing) over [start, end] and score
    each ticker timed-vs-buy-and-hold. No parameter search — this evaluates criteria
    exactly as given (e.g. the seed, or a calibrated set on a held-out window).
    """
    close_panel = price_data["Close"]
    all_ts = close_panel.index
    in_window = [(i, ts) for i, ts in enumerate(all_ts) if start_date <= ts.date() <= end_date]
    if not in_window:
        return []
    win_first, win_last = in_window[0][0], in_window[-1][0]

    results: List[Dict[str, Any]] = []
    for ticker, (fast, slow, trailing) in criteria.items():
        if ticker not in close_panel.columns:
            continue
        series = close_panel[ticker]
        close = series.to_numpy()
        sma = {w: series.rolling(w).mean().to_numpy() for w in {fast, slow}}
        valid = np.where(~np.isnan(close[: win_last + 1]))[0]
        if valid.size == 0:
            continue
        a = max(win_first, int(valid[0]), slow)   # warm up the slow MA before deciding
        b = win_last
        if b - a < 5:
            continue

        res = _simulate(close, a, b, sma, fast, slow, trailing, slippage)
        timed_total, timed_daily, frac = res["total_return"], res["daily_returns"], res["frac_long"]
        n_oos = len(timed_daily) + 1
        hold_total = _hold_return(close, a, b)
        hc = close[a: b + 1]
        hold_daily = hc[1:] / hc[:-1] - 1.0 if len(hc) > 1 else np.array([])
        timed_dd, hold_dd = _max_drawdown(timed_daily), _max_drawdown(hold_daily)
        exp = (frac * hold_total) if hold_total is not None and not np.isnan(hold_total) else None

        results.append({
            "ticker": ticker,
            "timed_return": timed_total,
            "hold_return": hold_total,
            "outperformance": (timed_total - hold_total) if not np.isnan(hold_total) else None,
            "oos_trades": res["n_trades"],
            "avg_frac_long": frac,
            "timed_sharpe": _sharpe(timed_daily),
            "hold_sharpe": _sharpe(hold_daily),
            "timed_max_drawdown": timed_dd,
            "hold_max_drawdown": hold_dd,
            "timed_calmar": _calmar(timed_total, n_oos, timed_dd),
            "hold_calmar": _calmar(hold_total, n_oos, hold_dd) if hold_total is not None else None,
            "exposure_matched_return": exp,
            "beats_exposure_matched": (exp is not None and timed_total > exp),
            "modal_params": {"fast": fast, "slow": slow, "trailing": trailing},
            "param_stability": None, "test_win_rate": None, "n_folds": None,
        })
    return results


# ─── Reporting ────────────────────────────────────────────────────────────────


def _pct(v: Optional[float], d: str = "—") -> str:
    return d if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v * 100:+.2f}%"


def _num(v: Optional[float], d: str = "—") -> str:
    return d if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v:.2f}"


def render_report(results: List[Dict[str, Any]], run_date: date,
                  start_date: date, end_date: date, objective: str = "total_return") -> str:
    valid = [r for r in results if r.get("outperformance") is not None]
    n = len(valid)
    n_beat = sum(1 for r in valid if r["outperformance"] > 0)
    median_out = float(np.median([r["outperformance"] for r in valid])) if valid else None

    lines: List[str] = [
        "# Per-Ticker Signal Calibration — Timing vs Buy-and-Hold",
        f"**Period:** {start_date} → {end_date}  |  **Generated:** {run_date.isoformat()}",
        "",
        f"> **Out-of-sample, walk-forward.** Calibration objective: **{objective}** (the rule chosen "
        "on each 252-day train window maximises this), reported ONLY on the following 63-day test "
        "window, stepped quarterly. Comparison is timed vs buy-and-hold of the same ticker over the "
        "same out-of-sample span.",
        "",
        "---",
        "",
        "## Does timing beat holding? (out-of-sample)",
        "",
        f"- **{n_beat} / {n} tickers** had positive OOS timed-minus-hold outperformance.",
        f"- Median OOS outperformance: **{_pct(median_out)}**.",
        "",
        "> ⚠️ With ~25 names tested, roughly half would beat hold by chance even with no skill. "
        "Treat a result as real only if outperformance is large, the per-fold parameters are "
        "stable, and it survives a fresh out-of-sample period. Few trades per ticker = high variance.",
        "",
        "## Per-Ticker Results (out-of-sample)",
        "",
        "| Ticker | Timed Ret | Hold Ret | Outperf | Test-win rate | OOS Trades | % In-Market | Param Stability | Modal Rule (fast/slow/trail) |",
        "|--------|-----------|----------|---------|---------------|------------|-------------|-----------------|------------------------------|",
    ]
    for r in sorted(valid, key=lambda x: (x["outperformance"] or -9), reverse=True):
        mp = r["modal_params"]
        trail = "none" if mp["trailing"] is None else f"{mp['trailing']:.0%}"
        lines.append(
            f"| {r['ticker']} | {_pct(r['timed_return'])} | {_pct(r['hold_return'])} "
            f"| {_pct(r['outperformance'])} | {_pct(r['test_win_rate'])} | {r['oos_trades']} "
            f"| {_pct(r['avg_frac_long'])} | {_pct(r['param_stability'])} "
            f"| {mp['fast']}/{mp['slow']}/{trail} |"
        )
    lines.append("")

    # Risk-adjusted & exposure-matched comparison
    n_sharpe = sum(1 for r in valid if r.get("timed_sharpe") is not None
                   and r.get("hold_sharpe") is not None and r["timed_sharpe"] > r["hold_sharpe"])
    n_expm = sum(1 for r in valid if r.get("beats_exposure_matched"))
    lines += [
        "## Risk-Adjusted & Exposure-Matched (out-of-sample)",
        "",
        "_A timing strategy sits in cash part of the time, so compare risk-adjusted and against an "
        "**exposure-matched** hold (same % time in market, rest cash). 'Beats exp-matched' is the fair "
        "test of whether *when* you were in beat simply being in that fraction of the time._",
        "",
        f"- **{n_sharpe} / {n}** tickers had a higher timed Sharpe than buy-and-hold.",
        f"- **{n_expm} / {n}** tickers beat their exposure-matched hold (the fair return test).",
        "",
        "| Ticker | Timed Ret | Exp-Matched Hold | Beats Exp-Matched | Timed Sharpe | Hold Sharpe | Timed MaxDD | Hold MaxDD | Timed Calmar | Hold Calmar |",
        "|--------|-----------|------------------|-------------------|--------------|-------------|-------------|------------|--------------|-------------|",
    ]
    for r in sorted(valid, key=lambda x: (x["outperformance"] or -9), reverse=True):
        lines.append(
            f"| {r['ticker']} | {_pct(r['timed_return'])} | {_pct(r.get('exposure_matched_return'))} "
            f"| {'✅' if r.get('beats_exposure_matched') else '❌'} | {_num(r.get('timed_sharpe'))} "
            f"| {_num(r.get('hold_sharpe'))} | {_pct(r.get('timed_max_drawdown'))} "
            f"| {_pct(r.get('hold_max_drawdown'))} | {_num(r.get('timed_calmar'))} "
            f"| {_num(r.get('hold_calmar'))} |"
        )
    lines.append("")

    # Interpretation
    lines += ["## Interpretation", ""]
    if valid:
        stable_winners = [r for r in valid if r["outperformance"] > 0.05 and r["param_stability"] >= 0.5]
        lines.append(
            f"- **{n_beat}/{n}** beat buy-and-hold OOS; median edge {_pct(median_out)}. "
            + ("That's around coin-flip — no broad evidence that this timing rule adds value over holding."
               if n and abs(n_beat / n - 0.5) < 0.15 else
               ("A majority beat holding, but see the multiple-testing caveat." if n_beat > n / 2 else
                "Most names did worse timed than held — the rule mostly costs return via whipsaws/cash drag."))
        )
        if stable_winners:
            names = ", ".join(f"`{r['ticker']}`" for r in stable_winners)
            lines.append(
                f"- **Stable candidates** (>+5% OOS edge AND ≥50% param stability): {names}. These are the "
                "only ones worth a dedicated out-of-sample retest; everything else is likely noise."
            )
        else:
            lines.append(
                "- **No ticker** combined a >+5% OOS edge with stable per-fold parameters. That is the "
                "signature of curve-fitting: the 'best' train parameters keep changing and don't carry "
                "to test data — i.e. there is no reliable per-ticker timing edge here."
            )
        n_expm = sum(1 for r in valid if r.get("beats_exposure_matched"))
        n_sharpe = sum(1 for r in valid if r.get("timed_sharpe") is not None
                       and r.get("hold_sharpe") is not None and r["timed_sharpe"] > r["hold_sharpe"])
        lines.append(
            f"- **Fair (exposure-matched) verdict:** {n_expm}/{n} names beat their exposure-matched hold and "
            f"{n_sharpe}/{n} improved Sharpe vs holding. "
            + ("Even adjusting for time-in-market, the timing rule does not broadly add value here."
               if n and n_expm <= n / 2 else
               "A majority cleared the exposure-matched bar — worth an out-of-sample retest, mindful of multiple testing.")
        )
    else:
        lines.append("- Not enough history in the window to calibrate any ticker.")
    lines += [
        "",
        "- **Next:** re-run on a later, non-overlapping window. A genuine per-ticker edge persists; "
        "an overfit one evaporates. All results here are still in-sample at the universe-selection level "
        "(we chose these tickers), so treat survivors as hypotheses, not conclusions.",
        "",
    ]
    return "\n".join(lines)


def render_evaluation(results: List[Dict[str, Any]], criteria_label: str,
                      run_date: date, start_date: date, end_date: date) -> str:
    valid = [r for r in results if r.get("outperformance") is not None]
    n = len(valid)
    n_beat = sum(1 for r in valid if r["outperformance"] > 0)
    n_expm = sum(1 for r in valid if r.get("beats_exposure_matched"))
    median_out = float(np.median([r["outperformance"] for r in valid])) if valid else None

    lines: List[str] = [
        "# Per-Ticker Criteria Evaluation — Timing vs Buy-and-Hold",
        f"**Criteria:** `{criteria_label}`  |  **Period:** {start_date} → {end_date}  "
        f"|  **Generated:** {run_date.isoformat()}",
        "",
        "> Applies a **fixed** per-ticker rule as given — **no parameter search**. Use a period "
        "**disjoint** from where the criteria were calibrated for a true out-of-sample read; over "
        "the calibration period this is in-sample.",
        "",
        "---",
        "",
        "## Summary",
        "",
        f"- **{n_beat} / {n}** tickers beat buy-and-hold (total return).",
        f"- **{n_expm} / {n}** beat their exposure-matched hold (the fair test).",
        f"- Median outperformance: **{_pct(median_out)}**.",
        "",
        "## Per-Ticker (fixed criteria)",
        "",
        "| Ticker | Rule (fast/slow/trail) | Timed Ret | Hold Ret | Outperf | Beats Exp-Matched | Timed Sharpe | Hold Sharpe | Timed MaxDD | Hold MaxDD | % In-Mkt | Trades |",
        "|--------|------------------------|-----------|----------|---------|-------------------|--------------|-------------|-------------|------------|----------|--------|",
    ]
    for r in sorted(valid, key=lambda x: (x["outperformance"] or -9), reverse=True):
        mp = r["modal_params"]
        trail = "none" if mp["trailing"] is None else f"{mp['trailing']:.0%}"
        lines.append(
            f"| {r['ticker']} | {mp['fast']}/{mp['slow']}/{trail} | {_pct(r['timed_return'])} "
            f"| {_pct(r['hold_return'])} | {_pct(r['outperformance'])} "
            f"| {'✅' if r.get('beats_exposure_matched') else '❌'} | {_num(r.get('timed_sharpe'))} "
            f"| {_num(r.get('hold_sharpe'))} | {_pct(r.get('timed_max_drawdown'))} "
            f"| {_pct(r.get('hold_max_drawdown'))} | {_pct(r['avg_frac_long'])} | {r['oos_trades']} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        f"- {n_beat}/{n} beat hold and {n_expm}/{n} cleared the exposure-matched bar. "
        + ("If this window is disjoint from calibration, the survivors are the criteria worth keeping."
           if n else "No tickers had enough data to evaluate."),
        "- Compare this against the **seed** criteria over the same window to see whether calibration "
        "actually improved on the broad-bucket defaults.",
        "",
    ]
    return "\n".join(lines)


def results_csv(results: List[Dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for r in results:
        mp = r.get("modal_params", {})
        rows.append({
            "ticker": r.get("ticker"),
            "n_folds": r.get("n_folds"),
            "timed_return": r.get("timed_return"),
            "hold_return": r.get("hold_return"),
            "outperformance": r.get("outperformance"),
            "test_win_rate": r.get("test_win_rate"),
            "oos_trades": r.get("oos_trades"),
            "avg_frac_long": r.get("avg_frac_long"),
            "param_stability": r.get("param_stability"),
            "modal_fast": mp.get("fast"),
            "modal_slow": mp.get("slow"),
            "modal_trailing": mp.get("trailing"),
            "timed_sharpe": r.get("timed_sharpe"),
            "hold_sharpe": r.get("hold_sharpe"),
            "timed_max_drawdown": r.get("timed_max_drawdown"),
            "hold_max_drawdown": r.get("hold_max_drawdown"),
            "timed_calmar": r.get("timed_calmar"),
            "hold_calmar": r.get("hold_calmar"),
            "exposure_matched_return": r.get("exposure_matched_return"),
            "beats_exposure_matched": r.get("beats_exposure_matched"),
        })
    return pd.DataFrame(rows)


def export_criteria(results: List[Dict[str, Any]], out_path: Path, run_date: date) -> str:
    """
    Write the per-ticker calibrated timing rule (modal fast/slow/trailing) to a YAML
    criteria config. `candidate: true` means the ticker beat its exposure-matched hold
    AND had stable parameters across folds — the only ones worth an OOS retest.
    """
    lines = [
        "# Per-ticker single-name timing criteria — DATA-DERIVED via walk-forward calibration.",
        f"# Generated: {run_date.isoformat()}  (IN-SAMPLE at universe-selection level — retest OOS).",
        "# Rule: long when close > SMA(fast) and close > SMA(slow); exit when close < SMA(fast)",
        "#       or price falls `trailing` below its peak since entry (trailing: null disables).",
        "# candidate: true  =>  beat exposure-matched hold AND param_stability >= 0.50.",
        "ticker_timing_criteria:",
    ]
    for r in sorted(results, key=lambda x: (x.get("outperformance") or -9), reverse=True):
        mp = r.get("modal_params", {})
        trailing = "null" if mp.get("trailing") is None else f"{mp['trailing']}"
        candidate = bool(r.get("beats_exposure_matched") and (r.get("param_stability") or 0) >= 0.5)
        lines.append(
            f"  {r['ticker']}: {{fast: {mp.get('fast')}, slow: {mp.get('slow')}, trailing: {trailing}, "
            f"candidate: {str(candidate).lower()}, param_stability: {round(r.get('param_stability') or 0, 2)}, "
            f"timed_return: {round(r.get('timed_return') or 0, 4)}, "
            f"hold_return: {round(r.get('hold_return') or 0, 4)}}}"
        )
    out_path.write_text("\n".join(lines) + "\n")
    return str(out_path)


def load_criteria(path: Path) -> Dict[str, Tuple[int, int, Optional[float]]]:
    """Read a ticker_timing_criteria YAML into {ticker: (fast, slow, trailing)}."""
    data = yaml.safe_load(Path(path).read_text()) or {}
    crit = data.get("ticker_timing_criteria", {}) or {}
    out: Dict[str, Tuple[int, int, Optional[float]]] = {}
    for ticker, spec in crit.items():
        out[ticker] = (int(spec["fast"]), int(spec["slow"]), spec.get("trailing"))
    return out


def save_outputs(report: str, csv_df: pd.DataFrame, reports_dir: Path,
                 backtests_dir: Path, run_date: date) -> Dict[str, str]:
    reports_dir.mkdir(parents=True, exist_ok=True)
    backtests_dir.mkdir(parents=True, exist_ok=True)
    tag = run_date.isoformat()
    md = reports_dir / f"signal_calibration_{tag}.md"
    md.write_text(report)
    csv = backtests_dir / f"signal_calibration_{tag}.csv"
    csv_df.to_csv(csv, index=False)
    return {"report": str(md), "csv": str(csv)}


# ─── CLI ──────────────────────────────────────────────────────────────────────


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="AI Paper Trader — Per-Ticker Signal Calibration")
    p.add_argument("--start", required=True, metavar="YYYY-MM-DD")
    p.add_argument("--end", required=True, metavar="YYYY-MM-DD")
    p.add_argument("--objective", default="total_return", choices=OBJECTIVES,
                   help="What the train-window grid search maximises (default: total_return)")
    return p.parse_args()


def run(start_date: date, end_date: date, objective: str = "total_return") -> Dict[str, str]:
    """Calibrate per-ticker timing rules walk-forward and write outputs."""
    setup_logging()
    run_date = date.today()
    root = Path(__file__).parent.parent
    config = load_config(root / "config")
    slippage = config["risk"].get("slippage", 0.001)

    log.info("=== Per-Ticker Signal Calibration (walk-forward, objective=%s) ===", objective)
    price_data = fetch_backtest_data(config["tickers"], start_date, end_date)
    results = calibrate_universe(price_data, config["tickers"], start_date, end_date, slippage, objective)
    report = render_report(results, run_date, start_date, end_date, objective)
    csv_df = results_csv(results)
    paths = save_outputs(report, csv_df, root / "reports", root / "backtests", run_date)
    # Data-derived per-ticker criteria config (dated; never overwrites the seed).
    criteria_path = root / "config" / f"ticker_timing_criteria_{run_date.isoformat()}.yaml"
    paths["criteria"] = export_criteria(results, criteria_path, run_date)

    print()
    valid = [r for r in results if r.get("outperformance") is not None]
    n_beat = sum(1 for r in valid if r["outperformance"] > 0)
    n_cand = sum(1 for r in valid if r.get("beats_exposure_matched") and (r.get("param_stability") or 0) >= 0.5)
    print(f"  Objective          : {objective}")
    print(f"  Tickers calibrated : {len(valid)}")
    print(f"  Beat buy-and-hold  : {n_beat}/{len(valid)} (out-of-sample)")
    print(f"  Candidate criteria : {n_cand}/{len(valid)} (beat exp-matched + stable params)")
    print()
    print(f"  Report   : {paths['report']}")
    print(f"  CSV      : {paths['csv']}")
    print(f"  Criteria : {paths['criteria']}")
    print("  NOTE: walk-forward OOS, but universe selection is in-sample — retest on a fresh period.")
    print()
    return paths


def run_evaluate(start_date: date, end_date: date, criteria_path: Path) -> Dict[str, str]:
    """Apply a fixed criteria file over [start, end] and score timed vs buy-and-hold."""
    setup_logging()
    run_date = date.today()
    root = Path(__file__).parent.parent
    config = load_config(root / "config")
    slippage = config["risk"].get("slippage", 0.001)

    criteria = load_criteria(criteria_path)
    if not criteria:
        print(f"Error: no ticker_timing_criteria found in {criteria_path}")
        sys.exit(1)

    log.info("=== Criteria Evaluation (fixed rules) ===")
    price_data = fetch_backtest_data(list(criteria), start_date, end_date)
    results = evaluate_criteria(price_data, criteria, start_date, end_date, slippage)
    report = render_evaluation(results, criteria_path.name, run_date, start_date, end_date)
    csv_df = results_csv(results)

    (root / "reports").mkdir(parents=True, exist_ok=True)
    (root / "backtests").mkdir(parents=True, exist_ok=True)
    tag = run_date.isoformat()
    md = root / "reports" / f"criteria_evaluation_{tag}.md"
    md.write_text(report)
    csv = root / "backtests" / f"criteria_evaluation_{tag}.csv"
    csv_df.to_csv(csv, index=False)

    valid = [r for r in results if r.get("outperformance") is not None]
    n_beat = sum(1 for r in valid if r["outperformance"] > 0)
    n_expm = sum(1 for r in valid if r.get("beats_exposure_matched"))
    print()
    print(f"  Criteria : {criteria_path}")
    print(f"  Evaluated: {len(valid)} tickers")
    print(f"  Beat hold: {n_beat}/{len(valid)}  |  beat exposure-matched: {n_expm}/{len(valid)}")
    print()
    print(f"  Report : {md}")
    print(f"  CSV    : {csv}")
    print("  NOTE: out-of-sample only if this window is disjoint from where the criteria were calibrated.")
    print()
    return {"report": str(md), "csv": str(csv)}


def main() -> None:
    args = _parse_args()
    try:
        start_date = date.fromisoformat(args.start)
        end_date = date.fromisoformat(args.end)
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)
    if end_date <= start_date:
        print("Error: --end must be after --start")
        sys.exit(1)
    run(start_date, end_date, args.objective)


if __name__ == "__main__":
    main()
