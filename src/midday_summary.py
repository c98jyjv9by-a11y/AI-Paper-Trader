"""midday_summary.py — one consolidated Midday Pulse SUMMARY across the model_v4 scenario and the
broker account trackers (topten/copymodel/rampup).

For each book it builds the SAME intraday view the per-book Midday Pulse uses (held book marked to
the latest provisional price, NO snapshot write), optionally renders that book's own midday PDF,
then rolls the headline numbers (PV, day return vs SPY/QQQ, held-book move, signal spread, #positions)
into a single comparison table written to reports/midday_summary_<date>.md.

CLI:
    python src/midday_summary.py [--end YYYY-MM-DD] [--prepost] [--no-pdf] [--accounts a b c]
    python run.py midday-summary  [--end …] [--prepost] [--no-pdf]
"""
from __future__ import annotations

import sys
import argparse
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from eod_accounts import disp                         # friendly account display names (shared)

DEFAULT_SCENARIO = "model_v4"
DEFAULT_ACCOUNTS = ["topten", "copymodel", "rampup"]


def _account_label(name: str, man: Optional[Dict[str, Any]]) -> str:
    """Short, human label describing an account's target mode (for the summary's Book column)."""
    tm = (man or {}).get("target_mode") or {}
    kind = tm.get("kind")
    if kind == "top_n":
        return f"{name} · top-{tm.get('n', 10)}"
    if kind == "model_equal":
        return f"{name} · model-equal({tm.get('source', 'primary')})"
    if kind == "score_gate":
        return f"{name} · score≥{tm.get('min_score', 0.9):g}"
    if kind == "model_v4":
        return f"{name} · model_v4"
    if kind == "score_gate_rampup":
        return f"{name} · score-gate ramp-up"
    return f"{name} · ramp-up"


def _book_view(scenario: str, end: Optional[date], account: Optional[str] = None,
               prepost: bool = False, want_pdf: bool = True) -> "tuple[Dict[str, Any], str, Optional[Path]]":
    """Build one book's midday view (and optionally its PDF). Mirrors midday_pdf.run: account mode
    serves the frozen+living ledger marked to `end`; scenario mode runs a fresh model_v4 backtest."""
    import rank_report
    import midday_pdf
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
    d = rank_report.build_report(scenario, start, end, cfg=cfg, write_snapshot=False,
                                 account=account, prepost=prepost)
    # Broker accounts: overlay the live Alpaca book (real avg-entry + current price + equity) so the
    # summary's intraday returns reflect actual fills, not the ledger. Live render only.
    if account and end >= date.today():
        try:
            import broker_sync
            broker_sync.apply_live_broker_marks(d, account)
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning("live broker marks skipped for %s: %s", account, exc)
    pdf: Optional[Path] = None
    if want_pdf:
        pdf = midday_pdf.build_pdf(d, cfg, midday_pdf.report_path(scenario, account, d["mark"]))
    label = disp(account) if account else f"{scenario} · scenario"
    return d, label, pdf


def build_summary(end: Optional[date] = None, accounts: Optional[List[str]] = None,
                  scenario: str = DEFAULT_SCENARIO, prepost: bool = False,
                  want_pdf: bool = True) -> List[Dict[str, Any]]:
    """One summary row per book: the model_v4 scenario first, then each account tracker. A book that
    fails to build is captured as an `error` row rather than aborting the whole summary."""
    accounts = DEFAULT_ACCOUNTS if accounts is None else accounts
    specs: List[tuple] = [(scenario, None)] + [(scenario, a) for a in accounts]
    rows: List[Dict[str, Any]] = []
    for scen, acct in specs:
        try:
            d, label, pdf = _book_view(scen, end, account=acct, prepost=prepost, want_pdf=want_pdf)
            stats = d.get("stats") or {}
            since_key = next((k for k in stats if str(k).startswith("Since ")), None)
            rows.append({
                "label": label, "account": acct, "mark": d["mark"],
                "pv": d.get("pv"), "n_positions": len(d.get("positions")),
                "n_gate_cur": d.get("n_gate_cur"),
                "day": stats.get("1D"), "since": stats.get(since_key) if since_key else None,
                "since_label": since_key, "held_dw": d.get("held_dw"),
                "signal": d.get("signal_strength"),
                "pdf": str(pdf) if pdf else None,
            })
        except Exception as e:                       # one bad book shouldn't sink the summary
            rows.append({"label": (disp(acct) if acct else scen), "account": acct,
                         "error": f"{type(e).__name__}: {e}"})
    return rows


def _pct(v: Optional[float]) -> str:
    return "—" if v is None else f"{v * 100:+.2f}%"


def render_md(rows: List[Dict[str, Any]], end: date) -> str:
    ok = [r for r in rows if not r.get("error")]
    since_lbl = next((r.get("since_label") for r in ok if r.get("since_label")), "Since inception")
    L = [
        "# Midday Pulse — cross-book summary",
        f"**Marked:** {end.isoformat()}  |  **Generated:** {date.today().isoformat()}  |  "
        f"**Books:** {len(ok)}/{len(rows)}",
        "",
        "_All books on model_v4. Day = portfolio return vs the prior close (provisional intraday), "
        "SPY/QQQ for context. Held DW = dollar-weighted return of the held book today. "
        "Signal = top-10 minus bottom-10 avg return on the prior-close ranking._",
        "",
        f"| Book | Marked | PV | Day (port / SPY / QQQ) | {since_lbl} (port) | Held DW | Signal | #Pos |",
        "|------|:------:|---:|:----------------------:|------:|------:|------:|:----:|",
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
            f"| {_pct(r.get('held_dw'))} | {_pct(r.get('signal'))} | {r['n_positions']} |")
    L += ["", "### Per-book midday reports", ""]
    for r in rows:
        if r.get("error"):
            continue
        rel = Path(r["pdf"]).relative_to(ROOT) if r.get("pdf") else None
        L.append(f"- **{r['label']}** — {rel if rel else '(PDF skipped)'}")
    L.append("")
    return "\n".join(L)


def run(end: Optional[date] = None, output: Optional[Path] = None,
        accounts: Optional[List[str]] = None, scenario: str = DEFAULT_SCENARIO,
        prepost: bool = False, want_pdf: bool = True) -> "tuple[Path, List[Dict[str, Any]]]":
    end = end or date.today()
    rows = build_summary(end=end, accounts=accounts, scenario=scenario,
                         prepost=prepost, want_pdf=want_pdf)
    md = render_md(rows, end)
    out = Path(output) if output else ROOT / "reports" / f"midday_summary_{end.isoformat()}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md)
    return out, rows


def main(argv=None):
    ap = argparse.ArgumentParser(description="Consolidated Midday Pulse summary across model_v4 + account trackers")
    ap.add_argument("--end", metavar="YYYY-MM-DD")
    ap.add_argument("--accounts", nargs="*", help="override the default account list (topten/copymodel/rampup)")
    ap.add_argument("--prepost", action="store_true", help="mark books to the latest pre/post-market print")
    ap.add_argument("--no-pdf", action="store_true", help="summary only; skip each book's midday PDF")
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
