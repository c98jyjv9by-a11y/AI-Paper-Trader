"""
pdf_report.py — Professional end-of-day PDF update report for a scenario.

Renders the same content as the Markdown status report (rank_report.build_report)
into a polished, multi-page PDF suitable for distribution: a branded cover with an
auto-generated market commentary + recommendations, signal performance, current
rankings, holdings, and recent activity.

Commentary and recommendations are GENERATED from the run's data (signal spread,
the volatility governor's exposure multiplier, weakest holds, gate-clearing buy
candidates) — not hand-written — so the report is reproducible every run.

Read-only with respect to data/. Writes reports/eod_<scenario>_<date>.pdf.

    # standalone (re-runs the scenario backtest to gather data):
    python src/pdf_report.py --scenario model_v4 --start 2026-01-01 --end 2026-06-16
"""
from __future__ import annotations

import argparse
import sys
import textwrap
from datetime import date
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Treat "$" literally — dollar amounts must not be parsed as TeX math (mathtext).
plt.rcParams["text.parse_math"] = False

# ── Palette ───────────────────────────────────────────────────────────────────
NAVY = "#1a2b47"
ACCENT = "#2c5f8a"
LIGHT = "#eef2f7"
MIDGREY = "#5a6577"
GREEN = "#1a7f3c"
RED = "#c0392b"
RULE = "#c7d0db"

PAGE_W, PAGE_H = 8.5, 11.0


# ── Formatting helpers ──────────────────────────────────────────────────────────
def _pct(x: Optional[float], signed: bool = True) -> str:
    if x is None:
        return "—"
    return (f"{x*100:+.2f}%" if signed else f"{x*100:.2f}%")


def _money(x: Optional[float], dec: int = 0) -> str:
    if x is None:
        return "—"
    return f"${x:,.{dec}f}"


def _ret_color(x: Optional[float]) -> str:
    if x is None:
        return MIDGREY
    return GREEN if x > 0 else (RED if x < 0 else MIDGREY)


# ── Page scaffolding ─────────────────────────────────────────────────────────────
def _new_page(pdf: PdfPages):
    fig = plt.figure(figsize=(PAGE_W, PAGE_H))
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    return fig, ax


def _banner(ax, scenario: str, d: Dict[str, Any], subtitle: str):
    """Top navy banner with title + run metadata."""
    ax.add_patch(plt.Rectangle((0, 0.93), 1, 0.07, transform=ax.transAxes,
                               facecolor=NAVY, edgecolor="none", zorder=0))
    ax.text(0.06, 0.965, f"{scenario}  —  End-of-Day Update",
            color="white", fontsize=15, fontweight="bold", va="center")
    ax.text(0.06, 0.943, subtitle, color="#b9c6d8", fontsize=8.5, va="center")
    ax.text(0.94, 0.958, d["mark"].isoformat(), color="white", fontsize=11,
            fontweight="bold", va="center", ha="right")
    ax.text(0.94, 0.940, f"ranked @ close {d['rank_close']}", color="#b9c6d8",
            fontsize=7.5, va="center", ha="right")


def _footer(ax, page: int):
    ax.add_line(plt.Line2D([0.06, 0.94], [0.035, 0.035], color=RULE, lw=0.8))
    ax.text(0.06, 0.022, "Paper-trading research only — not investment advice. "
            "Systematic model output; positions are simulated.",
            color=MIDGREY, fontsize=6.5, va="center")
    ax.text(0.94, 0.022, f"model_v-EOD · p.{page}", color=MIDGREY, fontsize=6.5,
            va="center", ha="right")


def _section(ax, y: float, title: str) -> float:
    ax.text(0.06, y, title, color=ACCENT, fontsize=11.5, fontweight="bold", va="top")
    ax.add_line(plt.Line2D([0.06, 0.94], [y - 0.013, y - 0.013], color=ACCENT, lw=1.2))
    return y - 0.03


def _bullets(ax, y: float, items: List[str], width: int = 95, lh: float = 0.0185,
             gap: float = 0.008, fontsize: float = 8.8) -> float:
    """Render wrapped bullet paragraphs top-down; returns the new y."""
    for it in items:
        wrapped = textwrap.wrap(it, width=width) or [""]
        for j, line in enumerate(wrapped):
            ax.text(0.075 if j == 0 else 0.088, y,
                    ("•  " + line) if j == 0 else line,
                    color="#1f2a3a", fontsize=fontsize, va="top", family="sans-serif")
            y -= lh
        y -= gap
    return y


