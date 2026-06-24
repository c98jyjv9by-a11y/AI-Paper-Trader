"""Backtest the IC-optimal z-reversal variant: rank by the 10-DAY avg of the 60-day z, BUY bottom-10,
hold ~10 trading days (BIWEEKLY). Compare to 5d-weekly / 10d-weekly / 5d-daily + QQQ + model_v4, gross
+ net of transaction costs. Reuses the cached score panel. 2020+ (z warmup); survivorship-biased."""
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
Z = (S - S.rolling(60).mean()) / S.rolling(60).std()
qqq = fetch_backtest_data(["QQQ"], date(2018, 6, 1), date.today())["Close"]
qqq = qqq["QQQ"] if hasattr(qqq, "columns") else qqq
eq = pd.read_csv(sorted(glob.glob(str(ROOT / "backtests" / "scenario_model_v4_*_equity.csv")))[-1],
                 parse_dates=["date"]).set_index("date")
N = 10


def sampled(window, cadence):
    sig = Z.rolling(window).mean()
    if cadence == "daily":
        return sig, close, 252
    pw, sw = close.resample("W-FRI").last(), sig.resample("W-FRI").last()
    if cadence == "weekly":
        return sw, pw, 52
    idx = pw.index[::2]                                         # biweekly = every other Friday
    return sw.reindex(idx), pw.reindex(idx), 26


def backtest(sig_at, px_at):
    dts = [d for d in px_at.index if d.year >= 2020 and d in sig_at.index]
    rets, turn, prev = [], [], set()
    for i in range(len(dts) - 1):
        cur, nxt = dts[i], dts[i + 1]
        sig = sig_at.loc[cur].dropna().sort_values()
        if len(sig) < 20:
            prev = set(); continue
        bot = list(sig.head(N).index)
        rets.append((nxt, (px_at.loc[nxt] / px_at.loc[cur] - 1).reindex(bot).mean() * 100))
        turn.append((len(set(bot) ^ prev) / 2.0 if prev else N) / N)
        prev = set(bot)
    return pd.Series(dict(rets)), (float(np.mean(turn)) if turn else 0.0)


def stat(s, per):
    g = s.dropna() / 100
    grow = np.prod(1 + g)
    return (grow ** (per / len(g)) - 1) * 100, (g.mean() / g.std() * np.sqrt(per) if g.std() else 0)


VARIANTS = [("5d-avg / weekly", 5, "weekly"), ("10d-avg / weekly", 10, "weekly"),
            ("10d-avg / BIWEEKLY", 10, "biweekly"), ("5d-avg / daily", 5, "daily")]
print("z-REVERSAL bottom-10, variants  (gross + net of cost; 2020+)\n")
print("%-20s | %-20s | %5s | %-24s | %7s" %
      ("VARIANT", "GROSS ann / Sharpe", "turn", "NET ann @ 5bp / 10bp", "worst"))
print("-" * 92)
keep = {}
for lbl, w, cad in VARIANTS:
    sa, pa, ppy = sampled(w, cad)
    r, turn = backtest(sa, pa)
    keep[lbl] = (r, ppy)
    ga, gs = stat(r, ppy)
    nets = [stat(r - turn * 2 * bps / 100.0, ppy)[0] for bps in (5, 10)]
    print("%-20s | %+7.1f%% / %.2f      | %4.0f%% | %+8.1f%% / %+8.1f%%     | %+5.1f%%"
          % (lbl, ga, gs, turn * 100, nets[0], nets[1], r.min()))
print("-" * 92)
qd = (qqq.pct_change() * 100).dropna(); qd = qd[qd.index.year >= 2020]
md = (eq["daily_return"] * 100).dropna(); md = md[md.index.year >= 2020]
for lbl, s in [("QQQ", qd), ("model_v4", md)]:
    a, sh = stat(s, 252)
    print("  %-9s ann %+6.1f%%  Sharpe %.2f" % (lbl, a, sh))

# annual breakdown for the focus variant
r, ppy = keep["10d-avg / BIWEEKLY"]
r.index = pd.to_datetime(r.index)
print("\n10d-avg / BIWEEKLY — annual returns:")
for y, g in r.groupby(r.index.year):
    print("  %d: %+6.1f%%" % (y, (np.prod(1 + g / 100) - 1) * 100))
