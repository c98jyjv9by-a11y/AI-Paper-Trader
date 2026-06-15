"""
scenario_charts.py — Per-ticker annotated price charts for a scenario's trades.

For each ticker traded in a scenario, plots the price over time, marks every BUY and
SELL with its reason (take-profit / stop-loss / trailing-stop / max-holding), shades
the held periods, and reports the active strategy's per-ticker return vs simply
buying and holding that ticker over the same window — so you can eyeball whether the
exit rationales helped or hurt.

Reads an existing scenario trades CSV (no re-backtest); fetches daily closes via
yfinance. Writes PNGs to reports/charts_<scenario>_<date>/. Read-only w.r.t. data/.

    python src/scenario_charts.py --scenario davids_model
"""
import argparse
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

# Composite-score bar color by band: prominent green (strong) → existing blue → prominent red (weak).
def _score_color(s: float):
    if s > 0.90:
        return mcolors.to_rgba("#1a9850", 0.65)   # prominent green
    if s >= 0.80:
        return mcolors.to_rgba("#66bd63", 0.45)   # lighter green
    if s >= 0.40:
        return mcolors.to_rgba("#4575b4", 0.22)   # existing (neutral)
    if s >= 0.20:
        return mcolors.to_rgba("#fc8d59", 0.50)   # lightish red
    return mcolors.to_rgba("#d73027", 0.70)       # prominent red

_REASON_LABEL = {
    "take_profit": ("take-profit", "#1a9850"),
    "stop_loss": ("stop-loss", "#d73027"),
    "trailing_stop": ("trailing-stop", "#fc8d59"),
    "max_holding_period": ("max-hold", "#4575b4"),
}


def _short_reason(reason: str) -> str:
    parts = [_REASON_LABEL.get(p, (p, ""))[0] for p in str(reason).split("+")]
    return "+".join(parts)


def _score_panel(price_data: "pd.DataFrame", config: Dict) -> "pd.DataFrame":
    """Composite score per (date, ticker) over the full panel — one pass, reused for every
    chart. Computed at a weekly cadence on long windows to stay fast and keep bars legible."""
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).parent))
    from signals import calculate_signals, rank_candidates
    from backtest import _build_ticker_weights, _SIGNAL_WINDOW

    uni = config["tickers"]
    weights = config.get("signals", {}).get("weights")
    tw = _build_ticker_weights(config) or None
    idx = price_data.index
    step = 5 if len(idx) > 400 else 1                     # weekly cadence on long windows
    rows: Dict = {}
    for i in range(_SIGNAL_WINDOW, len(idx), step):
        sl = price_data.iloc[max(0, i + 1 - _SIGNAL_WINDOW): i + 1]
        sig = calculate_signals(sl, uni)
        if sig.empty:
            continue
        rk = rank_candidates(sig, top_n=len(sig), weights=weights, ticker_weights=tw)
        rows[idx[i]] = dict(zip(rk["ticker"], rk["composite_score"]))
    return pd.DataFrame.from_dict(rows, orient="index").sort_index() if rows else pd.DataFrame()


def _per_ticker_returns(trades: pd.DataFrame, last_close: float,
                        seed_open: float = None) -> Tuple[float, float, List[float]]:
    """Active compounded return from round-trips (+ open MTM) and number of round trips.
    seed_open: entry price for a position already held when the window starts."""
    growth, open_buy, rts = 1.0, seed_open, []
    for _, r in trades.sort_values("date").iterrows():
        if r["action"] == "BUY":
            open_buy = float(r["price"])
        elif r["action"] == "SELL" and open_buy:
            rt = float(r["price"]) / open_buy - 1.0
            growth *= (1 + rt); rts.append(rt); open_buy = None
    if open_buy:                                   # still holding at end → mark to market
        growth *= (1 + (last_close / open_buy - 1.0))
    return growth - 1.0, len(rts), rts