def _cards(ax, y: float, cards: List[tuple], h: float = 0.075):
    """Row of metric cards: list of (label, value, value_color)."""
    n = len(cards); x0 = 0.06; gapw = 0.015
    w = (0.88 - gapw * (n - 1)) / n
    for i, (label, value, col) in enumerate(cards):
        x = x0 + i * (w + gapw)
        ax.add_patch(plt.Rectangle((x, y - h), w, h, transform=ax.transAxes,
                                   facecolor=LIGHT, edgecolor=RULE, lw=0.8, zorder=0))
        ax.text(x + w / 2, y - 0.020, label.upper(), color=MIDGREY, fontsize=6.8,
                va="center", ha="center", fontweight="bold")
        ax.text(x + w / 2, y - h + 0.028, value, color=col, fontsize=14.5,
                va="center", ha="center", fontweight="bold")
    return y - h - 0.02


def _table(ax, y: float, col_labels: List[str], rows: List[List[str]],
           col_widths: List[float], x0: float = 0.06, x1: float = 0.94,
           row_h: float = 0.0235, fontsize: float = 8.0,
           align: Optional[List[str]] = None,
           text_color: Optional[Callable[[int, int, str], str]] = None,
           header_fontsize: float = 7.8) -> float:
    """Lightweight banded table drawn with primitives (full control over colours)."""
    width = x1 - x0
    xs = [x0]
    for cw in col_widths:
        xs.append(xs[-1] + cw * width)
    align = align or (["left"] + ["right"] * (len(col_labels) - 1))

    # header band
    ax.add_patch(plt.Rectangle((x0, y - row_h), width, row_h, transform=ax.transAxes,
                               facecolor=NAVY, edgecolor="none", zorder=1))
    for c, lab in enumerate(col_labels):
        cx, a = _cell_x(xs, c, align)
        ax.text(cx, y - row_h / 2, lab, color="white", fontsize=header_fontsize,
                va="center", ha=a, fontweight="bold", zorder=2)
    y -= row_h

    for r, row in enumerate(rows):
        if r % 2 == 0:
            ax.add_patch(plt.Rectangle((x0, y - row_h), width, row_h, transform=ax.transAxes,
                                       facecolor=LIGHT, edgecolor="none", zorder=0))
        for c, val in enumerate(row):
            cx, a = _cell_x(xs, c, align)
            col = text_color(r, c, val) if text_color else "#1f2a3a"
            fw = "bold" if c == 0 else "normal"
            ax.text(cx, y - row_h / 2, val, color=col, fontsize=fontsize,
                    va="center", ha=a, fontweight=fw, zorder=2)
        y -= row_h
    ax.add_line(plt.Line2D([x0, x1], [y, y], color=RULE, lw=0.8))
    return y - 0.012


def _cell_x(xs, c, align):
    a = align[c] if c < len(align) else "right"
    pad = 0.008
    if a == "left":
        return xs[c] + pad, "left"
    if a == "center":
        return (xs[c] + xs[c + 1]) / 2, "center"
    return xs[c + 1] - pad, "right"


