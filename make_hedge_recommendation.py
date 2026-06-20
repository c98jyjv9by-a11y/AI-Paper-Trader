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
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))
import hedge_overlay as ho

CHART = ROOT / "reports" / "rolling_1y_returns_modified.png"
OUT = ROOT / "reports" / "hedge_overlay_recommendation.pdf"
TMP = ROOT / "reports" / "_rec_core.pdf"
# correlation / gap analysis appendices (built previously) to merge in after the recommendation
APPENDICES = [
    ("Appendix A — Correlation & Gap Analysis (full history 2016-2026)",
     ROOT / "reports" / "corr_tails_by_horizon.pdf"),
    ("Appendix B — Correlation & Gap Analysis (since-COVID, vol-normalized)",
     ROOT / "reports" / "corr_tails_by_horizon_since_covid_volz.pdf"),
]

# ── regenerate the chart so the embedded copy is current ──────────────────────────
import subprocess
subprocess.run([sys.executable, str(ROOT / "make_rolling_chart.py")], check=True)

# ── metrics from the codified overlay (default SOXS inverse-vol) ─────────────────
res = ho.run()
summ, wf = res["summary"], res["walk_forward"]

# ── per-horizon $ PnL on $100k — SOXS (long -3x inverse semis) sized INVERSE-VOL ──
df = pd.read_csv(ROOT / "backtests" / "model_v4_timeseries.csv", parse_dates=["date"]).set_index("date")
ov = ho.build_overlay(df, ho.HedgeConfig())                          # default = SOXS inverse-vol (long, no shorting)
fires = ov.index[ov["hedge_on"]]
BOOK, RT = 100_000, 0.0010
wf_ = ov["weight"].reindex(fires)
avg_w = wf_[wf_ > 0].mean()
_won = ov["hedge_on"]
worst_b = ov["book_ret"][_won].min() * 100
worst_h = (ov["book_ret"] + ov["sleeve_pnl"])[_won].min() * 100
pnl = {h: ((wf_ * df["soxs_fwd_%dd" % h].reindex(fires) - wf_ * RT) * BOOK).dropna() for h in (1, 5, 20)}
p1 = pnl[1]
j16 = ov["sleeve_pnl"].loc["2026-06-15"] * BOOK

# ── June-16 case study numbers ────────────────────────────────────────────────────
_T, _N = pd.Timestamp("2026-06-15"), pd.Timestamp("2026-06-16")
_volz = ((df["spy_vol_trl_5d"] - df["spy_vol_trl_5d"].rolling(63).mean().shift(1))
         / df["spy_vol_trl_5d"].rolling(63).std().shift(1))
CS = dict(
    qqq_up=df["qqq_trl_1d"].loc[_T] * 100, book_up=df["book_trl_1d"].loc[_T] * 100,
    volz=_volz.loc[_T],
    book_nx=df.loc[_N, "book_trl_1d"] * 100, top10=df.loc[_N, "top10_trl_1d"] * 100,
    smh=df.loc[_N, "smh_trl_1d"] * 100, qqq=df.loc[_N, "qqq_trl_1d"] * 100,
    spy=df.loc[_N, "spy_trl_1d"] * 100, spread=df.loc[_N, "spread_trl_1d"] * 100,
    w_soxs=ov["weight"].loc[_T] * 100,
    hed_soxs=ov["sleeve_pnl"].loc[_T] * 100, hed_usd=j16,
    softened=(df["book_fwd_1d"].loc[_T] + ov["sleeve_pnl"].loc[_T]) * 100,
)


def _t(ax, x, y, s, **kw):
    ax.text(x, y, s, transform=ax.transAxes, va="top", parse_math=False, **kw)


