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
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

_REASON_LABEL = {
    "take_profit": ("take-profit", "#1a9850"),
    "stop_loss": ("stop-loss", "#d73027"),
    "trailing_stop": ("trailing-stop", "#fc8d59"),
    "max_holding_period": ("max-hold", "#4575b4"),
}


def _short_reason(reason: str) -> str:
    parts = [_REASON_LABEL.get(p, (p, ""))[0] for p in str(reason).split("+")]
    return "+".join(parts)


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
                close: "pd.DataFrame" = None) -> Dict[str, Dict]:
    """If `close` ([dates × tickers]) is provided it is used directly (e.g. the panel
    the backtest already fetched); otherwise prices are downloaded via yfinance."""
    trades = pd.read_csv(trades_csv, parse_dates=["date"])
    tickers = sorted(trades["ticker"].unique())

    if close is None:
        import yfinance as yf
        start = (trades["date"].min() - timedelta(days=10)).date()
        end = (trades["date"].max() + timedelta(days=3)).date()
        raw = yf.download(tickers, start=start.isoformat(), end=end.isoformat(),
                          interval="1d", auto_adjust=True, progress=False)
        close = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw[["Close"]].rename(columns={"Close": tickers[0]})

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

    out_dir = root / "reports" / f"charts_{args.scenario}_{date.today().isoformat()}"
    summary = make_charts(trades_csv, out_dir, args.scenario, since=since)

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
