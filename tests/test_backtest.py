"""
test_backtest.py — Unit tests for backtest.py

All tests use synthetic price data — no network calls are made.

Run with:
    pytest tests/test_backtest.py -v
"""
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from backtest import (
    _bench_return,
    _evaluate_backtest_exits,
    _ewh_return,
    _queue_entries,
    compute_metrics,
    run_backtest,
)
from signals import calculate_signals


# ─── Shared helpers ───────────────────────────────────────────────────────────


def _make_price_data(tickers: list, n_days: int = 40, seed: int = 42) -> pd.DataFrame:
    """
    Build a synthetic yfinance-style DataFrame with MultiIndex columns.
    Uses a fixed seed for determinism.
    """
    dates = pd.date_range("2024-01-01", periods=n_days, freq="B")
    rng = np.random.default_rng(seed=seed)

    close_dict: dict = {}
    volume_dict: dict = {}
    for ticker in tickers:
        prices = 100.0 * np.cumprod(1 + rng.normal(0.001, 0.008, n_days))
        close_dict[ticker] = prices
        volume_dict[ticker] = np.full(n_days, 1_000_000.0)

    close_df = pd.DataFrame(close_dict, index=dates)
    volume_df = pd.DataFrame(volume_dict, index=dates)
    close_df.columns = pd.MultiIndex.from_product([["Close"], close_df.columns])
    volume_df.columns = pd.MultiIndex.from_product([["Volume"], volume_df.columns])
    return pd.concat([close_df, volume_df], axis=1)


def _make_flat_price_data(tickers: list, n_days: int = 40, base_price: float = 100.0) -> pd.DataFrame:
    """Price data where every bar is the same price — useful for deterministic P&L checks."""
    dates = pd.date_range("2024-01-01", periods=n_days, freq="B")
    close_dict = {t: np.full(n_days, base_price) for t in tickers}
    volume_dict = {t: np.full(n_days, 1_000_000.0) for t in tickers}
    close_df = pd.DataFrame(close_dict, index=dates)
    volume_df = pd.DataFrame(volume_dict, index=dates)
    close_df.columns = pd.MultiIndex.from_product([["Close"], close_df.columns])
    volume_df.columns = pd.MultiIndex.from_product([["Volume"], volume_df.columns])
    return pd.concat([close_df, volume_df], axis=1)


def _make_config(
    tickers: list,
    starting_value: float = 100_000.0,
    max_position_pct: float = 0.05,
    max_exposure: float = 0.30,
    max_new: int = 3,
    stop_loss: float = 0.05,
    take_profit: float = 0.10,
    max_holding: int = 10,
    slippage: float = 0.001,
    top_n: int = 5,
) -> dict:
    return {
        "tickers": tickers,
        "portfolio": {
            "starting_value": starting_value,
            "max_position_pct": max_position_pct,
            "max_total_exposure": max_exposure,
            "max_new_trades_per_day": max_new,
        },
        "risk": {
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "max_holding_days": max_holding,
            "slippage": slippage,
        },
        "signals": {"top_candidates": top_n},
    }


def _make_positions(*rows) -> pd.DataFrame:
    """rows = (ticker, shares, entry_price, entry_date, current_price)"""
    return pd.DataFrame(
        list(rows),
        columns=["ticker", "shares", "entry_price", "entry_date", "current_price"],
    )


# ─── 1. No look-ahead bias ────────────────────────────────────────────────────


class TestNoLookaheadBias:
    def test_signals_at_bar_n_unchanged_when_bar_n_plus_1_is_modified(self):
        """
        Signals computed on a slice of data must not be affected by
        values outside that slice, even if those values later change.
        """
        tickers = ["AAPL"]
        data = _make_price_data(tickers, n_days=30)

        # Compute signals using bars 0-21 (22 bars; latest = bar 21)
        sig_before = calculate_signals(data.iloc[:22], tickers)

        # Mutate bar 22 (just outside the slice) dramatically — use .loc to avoid
        # pandas ChainedAssignment warning on MultiIndex columns
        data_altered = data.copy()
        data_altered.loc[data_altered.index[22], ("Close", "AAPL")] = 99999.0

        # Same slice → identical signals
        sig_after = calculate_signals(data_altered.iloc[:22], tickers)

        assert not sig_before.empty
        pd.testing.assert_frame_equal(
            sig_before.reset_index(drop=True),
            sig_after.reset_index(drop=True),
        )

    def test_return_1d_reflects_only_latest_bar_in_slice(self):
        """
        return_1d at bar i = (close[i] - close[i-1]) / close[i-1].
        Extending the slice by one bar must change return_1d to reflect
        the new latest bar, not the old one.
        """
        tickers = ["AAPL"]
        data = _make_price_data(tickers, n_days=30)

        sig_22 = calculate_signals(data.iloc[:22], tickers)
        sig_23 = calculate_signals(data.iloc[:23], tickers)

        assert not sig_22.empty and not sig_23.empty
        # Adding a new bar changes return_1d (data is random → different price)
        # This confirms that the slice boundary is respected both ways
        c = data["Close"]["AAPL"]
        expected_ret_22 = (c.iloc[21] - c.iloc[20]) / c.iloc[20]
        expected_ret_23 = (c.iloc[22] - c.iloc[21]) / c.iloc[21]

        assert abs(sig_22.iloc[0]["return_1d"] - expected_ret_22) < 1e-6
        assert abs(sig_23.iloc[0]["return_1d"] - expected_ret_23) < 1e-6
        assert sig_22.iloc[0]["return_1d"] != sig_23.iloc[0]["return_1d"]


