"""Highest average composite score per ticker over 1M / YTD / 1Y / 3Y, + current-day return.
Recomputes the daily cross-sectional model_v4 scores (not stored anywhere as a per-ticker series)."""
import sys
import warnings
from datetime import date, timedelta
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).parent / "src"))
import pandas as pd

from backtest import load_config, fetch_backtest_data
from scenarios import load_scenario, build_config
from signals import calculate_signals, rank_candidates
from rank_report import _build_ticker_weights, _SIGNAL_WINDOW

cfg = build_config(load_config(Path(__file__).parent / "config"), load_scenario("model_v4"))
uni = cfg["tickers"]
w = cfg["signals"].get("weights")
tw = _build_ticker_weights(cfg) or None

end = date.today()
pdata = fetch_backtest_data(uni, end - timedelta(days=3 * 365 + 450), end)
close = pdata["Close"]
start3y = pd.Timestamp(end - timedelta(days=3 * 365))
days = [ts for ts in close.index if ts >= start3y]
print("computing daily scores: %d days x %d tickers..." % (len(days), len(uni)), file=sys.stderr)

rows = {}
for ts in days:
    sl = pdata.loc[:ts].iloc[-_SIGNAL_WINDOW:]
    rf = rank_candidates(calculate_signals(sl, uni), top_n=len(uni), weights=w, ticker_weights=tw)
    rows[ts] = dict(zip(rf["ticker"], rf["composite_score"]))
S = pd.DataFrame(rows).T
S.index = pd.to_datetime(S.index)

last, prev = close.index[-1], close.index[-2]
intr = (close.loc[last] / close.loc[prev] - 1) * 100.0          # current-day (latest bar vs prior close)

WINS = [("1M", end - timedelta(days=30)), ("YTD", date(2026, 1, 1)),
        ("1Y", end - timedelta(days=365)), ("3Y", end - timedelta(days=3 * 365))]
for label, st in WINS:
    sub = S[S.index >= pd.Timestamp(st)]
    avg = sub.mean().sort_values(ascending=False).head(10)
    print("\n=== highest AVG composite score — %s  (%s→%s, %d trading days) ==="
          % (label, pd.Timestamp(st).date(), last.date(), len(sub)))
    for t, v in avg.items():
        iv = intr.get(t)
        print("  %-6s  avg %.3f   today %s" % (t, v, "—" if pd.isna(iv) else f"{iv:+.2f}%"))
print("\n(current-day return = latest bar %s vs prior close %s)" % (last.date(), prev.date()))
