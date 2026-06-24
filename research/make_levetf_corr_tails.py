"""
make_levetf_corr_tails.py — "corr_tails by horizon" predictiveness report for the leveraged
QQQ ETFs, analysed SEPARATELY for TQQQ and SQQQ.

Question: which TRAILING measures are predictive of FORWARD ETF moves?
  • Forward target ("book return") = the respective ETF's OWN price return (TQQQ / SQQQ), 1/5/20d.
  • Trailing predictors = the REAL model_v4 metrics from backtests/model_v4_timeseries.csv —
    the score panels (score_top10/bottom10/universe/held), the long/short spread, the top10/bottom10
    baskets, market/inverse returns (spy/qqq/smh/psq/soxs), and the spy/qqq realized-vol measures —
    PLUS the ETF's own trailing return (replacing model_v4's "book").

Per ETF: (1) a full-sample trailing→forward correlation heatmap (factors × fwd 1/5/20d), and
(2) tail call-outs — split days into big-UP vs big-DN tails of the forward ETF return, then rank the
trailing metrics by UP−DN gap and by in-tail correlation.  Output: reports/corr_tails_levetf.pdf
"""
import glob
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import yfinance as yf

ROOT = Path(__file__).parent.parent
OUT = ROOT / "reports" / "corr_tails_levetf.pdf"
HZ = [1, 5, 20]
TAIL_Q = 0.60
NAVY = "#0b3d91"

# ── real model_v4 trailing-metric panel ──────────────────────────────────────────
mv = pd.read_csv(ROOT / "backtests" / "model_v4_timeseries.csv", parse_dates=["date"]).set_index("date")
MV_TRL = [c for c in mv.columns if c.endswith(("_trl_1d", "_trl_5d", "_trl_20d")) and not c.startswith("book_")]

# ── ETF prices → own trailing + forward returns ──────────────────────────────────
px = yf.download(["TQQQ", "SQQQ"], start=mv.index.min() - pd.Timedelta(days=40),
                 end=mv.index.max() + pd.Timedelta(days=2), auto_adjust=True, progress=False)["Close"]
idx = mv.index.intersection(px.dropna(how="all").index)
X = mv.loc[idx, MV_TRL].copy()
for tk in ("TQQQ", "SQQQ"):
    for h in HZ:
        X[f"{tk.lower()}_trl_{h}d"] = px[tk].pct_change(h).reindex(idx)
        X[f"{tk.lower()}_fwd_{h}d"] = (px[tk].shift(-h) / px[tk] - 1.0).reindex(idx)

# factor ordering by family (own ETF first, then model_v4 metrics)
FAMILIES = ["{etf}", "spy", "qqq", "smh", "psq", "soxs", "top10", "bottom10", "universe",
            "spread", "score_top10", "score_bottom10", "score_universe", "score_held",
            "spy_vol", "qqq_vol"]

def factors_for(etf):
    own = etf.lower()
    out = []
    for fam in FAMILIES:
        base = own if fam == "{etf}" else fam
        for h in HZ:
            col = f"{base}_trl_{h}d"
            if col in X.columns:
                out.append(col)
    return out

def is_pct(col):
    return not col.startswith("score_") and "_vol_" not in col

def favg(col, v):
    if v is None or np.isnan(v):
        return "—"
    return f"{v*100:+.1f}%" if is_pct(col) else f"{v:+.3f}"

# ── per-ETF stats ────────────────────────────────────────────────────────────────
def full_corr(etf):
    facs = factors_for(etf)
    M = pd.DataFrame(index=facs, columns=[f"fwd_{h}d" for h in HZ], dtype=float)
    for f in facs:
        for h in HZ:
            d = pd.concat([X[f], X[f"{etf.lower()}_fwd_{h}d"]], axis=1).dropna()
            M.loc[f, f"fwd_{h}d"] = d.iloc[:, 0].corr(d.iloc[:, 1]) if len(d) > 50 else np.nan
    return M

def tail_table(etf, h):
    facs = factors_for(etf)
    fwd = X[f"{etf.lower()}_fwd_{h}d"]
    thr = fwd.abs().quantile(TAIL_Q)
    up, dn = fwd > thr, fwd < -thr
    rows = []
    for f in facs:
        s = X[f]
        def seg(m):
            d = pd.concat([s[m], fwd[m]], axis=1).dropna()
            return (d.iloc[:, 0].mean(), d.iloc[:, 0].corr(d.iloc[:, 1])) if len(d) >= 8 else (np.nan, np.nan)
        ua, ur = seg(up); da, dr = seg(dn)
        rows.append(dict(f=f, ua=ua, ur=ur, da=da, dr=dr, d=ua - da))
    return pd.DataFrame(rows), thr, int(up.sum()), int(dn.sum())

