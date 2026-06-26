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
    experiments.run(s, e, Path(args.output) if args.output else None,
                    scenario=getattr(args, "scenario", None))


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
    e.add_argument("--scenario", default=None,
                   help="optional: overlay config/scenarios/<name>.yaml (universe + rules) first")
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

    af = sub.add_parser("account-freeze",
                        help="Freeze a scenario's trades+state over a window into an immutable account ledger")
    af.add_argument("--name", required=True, help="account name (e.g. primary)")
    af.add_argument("--scenario", required=True, help="scenario to freeze (e.g. model_v4)")
    af.add_argument("--start", required=True, metavar="YYYY-MM-DD")
    af.add_argument("--end", required=True, metavar="YYYY-MM-DD")
    af.add_argument("--force", action="store_true", help="re-freeze, overwriting an existing frozen account")
    af.add_argument("--no-promote", action="store_true", help="don't mark this account as the active/primary one")
    af.set_defaults(func=_cmd_account_freeze)

    as_ = sub.add_parser("account-seed",
                         help="Create a fresh live account funded with cash, buying a model's current top-N names")
    as_.add_argument("--name", required=True, help="account name (e.g. tracker)")
    as_.add_argument("--scenario", required=True, help="model to trail (e.g. model_v4)")
    as_.add_argument("--cash", type=float, default=100_000.0, help="starting cash (default 100000)")
    as_.add_argument("--top", type=int, default=3, help="how many top-ranked names to buy (default 3)")
    as_.add_argument("--per-name-pct", type=float, help="position size per name as a fraction (default: model's max_position_pct)")
    as_.add_argument("--as-of", metavar="YYYY-MM-DD", help="rank/buy as of this close (default: latest)")
    as_.add_argument("--force", action="store_true", help="overwrite an existing account")
    as_.add_argument("--promote", action="store_true", help="mark this account as active/primary")
    as_.set_defaults(func=_cmd_account_seed)

    av = sub.add_parser("account-verify",
                        help="Verify a frozen account's files still match their manifest hashes")
    av.add_argument("--name", required=True, help="account name")
    av.set_defaults(func=_cmd_account_verify)

    ak = sub.add_parser("account-continue",
                        help="Extend a frozen account forward (living continuation), seeded from its latest state")
    ak.add_argument("--name", required=True, help="account name")
    ak.add_argument("--end", required=True, metavar="YYYY-MM-DD", help="extend the account through this date")
    ak.add_argument("--scenario", help="model to trade forward with (default: the account's base; pass the current model to 'follow active')")
    ak.set_defaults(func=_cmd_account_continue)

    eo = sub.add_parser("eod", help="Render the end-of-day PDF (from --account ledger, or a fresh --scenario run)")
    eo.add_argument("--account", help="render from a frozen/living account ledger")
    eo.add_argument("--scenario", help="scenario (required if no --account)")
    eo.add_argument("--start", metavar="YYYY-MM-DD")
    eo.add_argument("--end", metavar="YYYY-MM-DD")
    eo.add_argument("--prepost", action="store_true",
                    help="mark the latest bar to the after-hours print (live session only)")
    eo.add_argument("--out")
    eo.set_defaults(func=_cmd_eod)

    md = sub.add_parser("midday", help="Render the intraday Midday Pulse PDF (from --account ledger, or a fresh --scenario run)")
    md.add_argument("--account", help="render the held book from a frozen/living account ledger")
    md.add_argument("--scenario", help="scenario (required if no --account)")
    md.add_argument("--start", metavar="YYYY-MM-DD")
    md.add_argument("--end", metavar="YYYY-MM-DD", help="the in-progress day to mark to (default: today)")
    md.add_argument("--prepost", action="store_true",
                    help="mark the book to the latest extended-hours (pre/post-market) print")
    md.add_argument("--out")
    md.set_defaults(func=_cmd_midday)

    ms = sub.add_parser("midday-summary",
                        help="One consolidated Midday Pulse summary across the model_v4 scenario + the broker accounts (topten/copymodel/rampup)")
    ms.add_argument("--end", metavar="YYYY-MM-DD", help="the in-progress day to mark to (default: today)")
    ms.add_argument("--accounts", nargs="*", help="override the default account list (topten/copymodel/rampup)")
    ms.add_argument("--prepost", action="store_true",
                    help="mark books to the latest extended-hours (pre/post-market) print")
    ms.add_argument("--no-pdf", action="store_true", help="summary only; skip each book's midday PDF")
    ms.add_argument("--out")
    ms.set_defaults(func=_cmd_midday_summary)

    es = sub.add_parser("eod-summary",
                        help="One consolidated End-of-Day summary across the model_v4 scenario + the broker accounts (topten/copymodel/rampup)")
    es.add_argument("--end", metavar="YYYY-MM-DD", help="the close to mark to (default: today)")
    es.add_argument("--accounts", nargs="*", help="override the default account list (topten/copymodel/rampup)")
    es.add_argument("--prepost", action="store_true",
                    help="mark books to the latest extended-hours (pre/post-market) print")
    es.add_argument("--no-pdf", action="store_true", help="summary only; skip each book's EOD PDF")
    es.add_argument("--out")
    es.set_defaults(func=_cmd_eod_summary)

    sn = sub.add_parser("snapshot",
                        help="One-page PDF performance snapshot (total return + vs-benchmark) across model_v4 + the Alpaca accounts")
    sn.add_argument("--end", metavar="YYYY-MM-DD", help="as-of date (default: today)")
    sn.add_argument("--window", default="1D",
                    help="window for the return + P&L columns: 1D (default), 5D/10D/1M/3M/6M/1Y, MTD, YTD, or an int of trading days")
    sn.add_argument("--accounts", nargs="*", help="override the default account list (topten/copymodel/rampup)")
    sn.add_argument("--out")
    sn.set_defaults(func=_cmd_snapshot)

    ic = sub.add_parser("intraday-check",
                        help="One-shot intraday trade check: live overlay signals (rebound/hedge) + dry-run account plans")
    ic.add_argument("--accounts", nargs="+", help="override the default account list (topten/copymodel/rampup)")
    ic.add_argument("--qqq", type=float, help="rebound what-if: override QQQ 1-day return")
    ic.add_argument("--spread", type=float, help="rebound what-if: override momentum spread")
    ic.add_argument("--vol-z", type=float, help="rebound what-if: override QQQ vol z")
    ic.add_argument("--extended-hours", action="store_true", help="extended-hours marketable-limit plan")
    ic.add_argument("--summary", action="store_true", help="also print the cross-book midday table")
    ic.set_defaults(func=_cmd_intraday_check)

    ea = sub.add_parser("eod-accounts",
                        help="Consolidated EOD PDF: daily activity + P&L for all broker accounts, with strategy descriptions")
    ea.add_argument("--accounts", nargs="+", help="override the account list (default: all 6 broker accounts)")
    ea.add_argument("--end", metavar="YYYY-MM-DD", help="as-of date for fills/labels (default: today)")
    ea.add_argument("--out", help="output PDF path (default reports/eod_accounts_<date>.pdf)")
    ea.set_defaults(func=_cmd_eod_accounts)

    oh = sub.add_parser("order-history",
                        help="Combined PDF: each account's full Alpaca order history + positions + P&L (realized/unrealized)")
    oh.add_argument("--accounts", nargs="+", help="override the account list (default: all broker accounts)")
    oh.add_argument("--status", default="all", choices=["all", "closed", "open"],
                    help="which orders to include (default: all)")
    oh.add_argument("--end", metavar="YYYY-MM-DD", help="as-of date for the title/filename (default: today)")
    oh.add_argument("--limit", type=int, default=500, help="max orders pulled per account (default: 500)")
    oh.add_argument("--prepost", action="store_true",
                    help="mark positions + benchmark to the latest extended-hours (pre/post-market) print")
    oh.add_argument("--out", help="output PDF path (default reports/account_orders_<date>.pdf)")
    oh.set_defaults(func=_cmd_order_history)

    return parser


