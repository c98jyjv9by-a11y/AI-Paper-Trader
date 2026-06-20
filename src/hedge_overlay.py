"""
hedge_overlay.py — standalone 1-day "up-shock + vol-surge" HEDGE OVERLAY for model_v4.

This sits ON TOP of model_v4 and never modifies it. It consumes the precomputed research
panel (backtests/model_v4_timeseries.csv) read-only — the book's daily return and the
candidate hedge instruments' next-day returns — and applies a configurable end-of-day rule:

    RULE (decide at close T, hold T+1 only, exit at close T+1) — TWO-GATE tiered sizing:
      SOFT gate:  qqq_trl_1d >= 1.5%  AND  z(spy_vol_trl_5d) >= 0.75   -> HALF-size hedge
      HARD gate:  qqq_trl_1d >= 2.0%  AND  z(spy_vol_trl_5d) >= 1.00   -> FULL-size hedge
      Hedge = long SOXS (-3x inverse semis; no shorting), sized inverse-vol to the book's risk;
      half-conviction (soft-only) fires get 50% of full size. (set tiered=False for single-gate.)

Validated finding (see backtests/hedge_overlay_model_v4_summary.md): neither factor works
alone — a QQQ up-day on its own *bounces*; it's the INTERACTION (up-shock while vol is already
elevated) that flags the next-day pullback (e.g. 2026-06-16). The edge is a robust plateau
across thresholds (ΔSharpe ~+0.05 full / +0.03 OOS) and survives a yearly walk-forward; it is
a Sharpe-adder + single-day-blow softener, NOT an all-time-max-drawdown reducer.

Everything is in HedgeConfig, so the hedge can be retuned/swapped WITHOUT touching the model.

    python src/hedge_overlay.py                       # default rule, writes artifacts
    python src/hedge_overlay.py --weight 0.45 --product soxs --up 0.015
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).parent.parent
PANEL = ROOT / "backtests" / "model_v4_timeseries.csv"
OUT_PREFIX = ROOT / "backtests" / "hedge_overlay_model_v4"

# hedge instrument -> next-day return (sign-adjusted) and the trailing daily-return
# column used to size it (inverse-vol). The vol column is the instrument's own daily move.
PRODUCTS = {
    "short_smh":   (lambda d: -d["smh_fwd_1d"],   "smh_trl_1d"),    # 1x short semis (no leverage decay)
    "soxs":        (lambda d: d["soxs_fwd_1d"],    "soxs_trl_1d"),   # 3x inverse semis (convex; carries)
    "psq":         (lambda d: d["psq_fwd_1d"],     "psq_trl_1d"),    # 1x inverse QQQ (not semi-specific)
    "short_top10": (lambda d: -d["top10_fwd_1d"],  "top10_trl_1d"),  # 1x short the leaders
}


@dataclass
class HedgeConfig:
    # ---- trigger (the rule; change freely, model untouched) ----
    up_factor: str = "qqq_trl_1d"      # the "up-shock" measure (today's move)
    # ---- two-gate tiered trigger ----
    #   SOFT gate (any fire): half-size hedge.  HARD gate (stronger): full-size hedge.
    up_threshold: float = 0.015        # SOFT up-shock (sweep-best: +1.5% QQQ day)
    vol_factor: str = "spy_vol_trl_5d" # the supporting signal (best in sensitivity)
    vol_z_threshold: float = 0.75      # SOFT vol gate, z(vol_factor) (sweep-best)
    tiered: bool = True                # True = two-gate (half on soft-only, full on hard)
    hard_up_threshold: float = 0.020   # HARD up-shock -> full size
    hard_vol_z_threshold: float = 1.00 # HARD vol gate -> full size
    soft_weight_frac: float = 0.50     # fraction of full size on soft-only fires
    vol_lookback: int = 63             # trailing window for the vol z-score
    # ---- hedge sleeve ----
    product: str = "soxs"              # long inverse-ETF only (no shorting); SOXS = -3x semis
    sizing: str = "inverse_vol"        # "inverse_vol" (risk-targeted) or "fixed"
    target_risk: float = 0.50          # inverse_vol: hedge daily-vol as a fraction of book daily-vol
    vol_window: int = 20               # trailing window for the sizing vols
    weight_cap: float = 0.60           # max sleeve notional (fraction of book)
    weight: float = 0.30               # fixed-mode sleeve size (used only when sizing="fixed")
    cost_bps: float = 10.0             # round-trip cost per on-day, bps of the TRADED sleeve notional
    # ---- accounting ----
    book_col: str = "book_fwd_1d"
    book_ret_col: str = "book_trl_1d"  # realized daily book return, for sizing vol
    covid_start: str = "2020-04-01"
    oos_start: str = "2024-01-01"


def _zscore(s: pd.Series, lookback: int) -> pd.Series:
    """Trailing z-score using only data known BEFORE today (shift 1)."""
    return (s - s.rolling(lookback).mean().shift(1)) / s.rolling(lookback).std().shift(1)


def _sizing_weight(df: pd.DataFrame, cfg: HedgeConfig) -> pd.Series:
    """Per-date sleeve notional (fraction of book). Inverse-vol = risk-targeted to the book."""
    if cfg.sizing == "fixed":
        return pd.Series(cfg.weight, index=df.index)
    fn, vol_col = PRODUCTS[cfg.product]
    sig_book = df[cfg.book_ret_col].rolling(cfg.vol_window).std().shift(1)
    sig_hedge = df[vol_col].rolling(cfg.vol_window).std().shift(1)
    w = cfg.target_risk * sig_book / sig_hedge          # hedge $-vol = target_risk * book $-vol
    return w.clip(upper=cfg.weight_cap).fillna(0.0)


def _gates(df: pd.DataFrame, cfg: HedgeConfig):
    """Two-gate signal -> (soft fire mask, hard fire mask, size multiplier series).
    soft-only fires get cfg.soft_weight_frac of full size; hard fires get full size."""
    up = df[cfg.up_factor]
    volz = _zscore(df[cfg.vol_factor], cfg.vol_lookback)
    soft = ((up >= cfg.up_threshold) & (volz >= cfg.vol_z_threshold)).fillna(False)
    hard = ((up >= cfg.hard_up_threshold) & (volz >= cfg.hard_vol_z_threshold)).fillna(False)
    if cfg.tiered:
        mult = pd.Series(np.where(hard, 1.0, np.where(soft, cfg.soft_weight_frac, 0.0)), index=df.index)
    else:
        mult = soft.astype(float)
    return soft, hard, mult


def build_overlay(df: pd.DataFrame, cfg: HedgeConfig) -> pd.DataFrame:
    """Return a frame with the signal, sleeve weight, hedge PnL, and overlaid daily return.
    Read-only on df. Sleeve weight is a fraction of the (current) book, so it scales with book size.
    Two-gate tiered sizing: half size on soft-only fires, full size when the hard gate also clears."""
    book = df[cfg.book_col]
    soft, hard, mult = _gates(df, cfg)
    on = soft                                            # any fire
    hedge_ret = PRODUCTS[cfg.product][0](df)
    w = _sizing_weight(df, cfg) * mult                   # effective weight (0 where no fire)
    rt = cfg.cost_bps / 1e4
    sleeve = np.where(on, w * hedge_ret - w * rt, 0.0)   # cost on the TRADED notional (w)
    out = pd.DataFrame(index=df.index)
    out["book_ret"] = book
    out["hedge_on"] = on
    out["tier"] = np.where(hard, "full", np.where(soft, "half", ""))
    out["weight"] = np.where(on, w, 0.0)
    out["hedge_instr_ret"] = hedge_ret
    out["sleeve_pnl"] = sleeve
    out["overlaid_ret"] = book + sleeve
    return out


def metrics(r: pd.Series) -> dict:
    r = r.dropna()
    if len(r) < 5:
        return dict(ann=np.nan, vol=np.nan, sharpe=np.nan, maxdd=np.nan, n=len(r))
    ann = r.mean() * 252
    vol = r.std() * np.sqrt(252)
    eq = (1 + r).cumprod()
    dd = (eq / eq.cummax() - 1).min()
    return dict(ann=ann, vol=vol, sharpe=(ann / vol if vol else np.nan), maxdd=dd, n=len(r))


def _window_row(ov: pd.DataFrame, mask: pd.Series, hedge_ret: pd.Series, w: float, rt: float) -> dict:
    m = mask & ov["book_ret"].notna()
    b = metrics(ov["book_ret"][m])
    h = metrics(ov["overlaid_ret"][m])
    on = ov["hedge_on"] & m
    k = int(on.sum())
    return dict(
        days=int(m.sum()), on=k, on_pct=100 * k / max(int(m.sum()), 1),
        book_sh=b["sharpe"], hed_sh=h["sharpe"], d_sh=h["sharpe"] - b["sharpe"],
        book_dd=b["maxdd"] * 100, d_dd=(h["maxdd"] - b["maxdd"]) * 100,
        on_book=ov["book_ret"][on].mean() * 100 if k else np.nan,
        paid=100 * (hedge_ret[on] > 0).mean() if k else np.nan,
        sleeve=ov["sleeve_pnl"][on].sum() * 100 if k else 0.0,
    )


def run(panel_path: Path = PANEL, cfg: HedgeConfig = None, out_prefix: Path = OUT_PREFIX) -> dict:
    cfg = cfg or HedgeConfig()
    df = pd.read_csv(panel_path, parse_dates=["date"]).set_index("date")
    ov = build_overlay(df, cfg)
    hedge_ret = ov["hedge_instr_ret"]; rt = cfg.cost_bps / 1e4

    windows = {
        "FULL": df.index >= df.index.min(),
        "COVID": df.index >= cfg.covid_start,
        "TRAIN(<oos)": df.index < cfg.oos_start,
        "OOS": df.index >= cfg.oos_start,
    }
    summary = {wn: _window_row(ov, m, hedge_ret, cfg.weight, rt) for wn, m in windows.items()}

    wf = {}
    for yr, _g in df.groupby(df.index.year):
        m = df.index.year == yr
        if (m & df[cfg.book_col].notna()).sum() < 20:
            continue
        wf[int(yr)] = _window_row(ov, pd.Series(m, index=df.index), hedge_ret, cfg.weight, rt)

    # ---- write artifacts ----
    out_prefix.parent.mkdir(parents=True, exist_ok=True)
    ov_out = ov.copy()
    ov_out.to_csv(f"{out_prefix}_daily.csv")
    _write_summary(f"{out_prefix}_summary.md", cfg, summary, wf, panel_path, df)
    return dict(config=asdict(cfg), summary=summary, walk_forward=wf)


def current_exposure(scenario: str = "model_v4", as_of: str = None) -> dict:
    """Live MARK-TO-MARKET exposure of the held book (sum of held_shares x latest price),
    excluding cash. Reconstructs holdings from the scenario trade log and marks them at the
    latest available close. This is the base the hedge sizes off — it moves with prices."""
    import glob, yfinance as yf
    f = sorted(glob.glob(str(ROOT / "backtests" / ("scenario_%s_*trades*.csv" % scenario))))[-1]
    t = pd.read_csv(f, parse_dates=["date"])
    if as_of:
        t = t[t["date"] <= pd.Timestamp(as_of)]
    t["signed"] = t.apply(lambda r: r["shares"] if str(r["action"]).upper() == "BUY" else -r["shares"], axis=1)
    held = {k: v for k, v in t.groupby("ticker")["signed"].sum().items() if v > 1e-6}
    px = yf.download(list(held), period="5d", auto_adjust=True, progress=False)["Close"].ffill().iloc[-1]
    mv = {k: held[k] * float(px[k]) for k in held if k in px.index and pd.notna(px[k])}
    return dict(market_value=float(sum(mv.values())), positions=mv, source=Path(f).name)


def recommend(market_value: float = None, cfg: HedgeConfig = None, panel_path: Path = PANEL,
              as_of: str = None, up_override: float = None, volz_override: float = None,
              scenario: str = "model_v4") -> dict:
    """Live sizing. Size = weight x CURRENT MARKET VALUE of the held positions (mark-to-market
    exposure, excluding cash) -- NOT cost basis and NOT a constant. If market_value is None it is
    computed live via current_exposure(). weight is the inverse-vol fraction
    (target_risk * sigma_book / sigma_hedge). Pass up_override/volz_override for today's fresh signal."""
    cfg = cfg or HedgeConfig()
    exposure_src = None
    if market_value is None:
        ex = current_exposure(scenario, as_of)
        market_value, exposure_src = ex["market_value"], ex["source"]
    df = pd.read_csv(panel_path, parse_dates=["date"]).set_index("date")
    base_w = _sizing_weight(df, cfg)
    volz = _zscore(df[cfg.vol_factor], cfg.vol_lookback)
    valid = df[cfg.up_factor].notna() & volz.notna()
    date = pd.Timestamp(as_of) if as_of else df.index[valid][-1]
    up = up_override if up_override is not None else float(df[cfg.up_factor].loc[date])
    vz = volz_override if volz_override is not None else float(volz.loc[date])
    soft = (up >= cfg.up_threshold) and (vz >= cfg.vol_z_threshold)
    hard = (up >= cfg.hard_up_threshold) and (vz >= cfg.hard_vol_z_threshold)
    if cfg.tiered:
        mult = 1.0 if hard else (cfg.soft_weight_frac if soft else 0.0)
        tier = "FULL" if hard else ("HALF" if soft else None)
    else:
        mult = 1.0 if soft else 0.0
        tier = "FULL" if soft else None
    weight = float(base_w.loc[date]) * mult
    dollars = weight * market_value if soft else 0.0
    return dict(date=str(date.date()), product=cfg.product, fires=soft, tier=tier,
                qqq_up=up, vol_z=vz, weight=weight, market_value=market_value,
                exposure_source=exposure_src, hedge_dollars=dollars,
                note="size = weight x CURRENT MARKET VALUE of positions (mark-to-market, excl. cash)")


