"""Weekly rebalance, but rank by the TRAILING 20-DAY average score (vs the prior-week 5-day avg).
Same Fri->Fri weekly hold; compares the two lookbacks for top-10 / bottom-10 / 20-name, vs QQQ + model_v4."""
import sys
import glob
import warnings
from datetime import date
from pathlib import Path

warnings.filterwarnings("ignore")
ROOT = Path(__file__).parent
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
                 parse_dates=["date"]).set_index("date")["total_portfolio_value"]

px_w = close.resample("W-FRI").last()
cmp = lambda s: (np.prod(1 + s.dropna() / 100) - 1) * 100


def weekly(score_w):                                   # score_w: ranking panel indexed by Fri
    out = []
    weeks = [d for d in px_w.index if d.year >= 2020]
    for i in range(1, len(weeks)):
        cur, prev = weeks[i], weeks[i - 1]
        if prev not in score_w.index:
            continue
        avg = score_w.loc[prev].dropna().sort_values(ascending=False)
        if len(avg) < 20:
            continue
        ret = (px_w.loc[cur] / px_w.loc[prev] - 1) * 100.0
        out.append((cur, ret.reindex(avg.head(10).index).mean(), ret.reindex(avg.tail(10).index).mean()))
    df = pd.DataFrame(out, columns=["p", "top", "bot"])
    df["combo"] = (df["top"] + df["bot"]) / 2
    df["year"] = df["p"].apply(lambda d: d.year)
    return df


wk5 = weekly(S.resample("W-FRI").mean())                       # prior-week 5-day avg
wk20 = weekly(S.rolling(20).mean().resample("W-FRI").last())   # trailing 20-day avg

qw = (qqq.resample("W-FRI").last().pct_change() * 100).dropna()
qw = qw[qw.index.year >= 2020]
qa = lambda y: cmp(qw[qw.index.year == y])
base19 = eq[eq.index.year == 2019].iloc[-1]
mv4 = {y: (eq[eq.index.year == y].iloc[-1] / eq[eq.index.year == y - 1].iloc[-1] - 1) * 100
       for y in range(2020, 2027) if len(eq[eq.index.year == y]) and len(eq[eq.index.year == y - 1])}

print("WEEKLY rebalance, ranked by TRAILING 20-DAY avg score")
print("%-6s | %9s %9s %9s | %8s %9s"
      % ("YEAR", "20D TOP", "20D BOT", "20D 20nm", "QQQ", "model_v4"))
print("-" * 64)
for y in sorted(set(wk20["year"])):
    g = wk20[wk20.year == y]
    print("%-6d | %+8.1f%% %+8.1f%% %+8.1f%% | %+7.1f%% %+8.1f%%"
          % (y, cmp(g["top"]), cmp(g["bot"]), cmp(g["combo"]), qa(y), mv4.get(y, float("nan"))))
print("-" * 64)
print("%-6s | %+8.1f%% %+8.1f%% %+8.1f%% | %+7.1f%% %+8.1f%%   (total)"
      % ("TOTAL", cmp(wk20["top"]), cmp(wk20["bot"]), cmp(wk20["combo"]), cmp(qw),
         (eq.iloc[-1] / base19 - 1) * 100))


def sh(s, per=52):
    g = s.dropna() / 100
    grow = np.prod(1 + g)
    return (grow ** (per / len(g)) - 1) * 100, (g.mean() / g.std() * np.sqrt(per) if g.std() else 0)


print("\nLOOKBACK COMPARISON (annualized / Sharpe):")
print("  %-10s %16s %16s" % ("", "5-DAY avg", "20-DAY avg"))
for col, lbl in [("top", "TOP-10"), ("bot", "BOT-10"), ("combo", "20-name")]:
    a5, s5 = sh(wk5[col]); a20, s20 = sh(wk20[col])
    print("  %-10s  %+7.1f%% / %.2f     %+7.1f%% / %.2f" % (lbl, a5, s5, a20, s20))
