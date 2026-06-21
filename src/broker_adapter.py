"""
broker_adapter.py — Alpaca *paper* broker adapter (SCAFFOLD: read-only + dry-run).

This is the bridge from simulated marks to real broker mechanics (actual fills, timing,
bid/ask, slippage). It is deliberately SAFE by default:

  • Hardwired to the Alpaca PAPER endpoint only — it refuses any non-paper host.
  • Read-only calls (account / positions / quotes / clock) need just API keys.
  • Order submission is INERT unless you double-opt-in: pass confirm=True AND set the
    env var BROKER_ADAPTER_ALLOW_SUBMIT=yes. Otherwise build_orders() only PLANS.

Keys come from the gitignored .env (never commit them):
    APCA_API_KEY_ID=...        APCA_API_SECRET_KEY=...

Order mapping to the strategy's timing:
  • entries (decide-at-close → fill-next-open)  -> market-on-open  (time_in_force "opg")
  • hedge exit (1-day, exit next close)         -> market-on-close (time_in_force "cls")
  (opg/cls require whole-share qty, so dollar sizes are converted via the latest price.)

CLI:
    python src/broker_adapter.py --status                  # account + positions (read-only)
    python src/broker_adapter.py --plan --account tracker  # dry-run order plan from the queue
    python src/broker_adapter.py --plan --account tracker --submit   # actually send (guarded)
"""
from __future__ import annotations

import os
import sys
import json
import argparse
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).parent.parent
PAPER_HOST = "https://paper-api.alpaca.markets"      # the ONLY trading host this adapter allows
DATA_HOST = "https://data.alpaca.markets"
SUBMIT_ENV = "BROKER_ADAPTER_ALLOW_SUBMIT"          # must equal "yes" to permit live paper orders


def _load_env() -> None:
    """Load .env (gitignored) into os.environ if present — no extra dependency."""
    f = ROOT / ".env"
    if not f.exists():
        return
    for line in f.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line and "(" not in line.split("=", 1)[0]:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


class AlpacaPaper:
    """Thin Alpaca paper-API client (read-only by default)."""

    def __init__(self, key: Optional[str] = None, secret: Optional[str] = None,
                 host: str = PAPER_HOST):
        if host != PAPER_HOST:
            raise ValueError(f"refusing non-paper host {host!r}; this adapter is paper-only.")
        _load_env()
        self.key = key or os.environ.get("APCA_API_KEY_ID")
        self.secret = secret or os.environ.get("APCA_API_SECRET_KEY")
        if not (self.key and self.secret):
            raise RuntimeError("Missing Alpaca keys — set APCA_API_KEY_ID / APCA_API_SECRET_KEY in .env")
        self.host = host
        try:
            import requests  # noqa: F401
        except ImportError as e:
            raise RuntimeError("broker_adapter needs `requests` (pip install requests)") from e

    @property
    def _hdr(self) -> Dict[str, str]:
        return {"APCA-API-KEY-ID": self.key, "APCA-API-SECRET-KEY": self.secret}

    def _get(self, url: str, params: Optional[dict] = None) -> Any:
        import requests
        r = requests.get(url, headers=self._hdr, params=params, timeout=20)
        r.raise_for_status()
        return r.json()

    # ── read-only ────────────────────────────────────────────────────────────────
    def account(self) -> Dict[str, Any]:
        a = self._get(f"{self.host}/v2/account")
        return {"status": a.get("status"), "cash": float(a.get("cash", 0)),
                "equity": float(a.get("equity", 0)), "buying_power": float(a.get("buying_power", 0)),
                "is_paper": True, "blocked": a.get("trading_blocked")}

    def positions(self) -> List[Dict[str, Any]]:
        return [{"ticker": p["symbol"], "qty": float(p["qty"]),
                 "avg_entry": float(p["avg_entry_price"]),
                 "price": float(p["current_price"]), "market_value": float(p["market_value"]),
                 "unrealized_plpc": float(p.get("unrealized_plpc", 0))}
                for p in self._get(f"{self.host}/v2/positions")]

    def latest_prices(self, symbols: List[str]) -> Dict[str, Dict[str, float]]:
        """Latest bid/ask/mid per symbol (for sizing + slippage measurement)."""
        if not symbols:
            return {}
        q = self._get(f"{DATA_HOST}/v2/stocks/quotes/latest",
                      {"symbols": ",".join(sorted(set(symbols)))}).get("quotes", {})
        out = {}
        for s, v in q.items():
            bid, ask = float(v.get("bp", 0)), float(v.get("ap", 0))
            mid = (bid + ask) / 2 if (bid and ask) else (ask or bid)
            out[s] = {"bid": bid, "ask": ask, "mid": mid}
        return out

    def clock(self) -> Dict[str, Any]:
        return self._get(f"{self.host}/v2/clock")

    def orders(self, status: str = "closed", after: Optional[str] = None,
               limit: int = 500) -> List[Dict[str, Any]]:
        """Recent orders (default closed/filled) with actual fill price & time, for reconciliation."""
        params = {"status": status, "limit": limit, "direction": "desc", "nested": "false"}
        if after:
            params["after"] = after
        out = []
        for o in self._get(f"{self.host}/v2/orders", params):
            fp = o.get("filled_avg_price")
            out.append({"id": o.get("id"), "client_order_id": o.get("client_order_id"), "symbol": o["symbol"],
                        "side": o["side"], "status": o["status"],
                        "filled_qty": float(o.get("filled_qty") or 0),
                        "fill_price": float(fp) if fp else None,
                        "submitted_at": o.get("submitted_at"), "filled_at": o.get("filled_at")})
        return out

    # ── orders (guarded) ──────────────────────────────────────────────────────────
    def submit(self, order: Dict[str, Any], *, confirm: bool = False) -> Dict[str, Any]:
        """Submit ONE order to the paper endpoint. Inert unless confirm=True AND
        env BROKER_ADAPTER_ALLOW_SUBMIT=yes. Returns the broker response or a dry-run note."""
        allowed = confirm and os.environ.get(SUBMIT_ENV, "").lower() == "yes"
        if not allowed:
            return {"dry_run": True, "would_submit": order,
                    "why": f"submission disabled (need confirm=True and {SUBMIT_ENV}=yes)"}
        import requests
        r = requests.post(f"{self.host}/v2/orders", headers=self._hdr, json=order, timeout=20)
        if not r.ok:
            # Surface Alpaca's JSON reason instead of a bare status code. The most common 422
            # here is a duplicate client_order_id — i.e. this order was already submitted today
            # (client_order_id is idempotent per day/side/symbol), so re-running the same plan
            # the same day is rejected by design rather than double-submitting.
            raise requests.HTTPError(
                f"Alpaca rejected {order.get('side')} {order.get('qty')} {order.get('symbol')} "
                f"(HTTP {r.status_code}): {r.text}", response=r)
        return r.json()

    def cancel(self, order_id: str, *, confirm: bool = True) -> Dict[str, Any]:
        """Cancel ONE open order (paper). Guarded like submit (needs BROKER_ADAPTER_ALLOW_SUBMIT=yes)."""
        if not (confirm and os.environ.get(SUBMIT_ENV, "").lower() == "yes"):
            return {"dry_run": True, "would_cancel": order_id}
        import requests
        r = requests.delete(f"{self.host}/v2/orders/{order_id}", headers=self._hdr, timeout=20)
        return {"canceled": order_id, "status": r.status_code}


