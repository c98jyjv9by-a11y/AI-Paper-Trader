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


def _sc(x):
    return "—" if x is None else f"{x:.2f}"


ROOT = Path(__file__).parent.parent

_WINDOWS = (1, 5, 20, 60)


def _trend_label(avg):
    """Classify a name's composite-score TRAJECTORY from its trailing avg scores (1/5/20/60d).
    Short avg above the medium baseline = momentum building; a monotonic stack = a clean trend."""
    s1, s5, s20 = avg.get(1), avg.get(5), avg.get(20)
    if s5 is None or s20 is None:
        return "—"
    spread = s5 - s20
    if s1 is not None and s1 >= s5 >= s20 and spread > 0.03:
        return "uptrend"
    if s1 is not None and s1 <= s5 <= s20 and spread < -0.03:
        return "downtrend"
    if spread > 0.05:
        return "rising"
    if spread < -0.05:
        return "falling"
    return "flat"


def _build_enrichment(symbols, scenario="model_v4", as_of=None):
    """For each symbol: composite score + cross-sectional rank, trailing 1/5/20/60d AVG score, a trend
    label, and trailing 1/5/20/60d price return. Universe scores come from one score panel; returns from
    one price fetch. Overlay names (TQQQ/SQQQ) aren't in the universe → score/rank/avg show '—'.

    `as_of` (a date) anchors EVERYTHING to that historical session instead of today — the score panel
    ends there, the trailing avgs/trend read the closes up to it, and the returns end on it. Passing the
    entry date thus reconstructs exactly what the same analytics looked like WHEN A POSITION WAS OPENED
    (same scoring/trend logic, just a different endpoint). Default None = live/today."""
    import pandas as pd
    import broker_sync as bs
    from backtest import fetch_backtest_data
    from datetime import date, timedelta
    end = as_of or date.today()
    panel = bs._score_panel(scenario, 60, as_of=as_of)          # rows = sessions, cols = universe tickers
    last = panel.iloc[-1]
    ranked = last.sort_values(ascending=False)
    rank_of = {t: i + 1 for i, t in enumerate(ranked.index)}
    n_uni = int(last.notna().sum())
    px = fetch_backtest_data(list(dict.fromkeys(symbols)),
                             end - timedelta(days=160), end)["Close"]

    def _avg(t, w):
        if t not in panel.columns:
            return None
        s = panel[t].dropna()
        return float(s.tail(w).mean()) if len(s) else None

    def _ret(t, w):
        if t not in getattr(px, "columns", []):
            return None
        s = px[t].dropna()
        if len(s) < w + 1:
            return None
        return float(s.iloc[-1] / s.iloc[-(w + 1)] - 1)

    out = {}
    for t in dict.fromkeys(symbols):
        score = float(last[t]) if (t in last.index and pd.notna(last[t])) else None
        avg = {w: _avg(t, w) for w in _WINDOWS}
        out[t] = {"score": score, "rank": rank_of.get(t), "n_uni": n_uni,
                  "avg": avg, "trend": _trend_label(avg),
                  "ret": {w: _ret(t, w) for w in _WINDOWS}}
    return out


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
    plans, all_syms, errs = [], [], {}
    for acct in accounts:
        try:
            res = bs.submit_session(acct, submit=False, extended=True, log=False)   # read-only preview
            plans.append((acct, res))
            all_syms += [o["symbol"] for o in res.get("orders", [])]
        except Exception as exc:
            errs[acct] = exc

    enrich = {}
    if all_syms:                                                        # only pay for the panel/price fetch
        try:                                                           # when something actually trades
            enrich = _build_enrichment(all_syms)
        except Exception as exc:
            print(f"  (per-ticker analytics unavailable — {exc}; showing reason only)")

    for acct in accounts:
        if acct in errs:
            print(f"  {acct}: ERROR — {errs[acct]}")
            continue
        res = next(r for a, r in plans if a == acct)
        print(f"  {acct}: {res['n_orders']} order(s)")
        for o in res.get("orders", []):
            pl, sym = o["_plan"], o["symbol"]
            print("    %-4s %-6s %-5s  %-7s $%-9.2f  collar %.1f%%  ~$%s"
                  % (o["side"].upper(), sym, o["qty"], pl.get("tif", o["time_in_force"]),
                     o["limit_price"], pl["collar"] * 100, f'{pl["est_value"]:,.0f}'))
            e = enrich.get(sym)
            if e:
                rank = f"#{e['rank']}/{e['n_uni']}" if e.get("rank") else "—"
                avg = "/".join(_sc(e["avg"][w]) for w in _WINDOWS)
                ret = "/".join(_pct(e["ret"][w]) for w in _WINDOWS)
                print("         score %s  rank %s  trend %-9s  avg-score 1/5/20/60d %s  ret 1/5/20/60d %s"
                      % (_sc(e["score"]), rank, e["trend"], avg, ret))
            dec = o.get("_decision") or {}
            reason = dec.get("reason")
            if reason:
                extra = []
                if dec.get("z") is not None:
                    extra.append(f"z {dec['z']:+.2f}")
                if dec.get("pnl") is not None:
                    extra.append(f"realized P&L ${dec['pnl']:,.2f}")
                print("         reason: %s%s" % (reason, ("  [" + ", ".join(extra) + "]") if extra else ""))
        for sup in res.get("suppressed", []):
            print("    HOLD %-6s %d→%d  (%+d-share trim suppressed — churn deadband)"
                  % (sup["symbol"], sup["current"], sup["target"], sup["delta"]))
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
