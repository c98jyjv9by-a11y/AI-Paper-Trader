"""
make_volfactor_compare.py — what changes for model_v4 if the overlays gate on QQQ 5d-vol z instead of
SPY 5d-vol z? Evaluates BOTH the hedge overlay (up-shock fade) and the rebound overlay (down-shock buy)
under vol_factor = spy_vol_trl_5d vs qqq_vol_trl_5d, on the model_v4 book, over FULL + OOS train/test.
Then re-tunes the rebound's vol-z gate for QQQ. Read-only on the panel. Console report.
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
WIN = {"FULL": ("2016-06-20", "2026-06-18"), "TRAIN": ("2018-06-22", "2022-06-22"),
       "TEST": ("2022-06-22", "2026-06-18")}


def met(r, w):
    r = r.loc[WIN[w][0]:WIN[w][1]].dropna()
    eq = (1 + r).cumprod()
    return ((r.mean() / r.std() * np.sqrt(252)) if r.std() > 0 else 0.0, (eq / eq.cummax() - 1).min(), r.min())


BASE = {w: met(df["book_fwd_1d"], w) for w in WIN}
print("\nBaseline model_v4 book Sharpe:  FULL %+.2f  TRAIN %+.2f  TEST %+.2f\n"
      % (BASE["FULL"][0], BASE["TRAIN"][0], BASE["TEST"][0]))


def compare(title, build, fires_col, mk_cfg):
    print(f"=== {title} ===")
    for label, vf in [("SPY vol", "spy_vol_trl_5d"), ("QQQ vol", "qqq_vol_trl_5d")]:
        ov = build(mk_cfg(vf))
        nf = int(ov[fires_col].sum())
        cells = []
        for w in WIN:
            sh, dd, worst = met(ov["overlaid_ret"], w)
            cells.append(f"{w} dSh {sh-BASE[w][0]:+.2f} (DD {dd*100:+.0f}%)")
        print(f"  {label}:  fires {nf:3d}  |  " + "  ".join(cells))
    print()


compare("HEDGE overlay (up-shock + vol -> buy SOXS, fade)",
        lambda cfg: ho.build_overlay(df, cfg), "hedge_on",
        lambda vf: ho.HedgeConfig(vol_factor=vf))

dfr = ro._add_instrument(df, ro.ReboundConfig())     # add tqqq_fwd_1d once
compare("REBOUND overlay (down-shock + signal<0 + vol -> buy TQQQ)",
        lambda cfg: ro.build_overlay(dfr, cfg), "rebound_on",
        lambda vf: ro.ReboundConfig(vol_factor=vf))

print("=== REBOUND re-tune with QQQ vol: sweep vol_z gate (QQQ<=-2.5% & spread<0 fixed) ===")
for vz in [0.0, 0.25, 0.50, 0.75, 1.0, 1.5]:
    ov = ro.build_overlay(dfr, ro.ReboundConfig(vol_factor="qqq_vol_trl_5d", vol_z_threshold=vz))
    nf = int(ov["rebound_on"].sum())
    won = float((ov["instr_ret"][ov["rebound_on"]] > 0).mean() * 100) if nf else 0
    cells = " ".join(f"{w} dSh {met(ov['overlaid_ret'], w)[0]-BASE[w][0]:+.2f}" for w in WIN)
    print(f"  vol_z>={vz:.2f}:  fires {nf:3d}  win {won:3.0f}%  {cells}  worst1d {met(ov['overlaid_ret'],'FULL')[2]*100:+.0f}%")
print("\n(for reference, the SPY-vol tuned config was vol_z>=0.50: FULL dSh +0.04 / TRAIN +0.04 / TEST +0.06, 28 fires)")
