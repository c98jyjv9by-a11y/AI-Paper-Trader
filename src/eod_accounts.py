"""Consolidated EOD report for the paper broker accounts: daily activity (today's fills) + P&L
(day + total) + position/trade counts, with a brief per-strategy description. Pulls each account's
LIVE Alpaca paper state. Renders reports/eod_accounts_<date>.pdf.

    python run.py eod-accounts [--accounts a b c] [--end YYYY-MM-DD] [--out FILE]
"""
import json
import glob
import textwrap
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from broker_adapter import AlpacaPaper

ROOT = Path(__file__).resolve().parent.parent
GREEN, RED = "#1a7f37", "#c0392b"

# Known accounts in display order, each with (short label, one-paragraph strategy description).
BLURBS = {
    "topten": ("Top-10 seed -> model_v4",
               "model_v4 momentum. Seeded as the 10 highest-scored names; now runs model_v4's full rules "
               "(0.70 buy gate, 8.5%/name cap, Barroso vol governor, score-gated 15% stop) on its own book, "
               "plus the 1-day TQQQ rebound overlay."),
    "copymodel": ("Model-equal seed -> model_v4",
                  "model_v4 momentum. Seeded by equal-weighting the live model book; now follows model_v4's "
                  "own buy/sell rules + the rebound overlay."),
    "rampup": ("Score-gate ramp-up",
               "Buys only names scoring > 0.90 (8.5% each), but sells only per model_v4's exit rules, until "
               "75% of starting cash is deployed, then graduates to full model_v4. + rebound overlay."),
    "monthly10": ("60-day momentum - monthly",
                  "Holds the top 10 by trailing 60-day average composite score, equal-weight; rebalances on "
                  "the first trading day of each month."),
    "weekly10": ("60-day momentum - weekly",
                 "Top 10 by trailing 60-day avg score, equal-weight; rebalances on the first trading day of "
                 "each week."),
    "combo20": ("Staggered 20-name",
                "Top 10 by 60-day score (refreshed monthly) + bottom 10 by 5-day score (refreshed weekly), "
                "equal-weight; rebalances weekly."),
    "zscore10d_biweekly": ("z-reversal - 10d / biweekly (validated)",
             "Mean reversion: buys the 10 MOST-FALLEN names by the 10-day avg of the 60-day z-score, "
             "equal-weight, biweekly; cash when QQQ < 200-day MA. The IC/cost-validated config."),
    "zscore5d_weekly": ("z-reversal - 5d / weekly",
             "Same idea, faster: 5-day avg of the 60-day z, weekly rebalance; cash when QQQ < 200-day MA."),
    "zscore1d_daily": ("z-reversal - 1d / daily",
             "Fastest: the raw (1-day) 60-day z, daily rebalance; cash when QQQ < 200-day MA. Highest gross "
             "Sharpe but highest turnover/cost."),
}
DEFAULT_ACCOUNTS = list(BLURBS)


def _blurb(name):
    if name in BLURBS:
        return BLURBS[name]
    try:                                                   # derive from the manifest target_mode
        man = json.load(open(glob.glob(str(ROOT / "accounts" / name / "*.json"))[0]))
        tm = man.get("target_mode") or {}
        return (tm.get("kind", "broker account"), "target_mode: %s" % json.dumps(tm))
    except Exception:
        return (name, "")


def _money(x):
    return ("-$%s" % f"{abs(x):,.0f}") if x < 0 else ("$%s" % f"{x:,.0f}")


def _pct(x):
    return f"{x * 100:+.2f}%"


def _collect(name, today):
    try:
        cli = AlpacaPaper(account=name)
        a = cli.account()
        eq = float(a.get("equity") or 0.0)
        le = float(a.get("last_equity") or eq)
        pos = cli.positions() or []
        fills = [o for o in (cli.orders(status="closed", limit=200) or [])
                 if o.get("status") == "filled" and (o.get("filled_at") or "").startswith(today)]
        man = json.load(open(glob.glob(str(ROOT / "accounts" / name / "*.json"))[0]))
        start = float(man.get("starting_value") or eq)
        try:                                               # days running = today - inception
            days = (date.fromisoformat(today) - date.fromisoformat(man["inception"])).days
        except Exception:
            days = None
        return {"name": name, "eq": eq, "le": le, "start": start, "day_pnl": eq - le,
                "day_ret": (eq / le - 1 if le else 0.0), "tot_ret": (eq / start - 1 if start else 0.0),
                "cash": float(a.get("cash") or 0.0), "pos": pos, "fills": fills, "days": days, "err": None}
    except Exception as exc:
        return {"name": name, "err": str(exc)[:60]}


