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
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

ROOT = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(ROOT / "src"))
import broker_adapter as ba
from account import _append_csv, _sha256, _manifest_path, load_manifest, load_ledger, _acct_dir
ASSUMED_COST_BPS = 10.0    # the flat round-trip cost the backtest assumes (for comparison)
HEDGE_SYM = "SOXS"         # the only hedge instrument (long inverse ETF; never shorted)
COLLAR_CACHE = ROOT / "backtests" / "collars.csv"


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


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


# ── data-driven execution collars (per-instrument limit tolerance) ──────────────────
def collars_from_gaps(gaps: Dict[str, "pd.Series"], p_base: float = 0.85, p_retry: float = 0.95,
                      floor: float = 0.0015, cap: float = 0.20) -> Dict[str, Dict[str, float]]:
    """PURE. Map {symbol: overnight-gap series (open/prevclose-1)} -> per-symbol collars.
      collar = clamp(P85(|gap|), floor, cap)   retry = clamp(P95(|gap|), floor, cap)
    A buy-limit at ref*(1+collar) fills on ~85% of normal opens and deliberately skips the worst
    ~15% (the adverse gaps we don't want to chase). `floor` covers the bid-ask on calm names."""
    out: Dict[str, Dict[str, float]] = {}
    for s, g in gaps.items():
        g = g.dropna().abs()
        if len(g) < 50:                       # not enough history -> safe default
            out[s] = {"collar": 0.02, "retry": 0.04, "n": int(len(g)), "src": "default"}
            continue
        out[s] = {"collar": round(float(min(max(g.quantile(p_base), floor), cap)), 4),
                  "retry": round(float(min(max(g.quantile(p_retry), floor), cap)), 4),
                  "n": int(len(g)), "src": "data"}
    return out


def compute_collars(symbols: List[str], cache_day: Optional[str] = None) -> Dict[str, Dict[str, float]]:
    """Fetch ~2y of opens/closes, derive per-symbol collars, and cache to backtests/collars.csv.
    Re-uses today's cache if present (one refresh per day) so submit/retry stay consistent."""
    symbols = sorted(set(symbols))
    if not symbols:
        return {}
    today = cache_day or _utcnow()[:10]
    if COLLAR_CACHE.exists():                 # same-day cache hit (covering all requested syms)
        c = pd.read_csv(COLLAR_CACHE)
        if str(c.get("asof", pd.Series([""])).iloc[0]) == today and set(symbols) <= set(c["symbol"]):
            c = c[c["symbol"].isin(symbols)].set_index("symbol")
            return {s: {"collar": float(r["collar"]), "retry": float(r["retry"]),
                        "n": int(r["n"]), "src": r["src"]} for s, r in c.iterrows()}
    import yfinance as yf
    px = yf.download(symbols, period="2y", auto_adjust=True, progress=False)
    op, cl = px["Open"], px["Close"]
    gaps = {s: (op[s] / cl[s].shift(1) - 1) for s in symbols
            if (s in getattr(op, "columns", [])) or (len(symbols) == 1)}
    if len(symbols) == 1:                     # yfinance returns a flat frame for one symbol
        gaps = {symbols[0]: (op / cl.shift(1) - 1)}
    cols = collars_from_gaps(gaps)
    df = pd.DataFrame([{"asof": today, "symbol": s, **v} for s, v in cols.items()])
    COLLAR_CACHE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(COLLAR_CACHE, index=False)
    return cols


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


# ── target book (reconcile-to-target) ───────────────────────────────────────────────
def compute_targets(name: str, cli: ba.AlpacaPaper,
                    current: Optional[Dict[str, float]] = None) -> "tuple[Dict[str,int], Dict[str,float]]":
    """TARGET book {symbol: shares} for the next session, computed from the broker's actual book:
        • hold every current NON-hedge position (ramp-up is accumulate-only),
        • add ramp-up entries (>0.9 names not yet held) at their queued size,
        • set the hedge to its recommended size (0 if the signal isn't firing).
    Diffing this vs the broker's current positions rolls the 1-day hedge and never re-buys held
    names. Returns (targets, ref_prices)."""
    current = current if current is not None else {p["ticker"]: p["qty"] for p in cli.positions()}
    q = ba.queue_from_account(name)
    targets: Dict[str, int] = {t: int(round(s)) for t, s in current.items() if t != HEDGE_SYM}
    refs: Dict[str, float] = {}
    hedge_seen = False
    for it in q:
        sym, px = it["ticker"], it.get("price")
        sh = int(round(it.get("shares") or 0))
        if px:
            refs[sym] = px
        if sym == HEDGE_SYM:
            targets[HEDGE_SYM] = sh; hedge_seen = True
        elif it.get("action", "BUY").upper() == "BUY":
            targets[sym] = int(round(current.get(sym, 0))) + sh    # held -> add; new -> shares
        else:                                                       # SELL / model exit
            targets[sym] = 0
    if not hedge_seen:
        targets[HEDGE_SYM] = 0                                      # hedge off -> flatten any hedge
    return targets, refs


