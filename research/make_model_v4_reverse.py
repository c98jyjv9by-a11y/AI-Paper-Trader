"""
make_model_v4_reverse.py — does the hedge overlay RUN IN REVERSE add value to model_v4, and does the
HOLD LENGTH matter?

Hedge in reverse: fire on a QQQ DOWN-shock in elevated vol and buy TQQQ (+3x) for the rebound.
Gates mirror the hedge:  SOFT qqq_1d<=-1.5% & z(spy 5d vol,63d)>=0.75 -> half;  HARD <=-2% & z>=1.0 -> full.
The sleeve is held N days after the fire (sweep N = 1,3,5,10,20) — the original test was N=1, but the
corr_tails report found the vol->forward-TQQQ signal peaks at the 20d horizon, so longer holds are tested.
Weight W of book notional (tiered half/full); 10 bp/turnover. Daily-return convention:
book_trl_1d + sleeve. Reported vs the model_v4 book over FULL + OOS train/test. Output: reports/model_v4_reverse.pdf
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import yfinance as yf

ROOT = Path(__file__).parent.parent
OUT = ROOT / "reports" / "model_v4_reverse.pdf"
TX, W = 0.0010, 0.45
HOLDS = [1, 3, 5, 10, 20]
WINDOWS = {"FULL 2016-2026": ("2016-06-20", "2026-06-18"),
           "TRAIN 2018-2022": ("2018-06-22", "2022-06-22"),
           "TEST 2022-2026": ("2022-06-22", "2026-06-18")}

mv = pd.read_csv(ROOT / "backtests" / "model_v4_timeseries.csv", parse_dates=["date"]).set_index("date")
book = mv["book_trl_1d"]                                   # realized daily book return
qqq1d = mv["qqq_trl_1d"]
def z(s, lb=63): return (s - s.rolling(lb).mean().shift(1)) / s.rolling(lb).std().shift(1)
vol_z = z(mv["spy_vol_trl_5d"])
soft = (qqq1d <= -0.015) & (vol_z >= 0.75)
hard = (qqq1d <= -0.020) & (vol_z >= 1.00)
m = pd.Series(np.where(hard, 1.0, np.where(soft, 0.5, 0.0)), index=mv.index)   # tier at the fire

px = yf.download(["TQQQ"], start="2015-01-01", end="2026-06-19", auto_adjust=True, progress=False)["Close"]
tqqq_dret = px["TQQQ"].pct_change().reindex(mv.index) if isinstance(px, pd.Series) \
    else px.iloc[:, 0].pct_change().reindex(mv.index)

def overlay(N):
    # sleeve ON for N days after each fire; weight = max active tier x W (no leverage stacking)
    mult_active = m.shift(1).rolling(N, min_periods=1).max().fillna(0.0)
    pos = mult_active * W
    sleeve = pos * tqqq_dret.fillna(0.0) - TX * pos.diff().abs().fillna(0.0)
    return book + sleeve

def metrics(r, rng):
    r = r.loc[rng[0]:rng[1]].dropna(); eq = (1 + r).cumprod(); n = len(r)
    tr = eq.iloc[-1] / eq.iloc[0] - 1
    return dict(tr=tr, sharpe=(r.mean() / r.std() * np.sqrt(252)) if r.std() > 0 else 0.0,
                dd=(eq / eq.cummax() - 1).min(), worst=r.min())

def pc(x): return f"{x*100:+.0f}%"
print(f"\nReverse hedge on model_v4 — TQQQ HOLD-LENGTH sweep (down-shock buy, W={W:.0%}, 10bp/turnover)\n")
base = {w: metrics(book, r) for w, r in WINDOWS.items()}
print(f"  {'no-overlay':<12} | " + " | ".join(
    f"{w.split()[0]}: TR {pc(base[w]['tr'])} Sh {base[w]['sharpe']:+.2f} DD {pc(base[w]['dd'])}" for w in WINDOWS))
print()
SER = {f"hold {N}d": overlay(N) for N in HOLDS}
for k, s in SER.items():
    line = f"  {k:<12} | "
    for w, rng in WINDOWS.items():
        mm = metrics(s, rng)
        line += (f"{w.split()[0]}: TR {pc(mm['tr'])} Sh {mm['sharpe']:+.2f} "
                 f"(d{mm['sharpe']-base[w]['sharpe']:+.2f}) DD {pc(mm['dd'])} w1d {pc(mm['worst'])} | ")
    print(line)
print()

full = WINDOWS["FULL 2016-2026"]
with PdfPages(OUT) as pdf:
    fig, (axc, axt) = plt.subplots(2, 1, figsize=(8.5, 11), gridspec_kw={"height_ratios": [3, 2]})
    axc.plot((1 + book.loc[full[0]:full[1]].dropna()).cumprod(), lw=1.4, color="k", label="no-overlay")
    for N in HOLDS:
        eq = (1 + overlay(N).loc[full[0]:full[1]].dropna()).cumprod()
        axc.plot(eq.index, eq.values, lw=1.5, label=f"hold {N}d", alpha=0.85)
    axc.set_yscale("log"); axc.legend(fontsize=8.5, ncol=2); axc.grid(alpha=0.3)
    axc.set_title("model_v4 + reverse hedge by TQQQ hold length — growth of $1 (log), 2016-2026",
                  fontsize=11, fontweight="bold", color="#0b3d91")
    axt.axis("off")
    rows = [["hold", "win", "TR", "Sharpe", "dSharpe", "MaxDD", "worst1d"]]
    rows += [["no-overlay", w.split()[0], pc(base[w]["tr"]), f"{base[w]['sharpe']:+.2f}", "",
              pc(base[w]["dd"]), pc(base[w]["worst"])] for w in WINDOWS]
    for N in HOLDS:
        s = overlay(N)
        for w, rng in WINDOWS.items():
            mm = metrics(s, rng)
            rows.append([f"{N}d", w.split()[0], pc(mm["tr"]), f"{mm['sharpe']:+.2f}",
                         f"{mm['sharpe']-base[w]['sharpe']:+.2f}", pc(mm["dd"]), pc(mm["worst"])])
    t = axt.table(cellText=rows[1:], colLabels=rows[0], loc="center", bbox=[0.04, 0.0, 0.92, 0.98])
    t.auto_set_font_size(False); t.set_fontsize(6.6)
    for (ri, ci), c in t.get_celld().items():
        if ri == 0:
            c.set_facecolor("#0b3d91"); c.set_text_props(color="white", fontweight="bold")
        elif (ri - 1) % 3 == 0 and ri <= 18:
            c.set_facecolor("#eef2f9")
    pdf.savefig(fig); plt.close(fig)
print("wrote", OUT)
