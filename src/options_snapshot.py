"""
options_snapshot.py — DAILY yfinance option-chain capture (build the history we don't have).

There is no free historical option chain, so the only way to backtest an options strategy on this
book is to START SAVING one now. This collector snapshots, once per day, the short-dated chain for
the model_v4 universe (83 tickers) + the SPY/QQQ benchmarks — both calls AND puts, every expiry
within `--max-dte` calendar days (default 31 = "1 month and under").

One gzipped CSV per snapshot date under data/options/options_<YYYY-MM-DD>.csv.gz, append-only across
days (idempotent within a day: re-running overwrites that day's file). A running data/options/
_manifest.csv logs each capture (rows / underlyings / errors) for monitoring.

The pure transform (_chain_records) is unit-tested without network; only run() touches yfinance.

CLI:
    python src/options_snapshot.py                 # capture today's chains
    python src/options_snapshot.py --max-dte 31 --force
    python run.py options-snapshot
"""
from __future__ import annotations

import argparse
import datetime as _dt
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

BENCHMARKS = ["SPY", "QQQ"]
OUTDIR = ROOT / "data" / "options"
_COLS = ["snapshot_date", "snapshot_ts", "underlying", "spot", "expiry", "dte", "right", "strike",
         "moneyness", "contract_symbol", "bid", "ask", "last", "mid", "volume", "open_interest",
         "implied_vol", "in_the_money"]


def _universe() -> List[str]:
    """The 83 model_v4 tickers + SPY/QQQ benchmarks (deduped, order-stable)."""
    from scenarios import build_config, load_scenario
    from backtest import load_config
    cfg = build_config(load_config(ROOT / "config"), load_scenario("model_v4"))
    seen, out = set(), []
    for t in list(cfg["tickers"]) + BENCHMARKS:
        u = str(t).strip().upper()
        if u and u not in seen:
            seen.add(u); out.append(u)
    return out


def _f(v) -> float:
    try:
        return float(v) if pd.notna(v) else 0.0
    except (TypeError, ValueError):
        return 0.0


def _i(v) -> int:
    try:
        return int(v) if pd.notna(v) else 0
    except (TypeError, ValueError):
        return 0


def _chain_records(underlying: str, spot: Optional[float], expiry: str,
                   calls: "pd.DataFrame", puts: "pd.DataFrame", snapshot_date: _dt.date,
                   ts: str) -> List[Dict[str, Any]]:
    """PURE: flatten a yfinance option_chain (calls + puts DataFrames) into snapshot rows.
    Columns expected from yfinance: contractSymbol, strike, bid, ask, lastPrice, volume,
    openInterest, impliedVolatility, inTheMoney."""
    dte = (_dt.date.fromisoformat(expiry) - snapshot_date).days
    sp = float(spot) if spot else None
    rows: List[Dict[str, Any]] = []
    for right, df in (("call", calls), ("put", puts)):
        if df is None or len(df) == 0:
            continue
        for _, r in df.iterrows():
            bid, ask, last = _f(r.get("bid")), _f(r.get("ask")), _f(r.get("lastPrice"))
            mid = (bid + ask) / 2 if (bid and ask) else (ask or bid or last)
            strike = _f(r.get("strike"))
            iv = r.get("impliedVolatility")
            itm = r.get("inTheMoney")
            rows.append({
                "snapshot_date": snapshot_date.isoformat(), "snapshot_ts": ts,
                "underlying": underlying, "spot": sp, "expiry": expiry, "dte": dte,
                "right": right, "strike": strike,
                "moneyness": round(strike / sp - 1, 4) if (sp and strike) else None,
                "contract_symbol": r.get("contractSymbol"),
                "bid": bid, "ask": ask, "last": last, "mid": round(mid, 4),
                "volume": _i(r.get("volume")), "open_interest": _i(r.get("openInterest")),
                "implied_vol": (float(iv) if pd.notna(iv) else None),
                "in_the_money": (bool(itm) if pd.notna(itm) else None),
            })
    return rows