# ── order building (pure / dry-run) ────────────────────────────────────────────────
def build_orders(intended: List[Dict[str, Any]], prices: Dict[str, Dict[str, float]],
                 asof: str) -> List[Dict[str, Any]]:
    """Turn strategy trades into Alpaca order payloads. Each intended item:
        {action: BUY|SELL, ticker, shares?|value?, role: entry|hedge_exit|exit}
    Entries -> market-on-open (opg); hedge exits / exits -> market-on-close (cls).
    Dollar `value` is converted to whole shares via the latest mid (opg/cls need integer qty)."""
    orders = []
    for it in intended:
        sym = it["ticker"]; side = it["action"].lower()
        role = it.get("role", "entry")
        px = (prices.get(sym) or {}).get("mid") or it.get("price") or 0.0
        qty = int(it["shares"]) if it.get("shares") else (int(it["value"] / px) if (it.get("value") and px) else 0)
        if qty <= 0:
            continue
        tif = "cls" if role in ("hedge_exit", "exit") else "opg"   # MOC for exits, MOO for entries
        orders.append({
            "symbol": sym, "qty": str(qty), "side": side, "type": "market",
            "time_in_force": tif,
            "client_order_id": f"mv4-{asof}-{side}-{sym}",          # idempotent per day/side/symbol
            "_plan": {"role": role, "ref_mid": px, "est_value": round(qty * px, 2)},
        })
    return orders


def build_reconcile_orders(targets: Dict[str, float], current: Dict[str, float],
                           prices: Dict[str, Dict[str, float]], collars: Dict[str, Dict[str, float]],
                           asof: str, retry: bool = False) -> List[Dict[str, Any]]:
    """RECONCILE-TO-TARGET: trade only the difference between the target book {sym:shares} and the
    broker's current {sym:shares}, as LIMIT orders with a per-symbol collar (tif=day).
      buy limit  = ref_mid * (1 + collar)      sell limit = ref_mid * (1 - collar)
    `retry=True` uses each symbol's wider retry collar. This nets the hedge roll and never
    re-buys names already held."""
    orders = []
    for s in sorted(set(targets) | set(current)):
        tgt, cur = int(round(targets.get(s, 0))), int(round(current.get(s, 0)))
        delta = tgt - cur
        ref = (prices.get(s) or {}).get("mid") or 0.0
        if delta == 0 or not ref:
            continue
        coll = (collars.get(s) or {}).get("retry" if retry else "collar", 0.02)
        side = "buy" if delta > 0 else "sell"
        lim = ref * (1 + coll) if side == "buy" else ref * (1 - coll)
        # First attempt: LIMIT-ON-OPEN (buy) / LIMIT-ON-CLOSE (sell) — targets the next auction, so
        # it can be pre-staged (incl. weekend via --prequeue) and fills at the open within the collar.
        # Retry pass: a plain DAY limit — an intraday working order at the wider collar.
        tif = "day" if retry else ("opg" if side == "buy" else "cls")
        orders.append({"symbol": s, "qty": str(abs(delta)), "side": side, "type": "limit",
                       "limit_price": round(lim, 2), "time_in_force": tif,
                       "client_order_id": f"mv4-{asof}-{side}-{s}",
                       "_plan": {"ref_mid": ref, "collar": coll, "target": tgt, "current": cur,
                                 "tif": tif, "est_value": round(abs(delta) * ref, 2)}})
    return orders


