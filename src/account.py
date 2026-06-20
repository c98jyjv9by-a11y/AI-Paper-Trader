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


# ── Seed (a fresh live account that trails a model) ───────────────────────────────
def seed(name: str, scenario: str, *, cash: float = 100_000.0, top_n: int = 3,
         per_name_pct: Optional[float] = None, as_of: Optional[date] = None,
         force: bool = False, promote: bool = False, now: Optional[str] = None) -> Dict[str, Any]:
    """Create a NEW living account funded with `cash`, opening positions in the scenario's
    current top-`top_n` ranked names (scored on the latest close, bought at that close +
    slippage). Each position is sized at the model's per-name budget (`per_name_pct` or the
    scenario's max_position_pct) so the book genuinely TRAILS the model — the remaining cash
    is what `account-continue --scenario <model>` deploys as the model adds/rotates forward.

    Writes a normal account ledger (trades/equity/positions + manifest) so verify() and
    continue_account() work on it unchanged. Refuses to overwrite without force."""
    from scenarios import build_config, load_scenario
    from backtest import (load_config, fetch_backtest_data, _SIGNAL_WINDOW,
                          _build_ticker_weights, resolve_max_position_pct)
    from signals import calculate_signals, rank_candidates
    from risk import apply_slippage
    import datetime as _dt

    d_dir = _acct_dir(name)
    if _manifest_path(name).exists() and not force:
        raise FileExistsError(f"Account '{name}' already exists ({_manifest_path(name)}). "
                              "Pass force=True to overwrite.")
    cfg = build_config(load_config(ROOT / "config"), load_scenario(scenario))
    uni, weights = cfg["tickers"], cfg["signals"].get("weights")
    tw = _build_ticker_weights(cfg) or None
    slip = float(cfg.get("risk", {}).get("slippage", 0.001))
    pct = float(per_name_pct if per_name_pct is not None else resolve_max_position_pct(cfg))

    as_of = as_of or date.today()
    pdata = fetch_backtest_data(uni, as_of - _dt.timedelta(days=400), as_of)
    close = pdata["Close"]
    mark, prior = close.index[-1], close.index[-2]      # latest close + the bar before it
    # Rank the whole universe on the latest close; take the top N tradeable names.
    sl = pdata.loc[:mark].iloc[-_SIGNAL_WINDOW:]
    rf = rank_candidates(calculate_signals(sl, uni), top_n=len(uni), weights=weights,
                         ticker_weights=tw).reset_index(drop=True)
    picks = []
    for _, r in rf.iterrows():
        t = r["ticker"]
        px = close.loc[mark, t] if t in close.columns else None
        if px is None or pd.isna(px):
            continue
        picks.append((t, float(px), float(r["composite_score"])))
        if len(picks) >= top_n:
            break

    budget = cash * pct
    pos_rows, trade_rows = [], []
    spent = 0.0
    for t, px, score in picks:
        fill = apply_slippage(px, "buy", slip)
        shares = int(budget // fill)
        if shares <= 0:
            continue
        tv = round(fill * shares, 2)
        spent += tv
        pos_rows.append({"ticker": t, "shares": shares, "entry_price": fill,
                         "entry_date": mark.date().isoformat(), "current_price": px,
                         "highest_price": px, "lowest_price": px})
        trade_rows.append({"date": mark.date().isoformat(), "action": "BUY", "ticker": t,
                           "shares": shares, "price": fill, "trade_value": tv,
                           "reason": f"seed_top{top_n}", "realized_pnl": float("nan"),
                           "holding_days": 0, "entry_price": fill,
                           "highest_price": px, "lowest_price": px})
    positions = pd.DataFrame(pos_rows)
    trades = pd.DataFrame(trade_rows)
    remaining = round(cash - spent, 2)
    mkt = float((positions["shares"] * positions["current_price"]).sum()) if not positions.empty else 0.0
    unreal = float((positions["shares"] * (positions["current_price"] - positions["entry_price"])).sum()) \
        if not positions.empty else 0.0
    # Two equity rows (prior all-cash → buy day) so reports' trailing-window stats have an anchor.
    equity = pd.DataFrame([
        {"date": prior.date().isoformat(), "cash": cash, "open_positions_value": 0.0,
         "total_portfolio_value": cash, "realized_pnl_to_date": 0.0, "unrealized_pnl": 0.0,
         "exposure_mult": 1.0},
        {"date": mark.date().isoformat(), "cash": remaining, "open_positions_value": round(mkt, 2),
         "total_portfolio_value": round(remaining + mkt, 2), "realized_pnl_to_date": 0.0,
         "unrealized_pnl": round(unreal, 2), "exposure_mult": 1.0},
    ])

    d_dir.mkdir(parents=True, exist_ok=True)
    trades.to_csv(d_dir / "trades.csv", index=False)
    equity.to_csv(d_dir / "equity.csv", index=False)
    positions.to_csv(d_dir / "positions.csv", index=False)
    hashes = {f: _sha256(d_dir / f) for f in _LEDGER_FILES}
    manifest = {
        "name": name, "scenario": scenario, "status": "living",
        "inception": mark.date().isoformat(), "frozen_through": mark.date().isoformat(),
        "live_through": mark.date().isoformat(),
        "starting_value": float(cash), "ending_value": float(round(remaining + mkt, 2)),
        "total_return": float((remaining + mkt) / cash - 1),
        "n_trades": int(len(trades)), "n_positions": int(len(positions)),
        "created_at": now or datetime.now().isoformat(timespec="seconds"),
        "seed": {"picks": [{"ticker": t, "score": round(s, 4), "close": round(p, 2)}
                           for t, p, s in picks], "per_name_pct": pct, "cash": float(cash)},
        "note": (f"Seeded live account: ${cash:,.0f} → bought top-{top_n} {scenario} names at the "
                 f"{mark.date()} close, sized at {pct:.1%}/name. Trails {scenario} via account-continue."),
        "hashes": hashes,
    }
    _manifest_path(name).write_text(json.dumps(manifest, indent=2))
    if promote:
        (ACCOUNTS_DIR / "ACTIVE").write_text(name + "\n")
    return manifest


# ── Continue (Phase 2: living continuation) ──────────────────────────────────────
def _continue_ramp_up(name, end, man, scenario, d_dir, cont, now) -> Dict[str, Any]:
    """Ramp-up continuation: accumulate the >=entry_score book + roll the 1-day SOXS hedge.
    Reuses build_report to mark the book to `end` and to produce the ramp-up queue, then
    executes it (sell yesterday's hedge → buy new entries + fresh hedge), all at the mark close."""
    import datetime as _dt
    import pandas as pd
    from scenarios import build_config, load_scenario
    from backtest import load_config
    import rank_report, pdf_report

    led = load_ledger(name); eq = led["equity"]
    last_iso = str(eq["date"].iloc[-1])
    if end.isoformat() <= last_iso:
        return {"noop": True, "live_through": last_iso, "requested_end": end.isoformat()}
    cfg = build_config(load_config(ROOT / "config"), load_scenario(scenario))
    d = rank_report.build_report(scenario, date.fromisoformat(man["inception"]), end,
                                 cfg=cfg, account=name, write_snapshot=False, with_intraday=False)
    mark_iso = str(d["mark"])
    if mark_iso <= last_iso:                       # no new trading data yet
        return {"noop": True, "live_through": last_iso, "requested_end": end.isoformat()}

    pos = d["positions"].copy()
    cash = float(d["cash"])
    # re-mark the held book to the latest close (current ranking carries the marked prices)
    pxmap = {r["ticker"]: r["price"] for r in (d.get("rows_cur") or []) if r.get("price")}
    for i in pos.index:
        t = pos.at[i, "ticker"]
        if t in pxmap:
            pos.at[i, "current_price"] = float(pxmap[t])
    total = cash + float((pos["shares"] * pos["current_price"]).sum())
    trows = []

    def _trade(action, t, sh, px, reason, pnl=""):
        trows.append({"date": mark_iso, "action": action, "ticker": t, "shares": int(sh),
                      "price": float(px), "trade_value": float(sh * px), "reason": reason,
                      "realized_pnl": pnl, "holding_days": 0, "entry_price": float(px),
                      "highest_price": float(px), "lowest_price": float(px)})

    # 1) roll the 1-day hedge: exit any SOXS held from the prior session at the mark close
    if "SOXS" in set(pos["ticker"]):
        i = pos.index[pos["ticker"] == "SOXS"][0]
        sh = float(pos.at[i, "shares"]); px = float(pos.at[i, "current_price"])
        cash += sh * px; _trade("SELL", "SOXS", sh, px, "hedge expiry (1-day)")
        pos = pos[pos["ticker"] != "SOXS"].reset_index(drop=True)

    # 2) execute the queued ramp-up buys + fresh hedge (cash -> positions; total unchanged)
    for b in ((d.get("next_session") or {}).get("buys") or []):
        sh, px = int(b["shares"]), float(b["price"])
        if sh <= 0:
            continue
        cash -= sh * px; _trade("BUY", b["ticker"], sh, px, b["reason"])
        if b["ticker"] in set(pos["ticker"]):
            j = pos.index[pos["ticker"] == b["ticker"]][0]
            pos.at[j, "shares"] = float(pos.at[j, "shares"]) + sh
        else:
            pos = pd.concat([pos, pd.DataFrame([{"ticker": b["ticker"], "shares": sh,
                "entry_price": px, "entry_date": mark_iso, "current_price": px,
                "highest_price": px, "lowest_price": px}])], ignore_index=True)

    open_pos = total - cash
    prior_total = float(eq["total_portfolio_value"].iloc[-1])
    start_val = float(man.get("starting_value", prior_total))
    new_eq = pd.DataFrame([{"date": mark_iso, "cash": cash, "open_positions_value": open_pos,
        "total_portfolio_value": total, "realized_pnl_to_date": 0.0, "unrealized_pnl": total - start_val,
        "daily_return": (total / prior_total - 1) if prior_total else 0.0,
        "cumulative_return": (total / start_val - 1) if start_val else 0.0,
        "spy_cumulative_return": 0.0, "qqq_cumulative_return": 0.0,
        "equal_weight_cumulative_return": 0.0, "forecast_vol": "", "exposure_mult": 1.0}])

    cont.mkdir(parents=True, exist_ok=True)
    _append_csv(cont / "equity.csv", new_eq)
    if trows:
        _append_csv(cont / "trades.csv", pd.DataFrame(trows))
    pos.to_csv(cont / "positions.csv", index=False)

    seg = {"scenario": scenario, "from": (date.fromisoformat(last_iso) + _dt.timedelta(days=1)).isoformat(),
           "to": mark_iso, "ran_at": now or _dt.datetime.now().isoformat(timespec="seconds"),
           "n_trades": len(trows), "mode": "ramp_up"}
    man["segments"] = man.get("segments", []) + [seg]
    man["live_through"] = mark_iso; man["live_value"] = total
    man["status"] = "living"; man["n_positions"] = len(pos)
    try:
        d2 = rank_report.build_report(scenario, date.fromisoformat(man["inception"]),
                                      date.fromisoformat(mark_iso), cfg=cfg, account=name,
                                      write_snapshot=False, with_intraday=False)
        (d_dir / "reports").mkdir(exist_ok=True)
        (d_dir / "reports" / f"status_{scenario}_{mark_iso}.md").write_text(rank_report.render_md(d2))
        pdf_report.build_pdf(d2, cfg, d_dir / "reports" / f"eod_{scenario}_{mark_iso}.pdf")
    except Exception as exc:
        seg["report_error"] = str(exc)
    man.setdefault("hashes", {})
    for f in sorted(cont.glob("*.csv")):
        man["hashes"][f"continuation/{f.name}"] = _sha256(f)
    for f in sorted((d_dir / "reports").glob("*")):
        man["hashes"][f"reports/{f.name}"] = _sha256(f)
    _manifest_path(name).write_text(json.dumps(man, indent=2))
    return {"noop": False, **seg, "live_through": mark_iso, "live_value": total,
            "segments": len(man["segments"])}


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

    # Ramp-up accounts: instead of mirroring the model, accumulate via the ramp-up queue
    # (buy current-ranking names >= entry_score not held @ size_pct, + the up-shock/vol hedge),
    # marked to `end`. Exits are off during ramp-up (accumulate-only).
    if man.get("ramp_up"):
        return _continue_ramp_up(name, end, man, scenario, d_dir, cont, now)

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
