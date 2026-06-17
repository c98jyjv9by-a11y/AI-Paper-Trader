"""
context_matrix.py — Context-source sensitivity matrix for the agent harness.

Sweeps the power set of context sources (rows) against the judgment-based behavior
settings (cols = balanced, discretionary) and reports return-vs-strict for each combo,
so you can see which sources — and which interactions — actually pay off.

  • Cover-series specs + price panel + benchmarks are built ONCE (prepare_window) and
    reused across every combo. Providers are instantiated once and shared (Finnhub
    fetches are cached across arms by (ticker, window)).
  • strict is run ONCE as the fixed reference (it deterministically follows the model and
    is invariant to context); it is never a context-varying row.
  • Defaults to the point-in-time-safe sources (macro,news) to avoid look-ahead and
    rate-limit blowups. Prints the run/-call estimate before executing.

    python src/context_matrix.py --scenario model_v4 --start 2026-01-01 --end 2026-06-16
    python src/context_matrix.py --scenario model_v4 --start ... --end ... --sources macro,news \
        --settings discretionary --repeats 2 --oos-window 2025-07-01:2025-12-31
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent))
import agent_backtest as AB
from pdf_report import _pct, _money

WEAK_MODELS = {"claude-haiku-4-5-20251001", "claude-haiku-4-5"}


def _powerset(sources: List[str], max_size: Optional[int]) -> List[Tuple[str, ...]]:
    """All combos incl. the empty set (baseline), optionally capped at max_size."""
    hi = len(sources) if max_size is None else min(max_size, len(sources))
    combos = [()]
    for k in range(1, hi + 1):
        combos += list(itertools.combinations(sources, k))
    return combos


def _combo_label(combo: Tuple[str, ...]) -> str:
    return "+".join(combo) if combo else "none"


def run_matrix(scenario: str, start: date, end: date, *,
               sources: List[str], settings: List[str], model: str,
               repeats: int = 1, max_combo_size: Optional[int] = None,
               oos_window: Optional[Tuple[date, date]] = None,
               start_cash: float = 100_000.0, slippage: float = 0.001,
               workers: Optional[int] = None, arm_workers: int = 8,
               out: Optional[Path] = None) -> Dict[str, Any]:
    import concurrent.futures as cf
    import anthropic
    from context_providers import build_providers

    root = Path(__file__).parent.parent
    combos = _powerset(sources, max_combo_size)
    settings = [s for s in settings if s != "strict"]      # strict is the fixed reference
    n_llm_arms = len(combos) * len(settings) * repeats
    if model in WEAK_MODELS:
        print(f"WARNING: '{model}' is a weak model — context value is model-dependent and "
              "may mislead. Prefer Sonnet/Opus for source experiments.")

    win = AB.prepare_window(scenario, start, end, workers)
    cfg, specs, close = win["cfg"], win["specs"], win["close"]
    n_days = len(specs)
    # Short per-call timeout + bounded retries: a single stalled socket must never hang the
    # whole sweep (the earlier run hung ~15 min on the SDK's 600s default timeout).
    client = anthropic.Anthropic(api_key=AB._load_api_key(root), timeout=60.0, max_retries=8)
    aw = max(1, min(arm_workers, n_llm_arms))
    print(f"Matrix: {len(combos)} source combos × {len(settings)} settings × {repeats} repeat(s) "
          f"= {n_llm_arms} LLM arms over {n_days} days ≈ {n_llm_arms * n_days:,} agent calls "
          f"(+ strict reference, no LLM). Model: {model}. Arms run {aw}-way parallel.", flush=True)

    # One provider instance per source, shared across combos (caches reused).
    pool = {s: build_providers([s], cfg["tickers"], start, end, close)[0] for s in sources}

    use_cache = (repeats == 1)        # never cache repeats — they measure run-to-run noise
    def _arm(provider_list, setting):
        decide = AB.make_decider(provider_list, cfg, client, model, no_llm=False, use_cache=use_cache)
        return AB._simulate(setting, specs, close, decide=decide,
                            start_cash=start_cash, slippage=slippage, seed_first_book=True)

    # Fixed reference: strict (no LLM, context-invariant).
    strict = AB._simulate("strict", specs, close,
                          decide=AB.make_decider([], cfg, None, model, no_llm=False),
                          start_cash=start_cash, slippage=slippage, seed_first_book=True)
    strict_ret = strict["ret"]

    # Independent arms (combo × setting × repeat) run concurrently — each is internally
    # sequential (its book evolves day by day), but arms don't depend on each other.
    tasks = [(combo, setting, rep) for combo in combos
             for setting in settings for rep in range(repeats)]

    def _task(t):
        combo, setting, _ = t
        try:
            return (combo, setting, _arm([pool[s] for s in combo], setting))
        except Exception as exc:                          # one bad arm must not sink the matrix
            return (combo, setting, {"ret": float("nan"), "mdd": float("nan"), "sharpe": None,
                                     "n_trades": 0, "n_divergences": 0, "_error": str(exc)})

    cells: Dict[tuple, list] = {}
    with cf.ThreadPoolExecutor(max_workers=aw) as ex:
        for combo, setting, r in ex.map(_task, tasks):
            cells.setdefault((_combo_label(combo), setting), []).append(r)
    failed = [(k, r.get("_error")) for k, rs in cells.items() for r in rs if "_error" in r]
    if failed:
        print(f"WARNING: {len(failed)}/{len(tasks)} arms failed and were dropped:", flush=True)
        for (lbl, setting), err in failed[:8]:
            print(f"  {lbl}/{setting}: {err[:140]}", flush=True)

    rows = []
    for combo in combos:
        for setting in settings:
            reps = cells[(_combo_label(combo), setting)]
            rets = [r["ret"] for r in reps if r["ret"] == r["ret"]]   # drop NaN (failed arms)
            if not rets:
                continue
            mean = sum(rets) / len(rets)
            std = (sum((x - mean) ** 2 for x in rets) / len(rets)) ** 0.5 if len(rets) > 1 else 0.0
            best = max((r for r in reps if r["ret"] == r["ret"]), key=lambda r: r["ret"])
            rows.append({
                "sources": _combo_label(combo), "setting": setting,
                "return": mean, "ret_std": std, "vs_strict": mean - strict_ret,
                "maxDD": best["mdd"], "sharpe": best["sharpe"],
                "trades": best["n_trades"], "divergences": best["n_divergences"],
                "significant": (repeats > 1 and abs(mean - strict_ret) > 2 * std),
            })

    res = {"scenario": scenario, "window": [win["d0"], win["d1"]], "model": model,
           "strict_ret": strict_ret, "bench": win["bench"], "repeats": repeats,
           "rows": rows}

    # Optional OOS check on the top-K combos (by vs_strict).
    if oos_window:
        topk = sorted(rows, key=lambda r: -r["vs_strict"])[:3]
        res["oos"] = _oos_check(scenario, oos_window, topk, settings, model, sources,
                                repeats, start_cash, slippage, workers)

    out = Path(out) if out else (root / "reports" /
          f"context_matrix_{scenario}_{win['d0']}_{win['d1']}.md")
    out.write_text(_render(res))
    _write_csv(out.with_suffix(".csv"), rows)
    (out.with_suffix(".json")).write_text(json.dumps(res, indent=2, default=str))
    res["report"] = str(out)
    return res


def _oos_check(scenario, oos_window, topk, settings, model, sources, repeats,
               start_cash, slippage, workers) -> Dict[str, Any]:
    import anthropic
    from context_providers import build_providers
    o0, o1 = oos_window
    win = AB.prepare_window(scenario, o0, o1, workers)
    cfg, specs, close = win["cfg"], win["specs"], win["close"]
    client = anthropic.Anthropic(api_key=AB._load_api_key(Path(__file__).parent.parent),
                                 timeout=60.0, max_retries=8)
    pool = {s: build_providers([s], cfg["tickers"], o0, o1, close)[0] for s in sources}
    strict = AB._simulate("strict", specs, close,
                          decide=AB.make_decider([], cfg, None, model, no_llm=False),
                          start_cash=start_cash, slippage=slippage, seed_first_book=True)
    out = []
    for r in topk:
        combo = tuple(t for t in r["sources"].split("+") if t != "none")
        plist = [pool[s] for s in combo if s in pool]
        sim = AB._simulate(r["setting"], specs, close,
                           decide=AB.make_decider(plist, cfg, client, model, no_llm=False),
                           start_cash=start_cash, slippage=slippage, seed_first_book=True)
        out.append({"sources": r["sources"], "setting": r["setting"],
                    "is_vs_strict": r["vs_strict"], "oos_vs_strict": sim["ret"] - strict["ret"],
                    "held_up": (r["vs_strict"] > 0) == (sim["ret"] - strict["ret"] > 0)})
    return {"window": [win["d0"], win["d1"]], "rows": out}


def _write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    import csv
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def _render(res: Dict[str, Any]) -> str:
    b = res["bench"]
    L = [f"# Context-source sensitivity matrix — {res['scenario']}",
         f"**Window:** {res['window'][0]} → {res['window'][1]}  |  **Model:** {res['model']}  "
         f"|  **Repeats/cell:** {res['repeats']}", "",
         f"**Reference — strict (follow the model):** {_pct(res['strict_ret'])}.  "
         f"Benchmarks: model {_pct(b['model'])} · SPY {_pct(b['SPY'])} · QQQ {_pct(b['QQQ'])}.", "",
         "_Each cell = a behavior setting given a combination of context sources. "
         "`vs strict` is the headline: positive ⇒ that context helped the agent beat just "
         "following the model. strict is context-invariant, so it is the fixed reference, not a row._", "",
         "| Sources | Setting | Return | vs strict | Max DD | Sharpe | Trades | Diverg. |"
         + (" Sig? |" if res["repeats"] > 1 else ""),
         "|---------|---------|------:|--------:|------:|------:|------:|-------:|"
         + ("------:|" if res["repeats"] > 1 else "")]
    for r in sorted(res["rows"], key=lambda x: (x["setting"], -x["vs_strict"])):
        sig = (" ✓" if r["significant"] else " ·") if res["repeats"] > 1 else ""
        std = f" ±{r['ret_std']*100:.2f}" if res["repeats"] > 1 else ""
        line = (f"| {r['sources']} | {r['setting']} | {_pct(r['return'])}{std} | "
                f"{_pct(r['vs_strict'])} | {_pct(r['maxDD'])} | "
                f"{'—' if r['sharpe'] is None else f'{r['sharpe']:.2f}'} | {r['trades']} | {r['divergences']} |")
        if res["repeats"] > 1:
            line += f"{sig} |"
        L.append(line)
    L += ["", "_Highest `vs strict` per setting = the most valuable context combo. "
          "Sub-noise deltas (Sig? = ·) are not trustworthy on one window — re-validate OOS._"]
    if res.get("oos"):
        o = res["oos"]
        L += ["", f"## OOS check ({o['window'][0]} → {o['window'][1]})", "",
              "| Sources | Setting | In-sample vs strict | OOS vs strict | Held up? |",
              "|---------|---------|------:|------:|:-------:|"]
        for r in o["rows"]:
            L.append(f"| {r['sources']} | {r['setting']} | {_pct(r['is_vs_strict'])} "
                     f"| {_pct(r['oos_vs_strict'])} | {'✓' if r['held_up'] else '✗'} |")
    L.append("\n_Paper-trading research only — not investment advice._")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Context-source sensitivity matrix.")
    ap.add_argument("--scenario", required=True)
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--sources", default="macro,news",
                    help="sources to sweep the power set of (default: macro,news — PIT-safe)")
    ap.add_argument("--settings", default="balanced,discretionary",
                    help="behavior settings to vary (strict is always the fixed reference)")
    ap.add_argument("--model", default=AB.DEFAULT_MODEL)
    ap.add_argument("--repeats", type=int, default=1, help="runs per cell for a noise band")
    ap.add_argument("--max-combo-size", type=int)
    ap.add_argument("--oos-window", help="disjoint window START:END to re-check the top combos")
    ap.add_argument("--workers", type=int, help="parallel workers for the cover-series build")
    ap.add_argument("--arm-workers", type=int, default=8, help="concurrent LLM arms (default 8)")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    oos = None
    if a.oos_window:
        o0, o1 = a.oos_window.split(":")
        oos = (date.fromisoformat(o0), date.fromisoformat(o1))
    res = run_matrix(
        a.scenario, date.fromisoformat(a.start), date.fromisoformat(a.end),
        sources=[s.strip() for s in a.sources.split(",") if s.strip()],
        settings=[s.strip() for s in a.settings.split(",") if s.strip()],
        model=a.model, repeats=a.repeats, max_combo_size=a.max_combo_size,
        oos_window=oos, workers=a.workers, arm_workers=a.arm_workers,
        out=Path(a.out) if a.out else None)
    print(f"\nWrote {res['report']}")
    print(f"Reference strict: {_pct(res['strict_ret'])}")
    for r in sorted(res["rows"], key=lambda x: -x["vs_strict"])[:6]:
        print(f"  {r['sources']:14s} {r['setting']:13s} {_pct(r['return'])}  "
              f"vs strict {_pct(r['vs_strict'])}")


if __name__ == "__main__":
    main()
