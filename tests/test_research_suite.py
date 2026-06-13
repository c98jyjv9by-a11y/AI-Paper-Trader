"""
test_research_suite.py — Consolidated-summary rendering and verdict logic.

The full end-to-end suite is a heavy, network-bound orchestration (validated
manually); here we unit-test the summary renderer with synthetic stage dicts so
the verdict logic and table assembly are covered fast and offline.
"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import research_suite as rs


def _stages(survivor=False):
    return {
        "backtest": {"total_return": 0.18, "irr": 0.09, "ew_return": 0.53, "spy": 0.58, "qqq": 0.18,
                     "max_dd": -0.03, "spread_20d": -0.0023, "beat_ew": False},
        "experiments": {"n": 12, "best": "wide_trailing", "best_ret": 0.26, "ew_return": 0.53, "beat_ew": 0},
        "ticker_experiments": {"n_active": 6, "beat_capital_matched": 0, "spread_20d": -0.0023},
        "calibrate": {"n": 21, "candidates": 9, "beat_hold": 6,
                      "candidate_names": ["NVDA", "AAPL"], "criteria": {}},
        "evaluate_calibrated": {"label": "calibrated", "n": 21, "beat_hold": 9, "beat_exp_matched": 8},
        "evaluate_seed": {"label": "seed", "n": 21, "beat_hold": 7, "beat_exp_matched": 5},
        "active": {"eligible": 0, "n": 21, "oos_return": None, "oos_ew_eligible": None,
                   "oos_capital_matched": None, "beat_ew": False, "beat_cm": False},
        "screen": {"n": 14, "survivors": (["mom_252_21"] if survivor else []),
                   "leaderboard": [("mom_252_21", 0.04 if survivor else 0.005, 3.1 if survivor else 0.4),
                                   ("mom_63", 0.01, 0.8)]},
        "_errors": {},
    }


def test_summary_has_all_sections():
    md = rs.render_summary(_stages(), date(2026, 6, 13), (date(2021, 6, 13), date(2024, 6, 13)),
                           (date(2024, 6, 13), date(2026, 6, 13)))
    for s in ["## Headline verdict", "## Most salient takeaway per stage",
              "## Signal screen — top 5", "## Recommended next step"]:
        assert s in md
    # every stage shows up as a row
    for label in ["Backtest", "Experiments", "Ticker-experiments", "Calibrate",
                  "Evaluate (calibrated)", "Evaluate (seed)", "Active portfolio", "Signal screen"]:
        assert label in md
    assert "$nan" not in md


def test_verdict_no_signal_when_no_survivor():
    md = rs.render_summary(_stages(survivor=False), date(2026, 6, 13),
                           (date(2021, 6, 13), date(2024, 6, 13)), (date(2024, 6, 13), date(2026, 6, 13)))
    assert "No predictive signal found" in md
    assert "different universe" in md.lower()


def test_verdict_candidate_when_survivor():
    md = rs.render_summary(_stages(survivor=True), date(2026, 6, 13),
                           (date(2021, 6, 13), date(2024, 6, 13)), (date(2024, 6, 13), date(2026, 6, 13)))
    assert "candidate signal cleared" in md.lower()
    assert "mom_252_21" in md


def test_errors_section_rendered():
    stages = _stages()
    stages["_errors"] = {"calibrate": "boom"}
    md = rs.render_summary(stages, date(2026, 6, 13), (date(2021, 6, 13), date(2024, 6, 13)),
                           (date(2024, 6, 13), date(2026, 6, 13)))
    assert "Stages that errored" in md and "boom" in md