def _spots(unders: List[str]) -> Dict[str, float]:
    """Last close per underlying in one batched yfinance download (for moneyness)."""
    try:
        import yfinance as yf
        data = yf.download(unders, period="2d", interval="1d", auto_adjust=True,
                           progress=False, group_by="column")
        close = data["Close"] if "Close" in data else data
        out: Dict[str, float] = {}
        for u in unders:
            try:
                ser = close[u] if (hasattr(close, "columns") and u in close.columns) else close
                v = ser.dropna()
                if len(v) and float(v.iloc[-1]) > 0:
                    out[u] = float(v.iloc[-1])
            except Exception:
                pass
        return out
    except Exception:
        return {}


def run(max_dte: int = 31, out: Optional[str] = None, tickers: Optional[List[str]] = None,
        force: bool = False) -> Dict[str, Any]:
    """Capture today's short-dated chains for the universe and write one gzipped CSV. Returns a
    summary dict. Per-underlying failures are recorded, not fatal (a flaky ticker can't sink the run)."""
    import yfinance as yf
    asof = _dt.date.today()
    ts = _dt.datetime.now().isoformat(timespec="seconds")
    unders = tickers or _universe()
    OUTDIR.mkdir(parents=True, exist_ok=True)
    path = Path(out) if out else OUTDIR / f"options_{asof.isoformat()}.csv.gz"
    if path.exists() and not force:
        return {"asof": asof.isoformat(), "path": str(path), "skipped": True,
                "reason": "already captured today (use --force to overwrite)"}
    spots = _spots(unders)
    all_rows: List[Dict[str, Any]] = []
    errors: List[str] = []
    n_exp = 0
    for u in unders:
        try:
            tk = yf.Ticker(u)
            for e in list(tk.options or []):
                d = (_dt.date.fromisoformat(e) - asof).days
                if d < 0 or d > max_dte:                    # keep only 0..max_dte DTE (1 month and under)
                    continue
                oc = tk.option_chain(e)
                all_rows.extend(_chain_records(u, spots.get(u), e, oc.calls, oc.puts, asof, ts))
                n_exp += 1
        except Exception as exc:
            errors.append(f"{u}: {exc}")
    df = pd.DataFrame(all_rows, columns=_COLS)
    df.to_csv(path, index=False, compression="gzip")
    summary = {"asof": asof.isoformat(), "path": str(path), "skipped": False,
               "underlyings": len(unders), "with_data": df["underlying"].nunique() if len(df) else 0,
               "expiries": n_exp, "rows": len(df), "errors": len(errors)}
    # append a monitoring row to the running manifest
    man_row = {**{k: summary[k] for k in ("asof", "rows", "underlyings", "with_data", "expiries", "errors")},
               "snapshot_ts": ts, "max_dte": max_dte}
    man_path = OUTDIR / "_manifest.csv"
    pd.DataFrame([man_row]).to_csv(man_path, mode="a", header=not man_path.exists(), index=False)
    if errors:
        summary["error_sample"] = errors[:5]
    return summary


def _cli(argv=None):
    p = argparse.ArgumentParser(description="Daily yfinance option-chain snapshot (1-month-and-under)")
    p.add_argument("--max-dte", type=int, default=31, help="keep expiries within this many days (default 31)")
    p.add_argument("--out", help="output path (default data/options/options_<date>.csv.gz)")
    p.add_argument("--tickers", help="comma-separated override of the underlyings (default 83 + SPY/QQQ)")
    p.add_argument("--force", action="store_true", help="overwrite today's snapshot if it already exists")
    a = p.parse_args(argv)
    tks = [t.strip().upper() for t in a.tickers.split(",")] if a.tickers else None
    r = run(max_dte=a.max_dte, out=a.out, tickers=tks, force=a.force)
    if r.get("skipped"):
        print("OPTIONS SNAPSHOT %s: SKIPPED (%s)" % (r["asof"], r["reason"]))
    else:
        print("OPTIONS SNAPSHOT %s: %d rows, %d/%d underlyings, %d expiries, %d errors -> %s" % (
            r["asof"], r["rows"], r["with_data"], r["underlyings"], r["expiries"], r["errors"], r["path"]))
        if r.get("error_sample"):
            for e in r["error_sample"]:
                print("   !", e)


if __name__ == "__main__":
    _cli()
