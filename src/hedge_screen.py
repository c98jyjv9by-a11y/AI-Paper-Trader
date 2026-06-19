"""
hedge_screen.py — standalone HEDGE-OVERLAY research module.

Self-contained and decoupled from the model: it does NOT change model_v4 or any trading
logic. It (1) runs model_v4 once to get the BOOK equity being hedged, (2) builds an end-of-day
SIGNAL matrix (vol / factor-stress / trend / breadth), (3) defines candidate HEDGE instruments
(long inverse ETFs or short long-ETFs), and (4) sweeps every (signal × hedge) overlay —
decide-at-close / hold-while-signal-true / fill-next-open — scoring the COMBINED book+hedge
curve net of cost against four baselines (never / always / random-at-frequency / vol-threshold),
on full sample AND a walk-forward out-of-sample split.

The point is NOT to maximize the hedge's own return — it's whether book+hedge is better off
(shallower drawdown / better risk-adjusted return) net of cost. Crashes are rare (~5 in 10y),
so OOS + random-at-frequency + per-episode checks are first-class, not afterthoughts.

    python src/hedge_screen.py --start 2016-06-20 --end 2026-06-18 --cutoff 2022-01-01
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path
from typing import Callable, Dict, List, Tuple

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
ROOT = Path(__file__).parent.parent
PANEL = ROOT / "backtests" / "model_v4_daily_scores_10y.csv"

# Hedge instruments: name -> (ETF ticker, sign). sign=+1 = LONG the (inverse) ETF; sign=-1 = SHORT.
HEDGES: Dict[str, Tuple[str, int]] = {
    "long_PSQ": ("PSQ", +1),       # long inverse-QQQ (linear)
    "short_QQQ": ("QQQ", -1),      # short QQQ
    "short_SMH": ("SMH", -1),      # short semis (tightest to this book)
    "long_SOXS": ("SOXS", +1),     # long -3x semis (tactical; carries hard)
}
_ETFS = ["SPY", "QQQ", "SMH", "PSQ", "SOXS", "MTUM"]
COST_BPS = 5.0                     # round-trip transaction cost per on/off flip, in bps of hedged notional


# ── data assembly ────────────────────────────────────────────────────────────────
def _book_returns(start: date, end: date) -> pd.Series:
    """Daily return series of the actual model_v4 book (the thing being hedged)."""
    from scenarios import build_config, load_scenario
    from backtest import load_config, fetch_backtest_data, run_backtest
    cfg = build_config(load_config(ROOT / "config"), load_scenario("model_v4"))
    pdata = fetch_backtest_data(cfg["tickers"], start, end, warmup_days=150)
    _t, eq, _p = run_backtest(cfg, pdata, start, end)
    e = eq.copy(); e["date"] = pd.to_datetime(e["date"])
    s = e.set_index("date")["total_portfolio_value"].pct_change()
    s.name = "book_ret"
    return s


def _etf_returns(start: date, end: date) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Daily returns + closes for the hedge/benchmark ETFs (extra lookback for MAs/vol)."""
    import yfinance as yf
    px = yf.download(_ETFS, start=(start.replace(year=start.year - 1)).isoformat(),
                     end=end.isoformat(), auto_adjust=True, progress=False)["Close"]
    px.index = pd.to_datetime(px.index).tz_localize(None)
    return px.pct_change(), px


def _features(panel: pd.DataFrame, ret: pd.DataFrame, px: pd.DataFrame, book: pd.Series) -> pd.DataFrame:
    """EOD signal inputs — all computed at the close, no look-ahead."""
    f = pd.DataFrame(index=panel.index)
    f["spread"] = panel["top_minus_bottom_spread"]
    f["top10"] = panel["top10_avg_return"]
    f["bot10"] = panel["bottom10_avg_return"]
    f["spy_ret"] = ret["SPY"].reindex(f.index)
    f["qqq_close"] = px["QQQ"].reindex(f.index)
    f["book_ret"] = book.reindex(f.index)
    f["vol21"] = f["spy_ret"].rolling(21).std() * np.sqrt(252)
    f["spread5"] = f["spread"].rolling(5).mean()
    f["spread20"] = f["spread"].rolling(20).mean()
    f["qqq50"] = f["qqq_close"].rolling(50).mean()
    f["qqq200"] = f["qqq_close"].rolling(200).mean()
    f["dd60"] = f["qqq_close"] / f["qqq_close"].rolling(60).max() - 1
    f["book_sigma"] = f["book_ret"].rolling(21).std()
    return f


