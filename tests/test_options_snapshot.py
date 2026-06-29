"""Unit tests for the daily option-chain snapshot transform (no network)."""
import datetime as _dt
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import options_snapshot as osnap


def _calls():
    return pd.DataFrame([
        {"contractSymbol": "AAPL260116C00150000", "strike": 150.0, "bid": 5.0, "ask": 5.2,
         "lastPrice": 5.1, "volume": 100, "openInterest": 2000, "impliedVolatility": 0.30,
         "inTheMoney": True},
        {"contractSymbol": "AAPL260116C00160000", "strike": 160.0, "bid": 1.0, "ask": 1.2,
         "lastPrice": 1.1, "volume": float("nan"), "openInterest": float("nan"),
         "impliedVolatility": float("nan"), "inTheMoney": False},
    ])


def _puts():
    return pd.DataFrame([
        {"contractSymbol": "AAPL260116P00150000", "strike": 150.0, "bid": 4.0, "ask": 4.4,
         "lastPrice": 4.2, "volume": 50, "openInterest": 1500, "impliedVolatility": 0.33,
         "inTheMoney": False},
    ])


def test_chain_records_shape_and_values():
    asof = _dt.date(2026, 1, 1)
    rows = osnap._chain_records("AAPL", 155.0, "2026-01-16", _calls(), _puts(), asof, "2026-01-01T16:10:00")
    assert len(rows) == 3                                   # 2 calls + 1 put
    by_sym = {r["contract_symbol"]: r for r in rows}
    c = by_sym["AAPL260116C00150000"]
    assert c["right"] == "call" and c["strike"] == 150.0
    assert c["dte"] == 15
    assert c["mid"] == pytest.approx(5.1)                   # (5.0+5.2)/2
    assert c["open_interest"] == 2000 and c["volume"] == 100
    assert c["implied_vol"] == pytest.approx(0.30)
    assert c["moneyness"] == pytest.approx(150.0 / 155.0 - 1, abs=1e-4)
    assert by_sym["AAPL260116P00150000"]["right"] == "put"


def test_chain_records_handles_nan_safely():
    asof = _dt.date(2026, 1, 1)
    rows = osnap._chain_records("AAPL", 155.0, "2026-01-16", _calls(), _puts(), asof, "ts")
    nanrow = next(r for r in rows if r["contract_symbol"] == "AAPL260116C00160000")
    assert nanrow["volume"] == 0 and nanrow["open_interest"] == 0   # NaN -> 0
    assert nanrow["implied_vol"] is None                            # NaN IV -> None
    assert nanrow["mid"] == pytest.approx(1.1)


def test_chain_records_no_spot_means_no_moneyness():
    rows = osnap._chain_records("AAPL", None, "2026-01-16", _calls(), None, _dt.date(2026, 1, 1), "ts")
    assert all(r["moneyness"] is None and r["spot"] is None for r in rows)
    assert all(r["right"] == "call" for r in rows)        # puts=None skipped cleanly


def test_run_filters_dte_and_writes(monkeypatch, tmp_path):
    asof = _dt.date.today()
    near = (asof + _dt.timedelta(days=10)).isoformat()
    far = (asof + _dt.timedelta(days=90)).isoformat()
    past = (asof - _dt.timedelta(days=5)).isoformat()

    class FakeChain:
        def __init__(self, c, p): self.calls, self.puts = c, p

    class FakeTicker:
        def __init__(self, sym): self.sym = sym
        @property
        def options(self): return [past, near, far]        # only `near` is within max_dte and not past
        def option_chain(self, e):
            assert e == near                                # far/past must be filtered before fetch
            return FakeChain(_calls(), _puts())

    import types
    fake_yf = types.SimpleNamespace(Ticker=FakeTicker, download=lambda *a, **k: pd.DataFrame())
    monkeypatch.setitem(sys.modules, "yfinance", fake_yf)
    monkeypatch.setattr(osnap, "_spots", lambda u: {"AAPL": 155.0})
    monkeypatch.setattr(osnap, "OUTDIR", tmp_path)

    r = osnap.run(max_dte=31, tickers=["AAPL"])
    assert r["rows"] == 3 and r["expiries"] == 1 and r["errors"] == 0
    df = pd.read_csv(r["path"])
    assert set(df["expiry"]) == {near}                      # far + past excluded
    assert list(df.columns) == osnap._COLS
    assert (tmp_path / "_manifest.csv").exists()


def test_run_skips_when_exists(monkeypatch, tmp_path):
    monkeypatch.setattr(osnap, "OUTDIR", tmp_path)
    p = tmp_path / ("options_%s.csv.gz" % _dt.date.today().isoformat())
    p.write_text("placeholder")
    r = osnap.run(tickers=["AAPL"])
    assert r["skipped"] is True
