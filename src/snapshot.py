"""snapshot.py — one-page PDF PERFORMANCE SNAPSHOT across the model_v4 scenario and the broker
accounts (topten/copymodel/rampup).

Unlike the intraday `midday-summary` (Day / Held-DW / Signal columns), this is a performance view:
return over a configurable trailing `--window` (default **1D** = since the prior close; also 5D / 1M /
MTD / YTD / …) and how it stacks up vs SPY / QQQ over that same window, plus current equity/cash and
1D P&L. Broker accounts are marked to their LIVE Alpaca book (real equity + holdings).

CLI:
    python src/snapshot.py [--end YYYY-MM-DD] [--accounts a b c] [--out FILE]
    python run.py snapshot  [--end …]
"""
from __future__ import annotations

import sys
import argparse
import textwrap
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

DEFAULT_SCENARIO = "model_v4"
DEFAULT_WINDOW = "1D"
# friendly display names + one-line definitions for the snapshot (keyed by account name)
DISPLAY = {"topten": "Top 10 Seed", "copymodel": "Existing Model Seed", "rampup": "Ramp Up"}
DEFINITIONS = {
    "model_v4": "model_v4 · scenario — the model_v4 momentum strategy backtest (83-name semis/AI/tech "
                "universe, Barroso vol-targeting) from its backtest start. Simulated, not a broker account.",
    "topten": "Top 10 Seed — Alpaca paper account holding the 10 highest CURRENT composite-score names, "
              "~8.5% each, rebalanced toward that set.",
    "copymodel": "Existing Model Seed — Alpaca paper account that EQUAL-WEIGHTS the names the live model_v4 "
                 "book (primary) currently holds.",
    "rampup": "Ramp Up — Alpaca paper account holding every name whose current composite score ≥ 0.9 at "
              "current ranks, 8.5% each (a score-gate ramp-up).",
}
# friendly window names → trailing TRADING-day counts (MTD/YTD are handled as calendar anchors)
_WMAP = {"1D": 1, "5D": 5, "10D": 10, "1M": 21, "3M": 63, "6M": 126, "1Y": 252}


def _anchor_date(cal, window: str):
    """The start of the common trailing window on the price calendar `cal` (a DatetimeIndex ending
    at the mark). MTD/YTD = calendar anchors; otherwise N trailing trading days (named or a raw int)."""
    import pandas as pd
    last = cal[-1]
    w = str(window).upper()
    if w == "MTD":
        return pd.Timestamp(last.year, last.month, 1)
    if w == "YTD":
        return pd.Timestamp(last.year, 1, 1)
    n = _WMAP.get(w) or int(w)
    return cal[-(n + 1)] if len(cal) > n else cal[0]


def _ret_from(series, anchor, end_val=None) -> Optional[float]:
    """Return of `series` from the last point at/before `anchor` to `end_val` (default: series end).
    None when the series has no point at/before the anchor (e.g. a book younger than the window)."""
    s = series[series.index <= anchor]
    if s.empty:
        return None
    a = float(s.iloc[-1])
    e = float(series.iloc[-1]) if end_val is None else float(end_val)
    return (e / a - 1) if a else None


