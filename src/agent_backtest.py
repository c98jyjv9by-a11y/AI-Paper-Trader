"""
agent_backtest.py — Backtest an AI agent reading the daily EOD packet and acting.

Drives an agent through the per-date cover pages produced by pdf_report.run_cover_series
(the same content the PDF packet shows), one day at a time, NO look-ahead, under three
settings:

  • strict        — follow the model's queued buys/sells exactly (deterministic; no LLM).
  • balanced      — defer to the model's queue MOST of the time; modify/skip with a reason.
  • discretionary — use the agent's own judgment more often than not.

The harness owns ALL accounting (cash, positions, next-open fills, slippage). The agent
returns ONLY structured decisions — so results are deterministic and reproducible. Each
setting runs its own independent paper portfolio. At the end we score every setting vs
the model itself (the trades it was told to make) and vs SPY/QQQ, and log every
divergence and whether it helped or hurt in aggregate.

Paper/research only — never touches data/ live state; writes to reports/ only.

    python src/agent_backtest.py --scenario model_v4 --start 2026-01-01 --end 2026-06-16
    python src/agent_backtest.py --scenario model_v4 --start 2026-01-01 --end 2026-06-16 --no-llm
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from pdf_report import run_cover_series, _pct, _money       # reuse fmt helpers
from risk import apply_slippage

DEFAULT_MODEL = "claude-sonnet-4-6"
SETTINGS = ("strict", "balanced", "discretionary")

# The forward plan the agent is asked to follow (per the user's spec).
PLAN = """You are a disciplined paper-trading agent reading a DAILY packet — one page per
trading day, in date order. Each page shows that day's portfolio (held book with values,
cash), the model's QUEUED buys/sells for the next session (with reasons), market
commentary, and recommendations.

Process strictly one day at a time with NO look-ahead. For THIS day:
1. Note the held book, cash, and the model's queued trades + reasons.
2. Decide your action for the next market open under your current SETTING:
   - balanced: defer to the model's queued trades MOST of the time; you may modify or skip
     a recommendation when you have a clear reason, but the default is to follow it.
   - discretionary: use your OWN logic more often than not — the queue is input, not orders;
     deviate whenever your read of the commentary/holdings warrants it.
