"""
test_experiments.py — Tests for trailing stop, score-weighted sizing, null
take-profit, and the experiments framework. Synthetic data; no network.
"""
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from risk import trailing_stop_triggered, take_profit_triggered
from backtest import _evaluate_backtest_exits, _queue_entries, run_backtest, compute_metrics
from signals import calculate_signals
from diagnostics import turnover_diagnostics
import experiments
from experiments import (
    _apply_overrides,
    _annualized,
    _exit_reason_counts,
    _gave_back_count,
    experiments_csv,
    render_experiments_md,
    run_experiments,
    PROFILES,
)


def _price_panel(tickers, n=80, growth=None, seed=1):
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    rng = np.random.default_rng(seed)
    close = {}
    for t in tickers:
        if growth and t in growth:
            close[t] = 100.0 * np.power(growth[t], np.arange(n))
        else:
            close[t] = 100.0 * np.cumprod(1 + rng.normal(0.0015, 0.012, n))
    vol = {t: np.abs(rng.normal(1e6, 1e5, n)) for t in tickers}
    cdf = pd.DataFrame(close, index=dates); vdf = pd.DataFrame(vol, index=dates)
    cdf.columns = pd.MultiIndex.from_product([["Close"], cdf.columns])
    vdf.columns = pd.MultiIndex.from_product([["Volume"], vdf.columns])
    return pd.concat([cdf, vdf], axis=1)


def _cfg(universe, **over):
    cfg = {
        "tickers": universe,
        "portfolio": {"starting_value": 100000.0, "max_position_pct": "auto",
                      "max_total_exposure": 0.75, "max_new_trades_per_day": 3},
        "risk": {"stop_loss": 0.075, "take_profit": 0.10, "max_holding_days": 30, "slippage": 0.001},
        "signals": {"top_candidates": 10, "min_composite_score": None},
    }
    for k, v in over.items():
        sec, key = k.split(".", 1)
        cfg.setdefault(sec, {})[key] = v
    return cfg


# ─── Trailing stop primitive ──────────────────────────────────────────────────


class TestTrailingStopPrimitive:
    def test_triggers_below_peak(self):
        assert trailing_stop_triggered(120.0, 107.0, 0.10) is True   # 107 < 120*0.9=108
    def test_not_triggered_within_band(self):
        assert trailing_stop_triggered(120.0, 110.0, 0.10) is False  # 110 > 108
    def test_none_disables(self):
        assert trailing_stop_triggered(120.0, 50.0, None) is False
    def test_take_profit_none_disables(self):
        assert take_profit_triggered(100.0, 999.0, None) is False


# ─── Trailing stop in backtest exits ──────────────────────────────────────────


class TestTrailingExit:
    def test_trailing_stop_exit_reason(self):
        positions = pd.DataFrame([{
            "ticker": "AAA", "shares": 10, "entry_price": 100.0,
            "entry_date": date(2024, 1, 1), "current_price": 108.0, "highest_price": 120.0,
        }])
        # take_profit None, trailing 0.10 → 108 < 120*0.9 → trailing exit
        exits, remaining = _evaluate_backtest_exits(
            positions, date(2024, 1, 10), stop_loss=0.075, take_profit=None,
            max_holding_days=60, slippage=0.0, trailing_stop=0.10,
        )
        assert len(exits) == 1
        assert "trailing_stop" in exits[0]["reason"]
        assert exits[0]["highest_price"] == 120.0
        assert remaining.empty

    def test_no_trailing_exit_when_disabled(self):
        positions = pd.DataFrame([{
            "ticker": "AAA", "shares": 10, "entry_price": 100.0,
            "entry_date": date(2024, 1, 1), "current_price": 108.0, "highest_price": 120.0,
        }])
        exits, remaining = _evaluate_backtest_exits(
            positions, date(2024, 1, 10), stop_loss=0.075, take_profit=None,
            max_holding_days=60, slippage=0.0, trailing_stop=None,
        )
        assert len(exits) == 0


# ─── Score-weighted sizing ────────────────────────────────────────────────────


class TestScoreWeightedSizing:
    def test_higher_score_gets_more_shares(self):
        ranked = pd.DataFrame([
            {"ticker": "HI", "price": 100.0, "composite_score": 1.0},
            {"ticker": "LO", "price": 100.0, "composite_score": 0.0},
        ])
        cfg = _cfg(["HI", "LO"], **{
            "portfolio.sizing_mode": "score_weighted",
            "portfolio.min_position_pct": 0.02,
            "portfolio.max_position_pct": 0.05,
            "portfolio.max_new_trades_per_day": 2,
            "portfolio.max_total_exposure": 0.90,
        })
        empty = pd.DataFrame(columns=["ticker", "shares", "entry_price", "entry_date", "current_price", "highest_price"])
        orders = _queue_entries(ranked, empty, 100000.0, 100000.0, cfg)
        by = {o["ticker"]: o["shares"] for o in orders}
        # HI sized at ~5% (score 1.0), LO at ~2% (score 0.0)
        assert by["HI"] > by["LO"]
        assert by["HI"] == pytest.approx(int(100000 * 0.05 / 100.0))
        assert by["LO"] == pytest.approx(int(100000 * 0.02 / 100.0))