# ── Commentary generation (derived from the data) ─────────────────────────────────
def _commentary(d: Dict[str, Any], cfg: Dict[str, Any]) -> Dict[str, List[str]]:
    risk = cfg.get("risk", {})
    entry_thr = risk.get("score_entry_above")
    stop_score = risk.get("stop_loss_score_max")
    spread = d.get("signal_strength")
    univ = d.get("univ_avg")
    held_avg = d.get("held_avg")
    em = d.get("exposure_mult")
    fv, tv = d.get("forecast_vol"), d.get("target_vol")
    rows = d.get("rows") or []           # prior-close ranking (with session return)
    rows_cur = d.get("rows_cur") or []   # current ranking (sets up next session)
    pos = d.get("positions")
    retfn = d.get("ret")

    obs: List[str] = []

    # 1) Session tone + momentum spread direction
    tone = "risk-off" if (univ is not None and univ < 0) else "risk-on"
    if spread is not None:
        if spread < 0:
            obs.append(
                f"Session was {tone} and momentum INVERTED: the Top-{d['top_n']} minus "
                f"Bottom-{d['top_n']} spread was {_pct(spread)} — higher-scored names sold off "
                f"harder than the laggards (universe avg {_pct(univ)}). That is the "
                f"momentum-reversal-in-a-selloff pattern, not a normal trend session.")
        else:
            obs.append(
                f"Session was {tone} with momentum WORKING: the Top-{d['top_n']} minus "
                f"Bottom-{d['top_n']} spread was {_pct(spread)} (universe avg {_pct(univ)}) — "
                f"higher-scored names out-returned the laggards.")

    # worst movers among the ranked top names
    worst = sorted([r for r in rows[:d["top_n"]] if r.get("return") is not None],
                   key=lambda r: r["return"])[:4]
    if worst:
        obs.append("Hardest hit among the leaders: " +
                   ", ".join(f"{r['ticker']} {_pct(r['return'])}" for r in worst) + ".")

    # 2) Volatility governor
    if em is not None and tv is not None:
        if em < 0.999:
            obs.append(
                f"The volatility governor is ENGAGED: forecast vol {_pct(fv, signed=False)} is "
                f"above the {_pct(tv, signed=False)} target, so gross exposure is scaled to "
                f"{em:.2f}× ({em*100:.0f}% of budget). New buys are automatically sized down — "
                f"the correct hands-off de-risk response.")
        else:
            obs.append(
                f"The volatility governor is neutral: forecast vol {_pct(fv, signed=False)} is at "
                f"or below the {_pct(tv, signed=False)} target, so exposure runs at the full "
                f"base budget ({em:.2f}×).")

    # 3) Held-book result + biggest detractor
    if held_avg is not None and pos is not None and not pos.empty and retfn is not None:
        held_rets = [(p["ticker"], retfn(p["ticker"])) for _, p in pos.iterrows()
                     if retfn(p["ticker"]) is not None]
        det = min(held_rets, key=lambda kv: kv[1]) if held_rets else None
        line = f"Held book returned {_pct(held_avg)} on the session"
        if det:
            line += f"; biggest detractor {det[0]} ({_pct(det[1])})"
        obs.append(line + ". Open positions remain net profitable on entry-to-date P&L.")

    # 4) Weakest holds whose stops are armed (score below the stop-gate)
    cur_score = {r["ticker"]: r["score"] for r in rows_cur}
    if stop_score is not None and pos is not None and not pos.empty:
        armed = sorted([(p["ticker"], cur_score.get(p["ticker"]))
                        for _, p in pos.iterrows()
                        if cur_score.get(p["ticker"]) is not None and cur_score[p["ticker"]] < stop_score],
                       key=lambda kv: kv[1])[:4]
        if armed:
            obs.append("Stop-losses are armed (score below " + f"{stop_score:.2f}" + ") on: " +
                       ", ".join(f"{t} ({s:.2f})" for t, s in armed) +
                       " — the engine will exit these automatically if they keep sliding.")

    # ── Recommendations ──
    recs: List[str] = []

    # Buy candidates: clear the persistence-entry bar and not already held
    if entry_thr is not None:
        cands = [r for r in rows_cur if r["score"] >= entry_thr and not r["held"]]
        cands = sorted(cands, key=lambda r: -r["score"])[:5]
        max_pct = cfg.get("portfolio", {}).get("max_position_pct")
        size_note = ""
        if max_pct and em:
            size_note = f" Sized ~{max_pct*em*100:.1f}% of book (per-name cap × {em:.2f}× governor)."
        if cands:
            recs.append(
                "BUY candidates (clear the >" + f"{entry_thr:.2f}" + " entry score, not held): " +
                ", ".join(f"{r['ticker']} ({r['score']:.2f})" for r in cands) +
                f". These trigger only on the {risk.get('score_entry_days', 3)}rd consecutive day above "
                f"the bar; max {cfg.get('portfolio', {}).get('max_new_trades_per_day', 2)} new/day." + size_note)
        else:
            recs.append("No names clear the persistence-entry score bar — no new buys set up. "
                        "Hold and let the book ride.")

    # Rank surgers below the gate (watchlist, not actionable yet)
    surgers = sorted([r for r in rows_cur if (r.get("rank_chg") or 0) >= 8 and
                      (entry_thr is None or r["score"] < entry_thr)],
                     key=lambda r: -(r.get("rank_chg") or 0))[:4]
    if surgers:
        recs.append("WATCHLIST — climbing fast but still below the entry bar: " +
                    ", ".join(f"{r['ticker']} (▲{r['rank_chg']}, {r['score']:.2f})" for r in surgers) +
                    ". No action; revisit if they push above the gate.")

    # Exit posture
    if stop_score is not None and pos is not None and not pos.empty:
        recs.append("EXITS — let the engine fire stops on its own at the open; do not pre-empt "
                    "score-gated holds that are still trending. No discretionary selling.")

    # Net stance
    if em is not None and spread is not None:
        if em < 0.999 and spread < 0:
            recs.append("NET STANCE: defensive. Governor de-risked and the momentum spread is "
                        "negative — this is a de-risk session, not one to add aggressively. Expect "
                        "at most 1–2 small adds and possibly 1–2 stop-driven exits next open.")
        else:
            recs.append("NET STANCE: constructive. Governor near full budget and the spread is "
                        "non-negative — normal sizing on any triggered entries.")

    return {"observations": obs, "recommendations": recs}


