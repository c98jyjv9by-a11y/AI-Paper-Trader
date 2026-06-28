"""Conditional forward return by CROSS-SECTIONAL z-RANK group (not absolute z-buckets). Each day, rank
the universe by its trailing avg-z and form 5 groups: BOTTOM 10 (lowest z = most-fallen, what the book
buys), 3 middle thirds, TOP 10 (highest z = most-extended). For each group show the MEAN forward return
at {1,5,10}d AND the group's typical z-range (10th..90th pct + avg over 2020+, to convey relative z
magnitude). Done for trailing {1,5,10}d avg-z. This is the view the strategy trades on (it holds the
cross-sectional bottom-N). Reuses the cached score panel + close. -> reports/zscore_rankgroups_horizon.pdf"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))    # so `import _common` resolves
from _common import load_ctx
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_pdf import PdfPages

ctx = load_ctx()                                            # close panel + cached score panel (model_v4)
close, Z, ROOT = ctx.close, ctx.Z, ctx.ROOT

WIN, FWD = [1, 5, 10], [1, 5, 10]
GROUPS = ["bottom 10", "mid-low", "mid", "mid-high", "top 10"]
dates = [d for d in Z.index if d.year >= 2020]
fwd = {h: (close.shift(-h) / close - 1) for h in FWD}


def grouped(w):
    rec = {g: {"z": [], 1: [], 5: [], 10: []} for g in GROUPS}
    az = Z.rolling(w).mean()
    for t in dates:
        if t not in az.index:
            continue
        row = az.loc[t].dropna().sort_values()             # ascending: most-fallen first
        n = len(row)
        if n < 40:
            continue
        names = row.index
        pos = np.arange(n)
        g = np.full(n, "mid", dtype=object)
        g[pos < 10] = "bottom 10"
        g[pos >= n - 10] = "top 10"
        mid = (pos >= 10) & (pos < n - 10)
        third = np.minimum(2, ((pos[mid] - 10) * 3) // (n - 20))
        g[mid] = np.array(["mid-low", "mid", "mid-high"])[third]
        zv = row.values
        fr = {h: fwd[h].loc[t].reindex(names).values for h in FWD}
        for grp in GROUPS:
            m = g == grp
            rec[grp]["z"].extend(zv[m])
            for h in FWD:
                rec[grp][h].extend(fr[h][m])
    out = []
    for grp in GROUPS:
        z = np.array(rec[grp]["z"], float)
        r = {"group": grp,
             "z range (p10..p90, avg)": "%+.1f .. %+.1f  (%+.1f)" % (np.nanpercentile(z, 10), np.nanpercentile(z, 90), np.nanmean(z))}
        for h in FWD:
            r[f"fwd{h}d"] = round(float(np.nanmean(np.array(rec[grp][h], float))) * 100, 2)
        r["N"] = int(np.isfinite(z).sum())
        out.append(r)
    # ALL-universe baseline row (every ranked name, all groups combined)
    z_all = np.concatenate([np.array(rec[g]["z"], float) for g in GROUPS])
    ra = {"group": "ALL universe",
          "z range (p10..p90, avg)": "%+.1f .. %+.1f  (%+.1f)" % (
              np.nanpercentile(z_all, 10), np.nanpercentile(z_all, 90), np.nanmean(z_all))}
    for h in FWD:
        ra[f"fwd{h}d"] = round(float(np.nanmean(np.concatenate(
            [np.array(rec[g][h], float) for g in GROUPS]))) * 100, 2)
    ra["N"] = int(np.isfinite(z_all).sum())
    out.append(ra)
    return pd.DataFrame(out).set_index("group")


tables = {w: grouped(w) for w in WIN}
for w in WIN:
    print(f"\n=== trailing {w}d avg-z  ->  mean fwd return (%) by z-RANK group  (daily; 2020+) ===")
    print(tables[w].to_string())

# ---- PDF: one heatmap per window; colored by rank WITHIN each horizon; strategy cell boxed ----
OUT = ROOT / "reports" / "zscore_rankgroups_horizon.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)
with PdfPages(OUT) as pdf:
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 5.6))
    fig.suptitle("z-reversal — mean forward return (%) by cross-sectional z-RANK group × horizon   (daily, 2020+)\n"
                 "boxed = the strategy account's window×horizon (the bottom-10 it buys); shading = rank within each "
                 "horizon column; bottom row = whole-universe baseline", fontsize=11, weight="bold")
    for ax, w in zip(axes, WIN):
        t = tables[w]
        rows = list(t.index)
        data = t[[f"fwd{h}d" for h in FWD]].values.astype(float)
        norm = np.full_like(data, 0.5)                     # color by rank within each horizon (column)
        for j in range(data.shape[1]):
            c = data[:, j]; lo, hi = np.nanmin(c), np.nanmax(c)
            if hi > lo:
                norm[:, j] = (c - lo) / (hi - lo)
        ax.imshow(norm, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")
        ax.set_xticks(range(len(FWD))); ax.set_xticklabels([f"fwd {h}d" for h in FWD], fontsize=9)
        ax.set_yticks(range(len(rows)))
        ax.set_yticklabels(["%s  [z %s]" % (g, t.loc[g, "z range (p10..p90, avg)"]) for g in rows], fontsize=7)
        ax.set_title(f"trailing {w}d avg-z", fontsize=11)
        sc = FWD.index(w)                                  # strategy cell column = the matched horizon
        for i in range(len(rows)):
            for j in range(len(FWD)):
                strat = (i == 0 and j == sc)
                ax.text(j, i, "%+.2f" % data[i, j], ha="center", va="center",
                        fontsize=10 if strat else 8.5, fontweight="bold" if strat else "normal")
        ax.add_patch(Rectangle((sc - 0.5, -0.5), 1, 1, fill=False, edgecolor="#15388a", lw=3))
        ax.axhline(len(rows) - 1.5, color="white", lw=2.5)   # separate the baseline row
    fig.text(0.5, 0.012, "Account ↔ cell:  zscore1d_daily = 1d-z × fwd 1d  ·  zscore5d_weekly = 5d-z × fwd 5d  ·  "
             "zscore10d_biweekly = 10d-z × fwd 10d   (each holds ≈ its horizon).   "
             "Reproduce: python research/make_zscore_rankgroups_horizon.py", ha="center", fontsize=7.5, color="#777")
    fig.tight_layout(rect=[0, 0.035, 1, 0.9])
    pdf.savefig(fig); plt.close(fig)
print("\nwrote", OUT)