def _fmt(row: dict) -> str:
    return ("days=%4d on=%3d (%4.1f%%) | bookSh %+.2f hedSh %+.2f dSh %+.2f | "
            "bookDD %.1f%% dDD %+.1f%% | onBook %+s%% SOXS+ %s%% sleeve %+.2f%%") % (
        row["days"], row["on"], row["on_pct"], row["book_sh"], row["hed_sh"], row["d_sh"],
        row["book_dd"], row["d_dd"],
        ("%.2f" % row["on_book"]) if row["on"] else "  na",
        ("%.0f" % row["paid"]) if row["on"] else "na", row["sleeve"])


def _write_summary(path, cfg, summary, wf, panel_path, df) -> None:
    L = []
    L.append("# Hedge overlay on model_v4 — up-shock + vol-surge 1-day hedge\n")
    L.append("Standalone overlay; **model_v4 is not modified**. Source panel: `%s` "
             "(%s to %s).\n" % (panel_path.name, df.index.min().date(), df.index.max().date()))
    L.append("## Rule (configurable in `HedgeConfig`)\n")
    L.append("```")
    if cfg.tiered:
        L.append("SOFT gate (half size):  %s >= %+.3f  AND  z(%s,%dd) >= %.2f"
                 % (cfg.up_factor, cfg.up_threshold, cfg.vol_factor, cfg.vol_lookback, cfg.vol_z_threshold))
        L.append("HARD gate (full size):  %s >= %+.3f  AND  z(%s,%dd) >= %.2f"
                 % (cfg.up_factor, cfg.hard_up_threshold, cfg.vol_factor, cfg.vol_lookback, cfg.hard_vol_z_threshold))
        L.append("soft-only fires use %.0f%% of the full inverse-vol size." % (cfg.soft_weight_frac * 100))
    else:
        L.append("if  %s >= %+.3f            (up-shock)" % (cfg.up_factor, cfg.up_threshold))
        L.append("AND z(%s, %dd) >= %.2f     (vol-surge supporting signal)" % (cfg.vol_factor, cfg.vol_lookback, cfg.vol_z_threshold))
    if cfg.sizing == "inverse_vol":
        L.append("then BUY %s, sized INVERSE-VOL: weight = %.2f * sigma_book / sigma_%s"
                 % (cfg.product, cfg.target_risk, cfg.product))
        L.append("     (%dd trailing vols, hedge $-vol targeted at %.0f%% of book $-vol, cap %.0f%% notional);"
                 % (cfg.vol_window, cfg.target_risk * 100, cfg.weight_cap * 100))
        avg_w = build_overlay(df, cfg)["weight"]
        avg_w = avg_w[avg_w > 0].mean()
        L.append("     avg fire-day weight ~ %.0f%% of book.  Hold 1 day, exit next close (cost %.0fbp)."
                 % (avg_w * 100, cfg.cost_bps))
    else:
        L.append("then BUY %s @ %.0f%% notional for 1 day (round-trip cost %.0fbp), exit next close."
                 % (cfg.product, cfg.weight * 100, cfg.cost_bps))
    L.append("```")
    L.append("\nKey finding: **no single factor works alone** — a QQQ up-day by itself bounces; "
             "the edge is the *interaction* (up-shock while vol already elevated). Best supporting "
             "signal in the sensitivity sweep was 5-day realized-vol z (`spy_vol_trl_5d`).\n")
    L.append("## Window summary\n```")
    for wn, r in summary.items():
        L.append("%-11s %s" % (wn, _fmt(r)))
    L.append("```")
    L.append("\n## Yearly walk-forward\n```")
    L.append("%-6s %4s %4s | %7s %7s %7s | %7s %7s | %8s %6s %8s" % (
        "year", "days", "on", "bookSh", "hedSh", "dSh", "bookDD", "dDD", "onBook%", "paid%", "sleeve%"))
    npos = ntot = 0
    for yr, r in wf.items():
        if r["on"]:
            ntot += 1; npos += int(r["d_sh"] > 0)
        L.append("%-6d %4d %4d | %+7.2f %+7.2f %+7.2f | %6.1f%% %+6.1f%% | %8s %6s %+7.2f%%" % (
            yr, r["days"], r["on"], r["book_sh"], r["hed_sh"], r["d_sh"], r["book_dd"], r["d_dd"],
            ("%.2f" % r["on_book"]) if r["on"] else "na", ("%.0f" % r["paid"]) if r["on"] else "na", r["sleeve"]))
    L.append("```")
    L.append("\nYears with active hedge & ΔSharpe>0: **%d/%d**.\n" % (npos, ntot))
    L.append("## Caveats\n")
    L.append("- Edge concentrates in genuine vol-spike episodes (2018–2021); marginal in calm years, "
             "slightly negative in the 2022 grind-bear. It is a Sharpe-adder + single-day-blow softener, "
             "**not** an all-time-max-drawdown reducer.\n")
    L.append("- Decide-at-close / fill-next-close; sized small. Re-validate after any model/universe change.\n")
    Path(path).write_text("\n".join(L))


