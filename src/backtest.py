"""
backtest.py — Walk-forward backtesting engine for the AI Paper Trader.

Usage:
    python src/backtest.py --start 2024-01-01 --end 2024-12-31

Outputs (written to backtests/):
    backtest_trades_YYYY-MM-DD.csv
    backtest_equity_curve_YYYY-MM-DD.csv
    backtest_report_YYYY-MM-DD.md

Execution assumptions (read before interpreting results):
    1. NO LOOK-AHEAD: Signals on day T use price_data.iloc[:bar_idx+1].
       The signal engine's .iloc[-1] therefore lands on day T's close, never beyond.
    2. NEXT-DAY ENTRY: A signal on day T queues an order; the order fills at
       day T+1's close with slippage. Position sizing uses day T's price as the
       estimate; the actual fill at T+1 may differ by the overnight move.
    3. SAME-DAY EXIT: Stop-loss, take-profit, and max-holding-period are checked
       against day T's close and filled at day T's close with slippage.
       This is mildly optimistic vs. a next-open fill; see Limitations section.
    4. WARM-UP: The first 20 bars of downloaded data build signal history.
       No trades are placed during warm-up, regardless of start_date.
    5. HOLDING PERIOD: Uses calendar_days × 5/7 (same as live agent).
    6. NO COMMISSIONS: Only slippage from risk.apply_slippage() is deducted.
"""

import argparse
import logging
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import yaml
# yfinance is imported lazily inside fetch_backtest_data — it is slow to import
# and unneeded by sensitivity worker processes (which only replay in-memory data).

sys.path.insert(0, str(Path(__file__).parent))

from diagnostics import compute_diagnostics, diagnostics_csv, render_diagnostics_md
from logger import setup_logging
from portfolio import update_current_prices
from risk import (
    apply_slippage,
    can_add_position,
    holding_period_exceeded,
    position_size_shares,
    resolve_max_position_pct,
    stop_loss_triggered,
    take_profit_triggered,
    trailing_stop_triggered,
)
from signals import calculate_signals, rank_candidates

log = logging.getLogger(__name__)

_BENCH_TICKERS = ["SPY", "QQQ"]
_POS_COLS = ["ticker", "shares", "entry_price", "entry_date", "current_price", "highest_price"]

# Signals look back at most 21 bars (20-day return + 20-day avg volume). Feeding
# calculate_signals only this tail — instead of the full growing history — keeps
# per-bar signal cost flat rather than O(bars²). 60 leaves margin for missing/NaN bars.
_SIGNAL_WINDOW = 60


# ─── Config (duplicated from main.py so this script is fully standalone) ──────


def load_config(config_dir: Path) -> Dict[str, Any]:
    with open(config_dir / "universe.yaml") as fh:
        universe = yaml.safe_load(fh)
    with open(config_dir / "strategy.yaml") as fh:
        strategy = yaml.safe_load(fh)
    return {**universe, **strategy}


# ─── Data fetch ───────────────────────────────────────────────────────────────


def fetch_backtest_data(
    tickers: List[str],
    start_date: date,
    end_date: date,
    warmup_days: int = 90,
) -> pd.DataFrame:
    """
    Download OHLCV for all universe tickers plus SPY and QQQ (benchmarks).

    Downloads warmup_days of extra history before start_date so that momentum
    signals (which need 20 bars) are available from the very first sim date.
    yfinance's end parameter is exclusive, so we add one day.
    """
    import yfinance as yf  # lazy: keeps module import (and worker startup) fast

    all_tickers = list(dict.fromkeys(tickers + _BENCH_TICKERS))
    fetch_start = (start_date - timedelta(days=warmup_days)).isoformat()
    fetch_end = (end_date + timedelta(days=1)).isoformat()

    log.info(
        "Fetching data: %d tickers  %s → %s  (incl. %d-day warmup)",
        len(all_tickers), fetch_start, end_date, warmup_days,
    )
    data = yf.download(
        all_tickers,
        start=fetch_start,
        end=fetch_end,
        interval="1d",
        auto_adjust=True,
        progress=False,
    )
    if data.empty:
        raise RuntimeError("yfinance returned no data. Check dates and connection.")

    if not isinstance(data.columns, pd.MultiIndex):
        data.columns = pd.MultiIndex.from_product([data.columns, all_tickers[:1]])

    log.info("Downloaded %d bars", len(data))
    return data


# ─── Exit evaluation (backtest variant) ──────────────────────────────────────


def _evaluate_backtest_exits(
    positions: pd.DataFrame,
    today: date,
    stop_loss: float,
    take_profit: Optional[float],
    max_holding_days: int,
    slippage: float,
    trailing_stop: Optional[float] = None,
) -> Tuple[List[Dict[str, Any]], pd.DataFrame]:
    """
    Scan open positions for exit conditions.

    Mirrors portfolio.evaluate_exits() but uses the column name 'realized_pnl'
    and includes 'holding_days' — required by the backtest trade log schema.
    Fill price = today's close with slippage (see assumption #3 in module doc).

    take_profit=None disables fixed take-profit; trailing_stop (when set) exits
    when price falls trailing_stop below the position's running peak (highest_price).
    The exit record also carries entry_price and highest_price so downstream
    diagnostics can detect winners that gave back gains.
    """
    exit_trades: List[Dict[str, Any]] = []
    keep: List[bool] = []

    for _, row in positions.iterrows():
        entry_price = float(row["entry_price"])
        current_price = float(row["current_price"])
        entry_date = row["entry_date"]
        ticker = str(row["ticker"])
        shares = int(row["shares"])
        highest_price = float(row.get("highest_price", current_price))

        triggered = []
        if stop_loss_triggered(entry_price, current_price, stop_loss):
            triggered.append("stop_loss")
        if take_profit_triggered(entry_price, current_price, take_profit):
            triggered.append("take_profit")
        if trailing_stop_triggered(highest_price, current_price, trailing_stop):
            triggered.append("trailing_stop")
        if holding_period_exceeded(entry_date, today, max_holding_days):
            triggered.append("max_holding_period")

        if triggered:
            sell_price = apply_slippage(current_price, "sell", slippage)
            trade_value = round(sell_price * shares, 2)
            pnl = round((sell_price - entry_price) * shares, 2)
            hold_days = round((today - entry_date).days * 5 / 7, 1)
            exit_trades.append(
                {
                    "date": today.isoformat(),
                    "action": "SELL",
                    "ticker": ticker,
                    "shares": shares,
                    "price": sell_price,
                    "trade_value": trade_value,
                    "reason": "+".join(triggered),
                    "realized_pnl": pnl,
                    "holding_days": hold_days,
                    "entry_price": entry_price,
                    "highest_price": highest_price,
                }
            )
            keep.append(False)
        else:
            keep.append(True)

    if not keep:
        return exit_trades, positions.copy()

    keep_indices = [idx for idx, flag in zip(positions.index, keep) if flag]
    remaining = positions.loc[keep_indices].reset_index(drop=True)
    return exit_trades, remaining


# ─── Entry queueing ──────────────────────────────────────────────────────────


