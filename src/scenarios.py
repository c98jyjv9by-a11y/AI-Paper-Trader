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
)
from diagnostics import compute_diagnostics, diagnostics_csv, render_diagnostics_md
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


# ─── Runner ───────────────────────────────────────────────────────────────────


def _pct(v: Optional[float], d: str = "—") -> str:
    return d if v is None else f"{v * 100:+.2f}%"


def run_scenario(name: str, start_date: date, end_date: date) -> Dict[str, str]:
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

    reports_dir, backtests_dir = root / "reports", root / "backtests"
    reports_dir.mkdir(parents=True, exist_ok=True)
    backtests_dir.mkdir(parents=True, exist_ok=True)
    tag = f"{name}_{run_date.isoformat()}"
    md = reports_dir / f"scenario_{tag}.md"
    md.write_text(report)
    trades.to_csv(backtests_dir / f"scenario_{tag}_trades.csv", index=False)
    equity.to_csv(backtests_dir / f"scenario_{tag}_equity.csv", index=False)
    diagnostics_csv(diag).to_csv(backtests_dir / f"scenario_{tag}_diagnostics.csv", index=False)

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
    print()
    return {"report": str(md)}


# ─── CLI ──────────────────────────────────────────────────────────────────────


def main() -> None:
    p = argparse.ArgumentParser(description="AI Paper Trader — run a named scenario")
    p.add_argument("name", nargs="?", help="scenario name (see config/scenarios/)")
    p.add_argument("--start", metavar="YYYY-MM-DD")
    p.add_argument("--end", metavar="YYYY-MM-DD")
    p.add_argument("--list", action="store_true", help="list available scenarios and exit")
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
    run_scenario(args.name, start_date, end_date)


if __name__ == "__main__":
    main()
