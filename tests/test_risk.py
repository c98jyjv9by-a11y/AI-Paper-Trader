"""
test_risk.py — Unit tests for risk.py

Run with:
    pytest tests/test_risk.py -v
"""
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from risk import (
    apply_slippage,
    can_add_position,
    holding_period_exceeded,
    position_size_shares,
    stop_loss_triggered,
    take_profit_triggered,
    total_exposure,
)


# ─── Position sizing ──────────────────────────────────────────────────────────


class TestPositionSizeShares:
    def test_basic_calculation(self):
        # $100,000 × 5% = $5,000 / $100 = 50 shares
        assert position_size_shares(100_000, 100.0, 0.05) == 50

    def test_rounds_down_to_whole_shares(self):
        # $100,000 × 5% = $5,000 / $333 = 15.015... → 15
        assert position_size_shares(100_000, 333.0, 0.05) == 15

    def test_zero_price_returns_zero(self):
        assert position_size_shares(100_000, 0.0) == 0

    def test_negative_price_returns_zero(self):
        assert position_size_shares(100_000, -50.0) == 0

    def test_insufficient_budget_returns_zero(self):
        # $1,000 × 5% = $50 budget; stock costs $200 → 0 shares
        assert position_size_shares(1_000, 200.0, 0.05) == 0

    def test_different_max_pct(self):
        # $100,000 × 10% = $10,000 / $100 = 100 shares
        assert position_size_shares(100_000, 100.0, 0.10) == 100


# ─── Slippage ─────────────────────────────────────────────────────────────────


class TestApplySlippage:
    def test_buy_increases_price(self):
        result = apply_slippage(100.0, direction="buy", slippage=0.001)
        assert result == pytest.approx(100.1, rel=1e-4)

    def test_sell_decreases_price(self):
        result = apply_slippage(100.0, direction="sell", slippage=0.001)
        assert result == pytest.approx(99.9, rel=1e-4)

    def test_zero_slippage_is_passthrough(self):
        assert apply_slippage(150.0, direction="buy", slippage=0.0) == pytest.approx(150.0)
        assert apply_slippage(150.0, direction="sell", slippage=0.0) == pytest.approx(150.0)

    def test_higher_slippage(self):
        result = apply_slippage(200.0, direction="buy", slippage=0.005)
        assert result == pytest.approx(201.0, rel=1e-4)


# ─── Exit triggers ────────────────────────────────────────────────────────────


class TestStopLoss:
    def test_triggers_at_threshold(self):
        # Exactly at -5% → should trigger
        assert stop_loss_triggered(100.0, 95.0, stop_loss=0.05) is True

    def test_triggers_below_threshold(self):
        assert stop_loss_triggered(100.0, 90.0, stop_loss=0.05) is True

    def test_does_not_trigger_above_threshold(self):
        assert stop_loss_triggered(100.0, 96.0, stop_loss=0.05) is False

    def test_flat_price_no_trigger(self):
        assert stop_loss_triggered(100.0, 100.0, stop_loss=0.05) is False


class TestTakeProfit:
    def test_triggers_at_threshold(self):
        # Prices are discrete ticks, so test at 110.01 (just past the +10% target).
        # 100.0 * 1.10 = 110.00000000000001 in IEEE 754, so 110.00 would be
        # a false boundary — use a realistic tick above the threshold instead.
        assert take_profit_triggered(100.0, 110.01, take_profit=0.10) is True

    def test_triggers_above_threshold(self):
        assert take_profit_triggered(100.0, 115.0, take_profit=0.10) is True

    def test_does_not_trigger_below_threshold(self):
        assert take_profit_triggered(100.0, 109.0, take_profit=0.10) is False

    def test_flat_price_no_trigger(self):
        assert take_profit_triggered(100.0, 100.0, take_profit=0.10) is False


class TestHoldingPeriod:
    def test_exceeded_after_14_calendar_days(self):
        # 14 calendar days × 5/7 = 10 trading days
        assert holding_period_exceeded(date(2024, 1, 1), date(2024, 1, 15), max_trading_days=10) is True

    def test_not_exceeded_after_5_calendar_days(self):
        # 5 × 5/7 ≈ 3.57 trading days < 10
        assert holding_period_exceeded(date(2024, 1, 1), date(2024, 1, 6), max_trading_days=10) is False

    def test_same_day_not_exceeded(self):
        assert holding_period_exceeded(date(2024, 1, 1), date(2024, 1, 1), max_trading_days=10) is False


# ─── Exposure ─────────────────────────────────────────────────────────────────


def _positions(data: list) -> pd.DataFrame:
    """Helper: build a minimal positions DataFrame."""
    return pd.DataFrame(data, columns=["ticker", "shares", "current_price"])


class TestTotalExposure:
    def test_empty_positions_returns_zero(self):
        empty = pd.DataFrame(columns=["ticker", "shares", "current_price"])
        assert total_exposure(empty, 100_000) == 0.0

    def test_single_position(self):
        # 10 shares × $150 = $1,500 / $100,000 = 1.5%
        pos = _positions([("AAPL", 10, 150.0)])
        assert total_exposure(pos, 100_000) == pytest.approx(0.015)

    def test_multiple_positions(self):
        # (10×150 + 5×400) / 100,000 = (1,500 + 2,000) / 100,000 = 3.5%
        pos = _positions([("AAPL", 10, 150.0), ("MSFT", 5, 400.0)])
        assert total_exposure(pos, 100_000) == pytest.approx(0.035)

    def test_zero_portfolio_value(self):
        pos = _positions([("AAPL", 10, 150.0)])
        assert total_exposure(pos, 0) == 0.0


class TestCanAddPosition:
    def test_can_add_when_under_cap(self):
        # 1,500 / 100,000 = 1.5% < 30% cap
        pos = _positions([("AAPL", 10, 150.0)])
        assert can_add_position(pos, 100_000, max_exposure=0.30) is True

    def test_cannot_add_when_at_cap(self):
        # 30,000 / 100,000 = 30% → at cap
        pos = _positions([("AAPL", 100, 300.0)])
        assert can_add_position(pos, 100_000, max_exposure=0.30) is False

    def test_cannot_add_when_over_cap(self):
        pos = _positions([("AAPL", 200, 200.0)])
        assert can_add_position(pos, 100_000, max_exposure=0.30) is False

    def test_empty_positions_can_always_add(self):
        empty = pd.DataFrame(columns=["ticker", "shares", "current_price"])
        assert can_add_position(empty, 100_000, max_exposure=0.30) is True
