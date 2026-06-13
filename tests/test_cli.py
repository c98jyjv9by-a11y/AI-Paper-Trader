"""
test_cli.py — Unified runner dispatch. The heavy run() functions are stubbed so
no network/compute happens; we only verify routing and argument handling.
"""
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import cli
import backtest
import experiments
import ticker_experiments
import signal_calibration
import active_experiment
import signal_screen
import research_suite
import scenarios
import main as agent


@pytest.fixture
def captured(monkeypatch):
    calls = {}
    monkeypatch.setattr(backtest, "run", lambda s, e, o=None: calls.update(cmd="backtest", s=s, e=e, o=o))
    monkeypatch.setattr(experiments, "run", lambda s, e, o=None: calls.update(cmd="experiments", s=s, e=e, o=o))
    monkeypatch.setattr(ticker_experiments, "run", lambda s, e: calls.update(cmd="ticker", s=s, e=e))
    monkeypatch.setattr(signal_calibration, "run",
                        lambda s, e, objective="total_return": calls.update(cmd="calibrate", s=s, e=e, objective=objective))
    monkeypatch.setattr(signal_calibration, "run_evaluate",
                        lambda s, e, c: calls.update(cmd="evaluate", s=s, e=e, crit=c))
    monkeypatch.setattr(active_experiment, "run",
                        lambda ts, te, vs, ve: calls.update(cmd="active", ts=ts, te=te, vs=vs, ve=ve))
    monkeypatch.setattr(signal_screen, "run",
                        lambda ts, te, vs, ve: calls.update(cmd="screen", ts=ts, te=te, vs=vs, ve=ve))
    monkeypatch.setattr(research_suite, "run",
                        lambda ts, te, vs, ve: calls.update(cmd="suite", ts=ts, te=te, vs=vs, ve=ve))
    monkeypatch.setattr(scenarios, "run_scenario",
                        lambda name, s, e: calls.update(cmd="scenario", name=name, s=s, e=e))
    monkeypatch.setattr(agent, "main", lambda: calls.update(cmd="agent"))
    return calls


def test_backtest_dispatch(captured):
    cli.main(["backtest", "--start", "2024-01-01", "--end", "2024-12-31"])
    assert captured["cmd"] == "backtest"
    assert captured["s"] == date(2024, 1, 1) and captured["e"] == date(2024, 12, 31)
    assert captured["o"] is None


def test_backtest_output_flag(captured):
    cli.main(["backtest", "--start", "2024-01-01", "--end", "2024-12-31", "--output", "/tmp/x"])
    assert captured["o"] == Path("/tmp/x")


def test_experiments_dispatch(captured):
    cli.main(["experiments", "--start", "2024-01-01", "--end", "2024-12-31"])
    assert captured["cmd"] == "experiments"


def test_ticker_experiments_dispatch(captured):
    cli.main(["ticker-experiments", "--start", "2024-01-01", "--end", "2024-12-31"])
    assert captured["cmd"] == "ticker"


def test_calibrate_dispatch(captured):
    cli.main(["calibrate", "--start", "2024-01-01", "--end", "2024-12-31"])
    assert captured["cmd"] == "calibrate"


def test_calibrate_objective_dispatch(captured):
    cli.main(["calibrate", "--start", "2024-01-01", "--end", "2024-12-31", "--objective", "sharpe"])
    assert captured["cmd"] == "calibrate" and captured["objective"] == "sharpe"


def test_calibrate_default_objective(captured):
    cli.main(["calibrate", "--start", "2024-01-01", "--end", "2024-12-31"])
    assert captured["objective"] == "total_return"


def test_evaluate_dispatch_default_criteria(captured):
    cli.main(["evaluate", "--start", "2024-01-01", "--end", "2024-12-31"])
    assert captured["cmd"] == "evaluate"
    assert captured["crit"].name == "ticker_timing_criteria.yaml"   # default seed


def test_evaluate_dispatch_explicit_criteria(captured):
    cli.main(["evaluate", "--start", "2024-01-01", "--end", "2024-12-31",
              "--criteria", "/tmp/my_crit.yaml"])
    assert captured["crit"] == Path("/tmp/my_crit.yaml")


def test_active_dispatch(captured):
    cli.main(["active", "--train-start", "2021-01-01", "--train-end", "2023-12-31",
              "--test-start", "2024-01-01", "--test-end", "2025-12-31"])
    assert captured["cmd"] == "active"
    assert captured["ts"] == date(2021, 1, 1) and captured["ve"] == date(2025, 12, 31)


def test_active_bad_window_exits(captured):
    with pytest.raises(SystemExit):
        cli.main(["active", "--train-start", "2023-12-31", "--train-end", "2021-01-01",
                  "--test-start", "2024-01-01", "--test-end", "2025-12-31"])


def test_screen_dispatch(captured):
    cli.main(["screen", "--train-start", "2021-01-01", "--train-end", "2023-12-31",
              "--test-start", "2024-01-01", "--test-end", "2025-12-31"])
    assert captured["cmd"] == "screen"
    assert captured["ts"] == date(2021, 1, 1) and captured["ve"] == date(2025, 12, 31)


def test_suite_dispatch(captured):
    cli.main(["suite", "--train-start", "2021-01-01", "--train-end", "2023-12-31",
              "--test-start", "2024-01-01", "--test-end", "2025-12-31"])
    assert captured["cmd"] == "suite"
    assert captured["ts"] == date(2021, 1, 1) and captured["ve"] == date(2025, 12, 31)


def test_scenario_dispatch(captured):
    cli.main(["scenario", "davids_model", "--start", "2024-01-01", "--end", "2025-12-31"])
    assert captured["cmd"] == "scenario"
    assert captured["name"] == "davids_model"
    assert captured["s"] == date(2024, 1, 1) and captured["e"] == date(2025, 12, 31)


def test_scenario_list_does_not_run(captured):
    cli.main(["scenario", "--list"])
    assert "cmd" not in captured            # --list just prints; no scenario executed


def test_agent_dispatch(captured):
    cli.main(["agent"])
    assert captured["cmd"] == "agent"


def test_end_before_start_exits(captured):
    with pytest.raises(SystemExit):
        cli.main(["backtest", "--start", "2024-12-31", "--end", "2024-01-01"])


def test_bad_date_exits(captured):
    with pytest.raises(SystemExit):
        cli.main(["calibrate", "--start", "not-a-date", "--end", "2024-12-31"])


def test_unknown_command_exits(captured):
    with pytest.raises(SystemExit):
        cli.main(["frobnicate"])


def test_all_subcommands_registered():
    parser = cli.build_parser()
    # subparsers action holds the registered command names
    choices = set()
    for action in parser._actions:
        if hasattr(action, "choices") and action.choices:
            choices.update(action.choices.keys())
    assert {"backtest", "experiments", "ticker-experiments", "calibrate",
            "evaluate", "active", "screen", "suite", "scenario", "agent"}.issubset(choices)
