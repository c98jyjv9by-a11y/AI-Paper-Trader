"""
test_ticker_experiments.py — Grouped per-ticker overrides, MFE/MAE/giveback
diagnostics, capital-matched benchmark, and the ticker-override experiment runner.
Synthetic data; no network.
"""
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from backtest import _build_ticker_overrides, _build_ticker_weights, _evaluate_backtest_exits, run_backtest
from diagnostics import group_to_tickers, ticker_level_diagnostics
from signals import calculate_signals, rank_candidates
import ticker_experiments as te


def _price_panel(tickers, n=120, seed=1):
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    rng = np.random.default_rng(seed)
    cl = pd.DataFrame({t: 100 * np.cumprod(1 + rng.normal(0.0012, 0.014, n)) for t in tickers}, index=dates)
    vol = pd.DataFrame({t: np.abs(rng.normal(1e6, 1e5, n)) for t in tickers}, index=dates)
    cl.columns = pd.MultiIndex.from_product([["Close"], cl.columns])
    vol.columns = pd.MultiIndex.from_product([["Volume"], vol.columns])
    return pd.concat([cl, vol], axis=1)


# ─── Override resolution ──────────────────────────────────────────────────────


class TestOverrideResolution:
    def test_nested_group_fields_resolve_per_ticker(self):
        cfg = {"ticker_groups": {
            "semis": {"tickers": ["NVDA", "AMD"], "stop_loss": 0.10, "take_profit": None, "trailing_stop": 0.15},
        }}
        ov = _build_ticker_overrides(cfg)
        assert ov["NVDA"]["stop_loss"] == 0.10
        assert ov["NVDA"]["take_profit"] is None        # explicit null preserved
        assert ov["AMD"]["trailing_stop"] == 0.15
        assert "max_holding_days" not in ov["NVDA"]      # unspecified field falls back

    def test_flat_group_form_yields_no_overrides(self):
        cfg = {"ticker_groups": {"semis": ["NVDA", "AMD"]}}
        assert _build_ticker_overrides(cfg) == {}

    def test_group_to_tickers_both_forms(self):
        assert group_to_tickers({"g": ["A", "B"]}) == {"g": ["A", "B"]}
        assert group_to_tickers({"g": {"tickers": ["A"], "stop_loss": 0.1}}) == {"g": ["A"]}


class TestPerGroupSignalWeights:
    def test_build_ticker_weights(self):
        cfg = {"ticker_groups": {
            "semis": {"tickers": ["NVDA", "AMD"], "signal_weights": {"return_20d": 1.0}},
            "fin": {"tickers": ["JPM"], "stop_loss": 0.1},   # no signal_weights → excluded
        }}
        tw = _build_ticker_weights(cfg)
        assert tw["NVDA"] == {"return_20d": 1.0}
        assert "JPM" not in tw

    def test_per_group_weights_change_ranking(self):
        # Two tickers: one strong on 5d, one strong on 20d. Per-group weights should
        # flip which is ranked #1 vs a uniform weighting.
        sig = pd.DataFrame([
            {"ticker": "FAST", "price": 100.0, "return_1d": 0.0, "return_5d": 0.10,
             "return_20d": 0.01, "vol_ratio": 1.0, "vol_adj_mom_20d": 0.1},
            {"ticker": "SLOW", "price": 100.0, "return_1d": 0.0, "return_5d": 0.01,
             "return_20d": 0.10, "vol_ratio": 1.0, "vol_adj_mom_20d": 0.9},
        ])
        # Give FAST a 5d-heavy weight, SLOW a 20d-heavy weight → both score high → tie-ish,
        # but compared to a 20d-only uniform ranking (SLOW wins), per-group lifts FAST.
        uniform = rank_candidates(sig, top_n=2, weights={"return_20d": 1.0})
        per_group = rank_candidates(sig, top_n=2, weights={"return_20d": 1.0},
                                    ticker_weights={"FAST": {"return_5d": 1.0}})
        assert uniform.iloc[0]["ticker"] == "SLOW"          # 20d-only → SLOW on top
        # FAST now scored on its own 5d strength (rank 1.0) → ties/beats SLOW
        assert per_group.iloc[0]["ticker"] == "FAST"


