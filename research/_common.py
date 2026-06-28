"""Shared setup for research/ scripts — DRY the ROOT / sys.path / price-panel / score-panel / z
boilerplate that every analysis script repeats.

Usage (from any research/*.py run as `python research/make_foo.py`):

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))   # so `import _common` resolves
    from _common import load_ctx

    ctx = load_ctx()                       # model_v4 by default
    close, Z = ctx.close, ctx.Z            # most scripts need just these

load_ctx() returns a SimpleNamespace with:
    ROOT  — repo root (Path)
    cfg   — built scenario config (universe + merged params)
    px    — full OHLC panel from `start` (Close/Open/High/Low/Volume)
    close — px["Close"]
    S     — cached daily composite score panel (backtests/daily_scores_<scenario>.csv)
    Z     — per-ticker `z_lookback`-day rolling z of S  ((S - mean) / std)
"""
import sys
import warnings
from datetime import date
from pathlib import Path
from types import SimpleNamespace

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import pandas as pd
from backtest import load_config, fetch_backtest_data
from scenarios import load_scenario, build_config


def load_ctx(scenario="model_v4", start=date(2018, 6, 1), end=None, z_lookback=60):
    """Load the common research context (price panel + cached score panel + rolling z)."""
    end = end or date.today()
    cfg = build_config(load_config(ROOT / "config"), load_scenario(scenario))
    px = fetch_backtest_data(cfg["tickers"], start, end)
    S = pd.read_csv(ROOT / "backtests" / f"daily_scores_{scenario}.csv", index_col=0, parse_dates=True)
    Z = (S - S.rolling(z_lookback).mean()) / S.rolling(z_lookback).std()
    return SimpleNamespace(ROOT=ROOT, cfg=cfg, px=px, close=px["Close"], S=S, Z=Z)
