"""
risk.py — Pure functions for position sizing, slippage, and exit-trigger checks.

All functions are stateless so they can be tested in isolation and reused
without side effects.
"""
import logging
from datetime import date
from typing import Any, Dict, Optional

import pandas as pd

log = logging.getLogger(__name__)


# ─── Position sizing ──────────────────────────────────────────────────────────


def resolve_max_position_pct(config: Dict[str, Any]) -> float:
    """
    Resolve the effective per-position size cap from config.

    If portfolio.max_position_pct is a number, it is used as-is (fixed cap).
    If it is "auto" or null, it scales dynamically with the universe size so the
    strategy can deploy up to max_total_exposure even with few tickers:

        effective = max_total_exposure / n_tickers

    This makes N equal-weight positions sum to exactly max_total_exposure, so a
    2-ticker universe is no longer starved by a 5%-per-name cap. Falls back to a
    sane value if the universe is empty.
    """
    portfolio = config.get("portfolio", {})
    raw = portfolio.get("max_position_pct", "auto")
    n_tickers = max(1, len(config.get("tickers", [])))

    if raw is None or (isinstance(raw, str) and raw.strip().lower() == "auto"):
        exposure = float(portfolio.get("max_total_exposure", 1.0))
        return exposure / n_tickers
    return float(raw)


def position_size_shares(
    portfolio_value: float,
    price: float,
    max_position_pct: float = 0.05,
) -> int:
    """
    Return how many whole shares to buy.

    Dollar budget = portfolio_value × max_position_pct.
    Result is rounded *down* to whole shares; never negative.

    Example:
        position_size_shares(100_000, 150.0, 0.05)
        → int(5_000 / 150) = 33 shares
    """
    if price <= 0:
        return 0
    max_dollars = portfolio_value * max_position_pct
    return int(max_dollars / price)


# ─── Slippage ─────────────────────────────────────────────────────────────────


def apply_slippage(price: float, direction: str = "buy", slippage: float = 0.001) -> float:
    """
    Adjust a quoted price for realistic execution slippage.

    Buys fill slightly *above* the mid price (you pay more).
    Sells fill slightly *below* the mid price (you receive less).

    Default slippage = 0.10 %.
    """
    if direction == "buy":
        return round(price * (1 + slippage), 4)
    return round(price * (1 - slippage), 4)


# ─── Exposure ─────────────────────────────────────────────────────────────────


def total_exposure(positions: pd.DataFrame, portfolio_value: float) -> float:
    """
    Return long exposure as a fraction of portfolio value.

    Requires 'shares' and 'current_price' columns in positions.
    Returns 0.0 for an empty positions DataFrame.
    """
    if positions.empty or portfolio_value <= 0:
        return 0.0
    market_value = (positions["shares"] * positions["current_price"]).sum()
    return float(market_value) / portfolio_value


def can_add_position(
    positions: pd.DataFrame,
    portfolio_value: float,
    max_exposure: float = 0.30,
) -> bool:
    """
    Return True if there is room for at least one more position
    without breaching the max total exposure limit.
    """
    exp = total_exposure(positions, portfolio_value)
    if exp >= max_exposure:
        log.debug("Exposure cap reached: %.1f%% >= %.1f%%", exp * 100, max_exposure * 100)
        return False
    return True


# ─── Exit triggers ────────────────────────────────────────────────────────────


def stop_loss_triggered(
    entry_price: float,
    current_price: float,
    stop_loss: float = 0.05,
) -> bool:
    """Return True if current_price has dropped stop_loss% or more below entry_price."""
    return current_price <= entry_price * (1 - stop_loss)


def take_profit_triggered(
    entry_price: float,
    current_price: float,
    take_profit: Optional[float] = 0.10,
) -> bool:
    """Return True if current_price has risen take_profit% or more above entry_price.

    take_profit=None disables the rule (used by trailing-stop-only profiles).
    """
    if take_profit is None:
        return False
    return current_price >= entry_price * (1 + take_profit)


def trailing_stop_triggered(
    highest_price: float,
    current_price: float,
    trailing_stop: Optional[float] = None,
) -> bool:
    """
    Return True if current_price has fallen trailing_stop% or more below the
    highest price seen since entry. trailing_stop=None disables the rule.

    highest_price is the running peak close since entry, so this only ever
    activates after the position has been held for at least one bar.
    """
    if trailing_stop is None or highest_price is None or highest_price <= 0:
        return False
    return current_price <= highest_price * (1 - trailing_stop)


def holding_period_exceeded(
    entry_date: date,
    current_date: date,
    max_trading_days: int = 10,
) -> bool:
    """
    Return True if the position has been held for approximately max_trading_days.

    Converts calendar days to approximate trading days using a 5/7 ratio
    (5 trading days per 7 calendar days).
    """
    calendar_days = (current_date - entry_date).days
    approx_trading_days = calendar_days * 5 / 7
    return approx_trading_days >= max_trading_days
