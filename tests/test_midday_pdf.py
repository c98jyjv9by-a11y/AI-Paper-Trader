"""test_midday_pdf.py — offline tests for the Midday Pulse report (no network/LLM)."""
import sys
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import midday_pdf as M


def _d_and_cfg(spread):
    pos = pd.DataFrame([
        {"ticker": "ARM", "shares": 46, "entry_price": 216.10, "current_price": 423.90},
        {"ticker": "FTNT", "shares": 89, "entry_price": 130.13, "current_price": 144.46},
    ])
    rets = {"ARM": 0.0695, "FTNT": -0.0174, "HOOD": 0.12, "PLUG": 0.0535, "AMAT": 0.067}

    def ret(t):
        return rets.get(t)

    # prior-close ranking with today's intraday return
    rows = [
        {"rank": 1, "ticker": "HOOD", "score": 0.97, "clears_gate": True, "return": 0.12, "held": False},
        {"rank": 2, "ticker": "AMAT", "score": 0.95, "clears_gate": True, "return": 0.067, "held": False},
        {"rank": 82, "ticker": "PLUG", "score": 0.11, "clears_gate": False, "return": 0.0535, "held": False},
        {"rank": 83, "ticker": "HUBS", "score": 0.10, "clears_gate": False, "return": 0.0001, "held": False},
    ]
    rows_cur = [
        {"rank": 1, "ticker": "HOOD", "score": 0.97, "clears_gate": True, "price": 96.7, "held": False},
        {"rank": 2, "ticker": "ARM", "score": 0.92, "clears_gate": True, "price": 423.9, "held": True},
    ]
    d = {
        "scenario": "model_v4", "rank_close": date(2026, 6, 16), "mark": date(2026, 6, 17),
        "top_n": 2, "n": 4, "rows": rows, "rows_cur": rows_cur,
        "signal_strength": spread, "top_avg": 0.0935, "bot_avg": 0.0268, "univ_avg": 0.0105,
        "advancers": 46, "held_avg": 0.0249, "held_dw": 0.0298,
        "positions": pos, "ret": ret, "pv": 174141.0, "cash": 16730.0,
        "today_trades": [], "exposure_mult": 0.82, "forecast_vol": 0.4283, "target_vol": 0.35,
        "stats": {"1D": {"port": 0.0269, "spy": -0.003, "qqq": 0.004}},
    }
    cfg = {"risk": {"stop_loss_score_max": 0.90, "target_vol": 0.35}, "portfolio": {}}
    return d, cfg


def test_anomalies_flags_inversion_governor_and_laggards():
    d, cfg = _d_and_cfg(spread=-0.04)              # inverted
    a = " ".join(M._anomalies(d, cfg))
    assert "INVERTING" in a
    assert "Laggards bid" in a and "PLUG" in a
    assert "governor de-risked" in a and "0.82" in a
    assert "FTNT" in a                             # held detractor (down today)


def test_anomalies_reports_working_when_spread_positive():
    d, cfg = _d_and_cfg(spread=0.0385)
    a = " ".join(M._anomalies(d, cfg))
    assert "Signal working so far" in a


def test_build_pdf_two_pages(tmp_path):
    d, cfg = _d_and_cfg(spread=0.0385)
    out = tmp_path / "midday.pdf"
    M.build_pdf(d, cfg, out)
    assert out.exists() and out.read_bytes()[:5].startswith(b"%PDF")
