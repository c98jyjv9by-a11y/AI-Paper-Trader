"""
ticker_experiments.py — Grouped ticker-specific assumptions vs buy-and-hold.

Central question: do ticker-aware signal/exit assumptions beat simply owning the
same universe — on a FAIR, exposure-adjusted basis? The headline test is the
capital-matched equal-weight benchmark (own the universe at the strategy's own
average exposure, rest in cash).

All results are IN-SAMPLE. Nothing is claimed superior until validated out-of-sample.
Group assumptions use broad behaviour buckets — no per-ticker parameter fitting.

Outputs (baseline config and live data/ are never touched):
    reports/strategy_experiments_ticker_overrides_<date>.md
    backtests/ticker_override_experiments_<date>.csv

Usage:
    python src/ticker_experiments.py --start 2025-01-01 --end 2026-06-12
"""
import argparse
import copy
import logging
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from backtest import compute_metrics, fetch_backtest_data, load_config, run_backtest
from diagnostics import (
    build_signal_panel,
    exposure_benchmark_capture,
    pnl_attribution,
    signal_predictiveness,
    ticker_level_diagnostics,
    group_to_tickers,
)
from experiments import _annualized, _sharpe
from logger import setup_logging

log = logging.getLogger(__name__)


# ─── Grouped override definitions (broad behaviour buckets, not fitted) ───────

GROUPS_V1: Dict[str, Dict[str, Any]] = {
    "semiconductors": {
        "tickers": ["NVDA", "AVGO", "AMD", "MU", "TSM", "ASML"],
        "stop_loss": 0.10, "take_profit": None, "trailing_stop": 0.15,
        "max_holding_days": 60, "max_position_pct": 0.045,
    },
    "mega_cap_growth": {
        "tickers": ["MSFT", "AAPL", "AMZN", "GOOGL", "META", "TSLA", "NFLX", "COST"],
        "stop_loss": 0.075, "take_profit": None, "trailing_stop": 0.12,
        "max_holding_days": 60, "max_position_pct": 0.04,
    },
    "software_cybersecurity": {
        "tickers": ["ORCL", "CRWD", "PANW"],
        "stop_loss": 0.075, "take_profit": 0.15, "trailing_stop": None,
        "max_holding_days": 45, "max_position_pct": 0.03,
    },
    "financial_crypto_beta": {
        "tickers": ["JPM", "BAC", "GS", "COIN"],
        "stop_loss": 0.10, "take_profit": None, "trailing_stop": 0.15,
        "max_holding_days": 45, "max_position_pct": 0.035,
    },
}


def _conservative_groups() -> Dict[str, Dict[str, Any]]:
    g = copy.deepcopy(GROUPS_V1)
    g["semiconductors"]["trailing_stop"] = 0.12
    g["mega_cap_growth"]["trailing_stop"] = 0.10
    g["financial_crypto_beta"]["trailing_stop"] = 0.12
    for spec in g.values():
        spec["max_position_pct"] = min(spec["max_position_pct"], 0.035)
    return g


def _aggressive_groups() -> Dict[str, Dict[str, Any]]:
    g = copy.deepcopy(GROUPS_V1)
    g["semiconductors"]["max_position_pct"] = 0.05
    g["semiconductors"]["trailing_stop"] = 0.18
    g["financial_crypto_beta"]["trailing_stop"] = 0.18
    g["semiconductors"]["max_holding_days"] = 75
    g["mega_cap_growth"]["max_holding_days"] = 75
    return g


# Per-group signal weights (broad behaviour buckets, not fitted): high-beta names
# lean harder on 20-day trend + volatility-adjusted momentum; steadier names keep
# more medium-term trend; volume confirmation kept only where it plausibly helps.
GROUP_SIGNAL_WEIGHTS: Dict[str, Dict[str, float]] = {
    "semiconductors":         {"return_5d": 0.20, "return_20d": 0.50, "vol_adj_mom_20d": 0.30},
    "mega_cap_growth":        {"return_5d": 0.25, "return_20d": 0.45, "vol_adj_mom_20d": 0.30},
    "software_cybersecurity": {"return_5d": 0.30, "return_20d": 0.40, "vol_ratio": 0.30},
    "financial_crypto_beta":  {"return_5d": 0.20, "return_20d": 0.40, "vol_adj_mom_20d": 0.40},
}