def _cmd_account_freeze(args: argparse.Namespace) -> None:
    import account
    try:
        man = account.freeze(args.name, args.scenario,
                             date.fromisoformat(args.start), date.fromisoformat(args.end),
                             force=args.force, promote=not args.no_promote)
    except FileExistsError as e:
        print(f"Error: {e}")
        sys.exit(1)
    print(f"Froze account '{man['name']}' ({man['scenario']}) {man['inception']} → {man['frozen_through']}")
    print(f"  ending value {man['ending_value']:,.0f}  ·  return {man['total_return']*100:+.2f}%  "
          f"·  {man['n_trades']} trades  ·  {man['n_positions']} open positions")
    print(f"  wrote accounts/{man['name']}/ (ledger + reports + {len(man['rankings_copied'])} ranking snapshots)"
          + ("  ·  promoted to ACTIVE" if not args.no_promote else ""))


def _cmd_account_seed(args: argparse.Namespace) -> None:
    import account
    try:
        man = account.seed(args.name, args.scenario, cash=args.cash, top_n=args.top,
                           per_name_pct=args.per_name_pct,
                           as_of=date.fromisoformat(args.as_of) if args.as_of else None,
                           force=args.force, promote=args.promote)
    except FileExistsError as e:
        print(f"Error: {e}")
        sys.exit(1)
    print(f"Seeded account '{man['name']}' trailing {man['scenario']} — ${man['seed']['cash']:,.0f} as of {man['inception']}")
    for p in man["seed"]["picks"]:
        print(f"  BUY {p['ticker']:6} score {p['score']:.3f}  @ {p['close']:.2f}")
    print(f"  invested {man['n_positions']} names at {man['seed']['per_name_pct']:.1%}/name  ·  book value ${man['ending_value']:,.0f}")
    print(f"  → extend it daily with:  python run.py account-continue --name {man['name']} --end <date> --scenario {man['scenario']}")