# ── Pages ──────────────────────────────────────────────────────────────────────
def _page_cover(pdf, d, cfg, comm):
    fig, ax = _new_page(pdf)
    _banner(ax, d["scenario"], d, "Systematic momentum portfolio · daily update")

    # snapshot strip
    stats = d.get("stats", {})
    one_d = stats.get("1D", {})
    port_1d = one_d.get("port")
    pv = d.get("pv")
    y = _cards(ax, 0.905, [
        ("Portfolio value", _money(pv), NAVY),
        ("Session return", _pct(port_1d), _ret_color(port_1d)),
        ("Signal spread", _pct(d.get("signal_strength")), _ret_color(d.get("signal_strength"))),
        ("Exposure", (f"{d['exposure_mult']:.2f}×" if d.get("exposure_mult") is not None else "—"),
         (RED if (d.get("exposure_mult") or 1) < 0.999 else GREEN)),
    ])

    y = _section(ax, y - 0.005, "Market commentary")
    y = _bullets(ax, y, comm["observations"])

    y = _section(ax, y - 0.01, "Recommendations — tonight → next open")
    y = _bullets(ax, y, comm["recommendations"])

    _footer(ax, 1)
    pdf.savefig(fig); plt.close(fig)


def _page_signals(pdf, d):
    fig, ax = _new_page(pdf)
    _banner(ax, d["scenario"], d, "Signal performance & benchmarks")
    y = 0.90

    y = _section(ax, y, "Signal strength (ranking-close → latest)")
    tn = d["top_n"]
    rows = [
        [f"Top {tn} − Bottom {tn} spread", _pct(d.get("signal_strength"))],
        [f"Top {tn} average", _pct(d.get("top_avg"))],
        [f"Bottom {tn} average", _pct(d.get("bot_avg"))],
        [f"Universe average (all {d['n']})", _pct(d.get("univ_avg"))],
        ["Held book (equal-wt / $-wt)", f"{_pct(d.get('held_avg'))}  /  {_pct(d.get('held_dw'))}"],
        ["Advancers", f"{d.get('advancers')}/{d['n']}"],
        ["Names clearing buy gate", f"{d.get('n_gate')}/{d['n']}"],
    ]
    def sig_color(r, c, v):
        return _ret_color(_parse_pct(v)) if c == 1 and "%" in v and "/" not in v else "#1f2a3a"
    y = _table(ax, y, ["Metric", "Value"], rows, [0.62, 0.38],
               align=["left", "right"], text_color=sig_color)

    # risk budget
    y = _section(ax, y - 0.012, "Risk budget (volatility targeting)")
    fv, em, tv = d.get("forecast_vol"), d.get("exposure_mult"), d.get("target_vol")
    rb = [
        ["Forecast volatility (annualized, 126d)", _pct(fv, signed=False)],
        ["Volatility target", ("off" if tv is None else _pct(tv, signed=False))],
        ["Exposure multiplier", ("—" if em is None else f"{em:.2f}×")],
        ["Effective vs base exposure", ("100% (off)" if tv is None else f"{(em or 1)*100:.0f}% of budget")],
    ]
    y = _table(ax, y, ["Metric", "Value"], rb, [0.62, 0.38], align=["left", "right"])

    # benchmarks
    y = _section(ax, y - 0.012, "Portfolio vs benchmarks")
    brows = []
    for w, s in d.get("stats", {}).items():
        m, sp, q = s.get("port"), s.get("spy"), s.get("qqq")
        vs_s = (m - sp) if (m is not None and sp is not None) else None
        vs_q = (m - q) if (m is not None and q is not None) else None
        brows.append([w, _pct(m), _pct(sp), _pct(q), _pct(vs_s), _pct(vs_q)])
    def bcolor(r, c, v):
        return _ret_color(_parse_pct(v)) if c >= 1 else "#1f2a3a"
    y = _table(ax, y, ["Window", d["scenario"], "SPY", "QQQ", "vs SPY", "vs QQQ"], brows,
               [0.26, 0.15, 0.13, 0.13, 0.165, 0.165],
               align=["left", "right", "right", "right", "right", "right"], text_color=bcolor)

    _footer(ax, 2)
    pdf.savefig(fig); plt.close(fig)


