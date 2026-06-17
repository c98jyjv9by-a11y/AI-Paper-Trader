"""
account.py — Frozen paper-trading account ledgers (Phase 1: static record).

A persisted, IMMUTABLE record of a scenario's trades + daily portfolio state over a
window. We freeze the DERIVED ledger (trades / equity / positions / rankings / rendered
reports) — not the config — so the record survives later model/config changes AND
yfinance revising old prices. Reports can read the frozen ledger via
`rank_report.build_report(..., account=<name>)`, so the locked window stays reproducible.

Layout (accounts/<name>/):
  manifest.json   metadata + SHA-256 of each frozen file (integrity)
  trades.csv      full BUY/SELL log for the window (authoritative)
  equity.csv      daily total value / cash / exposure_mult / forecast_vol
  positions.csv   open book at frozen_through
  rankings/       daily write-once ranking snapshots (copied in)
  reports/        rendered status MD + EOD PDF + backtest report for the window

Read-only w.r.t. the live-agent data/ files — writes only under accounts/.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

ROOT = Path(__file__).parent.parent
ACCOUNTS_DIR = ROOT / "accounts"
_LEDGER_FILES = ("trades.csv", "equity.csv", "positions.csv")


def _acct_dir(name: str) -> Path:
    return ACCOUNTS_DIR / name


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _manifest_path(name: str) -> Path:
    return _acct_dir(name) / "manifest.json"


def load_manifest(name: str) -> Dict[str, Any]:
    p = _manifest_path(name)
    if not p.exists():
        raise FileNotFoundError(f"No frozen account '{name}' (missing {p}).")
    return json.loads(p.read_text())


def load_ledger(name: str) -> Dict[str, Any]:
    """Frozen trades / equity / positions DataFrames + manifest for an account."""
    d = _acct_dir(name)
    man = load_manifest(name)
    return {
        "manifest": man,
        "trades": pd.read_csv(d / "trades.csv"),
        "equity": pd.read_csv(d / "equity.csv"),
        "positions": pd.read_csv(d / "positions.csv"),
    }


def active_account() -> Optional[str]:
    """The promoted/primary account name, if any (accounts/ACTIVE)."""
    p = ACCOUNTS_DIR / "ACTIVE"
    return p.read_text().strip() if p.exists() else None


# ── Freeze ────────────────────────────────────────────────────────────────────────
def freeze(name: str, scenario: str, start: date, end: date, *,
           force: bool = False, promote: bool = True, now: Optional[str] = None) -> Dict[str, Any]:
    """Run the scenario once over [start, end] and persist an immutable account ledger
    + rendered reports. Refuses to overwrite an existing frozen account unless force=True."""
    import rank_report
    import pdf_report
    from scenarios import build_config, load_scenario
    from backtest import (load_config, fetch_backtest_data, run_backtest,
                          compute_metrics, generate_backtest_report)

    d_dir = _acct_dir(name)
    if _manifest_path(name).exists() and not force:
        raise FileExistsError(
            f"Account '{name}' is already frozen ({_manifest_path(name)}). "
            "Refusing to overwrite — pass force=True to intentionally re-freeze.")
    (d_dir / "rankings").mkdir(parents=True, exist_ok=True)
    (d_dir / "reports").mkdir(parents=True, exist_ok=True)

    cfg = build_config(load_config(ROOT / "config"), load_scenario(scenario))
    pdata = fetch_backtest_data(cfg["tickers"], start, end)
    trades, eq, positions = run_backtest(cfg, pdata, start, end)
    metrics = compute_metrics(trades, eq, positions, cfg, start, end)

    # 1) Ledger
    trades.to_csv(d_dir / "trades.csv", index=False)
    eq.to_csv(d_dir / "equity.csv", index=False)
    positions.to_csv(d_dir / "positions.csv", index=False)

    # 2) Rendered reports (status MD + EOD PDF + backtest report MD), built from THIS run
    d = rank_report.build_report(scenario, start, end, cfg=cfg, pdata=pdata,
                                 eq=eq, positions=positions, trades=trades)
    (d_dir / "reports" / f"status_{scenario}_{end.isoformat()}.md").write_text(rank_report.render_md(d))
    pdf_report.build_pdf(d, cfg, d_dir / "reports" / f"eod_{scenario}_{end.isoformat()}.pdf")
    (d_dir / "reports" / f"backtest_{scenario}_{end.isoformat()}.md").write_text(
        generate_backtest_report(metrics, cfg, trades, eq, positions, end))

    # 3) Copy any daily ranking snapshots that fall in the window
    copied_rankings = []
    for snap in sorted((ROOT / "backtests").glob(f"rankings_{scenario}_*.csv")):
        try:
            d_iso = snap.stem.split("_")[-1]
            if start.isoformat() <= d_iso <= end.isoformat():
                shutil.copy2(snap, d_dir / "rankings" / snap.name)
                copied_rankings.append(snap.name)
        except Exception:
            continue

    # 4) Manifest with content hashes
    hashes = {f: _sha256(d_dir / f) for f in _LEDGER_FILES}
    for sub in ("reports", "rankings"):
        for f in sorted((d_dir / sub).glob("*")):
            hashes[f"{sub}/{f.name}"] = _sha256(f)
    manifest = {
        "name": name, "scenario": scenario, "status": "frozen",
        "inception": start.isoformat(), "frozen_through": end.isoformat(),
        "starting_value": float(cfg["portfolio"]["starting_value"]),
        "ending_value": float(eq["total_portfolio_value"].iloc[-1]),
        "total_return": metrics.get("total_return"),
        "n_trades": int(len(trades)), "n_positions": int(len(positions)),
        "created_at": now or datetime.now().isoformat(timespec="seconds"),
        "rankings_copied": copied_rankings,
        "note": ("Immutable derived ledger; frozen against config/model changes and price "
                 "revisions. Phase 1 = static record (no forward trading)."),
        "hashes": hashes,
    }
    _manifest_path(name).write_text(json.dumps(manifest, indent=2))
    if promote:
        (ACCOUNTS_DIR / "ACTIVE").write_text(name + "\n")
    return manifest


# ── Verify ──────────────────────────────────────────────────────────────────────
def verify(name: str) -> Dict[str, Any]:
    """Recompute hashes and report any drift vs the manifest. Returns a result dict."""
    man = load_manifest(name)
    d_dir = _acct_dir(name)
    drift, missing, ok = [], [], []
    for rel, want in (man.get("hashes") or {}).items():
        p = d_dir / rel
        if not p.exists():
            missing.append(rel)
        elif _sha256(p) != want:
            drift.append(rel)
        else:
            ok.append(rel)
    return {"name": name, "intact": (not drift and not missing),
            "ok": ok, "drift": drift, "missing": missing,
            "frozen_through": man.get("frozen_through")}
