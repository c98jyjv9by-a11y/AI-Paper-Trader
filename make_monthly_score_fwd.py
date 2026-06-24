"""For each month of 2026: rank tickers by their AVERAGE composite score in the PRIOR month, take the
top 10 / bottom 10, and show each name's realized forward 1-month return (the return over THAT month).
Tests whether prior-month score predicts next-month return, monthly, top vs bottom."""
import sys
import warnings
from datetime import date
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
pdata = fetch_backtest_data(uni, date(2024, 6, 1), end)
close = pdata["Close"]
days = [ts for ts in close.index if ts >= pd.Timestamp("2025-12-01")]   # need Dec-2025 for Jan ranking
print("computing daily scores: %d days x %d tickers..." % (len(days), len(uni)), file=sys.stderr)

rows = {}
for ts in days:
    sl = pdata.loc[:ts].iloc[-_SIGNAL_WINDOW:]
    rf = rank_candidates(calculate_signals(sl, uni), top_n=len(uni), weights=w, ticker_weights=tw)
    rows[ts] = dict(zip(rf["ticker"], rf["composite_score"]))
S = pd.DataFrame(rows).T
S.index = pd.to_datetime(S.index)

S_m = S.groupby(S.index.to_period("M")).mean()            # month -> avg score per ticker
px_m = close.groupby(close.index.to_period("M")).last()   # month -> month-end (last) price per ticker
MONTHS = ["", "January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]

last_bar = close.index[-1]
for m in range(1, 7):                                     # Jan..Jun 2026
    prior = pd.Period("2025-12", "M") if m == 1 else pd.Period(f"2026-{m - 1:02d}", "M")
    cur = pd.Period(f"2026-{m:02d}", "M")
    if prior not in S_m.index or cur not in px_m.index:
        continue
    avg = S_m.loc[prior].dropna().sort_values(ascending=False)
    fwd = (px_m.loc[cur] / px_m.loc[prior] - 1) * 100.0   # realized return OVER month m
    partial = " (PARTIAL, through %s)" % last_bar.date() if m == end.month and end.year == 2026 else ""
    top, bot = avg.head(10), avg.tail(10)
    tA, bA = fwd.reindex(top.index).mean(), fwd.reindex(bot.index).mean()
    print("\n=== %s 2026 — ranked by %s avg score; forward = %s return%s ==="
          % (MONTHS[m].upper(), MONTHS[prior.month], MONTHS[m], partial))
    print("  TOP 10 by prior-mo score            BOTTOM 10 by prior-mo score")
    for (tt, ts_), (bt, bs_) in zip(top.items(), bot.items()):
        tf, bf = fwd.get(tt), fwd.get(bt)
        print("   %-6s score %.2f  fwd %+6.1f%%      %-6s score %.2f  fwd %+6.1f%%"
              % (tt, ts_, (tf if pd.notna(tf) else 0), bt, bs_, (bf if pd.notna(bf) else 0)))
    print("   -> TOP10 avg fwd %+.1f%%               BOTTOM10 avg fwd %+.1f%%   |  spread %+.1f%%"
          % (tA, bA, tA - bA))
