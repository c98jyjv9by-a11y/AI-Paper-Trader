"""
adaptive_backtest.py — Per-ticker rotating-signal backtest.

Instead of one fixed signal, this re-evaluates EACH ticker every week: which of a
small set of signals has *recently* worked on that ticker (over a trailing window)?
A ticker is held only when its recently-best signal is currently ON and cleared a
minimum edge; otherwise it sits in cash. The focus tickers and each ticker's
assigned signal therefore drift over the run.

Honest caveat (surfaced in the report, not hidden): weekly re-fitting on a ~63-day
window is small-sample and high-turnover — this variant tends to look strong
in-sample and bleed after slippage / out-of-sample. The run therefore fully
charges slippage, reports turnover + % time in cash + signal churn, and compares
to SPY / QQQ / equal-weight-hold benchmarks. Validate on a disjoint window before
trusting it.

Look-ahead safety: at each rebalance date T every input uses data ≤ T (signals use
`.shift(1)` so the decision precedes the return); orders fill at T+1's close.
Live paper state (data/) is never touched; outputs go to reports/ and backtests/.

    python run.py adaptive --start 2021-06-13 --end 2026-06-13
"""
import argparse
import logging
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from backtest import (
    _bench_return,
    _equal_weight_hold_return,
    compute_metrics,
    fetch_backtest_data,
    generate_backtest_report,
    load_config,
    resolve_max_position_pct,
    save_backtest_outputs,
)
from diagnostics import compute_diagnostics, diagnostics_csv, render_diagnostics_md
from risk import apply_slippage
from logger import setup_logging

log = logging.getLogger(__name__)

# Defaults (overridable via CLI / config["adaptive"]).
_DEFAULTS = {"rebalance_days": 5, "lookback_days": 63, "top_n": 5, "min_edge": 0.0}
_BENCH = ("SPY", "QQQ")


# ─── Per-ticker candidate signals (binary long/flat, vectorized) ──────────────


