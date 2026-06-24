"""Re-run the winner (60-day score / monthly / top-10) on a BROADER, existence-gated pool to reduce
selection bias. Recomputes cross-sectional scores within the broad pool (ranks change with the universe).
Compares broad vs curated-83, full + train/test, vs QQQ.

NOT fully survivorship-free: the broad pool is still today's survivors (no delisted names available),
so this strips IPO look-ahead + narrow-83-curation, but NOT delisting survivorship."""
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

BROAD = ['NVDA','AMD','INTC','QCOM','AVGO','TXN','AMAT','MU','ADI','KLAC','LRCX','ASML','TSM','NXPI',
         'MCHP','SWKS','TER','ON','STX','WDC','MRVL','MPWR','AAPL','MSFT','GOOGL','AMZN','META','NFLX',
         'ORCL','CRM','ADBE','INTU','CSCO','IBM','NOW','WDAY','ANSS','CDNS','SNPS','VRSN','AKAM','FTNT',
         'ADSK','PANW','TSLA','EBAY','BKNG','SHOP','PYPL','ZS','DDOG','CRWD','NET','SNOW','OKTA','TTD',
         'HUBS','TWLO']
cfg = build_config(load_config(ROOT / "config"), load_scenario("model_v4"))
mv4 = list(cfg["tickers"])
uni = sorted(set(mv4) | set(BROAD))
w, tw = cfg["signals"].get("weights"), _build_ticker_weights(cfg) or None
print("curated-83=%d  broad-union=%d names" % (len(mv4), len(uni)), file=sys.stderr)

pdata_b = fetch_backtest_data(uni, date(2018, 6, 1), date.today())
close_b = pdata_b["Close"]
qqq = fetch_backtest_data(["QQQ"], date(2018, 6, 1), date.today())["Close"]
qqq = qqq["QQQ"] if hasattr(qqq, "columns") else qqq

CACHE = ROOT / "backtests" / "daily_scores_broad.csv"
if CACHE.exists():
    Sb = pd.read_csv(CACHE, index_col=0, parse_dates=True)
else:
    days = [ts for ts in close_b.index if ts >= pd.Timestamp("2019-12-01")]
    print("computing broad-pool daily scores: %d days x %d names..." % (len(days), len(uni)), file=sys.stderr)
    rows = {}
    for i, ts in enumerate(days):
        sl = pdata_b.loc[:ts].iloc[-_SIGNAL_WINDOW:]
        # existence gate is automatic: calculate_signals drops names with insufficient history (NaN signals)
        rf = rank_candidates(calculate_signals(sl, uni), top_n=len(uni), weights=w, ticker_weights=tw)
        rows[ts] = dict(zip(rf["ticker"], rf["composite_score"]))
        if i % 200 == 0:
            print("  %d/%d" % (i, len(days)), file=sys.stderr)
    Sb = pd.DataFrame(rows).T
    Sb.index = pd.to_datetime(Sb.index)
    Sb.to_csv(CACHE)

Sc = pd.read_csv(ROOT / "backtests" / "daily_scores_model_v4.csv", index_col=0, parse_dates=True)  # curated-83
close_c = fetch_backtest_data(mv4, date(2018, 6, 1), date.today())["Close"]


def top10_monthly(S, close):
    S60 = S.rolling(60).mean()
    px = close.resample("ME").last()
    sc = S60.reindex(px.index, method="ffill")
    dts = [d for d in px.index if d.year >= 2020]
    out = []
    for i in range(1, len(dts)):
        cur, prev = dts[i], dts[i - 1]
        avg = sc.loc[prev].dropna().sort_values(ascending=False)
        if len(avg) < 20:
            continue
        ret = (px.loc[cur] / px.loc[prev] - 1) * 100.0
        out.append((cur, ret.reindex(avg.head(10).index).mean(), len(avg)))
    return pd.DataFrame(out, columns=["d", "r", "n"]).set_index("d")


def stat(s, per=12):
    g = s.dropna() / 100
    grow = np.prod(1 + g)
    return (grow ** (per / len(g)) - 1) * 100, (g.mean() / g.std() * np.sqrt(per) if g.std() else 0)


broad, cur = top10_monthly(Sb, close_b), top10_monthly(Sc, close_c)
qm = (qqq.resample("ME").last().pct_change() * 100).dropna()
qm = qm[qm.index.year >= 2020]
SPLITS = [("FULL 2020-26", 2020, 2099), ("TRAIN 2020-22", 2020, 2022), ("TEST 2023-26", 2023, 2099)]
print("\n60-day / MONTHLY / top-10  —  CURATED-83 vs BROAD-%d pool (annualized%% / Sharpe)\n" % len(uni))
print("%-15s | %-15s | %-15s | %-15s" % ("SPLIT", "CURATED-83", "BROAD pool", "QQQ"))
print("-" * 70)
for lbl, y0, y1 in SPLITS:
    bm = (broad.index.year >= y0) & (broad.index.year <= y1)
    cm = (cur.index.year >= y0) & (cur.index.year <= y1)
    qmm = (qm.index.year >= y0) & (qm.index.year <= y1)
    ca, cs = stat(cur.loc[cm, "r"]); ba, bs = stat(broad.loc[bm, "r"]); qa, qs = stat(qm[qmm])
    print("%-15s | %+7.1f%% / %.2f | %+7.1f%% / %.2f | %+7.1f%% / %.2f"
          % (lbl, ca, cs, ba, bs, qa, qs))
print("\nbroad-pool rankable names/month: min %d -> max %d (existence-gated)"
      % (int(broad["n"].min()), int(broad["n"].max())))
