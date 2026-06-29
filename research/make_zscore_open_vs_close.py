"""Open- vs close-EXECUTION backtest for the z-reversal WEEKLY books (zscore5d_weekly + zscore10d_biweekly).

Question: the books decide off the close (the z-signal at the rebalance close). The CLOSE model fills at
that decision close (the idealized close-to-close the frictionless backtest assumes — which live can't
actually capture). The new OPEN model fills at the NEXT SESSION'S OPEN (signal off the prior close, e.g.
a Monday-open rebalance off Friday's close). We hold the SIGNAL and the PICKS fixed and vary ONLY the fill
point, so this isolates the cost/benefit of executing at the next open instead of the decision close.

Both run under the live regime filter (cash when QQQ < 200-day MA). Reports gross + net (turnover-costed)
annualized return, Sharpe, worst period, and annual breakdown for CLOSE vs OPEN. Writes a dated markdown
to backtests/. 2020+; uses the precomputed daily score panel; survivorship-affected (fixed universe)."""
import sys
import warnings
from datetime import date
from pathlib import Path

warnings.filterwarnings("ignore")
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))
import numpy as np
import pandas as pd
from backtest import load_config, fetch_backtest_data
from scenarios import load_scenario, build_config

cfg = build_config(load_config(ROOT / "config"), load_scenario("model_v4"))
data = fetch_backtest_data(cfg["tickers"], date(2018, 6, 1), date.today())
close = data["Close"]
openN = data["Open"].shift(-1)                       # the NEXT session's open, aligned to each date
qqq = fetch_backtest_data(["QQQ"], date(2018, 6, 1), date.today())["Close"]
qqq = qqq["QQQ"] if hasattr(qqq, "columns") else qqq
S = pd.read_csv(ROOT / "backtests" / "daily_scores_model_v4.csv", index_col=0, parse_dates=True)
Z = (S - S.rolling(60).mean()) / S.rolling(60).std()
N = 10


def _grids(aw, biweekly):
    """Aligned (close-fill, next-open-fill, signal) grids on ONE (bi)weekly date index. The index is taken
    from the close grid; the open + signal series are reindexed onto it (the scores start on a different
    date than the prices, so a separate ::2 on each would misalign the alternating biweekly weeks)."""
    cw, ow, sw = (x.resample("W-FRI").last() for x in (close, openN, Z.rolling(aw).mean()))
    idx = (cw.iloc[::2] if biweekly else cw).index
    return cw.reindex(idx), ow.reindex(idx), sw.reindex(idx)


def _regime(idx, ma_days=200):
    ma = qqq.rolling(ma_days).mean()
    return (qqq > ma).reindex(idx, method="ffill")


def backtest(px, sig, reg):
    """px = the price grid to fill on (close grid = CLOSE model; next-open grid = OPEN model). Picks come
    from `sig` at the decision date (identical for both models). Returns (per-period %% series, avg turnover)."""
    dts = [d for d in px.index if d.year >= 2020]
    rets, turn, prev = [], [], set()
    for i in range(len(dts) - 1):
        cur, nxt = dts[i], dts[i + 1]
        on = bool(reg.get(cur, True))
        hold, ret = set(), 0.0
        if on:
            s = sig.loc[cur].dropna().sort_values()
            if len(s) >= 20:
                bot = list(s.head(N).index)
                hold = set(bot)
                ret = (px.loc[nxt] / px.loc[cur] - 1).reindex(bot).mean() * 100
        rets.append((nxt, ret))
        turn.append((len(hold ^ prev) / 2.0) / N)
        prev = hold
    return pd.Series(dict(rets)), (float(np.mean(turn)) if turn else 0.0)


def stat(s, per):
    g = s.dropna() / 100
    if len(g) == 0:
        return 0.0, 0.0
    grow = float(np.prod(1 + g))
    ann = (grow ** (per / len(g)) - 1) * 100
    sharpe = (g.mean() / g.std() * np.sqrt(per)) if g.std() else 0.0
    return ann, sharpe


BOOKS = [("zscore5d_weekly", 5, False, 52), ("zscore10d_biweekly", 10, True, 26)]
out = ["# z-reversal WEEKLY books — OPEN vs CLOSE execution  (%s)\n" % date.today().isoformat(),
       "Signal + picks held fixed at the decision close; only the FILL point varies "
       "(decision close vs next-session open). Regime filter: cash when QQQ < 200-day MA. 2020+.\n"]


def emit(line=""):
    print(line)
    out.append(line)


for name, aw, biweekly, per in BOOKS:
    pxC, pxO, sig = _grids(aw, biweekly)
    reg = _regime(pxC.index)
    rc, turn = backtest(pxC, sig, reg)
    ro, _ = backtest(pxO, sig, reg)            # same picks/turnover -> cost drag identical

    emit("\n## %s  (%dd-avg z, %s)" % (name, aw, "biweekly" if biweekly else "weekly"))
    emit("%-7s | %-19s | %5s | %-22s | %7s" % ("FILL", "GROSS ann / Sharpe", "turn", "NET ann @5bp/10bp", "worst"))
    emit("-" * 78)
    rows = {}
    for lbl, r in [("CLOSE", rc), ("OPEN", ro)]:
        ga, gs = stat(r, per)
        nets = [stat(r - turn * 2 * bps / 100.0, per)[0] for bps in (5, 10)]
        rows[lbl] = (ga, gs, nets)
        emit("%-7s | %+7.1f%% / %5.2f     | %4.0f%% | %+8.1f%% / %+8.1f%%   | %+5.1f%%"
             % (lbl, ga, gs, turn * 100, nets[0], nets[1], r.min()))
    dga = rows["OPEN"][0] - rows["CLOSE"][0]
    dgs = rows["OPEN"][1] - rows["CLOSE"][1]
    dnet = rows["OPEN"][2][1] - rows["CLOSE"][2][1]
    emit("%-7s | %+7.1f%% / %+5.2f     | %4s | %+8s   / %+8.1f%%   |" %
         ("Δ O-C", dga, dgs, "", "", dnet))
    # annual gross
    emit("\nAnnual gross return by year:")
    emit("  %-7s %s" % ("", "  ".join("%6d" % y for y in range(2020, 2027))))
    for lbl, r in [("CLOSE", rc), ("OPEN", ro)]:
        r = r.copy(); r.index = pd.to_datetime(r.index)
        ann = {y: (np.prod(1 + g / 100) - 1) * 100 for y, g in r.groupby(r.index.year)}
        emit("  %-7s %s" % (lbl, "  ".join("%+5.0f%%" % ann.get(y, 0) for y in range(2020, 2027))))

emit("\nΔ O-C = OPEN minus CLOSE. Positive = open execution HELPS; negative = the decision-close fill "
     "(which live can't fully capture) was richer. Net uses round-trip turnover cost; turnover is identical "
     "across fills, so the gross gap drives the verdict.")

dst = ROOT / "backtests" / ("zscore_open_vs_close_%s.md" % date.today().isoformat())
dst.write_text("\n".join(out) + "\n")
print("\nwrote", dst)
