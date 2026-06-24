"""Sweep the REBALANCE frequency (daily/weekly/2-week/monthly/quarterly) for the 60-day-lookback
top-10, holding the score lookback fixed at 60 days. How much does trade frequency matter?"""
import sys
import warnings
from datetime import date
from pathlib import Path

warnings.filterwarnings("ignore")
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))
import numpy as np
import pandas as pd

from backtest import load_config, fetch_backtest_data
from scenarios import load_scenario, build_config

cfg = build_config(load_config(ROOT / "config"), load_scenario("model_v4"))
close = fetch_backtest_data(cfg["tickers"], date(2018, 6, 1), date.today())["Close"]
S = pd.read_csv(ROOT / "backtests" / "daily_scores_model_v4.csv", index_col=0, parse_dates=True)
qqq = fetch_backtest_data(["QQQ"], date(2018, 6, 1), date.today())["Close"]
qqq = qqq["QQQ"] if hasattr(qqq, "columns") else qqq
S60 = S.rolling(60).mean()                                  # fixed 60-day lookback


def run(score_p, px_p, qpx, ppy):
    dates = [d for d in px_p.index if d.year >= 2020]
    top, q = [], []
    for i in range(1, len(dates)):
        cur, prev = dates[i], dates[i - 1]
        if prev not in score_p.index:
            continue
        avg = score_p.loc[prev].dropna().sort_values(ascending=False)
        if len(avg) < 20:
            continue
        ret = (px_p.loc[cur] / px_p.loc[prev] - 1) * 100.0
        top.append(ret.reindex(avg.head(10).index).mean())
        q.append((qpx.loc[cur] / qpx.loc[prev] - 1) * 100.0 if (cur in qpx.index and prev in qpx.index) else np.nan)

    def st(lst):
        s = pd.Series(lst).dropna() / 100
        grow = np.prod(1 + s)
        return (grow - 1) * 100, (grow ** (ppy / len(s)) - 1) * 100, (s.mean() / s.std() * np.sqrt(ppy) if s.std() else 0)
    return st(top), st(q), len([t for t in top if not np.isnan(t)])


FREQS = [("Daily", None, 252), ("Weekly", "W-FRI", 52), ("2-Week", "2W-FRI", 26),
         ("Monthly", "ME", 12), ("Quarterly", "QE", 4)]
print("REBALANCE-FREQUENCY sweep — 60-day-lookback top-10  (lookback held fixed)\n")
print("%-10s %7s | %9s %11s %8s | %8s %7s" %
      ("REBAL", "#rebal", "TOTAL", "annualized", "Sharpe", "QQQ ann", "QQQ Sh"))
print("-" * 70)
for lbl, rule, ppy in FREQS:
    if rule is None:
        sc, px, qp = S60, close, qqq
    else:
        px = close.resample(rule).last()
        sc = S60.reindex(px.index, method="ffill")          # align 60D score to the rebalance dates
        qp = qqq.resample(rule).last()
    (tot, ann, sh), (_, qa, qs), n = run(sc, px, qp, ppy)
    print("%-10s %7d | %+8.0f%% %+9.1f%% %8.2f | %+7.1f%% %7.2f"
          % (lbl, n, tot, ann, sh, qa, qs))
