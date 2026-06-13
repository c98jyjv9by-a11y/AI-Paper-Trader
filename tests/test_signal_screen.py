"""
test_signal_screen.py — Factor predictiveness screen. Synthetic data; no network.
Core check: the screen detects a PLANTED predictive factor and stays near zero on
pure noise.
"""
import logging
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import signal_screen as ss

logging.disable(logging.CRITICAL)


def _panel_with_planted_momentum(n=700, k=12, seed=0):
    """Panel where each day's return loads on the prior day's 21d-momentum rank."""
    tickers = [f"T{i}" for i in range(k)]
    dates = pd.date_range("2021-01-01", periods=n, freq="B")
    rng = np.random.default_rng(seed)
    ret = pd.DataFrame(rng.normal(0.0004, 0.012, (n, k)), index=dates, columns=tickers)
    close = pd.DataFrame(100 * np.cumprod(1 + ret.values, axis=0), index=dates, columns=tickers)
    mom = close.pct_change(21)
    z = mom.sub(mom.mean(axis=1), axis=0).div(mom.std(axis=1).replace(0, np.nan), axis=0)
    ret2 = ret.add(0.006 * z.shift(1).fillna(0))     # next-day return loaded on prior momentum
    close = pd.DataFrame(100 * np.cumprod(1 + ret2.values, axis=0), index=dates, columns=tickers)
    vol = pd.DataFrame(np.abs(rng.normal(1e6, 1e5, (n, k))), index=dates, columns=tickers)
    return close, vol, dates


def _noise_panel(n=700, k=12, seed=3):
    tickers = [f"T{i}" for i in range(k)]
    dates = pd.date_range("2021-01-01", periods=n, freq="B")
    rng = np.random.default_rng(seed)
    close = pd.DataFrame(100 * np.cumprod(1 + rng.normal(0.0003, 0.013, (n, k)), axis=0),
                         index=dates, columns=tickers)
    vol = pd.DataFrame(np.abs(rng.normal(1e6, 1e5, (n, k))), index=dates, columns=tickers)
    return close, vol, dates


class TestStats:
    def test_rank_ic_perfect_when_factor_equals_fwd(self):
        idx = pd.date_range("2021-01-01", periods=5, freq="B")
        fac = pd.DataFrame(np.arange(20).reshape(5, 4), index=idx, columns=list("ABCD")).astype(float)
        ic = ss._rank_ic(fac, fac, idx)              # factor vs itself → IC = 1
        assert ic.dropna().mean() == pytest.approx(1.0)

    def test_stats_tstat(self):
        s = pd.Series([0.05, 0.10, 0.15, 0.10, 0.12, 0.08])   # >=5 points, real variance
        st = ss._stats(s)
        assert st["mean"] == pytest.approx(float(s.mean()))
        assert st["t"] is not None and st["t"] > 0

    def test_stats_too_few_points(self):
        assert ss._stats(pd.Series([0.1, 0.1, 0.1]))["mean"] is None


class TestScreen:
    def test_detects_planted_signal(self):
        close, vol, dates = _panel_with_planted_momentum()
        rows = ss.screen_factors(close, vol, (dates[260].date(), dates[480].date()),
                                 (dates[481].date(), dates[-1].date()))
        assert len(rows) == 14
        mom = next(r for r in rows if r["factor"] == "mom_21")
        assert mom["ic_test_20"] > 0.05               # strong out-of-sample IC
        assert ss._is_real(mom) is True               # positive both windows + significant

    def test_noise_has_no_strong_survivor(self):
        close, vol, dates = _noise_panel()
        rows = ss.screen_factors(close, vol, (dates[260].date(), dates[480].date()),
                                 (dates[481].date(), dates[-1].date()))
        # pure noise: IC magnitudes should be small (no large, stable edge)
        assert all(abs(r["ic_test_20"] or 0) < 0.12 for r in rows)

    def test_report_and_csv(self):
        close, vol, dates = _panel_with_planted_momentum()
        rows = ss.screen_factors(close, vol, (dates[260].date(), dates[480].date()),
                                 (dates[481].date(), dates[-1].date()))
        md = ss.render_report(rows, date(2026, 6, 13), (dates[260].date(), dates[480].date()),
                              (dates[481].date(), dates[-1].date()))
        assert "Factor Leaderboard" in md and "rank ic" in md.lower()
        assert "$nan" not in md
        df = ss.results_csv(rows)
        assert "factor" in df.columns and "ic_test_20" in df.columns and len(df) == 14

    def test_is_real_requires_both_windows_and_significance(self):
        assert ss._is_real({"ic_train_20": 0.1, "ic_test_20": 0.1, "ic_test_t_20": 3.0})
        assert not ss._is_real({"ic_train_20": 0.1, "ic_test_20": -0.1, "ic_test_t_20": 3.0})
        assert not ss._is_real({"ic_train_20": 0.1, "ic_test_20": 0.1, "ic_test_t_20": 1.0})