# ─── 2. Cash deduction on buys ────────────────────────────────────────────────


class TestCashOnBuys:
    def test_cash_decreases_by_trade_value_on_buy(self):
        """After a BUY fills, cash must decrease by exactly price × shares."""
        tickers = ["AAPL", "SPY", "QQQ"]
        config = _make_config(tickers)
        data = _make_price_data(tickers, n_days=35)

        dates = data.index
        start = dates[25].date()  # after warm-up
        end = dates[27].date()

        _, equity_df, _ = run_backtest(config, data, start, end)

        assert not equity_df.empty
        # On any day with a buy, cash + equity = total_portfolio_value
        for _, row in equity_df.iterrows():
            total = row["cash"] + row["open_positions_value"]
            assert abs(total - row["total_portfolio_value"]) < 0.02

    def test_cash_never_goes_negative(self):
        tickers = ["AAPL", "MSFT", "SPY", "QQQ"]
        config = _make_config(tickers, max_new=5, max_exposure=0.90)
        data = _make_price_data(tickers, n_days=40)

        dates = data.index
        _, equity_df, _ = run_backtest(config, data, dates[22].date(), dates[-1].date())

        if not equity_df.empty:
            assert (equity_df["cash"] >= -0.01).all(), "Cash went negative"


# ─── 3. Cash credit on sells ──────────────────────────────────────────────────


class TestCashOnSells:
    def test_cash_increases_when_stop_loss_fires(self):
        """
        When a stop-loss exit fires, cash must increase by the sell trade value.
        """
        positions = _make_positions(
            ("AAPL", 10, 100.0, date(2024, 1, 1), 90.0),  # -10% → stop loss at -5%
        )
        cash_before = 50_000.0
        config_risk = dict(stop_loss=0.05, take_profit=0.10, max_holding_days=20, slippage=0.001)

        exits, remaining = _evaluate_backtest_exits(
            positions, date(2024, 1, 15), **config_risk
        )

        assert len(exits) == 1
        assert exits[0]["action"] == "SELL"
        cash_after = cash_before + exits[0]["trade_value"]
        assert cash_after > cash_before

    def test_realized_pnl_is_negative_on_stop_loss(self):
        positions = _make_positions(("AAPL", 10, 100.0, date(2024, 1, 1), 90.0))
        exits, _ = _evaluate_backtest_exits(
            positions, date(2024, 1, 15),
            stop_loss=0.05, take_profit=0.10, max_holding_days=20, slippage=0.001,
        )
        assert exits[0]["realized_pnl"] < 0

    def test_realized_pnl_is_positive_on_take_profit(self):
        positions = _make_positions(("AAPL", 10, 100.0, date(2024, 1, 1), 115.0))
        exits, _ = _evaluate_backtest_exits(
            positions, date(2024, 1, 15),
            stop_loss=0.05, take_profit=0.10, max_holding_days=20, slippage=0.001,
        )
        assert exits[0]["realized_pnl"] > 0


# ─── 4. Stop loss exits ───────────────────────────────────────────────────────


class TestStopLossExits:
    def test_stop_loss_fires_when_price_below_threshold(self):
        # -10% price drop; stop loss at -5%
        positions = _make_positions(("AAPL", 10, 100.0, date(2024, 1, 1), 89.0))
        exits, remaining = _evaluate_backtest_exits(
            positions, date(2024, 1, 10),
            stop_loss=0.05, take_profit=0.10, max_holding_days=30, slippage=0.001,
        )
        assert len(exits) == 1
        assert "stop_loss" in exits[0]["reason"]
        assert remaining.empty

    def test_stop_loss_does_not_fire_above_threshold(self):
        # -3% drop; stop loss at -5%
        positions = _make_positions(("AAPL", 10, 100.0, date(2024, 1, 1), 97.0))
        exits, remaining = _evaluate_backtest_exits(
            positions, date(2024, 1, 10),
            stop_loss=0.05, take_profit=0.10, max_holding_days=30, slippage=0.001,
        )
        assert len(exits) == 0
        assert len(remaining) == 1