def _cli(argv=None):
    p = argparse.ArgumentParser(description="model_v4 up-shock+vol 1-day hedge overlay (standalone)")
    p.add_argument("--panel", default=str(PANEL))
    p.add_argument("--up", type=float, help="up-shock threshold (e.g. 0.02)")
    p.add_argument("--vol-z", type=float, help="vol z threshold (e.g. 1.0)")
    p.add_argument("--vol-factor", help="vol factor column (e.g. spy_vol_trl_5d)")
    p.add_argument("--lookback", type=int, help="vol z lookback (days)")
    p.add_argument("--product", choices=list(PRODUCTS), help="hedge instrument")
    p.add_argument("--sizing", choices=["inverse_vol", "fixed"], help="sleeve sizing mode")
    p.add_argument("--target-risk", type=float, help="inverse-vol: hedge $-vol as fraction of book $-vol")
    p.add_argument("--vol-window", type=int, help="trailing window for sizing vols")
    p.add_argument("--weight", type=float, help="fixed-mode sleeve notional weight")
    p.add_argument("--recommend", action="store_true",
                   help="live mode: recommend $ of hedge to buy (sized off current position market value)")
    p.add_argument("--market-value", type=float,
                   help="recommend: current mark-to-market value of positions (excl. cash); auto-computed if omitted")
    p.add_argument("--qqq", type=float, help="recommend: override today's QQQ 1-day return (e.g. 0.025)")
    p.add_argument("--spy-vol-z", type=float, help="recommend: override today's SPY 5d-vol z")
    a = p.parse_args(argv)
    cfg = HedgeConfig()
    for k_arg, k_cfg in [("up", "up_threshold"), ("vol_z", "vol_z_threshold"),
                         ("vol_factor", "vol_factor"), ("lookback", "vol_lookback"),
                         ("product", "product"), ("weight", "weight"),
                         ("sizing", "sizing"), ("target_risk", "target_risk"),
                         ("vol_window", "vol_window")]:
        v = getattr(a, k_arg)
        if v is not None:
            setattr(cfg, k_cfg, v)
    if a.recommend:
        rec = recommend(a.market_value, cfg, Path(a.panel), up_override=a.qqq, volz_override=a.spy_vol_z)
        print("HEDGE RECOMMENDATION  (as of %s, %s)" % (rec["date"], rec["product"]))
        print("  soft gate: QQQ %+.2f%% (>=%.1f%%) & vol-z %+.2f (>=%.2f)   hard gate: QQQ>=%.1f%% & vol-z>=%.2f"
              % (rec["qqq_up"] * 100, cfg.up_threshold * 100, rec["vol_z"], cfg.vol_z_threshold,
                 cfg.hard_up_threshold * 100, cfg.hard_vol_z_threshold))
        print("  -> TIER: %s" % (rec["tier"] or "none (no fire)"))
        src = (" [mark-to-market from %s]" % rec["exposure_source"]) if rec["exposure_source"] else ""
        print("  current position market value (ex-cash): $%s%s" % (f"{rec['market_value']:,.0f}", src))
        if rec["fires"]:
            print("  -> BUY $%s of %s   (%s size: %.1f%% of current exposure)"
                  % (f"{rec['hedge_dollars']:,.0f}", rec["product"], rec["tier"], rec["weight"] * 100))
        else:
            print("  -> no hedge today (neither gate triggered)")
        return
    res = run(Path(a.panel), cfg)
    print("config:", res["config"])
    for wn, r in res["summary"].items():
        print("%-11s %s" % (wn, _fmt(r)))
    print("\nartifacts -> %s_summary.md , %s_daily.csv" % (OUT_PREFIX, OUT_PREFIX))


if __name__ == "__main__":
    _cli()
