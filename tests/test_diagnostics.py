"""
test_diagnostics.py — Unit tests for diagnostics.py

All synthetic data; no network. Focus on correctness of forward returns
(no look-ahead), quintiles, attribution, turnover, and benchmark capture.
"""
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from diagnostics import (
    build_signal_panel,
    compute_diagnostics,
    diagnostics_csv,
    entry_vs_exit_attribution,
    exposure_benchmark_capture,
    pnl_attribution,
    render_diagnostics_md,
    signal_predictiveness,
    turnover_diagnostics,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _price_panel(tickers, n=60, growth=None, seed=1):
    """Build a Close/Volume MultiIndex panel. growth: dict ticker->daily factor."""
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    rng = np.random.default_rng(seed)
    close = {}
    for t in tickers:
        if growth and t in growth:
            close[t] = 100.0 * np.power(growth[t], np.arange(n))
        else:
            close[t] = 100.0 * np.cumprod(1 + rng.normal(0.001, 0.01, n))
    vol = {t: np.full(n, 1_000_000.0) + rng.normal(0, 1000, n) for t in tickers}
    cdf = pd.DataFrame(close, index=dates)
    vdf = pd.DataFrame(vol, index=dates)
    cdf.columns = pd.MultiIndex.from_product([["Close"], cdf.columns])
    vdf.columns = pd.MultiIndex.from_product([["Volume"], vdf.columns])
    return pd.concat([cdf, vdf], axis=1)


def _signal_history(tickers, bar_indices, scores_by_idx=None):
    """Minimal signal history rows for the given (bar_idx, ticker) grid."""
    rows = []
    for idx in bar_indices:
        for j, t in enumerate(tickers):
            score = (scores_by_idx or {}).get(idx, {}).get(t, j / max(len(tickers) - 1, 1))
            rows.append({
                "date": pd.Timestamp("2024-01-01").date().isoformat(),
                "bar_idx": idx,
                "ticker": t,
                "return_1d": 0.01 * j,
                "return_5d": 0.02 * j,
                "return_20d": 0.03 * j,
                "vol_ratio": 1.0 + 0.1 * j,
                "composite_score": score,
            })
    return rows


# ─── Forward returns / no look-ahead ──────────────────────────────────────────


class TestForwardReturns:
    def test_forward_return_matches_future_close(self):
        # A rises exactly 1% per bar → fwd_5d = 1.01^5 - 1
        data = _price_panel(["A", "B"], n=60, growth={"A": 1.01, "B": 1.0})
        hist = _signal_history(["A"], [10])
        panel = build_signal_panel(data, hist)
        row = panel[(panel["ticker"] == "A") & (panel["bar_idx"] == 10)].iloc[0]
        assert row["fwd_5d"] == pytest.approx(1.01 ** 5 - 1, rel=1e-9)
        assert row["fwd_10d"] == pytest.approx(1.01 ** 10 - 1, rel=1e-9)
        assert row["fwd_20d"] == pytest.approx(1.01 ** 20 - 1, rel=1e-9)

    def test_forward_return_nan_near_end(self):
        # bar_idx within 20 bars of the end has no full forward window
        data = _price_panel(["A"], n=30, growth={"A": 1.01})
        hist = _signal_history(["A"], [28])   # 28 + 5/10/20 mostly out of range
        panel = build_signal_panel(data, hist)
        row = panel.iloc[0]
        assert np.isnan(row["fwd_20d"])       # 28+20 = 48 >= 30
        assert np.isnan(row["fwd_5d"])        # 28+5 = 33 >= 30

    def test_empty_history_returns_empty_panel(self):
        data = _price_panel(["A"], n=30)
        assert build_signal_panel(data, []).empty


# ─── Quintiles & predictiveness ───────────────────────────────────────────────


class TestPredictiveness:
    def test_quintiles_assigned_when_enough_names(self):
        tickers = [f"T{i}" for i in range(10)]
        data = _price_panel(tickers, n=60)
        hist = _signal_history(tickers, [5, 6, 7])
        panel = build_signal_panel(data, hist)
        qs = set(panel["score_quintile"].dropna().unique())
        assert qs == {1, 2, 3, 4, 5}

    def test_predictiveness_structure(self):
        tickers = [f"T{i}" for i in range(10)]
        data = _price_panel(tickers, n=80)
        hist = _signal_history(tickers, list(range(5, 40)))
        panel = build_signal_panel(data, hist)
        pred = signal_predictiveness(panel)
        assert "composite_score" in pred["correlations"]
        assert set(pred["correlations"]["composite_score"]) == {"fwd_5d", "fwd_10d", "fwd_20d"}
        assert len(pred["quintile_profile"]) == 5
        assert set(pred["top_minus_bottom_spread"]) == {"spread_5d", "spread_10d", "spread_20d"}

    def test_constant_signal_corr_is_none_no_warning(self):
        # vol_ratio constant → correlation undefined, must be None (and no crash/warning)
        tickers = ["A", "B", "C", "D", "E"]
        data = _price_panel(tickers, n=80)
        hist = _signal_history(tickers, list(range(5, 30)))
        for r in hist:
            r["vol_ratio"] = 1.0  # constant
        panel = build_signal_panel(data, hist)
        pred = signal_predictiveness(panel)
        assert pred["correlations"]["vol_ratio"]["fwd_5d"] is None


# ─── Entry vs exit attribution ────────────────────────────────────────────────


class TestEntryExitAttribution:
    def test_raw_returns_positive_for_rising_names(self):
        data = _price_panel(["A", "B"], n=60, growth={"A": 1.01, "B": 1.005})
        hist = _signal_history(["A", "B"], list(range(5, 25)))
        cfg = {"portfolio": {"max_new_trades_per_day": 2}, "risk": {"slippage": 0.0}, "signals": {}}
        attr = entry_vs_exit_attribution(data, hist, cfg, {"total_return": 0.1})
        assert attr["by_period"][5]["avg_return"] > 0
        assert attr["by_period"][30]["avg_return"] > attr["by_period"][5]["avg_return"]
        assert attr["by_period"][5]["win_rate"] == pytest.approx(1.0)


# ─── P&L attribution ──────────────────────────────────────────────────────────


class TestPnLAttribution:
    def _trades(self):
        return pd.DataFrame([
            {"action": "BUY", "ticker": "AAA", "realized_pnl": None},
            {"action": "SELL", "ticker": "AAA", "realized_pnl": 500.0},
            {"action": "SELL", "ticker": "AAA", "realized_pnl": -100.0},
            {"action": "SELL", "ticker": "BBB", "realized_pnl": -300.0},
            {"action": "SELL", "ticker": "CCC", "realized_pnl": 200.0},
        ])

    def test_pnl_by_ticker_sums_realized(self):
        attr = pnl_attribution(self._trades(), pd.DataFrame(), {})
        assert attr["pnl_by_ticker"]["AAA"] == pytest.approx(400.0)
        assert attr["pnl_by_ticker"]["BBB"] == pytest.approx(-300.0)

    def test_includes_unrealized_from_open_positions(self):
        positions = pd.DataFrame([
            {"ticker": "DDD", "shares": 10, "entry_price": 100.0, "current_price": 110.0},
        ])
        attr = pnl_attribution(pd.DataFrame(columns=["action", "ticker", "realized_pnl"]), positions, {})
        assert attr["pnl_by_ticker"]["DDD"] == pytest.approx(100.0)

    def test_top_and_bottom_ordering(self):
        attr = pnl_attribution(self._trades(), pd.DataFrame(), {})
        assert attr["top5"][0][0] == "AAA"      # +400 highest
        assert attr["bottom5"][0][0] == "BBB"   # -300 lowest

    def test_pnl_by_group(self):
        cfg = {"ticker_groups": {"g1": ["AAA", "CCC"], "g2": ["BBB"]}}
        attr = pnl_attribution(self._trades(), pd.DataFrame(), cfg)
        assert attr["has_groups"] is True
        assert attr["pnl_by_group"]["g1"] == pytest.approx(600.0)   # 400 + 200
        assert attr["pnl_by_group"]["g2"] == pytest.approx(-300.0)


# ─── Turnover & re-entry ──────────────────────────────────────────────────────


class TestTurnover:
    def test_stop_then_reentry_counted_within_5_days(self):
        data = _price_panel(["XYZ"], n=30)
        d = [ts.date().isoformat() for ts in data["Close"].index]
        trades = pd.DataFrame([
            {"action": "BUY", "ticker": "XYZ", "date": d[0], "reason": "momentum", "realized_pnl": None},
            {"action": "SELL", "ticker": "XYZ", "date": d[5], "reason": "stop_loss", "realized_pnl": -50.0},
            {"action": "BUY", "ticker": "XYZ", "date": d[8], "reason": "momentum", "realized_pnl": None},  # 3 days later
        ])
        tov = turnover_diagnostics(trades, data, {"avg_holding_days": 4.0}, date(2024, 1, 1), date(2024, 2, 15))
        assert tov["stop_then_reentry_count"] == 1
        assert tov["most_reentered_after_stop"][0] == ("XYZ", 1)

    def test_reentry_not_counted_beyond_5_days(self):
        data = _price_panel(["XYZ"], n=30)
        d = [ts.date().isoformat() for ts in data["Close"].index]
        trades = pd.DataFrame([
            {"action": "SELL", "ticker": "XYZ", "date": d[2], "reason": "stop_loss", "realized_pnl": -50.0},
            {"action": "BUY", "ticker": "XYZ", "date": d[12], "reason": "momentum", "realized_pnl": None},  # 10 days
        ])
        tov = turnover_diagnostics(trades, data, {"avg_holding_days": 4.0}, date(2024, 1, 1), date(2024, 2, 15))
        assert tov["stop_then_reentry_count"] == 0


# ─── Exposure & benchmark capture ─────────────────────────────────────────────


class TestExposureCapture:
    def _equity(self, n=40, mult=2.0):
        dates = pd.date_range("2024-01-01", periods=n, freq="B")
        rng = np.random.default_rng(3)
        qqq_daily = rng.normal(0.0, 0.01, n)
        qqq_daily[0] = 0.0
        strat_daily = mult * qqq_daily               # strategy = mult x QQQ
        qqq_cum = np.cumprod(1 + qqq_daily) - 1
        spy_cum = np.cumprod(1 + 0.5 * qqq_daily) - 1
        total = 100000 * np.cumprod(1 + strat_daily)
        return pd.DataFrame({
            "date": [d.date().isoformat() for d in dates],
            "cash": total * 0.3,
            "open_positions_value": total * 0.7,
            "total_portfolio_value": total,
            "daily_return": strat_daily,
            "spy_cumulative_return": spy_cum,
            "qqq_cumulative_return": qqq_cum,
        })

    def test_beta_and_capture_recovered(self):
        cap = exposure_benchmark_capture(self._equity(mult=2.0))
        assert cap["beta_qqq"] == pytest.approx(2.0, rel=1e-6)
        assert cap["corr_qqq"] == pytest.approx(1.0, rel=1e-6)
        assert cap["up_capture_qqq"] == pytest.approx(2.0, rel=1e-6)
        assert cap["down_capture_qqq"] == pytest.approx(2.0, rel=1e-6)

    def test_exposure_levels(self):
        cap = exposure_benchmark_capture(self._equity())
        assert cap["avg_exposure"] == pytest.approx(0.7, rel=1e-6)
        assert cap["avg_cash_pct"] == pytest.approx(0.3, rel=1e-6)


# ─── Orchestration / rendering ────────────────────────────────────────────────


class TestOrchestration:
    def test_compute_render_and_csv(self):
        tickers = [f"T{i}" for i in range(8)]
        data = _price_panel(tickers, n=80)
        hist = _signal_history(tickers, list(range(5, 40)))
        trades = pd.DataFrame([
            {"action": "BUY", "ticker": "T0", "date": data["Close"].index[6].date().isoformat(), "reason": "m", "realized_pnl": None},
            {"action": "SELL", "ticker": "T0", "date": data["Close"].index[12].date().isoformat(), "reason": "take_profit", "realized_pnl": 120.0},
        ])
        equity = pd.DataFrame({
            "date": [ts.date().isoformat() for ts in data["Close"].index],
            "cash": np.full(80, 70000.0),
            "open_positions_value": np.full(80, 30000.0),
            "total_portfolio_value": np.full(80, 100000.0),
            "daily_return": np.r_[np.nan, np.zeros(79)],
            "spy_cumulative_return": np.zeros(80),
            "qqq_cumulative_return": np.zeros(80),
        })
        cfg = {"tickers": tickers, "portfolio": {"max_new_trades_per_day": 2}, "risk": {"slippage": 0.0}, "signals": {}}
        diag = compute_diagnostics(cfg, data, trades, equity, pd.DataFrame(), hist, {"total_return": 0.01}, date(2024, 1, 1), date(2024, 4, 1))
        md = render_diagnostics_md(diag, cfg)
        for section in [
            "## Signal Predictiveness", "## Entry vs Exit Attribution", "## P&L Attribution",
            "## Turnover and Re-entry Diagnostics", "## Exposure and Benchmark Capture",
            "## Suggested Next Config Tests",
        ]:
            assert section in md
        csv = diagnostics_csv(diag)
        assert {"section", "metric", "value"}.issubset(csv.columns)
        assert len(csv) > 0