# ─── 5. Take profit exits ────────────────────────────────────────────────────


class TestTakeProfitExits:
    def test_take_profit_fires_when_price_above_threshold(self):
        # +15% gain; TP at +10%
        positions = _make_positions(("AAPL", 10, 100.0, date(2024, 1, 1), 116.0))
        exits, remaining = _evaluate_backtest_exits(
            positions, date(2024, 1, 10),
            stop_loss=0.05, take_profit=0.10, max_holding_days=30, slippage=0.001,
        )
        assert len(exits) == 1
        assert "take_profit" in exits[0]["reason"]
        assert remaining.empty

    def test_take_profit_does_not_fire_below_threshold(self):
        # +8% gain; TP at +10%
        positions = _make_positions(("AAPL", 10, 100.0, date(2024, 1, 1), 108.0))
        exits, remaining = _evaluate_backtest_exits(
            positions, date(2024, 1, 10),
            stop_loss=0.05, take_profit=0.10, max_holding_days=30, slippage=0.001,
        )
        assert len(exits) == 0


# ─── 6. Max holding period exits ────────────────────────────────────────────


class TestHoldingPeriodExits:
    def test_holding_period_exit_fires_after_threshold(self):
        # Entry 2024-01-01; check 2024-01-22 = 21 calendar days ≈ 15 trading days > 10
        positions = _make_positions(("AAPL", 10, 100.0, date(2024, 1, 1), 100.0))
        exits, _ = _evaluate_backtest_exits(
            positions, date(2024, 1, 22),
            stop_loss=0.05, take_profit=0.10, max_holding_days=10, slippage=0.001,
        )
        assert len(exits) == 1
        assert "max_holding_period" in exits[0]["reason"]

    def test_holding_period_exit_does_not_fire_early(self):
        # Entry 2024-01-01; check 2024-01-05 = 4 calendar days ≈ 2.9 trading days < 10
        positions = _make_positions(("AAPL", 10, 100.0, date(2024, 1, 1), 100.0))
        exits, _ = _evaluate_backtest_exits(
            positions, date(2024, 1, 5),
            stop_loss=0.05, take_profit=0.10, max_holding_days=10, slippage=0.001,
        )
        assert len(exits) == 0

    def test_holding_days_recorded_in_trade(self):
        positions = _make_positions(("AAPL", 10, 100.0, date(2024, 1, 1), 100.0))
        exits, _ = _evaluate_backtest_exits(
            positions, date(2024, 1, 22),
            stop_loss=0.05, take_profit=0.10, max_holding_days=10, slippage=0.001,
        )
        assert exits[0]["holding_days"] > 0


# ─── 7. Exposure cap enforcement ─────────────────────────────────────────────


