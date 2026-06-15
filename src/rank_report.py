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


def _win_ret(series: pd.Series, anchor: pd.Timestamp) -> Optional[float]:
    s = series[series.index <= anchor]
    if s.empty:
        return None
    a = float(s.iloc[-1])
    return float(series.iloc[-1]) / a - 1 if a else None


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

    # ranking as of the last completed close
    sl = pdata.loc[:rank_close].iloc[-_SIGNAL_WINDOW:]
    rf = rank_candidates(calculate_signals(sl, uni), top_n=len(uni),
                         weights=weights, ticker_weights=tw).reset_index(drop=True)

    # current held book + portfolio stats (reuse the scenario run's results if given)
    if eq is None or positions is None:
        _, eq, positions = run_backtest(cfg, pdata, start, end)
    held = set(positions["ticker"]) if not positions.empty else set()
    pv = float(eq["total_portfolio_value"].iloc[-1])
    cash = float(eq["cash"].iloc[-1])
    starting = float(cfg["portfolio"]["starting_value"])

    rows = []
    for i, r in rf.iterrows():
        t = r["ticker"]
        rows.append({
            "rank": i + 1, "ticker": t, "score": float(r["composite_score"]),
            "clears_gate": (min_score is None or r["composite_score"] >= min_score),
            "rank_close_px": float(close.loc[rank_close, t]) if t in close.columns else None,
            "mark_px": float(close.loc[mark, t]) if t in close.columns else None,
            "return": ret(t), "held": t in held,
        })
    n = len(rows)
    rets = [x["return"] for x in rows if x["return"] is not None]
    held_rets = [ret(t) for t in held if ret(t) is not None]
    advancers = sum(1 for r in rets if r > 0)
    top_avg = (sum(x["return"] for x in rows[:top_n] if x["return"] is not None) / top_n) if n else None
    bot_avg = (sum(x["return"] for x in rows[-top_n:] if x["return"] is not None) / top_n) if n else None
    signal_strength = (top_avg - bot_avg) if (top_avg is not None and bot_avg is not None) else None
    n_gate = sum(1 for x in rows if x["clears_gate"])
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
        "univ_avg": (sum(rets) / len(rets)) if rets else None,
        "top_avg": top_avg, "bot_avg": bot_avg, "signal_strength": signal_strength,
        "advancers": advancers, "n_gate": n_gate,
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
        "> Composite-momentum ranking of the scenario universe as of the last completed close "
        "(the bar that sets up the next session's open), each name marked to the latest price. "
        "`Return` = ranking-close → latest. ✓ = clears the buy gate.",
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

    def tbl(title, rows, avg):
        out = [f"## {title}", "",
               f"| # | Ticker | Score | Gate | {d['rank_close']} | {d['mark']} | Return | Held |",
               "|---|--------|------:|:----:|------:|------:|-------:|:----:|"]
        for r in rows:
            out.append(
                f"| {r['rank']} | {r['ticker']} | {r['score']:.3f} | {'✓' if r['clears_gate'] else '—'} "
                f"| {r['rank_close_px']:.2f} | {r['mark_px']:.2f} | {_pct(r['return'])} "
                f"| {'HELD' if r['held'] else ''} |")
        out += [f"| | | | | | | **AVG {_pct(avg)}** | |", ""]
        return out

    rows = d["rows"]
    L += tbl(f"Top {tn} (highest buy scores)", rows[:tn], d["top_avg"])
    L += tbl(f"Bottom {tn} (lowest buy scores)", rows[-tn:], d["bot_avg"])

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
