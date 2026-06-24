"""eod_summary.py — one consolidated END-OF-DAY summary across the model_v4 scenario and the broker
account trackers (topten/copymodel/rampup). The EOD sibling of midday_summary.

For each book it builds the EOD view (held book marked to the session CLOSE, the 1-day overlay hedge
SOLD at the close), renders that book's own EOD PDF into reports/eod/, and rolls the headline numbers
(PV, day return vs SPY/QQQ, held-book move, realized hedge P&L, #positions) into one comparison table
written to reports/eod_summary_<date>.md.

CLI:
    python src/eod_summary.py [--end YYYY-MM-DD] [--prepost] [--no-pdf] [--accounts a b c]
    python run.py eod-summary  [--end …] [--prepost] [--no-pdf]
"""
from __future__ import annotations

import sys
import argparse
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

DEFAULT_SCENARIO = "model_v4"
DEFAULT_ACCOUNTS = ["topten", "copymodel", "rampup"]


def _book_view(scenario: str, end: Optional[date], account: Optional[str] = None,
               prepost: bool = False, want_pdf: bool = True) -> "tuple[Dict[str, Any], str, Optional[Path]]":
    """Build one book's EOD view (and optionally its PDF into reports/eod/). Mirrors pdf_report.run:
    account mode serves the frozen+living ledger marked to the close; scenario mode runs the backtest.
    `at_close=True` exits the overlay hedge at the session close (guarded to a final close)."""
    import rank_report
    import pdf_report
    import midday_summary as MS
    from scenarios import build_config, load_scenario
    from backtest import load_config as _load_cfg
    man = None
    start: Optional[date] = None
    if account:
        from account import load_manifest
        man = load_manifest(account)
        scenario = scenario or man["scenario"]
        start = date.fromisoformat(man["inception"])
    end = end or date.today()
    start = start or date(end.year, 1, 1)
    cfg = build_config(_load_cfg(ROOT / "config"), load_scenario(scenario))
    # write_snapshot=False: a SUMMARY render must not mutate the authoritative ranking snapshot
    # (that's `run.py eod`'s job); everything else matches the EOD render.
    d = rank_report.build_report(scenario, start, end, cfg=cfg, write_snapshot=False,
                                 with_intraday=True, account=account, prepost=prepost, at_close=True)
    # Broker accounts: overlay the live Alpaca book (real fills + equity). Live render only.
    if account and end >= date.today():
        try:
            import broker_sync
            broker_sync.apply_live_broker_marks(d, account)
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning("live broker marks skipped for %s: %s", account, exc)
    pdf: Optional[Path] = None
    if want_pdf:
        pdf = pdf_report.build_pdf(d, cfg, pdf_report.report_path(scenario, account, d["mark"]))
    label = MS._account_label(account, man) if account else f"{scenario} · scenario"
    return d, label, pdf


def build_summary(end: Optional[date] = None, accounts: Optional[List[str]] = None,
                  scenario: str = DEFAULT_SCENARIO, prepost: bool = False,
                  want_pdf: bool = True) -> List[Dict[str, Any]]:
    """One summary row per book: the model_v4 scenario first, then each account. A book that fails to
    build is captured as an `error` row rather than aborting the whole summary."""
    accounts = DEFAULT_ACCOUNTS if accounts is None else accounts
    specs: List[tuple] = [(scenario, None)] + [(scenario, a) for a in accounts]
    rows: List[Dict[str, Any]] = []
    for scen, acct in specs:
        try:
            d, label, pdf = _book_view(scen, end, account=acct, prepost=prepost, want_pdf=want_pdf)
            stats = d.get("stats") or {}
            since_key = next((k for k in stats if str(k).startswith("Since ")), None)
            hed = d.get("hedge") or {}
            rows.append({
                "label": label, "account": acct, "mark": d["mark"],
                "pv": d.get("pv"), "n_positions": len(d.get("positions")),
                "day": stats.get("1D"), "since": stats.get(since_key) if since_key else None,
                "since_label": since_key, "held_dw": d.get("held_dw"),
                "hedge_pnl": (hed.get("realized_pnl") if hed.get("closed") else None),
                "pdf": str(pdf) if pdf else None,
            })
        except Exception as e:                       # one bad book shouldn't sink the summary
            rows.append({"label": (acct or scen), "account": acct,
                         "error": f"{type(e).__name__}: {e}"})
    return rows


def _pct(v: Optional[float]) -> str:
    return "—" if v is None else f"{v * 100:+.2f}%"


def _money(v: Optional[float]) -> str:
    return "—" if v is None else (("+$" if v >= 0 else "−$") + format(abs(round(v)), ","))