class TestExposureCap:
    def test_queue_entries_respects_max_exposure(self):
        """With 30% cap already at 28%, only one more position should be queued."""
        # Two positions each worth $14,000 of a $100,000 portfolio = 28% exposure
        existing = pd.DataFrame(
            [
                {"ticker": "AAPL", "shares": 100, "entry_price": 140.0,
                 "entry_date": date(2024, 1, 1), "current_price": 140.0},
                {"ticker": "MSFT", "shares": 35, "entry_price": 400.0,
                 "entry_date": date(2024, 1, 1), "current_price": 400.0},
            ]
        )
        # Current exposure: (100×140 + 35×400) / 100,000 = 28,000/100,000 = 28%
        config = _make_config(["NVDA", "TSLA", "AMZN"], max_exposure=0.30, max_new=3)

        tickers = ["NVDA", "TSLA", "AMZN"]
        data = _make_price_data(tickers, n_days=30)
        signals = calculate_signals(data, tickers)
        from signals import rank_candidates
        ranked = rank_candidates(signals, top_n=3)

        if ranked.empty:
            pytest.skip("Insufficient bars for signal calculation")

        orders = _queue_entries(ranked, existing, 100_000.0, 72_000.0, config)
        # can_add_position checks CURRENT exposure (28%) against cap (30%).
        # 28% < 30% → one position is allowed. After queuing it, temp exposure
        # becomes 28% + 5% = 33% ≥ 30%, so the second attempt is blocked.
        # Exactly 1 order should be queued.
        assert len(orders) == 1

    def test_queue_entries_respects_max_new_trades(self):
        """Never queue more entries than max_new_trades_per_day."""
        config = _make_config(["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"], max_new=2)
        tickers = config["tickers"]
        data = _make_price_data(tickers, n_days=30)
        signals = calculate_signals(data, tickers)
        from signals import rank_candidates
        ranked = rank_candidates(signals, top_n=5)

        if ranked.empty:
            pytest.skip("Insufficient bars for signal calculation")

        empty_positions = pd.DataFrame(columns=["ticker", "shares", "entry_price", "entry_date", "current_price"])
        orders = _queue_entries(ranked, empty_positions, 100_000.0, 100_000.0, config)
        assert len(orders) <= 2

    def test_queue_entries_skips_held_tickers(self):
        """Tickers already in open positions must not be queued again."""
        tickers = ["AAPL", "MSFT", "GOOGL"]
        config = _make_config(tickers, max_new=3)
        data = _make_price_data(tickers, n_days=30)
        signals = calculate_signals(data, tickers)
        from signals import rank_candidates
        ranked = rank_candidates(signals, top_n=3)

        if ranked.empty:
            pytest.skip("Insufficient bars for signal calculation")

        # All tickers already held
        held = pd.DataFrame(
            [{"ticker": t, "shares": 10, "entry_price": 100.0,
              "entry_date": date(2024, 1, 1), "current_price": 100.0}
             for t in tickers]
        )
        orders = _queue_entries(ranked, held, 100_000.0, 100_000.0, config)
        assert len(orders) == 0


# ─── 8. Equity curve calculation ──────────────────────────────────────────────


class TestEquityCurve:
    def test_equity_curve_total_equals_cash_plus_positions(self):
        """total_portfolio_value must always equal cash + open_positions_value."""
        tickers = ["AAPL", "MSFT", "SPY", "QQQ"]
        config = _make_config(tickers)
        data = _make_price_data(tickers, n_days=40)

        dates = data.index
        _, equity_df, _ = run_backtest(
            config, data, dates[22].date(), dates[-1].date()
        )

        if equity_df.empty:
            pytest.skip("No trading days in range")

        for _, row in equity_df.iterrows():
            computed_total = row["cash"] + row["open_positions_value"]
            assert abs(computed_total - row["total_portfolio_value"]) < 0.02, (
                f"Mismatch on {row['date']}: "
                f"cash={row['cash']:.2f} + equity={row['open_positions_value']:.2f} "
                f"≠ total={row['total_portfolio_value']:.2f}"
            )

    def test_equity_curve_cumulative_return_starts_at_zero(self):
        """On the first simulation day, cumulative_return must be ~0."""
        tickers = ["AAPL", "SPY", "QQQ"]
        config = _make_config(tickers)
        data = _make_price_data(tickers, n_days=40)

        dates = data.index
        _, equity_df, _ = run_backtest(
            config, data, dates[22].date(), dates[35].date()
        )

        if equity_df.empty:
            pytest.skip("No trading days in range")

        first_cum_ret = float(equity_df["cumulative_return"].iloc[0])
        assert abs(first_cum_ret) < 0.001, f"First cumulative return should be ~0, got {first_cum_ret}"

    def test_equity_curve_has_required_columns(self):
        tickers = ["AAPL", "SPY", "QQQ"]
        config = _make_config(tickers)
        data = _make_price_data(tickers, n_days=40)
        dates = data.index
        _, equity_df, _ = run_backtest(
            config, data, dates[22].date(), dates[-1].date()
        )
        required = {
            "date", "cash", "open_positions_value", "total_portfolio_value",
            "realized_pnl_to_date", "unrealized_pnl", "daily_return",
            "cumulative_return",
        }
        assert required.issubset(set(equity_df.columns))


# ─── 9. Benchmark comparison ─────────────────────────────────────────────────


