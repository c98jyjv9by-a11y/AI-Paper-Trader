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

    a = sub.add_parser("agent", help="Run the LIVE daily paper-trading agent (mutates data/)")
    a.set_defaults(func=_cmd_agent)

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
