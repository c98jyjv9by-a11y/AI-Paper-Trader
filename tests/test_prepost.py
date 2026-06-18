"""test_prepost.py — extended-hours (--prepost) marking in rank_report.build_report.

Deterministic & offline: the network helper extended_hours_prices is monkeypatched, so we
verify the wiring (mark-bar override → returns / current_price / PV / stamp) without yfinance.
"""
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import rank_report as R


def _panel(last_day: date, n: int = 30):
    """Daily OHLC-style panel (Close+Volume MultiIndex) ending on `last_day`. AAA's last
    (mark) close is 105 with a 100 prior close, so a 110 extended print is distinguishable."""
    idx = pd.bdate_range(end=pd.Timestamp(last_day), periods=n)
    close = {}
    for t in ["AAA", "BBB", "SPY", "QQQ"]:
        close[t] = 100.0 * 1.001 ** np.arange(n)
    close["AAA"][-2] = 100.0          # prior close
    close["AAA"][-1] = 105.0          # daily mark close (regular session)
    cl = pd.DataFrame(close, index=idx)
    vol = pd.DataFrame({t: np.full(n, 1e6) for t in close}, index=idx)
    cl.columns = pd.MultiIndex.from_product([["Close"], cl.columns])
    vol.columns = pd.MultiIndex.from_product([["Volume"], vol.columns])
    return pd.concat([cl, vol], axis=1)


def _cfg():
    return {"tickers": ["AAA", "BBB"], "signals": {"min_composite_score": None},
            "portfolio": {"starting_value": 100_000.0, "max_position_pct": 0.1,
                          "max_total_exposure": 0.9, "max_new_trades_per_day": 2},
            "risk": {"slippage": 0.001, "stop_loss": 0.15, "take_profit": None,
                     "max_holding_days": 90}}


def _eq_pos(pdata):
    idx = pdata.index
    eq = pd.DataFrame({"date": [d.date().isoformat() for d in idx],
                       "total_portfolio_value": np.full(len(idx), 101_000.0),
                       "cash": np.full(len(idx), 1_000.0)})
    pos = pd.DataFrame([{"ticker": "AAA", "shares": 10, "entry_price": 100.0,
                         "current_price": 100.0, "entry_date": idx[-4].date().isoformat()}])
    return eq, pos


def _build(pdata, prepost, monkeypatch, ext=None, label="19:59 ET post-market", asof=None):
    if ext is not None:
        monkeypatch.setattr(R, "extended_hours_prices",
                            lambda tickers, **k: (ext, label, asof))
    eq, pos = _eq_pos(pdata)
    return R.build_report("t", pdata.index[0].date(), pdata.index[-1].date(), cfg=_cfg(),
                          pdata=pdata, eq=eq, positions=pos, trades=pd.DataFrame(),
                          write_snapshot=False, with_intraday=False, prepost=prepost)


def test_prepost_overwrites_same_day_mark(monkeypatch):
    """Post-market: the extended print is for the SAME day as the latest daily bar → overwrite."""
    pdata = _panel(date.today())
    ext = {"AAA": 110.0, "BBB": 100.0, "SPY": 100.0, "QQQ": 100.0}
    d = _build(pdata, True, monkeypatch, ext=ext, asof=date.today())
    assert d["prepost"] is True and d["mark_note"] == "19:59 ET post-market"
    # AAA return uses the 110 after-hours print over the 100 prior close (not the 105 mark)
    assert abs(d["ret"]("AAA") - 0.10) < 1e-9
    assert abs(float(d["positions"].loc[d["positions"].ticker == "AAA", "current_price"].iloc[0]) - 110.0) < 1e-9
    assert abs(d["pv"] - (1_000.0 + 10 * 110.0)) < 1e-6


def test_prepost_appends_bar_for_newer_session(monkeypatch):
    """Pre-market on a new day: the extended print post-dates the daily panel → append a fresh
    mark bar, so the prior daily close becomes rank_close and 'latest' is distinguished."""
    last_bd = (pd.Timestamp(date.today()) - pd.tseries.offsets.BDay(1)).date()
    pdata = _panel(last_bd)                              # daily panel ends on the prior session
    ext = {"AAA": 120.0, "BBB": 100.0, "SPY": 100.0, "QQQ": 100.0}
    d = _build(pdata, True, monkeypatch, ext=ext, label="08:31 ET pre-market", asof=date.today())
    assert d["prepost"] is True and d["mark_note"] == "08:31 ET pre-market"
    assert d["mark"] == date.today() and d["rank_close"] == last_bd   # new bar appended
    # AAA latest 120 vs the prior daily close 105 (the panel's last regular close)
    assert abs(d["ret"]("AAA") - (120.0 / 105.0 - 1)) < 1e-9
    assert abs(d["pv"] - (1_000.0 + 10 * 120.0)) < 1e-6


def test_no_prepost_uses_regular_mark(monkeypatch):
    pdata = _panel(date.today())
    # even if the helper would return something, prepost=False must ignore it
    monkeypatch.setattr(R, "extended_hours_prices", lambda tickers, **k: ({"AAA": 110.0}, "x", date.today()))
    d = _build(pdata, False, monkeypatch=monkeypatch)
    assert d["prepost"] is False and d["mark_note"] is None
    assert abs(d["ret"]("AAA") - 0.05) < 1e-9          # 105 / 100 - 1, the regular daily mark


def test_prepost_guarded_to_live_render(monkeypatch):
    # a historical render (end far in the past) must NOT fetch or apply extended prices
    pdata = _panel(date(2024, 6, 14))
    called = {"n": 0}

    def _spy(tickers, **k):
        called["n"] += 1
        return ({"AAA": 110.0}, "x", date(2024, 6, 14))
    monkeypatch.setattr(R, "extended_hours_prices", _spy)
    d = _build(pdata, True, monkeypatch=monkeypatch)
    assert called["n"] == 0                              # helper not even invoked off-session
    assert d["prepost"] is False and d["mark_note"] is None
    assert abs(d["ret"]("AAA") - 0.05) < 1e-9