def build_rows(end: Optional[date] = None, accounts: Optional[List[str]] = None,
               scenario: str = DEFAULT_SCENARIO, window: str = DEFAULT_WINDOW) -> List[Dict[str, Any]]:
    """One row per book (scenario first, then each account): equity + return over a COMMON trailing
    `window` (same anchor date for every book) + SPY/QQQ over that window + α (book − benchmark) +
    today's move + #positions. A book younger than the window shows '—' for its portfolio leg."""
    import midday_summary as MS
    accounts = MS.DEFAULT_ACCOUNTS if accounts is None else accounts
    specs = [(scenario, None)] + [(scenario, a) for a in accounts]
    w = str(window).upper()

    # Pass 1 — build each book's view (preserve order). Capture ONE reference benchmark series so the
    # market benchmarks (SPY/QQQ) are computed on the SAME final prices for every book (each book's
    # own yfinance pull jitters by a few bps; the benchmark is market-wide, so it must not differ).
    built: List[tuple] = []
    ref_spy = ref_qqq = None
    for scen, acct in specs:
        try:
            d, _label, _ = MS._book_view(scen, end, account=acct, want_pdf=False)
            label = DISPLAY.get(acct, _label) if acct else f"{scen} · scenario"
            built.append((acct, scen, label, d, None))
            if ref_spy is None and d.get("spy_series") is not None:
                ref_spy, ref_qqq = d.get("spy_series"), d.get("qqq_series")
        except Exception as e:                       # one bad book shouldn't sink the snapshot
            built.append((acct, scen, DISPLAY.get(acct, acct or scen), None, f"{type(e).__name__}: {e}"))

    # Unified benchmark return for the window — computed ONCE from the reference series.
    banchor = s_bench = q_bench = None
    if ref_spy is not None:
        banchor = (ref_spy.index[-2] if (w == "1D" and len(ref_spy.index) >= 2)
                   else _anchor_date(ref_spy.index, window))
        s_bench, q_bench = _ret_from(ref_spy, banchor), _ret_from(ref_qqq, banchor)
    anchor_str = str(banchor.date()) if banchor is not None else "—"

    # Pass 2 — assemble rows: book-specific return/P&L, SAME benchmark for all.
    rows: List[Dict[str, Any]] = []
    for acct, scen, label, d, err in built:
        if err is not None or d is None:
            rows.append({"label": label, "key": (acct or scen), "error": err or "no data"})
            continue
        stats = d.get("stats") or {}
        eqs = d.get("eq_series")
        pv, cash = d.get("pv"), d.get("cash")
        if w == "1D":
            # 1D = since the prior trading close. Use stats["1D"]["port"] so the BROKER day return
            # (live equity vs last_equity) is used for accounts, not the sparse ledger series.
            p = (stats.get("1D") or {}).get("port")
        else:
            p = _ret_from(eqs, banchor, end_val=pv) if banchor is not None else None
        pos = d.get("positions")
        mkt = (pv - cash) if (pv is not None and cash is not None) else pv   # held-positions value
        pnl = (pv * p / (1 + p)) if (pv is not None and p is not None and (1 + p) != 0) else None
        rows.append({
            "label": label, "key": (acct or scen), "anchor": anchor_str,
            "equity": pv, "cash": cash, "mkt_value": mkt, "ret": p, "pnl": pnl,
            "spy": s_bench, "qqq": q_bench,            # SAME benchmark for every book
            "vs_spy": (p - s_bench) if (p is not None and s_bench is not None) else None,
            "vs_qqq": (p - q_bench) if (p is not None and q_bench is not None) else None,
            "n_pos": (len(pos) if (pos is not None and not pos.empty) else 0),
        })
    return rows


