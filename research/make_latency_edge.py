"""Latency-edge backtest. A close-computed signal predicts a forward return; HOW MUCH of it accrues
OVERNIGHT (close T -> open T+1, which you LOSE if you can only execute at the next open) vs INTRADAY
(open T+1 -> close T+1, which realistic open-execution still captures)? If a strategy's edge is front-
loaded into the overnight gap, it bleeds to execution latency (live << frictionless backtest). Compares
momentum top-10 (by the close composite score) vs z-reversal bottom-10 (by the 1-day 60-day z). Daily
selection. Reuses the cached score panel + OHLC. 2020+; survivorship-biased."""
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
px = fetch_backtest_data(cfg["tickers"], date(2018, 6, 1), date.today())
close, openp = px["Close"], px["Open"]
S = pd.read_csv(ROOT / "backtests" / "daily_scores_model_v4.csv", index_col=0, parse_dates=True)
Z = (S - S.rolling(60).mean()) / S.rolling(60).std()

ov = (openp.shift(-1) / close - 1)               # close T -> open T+1   (overnight; missed at open-exec)
intr = (close.shift(-1) / openp.shift(-1) - 1)   # open T+1 -> close T+1 (intraday; captured at open-exec)
full = (close.shift(-1) / close - 1)             # close T -> close T+1  (frictionless backtest)
dates = [d for d in S.index if d.year >= 2020 and d in close.index and d in ov.index]


def run(panel, asc, n=10):
    o, i, f = [], [], []
    for t in dates:
        r = panel.loc[t].dropna()
        if len(r) < 20:
            continue
        sel = [s for s in r.sort_values(ascending=asc).head(n).index if s in close.columns]
        o.append(float(ov.loc[t, sel].mean()))
        i.append(float(intr.loc[t, sel].mean()))
        f.append(float(full.loc[t, sel].mean()))
    return pd.Series(o).dropna(), pd.Series(i).dropna(), pd.Series(f).dropna()


def ann(s):
    g = s.dropna()
    return (((1 + g).prod()) ** (252 / len(g)) - 1) * 100 if len(g) else 0.0


print("Where does the close-signal's 1-day forward return accrue?  (daily top/bottom-10, 2020+)\n")
print("%-24s | %11s | %11s | %11s | %s" % ("strategy", "FULL c->c", "overnight", "intraday", "% edge overnight"))
print("-" * 84)
for lbl, panel, asc in [("momentum  (top score)", S, False), ("z-reversal (bottom 1d-z)", Z, True)]:
    o, i, f = run(panel, asc)
    af, ao, ai = ann(f), ann(o), ann(i)
    print("%-24s | %+9.1f%% | %+9.1f%% | %+9.1f%% | %5.0f%%" % (lbl, af, ao, ai, (ao / af * 100) if af else 0))
print("-" * 84)
print("FULL c->c = frictionless backtest (rank + execute at close T).")
print("overnight = close T -> open T+1  (LOST if you can only execute at the next open = the LATENCY COST).")
print("intraday  = open T+1 -> close T+1 (what realistic open-execution actually captures = ~the live return).")
print("Thesis: momentum's edge is front-loaded overnight (bleeds to latency); z-reversal's is intraday-captured.")