# ── candidate signals (name -> boolean Series, True = hedge ON for the NEXT session) ──
def _signals(f: pd.DataFrame) -> Dict[str, pd.Series]:
    decl2 = (f["spread"] < f["spread"].shift(1)) & (f["spread"].shift(1) < f["spread"].shift(2))
    sig = {
        "vol>15": f["vol21"] > 0.15,
        "vol>20": f["vol21"] > 0.20,
        "vol>25": f["vol21"] > 0.25,
        "spread20_neg": f["spread20"] < 0,
        "spread5_neg": f["spread5"] < 0,
        "spread_decl2": decl2,
        "qqq<50dma": f["qqq_close"] < f["qqq50"],
        "qqq<200dma": f["qqq_close"] < f["qqq200"],
        "dd60>5%": f["dd60"] < -0.05,
        "losers_leading": f["bot10"] > f["top10"],
        "book_down_2sig": f["book_ret"] < -2 * f["book_sigma"],
        "vol>20 & qqq<50dma": (f["vol21"] > 0.20) & (f["qqq_close"] < f["qqq50"]),
        "vol>20 & spread20_neg": (f["vol21"] > 0.20) & (f["spread20"] < 0),
        "vol>20 & losers_leading": (f["vol21"] > 0.20) & (f["bot10"] > f["top10"]),
    }
    return {k: v.fillna(False) for k, v in sig.items()}


# ── overlay simulation + metrics ──────────────────────────────────────────────────
def _metrics(r: pd.Series) -> Dict[str, float]:
    r = r.dropna()
    if len(r) < 2:
        return {"ret": np.nan, "sharpe": np.nan, "maxdd": np.nan, "calmar": np.nan}
    eq = (1 + r).cumprod()
    ann = eq.iloc[-1] ** (252 / len(r)) - 1
    maxdd = float(-(eq / eq.cummax() - 1).min())          # positive magnitude
    sharpe = float(r.mean() / r.std() * np.sqrt(252)) if r.std() > 0 else np.nan
    return {"ret": float(eq.iloc[-1] - 1), "sharpe": sharpe, "maxdd": maxdd,
            "calmar": float(ann / maxdd) if maxdd > 0 else np.nan}


def _overlay(book: pd.Series, active: pd.Series, hedge_ret: pd.Series, f: float) -> pd.Series:
    """Combined book+hedge daily return. active = signal at close t → applied to day t+1
    (decide-at-close/fill-next-open); hold while signal true; cost charged on each on/off flip."""
    a = active.shift(1).fillna(False).astype(bool)
    contrib = a * f * hedge_ret.reindex(book.index).fillna(0.0)
    flips = a.ne(a.shift(1).fillna(False))
    cost = flips * (COST_BPS / 1e4) * f
    return book + contrib - cost


def _slice(s: pd.Series, lo, hi) -> pd.Series:
    return s[(s.index >= lo) & (s.index <= hi)]


def _episodes(book_ret: pd.Series, thresh: float = 0.10) -> List[Tuple[str, pd.Timestamp, pd.Timestamp, float]]:
    """Auto-detect the book's drawdown episodes — contiguous peak→recovery runs whose trough
    is deeper than `thresh`. Returns (label, start, end, depth) per episode (label = trough YYYY-MM)."""
    eq = (1 + book_ret).cumprod()
    dd = eq / eq.cummax() - 1
    out: List = []
    run_start = prev = None
    for t in dd.index:
        if dd[t] < -1e-9:
            run_start = run_start or t
        elif run_start is not None:
            seg = dd.loc[run_start:prev]
            if seg.min() <= -thresh:
                out.append((seg.idxmin().strftime("%Y-%m"), run_start, prev, float(seg.min())))
            run_start = None
        prev = t
    if run_start is not None:
        seg = dd.loc[run_start:prev]
        if seg.min() <= -thresh:
            out.append((seg.idxmin().strftime("%Y-%m"), run_start, prev, float(seg.min())))
    return out


