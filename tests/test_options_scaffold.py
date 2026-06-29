"""Integration tests for the options scaffolding using a fake (no-network) Alpaca client."""
import datetime as _dt
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import broker_adapter as ba
import broker_sync as bs
import options_symbols as osym

EXPIRY = (_dt.date.today() + _dt.timedelta(days=35)).isoformat()
SPOTS = {"SPY": 500.0, "QQQ": 430.0}

MAN = {
    "name": "opt_test", "scenario": "model_v4", "broker": "alpaca_paper",
    "broker_keys": {"key_env": "X", "secret_env": "Y"}, "asset_class": "us_option",
    "options": {"level": 2, "underlyings": ["SPY", "QQQ"], "expiry_window_days": [25, 45],
                "roll_dte": 7, "moneyness": [-0.05, 0.05], "min_open_interest": 100,
                "max_spread_pct": 0.20, "feed": "indicative"},
    "target_mode": {"kind": "options", "strategy": "long_directional", "right": "call",
                    "top_n": 2, "rebalance": "weekly", "gross": 0.30},
}


class FakeAlpaca:
    """Canned chain/account data so the options paths run fully offline."""
    def __init__(self, positions=None, level=2):
        self._positions = positions or []
        self._level = level

    def account(self):
        return {"equity": 100000.0, "cash": 100000.0, "last_equity": 99000.0,
                "options_trading_level": self._level, "status": "ACTIVE"}

    def positions(self):
        return list(self._positions)

    def clock(self):
        return {"timestamp": _dt.date.today().isoformat() + "T15:45:00Z", "is_open": True}

    def latest_prices(self, symbols):
        return {s: {"bid": SPOTS[s] - 0.05, "ask": SPOTS[s] + 0.05, "mid": SPOTS[s]}
                for s in symbols if s in SPOTS}

    def option_contracts(self, underlying, expiration_gte=None, expiration_lte=None,
                         strike_gte=None, strike_lte=None, type=None, limit=1000):
        spot = SPOTS[underlying]
        out = []
        for k in [spot - 10, spot - 5, spot, spot + 5, spot + 10]:
            if strike_gte and k < strike_gte:
                continue
            if strike_lte and k > strike_lte:
                continue
            for right in ("call", "put"):
                out.append({"symbol": osym.to_occ(underlying, EXPIRY, k, right),
                            "open_interest": 1000, "strike_price": k})
        return out

    def option_snapshots(self, underlying, feed="indicative"):
        out = {}
        for c in self.option_contracts(underlying):
            occ = c["symbol"]; p = osym.parse_occ(occ)
            prem = max(0.5, 8 - abs(p["strike"] - SPOTS[underlying]) * 0.3)
            out[occ] = {"latestQuote": {"bp": prem - 0.10, "ap": prem + 0.10},
                        "greeks": {"delta": 0.5}, "impliedVolatility": 0.25}
        return out

    def option_quotes(self, occ_symbols, feed="indicative"):
        q = {}
        for occ in occ_symbols:
            p = osym.parse_occ(occ)
            prem = max(0.5, 8 - abs(p["strike"] - SPOTS[p["underlying"]]) * 0.3)
            q[occ] = {"bid": prem - 0.10, "ask": prem + 0.10, "mid": prem}
        return q


@pytest.fixture(autouse=True)
def _offline(monkeypatch):
    monkeypatch.setattr(bs, "load_manifest", lambda name: MAN)
    monkeypatch.setattr(bs, "_recent_trading_days", lambda *a, **k: [])
    monkeypatch.setattr(bs, "_last_closes", lambda syms: {})


def test_compute_targets_picks_atm_calls():
    cli = FakeAlpaca()
    targets, refs, dec = bs.compute_targets("opt_test", cli, {})
    assert len(targets) == 2                                   # one contract per underlying
    for occ, contracts in targets.items():
        p = osym.parse_occ(occ)
        assert p["right"] == "call"                            # right=call honored
        assert p["strike"] == SPOTS[p["underlying"]]          # ATM
        assert contracts >= 1                                  # sized by premium*100
        assert occ in refs and occ in dec


