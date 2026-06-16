"""
test_agent_backtest.py — Agent-vs-packet harness. Offline: no network, no LLM
(uses the deterministic rule deciders and synthetic specs + price panel).
"""
import sys
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import agent_backtest as A


def _spec(d, holdings=None, buys=None, sells=None):
    return {"mark": d, "holdings": holdings or [],
            "next_session": {"buys": buys or [], "sells": sells or [],
                             "buy_reason": "", "sell_reason": ""},
            "observations": ["obs"], "recommendations": ["rec"]}


def _close(dates, prices):
    cols = pd.MultiIndex.from_product([["Close"], list(prices)])
    df = pd.DataFrame({(("Close"), t): prices[t] for t in prices}, index=dates)
    df.columns = cols
    return df["Close"]


# ── Paper accounting ──────────────────────────────────────────────────────────────
def test_paper_buy_sell_cash_and_pnl():
    pf = A.Paper(10_000)
    n = pf.buy("AAA", 50, 100.0)               # $5,000
    assert n == 50 and pf.cash == 5_000
    n = pf.buy("AAA", 1000, 100.0)             # only 50 more affordable ($5,000)
    assert n == 50 and pf.cash == 0 and pf.pos["AAA"]["shares"] == 100
    sold = pf.sell("AAA", 40, 110.0)
    assert sold == 40 and round(pf.cash) == 4_400 and round(pf.realized) == 400
    assert pf.sell("AAA", 999, 110.0) == 60    # clamps to held; position closes
    assert "AAA" not in pf.pos


def test_paper_value_marks_to_prices():
    pf = A.Paper(1_000)
    pf.buy("AAA", 5, 100.0)                     # cash 500, 5 sh
    assert pf.value({"AAA": 120.0}) == 500 + 600


# ── Strict + divergence ───────────────────────────────────────────────────────────
def test_strict_actions_from_queue():
    spec = _spec(date(2026, 1, 5),
                 buys=[{"ticker": "MU", "shares": 10, "price": 100.0, "reason": "mom"}],
                 sells=[{"ticker": "BA", "shares": 5, "price": 50.0, "reason": "stop"}])
    acts = A._strict_actions(spec)
    assert {"action": "SELL", "ticker": "BA", "shares": 5} == {k: acts[0][k] for k in ("action", "ticker", "shares")}
    assert {"action": "BUY", "ticker": "MU", "shares": 10} == {k: acts[1][k] for k in ("action", "ticker", "shares")}
    assert A._divergence(spec, acts) is None    # strict never diverges


def test_divergence_detects_skip_add_resize():
    spec = _spec(date(2026, 1, 5),
                 buys=[{"ticker": "MU", "shares": 10, "price": 100.0}])
    acts = [{"action": "BUY", "ticker": "NVDA", "shares": 3, "reason": "own pick"},
            {"action": "BUY", "ticker": "MU", "shares": 4, "reason": "smaller"}]
    div = A._divergence(spec, acts)
    assert div["added"] == ["BUY NVDA"]
    assert div["resized"] == ["BUY MU"]
    assert div["skipped"] == []


# ── End-to-end simulate (deterministic) ───────────────────────────────────────────
def test_simulate_strict_executes_next_open_fills():
    dates = pd.to_datetime(["2026-01-05", "2026-01-06", "2026-01-07"])
    close = _close(dates, {"MU": [100.0, 110.0, 121.0], "SPY": [100.0, 101.0, 102.0]})
    specs = [
        _spec(date(2026, 1, 5), buys=[{"ticker": "MU", "shares": 10, "price": 100.0, "reason": "mom"}]),
        _spec(date(2026, 1, 6)),
        _spec(date(2026, 1, 7)),
    ]
    r = A._simulate("strict", specs, close, decide=lambda *a: A._strict_actions(a[1]),
                    start_cash=100_000, slippage=0.0)
    # decision on 01-05 fills at 01-06 close (110); 10 sh held into 01-07
    assert r["n_trades"] == 1
    assert r["trades"][0]["date"] == "2026-01-06" and r["trades"][0]["price"] == 110.0
    # final value 01-07: cash (100000 - 1100) + 10*121 = 98900 + 1210 = 100110
    assert round(r["final"]) == 100_110


def test_rule_settings_differentiate_and_diverge():
    dates = pd.to_datetime(["2026-01-05", "2026-01-06"])
    close = _close(dates, {"MU": [100.0, 100.0], "NVDA": [200.0, 200.0], "SPY": [10.0, 10.0]})
    twobuys = _spec(date(2026, 1, 5),
                    buys=[{"ticker": "MU", "shares": 10, "price": 100.0, "value": 1000.0},
                          {"ticker": "NVDA", "shares": 5, "price": 200.0, "value": 1000.0}])
    specs = [twobuys, _spec(date(2026, 1, 6))]

    def dec(setting, spec, pf, prices):
        return A._rule_actions(setting, spec, pf, prices)

    disc = A._simulate("discretionary", specs, close, decide=dec, start_cash=100_000, slippage=0.0)
    # discretionary concentrates -> takes one buy, skips the other -> a divergence is logged
    assert disc["n_divergences"] >= 1
    assert disc["n_trades"] == 1
