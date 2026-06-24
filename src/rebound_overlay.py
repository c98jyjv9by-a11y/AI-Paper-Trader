"""
rebound_overlay.py — standalone 1-day "down-shock + momentum-crash" REBOUND overlay for model_v4.

The mirror image of hedge_overlay.py: it sits ON TOP of model_v4 and never modifies it. On a
confirmed sell-off where the strategy's OWN momentum signal is inverting (top losing to bottom),
buy TQQQ (+3x QQQ) for the 1-day rebound.

    RULE (decide at close T, hold T+1 only, exit at close T+1):
      FIRE (combo):  qqq_trl_1d <= -2.5%  AND  spread_trl_1d < 0  AND  z(qqq_vol_trl_5d) >= 0.25
      CRASH (full):  + top10_trl_1d <= -3%  AND  bottom10_trl_1d > 0   (escalate size, if tiered)
      then BUY TQQQ at `weight` of the held book (crash -> `weight_cap`), hold 1 day, exit next close.

Tuned (make_model_v4_rebound_sweep.py + make_volfactor_compare.py): QQQ 5d-vol gate is the only robust
region — ΔSharpe ~+0.06 full / +0.07 train / +0.03 test, MaxDD -39% vs -40%, worst-day unchanged at -9%
(NO tail blowout), ~3-4 fires/yr, 65% win. (QQQ vol beats SPY here by catching Nasdaq-concentrated crashes.) The `spread < 0` filter is what selects the mean-reverting setups and skips the
trend-continuation knives that wreck a naive down-shock buy. Honest scope: a SMALL, robust, tail-neutral
Sharpe-adder — return-additive leverage with a selectivity filter, not transformative alpha.

Everything is in ReboundConfig; retune/swap WITHOUT touching the model.

    python src/rebound_overlay.py                                  # backtest summary + artifacts
    python src/rebound_overlay.py --recommend --qqq -0.03 --spread -0.01 --spy-vol-z 0.9
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, asdict
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).parent.parent
PANEL = ROOT / "backtests" / "model_v4_timeseries.csv"
OUT_PREFIX = ROOT / "backtests" / "rebound_overlay_model_v4"


@dataclass
class ReboundConfig:
    # ---- trigger: COMBO = down-shock AND momentum-signal-negative AND vol-up (all configurable) ----
    down_factor: str = "qqq_trl_1d"        # the sell-off measure (today's QQQ move)
    down_threshold: float = -0.025         # FIRE when QQQ 1-day <= -2.5% (tuned)
    signal_factor: str = "spread_trl_1d"   # the strategy's momentum signal (top10 - bottom10)
    signal_threshold: float = 0.0          # FIRE only when signal < 0 (momentum inverting) -- the key filter
    vol_factor: str = "qqq_vol_trl_5d"     # vol-up signal — QQQ 5d vol (catches Nasdaq-concentrated
                                           # crashes the broad SPY-vol gate misses; SPY≈QQQ for the hedge)
    vol_z_threshold: float = 0.25          # FIRE when z(vol_factor) >= 0.25 (re-tuned for QQQ vol; the
                                           # QQQ-vol edge improves as the gate loosens, ~+0.06 ΔSharpe)
    vol_lookback: int = 63
    # ---- optional crash escalation -> full size ----
    tiered: bool = False                   # True: escalate to weight_cap on a true momentum crash
    crash_top_factor: str = "top10_trl_1d"
    crash_bottom_factor: str = "bottom10_trl_1d"
    crash_top_threshold: float = -0.03     # top10 <= -3% AND bottom10 > 0 -> crash tier
    # ---- rebound sleeve ----
    instrument: str = "TQQQ"               # the long +3x ETF actually bought / shown / traded
    instr_fwd_col: str = "tqqq_fwd_1d"     # next-day instrument return (added by run() from prices)
    weight: float = 0.50                   # sleeve notional as a fraction of the held book (tuned)
    weight_cap: float = 0.60               # crash-tier / max sleeve notional
    cost_bps: float = 10.0                 # round-trip cost per on-day, bps of the traded sleeve notional
    # ---- accounting ----
    book_col: str = "book_fwd_1d"
    book_ret_col: str = "book_trl_1d"
    covid_start: str = "2020-04-01"
    oos_start: str = "2024-01-01"


def _zscore(s: pd.Series, lookback: int) -> pd.Series:
    """Trailing z-score using only data known BEFORE today (shift 1)."""
    return (s - s.rolling(lookback).mean().shift(1)) / s.rolling(lookback).std().shift(1)


def _gates(df: pd.DataFrame, cfg: ReboundConfig):
    """Combo trigger -> (combo fire mask, crash mask, effective per-date sleeve weight series)."""
    down = df[cfg.down_factor]
    sig = df[cfg.signal_factor]
    volz = _zscore(df[cfg.vol_factor], cfg.vol_lookback)
    combo = ((down <= cfg.down_threshold) & (sig < cfg.signal_threshold)
             & (volz >= cfg.vol_z_threshold)).fillna(False)
    crash = (combo & (df.get(cfg.crash_top_factor, pd.Series(np.nan, index=df.index)) <= cfg.crash_top_threshold)
             & (df.get(cfg.crash_bottom_factor, pd.Series(np.nan, index=df.index)) > 0)).fillna(False)
    w_eff = pd.Series(0.0, index=df.index)
    w_eff[combo] = cfg.weight
    if cfg.tiered:
        w_eff[crash] = cfg.weight_cap
    return combo, crash, w_eff


def build_overlay(df: pd.DataFrame, cfg: ReboundConfig) -> pd.DataFrame:
    """Signal, sleeve weight, rebound PnL, overlaid daily return. Read-only on df; requires the
    instrument's next-day return column `cfg.instr_fwd_col` (run() adds it from prices)."""
    book = df[cfg.book_col]
    combo, crash, w_eff = _gates(df, cfg)
    instr_ret = df[cfg.instr_fwd_col]
    rt = cfg.cost_bps / 1e4
    sleeve = np.where(combo, w_eff * instr_ret - w_eff * rt, 0.0)
    out = pd.DataFrame(index=df.index)
    out["book_ret"] = book
    out["rebound_on"] = combo
    out["tier"] = np.where(crash, "crash", np.where(combo, "combo", ""))
    out["weight"] = np.where(combo, w_eff, 0.0)
    out["instr_ret"] = instr_ret
    out["sleeve_pnl"] = sleeve
    out["overlaid_ret"] = book + sleeve
    return out


