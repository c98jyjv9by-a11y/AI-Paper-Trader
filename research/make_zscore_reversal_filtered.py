"""Regime-filtered z-reversal: 10-day-avg z, bottom-10, BIWEEKLY, but hold the book ONLY when QQQ is in
an uptrend (> its 200-day MA at the rebalance) — else go to CASH. Targets the 2022 'buy the falling
knife' blow-up. Compares unfiltered vs 200d-MA vs 100d-MA filter, gross + net of cost. 2020+; survivorship."""
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
SIG = Z.rolling(10).mean()
px_bw = close.resample("W-FRI").last().iloc[::2]               # biweekly = every other Friday
sig_bw = SIG.resample("W-FRI").last().reindex(px_bw.index)


def regime(ma_days):
    if ma_days is None:
        return None
    ma = qqq.rolling(ma_days).mean()
    on = (qqq > ma).reindex(px_bw.index, method="ffill")        # QQQ > MA at each biweekly date
    return on


def backtest(reg):
    dts = [d for d in px_bw.index if d.year >= 2020]
    rets, turn, prev = [], [], set()
    for i in range(len(dts) - 1):
        cur, nxt = dts[i], dts[i + 1]
        on = True if reg is None else bool(reg.get(cur, True))
        hold, ret = set(), 0.0
        if on:
            sig = sig_bw.loc[cur].dropna().sort_values()
            if len(sig) >= 20:
                bot = list(sig.head(N).index)
                hold = set(bot)
                ret = (px_bw.loc[nxt] / px_bw.loc[cur] - 1).reindex(bot).mean() * 100
        rets.append((nxt, ret))
        turn.append((len(hold ^ prev) / 2.0) / N)
        prev = hold
    return pd.Series(dict(rets)), (float(np.mean(turn)) if turn else 0.0)


def stat(s, per=26):
    g = s.dropna() / 100
    grow = np.prod(1 + g)
    return (grow ** (per / len(g)) - 1) * 100, (g.mean() / g.std() * np.sqrt(per) if g.std() else 0)


print("10d-avg z / bottom-10 / BIWEEKLY — regime filter (cash when QQQ < MA)\n")
print("%-18s | %-19s | %5s | %-22s | %7s" %
      ("FILTER", "GROSS ann / Sharpe", "turn", "NET ann @ 5bp / 10bp", "worst"))
print("-" * 86)
keep = {}
for lbl, mad in [("none (unfiltered)", None), ("QQQ > 200d MA", 200), ("QQQ > 100d MA", 100)]:
    r, turn = backtest(regime(mad))
    keep[lbl] = r
    ga, gs = stat(r)
    nets = [stat(r - turn * 2 * bps / 100.0)[0] for bps in (5, 10)]
    print("%-18s | %+7.1f%% / %.2f     | %4.0f%% | %+8.1f%% / %+8.1f%%   | %+5.1f%%"
          % (lbl, ga, gs, turn * 100, nets[0], nets[1], r.min()))
print("-" * 86)
qd = (qqq.pct_change() * 100).dropna(); qd = qd[qd.index.year >= 2020]
md = (eq["daily_return"] * 100).dropna(); md = md[md.index.year >= 2020]
for lbl, s in [("QQQ", qd), ("model_v4", md)]:
    a, sh = stat(s, 252)
    print("  %-9s ann %+6.1f%%  Sharpe %.2f" % (lbl, a, sh))

print("\nAnnual returns:")
print("  %-18s %s" % ("year", "  ".join("%6d" % y for y in range(2020, 2027))))
for lbl in ["none (unfiltered)", "QQQ > 200d MA"]:
    r = keep[lbl]; r.index = pd.to_datetime(r.index)
    ann = {y: (np.prod(1 + g / 100) - 1) * 100 for y, g in r.groupby(r.index.year)}
    print("  %-18s %s" % (lbl, "  ".join("%+5.0f%%" % ann.get(y, 0) for y in range(2020, 2027))))
