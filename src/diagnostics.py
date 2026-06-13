"""
diagnostics.py — Strategy diagnostics for the AI Paper Trader backtester.

These are EXPLANATORY diagnostics, not optimizers. They answer: does the signal
actually rank winners above losers, are exit rules helping or hurting, is P&L
broad-based or concentrated, is the book overtrading, and is it adding alpha or
just changing market exposure.

Look-ahead safety: forward returns are computed AFTER the simulation completes,
purely for evaluation, and are never fed back into any trading decision. Records
without a full forward window (near the end of the sample) are dropped, not padded.

Live-state safety: everything here operates on in-memory backtest outputs and the
price panel. Nothing in this module reads or writes data/ (live paper state).
"""
import logging
from datetime import date
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

_SIGNAL_COLS = ["return_1d", "return_5d", "return_20d", "vol_ratio", "vol_adj_mom_20d"]
_FWD_HORIZONS = [5, 10, 20]
_RAW_HOLD_PERIODS = [5, 10, 20, 30]
_N_QUINTILES = 5


# ─── Forward-return panel ─────────────────────────────────────────────────────


def build_signal_panel(
    price_data: pd.DataFrame,
    signal_history: List[Dict[str, Any]],
) -> pd.DataFrame:
    """
    Turn the per-(date, ticker) signal history into a panel with forward returns
    and a cross-sectional composite-score quintile per day.

    Forward return fwd_Nd for a row at bar_idx = close[idx+N]/close[idx] - 1,
    using the price panel. idx+N beyond the sample → NaN (dropped downstream).
    """
    if not signal_history:
        return pd.DataFrame()

    panel = pd.DataFrame(signal_history)
    close = price_data["Close"]
    # Cache each ticker's close as a numpy array for O(1) positional forward lookups.
    close_arrays: Dict[str, np.ndarray] = {}
    for ticker in panel["ticker"].unique():
        if ticker in close.columns:
            close_arrays[ticker] = close[ticker].to_numpy()

    n_bars = len(close.index)
    for horizon in _FWD_HORIZONS:
        col = f"fwd_{horizon}d"
        out = np.full(len(panel), np.nan)
        for i, (ticker, idx) in enumerate(zip(panel["ticker"], panel["bar_idx"])):
            arr = close_arrays.get(ticker)
            if arr is None:
                continue
            j = idx + horizon
            if j < n_bars:
                p0 = arr[idx]
                pj = arr[j]
                if p0 > 0 and not np.isnan(p0) and not np.isnan(pj):
                    out[i] = pj / p0 - 1.0
        panel[col] = out

    # Cross-sectional composite-score quintile (1 = lowest, 5 = highest), per day.
    panel["score_quintile"] = (
        panel.groupby("date")["composite_score"].transform(_safe_quintile)
    )
    return panel


def _safe_quintile(scores: pd.Series) -> pd.Series:
    """Assign 1..5 quintiles within one day; NaN if fewer than _N_QUINTILES names."""
    if scores.notna().sum() < _N_QUINTILES:
        return pd.Series(np.nan, index=scores.index)
    # rank(method='first') breaks ties so qcut always yields 5 equal-width buckets.
    ranks = scores.rank(method="first")
    try:
        q = pd.qcut(ranks, _N_QUINTILES, labels=False, duplicates="drop")
    except ValueError:
        return pd.Series(np.nan, index=scores.index)
    return q + 1


# ─── 1. Signal predictiveness ─────────────────────────────────────────────────