def reconcile(intended_book: Dict[str, float], broker_positions: List[Dict[str, Any]]) -> List[str]:
    """Compare a target {ticker: shares} book vs the broker's actual positions; report diffs."""
    have = {p["ticker"]: p["qty"] for p in broker_positions}
    lines, names = [], sorted(set(intended_book) | set(have))
    for t in names:
        want, got = intended_book.get(t, 0.0), have.get(t, 0.0)
        if abs(want - got) > 1e-6:
            lines.append(f"  {t}: target {want:g} vs broker {got:g}  (Δ {want-got:+g})")
    return lines or ["  (book matches broker)"]


def queue_from_account(name: str) -> List[Dict[str, Any]]:
    """Pull the account's queued trades (ramp-up/model buys + hedge) from the report layer."""
    sys.path.insert(0, str(ROOT / "src"))
    import rank_report
    from scenarios import build_config, load_scenario
    from backtest import load_config
    from account import load_manifest
    man = load_manifest(name)
    cfg = build_config(load_config(ROOT / "config"), load_scenario(man["scenario"]))
    d = rank_report.build_report(man["scenario"], date.fromisoformat(man["inception"]),
                                 date.fromisoformat(man.get("live_through", man["frozen_through"])),
                                 cfg=cfg, account=name, write_snapshot=False, with_intraday=False)
    ns = d.get("next_session") or {}
    out = []
    for b in ns.get("buys") or []:
        out.append({"action": "BUY", "ticker": b["ticker"], "shares": b.get("shares"),
                    "value": b.get("value"), "role": "entry", "price": b.get("price")})
    for s in ns.get("sells") or []:
        out.append({"action": "SELL", "ticker": s["ticker"], "shares": s.get("shares"),
                    "role": "exit", "price": s.get("price")})
    return out


# ── CLI ─────────────────────────────────────────────────────────────────────────────
def _cli(argv=None):
    p = argparse.ArgumentParser(description="Alpaca paper adapter (read-only + dry-run scaffold)")
    p.add_argument("--status", action="store_true", help="print paper account + positions")
    p.add_argument("--plan", action="store_true", help="build a dry-run order plan from an account's queue")
    p.add_argument("--account", help="account name to source the queue from (e.g. tracker)")
    p.add_argument("--submit", action="store_true", help="actually send orders (also needs %s=yes)" % SUBMIT_ENV)
    a = p.parse_args(argv)

    cli = AlpacaPaper()
    if a.status or not (a.plan):
        acct = cli.account()
        print(f"PAPER ACCOUNT  status={acct['status']}  equity=${acct['equity']:,.0f}  "
              f"cash=${acct['cash']:,.0f}  buying_power=${acct['buying_power']:,.0f}")
        pos = cli.positions()
        print("positions (%d):" % len(pos))
        for q in sorted(pos, key=lambda x: -x["market_value"]):
            print("  %-6s %8.2f sh  @ $%-9.2f  = $%-10.0f  (%+.1f%%)"
                  % (q["ticker"], q["qty"], q["price"], q["market_value"], q["unrealized_plpc"] * 100))

    if a.plan:
        if not a.account:
            print("--plan needs --account"); return
        intended = queue_from_account(a.account)
        prices = cli.latest_prices([it["ticker"] for it in intended])
        asof = cli.clock().get("timestamp", datetime.utcnow().isoformat())[:10]
        orders = build_orders(intended, prices, asof)
        print("\nDRY-RUN ORDER PLAN  (account=%s, as-of %s) — %d orders" % (a.account, asof, len(orders)))
        for o in orders:
            pl = o["_plan"]
            print("  %-4s %-6s qty %-5s  tif=%s  ~$%-8.0f  [%s]  id=%s"
                  % (o["side"].upper(), o["symbol"], o["qty"], o["time_in_force"],
                     pl["est_value"], pl["role"], o["client_order_id"]))
        if a.submit:
            print("\nSubmitting (guarded)…")
            for o in orders:
                payload = {k: v for k, v in o.items() if not k.startswith("_")}
                res = cli.submit(payload, confirm=True)
                print("  %s -> %s" % (o["client_order_id"], "DRY-RUN" if res.get("dry_run") else res.get("status", res)))
        else:
            print("\n(plan only — add --submit and set %s=yes to send to the paper account)" % SUBMIT_ENV)


if __name__ == "__main__":
    _cli()