def _groups_signal_only() -> Dict[str, Dict[str, Any]]:
    """Groups carrying ONLY per-group signal_weights (default exits) — isolates the
    effect of ticker-specific *ranking* from exit/sizing changes."""
    return {name: {"tickers": list(GROUPS_V1[name]["tickers"]),
                   "signal_weights": GROUP_SIGNAL_WEIGHTS[name]}
            for name in GROUPS_V1}


def _groups_signals_plus_exits() -> Dict[str, Dict[str, Any]]:
    """v1 exit/sizing overrides AND per-group signal weights."""
    g = copy.deepcopy(GROUPS_V1)
    for name, spec in g.items():
        spec["signal_weights"] = GROUP_SIGNAL_WEIGHTS[name]
    return g


PROFILES: List[Tuple[str, List[Tuple[str, Any]]]] = [
    ("baseline", []),
    ("trailing_stop_baseline", [
        ("risk.take_profit", None), ("risk.trailing_stop", 0.15), ("risk.max_holding_days", 60),
    ]),
    ("grouped_ticker_overrides_v1", [("ticker_groups", GROUPS_V1)]),
    ("grouped_ticker_overrides_conservative", [("ticker_groups", _conservative_groups())]),
    ("grouped_ticker_overrides_aggressive", [("ticker_groups", _aggressive_groups())]),
    # Ticker-specific SIGNALS: per-group ranking weights (isolated, then stacked on exits).
    ("grouped_signal_weights_only", [("ticker_groups", _groups_signal_only())]),
    ("grouped_signals_plus_exits", [("ticker_groups", _groups_signals_plus_exits())]),
]


def _apply(baseline: Dict[str, Any], overrides: List[Tuple[str, Any]]) -> Dict[str, Any]:
    cfg = copy.deepcopy(baseline)
    for key, value in overrides:
        if "." in key:
            sec, k = key.split(".", 1)
            cfg.setdefault(sec, {})[k] = value
        else:
            cfg[key] = value
    return cfg


# ─── Benchmarks ───────────────────────────────────────────────────────────────


def _capital_matched(equity_df: pd.DataFrame, frac: float) -> Dict[str, Optional[float]]:
    """
    Equal-weight buy-and-hold of the universe at `frac` exposure, rest in cash.

    Built from the equity curve's equal_weight_cumulative_return: a portfolio that
    holds frac of capital in the EW basket has level_t = 1 + frac*ew_cum_t. We
    compute return, max drawdown and Sharpe from that scaled level series.
    """
    if equity_df.empty or "equal_weight_cumulative_return" not in equity_df.columns:
        return {"total_return": None, "max_drawdown": None, "sharpe": None, "annualized": None}
    ew = equity_df["equal_weight_cumulative_return"].astype(float)
    level = 1.0 + frac * ew
    total_return = float(level.iloc[-1] - 1.0)
    roll_max = level.cummax()
    max_dd = float(((level - roll_max) / roll_max).min())
    daily = level / level.shift(1) - 1.0
    daily = daily.dropna()
    sharpe = float(daily.mean() / daily.std() * np.sqrt(252)) if len(daily) > 1 and daily.std() > 0 else None
    return {
        "total_return": total_return,
        "max_drawdown": max_dd,
        "sharpe": sharpe,
        "annualized": _annualized(total_return, len(equity_df)),
    }


def _ew_sharpe(equity_df: pd.DataFrame) -> Optional[float]:
    return _capital_matched(equity_df, 1.0)["sharpe"]


def _calmar(annualized: Optional[float], max_dd: Optional[float]) -> Optional[float]:
    if annualized is None or max_dd is None or max_dd == 0:
        return None
    return annualized / abs(max_dd)


