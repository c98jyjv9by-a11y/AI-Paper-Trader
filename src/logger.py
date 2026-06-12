"""
logger.py — Logging setup and trade-record appending.
"""
import csv
import logging
import os
from typing import Any, Dict, List

TRADE_LOG_HEADERS = [
    "date",
    "action",
    "ticker",
    "shares",
    "price_with_slippage",
    "trade_value",
    "reason",
    "pnl",
    "portfolio_value_after",
]


def setup_logging(log_level: str = "INFO") -> None:
    """Configure console logging for the whole application."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def append_trades(trades: List[Dict[str, Any]], filepath: str) -> None:
    """
    Append trade recommendation dicts to the CSV trade log.

    Creates the file with a header row if it does not already exist
    or is empty. Each dict only needs to contain keys from TRADE_LOG_HEADERS;
    extra keys are silently ignored.
    """
    log = logging.getLogger(__name__)
    file_exists = os.path.isfile(filepath) and os.path.getsize(filepath) > 0

    with open(filepath, "a", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=TRADE_LOG_HEADERS, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        for trade in trades:
            writer.writerow(trade)

    log.info("Logged %d trade(s) to %s", len(trades), filepath)
