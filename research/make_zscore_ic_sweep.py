"""IC sweep: trailing-avg z-score vs forward returns. z = per-ticker 60-DAY rolling z of the model_v4
composite (60d history fixed). Sweep the AVG-Z trailing window {1,2,3,4,5,10}d x forward-return horizon
{1,2,3,4,5,10}d. Cell = average daily CROSS-SECTIONAL rank-IC (Spearman) between the trailing-avg-z and
the forward return, across the universe. Negative = mean-reversion (low z predicts high forward return).
Reuses the cached score panel. 2020+ (z warmup)."""
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
close = fetch_backtest_data(cfg["tickers"], date(2018, 6, 1), date.today())["Close"]
S = pd.read_csv(ROOT / "backtests" / "daily_scores_model_v4.csv", index_col=0, parse_dates=True)
Z = (S - S.rolling(60).mean()) / S.rolling(60).std()           # per-ticker 60-day rolling z

AVG_WIN = [1, 2, 3, 4, 5, 10]
FWD = [1, 2, 3, 4, 5, 10]
dates = Z.index[Z.index.year >= 2020]                          # where z is valid
fwd_ret = {h: (close.shift(-h) / close - 1) for h in FWD}      # forward h-day return per ticker


def ic(avgz, fwd):
    a = avgz.reindex(dates)
    f = fwd.reindex(dates).reindex(columns=a.columns)
    daily = a.rank(axis=1).corrwith(f.rank(axis=1), axis=1)    # Pearson of ranks = Spearman rank-IC (no scipy)
    return daily.mean()


print("Average cross-sectional rank-IC  (trailing-avg-z  vs  forward return)")
print("z = 60-day rolling z; negative = mean-reversion edge.  2020+\n")
print("avg-z\\fwd | " + " ".join("%6dD" % h for h in FWD))
print("-" * (11 + 7 * len(FWD)))
best = (None, 0.0)
for aw in AVG_WIN:
    avgz = Z.rolling(aw).mean()
    row = []
    for h in FWD:
        v = ic(avgz, fwd_ret[h])
        row.append(v)
        if v < best[1]:
            best = ((aw, h), v)
    print("%6dD   | " % aw + " ".join("%+6.3f" % v for v in row))
print("-" * (11 + 7 * len(FWD)))
print("\nstrongest reversal IC: %dd-avg-z vs %dd-fwd  ->  IC %+.3f" % (best[0][0], best[0][1], best[1]))