def _concentration_shares(pnl_by_ticker: Dict[str, float], pnl_by_group: Dict[str, float]) -> Dict[str, Optional[float]]:
    total = sum(pnl_by_ticker.values())
    top3 = sum(sorted(pnl_by_ticker.values(), reverse=True)[:3])
    semis = pnl_by_group.get("semiconductors", 0.0)
    if abs(total) < 1e-9:
        return {"top3_share": None, "semis_share": None}
    return {"top3_share": top3 / total, "semis_share": semis / total}


# ─── Run one profile ──────────────────────────────────────────────────────────


def run_profile(name: str, overrides: List[Tuple[str, Any]], baseline_config: Dict[str, Any],
                price_data: pd.DataFrame, start_date: date, end_date: date) -> Dict[str, Any]:
    cfg = _apply(baseline_config, overrides)
    sink: List[Dict[str, Any]] = []
    trades_df, equity_df, positions = run_backtest(cfg, price_data, start_date, end_date, signal_sink=sink)
    m = compute_metrics(trades_df, equity_df, positions, cfg, start_date, end_date)
    cap = exposure_benchmark_capture(equity_df)
    panel = build_signal_panel(price_data, sink)
    pred = signal_predictiveness(panel) if not panel.empty else {}
    pnl = pnl_attribution(trades_df, positions, cfg)

    trading_days = m.get("trading_days")
    months = max((end_date - start_date).days / 30.44, 1e-9)
    ann = _annualized(m.get("total_return"), trading_days)
    avg_exp = cap.get("avg_exposure")

    return {
        "name": name,
        "config": cfg,
        "metrics": m,
        "annualized": ann,
        "sharpe": _sharpe(equity_df),
        "calmar": _calmar(ann, m.get("max_drawdown")),
        "trades_per_month": (m.get("n_trades", 0) / months),
        "capture": cap,
        "predictiveness": pred,
        "pnl": pnl,
        "concentration": _concentration_shares(pnl.get("pnl_by_ticker", {}), pnl.get("pnl_by_group", {})),
        "capital_matched_avg": _capital_matched(equity_df, avg_exp if avg_exp is not None else 0.0),
        "capital_matched_75": _capital_matched(equity_df, 0.75),
        "equity_df": equity_df,
        "trades_df": trades_df,
        "positions": positions,
        "signal_history": sink,
    }


def run_ticker_experiments(baseline_config: Dict[str, Any], price_data: pd.DataFrame,
                           start_date: date, end_date: date) -> List[Dict[str, Any]]:
    return [run_profile(n, ov, baseline_config, price_data, start_date, end_date)
            for n, ov in PROFILES]


# ─── Formatting ───────────────────────────────────────────────────────────────


def _pct(v: Optional[float], d: str = "—") -> str:
    return d if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v * 100:+.2f}%"


def _num(v: Optional[float], d: str = "—") -> str:
    return d if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v:.2f}"


def _dollar(v: Optional[float], d: str = "—") -> str:
    return d if v is None or (isinstance(v, float) and np.isnan(v)) else f"${v:,.0f}"


def _yn(b: bool) -> str:
    return "✅ yes" if b else "❌ no"


def _by(results: List[Dict[str, Any]], name: str) -> Dict[str, Any]:
    return next(r for r in results if r["name"] == name)


# ─── Report ───────────────────────────────────────────────────────────────────