def signal_predictiveness(panel: pd.DataFrame) -> Dict[str, Any]:
    """Correlations of each signal (and composite) with forward returns, plus
    quintile forward-return / win-rate profiles."""
    if panel.empty:
        return {}

    signal_cols = [c for c in _SIGNAL_COLS + ["composite_score"] if c in panel.columns]
    fwd_cols = [f"fwd_{h}d" for h in _FWD_HORIZONS]

    correlations: Dict[str, Dict[str, Optional[float]]] = {}
    for sig in signal_cols:
        correlations[sig] = {}
        for fwd in fwd_cols:
            sub = panel[[sig, fwd]].dropna()
            # Need ≥3 points and non-zero variance on both sides, else corr is undefined.
            if len(sub) >= 3 and sub[sig].std() > 0 and sub[fwd].std() > 0:
                correlations[sig][fwd] = float(sub[sig].corr(sub[fwd]))
            else:
                correlations[sig][fwd] = None

    # Quintile profiles (cross-sectional).
    quintile_rows: List[Dict[str, Any]] = []
    spreads: Dict[str, Optional[float]] = {}
    has_q = "score_quintile" in panel.columns and panel["score_quintile"].notna().any()
    if has_q:
        grouped = panel.dropna(subset=["score_quintile"]).groupby("score_quintile")
        for q in range(1, _N_QUINTILES + 1):
            if q not in grouped.groups:
                continue
            g = grouped.get_group(q)
            row: Dict[str, Any] = {"quintile": int(q), "n": int(len(g))}
            for h in _FWD_HORIZONS:
                fwd = f"fwd_{h}d"
                vals = g[fwd].dropna()
                row[f"avg_fwd_{h}d"] = float(vals.mean()) if len(vals) else None
                row[f"win_rate_{h}d"] = float((vals > 0).mean()) if len(vals) else None
            quintile_rows.append(row)

        for h in _FWD_HORIZONS:
            fwd = f"fwd_{h}d"
            top = panel.loc[panel["score_quintile"] == _N_QUINTILES, fwd].dropna()
            bot = panel.loc[panel["score_quintile"] == 1, fwd].dropna()
            spreads[f"spread_{h}d"] = (
                float(top.mean() - bot.mean()) if len(top) and len(bot) else None
            )

    return {
        "n_observations": int(len(panel)),
        "correlations": correlations,
        "quintile_profile": quintile_rows,
        "top_minus_bottom_spread": spreads,
    }


# ─── 2. Entry vs exit attribution (raw signal test) ───────────────────────────


