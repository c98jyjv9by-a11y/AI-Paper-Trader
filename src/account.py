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
    """Combined account view: the immutable frozen core PLUS any Phase-2 continuation
    segments (trades/equity appended; positions = the latest live book)."""
    d = _acct_dir(name)
    man = load_manifest(name)
    trades = pd.read_csv(d / "trades.csv")
    equity = pd.read_csv(d / "equity.csv")
    positions = pd.read_csv(d / "positions.csv")
    cont = d / "continuation"
    if (cont / "equity.csv").exists():            # living account — layer continuation on top
        ct = cont / "trades.csv"
        if ct.exists() and ct.stat().st_size > 0:
            trades = pd.concat([trades, pd.read_csv(ct)], ignore_index=True)
        equity = pd.concat([equity, pd.read_csv(cont / "equity.csv")], ignore_index=True)
        if (cont / "positions.csv").exists():
            positions = pd.read_csv(cont / "positions.csv")   # current book replaces frozen
    return {"manifest": man, "trades": trades, "equity": equity, "positions": positions}


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


# ── Continue (Phase 2: living continuation) ──────────────────────────────────────
def continue_account(name: str, end: date, *, scenario: Optional[str] = None,
                     now: Optional[str] = None) -> Dict[str, Any]:
    """Extend a frozen account forward to `end`, seeded from its latest state, trading with
    `scenario` (defaults to the account's base — pass the CURRENT model to 'follow active').
    The frozen core is never modified; new days are appended under continuation/. Returns a
    summary dict (or {'noop': True} if there's nothing past the current live end)."""
    import datetime as _dt
    from scenarios import build_config, load_scenario
    from backtest import load_config, fetch_backtest_data, run_backtest

    man = load_manifest(name)
    scenario = scenario or man["scenario"]
    d_dir = _acct_dir(name)
    cont = d_dir / "continuation"

    # Integrity gate: the frozen core must be intact before we extend it.
    chk = verify(name)
    core_drift = [f for f in (chk["drift"] + chk["missing"]) if not f.startswith("continuation/")]
    if core_drift:
        raise RuntimeError(f"Frozen core of '{name}' has drifted ({core_drift}); refusing to continue.")

    led = load_ledger(name)                       # combined latest state
    eq = led["equity"]
    last_iso = str(eq["date"].iloc[-1])
    if end.isoformat() <= last_iso:
        return {"noop": True, "live_through": last_iso, "requested_end": end.isoformat()}
    cont_start = date.fromisoformat(last_iso) + _dt.timedelta(days=1)

    seed_cash = float(eq["cash"].iloc[-1])
    seed_equity = list(eq["total_portfolio_value"].astype(float).iloc[-200:])
    seed_positions = led["positions"]

    cfg = build_config(load_config(ROOT / "config"), load_scenario(scenario))
    # Price the continuation universe UNION held names, so seeded positions are always priced
    # even if the (possibly switched) model's universe no longer lists them.
    uni = list(dict.fromkeys(list(cfg["tickers"]) + list(seed_positions.get("ticker", []))))
    pdata = fetch_backtest_data(uni, cont_start, end, warmup_days=150)
    new_trades, new_eq, new_pos = run_backtest(
        cfg, pdata, cont_start, end,
        initial_cash=seed_cash, initial_positions=seed_positions, initial_equity=seed_equity)
    if new_eq.empty:
        return {"noop": True, "live_through": last_iso, "requested_end": end.isoformat()}

    cont.mkdir(parents=True, exist_ok=True)
    _append_csv(cont / "trades.csv", new_trades)
    _append_csv(cont / "equity.csv", new_eq)
    new_pos.to_csv(cont / "positions.csv", index=False)     # current book (replaced)

    seg = {"scenario": scenario, "from": cont_start.isoformat(), "to": end.isoformat(),
           "ran_at": now or _dt.datetime.now().isoformat(timespec="seconds"),
           "n_trades": int(len(new_trades))}
    segments = man.get("segments", []) + [seg]
    man["segments"] = segments
    man["live_through"] = str(new_eq["date"].iloc[-1])
    man["live_value"] = float(new_eq["total_portfolio_value"].iloc[-1])
    man["status"] = "living"

    # Render + archive the EOD + status reports for the new live date, FROM the living
    # ledger (combined frozen + continuation). Reports are a nicety — never fail the update.
    reports_written = []
    try:
        import rank_report
        import pdf_report
        end_iso = man["live_through"]
        d_rep = rank_report.build_report(scenario, date.fromisoformat(man["inception"]),
                                         date.fromisoformat(end_iso), cfg=cfg, account=name,
                                         write_snapshot=False, with_intraday=False)
        (d_dir / "reports").mkdir(exist_ok=True)
        smd = d_dir / "reports" / f"status_{scenario}_{end_iso}.md"
        epdf = d_dir / "reports" / f"eod_{scenario}_{end_iso}.pdf"
        smd.write_text(rank_report.render_md(d_rep))
        pdf_report.build_pdf(d_rep, cfg, epdf)
        reports_written = [smd.name, epdf.name]
    except Exception as exc:
        seg["report_error"] = str(exc)

    # Refresh continuation + (re-rendered) report hashes; the frozen-core ledger hashes stay.
    man.setdefault("hashes", {})
    for f in sorted(cont.glob("*.csv")):
        man["hashes"][f"continuation/{f.name}"] = _sha256(f)
    for f in sorted((d_dir / "reports").glob("*")):
        man["hashes"][f"reports/{f.name}"] = _sha256(f)
    _manifest_path(name).write_text(json.dumps(man, indent=2))
    return {"noop": False, **seg, "live_through": man["live_through"],
            "live_value": man["live_value"], "segments": len(segments),
            "reports": reports_written}


def _append_csv(path: Path, df: pd.DataFrame) -> None:
    """Append rows to a CSV (header only when creating it). No-op for an empty frame."""
    if df is None or df.empty:
        return
    if path.exists():
        df.to_csv(path, mode="a", header=False, index=False)
    else:
        df.to_csv(path, index=False)


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
