"""
main.py — Orchestrator for the AI Paper Trader.

Run from the project root:
    python src/main.py

What happens each run:
  1. Load ticker universe and strategy config
  2. Fetch 60 days of daily OHLCV data via yfinance
  3. Calculate momentum signals and rank candidates
  4. Load open positions; refresh their current prices
  5. Evaluate exit conditions (stop loss / take profit / max holding period)
  6. Generate new entry recommendations (up to max_new_trades_per_day)
  7. Update positions.csv and portfolio_state.json
  8. Append all recommendations to trade_log.csv
  9. Write a Markdown report to reports/
"""
import logging
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import yaml

# Make src/ importable regardless of where the script is launched from.
sys.path.insert(0, str(Path(__file__).parent))

from logger import append_trades, setup_logging
from market_data import fetch_prices, get_latest_prices
from portfolio import (
    evaluate_exits,
    generate_entries,
    load_portfolio_state,
    load_positions,
    save_portfolio_state,
    save_positions,
    update_current_prices,
)
from report import generate_report, save_report
from signals import calculate_signals, rank_candidates

log = logging.getLogger(__name__)


def load_config(config_dir: Path) -> dict:
    """Merge universe.yaml and strategy.yaml into a single config dict."""
    with open(config_dir / "universe.yaml") as fh:
        universe = yaml.safe_load(fh)
    with open(config_dir / "strategy.yaml") as fh:
        strategy = yaml.safe_load(fh)
    return {**universe, **strategy}


def main() -> None:
    setup_logging()
    today = date.today()
    log.info("=== AI Paper Trader — %s ===", today.isoformat())

    # ── Paths ──────────────────────────────────────────────────────────────────
    root = Path(__file__).parent.parent
    config_dir = root / "config"
    data_dir = root / "data"
    reports_dir = root / "reports"
    data_dir.mkdir(exist_ok=True)

    trade_log_path = data_dir / "trade_log.csv"
    positions_path = data_dir / "positions.csv"
    state_path = data_dir / "portfolio_state.json"

    # ── Config ─────────────────────────────────────────────────────────────────
    log.info("Loading configuration")
    config = load_config(config_dir)
    tickers: list = config["tickers"]

    # ── Market data ────────────────────────────────────────────────────────────
    data_cfg = config.get("data", {})
    price_data = fetch_prices(
        tickers,
        period=data_cfg.get("period", "60d"),
        interval=data_cfg.get("interval", "1d"),
    )
    latest_prices = get_latest_prices(price_data, tickers)

    # ── Signals ────────────────────────────────────────────────────────────────
    signals = calculate_signals(price_data, tickers)
    top_n = config.get("signals", {}).get("top_candidates", 10)
    ranked = rank_candidates(signals, top_n=top_n)

    # ── Portfolio state ────────────────────────────────────────────────────────
    state = load_portfolio_state(str(state_path), config["portfolio"]["starting_value"])
    positions = load_positions(str(positions_path))
    positions = update_current_prices(positions, latest_prices)

    # Compute portfolio value before today's trades (cash + open position equity)
    equity_before = 0.0
    if not positions.empty:
        equity_before = float((positions["shares"] * positions["current_price"]).sum())
    portfolio_value = state["cash"] + equity_before

    # ── Evaluate exits ─────────────────────────────────────────────────────────
    exit_trades, remaining_positions = evaluate_exits(
        positions,
        today,
        stop_loss=config["risk"]["stop_loss"],
        take_profit=config["risk"]["take_profit"],
        max_holding_days=config["risk"]["max_holding_days"],
        slippage=config["risk"]["slippage"],
    )

    # Credit proceeds from exits back to cash
    for t in exit_trades:
        state["cash"] += t["trade_value"]

    # ── Generate entries ───────────────────────────────────────────────────────
    entry_trades = generate_entries(
        ranked,
        remaining_positions,
        portfolio_value,
        state["cash"],
        config,
        today,
    )

    # Debit cost of new entries from cash
    for t in entry_trades:
        state["cash"] -= t["trade_value"]

    # ── Update open positions with new entries ─────────────────────────────────
    if entry_trades:
        new_rows = pd.DataFrame(
            [
                {
                    "ticker": t["ticker"],
                    "shares": t["shares"],
                    "entry_price": t["price_with_slippage"],
                    "entry_date": today,
                    "current_price": t["price_with_slippage"],
                }
                for t in entry_trades
            ]
        )
        remaining_positions = pd.concat([remaining_positions, new_rows], ignore_index=True)

    # ── Final portfolio value ──────────────────────────────────────────────────
    equity_after = 0.0
    if not remaining_positions.empty:
        equity_after = float(
            (remaining_positions["shares"] * remaining_positions["current_price"]).sum()
        )
    final_value = state["cash"] + equity_after

    # Back-fill the portfolio_value_after field in all trade records
    all_trades = exit_trades + entry_trades
    for t in all_trades:
        t["portfolio_value_after"] = round(final_value, 2)

    # ── Persist state ──────────────────────────────────────────────────────────
    save_positions(remaining_positions, str(positions_path))
    save_portfolio_state(state, str(state_path))
    if all_trades:
        append_trades(all_trades, str(trade_log_path))

    # ── Report ─────────────────────────────────────────────────────────────────
    report_content = generate_report(
        today=today,
        signals=signals,
        ranked=ranked,
        positions=remaining_positions,
        exit_trades=exit_trades,
        entry_trades=entry_trades,
        portfolio_state=state,
        config=config,
    )
    report_path = save_report(report_content, str(reports_dir), today)

    # ── Summary ────────────────────────────────────────────────────────────────
    print()
    print(f"  Report   : {report_path}")
    print(f"  Value    : {_dollar(final_value)}  (was {_dollar(portfolio_value)})")
    print(f"  Cash     : {_dollar(state['cash'])}")
    print(f"  Positions: {len(remaining_positions)} open")
    print(f"  Exits    : {len(exit_trades)}")
    print(f"  Entries  : {len(entry_trades)}")
    print()


def _dollar(v: float) -> str:
    return f"${v:,.2f}"


if __name__ == "__main__":
    main()
