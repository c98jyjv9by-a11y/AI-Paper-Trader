"""
3-year-cycle backtest of model_v4 across three universes — saves a backtests/ artifact.

Variants per cycle:
  • curated      — model_v4's real ~83-name list (as shipped)
  • broad        — a broad, long-history relevant-ticker list (TEST ONLY; model_v4 unchanged)
  • broad+hedge  — broad universe with the hybrid up-shock+vol SOXS overlay applied

Outputs:
  backtests/model_v4_cycle_test.csv   (one row per cycle × variant)
  backtests/model_v4_cycle_test.md    (summary table + caveats)

TEST ONLY — does not modify model_v4's universe or any model state.
"""
import sys, io, contextlib
from datetime import date
from pathlib import Path
import numpy as np, pandas as pd, yfinance as yf

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))
from scenarios import build_config, load_scenario
from backtest import load_config, fetch_backtest_data, run_backtest, compute_metrics

BROAD = ['NVDA','AMD','INTC','QCOM','AVGO','TXN','AMAT','MU','ADI','KLAC','LRCX','ASML','TSM','NXPI',
 'MCHP','SWKS','TER','ON','STX','WDC','MRVL','MPWR','AAPL','MSFT','GOOGL','AMZN','META','NFLX','ORCL',
 'CRM','ADBE','INTU','CSCO','IBM','NOW','WDAY','ANSS','CDNS','SNPS','VRSN','AKAM','FTNT','ADSK','PANW',
 'TSLA','EBAY','BKNG','SHOP','PYPL','ZS','DDOG','CRWD','NET','SNOW','OKTA','TTD','HUBS','TWLO']
END = date(2026, 6, 18)
N_CYCLES = 9   # back to ~1999-2002 (covers the 2000 dot-com cycle)

base_cfg = build_config(load_config(ROOT / "config"), load_scenario("model_v4"))
CURATED = list(base_cfg["tickers"])

# 3-year cycles back from END
cycles = []; e = END
for _ in range(N_CYCLES):
    s = date(e.year - 3, e.month, e.day); cycles.append((s, e)); e = s
cycles = list(reversed(cycles))

# hedge inputs (QQQ up-shock, SPY 5d-vol z, SOXS returns)
hx = yf.download(["QQQ", "SPY", "SOXS"], start="1999-01-01", end="2026-06-19",
                 auto_adjust=True, progress=False)["Close"]
hx.index = pd.to_datetime(hx.index).tz_localize(None)
QUP = hx["QQQ"].pct_change()
_sv = hx["SPY"].pct_change().rolling(5).std() * np.sqrt(252)
VOLZ = (_sv - _sv.rolling(63).mean().shift(1)) / _sv.rolling(63).std().shift(1)
SOXS_RET = hx["SOXS"].pct_change()
SOXS_VOL = SOXS_RET.rolling(20).std().shift(1)


def hybrid_overlay(book_eq):
    """Apply the hybrid 2-gate inverse-vol SOXS overlay to a book equity curve -> (total_ret, maxDD)."""
    r = book_eq.pct_change()
    bvol = r.rolling(20).std().shift(1)
    w = (0.5 * bvol / SOXS_VOL.reindex(r.index)).clip(upper=0.6)
    soft = (QUP.reindex(r.index) >= 0.015) & (VOLZ.reindex(r.index) >= 0.75)
    hard = (QUP.reindex(r.index) >= 0.020) & (VOLZ.reindex(r.index) >= 1.0)
    mult = np.where(hard, 1.0, np.where(soft, 0.5, 0.0))
    effw = (pd.Series(mult, index=r.index) * w).shift(1).fillna(0.0)
    sleeve = np.where(effw > 0, effw * SOXS_RET.reindex(r.index) - effw * 0.0010, 0.0)
    ov = (r + pd.Series(sleeve, index=r.index)).fillna(0.0)
    eq = (1 + ov).cumprod()
    return float(eq.iloc[-1] - 1), float((eq / eq.cummax() - 1).min())


