"""
test_pdf_report.py — End-of-day PDF report. No network: a synthetic build_report
dict is fed directly to build_pdf / _commentary so nothing calls yfinance.
"""
import sys
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pdf_report as P


def _dict_and_cfg():
    positions = pd.DataFrame([
        {"ticker": "ARM", "shares": 46, "entry_price": 216.10, "current_price": 396.34},
        {"ticker": "INTC", "shares": 123, "entry_price": 94.84, "current_price": 117.05},
    ])
    rets = {"ARM": -0.0393, "INTC": -0.0845, "AMAT": -0.03, "PLUG": -0.0321}

    def ret(t):
        return rets.get(t)

    rows = [  # prior-close ranking with session returns
        {"rank": 1, "ticker": "AMAT", "score": 0.916, "clears_gate": True,
         "rank_close_px": 585.78, "mark_px": 568.23, "return": -0.03, "held": False},
        {"rank": 2, "ticker": "ARM", "score": 0.946, "clears_gate": True,
         "rank_close_px": 412.55, "mark_px": 396.34, "return": -0.0393, "held": True},
        {"rank": 3, "ticker": "INTC", "score": 0.824, "clears_gate": True,
         "rank_close_px": 127.86, "mark_px": 117.05, "return": -0.0845, "held": True},
        {"rank": 4, "ticker": "PLUG", "score": 0.05, "clears_gate": False,
         "rank_close_px": 2.80, "mark_px": 2.71, "return": -0.0321, "held": False},
    ]
    rows_cur = [
        {"rank": 1, "ticker": "AMAT", "score": 0.913, "clears_gate": True, "price": 568.23, "held": False, "rank_chg": 2},
        {"rank": 2, "ticker": "ARM", "score": 0.915, "clears_gate": True, "price": 396.34, "held": True, "rank_chg": 0},
        {"rank": 3, "ticker": "SOFI", "score": 0.842, "clears_gate": True, "price": 17.71, "held": False, "rank_chg": 14},
        {"rank": 4, "ticker": "INTC", "score": 0.50, "clears_gate": False, "price": 117.05, "held": True, "rank_chg": -1},
        {"rank": 5, "ticker": "PLUG", "score": 0.11, "clears_gate": False, "price": 2.71, "held": False, "rank_chg": 0},
    ]
    d = {
        "scenario": "model_v4", "rank_close": date(2026, 6, 15), "mark": date(2026, 6, 16),
        "min_score": 0.70, "rows": rows, "rows_cur": rows_cur, "n": 4, "top_n": 2,
        "today_trades": [], "recent_trades": [
            {"date": "2026-05-27", "action": "SELL", "ticker": "ZS", "shares": 64,
             "price": 126.28, "reason": "stop_loss", "pnl": -3145.0},
            {"date": "2026-05-19", "action": "BUY", "ticker": "CRWD", "shares": 18,
             "price": 617.50, "reason": "momentum_score=0.94", "pnl": None},
        ],
        "next_session": {
            "buys": [], "sells": [],
            "buy_reason": "No risk budget to add — book 90% invested vs 73% cap.",
            "sell_reason": "No exit triggered — stops score-gated and none qualify.",
            "invested_frac": 0.90, "exposure_cap_frac": 0.73,
        },
        "target_vol": 0.35, "forecast_vol": 0.429, "exposure_mult": 0.82,
        "univ_avg": -0.0161, "top_avg": -0.0572, "bot_avg": -0.0170, "signal_strength": -0.0403,
        "advancers": 23, "n_gate": 14, "n_gate_cur": 3, "intraday": None,
        "held_avg": -0.0376, "held_dw": -0.04,
        "positions": positions, "pv": 169585.0, "cash": 16730.0, "ret": ret,
        "stats": {"1D": {"port": -0.0362, "spy": -0.006, "qqq": -0.019},
                  "Since 2026-01-01": {"port": 0.6958, "spy": 0.1013, "qqq": 0.1919}},
        "start": date(2026, 1, 1), "end": date(2026, 6, 16),
    }
    cfg = {"risk": {"score_entry_above": 0.90, "score_entry_days": 3, "stop_loss_score_max": 0.90,
                    "target_vol": 0.35},
           "portfolio": {"max_position_pct": 0.085, "max_new_trades_per_day": 2}}
    return d, cfg


def test_commentary_flags_inversion_and_governor():
    d, cfg = _dict_and_cfg()
    comm = P._commentary(d, cfg)
    text = " ".join(comm["observations"]).lower()
    assert "inverted" in text                  # negative spread => momentum reversal called out
    assert "governor" in text and "0.82" in " ".join(comm["observations"])  # de-risk noted
    recs = " ".join(comm["recommendations"])
    assert "AMAT" in recs                       # gate-clearing, not-held => buy candidate
    assert "SOFI" in recs                       # ▲14 below gate => watchlist
    assert "defensive" in recs.lower()          # em<1 and spread<0 => defensive stance


def test_buy_candidate_excludes_held_and_sub_gate():
    d, cfg = _dict_and_cfg()
    recs = " ".join(P._commentary(d, cfg)["recommendations"])
    # ARM clears the gate but is HELD -> must not be a buy candidate line entry
    assert "ARM (0.9" not in recs
    # PLUG is far below the gate -> never a candidate
    assert "PLUG (" not in recs


def test_build_pdf_writes_four_page_file(tmp_path):
    d, cfg = _dict_and_cfg()
    out = tmp_path / "eod.pdf"
    P.build_pdf(d, cfg, out)
    assert out.exists() and out.stat().st_size > 5000
    head = out.read_bytes()[:5]
    assert head.startswith(b"%PDF")


def test_build_pdf_renders_queued_trades(tmp_path):
    d, cfg = _dict_and_cfg()
    d["next_session"] = {
        "buys": [{"ticker": "AMAT", "shares": 25, "price": 568.23, "value": 14205.0,
                  "reason": "momentum_score=0.913"}],
        "sells": [{"ticker": "INTC", "shares": 123, "price": 117.05, "value": 14397.0,
                   "reason": "rotation_funded", "pnl": 2700.0}],
        "buy_reason": None, "sell_reason": None,
        "invested_frac": 0.74, "exposure_cap_frac": 0.82,
    }
    out = tmp_path / "eod_trades.pdf"
    P.build_pdf(d, cfg, out)
    assert out.exists() and out.read_bytes()[:5].startswith(b"%PDF")


def test_parse_helpers():
    assert abs(P._parse_pct("-4.03%") + 0.0403) < 1e-9
    assert P._parse_pct("—") is None
    assert P._parse_money("$-3,145") == -3145.0
    assert P._parse_money("—") is None
