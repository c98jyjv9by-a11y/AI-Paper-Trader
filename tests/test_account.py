"""test_account.py — frozen-account ledger integrity (offline; no network/backtest)."""
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import account as A


def _make_account(root: Path, name: str = "primary") -> Path:
    d = root / name
    (d / "reports").mkdir(parents=True, exist_ok=True)
    (d / "rankings").mkdir(parents=True, exist_ok=True)
    (d / "trades.csv").write_text("date,action,ticker,shares,price\n2026-01-05,BUY,MU,26,312.33\n")
    (d / "equity.csv").write_text("date,total_portfolio_value,cash\n2026-01-05,100000,50000\n")
    (d / "positions.csv").write_text("ticker,shares,entry_price,entry_date,current_price\nMU,26,312.33,2026-01-05,320.0\n")
    (d / "reports" / "status.md").write_text("# status\n")
    hashes = {f: A._sha256(d / f) for f in A._LEDGER_FILES}
    hashes["reports/status.md"] = A._sha256(d / "reports" / "status.md")
    (d / "manifest.json").write_text(json.dumps({
        "name": name, "scenario": "model_v4", "status": "frozen",
        "inception": "2026-01-01", "frozen_through": "2026-06-17",
        "starting_value": 100000.0, "hashes": hashes,
    }))
    return d


def test_verify_intact(tmp_path, monkeypatch):
    monkeypatch.setattr(A, "ACCOUNTS_DIR", tmp_path)
    _make_account(tmp_path)
    r = A.verify("primary")
    assert r["intact"] and not r["drift"] and not r["missing"]
    assert "trades.csv" in r["ok"]


def test_verify_detects_drift_and_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(A, "ACCOUNTS_DIR", tmp_path)
    d = _make_account(tmp_path)
    (d / "trades.csv").write_text("date,action,ticker,shares,price\n2026-01-05,BUY,NVDA,1,1.0\n")  # tamper
    (d / "reports" / "status.md").unlink()                                                          # remove
    r = A.verify("primary")
    assert not r["intact"]
    assert "trades.csv" in r["drift"]
    assert "reports/status.md" in r["missing"]


def test_load_ledger_and_active(tmp_path, monkeypatch):
    monkeypatch.setattr(A, "ACCOUNTS_DIR", tmp_path)
    _make_account(tmp_path)
    (tmp_path / "ACTIVE").write_text("primary\n")
    led = A.load_ledger("primary")
    assert led["manifest"]["frozen_through"] == "2026-06-17"
    assert list(led["trades"]["ticker"]) == ["MU"]
    assert A.active_account() == "primary"


def test_freeze_refuses_overwrite(tmp_path, monkeypatch):
    monkeypatch.setattr(A, "ACCOUNTS_DIR", tmp_path)
    _make_account(tmp_path)                                # manifest already exists
    try:
        A.freeze("primary", "model_v4", date(2026, 1, 1), date(2026, 6, 17), force=False)
        assert False, "expected FileExistsError"
    except FileExistsError as e:
        assert "already frozen" in str(e)


def test_load_manifest_missing_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(A, "ACCOUNTS_DIR", tmp_path)
    try:
        A.load_manifest("nope")
        assert False, "expected FileNotFoundError"
    except FileNotFoundError:
        pass


# ── Phase 2: living continuation ──────────────────────────────────────────────
import numpy as np
import pandas as pd


def _make_living_seed(root: Path, name: str = "acct") -> Path:
    """A frozen account whose ledger lives in the synthetic 2024 window."""
    d = root / name
    (d / "reports").mkdir(parents=True, exist_ok=True)
    (d / "trades.csv").write_text("date,action,ticker,shares,price,trade_value,reason,realized_pnl,holding_days\n"
                                  "2024-01-03,BUY,AAA,10,100.0,1000.0,seed,,0\n")
    (d / "equity.csv").write_text("date,total_portfolio_value,cash\n"
                                  "2024-01-03,100000,99000\n2024-01-10,100000,99000\n")
    (d / "positions.csv").write_text("ticker,shares,entry_price,entry_date,current_price,highest_price,lowest_price\n"
                                     "AAA,10,100.0,2024-01-03,100.0,100.0,100.0\n")
    hashes = {f: A._sha256(d / f) for f in A._LEDGER_FILES}
    (d / "manifest.json").write_text(json.dumps({
        "name": name, "scenario": "model_x", "status": "frozen",
        "inception": "2024-01-02", "frozen_through": "2024-01-10",
        "starting_value": 100000.0, "hashes": hashes}))
    return d


def _flat_panel(tickers, lo="2023-10-01", hi="2024-01-20", px=100.0):
    dates = pd.bdate_range(lo, hi)
    cols = pd.MultiIndex.from_product([["Close", "Volume"], tickers])
    df = pd.DataFrame(index=dates, columns=cols, dtype=float)
    for t in tickers:
        df[("Close", t)] = px
        df[("Volume", t)] = 1e6
    return df


def test_continue_noop_when_end_not_past_live(tmp_path, monkeypatch):
    monkeypatch.setattr(A, "ACCOUNTS_DIR", tmp_path)
    _make_living_seed(tmp_path)
    r = A.continue_account("acct", date(2024, 1, 10))      # == live end → nothing to do
    assert r.get("noop") and r["live_through"] == "2024-01-10"
    assert not (tmp_path / "acct" / "continuation").exists()


def test_continue_appends_and_merges(tmp_path, monkeypatch):
    monkeypatch.setattr(A, "ACCOUNTS_DIR", tmp_path)
    _make_living_seed(tmp_path)
    import scenarios, backtest
    cfg = {"tickers": ["AAA"],
           "portfolio": {"starting_value": 100000.0, "max_position_pct": 0.05,
                         "max_total_exposure": 0.30, "max_new_trades_per_day": 0},
           "risk": {"stop_loss": 0.9, "take_profit": 9.0, "max_holding_days": 999, "slippage": 0.0},
           "signals": {"top_candidates": 5}}
    monkeypatch.setattr(scenarios, "build_config", lambda *a, **k: cfg)
    monkeypatch.setattr(scenarios, "load_scenario", lambda *a, **k: {})
    monkeypatch.setattr(backtest, "load_config", lambda *a, **k: {})
    monkeypatch.setattr(backtest, "fetch_backtest_data",
                        lambda tickers, s, e, **k: _flat_panel(list(tickers) + ["SPY", "QQQ"]))

    r = A.continue_account("acct", date(2024, 1, 18), scenario="model_x")
    assert not r.get("noop") and r["segments"] == 1
    assert (tmp_path / "acct" / "continuation" / "equity.csv").exists()
    # combined view extends past the frozen end and still holds the seeded position
    led = A.load_ledger("acct")
    assert led["equity"]["date"].iloc[-1] > "2024-01-10"
    assert "AAA" in set(led["positions"]["ticker"])
    assert led["manifest"]["status"] == "living"
    # frozen core is untouched → verify's core hashes still match
    v = A.verify("acct")
    assert "trades.csv" not in v["drift"] and "equity.csv" not in v["drift"]
