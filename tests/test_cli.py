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
import main as agent


@pytest.fixture
def captured(monkeypatch):
    calls = {}
    monkeypatch.setattr(backtest, "run", lambda s, e, o=None: calls.update(cmd="backtest", s=s, e=e, o=o))
    monkeypatch.setattr(experiments, "run", lambda s, e, o=None: calls.update(cmd="experiments", s=s, e=e, o=o))
    monkeypatch.setattr(ticker_experiments, "run", lambda s, e: calls.update(cmd="ticker", s=s, e=e))
    monkeypatch.setattr(signal_calibration, "run", lambda s, e: calls.update(cmd="calibrate", s=s, e=e))
    monkeypatch.setattr(signal_calibration, "run_evaluate",
                        lambda s, e, c: calls.update(cmd="evaluate", s=s, e=e, crit=c))
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


def test_evaluate_dispatch_default_criteria(captured):
    cli.main(["evaluate", "--start", "2024-01-01", "--end", "2024-12-31"])
    assert captured["cmd"] == "evaluate"
    assert captured["crit"].name == "ticker_timing_criteria.yaml"   # default seed


def test_evaluate_dispatch_explicit_criteria(captured):
    cli.main(["evaluate", "--start", "2024-01-01", "--end", "2024-12-31",
              "--criteria", "/tmp/my_crit.yaml"])
    assert captured["crit"] == Path("/tmp/my_crit.yaml")


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
            "evaluate", "agent"}.issubset(choices)
