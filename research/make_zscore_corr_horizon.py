"""corr_tails-by-horizon, z-score version, NO tail filtering. Pooled Pearson correlation between the
trailing {1,5,10}-day average of the per-ticker 60-day z-score of the model_v4 composite and the forward
{1,5,10}-day return, across all ticker-days. A plain 3x3 heatmap (no return-tail conditioning).
Negative = reversal (low z -> high forward return). Reuses the cached score panel + close.
2020+; survivorship-biased. -> reports/corr_tails_zscore.pdf"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))    # so `import _common` resolves
from _common import load_ctx
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

ctx = load_ctx()                                            # close panel + cached score panel (model_v4)
close, Z, ROOT = ctx.close, ctx.Z, ctx.ROOT                 # Z = per-ticker 60-day z of the composite

WIN, FWD = [1, 5, 10], [1, 5, 10]
dates = Z.index[Z.index.year >= 2020]
fwd = {h: (close.shift(-h) / close - 1) for h in FWD}        # forward h-day return per ticker
M = pd.DataFrame(index=[f"{w}d avg-z" for w in WIN], columns=[f"fwd {h}d" for h in FWD], dtype=float)
for w in WIN:
    az = Z.rolling(w).mean().reindex(dates)
    for h in FWD:
        f = fwd[h].reindex(dates).reindex(columns=az.columns)
        x, y = az.values.ravel(), f.values.ravel()
        m = np.isfinite(x) & np.isfinite(y)
        M.loc[f"{w}d avg-z", f"fwd {h}d"] = float(np.corrcoef(x[m], y[m])[0, 1])

OUT = ROOT / "reports" / "corr_tails_zscore.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)
data = M.values.astype(float)
lim = float(np.nanmax(np.abs(data))) or 0.05
with PdfPages(OUT) as pdf:
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    im = ax.imshow(data, cmap="RdBu_r", vmin=-lim, vmax=lim, aspect="auto")
    ax.set_xticks(range(len(FWD))); ax.set_xticklabels(M.columns, fontsize=11)
    ax.set_yticks(range(len(WIN))); ax.set_yticklabels(M.index, fontsize=11)
    ax.set_xlabel("forward return horizon"); ax.set_ylabel("trailing avg-z window")
    for i in range(len(WIN)):
        for j in range(len(FWD)):
            ax.text(j, i, "%+.4f" % data[i, j], ha="center", va="center", fontsize=12,
                    color="white" if abs(data[i, j]) > 0.6 * lim else "black")
    ax.set_title("Trailing avg z-score  →  forward return\npooled Pearson r, all ticker-days, 2020+ "
                 "(negative = reversal)", fontsize=12)
    fig.colorbar(im, ax=ax, fraction=0.045, pad=0.03, label="Pearson r")
    fig.text(0.5, 0.015, "z = per-ticker 60-day z of the model_v4 composite score; NO return-tail filtering. "
             "Reproduce: python research/make_zscore_corr_horizon.py", ha="center", fontsize=7, color="#999")
    fig.tight_layout(rect=[0, 0.03, 1, 1]); pdf.savefig(fig); plt.close(fig)

print("wrote", OUT)
print("\npooled Pearson r  (trailing avg-z  vs  forward return):")
print(M.round(4).to_string())
