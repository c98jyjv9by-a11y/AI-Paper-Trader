"""DAILY-rebalanced BOTTOM-10 (mean-reversion) book on the 60-day z-score, two ranking signals:
(A) latest z (1-day), (B) trailing 5-day-avg z. Equal-weight, re-rank daily, earn t->t+1. QQQ + model_v4
for context. Reuses cache. Frictionless; 2020 partial (z warmup)."""
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
Z = (S - S.rolling(60).mean()) / S.rolling(60).std()           # per-ticker 60-day rolling z
qc = fetch_backtest_data(["QQQ"], date(2018, 6, 1), date.today())["Close"]
qqq = qc["QQQ"] if hasattr(qc, "columns") else qc
eq = pd.read_csv(sorted(glob.glob(str(ROOT / "backtests" / "scenario_model_v4_*_equity.csv")))[-1],
                 parse_dates=["date"]).set_index("date")


def bottom_daily(sig):
    dates = [d for d in close.index if d.year >= 2020 and d in sig.index]
    rec = []
    for i in range(len(dates) - 1):
        t, nxt = dates[i], dates[i + 1]
        z = sig.loc[t].dropna().sort_values()                  # ascending -> lowest z first
        if len(z) < 20:
            continue
        fwd = (close.loc[nxt] / close.loc[t] - 1) * 100.0
        rec.append((nxt, fwd.reindex(z.head(10).index).mean()))  # bottom-10 = 10 lowest z
    return pd.Series(dict(rec))


b1 = bottom_daily(Z)                                            # (A) latest z (1-day)
b5 = bottom_daily(Z.rolling(5).mean())                          # (B) trailing 5-day-avg z
idx = b1.index.union(b5.index)
qd = (qqq.pct_change() * 100).reindex(idx)
md = (eq["daily_return"] * 100).reindex(idx)
cmp = lambda s: (np.prod(1 + s.dropna() / 100) - 1) * 100

print("DAILY rebalance, BOTTOM-10 by 60-day z-score (mean-reversion). 2020 partial.\n")
print("%-6s | %-13s %-13s | %8s %9s" % ("YEAR", "BOT10 (1D z)", "BOT10 (5D z)", "QQQ", "model_v4"))
print("-" * 58)
years = sorted({d.year for d in idx})
for y in years:
    m = [d for d in idx if d.year == y]
    print("%-6d | %+11.1f%% %+11.1f%% | %+7.1f%% %+8.1f%%"
          % (y, cmp(b1.reindex(m)), cmp(b5.reindex(m)), cmp(qd.reindex(m)), cmp(md.reindex(m))))
print("-" * 58)
print("%-6s | %+11.1f%% %+11.1f%% | %+7.1f%% %+8.1f%%   (total)"
      % ("TOTAL", cmp(b1), cmp(b5), cmp(qd), cmp(md)))


def annsh(s):
    g = s.dropna() / 100
    return (np.prod(1 + g) ** (252.0 / len(g)) - 1) * 100, (g.mean() / g.std() * np.sqrt(252) if g.std() else 0)


print()
for lbl, s in [("BOT-10 (1D z)", b1), ("BOT-10 (5D z)", b5), ("QQQ", qd), ("model_v4", md)]:
    a, sh = annsh(s)
    print("  %-14s annualized %+6.1f%%   Sharpe %.2f   worst-day %+.1f%%" % (lbl, a, sh, s.dropna().min()))