# ── session steps ──────────────────────────────────────────────────────────────────
def submit_session(name: str, cli: ba.AlpacaPaper = None, submit: bool = False,
                   prequeue: bool = False, retry: bool = False) -> Dict[str, Any]:
    """Build the day's RECONCILE-TO-TARGET plan (limit orders with data-driven per-symbol collars),
    persist the decision references + collars (for slippage & the retry pass), and optionally submit
    — guarded by a clock/calendar window. `retry=True` rebuilds unfilled deltas at the wider collar."""
    cli = cli or ba.AlpacaPaper()
    clk = cli.clock()
    asof = clk.get("timestamp", _utcnow())[:10]
    current = {p["ticker"]: p["qty"] for p in cli.positions()}
    targets, _refpx = compute_targets(name, cli, current)
    delta_syms = sorted({s for s in set(targets) | set(current)
                         if int(round(targets.get(s, 0))) != int(round(current.get(s, 0)))})
    prices = cli.latest_prices(delta_syms) if delta_syms else {}
    collars = compute_collars(delta_syms, cache_day=asof)
    orders = ba.build_reconcile_orders(targets, current, prices, collars, asof, retry=retry)
    refs = {o["client_order_id"]: o["_plan"]["ref_mid"] for o in orders}
    (_broker_dir(name) / f"plan_{asof}.json").write_text(json.dumps(
        {"asof": asof, "retry": retry, "refs": refs,
         "collars": {s: collars.get(s, {}) for s in delta_syms},
         "orders": [{k: v for k, v in o.items() if not k.startswith("_")} for o in orders],
         "detail": [dict(symbol=o["symbol"], side=o["side"], qty=o["qty"],
                         limit_price=o["limit_price"], **o["_plan"]) for o in orders]}, indent=2))
    win = submit_window(clk, prequeue)
    if submit and not win["ok"]:
        return {"asof": asof, "n_orders": len(orders), "submitted": 0, "dry_run": True,
                "blocked": True, "reason": win["reason"], "orders": orders}
    results = [cli.submit({k: v for k, v in o.items() if not k.startswith("_")}, confirm=submit)
               for o in orders]
    sent = sum(1 for r in results if not r.get("dry_run"))
    return {"asof": asof, "n_orders": len(orders), "submitted": sent,
            "dry_run": sent == 0, "window": win["reason"], "orders": orders}


def retry_unfilled(name: str, cli: ba.AlpacaPaper = None) -> Dict[str, Any]:
    """RETRY-ONCE-WIDER: cancel any still-open limit orders from today's plan and resubmit the
    remaining delta at each symbol's wider retry collar; anything still unfilled after this is
    SKIPPED (logged). Call once, after the first plan has had time to work."""
    cli = cli or ba.AlpacaPaper()
    asof = cli.clock().get("timestamp", _utcnow())[:10]
    open_orders = [o for o in cli.orders(status="open")]
    todays = [o for o in open_orders if (o.get("client_order_id") or "").startswith(f"mv4-{asof}-")]
    for o in todays:                                   # cancel the unfilled first attempt
        cli.cancel(o["id"]) if hasattr(cli, "cancel") else None
    res = submit_session(name, cli=cli, submit=True, prequeue=False, retry=True)
    # record what got skipped (still no position vs target) for honesty
    targets, _ = compute_targets(name, cli)
    current = {p["ticker"]: p["qty"] for p in cli.positions()}
    skipped = [{"asof": asof, "symbol": s, "target": int(round(targets.get(s, 0))),
                "current": int(round(current.get(s, 0)))}
               for s in sorted(set(targets) | set(current))
               if int(round(targets.get(s, 0))) != int(round(current.get(s, 0)))]
    if skipped:
        _append_csv(_broker_dir(name) / "skips.csv", pd.DataFrame(skipped))
    return {"asof": asof, "canceled": len(todays), "resubmitted": res["n_orders"],
            "still_unfilled": len(skipped)}


