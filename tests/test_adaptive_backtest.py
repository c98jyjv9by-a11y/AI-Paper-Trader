"""
test_adaptive_backtest.py — Per-ticker rotating-signal backtest. Synthetic; no network.
"""
import logging
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import adaptive_backtest as ab
from backtest import compute_metrics

logging.disable(logging.CRITICAL)


def _panel(series: dict, n: int, seed=1):
    dates = pd.date_range("2022-01-03", periods=n, freq="B")
    rng = np.random.default_rng(seed)
    cl = pd.DataFrame(series, index=dates)
    vol = pd.DataFrame({t: np.abs(rng.normal(1e6, 1e5, n)) for t in series}, index=dates)
    cl.columns = pd.MultiIndex.from_product([["Close"], cl.columns])
    vol.columns = pd.MultiIndex.from_product([["Volume"], vol.columns])
    return pd.concat([cl, vol], axis=1)


def _cfg(tickers, **over):
    cfg = {"tickers": tickers,
           "portfolio": {"starting_value": 100000.0, "max_position_pct": "auto",
                         "max_total_exposure": 0.90, "max_new_trades_per_day": 5},
           "risk": {"stop_loss": 0.10, "take_profit": 0.10, "max_holding_days": 30, "slippage": 0.001},
           "signals": {"top_candidates": 10}}
    for k, v in over.items():
        sec, key = k.split(".", 1)
        cfg.setdefault(sec, {})[key] = v
    return cfg


_P = {"rebalance_days": 5, "lookback_days": 63, "top_n": 5, "min_edge": 0.0}


class TestSignalsAndEdge:
    def test_build_signals_are_boolean_frames(self):
        data = _panel({"A": 100 * 1.001 ** np.arange(300), "B": 100 * 0.999 ** np.arange(300)}, 300)
        sigs = ab.build_signals(data["Close"], data["Volume"])
        assert set(sigs) == {"trend_50", "trend_20", "mom20_pos", "dip_5", "near_52w_high"}
        assert sigs["trend_50"].dtypes.eq(bool).all()

    def test_recent_edge_captures_uptrend_when_on(self):
        n = 80
        close = 100 * 1.01 ** np.arange(n)
        fwd1 = np.append(close[1:] / close[:-1] - 1.0, np.nan)
        on = np.ones(n, dtype=bool)
        edge = ab._recent_edge(on, fwd1, 10, 70)
        assert edge > 0                       # always-on in a steady uptrend → positive
        off = np.zeros(n, dtype=bool)
        assert ab._recent_edge(off, fwd1, 10, 70) == 0.0   # never on → flat


class TestSelection:
    def _sigfwd(self, data, tickers):
        close = data["Close"]
        raw = ab.build_signals(close, data["Volume"])
        sig = {nm: {t: fr.shift(1)[t].to_numpy() for t in tickers} for nm, fr in raw.items()}
        arr = {t: close[t].to_numpy() for t in tickers}
        fwd1 = {t: np.append(arr[t][1:] / arr[t][:-1] - 1.0, np.nan) for t in tickers}
        return sig, fwd1

    def test_uptrend_qualifies_decline_excluded(self):
        n = 300
        data = _panel({"UP": 100 * 1.0015 ** np.arange(n), "DOWN": 100 * 0.997 ** np.arange(n)}, n)
        sig, fwd1 = self._sigfwd(data, ["UP", "DOWN"])
        targets = ab.select_targets(sig, fwd1, ["UP", "DOWN"], t=250, lookback=63, top_n=5, min_edge=0.0)
        names = [tk for tk, _, _ in targets]
        assert "UP" in names and "DOWN" not in names

    def test_respects_top_n(self):
        n = 300
        series = {f"T{i}": 100 * (1.001 + 0.0001 * i) ** np.arange(n) for i in range(8)}
        data = _panel(series, n)
        tickers = list(series)
        sig, fwd1 = self._sigfwd(data, tickers)
        targets = ab.select_targets(sig, fwd1, tickers, t=250, lookback=63, top_n=3, min_edge=0.0)
        assert len(targets) <= 3

    def test_no_lookahead_future_bar_does_not_change_selection(self):
        # _recent_edge only reads [a, t]; a future fwd1 value must not affect selection at t.
        n = 200
        data = _panel({"A": 100 * 1.001 ** np.arange(n), "B": 100 * np.cumprod(1 + np.zeros(n))}, n)
        sig, fwd1 = self._sigfwd(data, ["A", "B"])
        base = ab.select_targets(sig, fwd1, ["A", "B"], t=120, lookback=63, top_n=5, min_edge=0.0)
        fwd1["A"] = fwd1["A"].copy(); fwd1["A"][150] = 5.0      # spike a FUTURE bar
        after = ab.select_targets(sig, fwd1, ["A", "B"], t=120, lookback=63, top_n=5, min_edge=0.0)
        assert base == after


class TestEndToEnd:
    def test_standard_schema_and_metrics(self):
        n = 500
        rng = np.random.default_rng(2)
        series = {"UP": 100 * 1.0015 ** np.arange(n), "DOWN": 100 * 0.997 ** np.arange(n)}
        for t in ["N1", "N2", "SPY", "QQQ"]:
            series[t] = 100 * np.cumprod(1 + rng.normal(0.0004, 0.014, n))
        data = _panel(series, n)
        cfg = _cfg(["UP", "DOWN", "N1", "N2"])
        dates = data["Close"].index
        trades, equity, pos, rot = ab.run_adaptive(cfg, data, dates[80].date(), dates[-1].date(), _P)
        # equity_df carries the columns compute_metrics needs (benchmarks included)
        for c in ["total_portfolio_value", "open_positions_value", "cash", "daily_return",
                  "equal_weight_cumulative_return"]:
            assert c in equity.columns
        m = compute_metrics(trades, equity, pos, cfg, dates[80].date(), dates[-1].date())
        assert "total_return" in m and "equal_weight_return" in m
        # the steady uptrender is selected; the decliner is not
        held = {tk for r in rot for tk in r["assignments"]}
        assert "UP" in held and "DOWN" not in held

    def test_all_decline_goes_to_cash(self):
        n = 400
        series = {"D1": 100 * 0.996 ** np.arange(n), "D2": 100 * 0.997 ** np.arange(n),
                  "SPY": 100 * 0.998 ** np.arange(n), "QQQ": 100 * 0.998 ** np.arange(n)}
        data = _panel(series, n)
        cfg = _cfg(["D1", "D2"])
        dates = data["Close"].index
        trades, equity, pos, rot = ab.run_adaptive(cfg, data, dates[80].date(), dates[-1].date(), _P)
        # mostly cash: few/no positions held; total portfolio ~ flat (no big losses)
        assert all(r["n_held_target"] <= cfg["portfolio"]["max_new_trades_per_day"] for r in rot)
        m = compute_metrics(trades, equity, pos, cfg, dates[80].date(), dates[-1].date())
        assert m["total_return"] > -0.20          # cash discipline avoids riding declines down

    def test_rotation_section_renders(self):
        n = 400
        rng = np.random.default_rng(5)
        series = {t: 100 * np.cumprod(1 + rng.normal(0.0006, 0.013, n)) for t in ["A", "B", "C", "SPY", "QQQ"]}
        data = _panel(series, n)
        cfg = _cfg(["A", "B", "C"])
        dates = data["Close"].index
        trades, equity, pos, rot = ab.run_adaptive(cfg, data, dates[80].date(), dates[-1].date(), _P)
        md = ab.rotation_section(rot, equity, trades, _P)
        assert "Signal Rotation Log" in md and "Signal usage" in md
        assert "$nan" not in md
