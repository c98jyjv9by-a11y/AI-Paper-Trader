"""
portfolio.py — Portfolio state I/O and trade recommendation engine.

Responsibilities:
  - Load / save positions.csv and portfolio_state.json
  - Update current prices on open positions
  - Evaluate exit conditions (stop loss, take profit, max holding period)
  - Generate new entry recommendations under all risk caps
"""
import json
import logging
import os
from datetime import date
from typing import Any, Dict, List, Tuple

import pandas as pd

from risk import (
    apply_slippage,
    can_add_position,
    holding_period_exceeded,
    position_size_shares,
    stop_loss_triggered,
    take_profit_triggered,
    total_exposure,
)

log = logging.getLogger(__name__)

_POSITIONS_COLUMNS = ["ticker", "shares", "entry_price", "entry_date", "current_price"]


# ─── State I/O ────────────────────────────────────────────────────────────────


def load_portfolio_state(filepath: str, starting_value: float) -> Dict[str, float]:
    """
    Load cash balance from a JSON file.
    If the file does not exist, return a fresh state using starting_value.
    """
    if os.path.isfile(filepath):
        with open(filepath) as fh:
            state = json.load(fh)
        log.info("Portfolio state loaded: cash=%.2f", state.get("cash", 0))
        return state
    log.info("No portfolio state found — initialising with $%.2f", starting_value)
    return {"cash": starting_value, "starting_value": starting_value}


def save_portfolio_state(state: Dict[str, float], filepath: str) -> None:
    """Persist portfolio state (cash balance etc.) to JSON."""
    with open(filepath, "w") as fh:
        json.dump(state, fh, indent=2)
    log.debug("Portfolio state saved to %s", filepath)


def load_positions(filepath: str) -> pd.DataFrame:
    """
    Load open positions from CSV.
    Returns an empty DataFrame (with correct column names) if the file is
    absent or contains only a header row.
    """
    if os.path.isfile(filepath) and os.path.getsize(filepath) > 0:
        df = pd.read_csv(filepath, parse_dates=["entry_date"])
        df["entry_date"] = pd.to_datetime(df["entry_date"]).dt.date
        if not df.empty:
            log.info("Loaded %d open position(s)", len(df))
            return df
    return pd.DataFrame(columns=_POSITIONS_COLUMNS)


def save_positions(positions: pd.DataFrame, filepath: str) -> None:
    """Write the current open positions to CSV."""
    positions.to_csv(filepath, index=False)
    log.debug("Positions saved: %d row(s) → %s", len(positions), filepath)


# ─── Price refresh ────────────────────────────────────────────────────────────


def update_current_prices(positions: pd.DataFrame, latest_prices: pd.Series) -> pd.DataFrame:
    """
    Overwrite the current_price column with today's closing prices.
    Positions whose ticker is not in latest_prices are left unchanged.
    """
    if positions.empty:
        return positions
    df = positions.copy()
    for i, row in df.iterrows():
        ticker = row["ticker"]
        if ticker in latest_prices.index and not pd.isna(latest_prices[ticker]):
            df.at[i, "current_price"] = round(float(latest_prices[ticker]), 4)
    return df


# ─── Exit evaluation ─────────────────────────────────────────────────────────


def evaluate_exits(
    positions: pd.DataFrame,
    today: date,
    stop_loss: float,
    take_profit: float,
    max_holding_days: int,
    slippage: float,
) -> Tuple[List[Dict[str, Any]], pd.DataFrame]:
    """
    Scan every open position for an exit condition.

    Conditions checked (any one triggers a SELL):
      - Stop loss   : price has fallen ≥ stop_loss% below entry
      - Take profit : price has risen  ≥ take_profit% above entry
      - Max holding : position held for approximately max_holding_days trading days

    Returns:
        exit_trades      — list of SELL recommendation dicts
        remaining        — positions DataFrame with exited rows removed
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
            sell_price = apply_slippage(current_price, direction="sell", slippage=slippage)
            pnl = round((sell_price - entry_price) * shares, 2)
            exit_trades.append(
                {
                    "date": today.isoformat(),
                    "action": "SELL",
                    "ticker": ticker,
                    "shares": shares,
                    "price_with_slippage": sell_price,
                    "trade_value": round(sell_price * shares, 2),
                    "reason": "+".join(triggered),
                    "pnl": pnl,
                    "portfolio_value_after": None,  # filled by main.py after all trades settle
                }
            )
            keep.append(False)
            log.info("EXIT %s | %s | P&L=%.2f", ticker, triggered, pnl)
        else:
            keep.append(True)

    if not keep:
        return exit_trades, positions.copy()

    keep_indices = [idx for idx, flag in zip(positions.index, keep) if flag]
    remaining = positions.loc[keep_indices].reset_index(drop=True)
    return exit_trades, remaining


# ─── Entry generation ─────────────────────────────────────────────────────────


def generate_entries(
    ranked_candidates: pd.DataFrame,
    open_positions: pd.DataFrame,
    portfolio_value: float,
    cash: float,
    config: Dict[str, Any],
    today: date,
) -> List[Dict[str, Any]]:
    """
    Build BUY recommendations from the top-ranked signal candidates.

    Rules enforced:
      - Skip tickers already held
      - Stop when max_new_trades_per_day is reached
      - Stop when max_total_exposure would be breached
      - Skip if available cash is insufficient for even one share
      - Apply slippage to the buy price

    Returns a list of BUY recommendation dicts.
    """
    max_new = config["portfolio"]["max_new_trades_per_day"]
    max_pct = config["portfolio"]["max_position_pct"]
    max_exp = config["portfolio"]["max_total_exposure"]
    slippage = config["risk"]["slippage"]

    held = set(open_positions["ticker"].tolist()) if not open_positions.empty else set()
    entries: List[Dict[str, Any]] = []
    temp_positions = open_positions.copy()  # local copy to track intra-day exposure

    for _, row in ranked_candidates.iterrows():
        if len(entries) >= max_new:
            log.info("Max new trades (%d) reached — stopping entry generation", max_new)
            break

        ticker = str(row["ticker"])
        if ticker in held:
            continue

        if not can_add_position(temp_positions, portfolio_value, max_exp):
            log.info("Exposure cap hit — no further entries today")
            break

        price = float(row["price"])
        buy_price = apply_slippage(price, direction="buy", slippage=slippage)
        shares = position_size_shares(portfolio_value, buy_price, max_pct)

        if shares == 0:
            log.debug("%s: position size rounds to 0 shares — skipped", ticker)
            continue

        trade_value = round(buy_price * shares, 2)
        if trade_value > cash:
            log.info("%s: need %.2f but only %.2f cash available — skipped", ticker, trade_value, cash)
            continue

        score = row.get("composite_score", "n/a")
        entries.append(
            {
                "date": today.isoformat(),
                "action": "BUY",
                "ticker": ticker,
                "shares": shares,
                "price_with_slippage": buy_price,
                "trade_value": trade_value,
                "reason": f"momentum_score={score}",
                "pnl": None,
                "portfolio_value_after": None,
            }
        )

        # Update temp tracker so the next iteration sees correct exposure
        new_row = pd.DataFrame(
            [
                {
                    "ticker": ticker,
                    "shares": shares,
                    "entry_price": buy_price,
                    "entry_date": today,
                    "current_price": price,
                }
            ]
        )
        temp_positions = pd.concat([temp_positions, new_row], ignore_index=True)
        held.add(ticker)
        cash -= trade_value
        log.info("ENTRY %s | shares=%d | buy_price=%.4f | value=%.2f", ticker, shares, buy_price, trade_value)

    return entries