def metrics(r: pd.Series) -> dict:
    r = r.dropna()
    if len(r) < 5:
        return dict(ann=np.nan, vol=np.nan, sharpe=np.nan, maxdd=np.nan, n=len(r))
    ann, vol = r.mean() * 252, r.std() * np.sqrt(252)
    eq = (1 + r).cumprod()
    return dict(ann=ann, vol=vol, sharpe=(ann / vol if vol else np.nan),
                maxdd=(eq / eq.cummax() - 1).min(), n=len(r))


def _window_row(ov: pd.DataFrame, mask: pd.Series) -> dict:
    m = mask & ov["book_ret"].notna()
    b, h = metrics(ov["book_ret"][m]), metrics(ov["overlaid_ret"][m])
    on = ov["rebound_on"] & m
    k = int(on.sum())
    return dict(days=int(m.sum()), on=k, on_pct=100 * k / max(int(m.sum()), 1),
                book_sh=b["sharpe"], reb_sh=h["sharpe"], d_sh=h["sharpe"] - b["sharpe"],
                book_dd=b["maxdd"] * 100, d_dd=(h["maxdd"] - b["maxdd"]) * 100,
                won=100 * (ov["instr_ret"][on] > 0).mean() if k else np.nan,
                sleeve=ov["sleeve_pnl"][on].sum() * 100 if k else 0.0)


def _add_instrument(df: pd.DataFrame, cfg: ReboundConfig) -> pd.DataFrame:
    """Add the instrument's next-day return column from prices (the panel doesn't carry TQQQ)."""
    if cfg.instr_fwd_col in df.columns:
        return df
    import yfinance as yf
    px = yf.download(cfg.instrument, start=(df.index.min() - timedelta(days=10)).date(),
                     end=(df.index.max() + timedelta(days=2)).date(),
                     auto_adjust=True, progress=False)["Close"]
    px = px if isinstance(px, pd.Series) else px.iloc[:, 0]
    df = df.copy()
    df[cfg.instr_fwd_col] = (px.shift(-1) / px - 1.0).reindex(df.index)
    return df