with PdfPages(TMP) as pdf:
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
        "FIRE (two gates):  SOFT  QQQ>=+1.5% & z(SPY 5d vol,63d)>=0.75  -> HALF size",
        "                   HARD  QQQ>=+2.0% & z>=1.00                   -> FULL size",
        f"THEN buy:  SOXS (long -3x inverse semis; no shorting), inverse-vol sized off",
        f"           CURRENT position market value (ex-cash); full ~{avg_w*100:.0f}% / half ~{avg_w*50:.0f}% of exposure.",
    ])
    y = section(y, "WHAT IT TARGETS", [
        "- Sharp up-days that occur while volatility is already elevated -- a combination",
        "  that tends to mean-revert (pull back) the next session.",
        "- No single factor works alone (a QQQ up-day alone BOUNCES); the edge is the",
        "  INTERACTION of up-shock x elevated vol.",
        "- Best supporting signal (sensitivity): 5-day realized-vol z-score. Relative vol",
        "  beats absolute level / surge-ratio; the 5d window beats 1d and 20d.",
    ])
    y = section(y, f"QUANTIFIED VALUE   ($100k book, SOXS inverse-vol ~{avg_w*100:.0f}% avg, {len(p1)} fires)", [
        f"1-DAY hold (THE RULE):  net ${p1.sum():+,.0f}   "
        f"[wins ${p1[p1>0].sum():+,.0f} / losses ${p1[p1<0].sum():+,.0f}, {100*(p1>0).mean():.0f}% win]",
        f"if held 5D:  ${pnl[5].sum():+,.0f}      if held 20D:  ${pnl[20].sum():+,.0f}   "
        f"->  the 1-day exit IS the edge",
        f"best saves:  2020-03-13 ${pnl[1].max():+,.0f} (book -9.0%)   -   "
        f"2026-06-16 ${j16:+,.0f} (book -3.8%)",
    ], hc="#0a5d00")
    sf = summ["FULL"]; so = summ["OOS"]
    y = section(y, "RISK-ADJUSTED  (SOXS inverse-vol)", [
        "FULL:  dSharpe %+.2f   sleeve PnL %+.1f%%   worst on-day %+.1f%% -> %+.1f%%"
        % (sf["d_sh"], sf["sleeve"], worst_b, worst_h),
        "OOS (>=2024):  dSharpe %+.2f   sleeve %+.1f%%" % (so["d_sh"], so["sleeve"]),
        "Walk-forward: %d/%d active years dSharpe>0; gains concentrated in vol-spike years"
        % (sum(1 for r in wf.values() if r["on"] and r["d_sh"] > 0),
           sum(1 for r in wf.values() if r["on"])),
    ])
    section(y, "CAVEATS", [
        "- A Sharpe-adder + single-day-blow softener, NOT an all-time-max-drawdown reducer.",
        "- Edge concentrates in vol spikes; marginal in calm years; slightly -ve in 2022 bear.",
        "- Costs use a flat 10bp; SOXS real spread / expense / 1-day -3x decay may be higher.",
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
    _t(ax, 0.04, 0.935, "Default: SOXS (long -3x) sized inverse-vol (hedge=50%% of book risk), "
       "trigger qqq_1d>=2%% & z(spy_vol_5d)>=1.  dSh = hedged-minus-book Sharpe; dDD = max-DD change (+=better).",
       fontsize=8, color="#666")
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
    # --- June-16 example case study (boxed, lower portion of page 3) ---
    cs = (
        "EXAMPLE CASE STUDY  -  2026-06-16\n"
        f"  Trigger @ 2026-06-15 close:  QQQ {CS['qqq_up']:+.1f}% up-shock,  "
        f"SPY 5d-vol z = {CS['volz']:+.2f} (elevated)   ->  RULE FIRES\n"
        f"  Next day 2026-06-16:  book {CS['book_nx']:+.2f}%  (leaders-led: top10 {CS['top10']:+.1f}%, "
        f"SMH {CS['smh']:+.1f}%, QQQ {CS['qqq']:+.1f}%, SPY {CS['spy']:+.1f}%; spread {CS['spread']:+.1f}%)\n"
        f"  Hedge result:  SOXS (inv-vol, {CS['w_soxs']:.0f}% of exposure = ~${CS['w_soxs']/100*BOOK/1000:.0f}k) "
        f"-> {CS['hed_soxs']:+.2f}% (${CS['hed_usd']:+,.0f} on $100k)   "
        f"->  the -3.8% book day softened to ~ {CS['softened']:+.1f}%"
    )
    ax.text(0.04, 0.30, cs, transform=ax.transAxes, va="top", ha="left",
            family="monospace", fontsize=9, parse_math=False,
            bbox=dict(boxstyle="round,pad=0.6", facecolor="#eef4fb",
                      edgecolor="#0b3d91", linewidth=1.2))
    pdf.savefig(fig); plt.close(fig)

    # --- appendix divider pages (one per merged correlation/gap PDF) ---
    for title, _path in APPENDICES:
        figd = plt.figure(figsize=(8.5, 11)); axd = figd.add_axes([0, 0, 1, 1]); axd.axis("off")
        axd.set_xlim(0, 1); axd.set_ylim(0, 1)
        axd.text(0.5, 0.6, title.split(" - ")[0].split(" — ")[0], ha="center", va="center",
                 fontsize=22, fontweight="bold", color="#0b3d91")
        axd.text(0.5, 0.52, title.split("—", 1)[-1].strip(), ha="center", va="center",
                 fontsize=12, color="#333", wrap=True)
        axd.text(0.5, 0.45, "(source: %s)" % _path.name, ha="center", va="center",
                 fontsize=8.5, color="#888", style="italic")
        pdf.savefig(figd); plt.close(figd)

# ── merge: recommendation core + (divider, appendix pages) for each corr PDF ──────
core = PdfReader(str(TMP))
writer = PdfWriter()
for p in core.pages[:3]:                       # cover, chart, tables+case-study
    writer.add_page(p)
for i, (_title, path) in enumerate(APPENDICES):
    writer.add_page(core.pages[3 + i])         # divider page
    if path.exists():
        for p in PdfReader(str(path)).pages:
            writer.add_page(p)
with open(OUT, "wb") as fh:
    writer.write(fh)
TMP.unlink(missing_ok=True)
print("wrote", OUT, "pages:", len(writer.pages))