def create_broker_account(name: str, scenario: str = "model_v4", starting: float = 100000.0,
                          ramp_up: Optional[Dict[str, Any]] = None, asof: Optional[str] = None) -> Dict[str, Any]:
    """Create a fresh broker-driven account: an empty frozen ledger (cash only, no positions) that
    reconcile_session() then drives forward from the real Alpaca fills (broker = source of truth)."""
    d = _acct_dir(name); d.mkdir(parents=True, exist_ok=True)
    asof = asof or _utcnow()[:10]
    pd.DataFrame(columns=["date", "action", "ticker", "shares", "price", "trade_value", "reason",
                          "realized_pnl", "holding_days", "entry_price", "highest_price",
                          "lowest_price"]).to_csv(d / "trades.csv", index=False)
    pd.DataFrame([{"date": asof, "cash": starting, "open_positions_value": 0.0,
                   "total_portfolio_value": starting, "realized_pnl_to_date": 0.0,
                   "unrealized_pnl": 0.0, "daily_return": 0.0, "cumulative_return": 0.0,
                   "spy_cumulative_return": 0.0, "qqq_cumulative_return": 0.0,
                   "equal_weight_cumulative_return": 0.0, "forecast_vol": "",
                   "exposure_mult": 1.0}]).to_csv(d / "equity.csv", index=False)
    pd.DataFrame(columns=["ticker", "shares", "entry_price", "entry_date", "current_price",
                          "highest_price", "lowest_price"]).to_csv(d / "positions.csv", index=False)
    man = {"name": name, "scenario": scenario, "status": "frozen", "inception": asof,
           "frozen_through": asof, "live_through": asof, "starting_value": starting,
           "ending_value": starting, "total_return": 0.0, "n_trades": 0, "n_positions": 0,
           "broker": "alpaca_paper",
           "ramp_up": ramp_up or {"entry_score": 0.9, "entry_size_pct": 0.085, "hedge": True},
           "hashes": {}}
    for f in ["trades.csv", "equity.csv", "positions.csv"]:
        man["hashes"][f] = _sha256(d / f)
    _manifest_path(name).write_text(json.dumps(man, indent=2))
    return man


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
    p.add_argument("--retry", action="store_true", help="cancel unfilled orders + resubmit at the wider retry collar")
    p.add_argument("--create-account", action="store_true", help="create a fresh broker-driven ramp-up account")
    a = p.parse_args(argv)
    if a.create_account:
        man = create_broker_account(a.account)
        print("CREATED broker account '%s' (scenario=%s, $%s cash, ramp_up entry>=%.2f). "
              "Broker now drives the ledger via --reconcile." % (
              man["name"], man["scenario"], format(int(man["starting_value"]), ","),
              man["ramp_up"]["entry_score"]))
    if a.submit_plan:
        r = submit_session(a.account, submit=a.submit, prequeue=a.prequeue)
        if r.get("blocked"):
            print("PLAN %s: %d orders — NOT submitted. %s" % (r["asof"], r["n_orders"], r["reason"]))
        else:
            print("PLAN %s: %d orders, %s" % (r["asof"], r["n_orders"],
                  "DRY-RUN (nothing sent)" if r["dry_run"] else f"{r['submitted']} submitted"))
        for o in r.get("orders", []):
            pl = o["_plan"]
            print("  %-4s %-6s qty %-5s  limit $%-8.2f  collar %.1f%%  (tgt %d / now %d)  ~$%-8.0f" % (
                o["side"].upper(), o["symbol"], o["qty"], o["limit_price"], pl["collar"] * 100,
                pl["target"], pl["current"], pl["est_value"]))
    if a.retry:
        r = retry_unfilled(a.account)
        print("RETRY %s: canceled %d, resubmitted %d, still unfilled %d" % (
            r["asof"], r["canceled"], r["resubmitted"], r["still_unfilled"]))
    if a.reconcile:
        r = reconcile_session(a.account)
        print(f"RECONCILED {r['asof']}: {r['fills']} fills, avg slippage {r['avg_slippage_bps']} bps, "
              f"equity ${r['equity']:,.0f}, {r['positions']} positions")
    if a.slippage:
        print("SLIPPAGE SUMMARY:", json.dumps(slippage_summary(a.account), indent=2))


if __name__ == "__main__":
    _cli()