def render_md(rows: List[Dict[str, Any]], end: date) -> str:
    ok = [r for r in rows if not r.get("error")]
    since_lbl = next((r.get("since_label") for r in ok if r.get("since_label")), "Since inception")
    L = [
        "# End-of-Day — cross-book summary",
        f"**Marked to close:** {end.isoformat()}  |  **Generated:** {date.today().isoformat()}  |  "
        f"**Books:** {len(ok)}/{len(rows)}",
        "",
        "_All books on model_v4, marked to the official close (the 1-day overlay hedge is sold at the "
        "close). Day = portfolio return vs the prior close. Held DW = dollar-weighted held-book return. "
        "Hedge P&L = realized P&L of the overlay hedge exit (— if it didn't fire)._",
        "",
        f"| Book | Close | PV | Day (port / SPY / QQQ) | {since_lbl} (port) | Held DW | Hedge P&L | #Pos |",
        "|------|:-----:|---:|:----------------------:|------:|------:|------:|:----:|",
    ]
    for r in rows:
        if r.get("error"):
            L.append(f"| {r['label']} | — | — | **ERROR:** {r['error']} | — | — | — | — |")
            continue
        day = r.get("day") or {}
        daycell = f"{_pct(day.get('port'))} / {_pct(day.get('spy'))} / {_pct(day.get('qqq'))}"
        since = (r.get("since") or {}).get("port")
        L.append(
            f"| {r['label']} | {r['mark']} | ${r['pv']:,.0f} | {daycell} | {_pct(since)} "
            f"| {_pct(r.get('held_dw'))} | {_money(r.get('hedge_pnl'))} | {r['n_positions']} |")
    L += ["", "### Per-book EOD reports", ""]
    for r in rows:
        if r.get("error"):
            continue
        rel = Path(r["pdf"]).relative_to(ROOT) if r.get("pdf") else None
        L.append(f"- **{r['label']}** — {rel if rel else '(PDF skipped)'}")
    L.append("")
    return "\n".join(L)


def _pnl_str(x: Optional[float]) -> str:
    if x is None:
        return "—"
    return ("+$" if x >= 0 else "−$") + format(abs(round(x)), ",")


