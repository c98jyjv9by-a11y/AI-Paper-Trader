"""Monthly score-spread table back to Jan 2020 + a yearly summary. Each month: rank by the PRIOR
month's average composite score, take top 10 / bottom 10, measure each basket's realized return over
that month. Per year: avg monthly spread, hit rate, and compounded top-vs-bottom basket returns.

Caveat: uses the CURRENT model_v4 universe; names that IPO'd later are simply absent (NaN) in early
years, so `n` (rankable names) grows over time — early-year baskets are drawn from a smaller set."""
import sys
import warnings
from datetime import date
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).parent / "src"))
import numpy as np
import pandas as pd

from backtest import load_config, fetch_backtest_data
from scenarios import load_scenario, build_config
from signals import calculate_signals, rank_candidates
from rank_report import _build_ticker_weights, _SIGNAL_WINDOW

cfg = build_config(load_config(Path(__file__).parent / "config"), load_scenario("model_v4"))
uni, w = cfg["tickers"], cfg["signals"].get("weights")
tw = _build_ticker_weights(cfg) or None

end = date.today()
pdata = fetch_backtest_data(uni, date(2018, 6, 1), end)        # signal-window history before Dec 2019
close = pdata["Close"]
days = [ts for ts in close.index if ts >= pd.Timestamp("2019-12-01")]
print("computing daily scores: %d days x %d tickers..." % (len(days), len(uni)), file=sys.stderr)

rows = {}
for i, ts in enumerate(days):
    sl = pdata.loc[:ts].iloc[-_SIGNAL_WINDOW:]
    rf = rank_candidates(calculate_signals(sl, uni), top_n=len(uni), weights=w, ticker_weights=tw)
    rows[ts] = dict(zip(rf["ticker"], rf["composite_score"]))
    if i % 200 == 0:
        print("  %d/%d" % (i, len(days)), file=sys.stderr)
S = pd.DataFrame(rows).T
S.index = pd.to_datetime(S.index)

S_m = S.groupby(S.index.to_period("M")).mean()
px_m = close.groupby(close.index.to_period("M")).last()

res = []
endp = pd.Period(f"{end.year}-{end.month:02d}", "M")
m = pd.Period("2020-01", "M")
while m <= endp:
    prior = m - 1
    if prior in S_m.index and m in px_m.index and prior in px_m.index:
        avg = S_m.loc[prior].dropna().sort_values(ascending=False)
        if len(avg) >= 20:
            fwd = (px_m.loc[m] / px_m.loc[prior] - 1) * 100.0
            tA = fwd.reindex(avg.head(10).index).mean()
            bA = fwd.reindex(avg.tail(10).index).mean()
            res.append((m, tA, bA, tA - bA, len(avg)))
    m += 1

df = pd.DataFrame(res, columns=["period", "top", "bot", "spread", "n"])
df["year"] = df["period"].apply(lambda p: p.year)
print("\n%-5s %9s %9s %9s %5s" % ("", "TOP10", "BOT10", "SPREAD", "n"))
for yr, g in df.groupby("year"):
    print("=== %d ===" % yr)
    for _, r in g.iterrows():
        star = " *partial" if r["period"] == endp and endp.month != 12 else ""
        print("  %-3s %+8.1f%% %+8.1f%% %+8.1f%%  %4d%s"
              % (r["period"].strftime("%b"), r["top"], r["bot"], r["spread"], r["n"], star))
    ct = (np.prod(1 + g["top"] / 100) - 1) * 100
    cb = (np.prod(1 + g["bot"] / 100) - 1) * 100
    print("  -- %d SUMMARY: avg spread %+.1f%% | spread>0 %d/%d mo | compounded TOP %+.1f%% vs BOT %+.1f%%  (gap %+.1f%%)\n"
          % (yr, g["spread"].mean(), int((g["spread"] > 0).sum()), len(g), ct, cb, ct - cb))

print("ALL-YEARS: avg monthly spread %+.1f%% | spread>0 %d/%d months (%.0f%%)"
      % (df["spread"].mean(), int((df["spread"] > 0).sum()), len(df), 100 * (df["spread"] > 0).mean()))
