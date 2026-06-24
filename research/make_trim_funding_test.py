"""
make_trim_funding_test.py — if we FUND the overlay by trimming the book (rotation, like a persistence
buy) instead of from spare cash, what's the optimal trim weight for the hedge and the rebound?

Funded-by-CASH (current model): on a fire day, ADD W of the instrument on top -> book + W*instr.
Funded-by-TRIM (rotation): SELL W of the book and put it into the instrument for the 1-day hold ->
    book*(1-W) + W*instr  =  book + W*(instr - book).  Costs ~2x turnover (trade the book AND the
    overlay, round-trip). Trimming gives up the book's own return on the swapped slice — that's the
    opportunity cost we're sizing here. (We approximate the trimmed slice's return by the book average;
    rotating out the *weakest* names would be marginally better.)

Sweeps W for both overlays on the model_v4 book, FULL + OOS train/test. Read-only. Console report.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import hedge_overlay as ho
import rebound_overlay as ro

ROOT = Path(__file__).parent.parent
df = pd.read_csv(ROOT / "backtests" / "model_v4_timeseries.csv", parse_dates=["date"]).set_index("date")
dfr = ro._add_instrument(df, ro.ReboundConfig())
WIN = {"FULL": ("2016-06-20", "2026-06-18"), "TRAIN": ("2018-06-22", "2022-06-22"),
       "TEST": ("2022-06-22", "2026-06-18")}
RT = 0.0010
book = df["book_fwd_1d"]


def sh(r, w):
    r = r.loc[WIN[w][0]:WIN[w][1]].dropna()
    return (r.mean() / r.std() * np.sqrt(252)) if r.std() > 0 else 0.0


def worst(r):
    return r.loc[WIN["FULL"][0]:WIN["FULL"][1]].dropna().min()


BASE = {w: sh(book, w) for w in WIN}

hov = ho.build_overlay(df, ho.HedgeConfig())
rov = ro.build_overlay(dfr, ro.ReboundConfig())
OVERLAYS = [("HEDGE  (up-shock -> SOXS)", hov["hedge_on"], hov["hedge_instr_ret"], 0.45),
            ("REBOUND (down-shock -> TQQQ)", rov["rebound_on"], dfr["tqqq_fwd_1d"], 0.50)]


def cash(fire, instr, W):
    s = np.where(fire & instr.notna(), W * instr - W * RT, 0.0)
    return book + pd.Series(s, index=book.index)


def trim(fire, instr, W):
    s = np.where(fire & instr.notna(), W * (instr - book) - 2 * W * RT, 0.0)
    return book + pd.Series(s, index=book.index)


print("\nBaseline book Sharpe:  FULL %+.2f  TRAIN %+.2f  TEST %+.2f\n"
      % (BASE["FULL"], BASE["TRAIN"], BASE["TEST"]))
for name, fire, instr, Wt in OVERLAYS:
    print(f"=== {name}  ({int(fire.sum())} fires) ===")
    rc = cash(fire, instr, Wt)
    print("  funded-by-CASH  W=%2.0f%%:  dSh FULL %+.2f / TRAIN %+.2f / TEST %+.2f  worst1d %+.0f%%  (current model)"
          % (Wt * 100, sh(rc, "FULL") - BASE["FULL"], sh(rc, "TRAIN") - BASE["TRAIN"],
             sh(rc, "TEST") - BASE["TEST"], worst(rc) * 100))
    print("  funded-by-TRIM (rotation):")
    best = None
    for W in [0.10, 0.20, 0.30, 0.40, 0.50, 0.60]:
        rt_ = trim(fire, instr, W)
        d = {w: sh(rt_, w) - BASE[w] for w in WIN}
        mn = min(d.values())
        if best is None or mn > best[1]:
            best = (W, mn)
        print("    W=%2.0f%%:  dSh FULL %+.2f / TRAIN %+.2f / TEST %+.2f   worst1d %+.0f%%"
              % (W * 100, d["FULL"], d["TRAIN"], d["TEST"], worst(rt_) * 100))
    print("  -> best trim W (by worst-window dSharpe): %.0f%%\n" % (best[0] * 100))
