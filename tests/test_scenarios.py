"""
test_scenarios.py — Named-scenario loading and config overlay. No network.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import scenarios as sc


def _base():
    return {
        "tickers": ["A", "B", "C", "D"],
        "portfolio": {"starting_value": 100000.0, "max_position_pct": 0.05,
                      "max_total_exposure": 0.75, "max_new_trades_per_day": 2},
        "risk": {"stop_loss": 0.05, "take_profit": 0.10, "max_holding_days": 10, "slippage": 0.001},
        "signals": {"top_candidates": 10, "min_composite_score": 0.7, "weights": {"a": 1.0}},
        "ticker_groups": {"old_group": ["A", "B"]},
        "data": {"period": "90d", "interval": "1d"},
    }


class TestMerge:
    def test_tickers_replaced_wholesale(self):
        cfg = sc.build_config(_base(), {"tickers": ["X", "Y"]})
        assert cfg["tickers"] == ["X", "Y"]

    def test_ticker_groups_replaced_not_merged(self):
        cfg = sc.build_config(_base(), {"ticker_groups": {"new": {"tickers": ["X"], "stop_loss": 0.1}}})
        assert set(cfg["ticker_groups"]) == {"new"}        # old_group dropped, not merged

    def test_nested_dicts_deep_merge(self):
        cfg = sc.build_config(_base(), {"portfolio": {"max_total_exposure": 0.90}})
        assert cfg["portfolio"]["max_total_exposure"] == 0.90      # overridden
        assert cfg["portfolio"]["starting_value"] == 100000.0      # base key kept

    def test_metadata_keys_ignored(self):
        cfg = sc.build_config(_base(), {"name": "x", "description": "y", "signals": {"min_composite_score": None}})
        assert "name" not in cfg and "description" not in cfg
        assert cfg["signals"]["min_composite_score"] is None
        assert cfg["signals"]["weights"] == {"a": 1.0}             # untouched base key

    def test_base_not_mutated(self):
        base = _base()
        sc.build_config(base, {"tickers": ["Z"], "portfolio": {"max_total_exposure": 0.9}})
        assert base["tickers"] == ["A", "B", "C", "D"]
        assert base["portfolio"]["max_total_exposure"] == 0.75


class TestSensitivityTasks:
    """The scenario sensitivity task builder (pure — no backtests run here)."""

    def _cfg(self):
        return {
            "tickers": ["A", "B"],
            "portfolio": {"starting_value": 100000.0, "max_position_pct": "auto",
                          "max_total_exposure": 0.90, "max_new_trades_per_day": 3},
            "risk": {"stop_loss": 0.075, "take_profit": None, "max_holding_days": 30,
                     "slippage": 0.001, "reentry_recover_pct": 0.05},
            "signals": {"min_composite_score": None, "weights": {"return_5d": 1.0}},
            "ticker_groups": {
                "a": {"tickers": ["A"], "stop_loss": 0.075, "take_profit": None,
                      "trailing_stop": 0.10, "max_holding_days": 30},
                "b": {"tickers": ["B"], "stop_loss": 0.10, "take_profit": 0.20,
                      "trailing_stop": None, "max_holding_days": 60},
            },
        }

    def test_runwide_and_ticker_groups_present(self):
        tasks, groups, marks, has_ticker = sc._scenario_sensitivity_tasks(self._cfg())
        keys = {g[0] for g in groups}
        assert {"max_total_exposure", "max_position_pct", "max_new_trades_per_day",
                "min_composite_score", "slippage", "reentry_recover_pct", "signal_weights"}.issubset(keys)
        assert {"tk_stop_loss", "tk_take_profit", "tk_trailing_stop", "tk_max_holding_days"}.issubset(keys)
        assert has_ticker is True
        assert len(tasks) > 20

    def test_baseline_included_in_runwide_sweep(self):
        tasks, groups, marks, _ = sc._scenario_sensitivity_tasks(self._cfg())
        # baseline exposure (90%) must appear among the swept values for that param
        exp_vals = [v for (param, v, _c) in tasks if param == "max_total_exposure"]
        assert marks["max_total_exposure"] == "90%"
        assert "90%" in exp_vals

    def test_ticker_variant_overwrites_every_group(self):
        tasks, _g, _m, _h = sc._scenario_sensitivity_tasks(self._cfg())
        # a tk_stop_loss=15% variant sets BOTH groups' stop_loss to 0.15
        variant = next(c for (param, v, c) in tasks if param == "tk_stop_loss" and v == "15.0%")
        stops = {spec["stop_loss"] for spec in variant["ticker_groups"].values()}
        assert stops == {0.15}

    def test_max_position_size_swept_by_multiples(self):
        # baseline resolves to max_total_exposure / n = 0.90 / 2 = 0.45; sweep = ×0.5..×3.0
        tasks, _g, marks, _h = sc._scenario_sensitivity_tasks(self._cfg())
        vals = sorted(round(c["portfolio"]["max_position_pct"], 6)
                      for (param, _v, c) in tasks if param == "max_position_pct")
        assert vals == [0.225, 0.45, 0.675, 0.90, 1.35]      # 0.5,1.0,1.5,2.0,3.0 × 0.45
        assert marks["max_position_pct"] == "45.00%"

    def test_no_ticker_groups_means_no_ticker_sweeps(self):
        cfg = self._cfg()
        cfg["ticker_groups"] = {}
        tasks, groups, _m, has_ticker = sc._scenario_sensitivity_tasks(cfg)
        assert has_ticker is False
        assert not any(g[0].startswith("tk_") for g in groups)

    def test_source_cfg_not_mutated(self):
        cfg = self._cfg()
        sc._scenario_sensitivity_tasks(cfg)
        assert cfg["portfolio"]["max_total_exposure"] == 0.90       # untouched
        assert cfg["ticker_groups"]["a"]["stop_loss"] == 0.075


class TestLoading:
    def test_davids_model_loads_and_is_valid(self):
        assert "davids_model" in sc.list_scenarios()
        scen = sc.load_scenario("davids_model")
        assert scen["name"] == "davids_model"
        assert scen["tickers"] == ["MSFT", "ORCL", "CRWD"]
        # every group lists tickers drawn from the scenario universe
        uni = set(scen["tickers"])
        for spec in scen["ticker_groups"].values():
            assert set(spec["tickers"]).issubset(uni)

    def test_unknown_scenario_raises(self):
        with pytest.raises(FileNotFoundError):
            sc.load_scenario("does_not_exist")

    def test_built_config_applies_per_ticker_overrides(self):
        # build_config + the backtest override resolver should yield per-ticker exits.
        # Assert the resolution MECHANISM against whatever the YAML declares (the values
        # are user-tunable), not hardcoded numbers.
        from backtest import _build_ticker_overrides
        base = {"tickers": ["MSFT", "ORCL", "CRWD"], "portfolio": {}, "risk": {}, "signals": {}}
        scen = sc.load_scenario("davids_model")
        cfg = sc.build_config(base, scen)
        ov = _build_ticker_overrides(cfg)
        assert set(ov) == {"MSFT", "ORCL", "CRWD"}
        # Each ticker resolves to exactly the exit fields its own group declares.
        for spec in scen["ticker_groups"].values():
            for tk in spec["tickers"]:
                assert "stop_loss" in ov[tk]                  # stop is always set per name
                if "trailing_stop" in spec:
                    assert ov[tk]["trailing_stop"] == spec["trailing_stop"]
                if "take_profit" in spec:
                    assert ov[tk]["take_profit"] == spec["take_profit"]