def _queue_entries(
    ranked: pd.DataFrame,
    open_positions: pd.DataFrame,
    portfolio_value: float,
    cash: float,
    config: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Determine which tickers to buy tomorrow based on today's signals.

    Orders are QUEUED here (not filled). They fill at tomorrow's close price.
    Sizing uses today's close as an estimate; overnight moves cause minor drift.

    Returns a list of order dicts: {ticker, shares, signal_price, reason}.
    """
    max_new = config["portfolio"]["max_new_trades_per_day"]
    max_pct = resolve_max_position_pct(config)
    max_exp = config["portfolio"]["max_total_exposure"]

    # Optional score-weighted sizing: position size scales linearly with the
    # ticker's composite_score (in [0,1]) between min_position_pct and max_pct.
    sizing_mode = config["portfolio"].get("sizing_mode", "equal")
    min_pct = config["portfolio"].get("min_position_pct", max_pct)

    held = set(open_positions["ticker"].tolist()) if not open_positions.empty else set()
    orders: List[Dict[str, Any]] = []
    temp_positions = open_positions.copy()
    running_cash = cash  # conservative estimate — decremented per order

    for _, row in ranked.iterrows():
        if len(orders) >= max_new:
            break
        ticker = str(row["ticker"])
        if ticker in held:
            continue
        if not can_add_position(temp_positions, portfolio_value, max_exp):
            break

        price = float(row["price"])
        if sizing_mode == "score_weighted":
            score = float(row.get("composite_score") or 0.0)
            pct = min_pct + (max_pct - min_pct) * max(0.0, min(1.0, score))
        else:
            pct = max_pct
        shares = position_size_shares(portfolio_value, price, pct)
        if shares == 0:
            continue
        est_value = round(price * shares, 2)
        if est_value > running_cash:
            continue

        score = row.get("composite_score", "n/a")
        orders.append(
            {
                "ticker": ticker,
                "shares": shares,
                "signal_price": price,
                "reason": f"momentum_score={score}",
            }
        )
        # Track in temp so exposure cap is enforced across the batch
        temp_positions = pd.concat(
            [
                temp_positions,
                pd.DataFrame(
                    [
                        {
                            "ticker": ticker,
                            "shares": shares,
                            "entry_price": price,
                            "entry_date": None,
                            "current_price": price,
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
        held.add(ticker)
        running_cash -= est_value

    return orders


# ─── Benchmark helper ─────────────────────────────────────────────────────────


def _bench_return(
    close: pd.DataFrame,
    ticker: str,
    current_ts: Any,
    start_ts: Any,
) -> Optional[float]:
    """Return close-to-close cumulative return for a benchmark ticker, or None."""
    if ticker not in close.columns:
        return None
    try:
        p0 = float(close.loc[start_ts, ticker])
        pt = float(close.loc[current_ts, ticker])
        if p0 == 0 or pd.isna(p0) or pd.isna(pt):
            return None
        return round(pt / p0 - 1, 6)
    except (KeyError, TypeError):
        return None


def _equal_weight_hold_return(
    close: pd.DataFrame,
    tickers: List[str],
    current_ts: Any,
    start_ts: Any,
) -> Optional[float]:
    """
    Equal-weight buy-and-hold return: simple average of every universe ticker's
    return since the first sim date. This is a SYNTHETIC benchmark computed from the
    universe — it is not a fetched security. (Note: 'EWH' is a real, unrelated ETF;
    do not label this series 'EWH'. It is shown as 'Equal-Wt Hold' in reports.)
    """
    rets = []
    for ticker in tickers:
        if ticker not in close.columns:
            continue
        try:
            p0 = float(close.loc[start_ts, ticker])
            pt = float(close.loc[current_ts, ticker])
            if p0 > 0 and not pd.isna(p0) and not pd.isna(pt):
                rets.append(pt / p0 - 1)
        except (KeyError, TypeError):
            continue
    if not rets:
        return None
    return round(sum(rets) / len(rets), 6)


def _cum_ret_max_drawdown(cum_series: pd.Series) -> Optional[float]:
    """Max drawdown computed from a cumulative-return series (e.g. 0.10 = +10%)."""
    clean = cum_series.dropna()
    if clean.empty:
        return None
    levels = 1.0 + clean
    roll_max = levels.cummax()
    return float(((levels - roll_max) / roll_max).min())


def _trailing_return_from_cum_ret(cum_series: pd.Series, n_bars: int) -> Optional[float]:
    """Return over the trailing n_bars window from a cumulative-return series."""
    clean = cum_series.dropna()
    if len(clean) < n_bars + 1:
        return None
    end_level = 1.0 + float(clean.iloc[-1])
    start_level = 1.0 + float(clean.iloc[-n_bars])
    if start_level <= 0 or pd.isna(start_level) or pd.isna(end_level):
        return None
    return round(end_level / start_level - 1, 6)


def _xirr(cashflows: List[Tuple[date, float]]) -> Optional[float]:
    """
    Annualized internal rate of return (money-weighted) for dated cash flows.

    cashflows: (date, amount) pairs; negative = cash out (a BUY), positive = cash
    in (a SELL, or terminal mark-to-market of still-open positions). Returns the
    annual rate r solving sum(amount / (1+r)**years_from_first) == 0, or None if
    the stream lacks both signs or cannot be solved.

    Newton-Raphson first, with a bracketed bisection fallback for robustness. The
    rate domain is (-100%, ∞), so IRR cannot print below -100%.
    """
    if len(cashflows) < 2:
        return None
    amounts = [a for _, a in cashflows]
    if not (any(a > 0 for a in amounts) and any(a < 0 for a in amounts)):
        return None

    t0 = min(d for d, _ in cashflows)
    years = [(d - t0).days / 365.0 for d, _ in cashflows]
    scale = sum(abs(a) for a in amounts)
    tol = 1e-6 * scale + 1e-6

    def npv(rate: float) -> float:
        return sum(a / (1.0 + rate) ** y for a, y in zip(amounts, years))

    # Newton-Raphson
    rate = 0.1
    for _ in range(100):
        f = npv(rate)
        deriv = sum(-y * a / (1.0 + rate) ** (y + 1.0) for a, y in zip(amounts, years))
        if abs(deriv) < 1e-12:
            break
        new_rate = rate - f / deriv
        if new_rate <= -0.999999:
            new_rate = (rate - 0.999999) / 2.0
        if abs(new_rate - rate) < 1e-9:
            rate = new_rate
            break
        rate = new_rate
    if rate > -0.999999 and abs(npv(rate)) < tol:
        return rate

    # Bisection fallback
    lo, hi = -0.999999, 1.0
    f_lo, f_hi = npv(lo), npv(hi)
    tries = 0
    while f_lo * f_hi > 0 and hi < 1e7 and tries < 80:
        hi *= 2.0
        f_hi = npv(hi)
        tries += 1
    if f_lo * f_hi > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2.0
        f_mid = npv(mid)
        if abs(f_mid) < tol or (hi - lo) < 1e-12:
            return mid
        if f_lo * f_mid < 0:
            hi = mid
        else:
            lo, f_lo = mid, f_mid
    return (lo + hi) / 2.0


# ─── Main simulation loop ─────────────────────────────────────────────────────


def run_backtest(
    config: Dict[str, Any],
    price_data: pd.DataFrame,
    start_date: date,
    end_date: date,
    signal_sink: Optional[List[Dict[str, Any]]] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Walk-forward simulation over [start_date, end_date].

    Returns:
        trades_df    — every simulated BUY and SELL
        equity_df    — daily equity curve with benchmark columns
        positions    — positions still open at the end of the period

    signal_sink: optional list; when provided, each sim day's full-universe scored
    signals (every ticker, not just the top-N) are appended as dicts for post-hoc
    diagnostics. This only *reads* signals already computed for trading — it never
    affects any decision — so it cannot introduce look-ahead. Left None by the
    sensitivity runs and tests so their behaviour and speed are unchanged.
    """
    tickers: List[str] = config["tickers"]
    slippage = config["risk"]["slippage"]
    stop_loss = config["risk"]["stop_loss"]
    take_profit = config["risk"].get("take_profit")        # may be None (trailing-only)
    trailing_stop = config["risk"].get("trailing_stop")    # None unless a profile sets it
    max_holding = config["risk"]["max_holding_days"]
    starting_value = config["portfolio"]["starting_value"]
    top_n = config.get("signals", {}).get("top_candidates", 10)
    weights = config.get("signals", {}).get("weights")
    min_score = config.get("signals", {}).get("min_composite_score")

    close = price_data["Close"]
    all_timestamps = close.index.tolist()

    sim_timestamps = [
        ts for ts in all_timestamps
        if start_date <= ts.date() <= end_date
    ]
    if not sim_timestamps:
        raise ValueError(f"No trading days found between {start_date} and {end_date}.")

    bench_start_ts = sim_timestamps[0]
    # sim_timestamps is a contiguous tail of all_timestamps, so the integer bar
    # index just increments — avoids an O(n) list.index() lookup every bar.
    sim_start_idx = all_timestamps.index(bench_start_ts)
    n_timestamps = len(all_timestamps)

    # ── State ─────────────────────────────────────────────────────────────────
    cash = float(starting_value)
    positions = pd.DataFrame(columns=_POS_COLS)
    pending_orders: List[Dict[str, Any]] = []
    all_trades: List[Dict[str, Any]] = []
    equity_curve: List[Dict[str, Any]] = []
    realized_pnl = 0.0

    log.info(
        "Backtest: %s → %s  (%d trading days)",
        start_date, end_date, len(sim_timestamps),
    )

    for offset, bar_ts in enumerate(sim_timestamps):
        bar_date = bar_ts.date()
        bar_idx = sim_start_idx + offset
        today_prices: pd.Series = close.loc[bar_ts].dropna()

        # ── 1. Fill pending buy orders (queued from yesterday's signals) ──────
        #    Fill price = today's close + slippage (next-day execution assumption)
        filled: List[Dict[str, Any]] = []
        for order in pending_orders:
            ticker = order["ticker"]
            if ticker not in today_prices.index:
                log.debug("No price for %s on %s — order lapsed", ticker, bar_date)
                continue
            fill_price = apply_slippage(float(today_prices[ticker]), "buy", slippage)
            shares = order["shares"]
            trade_value = round(fill_price * shares, 2)
            if shares == 0 or trade_value > cash:
                log.debug("Cash insufficient for %s on %s — order lapsed", ticker, bar_date)
                continue
            cash -= trade_value
            all_trades.append(
                {
                    "date": bar_date.isoformat(),
                    "action": "BUY",
                    "ticker": ticker,
                    "shares": shares,
                    "price": fill_price,
                    "trade_value": trade_value,
                    "reason": order["reason"],
                    "realized_pnl": None,
                    "holding_days": 0,
                }
            )
            filled.append(
                {
                    "ticker": ticker,
                    "shares": shares,
                    "entry_price": fill_price,
                    "entry_date": bar_date,
                    "current_price": fill_price,
                    "highest_price": fill_price,
                }
            )
        if filled:
            positions = pd.concat(
                [positions, pd.DataFrame(filled)], ignore_index=True
            )
        pending_orders = []

        # ── 2. Update open position prices + running peak (for trailing stop) ─
        positions = update_current_prices(positions, today_prices)
        if not positions.empty:
            positions["highest_price"] = positions[["highest_price", "current_price"]].max(axis=1)

        # ── 3. Evaluate exits against today's close ───────────────────────────
        exit_trades, positions = _evaluate_backtest_exits(
            positions, bar_date, stop_loss, take_profit, max_holding, slippage,
            trailing_stop=trailing_stop,
        )
        for e in exit_trades:
            cash += e["trade_value"]
            realized_pnl += e["realized_pnl"]
            all_trades.append(e)

        # ── 4. Portfolio value snapshot ───────────────────────────────────────
        equity = (
            float((positions["shares"] * positions["current_price"]).sum())
            if not positions.empty
            else 0.0
        )
        portfolio_value = cash + equity

        # ── 5. Compute signals (no look-ahead) and queue entries for tomorrow ─
        if bar_idx + 1 < n_timestamps:
            # Windowed tail ending at today's bar — never includes future data,
            # but bounds per-bar cost (see _SIGNAL_WINDOW).
            data_slice = price_data.iloc[max(0, bar_idx + 1 - _SIGNAL_WINDOW): bar_idx + 1]
            signals = calculate_signals(data_slice, tickers)
            if not signals.empty:
                ranked = rank_candidates(signals, top_n=top_n, weights=weights)
                if min_score is not None and not ranked.empty:
                    ranked = ranked[ranked["composite_score"] >= min_score].reset_index(drop=True)
                pending_orders = _queue_entries(
                    ranked, positions, portfolio_value, cash, config
                )
                if signal_sink is not None:
                    # Score the whole cross-section (not just top-N) for diagnostics.
                    scored_all = rank_candidates(signals, top_n=len(signals), weights=weights)
                    for _, srow in scored_all.iterrows():
                        signal_sink.append(
                            {
                                "date": bar_date.isoformat(),
                                "bar_idx": bar_idx,
                                "ticker": srow["ticker"],
                                "return_1d": srow.get("return_1d"),
                                "return_5d": srow.get("return_5d"),
                                "return_20d": srow.get("return_20d"),
                                "vol_ratio": srow.get("vol_ratio"),
                                "composite_score": srow.get("composite_score"),
                            }
                        )

        # ── 6. Record equity curve row ────────────────────────────────────────
        unrealized = (
            float(
                ((positions["current_price"] - positions["entry_price"]) * positions["shares"]).sum()
            )
            if not positions.empty
            else 0.0
        )
        equity_curve.append(
            {
                "date": bar_date.isoformat(),
                "cash": round(cash, 2),
                "open_positions_value": round(equity, 2),
                "total_portfolio_value": round(portfolio_value, 2),
                "realized_pnl_to_date": round(realized_pnl, 2),
                "unrealized_pnl": round(unrealized, 2),
                "daily_return": None,          # filled after loop
                "cumulative_return": None,     # filled after loop
                "spy_cumulative_return": _bench_return(close, "SPY", bar_ts, bench_start_ts),
                "qqq_cumulative_return": _bench_return(close, "QQQ", bar_ts, bench_start_ts),
                "equal_weight_cumulative_return": _equal_weight_hold_return(close, tickers, bar_ts, bench_start_ts),
            }
        )

    # ── Post-loop: derive return columns ──────────────────────────────────────
    trades_df = pd.DataFrame(all_trades)
    equity_df = pd.DataFrame(equity_curve)

    if not equity_df.empty:
        equity_df["daily_return"] = equity_df["total_portfolio_value"].pct_change().round(6)
        equity_df["cumulative_return"] = (
            equity_df["total_portfolio_value"] / starting_value - 1
        ).round(6)

    # Re-order equity_curve columns to match spec
    col_order = [
        "date", "cash", "open_positions_value", "total_portfolio_value",
        "realized_pnl_to_date", "unrealized_pnl", "daily_return",
        "cumulative_return", "spy_cumulative_return", "qqq_cumulative_return",
        "equal_weight_cumulative_return",
    ]
    equity_df = equity_df.reindex(columns=[c for c in col_order if c in equity_df.columns])

    return trades_df, equity_df, positions


# ─── Metrics ──────────────────────────────────────────────────────────────────


def compute_metrics(
    trades_df: pd.DataFrame,
    equity_df: pd.DataFrame,
    positions: pd.DataFrame,
    config: Dict[str, Any],
    start_date: date,
    end_date: date,
) -> Dict[str, Any]:
    """Compute summary statistics from simulation outputs."""
    starting_value = float(config["portfolio"]["starting_value"])

    if equity_df.empty:
        return {"error": "No equity data — backtest produced no trading days."}

    final_value = float(equity_df["total_portfolio_value"].iloc[-1])
    total_pnl = final_value - starting_value
    total_return = total_pnl / starting_value

    # ── Capital deployment & money-weighted return (IRR) ──────────────────────
    # Snapshot deployment: market value of open positions at each day's close.
    # These describe how much capital was at work *at any one moment* (a stock).
    deployed = equity_df["open_positions_value"]
    avg_deployed = float(deployed.mean())
    peak_deployed = float(deployed.max())
    pct_time_invested = float((deployed > 0).mean())
    total_capital_deployed = (
        float(trades_df.loc[trades_df["action"] == "BUY", "trade_value"].sum())
        if not trades_df.empty else 0.0
    )

    # IRR (annualized, money-weighted) on the capital actually put into positions.
    # Cash flows are the dated BUYs (out) and SELLs (in), plus a terminal mark-to-
    # market of any still-open positions on the last day. Idle cash never enters,
    # so this isolates how the *deployed* capital performed, time-weighted by when
    # it was committed. The rate domain is (-100%, ∞), so IRR cannot exceed -100%.
    cashflows: List[Tuple[date, float]] = []
    if not trades_df.empty:
        for _, tr in trades_df.iterrows():
            amt = -float(tr["trade_value"]) if tr["action"] == "BUY" else float(tr["trade_value"])
            cashflows.append((date.fromisoformat(str(tr["date"])), amt))
    terminal_value = (
        float((positions["shares"] * positions["current_price"]).sum())
        if not positions.empty else 0.0
    )
    if terminal_value > 0:
        cashflows.append((date.fromisoformat(str(equity_df["date"].iloc[-1])), terminal_value))
    irr = _xirr(cashflows)

    # Max drawdown
    roll_max = equity_df["total_portfolio_value"].cummax()
    drawdown = (equity_df["total_portfolio_value"] - roll_max) / roll_max
    max_drawdown = float(drawdown.min())

    slippage_rate = config["risk"]["slippage"]

    # Slippage cost: buy fill = price*(1+slip), so cost = TV*slip/(1+slip); sell is TV*slip/(1-slip)
    if not trades_df.empty:
        buy_tv  = float(trades_df.loc[trades_df["action"] == "BUY",  "trade_value"].sum())
        sell_tv = float(trades_df.loc[trades_df["action"] == "SELL", "trade_value"].sum())
        total_slippage = round(
            buy_tv  * slippage_rate / (1 + slippage_rate) +
            sell_tv * slippage_rate / (1 - slippage_rate),
            2,
        )
        n_trades_total = len(trades_df)
        avg_slippage_per_trade = round(total_slippage / n_trades_total, 2)
        slippage_pct_portfolio = total_slippage / starting_value
    else:
        total_slippage = avg_slippage_per_trade = slippage_pct_portfolio = 0.0

    # Trade statistics
    sells = trades_df[trades_df["action"] == "SELL"] if not trades_df.empty else pd.DataFrame()
    n_sells = len(sells)

    if n_sells > 0:
        pnls = sells["realized_pnl"].dropna()
        wins = pnls[pnls > 0]
        losses = pnls[pnls <= 0]
        win_rate = len(wins) / n_sells
        avg_win = float(wins.mean()) if len(wins) > 0 else 0.0
        avg_loss = float(losses.mean()) if len(losses) > 0 else 0.0
        gross_profit = float(wins.sum()) if len(wins) > 0 else 0.0
        gross_loss = abs(float(losses.sum())) if len(losses) > 0 else 0.0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else None
        avg_holding = float(sells["holding_days"].mean())
        largest_winner = float(pnls.max())
        largest_loser = float(pnls.min())
    else:
        win_rate = avg_win = avg_loss = avg_holding = 0.0
        gross_profit = gross_loss = largest_winner = largest_loser = 0.0
        profit_factor = None

    # Benchmarks (last row of equity curve)
    def _last_bench(col: str) -> Optional[float]:
        if col not in equity_df.columns:
            return None
        val = equity_df[col].dropna()
        return float(val.iloc[-1]) if not val.empty else None

    spy_return = _last_bench("spy_cumulative_return")
    qqq_return = _last_bench("qqq_cumulative_return")
    equal_weight_return = _last_bench("equal_weight_cumulative_return")

    def _bench_dd(col: str) -> Optional[float]:
        return _cum_ret_max_drawdown(equity_df[col]) if col in equity_df.columns else None

    def _bench_trailing(col: str, n: int) -> Optional[float]:
        series = equity_df[col] if col in equity_df.columns else pd.Series(dtype=float)
        return _trailing_return_from_cum_ret(series, n)

    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "trading_days": len(equity_df),
        "starting_value": starting_value,
        "ending_value": final_value,
        "total_return": total_return,
        "irr": irr,
        "total_capital_deployed": total_capital_deployed,
        "avg_capital_deployed": avg_deployed,
        "avg_capital_deployed_pct": avg_deployed / starting_value,
        "peak_capital_deployed": peak_deployed,
        "peak_capital_deployed_pct": peak_deployed / starting_value,
        "pct_time_invested": pct_time_invested,
        "max_drawdown": max_drawdown,
        "spy_return": spy_return,
        "qqq_return": qqq_return,
        "equal_weight_return": equal_weight_return,
        "spy_max_drawdown": _bench_dd("spy_cumulative_return"),
        "qqq_max_drawdown": _bench_dd("qqq_cumulative_return"),
        "equal_weight_max_drawdown": _bench_dd("equal_weight_cumulative_return"),
        "excess_vs_spy": (total_return - spy_return) if spy_return is not None else None,
        "excess_vs_qqq": (total_return - qqq_return) if qqq_return is not None else None,
        "excess_vs_equal_weight": (total_return - equal_weight_return) if equal_weight_return is not None else None,
        "strategy_return_1y": _bench_trailing("cumulative_return", 252),
        "strategy_return_2y": _bench_trailing("cumulative_return", 504),
        "strategy_return_3y": _bench_trailing("cumulative_return", 756),
        "spy_return_1y": _bench_trailing("spy_cumulative_return", 252),
        "spy_return_2y": _bench_trailing("spy_cumulative_return", 504),
        "spy_return_3y": _bench_trailing("spy_cumulative_return", 756),
        "qqq_return_1y": _bench_trailing("qqq_cumulative_return", 252),
        "qqq_return_2y": _bench_trailing("qqq_cumulative_return", 504),
        "qqq_return_3y": _bench_trailing("qqq_cumulative_return", 756),
        "equal_weight_return_1y": _bench_trailing("equal_weight_cumulative_return", 252),
        "equal_weight_return_2y": _bench_trailing("equal_weight_cumulative_return", 504),
        "equal_weight_return_3y": _bench_trailing("equal_weight_cumulative_return", 756),
        "n_trades": len(trades_df) if not trades_df.empty else 0,
        "n_buys": int((trades_df["action"] == "BUY").sum()) if not trades_df.empty else 0,
        "n_sells": n_sells,
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "profit_factor": profit_factor,
        "avg_holding_days": avg_holding,
        "largest_winner": largest_winner,
        "largest_loser": largest_loser,
        "open_positions_at_end": len(positions),
        "total_slippage_cost": total_slippage,
        "avg_slippage_per_trade": avg_slippage_per_trade,
        "slippage_pct_of_portfolio": slippage_pct_portfolio,
    }


