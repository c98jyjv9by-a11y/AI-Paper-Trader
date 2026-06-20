"""
hedge_overlay.py — standalone 1-day "up-shock + vol-surge" HEDGE OVERLAY for model_v4.

This sits ON TOP of model_v4 and never modifies it. It consumes the precomputed research
panel (backtests/model_v4_timeseries.csv) read-only — the book's daily return and the
candidate hedge instruments' next-day returns — and applies a configurable end-of-day rule:

    RULE (decide at close T, hold T+1 only, exit at close T+1):
      if  qqq_trl_1d >= up_threshold        (QQQ had a big up day)
      AND z(spy_vol_trl_5d) >= vol_z         (5-day realized vol elevated vs its recent norm)
      then BUY a 1-day semis hedge sized `weight` (short-SMH by default; SOXS/PSQ selectable).

Validated finding (see backtests/hedge_overlay_model_v4_summary.md): neither factor works
alone — a QQQ up-day on its own *bounces*; it's the INTERACTION (up-shock while vol is already
elevated) that flags the next-day pullback (e.g. 2026-06-16). The edge is a robust plateau
across thresholds (ΔSharpe ~+0.05 full / +0.03 OOS) and survives a yearly walk-forward; it is
a Sharpe-adder + single-day-blow softener, NOT an all-time-max-drawdown reducer.

Everything is in HedgeConfig, so the hedge can be retuned/swapped WITHOUT touching the model.

    python src/hedge_overlay.py                       # default rule, writes artifacts
    python src/hedge_overlay.py --weight 0.45 --product soxs --up 0.015
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).parent.parent
PANEL = ROOT / "backtests" / "model_v4_timeseries.csv"
OUT_PREFIX = ROOT / "backtests" / "hedge_overlay_model_v4"

# hedge instrument -> how to build its next-day return from panel columns (sign-adjusted)
PRODUCTS = {
    "short_smh": lambda d: -d["smh_fwd_1d"],     # 1x short semis (preferred: no leverage decay)
    "soxs":      lambda d: d["soxs_fwd_1d"],      # 3x inverse semis (more tail convexity, carries)
    "psq":       lambda d: d["psq_fwd_1d"],       # 1x inverse QQQ (weaker — not semi-specific)
    "short_top10": lambda d: -d["top10_fwd_1d"],  # 1x short the leaders
}


@dataclass
class HedgeConfig:
    # ---- trigger (the rule; change freely, model untouched) ----
    up_factor: str = "qqq_trl_1d"      # the "up-shock" measure (today's move)
    up_threshold: float = 0.02         # fire when up_factor >= this (e.g. +2% QQQ day)
    vol_factor: str = "spy_vol_trl_5d" # the supporting signal (best in sensitivity)
    vol_z_threshold: float = 1.0       # fire when z(vol_factor) >= this
    vol_lookback: int = 63             # trailing window for the vol z-score
    # ---- hedge sleeve ----
    product: str = "short_smh"
    weight: float = 0.30               # notional sleeve size (additive overlay)
    cost_bps: float = 10.0             # round-trip cost per on-day, bps of sleeve notional
    # ---- accounting ----
    book_col: str = "book_fwd_1d"
    covid_start: str = "2020-04-01"
    oos_start: str = "2024-01-01"


def _zscore(s: pd.Series, lookback: int) -> pd.Series:
    """Trailing z-score using only data known BEFORE today (shift 1)."""
    return (s - s.rolling(lookback).mean().shift(1)) / s.rolling(lookback).std().shift(1)


def build_overlay(df: pd.DataFrame, cfg: HedgeConfig) -> pd.DataFrame:
    """Return a frame with the signal, hedge sleeve, and overlaid daily return. Read-only on df."""
    book = df[cfg.book_col]
    up = df[cfg.up_factor] >= cfg.up_threshold
    volz = _zscore(df[cfg.vol_factor], cfg.vol_lookback)
    on = (up & (volz >= cfg.vol_z_threshold)).fillna(False)
    hedge_ret = PRODUCTS[cfg.product](df)
    rt = cfg.cost_bps / 1e4
    sleeve = np.where(on, cfg.weight * hedge_ret - rt, 0.0)
    out = pd.DataFrame(index=df.index)
    out["book_ret"] = book
    out["hedge_on"] = on
    out["hedge_instr_ret"] = hedge_ret
    out["sleeve_pnl"] = sleeve
    out["overlaid_ret"] = book + sleeve
    return out


def metrics(r: pd.Series) -> dict:
    r = r.dropna()
    if len(r) < 5:
        return dict(ann=np.nan, vol=np.nan, sharpe=np.nan, maxdd=np.nan, n=len(r))
    ann = r.mean() * 252
    vol = r.std() * np.sqrt(252)
    eq = (1 + r).cumprod()
    dd = (eq / eq.cummax() - 1).min()
    return dict(ann=ann, vol=vol, sharpe=(ann / vol if vol else np.nan), maxdd=dd, n=len(r))


def _window_row(ov: pd.DataFrame, mask: pd.Series, hedge_ret: pd.Series, w: float, rt: float) -> dict:
    m = mask & ov["book_ret"].notna()
    b = metrics(ov["book_ret"][m])
    h = metrics(ov["overlaid_ret"][m])
    on = ov["hedge_on"] & m
    k = int(on.sum())
    return dict(
        days=int(m.sum()), on=k, on_pct=100 * k / max(int(m.sum()), 1),
        book_sh=b["sharpe"], hed_sh=h["sharpe"], d_sh=h["sharpe"] - b["sharpe"],
        book_dd=b["maxdd"] * 100, d_dd=(h["maxdd"] - b["maxdd"]) * 100,
        on_book=ov["book_ret"][on].mean() * 100 if k else np.nan,
        paid=100 * (hedge_ret[on] > 0).mean() if k else np.nan,
        sleeve=ov["sleeve_pnl"][on].sum() * 100 if k else 0.0,
    )


def run(panel_path: Path = PANEL, cfg: HedgeConfig = None, out_prefix: Path = OUT_PREFIX) -> dict:
    cfg = cfg or HedgeConfig()
    df = pd.read_csv(panel_path, parse_dates=["date"]).set_index("date")
    ov = build_overlay(df, cfg)
    hedge_ret = ov["hedge_instr_ret"]; rt = cfg.cost_bps / 1e4

    windows = {
        "FULL": df.index >= df.index.min(),
        "COVID": df.index >= cfg.covid_start,
        "TRAIN(<oos)": df.index < cfg.oos_start,
        "OOS": df.index >= cfg.oos_start,
    }
    summary = {wn: _window_row(ov, m, hedge_ret, cfg.weight, rt) for wn, m in windows.items()}

    wf = {}
    for yr, _g in df.groupby(df.index.year):
        m = df.index.year == yr
        if (m & df[cfg.book_col].notna()).sum() < 20:
            continue
        wf[int(yr)] = _window_row(ov, pd.Series(m, index=df.index), hedge_ret, cfg.weight, rt)

    # ---- write artifacts ----
    out_prefix.parent.mkdir(parents=True, exist_ok=True)
    ov_out = ov.copy()
    ov_out.to_csv(f"{out_prefix}_daily.csv")
    _write_summary(f"{out_prefix}_summary.md", cfg, summary, wf, panel_path, df)
    return dict(config=asdict(cfg), summary=summary, walk_forward=wf)


def _fmt(row: dict) -> str:
    return ("days=%4d on=%3d (%4.1f%%) | bookSh %+.2f hedSh %+.2f dSh %+.2f | "
            "bookDD %.1f%% dDD %+.1f%% | onBook %+s%% SOXS+ %s%% sleeve %+.2f%%") % (
        row["days"], row["on"], row["on_pct"], row["book_sh"], row["hed_sh"], row["d_sh"],
        row["book_dd"], row["d_dd"],
        ("%.2f" % row["on_book"]) if row["on"] else "  na",
        ("%.0f" % row["paid"]) if row["on"] else "na", row["sleeve"])


def _write_summary(path, cfg, summary, wf, panel_path, df) -> None:
    L = []
    L.append("# Hedge overlay on model_v4 — up-shock + vol-surge 1-day hedge\n")
    L.append("Standalone overlay; **model_v4 is not modified**. Source panel: `%s` "
             "(%s to %s).\n" % (panel_path.name, df.index.min().date(), df.index.max().date()))
    L.append("## Rule (configurable in `HedgeConfig`)\n")
    L.append("```")
    L.append("if  %s >= %+.3f            (up-shock)" % (cfg.up_factor, cfg.up_threshold))
    L.append("AND z(%s, %dd) >= %.2f     (vol-surge supporting signal)" % (cfg.vol_factor, cfg.vol_lookback, cfg.vol_z_threshold))
    L.append("then BUY %s @ %.0f%% notional for 1 day (round-trip cost %.0fbp), exit next close."
             % (cfg.product, cfg.weight * 100, cfg.cost_bps))
    L.append("```")
    L.append("\nKey finding: **no single factor works alone** — a QQQ up-day by itself bounces; "
             "the edge is the *interaction* (up-shock while vol already elevated). Best supporting "
             "signal in the sensitivity sweep was 5-day realized-vol z (`spy_vol_trl_5d`).\n")
    L.append("## Window summary\n```")
    for wn, r in summary.items():
        L.append("%-11s %s" % (wn, _fmt(r)))
    L.append("```")
    L.append("\n## Yearly walk-forward\n```")
    L.append("%-6s %4s %4s | %7s %7s %7s | %7s %7s | %8s %6s %8s" % (
        "year", "days", "on", "bookSh", "hedSh", "dSh", "bookDD", "dDD", "onBook%", "paid%", "sleeve%"))
    npos = ntot = 0
    for yr, r in wf.items():
        if r["on"]:
            ntot += 1; npos += int(r["d_sh"] > 0)
        L.append("%-6d %4d %4d | %+7.2f %+7.2f %+7.2f | %6.1f%% %+6.1f%% | %8s %6s %+7.2f%%" % (
            yr, r["days"], r["on"], r["book_sh"], r["hed_sh"], r["d_sh"], r["book_dd"], r["d_dd"],
            ("%.2f" % r["on_book"]) if r["on"] else "na", ("%.0f" % r["paid"]) if r["on"] else "na", r["sleeve"]))
    L.append("```")
    L.append("\nYears with active hedge & ΔSharpe>0: **%d/%d**.\n" % (npos, ntot))
    L.append("## Caveats\n")
    L.append("- Edge concentrates in genuine vol-spike episodes (2018–2021); marginal in calm years, "
             "slightly negative in the 2022 grind-bear. It is a Sharpe-adder + single-day-blow softener, "
             "**not** an all-time-max-drawdown reducer.\n")
    L.append("- Decide-at-close / fill-next-close; sized small. Re-validate after any model/universe change.\n")
    Path(path).write_text("\n".join(L))


def _cli(argv=None):
    p = argparse.ArgumentParser(description="model_v4 up-shock+vol 1-day hedge overlay (standalone)")
    p.add_argument("--panel", default=str(PANEL))
    p.add_argument("--up", type=float, help="up-shock threshold (e.g. 0.02)")
    p.add_argument("--vol-z", type=float, help="vol z threshold (e.g. 1.0)")
    p.add_argument("--vol-factor", help="vol factor column (e.g. spy_vol_trl_5d)")
    p.add_argument("--lookback", type=int, help="vol z lookback (days)")
    p.add_argument("--product", choices=list(PRODUCTS), help="hedge instrument")
    p.add_argument("--weight", type=float, help="sleeve notional weight")
    a = p.parse_args(argv)
    cfg = HedgeConfig()
    for k_arg, k_cfg in [("up", "up_threshold"), ("vol_z", "vol_z_threshold"),
                         ("vol_factor", "vol_factor"), ("lookback", "vol_lookback"),
                         ("product", "product"), ("weight", "weight")]:
        v = getattr(a, k_arg)
        if v is not None:
            setattr(cfg, k_cfg, v)
    res = run(Path(a.panel), cfg)
    print("config:", res["config"])
    for wn, r in res["summary"].items():
        print("%-11s %s" % (wn, _fmt(r)))
    print("\nartifacts -> %s_summary.md , %s_daily.csv" % (OUT_PREFIX, OUT_PREFIX))


if __name__ == "__main__":
    _cli()
