"""
signals.py — Momentum signal calculation and candidate ranking.
"""
import logging
from typing import List

import pandas as pd

log = logging.getLogger(__name__)

# Weights for the composite momentum score (must sum to 1.0).
_WEIGHTS = {
    "return_1d": 0.20,
    "return_5d": 0.30,
    "return_20d": 0.30,
    "vol_ratio": 0.20,
}


def calculate_signals(data: pd.DataFrame, tickers: List[str]) -> pd.DataFrame:
    """
    Calculate four momentum signals for every ticker that has enough data.

    Signals returned per ticker:
      - price     : latest adjusted closing price
      - return_1d : 1-session price return
      - return_5d : 5-session price return
      - return_20d: 20-session price return
      - vol_ratio : today's volume divided by 20-session average volume

    Tickers with fewer than 21 bars, or not present in the download, are
    skipped with a warning rather than raising an error.

    Returns a DataFrame with one row per valid ticker.
    """
    close = data["Close"]
    volume = data["Volume"]

    records = []
    for ticker in tickers:
        if ticker not in close.columns:
            log.warning("No price data for %s — skipped", ticker)
            continue

        c = close[ticker].dropna()
        v = volume[ticker].dropna()

        if len(c) < 21:
            log.warning("%s has only %d bars (need 21) — skipped", ticker, len(c))
            continue

        ret_1d = float(c.pct_change(1).iloc[-1])
        ret_5d = float(c.pct_change(5).iloc[-1])
        ret_20d = float(c.pct_change(20).iloc[-1])

        avg_vol_20 = float(v.iloc[-21:-1].mean())
        vol_ratio = float(v.iloc[-1]) / avg_vol_20 if avg_vol_20 > 0 else None

        records.append(
            {
                "ticker": ticker,
                "price": round(float(c.iloc[-1]), 4),
                "return_1d": round(ret_1d, 6),
                "return_5d": round(ret_5d, 6),
                "return_20d": round(ret_20d, 6),
                "vol_ratio": round(vol_ratio, 4) if vol_ratio is not None else None,
            }
        )

    df = pd.DataFrame(records)
    log.info("Signals calculated for %d / %d tickers", len(df), len(tickers))
    return df


def rank_candidates(signals: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Score every ticker by a composite momentum rank and return the top-N.

    Each signal is converted to a 0–1 percentile rank (higher = stronger),
    then multiplied by its weight. The composite score is the weighted sum.
    Tickers with any missing signal value are excluded before ranking.

    Returns a sorted DataFrame (best first) with at most top_n rows.
    """
    required = list(_WEIGHTS.keys())
    df = signals.dropna(subset=required).copy()

    if df.empty:
        log.warning("No tickers survived the signal filter — ranked list is empty")
        return df

    for col, weight in _WEIGHTS.items():
        df[f"rank_{col}"] = df[col].rank(pct=True) * weight

    rank_cols = [f"rank_{c}" for c in _WEIGHTS]
    df["composite_score"] = df[rank_cols].sum(axis=1).round(4)

    ranked = (
        df.sort_values("composite_score", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    log.info("Top-%d candidates: %s", len(ranked), ranked["ticker"].tolist())
    return ranked