3. For every action give a one-line reason. Buys fill next open; you cannot spend more cash
   than you hold; you cannot sell more than you hold."""

_ACTION_TOOL = {
    "name": "submit_decisions",
    "description": "Submit trade decisions to execute at the next market open.",
    "input_schema": {
        "type": "object",
        "properties": {
            "actions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["BUY", "SELL"]},
                        "ticker": {"type": "string"},
                        "shares": {"type": "integer", "minimum": 1},
                        "reason": {"type": "string"},
                    },
                    "required": ["action", "ticker", "shares", "reason"],
                },
            },
            "summary": {"type": "string"},
        },
        "required": ["actions"],
    },
}


# ── Paper portfolio (harness-owned accounting) ────────────────────────────────────
class Paper:
    def __init__(self, cash: float):
        self.cash = float(cash)
        self.pos: Dict[str, Dict[str, float]] = {}   # ticker -> {shares, cost (avg)}
        self.realized = 0.0

    def value(self, prices: Dict[str, float]) -> float:
        eq = sum(p["shares"] * prices.get(t, p["cost"]) for t, p in self.pos.items())
        return self.cash + eq

    def buy(self, t: str, shares: int, price: float) -> int:
        affordable = int(min(shares, self.cash // price)) if price > 0 else 0
        if affordable <= 0:
            return 0
        cost = affordable * price
        prev = self.pos.get(t, {"shares": 0, "cost": 0.0})
        new_sh = prev["shares"] + affordable
        self.pos[t] = {"shares": new_sh,
                       "cost": (prev["shares"] * prev["cost"] + cost) / new_sh}
        self.cash -= cost
        return affordable

    def sell(self, t: str, shares: int, price: float) -> int:
        held = int(self.pos.get(t, {}).get("shares", 0))
        n = min(shares, held)
        if n <= 0:
            return 0
        self.realized += (price - self.pos[t]["cost"]) * n
        self.cash += n * price
        if n == held:
            del self.pos[t]
        else:
            self.pos[t]["shares"] = held - n
        return n


# ── Deciders ──────────────────────────────────────────────────────────────────────
def _strict_actions(spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    ns = spec.get("next_session") or {}
    out = []
    for s in ns.get("sells") or []:
        out.append({"action": "SELL", "ticker": s["ticker"], "shares": int(s["shares"]),
                    "reason": f"strict: model {s.get('reason', 'exit')}"})
    for b in ns.get("buys") or []:
        out.append({"action": "BUY", "ticker": b["ticker"], "shares": int(b["shares"]),
                    "reason": f"strict: model {b.get('reason', 'entry')}"})
    return out


def _rule_actions(setting: str, spec: Dict[str, Any], pf: Paper, prices: Dict[str, float]) -> List[Dict[str, Any]]:
    """Deterministic stand-ins for balanced/discretionary (offline / --no-llm). Real runs
    use the LLM; these just keep the harness runnable and the settings differentiated."""
    ns = spec.get("next_session") or {}
    buys, sells = ns.get("buys") or [], ns.get("sells") or []
    acts = [{"action": "SELL", "ticker": s["ticker"], "shares": int(s["shares"]),
             "reason": f"{setting}-rule: take model exit"} for s in sells]
    if setting == "balanced":                      # follow buys unless already ~90% invested
        pv = pf.value(prices) or 1.0
        invested = pv - pf.cash
        for b in buys:
            if invested / pv < 0.90:
                acts.append({"action": "BUY", "ticker": b["ticker"], "shares": int(b["shares"]),
                             "reason": "balanced-rule: follow within exposure budget"})
                invested += b["shares"] * b["price"]
            else:
                acts.append({"action": "SELL", "ticker": b["ticker"], "shares": 0,
                             "reason": "balanced-rule: skip buy — exposure full"})
    else:                                          # discretionary: concentrate — top buy only
        if buys:
            top = max(buys, key=lambda b: b.get("value", 0))
            acts.append({"action": "BUY", "ticker": top["ticker"], "shares": int(top["shares"]),
                         "reason": "discretionary-rule: concentrate in highest-conviction buy"})
    return [a for a in acts if a["shares"] > 0]


def _spec_to_text(spec: Dict[str, Any], pf: Paper, prices: Dict[str, float]) -> str:
    L = [f"DAILY PACKET PAGE — {spec['mark']}", ""]
    hold = spec.get("holdings") or []
    L.append("MODEL HELD BOOK:")
    if hold:
        for h in hold:
            L.append(f"  {h['ticker']}: {h['shares']} sh @ {_money(h['now'],2)} "
                     f"= {_money(h.get('value'))}  (unreal {_pct(h['unreal'])}, session {_pct(h['session'])})")
    else:
        L.append("  (flat)")
    ns = spec.get("next_session") or {}
    L += ["", "MODEL QUEUED FOR NEXT SESSION:"]
    for s in ns.get("sells") or []:
        L.append(f"  SELL {s['ticker']} {s['shares']} @ {_money(s['price'],2)} — {s.get('reason','')}")
    for b in ns.get("buys") or []:
        L.append(f"  BUY  {b['ticker']} {b['shares']} @ {_money(b['price'],2)} — {b.get('reason','')}")
    if not (ns.get("buys") or ns.get("sells")):
        L.append(f"  NO TRADES. {ns.get('buy_reason','')} {ns.get('sell_reason','')}".rstrip())
    L += ["", "COMMENTARY:"] + [f"  - {o}" for o in (spec.get("observations") or [])]
    L += ["", "RECOMMENDATIONS:"] + [f"  - {r}" for r in (spec.get("recommendations") or [])]
    L += ["", "YOUR CURRENT PAPER PORTFOLIO:",
          f"  cash {_money(pf.cash)}, total value {_money(pf.value(prices))}"]
    for t, p in sorted(pf.pos.items()):
        L.append(f"  {t}: {int(p['shares'])} sh (avg cost {_money(p['cost'],2)})")
    return "\n".join(L)


def _llm_actions(client, model: str, setting: str, spec, pf, prices, universe) -> List[Dict[str, Any]]:
    prompt = (f"{PLAN}\n\nYOUR SETTING: {setting.upper()}\nTradeable universe: "
              f"{', '.join(universe)}\n\n{_spec_to_text(spec, pf, prices)}\n\n"
              "Call submit_decisions with your actions for the next open (empty list = hold).")
    resp = client.messages.create(
        model=model, max_tokens=1500,
        tools=[_ACTION_TOOL], tool_choice={"type": "tool", "name": "submit_decisions"},
        messages=[{"role": "user", "content": prompt}],
    )
    for block in resp.content:
        if getattr(block, "type", None) == "tool_use":
            acts = block.input.get("actions", [])
            return [{"action": a["action"], "ticker": str(a["ticker"]).upper(),
                     "shares": int(a["shares"]), "reason": a.get("reason", "")}
                    for a in acts if a.get("ticker") and int(a.get("shares", 0)) > 0]
    return []


# ── Divergence vs the model's queue ───────────────────────────────────────────────
def _divergence(spec: Dict[str, Any], actions: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    ns = spec.get("next_session") or {}
    model: Dict[tuple, int] = {}
    for x in ns.get("buys") or []:
        model[("BUY", x["ticker"])] = int(x["shares"])
    for x in ns.get("sells") or []:
        model[("SELL", x["ticker"])] = int(x["shares"])
    agent = {(a["action"], a["ticker"]): a["shares"] for a in actions}
    skipped = [k for k in model if k not in agent]
    added = [k for k in agent if k not in model]
    resized = [k for k in agent if k in model and agent[k] != model[k]]
    if not (skipped or added or resized):
        return None
    return {"skipped": [f"{a} {t}" for a, t in skipped],
            "added": [f"{a} {t}" for a, t in added],
            "resized": [f"{a} {t}" for a, t in resized]}


# ── Simulation ──────────────────────────────────────────────────────────────────
def _mdd(vals: List[float]) -> float:
    peak, dd = vals[0], 0.0
    for v in vals:
        peak = max(peak, v)
        dd = min(dd, v / peak - 1)
    return dd


def _seed_from_first_page(pf: Paper, spec: Dict[str, Any]) -> None:
    """Initialize the paper book to the model's held book shown on the first page, so the
    agent starts level with the model instead of flat (it would otherwise permanently miss
    positions opened before the packet began). Cost basis = entry price; cash is reduced by
    the entry value, mirroring the capital the model had already deployed."""
    for h in spec.get("holdings") or []:
        sh, entry = int(h["shares"]), float(h["entry"])
        pf.pos[h["ticker"]] = {"shares": sh, "cost": entry}
        pf.cash -= sh * entry


def _simulate(setting: str, specs: List[Dict[str, Any]], close: pd.DataFrame,
              *, decide: Callable, start_cash: float, slippage: float,
              seed_first_book: bool = True) -> Dict[str, Any]:
    pf = Paper(start_cash)
    if seed_first_book and specs:
        _seed_from_first_page(pf, specs[0])
    equity: List[tuple] = []
    trades: List[Dict[str, Any]] = []
    divergences: List[Dict[str, Any]] = []
    pending: List[Dict[str, Any]] = []

    for i, spec in enumerate(specs):
        ts = pd.Timestamp(spec["mark"])
        prices = {t: float(close.loc[ts, t]) for t in close.columns
                  if ts in close.index and pd.notna(close.loc[ts, t])}
        # fill yesterday's decisions at today's price (next-open proxy = this close)
        for a in pending:
            px = prices.get(a["ticker"])
            if px is None:
                continue
            if a["action"] == "BUY":
                n = pf.buy(a["ticker"], a["shares"], apply_slippage(px, "buy", slippage))
            else:
                n = pf.sell(a["ticker"], a["shares"], apply_slippage(px, "sell", slippage))
            if n > 0:
                trades.append({"date": spec["mark"].isoformat(), "action": a["action"],
                               "ticker": a["ticker"], "shares": n, "price": round(px, 2),
                               "reason": a["reason"]})
        pending = []
        equity.append((spec["mark"], pf.value(prices)))

        if i + 1 < len(specs):                      # decide for the next session
            actions = decide(setting, spec, pf, prices)
            div = _divergence(spec, actions)
            if div:
                divergences.append({"date": spec["mark"].isoformat(), **div})
            pending = actions

    vals = [v for _, v in equity]
    return {"setting": setting, "equity": equity, "trades": trades, "divergences": divergences,
            "final": vals[-1], "ret": vals[-1] / start_cash - 1, "mdd": _mdd(vals),
            "n_trades": len(trades), "n_divergences": len(divergences)}


# ── Orchestration ──────────────────────────────────────────────────────────────
def run(scenario: str, start: date, end: date, *,
        settings=SETTINGS, model: str = DEFAULT_MODEL, no_llm: bool = False,
        start_cash: float = 100_000.0, slippage: float = 0.001, seed_first_book: bool = True,
        workers: Optional[int] = None, out: Optional[Path] = None) -> Dict[str, Any]:
    from scenarios import build_config, load_scenario
    from backtest import load_config, fetch_backtest_data, run_backtest

    root = Path(__file__).parent.parent
    # 1) Build the daily packet (PDF + per-date specs the agent reads).
    series = run_cover_series(scenario, start, end, workers=workers)
    specs = series["specs"]
    if not specs:
        raise RuntimeError("No daily pages produced.")

    # 2) Prices for fills/marks + the model & index benchmarks.
    cfg = build_config(load_config(root / "config"), load_scenario(scenario))
    panel = fetch_backtest_data(cfg["tickers"], start, end)
    close = panel["Close"]
    _t, eq, _p = run_backtest(cfg, panel, start, end)
    eq_by = dict(zip(eq["date"].astype(str), eq["total_portfolio_value"].astype(float)))

    client = None
    if not no_llm and any(s != "strict" for s in settings):
        import anthropic                            # lazy: only when an LLM setting runs
        client = anthropic.Anthropic()

    def decide(setting, spec, pf, prices):
        if setting == "strict":
            return _strict_actions(spec)
        if no_llm:
            return _rule_actions(setting, spec, pf, prices)
        return _llm_actions(client, model, setting, spec, pf, prices, cfg["tickers"])

    results = {s: _simulate(s, specs, close, decide=decide, start_cash=start_cash,
                            slippage=slippage, seed_first_book=seed_first_book)
               for s in settings}

    # 3) Benchmarks over the same page window.
    d0, d1 = specs[0]["mark"].isoformat(), specs[-1]["mark"].isoformat()
    ts0, ts1 = pd.Timestamp(d0), pd.Timestamp(d1)
    def _bench(sym):
        try:
            return float(close.loc[ts1, sym]) / float(close.loc[ts0, sym]) - 1
        except Exception:
            return None
    model_ret = (eq_by[d1] / eq_by[d0] - 1) if d0 in eq_by and d1 in eq_by else None
    bench = {"model": model_ret, "SPY": _bench("SPY"), "QQQ": _bench("QQQ")}

    out = Path(out) if out else (root / "reports" /
          f"agent_backtest_{scenario}_{start.isoformat()}_{end.isoformat()}.md")
    out.write_text(_report(scenario, d0, d1, results, bench, model, no_llm, series["pdf"],
                           seed_first_book))
    return {"report": str(out), "pdf": series["pdf"], "results": results, "bench": bench}


def _report(scenario, d0, d1, results, bench, model, no_llm, pdf, seeded=True) -> str:
    strict_ret = results.get("strict", {}).get("ret")
    L = [f"# Agent backtest — {scenario}",
         f"**Window:** {d0} → {d1}  |  **Decider:** {'deterministic rules (--no-llm)' if no_llm else model}  "
         f"|  **Packet:** `{Path(pdf).name}`", "",
         "_The agent reads one daily page at a time (no look-ahead) and emits structured trades; "
         "the harness owns all fills (next-open, with slippage) and accounting._",
         f"_Start: {'seeded with the first page held book (level with the model)' if seeded else 'flat (100% cash)'}._",
         "",
         "## Scorecard", "",
         "| Setting | Final | Return | Max DD | Trades | Divergences | vs Model |",
         "|---------|------:|------:|------:|------:|-----------:|--------:|"]
    for s, r in results.items():
        vs = "—" if strict_ret is None else _pct(r["ret"] - strict_ret)
        L.append(f"| {s} | {_money(r['final'])} | {_pct(r['ret'])} | {_pct(r['mdd'])} "
                 f"| {r['n_trades']} | {r['n_divergences']} | {vs} |")
    L += ["",
          f"**Benchmarks (same window):** model_v4 {_pct(bench['model'])} · "
          f"SPY {_pct(bench['SPY'])} · QQQ {_pct(bench['QQQ'])}.",
          "_`vs Model` = setting return minus the strict (follow-the-model) return — the net "
          "effect of the agent's divergences. Positive = its deviations helped._", ""]
    for s, r in results.items():
        L += [f"## {s} — divergences ({r['n_divergences']})"]
        if not r["divergences"]:
            L.append("_None — followed the model exactly._")
        else:
            for d in r["divergences"][:40]:
                bits = []
                for k in ("skipped", "added", "resized"):
                    if d.get(k):
                        bits.append(f"{k}: {', '.join(d[k])}")
                L.append(f"- **{d['date']}** — " + "; ".join(bits))
            if len(r["divergences"]) > 40:
                L.append(f"- …and {len(r['divergences']) - 40} more.")
        L.append("")
    L += ["## Trade logs", ""]
    for s, r in results.items():
        L += [f"### {s} ({r['n_trades']} trades)", "",
              "| Date | Action | Ticker | Shares | Price | Reason |",
              "|------|--------|--------|------:|------:|--------|"]
        for t in r["trades"]:
            L.append(f"| {t['date']} | {t['action']} | {t['ticker']} | {t['shares']} "
                     f"| {t['price']:.2f} | {t['reason']} |")
        L.append("")
    L.append("_Paper-trading research only — not investment advice._")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Backtest an agent reading the daily EOD packet.")
    ap.add_argument("--scenario", required=True)
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--settings", default=",".join(SETTINGS),
                    help="comma list of strict,balanced,discretionary")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--no-llm", action="store_true",
                    help="use deterministic rule stand-ins instead of the LLM (offline)")
    ap.add_argument("--no-seed", action="store_true",
                    help="start the agent flat instead of seeding it with the first page's held book")
    ap.add_argument("--workers", type=int)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    res = run(a.scenario, date.fromisoformat(a.start), date.fromisoformat(a.end),
              settings=tuple(s.strip() for s in a.settings.split(",") if s.strip()),
              model=a.model, no_llm=a.no_llm, seed_first_book=not a.no_seed,
              workers=a.workers, out=Path(a.out) if a.out else None)
    print(f"Wrote {res['report']}")
    for s, r in res["results"].items():
        print(f"  {s:14s} final {_money(r['final'])}  return {_pct(r['ret'])}  "
              f"({r['n_trades']} trades, {r['n_divergences']} divergences)")


if __name__ == "__main__":
    main()