def render_report(results: List[Dict[str, Any]], run_date: date,
                  start_date: date, end_date: date, price_data: pd.DataFrame) -> str:
    base = _by(results, "baseline")
    bm = base["metrics"]
    trading_days = bm.get("trading_days")
    ew_ret = bm.get("equal_weight_return")
    ew_dd = bm.get("equal_weight_max_drawdown")
    ew_sharpe = _ew_sharpe(base["equity_df"])
    start_val = bm.get("starting_value", 100000.0)

    lines: List[str] = [
        "# Strategy Experiments — Grouped Ticker Overrides",
        f"**Period:** {start_date} → {end_date}  |  **Generated:** {run_date.isoformat()}",
        "",
        "> ⚠️ **IN-SAMPLE only**, one historical window. No profile is claimed superior. "
        "Group assumptions are broad behaviour buckets, not fitted parameters. Validate "
        "out-of-sample before acting.",
        "",
        "---",
        "",
    ]

    # ── Pass/Fail summary ─────────────────────────────────────────────────────
    active = [r for r in results if r["name"] != "baseline"]
    lines += [
        "## Strategy vs Buy-and-Hold Test",
        "",
        "_Does each active strategy beat passively owning the same universe — including on "
        "an exposure-adjusted basis? ✅/❌ per profile._",
        "",
        "| Test | " + " | ".join(r["name"] for r in results) + " |",
        "|------|" + "|".join(["---"] * len(results)) + "|",
    ]

    def _row(label: str, fn) -> str:
        cells = " | ".join("✅" if fn(r) else "❌" for r in results)
        return f"| {label} | {cells} |"

    lines += [
        _row("Beat SPY", lambda r: (r["metrics"].get("total_return") or -9) > (bm.get("spy_return") or 9)),
        _row("Beat QQQ", lambda r: (r["metrics"].get("total_return") or -9) > (bm.get("qqq_return") or 9)),
        _row("Beat equal-weight BH", lambda r: (r["metrics"].get("total_return") or -9) > (ew_ret or 9)),
        _row("Beat capital-matched EW", lambda r: (r["metrics"].get("total_return") or -9) >
             ((r["capital_matched_avg"]["total_return"]) if r["capital_matched_avg"]["total_return"] is not None else 9)),
        _row("Lower DD than EW BH", lambda r: abs(r["metrics"].get("max_drawdown") or 9) < abs(ew_dd or 0)),
        _row("Higher Sharpe than EW BH", lambda r: (r["sharpe"] or -9) > (ew_sharpe or 9)),
        _row("Positive quintile spread", lambda r: (r["predictiveness"].get("top_minus_bottom_spread", {}).get("spread_20d") or -9) > 0),
        "",
        f"_Equal-weight BH of the universe: return {_pct(ew_ret)}, max DD {_pct(ew_dd)}, "
        f"Sharpe {_num(ew_sharpe)}. Capital-matched targets each profile's own average exposure._",
        "",
    ]

    # ── Returns & Risk + benchmarks ───────────────────────────────────────────
    lines += [
        "## Returns & Risk",
        "",
        "| Profile | Ending Bal | Total Ret | Annualized | Max DD | Sharpe | Calmar | Avg Exp | Peak Exp | β QQQ | ρ QQQ | Up-cap | Down-cap |",
        "|---------|-----------|-----------|------------|--------|--------|--------|---------|----------|-------|-------|--------|----------|",
    ]
    for r in results:
        m = r["metrics"]; c = r["capture"]
        lines.append(
            f"| {r['name']} | {_dollar(m.get('ending_value'))} | {_pct(m.get('total_return'))} "
            f"| {_pct(r['annualized'])} | {_pct(m.get('max_drawdown'))} | {_num(r['sharpe'])} "
            f"| {_num(r['calmar'])} | {_pct(c.get('avg_exposure'))} | {_pct(c.get('max_exposure'))} "
            f"| {_num(c.get('beta_qqq'))} | {_num(c.get('corr_qqq'))} | {_num(c.get('up_capture_qqq'))} "
            f"| {_num(c.get('down_capture_qqq'))} |"
        )
    # Benchmark rows
    def _bench_row(label, ret, dd, sharpe):
        ann = _annualized(ret, trading_days)
        bal = start_val * (1 + ret) if ret is not None else None
        return (f"| _{label}_ | {_dollar(bal)} | {_pct(ret)} | {_pct(ann)} | {_pct(dd)} "
                f"| {_num(sharpe)} | {_num(_calmar(ann, dd))} | — | — | — | — | — | — |")
    lines += [
        _bench_row("SPY buy & hold", bm.get("spy_return"), bm.get("spy_max_drawdown"), None),
        _bench_row("QQQ buy & hold", bm.get("qqq_return"), bm.get("qqq_max_drawdown"), None),
        _bench_row("Equal-weight BH (100%)", ew_ret, ew_dd, ew_sharpe),
    ]
    cm75 = base["capital_matched_75"]
    lines.append(_bench_row("EW BH 75% / 25% cash", cm75["total_return"], cm75["max_drawdown"], cm75["sharpe"]))
    for r in active:
        cma = r["capital_matched_avg"]
        exp = r["capture"].get("avg_exposure")
        lines.append(_bench_row(
            f"EW BH capital-matched to {r['name']} ({_pct(exp)})",
            cma["total_return"], cma["max_drawdown"], cma["sharpe"]))
    lines.append("")

    # ── Trading activity ──────────────────────────────────────────────────────
    lines += [
        "## Trading Activity",
        "",
        "| Profile | Trades | / month | Win Rate | Avg Win | Avg Loss | PF | Avg Hold | Slippage | Largest Win | Largest Loss |",
        "|---------|--------|---------|----------|---------|----------|----|----------|----------|-------------|--------------|",
    ]
    for r in results:
        m = r["metrics"]; pf = m.get("profit_factor")
        lines.append(
            f"| {r['name']} | {m.get('n_trades', 0)} | {_num(r['trades_per_month'])} "
            f"| {_pct(m.get('win_rate'))} | {_dollar(m.get('avg_win'))} | {_dollar(m.get('avg_loss'))} "
            f"| {_num(pf) if pf is not None else '—'} | {_num(m.get('avg_holding_days'))} "
            f"| {_dollar(m.get('total_slippage_cost'))} | {_dollar(m.get('largest_winner'))} "
            f"| {_dollar(m.get('largest_loser'))} |"
        )
    lines.append("")

    # ── Signal effectiveness ──────────────────────────────────────────────────
    lines += [
        "## Signal Effectiveness",
        "",
        "_Does composite ranking actually sort winners from losers? Exit/sizing-only "
        "profiles share the baseline's ranking (identical spreads); the per-group "
        "`signal_weights` profiles re-rank and should move the spread if they help._",
        "",
        "| Profile | corr 5d | corr 10d | corr 20d | Spread 5d | Spread 10d | Spread 20d |",
        "|---------|---------|----------|----------|-----------|------------|------------|",
    ]
    for r in results:
        p = r["predictiveness"]
        cc = p.get("correlations", {}).get("composite_score", {})
        sp = p.get("top_minus_bottom_spread", {})
        lines.append(
            f"| {r['name']} | {_num(cc.get('fwd_5d'))} | {_num(cc.get('fwd_10d'))} | {_num(cc.get('fwd_20d'))} "
            f"| {_pct(sp.get('spread_5d'))} | {_pct(sp.get('spread_10d'))} | {_pct(sp.get('spread_20d'))} |"
        )
    # quintile profile for baseline (representative of shared ranking)
    qp = base["predictiveness"].get("quintile_profile", [])
    if qp:
        lines += [
            "",
            "**Baseline avg forward return / win rate by composite quintile (5 = top):**",
            "",
            "| Quintile | Avg fwd 20d | Win 20d |",
            "|----------|-------------|---------|",
        ]
        for q in qp:
            lines.append(f"| Q{q['quintile']} | {_pct(q.get('avg_fwd_20d'))} | {_pct(q.get('win_rate_20d'))} |")
    lines.append("")

    # ── P&L attribution ───────────────────────────────────────────────────────
    lines += ["## P&L Attribution", ""]
    all_groups = sorted({g for r in results for g in r["pnl"]["pnl_by_group"]})
    if all_groups:
        lines += ["| Profile | " + " | ".join(all_groups) + " | Top-3 share | Semis share |",
                  "|---------|" + "|".join(["---"] * (len(all_groups) + 2)) + "|"]
        for r in results:
            cells = " | ".join(_dollar(r["pnl"]["pnl_by_group"].get(g)) for g in all_groups)
            conc = r["concentration"]
            lines.append(f"| {r['name']} | {cells} | {_pct(conc['top3_share'])} | {_pct(conc['semis_share'])} |")
        lines.append("")
    for r in results:
        top = ", ".join(f"`{t}` {_dollar(v)}" for t, v in r["pnl"]["top5"][:5]) or "—"
        bot = ", ".join(f"`{t}` {_dollar(v)}" for t, v in r["pnl"]["bottom5"][:5]) or "—"
        lines.append(f"- **{r['name']}** — top: {top}")
        lines.append(f"  worst: {bot}")
    lines.append("")
    lines.append("_(Full per-ticker P&L in the CSV.)_")
    lines.append("")

    # ── Ticker-level diagnostics (baseline — justifies group assumptions) ─────
    tdiag = ticker_level_diagnostics(base["trades_df"], base["positions"], price_data)
    if tdiag:
        lines += [
            "## Ticker-Level Behaviour (baseline — basis for group assumptions)",
            "",
            "_MFE = peak unrealized gain; MAE = worst unrealized drawdown; giveback = MFE − realized._",
            "",
            "| Ticker | Trades | Total P&L | Win% | PF | Avg Hold | Avg MFE | Med MFE | Avg MAE | Med MAE | Avg Giveback | SL/TP/Trail/Hold | Stop→re-entry |",
            "|--------|--------|-----------|------|----|----------|---------|---------|---------|---------|--------------|------------------|---------------|",
        ]
        for d in sorted(tdiag, key=lambda x: x["total_pnl"], reverse=True):
            pf = d["profit_factor"]
            lines.append(
                f"| {d['ticker']} | {d['trades']} | {_dollar(d['total_pnl'])} | {_pct(d['win_rate'])} "
                f"| {_num(pf) if pf is not None else '—'} | {_num(d['avg_holding_days'])} "
                f"| {_pct(d['avg_mfe'])} | {_pct(d['median_mfe'])} | {_pct(d['avg_mae'])} | {_pct(d['median_mae'])} "
                f"| {_pct(d['avg_giveback'])} "
                f"| {d['exits_stop_loss']}/{d['exits_take_profit']}/{d['exits_trailing_stop']}/{d['exits_max_holding']} "
                f"| {d['stop_then_reentry_5d']} |"
            )
        lines.append("")

    # ── Interpretation ────────────────────────────────────────────────────────
    lines += ["## Interpretation", ""]
    for note in _interpretation(results, ew_ret, ew_dd, ew_sharpe):
        lines += [note, ""]

    return "\n".join(lines)


