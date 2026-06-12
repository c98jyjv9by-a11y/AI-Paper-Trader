"""
report.py — Build and save the daily Markdown report.
"""
import logging
import os
from datetime import date
from typing import Any, Dict, List

import pandas as pd

log = logging.getLogger(__name__)


# ─── Formatting helpers ───────────────────────────────────────────────────────


def _pct(value: float) -> str:
    """Format a decimal ratio as a signed percentage string."""
    return f"{value * 100:+.2f}%"


def _dollar(value: float) -> str:
    """Format a float as a dollar amount."""
    return f"${value:,.2f}"


# ─── Report builder ───────────────────────────────────────────────────────────


def generate_report(
    today: date,
    signals: pd.DataFrame,
    ranked: pd.DataFrame,
    positions: pd.DataFrame,
    exit_trades: List[Dict[str, Any]],
    entry_trades: List[Dict[str, Any]],
    portfolio_state: Dict[str, float],
    config: Dict[str, Any],
) -> str:
    """
    Assemble the full Markdown report and return it as a string.

    Sections:
      1. Portfolio summary
      2. Open positions
      3. Exits recommended today
      4. New entries recommended today
      5. Signal rankings (top candidates)
      6. Catalyst scoring (placeholder — disabled until a news API is configured)
      7. Risk parameters
    """
    cash = portfolio_state["cash"]
    starting_value = portfolio_state["starting_value"]

    # Compute total portfolio value (cash + market value of positions)
    equity = 0.0
    if not positions.empty:
        equity = float((positions["shares"] * positions["current_price"]).sum())
    portfolio_value = cash + equity
    total_return = (portfolio_value - starting_value) / starting_value

    lines: List[str] = []

    # ── Header ────────────────────────────────────────────────────────────────
    lines += [
        "# AI Paper Trader — Daily Report",
        f"**Date:** {today.isoformat()}  |  **For research and paper trading only.**",
        "",
        "---",
        "",
    ]

    # ── Portfolio summary ─────────────────────────────────────────────────────
    lines += [
        "## Portfolio Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Starting Value | {_dollar(starting_value)} |",
        f"| Current Value  | {_dollar(portfolio_value)} |",
        f"| Cash           | {_dollar(cash)} |",
        f"| Invested (equity) | {_dollar(equity)} |",
        f"| Total Return   | {_pct(total_return)} |",
        f"| Open Positions | {len(positions)} |",
        "",
    ]

    # ── Open positions ────────────────────────────────────────────────────────
    lines += ["## Open Positions", ""]
    if positions.empty:
        lines.append("_No open positions._")
    else:
        lines += [
            "| Ticker | Shares | Entry Price | Current Price | Unrealized P&L | Entry Date |",
            "|--------|--------|------------|--------------|----------------|------------|",
        ]
        for _, row in positions.iterrows():
            pnl = (float(row["current_price"]) - float(row["entry_price"])) * int(row["shares"])
            lines.append(
                f"| {row['ticker']} | {int(row['shares'])} "
                f"| {_dollar(float(row['entry_price']))} "
                f"| {_dollar(float(row['current_price']))} "
                f"| {_dollar(pnl)} "
                f"| {row['entry_date']} |"
            )
    lines.append("")

    # ── Exits today ───────────────────────────────────────────────────────────
    lines += ["## Exits Recommended Today", ""]
    if not exit_trades:
        lines.append("_No exits recommended._")
    else:
        lines += [
            "| Ticker | Shares | Sell Price (w/ slippage) | Reason | P&L |",
            "|--------|--------|------------------------|--------|-----|",
        ]
        for t in exit_trades:
            lines.append(
                f"| {t['ticker']} | {t['shares']} "
                f"| {_dollar(t['price_with_slippage'])} "
                f"| {t['reason']} "
                f"| {_dollar(t['pnl'])} |"
            )
    lines.append("")

    # ── New entries today ─────────────────────────────────────────────────────
    lines += ["## New Entries Recommended Today", ""]
    if not entry_trades:
        lines.append("_No new entries recommended._")
    else:
        lines += [
            "| Ticker | Shares | Buy Price (w/ slippage) | Trade Value | Signal Score |",
            "|--------|--------|------------------------|------------|-------------|",
        ]
        for t in entry_trades:
            score = t["reason"].replace("momentum_score=", "")
            lines.append(
                f"| {t['ticker']} | {t['shares']} "
                f"| {_dollar(t['price_with_slippage'])} "
                f"| {_dollar(t['trade_value'])} "
                f"| {score} |"
            )
    lines.append("")

    # ── Signal rankings ───────────────────────────────────────────────────────
    lines += ["## Signal Rankings — Top Candidates", ""]
    if ranked.empty:
        lines.append("_No ranked signal data available._")
    else:
        lines += [
            "| Rank | Ticker | Price | 1d Ret | 5d Ret | 20d Ret | Vol Ratio | Score |",
            "|------|--------|-------|--------|--------|---------|----------|-------|",
        ]
        for i, row in ranked.head(10).iterrows():
            lines.append(
                f"| {i + 1} "
                f"| {row['ticker']} "
                f"| {_dollar(row['price'])} "
                f"| {_pct(row['return_1d'])} "
                f"| {_pct(row['return_5d'])} "
                f"| {_pct(row['return_20d'])} "
                f"| {row['vol_ratio']:.2f}x "
                f"| {row['composite_score']:.4f} |"
            )
    lines.append("")

    # ── Catalyst scoring (disabled placeholder) ───────────────────────────────
    lines += [
        "## Catalyst Scoring",
        "",
        "> **Disabled** — no news data source is configured.",
        ">",
        "> To enable catalyst scoring:",
        "> 1. Obtain a [NewsAPI](https://newsapi.org) key (free tier available).",
        "> 2. Add `NEWS_API_KEY=your_key` to a `.env` file in the project root.",
        "> 3. Implement a `news.py` module and integrate it with `signals.py`.",
        "",
    ]

    # ── Risk parameters ───────────────────────────────────────────────────────
    r = config["risk"]
    p = config["portfolio"]
    lines += [
        "## Risk Parameters",
        "",
        "| Parameter | Value |",
        "|-----------|-------|",
        f"| Max position size | {p['max_position_pct'] * 100:.0f}% of portfolio |",
        f"| Max total exposure | {p['max_total_exposure'] * 100:.0f}% of portfolio |",
        f"| Max new trades / day | {p['max_new_trades_per_day']} |",
        f"| Stop loss | {r['stop_loss'] * 100:.0f}% below entry |",
        f"| Take profit | {r['take_profit'] * 100:.0f}% above entry |",
        f"| Max holding period | {r['max_holding_days']} trading days |",
        f"| Slippage assumption | {r['slippage'] * 100:.2f}% per fill |",
        "",
        "---",
        "*This report is generated for paper trading research only.*  ",
        "*No real trades are placed. Not financial advice.*",
    ]

    return "\n".join(lines)


def save_report(content: str, reports_dir: str, today: date) -> str:
    """Write the Markdown report to reports_dir and return the file path."""
    os.makedirs(reports_dir, exist_ok=True)
    filepath = os.path.join(reports_dir, f"report_{today.isoformat()}.md")
    with open(filepath, "w") as fh:
        fh.write(content)
    log.info("Report saved to %s", filepath)
    return filepath
