"""
test_signals.py — Unit tests for signals.py

Run with:
    pytest tests/test_signals.py -v
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from signals import calculate_signals, rank_candidates


# ─── Test data factory ────────────────────────────────────────────────────────


def _make_price_data(tickers: list, n_days: int = 30) -> pd.DataFrame:
    """
    Build a synthetic yfinance-style DataFrame with MultiIndex columns.

    Column structure matches yfinance multi-ticker downloads:
        level 0 → field  (Close, Volume)
        level 1 → ticker

    Uses a fixed random seed so tests are deterministic.
    """
    dates = pd.date_range("2024-01-01", periods=n_days, freq="B")
    rng = np.random.default_rng(seed=42)

    close_dict: dict = {}
    volume_dict: dict = {}
    for ticker in tickers:
        # Random walk starting at $100
        prices = 100.0 * np.cumprod(1 + rng.normal(0.001, 0.01, n_days))
        close_dict[ticker] = prices
        volume_dict[ticker] = rng.integers(1_000_000, 5_000_000, n_days).astype(float)

    close_df = pd.DataFrame(close_dict, index=dates)
    volume_df = pd.DataFrame(volume_dict, index=dates)

    # Wrap in MultiIndex matching yfinance output
    close_df.columns = pd.MultiIndex.from_product([["Close"], close_df.columns])
    volume_df.columns = pd.MultiIndex.from_product([["Volume"], volume_df.columns])
    return pd.concat([close_df, volume_df], axis=1)


# ─── calculate_signals ────────────────────────────────────────────────────────


class TestCalculateSignals:
    TICKERS = ["AAPL", "MSFT", "GOOGL"]

    def test_returns_one_row_per_valid_ticker(self):
        data = _make_price_data(self.TICKERS)
        signals = calculate_signals(data, self.TICKERS)
        assert len(signals) == len(self.TICKERS)

    def test_expected_columns_present(self):
        data = _make_price_data(self.TICKERS)
        signals = calculate_signals(data, self.TICKERS)
        expected = {"ticker", "price", "return_1d", "return_5d", "return_20d", "vol_ratio"}
        assert expected.issubset(signals.columns)

    def test_all_tickers_present_in_output(self):
        data = _make_price_data(self.TICKERS)
        signals = calculate_signals(data, self.TICKERS)
        assert set(signals["ticker"].tolist()) == set(self.TICKERS)

    def test_price_is_positive(self):
        data = _make_price_data(self.TICKERS)
        signals = calculate_signals(data, self.TICKERS)
        assert (signals["price"] > 0).all()

    def test_vol_ratio_is_positive(self):
        data = _make_price_data(self.TICKERS)
        signals = calculate_signals(data, self.TICKERS)
        assert (signals["vol_ratio"] > 0).all()

    def test_skips_ticker_with_insufficient_bars(self):
        # n_days=15 < 21 required → both tickers should be skipped
        data = _make_price_data(["AAPL", "MSFT"], n_days=15)
        signals = calculate_signals(data, ["AAPL", "MSFT"])
        assert signals.empty

    def test_skips_ticker_not_in_download(self):
        data = _make_price_data(["AAPL"])
        signals = calculate_signals(data, ["AAPL", "NONEXISTENT"])
        assert len(signals) == 1
        assert signals.iloc[0]["ticker"] == "AAPL"

    def test_returns_empty_dataframe_when_all_skipped(self):
        data = _make_price_data(["AAPL"], n_days=10)  # too few bars
        signals = calculate_signals(data, ["AAPL"])
        assert isinstance(signals, pd.DataFrame)
        assert signals.empty


# ─── rank_candidates ─────────────────────────────────────────────────────────


class TestRankCandidates:
    TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]

    def test_returns_at_most_top_n(self):
        data = _make_price_data(self.TICKERS)
        signals = calculate_signals(data, self.TICKERS)
        ranked = rank_candidates(signals, top_n=3)
        assert len(ranked) <= 3

    def test_sorted_by_composite_score_descending(self):
        data = _make_price_data(self.TICKERS)
        signals = calculate_signals(data, self.TICKERS)
        ranked = rank_candidates(signals)
        scores = ranked["composite_score"].tolist()
        assert scores == sorted(scores, reverse=True), "Scores must be in descending order"

    def test_composite_score_column_present_and_non_null(self):
        data = _make_price_data(self.TICKERS)
        signals = calculate_signals(data, self.TICKERS)
        ranked = rank_candidates(signals)
        assert "composite_score" in ranked.columns
        assert ranked["composite_score"].notna().all()

    def test_composite_score_between_zero_and_one(self):
        data = _make_price_data(self.TICKERS)
        signals = calculate_signals(data, self.TICKERS)
        ranked = rank_candidates(signals)
        # Percentile-based scores weighted to sum to 1.0 max
        assert (ranked["composite_score"] >= 0).all()
        assert (ranked["composite_score"] <= 1.0).all()

    def test_returns_fewer_rows_than_universe_when_top_n_is_small(self):
        data = _make_price_data(self.TICKERS)
        signals = calculate_signals(data, self.TICKERS)
        ranked = rank_candidates(signals, top_n=2)
        assert len(ranked) == 2

    def test_handles_empty_signals(self):
        empty = pd.DataFrame(columns=["ticker", "price", "return_1d", "return_5d", "return_20d", "vol_ratio"])
        ranked = rank_candidates(empty)
        assert ranked.empty

    def test_top_n_larger_than_universe_returns_full_universe(self):
        data = _make_price_data(self.TICKERS)
        signals = calculate_signals(data, self.TICKERS)
        ranked = rank_candidates(signals, top_n=100)
        assert len(ranked) == len(self.TICKERS)
