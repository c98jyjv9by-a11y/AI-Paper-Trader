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
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import yfinance as yf
import yaml

sys.path.insert(0, str(Path(__file__).parent))

from logger import setup_logging
from portfolio import update_current_prices
from risk import (
    apply_slippage,
    can_add_position,
    holding_period_exceeded,
    position_size_shares,
    stop_loss_triggered,
    take_profit_triggered,
)
from signals import calculate_signals, rank_candidates

log = logging.getLogger(__name__)

_BENCH_TICKERS = ["SPY", "QQQ"]
_POS_COLS = ["ticker", "shares", "entry_price", "entry_date", "current_price"]


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
    take_profit: float,
    max_holding_days: int,
    slippage: float,
) -> Tuple[List[Dict[str, Any]], pd.DataFrame]:
    """
    Scan open positions for exit conditions.

    Mirrors portfolio.evaluate_exits() but uses the column name 'realized_pnl'
    and includes 'holding_days' — required by the backtest trade log schema.
    Fill price = today's close with slippage (see assumption #3 in module doc).
    """
    exit_trades: List[Dict[str, Any]] = []
    keep: List[bool] = []

    for _, row in positions.iterrows():
        entry_price = float(row["entry_price"])
        current_price = float(row["current_price"])
        entry_date = row["entry_date"]
        ticker = str(row["ticker"])
        shares = int(row["shares"])

        triggered = []
        if stop_loss_triggered(entry_price, current_price, stop_loss):
            triggered.append("stop_loss")
        if take_profit_triggered(entry_price, current_price, take_profit):
            triggered.append("take_profit")
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
    max_pct = config["portfolio"]["max_position_pct"]
    max_exp = config["portfolio"]["max_total_exposure"]

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
        shares = position_size_shares(portfolio_value, price, max_pct)
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


# ─── Main simulation loop ─────────────────────────────────────────────────────


def run_backtest(
    config: Dict[str, Any],
    price_data: pd.DataFrame,
    start_date: date,
    end_date: date,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Walk-forward simulation over [start_date, end_date].

    Returns:
        trades_df    — every simulated BUY and SELL
        equity_df    — daily equity curve with benchmark columns
        positions    — positions still open at the end of the period
    """
    tickers: List[str] = config["tickers"]
    slippage = config["risk"]["slippage"]
    stop_loss = config["risk"]["stop_loss"]
    take_profit = config["risk"]["take_profit"]
    max_holding = config["risk"]["max_holding_days"]
    starting_value = config["portfolio"]["starting_value"]
    top_n = config.get("signals", {}).get("top_candidates", 10)

    close = price_data["Close"]
    all_timestamps = close.index.tolist()

    sim_timestamps = [
        ts for ts in all_timestamps
        if start_date <= ts.date() <= end_date
    ]
    if not sim_timestamps:
        raise ValueError(f"No trading days found between {start_date} and {end_date}.")

    bench_start_ts = sim_timestamps[0]

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

    for bar_ts in sim_timestamps:
        bar_date = bar_ts.date()
        bar_idx = all_timestamps.index(bar_ts)
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
                }
            )
        if filled:
            positions = pd.concat(
                [positions, pd.DataFrame(filled)], ignore_index=True
            )
        pending_orders = []

        # ── 2. Update open position prices ────────────────────────────────────
        positions = update_current_prices(positions, today_prices)

        # ── 3. Evaluate exits against today's close ───────────────────────────
        exit_trades, positions = _evaluate_backtest_exits(
            positions, bar_date, stop_loss, take_profit, max_holding, slippage
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
        if bar_idx + 1 < len(all_timestamps):
            data_slice = price_data.iloc[: bar_idx + 1]   # ← only data up to today
            signals = calculate_signals(data_slice, tickers)
            if not signals.empty:
                ranked = rank_candidates(signals, top_n=top_n)
                pending_orders = _queue_entries(
                    ranked, positions, portfolio_value, cash, config
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
    total_return = (final_value - starting_value) / starting_value

    # Max drawdown
    roll_max = equity_df["total_portfolio_value"].cummax()
    drawdown = (equity_df["total_portfolio_value"] - roll_max) / roll_max
    max_drawdown = float(drawdown.min())

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

    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "trading_days": len(equity_df),
        "starting_value": starting_value,
        "ending_value": final_value,
        "total_return": total_return,
        "max_drawdown": max_drawdown,
        "spy_return": spy_return,
        "qqq_return": qqq_return,
        "excess_vs_spy": (total_return - spy_return) if spy_return is not None else None,
        "excess_vs_qqq": (total_return - qqq_return) if qqq_return is not None else None,
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
    }


# ─── Report builder ───────────────────────────────────────────────────────────


def _pct(v: Optional[float], default: str = "N/A") -> str:
    return f"{v * 100:+.2f}%" if v is not None else default


def _dollar(v: Optional[float], default: str = "N/A") -> str:
    return f"${v:,.2f}" if v is not None else default


def _pf(v: Optional[float]) -> str:
    return f"{v:.2f}" if v is not None else "N/A (no losses)"


def generate_backtest_report(
    metrics: Dict[str, Any],
    config: Dict[str, Any],
    trades_df: pd.DataFrame,
    equity_df: pd.DataFrame,
    positions: pd.DataFrame,
    run_date: date,
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
        "| Metric | Strategy | SPY | QQQ |",
        "|--------|----------|-----|-----|",
        f"| Total Return | {_pct(m.get('total_return'))} | {_pct(m.get('spy_return'))} | {_pct(m.get('qqq_return'))} |",
        f"| Excess vs SPY | {_pct(m.get('excess_vs_spy'))} | — | — |",
        f"| Excess vs QQQ | {_pct(m.get('excess_vs_qqq'))} | — | — |",
        f"| Max Drawdown | {_pct(m.get('max_drawdown'))} | — | — |",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Starting Value | {_dollar(m.get('starting_value'))} |",
        f"| Ending Value | {_dollar(m.get('ending_value'))} |",
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
        "",
    ]

    # ── Strategy parameters ───────────────────────────────────────────────────
    lines += [
        "## Strategy Parameters Used",
        "",
        "| Parameter | Value |",
        "|-----------|-------|",
        f"| Starting Portfolio | {_dollar(p.get('starting_value'))} |",
        f"| Max Position Size | {p.get('max_position_pct', 0) * 100:.0f}% |",
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
            pnl_str = _dollar(row.get("realized_pnl")) if row.get("realized_pnl") is not None else "—"
            hold_str = str(row.get("holding_days", "—")) if row["action"] == "SELL" else "—"
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
            "| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret |",
            "|------|----------------|----------|----------------|---------|---------|",
        ]
        for _, row in sample.iterrows():
            lines.append(
                f"| {row['date']} "
                f"| {_dollar(row['total_portfolio_value'])} "
                f"| {_pct(row.get('daily_return'), '—')} "
                f"| {_pct(row.get('cumulative_return'), '—')} "
                f"| {_pct(row.get('spy_cumulative_return'), '—')} "
                f"| {_pct(row.get('qqq_cumulative_return'), '—')} |"
            )
    lines.append("")

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

    trades_df, equity_df, final_positions = run_backtest(
        config, price_data, start_date, end_date
    )

    metrics = compute_metrics(
        trades_df, equity_df, final_positions, config, start_date, end_date
    )

    report = generate_backtest_report(
        metrics, config, trades_df, equity_df, final_positions, run_date
    )

    paths = save_backtest_outputs(trades_df, equity_df, report, output_dir, run_date)

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
    print()


if __name__ == "__main__":
    main()
