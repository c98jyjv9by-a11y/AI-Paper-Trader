"""Sweep the score LOOKBACK (trailing N-day avg) at a weekly rebalance: where does the top-10 Sharpe
peak? top-10 / bottom-10 / 20-name, annualized + Sharpe + total. Reuses cached daily scores."""
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
px_w = close.resample("W-FRI").last()
weeks = [d for d in px_w.index if d.year >= 2020]


def weekly(score_w):
    out = []
    for i in range(1, len(weeks)):
        cur, prev = weeks[i], weeks[i - 1]
        if prev not in score_w.index:
            continue
        avg = score_w.loc[prev].dropna().sort_values(ascending=False)
        if len(avg) < 20:
            continue
        ret = (px_w.loc[cur] / px_w.loc[prev] - 1) * 100.0
        out.append((ret.reindex(avg.head(10).index).mean(), ret.reindex(avg.tail(10).index).mean()))
    d = pd.DataFrame(out, columns=["top", "bot"])
    d["combo"] = (d["top"] + d["bot"]) / 2
    return d


def stats(s):
    g = s.dropna() / 100
    grow = np.prod(1 + g)
    ann = (grow ** (52.0 / len(g)) - 1) * 100
    sh = g.mean() / g.std() * np.sqrt(52) if g.std() else 0
    return (grow - 1) * 100, ann, sh


print("WEEKLY rebalance — score lookback sweep (annualized%% / Sharpe; total in parens)\n")
print("%-7s | %-22s | %-22s | %-22s" % ("LOOKBK", "TOP-10", "BOTTOM-10", "20-NAME"))
print("-" * 80)
for L in [5, 10, 20, 30, 40, 60]:
    d = weekly(S.rolling(L).mean().resample("W-FRI").last())
    cells = []
    for col in ["top", "bot", "combo"]:
        tot, ann, sh = stats(d[col])
        cells.append("%+6.1f%% / %.2f (%+.0f%%)" % (ann, sh, tot))
    print("%-7s | %-22s | %-22s | %-22s" % ("%dD" % L, cells[0], cells[1], cells[2]))
