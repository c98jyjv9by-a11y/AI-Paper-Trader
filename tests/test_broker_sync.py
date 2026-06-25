"""test_broker_sync.py — pure target-book logic (offline; no broker/network).

Covers the top-N target builder used by the top_n-mode broker accounts (e.g. topten):
size each of the N highest-scored names at size_pct of equity, accumulate (never trim a held
winner), and drop names that fall out of the top N (reconcile then sells them to 0)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import broker_sync as bs


def test_topn_targets_sizes_each_name_at_size_pct_of_equity():
    intended = [{"ticker": "MU", "price": 100.0}, {"ticker": "NVDA", "price": 200.0}]
    targets, refs = bs.topn_targets(intended, equity=100_000.0, current={}, size_pct=0.085)
    # 8.5% of 100k = $8,500 per name -> 85 sh @ $100, 42 sh @ $200 (whole shares, floor)
    assert targets == {"MU": 85, "NVDA": 42}
    assert refs == {"MU": 100.0, "NVDA": 200.0}


def test_topn_targets_accumulates_never_trims_held_winner():
    intended = [{"ticker": "MU", "price": 100.0}]
    # already hold 200 sh; the 8.5% target is only 85 sh -> keep the larger held size
    targets, _ = bs.topn_targets(intended, equity=100_000.0, current={"MU": 200}, size_pct=0.085)
    assert targets["MU"] == 200


def test_topn_targets_omits_dropouts_so_reconcile_sells_them():
    intended = [{"ticker": "MU", "price": 100.0}]
    # AMD held but no longer in the top-N -> absent from targets; reconcile vs current sells it
    targets, _ = bs.topn_targets(intended, equity=100_000.0, current={"MU": 50, "AMD": 30},
                                 size_pct=0.085)
    assert "AMD" not in targets
    orders = __import__("broker_adapter").build_reconcile_orders(
        targets, {"MU": 50, "AMD": 30},
        prices={"MU": {"mid": 100.0}, "AMD": {"mid": 10.0}},
        collars={}, asof="2026-06-22")
    amd = [o for o in orders if o["symbol"] == "AMD"]
    assert amd and amd[0]["side"] == "sell" and amd[0]["qty"] == "30"


def test_topn_targets_skips_names_without_a_price():
    intended = [{"ticker": "MU", "price": 100.0}, {"ticker": "BAD", "price": None},
                {"ticker": "ZERO", "price": 0.0}]
    targets, refs = bs.topn_targets(intended, equity=100_000.0, current={}, size_pct=0.085)
    assert set(targets) == {"MU"} and "BAD" not in refs and "ZERO" not in refs


def test_equal_weight_targets_splits_equity_evenly():
    prices = {"A": 100.0, "B": 200.0, "C": 50.0, "D": 25.0}
    targets, refs = bs.equal_weight_targets(prices, equity=100_000.0, current={}, gross=1.0)
    # 4 names -> $25,000 each: 250 @ $100, 125 @ $200, 500 @ $50, 1000 @ $25
    assert targets == {"A": 250, "B": 125, "C": 500, "D": 1000}
    assert refs == prices


def test_equal_weight_targets_respects_gross_and_floors_to_whole_shares():
    prices = {"A": 300.0, "B": 300.0}
    # gross 0.9 -> $45,000 each -> floor(45000/300)=150 sh; never exceeds buying power
    targets, _ = bs.equal_weight_targets(prices, equity=100_000.0, current={}, gross=0.9)
    assert targets == {"A": 150, "B": 150}


def test_score_gate_sizes_gated_names_at_size_pct():
    # score_gate reuses topn_targets for sizing: the adapter pre-filters to score >= min_score,
    # so here we just confirm each gated name is sized at size_pct of equity.
    gated = [{"ticker": "ARM", "price": 400.0}, {"ticker": "MRVL", "price": 300.0}]
    targets, _ = bs.topn_targets(gated, equity=100_000.0, current={}, size_pct=0.085)
    # 8.5% of 100k = $8,500 -> floor(8500/400)=21 sh, floor(8500/300)=28 sh
    assert targets == {"ARM": 21, "MRVL": 28}


def test_equal_weight_targets_accumulates_and_drops_absent_names():
    prices = {"A": 100.0}  # B fell out of the source book -> not priced here
    targets, _ = bs.equal_weight_targets(prices, equity=100_000.0,
                                         current={"A": 9999, "B": 30}, gross=1.0)
    assert targets["A"] == 9999          # held more than target -> never trimmed
    assert "B" not in targets            # absent -> reconcile sells it to 0


class _RbCli:
    def __init__(self, cash=60_000.0): self._cash = cash
    def account(self): return {"equity": 100_000.0, "cash": self._cash}
    def latest_prices(self, syms): return {s: {"mid": 100.0} for s in syms}   # everything at $100


def _fires(monkeypatch, dollars=50_000.0):
    import rebound_overlay
    monkeypatch.setattr(rebound_overlay, "recommend",
                        lambda **k: {"fires": True, "rebound_dollars": dollars, "instrument": "TQQQ"})


def test_rebound_funds_from_cash_when_sufficient(monkeypatch):
    monkeypatch.setattr(bs, "load_manifest", lambda n: {"rebound": True})
    _fires(monkeypatch)
    t, _ = bs._rebound_target("topten", _RbCli(cash=60_000.0), {"AAPL": 10}, {})
    assert t["TQQQ"] == 500 and t["AAPL"] == 10        # 50k from cash, book untouched, no trim


def test_rebound_trims_two_lowest_5d_avg_score(monkeypatch):
    monkeypatch.setattr(bs, "load_manifest", lambda n: {"rebound": True, "rebound_funding": "trim"})
    monkeypatch.setattr(bs, "_avg_scores", lambda s="model_v4", n=5: {"A": 0.20, "B": 0.30, "C": 0.90})
    _fires(monkeypatch, dollars=50_000.0)
    # cash 10k -> avail 9.5k; shortfall 40.5k; exit the 2 lowest-avg (A fully 30k, B 106 sh) -> covers it
    t, _ = bs._rebound_target("topten", _RbCli(cash=10_000.0), {"A": 300, "B": 300, "C": 300}, {})
    assert t["A"] == 0 and t["B"] == 194              # two weakest exited (A full, B partial)
    assert t["C"] == 300                              # 3rd-weakest untouched -> capped at 2 exits
    assert t["TQQQ"] == 500                           # full 50k funded by cash + 2 exits


def test_rebound_trim_capped_at_two_exits(monkeypatch):
    monkeypatch.setattr(bs, "load_manifest", lambda n: {"rebound": True, "rebound_funding": "trim"})
    monkeypatch.setattr(bs, "_avg_scores", lambda s="model_v4", n=5: {"A": 0.2, "B": 0.3, "C": 0.4})
    _fires(monkeypatch, dollars=50_000.0)
    # cash 5k -> avail 4.75k; positions 10k each; 2 full exits (20k) + cash < 50k -> overlay CAPPED
    t, _ = bs._rebound_target("topten", _RbCli(cash=5_000.0), {"A": 100, "B": 100, "C": 100}, {})
    assert t["A"] == 0 and t["B"] == 0                # both weakest fully exited (cap 2)
    assert t["C"] == 100                              # 3rd untouched
    assert t["TQQQ"] == 247                           # capped at (4.75k + 20k) / 100


def test_rebound_cash_mode_caps_no_trim(monkeypatch):
    monkeypatch.setattr(bs, "load_manifest", lambda n: {"rebound": True, "rebound_funding": "cash"})
    _fires(monkeypatch, dollars=50_000.0)
    t, _ = bs._rebound_target("topten", _RbCli(cash=10_000.0), {"AAPL": 300}, {})
    assert t["TQQQ"] == 95 and t["AAPL"] == 300        # cash mode -> cap at 95% of 10k; book untouched


def test_rebound_no_fire_leaves_no_tqqq(monkeypatch):
    import rebound_overlay
    monkeypatch.setattr(bs, "load_manifest", lambda n: {"rebound": True})
    monkeypatch.setattr(rebound_overlay, "recommend", lambda **k: {"fires": False, "rebound_dollars": 0.0})
    t, _ = bs._rebound_target("topten", _RbCli(), {"AAPL": 10}, {})
    assert "TQQQ" not in t                              # absent -> reconcile flattens any held TQQQ next session


def test_rebound_opt_out_via_manifest(monkeypatch):
    monkeypatch.setattr(bs, "load_manifest", lambda n: {"rebound": False})
    _fires(monkeypatch)
    t, _ = bs._rebound_target("topten", _RbCli(cash=10_000.0), {"AAPL": 10}, {})
    assert "TQQQ" not in t                              # rebound:false -> overlay disabled


class _SrCli:
    def __init__(self, equity=100_000.0): self._eq = equity
    def account(self): return {"equity": self._eq}
    def latest_prices(self, syms): return {s: {"mid": 100.0} for s in syms}


def test_score_rebalance_picks_top_n_equal_weight(monkeypatch):
    monkeypatch.setattr(bs, "load_manifest", lambda n: {"scenario": "model_v4"})
    monkeypatch.setattr(bs, "_lookback_avg_scores", lambda s, lb: {"A": 0.9, "B": 0.8, "C": 0.7, "D": 0.2})
    tm = {"kind": "score_rebalance", "lookback_days": 60, "top_n": 2, "bottom_n": 0,
          "rebalance": "monthly", "gross": 0.90}
    t, r = bs._score_rebalance_targets("monthly10", _SrCli(), {}, tm)     # empty book -> always rebalances
    assert t == {"A": 450, "B": 450}                    # 0.9*100k/2 = 45k each / $100
    assert set(r) == {"A", "B"}


def test_score_rebalance_combo_includes_bottom(monkeypatch):
    monkeypatch.setattr(bs, "load_manifest", lambda n: {"scenario": "model_v4"})
    monkeypatch.setattr(bs, "_lookback_avg_scores", lambda s, lb: {"A": 0.9, "B": 0.8, "C": 0.7, "D": 0.2})
    tm = {"kind": "score_rebalance", "lookback_days": 60, "top_n": 2, "bottom_n": 1,
          "rebalance": "weekly", "gross": 0.90}
    t, _ = bs._score_rebalance_targets("combo20", _SrCli(), {}, tm)
    assert t == {"A": 300, "B": 300, "D": 300}          # 3 names (2 top + 1 bottom), 30k each


def test_score_rebalance_holds_off_rebalance_day(monkeypatch):
    monkeypatch.setattr(bs, "load_manifest", lambda n: {"scenario": "model_v4"})
    monkeypatch.setattr(bs, "_recent_trading_days", lambda: ["d1", "d2"])
    monkeypatch.setattr(bs, "_is_rebalance_day", lambda f, c: False)
    called = []
    monkeypatch.setattr(bs, "_lookback_avg_scores", lambda s, lb: called.append(1) or {"A": 0.9})
    tm = {"kind": "score_rebalance", "rebalance": "monthly", "top_n": 10}
    t, _ = bs._score_rebalance_targets("monthly10", _SrCli(), {"A": 450, "B": 450}, tm)
    assert t == {"A": 450, "B": 450}                    # held unchanged off-rebalance
    assert not called                                   # and scores NOT recomputed


def test_score_rebalance_split_top_monthly_bottom_5d(monkeypatch):
    import pandas as pd
    monkeypatch.setattr(bs, "load_manifest", lambda n: {"scenario": "model_v4"})
    monkeypatch.setattr(bs, "_recent_trading_days",
                        lambda: pd.to_datetime(["2026-06-01", "2026-06-22", "2026-06-24"]))
    monkeypatch.setattr(bs, "_is_rebalance_day", lambda f, c: True)
    seen = {}

    def fake(scenario, lb, as_of=None):
        seen[lb] = as_of                                  # record which anchor each sleeve used
        if lb >= 60:                                      # TOP sleeve: 60D, anchored to month start
            return {"A": 0.9, "B": 0.8, "C": 0.7, "D": 0.2}
        return {"A": 0.6, "B": 0.5, "X": 0.1, "Y": 0.05}  # BOTTOM sleeve: 5D, as-of today
    monkeypatch.setattr(bs, "_lookback_avg_scores", fake)
    tm = {"kind": "score_rebalance", "rebalance": "weekly", "gross": 0.90,
          "top_n": 2, "top_lookback_days": 60, "top_refresh": "monthly",
          "bottom_n": 2, "bottom_lookback_days": 5, "bottom_refresh": "weekly"}
    t, _ = bs._score_rebalance_targets("combo20", _SrCli(), {}, tm)
    assert set(t) == {"A", "B", "Y", "X"}                 # top-2 by 60D (A,B) + bottom-2 by 5D (Y,X)
    assert all(v == 225 for v in t.values())              # 4 names, 0.9*100k/4 = 22.5k / $100
    assert str(seen[60].date()) == "2026-06-01"           # top anchored to first trading day of the month
    assert seen[5] is None                                # bottom uses today (no anchor)


def test_combo_top_held_on_non_monthly_week(monkeypatch):
    import pandas as pd
    monkeypatch.setattr(bs, "load_manifest", lambda n: {"scenario": "model_v4"})
    # today = Mon 2026-06-22: a WEEKLY rebalance, but NOT the month's first week (anchor 06-01 is 3 wks back)
    monkeypatch.setattr(bs, "_recent_trading_days",
                        lambda: pd.to_datetime(["2026-06-01", "2026-06-15", "2026-06-22"]))
    monkeypatch.setattr(bs, "_is_rebalance_day", lambda f, c: True)

    def fake(scenario, lb, as_of=None):
        if lb >= 60:
            return {"A": 0.9, "B": 0.8}                  # top sleeve
        return {"Y": 0.05, "Z": 0.06, "X": 0.5}          # bottom sleeve (lowest two = Y, Z)
    monkeypatch.setattr(bs, "_lookback_avg_scores", fake)
    tm = {"kind": "score_rebalance", "rebalance": "weekly", "gross": 0.90,
          "top_n": 2, "top_lookback_days": 60, "top_refresh": "monthly",
          "bottom_n": 2, "bottom_lookback_days": 5}
    cur = {"A": 999, "B": 111, "W": 50}                  # top held at drifted shares; W = stale old bottom
    t, _ = bs._score_rebalance_targets("combo20", _SrCli(), cur, tm)
    assert t["A"] == 999 and t["B"] == 111              # TOP kept untouched on a non-monthly week
    assert t["Y"] == 225 and t["Z"] == 225              # BOTTOM re-sized weekly (0.9*100k/4 = 22.5k/$100)
    assert "W" not in t                                  # stale bottom name flattened


class _FlatCli:
    def __init__(self, qty=313, open_orders=None):
        self.qty = qty
        self._open = open_orders if open_orders is not None else \
            [{"id": "o1", "symbol": "TQQQ"}, {"id": "o2", "symbol": "AAPL"}]
        self.canceled, self.submitted = [], []
    def orders(self, status="closed"): return self._open
    def positions(self):
        return [{"ticker": "TQQQ", "qty": float(self.qty), "price": 70.0}] if self.qty else []
    def latest_prices(self, syms): return {s: {"bid": 70.0, "mid": 70.0} for s in syms}
    def cancel(self, oid, confirm=True):
        if confirm: self.canceled.append(oid)
    def submit(self, order, confirm=False):
        self.submitted.append(order)
        return {"id": "x1"} if confirm else {"note": "dry-run"}


def test_flatten_overlay_cancels_then_sells_full_position():
    cli = _FlatCli(qty=313)
    r = bs.flatten_overlay("topten", cli=cli, submit=True)
    assert cli.canceled == ["o1"]                          # only the TQQQ working order (not AAPL)
    o = cli.submitted[0]
    assert o["symbol"] == "TQQQ" and o["side"] == "sell" and o["qty"] == "313"
    assert o["extended_hours"] is True and o["limit_price"] == round(70 * 0.97, 2)
    assert r["qty"] == 313 and r["submitted"] is True and r["canceled"] == 1


def test_flatten_overlay_no_position_no_sell():
    cli = _FlatCli(qty=0)
    r = bs.flatten_overlay("topten", cli=cli, submit=True)
    assert cli.canceled == ["o1"]                          # still cancels the stale TQQQ order
    assert cli.submitted == [] and r["qty"] == 0 and r["submitted"] is False


class _ZrCli:
    def account(self): return {"equity": 100_000.0}
    def latest_prices(self, syms): return {s: {"mid": 100.0} for s in syms}


def test_zscore_reversal_buys_lowest_n(monkeypatch):
    monkeypatch.setattr(bs, "load_manifest", lambda n: {"scenario": "model_v4"})
    monkeypatch.setattr(bs, "_recent_trading_days", lambda: ["d1", "d2"])
    monkeypatch.setattr(bs, "_qqq_above_ma", lambda ma: True)                 # uptrend -> trade
    monkeypatch.setattr(bs, "_zscore_reversal_signal",
                        lambda s, zl, aw: {"A": 0.9, "B": 0.5, "C": -0.5, "D": -0.9})
    tm = {"kind": "zscore_reversal", "n": 2, "rebalance": "biweekly", "regime_ma": 200, "gross": 0.90}
    t, _ = bs._zscore_reversal_targets("zrev", _ZrCli(), {}, tm)
    assert set(t) == {"C", "D"}                  # the 2 LOWEST-signal (most-fallen) names
    assert all(v == 450 for v in t.values())     # 0.9*100k/2 = 45k / $100


def test_zscore_reversal_regime_off_goes_cash(monkeypatch):
    monkeypatch.setattr(bs, "load_manifest", lambda n: {"scenario": "model_v4"})
    monkeypatch.setattr(bs, "_recent_trading_days", lambda: ["d1", "d2"])
    monkeypatch.setattr(bs, "_is_rebalance_day", lambda f, c: True)
    monkeypatch.setattr(bs, "_qqq_above_ma", lambda ma: False)                # QQQ below MA -> downtrend
    seen = []
    monkeypatch.setattr(bs, "_zscore_reversal_signal", lambda s, zl, aw: seen.append(1) or {"A": 0.1})
    tm = {"kind": "zscore_reversal", "n": 10, "rebalance": "biweekly", "regime_ma": 200}
    t, _ = bs._zscore_reversal_targets("zrev", _ZrCli(), {"X": 50}, tm)
    assert t == {}                               # cash -> reconcile flattens the held book
    assert not seen                              # signal not even computed when regime is off


def test_sanitize_quotes_one_sided_falls_back_to_close():
    prices = {"GE": {"bid": 344.0, "ask": 0.0, "mid": 344.0}}        # missing ask (after-hours)
    out = bs._sanitize_quotes(prices, {"GE": 365.88})
    assert out["GE"]["mid"] == 365.88 and out["GE"].get("_quote_fallback")


def test_sanitize_quotes_sane_quote_unchanged():
    prices = {"AAPL": {"bid": 199.9, "ask": 200.1, "mid": 200.0}}
    out = bs._sanitize_quotes(prices, {"AAPL": 198.0})              # 1% off close -> trust the quote
    assert out["AAPL"]["mid"] == 200.0 and not out["AAPL"].get("_quote_fallback")


def test_sanitize_quotes_stale_two_sided_falls_back():
    prices = {"X": {"bid": 50.0, "ask": 50.2, "mid": 50.1}}          # mid 50 vs close 100 -> >25% stale
    out = bs._sanitize_quotes(prices, {"X": 100.0})
    assert out["X"]["mid"] == 100.0 and out["X"].get("_quote_fallback")


def test_sanitize_quotes_no_close_leaves_quote():
    prices = {"Y": {"bid": 10.0, "ask": 0.0, "mid": 10.0}}
    out = bs._sanitize_quotes(prices, {})                            # no reference close -> don't touch
    assert out["Y"]["mid"] == 10.0 and not out["Y"].get("_quote_fallback")
