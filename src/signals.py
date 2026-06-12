"""
signals.py — Momentum signal calculation and candidate ranking.
"""
import logging
from typing import List

import numpy as np
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

        # Work on the raw numpy arrays: scalar indexing here is far cheaper than
        # building full pct_change Series just to read the last value, and this is
        # called once per ticker per bar across an entire backtest.
        c = close[ticker].dropna().to_numpy()
        v = volume[ticker].dropna().to_numpy()

        if len(c) < 21:
            log.warning("%s has only %d bars (need 21) — skipped", ticker, len(c))
            continue

        # pct_change(n).iloc[-1] == c[-1] / c[-1-n] - 1
        ret_1d = float(c[-1] / c[-2] - 1)
        ret_5d = float(c[-1] / c[-6] - 1)
        ret_20d = float(c[-1] / c[-21] - 1)

        avg_vol_20 = float(v[-21:-1].mean())
        vol_ratio = float(v[-1]) / avg_vol_20 if avg_vol_20 > 0 else None

        # Realized 20-day volatility (std of the last 20 daily returns) and
        # volatility-adjusted momentum (return per unit of risk).
        daily_rets_20 = c[-21:][1:] / c[-21:][:-1] - 1.0
        realized_vol_20d = float(np.std(daily_rets_20))
        vol_adj_mom_20d = ret_20d / realized_vol_20d if realized_vol_20d > 0 else None

        records.append(
            {
                "ticker": ticker,
                "price": round(float(c[-1]), 4),
                "return_1d": round(ret_1d, 6),
                "return_5d": round(ret_5d, 6),
                "return_20d": round(ret_20d, 6),
                "vol_ratio": round(vol_ratio, 4) if vol_ratio is not None else None,
                "realized_vol_20d": round(realized_vol_20d, 6),
                "vol_adj_mom_20d": round(vol_adj_mom_20d, 6) if vol_adj_mom_20d is not None else None,
            }
        )

    df = pd.DataFrame(records)
    log.info("Signals calculated for %d / %d tickers", len(df), len(tickers))
    return df


def rank_candidates(signals: pd.DataFrame, top_n: int = 10, weights: dict = None) -> pd.DataFrame:
    """
    Score every ticker by a composite momentum rank and return the top-N.

    Each signal is converted to a 0–1 percentile rank (higher = stronger),
    then multiplied by its weight. The composite score is the weighted sum.
    Tickers with any missing signal value are excluded before ranking.

    weights: optional dict overriding _WEIGHTS (used by sensitivity analysis).
    Returns a sorted DataFrame (best first) with at most top_n rows.
    """
    effective_weights = weights if weights is not None else _WEIGHTS
    required = list(effective_weights.keys())
    df = signals.dropna(subset=required).copy()

    if df.empty:
        log.warning("No tickers survived the signal filter — ranked list is empty")
        return df

    for col, weight in effective_weights.items():
        df[f"rank_{col}"] = df[col].rank(pct=True) * weight

    rank_cols = [f"rank_{c}" for c in effective_weights]
    df["composite_score"] = df[rank_cols].sum(axis=1).round(4)

    ranked = (
        df.sort_values("composite_score", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    log.info("Top-%d candidates: %s", len(ranked), ranked["ticker"].tolist())
    return ranked