def build_summary_pdf(rows: List[Dict[str, Any]], out_path: Path, end: date) -> Path:
    """One-page consolidated EOD summary PDF (the cross-book table as a PDF, like the snapshot)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    import pdf_report as P
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    ok = [r for r in rows if not r.get("error")]
    with PdfPages(out_path) as pdf:
        fig, ax = P._new_page(pdf)
        ax.add_patch(plt.Rectangle((0, 0.93), 1, 0.07, transform=ax.transAxes,
                                   facecolor=P.NAVY, edgecolor="none", zorder=0))
        ax.text(0.06, 0.965, "End-of-Day Summary — model_v4 + Alpaca accounts",
                color="white", fontsize=15, fontweight="bold", va="center")
        ax.text(0.06, 0.943, "Marked to the official close · overlay hedge sold at the close",
                color="#b9c6d8", fontsize=8.5, va="center")
        ax.text(0.94, 0.958, end.isoformat(), color="white", fontsize=11,
                fontweight="bold", va="center", ha="right")

        scen = next((r for r in ok if r.get("account") is None), None)
        accts = [r for r in ok if r.get("account") is not None]
        cards = []
        if scen:
            cards.append(("model_v4 day", P._pct((scen.get("day") or {}).get("port")),
                          P._ret_color((scen.get("day") or {}).get("port"))))
            cards.append(("model_v4 equity", P._money(scen.get("pv")), P.NAVY))
        if accts:
            cards.append(("accounts equity (Σ)", P._money(sum(r.get("pv") or 0 for r in accts)), P.NAVY))
        hpnl = sum((r.get("hedge_pnl") or 0) for r in ok)
        cards.append(("hedge P&L (Σ)", _pnl_str(hpnl), P._ret_color(hpnl)))
        y = P._cards(ax, 0.885, cards) if cards else 0.86

        y = P._section(ax, y - 0.01, "Books — close-marked return, held book, and hedge")
        cols = ["Book", "PV", "Day", "SPY", "QQQ", "Since incep", "Held DW", "Hedge P&L", "#Pos"]
        widths = [0.235, 0.105, 0.075, 0.07, 0.07, 0.092, 0.085, 0.098, 0.05]
        align = ["left", "right", "right", "right", "right", "right", "right", "right", "center"]

        def _trow(r):
            lbl = str(r["label"]).replace("model-equal(primary)", "model-eq").replace("model-equal", "model-eq")
            if r.get("error"):
                return [lbl, "—", "ERR", "—", "—", "—", "—", "—", "—"]
            day = r.get("day") or {}
            return [lbl, P._money(r.get("pv")), P._pct(day.get("port")), P._pct(day.get("spy")),
                    P._pct(day.get("qqq")), P._pct((r.get("since") or {}).get("port")),
                    P._pct(r.get("held_dw")), _pnl_str(r.get("hedge_pnl")), str(r.get("n_positions", 0))]

        def cb(ri, ci, v):
            if ci == 0:
                return P.NAVY
            if ci == 7:                                  # Hedge P&L ($) — colour by sign
                return P.GREEN if v.startswith("+") else (P.RED if v.startswith("−") else "#1f2a3a")
            if ci in (2, 3, 4, 5, 6):                    # % columns
                return P._ret_color(P._parse_pct(v))
            return "#1f2a3a"

        scen_rows = [r for r in rows if r.get("account") is None]
        acct_rows = [r for r in rows if r.get("account") is not None]
        y = P._section(ax, y - 0.01, "Simulated reference — model_v4 scenario (backtest)")
        if scen_rows:
            y = P._table(ax, y, cols, [_trow(r) for r in scen_rows], widths, align=align,
                         text_color=cb, row_h=0.032, fontsize=8.2, header_fontsize=7.3, emph_rows={0})
        y = P._section(ax, y - 0.016, "Live Alpaca paper accounts (marked to close)")
        y = P._table(ax, y, cols, [_trow(r) for r in acct_rows], widths, align=align,
                     text_color=cb, row_h=0.032, fontsize=8.2, header_fontsize=7.3)

        y = P._section(ax, y - 0.018, "Per-book EOD reports")
        links = [f"{r['label']} — {Path(r['pdf']).relative_to(ROOT)}" for r in ok if r.get("pdf")]
        if links:
            y = P._bullets(ax, y, links, width=120, lh=0.018, gap=0.004, fontsize=7.8)
        else:
            ax.text(0.06, y, "(per-book PDFs skipped — run without --no-pdf)", color=P.MIDGREY,
                    fontsize=7.8, va="top"); y -= 0.02

        note = ("All books on model_v4, marked to the official close (the 1-day overlay hedge is sold "
                "at the close). Day = portfolio return vs the prior close (port/SPY/QQQ); session/held "
                "returns are hedge-inclusive. Since incep = since each book's inception (the scenario "
                "from its backtest start; accounts from their funding date — so it differs by row). "
                "Held DW = dollar-weighted held-book return. Hedge P&L = realized P&L of the overlay "
                "hedge exit. Paper-trading research only — not advice.")
        import textwrap
        ax.text(0.06, y - 0.015, textwrap.fill(note, 132), color=P.MIDGREY, fontsize=7.3, va="top")
        ax.text(0.94, 0.022, f"eod-summary · {end.isoformat()}", color=P.MIDGREY, fontsize=6.5,
                va="center", ha="right")
        pdf.savefig(fig)
        plt.close(fig)
    return out_path


def run(end: Optional[date] = None, output: Optional[Path] = None,
        accounts: Optional[List[str]] = None, scenario: str = DEFAULT_SCENARIO,
        prepost: bool = False, want_pdf: bool = True) -> "tuple[Path, List[Dict[str, Any]]]":
    end = end or date.today()
    rows = build_summary(end=end, accounts=accounts, scenario=scenario,
                         prepost=prepost, want_pdf=want_pdf)
    # consolidated summary is a PDF (parallel to the snapshot); the .md is written alongside.
    (ROOT / "reports" / f"eod_summary_{end.isoformat()}.md").write_text(render_md(rows, end))
    out = Path(output) if output else ROOT / "reports" / f"eod_summary_{end.isoformat()}.pdf"
    build_summary_pdf(rows, out, end)
    return out, rows


def main(argv=None):
    ap = argparse.ArgumentParser(description="Consolidated End-of-Day summary across model_v4 + account trackers")
    ap.add_argument("--end", metavar="YYYY-MM-DD")
    ap.add_argument("--accounts", nargs="*", help="override the default account list (topten/copymodel/rampup)")
    ap.add_argument("--prepost", action="store_true", help="mark books to the latest pre/post-market print")
    ap.add_argument("--no-pdf", action="store_true", help="summary only; skip each book's EOD PDF")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    out, rows = run(end=date.fromisoformat(a.end) if a.end else None,
                    output=Path(a.out) if a.out else None,
                    accounts=a.accounts or None, prepost=a.prepost, want_pdf=not a.no_pdf)
    ok = sum(1 for r in rows if not r.get("error"))
    print(f"Wrote {out}  ({ok}/{len(rows)} books)")
    for r in rows:
        if r.get("error"):
            print(f"  ! {r['label']}: {r['error']}")


if __name__ == "__main__":
    main()