def build_signals(close: pd.DataFrame, volume: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Boolean [dates × tickers] long-eligibility frames. Higher set = expected long."""
    c = close
    return {
        "trend_50": c > c.rolling(50).mean(),
        "trend_20": c > c.rolling(20).mean(),
        "mom20_pos": c.pct_change(20) > 0,
        "dip_5": c.pct_change(5) < 0,                      # short-term reversal: buy dips
        "near_52w_high": c >= 0.95 * c.rolling(252).max(),
    }


def _recent_edge(sig_on: np.ndarray, fwd1: np.ndarray, a: int, b: int) -> float:
    """Return of 'hold next day when signal ON, else flat' over bars [a, b]."""
    growth = 1.0
    for t in range(a, b + 1):
        if sig_on[t] and not np.isnan(fwd1[t]):
            growth *= (1.0 + fwd1[t])
    return growth - 1.0


def select_targets(signals: Dict[str, np.ndarray], fwd1: Dict[str, np.ndarray],
                   tickers: List[str], t: int, lookback: int, top_n: int,
                   min_edge: float) -> List[Tuple[str, str, float]]:
    """
    At bar t, assign each ticker its recently-best signal and return up to top_n
    qualifying (ticker, assigned_signal, edge) tuples sorted by edge desc.
    A ticker qualifies if its best recent edge > min_edge AND that signal is ON at t.
    """
    a = max(0, t - lookback)
    chosen: List[Tuple[str, str, float]] = []
    for tk in tickers:
        best_sig, best_edge = None, -np.inf
        for name, frame in signals.items():
            on = frame.get(tk)
            if on is None:
                continue
            edge = _recent_edge(on, fwd1[tk], a, t)        # uses on.shift(1) alignment (see run)
            if edge > best_edge:
                best_sig, best_edge = name, edge
        if best_sig is None:
            continue
        currently_on = signals[best_sig][tk][t]
        if best_edge > min_edge and currently_on:
            chosen.append((tk, best_sig, float(best_edge)))
    chosen.sort(key=lambda x: x[2], reverse=True)
    return chosen[:top_n]


# ─── Weekly target-rebalancing loop ───────────────────────────────────────────


def run_adaptive(config: Dict[str, Any], price_data: pd.DataFrame,
                 start_date: date, end_date: date,
                 params: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, List[Dict[str, Any]]]:
    """Returns (trades_df, equity_df, final_positions_df, rotation_log) in the
    standard backtest schema so compute_metrics/report/diagnostics all reuse."""
    tickers: List[str] = config["tickers"]
    slippage = config["risk"]["slippage"]
    stop_loss = config["risk"].get("stop_loss")
    starting = float(config["portfolio"]["starting_value"])
    max_exp = float(config["portfolio"]["max_total_exposure"])
    max_pos = resolve_max_position_pct(config)
    reb, lb = params["rebalance_days"], params["lookback_days"]
    top_n, min_edge = params["top_n"], params["min_edge"]

    close = price_data["Close"]
    volume = price_data["Volume"]
    all_ts = close.index.tolist()
    sim = [ts for ts in all_ts if start_date <= ts.date() <= end_date]
    if not sim:
        raise ValueError(f"No trading days between {start_date} and {end_date}.")
    sim_start = all_ts.index(sim[0])
    bench_start_ts = sim[0]

    # Precompute boolean signal arrays (shifted by 1 so a decision at t uses the
    # signal state observed up to t-1's close → no same-bar look-ahead in the edge).
    raw = build_signals(close, volume)
    sig: Dict[str, Dict[str, np.ndarray]] = {}
    for name, frame in raw.items():
        shifted = frame.shift(1)
        sig[name] = {tk: shifted[tk].to_numpy() for tk in tickers if tk in shifted.columns}
    arrs = {tk: close[tk].to_numpy() for tk in tickers if tk in close.columns}
    fwd1 = {tk: (arrs[tk][1:] / arrs[tk][:-1] - 1.0) if tk in arrs else None for tk in tickers}
    fwd1 = {tk: np.append(v, np.nan) if v is not None else None for tk, v in fwd1.items()}  # align len

    cash = starting
    positions: Dict[str, Dict[str, Any]] = {}      # ticker -> {shares, entry_price, signal}
    pending_buys: List[Tuple[str, int, str]] = []
    pending_sells: List[str] = []
    trades: List[Dict[str, Any]] = []
    equity_rows: List[Dict[str, Any]] = []
    rotation_log: List[Dict[str, Any]] = []
    realized = 0.0

    for offset, bar_ts in enumerate(sim):
        t = sim_start + offset
        bar_date = bar_ts.date()
        today = close.loc[bar_ts]

        # 1. Fill pending sells then buys at today's close + slippage
        for tk in pending_sells:
            if tk in positions and not np.isnan(today.get(tk, np.nan)):
                p = positions.pop(tk)
                sell = apply_slippage(float(today[tk]), "sell", slippage)
                pnl = round((sell - p["entry_price"]) * p["shares"], 2)
                cash += sell * p["shares"]
                realized += pnl
                trades.append({"date": bar_date.isoformat(), "action": "SELL", "ticker": tk,
                               "shares": p["shares"], "price": sell, "trade_value": round(sell * p["shares"], 2),
                               "reason": p.get("exit_reason", "rebalance"), "realized_pnl": pnl,
                               "holding_days": None})
        for tk, shares, signame in pending_buys:
            px = today.get(tk, np.nan)
            if tk not in positions and shares > 0 and not np.isnan(px):
                fill = apply_slippage(float(px), "buy", slippage)
                cost = round(fill * shares, 2)
                if cost <= cash:
                    cash -= cost
                    positions[tk] = {"shares": shares, "entry_price": fill, "signal": signame}
                    trades.append({"date": bar_date.isoformat(), "action": "BUY", "ticker": tk,
                                   "shares": shares, "price": fill, "trade_value": cost,
                                   "reason": f"signal={signame}", "realized_pnl": None, "holding_days": 0})
        pending_buys, pending_sells = [], []

        # 2. Mark to market
        invested = sum(p["shares"] * float(today[tk]) for tk, p in positions.items()
                       if not np.isnan(today.get(tk, np.nan)))
        port_val = cash + invested

        # 3. Stop-loss safety (between rebalances)
        if stop_loss:
            for tk, p in list(positions.items()):
                px = today.get(tk, np.nan)
                if not np.isnan(px) and float(px) <= p["entry_price"] * (1 - stop_loss):
                    p["exit_reason"] = "stop_loss"
                    pending_sells.append(tk)

        # 4. Weekly rebalance → new target set
        is_reb = (offset % reb == 0)
        if is_reb and t + 1 < len(all_ts):
            targets = select_targets(sig, fwd1, tickers, t, lb, top_n, min_edge)
            target_map = {tk: s for tk, s, _ in targets}
            rotation_log.append({"date": bar_date.isoformat(), "n_held_target": len(targets),
                                 "assignments": dict(sorted({tk: s for tk, s, _ in targets}.items()))})
            # sell held names not in target (and not already pending stop-sell)
            for tk in list(positions):
                if tk not in target_map and tk not in pending_sells:
                    positions[tk]["exit_reason"] = "rebalance"
                    pending_sells.append(tk)
            # buy new target names, equal-weight within exposure cap
            held_after = [tk for tk in positions if tk not in pending_sells]
            slots = max(0, top_n - len(held_after))
            reserve = sum(positions[tk]["shares"] * float(today[tk]) for tk in held_after
                          if not np.isnan(today.get(tk, np.nan)))
            for tk, signame, _ in targets:
                if tk in positions or slots <= 0:
                    continue
                px = today.get(tk, np.nan)
                if np.isnan(px) or px <= 0:
                    continue
                pct = min(max_pos, max(0.0, max_exp - reserve / port_val) if port_val > 0 else 0.0)
                shares = int((port_val * min(max_pos, pct)) / float(px))
                if shares <= 0:
                    continue
                pending_buys.append((tk, shares, signame))
                reserve += shares * float(px)
                slots -= 1

        # 5. Equity row (standard schema + benchmark columns)
        unreal = sum((float(today[tk]) - p["entry_price"]) * p["shares"]
                     for tk, p in positions.items() if not np.isnan(today.get(tk, np.nan)))
        equity_rows.append({
            "date": bar_date.isoformat(), "cash": round(cash, 2),
            "open_positions_value": round(invested, 2), "total_portfolio_value": round(port_val, 2),
            "realized_pnl_to_date": round(realized, 2), "unrealized_pnl": round(unreal, 2),
            "daily_return": None, "cumulative_return": None,
            "spy_cumulative_return": _bench_return(close, "SPY", bar_ts, bench_start_ts),
            "qqq_cumulative_return": _bench_return(close, "QQQ", bar_ts, bench_start_ts),
            "equal_weight_cumulative_return": _equal_weight_hold_return(close, tickers, bar_ts, bench_start_ts),
        })

    trades_df = pd.DataFrame(trades)
    equity_df = pd.DataFrame(equity_rows)
    if not equity_df.empty:
        equity_df["daily_return"] = equity_df["total_portfolio_value"].pct_change().round(6)
        equity_df["cumulative_return"] = (equity_df["total_portfolio_value"] / starting - 1).round(6)

    final_positions = pd.DataFrame([
        {"ticker": tk, "shares": p["shares"], "entry_price": p["entry_price"],
         "entry_date": None, "current_price": float(close[tk].loc[sim[-1]]),
         "highest_price": p["entry_price"], "lowest_price": p["entry_price"]}
        for tk, p in positions.items() if tk in close.columns
    ], columns=["ticker", "shares", "entry_price", "entry_date", "current_price",
                "highest_price", "lowest_price"])

    return trades_df, equity_df, final_positions, rotation_log


# ─── Rotation-log report section ──────────────────────────────────────────────


def rotation_section(rotation_log: List[Dict[str, Any]], equity_df: pd.DataFrame,
                     trades_df: pd.DataFrame, params: Dict[str, Any]) -> str:
    from collections import Counter
    lines = ["## Signal Rotation Log", ""]
    if not rotation_log:
        return "\n".join(lines + ["_No rebalances._", ""])

    sig_counts: Counter = Counter()
    held_counts: List[int] = []
    for r in rotation_log:
        held_counts.append(r["n_held_target"])
        sig_counts.update(r["assignments"].values())
    n_reb = len(rotation_log)
    cash_pct = (equity_df["open_positions_value"] == 0).mean() if not equity_df.empty else 0.0
    avg_held = float(np.mean(held_counts)) if held_counts else 0.0
    buy_tv = float(trades_df.loc[trades_df["action"] == "BUY", "trade_value"].sum()) if not trades_df.empty else 0.0
    start_val = float(equity_df["total_portfolio_value"].iloc[0]) if not equity_df.empty else 1.0
    turnover = buy_tv / start_val if start_val else 0.0

    lines += [
        f"_{params['rebalance_days']}-day rebalance, {params['lookback_days']}-day lookback, "
        f"top {params['top_n']}, min edge {params['min_edge']:+.1%}._", "",
        "| Metric | Value |", "|--------|-------|",
        f"| Rebalances | {n_reb} |",
        f"| Avg names held (target) | {avg_held:.1f} / {params['top_n']} |",
        f"| Days fully in cash | {cash_pct * 100:.1f}% |",
        f"| Cumulative turnover (buys ÷ start) | {turnover:.1f}× |",
        "",
        "**Signal usage (how often each was the assigned signal):**", "",
        "| Signal | Times chosen | Share |", "|--------|--------------|-------|",
    ]
    total = sum(sig_counts.values()) or 1
    for name, n in sig_counts.most_common():
        lines.append(f"| {name} | {n} | {n / total * 100:.0f}% |")
    # sample of the rotation timeline (first/last few rebalances)
    sample = rotation_log[:3] + (rotation_log[-2:] if len(rotation_log) > 5 else [])
    lines += ["", "**Sample rotation timeline (date → ticker:signal):**", ""]
    for r in sample:
        amap = ", ".join(f"{tk}:{s}" for tk, s in r["assignments"].items()) or "(all cash)"
        lines.append(f"- {r['date']} — {amap}")
    lines.append("")
    return "\n".join(lines)


# ─── Runner ───────────────────────────────────────────────────────────────────


def _pct(v: Optional[float], d: str = "—") -> str:
    return d if v is None else f"{v * 100:+.2f}%"


def run(start_date: date, end_date: date, rebalance_days: Optional[int] = None,
        lookback_days: Optional[int] = None, top_n: Optional[int] = None) -> Dict[str, str]:
    setup_logging()
    run_date = date.today()
    root = Path(__file__).parent.parent
    config = load_config(root / "config")
    p = dict(_DEFAULTS)
    p.update({k: v for k, v in (config.get("adaptive") or {}).items() if k in _DEFAULTS})
    if rebalance_days:
        p["rebalance_days"] = rebalance_days
    if lookback_days:
        p["lookback_days"] = lookback_days
    if top_n:
        p["top_n"] = top_n

    log.info("=== Adaptive rotating-signal backtest %s ===", p)
    price_data = fetch_backtest_data(config["tickers"], start_date, end_date, warmup_days=420)
    trades, equity, positions, rotation = run_adaptive(config, price_data, start_date, end_date, p)
    metrics = compute_metrics(trades, equity, positions, config, start_date, end_date)

    sink: List[Dict[str, Any]] = []   # diagnostics signal panel not populated (rotating signal ≠ composite)
    diag = compute_diagnostics(config, price_data, trades, equity, positions, sink, metrics,
                               start_date, end_date)
    diag_md = render_diagnostics_md(diag, config)
    report = generate_backtest_report(metrics, config, trades, equity, positions, run_date,
                                      diagnostics_md=diag_md)
    header = ("# Adaptive Rotating-Signal Backtest\n\n"
              "Per-ticker weekly signal rotation — each name trades its recently-best signal or sits "
              "in cash. **High-turnover, small-sample, overfit-prone — validate out-of-sample and "
              "against a fixed-signal baseline.**\n\n---\n\n")
    report = header + rotation_section(rotation, equity, trades, p) + "\n---\n\n" + report

    paths = save_backtest_outputs(trades, equity, report, root / "backtests", run_date,
                                  diagnostics_df=diagnostics_csv(diag))
    # rename the default-tagged report to an adaptive-tagged name to avoid clobbering `backtest`
    tag = run_date.isoformat()
    md = root / "reports" / f"adaptive_backtest_{tag}.md"
    (root / "reports").mkdir(parents=True, exist_ok=True)
    md.write_text(report)

    print()
    print(f"  Total Return : {_pct(metrics.get('total_return'))}  (IRR {_pct(metrics.get('irr'))})")
    print(f"  Equal-Wt Hold: {_pct(metrics.get('equal_weight_return'))}   "
          f"SPY {_pct(metrics.get('spy_return'))}   QQQ {_pct(metrics.get('qqq_return'))}")
    print(f"  Max Drawdown : {_pct(metrics.get('max_drawdown'))}  |  trades: {metrics.get('n_trades', 0)}")
    print()
    print(f"  Report : {md}")
    print("  NOTE: weekly rotation is overfit-prone — re-run on a disjoint window before trusting.")
    print()
    return {"report": str(md)}


def main() -> None:
    ap = argparse.ArgumentParser(description="AI Paper Trader — Adaptive Rotating-Signal Backtest")
    ap.add_argument("--start", required=True, metavar="YYYY-MM-DD")
    ap.add_argument("--end", required=True, metavar="YYYY-MM-DD")
    ap.add_argument("--rebalance-days", type=int, default=None)
    ap.add_argument("--lookback-days", type=int, default=None)
    ap.add_argument("--top-n", type=int, default=None)
    args = ap.parse_args()
    try:
        s, e = date.fromisoformat(args.start), date.fromisoformat(args.end)
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)
    if e <= s:
        print("Error: --end must be after --start")
        sys.exit(1)
    run(s, e, args.rebalance_days, args.lookback_days, args.top_n)


if __name__ == "__main__":
    main()
