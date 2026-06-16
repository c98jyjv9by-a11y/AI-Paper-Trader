"""
cli.py — Single entry point for every AI Paper Trader runner.

Usage:
    python run.py <command> [options]      # from the repo root (recommended)
    python src/cli.py <command> [options]  # equivalent

Commands:
    backtest            Walk-forward backtest + diagnostics + sensitivity
    experiments         Strategy experiment profiles (signal/exit variants)
    ticker-experiments  Grouped ticker-override experiments + capital-matched BH test
    calibrate           Per-ticker single-name timing vs buy-and-hold (walk-forward)
    evaluate            Apply a fixed ticker criteria file, score timed vs buy-and-hold
    active              Ticker-level active-vs-BH grid + eligible-ticker portfolio (train/test OOS)
    screen              Factor screen — rank candidate signals by out-of-sample predictive power
    suite               Run the whole stack once → ONE consolidated summary report
    scenario            Run a named scenario (trimmed universe + per-ticker rules)
    rank                Rank a scenario's universe as of the last close → dated Markdown report
    adaptive            Adaptive per-ticker rotating-signal backtest (weekly signal rotation)
    agent               Run the LIVE daily paper-trading agent (mutates data/)

Each command also remains runnable on its own (e.g. `python src/backtest.py ...`);
this dispatcher just centralises them behind one front door.
"""
import argparse
import sys
from datetime import date
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).parent))


def _dates(args: argparse.Namespace) -> tuple:
    try:
        start_date = date.fromisoformat(args.start)
        end_date = date.fromisoformat(args.end)
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)
    if end_date <= start_date:
        print("Error: --end must be after --start")
        sys.exit(1)
    return start_date, end_date


# ─── Command handlers (modules imported lazily so unused deps don't load) ─────


def _cmd_backtest(args: argparse.Namespace) -> None:
    import backtest
    s, e = _dates(args)
    backtest.run(s, e, Path(args.output) if args.output else None)


def _cmd_experiments(args: argparse.Namespace) -> None:
    import experiments
    s, e = _dates(args)
    experiments.run(s, e, Path(args.output) if args.output else None)


def _cmd_ticker_experiments(args: argparse.Namespace) -> None:
    import ticker_experiments
    s, e = _dates(args)
    ticker_experiments.run(s, e)


def _cmd_calibrate(args: argparse.Namespace) -> None:
    import signal_calibration
    s, e = _dates(args)
    signal_calibration.run(s, e, objective=args.objective)


def _cmd_evaluate(args: argparse.Namespace) -> None:
    import signal_calibration
    s, e = _dates(args)
    root = Path(__file__).parent.parent
    criteria = Path(args.criteria) if args.criteria else root / "config" / "ticker_timing_criteria.yaml"
    signal_calibration.run_evaluate(s, e, criteria)


def _cmd_active(args: argparse.Namespace) -> None:
    import active_experiment
    try:
        ts, te = date.fromisoformat(args.train_start), date.fromisoformat(args.train_end)
        vs, ve = date.fromisoformat(args.test_start), date.fromisoformat(args.test_end)
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)
    if te <= ts or ve <= vs:
        print("Error: each --*-end must be after its --*-start")
        sys.exit(1)
    active_experiment.run(ts, te, vs, ve)


def _cmd_screen(args: argparse.Namespace) -> None:
    import signal_screen
    try:
        ts, te = date.fromisoformat(args.train_start), date.fromisoformat(args.train_end)
        vs, ve = date.fromisoformat(args.test_start), date.fromisoformat(args.test_end)
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)
    if te <= ts or ve <= vs:
        print("Error: each --*-end must be after its --*-start")
        sys.exit(1)
    signal_screen.run(ts, te, vs, ve)


def _cmd_suite(args: argparse.Namespace) -> None:
    import research_suite
    try:
        ts, te = date.fromisoformat(args.train_start), date.fromisoformat(args.train_end)
        vs, ve = date.fromisoformat(args.test_start), date.fromisoformat(args.test_end)
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)
    if te <= ts or ve <= vs:
        print("Error: each --*-end must be after its --*-start")
        sys.exit(1)
    research_suite.run(ts, te, vs, ve)


def _cmd_scenario(args: argparse.Namespace) -> None:
    import scenarios
    if args.list or not args.name:
        print("Available scenarios:", ", ".join(scenarios.list_scenarios()) or "none")
        return
    if not (args.start and args.end):
        print("Error: --start and --end are required (or use --list)")
        sys.exit(1)
    s, e = _dates(args)
    scenarios.run_scenario(args.name, s, e, charts=not args.no_charts,
                           sensitivity=not args.no_sensitivity, status=not args.no_status)


def _cmd_rank(args: argparse.Namespace) -> None:
    import rank_report
    end = date.fromisoformat(args.end) if args.end else date.today()
    start = date.fromisoformat(args.start) if args.start else date(end.year, 1, 1)
    if end <= start:
        print("Error: --end must be after --start")
        sys.exit(1)
    rank_report.run(args.scenario, start, end, args.top)


def _cmd_adaptive(args: argparse.Namespace) -> None:
    import adaptive_backtest
    s, e = _dates(args)
    adaptive_backtest.run(s, e, args.rebalance_days, args.lookback_days, args.top_n,
                          charts=not args.no_charts)


def _cmd_agent(args: argparse.Namespace) -> None:
    import main as agent
    agent.main()