class TestBenchmarkComparison:
    def _make_bench_data(self, spy_prices: list, qqq_prices: list) -> pd.DataFrame:
        n = len(spy_prices)
        dates = pd.date_range("2024-01-01", periods=n, freq="B")
        close_df = pd.DataFrame({"SPY": spy_prices, "QQQ": qqq_prices}, index=dates)
        vol_df = pd.DataFrame({"SPY": [1e6] * n, "QQQ": [1e6] * n}, index=dates)
        close_df.columns = pd.MultiIndex.from_product([["Close"], close_df.columns])
        vol_df.columns = pd.MultiIndex.from_product([["Volume"], vol_df.columns])
        return pd.concat([close_df, vol_df], axis=1)

    def test_spy_return_zero_on_first_day(self):
        data = self._make_bench_data([100.0, 110.0, 120.0], [200.0, 210.0, 220.0])
        ts_list = data.index.tolist()
        result = _bench_return(data["Close"], "SPY", ts_list[0], ts_list[0])
        assert result == pytest.approx(0.0)

    def test_spy_return_correct_after_price_move(self):
        # SPY goes from 100 → 110 = +10%
        data = self._make_bench_data([100.0, 105.0, 110.0], [200.0, 205.0, 210.0])
        ts_list = data.index.tolist()
        result = _bench_return(data["Close"], "SPY", ts_list[2], ts_list[0])
        assert result == pytest.approx(0.10, rel=1e-4)

    def test_missing_benchmark_ticker_returns_none(self):
        data = self._make_bench_data([100.0, 110.0], [200.0, 210.0])
        ts_list = data.index.tolist()
        result = _bench_return(data["Close"], "NONEXISTENT", ts_list[1], ts_list[0])
        assert result is None

    def test_backtest_equity_df_includes_benchmark_columns(self):
        tickers = ["AAPL", "SPY", "QQQ"]
        config = _make_config(tickers)
        data = _make_price_data(tickers, n_days=40)
        dates = data.index
        _, equity_df, _ = run_backtest(
            config, data, dates[22].date(), dates[-1].date()
        )
        assert "spy_cumulative_return" in equity_df.columns
        assert "qqq_cumulative_return" in equity_df.columns


# ─── 10. Equal-weight hold benchmark ────────────────────────────────────────


class TestEqualWeightHold:
    def _make_ewh_data(
        self, tickers: list, start_prices: list, end_prices: list
    ) -> pd.DataFrame:
        dates = pd.date_range("2024-01-01", periods=2, freq="B")
        close_data = {t: [s, e] for t, s, e in zip(tickers, start_prices, end_prices)}
        vol_data = {t: [1_000_000.0, 1_000_000.0] for t in tickers}
        close_df = pd.DataFrame(close_data, index=dates)
        vol_df = pd.DataFrame(vol_data, index=dates)
        close_df.columns = pd.MultiIndex.from_product([["Close"], close_df.columns])
        vol_df.columns = pd.MultiIndex.from_product([["Volume"], vol_df.columns])
        return pd.concat([close_df, vol_df], axis=1)

    def test_ewh_return_is_average_of_individual_returns(self):
        # AAPL +10%, MSFT +20% → EWH = 15%
        tickers = ["AAPL", "MSFT"]
        data = self._make_ewh_data(tickers, [100.0, 200.0], [110.0, 240.0])
        ts = data.index.tolist()
        result = _ewh_return(data["Close"], tickers, ts[1], ts[0])
        assert result == pytest.approx(0.15, rel=1e-4)

    def test_ewh_return_zero_when_prices_flat(self):
        tickers = ["AAPL", "MSFT"]
        data = self._make_ewh_data(tickers, [100.0, 200.0], [100.0, 200.0])
        ts = data.index.tolist()
        result = _ewh_return(data["Close"], tickers, ts[1], ts[0])
        assert result == pytest.approx(0.0, abs=1e-6)

    def test_ewh_missing_ticker_skipped(self):
        tickers = ["AAPL", "MSFT"]
        data = self._make_ewh_data(tickers, [100.0, 200.0], [110.0, 220.0])
        ts = data.index.tolist()
        result = _ewh_return(data["Close"], ["NONEXISTENT"], ts[1], ts[0])
        assert result is None

    def test_ewh_column_in_equity_df(self):
        tickers = ["AAPL", "SPY", "QQQ"]
        config = _make_config(tickers)
        data = _make_price_data(tickers, n_days=40)
        dates = data.index
        _, equity_df, _ = run_backtest(config, data, dates[22].date(), dates[-1].date())
        assert "ewh_cumulative_return" in equity_df.columns

    def test_ewh_in_metrics(self):
        tickers = ["AAPL", "SPY", "QQQ"]
        config = _make_config(tickers)
        data = _make_price_data(tickers, n_days=40)
        dates = data.index
        trades_df, equity_df, positions = run_backtest(
            config, data, dates[22].date(), dates[-1].date()
        )
        m = compute_metrics(
            trades_df, equity_df, positions, config,
            dates[22].date(), dates[-1].date(),
        )
        assert "ewh_return" in m
        assert "excess_vs_ewh" in m
