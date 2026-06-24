"""DAILY-rebalanced portfolio: each day hold the top-10 by per-ticker 60-DAY z-score (equal-weight),
earn the next day's return; re-rank every day. Bottom-10 + QQQ + model_v4 for context. Reuses cache.
No look-ahead: rank on Z as of day t's close, earn t->t+1. Frictionless; 2020 partial (z warmup)."""
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
Z = (S - S.rolling(60).mean()) / S.rolling(60).std()           # per-ticker 60-day rolling z
qc = fetch_backtest_data(["QQQ"], date(2018, 6, 1), date.today())["Close"]
qqq = qc["QQQ"] if hasattr(qc, "columns") else qc
eq = pd.read_csv(sorted(glob.glob(str(ROOT / "backtests" / "scenario_model_v4_*_equity.csv")))[-1],
                 parse_dates=["date"]).set_index("date")

dates = [d for d in close.index if d.year >= 2020 and d in Z.index]
rec = []
for i in range(len(dates) - 1):
    t, nxt = dates[i], dates[i + 1]
    z = Z.loc[t].dropna().sort_values(ascending=False)
    if len(z) < 20:
        continue
    fwd = (close.loc[nxt] / close.loc[t] - 1) * 100.0          # earn t -> t+1
    rec.append((nxt, fwd.reindex(z.head(10).index).mean(), fwd.reindex(z.tail(10).index).mean()))
df = pd.DataFrame(rec, columns=["d", "top", "bot"]).set_index("d")
df["year"] = df.index.year
qd = (qqq.pct_change() * 100).reindex(df.index)
md = (eq["daily_return"] * 100).reindex(df.index)
cmp = lambda s: (np.prod(1 + s.dropna() / 100) - 1) * 100

print("DAILY rebalance, TOP-10 by 60-day z-score, equal-weight  (2020 partial — z warmup)\n")
print("%-6s | %9s %9s | %8s %9s" % ("YEAR", "TOP10", "BOT10", "QQQ", "model_v4"))
print("-" * 52)
for y in sorted(set(df["year"])):
    g = df[df.year == y]
    print("%-6d | %+8.1f%% %+8.1f%% | %+7.1f%% %+8.1f%%"
          % (y, cmp(g["top"]), cmp(g["bot"]), cmp(qd.reindex(g.index)), cmp(md.reindex(g.index))))
print("-" * 52)
print("%-6s | %+8.1f%% %+8.1f%% | %+7.1f%% %+8.1f%%   (total compounded)"
      % ("TOTAL", cmp(df["top"]), cmp(df["bot"]), cmp(qd), cmp(md)))


def annsh(s):
    g = s.dropna() / 100
    return (np.prod(1 + g) ** (252.0 / len(g)) - 1) * 100, (g.mean() / g.std() * np.sqrt(252) if g.std() else 0)


print()
for lbl, s in [("TOP-10 daily", df["top"]), ("BOT-10 daily", df["bot"]),
               ("QQQ", qd), ("model_v4", md)]:
    a, sh = annsh(s)
    print("  %-13s annualized %+6.1f%%   Sharpe %.2f" % (lbl, a, sh))
print("\n  (top-10 daily worst 1-day %+.1f%%, best %+.1f%%; %d trading days)"
      % (df["top"].min(), df["top"].max(), len(df)))