def entry_vs_exit_attribution(
    price_data: pd.DataFrame,
    signal_history: List[Dict[str, Any]],
    config: Dict[str, Any],
    metrics: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Raw signal test: each day, buy the same top-K names the strategy would pick
    (same ranking + min-score filter), then hold a FIXED number of days with NO
    stop-loss / take-profit / max-holding rules. Entry at next-day close + buy
    slippage, exit at close + sell slippage — mirroring the strategy's execution.

    Isolates whether returns come from the signal itself or from the exit rules.
    """
    if not signal_history:
        return {}

    panel = pd.DataFrame(signal_history)
    close = price_data["Close"]
    n_bars = len(close.index)
    close_arrays = {
        t: close[t].to_numpy() for t in panel["ticker"].unique() if t in close.columns
    }

    top_k = config["portfolio"].get("max_new_trades_per_day", 3)
    min_score = config.get("signals", {}).get("min_composite_score")
    slip = config["risk"].get("slippage", 0.0)

    by_period: Dict[int, Dict[str, Any]] = {}
    for hold in _RAW_HOLD_PERIODS:
        trade_returns: List[float] = []
        for _, day in panel.groupby("date"):
            ranked = day.sort_values("composite_score", ascending=False)
            if min_score is not None:
                ranked = ranked[ranked["composite_score"] >= min_score]
            chosen = ranked.head(top_k)
            for _, row in chosen.iterrows():
                arr = close_arrays.get(row["ticker"])
                if arr is None:
                    continue
                entry_idx = int(row["bar_idx"]) + 1          # next-day fill
                exit_idx = entry_idx + hold
                if exit_idx >= n_bars:
                    continue
                p_in, p_out = arr[entry_idx], arr[exit_idx]
                if p_in > 0 and not np.isnan(p_in) and not np.isnan(p_out):
                    buy = p_in * (1 + slip)
                    sell = p_out * (1 - slip)
                    trade_returns.append(sell / buy - 1.0)
        if trade_returns:
            arr = np.array(trade_returns)
            by_period[hold] = {
                "avg_return": float(arr.mean()),
                "win_rate": float((arr > 0).mean()),
                "n_trades": int(len(arr)),
            }
        else:
            by_period[hold] = {"avg_return": None, "win_rate": None, "n_trades": 0}

    return {
        "top_k": top_k,
        "by_period": by_period,
        "strategy_total_return": metrics.get("total_return"),
        "strategy_win_rate": metrics.get("win_rate"),
        "strategy_avg_holding_days": metrics.get("avg_holding_days"),
    }


def _attribution_interpretation(attr: Dict[str, Any]) -> str:
    """Plain-English read on signal quality vs exit-rule contribution."""
    by_period = attr.get("by_period", {})
    raw_returns = [v["avg_return"] for v in by_period.values() if v.get("avg_return") is not None]
    raw_wins = [v["win_rate"] for v in by_period.values() if v.get("win_rate") is not None]
    if not raw_returns:
        return "_Not enough raw-hold trades to attribute performance._"

    avg_raw = float(np.mean(raw_returns))
    avg_win = float(np.mean(raw_wins)) if raw_wins else 0.0
    strat = attr.get("strategy_total_return")

    if avg_raw > 0.005 and avg_win > 0.5:
        signal_msg = (
            "The raw signal (buy top names, hold fixed, no stops) is **positive across "
            f"holding periods** (avg {avg_raw * 100:+.2f}% per trade, {avg_win * 100:.0f}% win rate). "
            "That points to genuine signal quality — higher-ranked names tend to rise even "
            "without exit rules."
        )
    elif avg_raw <= 0 and strat is not None and strat > 0:
        signal_msg = (
            "The raw signal is **flat-to-negative** without exit rules "
            f"(avg {avg_raw * 100:+.2f}% per trade) even though the full strategy is positive. "
            "That suggests the stop-loss / take-profit / max-holding rules — not the signal — "
            "are doing most of the work. Treat the edge as risk-management, not prediction."
        )
    else:
        signal_msg = (
            f"The raw signal is marginal (avg {avg_raw * 100:+.2f}% per trade, "
            f"{avg_win * 100:.0f}% win rate). Signal and exit rules likely share the credit; "
            "the predictiveness section above shows whether ranking adds cross-sectional edge."
        )
    return signal_msg


# ─── 3. P&L attribution ───────────────────────────────────────────────────────


def group_to_tickers(groups: Dict[str, Any]) -> Dict[str, List[str]]:
    """Normalise ticker_groups: accepts either {group: [tickers]} (flat) or
    {group: {tickers: [...], ...}} (nested with per-group settings)."""
    out: Dict[str, List[str]] = {}
    for name, spec in (groups or {}).items():
        if isinstance(spec, dict) and "tickers" in spec:
            out[name] = list(spec["tickers"])
        elif isinstance(spec, (list, tuple)):
            out[name] = list(spec)
    return out


def pnl_attribution(
    trades_df: pd.DataFrame,
    positions: pd.DataFrame,
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """Realized + unrealized P&L per ticker, top/bottom contributors, and by group."""
    pnl_by_ticker: Dict[str, float] = {}

    if not trades_df.empty:
        sells = trades_df[trades_df["action"] == "SELL"]
        for ticker, grp in sells.groupby("ticker"):
            pnl_by_ticker[ticker] = pnl_by_ticker.get(ticker, 0.0) + float(
                grp["realized_pnl"].fillna(0.0).sum()
            )

    if not positions.empty:
        for _, row in positions.iterrows():
            unreal = (float(row["current_price"]) - float(row["entry_price"])) * int(row["shares"])
            pnl_by_ticker[row["ticker"]] = pnl_by_ticker.get(row["ticker"], 0.0) + unreal

    ranked = sorted(pnl_by_ticker.items(), key=lambda kv: kv[1], reverse=True)

    # By configured group (only groups that actually traded show up).
    groups = group_to_tickers(config.get("ticker_groups", {}) or {})
    pnl_by_group: Dict[str, float] = {}
    ticker_to_group = {t: g for g, members in groups.items() for t in members}
    grouped_total = 0.0
    for ticker, pnl in pnl_by_ticker.items():
        grp = ticker_to_group.get(ticker)
        if grp is not None:
            pnl_by_group[grp] = pnl_by_group.get(grp, 0.0) + pnl
            grouped_total += pnl
    ungrouped = sum(pnl_by_ticker.values()) - grouped_total

    return {
        "pnl_by_ticker": dict(ranked),
        "top5": ranked[:5],
        "bottom5": list(reversed(ranked[-5:])) if len(ranked) >= 5 else list(reversed(ranked)),
        "pnl_by_group": dict(sorted(pnl_by_group.items(), key=lambda kv: kv[1], reverse=True)),
        "ungrouped_pnl": ungrouped if groups else None,
        "has_groups": bool(groups),
    }


def ticker_level_diagnostics(
    trades_df: pd.DataFrame,
    positions: pd.DataFrame,
    price_data: pd.DataFrame,
) -> List[Dict[str, Any]]:
    """
    Per-ticker behaviour from closed trades, used to justify group assumptions.

    MFE = max favorable excursion (highest/entry - 1); MAE = max adverse excursion
    (lowest/entry - 1); giveback = MFE - realized exit gain (peak gain handed back).
    Also exit-reason counts and stop-loss → re-entry-within-5-trading-days per ticker.
    """
    if trades_df.empty:
        return []

    sells = trades_df[trades_df["action"] == "SELL"].copy()
    buys = trades_df[trades_df["action"] == "BUY"]
    bar_dates = [ts.date() for ts in price_data["Close"].index]
    date_to_pos = {d: i for i, d in enumerate(bar_dates)}

    rows: List[Dict[str, Any]] = []
    for ticker in sorted(set(trades_df["ticker"])):
        t_sells = sells[sells["ticker"] == ticker]
        n = len(t_sells)
        if n == 0:
            continue
        pnls = t_sells["realized_pnl"].astype(float)
        entry = t_sells["entry_price"].astype(float)
        sell_px = t_sells["price"].astype(float)
        high = t_sells.get("highest_price", entry).astype(float)
        low = t_sells.get("lowest_price", entry).astype(float)

        trade_ret = (sell_px / entry - 1.0)
        mfe = (high / entry - 1.0)
        mae = (low / entry - 1.0)
        giveback = mfe - trade_ret
        wins = pnls[pnls > 0]
        losses = pnls[pnls <= 0]
        gross_loss = abs(float(losses.sum()))

        reasons = t_sells["reason"].astype(str)
        # stop → re-entry within 5 trading days
        reentry = 0
        for _, sr in t_sells[reasons.str.contains("stop_loss")].iterrows():
            sp = date_to_pos.get(date.fromisoformat(str(sr["date"])))
            if sp is None:
                continue
            for _, br in buys[buys["ticker"] == ticker].iterrows():
                bp = date_to_pos.get(date.fromisoformat(str(br["date"])))
                if bp is not None and 0 < (bp - sp) <= 5:
                    reentry += 1
                    break

        rows.append({
            "ticker": ticker,
            "trades": n,
            "total_pnl": float(pnls.sum()),
            "avg_return_per_trade": float(trade_ret.mean()),
            "win_rate": float((pnls > 0).mean()),
            "profit_factor": (float(wins.sum()) / gross_loss) if gross_loss > 0 else None,
            "avg_holding_days": float(t_sells["holding_days"].astype(float).mean()),
            "avg_mfe": float(mfe.mean()),
            "median_mfe": float(mfe.median()),
            "avg_mae": float(mae.mean()),
            "median_mae": float(mae.median()),
            "avg_giveback": float(giveback.mean()),
            "exits_stop_loss": int(reasons.str.contains("stop_loss").sum()),
            "exits_take_profit": int(reasons.str.contains("take_profit").sum()),
            "exits_trailing_stop": int(reasons.str.contains("trailing_stop").sum()),
            "exits_max_holding": int(reasons.str.contains("max_holding_period").sum()),
            "stop_then_reentry_5d": reentry,
        })
    return rows


# ─── 4. Turnover and re-entry diagnostics ─────────────────────────────────────


def turnover_diagnostics(
    trades_df: pd.DataFrame,
    price_data: pd.DataFrame,
    metrics: Dict[str, Any],
    start_date: date,
    end_date: date,
) -> Dict[str, Any]:
    """Trade frequency, repeated entries, and stop-loss → fast re-entry counts."""
    n_trades = int(len(trades_df)) if not trades_df.empty else 0
    months = max((end_date - start_date).days / 30.44, 1e-9)
    trades_per_month = n_trades / months

    repeated_entries: Dict[str, int] = {}
    reentry_after_stop = 0
    reentry_tickers: Dict[str, int] = {}

    if not trades_df.empty:
        buys = trades_df[trades_df["action"] == "BUY"]
        repeated_entries = (
            buys["ticker"].value_counts().to_dict() if not buys.empty else {}
        )

        # Trading-day positions for "within 5 trading days" tests.
        bar_dates = [ts.date() for ts in price_data["Close"].index]
        date_to_pos = {d: i for i, d in enumerate(bar_dates)}

        sells = trades_df[trades_df["action"] == "SELL"]
        for _, srow in sells.iterrows():
            if "stop_loss" not in str(srow["reason"]):
                continue
            ticker = srow["ticker"]
            sell_pos = date_to_pos.get(date.fromisoformat(str(srow["date"])))
            if sell_pos is None:
                continue
            # any BUY of the same ticker within the next 5 trading days?
            future_buys = buys[buys["ticker"] == ticker]
            for _, brow in future_buys.iterrows():
                buy_pos = date_to_pos.get(date.fromisoformat(str(brow["date"])))
                if buy_pos is not None and 0 < (buy_pos - sell_pos) <= 5:
                    reentry_after_stop += 1
                    reentry_tickers[ticker] = reentry_tickers.get(ticker, 0) + 1
                    break

    most_reentered = sorted(reentry_tickers.items(), key=lambda kv: kv[1], reverse=True)[:5]
    repeated_sorted = sorted(repeated_entries.items(), key=lambda kv: kv[1], reverse=True)

    return {
        "total_trades": n_trades,
        "trades_per_month": trades_per_month,
        "avg_holding_days": metrics.get("avg_holding_days"),
        "repeated_entries": repeated_sorted,
        "stop_then_reentry_count": reentry_after_stop,
        "most_reentered_after_stop": most_reentered,
    }


# ─── 5. Exposure and benchmark capture ────────────────────────────────────────


def exposure_benchmark_capture(equity_df: pd.DataFrame) -> Dict[str, Any]:
    """Exposure, cash drag, correlation/beta and up/down capture vs benchmarks."""
    if equity_df.empty:
        return {}

    total = equity_df["total_portfolio_value"]
    exposure = equity_df["open_positions_value"] / total
    cash_pct = equity_df["cash"] / total

    strat_ret = equity_df["daily_return"].astype(float)

    def _daily_from_cum(col: str) -> Optional[pd.Series]:
        if col not in equity_df.columns:
            return None
        cum = equity_df[col].astype(float)
        lvl = 1.0 + cum
        return lvl / lvl.shift(1) - 1.0

    spy_ret = _daily_from_cum("spy_cumulative_return")
    qqq_ret = _daily_from_cum("qqq_cumulative_return")

    def _corr(a: pd.Series, b: Optional[pd.Series]) -> Optional[float]:
        if b is None:
            return None
        df = pd.concat([a, b], axis=1).dropna()
        if len(df) < 3 or df.iloc[:, 0].std() == 0 or df.iloc[:, 1].std() == 0:
            return None
        return float(df.iloc[:, 0].corr(df.iloc[:, 1]))

    def _beta(a: pd.Series, b: Optional[pd.Series]) -> Optional[float]:
        if b is None:
            return None
        df = pd.concat([a, b], axis=1).dropna()
        if len(df) < 3:
            return None
        var = df.iloc[:, 1].var()
        return float(df.iloc[:, 0].cov(df.iloc[:, 1]) / var) if var > 0 else None

    def _capture(a: pd.Series, b: Optional[pd.Series], up: bool) -> Optional[float]:
        if b is None:
            return None
        df = pd.concat([a, b], axis=1).dropna()
        df.columns = ["strat", "bench"]
        side = df[df["bench"] > 0] if up else df[df["bench"] < 0]
        if len(side) < 2 or side["bench"].mean() == 0:
            return None
        return float(side["strat"].mean() / side["bench"].mean())

    return {
        "avg_exposure": float(exposure.mean()),
        "max_exposure": float(exposure.max()),
        "avg_cash_pct": float(cash_pct.mean()),
        "corr_spy": _corr(strat_ret, spy_ret),
        "corr_qqq": _corr(strat_ret, qqq_ret),
        "beta_spy": _beta(strat_ret, spy_ret),
        "beta_qqq": _beta(strat_ret, qqq_ret),
        "up_capture_qqq": _capture(strat_ret, qqq_ret, up=True),
        "down_capture_qqq": _capture(strat_ret, qqq_ret, up=False),
    }


# ─── 6. Suggested next config tests (static, not implemented) ─────────────────


def suggested_next_config_tests() -> List[str]:
    return [
        "**QQQ trend filter** — only take entries while QQQ is above its 50-day moving average.",
        "**Volatility-adjusted momentum** — rank on `return_20d / realized_vol_20d` instead of raw return.",
        "**Moving-average confirmation** — require price above both its 20-day and 50-day moving averages.",
        "**Overextension filter** — skip names too far above their 20-day moving average (avoid chasing).",
        "**Cooldown after stop-loss** — block re-entry into a name for 5 trading days after a stop-out.",
        "**Separate leveraged-ETF rules** — smaller max position size and shorter max holding for leveraged ETFs.",
    ]


# ─── Orchestration ────────────────────────────────────────────────────────────


def compute_diagnostics(
    config: Dict[str, Any],
    price_data: pd.DataFrame,
    trades_df: pd.DataFrame,
    equity_df: pd.DataFrame,
    positions: pd.DataFrame,
    signal_history: List[Dict[str, Any]],
    metrics: Dict[str, Any],
    start_date: date,
    end_date: date,
) -> Dict[str, Any]:
    """Compute every diagnostic block. Pure function — reads only in-memory inputs."""
    panel = build_signal_panel(price_data, signal_history)
    return {
        "predictiveness": signal_predictiveness(panel),
        "attribution": entry_vs_exit_attribution(price_data, signal_history, config, metrics),
        "pnl": pnl_attribution(trades_df, positions, config),
        "turnover": turnover_diagnostics(trades_df, price_data, metrics, start_date, end_date),
        "capture": exposure_benchmark_capture(equity_df),
        "panel": panel,
    }


# ─── Rendering ────────────────────────────────────────────────────────────────


def _pct(v: Optional[float], default: str = "—") -> str:
    return default if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v * 100:+.2f}%"


def _num(v: Optional[float], default: str = "—") -> str:
    return default if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v:.2f}"


def _dollar(v: Optional[float], default: str = "—") -> str:
    return default if v is None or (isinstance(v, float) and np.isnan(v)) else f"${v:,.2f}"


def render_diagnostics_md(diag: Dict[str, Any], config: Dict[str, Any]) -> str:
    lines: List[str] = ["## Signal Predictiveness", ""]

    pred = diag.get("predictiveness", {})
    if not pred:
        lines += ["_No signal history captured — diagnostics unavailable._", ""]
    else:
        lines.append(
            f"_Cross-section of {pred.get('n_observations', 0):,} (date, ticker) "
            "signal observations. Correlations are Pearson vs forward returns._"
        )
        lines += [
            "",
            "| Signal | vs fwd 5d | vs fwd 10d | vs fwd 20d |",
            "|--------|-----------|------------|------------|",
        ]
        for sig, corrs in pred.get("correlations", {}).items():
            lines.append(
                f"| {sig} | {_num(corrs.get('fwd_5d'))} | "
                f"{_num(corrs.get('fwd_10d'))} | {_num(corrs.get('fwd_20d'))} |"
            )
        lines.append("")

        if pred.get("quintile_profile"):
            lines += [
                "**Forward returns by composite-score quintile** (5 = highest-ranked):",
                "",
                "| Quintile | N | Avg fwd 5d | Win 5d | Avg fwd 10d | Win 10d | Avg fwd 20d | Win 20d |",
                "|----------|---|-----------|--------|-------------|---------|-------------|---------|",
            ]
            for r in pred["quintile_profile"]:
                lines.append(
                    f"| Q{r['quintile']} | {r['n']} "
                    f"| {_pct(r.get('avg_fwd_5d'))} | {_pct(r.get('win_rate_5d'))} "
                    f"| {_pct(r.get('avg_fwd_10d'))} | {_pct(r.get('win_rate_10d'))} "
                    f"| {_pct(r.get('avg_fwd_20d'))} | {_pct(r.get('win_rate_20d'))} |"
                )
            lines.append("")
            sp = pred.get("top_minus_bottom_spread", {})
            lines.append(
                "**Top-minus-bottom quintile spread:** "
                f"5d {_pct(sp.get('spread_5d'))}  |  "
                f"10d {_pct(sp.get('spread_10d'))}  |  "
                f"20d {_pct(sp.get('spread_20d'))}  "
                "(positive ⇒ higher-ranked names outperform lower-ranked names)."
            )
            lines.append("")

    # ── Entry vs Exit Attribution ─────────────────────────────────────────────
    attr = diag.get("attribution", {})
    lines += ["## Entry vs Exit Attribution", ""]
    if not attr or not attr.get("by_period"):
        lines += ["_No raw-hold trades available._", ""]
    else:
        lines += [
            f"_Buy the top {attr.get('top_k')} ranked names each day, hold a fixed period, "
            "**no** stop-loss / take-profit / max-holding. Next-day entry, slippage applied._",
            "",
            "| Hold period | Raw avg return / trade | Raw win rate | N trades |",
            "|-------------|------------------------|--------------|----------|",
        ]
        for hold, v in attr["by_period"].items():
            lines.append(
                f"| {hold}d | {_pct(v.get('avg_return'))} | "
                f"{_pct(v.get('win_rate'))} | {v.get('n_trades', 0)} |"
            )
        lines += [
            "",
            f"**Full strategy (with exit rules):** total return {_pct(attr.get('strategy_total_return'))}, "
            f"win rate {_pct(attr.get('strategy_win_rate'))}, "
            f"avg hold {_num(attr.get('strategy_avg_holding_days'))} trading days.",
            "",
            _attribution_interpretation(attr),
            "",
        ]

    # ── P&L Attribution ───────────────────────────────────────────────────────
    pnl = diag.get("pnl", {})
    lines += ["## P&L Attribution", ""]
    if not pnl or not pnl.get("pnl_by_ticker"):
        lines += ["_No closed or open P&L to attribute._", ""]
    else:
        lines += ["**Top 5 contributors:**", "", "| Ticker | P&L |", "|--------|-----|"]
        for ticker, v in pnl.get("top5", []):
            lines.append(f"| {ticker} | {_dollar(v)} |")
        lines += ["", "**Worst 5 contributors:**", "", "| Ticker | P&L |", "|--------|-----|"]
        for ticker, v in pnl.get("bottom5", []):
            lines.append(f"| {ticker} | {_dollar(v)} |")
        lines.append("")
        if pnl.get("has_groups"):
            lines += ["**P&L by asset group:**", "", "| Group | P&L |", "|-------|-----|"]
            for grp, v in pnl.get("pnl_by_group", {}).items():
                lines.append(f"| {grp} | {_dollar(v)} |")
            if pnl.get("ungrouped_pnl"):
                lines.append(f"| _(ungrouped)_ | {_dollar(pnl.get('ungrouped_pnl'))} |")
            lines.append("")

    # ── Turnover and Re-entry ─────────────────────────────────────────────────
    tov = diag.get("turnover", {})
    lines += ["## Turnover and Re-entry Diagnostics", ""]
    if not tov:
        lines += ["_No trades to analyze._", ""]
    else:
        lines += [
            "| Metric | Value |",
            "|--------|-------|",
            f"| Total trades | {tov.get('total_trades', 0)} |",
            f"| Trades / month | {_num(tov.get('trades_per_month'))} |",
            f"| Avg holding period | {_num(tov.get('avg_holding_days'))} trading days |",
            f"| Stop-loss → re-entry ≤5d | {tov.get('stop_then_reentry_count', 0)} |",
            "",
        ]
        rep = tov.get("repeated_entries", [])
        if rep:
            top_rep = ", ".join(f"`{t}`×{n}" for t, n in rep[:8])
            lines += [f"**Most-entered tickers:** {top_rep}", ""]
        most_re = tov.get("most_reentered_after_stop", [])
        if most_re:
            lst = ", ".join(f"`{t}`×{n}" for t, n in most_re)
            lines += [f"**Most re-entered after a stop-loss:** {lst}", ""]

    # ── Exposure and Benchmark Capture ────────────────────────────────────────
    cap = diag.get("capture", {})
    lines += ["## Exposure and Benchmark Capture", ""]
    if not cap:
        lines += ["_No equity data to analyze._", ""]
    else:
        lines += [
            "| Metric | Value |",
            "|--------|-------|",
            f"| Avg exposure | {_pct(cap.get('avg_exposure'))} |",
            f"| Max exposure | {_pct(cap.get('max_exposure'))} |",
            f"| Avg cash (drag) | {_pct(cap.get('avg_cash_pct'))} |",
            f"| Correlation to SPY | {_num(cap.get('corr_spy'))} |",
            f"| Correlation to QQQ | {_num(cap.get('corr_qqq'))} |",
            f"| Beta to SPY | {_num(cap.get('beta_spy'))} |",
            f"| Beta to QQQ | {_num(cap.get('beta_qqq'))} |",
            f"| Up-capture vs QQQ | {_num(cap.get('up_capture_qqq'))} |",
            f"| Down-capture vs QQQ | {_num(cap.get('down_capture_qqq'))} |",
            "",
            "_Beta ≈ 1 with high correlation ⇒ performance is mostly market exposure; "
            "low beta with a positive quintile spread ⇒ more genuine selection alpha._",
            "",
        ]

    # ── Suggested next config tests ───────────────────────────────────────────
    lines += ["## Suggested Next Config Tests", "", "_Ideas to test next — not yet implemented._", ""]
    for idea in suggested_next_config_tests():
        lines.append(f"- {idea}")
    lines.append("")

    return "\n".join(lines)


# ─── Compact CSV ──────────────────────────────────────────────────────────────


def diagnostics_csv(diag: Dict[str, Any]) -> pd.DataFrame:
    """One tidy long-format table (section, metric, value) of the key numbers."""
    rows: List[Dict[str, Any]] = []

    def add(section: str, metric: str, value: Any) -> None:
        rows.append({"section": section, "metric": metric, "value": value})

    pred = diag.get("predictiveness", {})
    for sig, corrs in pred.get("correlations", {}).items():
        for fwd, v in corrs.items():
            add("predictiveness", f"corr[{sig}|{fwd}]", v)
    for r in pred.get("quintile_profile", []):
        for h in _FWD_HORIZONS:
            add("predictiveness", f"Q{r['quintile']}_avg_fwd_{h}d", r.get(f"avg_fwd_{h}d"))
            add("predictiveness", f"Q{r['quintile']}_win_{h}d", r.get(f"win_rate_{h}d"))
    for k, v in pred.get("top_minus_bottom_spread", {}).items():
        add("predictiveness", k, v)

    attr = diag.get("attribution", {})
    for hold, v in attr.get("by_period", {}).items():
        add("attribution", f"raw_avg_return_{hold}d", v.get("avg_return"))
        add("attribution", f"raw_win_rate_{hold}d", v.get("win_rate"))

    pnl = diag.get("pnl", {})
    for ticker, v in pnl.get("pnl_by_ticker", {}).items():
        add("pnl_by_ticker", ticker, v)
    for grp, v in pnl.get("pnl_by_group", {}).items():
        add("pnl_by_group", grp, v)

    tov = diag.get("turnover", {})
    for k in ["total_trades", "trades_per_month", "avg_holding_days", "stop_then_reentry_count"]:
        add("turnover", k, tov.get(k))

    cap = diag.get("capture", {})
    for k, v in cap.items():
        add("capture", k, v)

    return pd.DataFrame(rows, columns=["section", "metric", "value"])
