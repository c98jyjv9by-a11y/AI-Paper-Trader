"""
scenarios.py — Named strategy scenarios (trimmed universe + per-ticker overrides).

A scenario is a self-contained YAML in config/scenarios/<name>.yaml that overlays
config/strategy.yaml + universe.yaml: it can replace the ticker universe and merge
in portfolio/risk/signal overrides and per-ticker ticker_groups. This makes a tuned
configuration a first-class, reusable, named object (e.g. "davids_model") instead
of edits scattered through the base config.

`run.py scenario <name> --start … --end …` runs a backtest (+diagnostics) against
the merged config and writes scenario-tagged outputs to reports/ and backtests/.
The base config and live paper state (data/) are never modified.
"""
import argparse
import copy
import logging
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

sys.path.insert(0, str(Path(__file__).parent))

from backtest import (
    compute_metrics,
    fetch_backtest_data,
    generate_backtest_report,
    load_config,
    run_backtest,
    _execute_sensitivity_tasks,
    _robustness_commentary,
    _sweep_with_baseline,
    _ALT_WEIGHT_PROFILES,
    _DEFAULT_WEIGHTS,
    _pct as _b_pct,
    _pf as _b_pf,
)
from diagnostics import compute_diagnostics, diagnostics_csv, render_diagnostics_md
from risk import resolve_max_position_pct
from logger import setup_logging

log = logging.getLogger(__name__)

_REPLACE_WHOLE = {"tickers", "ticker_groups"}   # overlaid wholesale, not deep-merged


def scenarios_dir() -> Path:
    return Path(__file__).parent.parent / "config" / "scenarios"


def list_scenarios() -> List[str]:
    d = scenarios_dir()
    return sorted(p.stem for p in d.glob("*.yaml")) if d.is_dir() else []


def load_scenario(name: str) -> Dict[str, Any]:
    path = scenarios_dir() / f"{name}.yaml"
    if not path.is_file():
        raise FileNotFoundError(
            f"Scenario '{name}' not found in {scenarios_dir()}. Available: {list_scenarios() or 'none'}"
        )
    return yaml.safe_load(path.read_text()) or {}


