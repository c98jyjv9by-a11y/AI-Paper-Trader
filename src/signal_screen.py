"""
signal_screen.py — Factor discovery: which candidate signals actually predict?

The momentum composite used by the strategy has ~zero cross-sectional predictive
power (quintile spread ≈ 0). Before building ANY new strategy, this tool screens a
LIBRARY of candidate factors for forward-return predictiveness — no trading, no
exit rules, just "does ranking tickers by this factor sort future winners from
losers?" — measured in-sample AND out-of-sample.

Metric: daily cross-sectional **rank information coefficient** (Spearman corr of
factor ranks vs forward-return ranks across the universe), averaged over the
window, with a t-stat. Plus the top-minus-bottom quintile long-short forward
return. A factor is only interesting if its IC is positive and significant on the
TEST window, not just TRAIN.

Look-ahead: factors at date t use only data ≤ t; forward returns are the post-hoc
evaluation target and never feed a factor. Live paper state (data/) is untouched;
outputs go to reports/ and backtests/.

    python run.py screen --train-start 2021-06-12 --train-end 2024-06-12 \
                         --test-start 2024-06-12 --test-end 2026-06-12
"""
import argparse
import logging
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from backtest import fetch_backtest_data, load_config
from logger import setup_logging

log = logging.getLogger(__name__)

FWD_HORIZONS = [5, 10, 20, 60]
HEADLINE_H = 20
_BENCH = {"SPY", "QQQ"}


# ─── Factor library ───────────────────────────────────────────────────────────


