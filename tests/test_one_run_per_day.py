"""Once-per-ET-day rebalance guard for cadence books (score_rebalance / zscore_reversal / options)."""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import broker_sync as bs


def test_is_cadence_account():
    for k in ("score_rebalance", "zscore_reversal", "options"):
        assert bs._is_cadence_account({"target_mode": {"kind": k}})
    assert not bs._is_cadence_account({"target_mode": {"kind": "model_v4"}})
    assert not bs._is_cadence_account({"target_mode": {"kind": "score_gate_rampup"}})
    assert not bs._is_cadence_account({})


def test_marker_roundtrip(monkeypatch, tmp_path):
    monkeypatch.setattr(bs, "_acct_dir", lambda name: tmp_path)
    assert bs._already_rebalanced_today("x", "2026-06-29") is False
    bs._mark_rebalanced("x", "2026-06-29")
    assert bs._already_rebalanced_today("x", "2026-06-29") is True
    assert bs._already_rebalanced_today("x", "2026-06-30") is False   # different day


class _Clk:
    def clock(self): return {"timestamp": "2026-06-29T15:45:00Z"}
    def positions(self): raise RuntimeError("proceeded past guard")   # tripwire: ran past the guard


def test_second_submit_same_day_blocked(monkeypatch, tmp_path):
    monkeypatch.setattr(bs, "_acct_dir", lambda name: tmp_path)
    monkeypatch.setattr(bs, "load_manifest", lambda name: {"target_mode": {"kind": "zscore_reversal"}})
    bs._mark_rebalanced("zz", "2026-06-29")                            # already rebalanced today
    r = bs.submit_session("zz", cli=_Clk(), submit=True)
    assert r.get("blocked") and "one run per day" in r["reason"] and r["n_orders"] == 0


def test_force_env_bypasses_guard(monkeypatch, tmp_path):
    monkeypatch.setattr(bs, "_acct_dir", lambda name: tmp_path)
    monkeypatch.setattr(bs, "load_manifest", lambda name: {"target_mode": {"kind": "zscore_reversal"}})
    monkeypatch.setenv("BROKER_REBALANCE_FORCE_TODAY", "1")
    bs._mark_rebalanced("zz", "2026-06-29")
    with pytest.raises(RuntimeError, match="proceeded past guard"):     # force -> bypasses, proceeds
        bs.submit_session("zz", cli=_Clk(), submit=True)


def test_dry_run_never_blocked(monkeypatch, tmp_path):
    monkeypatch.setattr(bs, "_acct_dir", lambda name: tmp_path)
    monkeypatch.setattr(bs, "load_manifest", lambda name: {"target_mode": {"kind": "zscore_reversal"}})
    bs._mark_rebalanced("zz", "2026-06-29")
    with pytest.raises(RuntimeError, match="proceeded past guard"):     # submit=False -> guard skipped
        bs.submit_session("zz", cli=_Clk(), submit=False)