class TestPerTickerExits:
    def _pos(self, ticker, current, highest):
        return pd.DataFrame([{
            "ticker": ticker, "shares": 10, "entry_price": 100.0,
            "entry_date": date(2024, 1, 1), "current_price": current,
            "highest_price": highest, "lowest_price": min(current, 100.0),
        }])

    def test_override_disables_take_profit_for_one_ticker(self):
        overrides = {"NVDA": {"take_profit": None, "trailing_stop": 0.15}}
        # +15% gain: global take_profit 0.10 would normally fire, but NVDA's is None
        exits, remaining = _evaluate_backtest_exits(
            self._pos("NVDA", 115.0, 120.0), date(2024, 1, 10),
            stop_loss=0.075, take_profit=0.10, max_holding_days=90, slippage=0.0,
            ticker_overrides=overrides,
        )
        # No take_profit; trailing 0.15 → 115 vs 120*0.85=102 → not triggered → still held
        assert len(exits) == 0
        assert len(remaining) == 1

    def test_override_take_profit_threshold_applies(self):
        overrides = {"ORCL": {"take_profit": 0.15}}
        # +12%: below ORCL's 0.15 TP → no exit (global 0.10 would have fired)
        exits, _ = _evaluate_backtest_exits(
            self._pos("ORCL", 112.0, 112.0), date(2024, 1, 10),
            stop_loss=0.075, take_profit=0.10, max_holding_days=90, slippage=0.0,
            ticker_overrides=overrides,
        )
        assert len(exits) == 0


# ─── MFE / MAE / giveback ─────────────────────────────────────────────────────


class TestTickerLevelDiagnostics:
    def test_mfe_mae_giveback(self):
        data = _price_panel(["AAA"], n=30)
        d = [ts.date().isoformat() for ts in data["Close"].index]
        trades = pd.DataFrame([
            {"action": "BUY", "ticker": "AAA", "date": d[0], "reason": "m", "realized_pnl": None,
             "price": 100.0, "shares": 10, "holding_days": 0},
            {"action": "SELL", "ticker": "AAA", "date": d[5], "reason": "trailing_stop", "realized_pnl": 50.0,
             "price": 105.0, "shares": 10, "holding_days": 3.0,
             "entry_price": 100.0, "highest_price": 112.0, "lowest_price": 97.0},
        ])
        rows = ticker_level_diagnostics(trades, pd.DataFrame(), data)
        d0 = rows[0]
        assert d0["ticker"] == "AAA"
        assert d0["avg_mfe"] == pytest.approx(0.12)       # 112/100 - 1
        assert d0["avg_mae"] == pytest.approx(-0.03)      # 97/100 - 1
        # giveback = MFE - realized = 0.12 - (105/100-1)=0.05 → 0.07
        assert d0["avg_giveback"] == pytest.approx(0.07)
        assert d0["exits_trailing_stop"] == 1


# ─── Capital-matched benchmark ────────────────────────────────────────────────


