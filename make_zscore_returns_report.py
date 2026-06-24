"""PDF (sibling of make_score_returns_report): rank by a per-ticker 60-DAY ROLLING Z-SCORE of the
composite score — z_t = (score_t - mean of the ticker's score over the trailing 60 days) / its 60-day std.
Each table ranks by the AVERAGE of that 60-day z over the table's horizon: 1D = latest z (at yesterday's
close), 5D = avg z over the last 5 days, 30D, 60D. The z is ALWAYS 60-day-based; the horizon only averages
it. Top/bottom 10 + AVG row + heat-mapped trailing 1D/5D/20D/30D/60D returns. -> reports/score_zscore_returns_<date>.pdf
"""
import sys
import warnings
import datetime as dt
from pathlib import Path

warnings.filterwarnings("ignore")
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from backtest import load_config, fetch_backtest_data
from scenarios import load_scenario, build_config

ZWIN = 60                                                          # all z-scores use a 60-day lookback
cfg = build_config(load_config(ROOT / "config"), load_scenario("model_v4"))
uni = cfg["tickers"]
pdata = fetch_backtest_data(uni, dt.date.today() - dt.timedelta(days=260), dt.date.today())
close = pdata["Close"]
idx = close.index
latest, ystd = idx[-1], idx[-2]                                   # latest=returns (intraday); ystd=score anchor

# composite scores up to yesterday — reuse the cached panel if it reaches yesterday, else recompute the tail
S = pd.DataFrame()
CACHE = ROOT / "backtests" / "daily_scores_model_v4.csv"
if CACHE.exists():
    Sc = pd.read_csv(CACHE, index_col=0, parse_dates=True)
    Sc = Sc[Sc.index <= ystd]
    if not Sc.empty and Sc.index[-1] >= ystd:
        S = Sc.tail(135)
if S.empty:
    from signals import calculate_signals, rank_candidates
    from rank_report import _build_ticker_weights, _SIGNAL_WINDOW
    w, tw = cfg["signals"].get("weights"), _build_ticker_weights(cfg) or None
    days = idx[idx <= ystd][-135:]                                # 60d z-window + 60d averaging + buffer
    print("scoring %d days through %s ..." % (len(days), ystd.date()), file=sys.stderr)
    rows = {}
    for ts in days:
        sl = pdata.loc[:ts].iloc[-_SIGNAL_WINDOW:]
        rf = rank_candidates(calculate_signals(sl, uni), top_n=len(uni), weights=w, ticker_weights=tw)
        rows[ts] = dict(zip(rf["ticker"], rf["composite_score"]))
    S = pd.DataFrame(rows).T
    S.index = pd.to_datetime(S.index)

Z = (S - S.rolling(ZWIN).mean()) / S.rolling(ZWIN).std()          # per-ticker 60-day rolling z-score

WINDOWS = [("Latest 60-day z-score (1-day)", Z.iloc[-1]),
           ("Avg 60-day z-score over the last 5 days", Z.iloc[-5:].mean()),
           ("Avg 60-day z-score over the last 30 days", Z.iloc[-30:].mean()),
           ("Avg 60-day z-score over the last 60 days", Z.iloc[-60:].mean())]
RWIN = [("1D", 1), ("5D", 5), ("20D", 20), ("30D", 30), ("60D", 60)]
CMAP = plt.get_cmap("RdYlGn")


def ret(t, n):
    try:
        a, b = close[t].iloc[-1], close[t].iloc[-1 - n]
        return a / b - 1 if (b and not np.isnan(b) and not np.isnan(a)) else np.nan
    except Exception:
        return np.nan


def pct(x):
    return "—" if (x is None or (isinstance(x, float) and np.isnan(x))) else f"{x * 100:+.1f}%"


def _heat(x, scale):
    if x != x:
        return "#f2f2f2"
    return CMAP(max(0.0, min(1.0, 0.5 + 0.5 * (x / (scale or 1.0)))))


def draw(ax, title, names, zv):
    ax.axis("off")
    ax.set_title(title, fontsize=10, weight="bold", loc="left", color="#333")
    cols = ["Ticker", "Z"] + [r[0] for r in RWIN]
    rmat = [[ret(t, n) for _, n in RWIN] for t in names]
    col_scale = [max([abs(rmat[i][j]) for i in range(len(names)) if rmat[i][j] == rmat[i][j]] or [1.0])
                 for j in range(len(RWIN))]
    cell = [[t, "%+.2f" % zv[t]] + [pct(x) for x in rmat[i]] for i, t in enumerate(names)]
    avg_rs = [np.nanmean([rmat[i][j] for i in range(len(names))]) for j in range(len(RWIN))]
    cell.append(["AVG", "%+.2f" % np.nanmean([zv[t] for t in names])] + [pct(x) for x in avg_rs])
    rmat.append(avg_rs)
    tbl = ax.table(cellText=cell, colLabels=cols, loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8)
    tbl.scale(1, 1.32)
    for j in range(len(cols)):
        tbl[0, j].set_facecolor("#34495e")
        tbl[0, j].set_text_props(color="white", weight="bold")
    for i, rs in enumerate(rmat):
        for j, x in enumerate(rs):
            tbl[i + 1, 2 + j].set_facecolor(_heat(x, col_scale[j]))
    avg_row = len(names) + 1
    for j in range(len(cols)):
        tbl[avg_row, j].set_text_props(weight="bold")
        if j < 2:
            tbl[avg_row, j].set_facecolor("#d5d8dc")
    return tbl


out = ROOT / "reports" / f"score_zscore_returns_{dt.date.today().isoformat()}.pdf"
out.parent.mkdir(exist_ok=True)
with PdfPages(out) as pdf:
    for title, zv in WINDOWS:
        zz = zv.dropna().sort_values(ascending=False)
        top = list(zz.head(10).index)
        bot = list(zz.tail(10).sort_values().index)
        fig, (a1, a2) = plt.subplots(2, 1, figsize=(11, 8.5))
        fig.suptitle("model_v4 — %s\nZ = per-ticker 60-day rolling z of composite score (vs the ticker's OWN "
                     "norm). Returns trailing as of %s (intraday); cells heat-mapped per column; AVG = basket mean."
                     % (title, latest.date()), fontsize=11.5, weight="bold")
        draw(a1, "TOP 10 (highest z)", top, zv)
        draw(a2, "BOTTOM 10 (lowest z)", bot, zv)
        fig.subplots_adjust(top=0.85, hspace=0.2)
        pdf.savefig(fig)
        plt.close(fig)
print("wrote", out)