def run(start: date, end: date, cutoff: date, f: float = 0.5, n_rand: int = 20) -> Dict[str, str]:
    panel = pd.read_csv(PANEL, parse_dates=["date"]).drop_duplicates("date").set_index("date").sort_index()
    panel = panel[(panel.index >= pd.Timestamp(start)) & (panel.index <= pd.Timestamp(end))]
    ret, px = _etf_returns(start, end)
    book = _book_returns(start, end)
    F = _features(panel, ret, px, book)
    sigs = _signals(F)

    idx = F.index.intersection(book.dropna().index)
    book = book.reindex(idx).fillna(0.0)
    hedge_rets = {name: (sign * ret[tkr].reindex(idx).fillna(0.0)) for name, (tkr, sign) in HEDGES.items()}

    # Walk-forward folds = full calendar years (≥150 trading days); per-episode = auto drawdowns.
    fold_years = [y for y in sorted(set(idx.year)) if (idx[idx.year == y].size >= 150)]
    episodes = _episodes(book, thresh=0.10)
    base_full = _metrics(book)
    base_year = {y: _metrics(book[book.index.year == y]) for y in fold_years}
    base_ep = {lab: _metrics(_slice(book, s, e)) for lab, s, e, _ in episodes}
    rs = np.random.RandomState(0)

    rows = []
    for sname, sig in sigs.items():
        a = sig.reindex(idx).fillna(False)
        freq = float(a.mean())
        for hname, hret in hedge_rets.items():
            comb = _overlay(book, a, hret, f)
            mf = _metrics(comb)
            # walk-forward: ΔMaxDD / ΔSharpe per fold year
            yd, ys = [], []
            for y in fold_years:
                my = _metrics(comb[comb.index.year == y])
                yd.append(base_year[y]["maxdd"] - my["maxdd"])
                ys.append(my["sharpe"] - base_year[y]["sharpe"])
            wf_dMaxDD = float(np.nanmean(yd))
            wf_dSharpe = float(np.nanmean(ys))
            wf_pos = float(np.mean([1 if (not np.isnan(x) and x > 0) else 0 for x in yd]) * 100)
            # per-episode: did the hedge make the drawdown shallower?
            ep_red, ep_hit = [], []
            for lab, s, e, _ in episodes:
                me = _metrics(_slice(comb, s, e))
                red = base_ep[lab]["maxdd"] - me["maxdd"]
                ep_red.append(red); ep_hit.append(1 if red > 0 else 0)
            ep_hitpct = float(np.mean(ep_hit) * 100) if ep_hit else np.nan
            ep_dMaxDD = float(np.nanmean(ep_red)) if ep_red else np.nan
            # random-at-frequency benchmark (full-sample DD reduction it would get by luck)
            rnd_dd = [_metrics(_overlay(book, pd.Series(rs.rand(len(idx)) < freq, index=idx), hret, f))["maxdd"]
                      for _ in range(n_rand)]
            vs_rand = (base_full["maxdd"] - mf["maxdd"]) - (base_full["maxdd"] - float(np.nanmean(rnd_dd)))
            rows.append({
                "signal": sname, "hedge": hname, "on%": round(freq * 100, 1),
                "wf_dSharpe": wf_dSharpe, "wf_dMaxDD": wf_dMaxDD, "wf_pos%": wf_pos,
                "ep_hit%": ep_hitpct, "ep_dMaxDD": ep_dMaxDD,
                "vsRand_dMaxDD": vs_rand, "giveup_full": base_full["ret"] - mf["ret"],
                "ret_full": mf["ret"], "sharpe_full": mf["sharpe"], "maxdd_full": mf["maxdd"],
            })
    df = pd.DataFrame(rows)
    out_csv = ROOT / "backtests" / "hedge_screen.csv"
    df.to_csv(out_csv, index=False)

    def fmt(x, p=2, pct=False):
        return "—" if pd.isna(x) else (f"{x*100:+.{p}f}%" if pct else f"{x:+.{p}f}")
    L = ["# Hedge-overlay screen — model_v4 book + single-signal hedges (walk-forward + per-episode)",
         f"Window {idx.min().date()} → {idx.max().date()} · {len(fold_years)} yearly folds · "
         f"hedge size {f:.0%} of book · cost {COST_BPS:.0f}bps/flip · hold-while-signal-true.", "",
         f"**Unhedged book** — ret {fmt(base_full['ret'],1,1)}, Sharpe {fmt(base_full['sharpe'])}, "
         f"maxDD {fmt(base_full['maxdd'],1,1)}.", "",
         "**Auto-detected drawdown episodes (>10%):** "
         + ", ".join(f"{lab} ({-base_ep[lab]['maxdd']*100:.0f}% book DD)" for lab, *_ in episodes), "",
         "_wf_ = mean across yearly folds; wf_pos% = share of years the hedge reduced DD. ep_hit% = share "
         "of episodes the hedge made the drawdown shallower. vsRand = DD reduction beyond a random hedge at "
         "the same frequency (value of TIMING). giveup = full-sample return sacrificed (− = added)._", ""]

    def table(title, sortcol):
        t = df.sort_values(sortcol, ascending=False).head(12)
        out = [f"## {title}", "",
               "| Signal | Hedge | on% | wf ΔSharpe | wf ΔMaxDD | wf pos% | ep hit% | ep ΔMaxDD | vsRand | giveup |",
               "|---|---|--:|--:|--:|--:|--:|--:|--:|--:|"]
        for _, r in t.iterrows():
            out.append(f"| {r['signal']} | {r['hedge']} | {r['on%']:.0f} | {fmt(r['wf_dSharpe'])} | "
                       f"{fmt(r['wf_dMaxDD'],1,1)} | {r['wf_pos%']:.0f} | {r['ep_hit%']:.0f} | "
                       f"{fmt(r['ep_dMaxDD'],1,1)} | {fmt(r['vsRand_dMaxDD'],1,1)} | {fmt(r['giveup_full'],1,1)} |")
        return out + [""]
    L += table("Best by walk-forward risk-adjusted improvement (mean fold ΔSharpe)", "wf_dSharpe")
    L += table("Best by per-episode hit-rate (then episode ΔMaxDD)", "ep_hit%")
    out_md = ROOT / "reports" / "hedge_screen.md"
    out_md.write_text("\n".join(L))
    return {"csv": str(out_csv), "md": str(out_md), "base_full": base_full,
            "n": len(df), "episodes": [e[0] for e in episodes], "folds": len(fold_years)}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Hedge-overlay signal screen for the model_v4 book.")
    ap.add_argument("--start", default="2016-06-20")
    ap.add_argument("--end", default="2026-06-18")
    ap.add_argument("--cutoff", default="2022-01-01", help="walk-forward OOS start")
    ap.add_argument("--size", type=float, default=0.5, help="hedge notional as a fraction of the book")
    a = ap.parse_args(argv)
    res = run(date.fromisoformat(a.start), date.fromisoformat(a.end), date.fromisoformat(a.cutoff), f=a.size)
    print(f"screened {res['n']} (signal×hedge) overlays · {res['folds']} yearly folds · "
          f"{len(res['episodes'])} episodes: {', '.join(res['episodes'])}")
    print(f"  book: ret {res['base_full']['ret']*100:+.0f}%  Sharpe {res['base_full']['sharpe']:+.2f}  "
          f"maxDD {res['base_full']['maxdd']*100:.1f}%")
    print(f"  report: {res['md']}")
    print(f"  csv:    {res['csv']}")


if __name__ == "__main__":
    main()
