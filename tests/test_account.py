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
