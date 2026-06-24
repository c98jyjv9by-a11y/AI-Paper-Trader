"""
make_levetf_shock.py — 1-day vol-gated SHOCK-REVERSAL on the leveraged QQQ ETFs, with an optional
TREND FILTER.

Base rule (decide at close T, hold T+1 only, then cash):
  • QQQ −1d < −2% AND rel-vol >= 0.75  ->  buy TQQQ  (bet the bounce)
  • QQQ +1d > +2% AND rel-vol >= 0.75  ->  buy SQQQ  (bet the fade)
rel-vol = z-score of QQQ 5d realized vol vs trailing 63d (hedge gate; mean/std lagged 1d, no look-ahead).

Trend filter (trend-aligned mean reversion): take the dip-buy ONLY in an uptrend (QQQ close >= its
N-day MA) and the rip-fade ONLY in a downtrend (close < MA) — i.e. don't fade strength in a bull or
buy weakness in a bear. Tested with N=50 and N=200, vs the unfiltered base and buy-and-hold.
10 bp per transaction. Output: reports/levetf_shock.pdf
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
OUT = ROOT / "reports" / "levetf_shock.pdf"
SHOCK, GATE, TX = 0.02, 0.75, 0.0010
WINDOWS = {"FULL 2016-2026": ("2016-06-20", "2026-06-18"),
           "TRAIN 2018-2022": ("2018-06-22", "2022-06-22"),
           "TEST 2022-2026": ("2022-06-22", "2026-06-18")}

px = yf.download(["TQQQ", "SQQQ", "QQQ"], start="2014-01-01", end="2026-06-19",
                 auto_adjust=True, progress=False)["Close"].dropna(how="all")
ret = px.pct_change()
qret = ret["QQQ"]
vol5 = qret.rolling(5).std()
rel_vol = (vol5 - vol5.rolling(63).mean().shift(1)) / vol5.rolling(63).std().shift(1)
down_shock = (qret <= -SHOCK) & (rel_vol >= GATE)
up_shock = (qret >= SHOCK) & (rel_vol >= GATE)

def build_sig(ma_n=None):
    dip, fade = down_shock.copy(), up_shock.copy()
    if ma_n:
        uptrend = px["QQQ"] >= px["QQQ"].rolling(ma_n).mean()    # known at close T
        dip = dip & uptrend                                       # buy dips only in an uptrend
        fade = fade & (~uptrend)                                  # fade rips only in a downtrend
    s = pd.Series("CASH", index=px.index)
    s[dip] = "TQQQ"; s[fade] = "SQQQ"; s[rel_vol.isna()] = "CASH"
    return s

def strat_ret(sig):
    pos = sig.shift(1)
    g = pd.Series(np.select([pos == "TQQQ", pos == "SQQQ"], [ret["TQQQ"], ret["SQQQ"]], default=0.0),
                  index=px.index)
    sw = (pos != pos.shift(1)) & pos.notna()
    return (g - sw.astype(float) * TX).fillna(0.0), pos

VARIANTS = {"base (no filter)": build_sig(None),
            "trend50": build_sig(50), "trend200": build_sig(200)}
R = {k: strat_ret(v) for k, v in VARIANTS.items()}
R["BH_TQQQ"] = (ret["TQQQ"].fillna(0.0), None)
R["BH_QQQ"] = (ret["QQQ"].fillna(0.0), None)

def metrics(r, rng):
    r = r.loc[rng[0]:rng[1]]; eq = (1 + r).cumprod(); n = len(r)
    tr = eq.iloc[-1] / eq.iloc[0] - 1
    return dict(tr=tr, cagr=(1 + tr) ** (252 / n) - 1,
                sharpe=(r.mean() / r.std() * np.sqrt(252)) if r.std() > 0 else 0.0,
                dd=(eq / eq.cummax() - 1).min())

def betstats(pos, rng):
    p = pos.loc[rng[0]:rng[1]]; out = {}
    for etf in ("TQQQ", "SQQQ"):
        rr = ret[etf].loc[rng[0]:rng[1]][p == etf]
        out[etf] = (int((p == etf).sum()), float((rr > 0).mean() * 100) if len(rr) else 0.0)
    return out

def pc(x): return f"{x*100:+.0f}%"
order = ["base (no filter)", "trend50", "trend200", "BH_TQQQ", "BH_QQQ"]
print(f"\n1-day vol-gated shock-reversal + trend filter  (|QQQ 1d|>{SHOCK:.0%} & rel-vol>={GATE}, hold 1d)\n")
for win, rng in WINDOWS.items():
    print(f"=== {win} ===")
    for k in order:
        m = metrics(R[k][0], rng)
        extra = ""
        if R[k][1] is not None:
            bs = betstats(R[k][1], rng)
            extra = f"   TQQQ {bs['TQQQ'][0]}/{bs['TQQQ'][1]:.0f}%w  SQQQ {bs['SQQQ'][0]}/{bs['SQQQ'][1]:.0f}%w"
        print(f"  {k:<16} TR {pc(m['tr']):>7}  CAGR {pc(m['cagr']):>6}  Sharpe {m['sharpe']:+.2f}  "
              f"MaxDD {pc(m['dd']):>6}{extra}")
    print()

full = WINDOWS["FULL 2016-2026"]
with PdfPages(OUT) as pdf:
    fig, (axc, axt) = plt.subplots(2, 1, figsize=(8.5, 11), gridspec_kw={"height_ratios": [3, 2]})
    styles = {"base (no filter)": "-", "trend50": "-", "trend200": "-", "BH_TQQQ": "--", "BH_QQQ": "--"}
    for k in order:
        eq = (1 + R[k][0].loc[full[0]:full[1]]).cumprod()
        axc.plot(eq.index, eq.values, styles[k], lw=1.9 if k == "trend50" else 1.1, label=k, alpha=0.85)
    axc.set_yscale("log"); axc.legend(fontsize=8.5, ncol=2); axc.grid(alpha=0.3)
    axc.set_title("LevEtf shock-reversal + trend filter vs buy-and-hold — growth of $1 (log), 2016-2026",
                  fontsize=11, fontweight="bold", color="#0b3d91")
    axt.axis("off")
    rows = [["variant", "FULL", "TRAIN 18-22", "TEST 22-26", "FULL Sharpe", "TEST Sharpe"]]
    for k in ["base (no filter)", "trend50", "trend200", "BH_TQQQ"]:
        rows.append([k, pc(metrics(R[k][0], WINDOWS["FULL 2016-2026"])["tr"]),
                     pc(metrics(R[k][0], WINDOWS["TRAIN 2018-2022"])["tr"]),
                     pc(metrics(R[k][0], WINDOWS["TEST 2022-2026"])["tr"]),
                     f"{metrics(R[k][0], WINDOWS['FULL 2016-2026'])['sharpe']:+.2f}",
                     f"{metrics(R[k][0], WINDOWS['TEST 2022-2026'])['sharpe']:+.2f}"])
    t = axt.table(cellText=rows[1:], colLabels=rows[0], loc="center", bbox=[0.02, 0.2, 0.96, 0.62])
    t.auto_set_font_size(False); t.set_fontsize(8.5)
    for (ri, ci), c in t.get_celld().items():
        if ri == 0:
            c.set_facecolor("#0b3d91"); c.set_text_props(color="white", fontweight="bold")
    axt.set_title("Trend filter: dip-buy only when QQQ ≥ MA(N); rip-fade only when QQQ < MA(N)",
                  fontsize=9.5, color="#444")
    pdf.savefig(fig); plt.close(fig)
print("wrote", OUT)