def _cmd_account_verify(args: argparse.Namespace) -> None:
    import account
    r = account.verify(args.name)
    if r["intact"]:
        print(f"Account '{r['name']}' INTACT — {len(r['ok'])} files match the manifest "
              f"(frozen through {r['frozen_through']}).")
    else:
        print(f"Account '{r['name']}' DRIFTED:")
        for f in r["drift"]:
            print(f"  CHANGED: {f}")
        for f in r["missing"]:
            print(f"  MISSING: {f}")
        sys.exit(1)


def _cmd_account_continue(args: argparse.Namespace) -> None:
    import account
    try:
        r = account.continue_account(args.name, date.fromisoformat(args.end), scenario=args.scenario)
    except (FileNotFoundError, RuntimeError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    if r.get("noop"):
        print(f"Nothing to do — '{args.name}' already live through {r['live_through']} "
              f"(requested {r['requested_end']}).")
        return
    print(f"Extended '{args.name}' with {r['scenario']}: {r['from']} → {r['to']}  "
          f"({r['n_trades']} new trades)")
    print(f"  live through {r['live_through']}  ·  value {r['live_value']:,.0f}  ·  {r['segments']} segment(s)")


def _cmd_eod(args: argparse.Namespace) -> None:
    import pdf_report
    if not args.account and not args.scenario:
        print("Error: pass --account or --scenario")
        sys.exit(1)
    out = pdf_report.run(args.scenario,
                         date.fromisoformat(args.start) if args.start else None,
                         date.fromisoformat(args.end) if args.end else None,
                         Path(args.out) if args.out else None, account=args.account,
                         prepost=args.prepost)
    print(f"Wrote {out}")


def _cmd_midday(args: argparse.Namespace) -> None:
    import midday_pdf
    if not args.account and not args.scenario:
        print("Error: pass --account or --scenario")
        sys.exit(1)
    out = midday_pdf.run(args.scenario,
                         date.fromisoformat(args.start) if args.start else None,
                         date.fromisoformat(args.end) if args.end else None,
                         Path(args.out) if args.out else None, account=args.account,
                         prepost=args.prepost)
    print(f"Wrote {out}")


def _cmd_midday_summary(args: argparse.Namespace) -> None:
    import midday_summary
    out, rows = midday_summary.run(
        end=date.fromisoformat(args.end) if args.end else None,
        output=Path(args.out) if args.out else None,
        accounts=args.accounts or None,
        prepost=args.prepost, want_pdf=not args.no_pdf)
    ok = sum(1 for r in rows if not r.get("error"))
    print(f"Wrote {out}  ({ok}/{len(rows)} books)")
    for r in rows:
        if r.get("error"):
            print(f"  ! {r['label']}: {r['error']}")


def _cmd_eod_summary(args: argparse.Namespace) -> None:
    import eod_summary
    out, rows = eod_summary.run(
        end=date.fromisoformat(args.end) if args.end else None,
        output=Path(args.out) if args.out else None,
        accounts=args.accounts or None, prepost=args.prepost, want_pdf=not args.no_pdf)
    ok = sum(1 for r in rows if not r.get("error"))
    print(f"Wrote {out}  ({ok}/{len(rows)} books)")
    for r in rows:
        if r.get("error"):
            print(f"  ! {r['label']}: {r['error']}")


def _cmd_intraday_check(args: argparse.Namespace) -> None:
    import intraday_check
    intraday_check.run(getattr(args, "accounts", None), args.qqq, args.spread, args.vol_z,
                       args.extended_hours, args.summary)


def _cmd_eod_accounts(args: argparse.Namespace) -> None:
    import eod_accounts
    r = eod_accounts.run(accounts=getattr(args, "accounts", None), end=args.end, out=args.out)
    print("wrote", r["pdf"])


def _cmd_order_history(args: argparse.Namespace) -> None:
    import account_orders_report
    r = account_orders_report.run(accounts=getattr(args, "accounts", None), end=args.end,
                                  out=args.out, status=args.status, limit=args.limit,
                                  prepost=getattr(args, "prepost", False))
    ok = sum(1 for d in r["data"].values() if not d.get("err"))
    print("wrote %s  (%d/%d accounts live)" % (r["pdf"], ok, len(r["data"])))


def _cmd_snapshot(args: argparse.Namespace) -> None:
    import snapshot
    out, rows = snapshot.run(
        end=date.fromisoformat(args.end) if args.end else None,
        output=Path(args.out) if args.out else None,
        accounts=args.accounts or None, window=args.window)
    ok = sum(1 for r in rows if not r.get("error"))
    print(f"Wrote {out}  ({ok}/{len(rows)} books)")
    for r in rows:
        if r.get("error"):
            print(f"  ! {r['label']}: {r['error']}")


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
