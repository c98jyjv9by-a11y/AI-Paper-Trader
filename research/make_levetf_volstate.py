"""
make_levetf_volstate.py — backtest a VOL-STATE TILT variant on the leveraged QQQ ETFs.

Motivation (from make_levetf_corr_tails.py): the only trailing metric predictive of forward TQQQ/SQQQ
moves is the QQQ/SPY realized-vol regime (high trailing vol -> higher forward TQQQ, ~+0.22 at 20d;
mirror for SQQQ). This tests whether a daily vol-state switch monetizes that — both directions:
  buy-STRESS : long TQQQ when vol_z is HIGH (>=thr), else CASH / SQQQ   (per the +corr finding)
  risk-OFF   : long TQQQ when vol_z is LOW  (<thr),  else CASH / SQQQ   (conventional, the opposite)
Signal = z-score of QQQ 20d trailing realized vol vs its trailing 63d mean/std, lagged 1 day (no
look-ahead). Decide at close t, hold t+1; 10 bp per switch. Reported over FULL + OOS train/test, vs
buy-and-hold QQQ and TQQQ.  No files written except the summary PDF (reports/levetf_volstate.pdf).
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
OUT = ROOT / "reports" / "levetf_volstate.pdf"
TX = 0.0010                                  # 10 bp per switch
THR = 0.0                                    # vol_z threshold (high vs low regime)
WINDOWS = {"FULL 2016-2026": ("2016-06-20", "2026-06-18"),
           "TRAIN 2018-2022": ("2018-06-22", "2022-06-22"),
           "TEST 2022-2026": ("2022-06-22", "2026-06-18")}

px = yf.download(["TQQQ", "SQQQ", "QQQ"], start="2014-01-01", end="2026-06-19",
                 auto_adjust=True, progress=False)["Close"].dropna(how="all")
ret = px.pct_change()
# vol-state signal: z-score of QQQ 20d realized vol, lagged 1d (uses data <= t only)
vol = ret["QQQ"].rolling(20).std()
vol_z = ((vol - vol.rolling(63).mean()) / vol.rolling(63).std()).shift(1)

def holdings(rule):
    hi = vol_z >= THR
    if rule == "buyStress_cash":  h = np.where(hi, "TQQQ", "CASH")
    elif rule == "buyStress_ls":  h = np.where(hi, "TQQQ", "SQQQ")
    elif rule == "riskOff_cash":  h = np.where(hi, "CASH", "TQQQ")
    elif rule == "riskOff_ls":    h = np.where(hi, "SQQQ", "TQQQ")
    elif rule == "BH_TQQQ":       h = np.full(len(px), "TQQQ")
    elif rule == "BH_QQQ":        h = np.full(len(px), "QQQ")
    return pd.Series(h, index=px.index).where(vol_z.notna() | (rule.startswith("BH")), "CASH")

def strat_returns(rule):
    pos = holdings(rule).shift(1)             # held during day d = decided at close d-1
    g = np.select([pos == "TQQQ", pos == "SQQQ", pos == "QQQ"],
                  [ret["TQQQ"], ret["SQQQ"], ret["QQQ"]], default=0.0)
    g = pd.Series(g, index=px.index)
    switch = (pos != pos.shift(1)) & pos.notna()
    return (g - switch.astype(float) * TX).fillna(0.0), holdings(rule)

def metrics(r, win):
    s, e = pd.Timestamp(win[0]), pd.Timestamp(win[1])
    r = r.loc[s:e]
    if len(r) < 20:
        return None
    eq = (1 + r).cumprod()
    n = len(r)
    tr = eq.iloc[-1] / eq.iloc[0] - 1
    cagr = (1 + tr) ** (252 / n) - 1
    sharpe = r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else 0.0
    dd = (eq / eq.cummax() - 1).min()
    return dict(tr=tr, cagr=cagr, sharpe=sharpe, dd=dd)

RULES = ["buyStress_cash", "buyStress_ls", "riskOff_cash", "riskOff_ls", "BH_TQQQ", "BH_QQQ"]
RET = {ru: strat_returns(ru) for ru in RULES}

def pc(x): return f"{x*100:+.0f}%"
print(f"\nVol-state tilt (vol_z>= {THR} = HIGH regime, 10bp/switch).  TR / CAGR / Sharpe / MaxDD\n")
for win, rng in WINDOWS.items():
    print(f"=== {win} ===")
    for ru in RULES:
        m = metrics(RET[ru][0], rng)
        if m:
            sw = (RET[ru][1].loc[rng[0]:rng[1]] != RET[ru][1].loc[rng[0]:rng[1]].shift(1)).sum()
            yrs = max(1e-9, (pd.Timestamp(rng[1]) - pd.Timestamp(rng[0])).days / 365)
            print(f"  {ru:<16} TR {pc(m['tr']):>7}  CAGR {pc(m['cagr']):>6}  "
                  f"Sharpe {m['sharpe']:+.2f}  MaxDD {pc(m['dd']):>6}  switches/yr {sw/yrs:4.0f}")
    print()

# ── PDF: equity curves (log) + metrics table over FULL ──
full = WINDOWS["FULL 2016-2026"]
with PdfPages(OUT) as pdf:
    fig, (axc, axt) = plt.subplots(2, 1, figsize=(8.5, 11), gridspec_kw={"height_ratios": [3, 2]})
    for ru in RULES:
        r = RET[ru][0].loc[full[0]:full[1]]
        eq = (1 + r).cumprod()
        axc.plot(eq.index, eq.values, lw=1.6 if ru.startswith("buy") else 1.1,
                 label=ru, alpha=0.9 if not ru.startswith("BH") else 0.6,
                 ls="--" if ru.startswith("BH") else "-")
    axc.set_yscale("log"); axc.legend(fontsize=8, ncol=2); axc.grid(alpha=0.3)
    axc.set_title("LevEtf vol-state tilt vs buy-and-hold — growth of $1 (log), 2016-2026",
                  fontsize=12, fontweight="bold", color="#0b3d91")
    axt.axis("off")
    cells = [["rule", "TR", "CAGR", "Sharpe", "MaxDD"]]
    for ru in RULES:
        m = metrics(RET[ru][0], full)
        cells.append([ru, pc(m["tr"]), pc(m["cagr"]), f"{m['sharpe']:+.2f}", pc(m["dd"])])
    t = axt.table(cellText=cells[1:], colLabels=cells[0], loc="center", bbox=[0.05, 0.1, 0.9, 0.8])
    t.auto_set_font_size(False); t.set_fontsize(9)
    for (ri, ci), c in t.get_celld().items():
        if ri == 0:
            c.set_facecolor("#0b3d91"); c.set_text_props(color="white", fontweight="bold")
    axt.set_title("Full-window metrics  (signal = QQQ 20d realized-vol z-score, lagged)",
                  fontsize=10, color="#444")
    pdf.savefig(fig); plt.close(fig)
print("wrote", OUT)