def test_option_orders_are_day_tif_marketable():
    cli = FakeAlpaca()
    targets, _, _ = bs.compute_targets("opt_test", cli, {})
    quotes = cli.option_quotes(list(targets))
    orders = ba.build_option_reconcile_orders(targets, {}, quotes, "2026-06-29", spread_pct=0.20)
    assert orders and len(orders) == len(targets)
    for o in orders:
        assert o["time_in_force"] == "day"                    # no opg/cls for options
        assert "extended_hours" not in o
        assert o["type"] == "limit" and o["side"] == "buy"
        assert osym.is_occ(o["symbol"])
        assert o["_plan"]["est_value"] == pytest.approx(int(o["qty"]) * o["_plan"]["ref_mid"] * 100)


def test_held_contract_rolls_near_expiry():
    near = osym.to_occ("SPY", (_dt.date.today() + _dt.timedelta(days=3)).isoformat(), 500, "call")
    cli = FakeAlpaca(positions=[{"ticker": near, "qty": 5.0, "avg_entry": 7.0, "price": 6.0,
                                 "market_value": 3000.0, "asset_class": "us_option"}])
    targets, _, dec = bs.compute_targets("opt_test", cli, {near: 5})
    assert near not in targets                                 # expiring contract is flattened (rolled)
    assert "roll" in dec[near]["reason"].lower()


def test_ledger_from_broker_has_option_columns():
    occ = osym.to_occ("SPY", EXPIRY, 500, "call")
    snap = bs.ledger_from_broker(
        [{"ticker": occ, "qty": 5.0, "avg_entry": 7.0, "price": 8.0,
          "market_value": 4000.0, "asset_class": "us_option"}],
        cash=96000.0, equity=100000.0, asof="2026-06-29")
    pos = snap["positions"]
    for col in bs._OPT_POS_EXTRA:
        assert col in pos.columns
    row = pos.iloc[0]
    assert row["underlying"] == "SPY" and row["right"] == "call"
    assert row["strike"] == 500.0 and row["multiplier"] == 100
    assert row["occ_symbol"] == occ


def test_create_account_writes_option_headers(monkeypatch, tmp_path):
    monkeypatch.setattr(bs, "_acct_dir", lambda name: tmp_path)
    monkeypatch.setattr(bs, "_manifest_path", lambda name: tmp_path / "manifest.json")
    monkeypatch.setattr(bs, "_sha256", lambda f: "deadbeef")
    man = bs.create_broker_account("opt_x", target_mode=MAN["target_mode"], options=MAN["options"])
    assert man["asset_class"] == "us_option"
    import pandas as pd
    pcols = list(pd.read_csv(tmp_path / "positions.csv").columns)
    tcols = list(pd.read_csv(tmp_path / "trades.csv").columns)
    assert "occ_symbol" in pcols and "right" in pcols
    assert "open_close" in tcols and "premium" in tcols


def test_apply_option_marks():
    occ = osym.to_occ("SPY", EXPIRY, 500, "call")
    cli = FakeAlpaca(positions=[{"ticker": occ, "qty": 5.0, "avg_entry": 7.0, "price": 8.0,
                                 "market_value": 4000.0, "asset_class": "us_option"}])
    d = {"mark": "2026-06-29", "pv": 0, "cash": 0}
    assert bs.apply_live_broker_marks(d, "opt_test", cli) is True
    assert d["hedge"] is None
    assert d["pv"] == 100000.0
    assert d["positions"].iloc[0]["underlying"] == "SPY"
    assert d["broker_day_return"] == pytest.approx(100000.0 / 99000.0 - 1)


def test_submit_session_blocks_on_low_level(monkeypatch):
    cli = FakeAlpaca(level=0)                                  # options not enabled
    monkeypatch.setattr(ba, "AlpacaPaper", lambda *a, **k: cli)
    res = bs.submit_session("opt_test", cli=cli, submit=True)
    assert res.get("blocked") and "level" in res["reason"]