# ─── Parser ───────────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="paper-trader",
        description="AI Paper Trader — unified runner. Paper trading only; no live orders.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def _add_dates(sp: argparse.ArgumentParser, with_output: bool = False) -> None:
        sp.add_argument("--start", required=True, metavar="YYYY-MM-DD")
        sp.add_argument("--end", required=True, metavar="YYYY-MM-DD")
        if with_output:
            sp.add_argument("--output", default=None, metavar="DIR",
                            help="Output directory (default: backtests/)")

    b = sub.add_parser("backtest", help="Walk-forward backtest + diagnostics + sensitivity")
    _add_dates(b, with_output=True)
    b.set_defaults(func=_cmd_backtest)

    e = sub.add_parser("experiments", help="Strategy experiment profiles")
    _add_dates(e, with_output=True)
    e.set_defaults(func=_cmd_experiments)

    t = sub.add_parser("ticker-experiments",
                       help="Grouped ticker-override experiments + capital-matched buy-and-hold test")
    _add_dates(t)
    t.set_defaults(func=_cmd_ticker_experiments)

    c = sub.add_parser("calibrate",
                       help="Per-ticker single-name timing vs buy-and-hold (walk-forward)")
    _add_dates(c)
    c.add_argument("--objective", default="total_return",
                   choices=("total_return", "sharpe", "calmar"),
                   help="What the train-window grid search maximises (default: total_return)")
    c.set_defaults(func=_cmd_calibrate)

    ev = sub.add_parser("evaluate",
                        help="Apply a fixed ticker criteria file and score timed vs buy-and-hold (no re-fitting)")
    _add_dates(ev)
    ev.add_argument("--criteria", default=None, metavar="FILE",
                    help="criteria YAML (default: config/ticker_timing_criteria.yaml)")
    ev.set_defaults(func=_cmd_evaluate)

    ac = sub.add_parser("active",
                        help="Ticker-level active-vs-buy-and-hold grid + eligible-ticker portfolio (train/test OOS)")
    ac.add_argument("--train-start", required=True, metavar="YYYY-MM-DD")
    ac.add_argument("--train-end", required=True, metavar="YYYY-MM-DD")
    ac.add_argument("--test-start", required=True, metavar="YYYY-MM-DD")
    ac.add_argument("--test-end", required=True, metavar="YYYY-MM-DD")
    ac.set_defaults(func=_cmd_active)

    sc = sub.add_parser("screen",
                        help="Factor screen: rank candidate signals by out-of-sample predictive power (rank-IC)")
    sc.add_argument("--train-start", required=True, metavar="YYYY-MM-DD")
    sc.add_argument("--train-end", required=True, metavar="YYYY-MM-DD")
    sc.add_argument("--test-start", required=True, metavar="YYYY-MM-DD")
    sc.add_argument("--test-end", required=True, metavar="YYYY-MM-DD")
    sc.set_defaults(func=_cmd_screen)

    su = sub.add_parser("suite",
                        help="Run the whole stack once → one consolidated summary report")
    su.add_argument("--train-start", required=True, metavar="YYYY-MM-DD")
    su.add_argument("--train-end", required=True, metavar="YYYY-MM-DD")
    su.add_argument("--test-start", required=True, metavar="YYYY-MM-DD")
    su.add_argument("--test-end", required=True, metavar="YYYY-MM-DD")
    su.set_defaults(func=_cmd_suite)

    scn = sub.add_parser("scenario",
                         help="Run a named scenario (trimmed universe + per-ticker rules), e.g. davids_model")
    scn.add_argument("name", nargs="?", help="scenario name (see config/scenarios/; omit with --list)")
    scn.add_argument("--start", metavar="YYYY-MM-DD")
    scn.add_argument("--end", metavar="YYYY-MM-DD")
    scn.add_argument("--list", action="store_true", help="list available scenarios and exit")
    scn.add_argument("--no-charts", action="store_true", help="skip the auto per-ticker charts")
    scn.add_argument("--no-sensitivity", action="store_true", help="skip the sensitivity analysis section")
    scn.add_argument("--no-status", action="store_true", help="skip the auto status & rank report")
    scn.set_defaults(func=_cmd_scenario)

    rk = sub.add_parser("rank",
                        help="Rank a scenario's universe as of the last close → dated Markdown report")
    rk.add_argument("scenario", help="scenario name (see config/scenarios/)")
    rk.add_argument("--start", metavar="YYYY-MM-DD", help="backtest start (default: Jan 1 of end's year)")
    rk.add_argument("--end", metavar="YYYY-MM-DD", help="end date (default: today)")
    rk.add_argument("--top", type=int, default=10, help="top/bottom N to show (default 10)")
    rk.set_defaults(func=_cmd_rank)

    ad = sub.add_parser("adaptive",
                        help="Adaptive per-ticker rotating-signal backtest (weekly, holds the recently-best signal per name)")
    _add_dates(ad)
    ad.add_argument("--rebalance-days", type=int, default=None, help="rebalance cadence (default 5)")
    ad.add_argument("--lookback-days", type=int, default=None, help="recent-edge window (default 63)")
    ad.add_argument("--top-n", type=int, default=None, help="max focus tickers (default 5)")
    ad.add_argument("--no-charts", action="store_true", help="skip the auto per-ticker charts")
    ad.set_defaults(func=_cmd_adaptive)

    a = sub.add_parser("agent", help="Run the LIVE daily paper-trading agent (mutates data/)")
    a.set_defaults(func=_cmd_agent)

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
