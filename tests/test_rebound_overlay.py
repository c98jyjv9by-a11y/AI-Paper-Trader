"""Tests for the model_v4 rebound overlay (down-shock + signal-negative + vol-up -> 1-day TQQQ)."""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import rebound_overlay as ro


def _df():
    idx = pd.date_range("2020-01-01", periods=6, freq="D")
    return pd.DataFrame({
        "book_fwd_1d":    [0.01, -0.02, 0.00, 0.005, -0.01, 0.00],
        "book_trl_1d":    [0.0] * 6,
        "qqq_trl_1d":     [-0.03, -0.01, -0.03, -0.03, 0.00, -0.03],   # row1 too shallow, row4 up
        "spread_trl_1d":  [-0.01, -0.01, 0.005, -0.01, -0.01, -0.01],  # row2 signal not negative
        "spy_vol_trl_5d": [0.02] * 6,
        "qqq_vol_trl_5d": [0.02] * 6,                                 # default vol_factor is QQQ vol
        "top10_trl_1d":   [-0.04, 0.0, 0.0, -0.02, 0.0, 0.0],
        "bottom10_trl_1d":[0.01, 0.0, 0.0, 0.01, 0.0, 0.0],
        "tqqq_fwd_1d":    [0.05, -0.05, 0.0, 0.05, 0.0, 0.05],
    }, index=idx)


def test_combo_gate_fires_only_when_all_three_clear(monkeypatch):
    df = _df()
    monkeypatch.setattr(ro, "_zscore", lambda s, lb: pd.Series([1.0, 1.0, 1.0, 1.0, 1.0, 0.0], index=df.index))
    combo, crash, w = ro._gates(df, ro.ReboundConfig())
    assert combo.iloc[0]            # qqq<=-2.5%, spread<0, volz>=0.5
    assert not combo.iloc[1]        # qqq -1% too shallow
    assert not combo.iloc[2]        # spread +0.5% not negative
    assert not combo.iloc[3] is None and combo.iloc[3]  # qqq-3%, spread<0, volz ok -> fires
    assert not combo.iloc[5]        # volz 0 < 0.5
    assert abs(w.iloc[0] - ro.ReboundConfig().weight) < 1e-9


def test_crash_tier_escalates_only_when_tiered(monkeypatch):
    df = _df()
    monkeypatch.setattr(ro, "_zscore", lambda s, lb: pd.Series([1.0] * 6, index=df.index))
    flat = ro._gates(df, ro.ReboundConfig(tiered=False))[2]
    tier = ro._gates(df, ro.ReboundConfig(tiered=True))[2]
    assert abs(flat.iloc[0] - 0.50) < 1e-9                    # combo size, no escalation
    assert abs(tier.iloc[0] - 0.60) < 1e-9                    # row0 is a crash (top10<=-3% & bottom10>0) -> cap


def test_overlay_math(monkeypatch):
    df = _df()
    monkeypatch.setattr(ro, "_zscore", lambda s, lb: pd.Series([1.0] * 6, index=df.index))
    ov = ro.build_overlay(df, ro.ReboundConfig(cost_bps=0.0))
    assert abs(ov["sleeve_pnl"].iloc[0] - 0.5 * 0.05) < 1e-9          # weight * tqqq_fwd
    assert abs(ov["overlaid_ret"].iloc[0] - (0.01 + 0.025)) < 1e-9    # book + sleeve
    assert ov["sleeve_pnl"].iloc[2] == 0.0                            # no fire -> no sleeve


def test_recommend_fires_and_sizes():
    r = ro.recommend(market_value=100_000, down_override=-0.03, signal_override=-0.01, volz_override=0.9)
    assert r["fires"] and r["tier"] == "COMBO"
    assert abs(r["rebound_dollars"] - 50_000) < 1.0                   # weight 0.5 * 100k


def test_recommend_no_fire_on_shallow_drop():
    r = ro.recommend(market_value=100_000, down_override=-0.01, signal_override=-0.01, volz_override=0.9)
    assert not r["fires"] and r["rebound_dollars"] == 0.0
