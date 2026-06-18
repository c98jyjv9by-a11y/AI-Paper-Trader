"""test_context_matrix.py — offline tests for the sensitivity-matrix pure functions."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import context_matrix as M


def test_powerset_includes_baseline_and_all():
    combos = M._powerset(["macro", "news"], None)
    assert () in combos                                  # baseline
    assert ("macro",) in combos and ("news",) in combos
    assert ("macro", "news") in combos
    assert len(combos) == 4


def test_powerset_respects_max_combo_size():
    combos = M._powerset(["macro", "news", "social"], 1)
    assert combos == [(), ("macro",), ("news",), ("social",)]


def test_combo_label():
    assert M._combo_label(()) == "none"
    assert M._combo_label(("macro",)) == "macro"
    assert M._combo_label(("macro", "news")) == "macro+news"


def test_render_and_csv(tmp_path):
    res = {
        "scenario": "model_v4", "window": ["2026-01-05", "2026-06-16"], "model": "sonnet",
        "strict_ret": 0.10, "repeats": 1,
        "bench": {"model": 0.10, "SPY": 0.05, "QQQ": 0.06},
        "rows": [
            {"sources": "none", "setting": "discretionary", "return": 0.08, "ret_std": 0.0,
             "vs_strict": -0.02, "maxDD": -0.1, "sharpe": 1.1, "trades": 20,
             "divergences": 5, "significant": False},
            {"sources": "macro", "setting": "discretionary", "return": 0.12, "ret_std": 0.0,
             "vs_strict": 0.02, "maxDD": -0.08, "sharpe": 1.4, "trades": 18,
             "divergences": 6, "significant": False},
        ],
    }
    md = M._render(res)
    assert "sensitivity matrix" in md and "vs strict" in md
    assert "macro" in md and "+2.00%" in md
    csv = tmp_path / "m.csv"
    M._write_csv(csv, res["rows"])
    text = csv.read_text()
    assert "sources,setting,return" in text and "macro" in text
