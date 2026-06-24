"""
intraday_check.py — one-shot intraday trade-determination check.

Prints, for the current session, in one go:
  1. LIVE overlay signals — does the REBOUND (buy TQQQ) or the HEDGE (buy SQQQ) fire, and how big.
  2. The DRY-RUN order plan for each live account (the model_v4 reconcile + any overlay buy with its
     cash / 2-exit rotation funding) — what you'd actually submit right now.
  3. (optional, --summary) the cross-book midday table (PV / day return / held-DW per book).

Read-only — submits NOTHING. The model's own entries/exits are decide-at-close, so the intraday-
actionable part is the overlays + the reconcile plan shown here.

    python src/intraday_check.py
    python src/intraday_check.py --accounts topten rampup --extended-hours
    python src/intraday_check.py --qqq -0.03 --spread -0.02 --vol-z 1.0    # rebound what-if
    python src/intraday_check.py --summary                                  # + cross-book midday table
"""
import argparse
import sys
import warnings
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
warnings.filterwarnings("ignore")

DEFAULT_ACCOUNTS = ["topten", "copymodel", "rampup"]


def _pct(x):
    return "—" if x is None else f"{x * 100:+.2f}%"


ROOT = Path(__file__).parent.parent


def _persistence_live(scenario="model_v4"):
    """Persistence-buy candidates scored LIVE over the last `score_entry_days` closes — INCLUDING today's
    intraday bar. The panel's last row is the provisional/latest print when the market is open, and
    rank_report's cross-sectional scorer recomputes each day's composite, so today's intraday score counts
    toward the >threshold streak (vs the old snapshot version, which only saw completed closes)."""
    import rank_report as rr
    from backtest import load_config, fetch_backtest_data
    from scenarios import load_scenario, build_config
    from datetime import date, timedelta
    cfg = build_config(load_config(ROOT / "config"), load_scenario(scenario))
    end = date.today()
    pdata = fetch_backtest_data(cfg["tickers"], end - timedelta(days=500), end)
    thr = float(cfg["risk"].get("score_entry_above", 0.90))
    days = int(cfg["risk"].get("score_entry_days", 3))
    cands = rr._persistence_candidates(pdata, cfg, set(), thr, days)   # held=∅ → show every qualifier
    return cands, thr, days, pdata["Close"].index[-1]


def run(accounts=None, qqq=None, spread=None, vol_z=None, extended=False, summary=False):
    accounts = accounts or DEFAULT_ACCOUNTS
    print(f"\n=== INTRADAY CHECK — {date.today().isoformat()} ===\n")

    # ── 1. live overlay signals ──────────────────────────────────────────────
    print("OVERLAY SIGNALS")
    whatif = " (WHAT-IF override)" if (qqq is not None or spread is not None or vol_z is not None) else ""
    try:
        import rebound_overlay as ro
        r = ro.recommend(down_override=qqq, signal_override=spread, volz_override=vol_z, live=True)
        head = f"FIRE ({r['tier']})" if r["fires"] else "idle (no trigger)"
        print(f"  Rebound (TQQQ, traded by accounts): {head}{whatif}   [{r.get('source')}]")
        print(f"     QQQ {_pct(r['qqq_down'])} · signal {_pct(r['signal'])} · QQQ-vol-z {r['vol_z']:+.2f}"
              f"     gate: QQQ≤−2.5% & signal<0 & vol-z≥0.25")
    except Exception as exc:
        print(f"  Rebound: ERROR — {exc}")
    try:
        import hedge_overlay as ho
        h = ho.recommend()                              # panel-based signal; informational (scenario only)
        head = f"FIRE ({h['tier']})" if h["fires"] else "idle (no trigger)"
        print(f"  Hedge (SQQQ, model_v4 scenario only): {head}")
        print(f"     QQQ {_pct(h['qqq_up'])} · SPY-vol-z {h['vol_z']:+.2f}"
              f"     gate: QQQ≥+1.5% & vol-z≥0.75")
    except Exception as exc:
        print(f"  Hedge: ERROR — {exc}")
    if whatif:
        print("  (what-if overrides affect this SIGNAL line only — the account plans below always use the "
              "real live state)")
    print()

    # ── persistence-buy candidates (composite >= threshold for N closes, incl. today intraday) ──
    print("PERSISTENCE-BUY CANDIDATES  (composite >= entry threshold for N consecutive closes, incl. today)")
    try:
        cands, thr, days, asof = _persistence_live()
        print("  " + (", ".join(cands) if cands else "none")
              + f"    (>= {thr:.2f} for {days} closes through {asof.date()} INCL. today's intraday bar;"
              + " the model buys the UNHELD ones, subject to funding + the 2-trades/day cap)")
    except Exception as exc:
        print(f"  ERROR — {exc}")
    print()

    # ── 2. dry-run order plans (what you'd submit now) ───────────────────────
    print("ACCOUNT PLANS — DRY-RUN, nothing sent  (fill-ASAP marketable; overlay TQQQ exit stays at close)")
    import broker_sync as bs
    for acct in accounts:
        try:
            res = bs.submit_session(acct, submit=False, extended=True)   # preview the fill-ASAP default
            print(f"  {acct}: {res['n_orders']} order(s)")
            for o in res.get("orders", []):
                pl = o["_plan"]
                print("    %-4s %-6s %-5s  %-7s $%-9.2f  collar %.1f%%  ~$%s"
                      % (o["side"].upper(), o["symbol"], o["qty"], pl.get("tif", o["time_in_force"]),
                         o["limit_price"], pl["collar"] * 100, f'{pl["est_value"]:,.0f}'))
        except Exception as exc:
            print(f"  {acct}: ERROR — {exc}")
    print()

    # ── 3. optional cross-book midday summary ────────────────────────────────
    if summary:
        print("CROSS-BOOK MIDDAY SUMMARY")
        try:
            import midday_summary as ms
            for rrow in ms.build_summary(accounts=accounts, want_pdf=False):
                if rrow.get("error"):
                    print(f"  {rrow['label']}: ERROR"); continue
                d = rrow.get("day") or {}
                print("  %-30s PV $%-11s  day %s  held-DW %s  #pos %d"
                      % (rrow["label"], f"{rrow.get('pv', 0):,.0f}", _pct(d.get("port")),
                         _pct(rrow.get("held_dw")), rrow.get("n_positions", 0)))
        except Exception as exc:
            print(f"  summary ERROR — {exc}")
        print()
    print("(read-only. to act: add  --submit --extended-hours  with BROKER_ADAPTER_ALLOW_SUBMIT=yes "
          "on broker_sync.py)\n")


def main(argv=None):
    p = argparse.ArgumentParser(description="Intraday trade-determination check: overlay signals + dry-run plans")
    p.add_argument("--accounts", nargs="+", default=DEFAULT_ACCOUNTS)
    p.add_argument("--qqq", type=float, help="rebound what-if: override QQQ 1-day return (e.g. -0.03)")
    p.add_argument("--spread", type=float, help="rebound what-if: override momentum spread (e.g. -0.02)")
    p.add_argument("--vol-z", type=float, help="rebound what-if: override QQQ vol z (e.g. 1.0)")
    p.add_argument("--extended-hours", action="store_true", help="extended-hours marketable-limit plan")
    p.add_argument("--summary", action="store_true", help="also print the cross-book midday table")
    a = p.parse_args(argv)
    run(a.accounts, a.qqq, a.spread, a.vol_z, a.extended_hours, a.summary)


if __name__ == "__main__":
    main()