def run_universe(tickers, label):
    cfg = build_config(load_config(ROOT / "config"), load_scenario("model_v4"))
    cfg["tickers"] = tickers
    pdata = fetch_backtest_data(tickers, date(1999, 1, 1), END, warmup_days=0)
    close = pdata["Close"] if ("Close" in pdata.columns.get_level_values(0)) else pdata
    rows = []
    for s, e in cycles:
        with contextlib.redirect_stdout(io.StringIO()):
            t, eq, p = run_backtest(cfg, pdata, s, e)
            m = compute_metrics(t, eq, p, cfg, s, e)
        yrs = (e - s).days / 365.25
        cagr = (1 + m["total_return"]) ** (1 / yrs) - 1 if m["total_return"] > -1 else float("nan")
        nm = int(((close.loc[:str(s)].notna().sum()) > 21).sum())
        row = dict(cycle=f"{s}→{e}", start=str(s), end=str(e), variant=label, n_names=nm,
                   trades=int(len(t)), total_return=m["total_return"], cagr=cagr,
                   max_drawdown=m["max_drawdown"], spy_return=m["spy_return"], qqq_return=m["qqq_return"],
                   excess_vs_spy=m["excess_vs_spy"], excess_vs_qqq=m["excess_vs_qqq"])
        rows.append((row, eq))
    return rows


out = []
cur = run_universe(CURATED, "curated")
for row, _eq in cur:
    out.append(row)
brd = run_universe(BROAD, "broad")
for row, eq in brd:
    out.append(row)
    beq = pd.Series(eq["total_portfolio_value"].values, index=pd.to_datetime(eq["date"]))
    htot, hdd = hybrid_overlay(beq)
    h = dict(row); h["variant"] = "broad+hedge"; h["total_return"] = htot; h["max_drawdown"] = hdd
    yrs = (date.fromisoformat(row["end"]) - date.fromisoformat(row["start"])).days / 365.25
    h["cagr"] = (1 + htot) ** (1 / yrs) - 1 if htot > -1 else float("nan")
    h["excess_vs_spy"] = htot - row["spy_return"]; h["excess_vs_qqq"] = htot - row["qqq_return"]
    out.append(h)

df = pd.DataFrame(out)
csv = ROOT / "backtests" / "model_v4_cycle_test.csv"
df.to_csv(csv, index=False)


def pct(x):
    return ("%+.0f%%" % (x * 100)) if pd.notna(x) else "na"

L = ["# model_v4 — 3-year-cycle backtest (curated vs broad vs broad+hedge)", ""]
L.append("Paper/simulated. model_v4's logic is fixed; only the **universe** changes. "
         "`broad` = a 58-name long-history relevant set (TEST ONLY). `broad+hedge` adds the hybrid "
         "up-shock+vol SOXS overlay. Generated by `make_cycle_test.py`.\n")
for var in ["curated", "broad", "broad+hedge"]:
    L.append(f"## {var}\n")
    L.append("| cycle | #names | trades | total | CAGR | maxDD | vs SPY | vs QQQ |")
    L.append("|---|--:|--:|--:|--:|--:|--:|--:|")
    for r in [r for r in out if r["variant"] == var]:
        L.append("| %s | %d | %d | %s | %s | %s | %s | %s |" % (
            r["cycle"], r["n_names"], r["trades"], pct(r["total_return"]), pct(r["cagr"]),
            pct(r["max_drawdown"]), pct(r["excess_vs_spy"]), pct(r["excess_vs_qqq"])))
    L.append("")
L.append("## Caveats")
L.append("- **Survivorship:** all lists are survivors only (no delisted names) — early-cycle returns are upward-biased.")
L.append("- **Curated list is recency-skewed:** many model_v4 names IPO'd late, so its early cycles trade a thin subset.")
L.append("- **Mostly in-sample:** model_v4 was tuned ~2018–2026; recent cycles are the least independent.")
L.append("- **Hedge inactive before 2011** (SOXS did not exist) — pre-2011 broad+hedge equals broad.")
L.append("- **Hedge** modeled on QQQ/SPY/SOXS with flat 10bp costs; shines in crash/vol-spike cycles, mild drag in calm ones.")
(ROOT / "backtests" / "model_v4_cycle_test.md").write_text("\n".join(L))
print("wrote", csv.name, "and model_v4_cycle_test.md  (%d rows)" % len(df))