def run(panel_path: Path = PANEL, cfg: ReboundConfig = None, out_prefix: Path = OUT_PREFIX) -> dict:
    cfg = cfg or ReboundConfig()
    df = pd.read_csv(panel_path, parse_dates=["date"]).set_index("date")
    df = _add_instrument(df, cfg)
    ov = build_overlay(df, cfg)
    windows = {"FULL": df.index >= df.index.min(),
               "COVID": df.index >= cfg.covid_start,
               "TRAIN(<oos)": df.index < cfg.oos_start,
               "OOS": df.index >= cfg.oos_start}
    summary = {wn: _window_row(ov, pd.Series(m, index=df.index)) for wn, m in windows.items()}
    wf = {}
    for yr in sorted(set(df.index.year)):
        m = pd.Series(df.index.year == yr, index=df.index)
        if (m & df[cfg.book_col].notna()).sum() >= 20:
            wf[int(yr)] = _window_row(ov, m)
    out_prefix.parent.mkdir(parents=True, exist_ok=True)
    ov.to_csv(f"{out_prefix}_daily.csv")
    _write_summary(f"{out_prefix}_summary.md", cfg, summary, wf, panel_path, df)
    return dict(config=asdict(cfg), summary=summary, walk_forward=wf)


def live_signal(cfg: ReboundConfig = None, scenario: str = "model_v4", n_basket: int = 10,
                as_of: str = None) -> dict:
    """Compute the trigger inputs LIVE from yfinance + the latest ranking snapshot, so the overlay works
    on ANY date. QQQ 1-day return; SPY 5d-vol z; momentum spread = mean 1-day return of the top-N ranked
    names minus the bottom-N (from the newest rankings_*.csv). `as_of` evaluates the signal at that close
    (the bar at/just before it) for report use; default = the latest available bar (for the live order)."""
    cfg = cfg or ReboundConfig()
    import glob
    import yfinance as yf
    snaps = sorted(glob.glob(str(ROOT / "backtests" / f"rankings_{scenario}_*.csv")))
    if not snaps:
        raise FileNotFoundError("no ranking snapshot to derive the top/bottom baskets")
    rk = pd.read_csv(snaps[-1])
    rk["ticker"] = rk["ticker"].astype(str).str.strip()
    top = rk.nsmallest(n_basket, "rank")["ticker"].tolist()
    bottom = rk.nlargest(n_basket, "rank")["ticker"].tolist()
    tks = sorted(set(top + bottom + ["QQQ", "SPY"]))
    px = yf.download(tks, period="250d", auto_adjust=True, progress=False)["Close"].dropna(how="all")
    ret = px.pct_change()
    if as_of:
        ret = ret.loc[:pd.Timestamp(as_of)]                       # signal AS OF that close
    last = ret.iloc[-1]
    vol_tk = "QQQ" if str(cfg.vol_factor).lower().startswith("qqq") else "SPY"   # match cfg.vol_factor
    v = ret[vol_tk].rolling(5).std()
    vz = float(((v - v.rolling(63).mean().shift(1)) / v.rolling(63).std().shift(1)).iloc[-1])
    top_1d = float(last[[t for t in top if t in last.index]].mean())
    bottom_1d = float(last[[t for t in bottom if t in last.index]].mean())
    return dict(date=str(ret.index[-1].date()), qqq_down=float(last["QQQ"]),
                signal=top_1d - bottom_1d, vol_z=vz, top_1d=top_1d, bottom_1d=bottom_1d,
                ranking=Path(snaps[-1]).name)


