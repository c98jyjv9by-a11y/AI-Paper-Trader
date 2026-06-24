"""
make_model_v4_rebound_sweep.py — tune the COMBO rebound trigger (QQQ down & momentum signal negative
& vol up) for the 1-day TQQQ overlay on model_v4.

Sweeps the 3 gates:  QQQ_1d <= q  AND  spread_trl_1d < s  AND  z(spy 5d vol,63d) >= v.
Ranks by ROBUSTNESS: ΔSharpe vs the book must be > 0 in ALL of FULL / TRAIN / TEST, tail not worse
than the book (worst-1d), with an adequate fire count. Then size-sweeps the winner.
Output: reports/model_v4_rebound_sweep.pdf
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import yfinance as yf

ROOT = Path(__file__).parent
OUT = ROOT / "reports" / "model_v4_rebound_sweep.pdf"
TX, W0 = 0.0010, 0.45
WIN = {"FULL": ("2016-06-20", "2026-06-18"), "TRAIN": ("2018-06-22", "2022-06-22"),
       "TEST": ("2022-06-22", "2026-06-18")}
QS = [-0.010, -0.015, -0.020, -0.025]
VS = [0.0, 0.5, 0.75, 1.0]
SS = [0.0, -0.01, -0.02]

mv = pd.read_csv(ROOT / "backtests" / "model_v4_timeseries.csv", parse_dates=["date"]).set_index("date")
book, qqq1d, spread = mv["book_fwd_1d"], mv["qqq_trl_1d"], mv["spread_trl_1d"]
def z(s, lb=63): return (s - s.rolling(lb).mean().shift(1)) / s.rolling(lb).std().shift(1)
volz = z(mv["spy_vol_trl_5d"])
px = yf.download(["TQQQ"], start="2015-01-01", end="2026-06-19", auto_adjust=True, progress=False)["Close"]
px = px if isinstance(px, pd.Series) else px.iloc[:, 0]
tqqq_fwd = (px.shift(-1) / px - 1.0).reindex(mv.index)

def met(r, w):
    r = r.loc[WIN[w][0]:WIN[w][1]].dropna(); eq = (1 + r).cumprod()
    tr = eq.iloc[-1] / eq.iloc[0] - 1
    return ((r.mean() / r.std() * np.sqrt(252)) if r.std() > 0 else 0.0,
            (eq / eq.cummax() - 1).min(), r.min(), tr)
BASE = {w: met(book, w) for w in WIN}

def overlay(mask, W=W0):
    posw = mask.astype(float) * W
    return book + posw * tqqq_fwd.fillna(0.0) - TX * posw.diff().abs().fillna(0.0)

rows = []
for q in QS:
    for v in VS:
        for s in SS:
            mask = (qqq1d <= q) & (spread < s) & (volz >= v)
            r = overlay(mask)
            d = {w: met(r, w)[0] - BASE[w][0] for w in WIN}
            full = met(r, "FULL")
            rows.append(dict(q=q, v=v, s=s, fires=int(mask.sum()),
                             win=float((tqqq_fwd[mask] > 0).mean() * 100) if mask.any() else 0,
                             dF=d["FULL"], dTr=d["TRAIN"], dTe=d["TEST"],
                             minD=min(d.values()), dd=full[1], worst=full[2], tr=full[3]))
df = pd.DataFrame(rows)
def pc(x): return f"{x*100:+.0f}%"
print(f"\nCombo rebound gate sweep (W={W0:.0%}). Baseline Sharpe "
      f"FULL {BASE['FULL'][0]:+.2f} / TRAIN {BASE['TRAIN'][0]:+.2f} / TEST {BASE['TEST'][0]:+.2f}, "
      f"MaxDD {pc(BASE['FULL'][1])}, worst1d {pc(BASE['FULL'][2])}\n")
robust = df[(df.dF > 0) & (df.dTr > 0) & (df.dTe > 0) & (df.worst >= BASE["FULL"][2] - 0.005) & (df.fires >= 15)]
robust = robust.sort_values("minD", ascending=False)
print(f"ROBUST configs (ΔSharpe>0 in ALL windows, tail<=book, fires>=15):  {len(robust)} of {len(df)}\n")
print("   q      s      v   fires win%  dSh_FULL dSh_TRAIN dSh_TEST   MaxDD  worst1d")
for _, r in robust.head(14).iterrows():
    print("  %+.1f%%  %+.0f%%  %.2f   %3d  %3.0f   %+0.2f     %+0.2f     %+0.2f    %5s  %5s" % (
        r.q*100, r.s*100, r.v, r.fires, r.win, r.dF, r.dTr, r.dTe, pc(r.dd), pc(r.worst)))
if robust.empty:
    print("  (none fully robust — showing best by min-window ΔSharpe)")
    for _, r in df.sort_values("minD", ascending=False).head(8).iterrows():
        print("  %+.1f%%  %+.0f%%  %.2f   %3d  %3.0f   %+0.2f  %+0.2f  %+0.2f   %5s %5s" % (
            r.q*100, r.s*100, r.v, r.fires, r.win, r.dF, r.dTr, r.dTe, pc(r.dd), pc(r.worst)))

best = (robust if not robust.empty else df.sort_values("minD", ascending=False)).iloc[0]
print(f"\nBEST gate: QQQ<={best.q:+.1%}  spread<{best.s:+.0%}  vol-z>={best.v:.2f}  "
      f"({int(best.fires)} fires, {best.win:.0f}% win)")
print("\nSIZE sweep at the best gate (W):")
bm = (qqq1d <= best.q) & (spread < best.s) & (volz >= best.v)
for W in [0.20, 0.35, 0.45, 0.60, 0.80]:
    r = overlay(bm, W)
    print("  W=%.0f%%:  dSh FULL %+.2f / TRAIN %+.2f / TEST %+.2f   MaxDD %s  worst1d %s  TR %s" % (
        W*100, met(r, "FULL")[0]-BASE["FULL"][0], met(r, "TRAIN")[0]-BASE["TRAIN"][0],
        met(r, "TEST")[0]-BASE["TEST"][0], pc(met(r, "FULL")[1]), pc(met(r, "FULL")[2]), pc(met(r, "FULL")[3])))

with PdfPages(OUT) as pdf:
    fig, axes = plt.subplots(1, 3, figsize=(11, 5.2))
    for ax, s in zip(axes, SS):
        g = df[df.s == s].pivot(index="q", columns="v", values="dF")
        im = ax.imshow(g.values, cmap="RdBu_r", vmin=-0.1, vmax=0.1, aspect="auto")
        ax.set_xticks(range(len(VS))); ax.set_xticklabels([f"{v:.2f}" for v in VS], fontsize=8)
        ax.set_yticks(range(len(QS))); ax.set_yticklabels([f"{q:+.1%}" for q in QS], fontsize=8)
        ax.set_xlabel("vol-z gate"); ax.set_ylabel("QQQ gate" if s == SS[0] else "")
        ax.set_title(f"spread < {s:+.0%}", fontsize=10)
        for i in range(len(QS)):
            for j in range(len(VS)):
                ax.text(j, i, f"{g.values[i,j]:+.2f}", ha="center", va="center", fontsize=7,
                        color="white" if abs(g.values[i, j]) > 0.06 else "#222")
    fig.suptitle("Combo rebound tuning — FULL-window ΔSharpe vs book (red=better)", fontsize=12,
                 fontweight="bold", color="#0b3d91")
    fig.colorbar(im, ax=axes, fraction=0.015, pad=0.02, label="ΔSharpe")
    pdf.savefig(fig); plt.close(fig)
print("\nwrote", OUT)
