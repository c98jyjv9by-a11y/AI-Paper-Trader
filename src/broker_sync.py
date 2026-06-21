"""
broker_sync.py — reconciliation, realized-slippage logging, broker→ledger sync, and the
daily session orchestrator that sits on top of broker_adapter (Alpaca paper).

This is the layer that replaces *assumed* fills with the broker's *actual* fills:
  • submit_session()    — build the day's queue, save the decision reference prices, and
                          (optionally, guarded) submit the orders to the paper account.
  • reconcile_session() — pull the broker's actual fills + positions, compute realized
                          slippage vs the saved references, log it, and rewrite the
                          account ledger from the broker (broker = source of truth).
  • slippage_summary()  — aggregate the fills log vs the model's assumed cost.

Pure cores (compute_slippage / ledger_from_broker) are unit-testable without a broker.
Broker calls go through broker_adapter, which is paper-only and submit-guarded.

CLI:
    python src/broker_sync.py --submit-plan --account tracker [--submit]
    python src/broker_sync.py --reconcile  --account tracker
    python src/broker_sync.py --slippage   --account tracker
"""
from __future__ import annotations

import json
import argparse
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

ROOT = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(ROOT / "src"))
import broker_adapter as ba
from account import _append_csv, _sha256, _manifest_path, load_manifest, load_ledger, _acct_dir
ASSUMED_COST_BPS = 10.0    # the flat round-trip cost the backtest assumes (for comparison)


def _broker_dir(name: str) -> Path:
    d = _acct_dir(name) / "broker"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ── pure cores (unit-testable, no broker) ──────────────────────────────────────────
def compute_slippage(fills: List[Dict[str, Any]], refs: Dict[str, float]) -> pd.DataFrame:
    """Realized slippage per fill vs its decision reference price.
    fills: [{client_order_id, symbol, side, filled_qty, fill_price}]; refs: {client_order_id: ref_mid}.
    slippage_bps > 0 means WORSE than the reference (paid up on a buy / sold low on a sell)."""
    rows = []
    for f in fills:
        ref = refs.get(f.get("client_order_id"))
        fp, qty = f.get("fill_price"), f.get("filled_qty") or 0
        if not (ref and fp and qty):
            continue
        sign = 1.0 if f["side"].lower() == "buy" else -1.0
        bps = sign * (fp - ref) / ref * 1e4
        rows.append({"client_order_id": f["client_order_id"], "symbol": f["symbol"],
                     "side": f["side"], "qty": qty, "ref_price": round(ref, 4),
                     "fill_price": round(fp, 4), "slippage_bps": round(bps, 2),
                     "slippage_$": round(sign * (fp - ref) * qty, 2),
                     "filled_at": f.get("filled_at")})
    return pd.DataFrame(rows)


def ledger_from_broker(positions: List[Dict[str, Any]], cash: float, equity: float, asof: str,
                       prior_entry_dates: Optional[Dict[str, str]] = None) -> Dict[str, pd.DataFrame]:
    """Build continuation positions + an equity row from a broker snapshot (broker = truth)."""
    ped = prior_entry_dates or {}
    pos = pd.DataFrame([{
        "ticker": p["ticker"], "shares": p["qty"], "entry_price": p["avg_entry"],
        "entry_date": ped.get(p["ticker"], asof), "current_price": p["price"],
        "highest_price": p["price"], "lowest_price": p["price"]} for p in positions])
    open_val = float(sum(p["market_value"] for p in positions))
    eq = pd.DataFrame([{"date": asof, "cash": cash, "open_positions_value": open_val,
                        "total_portfolio_value": equity, "realized_pnl_to_date": 0.0,
                        "unrealized_pnl": 0.0, "daily_return": "", "cumulative_return": "",
                        "spy_cumulative_return": 0.0, "qqq_cumulative_return": 0.0,
                        "equal_weight_cumulative_return": 0.0, "forecast_vol": "", "exposure_mult": 1.0}])
    return {"positions": pos, "equity": eq}


def submit_window(clk: Dict[str, Any], prequeue: bool = False, far_hours: float = 20.0) -> Dict[str, Any]:
    """Decide whether it's a sensible moment to SEND market-on-open/close orders.
    Pure & testable. Returns {ok, reason}. The intended window is "market closed, next open
    imminent" (evening/pre-open). Blocks when the market is open (MOO/MOC would queue for the
    NEXT session, not today) or when the next open is far away (weekend/holiday) unless prequeue."""
    from datetime import datetime as _dt
    try:
        now = _dt.fromisoformat(clk["timestamp"]); nopen = _dt.fromisoformat(clk["next_open"])
        hrs = (nopen - now).total_seconds() / 3600.0
    except Exception:
        hrs = None
    if clk.get("is_open"):
        return {"ok": bool(prequeue), "reason": "market is OPEN — MOO/MOC queue for the NEXT auction, "
                "not today; run after the close (or --prequeue to queue anyway)."}
    if hrs is not None and hrs > far_hours:
        return {"ok": bool(prequeue), "reason": "next open is %s (~%.0fh away, weekend/holiday) — "
                "submitting this early may be rejected by the broker; use --prequeue to queue deliberately."
                % (clk.get("next_open"), hrs)}
    return {"ok": True, "reason": "market closed, next open imminent — valid pre-open window."}