# ─── Sensitivity analysis ─────────────────────────────────────────────────────

# Default composite-score weights, used as the fallback "baseline" profile when
# config/strategy.yaml does not define signals.weights. The alternative profiles
# below are fixed comparison hypotheses, NOT derived from the config baseline.
_DEFAULT_WEIGHTS: Dict[str, float] = {
    "return_1d": 0.20, "return_5d": 0.30, "return_20d": 0.30, "vol_ratio": 0.20,
}
_ALT_WEIGHT_PROFILES: Dict[str, Dict[str, float]] = {
    "no_1d":       {"return_1d": 0.00, "return_5d": 0.40, "return_20d": 0.40, "vol_ratio": 0.20},
    "less_1d":     {"return_1d": 0.05, "return_5d": 0.35, "return_20d": 0.40, "vol_ratio": 0.20},
    "more_volume": {"return_1d": 0.10, "return_5d": 0.25, "return_20d": 0.30, "vol_ratio": 0.35},
}

# Test points swept for each numeric parameter. The live config baseline is always
# merged into its sweep at runtime (see _sweep_with_baseline), so changing a value
# in strategy.yaml automatically adds it to the table and flags it as the baseline.
_SENSITIVITY_TEST_POINTS: Dict[str, List[Optional[float]]] = {
    "stop_loss": [0.03, 0.05, 0.075, 0.10],
    "take_profit": [0.08, 0.10, 0.15],
    "max_holding_days": [5, 15, 30, 60],
    "max_new_trades_per_day": [1, 2, 3, 5],
    "min_composite_score": [None, 0.60, 0.70, 0.80],
}


