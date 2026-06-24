"""Train/test split (2020-2022 vs 2023-2026) of the 60-day-lookback weekly top-10 (+ bottom/combo),
vs QQQ and model_v4 on the same splits. Is the 60D top-10's Sharpe a single-period fit or robust?"""
import sys
import glob
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
eq = pd.read_csv(sorted(glob.glob(str(ROOT / "backtests" / "scenario_model_v4_*_equity.csv")))[-1],
                 parse_dates=["date"]).set_index("date")

px_w = close.resample("W-FRI").last()
score_w = S.rolling(60).mean().resample("W-FRI").last()           # 60-day trailing avg, at Friday
weeks = [d for d in px_w.index if d.year >= 2020]
recs = []
for i in range(1, len(weeks)):
    cur, prev = weeks[i], weeks[i - 1]
    if prev not in score_w.index:
        continue
    avg = score_w.loc[prev].dropna().sort_values(ascending=False)
    if len(avg) < 20:
        continue
    ret = (px_w.loc[cur] / px_w.loc[prev] - 1) * 100.0
    recs.append((cur, ret.reindex(avg.head(10).index).mean(), ret.reindex(avg.tail(10).index).mean()))
df = pd.DataFrame(recs, columns=["week", "top", "bot"]).set_index("week")
df["combo"] = (df["top"] + df["bot"]) / 2
qw = (qqq.resample("W-FRI").last().pct_change() * 100).dropna()


def stat(s, per=52):
    g = s.dropna() / 100
    grow = np.prod(1 + g)
    ann = (grow ** (per / len(g)) - 1) * 100 if len(g) else 0
    sh = g.mean() / g.std() * np.sqrt(per) if g.std() else 0
    return ann, sh


SPLITS = [("TRAIN 2020-2022", 2020, 2022), ("TEST  2023-2026", 2023, 2099),
          ("FULL  2020-2026", 2020, 2099)]
print("60-DAY-lookback weekly baskets, train vs test  (annualized%% / Sharpe)\n")
print("%-17s | %-13s %-13s %-13s | %-13s %-13s" %
      ("SPLIT", "60D TOP-10", "60D BOT-10", "60D 20-name", "QQQ", "model_v4"))
print("-" * 92)
for lbl, y0, y1 in SPLITS:
    m = (df.index.year >= y0) & (df.index.year <= y1)
    qm = (qw.index.year >= y0) & (qw.index.year <= y1)
    dm = (eq.index.year >= y0) & (eq.index.year <= y1)
    cells = [stat(df.loc[m, c]) for c in ["top", "bot", "combo"]]
    qc = stat(qw[qm])
    mc = stat(eq.loc[dm, "daily_return"] * 100, per=252)         # daily_return is a fraction, not %
    print("%-17s | %+6.1f%%/%.2f  %+6.1f%%/%.2f  %+6.1f%%/%.2f | %+6.1f%%/%.2f  %+6.1f%%/%.2f"
          % (lbl, cells[0][0], cells[0][1], cells[1][0], cells[1][1], cells[2][0], cells[2][1],
             qc[0], qc[1], mc[0], mc[1]))
