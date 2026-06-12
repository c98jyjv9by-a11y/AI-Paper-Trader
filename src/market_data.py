"""
market_data.py — Fetch OHLCV price data via yfinance.
"""
import logging
from typing import List

import pandas as pd
import yfinance as yf

log = logging.getLogger(__name__)


def fetch_prices(tickers: List[str], period: str = "60d", interval: str = "1d") -> pd.DataFrame:
    """
    Download daily OHLCV data for every ticker in the universe.

    Returns a DataFrame with two-level (MultiIndex) columns:
        level 0 → price field  (Close, Open, High, Low, Volume)
        level 1 → ticker symbol

    Example access:
        data["Close"]["AAPL"]   → Series of closing prices for AAPL
        data["Close"]           → DataFrame with one column per ticker
    """
    log.info("Downloading price data: %d tickers, period=%s", len(tickers), period)
    data = yf.download(
        tickers,
        period=period,
        interval=interval,
        auto_adjust=True,   # 'Close' already contains split/dividend-adjusted prices
        progress=False,
    )

    if data.empty:
        raise RuntimeError(
            "yfinance returned no data. "
            "Check your internet connection and ticker list."
        )

    # yfinance returns flat columns when only one ticker is passed as a string.
    # We always pass a list, but guard here anyway so the rest of the code can
    # rely on MultiIndex columns unconditionally.
    if not isinstance(data.columns, pd.MultiIndex):
        data.columns = pd.MultiIndex.from_product([data.columns, tickers[:1]])

    log.info("Price data shape: %s rows × %s columns", *data.shape)
    return data


def get_latest_prices(data: pd.DataFrame, tickers: List[str]) -> pd.Series:
    """
    Return the most recent closing price for each ticker as a Series
    indexed by ticker symbol.
    """
    close = data["Close"]
    available = [t for t in tickers if t in close.columns]
    return close.iloc[-1][available]