def _sweep_with_baseline(
    test_points: List[Optional[float]],
    baseline_value: Optional[float],
) -> List[Optional[float]]:
    """
    Merge the live config baseline into a parameter's test sweep.

    Guarantees the current baseline appears in the swept values (so it is always
    represented and gets the '◀ baseline' marker), then dedupes and sorts with any
    None ('disabled') first.
    """
    vals = list(test_points)
    if baseline_value not in vals:
        vals.append(baseline_value)
    numeric = sorted(v for v in vals if v is not None)
    return ([None] if None in vals else []) + numeric


# Each sensitivity variant is an independent full backtest, so they run in
# parallel across processes. Worker processes receive the (large, read-only) price
# data once via the pool initializer rather than re-pickling it for every task.
_SENS_CTX: Dict[str, Any] = {}


def _sensitivity_pool_init(price_data: pd.DataFrame, start_date: date, end_date: date) -> None:
    _SENS_CTX["price_data"] = price_data
    _SENS_CTX["start_date"] = start_date
    _SENS_CTX["end_date"] = end_date


def _run_variant(task: Tuple[str, str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Run one variant backtest and return its summary metrics (or None on failure)."""
    param, display_val, cfg = task
    price_data = _SENS_CTX["price_data"]
    start_date = _SENS_CTX["start_date"]
    end_date = _SENS_CTX["end_date"]
    try:
        t, e, pos = run_backtest(cfg, price_data, start_date, end_date)
        m = compute_metrics(t, e, pos, cfg, start_date, end_date)
        return {
            "parameter": param,
            "value": display_val,
            "total_return": m.get("total_return"),
            "excess_vs_spy": m.get("excess_vs_spy"),
            "excess_vs_qqq": m.get("excess_vs_qqq"),
            "excess_vs_equal_weight": m.get("excess_vs_equal_weight"),
            "max_drawdown": m.get("max_drawdown"),
            "total_trades": m.get("n_trades", 0),
            "win_rate": m.get("win_rate"),
            "profit_factor": m.get("profit_factor"),
            "avg_holding_period": m.get("avg_holding_days"),
        }
    except Exception as exc:
        log.warning("Sensitivity %s=%s failed: %s", param, display_val, exc)
        return None


def _build_sensitivity_tasks(baseline_config: Dict[str, Any]) -> List[Tuple[str, str, Dict[str, Any]]]:
    """Build the (parameter, display_value, config) tuples for every variant to run."""
    import copy

    r = baseline_config["risk"]
    p = baseline_config["portfolio"]
    s = baseline_config.get("signals", {})
    tasks: List[Tuple[str, str, Dict[str, Any]]] = []

    for val in _sweep_with_baseline(_SENSITIVITY_TEST_POINTS["stop_loss"], r["stop_loss"]):
        cfg = copy.deepcopy(baseline_config); cfg["risk"]["stop_loss"] = val
        tasks.append(("stop_loss", f"{val:.1%}", cfg))

    for val in _sweep_with_baseline(_SENSITIVITY_TEST_POINTS["take_profit"], r["take_profit"]):
        cfg = copy.deepcopy(baseline_config); cfg["risk"]["take_profit"] = val
        tasks.append(("take_profit", f"{val:.0%}", cfg))

    for val in _sweep_with_baseline(_SENSITIVITY_TEST_POINTS["max_holding_days"], r["max_holding_days"]):
        cfg = copy.deepcopy(baseline_config); cfg["risk"]["max_holding_days"] = val
        tasks.append(("max_holding_days", str(val), cfg))

    for val in _sweep_with_baseline(_SENSITIVITY_TEST_POINTS["max_new_trades_per_day"], p["max_new_trades_per_day"]):
        cfg = copy.deepcopy(baseline_config); cfg["portfolio"]["max_new_trades_per_day"] = val
        tasks.append(("max_new_trades_per_day", str(val), cfg))

    for val in _sweep_with_baseline(_SENSITIVITY_TEST_POINTS["min_composite_score"], s.get("min_composite_score")):
        cfg = copy.deepcopy(baseline_config); cfg["signals"]["min_composite_score"] = val
        tasks.append(("min_composite_score", "none" if val is None else f"{val:.2f}", cfg))

    # "baseline" profile reflects the live config weights; alternatives are fixed.
    config_weights = s.get("weights") or _DEFAULT_WEIGHTS
    weight_profiles = {"baseline": config_weights, **_ALT_WEIGHT_PROFILES}
    for name, wts in weight_profiles.items():
        cfg = copy.deepcopy(baseline_config); cfg["signals"]["weights"] = wts
        tasks.append(("signal_weights", name, cfg))

    return tasks


def _run_sensitivity_variants(
    baseline_config: Dict[str, Any],
    price_data: pd.DataFrame,
    start_date: date,
    end_date: date,
) -> List[Dict[str, Any]]:
    """
    One-way sensitivity analysis: vary one parameter at a time, all others held at
    the live config baseline.

    Each numeric sweep merges a fixed set of test points with the current baseline
    value from config/strategy.yaml, so the report stays correct as you edit
    baselines. Variants are independent full backtests, so they run across a process
    pool (set BACKTEST_SERIAL=1 to force single-process). deepcopy keeps
    baseline_config unmutated. Returns summary metric dicts only — no per-run trade
    logs or equity curves are retained. Result order matches task order regardless
    of execution mode, so the report is deterministic.
    """
    tasks = _build_sensitivity_tasks(baseline_config)

    force_serial = os.environ.get("BACKTEST_SERIAL") == "1"
    max_workers = min(len(tasks), os.cpu_count() or 1, 8)

    if not force_serial and max_workers > 1:
        try:
            with ProcessPoolExecutor(
                max_workers=max_workers,
                initializer=_sensitivity_pool_init,
                initargs=(price_data, start_date, end_date),
            ) as executor:
                results = [r for r in executor.map(_run_variant, tasks) if r is not None]
            log.info(
                "Sensitivity analysis: %d/%d variants across %d workers",
                len(results), len(tasks), max_workers,
            )
            return results
        except Exception as exc:  # pragma: no cover - environment-dependent
            log.warning("Parallel sensitivity unavailable (%s) — running serially", exc)

    # Serial fallback (also the path when BACKTEST_SERIAL=1 or a single CPU).
    _sensitivity_pool_init(price_data, start_date, end_date)
    results = [r for r in (_run_variant(t) for t in tasks) if r is not None]
    log.info("Sensitivity analysis: %d/%d variants (serial)", len(results), len(tasks))
    return results


def _robustness_commentary(
    results: List[Dict[str, Any]],
    baseline_return: float,
) -> str:
    """Return plain-text robustness notes derived from sensitivity results."""
    from collections import defaultdict

    valid = [r for r in results if r.get("total_return") is not None]
    if not valid:
        return "_No valid results to analyze._"

    n_beat = sum(1 for r in valid if r["total_return"] > baseline_return)
    pct_beat = n_beat / len(valid) * 100

    param_returns: Dict[str, List[float]] = defaultdict(list)
    for r in valid:
        param_returns[r["parameter"]].append(r["total_return"])
    ranges = {p: max(v) - min(v) for p, v in param_returns.items() if len(v) > 1}

    parts: List[str] = []

    if pct_beat < 25:
        parts.append(
            f"The baseline outperforms {100 - pct_beat:.0f}% of all variants. "
            "This is broadly consistent across parameter dimensions, suggesting the "
            "baseline settings are reasonably competitive in-sample."
        )
    elif pct_beat < 55:
        parts.append(
            f"{pct_beat:.0f}% of variants beat the baseline. Improvements are mixed — "
            "some directions help, others hurt — which is consistent with a strategy "
            "that has modest but not dominant in-sample edge."
        )
    else:
        parts.append(
            f"{pct_beat:.0f}% of variants beat the baseline. The baseline settings may "
            "not be well-suited to this period, or the strategy is broadly sensitive to "
            "parameter choice. Be cautious about reading these improvements as durable."
        )

    if ranges:
        most = max(ranges, key=lambda k: ranges[k])
        least = min(ranges, key=lambda k: ranges[k])
        parts.append(
            f"The widest in-sample return spread belongs to `{most}` "
            f"({ranges[most] * 100:.1f} pp range across its variants); "
            f"`{least}` shows the narrowest spread "
            f"({ranges[least] * 100:.1f} pp), suggesting the strategy is least "
            "sensitive to that parameter in this period."
        )

    parts.append(
        "Improvements that appear in only one or two variants should be treated with "
        "skepticism — isolated peaks are more likely to reflect in-sample noise than "
        "genuine edge. Prefer settings that perform consistently across the full sweep."
    )

    return "\n\n".join(parts)


def _sensitivity_section(
    results: List[Dict[str, Any]],
    baseline_metrics: Dict[str, Any],
    config: Dict[str, Any],
) -> str:
    """Build the ## Sensitivity Analysis block for the backtest Markdown report."""
    if not results:
        return "## Sensitivity Analysis\n\n_Sensitivity analysis produced no results._\n"

    from collections import defaultdict

    b = baseline_metrics
    r_cfg = config["risk"]
    p_cfg = config["portfolio"]
    s_cfg = config.get("signals", {})

    baseline_vals = {
        "stop_loss": f"{r_cfg.get('stop_loss', 0.05):.1%}",
        "take_profit": f"{r_cfg.get('take_profit', 0.10):.0%}",
        "max_holding_days": str(r_cfg.get("max_holding_days", 10)),
        "max_new_trades_per_day": str(p_cfg.get("max_new_trades_per_day", 3)),
        "min_composite_score": (
            "none" if s_cfg.get("min_composite_score") is None
            else f"{s_cfg.get('min_composite_score'):.2f}"
        ),
        "signal_weights": "baseline",
    }

    lines: List[str] = [
        "## Sensitivity Analysis",
        "",
        "> One parameter is varied at a time; all others remain at baseline values.",
        "> Do not select parameters based on in-sample performance alone — see Robustness Notes below.",
        "",
        f"**Baseline:** {_pct(b.get('total_return'))} return  |  "
        f"{_pct(b.get('max_drawdown'))} max drawdown  |  "
        f"{_pct(b.get('win_rate'))} win rate  |  "
        f"{_pf(b.get('profit_factor'))} profit factor",
        "",
    ]

    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in results:
        grouped[r["parameter"]].append(r)

    col_header  = "| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |"
    col_divider = "|-------|--------|--------|--------|--------|--------|----------|-----|"

    def _data_row(r: Dict[str, Any], mark_baseline: bool) -> str:
        marker = " ◀ baseline" if mark_baseline else ""
        pf = _pf(r["profit_factor"]) if r.get("profit_factor") is not None else "—"
        trades = r.get("total_trades", "—")
        return (
            f"| {r['value']}{marker} "
            f"| {_pct(r.get('total_return'), '—')} "
            f"| {_pct(r.get('excess_vs_spy'), '—')} "
            f"| {_pct(r.get('excess_vs_equal_weight'), '—')} "
            f"| {_pct(r.get('max_drawdown'), '—')} "
            f"| {trades} "
            f"| {_pct(r.get('win_rate'), '—')} "
            f"| {pf} |"
        )

    for param, label in [
        ("stop_loss",             "Stop Loss"),
        ("take_profit",           "Take Profit"),
        ("max_holding_days",      "Max Holding Days"),
        ("max_new_trades_per_day","Max New Trades / Day"),
        ("min_composite_score",   "Min Composite Score"),
        ("signal_weights",        "Signal Weight Profile"),
    ]:
        rows = grouped.get(param, [])
        if not rows:
            continue
        base_val = baseline_vals.get(param, "")
        lines += [f"### {label}  (baseline: {base_val})", "", col_header, col_divider]
        for r in rows:
            lines.append(_data_row(r, mark_baseline=(r["value"] == base_val)))
        lines.append("")

    sortable = sorted(
        [r for r in results if r.get("total_return") is not None],
        key=lambda r: r["total_return"],
        reverse=True,
    )

    rank_header  = "| Rank | Parameter | Value | Return | vs SPY | vs EqWt | Max DD | PF |"
    rank_divider = "|------|-----------|-------|--------|--------|--------|--------|-----|"

    def _ranked_row(rank: int, r: Dict[str, Any]) -> str:
        pf = _pf(r["profit_factor"]) if r.get("profit_factor") is not None else "—"
        return (
            f"| {rank} | {r['parameter']} | {r['value']} "
            f"| {_pct(r.get('total_return'), '—')} "
            f"| {_pct(r.get('excess_vs_spy'), '—')} "
            f"| {_pct(r.get('excess_vs_equal_weight'), '—')} "
            f"| {_pct(r.get('max_drawdown'), '—')} "
            f"| {pf} |"
        )

    lines += ["### Best 5 Variants by Total Return", "", rank_header, rank_divider]
    for i, r in enumerate(sortable[:5], 1):
        lines.append(_ranked_row(i, r))
    lines.append("")

    worst5 = list(reversed(sortable[-5:])) if len(sortable) >= 5 else list(reversed(sortable))
    lines += ["### Worst 5 Variants by Total Return", "", rank_header, rank_divider]
    for i, r in enumerate(worst5, 1):
        lines.append(_ranked_row(i, r))
    lines.append("")

    lines += [
        "### Robustness Notes",
        "",
        _robustness_commentary(results, b.get("total_return", 0.0)),
        "",
    ]

    return "\n".join(lines)


# ─── Report builder ───────────────────────────────────────────────────────────


def _pct(v: Optional[float], default: str = "N/A") -> str:
    # Treat None and NaN alike (e.g. first-day daily_return is NaN) → default, not "+nan%"
    return default if v is None or pd.isna(v) else f"{v * 100:+.2f}%"


def _dollar(v: Optional[float], default: str = "N/A") -> str:
    # Treat None and NaN alike (e.g. BUY rows have NaN realized_pnl) → default, not "$nan"
    return default if v is None or pd.isna(v) else f"${v:,.2f}"


def _pf(v: Optional[float]) -> str:
    return "N/A (no losses)" if v is None or pd.isna(v) else f"{v:.2f}"


def _bench_end_balance(m: Dict[str, Any], return_key: str) -> Optional[float]:
    """What the starting portfolio would be worth fully invested in a benchmark."""
    sv = m.get("starting_value")
    r = m.get(return_key)
    if sv is None or r is None or pd.isna(r):
        return None
    return sv * (1.0 + r)


def generate_backtest_report(
    metrics: Dict[str, Any],
    config: Dict[str, Any],
    trades_df: pd.DataFrame,
    equity_df: pd.DataFrame,
    positions: pd.DataFrame,
    run_date: date,
    sensitivity_results: Optional[List[Dict[str, Any]]] = None,
    diagnostics_md: Optional[str] = None,
) -> str:
    """Build and return the full Markdown backtest report as a string."""
    m = metrics
    p = config["portfolio"]
    r = config["risk"]
    tickers = config["tickers"]

    lines: List[str] = [
        "# AI Paper Trader — Backtest Report",
        f"**Period:** {m.get('start_date', 'N/A')} → {m.get('end_date', 'N/A')}  "
        f"|  **Generated:** {run_date.isoformat()}",
        "",
        "---",
        "",
        "## Results Summary",
        "",
        "| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |",
        "|--------|----------|-----|-----|-----|",
        f"| Ending Balance | {_dollar(m.get('ending_value'))} | {_dollar(_bench_end_balance(m, 'spy_return'), '—')} | {_dollar(_bench_end_balance(m, 'qqq_return'), '—')} | {_dollar(_bench_end_balance(m, 'equal_weight_return'), '—')} |",
        f"| Total Return | {_pct(m.get('total_return'))} | {_pct(m.get('spy_return'))} | {_pct(m.get('qqq_return'))} | {_pct(m.get('equal_weight_return'))} |",
        f"| Max Drawdown | {_pct(m.get('max_drawdown'))} | {_pct(m.get('spy_max_drawdown'), '—')} | {_pct(m.get('qqq_max_drawdown'), '—')} | {_pct(m.get('equal_weight_max_drawdown'), '—')} |",
        f"| Excess vs SPY | {_pct(m.get('excess_vs_spy'))} | — | — | — |",
        f"| Excess vs QQQ | {_pct(m.get('excess_vs_qqq'))} | — | — | — |",
        f"| Excess vs Equal-Wt | {_pct(m.get('excess_vs_equal_weight'))} | — | — | — |",
    ]
    for _lbl, _k in [("1-Year Return", "1y"), ("2-Year Return", "2y"), ("3-Year Return", "3y")]:
        _sv  = m.get(f"strategy_return_{_k}")
        _spy = m.get(f"spy_return_{_k}")
        _qqq = m.get(f"qqq_return_{_k}")
        _eqw = m.get(f"equal_weight_return_{_k}")
        if any(v is not None for v in [_sv, _spy, _qqq, _eqw]):
            lines.append(
                f"| {_lbl} | {_pct(_sv, '—')} | {_pct(_spy, '—')} | {_pct(_qqq, '—')} | {_pct(_eqw, '—')} |"
            )
    lines += [
        "",
        "_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. "
        "**Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's "
        "own universe (not the unrelated EWH ETF)._",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Starting Value | {_dollar(m.get('starting_value'))} |",
        f"| Ending Value | {_dollar(m.get('ending_value'))} |",
        f"| **IRR (annualized, money-weighted)** | **{_pct(m.get('irr'))}** |",
        f"| Total Return (on full $ portfolio) | {_pct(m.get('total_return'))} |",
        f"| Total Capital Deployed (all entries) | {_dollar(m.get('total_capital_deployed'))} |",
        f"| Avg Capital Deployed (snapshot) | {_dollar(m.get('avg_capital_deployed'))} ({_pct(m.get('avg_capital_deployed_pct'))} of portfolio) |",
        f"| Peak Capital Deployed (snapshot) | {_dollar(m.get('peak_capital_deployed'))} ({_pct(m.get('peak_capital_deployed_pct'))} of portfolio) |",
        f"| Time Invested | {_pct(m.get('pct_time_invested'))} of trading days |",
        f"| Trading Days | {m.get('trading_days', 'N/A')} |",
        f"| Total Trades | {m.get('n_trades', 0)} ({m.get('n_buys', 0)} buys, {m.get('n_sells', 0)} sells) |",
        f"| Win Rate | {_pct(m.get('win_rate'))} |",
        f"| Average Win | {_dollar(m.get('avg_win'))} |",
        f"| Average Loss | {_dollar(m.get('avg_loss'))} |",
        f"| Profit Factor | {_pf(m.get('profit_factor'))} |",
        f"| Avg Holding Period | {m.get('avg_holding_days', 0):.1f} approx. trading days |",
        f"| Largest Winner | {_dollar(m.get('largest_winner'))} |",
        f"| Largest Loser | {_dollar(m.get('largest_loser'))} |",
        f"| Open Positions at End | {m.get('open_positions_at_end', 0)} |",
        f"| Total Slippage Cost | {_dollar(m.get('total_slippage_cost'))} ({_pct(m.get('slippage_pct_of_portfolio'))} of start) |",
        f"| Avg Slippage / Trade | {_dollar(m.get('avg_slippage_per_trade'))} |",
        "",
        "_**IRR** is the annualized money-weighted (internal) rate of return on the capital "
        "actually put into positions: it solves for the rate that discounts the dated BUY "
        "outflows, SELL inflows, and the terminal mark-to-market of open positions to zero. "
        "It ignores idle cash, so it measures how the *deployed* capital performed, and is "
        "bounded at -100%. Being annualized, short backtests can extrapolate to large figures. "
        "**Total Return** is on the full starting portfolio (cash included) and is what the "
        "SPY/QQQ/Equal-Wt comparisons above use, since those benchmarks are fully invested._",
        "",
    ]

    # ── Strategy parameters ───────────────────────────────────────────────────
    eff_max_pos = resolve_max_position_pct(config)
    raw_max_pos = p.get("max_position_pct", "auto")
    max_pos_label = (
        f"{eff_max_pos * 100:.1f}% (auto: {p.get('max_total_exposure', 0) * 100:.0f}% ÷ {len(tickers)} tickers)"
        if raw_max_pos is None or (isinstance(raw_max_pos, str) and raw_max_pos.strip().lower() == "auto")
        else f"{eff_max_pos * 100:.1f}%"
    )
    lines += [
        "## Strategy Parameters Used",
        "",
        "| Parameter | Value |",
        "|-----------|-------|",
        f"| Starting Portfolio | {_dollar(p.get('starting_value'))} |",
        f"| Max Position Size | {max_pos_label} |",
        f"| Max Total Exposure | {p.get('max_total_exposure', 0) * 100:.0f}% |",
        f"| Max New Trades / Day | {p.get('max_new_trades_per_day')} |",
        f"| Stop Loss | {r.get('stop_loss', 0) * 100:.0f}% |",
        f"| Take Profit | {r.get('take_profit', 0) * 100:.0f}% |",
        f"| Max Holding Period | {r.get('max_holding_days')} trading days |",
        f"| Slippage | {r.get('slippage', 0) * 100:.2f}% per fill |",
        "",
    ]

    # ── Universe ──────────────────────────────────────────────────────────────
    lines += [
        "## Ticker Universe",
        "",
        ", ".join(f"`{t}`" for t in tickers),
        "",
    ]

    # ── Trade log sample ──────────────────────────────────────────────────────
    lines += ["## Trade Log (last 20 trades)", ""]
    if trades_df.empty:
        lines.append("_No trades were executed._")
    else:
        display = trades_df.tail(20)
        lines += [
            "| Date | Action | Ticker | Shares | Price | Value | Reason | P&L | Hold Days |",
            "|------|--------|--------|--------|-------|-------|--------|-----|-----------|",
        ]
        for _, row in display.iterrows():
            # BUY rows carry NaN realized_pnl/holding_days → render as em dash
            pnl_str = _dollar(row.get("realized_pnl"), "—")
            hold_str = str(row.get("holding_days")) if row["action"] == "SELL" else "—"
            lines.append(
                f"| {row['date']} | {row['action']} | {row['ticker']} "
                f"| {int(row['shares'])} | {_dollar(row['price'])} "
                f"| {_dollar(row['trade_value'])} | {row['reason']} "
                f"| {pnl_str} | {hold_str} |"
            )
    lines.append("")

    # ── Open positions at end ─────────────────────────────────────────────────
    lines += ["## Open Positions at End of Period", ""]
    if positions.empty:
        lines.append("_No open positions at end of backtest period._")
    else:
        lines += [
            "| Ticker | Shares | Entry Price | Final Price | Unrealized P&L | Entry Date |",
            "|--------|--------|------------|------------|----------------|------------|",
        ]
        for _, row in positions.iterrows():
            pnl = (float(row["current_price"]) - float(row["entry_price"])) * int(row["shares"])
            lines.append(
                f"| {row['ticker']} | {int(row['shares'])} "
                f"| {_dollar(float(row['entry_price']))} "
                f"| {_dollar(float(row['current_price']))} "
                f"| {_dollar(pnl)} | {row['entry_date']} |"
            )
    lines.append("")

    # ── Equity curve sample ───────────────────────────────────────────────────
    lines += ["## Equity Curve (first and last 5 days)", ""]
    if equity_df.empty:
        lines.append("_No equity data._")
    else:
        sample = pd.concat([equity_df.head(5), equity_df.tail(5)]).drop_duplicates("date")
        lines += [
            "| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |",
            "|------|----------------|----------|----------------|---------|---------|---------|",
        ]
        for _, row in sample.iterrows():
            lines.append(
                f"| {row['date']} "
                f"| {_dollar(row['total_portfolio_value'])} "
                f"| {_pct(row.get('daily_return'), '—')} "
                f"| {_pct(row.get('cumulative_return'), '—')} "
                f"| {_pct(row.get('spy_cumulative_return'), '—')} "
                f"| {_pct(row.get('qqq_cumulative_return'), '—')} "
                f"| {_pct(row.get('equal_weight_cumulative_return'), '—')} |"
            )
    lines.append("")

    # ── Strategy diagnostics ──────────────────────────────────────────────────
    if diagnostics_md:
        lines += ["", diagnostics_md, ""]

    # ── Sensitivity analysis ──────────────────────────────────────────────────
    if sensitivity_results is not None:
        lines += ["", _sensitivity_section(sensitivity_results, metrics, config), ""]

    # ── Limitations ───────────────────────────────────────────────────────────
    lines += [
        "## Limitations & Assumptions",
        "",
        "1. **Entry fills at next-day close.** Signals fire at day T's close; "
        "orders fill at day T+1's close. This approximates next-morning execution "
        "but uses close rather than true open prices.",
        "2. **Exit fills at same-day close.** Stop-loss, take-profit, and "
        "max-holding-period triggers are detected and filled on the same close. "
        "In practice you may fill at the next open, which could be worse.",
        "3. **Holding period is approximate.** Uses calendar days × 5/7; "
        "does not consult an actual trading-day calendar.",
        "4. **No commissions.** Only the configured slippage "
        f"({r.get('slippage', 0) * 100:.2f}%) is deducted per fill.",
        "5. **No partial fills, no market impact.** All orders assumed fully filled.",
        "6. **Survivorship bias possible.** Universe is fixed; tickers that "
        "were delisted during the test period may not appear in yfinance data.",
        "7. **Past results do not predict future performance.**",
        "",
        "---",
        "_This report is for research purposes only. No real trades are placed._",
    ]

    return "\n".join(lines)


# ─── CSV / file output ────────────────────────────────────────────────────────


def save_backtest_outputs(
    trades_df: pd.DataFrame,
    equity_df: pd.DataFrame,
    report: str,
    output_dir: Path,
    run_date: date,
    sensitivity_results: Optional[List[Dict[str, Any]]] = None,
    diagnostics_df: Optional[pd.DataFrame] = None,
) -> Dict[str, str]:
    """Write all backtest artefacts and return a dict of {label: path}."""
    output_dir.mkdir(parents=True, exist_ok=True)
    tag = run_date.isoformat()

    paths: Dict[str, str] = {}

    trades_path = output_dir / f"backtest_trades_{tag}.csv"
    trades_df.to_csv(trades_path, index=False)
    paths["trades"] = str(trades_path)

    equity_path = output_dir / f"backtest_equity_curve_{tag}.csv"
    equity_df.to_csv(equity_path, index=False)
    paths["equity_curve"] = str(equity_path)

    report_path = output_dir / f"backtest_report_{tag}.md"
    report_path.write_text(report)
    paths["report"] = str(report_path)

    if sensitivity_results:
        sens_df = pd.DataFrame(sensitivity_results)
        sens_path = output_dir / f"backtest_sensitivity_{tag}.csv"
        sens_df.to_csv(sens_path, index=False)
        paths["sensitivity"] = str(sens_path)

    if diagnostics_df is not None and not diagnostics_df.empty:
        diag_path = output_dir / f"backtest_diagnostics_{tag}.csv"
        diagnostics_df.to_csv(diag_path, index=False)
        paths["diagnostics"] = str(diag_path)

    return paths


# ─── CLI entry point ──────────────────────────────────────────────────────────


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AI Paper Trader — Backtest Mode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example:\n  python src/backtest.py --start 2024-01-01 --end 2024-12-31",
    )
    parser.add_argument("--start", required=True, metavar="YYYY-MM-DD", help="Backtest start date")
    parser.add_argument("--end", required=True, metavar="YYYY-MM-DD", help="Backtest end date")
    parser.add_argument(
        "--output",
        default=None,
        metavar="DIR",
        help="Output directory (default: <project_root>/backtests/)",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    setup_logging()

    try:
        start_date = date.fromisoformat(args.start)
        end_date = date.fromisoformat(args.end)
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    if end_date <= start_date:
        print("Error: --end must be after --start")
        sys.exit(1)

    run_date = date.today()
    root = Path(__file__).parent.parent
    config = load_config(root / "config")
    output_dir = Path(args.output) if args.output else root / "backtests"

    log.info("=== AI Paper Trader Backtest ===")
    log.info("Period: %s → %s", start_date, end_date)

    price_data = fetch_backtest_data(config["tickers"], start_date, end_date)

    signal_history: List[Dict[str, Any]] = []
    trades_df, equity_df, final_positions = run_backtest(
        config, price_data, start_date, end_date, signal_sink=signal_history
    )

    metrics = compute_metrics(
        trades_df, equity_df, final_positions, config, start_date, end_date
    )

    log.info("Computing strategy diagnostics...")
    diag = compute_diagnostics(
        config, price_data, trades_df, equity_df, final_positions,
        signal_history, metrics, start_date, end_date,
    )
    diagnostics_md = render_diagnostics_md(diag, config)
    diagnostics_df = diagnostics_csv(diag)

    log.info("Running one-way sensitivity analysis...")
    sensitivity_results = _run_sensitivity_variants(config, price_data, start_date, end_date)

    report = generate_backtest_report(
        metrics, config, trades_df, equity_df, final_positions, run_date,
        sensitivity_results=sensitivity_results,
        diagnostics_md=diagnostics_md,
    )

    paths = save_backtest_outputs(
        trades_df, equity_df, report, output_dir, run_date,
        sensitivity_results=sensitivity_results,
        diagnostics_df=diagnostics_df,
    )

    # ── Console summary ───────────────────────────────────────────────────────
    print()
    print(f"  Period       : {start_date} → {end_date}  ({metrics.get('trading_days', 0)} trading days)")
    print(f"  Total Return : {_pct(metrics.get('total_return'))}")
    print(f"  SPY Return   : {_pct(metrics.get('spy_return'))}")
    print(f"  QQQ Return   : {_pct(metrics.get('qqq_return'))}")
    print(f"  Max Drawdown : {_pct(metrics.get('max_drawdown'))}")
    print(f"  Trades       : {metrics.get('n_buys', 0)} buys / {metrics.get('n_sells', 0)} sells")
    print(f"  Win Rate     : {_pct(metrics.get('win_rate'))}")
    print(f"  Profit Factor: {_pf(metrics.get('profit_factor'))}")
    print()
    print(f"  Report       : {paths['report']}")
    print(f"  Trades CSV   : {paths['trades']}")
    print(f"  Equity CSV   : {paths['equity_curve']}")
    if "sensitivity" in paths:
        print(f"  Sensitivity  : {paths['sensitivity']}")
    if "diagnostics" in paths:
        print(f"  Diagnostics  : {paths['diagnostics']}")
    print()


if __name__ == "__main__":
    main()
