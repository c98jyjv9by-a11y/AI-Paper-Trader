"""
research_suite.py — Run every analysis once and emit ONE consolidated summary.

A single command that runs the whole research stack over one consistent train/test
split — backtest+diagnostics, experiments, ticker-experiments, per-ticker
calibrate, evaluate (seed + calibrated), active portfolio, and the factor screen —
then writes a single Markdown report with the most salient takeaway from each, an
auto-derived headline verdict, and a recommended next step.

Data is fetched once and sliced for every stage (no look-ahead changes; each stage
filters by date internally). Live paper state (data/) is never touched.

    python run.py suite --train-start 2021-06-13 --train-end 2024-06-13 \
                        --test-start 2024-06-13 --test-end 2026-06-13
"""
import argparse
import logging
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from backtest import compute_metrics, fetch_backtest_data, load_config, run_backtest
from diagnostics import compute_diagnostics
from experiments import run_experiments
from ticker_experiments import run_ticker_experiments
from signal_calibration import calibrate_universe, evaluate_criteria, load_criteria
from active_experiment import run_active_experiment
from signal_screen import screen_factors, _is_real, HEADLINE_H
from logger import setup_logging

log = logging.getLogger(__name__)


def _pct(v: Optional[float]) -> str:
    return "—" if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v * 100:+.2f}%"


def _safe(fn, label: str) -> Tuple[Optional[Any], Optional[str]]:
    try:
        return fn(), None
    except Exception as exc:  # one stage failing must not kill the suite
        log.warning("Suite stage '%s' failed: %s", label, exc)
        return None, str(exc)


# ─── Per-stage salient extraction ─────────────────────────────────────────────


def _stage_backtest(config, price_data, start, end) -> Dict[str, Any]:
    sink: List[Dict[str, Any]] = []
    t, e, p = run_backtest(config, price_data, start, end, signal_sink=sink)
    m = compute_metrics(t, e, p, config, start, end)
    diag = compute_diagnostics(config, price_data, t, e, p, sink, m, start, end)
    spread = diag.get("predictiveness", {}).get("top_minus_bottom_spread", {}).get("spread_20d")
    return {
        "total_return": m.get("total_return"), "irr": m.get("irr"),
        "ew_return": m.get("equal_weight_return"), "spy": m.get("spy_return"), "qqq": m.get("qqq_return"),
        "max_dd": m.get("max_drawdown"), "spread_20d": spread,
        "beat_ew": (m.get("total_return") or -9) > (m.get("equal_weight_return") or 9),
    }


def _stage_experiments(config, price_data, start, end) -> Dict[str, Any]:
    res = run_experiments(config, price_data, start, end)
    base = next((r for r in res if r["name"] == "baseline"), res[0])
    ew = base["metrics"].get("equal_weight_return")
    beat = sum(1 for r in res if (r["metrics"].get("total_return") or -9) > (ew or 9))
    best = max(res, key=lambda r: r["metrics"].get("total_return") or -9)
    return {"n": len(res), "best": best["name"], "best_ret": best["metrics"].get("total_return"),
            "ew_return": ew, "beat_ew": beat}


def _stage_ticker_experiments(config, price_data, start, end) -> Dict[str, Any]:
    res = run_ticker_experiments(config, price_data, start, end)
    active = [r for r in res if r["name"] != "baseline"]
    beat_cm = sum(1 for r in active
                  if r["capital_matched_avg"]["total_return"] is not None
                  and (r["metrics"].get("total_return") or -9) > r["capital_matched_avg"]["total_return"])
    spread = next((r["predictiveness"].get("top_minus_bottom_spread", {}).get("spread_20d")
                   for r in res if r["name"] == "baseline"), None)
    return {"n_active": len(active), "beat_capital_matched": beat_cm, "spread_20d": spread}


def _stage_calibrate(config, price_data, train_start, train_end) -> Dict[str, Any]:
    results = calibrate_universe(price_data, config["tickers"], train_start, train_end,
                                 config["risk"]["slippage"])
    valid = [r for r in results if r.get("outperformance") is not None]
    cand = [r for r in valid if r.get("beats_exposure_matched") and (r.get("param_stability") or 0) >= 0.5]
    beat = sum(1 for r in valid if r["outperformance"] > 0)
    criteria = {r["ticker"]: (r["modal_params"]["fast"], r["modal_params"]["slow"],
                              r["modal_params"]["trailing"]) for r in valid}
    return {"n": len(valid), "candidates": len(cand), "beat_hold": beat,
            "candidate_names": [r["ticker"] for r in cand], "criteria": criteria}


def _stage_evaluate(price_data, criteria, start, end, slippage, label) -> Dict[str, Any]:
    res = evaluate_criteria(price_data, criteria, start, end, slippage)
    valid = [r for r in res if r.get("outperformance") is not None]
    return {"label": label, "n": len(valid),
            "beat_hold": sum(1 for r in valid if r["outperformance"] > 0),
            "beat_exp_matched": sum(1 for r in valid if r.get("beats_exposure_matched"))}