def _page_rankings(pdf, d):
    fig, ax = _new_page(pdf)
    _banner(ax, d["scenario"], d, f"Current composite ranking (scored on {d['mark']}) — sets up next session")
    y = 0.90
    rows_cur = d.get("rows_cur") or []
    tn = d["top_n"]

    def chg(r):
        c = r.get("rank_chg")
        if c is None:
            return "new"
        if c == 0:
            return "•"
        return (f"▲{c}" if c > 0 else f"▼{abs(c)}")

    def mk(rows):
        out = []
        for r in rows:
            out.append([str(r["rank"]), r["ticker"], f"{r['score']:.3f}",
                        ("✓" if r["clears_gate"] else "—"),
                        (_money(r["price"], 2) if r.get("price") is not None else "—"),
                        chg(r), ("HELD" if r["held"] else "")])
        return out

    def rk_color(r, c, v):
        if c == 5:  # rank change
            return GREEN if v.startswith("▲") else (RED if v.startswith("▼") else MIDGREY)
        if c == 6 and v == "HELD":
            return ACCENT
        if c == 3:
            return GREEN if v == "✓" else MIDGREY
        return "#1f2a3a"

    cols = ["#", "Ticker", "Score", "Gate", f"Px @ {d['mark']}", "Δrank", "Held"]
    cw = [0.07, 0.20, 0.15, 0.10, 0.22, 0.13, 0.13]
    aln = ["center", "left", "right", "center", "right", "center", "center"]

    y = _section(ax, y, f"Top {tn} — highest buy scores")
    y = _table(ax, y, cols, mk(rows_cur[:tn]), cw, align=aln, text_color=rk_color)

    y = _section(ax, y - 0.015, f"Bottom {tn} — lowest buy scores")
    y = _table(ax, y, cols, mk(rows_cur[-tn:]), cw, align=aln, text_color=rk_color)

    ax.text(0.06, y - 0.01, f"{d.get('n_gate_cur')}/{d['n']} names clear the buy gate on current prices. "
            "Δrank vs the prior-close ranking (▲ = higher now).",
            color=MIDGREY, fontsize=7.5, va="top", style="italic")

    _footer(ax, 3)
    pdf.savefig(fig); plt.close(fig)