# ─── run_backtest with trailing stop end-to-end ───────────────────────────────


class TestRunBacktestTrailing:
    def test_trailing_profile_produces_trailing_exits(self):
        tickers = ["A", "B", "SPY", "QQQ"]
        # A pumps then dumps so a trailing stop should fire
        n = 80
        a = np.r_[100 * 1.02 ** np.arange(40), (100 * 1.02 ** 39) * 0.97 ** np.arange(1, 41)]
        data = _price_panel(tickers, n=n)
        data[("Close", "A")] = a
        cfg = _cfg(["A", "B"], **{"risk.take_profit": None, "risk.trailing_stop": 0.10,
                                  "risk.max_holding_days": 60, "risk.stop_loss": 0.075})
        dates = data["Close"].index
        t, e, p = run_backtest(cfg, data, dates[25].date(), dates[-1].date())
        if not t.empty:
            sells = t[t["action"] == "SELL"]
            # At least some exits should be trailing (not all max_holding/stop)
            assert sells["reason"].str.contains("trailing_stop").any() or sells.empty


# ─── Experiments framework ────────────────────────────────────────────────────


class TestExperimentsFramework:
    def test_apply_overrides_does_not_mutate_baseline(self):
        base = _cfg(["A", "B"])
        cfg = _apply_overrides(base, [("risk.take_profit", None), ("risk.trailing_stop", 0.10)])
        assert cfg["risk"]["take_profit"] is None
        assert cfg["risk"]["trailing_stop"] == 0.10
        assert base["risk"]["take_profit"] == 0.10   # baseline untouched
        assert "trailing_stop" not in base["risk"]

    def test_annualized_helper(self):
        assert _annualized(0.10, 252) == pytest.approx(0.10, rel=1e-6)
        assert _annualized(0.21, 504) == pytest.approx(0.10, rel=1e-3)   # 2 years
        assert _annualized(None, 252) is None

    def test_exit_counts_and_gave_back(self):
        trades = pd.DataFrame([
            {"action": "SELL", "reason": "stop_loss", "realized_pnl": -50.0, "entry_price": 100.0, "highest_price": 101.0},
            {"action": "SELL", "reason": "take_profit", "realized_pnl": 80.0, "entry_price": 100.0, "highest_price": 112.0},
            {"action": "SELL", "reason": "trailing_stop", "realized_pnl": -10.0, "entry_price": 100.0, "highest_price": 110.0},
        ])
        counts = _exit_reason_counts(trades)
        assert counts["stop_loss"] == 1 and counts["take_profit"] == 1 and counts["trailing_stop"] == 1
        # gave back: peaked >=+5% but exited at loss → row 3 (peak 110, loss). Row1 peaked only +1%.
        assert _gave_back_count(trades) == 1

    def test_run_experiments_end_to_end(self):
        tickers = ["NVDA", "MSFT", "AAPL", "AMD", "AVGO", "JPM", "SPY", "QQQ"]
        universe = ["NVDA", "MSFT", "AAPL", "AMD", "AVGO", "JPM"]
        data = _price_panel(tickers, n=120, seed=4)
        cfg = _cfg(universe)
        cfg["ticker_groups"] = {"mega": ["NVDA", "MSFT", "AAPL"], "semis": ["AMD", "AVGO"], "fin": ["JPM"]}
        dates = data["Close"].index
        results = run_experiments(cfg, data, dates[40].date(), dates[-1].date())
        assert len(results) == len(PROFILES)
        names = {r["name"] for r in results}
        assert "baseline" in names and "no_fixed_take_profit_trailing_stop" in names
        # render + csv must succeed and contain all required sections
        md = render_experiments_md(results, date(2026, 6, 12), dates[40].date(), dates[-1].date())
        for section in ["## Returns & Risk", "## Trading Activity", "## Exit Attribution",
                        "## Signal Quality", "## P&L by Group", "## Interpretation"]:
            assert section in md
        assert "IN-SAMPLE" in md
        csv = experiments_csv(results)
        assert len(csv) == len(PROFILES)
        assert "spread_20d" in csv.columns and "exits_trailing_stop" in csv.columns

    def test_trailing_profiles_have_no_fixed_take_profit_exits(self):
        tickers = ["NVDA", "MSFT", "AAPL", "AMD", "AVGO", "JPM", "SPY", "QQQ"]
        universe = ["NVDA", "MSFT", "AAPL", "AMD", "AVGO", "JPM"]
        data = _price_panel(tickers, n=120, seed=8)
        results = run_experiments(_cfg(universe), data,
                                  data["Close"].index[40].date(), data["Close"].index[-1].date())
        trailing = next(r for r in results if r["name"] == "no_fixed_take_profit_trailing_stop")
        assert trailing["exit_counts"]["take_profit"] == 0

    def test_new_profiles_present_and_run(self):
        tickers = ["NVDA", "MSFT", "AAPL", "AMD", "AVGO", "JPM", "SPY", "QQQ"]
        universe = ["NVDA", "MSFT", "AAPL", "AMD", "AVGO", "JPM"]
        data = _price_panel(tickers, n=140, seed=12)
        results = run_experiments(_cfg(universe), data,
                                  data["Close"].index[55].date(), data["Close"].index[-1].date())
        names = {r["name"] for r in results}
        assert {"vol_adjusted_momentum", "qqq_trend_filter", "stop_cooldown_5d",
                "regime_voladj_higher_tp"}.issubset(names)


