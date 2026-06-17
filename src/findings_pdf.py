"""
findings_pdf.py — Render the agent+context findings snapshot as a polished single-page PDF.

Pulls the Sonnet full-window matrix numbers from context_matrix_full.json (so they stay
accurate) and lays them out with the shared report styling, plus the hand-written
narrative + Haiku short-window cross-check.

    python src/findings_pdf.py        # -> reports/context_findings_snapshot.pdf
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib.backends.backend_pdf import PdfPages

sys.path.insert(0, str(Path(__file__).parent))
import pdf_report as P            # palette + _section/_table/_bullets/_new_page/_pct


def _vs(rows, sources, setting):
    for r in rows:
        if r["sources"] == sources and r["setting"] == setting:
            return r["vs_strict"]
    return None


def build(matrix_json: Path, out: Path) -> Path:
    d = json.loads(matrix_json.read_text())
    rows = d["rows"]
    w0, w1 = d["window"]
    b = d["bench"]
    order = ["none", "news", "macro", "macro+news"]

    out.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(out) as pdf:
        fig, ax = P._new_page(pdf)

        # Banner
        ax.add_patch(P.plt.Rectangle((0, 0.93), 1, 0.07, transform=ax.transAxes,
                                     facecolor=P.NAVY, edgecolor="none"))
        ax.text(0.06, 0.965, "Agent + Context Sources — Findings Snapshot",
                color="white", fontsize=15, fontweight="bold", va="center")
        ax.text(0.06, 0.943, "Does feeding an AI agent more info + autonomy beat just following model_v4?",
                color="#b9c6d8", fontsize=8.5, va="center")

        y = 0.905
        ax.text(0.06, y, "SETUP", color=P.MIDGREY, fontsize=7.5, fontweight="bold", va="top")
        y -= 0.018
        y = P._bullets(ax, y, [
            "Harness owns all fills/accounting; agent emits only structured trades, one day at a time, "
            "no look-ahead. strict = follow the model's queue exactly (fixed reference). "
            "balanced = mostly follow. discretionary = use own judgment. Scored as return vs strict."],
            width=120, lh=0.0145, gap=0.004, fontsize=7.6)

        # Headline reference
        y = P._section(ax, y - 0.004,
                       f"Sonnet 4.6  —  full window {w0} → {w1}")
        ax.text(0.075, y, f"Reference  strict = {P._pct(d['strict_ret'])}  "
                f"(≈ model {P._pct(b['model'])})   |   SPY {P._pct(b['SPY'])}  ·  QQQ {P._pct(b['QQQ'])}"
                "   —   every agent cell trailed strict.",
                color="#1f2a3a", fontsize=8.4, va="top", fontweight="bold")
        y -= 0.026

        # vs-strict matrix (settings × sources)
        hdr = ["Setting (vs strict)", "none", "+news", "+macro", "+macro&news"]
        mrows = []
        for setting in ("balanced", "discretionary"):
            mrows.append([setting] + [P._pct(_vs(rows, s, setting)) for s in order])
        y = P._table(ax, y, hdr, mrows, [0.28, 0.18, 0.18, 0.18, 0.18],
                     align=["left", "right", "right", "right", "right"],
                     text_color=lambda r, c, v: (P._ret_color(P._parse_pct(v)) if c >= 1 else "#1f2a3a"))

        # Key findings
        y = P._section(ax, y - 0.008, "Key findings  (deltas are 30–50pp — well above noise)")
        y = P._bullets(ax, y, [
            "Nothing beat strict. On a momentum bull tape the agent adds no alpha — only subtracts.",
            "Autonomy is destructive: discretion churned (100–160 trades) and bled −33 to −52pp vs strict.",
            "Context helps monotonically as DAMAGE CONTROL: none < news < macro < macro&news, in both "
            "settings. macro&news nearly halved the discretionary loss (−51.6% → −32.9%).",
            "Macro dominates; news is a small add-on (regime/breadth does most of the work).",
            "Best combo: macro&news + balanced (−0.44% vs strict, Sharpe ~3.0) — 'mostly follow the "
            "model, with full market context as a sanity check.'"],
            width=116, lh=0.0150, gap=0.005, fontsize=7.8)

        # Haiku cross-check
        y = P._section(ax, y - 0.006, "Cross-check  —  Haiku 4.5, short window (January, ~19 days)")
        y = P._bullets(ax, y, [
            "Weak model + short window = no clear signal: deltas were sub-1pp (within run-to-run noise).",
            "macro HURT Haiku slightly but HELPED Sonnet → a source's value is model-dependent; you "
            "cannot evaluate sources on a weak model.",
            "Autonomy's damage only became obvious over the longer window — short horizons hide it."],
            width=116, lh=0.0150, gap=0.005, fontsize=7.8)

        # Bottom line
        y = P._section(ax, y - 0.006, "Bottom line")
        y = P._bullets(ax, y, [
            "Trust the model; use context as a guardrail, not a license to deviate. Macro > news, and a "
            "capable model (Sonnet ≫ Haiku) is required to use context at all.",
            "Caveat: one strong-momentum bull window where model_v4 is near-optimal — so 'follow the "
            "model' winning is expected. Decisive next test: a choppy/selloff OOS window."],
            width=116, lh=0.0150, gap=0.005, fontsize=7.8)

        # Footer
        ax.add_line(P.plt.Line2D([0.06, 0.94], [0.035, 0.035], color=P.RULE, lw=0.8))
        ax.text(0.06, 0.022, "Paper-trading research only — not investment advice. Simulated; "
                "single window, not OOS-validated.", color=P.MIDGREY, fontsize=6.5, va="center")
        ax.text(0.94, 0.022, "context-findings-snapshot", color=P.MIDGREY, fontsize=6.5,
                va="center", ha="right")
        pdf.savefig(fig); P.plt.close(fig)
    return out


def main():
    root = Path(__file__).parent.parent
    mj = root / "reports" / "context_matrix_full.json"
    out = root / "reports" / "context_findings_snapshot.pdf"
    build(mj, out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
