"""
make_model_v4_rebound.py — test all 3 trigger versions of a 1-day TQQQ REBOUND overlay on model_v4.

On a fire (decide close T, hold T+1 only), buy TQQQ at weight W of book notional; combined = book + sleeve.
  mirror : QQQ_1d<=-1.5%/-2% & rel-vol z>=0.75/1.0  (tiered half/full)   [symmetric opposite of the hedge]
  deep   : QQQ_1d<=-4%                                                    [deep capitulation]
  crash  : top10_1d<=-3% AND bottom10_1d>0                                [true momentum crash]
rel-vol = z(spy 5d vol,63d). 10 bp/turnover. Reported vs the model_v4 book over FULL + OOS train/test,
with fire counts + sleeve win-rate. Output: reports/model_v4_rebound.pdf
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
OUT = ROOT / "reports" / "model_v4_rebound.pdf"
TX, W = 0.0010, 0.45
WINDOWS = {"FULL 2016-2026": ("2016-06-20", "2026-06-18"),
           "TRAIN 2018-2022": ("2018-06-22", "2022-06-22"),
           "TEST 2022-2026": ("2022-06-22", "2026-06-18")}

mv = pd.read_csv(ROOT / "backtests" / "model_v4_timeseries.csv", parse_dates=["date"]).set_index("date")
book = mv["book_fwd_1d"]
qqq1d = mv["qqq_trl_1d"]
def z(s, lb=63): return (s - s.rolling(lb).mean().shift(1)) / s.rolling(lb).std().shift(1)
volz = z(mv["spy_vol_trl_5d"])
px = yf.download(["TQQQ"], start="2015-01-01", end="2026-06-19", auto_adjust=True, progress=False)["Close"]
tqqq_fwd = ((px if isinstance(px, pd.Series) else px.iloc[:, 0]).shift(-1) /
            (px if isinstance(px, pd.Series) else px.iloc[:, 0]) - 1.0).reindex(mv.index)

soft = (qqq1d <= -0.015) & (volz >= 0.75)
hard = (qqq1d <= -0.020) & (volz >= 1.00)
TRIGGERS = {
    "mirror": pd.Series(np.where(hard, 1.0, np.where(soft, 0.5, 0.0)), index=mv.index),
    "deep":   (qqq1d <= -0.04).astype(float),
    "crash":  ((mv["top10_trl_1d"] <= -0.03) & (mv["bottom10_trl_1d"] > 0)).astype(float),
    # combo: QQQ down  AND  momentum signal negative (spread<0)  AND  vol up (z>=0.75)
    "combo":  ((qqq1d <= -0.015) & (mv["spread_trl_1d"] < 0) & (volz >= 0.75)).astype(float),
}

def overlay(mult):
    posw = mult * W
    sleeve = posw * tqqq_fwd.fillna(0.0) - TX * posw.diff().abs().fillna(0.0)
    return book + sleeve

def metrics(r, rng):
    r = r.loc[rng[0]:rng[1]].dropna(); eq = (1 + r).cumprod(); n = len(r)
    tr = eq.iloc[-1] / eq.iloc[0] - 1
    return dict(tr=tr, sharpe=(r.mean() / r.std() * np.sqrt(252)) if r.std() > 0 else 0.0,
                dd=(eq / eq.cummax() - 1).min(), worst=r.min())

def pc(x): return f"{x*100:+.0f}%"
print(f"\nmodel_v4 + 1-day TQQQ rebound overlay — 3 triggers (W={W:.0%}, 10bp/turnover)\n")
base = {w: metrics(book, r) for w, r in WINDOWS.items()}
for w in WINDOWS:
    b = base[w]
    print(f"  {'no-overlay':<10} {w.split()[0]:<6}  TR {pc(b['tr']):>7}  Sharpe {b['sharpe']:+.2f}  "
          f"MaxDD {pc(b['dd']):>6}  worst1d {pc(b['worst'])}")
print()
for name, mult in TRIGGERS.items():
    s = overlay(mult)
    fr = mult > 0
    win = float((tqqq_fwd[fr] > 0).mean() * 100) if fr.any() else 0.0
    avg = float(tqqq_fwd[fr].mean() * 100) if fr.any() else 0.0
    print(f"  [{name}]  total fires {int(fr.sum())}  TQQQ-next-day win {win:.0f}%  avg/bet {avg:+.2f}%")
    for w, rng in WINDOWS.items():
        mm = metrics(s, rng); fw = int((mult.loc[rng[0]:rng[1]] > 0).sum())
        print(f"      {w.split()[0]:<6} fires {fw:<3} TR {pc(mm['tr']):>7}  Sharpe {mm['sharpe']:+.2f} "
              f"(d{mm['sharpe']-base[w]['sharpe']:+.2f})  MaxDD {pc(mm['dd']):>6}  worst1d {pc(mm['worst'])}")
    print()

full = WINDOWS["FULL 2016-2026"]
with PdfPages(OUT) as pdf:
    fig, (axc, axt) = plt.subplots(2, 1, figsize=(8.5, 11), gridspec_kw={"height_ratios": [3, 2]})
    axc.plot((1 + book.loc[full[0]:full[1]].dropna()).cumprod(), lw=1.4, color="k", label="no-overlay")
    for name, mult in TRIGGERS.items():
        eq = (1 + overlay(mult).loc[full[0]:full[1]].dropna()).cumprod()
        axc.plot(eq.index, eq.values, lw=1.6, label=name, alpha=0.85)
    axc.set_yscale("log"); axc.legend(fontsize=9); axc.grid(alpha=0.3)
    axc.set_title("model_v4 + 1-day TQQQ rebound overlay — 3 triggers, growth of $1 (log), 2016-2026",
                  fontsize=10.5, fontweight="bold", color="#0b3d91")
    axt.axis("off")
    rows = [["trigger", "win", "FULL Sh", "dSh", "TRAIN Sh", "dSh", "TEST Sh", "dSh", "FULL TR", "FULL DD", "fires"]]
    rows.append(["no-overlay", "", f"{base['FULL 2016-2026']['sharpe']:+.2f}", "",
                 f"{base['TRAIN 2018-2022']['sharpe']:+.2f}", "", f"{base['TEST 2022-2026']['sharpe']:+.2f}", "",
                 pc(base['FULL 2016-2026']['tr']), pc(base['FULL 2016-2026']['dd']), ""])
    for name, mult in TRIGGERS.items():
        s = overlay(mult); win = float((tqqq_fwd[mult > 0] > 0).mean() * 100)
        def sh(w): return metrics(s, WINDOWS[w])["sharpe"]
        rows.append([name, f"{win:.0f}%",
                     f"{sh('FULL 2016-2026'):+.2f}", f"{sh('FULL 2016-2026')-base['FULL 2016-2026']['sharpe']:+.2f}",
                     f"{sh('TRAIN 2018-2022'):+.2f}", f"{sh('TRAIN 2018-2022')-base['TRAIN 2018-2022']['sharpe']:+.2f}",
                     f"{sh('TEST 2022-2026'):+.2f}", f"{sh('TEST 2022-2026')-base['TEST 2022-2026']['sharpe']:+.2f}",
                     pc(metrics(s, full)["tr"]), pc(metrics(s, full)["dd"]), str(int((mult > 0).sum()))])
    t = axt.table(cellText=rows[1:], colLabels=rows[0], loc="center", bbox=[0.0, 0.2, 1.0, 0.7])
    t.auto_set_font_size(False); t.set_fontsize(7.2)
    for (ri, ci), c in t.get_celld().items():
        if ri == 0:
            c.set_facecolor("#0b3d91"); c.set_text_props(color="white", fontweight="bold")
    axt.set_title("Sharpe vs no-overlay (dSh = overlay − book). 1-day TQQQ hold, W=45%.", fontsize=9, color="#444")
    pdf.savefig(fig); plt.close(fig)
print("wrote", OUT)