def _interpretation(results: List[Dict[str, Any]], ew_ret, ew_dd, ew_sharpe) -> List[str]:
    base = _by(results, "baseline")
    notes: List[str] = []
    active = [r for r in results if r["name"] != "baseline"]

    # Did ticker-specific assumptions improve returns?
    grouped = [r for r in active if r["name"].startswith("grouped")]
    if grouped:
        best_g = max(grouped, key=lambda r: r["metrics"].get("total_return") or -9)
        d_ret = (best_g["metrics"].get("total_return") or 0) - (base["metrics"].get("total_return") or 0)
        notes.append(
            f"**Ticker-specific assumptions:** best grouped profile is `{best_g['name']}` "
            f"({_pct(best_g['metrics'].get('total_return'))}, {_pct(d_ret)} vs baseline). Grouped exits "
            "mainly widen winner-capture and lengthen holds; they change *exits/sizing*, not the ranking."
        )

    # Beat buy-and-hold on a fair basis?
    beat_cm = [r for r in active
               if r["capital_matched_avg"]["total_return"] is not None
               and (r["metrics"].get("total_return") or -9) > r["capital_matched_avg"]["total_return"]]
    if beat_cm:
        notes.append(
            "**Fair (exposure-adjusted) test:** " +
            ", ".join(f"`{r['name']}`" for r in beat_cm) +
            " beat their **capital-matched** equal-weight benchmark — i.e. the signal/exit rules added "
            "value beyond owning the same names at the same average exposure."
        )
    else:
        notes.append(
            "**Fair (exposure-adjusted) test:** no active profile beat its capital-matched equal-weight "
            "benchmark. At equal exposure, simply owning the universe did as well or better — the active "
            "selection is **not** clearly adding value here; most of any return difference is exposure timing."
        )

    # Did ticker-specific SIGNAL weights improve ranking?
    base_spread = base["predictiveness"].get("top_minus_bottom_spread", {}).get("spread_20d")
    sig_profiles = [r for r in active if "signal" in r["name"]]
    if sig_profiles and base_spread is not None:
        improved = [r for r in sig_profiles
                    if (r["predictiveness"].get("top_minus_bottom_spread", {}).get("spread_20d") or -9) > base_spread]
        if improved:
            notes.append(
                "**Ticker-specific signal weights:** " +
                ", ".join(f"`{r['name']}`" for r in improved) +
                f" widened the 20d quintile spread beyond baseline ({_pct(base_spread)}) — per-group "
                "ranking sorted winners from losers better in-sample. Promising but fragile; confirm OOS."
            )
        else:
            notes.append(
                f"**Ticker-specific signal weights:** did **not** widen the 20d quintile spread beyond "
                f"baseline ({_pct(base_spread)}). Per-group ranking did not improve cross-sectional selection "
                "here, so the universe-wide signal is no worse than group-specific weighting."
            )

    # Signal alpha present?
    spread = base["predictiveness"].get("top_minus_bottom_spread", {}).get("spread_20d")
    if spread is not None and spread <= 0:
        notes.append(
            f"**Signal alpha:** the 20d top-minus-bottom quintile spread is {_pct(spread)} (≤ 0), so higher-ranked "
            "names did **not** clearly outperform lower-ranked ones. The active strategy is not demonstrating "
            "signal alpha, even where total return improves — gains are coming from exits/exposure, not ranking."
        )
    else:
        notes.append(
            f"**Signal alpha:** the 20d quintile spread is {_pct(spread)} (> 0), weak but positive — higher-ranked "
            "names slightly outperformed. Treat as fragile, not established edge."
        )

    # Concentration / overfitting
    most_conc = max(active, key=lambda r: abs(r["concentration"]["top3_share"] or 0))
    notes.append(
        f"**Concentration / overfitting:** P&L is concentrated — `{most_conc['name']}` draws "
        f"{_pct(most_conc['concentration']['top3_share'])} of net P&L from its top 3 names and "
        f"{_pct(most_conc['concentration']['semis_share'])} from semiconductors. Edge that lives in a few "
        "names on one window is a classic overfitting risk; prefer broad-based results."
    )

    notes.append(
        "**Out-of-sample next:** re-run the grouped profiles on a disjoint period (and ideally a different "
        "universe slice). Watch whether (a) they still beat the capital-matched benchmark and (b) the quintile "
        "spread stays positive. Until then, treat every ranking here as in-sample and provisional."
    )
    return notes