def build_factors(close: pd.DataFrame, volume: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Candidate signals as [dates × tickers] frames. Higher = expected better."""
    c, v = close, volume
    daily = c.pct_change()
    rv21 = daily.rolling(21).std()
    rv63 = daily.rolling(63).std()
    factors: Dict[str, pd.DataFrame] = {
        # momentum at several horizons
        "mom_21": c.pct_change(21),
        "mom_63": c.pct_change(63),
        "mom_126": c.pct_change(126),
        "mom_252": c.pct_change(252),
        "mom_252_21": c.shift(21) / c.shift(252) - 1.0,        # 12m skip last month
        # reversal (sign-flipped so "higher = expected better")
        "reversal_5": -c.pct_change(5),
        "reversal_21": -c.pct_change(21),
        # risk-adjusted / low-vol
        "vol_adj_mom_63": c.pct_change(63) / rv63.replace(0, np.nan),
        "low_vol": -rv21,
        # trend location
        "dist_50ma": c / c.rolling(50).mean() - 1.0,
        "dist_200ma": c / c.rolling(200).mean() - 1.0,
        "high_52w_prox": c / c.rolling(252).max(),
        # acceleration & volume
        "accel_21_63": c.pct_change(21) - c.pct_change(63),
        "vol_trend": v.rolling(5).mean() / v.rolling(63).mean() - 1.0,
    }
    return factors


# ─── Predictiveness ───────────────────────────────────────────────────────────


def _rank_ic(factor: pd.DataFrame, fwd: pd.DataFrame, dates: pd.Index) -> pd.Series:
    """Daily cross-sectional Spearman IC (rank corr of factor vs forward return)."""
    fr = factor.loc[dates].rank(axis=1)
    rr = fwd.loc[dates].rank(axis=1)
    return fr.corrwith(rr, axis=1)            # one IC per date, across tickers


def _long_short(factor: pd.DataFrame, fwd: pd.DataFrame, dates: pd.Index) -> pd.Series:
    """Daily top-quintile minus bottom-quintile forward return."""
    f = factor.loc[dates]
    g = fwd.loc[dates]
    pct = f.rank(axis=1, pct=True)
    top = g.where(pct >= 0.8).mean(axis=1)
    bot = g.where(pct <= 0.2).mean(axis=1)
    return top - bot


def _stats(series: pd.Series) -> Dict[str, Optional[float]]:
    s = series.dropna()
    if len(s) < 5:
        return {"mean": None, "t": None, "n": len(s)}
    mean = float(s.mean())
    t = float(mean / s.std() * np.sqrt(len(s))) if s.std() > 0 else None
    return {"mean": mean, "t": t, "n": len(s)}


def screen_factors(close: pd.DataFrame, volume: pd.DataFrame,
                   train: Tuple[date, date], test: Tuple[date, date]) -> List[Dict[str, Any]]:
    tickers = [c for c in close.columns if c not in _BENCH]
    close, volume = close[tickers], volume[tickers]
    idx = close.index

    def _mask(d0: date, d1: date) -> pd.Index:
        return idx[[d0 <= ts.date() <= d1 for ts in idx]]

    tr_dates, te_dates = _mask(*train), _mask(*test)
    factors = build_factors(close, volume)
    fwd = {h: close.shift(-h) / close - 1.0 for h in FWD_HORIZONS}

    rows: List[Dict[str, Any]] = []
    for name, fac in factors.items():
        row: Dict[str, Any] = {"factor": name}
        for h in FWD_HORIZONS:
            ic = _rank_ic(fac, fwd[h], idx)
            ls = _long_short(fac, fwd[h], idx)
            tr_ic, te_ic = _stats(ic.loc[tr_dates]), _stats(ic.loc[te_dates])
            tr_ls, te_ls = _stats(ls.loc[tr_dates]), _stats(ls.loc[te_dates])
            row[f"ic_train_{h}"] = tr_ic["mean"]
            row[f"ic_test_{h}"] = te_ic["mean"]
            row[f"ic_test_t_{h}"] = te_ic["t"]
            row[f"ls_train_{h}"] = tr_ls["mean"]
            row[f"ls_test_{h}"] = te_ls["mean"]
        rows.append(row)

    # rank by out-of-sample headline-horizon IC
    rows.sort(key=lambda r: (r.get(f"ic_test_{HEADLINE_H}") or -9), reverse=True)
    return rows


# ─── Reporting ────────────────────────────────────────────────────────────────


def _f(v: Optional[float], nd: int = 3) -> str:
    return "—" if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v:+.{nd}f}"


def _pct(v: Optional[float]) -> str:
    return "—" if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v * 100:+.2f}%"


def _is_real(r: Dict[str, Any], h: int = HEADLINE_H) -> bool:
    """Positive IC in BOTH windows and significant (|t|>2) out-of-sample."""
    ic_tr, ic_te, t = r.get(f"ic_train_{h}"), r.get(f"ic_test_{h}"), r.get(f"ic_test_t_{h}")
    return bool(ic_tr and ic_te and ic_tr > 0 and ic_te > 0 and t is not None and abs(t) > 2)


def render_report(rows: List[Dict[str, Any]], run_date: date,
                  train: Tuple[date, date], test: Tuple[date, date]) -> str:
    survivors = [r for r in rows if _is_real(r)]
    lines: List[str] = [
        "# Signal Screen — Cross-Sectional Factor Predictiveness",
        f"**Train:** {train[0]} → {train[1]}  |  **Test (OOS):** {test[0]} → {test[1]}  "
        f"|  **Generated:** {run_date.isoformat()}",
        "",
        "> Rank IC = daily Spearman corr of factor ranks vs forward-return ranks across the universe "
        f"(headline horizon {HEADLINE_H}d). A factor is a **candidate** only if its IC is positive in "
        "BOTH train and test and significant out-of-sample (|t| > 2). No trading — pure predictiveness.",
        "",
        "---",
        "",
        "## Verdict",
        "",
    ]
    if survivors:
        names = ", ".join(f"`{r['factor']}`" for r in survivors)
        lines += [f"- **{len(survivors)} candidate factor(s) survived OOS:** {names}.",
                  "- These are worth building a strategy around — they actually sort winners from losers "
                  "out-of-sample. Validate further before sizing real conviction."]
    else:
        lines += ["- **No factor showed positive, significant out-of-sample predictive power.**",
                  "- On this universe/period the cross-section looks efficient for these signals — "
                  "consistent with the dead momentum composite. Building another ranking strategy here "
                  "would chase noise. The productive moves are a **different universe** (more dispersion / "
                  "less-efficient names) or a **different data source** (fundamentals, estimates, "
                  "alt-data) — price/volume factors alone are not separating these names."]
    lines += ["", f"## Factor Leaderboard (ranked by OOS {HEADLINE_H}d rank IC)", "",
              "| Factor | IC train | **IC test** | IC t (test) | LS train | LS test | Candidate |",
              "|--------|----------|-------------|-------------|----------|---------|-----------|"]
    for r in rows:
        h = HEADLINE_H
        lines.append(
            f"| {r['factor']} | {_f(r.get(f'ic_train_{h}'))} | **{_f(r.get(f'ic_test_{h}'))}** "
            f"| {_f(r.get(f'ic_test_t_{h}'), 1)} | {_pct(r.get(f'ls_train_{h}'))} "
            f"| {_pct(r.get(f'ls_test_{h}'))} | {'✅' if _is_real(r) else '❌'} |"
        )
    lines += ["",
              "_IC ≈ 0.00 means no signal; |IC| ≳ 0.03 is interesting, ≳ 0.05 strong. "
              "LS = top-quintile minus bottom-quintile average forward return (per day). "
              "Per-horizon detail (5/10/20/60d) is in the CSV._", ""]
    return "\n".join(lines)


def results_csv(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows)


# ─── CLI ──────────────────────────────────────────────────────────────────────


def run(train_start: date, train_end: date, test_start: date, test_end: date) -> Dict[str, str]:
    setup_logging()
    run_date = date.today()
    root = Path(__file__).parent.parent
    config = load_config(root / "config")

    log.info("=== Signal Screen (factor predictiveness) ===")
    # long warmup so 12-month momentum / 52-week-high factors are valid from the start
    price_data = fetch_backtest_data(config["tickers"], train_start, test_end, warmup_days=420)
    close, volume = price_data["Close"], price_data["Volume"]
    rows = screen_factors(close, volume, (train_start, train_end), (test_start, test_end))
    report = render_report(rows, run_date, (train_start, train_end), (test_start, test_end))

    (root / "reports").mkdir(parents=True, exist_ok=True)
    (root / "backtests").mkdir(parents=True, exist_ok=True)
    tag = run_date.isoformat()
    md = root / "reports" / f"signal_screen_{tag}.md"
    md.write_text(report)
    csv = root / "backtests" / f"signal_screen_{tag}.csv"
    results_csv(rows).to_csv(csv, index=False)

    survivors = [r["factor"] for r in rows if _is_real(r)]
    print()
    print(f"  Factors screened : {len(rows)}")
    print(f"  OOS survivors    : {len(survivors)}" + (f" ({', '.join(survivors)})" if survivors else ""))
    best = rows[0] if rows else None
    if best:
        print(f"  Best OOS IC ({HEADLINE_H}d): {best['factor']} = {_f(best.get(f'ic_test_{HEADLINE_H}'))}")
    print()
    print(f"  Report : {md}")
    print(f"  CSV    : {csv}")
    print("  NOTE: a candidate must have positive IC in BOTH windows and |t|>2 OOS. Validate before trading.")
    print()
    return {"report": str(md), "csv": str(csv)}


def main() -> None:
    p = argparse.ArgumentParser(description="AI Paper Trader — Signal Screen (factor predictiveness)")
    p.add_argument("--train-start", required=True, metavar="YYYY-MM-DD")
    p.add_argument("--train-end", required=True, metavar="YYYY-MM-DD")
    p.add_argument("--test-start", required=True, metavar="YYYY-MM-DD")
    p.add_argument("--test-end", required=True, metavar="YYYY-MM-DD")
    args = p.parse_args()
    try:
        ts, te = date.fromisoformat(args.train_start), date.fromisoformat(args.train_end)
        vs, ve = date.fromisoformat(args.test_start), date.fromisoformat(args.test_end)
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)
    run(ts, te, vs, ve)


if __name__ == "__main__":
    main()