def _stage_active(config, price_data, train, test) -> Dict[str, Any]:
    res = run_active_experiment(config, price_data, train, test)
    port, bench = res["port_test"], res["bench_test"]
    ew = bench.get("EW_eligible", {}).get("total_return") if bench else None
    cm = bench.get("EW_eligible_capital_matched", {}).get("total_return") if bench else None
    pr = port["total_return"] if port else None
    return {"eligible": len(res["eligible"]), "n": len(res["per_ticker"]),
            "oos_return": pr, "oos_ew_eligible": ew, "oos_capital_matched": cm,
            "beat_ew": (pr is not None and ew is not None and pr > ew),
            "beat_cm": (pr is not None and cm is not None and pr > cm)}


def _stage_screen(price_data, train, test) -> Dict[str, Any]:
    rows = screen_factors(price_data["Close"], price_data["Volume"], train, test)
    survivors = [r for r in rows if _is_real(r)]
    return {"n": len(rows), "survivors": [r["factor"] for r in survivors],
            "leaderboard": [(r["factor"], r.get(f"ic_test_{HEADLINE_H}"), r.get(f"ic_test_t_{HEADLINE_H}"))
                            for r in rows[:5]]}


# ─── Report ───────────────────────────────────────────────────────────────────


def render_summary(stages: Dict[str, Any], run_date: date,
                   train: Tuple[date, date], test: Tuple[date, date]) -> str:
    bt = stages.get("backtest", {})
    scr = stages.get("screen", {})
    act = stages.get("active", {})

    # Auto headline verdict
    survivors = scr.get("survivors", []) if scr else []
    spread = bt.get("spread_20d")
    if survivors:
        verdict = (f"**A candidate signal cleared the out-of-sample screen** ({', '.join(survivors)}). "
                   "There may be a real edge to build on — validate it end-to-end next.")
    else:
        verdict = ("**No predictive signal found.** The composite ranker has ~zero cross-sectional power "
                   f"(20d quintile spread {_pct(spread)}), no variant beats exposure-matched buy-and-hold, "
                   "and no candidate factor survives the OOS screen. The active rules only **reduce drawdown** "
                   "— a de-risking overlay, not alpha.")

    L: List[str] = [
        "# Research Suite — Consolidated Summary",
        f"**Train:** {train[0]} → {train[1]}  |  **Test (OOS):** {test[0]} → {test[1]}  "
        f"|  **Generated:** {run_date.isoformat()}",
        "",
        "> One run of the whole stack over a single train/test split. All TRAIN figures are in-sample; "
        "TEST is the out-of-sample verdict. For full per-stage detail, run that stage's own command "
        "(e.g. `run.py screen …`) — this suite summarises, it does not write the individual reports.",
        "",
        "---", "",
        "## Headline verdict", "", verdict, "",
        "## Most salient takeaway per stage", "",
        "| Stage | Window | Salient result |",
        "|-------|--------|----------------|",
    ]

    def row(stage, window, text):
        L.append(f"| {stage} | {window} | {text} |")

    if "backtest" in stages and bt:
        row("Backtest", "full",
            f"Strategy {_pct(bt['total_return'])} vs EW-Hold {_pct(bt['ew_return'])} "
            f"(SPY {_pct(bt['spy'])}, QQQ {_pct(bt['qqq'])}); IRR {_pct(bt['irr'])}; "
            f"max DD {_pct(bt['max_dd'])}; **20d quintile spread {_pct(bt['spread_20d'])}**. "
            f"Beat EW-Hold: {'✅' if bt['beat_ew'] else '❌'}")
    ex = stages.get("experiments")
    if ex:
        row("Experiments", "full",
            f"{ex['n']} profiles; best `{ex['best']}` {_pct(ex['best_ret'])}; "
            f"beat EW-Hold: {ex['beat_ew']}/{ex['n']}")
    tx = stages.get("ticker_experiments")
    if tx:
        row("Ticker-experiments", "full",
            f"{tx['beat_capital_matched']}/{tx['n_active']} profiles beat capital-matched EW; "
            f"20d quintile spread {_pct(tx['spread_20d'])}")
    cal = stages.get("calibrate")
    if cal:
        names = (": " + ", ".join(cal["candidate_names"])) if cal["candidate_names"] else ""
        row("Calibrate", "train",
            f"{cal['beat_hold']}/{cal['n']} tickers beat hold OOS-in-folds; "
            f"{cal['candidates']}/{cal['n']} candidate criteria{names}")
    for key in ("evaluate_calibrated", "evaluate_seed"):
        evs = stages.get(key)
        if evs:
            row(f"Evaluate ({evs['label']})", "test",
                f"{evs['beat_hold']}/{evs['n']} beat hold; {evs['beat_exp_matched']}/{evs['n']} beat "
                "exposure-matched hold")
    if act:
        row("Active portfolio", "test",
            f"{act['eligible']}/{act['n']} eligible; OOS {_pct(act['oos_return'])} vs "
            f"EW-eligible {_pct(act['oos_ew_eligible'])} / capital-matched {_pct(act['oos_capital_matched'])}; "
            f"beat capital-matched: {'✅' if act['beat_cm'] else '❌'}")
    if scr:
        sv = ", ".join(scr["survivors"]) if scr["survivors"] else "none"
        row("Signal screen", "train+test",
            f"{len(scr['survivors'])}/{scr['n']} factors survive OOS (candidates: {sv})")
    L.append("")

    # Errors
    errs = {k: v for k, v in stages.get("_errors", {}).items()}
    if errs:
        L += ["## Stages that errored", ""]
        for k, v in errs.items():
            L.append(f"- **{k}**: {v}")
        L.append("")

    # Signal screen leaderboard (the current decision point)
    if scr and scr.get("leaderboard"):
        L += [f"## Signal screen — top 5 by OOS {HEADLINE_H}d rank IC", "",
              "| Factor | OOS IC | t-stat |", "|--------|--------|--------|"]
        for name, ic, t in scr["leaderboard"]:
            L.append(f"| {name} | {ic:+.3f} | {t:+.1f} |" if ic is not None and t is not None
                     else f"| {name} | — | — |")
        L += ["", "_IC ≈ 0 = no signal; |IC| ≳ 0.03 interesting, ≳ 0.05 strong._", ""]

    # Recommended next step
    L += ["## Recommended next step", ""]
    if survivors:
        L.append(f"- Build the next strategy around the surviving factor(s) ({', '.join(survivors)}): "
                 "wire into the ranker, then re-run `active`/`evaluate` to confirm it survives end-to-end.")
    else:
        L.append("- **Stop tuning price/volume signals on this universe** — nothing predicts. "
                 "Pivot to a *different universe* (higher dispersion / less-efficient names) or a "
                 "*different data source* (fundamentals, estimates, alt-data). If the goal is risk control "
                 "rather than alpha, keep the timing rules as a documented de-risking overlay.")
    L.append("")
    return "\n".join(L)