def recommend(market_value: float = None, cfg: ReboundConfig = None, panel_path: Path = PANEL,
              as_of: str = None, down_override: float = None, signal_override: float = None,
              volz_override: float = None, scenario: str = "model_v4", live="auto") -> dict:
    """Should we buy TQQQ today for tomorrow's rebound, and how much? Trigger inputs come from the
    panel (historical) or LIVE (yfinance + ranking) — `live=True` forces live, `live='auto'` (default)
    uses the panel when it covers `as_of` and falls back to live otherwise. Size = weight x CURRENT
    MARKET VALUE of the held positions (ex-cash); auto-computed via current_exposure() if not given."""
    cfg = cfg or ReboundConfig()
    src = None
    if market_value is None:
        import hedge_overlay as ho
        ex = ho.current_exposure(scenario, as_of)
        market_value, src = ex["market_value"], ex["source"]
    use_live, date, top_1d, bottom_1d, ranking = (live is True), None, None, None, None
    if not use_live:
        df = pd.read_csv(panel_path, parse_dates=["date"]).set_index("date")
        volz = _zscore(df[cfg.vol_factor], cfg.vol_lookback)
        valid = df[cfg.down_factor].notna() & df[cfg.signal_factor].notna() & volz.notna()
        want = pd.Timestamp(as_of) if as_of else (df.index[valid][-1] if valid.any() else df.index[-1])
        if want in df.index:
            date, down = want, float(df[cfg.down_factor].loc[want])
            sig, vz = float(df[cfg.signal_factor].loc[want]), float(volz.loc[want])
            top_1d = float(df[cfg.crash_top_factor].loc[want]) if cfg.crash_top_factor in df.columns else None
            bottom_1d = float(df[cfg.crash_bottom_factor].loc[want]) if cfg.crash_bottom_factor in df.columns else None
        elif live == "auto":
            use_live = True
        else:
            raise KeyError(f"{want} not in panel")
    if use_live:
        ls = live_signal(cfg, scenario, as_of=as_of)
        date, down, sig, vz = ls["date"], ls["qqq_down"], ls["signal"], ls["vol_z"]
        top_1d, bottom_1d, ranking = ls["top_1d"], ls["bottom_1d"], ls["ranking"]
    down = down_override if down_override is not None else down
    sig = signal_override if signal_override is not None else sig
    vz = volz_override if volz_override is not None else vz
    combo = (down <= cfg.down_threshold) and (sig < cfg.signal_threshold) and (vz >= cfg.vol_z_threshold)
    crash = bool(combo and cfg.tiered and top_1d is not None and top_1d <= cfg.crash_top_threshold
                 and bottom_1d is not None and bottom_1d > 0)
    weight = (cfg.weight_cap if crash else cfg.weight) if combo else 0.0
    return dict(date=str(date) if not hasattr(date, "date") else str(date.date()),
                instrument=cfg.instrument, fires=bool(combo),
                tier=("CRASH" if crash else ("COMBO" if combo else None)),
                qqq_down=down, signal=sig, vol_z=vz, weight=weight, market_value=market_value,
                exposure_source=src, source=("live" if use_live else "panel"), ranking=ranking,
                rebound_dollars=weight * market_value if combo else 0.0,
                note="size = weight x CURRENT MARKET VALUE of positions (mark-to-market, excl. cash)")


def _fmt(r: dict) -> str:
    return ("days=%4d on=%3d (%4.1f%%) | bookSh %+.2f rebSh %+.2f dSh %+.2f | "
            "bookDD %.1f%% dDD %+.1f%% | TQQQ+ %s%% sleeve %+.2f%%") % (
        r["days"], r["on"], r["on_pct"], r["book_sh"], r["reb_sh"], r["d_sh"], r["book_dd"], r["d_dd"],
        ("%.0f" % r["won"]) if r["on"] else "na", r["sleeve"])