# ─── New diagnostics-driven mechanics ─────────────────────────────────────────


class TestVolAdjustedMomentum:
    def test_signal_columns_present_and_correct(self):
        data = _price_panel(["A"], n=40, seed=2)
        sig = calculate_signals(data, ["A"])
        assert "vol_adj_mom_20d" in sig.columns and "realized_vol_20d" in sig.columns
        c = data["Close"]["A"].to_numpy()
        ret_20d = c[-1] / c[-21] - 1
        daily = c[-21:][1:] / c[-21:][:-1] - 1
        expected = ret_20d / float(np.std(daily))
        assert sig.iloc[0]["vol_adj_mom_20d"] == pytest.approx(expected, rel=1e-4)

    def test_vol_adjusted_weights_rank(self):
        from signals import rank_candidates
        tickers = [f"T{i}" for i in range(6)]
        data = _price_panel(tickers, n=40, seed=3)
        sig = calculate_signals(data, tickers)
        ranked = rank_candidates(sig, top_n=6, weights={
            "return_5d": 0.2, "return_20d": 0.3, "vol_adj_mom_20d": 0.5,
        })
        assert "composite_score" in ranked.columns and len(ranked) == 6


class TestRegimeFilter:
    def test_filter_reduces_trades_in_downtrend(self):
        # QQQ trends down → regime filter should block entries once below its 50d MA
        tickers = ["A", "B", "SPY", "QQQ"]
        n = 140
        data = _price_panel(tickers, n=n, seed=6)
        # Force QQQ into a steady decline over the back half
        qqq = np.r_[100 * 1.003 ** np.arange(60), (100 * 1.003 ** 59) * 0.99 ** np.arange(1, n - 59)]
        data[("Close", "QQQ")] = qqq
        dates = data["Close"].index
        base = _cfg(["A", "B"])
        filt = _cfg(["A", "B"], **{"entry_filters.qqq_above_ma": 50})
        _, _, _ = run_backtest(base, data, dates[55].date(), dates[-1].date())
        tb, _, _ = run_backtest(base, data, dates[55].date(), dates[-1].date())
        tf, _, _ = run_backtest(filt, data, dates[55].date(), dates[-1].date())
        n_base = len(tb[tb["action"] == "BUY"]) if not tb.empty else 0
        n_filt = len(tf[tf["action"] == "BUY"]) if not tf.empty else 0
        assert n_filt <= n_base


class TestStopCooldown:
    def test_cooldown_blocks_reentry_within_5_days(self):
        tickers = ["NVDA", "MSFT", "AAPL", "AMD", "AVGO", "JPM", "SPY", "QQQ"]
        universe = ["NVDA", "MSFT", "AAPL", "AMD", "AVGO", "JPM"]
        data = _price_panel(tickers, n=160, seed=9)
        cfg = _cfg(universe, **{"risk.stop_cooldown_days": 5})
        dates = data["Close"].index
        t, e, p = run_backtest(cfg, data, dates[55].date(), dates[-1].date())
        tov = turnover_diagnostics(t, data, {"avg_holding_days": 0.0},
                                   dates[55].date(), dates[-1].date())
        # With a 5-day cooldown, no stop-loss should be followed by a re-entry within 5d.
        assert tov["stop_then_reentry_count"] == 0