# ── session steps ──────────────────────────────────────────────────────────────────
def submit_session(name: str, cli: ba.AlpacaPaper = None, submit: bool = False,
                   prequeue: bool = False) -> Dict[str, Any]:
    """Build the day's order plan from the account queue, persist the decision reference
    prices (for later slippage), and optionally submit — guarded by a clock/calendar window."""
    cli = cli or ba.AlpacaPaper()
    clk = cli.clock()
    intended = ba.queue_from_account(name)
    prices = cli.latest_prices([it["ticker"] for it in intended]) if intended else {}
    asof = clk.get("timestamp", datetime.utcnow().isoformat())[:10]
    orders = ba.build_orders(intended, prices, asof)
    refs = {o["client_order_id"]: o["_plan"]["ref_mid"] for o in orders}
    (_broker_dir(name) / f"plan_{asof}.json").write_text(json.dumps(
        {"asof": asof, "refs": refs, "orders": [{k: v for k, v in o.items() if not k.startswith("_")}
                                                 for o in orders]}, indent=2))
    win = submit_window(clk, prequeue)
    if submit and not win["ok"]:
        return {"asof": asof, "n_orders": len(orders), "submitted": 0, "dry_run": True,
                "blocked": True, "reason": win["reason"], "orders": orders}
    results = []
    for o in orders:
        payload = {k: v for k, v in o.items() if not k.startswith("_")}
        results.append(cli.submit(payload, confirm=submit))
    sent = sum(1 for r in results if not r.get("dry_run"))
    return {"asof": asof, "n_orders": len(orders), "submitted": sent,
            "dry_run": sent == 0, "window": win["reason"], "orders": orders}


def reconcile_session(name: str, cli: ba.AlpacaPaper = None) -> Dict[str, Any]:
    """Pull the broker's actual fills + positions; log realized slippage vs the saved plan
    references; rewrite the account's continuation ledger from the broker (source of truth)."""
    cli = cli or ba.AlpacaPaper()
    asof = cli.clock().get("timestamp", datetime.utcnow().isoformat())[:10]
    bdir = _broker_dir(name)

    # merge all saved plan refs (so fills match their decision prices)
    refs: Dict[str, float] = {}
    for pf in bdir.glob("plan_*.json"):
        refs.update(json.loads(pf.read_text()).get("refs", {}))

    fills = [o for o in cli.orders(status="closed") if o["status"] == "filled" and o["fill_price"]]
    slip = compute_slippage(fills, refs)
    if not slip.empty:
        _append_csv(bdir / "fills.csv", slip)

    # rewrite the ledger from the broker snapshot
    acct = cli.account()
    prior = {p["ticker"]: p.get("entry_date") for _, p in load_ledger(name)["positions"].iterrows()} \
        if len(load_ledger(name)["positions"]) else {}
    snap = ledger_from_broker(cli.positions(), acct["cash"], acct["equity"], asof, prior)
    cont = _acct_dir(name) / "continuation"; cont.mkdir(exist_ok=True)
    _append_csv(cont / "equity.csv", snap["equity"])
    snap["positions"].to_csv(cont / "positions.csv", index=False)

    man = load_manifest(name)
    man["live_through"] = asof; man["live_value"] = acct["equity"]; man["status"] = "living"
    man["n_positions"] = len(snap["positions"]); man["broker"] = "alpaca_paper"
    man.setdefault("hashes", {})
    for f in sorted(cont.glob("*.csv")):
        man["hashes"][f"continuation/{f.name}"] = _sha256(f)
    _manifest_path(name).write_text(json.dumps(man, indent=2))

    return {"asof": asof, "fills": int(len(slip)),
            "avg_slippage_bps": float(slip["slippage_bps"].mean()) if not slip.empty else None,
            "equity": acct["equity"], "positions": len(snap["positions"])}


def slippage_summary(name: str) -> Dict[str, Any]:
    """Aggregate the realized-slippage fills log and compare to the model's assumed cost."""
    f = _broker_dir(name) / "fills.csv"
    if not f.exists():
        return {"note": "no fills logged yet"}
    df = pd.read_csv(f)
    by_sym = df.groupby("symbol")["slippage_bps"].mean().round(1).to_dict()
    return {"n_fills": len(df), "avg_slippage_bps": round(df["slippage_bps"].mean(), 2),
            "median_bps": round(df["slippage_bps"].median(), 2),
            "total_slippage_$": round(df["slippage_$"].sum(), 2),
            "assumed_bps": ASSUMED_COST_BPS, "by_symbol": by_sym}


# ── CLI ─────────────────────────────────────────────────────────────────────────────
def _cli(argv=None):
    p = argparse.ArgumentParser(description="Broker reconciliation / slippage / ledger sync")
    p.add_argument("--account", required=True)
    p.add_argument("--submit-plan", action="store_true", help="build + save the order plan")
    p.add_argument("--submit", action="store_true", help="actually send (needs BROKER_ADAPTER_ALLOW_SUBMIT=yes)")
    p.add_argument("--prequeue", action="store_true", help="allow submitting outside the pre-open window (weekend/holiday)")
    p.add_argument("--reconcile", action="store_true", help="pull fills, log slippage, sync ledger from broker")
    p.add_argument("--slippage", action="store_true", help="print realized-slippage summary")
    a = p.parse_args(argv)
    if a.submit_plan:
        r = submit_session(a.account, submit=a.submit, prequeue=a.prequeue)
        if r.get("blocked"):
            print("PLAN %s: %d orders — NOT submitted. %s" % (r["asof"], r["n_orders"], r["reason"]))
        else:
            print("PLAN %s: %d orders, %s" % (r["asof"], r["n_orders"],
                  "DRY-RUN (nothing sent)" if r["dry_run"] else f"{r['submitted']} submitted"))
    if a.reconcile:
        r = reconcile_session(a.account)
        print("RECONCILED %s: %d fills, avg slippage %s bps, equity $%,.0f, %d positions" % (
            r["asof"], r["fills"], r["avg_slippage_bps"], r["equity"], r["positions"]))
    if a.slippage:
        print("SLIPPAGE SUMMARY:", json.dumps(slippage_summary(a.account), indent=2))


if __name__ == "__main__":
    _cli()