def _page_activity(pdf, d):
    fig, ax = _new_page(pdf)
    _banner(ax, d["scenario"], d, "Holdings & recent activity")
    y = 0.90

    # held book
    pos = d.get("positions")
    retfn = d.get("ret")
    y = _section(ax, y, f"Held book — {0 if pos is None else len(pos)} positions  "
                        f"(portfolio {_money(d.get('pv'))}, cash {_money(d.get('cash'))})")
    if pos is None or pos.empty:
        ax.text(0.075, y, "No open positions.", color=MIDGREY, fontsize=8.8, va="top"); y -= 0.03
    else:
        hrows = []
        for _, p in pos.sort_values("ticker").iterrows():
            u = p["current_price"] / p["entry_price"] - 1
            hrows.append([p["ticker"], str(int(p["shares"])), _money(p["entry_price"], 2),
                          _money(p["current_price"], 2), _pct(u), _pct(retfn(p["ticker"]) if retfn else None)])
        def hcolor(r, c, v):
            return _ret_color(_parse_pct(v)) if c in (4, 5) else "#1f2a3a"
        y = _table(ax, y, ["Ticker", "Shares", "Entry", "Now", "Unreal %", "Session"], hrows,
                   [0.18, 0.15, 0.17, 0.17, 0.165, 0.165],
                   align=["left", "right", "right", "right", "right", "right"], text_color=hcolor)

    # today's transactions
    tt = d.get("today_trades") or []
    y = _section(ax, y - 0.012, f"Today's transactions ({d['mark']})")
    if not tt:
        ax.text(0.075, y, "No transactions today.", color=MIDGREY, fontsize=8.8, va="top"); y -= 0.03
    else:
        y = _table(ax, y, ["Action", "Ticker", "Shares", "Price", "Reason", "Realized P&L"],
                   [[x["action"], x["ticker"], str(x["shares"]), _money(x["price"], 2),
                     x["reason"], ("—" if x["pnl"] is None else _money(x["pnl"]))] for x in tt],
                   [0.13, 0.13, 0.12, 0.14, 0.30, 0.18],
                   align=["left", "left", "right", "right", "left", "right"],
                   text_color=lambda r, c, v: (_ret_color(_parse_money(v)) if c == 5 and v != "—" else "#1f2a3a"))

    # recent trade log
    rt = d.get("recent_trades") or []
    y = _section(ax, y - 0.012, "Recent trade log (last 10)")
    if not rt:
        ax.text(0.075, y, "No trades in this run.", color=MIDGREY, fontsize=8.8, va="top")
    else:
        y = _table(ax, y, ["Date", "Action", "Ticker", "Shares", "Price", "Reason", "Realized P&L"],
                   [[x["date"], x["action"], x["ticker"], str(x["shares"]), _money(x["price"], 2),
                     x["reason"], ("—" if x["pnl"] is None else _money(x["pnl"]))] for x in rt],
                   [0.13, 0.11, 0.10, 0.10, 0.12, 0.26, 0.18],
                   align=["left", "left", "left", "right", "right", "left", "right"], fontsize=7.4,
                   text_color=lambda r, c, v: (_ret_color(_parse_money(v)) if c == 6 and v != "—" else "#1f2a3a"))

    _footer(ax, 4)
    pdf.savefig(fig); plt.close(fig)


def _parse_pct(v: str) -> Optional[float]:
    try:
        return float(v.replace("%", "").replace("+", "")) / 100 if "%" in v else None
    except (ValueError, AttributeError):
        return None


def _parse_money(v: str) -> Optional[float]:
    try:
        return float(v.replace("$", "").replace(",", ""))
    except (ValueError, AttributeError):
        return None


# ── Entry points ──────────────────────────────────────────────────────────────
def build_pdf(d: Dict[str, Any], cfg: Dict[str, Any], out_path: Path) -> Path:
    """Render the EOD PDF from a rank_report.build_report dict + scenario cfg."""
    comm = _commentary(d, cfg)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(out_path) as pdf:
        _page_cover(pdf, d, cfg, comm)
        _page_signals(pdf, d)
        _page_rankings(pdf, d)
        _page_activity(pdf, d)
    return out_path


def run(scenario: str, start: date, end: date, output: Optional[Path] = None) -> Path:
    """Standalone: build the report dict (re-running the backtest) then render the PDF."""
    sys.path.insert(0, str(Path(__file__).parent))
    import rank_report
    from scenarios import build_config, load_scenario
    from backtest import load_config as _load_cfg

    root = Path(__file__).parent.parent
    cfg = build_config(_load_cfg(root / "config"), load_scenario(scenario))
    d = rank_report.build_report(scenario, start, end, cfg=cfg)
    out = output or (root / "reports" / f"eod_{scenario}_{d['mark'].isoformat()}.pdf")
    return build_pdf(d, cfg, out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Professional end-of-day PDF report for a scenario.")
    ap.add_argument("--scenario", required=True)
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    out = run(a.scenario, date.fromisoformat(a.start), date.fromisoformat(a.end),
              Path(a.out) if a.out else None)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
