"""S1 PROTOTYPE — put-WRITING on the z-reversal bottom-10 (cash-secured puts & put-credit spreads).

Thesis (see research/options_strategy_notes.md): the `zscore10d_biweekly` book BUYS the 10 names most
fallen vs their own 60-day z norm, betting on reversion. A freshly-fallen name also has SPIKED implied
vol, so SELLING a put on it stacks an IV-monetization edge on top of the same directional bet: if the
name reverts (or just doesn't keep falling) you keep premium; if it's assigned you own the name the book
wanted anyway, at a lower basis. Same regime gate (QQQ > 200d MA -> trade, else CASH) and the validated
10d-avg-z / bottom-10 / BIWEEKLY cadence — only the EXPRESSION changes (stock long -> short put).

What this compares, all regime-filtered, gross + net, 2020+ (60d z warm-up; survivorship-biased universe):
  * EQUITY        — the baseline zscore10d_biweekly book (hold the stock) for reference
  * CSP @ moneyness — cash-secured short put, return on the K collateral
  * PCS           — put-credit spread (short put / long lower put), return on the spread width (margin)

*** CREDIBILITY CAVEAT — read before trusting any magnitude ***
There is NO historical options data here. Premiums are MODELED via Black-Scholes with an IV PROXY =
(trailing 20d realized vol) x VRP_MULT. That proxy is the weakest link: real IV >> realized exactly on a
freshly-fallen name (the regime this trades), so modeled premium almost certainly UNDERSTATES the true
edge, while ignoring IV-crush/skew/earnings can overstate it. Treat the SIGN and the cross-variant
ordering as the signal; do NOT trust the absolute annualized numbers until validated against real chains
(the planned make_options_iv_sanity.py / make_options_pricer.py). Frictionless except the SPREAD_FRAC
haircut on premium.
"""
import sys
import glob
import math
import warnings
from datetime import date
from pathlib import Path

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import numpy as np
import pandas as pd
from _common import load_ctx

# ── tunables ────────────────────────────────────────────────────────────────
N = 10                  # bottom-N names (matches the book)
AVG_WIN = 10            # z averaging window (10d-avg z = the validated config)
REGIME_MA = 200         # QQQ regime filter (cash below)
VRP_MULT = 1.15         # IV proxy = trailing realized vol x this (vol-risk-premium fudge)
RV_WIN = 20             # trailing realized-vol window (trading days)
SIG_FLOOR, SIG_CAP = 0.10, 2.00   # clamp the annualized IV proxy
SPREAD_FRAC = 0.10      # option transaction cost = lose this fraction of premium to the bid/ask
RFREE = 0.0             # risk-free (kept 0 for a clean prototype)
PER = 26                # biweekly periods / year (annualization)
# variants: (label, kind, moneyness_otm, spread_width)  — otm/width as fractions of spot/strike
VARIANTS = [
    ("EQUITY (stock)",      "equity", None, None),
    ("CSP ATM",             "csp",    0.00, None),
    ("CSP 3% OTM",          "csp",    0.03, None),
    ("CSP 5% OTM",          "csp",    0.05, None),
    ("PCS 3% OTM / 5% wide", "pcs",   0.03, 0.05),
]


# ── Black-Scholes put (no scipy; erf via numpy-vectorized math.erf) ──────────
_erf = np.vectorize(math.erf)
def _ncdf(x):
    return 0.5 * (1.0 + _erf(np.asarray(x, float) / math.sqrt(2.0)))


def bs_put(S, K, T, sigma, r=RFREE):
    """European put price, vectorized over S/K/sigma arrays (scalar T)."""
    S = np.asarray(S, float); K = np.asarray(K, float)
    sigma = np.clip(np.asarray(sigma, float), 1e-6, None)
    T = max(float(T), 1e-6)
    vt = sigma * math.sqrt(T)
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / vt
    d2 = d1 - vt
    return K * math.exp(-r * T) * _ncdf(-d2) - S * _ncdf(-d1)


# ── data: reuse the cached score panel + price panel; add QQQ + realized vol ──
ctx = load_ctx("model_v4", z_lookback=60)
close = ctx.close
SIG = ctx.Z.rolling(AVG_WIN).mean()                                  # 10d-avg of the 60d z
rv = np.log(close).diff().rolling(RV_WIN).std() * math.sqrt(252)     # annualized realized-vol panel

px_bw = close.resample("W-FRI").last().iloc[::2]                     # biweekly = every other Friday
sig_bw = SIG.resample("W-FRI").last().reindex(px_bw.index)
rv_bw = rv.reindex(px_bw.index, method="ffill")

from backtest import fetch_backtest_data                            # qqq + equity ref not in load_ctx
qqq = fetch_backtest_data(["QQQ"], date(2018, 6, 1), date.today())["Close"]
qqq = qqq["QQQ"] if hasattr(qqq, "columns") else qqq
regime_on = (qqq > qqq.rolling(REGIME_MA).mean()).reindex(px_bw.index, method="ffill")
eq = pd.read_csv(sorted(glob.glob(str(ROOT.parent / "backtests" / "scenario_model_v4_*_equity.csv")))[-1],
                 parse_dates=["date"]).set_index("date")