# ─── CSV ──────────────────────────────────────────────────────────────────────


def experiments_csv(results: List[Dict[str, Any]]) -> pd.DataFrame:
    all_tickers = sorted({t for r in results for t in r["pnl"]["pnl_by_ticker"]})
    all_groups = sorted({g for r in results for g in r["pnl"]["pnl_by_group"]})
    rows = []
    for r in results:
        m = r["metrics"]; c = r["capture"]; sp = r["predictiveness"].get("top_minus_bottom_spread", {})
        cc = r["predictiveness"].get("correlations", {}).get("composite_score", {})
        row = {
            "profile": r["name"],
            "ending_value": m.get("ending_value"),
            "total_return": m.get("total_return"),
            "annualized_return": r["annualized"],
            "max_drawdown": m.get("max_drawdown"),
            "sharpe": r["sharpe"],
            "calmar": r["calmar"],
            "avg_exposure": c.get("avg_exposure"),
            "peak_exposure": c.get("max_exposure"),
            "beta_qqq": c.get("beta_qqq"),
            "corr_qqq": c.get("corr_qqq"),
            "up_capture_qqq": c.get("up_capture_qqq"),
            "down_capture_qqq": c.get("down_capture_qqq"),
            "n_trades": m.get("n_trades"),
            "trades_per_month": r["trades_per_month"],
            "win_rate": m.get("win_rate"),
            "avg_win": m.get("avg_win"),
            "avg_loss": m.get("avg_loss"),
            "profit_factor": m.get("profit_factor"),
            "avg_holding_days": m.get("avg_holding_days"),
            "total_slippage_cost": m.get("total_slippage_cost"),
            "largest_winner": m.get("largest_winner"),
            "largest_loser": m.get("largest_loser"),
            "corr_composite_fwd5d": cc.get("fwd_5d"),
            "corr_composite_fwd10d": cc.get("fwd_10d"),
            "corr_composite_fwd20d": cc.get("fwd_20d"),
            "spread_20d": sp.get("spread_20d"),
            "capital_matched_avg_return": r["capital_matched_avg"]["total_return"],
            "capital_matched_75_return": r["capital_matched_75"]["total_return"],
            "top3_pnl_share": r["concentration"]["top3_share"],
            "semis_pnl_share": r["concentration"]["semis_share"],
        }
        for g in all_groups:
            row[f"pnl_group_{g}"] = r["pnl"]["pnl_by_group"].get(g)
        for t in all_tickers:
            row[f"pnl_{t}"] = r["pnl"]["pnl_by_ticker"].get(t)
        rows.append(row)
    return pd.DataFrame(rows)