def _benchmarks(today):
    """({sym: day_return}, last_session_iso) for QQQ/SPY — latest close vs the prior close, plus the
    date of that latest close (the last trading session; used to flag non-trading-day runs)."""
    try:
        import datetime as _dt
        from backtest import fetch_backtest_data
        end = _dt.date.fromisoformat(today)
        cl = fetch_backtest_data(["QQQ", "SPY"], end - _dt.timedelta(days=10), end)["Close"]
        out, last = {}, None
        for s in ("QQQ", "SPY"):
            v = (cl[s] if (hasattr(cl, "columns") and s in cl.columns) else cl).dropna()
            if len(v) >= 2 and float(v.iloc[-2]) > 0:
                out[s] = float(v.iloc[-1] / v.iloc[-2] - 1)
                last = v.index[-1]
        return out, (last.date().isoformat() if last is not None else None)
    except Exception:
        return {}, None


def run(accounts=None, end=None, out=None):
    today = end or date.today().isoformat()
    accts = accounts or DEFAULT_ACCOUNTS
    data = {n: _collect(n, today) for n in accts}
    out = Path(out) if out else ROOT / "reports" / f"eod_accounts_{today}.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)

    with PdfPages(out) as pdf:
        # Page 1: summary table + strategy descriptions
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle("End-of-Day - Daily Activity & P&L (all accounts)   %s" % today, fontsize=14, weight="bold")
        ax = fig.add_axes([0.04, 0.52, 0.92, 0.36]); ax.axis("off")
        cols = ["Account", "Strategy", "Equity", "Cash", "Day P&L", "Day % inv", "Total %", "Days", "Pos", "Trades"]

        def _dayinv(d):                                    # 1D P&L as % of INVESTED capital (equity - cash)
            inv = max(d.get("eq", 0.0) - d.get("cash", 0.0), 0.0)
            return (d["day_pnl"] / inv) if inv > 1 else 0.0
        cells = []
        for n in accts:
            d, label = data[n], textwrap.fill(_blurb(n)[0], 24)
            if d.get("err"):
                cells.append([n, label, "—", "—", "ERR", "—", "—", "—", "—", "—"])
            else:
                cells.append([n, label, _money(d["eq"]), _money(d["cash"]), _money(d["day_pnl"]),
                              _pct(_dayinv(d)), _pct(d["tot_ret"]),
                              (str(d["days"]) if d.get("days") is not None else "—"),
                              str(len(d["pos"])), str(len(d["fills"]))])
        # TOTAL row — aggregate across the accounts that resolved (skip errored ones)
        ok = [data[n] for n in accts if not data[n].get("err")]
        tot = {k: sum(d[k] for d in ok) for k in ("eq", "le", "start", "cash", "day_pnl")} if ok else {}
        tot_inv = max(tot.get("eq", 0.0) - tot.get("cash", 0.0), 0.0)
        tot_day = (tot["day_pnl"] / tot_inv) if tot_inv > 1 else 0.0
        tot_ret = (tot["eq"] / tot["start"] - 1) if tot.get("start") else 0.0
        tot_pos = sum(len(d["pos"]) for d in ok)
        tot_trd = sum(len(d["fills"]) for d in ok)
        cells.append(["TOTAL", "%d accounts" % len(ok), _money(tot.get("eq", 0.0)), _money(tot.get("cash", 0.0)),
                      _money(tot.get("day_pnl", 0.0)), _pct(tot_day), _pct(tot_ret), "—",
                      str(tot_pos), str(tot_trd)])
        # benchmark rows: QQQ/SPY today's index return (in the Day % col; the rest N/A for an index)
        bm, last_session = _benchmarks(today)
        bm_syms = [s for s in ("QQQ", "SPY") if s in bm]
        closed = bool(last_session and last_session < today)   # report run on a non-trading day (weekend/holiday)
        if closed:
            fig.text(0.5, 0.925, "MARKET CLOSED on %s  —  equity / P&L are as of the last session "
                     "(%s close); any orders submitted now queue for the next open."
                     % (today, last_session), ha="center", fontsize=8.5, color=RED, weight="bold")
        for s in bm_syms:
            cells.append([s, "benchmark (index)", "—", "—", "—", _pct(bm[s]), "—", "—", "—", "—"])
        raw = [11, 24, 11, 10, 10, 9, 8, 6, 5, 7]          # Strategy widest; normalized to sum 1
        colw = [w / sum(raw) for w in raw]
        t = ax.table(cellText=cells, colLabels=cols, colWidths=colw, loc="center", cellLoc="center")
        t.auto_set_font_size(False); t.set_fontsize(7.5); t.scale(1, 1.45)
        for j in range(len(cols)):
            t[0, j].set_facecolor("#34495e"); t[0, j].set_text_props(color="white", weight="bold")
        for i, n in enumerate(accts):
            d = data[n]
            if d.get("err"):
                continue
            for j, val in [(4, d["day_pnl"]), (5, d["day_pnl"]), (6, d["tot_ret"])]:
                t[i + 1, j].set_text_props(color=(GREEN if val >= 0 else RED), weight="bold")
            t[i + 1, 1].set_text_props(fontsize=6.5)
        # style the TOTAL row: shaded + bold, P&L/returns colored
        tr = len(accts) + 1
        for j in range(len(cols)):
            t[tr, j].set_facecolor("#dfe6e9"); t[tr, j].set_text_props(weight="bold")
        for j, val in [(4, tot.get("day_pnl", 0.0)), (5, tot.get("day_pnl", 0.0)), (6, tot_ret)]:
            t[tr, j].set_text_props(color=(GREEN if val >= 0 else RED), weight="bold")
        # benchmark rows (after TOTAL): italic/grey, colored Day %
        for k, s in enumerate(bm_syms):
            row = tr + 1 + k
            for j in range(len(cols)):
                t[row, j].set_text_props(style="italic", color="#555")
            t[row, 5].set_text_props(color=(GREEN if bm[s] >= 0 else RED), weight="bold", style="italic")
        fig.text(0.04, 0.495, "Day % inv = 1D P&L as % of invested capital (equity - cash); "
                 "Days = calendar days since inception; QQQ/SPY rows = index day return.",
                 fontsize=6.5, color="#666")
        ax2 = fig.add_axes([0.04, 0.02, 0.92, 0.46]); ax2.axis("off")
        ax2.text(0, 1.0, "Strategies", fontsize=11, weight="bold", va="top")
        y = 0.92
        for n in accts:
            label, blurb = _blurb(n)
            ax2.text(0, y, "%s  —  %s" % (n, label), fontsize=8.5, weight="bold", va="top"); y -= 0.045
            for line in textwrap.wrap(blurb, 130):
                ax2.text(0.02, y, line, fontsize=7.5, va="top", color="#333"); y -= 0.038
            y -= 0.02
        pdf.savefig(fig); plt.close(fig)

        # Page 2: today's activity (fills)
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle("Today's Activity (fills) - %s" % today, fontsize=13, weight="bold")
        if closed:
            fig.text(0.5, 0.945, "Market closed on %s — no fills expected; orders queue for the next "
                     "session (last close %s)." % (today, last_session), ha="center", fontsize=8,
                     color=RED, style="italic")
        ax = fig.add_axes([0.05, 0.04, 0.9, 0.88]); ax.axis("off")
        y = 1.0
        for n in accts:
            d = data[n]
            ax.text(0, y, "%s  (%s)" % (n, _blurb(n)[0]), fontsize=10, weight="bold", va="top"); y -= 0.04
            if d.get("err"):
                ax.text(0.03, y, "broker error: %s" % d["err"], fontsize=8, color=RED, va="top"); y -= 0.05
                continue
            if not d["fills"]:
                ax.text(0.03, y, "— no trades today —", fontsize=8, color="#777", va="top"); y -= 0.05
                continue
            for o in sorted(d["fills"], key=lambda x: x.get("symbol", "")):
                q = float(o.get("filled_qty") or 0); px = float(o.get("fill_price") or 0)
                side = o.get("side", "").upper()
                ax.text(0.03, y, "%-4s %-6s %5d @ $%-9.2f   = %s" % (side, o.get("symbol", ""), q, px, _money(q * px)),
                        fontsize=8, family="monospace", va="top", color=(GREEN if side == "BUY" else RED))
                y -= 0.032
            y -= 0.02
        pdf.savefig(fig); plt.close(fig)

    return {"pdf": str(out), "data": data}


if __name__ == "__main__":
    print(run()["pdf"])