def _write_summary(path, cfg, summary, wf, panel_path, df) -> None:
    L = ["# Rebound overlay on model_v4 — down-shock + momentum-crash 1-day TQQQ buy\n",
         "Standalone overlay; **model_v4 is not modified**. Source panel: `%s` (%s to %s); TQQQ from prices.\n"
         % (panel_path.name, df.index.min().date(), df.index.max().date()),
         "## Rule (configurable in `ReboundConfig`)\n```",
         "FIRE (combo):  %s <= %+.3f  AND  %s < %+.2f  AND  z(%s,%dd) >= %.2f"
         % (cfg.down_factor, cfg.down_threshold, cfg.signal_factor, cfg.signal_threshold,
            cfg.vol_factor, cfg.vol_lookback, cfg.vol_z_threshold)]
    if cfg.tiered:
        L.append("CRASH (full):  + %s <= %+.2f AND %s > 0  -> escalate to %.0f%% notional"
                 % (cfg.crash_top_factor, cfg.crash_top_threshold, cfg.crash_bottom_factor, cfg.weight_cap * 100))
    L.append("then BUY %s @ %.0f%% of the held book for 1 day (round-trip %.0fbp), exit next close."
             % (cfg.instrument, cfg.weight * 100, cfg.cost_bps))
    L.append("```\n")
    L.append("Key filter: **`%s < 0`** (the strategy's momentum signal inverting) selects the "
             "mean-reverting setups and skips trend-continuation sell-offs. Small, robust, tail-neutral.\n"
             % cfg.signal_factor)
    L.append("## Window summary\n```")
    for wn, r in summary.items():
        L.append("%-11s %s" % (wn, _fmt(r)))
    L.append("```\n## Yearly walk-forward\n```")
    for yr, r in wf.items():
        L.append("%-6d on=%-3d dSh %+.2f sleeve %+.2f%%" % (yr, r["on"], r["d_sh"], r["sleeve"]))
    L.append("```\n- Decide-at-close / fill-next-close; sized small. Re-validate after any model/universe change.\n")
    Path(path).write_text("\n".join(L))


def _cli(argv=None):
    p = argparse.ArgumentParser(description="model_v4 down-shock+signal-negative 1-day TQQQ rebound overlay")
    p.add_argument("--panel", default=str(PANEL))
    p.add_argument("--down", type=float, help="down-shock threshold (e.g. -0.025)")
    p.add_argument("--signal-thr", type=float, help="momentum-signal threshold (fire when below; e.g. 0.0)")
    p.add_argument("--vol-z", type=float, help="vol z threshold (e.g. 0.5)")
    p.add_argument("--weight", type=float, help="sleeve notional weight (fraction of book)")
    p.add_argument("--tiered", action="store_true", help="escalate to weight_cap on a true momentum crash")
    p.add_argument("--recommend", action="store_true", help="live: recommend $ of TQQQ to buy")
    p.add_argument("--market-value", type=float, help="recommend: current mark-to-market positions value (ex-cash)")
    p.add_argument("--qqq", type=float, help="recommend: override today's QQQ 1-day return")
    p.add_argument("--spread", type=float, help="recommend: override today's momentum spread")
    p.add_argument("--spy-vol-z", type=float, help="recommend: override today's SPY 5d-vol z")
    a = p.parse_args(argv)
    cfg = ReboundConfig()
    for k_arg, k_cfg in [("down", "down_threshold"), ("signal_thr", "signal_threshold"),
                         ("vol_z", "vol_z_threshold"), ("weight", "weight"), ("tiered", "tiered")]:
        v = getattr(a, k_arg)
        if v is not None and v is not False:
            setattr(cfg, k_cfg, v)
    if a.tiered:
        cfg.tiered = True
    if a.recommend:
        r = recommend(a.market_value, cfg, Path(a.panel),
                      down_override=a.qqq, signal_override=a.spread, volz_override=a.spy_vol_z)
        print("REBOUND RECOMMENDATION  (as of %s, %s)" % (r["date"], r["instrument"]))
        print("  FIRE: QQQ %+.2f%% (<=%.1f%%) & signal %+.2f%% (<%.0f%%) & vol-z %+.2f (>=%.2f)" % (
            r["qqq_down"] * 100, cfg.down_threshold * 100, r["signal"] * 100, cfg.signal_threshold * 100,
            r["vol_z"], cfg.vol_z_threshold))
        print("  -> TIER: %s" % (r["tier"] or "none (no fire)"))
        if r["fires"]:
            print("  -> BUY $%s of %s  (%.0f%% of $%s current exposure)" % (
                f"{r['rebound_dollars']:,.0f}", r["instrument"], r["weight"] * 100, f"{r['market_value']:,.0f}"))
        else:
            print("  -> no rebound buy today (trigger not met)")
        return
    res = run(Path(a.panel), cfg)
    print("config:", {k: res["config"][k] for k in ("down_threshold", "signal_threshold",
                                                     "vol_z_threshold", "weight", "tiered")})
    for wn, r in res["summary"].items():
        print("%-11s %s" % (wn, _fmt(r)))
    print("\nartifacts -> %s_summary.md , %s_daily.csv" % (OUT_PREFIX, OUT_PREFIX))


if __name__ == "__main__":
    _cli()