def build_pdf(rows: List[Dict[str, Any]], out_path: Path, end: date, window: str = DEFAULT_WINDOW) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    import pdf_report as P
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    anchor = next((r.get("anchor") for r in rows if r.get("anchor")), None)
    wlabel = str(window).upper()
    with PdfPages(out_path) as pdf:
        fig, ax = P._new_page(pdf)
        # banner
        ax.add_patch(plt.Rectangle((0, 0.93), 1, 0.07, transform=ax.transAxes,
                                   facecolor=P.NAVY, edgecolor="none", zorder=0))
        ax.text(0.06, 0.965, "Performance Snapshot — model_v4 + Alpaca accounts",
                color="white", fontsize=15, fontweight="bold", va="center")
        ax.text(0.06, 0.943, f"{wlabel} return & {wlabel} P&L"
                + (f" (vs {anchor})" if anchor else "") + " · SPY / QQQ context · current marks",
                color="#b9c6d8", fontsize=8.5, va="center")
        ax.text(0.94, 0.958, end.isoformat(), color="white", fontsize=11,
                fontweight="bold", va="center", ha="right")

        def _pnl_str(x):
            if x is None:
                return "—"
            return ("+$" if x >= 0 else "−$") + format(abs(round(x)), ",")

        ok = [r for r in rows if not r.get("error")]
        accts = [r for r in ok if r.get("key") != "model_v4"]
        scen = next((r for r in ok if r.get("key") == "model_v4"), None)
        # headline cards: scenario window return + its P&L + aggregate account equity + accounts' P&L
        cards = []
        if scen:
            cards.append((f"model_v4 {wlabel} return", P._pct(scen.get("ret")), P._ret_color(scen.get("ret"))))
            cards.append((f"model_v4 {wlabel} P&L", _pnl_str(scen.get("pnl")), P._ret_color(scen.get("pnl"))))
        if accts:
            cards.append(("accounts equity (Σ)", P._money(sum(r.get("equity") or 0 for r in accts)), P.NAVY))
            apnl = sum((r.get("pnl") or 0) for r in accts)
            cards.append((f"accounts {wlabel} P&L (Σ)", _pnl_str(apnl), P._ret_color(apnl)))
        y = P._cards(ax, 0.885, cards) if cards else 0.86

        cols = ["Book", "Mkt Value", "Cash", f"{wlabel} Return", f"{wlabel} P&L", "SPY", "QQQ", "#Pos"]
        widths = [0.225, 0.115, 0.105, 0.10, 0.125, 0.085, 0.085, 0.055]
        align = ["left", "right", "right", "right", "right", "right", "right", "center"]

        def _trow(r):
            if r.get("error"):
                return [r["label"], "—", "—", "ERR", "—", "—", "—", "—"]
            return [r["label"], P._money(r.get("mkt_value")), P._money(r.get("cash")),
                    P._pct(r.get("ret")), _pnl_str(r.get("pnl")), P._pct(r.get("spy")),
                    P._pct(r.get("qqq")), str(r.get("n_pos", 0))]

        def cb(ri, ci, v):
            if ci == 0:
                return P.NAVY
            if ci == 4:                                  # the P&L ($) column — colour by sign
                return P.GREEN if v.startswith("+") else (P.RED if v.startswith("−") else "#1f2a3a")
            if ci in (3, 5, 6):                          # % columns: Return / SPY / QQQ
                return P._ret_color(P._parse_pct(v))
            return "#1f2a3a"

        # Group 1 — the SIMULATED model_v4 scenario (backtest reference), set apart from the live books.
        scen_rows = [r for r in rows if r.get("key") == "model_v4"]
        acct_rows = [r for r in rows if r.get("key") != "model_v4"]
        y = P._section(ax, y - 0.01, "Simulated reference — model_v4 scenario (backtest)")
        if scen_rows:
            y = P._table(ax, y, cols, [_trow(r) for r in scen_rows], widths, align=align,
                         text_color=cb, row_h=0.032, fontsize=8.2, header_fontsize=7.3, emph_rows={0})
        # Group 2 — the live Alpaca paper accounts: 3 ways to IMPLEMENT model_v4 on any given date.
        y = P._section(ax, y - 0.016, "Live Alpaca paper accounts — three ways to implement model_v4")
        explainer = ("Each account is a different way to put model_v4 to work at any given date: buy the "
                     "top-10 CURRENT ranks equally (Top 10 Seed), buy the model's CURRENT holdings "
                     "(Existing Model Seed), or ramp up by only buying names scoring > 0.9 each day (Ramp Up).")
        for ln in textwrap.wrap(explainer, 128):
            ax.text(0.06, y, ln, color=P.MIDGREY, fontsize=7.6, va="top", style="italic")
            y -= 0.016
        y -= 0.004
        y = P._table(ax, y, cols, [_trow(r) for r in acct_rows], widths, align=align,
                     text_color=cb, row_h=0.032, fontsize=8.2, header_fontsize=7.3)

        # Definitions of each book, in table order
        y = P._section(ax, y - 0.018, "Definitions")
        defs = [DEFINITIONS[r["key"]] for r in rows if r.get("key") in DEFINITIONS]
        y = P._bullets(ax, y, defs, width=128, lh=0.020, gap=0.006, fontsize=8.0)

        note = (f"{wlabel} Return / SPY / QQQ are measured over the {wlabel} window"
                + (f" (since {anchor})" if anchor else "") + " — for 1D, since the prior trading close. "
                f"{wlabel} P&L = the dollar change over that window (equity − equity at the window start). "
                "Broker accounts use live Alpaca equity vs the prior close; the model_v4 scenario uses its "
                "simulated equity. Mkt Value = market value of current holdings; Cash = cash balance "
                "(total equity = Mkt Value + Cash). Paper-trading research only — not advice.")
        ax.text(0.06, y - 0.02, textwrap.fill(note, 132), color=P.MIDGREY, fontsize=7.4, va="top")
        ax.text(0.94, 0.022, f"snapshot · {end.isoformat()}", color=P.MIDGREY, fontsize=6.5,
                va="center", ha="right")
        pdf.savefig(fig)
        plt.close(fig)
    return out_path


def run(end: Optional[date] = None, output: Optional[Path] = None, accounts: Optional[List[str]] = None,
        scenario: str = DEFAULT_SCENARIO, window: str = DEFAULT_WINDOW) -> "tuple[Path, List[Dict[str, Any]]]":
    end = end or date.today()
    rows = build_rows(end=end, accounts=accounts, scenario=scenario, window=window)
    out = Path(output) if output else ROOT / "reports" / f"snapshot_{end.isoformat()}.pdf"
    build_pdf(rows, out, end, window=window)
    return out, rows


def main(argv=None):
    ap = argparse.ArgumentParser(description="One-page performance snapshot: model_v4 + Alpaca accounts")
    ap.add_argument("--end", metavar="YYYY-MM-DD")
    ap.add_argument("--window", default=DEFAULT_WINDOW,
                    help="common trailing window for all books: 1D/5D/10D/1M/3M/6M/1Y, MTD, YTD, or an integer of trading days")
    ap.add_argument("--accounts", nargs="*", help="override the default account list (topten/copymodel/rampup)")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    out, rows = run(end=date.fromisoformat(a.end) if a.end else None,
                    output=Path(a.out) if a.out else None, accounts=a.accounts or None, window=a.window)
    ok = sum(1 for r in rows if not r.get("error"))
    print(f"Wrote {out}  ({ok}/{len(rows)} books)")
    for r in rows:
        if r.get("error"):
            print(f"  ! {r['label']}: {r['error']}")


if __name__ == "__main__":
    main()
