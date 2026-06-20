"""
Build reports/hedge_overlay_recommendation.pdf — a single combined recommendation
document for the model_v4 up-shock+vol 1-day hedge overlay.

Pulls everything together: the rule + rationale, the quantified $ value, the
rolling chart (with hedge stars + PnL banner), and the backtest window summary /
yearly walk-forward. Reproducible: reads the panel + hedge_overlay, regenerates
the chart, embeds it.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))
import hedge_overlay as ho

CHART = ROOT / "reports" / "rolling_1y_returns_modified.png"
OUT = ROOT / "reports" / "hedge_overlay_recommendation.pdf"

# ── regenerate the chart so the embedded copy is current ──────────────────────────
import subprocess
subprocess.run([sys.executable, str(ROOT / "make_rolling_chart.py")], check=True)

# ── metrics from the codified overlay (default short-SMH 0.30) ────────────────────
res = ho.run()
summ, wf = res["summary"], res["walk_forward"]

# ── per-horizon $ PnL on $100k (SOXS @10% = matched beta, matches the chart) ──────
df = pd.read_csv(ROOT / "backtests" / "model_v4_timeseries.csv", parse_dates=["date"]).set_index("date")
ov = ho.build_overlay(df, ho.HedgeConfig())
fires = ov.index[ov["hedge_on"]]
BOOK, W, RT = 100_000, 0.10, 0.0010
pnl = {h: ((W * df["soxs_fwd_%dd" % h].reindex(fires) - RT) * BOOK).dropna() for h in (1, 5, 20)}
p1 = pnl[1]
j16 = (W * df["soxs_fwd_1d"].loc["2026-06-15"] - RT) * BOOK


def _t(ax, x, y, s, **kw):
    ax.text(x, y, s, transform=ax.transAxes, va="top", parse_math=False, **kw)


with PdfPages(OUT) as pdf:
    # ============ PAGE 1 — recommendation ============
    fig = plt.figure(figsize=(8.5, 11)); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    _t(ax, 0.06, 0.965, "Hedge Overlay Recommendation", fontsize=20, fontweight="bold", color="#0b3d91")
    _t(ax, 0.06, 0.935, 'model_v4  —  "up-shock + vol-surge" 1-day semis hedge',
       fontsize=12, color="#333")
    _t(ax, 0.06, 0.917, "Standalone overlay (src/hedge_overlay.py); the model is NOT modified.",
       fontsize=8.5, color="#777", style="italic")

    def section(y, head, lines, hc="#0b3d91"):
        _t(ax, 0.06, y, head, fontsize=12, fontweight="bold", color=hc)
        yy = y - 0.024
        for ln in lines:
            _t(ax, 0.08, yy, ln, fontsize=9, family="monospace", color="#222")
            yy -= 0.0185
        return yy - 0.012

    y = 0.880
    y = section(y, "THE RULE  (decide at close T, hold T+1 only, exit next close)", [
        "FIRE if:   QQQ 1-day return >= +2%   AND   z(SPY 5d realized vol, 63d) >= 1.0",
        "THEN buy:  short-SMH ~30% notional (default)  OR  SOXS ~10% (matched -0.30 beta)",
    ])
    y = section(y, "WHY IT WORKS", [
        "- Targets the Jun-16 pattern: a sharp up day on surging vol -> next-day pullback.",
        "- No single factor works alone (a QQQ up-day alone BOUNCES); the edge is the",
        "  INTERACTION of up-shock x elevated vol.",
        "- Best supporting signal (sensitivity): 5-day realized-vol z-score. Relative vol",
        "  beats absolute level / surge-ratio; the 5d window beats 1d and 20d.",
    ])
    y = section(y, f"QUANTIFIED VALUE   ($100k book, SOXS @10%, {len(p1)} fires)", [
        f"1-DAY hold (THE RULE):  net ${p1.sum():+,.0f}   "
        f"[wins ${p1[p1>0].sum():+,.0f} / losses ${p1[p1<0].sum():+,.0f}, {100*(p1>0).mean():.0f}% win]",
        f"if held 5D:  ${pnl[5].sum():+,.0f}      if held 20D:  ${pnl[20].sum():+,.0f}   "
        f"->  the 1-day exit IS the edge",
        f"best saves:  2020-03-13 ${pnl[1].max():+,.0f} (book -9.0%)   -   "
        f"2026-06-16 ${j16:+,.0f} (book -3.8%)",
    ], hc="#0a5d00")
    sf = summ["FULL"]; so = summ["OOS"]
    y = section(y, "RISK-ADJUSTED  (default short-SMH 0.30)", [
        "FULL:  dSharpe %+.2f   sleeve PnL %+.1f%%   worst on-day -9.0%% -> -4.7%%" % (sf["d_sh"], sf["sleeve"]),
        "OOS (>=2024):  dSharpe %+.2f   sleeve %+.1f%%" % (so["d_sh"], so["sleeve"]),
        "Walk-forward: %d/%d active years dSharpe>0; gains concentrated in vol-spike years"
        % (sum(1 for r in wf.values() if r["on"] and r["d_sh"] > 0),
           sum(1 for r in wf.values() if r["on"])),
    ])
    section(y, "CAVEATS", [
        "- A Sharpe-adder + single-day-blow softener, NOT an all-time-max-drawdown reducer.",
        "- Edge concentrates in vol spikes; marginal in calm years; slightly -ve in 2022 bear.",
        "- SOXS spread/decay understated by flat 10bp; short-SMH is cheaper & decay-free.",
        "- Paper / recommendation only. Re-validate after any model or universe change.",
    ], hc="#8a1a1a")
    pdf.savefig(fig); plt.close(fig)

    # ============ PAGE 2 — chart ============
    img = mpimg.imread(CHART); h, w = img.shape[:2]
    fig = plt.figure(figsize=(11, 11 * h / w)); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.imshow(img)
    pdf.savefig(fig, dpi=150); plt.close(fig)

    # ============ PAGE 3 — window summary + walk-forward ============
    fig = plt.figure(figsize=(11, 8.5)); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    _t(ax, 0.04, 0.96, "Backtest — windows & yearly walk-forward", fontsize=15, fontweight="bold", color="#0b3d91")
    _t(ax, 0.04, 0.935, "Default config: short-SMH 0.30, trigger qqq_1d>=2%% & z(spy_vol_5d)>=1.  "
       "dSh = hedged minus book Sharpe; dDD = max-drawdown change (+=better).", fontsize=8, color="#666")
    yy = 0.895
    _t(ax, 0.04, yy, "WINDOW SUMMARY", fontsize=10.5, fontweight="bold"); yy -= 0.028
    hdr = "%-12s %5s %4s | %7s %7s %7s | %7s %7s | %8s %6s %8s" % (
        "window", "days", "on", "bookSh", "hedSh", "dSh", "bookDD", "dDD", "onBook%", "paid%", "sleeve%")
    _t(ax, 0.04, yy, hdr, fontsize=8.2, family="monospace", color="#000"); yy -= 0.020
    for wn, r in summ.items():
        ob = "%.2f" % r["on_book"] if r["on"] else "na"
        pdv = "%.0f" % r["paid"] if r["on"] else "na"
        _t(ax, 0.04, yy, "%-12s %5d %4d | %+7.2f %+7.2f %+7.2f | %6.1f%% %+6.1f%% | %8s %6s %+7.2f%%" % (
            wn, r["days"], r["on"], r["book_sh"], r["hed_sh"], r["d_sh"], r["book_dd"], r["d_dd"], ob, pdv, r["sleeve"]),
           fontsize=8.2, family="monospace"); yy -= 0.020
    yy -= 0.02
    _t(ax, 0.04, yy, "YEARLY WALK-FORWARD", fontsize=10.5, fontweight="bold"); yy -= 0.028
    _t(ax, 0.04, yy, hdr.replace("window", "year  "), fontsize=8.2, family="monospace"); yy -= 0.020
    for year, r in wf.items():
        ob = "%.2f" % r["on_book"] if r["on"] else "na"
        pdv = "%.0f" % r["paid"] if r["on"] else "na"
        col = "#0a5d00" if (r["on"] and r["d_sh"] > 0) else ("#8a1a1a" if r["on"] else "#999")
        _t(ax, 0.04, yy, "%-12d %5d %4d | %+7.2f %+7.2f %+7.2f | %6.1f%% %+6.1f%% | %8s %6s %+7.2f%%" % (
            year, r["days"], r["on"], r["book_sh"], r["hed_sh"], r["d_sh"], r["book_dd"], r["d_dd"], ob, pdv, r["sleeve"]),
           fontsize=8.2, family="monospace", color=col); yy -= 0.020
    _t(ax, 0.04, yy - 0.01, "Source: backtests/hedge_overlay_model_v4_summary.md  |  panel "
       "model_v4_timeseries.csv (%s to %s)" % (df.index.min().date(), df.index.max().date()),
       fontsize=7.5, color="#888", style="italic")
    pdf.savefig(fig); plt.close(fig)

print("wrote", OUT)
