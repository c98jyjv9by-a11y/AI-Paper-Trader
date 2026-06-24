"""Annual returns of a portfolio that trades on the per-ticker 60-DAY Z-SCORE ranking (z = (score -
mean60)/std60), weekly & monthly rebalance, top-10 / bottom-10 / 20-name, vs QQQ + model_v4. Mirror of
make_freq_compare but ranking by Z instead of the raw score. Reuses the cached score panel.
NOTE: Z has a 60-day warmup (cache starts 2019-12), so 2020 is PARTIAL (z-baskets begin ~Mar 2020)."""
import sys
import glob
import warnings
from datetime import date
from pathlib import Path

warnings.filterwarnings("ignore")
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))
import numpy as np
import pandas as pd
from backtest import load_config, fetch_backtest_data
from scenarios import load_scenario, build_config

cfg = build_config(load_config(ROOT / "config"), load_scenario("model_v4"))
close = fetch_backtest_data(cfg["tickers"], date(2018, 6, 1), date.today())["Close"]
S = pd.read_csv(ROOT / "backtests" / "daily_scores_model_v4.csv", index_col=0, parse_dates=True)
Z = (S - S.rolling(60).mean()) / S.rolling(60).std()           # per-ticker 60-day rolling z-score
qc = fetch_backtest_data(["QQQ"], date(2018, 6, 1), date.today())["Close"]
qqq = qc["QQQ"] if hasattr(qc, "columns") else qc
qqq_w = (qqq.resample("W-FRI").last().pct_change() * 100).dropna()
qqq_w = qqq_w[qqq_w.index.year >= 2020]
qqq_m = (qqq.groupby(qqq.index.to_period("M")).last().pct_change() * 100).dropna()
qqq_m = qqq_m[[p.year >= 2020 for p in qqq_m.index]]
eq = pd.read_csv(sorted(glob.glob(str(ROOT / "backtests" / "scenario_model_v4_*_equity.csv")))[-1],
                 parse_dates=["date"]).set_index("date")
pv = eq["total_portfolio_value"]
base19 = pv[pv.index.year == 2019].iloc[-1]
mv4_ann = {y: (pv[pv.index.year == y].iloc[-1] / pv[pv.index.year == y - 1].iloc[-1] - 1) * 100
           for y in range(2020, 2027) if len(pv[pv.index.year == y]) and len(pv[pv.index.year == y - 1])}
mv4_total = (pv.iloc[-1] / base19 - 1) * 100
mv4_dr = eq["daily_return"][eq.index.year >= 2020].dropna()
mv4_annual = ((pv.iloc[-1] / base19) ** (252.0 / len(mv4_dr)) - 1) * 100
mv4_sh = mv4_dr.mean() / mv4_dr.std() * np.sqrt(252)


def baskets(Sp, px):
    periods = [d for d in px.index if getattr(d, "year", d.year) >= 2020]
    out = []
    for i in range(1, len(periods)):
        cur, prev = periods[i], periods[i - 1]
        if prev not in Sp.index or cur not in px.index or prev not in px.index:
            continue
        avg = Sp.loc[prev].dropna().sort_values(ascending=False)
        if len(avg) < 20:
            continue
        ret = (px.loc[cur] / px.loc[prev] - 1) * 100.0
        out.append((cur, ret.reindex(avg.head(10).index).mean(), ret.reindex(avg.tail(10).index).mean()))
    df = pd.DataFrame(out, columns=["p", "top", "bot"])
    df["combo"] = (df["top"] + df["bot"]) / 2
    df["year"] = df["p"].apply(lambda d: d.year)
    return df


wk = baskets(Z.resample("W-FRI").mean(), close.resample("W-FRI").last())
mo = baskets(Z.groupby(Z.index.to_period("M")).mean(), close.groupby(close.index.to_period("M")).last())
cmp = lambda s: (np.prod(1 + s.dropna() / 100) - 1) * 100
qa = lambda y: cmp(qqq_w[qqq_w.index.year == y])

print("RANK BY 60-DAY Z-SCORE  (weekly & monthly rebalance; 2020 partial — z warmup)\n")
print("%-6s | %9s %9s %9s | %9s %9s | %8s %9s"
      % ("YEAR", "WK TOP10", "WK BOT10", "WK 20", "MO TOP10", "MO BOT10", "QQQ", "model_v4"))
print("-" * 84)
for y in sorted(set(wk["year"]) | set(mo["year"])):
    wy, my = wk[wk.year == y], mo[mo.year == y]
    print("%-6d | %+8.1f%% %+8.1f%% %+8.1f%% | %+8.1f%% %+8.1f%% | %+7.1f%% %+8.1f%%"
          % (y, cmp(wy["top"]), cmp(wy["bot"]), cmp(wy["combo"]),
             cmp(my["top"]), cmp(my["bot"]), qa(y), mv4_ann.get(y, float("nan"))))
print("-" * 84)
print("%-6s | %+8.1f%% %+8.1f%% %+8.1f%% | %+8.1f%% %+8.1f%% | %+7.1f%% %+8.1f%%   (total compounded)"
      % ("TOTAL", cmp(wk["top"]), cmp(wk["bot"]), cmp(wk["combo"]),
         cmp(mo["top"]), cmp(mo["bot"]), cmp(qqq_w), mv4_total))


def annsh(df, col, per):
    s = df[col].dropna() / 100
    grow = np.prod(1 + s)
    return (grow ** (per / len(s)) - 1) * 100, (s.mean() / s.std() * np.sqrt(per) if s.std() else 0)


print()
for lbl, df, col, per in [("WK TOP10", wk, "top", 52), ("WK BOT10", wk, "bot", 52),
                          ("WK 20-name", wk, "combo", 52), ("MO TOP10", mo, "top", 12),
                          ("MO BOT10", mo, "bot", 12)]:
    a, sh = annsh(df, col, per)
    print("  %-10s annualized %+6.1f%%   Sharpe %.2f" % (lbl, a, sh))
for lbl, s, per in [("QQQ (wk)", qqq_w, 52), ("QQQ (mo)", qqq_m, 12)]:
    g = s.dropna() / 100
    print("  %-10s annualized %+6.1f%%   Sharpe %.2f"
          % (lbl, (np.prod(1 + g) ** (per / len(g)) - 1) * 100, g.mean() / g.std() * np.sqrt(per)))
print("  %-10s annualized %+6.1f%%   Sharpe %.2f   (actual strategy)" % ("model_v4", mv4_annual, mv4_sh))