# ── render ───────────────────────────────────────────────────────────────────────
with PdfPages(OUT) as pdf:
    summary = {}
    for etf in ("TQQQ", "SQQQ"):
        M = full_corr(etf); summary[etf] = M
        # ---- page: correlation heatmap ----
        facs = M.index.tolist()
        fig, ax = plt.subplots(figsize=(8.5, 11))
        data = M.values.astype(float)
        im = ax.imshow(data, cmap="RdBu_r", vmin=-0.4, vmax=0.4, aspect="auto")
        ax.set_xticks(range(len(HZ))); ax.set_xticklabels([f"fwd {h}d" for h in HZ], fontsize=9)
        ax.set_yticks(range(len(facs))); ax.set_yticklabels(facs, fontsize=5.5, family="monospace")
        ax.xaxis.set_label_position("top"); ax.xaxis.tick_top()
        for i in range(len(facs)):
            for j in range(len(HZ)):
                v = data[i, j]
                if not np.isnan(v):
                    ax.text(j, i, f"{v:+.2f}", ha="center", va="center", fontsize=5,
                            color="white" if abs(v) > 0.22 else "#222")
        ax.set_title(f"{etf} — trailing model_v4 metric  →  forward {etf} return (full-sample corr, "
                     f"{len(idx)} days 2016–2026)", fontsize=11, fontweight="bold", color=NAVY, pad=26)
        fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02, label="Pearson r")
        fig.tight_layout(); pdf.savefig(fig); plt.close(fig)

        # ---- page: tail call-outs ----
        fig = plt.figure(figsize=(8.5, 11)); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
        ax.text(0.06, 0.965, f"{etf} — tail call-outs: which model_v4 trailing metrics separate the "
                f"forward-{etf} tails", fontsize=12.5, fontweight="bold", color=NAVY)
        ax.text(0.06, 0.94, f"UP = forward {etf} return > +thr, DN < −thr (thr = 60th pct of |fwd|). "
                "D = UP avg − DN avg of the trailing metric; r = its in-tail corr with the forward return.",
                fontsize=8, color="#555")
        y = 0.905
        for h in HZ:
            df, thr, nu, nd = tail_table(etf, h)
            df["abr"] = df["dr"].abs().fillna(0)
            ax.text(0.06, y, f"FWD {h}D   (thr ±{thr*100:.1f}%, UP n={nu} / DN n={nd}) — top metrics by "
                    "|in-tail corr|", fontsize=9.5, fontweight="bold", color="#6a3d9a"); y -= 0.021
            top = df.sort_values("abr", ascending=False).head(7)
            for _, r in top.iterrows():
                ax.text(0.08, y, f"{r['f']:<20} UP r={r['ur']:+.2f} DN r={r['dr']:+.2f}  "
                        f"D={favg(r['f'], r['d']):>8}  (UP {favg(r['f'], r['ua'])} / DN {favg(r['f'], r['da'])})",
                        fontsize=7.4, family="monospace", color="#222"); y -= 0.0145
            y -= 0.012
        ax.text(0.06, 0.05, "Paper-trading research only. In-tail panels are smaller → weight |r| by n. "
                "Reproduce: python make_levetf_corr_tails.py", fontsize=7, color="#999")
        pdf.savefig(fig); plt.close(fig)

    # ---- comparison page ----
    fig = plt.figure(figsize=(8.5, 11)); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.text(0.06, 0.965, "TQQQ vs SQQQ — strongest trailing→forward predictors (full-sample |r|)",
            fontsize=13, fontweight="bold", color=NAVY)
    y = 0.93
    for etf in ("TQQQ", "SQQQ"):
        M = summary[etf]
        flat = M.stack().rename("r").reset_index()
        flat["ar"] = flat["r"].abs()
        top = flat.sort_values("ar", ascending=False).head(12)
        ax.text(0.06, y, f"{etf}:", fontsize=11, fontweight="bold", color="#6a3d9a"); y -= 0.024
        for _, r in top.iterrows():
            ax.text(0.09, y, f"{r['level_0']:<20} {r['level_1']:<7}  r = {r['r']:+.2f}",
                    fontsize=8.2, family="monospace", color="#222"); y -= 0.016
        y -= 0.016
    pdf.savefig(fig); plt.close(fig)

print("wrote", OUT)
