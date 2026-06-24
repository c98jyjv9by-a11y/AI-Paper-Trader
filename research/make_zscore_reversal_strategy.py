"""STRATEGY: 5-day z-reversal (mean reversion).
  signal_t(ticker) = mean over the last 5 days of z_t, where z_t = (score_t - mean60)/std60 is the
  per-ticker 60-day rolling z-score of the model_v4 composite. Each rebalance, BUY the 10 LOWEST-signal
  names (the most-fallen vs their own 60-day norm), equal-weight, hold to the next rebalance.
Backtests DAILY and WEEKLY rebalance, gross + net of transaction costs, vs QQQ + model_v4.
Reuses the cached daily score panel. Frictionless caveats: survivorship-biased; 2020 partial (z warmup).
"""
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
SIG = Z.rolling(5).mean()                                       # 5-day avg of the z (the strategy signal)
qqq = fetch_backtest_data(["QQQ"], date(2018, 6, 1), date.today())["Close"]
qqq = qqq["QQQ"] if hasattr(qqq, "columns") else qqq
eq = pd.read_csv(sorted(glob.glob(str(ROOT / "backtests" / "scenario_model_v4_*_equity.csv")))[-1],
                 parse_dates=["date"]).set_index("date")
N = 10


def backtest(sig_at, px_at, ppy):
    """sig_at/px_at: signal & price sampled at the rebalance dates. Returns (gross %, turnover-fraction)
    series indexed by the realized (next) date, plus the bottom-10 churn."""
    dates = [d for d in px_at.index if d.year >= 2020 and d in sig_at.index]
    rets, turn, prev = [], [], set()
    for i in range(1, len(dates)):
        cur, nxt = dates[i], dates[i + 1] if i + 1 < len(dates) else None
        sig = sig_at.loc[cur].dropna().sort_values()           # ascending -> lowest first
        if len(sig) < 20 or nxt is None:
            prev = set()
            continue
        bot = list(sig.head(N).index)
        ret = (px_at.loc[nxt] / px_at.loc[cur] - 1).reindex(bot).mean() * 100
        rets.append((nxt, ret))
        changed = len(set(bot) ^ prev) / 2.0 if prev else N    # names entering/leaving
        turn.append(changed / N)                               # one-way turnover fraction
        prev = set(bot)
    r = pd.Series(dict(rets))
    return r, float(np.mean(turn)) if turn else 0.0


def stat(s, per):
    g = s.dropna() / 100
    grow = np.prod(1 + g)
    return (grow ** (per / len(g)) - 1) * 100, (g.mean() / g.std() * np.sqrt(per) if g.std() else 0)


print("STRATEGY: BUY bottom-10 by 5-day-avg of the 60-day z-score (mean reversion), equal-weight\n")
print("%-8s | %-22s | %6s | %-26s" % ("CADENCE", "GROSS (ann / Sharpe)", "turn", "NET ann @ 5bp / 10bp per-side"))
print("-" * 88)
for lbl, sampler, ppy, perreb in [("DAILY", lambda x: x, 252, 252), ("WEEKLY", lambda x: x.resample("W-FRI").last(), 52, 52)]:
    sig_at = sampler(SIG) if lbl == "WEEKLY" else SIG
    px_at = close.resample("W-FRI").last() if lbl == "WEEKLY" else close
    r, turn = backtest(sig_at, px_at, ppy)
    g_ann, g_sh = stat(r, ppy)
    # net: each rebalance pays ~ turnover(one-way) * 2 sides * cost_per_side
    nets = {}
    for bps in (5, 10):
        drag = turn * 2 * bps / 100.0                          # % per rebalance
        nets[bps] = stat(r - drag, ppy)[0]
    print("%-8s | %+7.1f%% / %.2f         | %5.0f%% | %+7.1f%% / %+7.1f%%   (worst %s %+.1f%%)"
          % (lbl, g_ann, g_sh, turn * 100, nets[5], nets[10],
             "day" if lbl == "DAILY" else "wk", r.min()))
# benchmarks
qd = (qqq.pct_change() * 100).dropna(); qd = qd[qd.index.year >= 2020]
md = (eq["daily_return"] * 100).dropna(); md = md[md.index.year >= 2020]
print("-" * 88)
for lbl, s in [("QQQ", qd), ("model_v4", md)]:
    a, sh = stat(s, 252)
    print("  %-9s ann %+6.1f%%  Sharpe %.2f" % (lbl, a, sh))
print("\n(turn = avg one-way turnover per rebalance; net subtracts turn*2*bps each rebalance. "
      "2020 partial; frictionless backtest is survivorship-biased.)")
