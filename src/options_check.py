"""
options_check.py — READ-ONLY dry-run for the options scaffolding (the cheap proof-of-life).

Two modes, neither writes any ledger / plan / decision file (unlike submit_session):

  • --account <name>   : for a configured options book, build the contract-keyed dry-run plan exactly
                         as the EOD path would (select underlyings → candidate chain → strategy leaf →
                         size by premium×100 → day-TIF marketable-limit orders), and print it.
  • --underlyings A,B  : ad-hoc chain preview for arbitrary underlyings using a default selection
                         config — proves out auth + contract enumeration + snapshot data quality
                         before any account exists.

Exercises every live dependency (Alpaca auth, /v2/options/contracts, options snapshots/quotes) with
zero side effects, so you learn whether the data feed is usable before building the durable paths.

CLI:
    python src/options_check.py --account opt_directional10
    python src/options_check.py --underlyings SPY,QQQ --right call
"""
from __future__ import annotations

import argparse
import datetime as _dt
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

import broker_adapter as ba
import broker_sync as bs
import options_symbols as osym
from account import load_manifest


def _default_ocfg() -> Dict[str, Any]:
    return {"level": 2, "underlyings": "scenario", "expiry_window_days": [25, 45], "roll_dte": 7,
            "moneyness": [-0.05, 0.05], "min_open_interest": 500, "max_spread_pct": 0.10,
            "feed": "indicative"}


def _print_orders(orders: List[Dict[str, Any]]) -> None:
    if not orders:
        print("    (no orders — already at target / no usable candidates)")
        return
    for o in orders:
        pl = o["_plan"]
        print("    %-4s %-22s qty %-4s  day limit $%-8.2f  spread %.0f%%  (tgt %d / now %d)  ~$%-9.0f"
              % (o["side"].upper(), osym.occ_label(o["symbol"]), o["qty"], o["limit_price"],
                 pl["collar"] * 100, pl["target"], pl["current"], pl["est_value"]))


def _check_account(name: str) -> None:
    cli = ba.AlpacaPaper(account=name)
    man = load_manifest(name) or {}
    if not bs._is_options_account(man):
        print("  %s: NOT an options account (target_mode.kind != options) — skipping" % name)
        return
    acct = cli.account()
    need = int((man.get("options") or {}).get("level", 1))
    have = int(acct.get("options_trading_level") or 0)
    lvl = "OK" if have >= need else "TOO LOW — enable in Alpaca dashboard"
    print("  {}: equity ${:,.0f}  options level have={} need={} ({})".format(
        name, acct.get("equity", 0), have, need, lvl))
    current = {p["ticker"]: p["qty"] for p in cli.positions()
               if p.get("asset_class") == "us_option" or osym.is_occ(p["ticker"])}
    targets, _refs, dec = bs.compute_targets(name, cli, current)
    delta = sorted({s for s in set(targets) | set(current)
                    if int(round(targets.get(s, 0))) != int(round(current.get(s, 0)))})
    quotes = cli.option_quotes(delta, feed=(man.get("options") or {}).get("feed", "indicative")) if delta else {}
    asof = cli.clock().get("timestamp", bs._utcnow())[:10]
    orders = ba.build_option_reconcile_orders(targets, current, quotes, asof,
                                              spread_pct=float((man.get("options") or {}).get("max_spread_pct", 0.10)))
    print("    DRY-RUN PLAN — %d order(s), nothing sent:" % len(orders))
    _print_orders(orders)
    for occ, info in dec.items():
        if occ not in targets:                       # roll/exit reasons for held contracts leaving the book
            print("    · %-22s %s" % (osym.occ_label(occ), info.get("reason", "")))


def _check_underlyings(unders: List[str], right: str, equity: float) -> None:
    cli = ba.AlpacaPaper()                            # default keys
    ocfg = _default_ocfg()
    print("  ad-hoc preview: %s  (right=%s, DTE %s, OI>=%d)"
          % (",".join(unders), right, ocfg["expiry_window_days"], ocfg["min_open_interest"]))
    cands = bs._option_candidates(cli, unders, ocfg, _dt.date.today())
    if not cands:
        print("    (no candidate contracts returned — check auth / data subscription / filters)")
        return
    picks = bs._options_strategy_targets("long_directional", cands,
                                         {"right": right, "strategy": "long_directional"})
    per = 0.30 * equity / max(len(picks), 1)
    print("    %d candidates across %d underlyings; ATM picks:" % (len(cands), len({c['underlying'] for c in cands})))
    for c in sorted(picks, key=lambda x: x["underlying"]):
        contracts = int(per / (c["mid"] * 100)) if c["mid"] > 0 else 0
        iv = ("%.0f%%" % (c["iv"] * 100)) if c.get("iv") else "—"
        dl = ("%.2f" % c["delta"]) if c.get("delta") is not None else "—"
        print("    {:<22} mid ${:<7.2f} IV {:<5} Δ {:<5} OI {:<6d} -> {} contract(s) (~${:,.0f})".format(
            osym.occ_label(c["occ"]), c["mid"], iv, dl, c["oi"], contracts, contracts * c["mid"] * 100))


def run(accounts: Optional[List[str]] = None, underlyings: Optional[str] = None,
        right: str = "call", equity: float = 100000.0) -> None:
    print("=== OPTIONS CHECK — %s (read-only, nothing sent) ===" % _dt.date.today())
    if underlyings:
        _check_underlyings([s.strip().upper() for s in underlyings.split(",")], right, equity)
        return
    accts = accounts or [m.parent.name for m in (ROOT / "accounts").glob("*/manifest.json")
                         if bs._is_options_account(load_manifest(m.parent.name))]
    if not accts:
        print("  no options accounts found. Pass --underlyings SPY,QQQ for an ad-hoc preview,")
        print("  or create one: broker_sync.py --create-account --target-mode options ...")
        return
    for name in accts:
        try:
            _check_account(name)
        except Exception as exc:
            print("  %s: ERROR — %s" % (name, exc))


def _cli(argv=None):
    p = argparse.ArgumentParser(description="Read-only options scaffolding dry-run (no writes)")
    p.add_argument("--account", help="options account name (repeatable via --accounts)")
    p.add_argument("--accounts", nargs="+", help="multiple options account names")
    p.add_argument("--underlyings", help="ad-hoc preview: comma-separated underlyings (no account needed)")
    p.add_argument("--right", default="call", choices=["call", "put", "both"], help="contract right (ad-hoc)")
    p.add_argument("--equity", type=float, default=100000.0, help="equity for ad-hoc sizing (default 100k)")
    a = p.parse_args(argv)
    accts = a.accounts or ([a.account] if a.account else None)
    run(accts, a.underlyings, a.right, a.equity)


if __name__ == "__main__":
    _cli()
