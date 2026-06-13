"""
test_signal_calibration.py — Per-ticker single-name timing + walk-forward.
Synthetic data; no network. Focus: simulator correctness, no look-ahead, and
the walk-forward driver producing OOS-only results.
"""
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import signal_calibration as sc


def _panel(tickers, closes_by_ticker, n):
    dates = pd.date_range("2020-01-01", periods=n, freq="B")
    cl = pd.DataFrame(closes_by_ticker, index=dates)
    vol = pd.DataFrame({t: np.full(n, 1e6) for t in tickers}, index=dates)
    cl.columns = pd.MultiIndex.from_product([["Close"], cl.columns])
    vol.columns = pd.MultiIndex.from_product([["Volume"], vol.columns])
    return pd.concat([cl, vol], axis=1)


def _smas(series):
    return {w: series.rolling(w).mean().to_numpy() for w in sc._ALL_WINDOWS}


class TestSimulator:
    def test_steady_uptrend_makes_money_and_holds(self):
        n = 200
        close = 100 * 1.005 ** np.arange(n)
        s = pd.Series(close)
        res = sc._simulate(close, 120, 199, _smas(s), fast=20, slow=50, trailing=None, slippage=0.0)
        assert res["total_return"] > 0
        assert res["frac_long"] > 0.8          # trend rule stays invested in an uptrend

    def test_trailing_stop_exits_on_reversal(self):
        n = 200
        up = 100 * 1.01 ** np.arange(120)
        down = up[-1] * 0.97 ** np.arange(1, 81)
        close = np.r_[up, down]
        s = pd.Series(close)
        # with a trailing stop the strategy should exit during the decline → end flat-ish
        res = sc._simulate(close, 110, 199, _smas(s), fast=20, slow=50, trailing=0.10, slippage=0.0)
        assert res["n_trades"] >= 2            # at least one buy and one sell
        assert res["frac_long"] < 1.0          # not invested the whole time

    def test_no_lookahead_decision_uses_only_past(self):
        # Spike a single FUTURE bar (index 160, after b=150); the result on [a,b]
        # must be unchanged because decisions at t use only close[..t].
        n = 200
        rng = np.random.default_rng(1)
        close = 100 * np.cumprod(1 + rng.normal(0.0005, 0.01, n))
        r1 = sc._simulate(close, 120, 150, _smas(pd.Series(close)), 20, 50, 0.10, 0.0)
        close2 = close.copy()
        close2[160] = 99999.0
        r2 = sc._simulate(close2, 120, 150, _smas(pd.Series(close2)), 20, 50, 0.10, 0.0)
        assert r1["total_return"] == pytest.approx(r2["total_return"])


class TestFolds:
    def test_fold_geometry_is_out_of_sample(self):
        folds = sc._build_folds(0, sc.TRAIN_BARS + sc.TEST_BARS - 1)
        assert len(folds) == 1
        tr_a, tr_b, te_a, te_b = folds[0]
        assert te_a == tr_b + 1                # test starts after train ends (no overlap)
        assert te_b - te_a + 1 == sc.TEST_BARS

    def test_multiple_folds_step(self):
        last = sc.TRAIN_BARS + 3 * sc.TEST_BARS
        folds = sc._build_folds(0, last)
        assert len(folds) >= 2
        # train windows advance by STEP_BARS
        assert folds[1][0] - folds[0][0] == sc.STEP_BARS


class TestWalkForwardAndUniverse:
    def test_walk_forward_returns_oos_metrics(self):
        n = sc.TRAIN_BARS + 4 * sc.TEST_BARS + 120
        close = 100 * 1.004 ** np.arange(n)
        s = pd.Series(close)
        res = sc.walk_forward_ticker(close, _smas(s), 0, n - 1, slippage=0.0)
        assert res is not None
        for k in ["timed_return", "hold_return", "outperformance", "test_win_rate",
                  "param_stability", "modal_params", "oos_trades"]:
            assert k in res
        assert 0.0 <= res["param_stability"] <= 1.0

    def test_universe_calibration_and_report(self):
        n = sc.TRAIN_BARS + 5 * sc.TEST_BARS + 120
        rng = np.random.default_rng(3)
        closes = {
            "UP": 100 * 1.004 ** np.arange(n),
            "CHOP": 100 * np.cumprod(1 + rng.normal(0.0, 0.012, n)),
        }
        data = _panel(["UP", "CHOP"], closes, n)
        d0 = data["Close"].index[0].date()
        d1 = data["Close"].index[-1].date()
        results = sc.calibrate_universe(data, ["UP", "CHOP"], d0, d1, slippage=0.001)
        assert len(results) == 2
        md = sc.render_report(results, date(2026, 6, 12), d0, d1)
        assert "Timing vs Buy-and-Hold" in md and "out-of-sample" in md.lower()
        csv = sc.results_csv(results)
        assert {"ticker", "timed_return", "hold_return", "outperformance",
                "param_stability", "modal_fast"}.issubset(csv.columns)

    def test_insufficient_history_skipped(self):
        n = 120  # far less than one train+test fold
        data = _panel(["X"], {"X": 100 * 1.003 ** np.arange(n)}, n)
        d0 = data["Close"].index[0].date(); d1 = data["Close"].index[-1].date()
        assert sc.calibrate_universe(data, ["X"], d0, d1, slippage=0.0) == []