class TestCapitalMatched:
    def test_scaled_return_and_drawdown(self):
        n = 40
        dates = pd.date_range("2024-01-01", periods=n, freq="B")
        # EW basket rises 20% smoothly
        ew_cum = np.linspace(0, 0.20, n)
        eq = pd.DataFrame({
            "date": [d.date().isoformat() for d in dates],
            "total_portfolio_value": np.full(n, 100000.0),
            "open_positions_value": np.full(n, 50000.0),
            "cash": np.full(n, 50000.0),
            "daily_return": np.r_[np.nan, np.zeros(n - 1)],
            "equal_weight_cumulative_return": ew_cum,
        })
        # At 50% exposure, final return = 0.5 * 0.20 = 0.10
        cm = te._capital_matched(eq, 0.5)
        assert cm["total_return"] == pytest.approx(0.10, rel=1e-9)
        # monotonic rise → no drawdown
        assert cm["max_drawdown"] == pytest.approx(0.0, abs=1e-9)

    def test_full_exposure_equals_ew(self):
        n = 20
        ew_cum = np.linspace(0, 0.15, n)
        eq = pd.DataFrame({"equal_weight_cumulative_return": ew_cum,
                           "total_portfolio_value": np.full(n, 1.0)})
        assert te._capital_matched(eq, 1.0)["total_return"] == pytest.approx(0.15, rel=1e-9)


# ─── End-to-end ───────────────────────────────────────────────────────────────


class TestRunnerEndToEnd:
    def _cfg(self, universe):
        return {
            "tickers": universe,
            "ticker_groups": {
                "semiconductors": ["NVDA", "AVGO", "AMD"],
                "mega_cap_growth": ["MSFT", "AAPL", "GOOGL"],
                "financial_crypto_beta": ["JPM", "BAC"],
            },
            "portfolio": {"starting_value": 100000.0, "max_position_pct": "auto",
                          "max_total_exposure": 0.75, "max_new_trades_per_day": 2},
            "risk": {"stop_loss": 0.075, "take_profit": 0.10, "max_holding_days": 30, "slippage": 0.001},
            "signals": {"top_candidates": 10, "min_composite_score": None},
        }

    def test_profiles_run_and_render(self):
        universe = ["NVDA", "AVGO", "AMD", "MSFT", "AAPL", "GOOGL", "JPM", "BAC"]
        data = _price_panel(universe + ["SPY", "QQQ"], n=160, seed=7)
        dates = data["Close"].index
        results = te.run_ticker_experiments(self._cfg(universe), data, dates[55].date(), dates[-1].date())
        assert len(results) == len(te.PROFILES)
        names = {r["name"] for r in results}
        assert {"baseline", "trailing_stop_baseline", "grouped_ticker_overrides_v1",
                "grouped_ticker_overrides_conservative", "grouped_ticker_overrides_aggressive",
                "grouped_signal_weights_only", "grouped_signals_plus_exits"}.issubset(names)
        md = te.render_report(results, date(2026, 6, 12), dates[55].date(), dates[-1].date(), data)
        for section in ["## Strategy vs Buy-and-Hold Test", "## Returns & Risk",
                        "## Signal Effectiveness", "## P&L Attribution",
                        "## Ticker-Level Behaviour", "## Interpretation"]:
            assert section in md
        assert "capital-matched" in md.lower() and "IN-SAMPLE" in md
        csv = te.experiments_csv(results)
        assert len(csv) == len(te.PROFILES)
        for col in ["capital_matched_avg_return", "spread_20d", "calmar", "semis_pnl_share"]:
            assert col in csv.columns

    def test_grouped_profile_changes_exit_mix(self):
        # grouped v1 sets take_profit=None for semis/mega → far fewer take-profit exits than baseline
        universe = ["NVDA", "AVGO", "AMD", "MSFT", "AAPL", "GOOGL", "JPM", "BAC"]
        data = _price_panel(universe + ["SPY", "QQQ"], n=160, seed=13)
        dates = data["Close"].index
        results = te.run_ticker_experiments(self._cfg(universe), data, dates[55].date(), dates[-1].date())
        base = next(r for r in results if r["name"] == "baseline")
        v1 = next(r for r in results if r["name"] == "grouped_ticker_overrides_v1")
        # baseline uses global TP; v1 disables TP for most tickers → its avg hold should be longer
        assert (v1["metrics"].get("avg_holding_days") or 0) >= (base["metrics"].get("avg_holding_days") or 0)