# ─── Orchestration ────────────────────────────────────────────────────────────


def run(train_start: date, train_end: date, test_start: date, test_end: date) -> Dict[str, str]:
    setup_logging()
    run_date = date.today()
    root = Path(__file__).parent.parent
    config = load_config(root / "config")
    slippage = config["risk"]["slippage"]
    full = (train_start, test_end)
    train, test = (train_start, train_end), (test_start, test_end)

    log.info("=== Research Suite: fetching data once ===")
    price_data = fetch_backtest_data(config["tickers"], train_start, test_end, warmup_days=420)

    stages: Dict[str, Any] = {}
    errors: Dict[str, str] = {}

    def stage(key, fn):
        log.info("Suite stage: %s", key)
        val, err = _safe(fn, key)
        if err:
            errors[key] = err
        else:
            stages[key] = val

    stage("backtest", lambda: _stage_backtest(config, price_data, *full))
    stage("experiments", lambda: _stage_experiments(config, price_data, *full))
    stage("ticker_experiments", lambda: _stage_ticker_experiments(config, price_data, *full))
    stage("calibrate", lambda: _stage_calibrate(config, price_data, train_start, train_end))
    # evaluate needs the calibrated criteria (if calibrate succeeded) and the seed
    if "calibrate" in stages and stages["calibrate"]["criteria"]:
        stage("evaluate_calibrated",
              lambda: {**_stage_evaluate(price_data, stages["calibrate"]["criteria"], test_start, test_end,
                                         slippage, "calibrated")})
    seed = load_criteria(root / "config" / "ticker_timing_criteria.yaml")
    stage("evaluate_seed", lambda: _stage_evaluate(price_data, seed, test_start, test_end, slippage, "seed"))
    stage("active", lambda: _stage_active(config, price_data, train, test))
    stage("screen", lambda: _stage_screen(price_data, train, test))

    stages["_errors"] = errors
    report = render_summary(stages, run_date, train, test)
    (root / "reports").mkdir(parents=True, exist_ok=True)
    out = root / "reports" / f"research_summary_{run_date.isoformat()}.md"
    out.write_text(report)

    print()
    print(report.split("## Most salient")[0].strip())   # print headline verdict to console
    print()
    print(f"  Full summary: {out}")
    if errors:
        print(f"  ({len(errors)} stage(s) errored — see report)")
    print()
    return {"report": str(out)}


def main() -> None:
    p = argparse.ArgumentParser(description="AI Paper Trader — full research suite, one consolidated report")
    p.add_argument("--train-start", required=True, metavar="YYYY-MM-DD")
    p.add_argument("--train-end", required=True, metavar="YYYY-MM-DD")
    p.add_argument("--test-start", required=True, metavar="YYYY-MM-DD")
    p.add_argument("--test-end", required=True, metavar="YYYY-MM-DD")
    args = p.parse_args()
    try:
        ts, te = date.fromisoformat(args.train_start), date.fromisoformat(args.train_end)
        vs, ve = date.fromisoformat(args.test_start), date.fromisoformat(args.test_end)
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)
    run(ts, te, vs, ve)


if __name__ == "__main__":
    main()