# ─── Output / CLI ─────────────────────────────────────────────────────────────


def save_outputs(report: str, csv_df: pd.DataFrame, reports_dir: Path,
                 backtests_dir: Path, run_date: date) -> Dict[str, str]:
    reports_dir.mkdir(parents=True, exist_ok=True)
    backtests_dir.mkdir(parents=True, exist_ok=True)
    tag = run_date.isoformat()
    md_path = reports_dir / f"strategy_experiments_ticker_overrides_{tag}.md"
    md_path.write_text(report)
    csv_path = backtests_dir / f"ticker_override_experiments_{tag}.csv"
    csv_df.to_csv(csv_path, index=False)
    return {"report": str(md_path), "csv": str(csv_path)}


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="AI Paper Trader — Grouped Ticker Override Experiments")
    p.add_argument("--start", required=True, metavar="YYYY-MM-DD")
    p.add_argument("--end", required=True, metavar="YYYY-MM-DD")
    return p.parse_args()


def run(start_date: date, end_date: date) -> Dict[str, str]:
    """Run the grouped ticker-override experiments and write outputs."""
    setup_logging()
    run_date = date.today()
    root = Path(__file__).parent.parent
    config = load_config(root / "config")

    log.info("=== Grouped Ticker Override Experiments ===")
    price_data = fetch_backtest_data(config["tickers"], start_date, end_date)

    results = run_ticker_experiments(config, price_data, start_date, end_date)
    report = render_report(results, run_date, start_date, end_date, price_data)
    csv_df = experiments_csv(results)
    paths = save_outputs(report, csv_df, root / "reports", root / "backtests", run_date)

    print()
    for r in results:
        cm = r["capital_matched_avg"]["total_return"]
        beat = "" if cm is None else ("  (beats capital-matched)" if (r["metrics"].get("total_return") or -9) > cm else "  (trails capital-matched)")
        print(f"  {r['name']:<42} total {_pct(r['metrics'].get('total_return'))}{beat}")
    print()
    print(f"  Report : {paths['report']}")
    print(f"  CSV    : {paths['csv']}")
    print("  NOTE: in-sample only — validate out-of-sample before acting.")
    print()
    return paths


def main() -> None:
    args = _parse_args()
    try:
        start_date = date.fromisoformat(args.start)
        end_date = date.fromisoformat(args.end)
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)
    if end_date <= start_date:
        print("Error: --end must be after --start")
        sys.exit(1)
    run(start_date, end_date)


if __name__ == "__main__":
    main()
