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
        # build_config + the backtest override resolver should yield per-ticker exits
        from backtest import _build_ticker_overrides
        base = {"tickers": ["MSFT", "ORCL", "CRWD"], "portfolio": {}, "risk": {}, "signals": {}}
        cfg = sc.build_config(base, sc.load_scenario("davids_model"))
        ov = _build_ticker_overrides(cfg)
        assert ov["MSFT"]["trailing_stop"] == 0.10 and ov["MSFT"]["take_profit"] is None
        assert ov["ORCL"]["take_profit"] == 0.15 and ov["ORCL"]["max_holding_days"] == 60
        assert ov["CRWD"]["trailing_stop"] == 0.10
