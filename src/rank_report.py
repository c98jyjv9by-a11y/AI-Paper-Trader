"""
rank_report.py — Daily ranking snapshot for a scenario, as a standard Markdown report.

Ranks a scenario's full universe by composite score **as of the last completed close**
(the bar that sets up the next session's open), marks each name to the latest available
price, and reports the top/bottom N, group averages, the current held book, and portfolio
performance vs SPY/QQQ. Read-only w.r.t. live state; writes to reports/ and backtests/.

    python run.py rank model_v2                       # YTD window, top/bottom 10
    python run.py rank model_v2 --start 2026-01-01 --end 2026-06-15 --top 15
"""
import argparse
import logging
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from scenarios import load_scenario, build_config
from backtest import (
    load_config, fetch_backtest_data, run_backtest,
    _build_ticker_weights, _SIGNAL_WINDOW,
)
from signals import calculate_signals, rank_candidates
from logger import setup_logging

log = logging.getLogger(__name__)


def _pct(v: Optional[float], d: str = "—") -> str:
    return d if v is None or (isinstance(v, float) and pd.isna(v)) else f"{v * 100:+.2f}%"


# Intraday checkpoints every 2 hours from open to close, labeled in Chicago Central Time.
# Keys are the underlying 30-min bar timestamps in market tz (America/New_York = CT+1);
# the official close (CT 15:00 / ET 16:00) is handled separately via the daily close.
#   ET 09:30 → CT 08:30 (open) · ET 11:30 → CT 10:30 · ET 13:30 → CT 12:30 · ET 15:30 → CT 14:30
_CHECKPOINTS = [("09:30", "8:30 CT (open)"), ("11:30", "10:30 CT"),
                ("13:30", "12:30 CT"), ("15:30", "14:30 CT")]
_CLOSE_LABEL = "Latest (≈15:00 CT close)"


def intraday_returns(tickers, day, prior_close: Dict[str, float]) -> Optional[Dict[str, Dict[str, float]]]:
    """Return {ticker: {checkpoint: ret_vs_prior_close}} for the given day, using 30-min bars
    (bar Open at each timestamp). None if no intraday data covers `day`."""
    import yfinance as yf
    raw = yf.download(list(tickers), period="5d", interval="30m", progress=False, auto_adjust=True)
    if raw.empty:
        return None
    op = raw["Open"]
    out: Dict[str, Dict[str, float]] = {}
    any_hit = False
    for t in tickers:
        rec: Dict[str, Optional[float]] = {}
        if t in getattr(op, "columns", []):
            s = op[t]
            day_idx = [ts for ts in s.index if ts.date() == day]
            for hhmm, _ in _CHECKPOINTS:
                m = [ts for ts in day_idx if ts.strftime("%H:%M") == hhmm]
                pc = prior_close.get(t)
                if m and pc:
                    px = float(s.loc[m[0]])
                    rec[hhmm] = (px / pc - 1) if px == px else None
                    any_hit = any_hit or rec[hhmm] is not None
                else:
                    rec[hhmm] = None
        out[t] = rec
    return out if any_hit else None


def _win_ret(series: pd.Series, anchor: pd.Timestamp) -> Optional[float]:
    s = series[series.index <= anchor]
    if s.empty:
        return None
    a = float(s.iloc[-1])
    return float(series.iloc[-1]) / a - 1 if a else None


def _ranking_snapshot_path(root: Path, scenario: str, d) -> Path:
    """backtests/rankings_<scenario>_<YYYY-MM-DD>.csv — the authoritative ranking AS OF
    that close. Each run writes its current ranking here; the next day's report reads the
    matching snapshot for its prior-close column instead of recomputing (immune to feed gaps)."""
    tag = d.isoformat() if hasattr(d, "isoformat") else str(d)
    return root / "backtests" / f"rankings_{scenario}_{tag}.csv"


