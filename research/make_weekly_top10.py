"""Weekly top-10 strategy, summarized by year.
Each week: rank by the PRIOR week's (prior 5 trading days') AVERAGE composite score, hold the top 10
EQUAL-WEIGHT for the coming week (Fri->Fri bars ~ a Monday rebalance). Compound weekly returns; report
per year vs the bottom-10, the equal-weight universe, and QQQ. Daily scores are cached for reuse.

Caveat: CURRENT model_v4 universe used back to 2020 (survivorship/look-ahead); `n` grows as names IPO."""
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
from signals import calculate_signals, rank_candidates
from rank_report import _build_ticker_weights, _SIGNAL_WINDOW

cfg = build_config(load_config(ROOT / "config"), load_scenario("model_v4"))
uni, w = cfg["tickers"], cfg["signals"].get("weights")
tw = _build_ticker_weights(cfg) or None

end = date.today()
pdata = fetch_backtest_data(uni, date(2018, 6, 1), end)
close = pdata["Close"]

CACHE = ROOT / "backtests" / "daily_scores_model_v4.csv"
if CACHE.exists():
    S = pd.read_csv(CACHE, index_col=0, parse_dates=True)
    print("loaded cached daily scores:", S.shape, file=sys.stderr)
else:
    days = [ts for ts in close.index if ts >= pd.Timestamp("2019-12-01")]
    print("computing daily scores: %d days..." % len(days), file=sys.stderr)
    rows = {}
    for i, ts in enumerate(days):
        sl = pdata.loc[:ts].iloc[-_SIGNAL_WINDOW:]
        rf = rank_candidates(calculate_signals(sl, uni), top_n=len(uni), weights=w, ticker_weights=tw)
        rows[ts] = dict(zip(rf["ticker"], rf["composite_score"]))
        if i % 200 == 0:
            print("  %d/%d" % (i, len(days)), file=sys.stderr)
    S = pd.DataFrame(rows).T
    S.index = pd.to_datetime(S.index)
    S.to_csv(CACHE)

# QQQ benchmark
qclose = fetch_backtest_data(["QQQ"], date(2019, 12, 1), end)["Close"]
qqq = qclose["QQQ"] if hasattr(qclose, "columns") else qclose

S_w = S.resample("W-FRI").mean()                 # prior-5D (weekly) avg score
px_w = close.resample("W-FRI").last()            # weekly close
qqq_w = qqq.resample("W-FRI").last()

res = []
weeks = [d for d in px_w.index if d.year >= 2020]
for i in range(1, len(weeks)):
    cur, prev = weeks[i], weeks[i - 1]
    if prev not in S_w.index:
        continue
    avg = S_w.loc[prev].dropna().sort_values(ascending=False)
    if len(avg) < 20:
        continue
    ret = (px_w.loc[cur] / px_w.loc[prev] - 1) * 100.0
    top = ret.reindex(avg.head(10).index).mean()
    bot = ret.reindex(avg.tail(10).index).mean()
    univ = ret.reindex(avg.index).mean()
    qr = (qqq_w.loc[cur] / qqq_w.loc[prev] - 1) * 100.0 if (cur in qqq_w.index and prev in qqq_w.index) else np.nan
    res.append((cur, top, bot, univ, qr, len(avg)))

df = pd.DataFrame(res, columns=["week", "top", "bot", "univ", "qqq", "n"])
df["year"] = df["week"].apply(lambda d: d.year)
cmp = lambda s: (np.prod(1 + s.dropna() / 100) - 1) * 100

print("\n%-6s %9s %9s %9s %9s %10s %8s %5s" %
      ("YEAR", "TOP10", "BOT10", "UnivEW", "QQQ", "TOP-QQQ", "wks>0", "wks"))
for yr, g in df.groupby("year"):
    t, b, u, q = cmp(g["top"]), cmp(g["bot"]), cmp(g["univ"]), cmp(g["qqq"])
    hit = 100 * (g["top"] > 0).mean()
    print("%-6d %+8.1f%% %+8.1f%% %+8.1f%% %+8.1f%% %+9.1f%% %6.0f%% %5d"
          % (yr, t, b, u, q, t - q, hit, len(g)))

print("\nTOTAL 2020->now (compounded, weekly rebalance):")
for lbl, col in [("TOP-10 strategy", "top"), ("BOTTOM-10", "bot"),
                 ("Universe EW", "univ"), ("QQQ buy-hold", "qqq")]:
    g = df[col].dropna()
    grow = np.prod(1 + g / 100)
    ann = (grow ** (52.0 / len(g)) - 1) * 100
    wk_sh = (g.mean() / g.std() * np.sqrt(52)) if g.std() else 0
    print("  %-16s total %+8.1f%%   (x%.2f)   ann %+6.1f%%   wkSharpe %.2f"
          % (lbl, (grow - 1) * 100, grow, ann, wk_sh))
print("\nweeks: %d (%s -> %s)" % (len(df), df["week"].iloc[0].date(), df["week"].iloc[-1].date()))
