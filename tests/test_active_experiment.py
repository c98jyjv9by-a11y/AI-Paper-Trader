"""
test_active_experiment.py — Ticker-level active-vs-buy-and-hold framework.
Synthetic data; no network.
"""
import logging
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import active_experiment as ae

logging.disable(logging.CRITICAL)   # silence the warmup signal warnings


def _panel(tickers, drift, n=420, seed=1, vol=0.015):
    dates = pd.date_range("2021-01-01", periods=n, freq="B")
    rng = np.random.default_rng(seed)
    cl = pd.DataFrame({t: 100 * np.cumprod(1 + rng.normal(drift.get(t, 0.0004), vol, n)) for t in tickers},
                      index=dates)
    vl = pd.DataFrame({t: np.abs(rng.normal(1e6, 2e5, n)) for t in tickers}, index=dates)
    cl.columns = pd.MultiIndex.from_product([["Close"], cl.columns])
    vl.columns = pd.MultiIndex.from_product([["Volume"], vl.columns])
    return pd.concat([cl, vl], axis=1)


# ─── Single-name simulator ────────────────────────────────────────────────────


class TestSimulateActive:
    def test_uptrend_with_ma_entry_makes_money(self):
        n = 200
        close = 100 * 1.005 ** np.arange(n)
        entry = np.ones(n, dtype=bool)                  # always eligible
        res = ae._simulate_active(close, entry, 60, n - 1, 0.10, None, None, 60, 0.0)
        assert res["total_return"] > 0
        assert res["total_trades"] >= 1

    def test_stop_loss_beats_holding_through_a_crash(self):
        n = 120
        close = np.r_[100 * np.ones(60), 100 * 0.99 ** np.arange(1, 61)]   # flat then -45% decline
        entry = np.ones(n, dtype=bool)
        res = ae._simulate_active(close, entry, 0, n - 1, 0.05, None, None, 60, 0.0)
        hold = close[-1] / close[0] - 1.0                                   # ≈ -45%
        # stopping out (even with re-entries) loses less than riding the crash down
        assert res["total_return"] > hold
        assert res["total_trades"] >= 1

    def test_no_entries_when_signal_off(self):
        n = 120
        close = 100 * 1.004 ** np.arange(n)
        entry = np.zeros(n, dtype=bool)
        res = ae._simulate_active(close, entry, 0, n - 1, 0.10, None, None, 60, 0.0)
        assert res["total_trades"] == 0
        assert res["total_return"] == pytest.approx(0.0)


# ─── Eligibility ──────────────────────────────────────────────────────────────


class TestEligibility:
    def _active(self, **kw):
        base = {"total_return": 0.30, "sharpe": 1.5, "max_drawdown": -0.15,
                "profit_factor": 1.5, "total_trades": 25}
        base.update(kw)
        return base

    def test_passes_when_all_met(self):
        assert ae._eligible(self._active(), hold_ret=0.20, hold_sharpe=1.0, hold_dd=-0.20) is True

    def test_fails_on_too_few_trades(self):
        assert ae._eligible(self._active(total_trades=10), 0.20, 1.0, -0.20) is False

    def test_fails_on_low_profit_factor(self):
        assert ae._eligible(self._active(profit_factor=1.0), 0.20, 1.0, -0.20) is False

    def test_fails_when_not_beating_hold_return(self):
        assert ae._eligible(self._active(total_return=0.10), 0.20, 1.0, -0.20) is False

    def test_drawdown_slack_allows_modest_increase_with_big_return(self):
        # active DD slightly worse (-0.23 vs -0.20) but return +15pp higher → allowed
        a = self._active(total_return=0.40, max_drawdown=-0.23)
        assert ae._eligible(a, hold_ret=0.20, hold_sharpe=1.0, hold_dd=-0.20) is True
        # but a big DD increase is not allowed
        a2 = self._active(total_return=0.40, max_drawdown=-0.40)
        assert ae._eligible(a2, hold_ret=0.20, hold_sharpe=1.0, hold_dd=-0.20) is False


# ─── Grid search + portfolio + benchmarks ─────────────────────────────────────


class TestGridAndPortfolio:
    def test_grid_search_returns_rule(self):
        n = 300
        close = 100 * np.cumprod(1 + np.random.default_rng(2).normal(0.001, 0.014, n))
        entry = {f: (close > pd.Series(close).rolling(50).mean().to_numpy()) for f in ae.ENTRY_FILTERS}
        gs = ae.grid_search_ticker(close, entry, 60, n - 1, 0.001)
        assert gs is not None
        assert set(gs["rule"]) == {"filter", "stop", "tp", "trail", "hold"}
        assert gs["rule"]["stop"] in ae.GRID_STOP and gs["rule"]["hold"] in ae.GRID_HOLD

    def test_portfolio_respects_exposure_cap(self):
        tickers = ["A", "B", "C"]
        data = _panel(tickers + ["SPY", "QQQ"], {"A": 0.001, "B": 0.001, "C": 0.001}, n=300)
        close = data["Close"]
        sig = {f: {t: np.ones(len(close.index), dtype=bool) for t in tickers} for f in ae.ENTRY_FILTERS}
        rules = {t: {"filter": "above_50ma", "stop": 0.10, "tp": None, "trail": None, "hold": 60}
                 for t in tickers}
        cfg = {"tickers": tickers,
               "portfolio": {"starting_value": 100000.0, "max_position_pct": 0.05, "max_total_exposure": 0.30},
               "risk": {"slippage": 0.001}}
        port = ae.simulate_portfolio(data, rules, sig, 60, len(close.index) - 1, cfg)
        assert port["max_exposure"] <= 0.30 + 1e-6        # never breaches global cap
        assert 0.0 <= port["avg_exposure"] <= 0.30 + 1e-6

    def test_ew_and_series_metrics(self):
        data = _panel(["A", "B"], {"A": 0.001, "B": 0.0008}, n=200)
        daily = ae._ew_daily(data["Close"], ["A", "B"], 0, 199)
        m = ae._series_metrics(daily)
        assert m["total_return"] is not None and m["sharpe"] is not None


# ─── End-to-end ───────────────────────────────────────────────────────────────


class TestEndToEnd:
    def test_run_and_render(self):
        uni = ["NVDA", "MSFT", "AAPL", "JPM"]
        data = _panel(uni + ["SPY", "QQQ"], {"NVDA": 0.0014, "MSFT": 0.0008}, n=500, seed=5)
        dates = data["Close"].index
        cfg = {"tickers": uni,
               "portfolio": {"starting_value": 100000.0, "max_position_pct": "auto",
                             "max_total_exposure": 0.75, "max_new_trades_per_day": 3},
               "risk": {"stop_loss": 0.075, "take_profit": 0.10, "max_holding_days": 30, "slippage": 0.001},
               "signals": {"top_candidates": 10, "min_composite_score": 0.6}}
        res = ae.run_active_experiment(cfg, data, (dates[0].date(), dates[300].date()),
                                       (dates[301].date(), dates[-1].date()))
        assert len(res["per_ticker"]) == len(uni)
        md = ae.render_report(res, date(2026, 6, 12))
        for section in ["## Pass / Fail", "Per-Ticker Active vs Buy-and-Hold",
                        "Portfolio vs Benchmarks — TRAIN", "Portfolio vs Benchmarks — TEST",
                        "## Interpretation"]:
            assert section in md
        csv = ae.results_csv(res)
        assert len(csv) == len(uni)
        assert {"ticker", "eligible", "entry_filter", "active_return", "hold_return"}.issubset(csv.columns)