def make_charts(trades_csv: Path, out_dir: Path, scenario: str, since=None,
                close: "pd.DataFrame" = None, price_data: "pd.DataFrame" = None,
                config: Dict = None) -> Dict[str, Dict]:
    """If `close` ([dates × tickers]) is provided it is used directly (e.g. the panel
    the backtest already fetched); otherwise prices are downloaded via yfinance.
    If `price_data` (full OHLCV panel) + `config` are provided, each chart also overlays
    the per-date composite score as bars on a secondary axis."""
    trades = pd.read_csv(trades_csv, parse_dates=["date"])
    tickers = sorted(trades["ticker"].unique())

    if close is None:
        import yfinance as yf
        start = (trades["date"].min() - timedelta(days=10)).date()
        end = (trades["date"].max() + timedelta(days=3)).date()
        raw = yf.download(tickers, start=start.isoformat(), end=end.isoformat(),
                          interval="1d", auto_adjust=True, progress=False)
        close = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw[["Close"]].rename(columns={"Close": tickers[0]})

    # Composite-score panel (optional overlay) — computed once, reused for every ticker.
    score_df = pd.DataFrame()
    min_score = (config or {}).get("signals", {}).get("min_composite_score")
    if price_data is not None and config is not None:
        try:
            score_df = _score_panel(price_data, config)
        except Exception:                                # overlay is a nicety; never fail charts
            score_df = pd.DataFrame()

    out_dir.mkdir(parents=True, exist_ok=True)
    summary: Dict[str, Dict] = {}
    since_ts = pd.Timestamp(since) if since else None

    for tk in tickers:
        if tk not in close.columns:
            continue
        px = close[tk].dropna()
        tt = trades[trades["ticker"] == tk].sort_values("date")
        if since_ts is not None:                       # zoom to a recent window for legibility
            px = px[px.index >= since_ts]
            tt = tt[tt["date"] >= since_ts]
            if px.empty:
                continue
        hold_ret = float(px.iloc[-1] / px.iloc[0] - 1.0)
        # if a position was already open when the window starts, seed the entry at the window-open price
        seed = float(px.iloc[0]) if (len(tt) and tt.iloc[0]["action"] == "SELL") else None
        active_ret, n_rt, _ = _per_ticker_returns(tt, float(px.iloc[-1]), seed_open=seed)

        fig, ax = plt.subplots(figsize=(13, 6))

        # composite-score bars on a secondary axis, scaled to the lower ~45% so the price
        # line/markers stay clearly readable above them.
        if not score_df.empty and tk in score_df.columns:
            ss = score_df[tk].dropna()
            ss = ss[(ss.index >= px.index[0]) & (ss.index <= px.index[-1])]
            if not ss.empty:
                ax2 = ax.twinx()
                diffs = ss.index.to_series().diff().dt.days.dropna()
                width = max(1.0, float(diffs.median()) * 0.85) if not diffs.empty else 5.0
                bar_colors = [_score_color(v) for v in ss.values]
                ax2.bar(ss.index, ss.values, width=width, color=bar_colors, zorder=0)
                ax2.set_ylim(0, 2.2)                       # score 1.0 → ~45% of chart height
                ax2.set_yticks([0, 0.5, 1.0])
                ax2.set_ylabel("composite score (0–1)  ·  green=strong, red=weak", color="#555", fontsize=8)
                ax2.tick_params(axis="y", labelcolor="#4575b4", labelsize=7)
                if min_score:
                    ax2.axhline(min_score, color="#4575b4", lw=0.7, ls=":", alpha=0.7)
                ax.set_zorder(ax2.get_zorder() + 1)        # draw price/markers above the bars
                ax.patch.set_visible(False)

        ax.plot(px.index, px.values, color="#333", lw=1.1, label=f"{tk} close")

        # shade held periods (buy → next sell)
        open_dt = None
        for _, r in tt.iterrows():
            if r["action"] == "BUY":
                open_dt = r["date"]
            elif r["action"] == "SELL" and open_dt is not None:
                ax.axvspan(open_dt, r["date"], color="#1a9850", alpha=0.06)
                open_dt = None
        if open_dt is not None:
            ax.axvspan(open_dt, px.index[-1], color="#1a9850", alpha=0.06)

        for _, r in tt.iterrows():
            if r["action"] == "BUY":
                ax.scatter(r["date"], r["price"], marker="^", s=90, color="#1a9850", zorder=5,
                           edgecolor="white", linewidth=0.6)
            else:
                ax.scatter(r["date"], r["price"], marker="v", s=90, color="#d73027", zorder=5,
                           edgecolor="white", linewidth=0.6)
                ax.annotate(_short_reason(r["reason"]), (r["date"], r["price"]),
                            textcoords="offset points", xytext=(0, 10), ha="center",
                            fontsize=7, color="#555", rotation=0)

        verdict = "active BEAT hold" if active_ret > hold_ret else "active TRAILED hold"
        ax.set_title(f"{tk} — active {active_ret*100:+.1f}%  vs  buy & hold {hold_ret*100:+.1f}%  "
                     f"({verdict}; {n_rt} round trips)", fontsize=11)
        ax.set_ylabel("Price ($, adj)"); ax.grid(alpha=0.25)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        ax.legend(loc="upper left", fontsize=8)
        # legend for markers/reasons
        ax.scatter([], [], marker="^", color="#1a9850", label="BUY")
        ax.scatter([], [], marker="v", color="#d73027", label="SELL (reason annotated)")
        ax.legend(loc="upper left", fontsize=8)
        fig.tight_layout()
        path = out_dir / f"{tk}.png"
        fig.savefig(path, dpi=130); plt.close(fig)

        summary[tk] = {"active_return": active_ret, "hold_return": hold_ret,
                       "excess": active_ret - hold_ret, "round_trips": n_rt, "png": str(path)}
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(description="Per-ticker annotated charts for a scenario's trades")
    ap.add_argument("--scenario", default="davids_model")
    ap.add_argument("--trades", default=None, help="explicit trades CSV (else newest scenario_<name>_*_trades.csv)")
    ap.add_argument("--since", default=None, metavar="YYYY-MM-DD", help="zoom charts to trades on/after this date")
    args = ap.parse_args()
    root = Path(__file__).parent.parent
    since = date.fromisoformat(args.since) if args.since else None

    if args.trades:
        trades_csv = Path(args.trades)
    else:
        matches = sorted((root / "backtests").glob(f"scenario_{args.scenario}_*_trades.csv"))
        if not matches:
            print(f"No trades CSV for scenario '{args.scenario}' in backtests/. Run the scenario first.")
            sys.exit(1)
        trades_csv = matches[-1]

    # Load the scenario config + full OHLCV panel so charts can overlay composite-score bars.
    price_data = cfg = None
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from scenarios import load_scenario, build_config
        from backtest import load_config, fetch_backtest_data
        cfg = build_config(load_config(root / "config"), load_scenario(args.scenario))
        trades_dates = pd.read_csv(trades_csv, parse_dates=["date"])["date"]
        price_data = fetch_backtest_data(cfg["tickers"], trades_dates.min().date(),
                                         (trades_dates.max() + timedelta(days=3)).date())
    except Exception as exc:
        print(f"  (composite-score overlay unavailable: {exc})")

    out_dir = root / "reports" / f"charts_{args.scenario}_{date.today().isoformat()}"
    summary = make_charts(trades_csv, out_dir, args.scenario, since=since,
                          price_data=price_data, config=cfg)

    print()
    print(f"  Trades : {trades_csv.name}")
    print(f"  Charts : {out_dir}")
    print()
    print(f"  {'Ticker':<8}{'Active':>10}{'Hold':>10}{'Excess':>10}{'RoundTrips':>12}")
    for tk, s in summary.items():
        print(f"  {tk:<8}{s['active_return']*100:>9.1f}%{s['hold_return']*100:>9.1f}%"
              f"{s['excess']*100:>9.1f}%{s['round_trips']:>12}")
    print()


if __name__ == "__main__":
    main()
