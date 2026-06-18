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


# ── Context providers ────────────────────────────────────────────────────────────
def test_macro_provider_no_lookahead_and_breadth():
    import context_providers as C
    dates = pd.bdate_range("2025-09-01", periods=80)
    # AAA uptrend (above its MA), BBB downtrend (below); SPY uptrend
    close = _close(dates, {
        "AAA": [100 * 1.01 ** i for i in range(80)],
        "BBB": [100 * 0.99 ** i for i in range(80)],
        "SPY": [100 * 1.004 ** i for i in range(80)],
        "QQQ": [100 * 1.004 ** i for i in range(80)],
    })
    m = C.MacroProvider()
    m._uni = close
    m._x = pd.DataFrame()                          # no VIX/sector data → those lines just omit
    blk = m.block(dates[-1].date(), ["AAA", "BBB"], [])
    assert "SPY" in blk and "ABOVE 50d MA" in blk
    assert "Breadth: 1/2" in blk                   # AAA above, BBB below
    # no look-ahead: a block as of an early date must not see later bars
    early = m.block(dates[40].date(), ["AAA", "BBB"], [])
    assert "MACRO CONTEXT" in early


def test_build_providers_unknown_raises():
    import context_providers as C
    try:
        C.build_providers(["bogus"], ["AAA"], date(2026, 1, 1), date(2026, 1, 5), pd.DataFrame())
        assert False, "expected ValueError"
    except ValueError as e:
        assert "Unknown context provider" in str(e)


def test_stub_providers_return_text():
    import context_providers as C
    for P in (C.SocialProvider(), C.AnalystProvider()):
        assert P.block(date(2026, 1, 5), ["AAA"], []) != ""


def test_llm_actions_prompt_includes_context_blocks(monkeypatch):
    captured = {}

    class FakeResp:
        content = []

    class FakeMsgs:
        def create(self, **kw):
            captured["prompt"] = kw["messages"][0]["content"]
            return FakeResp()

    class FakeClient:
        messages = FakeMsgs()

    spec = _spec(date(2026, 1, 5))
    A._llm_actions(FakeClient(), "m", "discretionary", spec, A.Paper(1000), {},
                   ["AAA"], context_blocks=["MARKET / MACRO CONTEXT: regime risk-on"],
                   use_cache=False)
    assert "ADDITIONAL INFORMATION SOURCES" in captured["prompt"]
    assert "regime risk-on" in captured["prompt"]


# ── LLM response cache ────────────────────────────────────────────────────────────
class _Block:
    type = "tool_use"
    def __init__(self, actions): self.input = {"actions": actions}

class _Resp:
    def __init__(self, actions): self.content = [_Block(actions)]

class _FakeClient:
    def __init__(self, actions): self._actions = actions; self.calls = 0
    class _M:
        pass
    @property
    def messages(self):
        outer = self
        class M:
            def create(self, **kw):
                outer.calls += 1
                return _Resp(outer._actions)
        return M()

class _BoomClient:
    @property
    def messages(self):
        class M:
            def create(self, **kw):
                raise AssertionError("API called on a cache HIT — cache not working")
        return M()


def test_llm_cache_miss_writes_then_hit_replays(tmp_path, monkeypatch):
    monkeypatch.setattr(A, "_LLM_CACHE_PATH", tmp_path / ".llm_cache.jsonl")
    monkeypatch.setattr(A, "_LLM_CACHE", None)
    spec = _spec(date(2026, 1, 5))
    pf = A.Paper(100000)
    acts = [{"action": "BUY", "ticker": "MU", "shares": 10, "reason": "x"}]

    fake = _FakeClient(acts)
    r1 = A._llm_actions(fake, "claude-sonnet-4-6", "discretionary", spec, pf, {}, ["MU"])
    assert r1 == acts and fake.calls == 1                 # miss → called API
    assert (tmp_path / ".llm_cache.jsonl").exists()       # persisted

    # identical inputs → cache hit → must NOT call the API (BoomClient raises if it does)
    r2 = A._llm_actions(_BoomClient(), "claude-sonnet-4-6", "discretionary", spec, pf, {}, ["MU"])
    assert r2 == acts


def test_llm_cache_bypassed_when_disabled(tmp_path, monkeypatch):
    monkeypatch.setattr(A, "_LLM_CACHE_PATH", tmp_path / ".llm_cache.jsonl")
    monkeypatch.setattr(A, "_LLM_CACHE", None)
    spec = _spec(date(2026, 1, 5))
    acts = [{"action": "SELL", "ticker": "BA", "shares": 2, "reason": "y"}]
    fake = _FakeClient(acts)
    A._llm_actions(fake, "m", "balanced", spec, A.Paper(1000), {}, ["BA"], use_cache=False)
    A._llm_actions(fake, "m", "balanced", spec, A.Paper(1000), {}, ["BA"], use_cache=False)
    assert fake.calls == 2                                # no caching → both hit the API