def _load_ranking_snapshot(root: Path, scenario: str, d) -> Optional[List[Dict[str, Any]]]:
    p = _ranking_snapshot_path(root, scenario, d)
    if not p.exists():
        return None
    try:
        df = pd.read_csv(p)
    except Exception:
        return None
    out = []
    for _, r in df.iterrows():
        try:
            out.append({"rank": int(r["rank"]), "ticker": str(r["ticker"]).strip(),
                        "score": float(r["score"]),
                        "gate": str(r.get("gate", "")).strip().lower() in ("yes", "true", "1", "y")})
        except Exception:
            continue
    return out or None


def _write_ranking_snapshot(root: Path, scenario: str, d, ranked_rows) -> None:
    p = _ranking_snapshot_path(root, scenario, d)
    p.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([{"rank": x["rank"], "ticker": x["ticker"], "score": round(x["score"], 4),
                   "gate": "yes" if x["clears_gate"] else "no"} for x in ranked_rows]).to_csv(p, index=False)


def build_report(scenario: str, start: date, end: date, top_n: int = 10,
                 *, cfg: Optional[Dict[str, Any]] = None, pdata: Optional[pd.DataFrame] = None,
                 eq: Optional[pd.DataFrame] = None, positions: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """Build the rank/status snapshot. The scenario run can pass its already-computed
    cfg/pdata/eq/positions to avoid re-fetching and re-running the backtest."""
    root = Path(__file__).parent.parent
    if cfg is None:
        cfg = build_config(load_config(root / "config"), load_scenario(scenario))
    uni = cfg["tickers"]
    weights = cfg["signals"].get("weights")
    tw = _build_ticker_weights(cfg) or None
    min_score = cfg["signals"].get("min_composite_score")

    if pdata is None:
        pdata = fetch_backtest_data(uni, start, end)
    close = pdata["Close"]
    rank_close = close.index[-2]          # last completed close → ranking anchor
    mark = close.index[-1]                # latest available price (may be provisional)

    def ret(t: str) -> Optional[float]:
        if t not in close.columns:
            return None
        a, b = close.loc[rank_close, t], close.loc[mark, t]
        return (b / a - 1) if (a == a and b == b and a > 0) else None

    # (A) ranking as of the last completed close (sets up the session that just happened)
    sl = pdata.loc[:rank_close].iloc[-_SIGNAL_WINDOW:]
    rf = rank_candidates(calculate_signals(sl, uni), top_n=len(uni),
                         weights=weights, ticker_weights=tw).reset_index(drop=True)
    # (B) ranking on the latest/current prices (the standing that sets up the NEXT session)
    sl_cur = pdata.loc[:mark].iloc[-_SIGNAL_WINDOW:]
    rf_cur = rank_candidates(calculate_signals(sl_cur, uni), top_n=len(uni),
                             weights=weights, ticker_weights=tw).reset_index(drop=True)

    # current held book + portfolio stats (reuse the scenario run's results if given)
    if eq is None or positions is None:
        _, eq, positions = run_backtest(cfg, pdata, start, end)
    held = set(positions["ticker"]) if not positions.empty else set()
    pv = float(eq["total_portfolio_value"].iloc[-1])
    cash = float(eq["cash"].iloc[-1])
    starting = float(cfg["portfolio"]["starting_value"])

    def _px(t, ts):
        return float(close.loc[ts, t]) if (t in close.columns and not pd.isna(close.loc[ts, t])) else None

    # Prior-close ranking (Section A). Prefer a saved snapshot for that date (authoritative —
    # what was actually produced, immune to later feed gaps); else recompute from data.
    snap = _load_ranking_snapshot(root, scenario, rank_close.date())
    snapshot_used = bool(snap)
    if snap:
        rows = [{
            "rank": s["rank"], "ticker": s["ticker"], "score": s["score"], "clears_gate": s["gate"],
            "rank_close_px": _px(s["ticker"], rank_close), "mark_px": _px(s["ticker"], mark),
            "return": ret(s["ticker"]), "held": s["ticker"] in held,
        } for s in sorted(snap, key=lambda x: x["rank"])]
    else:
        rows = []
        for i, r in rf.iterrows():
            t = r["ticker"]
            rows.append({
                "rank": i + 1, "ticker": t, "score": float(r["composite_score"]),
                "clears_gate": (min_score is None or r["composite_score"] >= min_score),
                "rank_close_px": _px(t, rank_close), "mark_px": _px(t, mark),
                "return": ret(t), "held": t in held,
            })
    # current-price ranking rows (no forward return — this is the standing right now)
    rows_cur = []
    for i, r in rf_cur.iterrows():
        t = r["ticker"]
        rows_cur.append({
            "rank": i + 1, "ticker": t, "score": float(r["composite_score"]),
            "clears_gate": (min_score is None or r["composite_score"] >= min_score),
            "price": _px(t, mark), "held": t in held,
        })
    # Persist the current ranking as the snapshot for `mark`'s date (becomes the next
    # session's authoritative prior-close ranking).
    try:
        _write_ranking_snapshot(root, scenario, mark.date(), rows_cur)
    except Exception as exc:
        log.warning("Could not write ranking snapshot: %s", exc)
    # rank movement vs the prior-close ranking (for context)
    prior_rank = {x["ticker"]: x["rank"] for x in rows}
    for x in rows_cur:
        x["rank_chg"] = (prior_rank.get(x["ticker"]) - x["rank"]) if x["ticker"] in prior_rank else None

    # intraday return progression (vs prior close) for the top/bottom-N prior-close names
    intraday = None
    try:
        need = ([x["ticker"] for x in rows[:top_n]] + [x["ticker"] for x in rows[-top_n:]]
                + sorted(held))                          # include held positions too
        pc_map = {x["ticker"]: x["rank_close_px"] for x in rows}
        intraday = intraday_returns(sorted(set(need)), mark.date(), pc_map)
    except Exception as exc:                              # intraday is a nicety; never fail the report
        log.warning("Intraday checkpoints skipped: %s", exc)
        intraday = None

    # Universe-level stats over ALL names (price-based, so they stay correct even when the
    # prior-close ranking comes from a partial snapshot).
    uni_rets = [ret(t) for t in uni if ret(t) is not None]
    n = sum(1 for t in uni if t in close.columns)
    rets = uni_rets
    held_rets = [ret(t) for t in held if ret(t) is not None]
    advancers = sum(1 for r in uni_rets if r > 0)
    _tret = [x["return"] for x in rows[:top_n] if x["return"] is not None]
    _bret = [x["return"] for x in rows[-top_n:] if x["return"] is not None]
    top_avg = (sum(_tret) / len(_tret)) if _tret else None
    bot_avg = (sum(_bret) / len(_bret)) if _bret else None
    signal_strength = (top_avg - bot_avg) if (top_avg is not None and bot_avg is not None) else None
    n_gate = sum(1 for _, r in rf.iterrows() if (min_score is None or r["composite_score"] >= min_score))
    # dollar-weighted held-book return over the session
    dw_num = sum(p["shares"] * close.loc[rank_close, p["ticker"]] * (ret(p["ticker"]) or 0.0)
                 for _, p in positions.iterrows() if p["ticker"] in close.columns)
    dw_den = sum(p["shares"] * close.loc[rank_close, p["ticker"]]
                 for _, p in positions.iterrows() if p["ticker"] in close.columns)
    held_dw = (dw_num / dw_den) if dw_den else None

    # portfolio vs benchmarks (trailing windows from the run's equity)
    P = eq.copy(); P["date"] = pd.to_datetime(P["date"]); P = P.set_index("date")["total_portfolio_value"]
    spy, qqq = close["SPY"], close["QQQ"]
    anchors = {"1D": P.index[-2], "5D": P.index[-6] if len(P) >= 6 else P.index[0],
               "MTD": pd.Timestamp(mark.year, mark.month, 1)}
    stats = {w: {"port": _win_ret(P, a), "spy": _win_ret(spy, a), "qqq": _win_ret(qqq, a)}
             for w, a in anchors.items()}
    stats[f"Since {start.isoformat()}"] = {
        "port": pv / starting - 1,
        "spy": float(spy.iloc[-1]) / float(spy[spy.index >= pd.Timestamp(start)].iloc[0]) - 1,
        "qqq": float(qqq.iloc[-1]) / float(qqq[qqq.index >= pd.Timestamp(start)].iloc[0]) - 1,
    }

    return {
        "scenario": scenario, "rank_close": rank_close.date(), "mark": mark.date(),
        "min_score": min_score, "rows": rows, "n": n, "top_n": top_n,
        "snapshot_used": snapshot_used,
        "univ_avg": (sum(rets) / len(rets)) if rets else None,
        "top_avg": top_avg, "bot_avg": bot_avg, "signal_strength": signal_strength,
        "advancers": advancers, "n_gate": n_gate,
        "rows_cur": rows_cur, "n_gate_cur": sum(1 for x in rows_cur if x["clears_gate"]),
        "intraday": intraday,
        "held_avg": (sum(held_rets) / len(held_rets)) if held_rets else None,
        "held_dw": held_dw,
        "positions": positions, "pv": pv, "cash": cash, "ret": ret, "stats": stats,
        "start": start, "end": end,
    }


def render_md(d: Dict[str, Any]) -> str:
    run_date = date.today()
    tn = d["top_n"]
    L = [
        f"# Status & Rank Report — {d['scenario']}",
        f"**Ranked as of close:** {d['rank_close']}  |  **Marked to:** {d['mark']} "
        f"(latest; may be provisional)  |  **Buy gate:** {d['min_score']}  |  "
        f"**Generated:** {run_date.isoformat()}",
        "",
        "> Two rankings, clearly separated: **(A) Prior-close ranking** — composite scores fixed "
        f"at the prior close ({d['rank_close']}) and marked forward to the latest price (shows how "
        "those picks did this session); and **(B) Current ranking** — composite scores recomputed on "
        f"the latest prices ({d['mark']}), i.e. the standing that sets up the next session. ✓ = clears the buy gate.",
        "",
        "## Signal strength (session: ranking-close → latest)",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| **Top {tn} − Bottom {tn} spread** | **{_pct(d['signal_strength'])}** |",
        f"| Top {tn} avg | {_pct(d['top_avg'])} |",
        f"| Bottom {tn} avg | {_pct(d['bot_avg'])} |",
        f"| Universe avg (all {d['n']}) | {_pct(d['univ_avg'])} |",
        f"| Held book (equal-wt / $-wt) | {_pct(d['held_avg'])} / {_pct(d['held_dw'])} |",
        f"| Advancers | {d['advancers']}/{d['n']} |",
        f"| Names clearing buy gate | {d['n_gate']}/{d['n']} |",
        "",
        "_Positive spread ⇒ higher-scored names out-returned lower-scored names this session "
        "(momentum signal working). One session is mostly market beta; read the spread, not the level._",
        "",
    ]

    # ── (A) ranking scored on the PRIOR CLOSE, marked forward to the latest price ──
    def _px2(v):
        return "—" if v is None else f"{v:.2f}"

    def tbl_prior(title, rows, avg):
        out = [f"### {title}", "",
               f"| # | Ticker | Score | Gate | {d['rank_close']} close | {d['mark']} latest | Return | Held |",
               "|---|--------|------:|:----:|------:|------:|-------:|:----:|"]
        for r in rows:
            out.append(
                f"| {r['rank']} | {r['ticker']} | {r['score']:.3f} | {'✓' if r['clears_gate'] else '—'} "
                f"| {_px2(r['rank_close_px'])} | {_px2(r['mark_px'])} | {_pct(r['return'])} "
                f"| {'HELD' if r['held'] else ''} |")
        out += [f"| | | | | | | **AVG {_pct(avg)}** | |", ""]
        return out

    rows = d["rows"]
    _snap_note = (" — _scores loaded from saved ranking snapshot (authoritative for that date)_"
                  if d.get("snapshot_used") else "")
    L += [f"## A) Ranking at PRIOR CLOSE ({d['rank_close']}) — scores fixed at that close, "
          f"marked to the latest price ({d['mark']}, may be intraday){_snap_note}", "",
          "_These are the scores that set up the most recent session; `Return` shows how each "
          "did from the prior close to the latest price (the latest bar may be a provisional "
          "intraday price, not an official close)._", ""]
    L += tbl_prior(f"Top {tn} (highest buy scores @ prior close)", rows[:tn], d["top_avg"])
    L += tbl_prior(f"Bottom {tn} (lowest buy scores @ prior close)", rows[-tn:], d["bot_avg"])

    # intraday progression (return vs prior close at each 2h CT checkpoint; Close = daily close)
    intra = d.get("intraday")
    if intra:
        cps = _CHECKPOINTS
        ret = d["ret"]

        def tbl_intra(title, items):
            # items: list of (ticker, close_return). Header uses CT labels; trailing Close column.
            hdr = "| Ticker | " + " | ".join(lbl for _, lbl in cps) + f" | {_CLOSE_LABEL} |"
            sep = "|--------|" + "------:|" * (len(cps) + 1)
            out = [f"### {title}", "", hdr, sep]
            sums = {hhmm: [0.0, 0] for hhmm, _ in cps}; csum = [0.0, 0]
            for tkr, cl in items:
                rec = intra.get(tkr, {})
                cells = []
                for hhmm, _ in cps:
                    v = rec.get(hhmm)
                    cells.append(_pct(v))
                    if v is not None:
                        sums[hhmm][0] += v; sums[hhmm][1] += 1
                if cl is not None:
                    csum[0] += cl; csum[1] += 1
                out.append(f"| {tkr} | " + " | ".join(cells) + f" | {_pct(cl)} |")
            avg_cells = [_pct(sums[h][0] / sums[h][1]) if sums[h][1] else "—" for h, _ in cps]
            out += ["| **AVG** | " + " | ".join(avg_cells) +
                    f" | {_pct(csum[0] / csum[1]) if csum[1] else '—'} |", ""]
            return out

        L += [f"## A2) Intraday return progression — {d['mark']} (vs prior close {d['rank_close']})", "",
              "_Return from the prior close to each **2-hour checkpoint, Chicago Central Time** "
              "(8:30 open → 15:00 close), using 30-min bars. `Close` is the official daily close. "
              "Watch the spread between the top and bottom AVG rows build through the session._", ""]
        L += tbl_intra(f"Top {tn} @ prior close — intraday path",
                       [(r["ticker"], r["return"]) for r in rows[:tn]])
        L += tbl_intra(f"Bottom {tn} @ prior close — intraday path",
                       [(r["ticker"], r["return"]) for r in rows[-tn:]])
        held_items = sorted((p["ticker"], ret(p["ticker"]))
                            for _, p in d["positions"].iterrows())
        if held_items:
            L += tbl_intra("Held positions — intraday path", held_items)

    # ── (B) ranking scored on the CURRENT/LATEST prices (sets up the NEXT session) ──
    def tbl_cur(title, rows):
        out = [f"### {title}", "",
               f"| # | Ticker | Score | Gate | {d['mark']} px | Δrank vs prior | Held |",
               "|---|--------|------:|:----:|------:|:-------------:|:----:|"]
        for r in rows:
            chg = r.get("rank_chg")
            chg_s = "—" if chg is None else (f"▲{chg}" if chg > 0 else (f"▼{-chg}" if chg < 0 else "•"))
            out.append(
                f"| {r['rank']} | {r['ticker']} | {r['score']:.3f} | {'✓' if r['clears_gate'] else '—'} "
                f"| {r['price']:.2f} | {chg_s} | {'HELD' if r['held'] else ''} |")
        out.append("")
        return out

    rc = d["rows_cur"]; nc = len(rc)
    L += [f"## B) CURRENT composite ranking (scored on latest prices {d['mark']}) — "
          "sets up the next session", "",
          f"_Recomputed on the current/provisional prices. {d['n_gate_cur']}/{nc} names clear the "
          "buy gate now. `Δrank vs prior` = move vs the prior-close ranking (▲ = ranked higher now)._", ""]
    L += tbl_cur(f"Top {tn} (highest buy scores @ current prices)", rc[:tn])
    L += tbl_cur(f"Bottom {tn} (lowest buy scores @ current prices)", rc[-tn:])

    L += ["## Group returns (ranking-close → latest)", "",
          "| Group | Avg return |", "|-------|-----------:|",
          f"| Top {tn} | {_pct(d['top_avg'])} |",
          f"| Universe (all {d['n']}) | {_pct(d['univ_avg'])} |",
          f"| Held book (equal-wt) | {_pct(d['held_avg'])} |",
          f"| Bottom {tn} | {_pct(d['bot_avg'])} |", ""]

    pos = d["positions"]; ret = d["ret"]
    L += [f"## Held book — {len(pos)} positions  (portfolio ${d['pv']:,.0f}, cash ${d['cash']:,.0f})", ""]
    if pos.empty:
        L.append("_No open positions._")
    else:
        L += ["| Ticker | Shares | Entry | Now | Unreal % | Return |",
              "|--------|-------:|------:|----:|---------:|-------:|"]
        for _, p in pos.sort_values("ticker").iterrows():
            u = p["current_price"] / p["entry_price"] - 1
            L.append(f"| {p['ticker']} | {int(p['shares'])} | {p['entry_price']:.2f} "
                     f"| {p['current_price']:.2f} | {_pct(u)} | {_pct(ret(p['ticker']))} |")
    L.append("")

    L += ["## Portfolio vs benchmarks", "",
          "| Window | " + d["scenario"] + " | SPY | QQQ | vs SPY | vs QQQ |",
          "|--------|------:|----:|----:|-------:|-------:|"]
    for w, s in d["stats"].items():
        m, sp, q = s["port"], s["spy"], s["qqq"]
        vs_s = _pct(m - sp) if (m is not None and sp is not None) else "—"
        vs_q = _pct(m - q) if (m is not None and q is not None) else "—"
        L.append(f"| {w} | {_pct(m)} | {_pct(sp)} | {_pct(q)} | {vs_s} | {vs_q} |")
    L += ["",
          "_Ranking is reproducible from price history (composite of 1d/5d/20d returns + volume "
          "ratio); the latest mark may be a provisional intraday bar that settles at the close._", ""]
    return "\n".join(L)


def ranking_csv(d: Dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame([{k: r[k] for k in ("rank", "ticker", "score", "clears_gate",
                                            "rank_close_px", "mark_px", "return", "held")}
                         for r in d["rows"]])


def run(scenario: str, start: date, end: date, top_n: int = 10) -> Dict[str, str]:
    setup_logging()
    root = Path(__file__).parent.parent
    log.info("=== Rank Report: %s ===", scenario)
    d = build_report(scenario, start, end, top_n)
    report = render_md(d)
    (root / "reports").mkdir(parents=True, exist_ok=True)
    (root / "backtests").mkdir(parents=True, exist_ok=True)
    tag = f"{scenario}_{date.today().isoformat()}"
    md = root / "reports" / f"rank_report_{tag}.md"
    md.write_text(report)
    csv = root / "backtests" / f"rank_report_{tag}.csv"
    ranking_csv(d).to_csv(csv, index=False)

    print()
    print(f"  Scenario  : {scenario}  (ranked {d['rank_close']} → marked {d['mark']})")
    print(f"  Top {top_n} avg : {_pct(d['top_avg'])}   Bottom {top_n} avg : {_pct(d['bot_avg'])}"
          f"   Universe : {_pct(d['univ_avg'])}")
    print(f"  Report    : {md}")
    print(f"  CSV       : {csv}")
    print()
    return {"report": str(md), "csv": str(csv)}


def main() -> None:
    p = argparse.ArgumentParser(description="AI Paper Trader — scenario rank report")
    p.add_argument("scenario")
    p.add_argument("--start", metavar="YYYY-MM-DD")
    p.add_argument("--end", metavar="YYYY-MM-DD")
    p.add_argument("--top", type=int, default=10, help="top/bottom N to show (default 10)")
    args = p.parse_args()
    end = date.fromisoformat(args.end) if args.end else date.today()
    start = date.fromisoformat(args.start) if args.start else date(end.year, 1, 1)
    run(args.scenario, start, end, args.top)


if __name__ == "__main__":
    main()
