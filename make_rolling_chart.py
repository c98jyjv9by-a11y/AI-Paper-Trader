"""
Reproduce reports/rolling_1y_returns.png with two changes:
  - top panel: drop MTUM and SMH (keep SPY, QQQ)
  - bottom panel: drop the model_v4 portfolio return line (and its right axis)

Standalone: needs only yfinance + backtests/model_v4_daily_scores_10y.csv.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import yfinance as yf

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))
PANEL = ROOT / "backtests" / "model_v4_daily_scores_10y.csv"
TIMESERIES = ROOT / "backtests" / "model_v4_timeseries.csv"
OUT = ROOT / "reports" / "rolling_1y_returns_modified.png"

START, END = "2016-06-20", "2026-06-18"
DL_START = "2015-06-20"          # extra year for the 20d window + vol regime

# ── data ────────────────────────────────────────────────────────────────────────
panel = (pd.read_csv(PANEL, parse_dates=["date"])
         .drop_duplicates("date").set_index("date").sort_index())
panel = panel.loc[START:END]

px = yf.download(["SPY", "QQQ", "PSQ", "SOXS"], start=DL_START, end="2026-06-19",
                 auto_adjust=True, progress=False)["Close"]
px.index = pd.to_datetime(px.index).tz_localize(None)

ts = pd.read_csv(TIMESERIES, parse_dates=["date"]).set_index("date").sort_index()
book20 = ts["book_trl_20d"] * 100.0                   # model_v4 book trailing 20-day return, %

# hedge fire-dates from the codified overlay rule (up-shock + vol-surge), model untouched
import hedge_overlay as ho
_ov = ho.build_overlay(ts, ho.HedgeConfig())
HEDGE_DATES = _ov.index[_ov["hedge_on"]]
HEDGE_DATES = HEDGE_DATES[(HEDGE_DATES >= START) & (HEDGE_DATES <= END)]

# hedge PnL per hold-horizon — SOXS sized INVERSE-VOL (risk-targeted to the book), $100k book.
# Per-fire notional weight comes from the codified overlay (scales with book size & relative vols).
BOOK, RT = 100_000, 0.0010
_cfg_soxs = ho.HedgeConfig(product="soxs", sizing="inverse_vol")
_ov_soxs = ho.build_overlay(ts, _cfg_soxs)
_wf = _ov_soxs["weight"].reindex(HEDGE_DATES)          # per-fire SOXS weight (fraction of book)
_avgw = _wf[_wf > 0].mean()
_pnl = {}
for _h in (1, 5, 20):
    _r = ts["soxs_fwd_%dd" % _h].reindex(HEDGE_DATES)
    _pnl[_h] = ((_wf * _r - _wf * RT) * BOOK).dropna()
_p1 = _pnl[1]
_j16 = _ov_soxs["sleeve_pnl"].loc["2026-06-15"] * BOOK
CALLOUT = (
    f"SOXS hedge, inverse-vol sized (~{_avgw*100:.0f}% avg notional) on ${BOOK//1000}k book "
    f"— PnL by hold horizon (n={len(_p1)} fires)\n"
    f"  1-DAY (the rule):  net ${_p1.sum():+,.0f}   "
    f"[wins ${_p1[_p1>0].sum():+,.0f} / losses ${_p1[_p1<0].sum():+,.0f}, {100*(_p1>0).mean():.0f}% win]\n"
    f"  5-DAY:  ${_pnl[5].sum():+,.0f}      20-DAY:  ${_pnl[20].sum():+,.0f}   "
    f"->  strict 1-day exit is what saves $\n"
    f"  best 1D saves:  2020-03-13 ${_pnl[1].max():+,.0f} (book -9.0%)  -  "
    f"2026-06-16 ${_j16:+,.0f} (book -3.8%)"
)

r20 = px.pct_change(20) * 100.0                       # trailing 20-day return, %
spy_vol = px["SPY"].pct_change().rolling(21).std() * np.sqrt(252)   # annualized 21d vol
regime = spy_vol > 0.15                               # high-vol regime
spread20 = panel["top_minus_bottom_spread"].rolling(20).sum() * 100.0   # 20d spread, %

# ── high-vol regime spans (for axvspan shading) ──────────────────────────────────
def regime_spans(mask: pd.Series):
    spans, start = [], None
    for t, on in mask.items():
        if on and start is None:
            start = t
        elif not on and start is not None:
            spans.append((start, t)); start = None
    if start is not None:
        spans.append((start, mask.index[-1]))
    return spans

SPANS = regime_spans(regime.fillna(False))

def shade(ax):
    for lo, hi in SPANS:
        ax.axvspan(lo, hi, color="peachpuff", alpha=0.45, lw=0, zorder=0)

# ── figure ───────────────────────────────────────────────────────────────────────
fig, (ax0, ax1, ax2) = plt.subplots(3, 1, figsize=(12, 11.6), sharex=True)
fig.subplots_adjust(hspace=0.30, top=0.855)   # top margin reserved for the PnL call-out banner

# panel 1 — book (main series) vs long-exposure benchmarks (MTUM & SMH removed)
shade(ax0)
# the portfolio — solid blue line on the left axis
ax0.plot(book20.index, book20, color="royalblue", lw=1.0, zorder=5,
         label="model_v4 book (20d)")
# SOXS on a right axis (its -3x swings are ~10x the book's scale)
ax0b = ax0.twinx()
ax0b.plot(r20.index, r20["SOXS"], color="purple", lw=0.9, alpha=0.65, zorder=3,
          label="SOXS -3x semis (20d, right)")
ax0b.set_ylabel("SOXS 20d return (%)", color="purple")
ax0b.tick_params(axis="y", labelcolor="purple")
# ★ stars where the codified up-shock+vol hedge would be placed (on the portfolio line)
_star_y = book20.reindex(HEDGE_DATES)
ax0.scatter(HEDGE_DATES, _star_y, marker="*", s=130, color="gold",
            edgecolors="black", linewidths=0.6, zorder=7)
ax0.axhline(0, color="black", lw=0.6)
ax0.set_title("model_v4 portfolio vs SOXS hedge  —  ★ = hedge placed (up-shock + vol-surge)",
              fontweight="bold")
ax0.set_ylabel("book 20d return (%)", color="royalblue")
ax0.tick_params(axis="y", labelcolor="royalblue")
h, l = ax0.get_legend_handles_labels()
hb, lb = ax0b.get_legend_handles_labels()
h += hb; l += lb
h.append(Patch(facecolor="peachpuff", alpha=0.45)); l.append("high-vol regime (SPY 21d vol >15%)")
h.append(Line2D([0], [0], marker="*", color="none", markerfacecolor="gold",
                markeredgecolor="black", markersize=12))
l.append("hedge placed (n=%d)" % len(HEDGE_DATES))
ax0.legend(h, l, ncol=4, fontsize=8, loc="upper left", framealpha=0.9)
# quantified PnL call-out — placed in the reserved top margin, clear of the chart lines
fig.text(0.5, 0.975, CALLOUT, ha="center", va="top",
         family="monospace", fontsize=8.5, zorder=12, parse_math=False,
         bbox=dict(boxstyle="round,pad=0.5", facecolor="#fffbe6",
                   edgecolor="goldenrod", linewidth=1.2, alpha=1.0))

# panel 2 — SPY / QQQ
shade(ax1)
ax1.plot(r20.index, r20["SPY"], color="gray", lw=1.1, label="SPY")
ax1.plot(r20.index, r20["QQQ"], color="darkorange", lw=1.1, label="QQQ")
ax1.axhline(0, color="black", lw=0.6)
ax1.set_title("SPY / QQQ — trailing 20-day return", fontweight="bold")
ax1.set_ylabel("20d return (%)")
ax1.legend(ncol=2, fontsize=8, loc="upper left", framealpha=0.9)

# panel 3 — Top10-Bottom10 spread fill only (model_v4 line + right axis removed)
shade(ax2)
ax2.fill_between(spread20.index, spread20, 0, where=spread20 >= 0,
                 color="tab:green", alpha=0.75, lw=0, interpolate=True)
ax2.fill_between(spread20.index, spread20, 0, where=spread20 < 0,
                 color="salmon", alpha=0.85, lw=0, interpolate=True)
ax2.axhline(0, color="black", lw=0.6)
ax2.set_title("Top10−Bottom10 spread (20d, fill)", fontweight="bold")
ax2.set_ylabel("spread 20d (%)")

for ax in (ax0, ax1, ax2):
    ax.grid(True, alpha=0.25)
    ax.margins(x=0.01)

fig.savefig(OUT, dpi=130, bbox_inches="tight")
print("wrote", OUT)