def period_returns(label, kind, otm, width):
    """Per-rebalance gross & net return (%) of the bottom-N basket under one expression + turnover."""
    dts = [d for d in px_bw.index if d.year >= 2020]
    gross, net, turn, prev = [], [], [], set()
    for i in range(len(dts) - 1):
        cur, nxt = dts[i], dts[i + 1]
        on = bool(regime_on.get(cur, True))
        hold, g, n = set(), 0.0, 0.0
        if on:
            sig = sig_bw.loc[cur].dropna().sort_values()
            if len(sig) >= 2 * N:
                bot = list(sig.head(N).index)
                S0 = px_bw.loc[cur].reindex(bot).astype(float)
                S1 = px_bw.loc[nxt].reindex(bot).astype(float)
                sg = (rv_bw.loc[cur].reindex(bot).astype(float) * VRP_MULT).clip(SIG_FLOOR, SIG_CAP)
                T = max((nxt - cur).days, 1) / 365.0
                ok = S0.notna() & S1.notna() & sg.notna() & (S0 > 0)
                bot = [b for b in bot if ok.get(b, False)]
                if bot:
                    hold = set(bot)
                    S0, S1, sg = S0[bot].values, S1[bot].values, sg[bot].values
                    if kind == "equity":
                        rg = S1 / S0 - 1.0
                        rn = rg                                     # equity cost handled below via turnover
                    elif kind == "csp":
                        K = S0 * (1.0 - otm)
                        prem = bs_put(S0, K, T, sg)
                        payoff = np.maximum(K - S1, 0.0)
                        rg = (prem - payoff) / K                    # return on cash collateral
                        rn = ((1 - SPREAD_FRAC) * prem - payoff) / K
                    else:                                           # put-credit spread
                        K1 = S0 * (1.0 - otm)
                        K2 = K1 * (1.0 - width)
                        p1, p2 = bs_put(S0, K1, T, sg), bs_put(S0, K2, T, sg)
                        net_prem = p1 - p2
                        payoff = np.maximum(K1 - S1, 0.0) - np.maximum(K2 - S1, 0.0)
                        margin = K1 - K2                            # max loss collateral
                        rg = (net_prem - payoff) / margin
                        rn = (net_prem - payoff - SPREAD_FRAC * (p1 + p2)) / margin
                    g, n = float(np.mean(rg) * 100), float(np.mean(rn) * 100)
        gross.append((nxt, g)); net.append((nxt, n))
        turn.append((len(hold ^ prev) / 2.0) / N); prev = hold
    return pd.Series(dict(gross)), pd.Series(dict(net)), (float(np.mean(turn)) if turn else 0.0)


def stat(s, per=PER):
    g = s.dropna() / 100.0
    if len(g) == 0:
        return 0.0, 0.0
    grow = float(np.prod(1 + g))
    ann = ((grow ** (per / len(g)) - 1) * 100) if grow > 0 else -100.0
    sh = (g.mean() / g.std() * math.sqrt(per)) if g.std() else 0.0
    return ann, sh


# ── report ──────────────────────────────────────────────────────────────────
print("S1: PUT-WRITING on the z-reversal bottom-%d  (10d-avg z / BIWEEKLY / QQQ>%dd MA -> else CASH)"
      % (N, REGIME_MA))
print("    IV proxy = %.0fd realized vol x %.2f  |  option cost = %.0f%% of premium  |  2020+, MODELED premiums\n"
      % (RV_WIN, VRP_MULT, SPREAD_FRAC * 100))
print("%-22s | %-19s | %-19s | %5s | %6s" %
      ("EXPRESSION", "GROSS ann / Sharpe", "NET  ann / Sharpe", "turn", "worst"))
print("-" * 92)
keep = {}
for label, kind, otm, width in VARIANTS:
    gs_, ns_, turn = period_returns(label, kind, otm, width)
    if kind == "equity":
        ns_ = gs_ - turn * 2 * 10 / 100.0                          # equity 10bp/turnover for a fair baseline
    keep[label] = ns_
    ga, gsh = stat(gs_); na, nsh = stat(ns_)
    print("%-22s | %+7.1f%% / %5.2f     | %+7.1f%% / %5.2f     | %4.0f%% | %+5.1f%%"
          % (label, ga, gsh, na, nsh, turn * 100, ns_.min()))
print("-" * 92)
qd = (qqq.pct_change() * 100).dropna(); qd = qd[qd.index.year >= 2020]
md = (eq["daily_return"] * 100).dropna(); md = md[md.index.year >= 2020]
for lbl, s in [("QQQ", qd), ("model_v4", md)]:
    a, sh = stat(s, 252)
    print("  ref %-9s ann %+6.1f%%  Sharpe %.2f" % (lbl, a, sh))

print("\nAnnual NET returns:")
print("  %-22s %s" % ("", "  ".join("%6d" % y for y in range(2020, 2027))))
for label, *_ in VARIANTS:
    r = keep[label]; r.index = pd.to_datetime(r.index)
    ann = {y: (np.prod(1 + g / 100) - 1) * 100 for y, g in r.groupby(r.index.year)}
    print("  %-22s %s" % (label, "  ".join("%+5.0f%%" % ann.get(y, 0) for y in range(2020, 2027))))

print("\n[caveat] premiums are MODELED (BS + realized-vol IV proxy), not real chains — see module docstring."
      "\n         The realized-vol proxy likely UNDERSTATES post-drop IV, so a real edge could be larger;"
      "\n         validate vs live chains (make_options_iv_sanity.py) before believing the magnitudes.")
