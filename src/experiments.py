"""
experiments.py — Named strategy experiments for the AI Paper Trader backtester.

Runs a fixed set of strategy *profiles* (config overrides on the current baseline)
over the same period and data, then writes a single comparison report + CSV to
backtests/. Profiles are deep-copied overrides — the baseline strategy.yaml and the
live paper-trading state (data/) are never modified.

All results are IN-SAMPLE. Nothing here selects a "winner"; out-of-sample testing
is required before trusting any profile.

Usage:
    python src/experiments.py --start 2025-01-01 --end 2026-06-12
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

from backtest import (
    compute_metrics,
    fetch_backtest_data,
    load_config,
    run_backtest,
)
from diagnostics import build_signal_panel, pnl_attribution, signal_predictiveness
from logger import setup_logging

log = logging.getLogger(__name__)


# ─── Profile definitions ──────────────────────────────────────────────────────
# Each profile is a list of (dotted_config_path, value) overrides on the baseline.
# "baseline" applies no overrides and is the comparison anchor.

PROFILES: List[Tuple[str, List[Tuple[str, Any]]]] = [
    ("baseline", []),
    ("trend_reweighted", [
        ("signals.weights", {"return_1d": 0.00, "return_5d": 0.25, "return_20d": 0.55, "vol_ratio": 0.20}),
    ]),
    ("trend_reweighted_aggressive", [
        ("signals.weights", {"return_1d": 0.00, "return_5d": 0.20, "return_20d": 0.70, "vol_ratio": 0.10}),
    ]),
    ("score_weighted_sizing", [
        ("portfolio.sizing_mode", "score_weighted"),
        ("portfolio.min_position_pct", 0.02),
        ("portfolio.max_position_pct", 0.05),
    ]),
    ("higher_take_profit", [
        ("risk.take_profit", 0.15),
        ("risk.max_holding_days", 60),
    ]),
    ("high_take_profit", [
        ("risk.take_profit", 0.20),
        ("risk.max_holding_days", 60),
    ]),
    ("no_fixed_take_profit_trailing_stop", [
        ("risk.take_profit", None),
        ("risk.trailing_stop", 0.10),
        ("risk.max_holding_days", 60),
    ]),
    ("no_fixed_take_profit_wide_trailing_stop", [
        ("risk.take_profit", None),
        ("risk.trailing_stop", 0.15),
        ("risk.max_holding_days", 60),
    ]),
    # ── Diagnostics-driven candidates (signal quality / regime / churn) ──────
    ("vol_adjusted_momentum", [
        # Replace the near-useless volume input with return-per-unit-of-risk.
        ("signals.weights", {"return_1d": 0.00, "return_5d": 0.20, "return_20d": 0.30, "vol_adj_mom_20d": 0.50}),
    ]),
    ("qqq_trend_filter", [
        # Only enter while QQQ is above its 50-day moving average (sit out downtrends).
        ("entry_filters.qqq_above_ma", 50),
    ]),
    ("stop_cooldown_5d", [
        # No re-entry into a name for 5 trading days after it stops out (reduce churn).
        ("risk.stop_cooldown_days", 5),
    ]),
    ("regime_voladj_higher_tp", [
        # Stacked best-guess: regime filter + vol-adjusted ranker + looser take-profit.
        ("entry_filters.qqq_above_ma", 50),
        ("signals.weights", {"return_1d": 0.00, "return_5d": 0.20, "return_20d": 0.30, "vol_adj_mom_20d": 0.50}),
        ("risk.take_profit", 0.15),
        ("risk.max_holding_days", 60),
    ]),
]


def _apply_overrides(baseline: Dict[str, Any], overrides: List[Tuple[str, Any]]) -> Dict[str, Any]:
    cfg = copy.deepcopy(baseline)
    for dotted, value in overrides:
        section, key = dotted.split(".", 1)
        cfg.setdefault(section, {})
        cfg[section][key] = value
    return cfg


# ─── Per-profile metric helpers ───────────────────────────────────────────────


def _annualized(total_return: Optional[float], trading_days: Optional[int]) -> Optional[float]:
    if total_return is None or not trading_days or trading_days <= 0:
        return None
    base = 1.0 + total_return
    if base <= 0:
        return -1.0
    years = trading_days / 252.0
    return base ** (1.0 / years) - 1.0 if years > 0 else None


def _sharpe(equity_df: pd.DataFrame) -> Optional[float]:
    if equity_df.empty or "daily_return" not in equity_df.columns:
        return None
    d = equity_df["daily_return"].dropna()
    if len(d) < 2 or d.std() == 0:
        return None
    return float(d.mean() / d.std() * np.sqrt(252))


def _exit_reason_counts(trades_df: pd.DataFrame) -> Dict[str, int]:
    counts = {"take_profit": 0, "stop_loss": 0, "trailing_stop": 0, "max_holding_period": 0}
    if trades_df.empty:
        return counts
    sells = trades_df[trades_df["action"] == "SELL"]
    for reason in sells["reason"].astype(str):
        for key in counts:
            if key in reason:
                counts[key] += 1
    return counts


def _gave_back_count(trades_df: pd.DataFrame, peak_threshold: float = 0.05) -> int:
    """Closed trades that reached >= +peak_threshold unrealized but exited at a loss."""
    if trades_df.empty:
        return 0
    sells = trades_df[trades_df["action"] == "SELL"]
    if "highest_price" not in sells.columns or "entry_price" not in sells.columns:
        return 0
    cnt = 0
    for _, r in sells.iterrows():
        hp, ep, pnl = r.get("highest_price"), r.get("entry_price"), r.get("realized_pnl")
        if pd.notna(hp) and pd.notna(ep) and ep > 0 and pd.notna(pnl):
            if (hp / ep - 1) >= peak_threshold and pnl < 0:
                cnt += 1
    return cnt


def _concentration(pnl_by_ticker: Dict[str, float]) -> Optional[float]:
    """Share of total absolute P&L held by the single largest-magnitude contributor."""
    if not pnl_by_ticker:
        return None
    mags = [abs(v) for v in pnl_by_ticker.values()]
    total = sum(mags)
    return (max(mags) / total) if total > 0 else None


# ─── Run one profile ──────────────────────────────────────────────────────────


def run_profile(
    name: str,
    overrides: List[Tuple[str, Any]],
    baseline_config: Dict[str, Any],
    price_data: pd.DataFrame,
    start_date: date,
    end_date: date,
) -> Dict[str, Any]:
    cfg = _apply_overrides(baseline_config, overrides)
    signal_sink: List[Dict[str, Any]] = []
    trades_df, equity_df, positions = run_backtest(
        cfg, price_data, start_date, end_date, signal_sink=signal_sink
    )
    m = compute_metrics(trades_df, equity_df, positions, cfg, start_date, end_date)

    panel = build_signal_panel(price_data, signal_sink)
    spread = signal_predictiveness(panel).get("top_minus_bottom_spread", {}) if not panel.empty else {}
    pnl = pnl_attribution(trades_df, positions, cfg)

    trading_days = m.get("trading_days")
    months = max((end_date - start_date).days / 30.44, 1e-9)

    return {
        "name": name,
        "metrics": m,
        "annualized_return": _annualized(m.get("total_return"), trading_days),
        "sharpe": _sharpe(equity_df),
        "trades_per_month": (m.get("n_trades", 0) / months),
        "exit_counts": _exit_reason_counts(trades_df),
        "gave_back": _gave_back_count(trades_df),
        "spread": spread,
        "pnl_by_ticker": pnl.get("pnl_by_ticker", {}),
        "pnl_by_group": pnl.get("pnl_by_group", {}),
        "concentration": _concentration(pnl.get("pnl_by_ticker", {})),
        "top5": pnl.get("top5", []),
        "bottom5": pnl.get("bottom5", []),
    }


def run_experiments(
    baseline_config: Dict[str, Any],
    price_data: pd.DataFrame,
    start_date: date,
    end_date: date,
) -> List[Dict[str, Any]]:
    results = []
    for name, overrides in PROFILES:
        log.info("Experiment profile: %s", name)
        results.append(run_profile(name, overrides, baseline_config, price_data, start_date, end_date))
    return results


# ─── Formatting helpers ───────────────────────────────────────────────────────


def _pct(v: Optional[float], d: str = "—") -> str:
    return d if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v * 100:+.2f}%"


def _num(v: Optional[float], d: str = "—") -> str:
    return d if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v:.2f}"


def _dollar(v: Optional[float], d: str = "—") -> str:
    return d if v is None or (isinstance(v, float) and np.isnan(v)) else f"${v:,.0f}"


def _by(results: List[Dict[str, Any]], name: str) -> Optional[Dict[str, Any]]:
    return next((r for r in results if r["name"] == name), None)


# ─── Interpretation (data-driven, hedged, in-sample) ──────────────────────────


def _interpretation(results: List[Dict[str, Any]]) -> List[str]:
    base = _by(results, "baseline")
    if base is None:
        return ["_Baseline missing — cannot interpret._"]
    b_ret = base["metrics"].get("total_return") or 0.0
    b_dd = base["metrics"].get("max_drawdown") or 0.0
    b_spread = base["spread"].get("spread_20d")
    notes: List[str] = []

    def ret(name: str) -> Optional[float]:
        r = _by(results, name)
        return r["metrics"].get("total_return") if r else None

    def spread20(name: str) -> Optional[float]:
        r = _by(results, name)
        return r["spread"].get("spread_20d") if r else None

    # 1. Trend reweighting / signal quality
    tr, tra = spread20("trend_reweighted"), spread20("trend_reweighted_aggressive")
    if b_spread is not None and (tr is not None or tra is not None):
        better = [n for n, s in [("trend_reweighted", tr), ("trend_reweighted_aggressive", tra)]
                  if s is not None and s > b_spread]
        if better:
            notes.append(
                f"**Trend reweighting:** raised the top-minus-bottom 20d quintile spread above "
                f"baseline ({_pct(b_spread)}) for {', '.join('`'+n+'`' for n in better)} — i.e. it "
                "improved cross-sectional *signal separation* in-sample, not just headline return."
            )
        else:
            notes.append(
                f"**Trend reweighting:** did **not** widen the 20d quintile spread beyond baseline "
                f"({_pct(b_spread)}); any return change came from exposure/timing, not better ranking."
            )

    # 2. Score-weighted sizing
    sw = _by(results, "score_weighted_sizing")
    if sw:
        d_ret = (sw["metrics"].get("total_return") or 0.0) - b_ret
        d_dd = (sw["metrics"].get("max_drawdown") or 0.0) - b_dd
        conc = sw.get("concentration")
        notes.append(
            f"**Score-weighted sizing:** return moved {_pct(d_ret)} vs baseline while max drawdown "
            f"moved {_pct(d_dd)} (more negative = worse) and the single-name P&L concentration is "
            f"{_pct(conc)}. If return rose mainly alongside higher concentration/drawdown, that is "
            "added **risk**, not added skill."
        )

    # 3. Higher take-profit / winner capture
    for name in ("higher_take_profit", "high_take_profit"):
        r = _by(results, name)
        if not r:
            continue
        d_ret = (r["metrics"].get("total_return") or 0.0) - b_ret
        d_aw = (r["metrics"].get("avg_win") or 0.0) - (base["metrics"].get("avg_win") or 0.0)
        notes.append(
            f"**{name}:** return {_pct(d_ret)} vs baseline, average win changed {_dollar(d_aw)}, "
            f"largest winner {_dollar(r['metrics'].get('largest_winner'))}, "
            f"gave-back trades {r['gave_back']} (baseline {base['gave_back']}). Higher avg/largest "
            "win with fewer give-backs ⇒ the old take-profit was clipping winners early."
        )

    # 4. Trailing stops vs fixed take-profit
    for name in ("no_fixed_take_profit_trailing_stop", "no_fixed_take_profit_wide_trailing_stop"):
        r = _by(results, name)
        if not r:
            continue
        d_ret = (r["metrics"].get("total_return") or 0.0) - b_ret
        d_dd = (r["metrics"].get("max_drawdown") or 0.0) - b_dd
        notes.append(
            f"**{name}:** return {_pct(d_ret)} and max drawdown {_pct(d_dd)} vs baseline, with "
            f"{r['exit_counts'].get('trailing_stop', 0)} trailing-stop exits. Better return *and* "
            "no worse drawdown would favour letting winners run; better return with deeper drawdown "
            "is just more risk."
        )

    # 5. Source of any improvement + 6. overfitting flag
    best = max(results, key=lambda r: (r["metrics"].get("total_return") or -9))
    if best["name"] != "baseline":
        conc = best.get("concentration")
        flag = ""
        if conc is not None and conc > 0.5:
            flag = (f" ⚠️ Its P&L is highly concentrated (top name = {_pct(conc)} of total |P&L|), "
                    "so the in-sample edge may be one or two lucky names — a classic overfitting risk.")
        notes.append(
            f"**Source / overfitting check:** the highest in-sample return is `{best['name']}` "
            f"({_pct(best['metrics'].get('total_return'))}).{flag} Treat ranking by in-sample return "
            "with suspicion — prefer profiles that improve the quintile spread *and* hold up across "
            "tickers/groups."
        )

    notes.append(
        "**All figures above are in-sample.** No profile is recommended as superior; differences of "
        "this size are well within noise for a single historical window. Validate any promising "
        "profile on a separate out-of-sample period before acting."
    )
    return notes


# ─── Rendering ────────────────────────────────────────────────────────────────


def render_experiments_md(results: List[Dict[str, Any]], run_date: date,
                          start_date: date, end_date: date) -> str:
    base = _by(results, "baseline")
    bm = base["metrics"] if base else {}
    trading_days = bm.get("trading_days")

    lines: List[str] = [
        "# AI Paper Trader — Strategy Experiments",
        f"**Period:** {start_date} → {end_date}  |  **Generated:** {run_date.isoformat()}",
        "",
        "> ⚠️ **All results are IN-SAMPLE** on a single historical window. No profile is claimed "
        "superior. Validate out-of-sample before trusting any of these.",
        "",
        "---",
        "",
        "## Returns & Risk",
        "",
        "| Profile | Total Return | Annualized | Max DD | Sharpe | vs SPY | vs QQQ |",
        "|---------|--------------|------------|--------|--------|--------|--------|",
    ]
    for r in results:
        m = r["metrics"]
        lines.append(
            f"| {r['name']} | {_pct(m.get('total_return'))} | {_pct(r['annualized_return'])} "
            f"| {_pct(m.get('max_drawdown'))} | {_num(r['sharpe'])} "
            f"| {_pct(m.get('excess_vs_spy'))} | {_pct(m.get('excess_vs_qqq'))} |"
        )
    # Benchmark rows
    for label, rkey, ddkey in [
        ("SPY (buy & hold)", "spy_return", "spy_max_drawdown"),
        ("QQQ (buy & hold)", "qqq_return", "qqq_max_drawdown"),
        ("Equal-Wt Hold", "equal_weight_return", "equal_weight_max_drawdown"),
    ]:
        lines.append(
            f"| _{label}_ | {_pct(bm.get(rkey))} | {_pct(_annualized(bm.get(rkey), trading_days))} "
            f"| {_pct(bm.get(ddkey))} | — | — | — |"
        )
    lines.append("")

    # Trading activity
    lines += [
        "## Trading Activity",
        "",
        "| Profile | Trades | / month | Win Rate | Avg Win | Avg Loss | Profit Factor | Avg Hold | Slippage |",
        "|---------|--------|---------|----------|---------|----------|---------------|----------|----------|",
    ]
    for r in results:
        m = r["metrics"]
        pf = m.get("profit_factor")
        lines.append(
            f"| {r['name']} | {m.get('n_trades', 0)} | {_num(r['trades_per_month'])} "
            f"| {_pct(m.get('win_rate'))} | {_dollar(m.get('avg_win'))} | {_dollar(m.get('avg_loss'))} "
            f"| {_num(pf) if pf is not None else '—'} | {_num(m.get('avg_holding_days'))} "
            f"| {_dollar(m.get('total_slippage_cost'))} |"
        )
    lines.append("")

    # Exit attribution
    lines += [
        "## Exit Attribution",
        "",
        "| Profile | Take-profit | Stop-loss | Trailing-stop | Max-hold | Gave back gains | Largest Win | Largest Loss |",
        "|---------|-------------|-----------|---------------|----------|-----------------|-------------|--------------|",
    ]
    for r in results:
        ec = r["exit_counts"]
        m = r["metrics"]
        lines.append(
            f"| {r['name']} | {ec['take_profit']} | {ec['stop_loss']} | {ec['trailing_stop']} "
            f"| {ec['max_holding_period']} | {r['gave_back']} "
            f"| {_dollar(m.get('largest_winner'))} | {_dollar(m.get('largest_loser'))} |"
        )
    lines.append("")

    # Signal quality (quintile spread)
    lines += [
        "## Signal Quality (composite-score quintile spread)",
        "",
        "_Top-minus-bottom quintile forward-return spread; positive ⇒ higher-ranked names outperform._",
        "",
        "| Profile | Spread 5d | Spread 10d | Spread 20d |",
        "|---------|-----------|------------|------------|",
    ]
    for r in results:
        s = r["spread"]
        lines.append(
            f"| {r['name']} | {_pct(s.get('spread_5d'))} | {_pct(s.get('spread_10d'))} "
            f"| {_pct(s.get('spread_20d'))} |"
        )
    lines.append("")

    # P&L by group matrix
    all_groups = sorted({g for r in results for g in r["pnl_by_group"]})
    if all_groups:
        lines += ["## P&L by Group", "", "| Profile | " + " | ".join(all_groups) + " |",
                  "|---------|" + "|".join(["-----"] * len(all_groups)) + "|"]
        for r in results:
            cells = " | ".join(_dollar(r["pnl_by_group"].get(g)) for g in all_groups)
            lines.append(f"| {r['name']} | {cells} |")
        lines.append("")

    # Top/bottom contributors per profile (compact)
    lines += ["## Top / Bottom P&L Contributors", ""]
    for r in results:
        top = ", ".join(f"`{t}` {_dollar(v)}" for t, v in r["top5"][:3]) or "—"
        bot = ", ".join(f"`{t}` {_dollar(v)}" for t, v in r["bottom5"][:3]) or "—"
        lines.append(f"- **{r['name']}** — top: {top}  |  worst: {bot}")
    lines.append("")
    lines.append("_(Full per-ticker P&L is in `backtest_experiments_<date>.csv`.)_")
    lines.append("")

    # Interpretation
    lines += ["## Interpretation", ""]
    for note in _interpretation(results):
        lines += [note, ""]

    return "\n".join(lines)


# ─── CSV ──────────────────────────────────────────────────────────────────────


def experiments_csv(results: List[Dict[str, Any]]) -> pd.DataFrame:
    """One wide row per profile: scalar metrics + per-group and per-ticker P&L."""
    all_tickers = sorted({t for r in results for t in r["pnl_by_ticker"]})
    all_groups = sorted({g for r in results for g in r["pnl_by_group"]})
    rows: List[Dict[str, Any]] = []
    for r in results:
        m = r["metrics"]
        row = {
            "profile": r["name"],
            "total_return": m.get("total_return"),
            "annualized_return": r["annualized_return"],
            "max_drawdown": m.get("max_drawdown"),
            "sharpe": r["sharpe"],
            "excess_vs_spy": m.get("excess_vs_spy"),
            "excess_vs_qqq": m.get("excess_vs_qqq"),
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
            "exits_take_profit": r["exit_counts"]["take_profit"],
            "exits_stop_loss": r["exit_counts"]["stop_loss"],
            "exits_trailing_stop": r["exit_counts"]["trailing_stop"],
            "exits_max_holding": r["exit_counts"]["max_holding_period"],
            "gave_back_gains": r["gave_back"],
            "spread_5d": r["spread"].get("spread_5d"),
            "spread_10d": r["spread"].get("spread_10d"),
            "spread_20d": r["spread"].get("spread_20d"),
            "pnl_concentration": r["concentration"],
        }
        for g in all_groups:
            row[f"pnl_group_{g}"] = r["pnl_by_group"].get(g)
        for t in all_tickers:
            row[f"pnl_{t}"] = r["pnl_by_ticker"].get(t)
        rows.append(row)
    return pd.DataFrame(rows)


# ─── Output ───────────────────────────────────────────────────────────────────


def save_experiment_outputs(report: str, csv_df: pd.DataFrame, output_dir: Path,
                            run_date: date) -> Dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    tag = run_date.isoformat()
    paths: Dict[str, str] = {}
    md_path = output_dir / f"backtest_experiments_{tag}.md"
    md_path.write_text(report)
    paths["report"] = str(md_path)
    csv_path = output_dir / f"backtest_experiments_{tag}.csv"
    csv_df.to_csv(csv_path, index=False)
    paths["csv"] = str(csv_path)
    return paths


# ─── CLI ──────────────────────────────────────────────────────────────────────


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="AI Paper Trader — Strategy Experiments")
    p.add_argument("--start", required=True, metavar="YYYY-MM-DD")
    p.add_argument("--end", required=True, metavar="YYYY-MM-DD")
    p.add_argument("--output", default=None, metavar="DIR")
    p.add_argument("--scenario", default=None,
                   help="optional: overlay config/scenarios/<name>.yaml (universe + rules) before running")
    return p.parse_args()


def run(start_date: date, end_date: date, output: Optional[Path] = None,
        scenario: Optional[str] = None) -> Dict[str, str]:
    """Run the strategy-experiment profiles and write outputs. `scenario` (optional) overlays a
    named scenario (config/scenarios/<name>.yaml) onto the base config first, so profiles run on
    that scenario's universe/rules; default None = the base config (unchanged behavior)."""
    setup_logging()
    run_date = date.today()
    root = Path(__file__).parent.parent
    config = load_config(root / "config")
    if scenario:
        from scenarios import build_config, load_scenario
        config = build_config(config, load_scenario(scenario))
    output_dir = output if output else root / "backtests"

    log.info("=== AI Paper Trader Experiments%s ===", f" — scenario {scenario}" if scenario else "")
    price_data = fetch_backtest_data(config["tickers"], start_date, end_date)

    results = run_experiments(config, price_data, start_date, end_date)
    report = render_experiments_md(results, run_date, start_date, end_date)
    csv_df = experiments_csv(results)
    paths = save_experiment_outputs(report, csv_df, output_dir, run_date)

    print()
    print(f"  Profiles run : {len(results)}")
    for r in results:
        print(f"    {r['name']:<40} total {_pct(r['metrics'].get('total_return'))}")
    print()
    print(f"  Report : {paths['report']}")
    print(f"  CSV    : {paths['csv']}")
    print()
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
    run(start_date, end_date, Path(args.output) if args.output else None, scenario=args.scenario)


if __name__ == "__main__":
    main()
