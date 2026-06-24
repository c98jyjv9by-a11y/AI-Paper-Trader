"""PDF: for the model_v4 universe, rank by 4 score windows AS OF YESTERDAY'S CLOSE — (1) yesterday's
single-day composite, (2) trailing 5-day avg, (3) trailing 30-day avg, (4) trailing 60-day avg — and for
the top-10 and bottom-10 of each, show trailing 1D(intraday)/5D/20D/30D/60D returns (as of the latest bar).
Writes reports/score_returns_<date>.pdf."""
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
from signals import calculate_signals, rank_candidates
from rank_report import _build_ticker_weights, _SIGNAL_WINDOW

cfg = build_config(load_config(ROOT / "config"), load_scenario("model_v4"))
uni, w = cfg["tickers"], cfg["signals"].get("weights")
tw = _build_ticker_weights(cfg) or None

pdata = fetch_backtest_data(uni, dt.date.today() - dt.timedelta(days=220), dt.date.today())
close = pdata["Close"]
idx = close.index
latest, ystd = idx[-1], idx[-2]                       # latest (intraday) for returns; yesterday close for scores
score_days = idx[idx <= ystd][-60:]                   # last 60 completed closes, ending yesterday
print("scoring %d days through %s ..." % (len(score_days), ystd.date()), file=sys.stderr)

rows = {}
for ts in score_days:
    sl = pdata.loc[:ts].iloc[-_SIGNAL_WINDOW:]
    rf = rank_candidates(calculate_signals(sl, uni), top_n=len(uni), weights=w, ticker_weights=tw)
    rows[ts] = dict(zip(rf["ticker"], rf["composite_score"]))
S = pd.DataFrame(rows).T

WINDOWS = [("Yesterday's close score (1-day composite)", S.iloc[-1]),
           ("Trailing 5-day avg score (at yesterday's close)", S.iloc[-5:].mean()),
           ("Trailing 30-day avg score", S.iloc[-30:].mean()),
           ("Trailing 60-day avg score", S.iloc[-60:].mean())]
RWIN = [("1D", 1), ("5D", 5), ("20D", 20), ("30D", 30), ("60D", 60)]


def ret(t, n):
    try:
        a, b = close[t].iloc[-1], close[t].iloc[-1 - n]
        return a / b - 1 if (b and not np.isnan(b) and not np.isnan(a)) else np.nan
    except Exception:
        return np.nan


def pct(x):
    return "—" if (x is None or (isinstance(x, float) and np.isnan(x))) else f"{x * 100:+.1f}%"


CMAP = plt.get_cmap("RdYlGn")


def _heat(x, scale):
    if x != x:
        return "#f2f2f2"
    return CMAP(max(0.0, min(1.0, 0.5 + 0.5 * (x / (scale or 1.0)))))      # diverging, centered at 0


def draw(ax, title, names, sc):
    ax.axis("off")
    ax.set_title(title, fontsize=10, weight="bold", loc="left", color="#333")
    cols = ["Ticker", "Score"] + [r[0] for r in RWIN]
    rmat = [[ret(t, n) for _, n in RWIN] for t in names]
    col_scale = [max([abs(rmat[i][j]) for i in range(len(names)) if rmat[i][j] == rmat[i][j]] or [1.0])
                 for j in range(len(RWIN))]                                 # per-column heatmap scale
    cell = [[t, "%.3f" % sc[t]] + [pct(x) for x in rmat[i]] for i, t in enumerate(names)]
    avg_rs = [np.nanmean([rmat[i][j] for i in range(len(names))]) for j in range(len(RWIN))]
    cell.append(["AVG", "%.3f" % np.nanmean([sc[t] for t in names])] + [pct(x) for x in avg_rs])
    rmat.append(avg_rs)
    tbl = ax.table(cellText=cell, colLabels=cols, loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8)
    tbl.scale(1, 1.32)
    for j in range(len(cols)):                                             # header
        tbl[0, j].set_facecolor("#34495e")
        tbl[0, j].set_text_props(color="white", weight="bold")
    for i, rs in enumerate(rmat):                                          # heatmap the return cells
        for j, x in enumerate(rs):
            tbl[i + 1, 2 + j].set_facecolor(_heat(x, col_scale[j]))
    avg_row = len(names) + 1                                                # AVG row emphasis
    for j in range(len(cols)):
        tbl[avg_row, j].set_text_props(weight="bold")
        if j < 2:
            tbl[avg_row, j].set_facecolor("#d5d8dc")
    return tbl


out = ROOT / "reports" / f"score_returns_{dt.date.today().isoformat()}.pdf"
out.parent.mkdir(exist_ok=True)
with PdfPages(out) as pdf:
    for title, sc in WINDOWS:
        scc = sc.dropna().sort_values(ascending=False)
        top = list(scc.head(10).index)
        bot = list(scc.tail(10).sort_values().index)
        fig, (a1, a2) = plt.subplots(2, 1, figsize=(11, 8.5))
        fig.suptitle("model_v4 — %s\nReturns trailing, as of %s (intraday); 1D = today's move. "
                     "Cells heat-mapped per column; AVG = basket mean."
                     % (title, latest.date()), fontsize=12, weight="bold")
        draw(a1, "TOP 10 (highest score)", top, sc)
        draw(a2, "BOTTOM 10 (lowest score)", bot, sc)
        fig.subplots_adjust(top=0.86, hspace=0.2)
        pdf.savefig(fig)
        plt.close(fig)
print("wrote", out)
