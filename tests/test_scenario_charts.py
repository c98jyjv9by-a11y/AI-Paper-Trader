"""
test_scenario_charts.py — Per-ticker annotated charts. No network (price panel
is injected via the `close=` arg so make_charts never calls yfinance).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import scenario_charts as sc


def _trades_and_close(tmp_path):
    dates = pd.date_range("2024-01-01", periods=120, freq="B")
    # AAA trends up, BBB chops; close panel [dates × tickers]
    close = pd.DataFrame({
        "AAA": 100 * 1.004 ** np.arange(120),
        "BBB": 100 * np.cumprod(1 + np.random.default_rng(1).normal(0, 0.01, 120)),
    }, index=dates)
    trades = pd.DataFrame([
        {"date": dates[10].date().isoformat(), "action": "BUY", "ticker": "AAA", "price": float(close["AAA"].iloc[10]), "reason": "signal=trend_50", "realized_pnl": None},
        {"date": dates[40].date().isoformat(), "action": "SELL", "ticker": "AAA", "price": float(close["AAA"].iloc[40]), "reason": "take_profit", "realized_pnl": 50.0},
        {"date": dates[50].date().isoformat(), "action": "BUY", "ticker": "AAA", "price": float(close["AAA"].iloc[50]), "reason": "signal=trend_50", "realized_pnl": None},
        {"date": dates[90].date().isoformat(), "action": "SELL", "ticker": "AAA", "price": float(close["AAA"].iloc[90]), "reason": "stop_loss+trailing_stop", "realized_pnl": -20.0},
        {"date": dates[20].date().isoformat(), "action": "BUY", "ticker": "BBB", "price": float(close["BBB"].iloc[20]), "reason": "signal=dip_5", "realized_pnl": None},
        {"date": dates[35].date().isoformat(), "action": "SELL", "ticker": "BBB", "price": float(close["BBB"].iloc[35]), "reason": "max_holding_period", "realized_pnl": 5.0},
    ])
    tcsv = tmp_path / "trades.csv"
    trades.to_csv(tcsv, index=False)
    return tcsv, close


def test_make_charts_with_injected_panel_writes_pngs(tmp_path):
    tcsv, close = _trades_and_close(tmp_path)
    out = tmp_path / "charts"
    summary = sc.make_charts(tcsv, out, "test", close=close)   # close provided → no network
    assert set(summary) == {"AAA", "BBB"}
    for tk in ("AAA", "BBB"):
        assert (out / f"{tk}.png").exists()
        assert "active_return" in summary[tk] and "hold_return" in summary[tk]
    # AAA is a clean uptrend held most of the window → positive hold return
    assert summary["AAA"]["hold_return"] > 0


def test_per_ticker_returns_compounds_round_trips():
    # two round trips of +10% then -5% → (1.1)(0.95) - 1 = 0.045
    trades = pd.DataFrame([
        {"date": "2024-01-02", "action": "BUY", "price": 100.0},
        {"date": "2024-01-10", "action": "SELL", "price": 110.0},
        {"date": "2024-01-15", "action": "BUY", "price": 100.0},
        {"date": "2024-01-20", "action": "SELL", "price": 95.0},
    ])
    ret, n, rts = sc._per_ticker_returns(trades, last_close=95.0)
    assert n == 2
    assert ret == __import__("pytest").approx(0.045, rel=1e-6)


def test_since_clip_and_seed_open(tmp_path):
    tcsv, close = _trades_and_close(tmp_path)
    out = tmp_path / "charts_since"
    # zoom to a window that starts mid-hold → seed_open path exercised
    summary = sc.make_charts(tcsv, out, "test", since=close.index[30].date(), close=close)
    assert (out / "AAA.png").exists()
