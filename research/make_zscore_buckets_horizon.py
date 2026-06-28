"""Conditional forward return by z-score THRESHOLD bucket (no tails dropped). For each trailing avg-z
window {1,5,10}d, bucket every ticker-day by its z (<-2, -2..-1, -1..0, 0..1, 1..2, >2) and show the
MEAN forward return at {1,5,10}d, plus the count. Answers "names whose trailing-5d avg z is below -2
earn X% over the next 1/5/10 days." Reversal => low-z buckets earn more than high-z buckets.
Reuses the cached score panel + close. 2020+; survivorship-biased. -> reports/zscore_buckets_horizon.pdf"""
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
close, Z, ROOT = ctx.close, ctx.Z, ctx.ROOT

WIN, FWD = [1, 5, 10], [1, 5, 10]
EDGES = [-np.inf, -2, -1, 0, 1, 2, np.inf]
LABELS = ["z<-2", "-2..-1", "-1..0", "0..1", "1..2", "z>2"]
dates = Z.index[Z.index.year >= 2020]
fwd = {h: (close.shift(-h) / close - 1) for h in FWD}

tables = {}
for w in WIN:
    az = Z.rolling(w).mean().reindex(dates)
    df = pd.DataFrame({"z": az.values.ravel()})
    for h in FWD:
        df[f"fwd{h}d"] = fwd[h].reindex(dates).reindex(columns=az.columns).values.ravel()
    df = df.dropna(subset=["z"])
    df["bucket"] = pd.cut(df["z"], EDGES, labels=LABELS)
    g = df.groupby("bucket", observed=False)
    t = (g[[f"fwd{h}d" for h in FWD]].mean() * 100).round(2)   # mean fwd return in %
    t["N"] = g.size().astype(int)
    t.index = t.index.astype(str)                              # de-categorize to append a baseline row
    base = (df[[f"fwd{h}d" for h in FWD]].mean() * 100).round(2)   # universe avg (all valid ticker-days)
    t.loc["ALL universe"] = list(base.values) + [int(len(df))]
    tables[w] = t

# ---- console ----
for w in WIN:
    print(f"\n=== trailing {w}d avg-z  ->  mean forward return (%) by z-bucket  (2020+) ===")
    print(tables[w].to_string())

# ---- PDF: one heatmap per trailing window (z-bucket x fwd horizon, colored by mean fwd return) ----
OUT = ROOT / "reports" / "zscore_buckets_horizon.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)
allvals = np.concatenate([tables[w][[f"fwd{h}d" for h in FWD]].values.ravel() for w in WIN])
lim = float(np.nanmax(np.abs(allvals)))
with PdfPages(OUT) as pdf:
    fig, axes = plt.subplots(1, 3, figsize=(13, 5))
    fig.suptitle("Mean forward return (%) by z-score bucket × horizon   —   2020+, no tail filtering "
                 "(low-z buckets earning more = reversal)", fontsize=12, weight="bold")
    for ax, w in zip(axes, WIN):
        t = tables[w]
        data = t[[f"fwd{h}d" for h in FWD]].values.astype(float)
        im = ax.imshow(data, cmap="RdYlGn", vmin=-lim, vmax=lim, aspect="auto")
        ax.set_xticks(range(len(FWD))); ax.set_xticklabels([f"fwd {h}d" for h in FWD])
        rows = list(t.index)
        ax.set_yticks(range(len(rows)))
        ax.set_yticklabels([f"{lab} (n={int(t.loc[lab, 'N']):,})" for lab in rows], fontsize=8)
        ax.set_title(f"trailing {w}d avg-z", fontsize=11)
        for i in range(len(rows)):
            for j in range(len(FWD)):
                ax.text(j, i, "%+.2f" % data[i, j], ha="center", va="center", fontsize=9,
                        color="black")
    fig.colorbar(im, ax=axes, fraction=0.02, pad=0.02, label="mean fwd return %")
    pdf.savefig(fig); plt.close(fig)
print("\nwrote", OUT)
