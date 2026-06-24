"""
make_model_v4_defense.py — compare two same-day SELL-OFF defenses as overlays on the model_v4 book,
vs no overlay. The up-shock hedge only fires on up-days; this asks what (if anything) defends a
straight sell-off the slow 126d vol governor misses.

  NO-OVERLAY : the model_v4 book as-is (book_fwd_1d daily P&L from model_v4_timeseries.csv).
  A  FAST DE-RISK (to cash): scale the book by a FAST Barroso governor on its own 10d realized vol —
       mult = clip(0.35 / vol10_ann, 0.25, 1.0), decided at close T, applied to the T+1 book return.
       (cash is the hedge; no inverse instrument.)
  B  STRUCTURAL SQQQ TRANCHE: 1-day SQQQ sleeve (weight W) fired ONLY on a sell-off in a confirmed
       downtrend — QQQ −1d <= −2% AND QQQ < 200d MA AND z(spy 5d vol,63d) >= 0.75.

book P&L = book_fwd_1d (signal at T, realized next session). 10 bp per unit turnover. Reported over
FULL + OOS train/test with the DEFENSE metrics: Sharpe, MaxDD, worst 1-day. Output: reports/model_v4_defense.pdf
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
OUT = ROOT / "reports" / "model_v4_defense.pdf"
TX, W = 0.0010, 0.25
WINDOWS = {"FULL 2016-2026": ("2016-06-20", "2026-06-18"),
           "TRAIN 2018-2022": ("2018-06-22", "2022-06-22"),
           "TEST 2022-2026": ("2022-06-22", "2026-06-18")}

mv = pd.read_csv(ROOT / "backtests" / "model_v4_timeseries.csv", parse_dates=["date"]).set_index("date")
book = mv["book_fwd_1d"]                                   # next-session book P&L, dated at T
qqq1d = mv["qqq_trl_1d"]
def z(s, lb=63): return (s - s.rolling(lb).mean().shift(1)) / s.rolling(lb).std().shift(1)
vol_z = z(mv["spy_vol_trl_5d"])

# external series aligned to the panel: QQQ 200d MA + SQQQ forward 1d
px = yf.download(["QQQ", "SQQQ"], start="2015-01-01", end="2026-06-19",
                 auto_adjust=True, progress=False)["Close"]
below200 = (px["QQQ"] < px["QQQ"].rolling(200).mean()).reindex(mv.index)
sqqq_fwd = (px["SQQQ"].shift(-1) / px["SQQQ"] - 1.0).reindex(mv.index)   # T+1 SQQQ return, dated at T

# A — fast de-risk governor (decided at T from realized 10d book vol, applied to book_fwd_T)
vol10_ann = mv["book_trl_1d"].rolling(10).std() * np.sqrt(252)
mult = (0.35 / vol10_ann).clip(0.25, 1.0)
A = book * mult - TX * mult.diff().abs().fillna(0)

# B — structural down-shock SQQQ tranche
fire = (qqq1d <= -0.02) & below200.fillna(False) & (vol_z >= 0.75)
w = pd.Series(np.where(fire, W, 0.0), index=mv.index)
B = book + w * sqqq_fwd.fillna(0.0) - TX * w.diff().abs().fillna(0)

SERIES = {"no-overlay": book, "A fast-derisk": A, "B SQQQ-tranche": B}

def metrics(r, rng):
    r = r.loc[rng[0]:rng[1]].dropna(); eq = (1 + r).cumprod(); n = len(r)
    tr = eq.iloc[-1] / eq.iloc[0] - 1
    return dict(tr=tr, cagr=(1 + tr) ** (252 / n) - 1,
                sharpe=(r.mean() / r.std() * np.sqrt(252)) if r.std() > 0 else 0.0,
                dd=(eq / eq.cummax() - 1).min(), worst=r.min())

def pc(x): return f"{x*100:+.0f}%"
print(f"\nmodel_v4 sell-off defenses  (W={W:.0%} SQQQ tranche, {TX*1e4:.0f}bp/turnover)\n")
for win, rng in WINDOWS.items():
    print(f"=== {win} ===")
    base = metrics(book, rng)
    for k, s in SERIES.items():
        m = metrics(s, rng)
        d = f"   dSharpe {m['sharpe']-base['sharpe']:+.2f}  dMaxDD {pc(m['dd']-base['dd'])}" if k != "no-overlay" else ""
        print(f"  {k:<15} TR {pc(m['tr']):>7}  Sharpe {m['sharpe']:+.2f}  MaxDD {pc(m['dd']):>6}  "
              f"worst1d {pc(m['worst']):>5}{d}")
    print()
fires_full = int(fire.loc[WINDOWS['FULL 2016-2026'][0]:WINDOWS['FULL 2016-2026'][1]].sum())
won = float((sqqq_fwd[fire] > 0).mean() * 100) if fire.any() else 0.0
print(f"B fires: {fires_full} over 2016-2026 ({won:.0f}% had SQQQ up next day);  "
      f"A de-risked (<1.0 mult) {100*(mult<0.999).mean():.0f}% of days, avg mult {mult.mean():.2f}\n")

full = WINDOWS["FULL 2016-2026"]
with PdfPages(OUT) as pdf:
    fig, (axc, axt) = plt.subplots(2, 1, figsize=(8.5, 11), gridspec_kw={"height_ratios": [3, 2]})
    for k, s in SERIES.items():
        eq = (1 + s.loc[full[0]:full[1]].dropna()).cumprod()
        axc.plot(eq.index, eq.values, lw=2 if k != "no-overlay" else 1.3, label=k, alpha=0.9)
    axc.set_yscale("log"); axc.legend(fontsize=9); axc.grid(alpha=0.3)
    axc.set_title("model_v4 sell-off defenses — growth of $1 (log), 2016-2026", fontsize=12,
                  fontweight="bold", color="#0b3d91")
    axt.axis("off")
    rows = [["overlay", "win", "TR", "Sharpe", "MaxDD", "worst1d", "dSharpe", "dMaxDD"]]
    for win, rng in WINDOWS.items():
        base = metrics(book, rng)
        for k, s in SERIES.items():
            m = metrics(s, rng)
            rows.append([k, win.split()[0], pc(m["tr"]), f"{m['sharpe']:+.2f}", pc(m["dd"]), pc(m["worst"]),
                         "" if k == "no-overlay" else f"{m['sharpe']-base['sharpe']:+.2f}",
                         "" if k == "no-overlay" else pc(m["dd"]-base["dd"])])
    t = axt.table(cellText=rows[1:], colLabels=rows[0], loc="center", bbox=[0.02, 0.05, 0.96, 0.9])
    t.auto_set_font_size(False); t.set_fontsize(7.8)
    for (ri, ci), c in t.get_celld().items():
        if ri == 0:
            c.set_facecolor("#0b3d91"); c.set_text_props(color="white", fontweight="bold")
        elif (ri - 1) % 3 == 0:
            c.set_facecolor("#eef2f9")
    pdf.savefig(fig); plt.close(fig)
print("wrote", OUT)