class TestCriteriaExport:
    def _fake_results(self):
        return [
            {"ticker": "NVDA", "outperformance": 0.12, "param_stability": 0.75,
             "beats_exposure_matched": True, "timed_return": 0.20, "hold_return": 0.08,
             "modal_params": {"fast": 20, "slow": 50, "trailing": 0.15}},
            {"ticker": "CHOP", "outperformance": -0.05, "param_stability": 0.4,
             "beats_exposure_matched": False, "timed_return": -0.02, "hold_return": 0.03,
             "modal_params": {"fast": 10, "slow": 50, "trailing": None}},
        ]

    def test_export_then_load_roundtrips(self, tmp_path):
        out = tmp_path / "crit.yaml"
        sc.export_criteria(self._fake_results(), out, date(2026, 6, 12))
        crit = sc.load_criteria(out)
        assert crit["NVDA"] == (20, 50, 0.15)
        assert crit["CHOP"] == (10, 50, None)   # trailing: null → None

    def test_export_flags_candidates(self, tmp_path):
        out = tmp_path / "crit.yaml"
        sc.export_criteria(self._fake_results(), out, date(2026, 6, 12))
        text = out.read_text()
        # NVDA beat exp-matched + stable → candidate true; CHOP → false
        assert "NVDA: {fast: 20, slow: 50, trailing: 0.15, candidate: true" in text
        assert "candidate: false" in text

    def test_seed_config_loads_and_covers_universe(self):
        root = Path(__file__).parent.parent
        crit = sc.load_criteria(root / "config" / "ticker_timing_criteria.yaml")
        universe = set(__import__("yaml").safe_load(
            (root / "config" / "universe.yaml").read_text())["tickers"])
        assert universe.issubset(set(crit))          # every universe ticker has seed criteria
        for fast, slow, trailing in crit.values():
            assert fast < slow                       # fast MA shorter than slow
            assert trailing is None or 0 < trailing < 1


class TestCalibrationObjective:
    def test_objective_value_picks_metric(self):
        # a simulation with known daily returns
        res = {"total_return": 0.20, "daily_returns": np.array([0.01, -0.005, 0.02, 0.0, 0.015])}
        assert sc._objective_value(res, "total_return") == 0.20
        assert sc._objective_value(res, "sharpe") == pytest.approx(sc._sharpe(res["daily_returns"]))
        # calmar uses annualized/maxdd
        cal = sc._objective_value(res, "calmar")
        assert cal == pytest.approx(sc._calmar(0.20, 6, sc._max_drawdown(res["daily_returns"])))

    def test_walk_forward_accepts_objective(self):
        n = sc.TRAIN_BARS + 4 * sc.TEST_BARS + 120
        rng = np.random.default_rng(2)
        close = 100 * np.cumprod(1 + rng.normal(0.0008, 0.013, n))
        s = pd.Series(close)
        smas = {w: s.rolling(w).mean().to_numpy() for w in sc._ALL_WINDOWS}
        r_tr = sc.walk_forward_ticker(close, smas, 0, n - 1, 0.001, objective="total_return")
        r_sh = sc.walk_forward_ticker(close, smas, 0, n - 1, 0.001, objective="sharpe")
        assert r_tr is not None and r_sh is not None
        # both produce valid OOS results; selection may differ but structure is identical
        assert set(r_tr) == set(r_sh)


class TestEvaluateCriteria:
    def test_evaluate_applies_fixed_rule(self):
        n = 400
        dates = pd.date_range("2021-01-01", periods=n, freq="B")
        closes = {
            "UP": 100 * 1.004 ** np.arange(n),                    # steady uptrend
            "DN": 100 * 0.997 ** np.arange(n),                    # steady downtrend
        }
        cl = pd.DataFrame(closes, index=dates)
        vol = pd.DataFrame({t: np.full(n, 1e6) for t in closes}, index=dates)
        cl.columns = pd.MultiIndex.from_product([["Close"], cl.columns])
        vol.columns = pd.MultiIndex.from_product([["Volume"], vol.columns])
        data = pd.concat([cl, vol], axis=1)
        criteria = {"UP": (20, 50, 0.15), "DN": (20, 50, 0.15)}
        d0, d1 = dates[0].date(), dates[-1].date()
        res = sc.evaluate_criteria(data, criteria, d0, d1, slippage=0.001)
        by = {r["ticker"]: r for r in res}
        assert by["UP"]["timed_return"] > 0                       # trend rule rides the uptrend
        assert by["DN"]["avg_frac_long"] < 0.2                    # rule stays out of the downtrend
        # modal_params echo the fixed criteria (no re-fitting)
        assert by["UP"]["modal_params"] == {"fast": 20, "slow": 50, "trailing": 0.15}

    def test_render_evaluation_sections(self):
        n = 400
        dates = pd.date_range("2021-01-01", periods=n, freq="B")
        cl = pd.DataFrame({"UP": 100 * 1.004 ** np.arange(n)}, index=dates)
        vol = pd.DataFrame({"UP": np.full(n, 1e6)}, index=dates)
        cl.columns = pd.MultiIndex.from_product([["Close"], cl.columns])
        vol.columns = pd.MultiIndex.from_product([["Volume"], vol.columns])
        data = pd.concat([cl, vol], axis=1)
        d0, d1 = dates[0].date(), dates[-1].date()
        res = sc.evaluate_criteria(data, {"UP": (20, 50, 0.15)}, d0, d1, 0.001)
        md = sc.render_evaluation(res, "seed.yaml", date(2026, 6, 12), d0, d1)
        assert "Criteria Evaluation" in md and "no parameter search" in md.lower()
        assert "Beats Exp-Matched" in md