def _deep_merge(base: Dict[str, Any], over: Dict[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def build_config(base_config: Dict[str, Any], scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Overlay a scenario onto the base config. tickers/ticker_groups replace
    wholesale; portfolio/risk/signals/etc. deep-merge; name/description are metadata."""
    cfg = copy.deepcopy(base_config)
    for k, v in scenario.items():
        if k in ("name", "description"):
            continue
        if k in _REPLACE_WHOLE or not isinstance(v, dict) or not isinstance(cfg.get(k), dict):
            cfg[k] = copy.deepcopy(v)
        else:
            cfg[k] = _deep_merge(cfg[k], v)
    return cfg


# ─── Sensitivity (scenario-aware: run-wide + per-ticker exit params) ──────────


def _scenario_sensitivity_tasks(cfg: Dict[str, Any]):
    """
    Build one-way sensitivity variants for a scenario config:
      * Run-wide params (affect the whole backtest): exposure, trades/day, min score,
        slippage, the re-entry recovery gate, and the signal-weight profile.
      * Ticker-level exit params: each variant overwrites that field for EVERY
        ticker_groups name at once — a uniform stand-in that shows how sensitive the
        run is to the per-ticker exit choices collectively.
    Returns (tasks, ordered_groups, baseline_marks). tasks = (param, value_str, cfg).
    """
    tasks = []
    groups = []                      # ordered (param_key, label) for rendering
    baseline_marks: Dict[str, str] = {}
    r, p = cfg["risk"], cfg["portfolio"]
    s = cfg.get("signals", {}) or {}

    def add_runwide(param, label, points, baseline, fmt, setter):
        groups.append((param, label))
        baseline_marks[param] = fmt(baseline)
        for v in _sweep_with_baseline(points, baseline):
            c = copy.deepcopy(cfg)
            setter(c, v)
            tasks.append((param, fmt(v), c))

    def _set(path):
        def _s(c, v):
            d = c
            for k in path[:-1]:
                d = d.setdefault(k, {})
            d[path[-1]] = v
        return _s

    add_runwide("max_total_exposure", "Max Total Exposure", [0.5, 0.7, 0.9, 1.0],
                p.get("max_total_exposure"), lambda v: f"{v:.0%}", _set(["portfolio", "max_total_exposure"]))

    # Max position size: sweep the resolved baseline (auto = exposure / n) by multiples.
    mpp_base = round(resolve_max_position_pct(cfg), 6)
    add_runwide("max_position_pct", "Max Position Size",
                [round(mpp_base * m, 6) for m in (0.5, 1.5, 2.0, 3.0)], mpp_base,
                lambda v: f"{v:.2%}", _set(["portfolio", "max_position_pct"]))
    add_runwide("max_new_trades_per_day", "Max New Trades / Day", [1, 2, 3, 5],
                p.get("max_new_trades_per_day"), lambda v: str(int(v)), _set(["portfolio", "max_new_trades_per_day"]))
    add_runwide("min_composite_score", "Min Composite Score", [None, 0.60, 0.70],
                s.get("min_composite_score"), lambda v: "none" if v is None else f"{v:.2f}",
                _set(["signals", "min_composite_score"]))
    add_runwide("slippage", "Slippage", [0.0005, 0.001, 0.002, 0.005],
                r.get("slippage"), lambda v: f"{v * 100:.2f}%", _set(["risk", "slippage"]))
    add_runwide("reentry_recover_pct", "Re-entry Recovery Gate", [None, 0.0, 0.05, 0.10],
                r.get("reentry_recover_pct"), lambda v: "off" if v is None else f"{v:.0%}",
                _set(["risk", "reentry_recover_pct"]))

    # Signal-weight profile (run-wide): the scenario's own weights vs fixed alternatives.
    config_weights = s.get("weights") or _DEFAULT_WEIGHTS
    groups.append(("signal_weights", "Signal Weight Profile"))
    baseline_marks["signal_weights"] = "baseline"
    for name, wts in {"baseline": config_weights, **_ALT_WEIGHT_PROFILES}.items():
        c = copy.deepcopy(cfg)
        c.setdefault("signals", {})["weights"] = wts
        tasks.append(("signal_weights", name, c))

    # Ticker-level exit params: overwrite the field in every nested ticker_groups spec.
    nested = {g: spec for g, spec in (cfg.get("ticker_groups") or {}).items()
              if isinstance(spec, dict) and "tickers" in spec}
    if nested:
        def add_ticker(param, label, points, fmt, field):
            groups.append((param, label))
            baseline_marks[param] = "as-configured"
            for v in points:
                c = copy.deepcopy(cfg)
                for spec in c["ticker_groups"].values():
                    if isinstance(spec, dict) and "tickers" in spec:
                        spec[field] = v
                tasks.append((param, fmt(v), c))

        add_ticker("tk_stop_loss", "Ticker Stop-Loss (all names)", [0.05, 0.075, 0.10, 0.15],
                   lambda v: f"{v:.1%}", "stop_loss")
        add_ticker("tk_take_profit", "Ticker Take-Profit (all names)", [None, 0.15, 0.20, 0.30],
                   lambda v: "off" if v is None else f"{v:.0%}", "take_profit")
        add_ticker("tk_trailing_stop", "Ticker Trailing-Stop (all names)", [None, 0.10, 0.15],
                   lambda v: "off" if v is None else f"{v:.0%}", "trailing_stop")
        add_ticker("tk_max_holding_days", "Ticker Max-Holding (all names)", [15, 30, 60],
                   lambda v: f"{int(v)}d", "max_holding_days")

    return tasks, groups, baseline_marks, bool(nested)


def _scenario_sensitivity_section(results, metrics, groups, baseline_marks) -> str:
    """Render the scenario ## Sensitivity Analysis block (run-wide + ticker-level)."""
    from collections import defaultdict

    if not results:
        return "## Sensitivity Analysis\n\n_Sensitivity analysis produced no results._\n"

    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in results:
        grouped[r["parameter"]].append(r)
    b = metrics

    col_header = "| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |"
    col_div = "|-------|--------|--------|--------|--------|--------|----------|-----|"

    def _row(r, base):
        mark = " ◀ baseline" if base else ""
        pf = _b_pf(r["profit_factor"]) if r.get("profit_factor") is not None else "—"
        return (f"| {r['value']}{mark} | {_b_pct(r.get('total_return'), '—')} "
                f"| {_b_pct(r.get('excess_vs_spy'), '—')} | {_b_pct(r.get('excess_vs_equal_weight'), '—')} "
                f"| {_b_pct(r.get('max_drawdown'), '—')} | {r.get('total_trades', '—')} "
                f"| {_b_pct(r.get('win_rate'), '—')} | {pf} |")

    base_row = {"value": "as-configured", "total_return": b.get("total_return"),
                "excess_vs_spy": b.get("excess_vs_spy"),
                "excess_vs_equal_weight": b.get("excess_vs_equal_weight"),
                "max_drawdown": b.get("max_drawdown"), "total_trades": b.get("n_trades"),
                "win_rate": b.get("win_rate"), "profit_factor": b.get("profit_factor")}

    lines = [
        "## Sensitivity Analysis", "",
        "> One parameter is varied at a time; everything else stays at the scenario's configured "
        "values. **Run-wide** params apply to the whole backtest. **Ticker** params overwrite that "
        "exit field for *every* `ticker_groups` name at once — a uniform stand-in for the per-ticker "
        "mix, with the real heterogeneous config shown as the `as-configured` baseline row.",
        "> In-sample only — do not pick parameters off these tables; see Robustness Notes.", "",
        f"**Baseline (as configured):** {_b_pct(b.get('total_return'))} return  |  "
        f"{_b_pct(b.get('max_drawdown'))} max drawdown  |  {_b_pct(b.get('win_rate'))} win rate  |  "
        f"{_b_pf(b.get('profit_factor'))} profit factor", "",
    ]

    runwide = [(k, l) for k, l in groups if not k.startswith("tk_")]
    tickerg = [(k, l) for k, l in groups if k.startswith("tk_")]

    if runwide:
        lines += ["### Run-wide parameters", ""]
    for k, label in runwide:
        rows = grouped.get(k, [])
        if not rows:
            continue
        bm = baseline_marks.get(k)
        lines += [f"#### {label}  (baseline: {bm})", "", col_header, col_div]
        for r in rows:
            lines.append(_row(r, r["value"] == bm))
        lines.append("")

    if tickerg:
        lines += ["### Ticker-level exit parameters (applied uniformly to all names)", ""]
    for k, label in tickerg:
        rows = grouped.get(k, [])
        if not rows:
            continue
        lines += [f"#### {label}", "", col_header, col_div, _row(base_row, True)]
        for r in rows:
            lines.append(_row(r, False))
        lines.append("")

    sortable = sorted([r for r in results if r.get("total_return") is not None],
                      key=lambda r: r["total_return"], reverse=True)
    rh = "| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |"
    rd = "|------|-----------|-------|--------|--------|--------|-----|"

    def _rr(i, r):
        pf = _b_pf(r["profit_factor"]) if r.get("profit_factor") is not None else "—"
        return (f"| {i} | {r['parameter']} | {r['value']} | {_b_pct(r.get('total_return'), '—')} "
                f"| {_b_pct(r.get('excess_vs_equal_weight'), '—')} | {_b_pct(r.get('max_drawdown'), '—')} | {pf} |")

    lines += ["### Best 5 Variants by Total Return", "", rh, rd]
    for i, r in enumerate(sortable[:5], 1):
        lines.append(_rr(i, r))
    lines.append("")
    worst = list(reversed(sortable[-5:])) if len(sortable) >= 5 else list(reversed(sortable))
    lines += ["### Worst 5 Variants by Total Return", "", rh, rd]
    for i, r in enumerate(worst, 1):
        lines.append(_rr(i, r))
    lines += ["", "### Robustness Notes", "", _robustness_commentary(results, b.get("total_return", 0.0)), ""]
    return "\n".join(lines)


# ─── Runner ───────────────────────────────────────────────────────────────────


def _pct(v: Optional[float], d: str = "—") -> str:
    return d if v is None else f"{v * 100:+.2f}%"


def run_scenario(name: str, start_date: date, end_date: date, charts: bool = True,
                 sensitivity: bool = True, status: bool = True) -> Dict[str, str]:
    setup_logging()
    run_date = date.today()
    root = Path(__file__).parent.parent
    base = load_config(root / "config")
    scenario = load_scenario(name)
    cfg = build_config(base, scenario)

    log.info("=== Scenario '%s': %d tickers ===", name, len(cfg.get("tickers", [])))
    price_data = fetch_backtest_data(cfg["tickers"], start_date, end_date)

    sink: List[Dict[str, Any]] = []
    trades, equity, positions = run_backtest(cfg, price_data, start_date, end_date, signal_sink=sink)
    metrics = compute_metrics(trades, equity, positions, cfg, start_date, end_date)
    diag = compute_diagnostics(cfg, price_data, trades, equity, positions, sink, metrics,
                               start_date, end_date)
    diag_md = render_diagnostics_md(diag, cfg)
    body = generate_backtest_report(metrics, cfg, trades, equity, positions, run_date,
                                    diagnostics_md=diag_md)
    header = (f"# Scenario — {scenario.get('name', name)}\n\n"
              f"{scenario.get('description', '').strip()}\n\n"
              f"**Universe ({len(cfg['tickers'])}):** {', '.join(cfg['tickers'])}\n\n---\n\n")
    report = header + body

    # Sensitivity analysis: run-wide params + per-ticker exit params (one-way sweep).
    sens_results = None
    if sensitivity:
        tasks, sgroups, baseline_marks, has_ticker = _scenario_sensitivity_tasks(cfg)
        log.info("Running scenario sensitivity: %d variants (run-wide + %s ticker-level)…",
                 len(tasks), "with" if has_ticker else "no")
        sens_results = _execute_sensitivity_tasks(tasks, price_data, start_date, end_date)
        report += "\n\n" + _scenario_sensitivity_section(sens_results, metrics, sgroups, baseline_marks)

    reports_dir, backtests_dir = root / "reports", root / "backtests"
    reports_dir.mkdir(parents=True, exist_ok=True)
    backtests_dir.mkdir(parents=True, exist_ok=True)
    tag = f"{name}_{run_date.isoformat()}"
    md = reports_dir / f"scenario_{tag}.md"
    md.write_text(report)
    trades_csv = backtests_dir / f"scenario_{tag}_trades.csv"
    trades.to_csv(trades_csv, index=False)
    equity.to_csv(backtests_dir / f"scenario_{tag}_equity.csv", index=False)
    diagnostics_csv(diag).to_csv(backtests_dir / f"scenario_{tag}_diagnostics.csv", index=False)
    if sens_results:
        import pandas as pd
        pd.DataFrame(sens_results).to_csv(backtests_dir / f"scenario_{tag}_sensitivity.csv", index=False)

    # Per-ticker annotated charts (buy/sell + reasons vs hold), reusing the fetched panel.
    chart_dir = None
    if charts and not trades.empty:
        try:
            import scenario_charts
            chart_dir = reports_dir / f"charts_{tag}"
            n = len(scenario_charts.make_charts(trades_csv, chart_dir, name, close=price_data["Close"],
                                                price_data=price_data, config=cfg))
            log.info("Wrote %d per-ticker charts to %s", n, chart_dir)
        except Exception as exc:                       # charts are a nicety; never fail the run
            log.warning("Chart generation skipped: %s", exc)
            chart_dir = None

    # Status & rank report (midday signal-strength snapshot), reusing this run's data.
    status_md = None
    if status:
        try:
            import rank_report
            d = rank_report.build_report(name, start_date, end_date,
                                         cfg=cfg, pdata=price_data, eq=equity, positions=positions)
            status_md = reports_dir / f"status_{tag}.md"
            status_md.write_text(rank_report.render_md(d))
            rank_report.ranking_csv(d).to_csv(backtests_dir / f"status_{tag}.csv", index=False)
            log.info("Wrote status & rank report: signal strength %s",
                     _pct(d.get("signal_strength")))
        except Exception as exc:                        # status is a nicety; never fail the run
            log.warning("Status report skipped: %s", exc)
            status_md = None

    print()
    print(f"  Scenario     : {scenario.get('name', name)}  ({len(cfg['tickers'])} tickers)")
    print(f"  Period       : {start_date} → {end_date}")
    print(f"  Total Return : {_pct(metrics.get('total_return'))}  (IRR {_pct(metrics.get('irr'))})")
    print(f"  Equal-Wt Hold: {_pct(metrics.get('equal_weight_return'))}   "
          f"SPY {_pct(metrics.get('spy_return'))}   QQQ {_pct(metrics.get('qqq_return'))}")
    print(f"  Max Drawdown : {_pct(metrics.get('max_drawdown'))}")
    print(f"  Beat EW-Hold : {'YES' if (metrics.get('total_return') or -9) > (metrics.get('equal_weight_return') or 9) else 'no'}")
    print()
    print(f"  Report : {md}")
    if status_md is not None:
        print(f"  Status : {status_md}  (rank + signal-strength snapshot)")
    if chart_dir is not None:
        print(f"  Charts : {chart_dir}  (per-ticker price + buy/sell reasons vs hold)")
    print()
    out = {"report": str(md)}
    if status_md is not None:
        out["status"] = str(status_md)
    if chart_dir is not None:
        out["charts"] = str(chart_dir)
    return out


# ─── CLI ──────────────────────────────────────────────────────────────────────


def main() -> None:
    p = argparse.ArgumentParser(description="AI Paper Trader — run a named scenario")
    p.add_argument("name", nargs="?", help="scenario name (see config/scenarios/)")
    p.add_argument("--start", metavar="YYYY-MM-DD")
    p.add_argument("--end", metavar="YYYY-MM-DD")
    p.add_argument("--list", action="store_true", help="list available scenarios and exit")
    p.add_argument("--no-charts", action="store_true", help="skip per-ticker annotated charts")
    p.add_argument("--no-sensitivity", action="store_true", help="skip the sensitivity analysis section")
    p.add_argument("--no-status", action="store_true", help="skip the status & rank report")
    args = p.parse_args()

    if args.list or not args.name:
        print("Available scenarios:", ", ".join(list_scenarios()) or "none")
        return
    if not (args.start and args.end):
        print("Error: --start and --end are required")
        sys.exit(1)
    try:
        start_date = date.fromisoformat(args.start)
        end_date = date.fromisoformat(args.end)
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)
    if end_date <= start_date:
        print("Error: --end must be after --start")
        sys.exit(1)
    run_scenario(args.name, start_date, end_date, charts=not args.no_charts,
                 sensitivity=not args.no_sensitivity, status=not args.no_status)


if __name__ == "__main__":
    main()
