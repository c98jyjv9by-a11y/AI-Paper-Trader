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
import os
import sys
import textwrap
from datetime import date
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Ellipse

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
HILITE = "#ffe28a"        # gold band for a stand-out row (e.g. the signal)
HILITE_RULE = "#c9a227"   # darker gold framing line
WARN = "#e8590c"          # warning orange (e.g. a signal-reversion column box)

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


# ── Shared signal/rank cell helpers (used by both the EOD and midday reports) ─────
_SIG_COLORS = {"Very Good": "#157a37", "Moderate Good": "#3f9c5e", "Mixed": MIDGREY,
               "Moderate Bad": "#d0663f", "Very Bad": "#c0392b", "—": MIDGREY}


def _signal_today(ret, univ):
    """Classify today's move vs the universe avg: excess = ret − univ."""
    if ret is None or univ is None:
        return "—"
    ex = ret - univ
    if ex >= 0.02:
        return "Very Good"
    if ex >= 0.005:
        return "Moderate Good"
    if ex > -0.005:
        return "Mixed"
    if ex > -0.02:
        return "Moderate Bad"
    return "Very Bad"


def _rk_icon(chg):
    """Rank-change icon: ▲ up / ▼ down / • flat / — unknown."""
    if chg is None:
        return "—"
    if chg == 0:
        return "•"
    return f"▲{chg}" if chg > 0 else f"▼{-chg}"


def _rk_color(v):
    return GREEN if v.startswith("▲") else (RED if v.startswith("▼") else MIDGREY)


def _score_trend_color(s):
    """Color a score-transition cell (e.g. '0.72→0.79→0.81') by last-vs-first direction."""
    import re
    nums = re.findall(r"[01]\.\d+", s)
    if len(nums) < 2:
        return "#1f2a3a"
    a, b = float(nums[0]), float(nums[-1])
    if b > a + 0.005:
        return GREEN
    if b < a - 0.005:
        return RED
    return MIDGREY


# ── Page scaffolding ─────────────────────────────────────────────────────────────
def _new_page(pdf: PdfPages):
    fig = plt.figure(figsize=(PAGE_W, PAGE_H))
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    return fig, ax


def _banner(ax, scenario: str, mark, rank_close, subtitle: str):
    """Top navy banner with title + run metadata."""
    ax.add_patch(plt.Rectangle((0, 0.93), 1, 0.07, transform=ax.transAxes,
                               facecolor=NAVY, edgecolor="none", zorder=0))
    ax.text(0.06, 0.965, f"{scenario}  —  End-of-Day Update",
            color="white", fontsize=15, fontweight="bold", va="center")
    ax.text(0.06, 0.943, subtitle, color="#b9c6d8", fontsize=8.5, va="center")
    ax.text(0.94, 0.958, mark.isoformat(), color="white", fontsize=11,
            fontweight="bold", va="center", ha="right")
    ax.text(0.94, 0.940, f"ranked @ close {rank_close}", color="#b9c6d8",
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


def _queued_block(ax, y: float, ns: Dict[str, Any], *, fontsize: float = 8.6,
                  lh: float = 0.0185, gap: float = 0.008, width: int = 95) -> float:
    """Render the next-session queued trades, or an explicit no-trade reason."""
    buys = ns.get("buys") or []
    sells = ns.get("sells") or []

    if not buys and not sells:
        # status chip
        ax.add_patch(plt.Rectangle((0.075, y - 0.024), 0.30, 0.022, transform=ax.transAxes,
                                   facecolor="#e8edf3", edgecolor=RULE, lw=0.8, zorder=0))
        ax.text(0.09, y - 0.013, "● NO TRADES — hold current book", color=NAVY,
                fontsize=8.5, va="center", fontweight="bold")
        y -= 0.034
        items = []
        if ns.get("buy_reason"):
            items.append("Buys — " + ns["buy_reason"])
        if ns.get("sell_reason"):
            items.append("Sells — " + ns["sell_reason"])
        return _bullets(ax, y, items, fontsize=fontsize, lh=lh, gap=gap, width=width)

    rows, colors = [], []
    for b in buys:
        rows.append(["BUY", b["ticker"], str(b["shares"]), _money(b["price"], 2),
                     _money(b["value"]), b["reason"]])
        colors.append(GREEN)
    for s in sells:
        rows.append(["SELL", s["ticker"], str(s["shares"]), _money(s["price"], 2),
                     _money(s.get("value")), s["reason"]])
        colors.append(RED)

    def qcolor(r, c, v):
        return colors[r] if c == 0 else "#1f2a3a"

    return _table(ax, y, ["Action", "Ticker", "Shares", "Price", "Value", "Reason"], rows,
                  [0.12, 0.13, 0.12, 0.14, 0.16, 0.33],
                  align=["left", "left", "right", "right", "right", "left"],
                  text_color=qcolor)


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
           header_fontsize: float = 7.8, emph_rows: Optional[set] = None,
           glyphs: Optional[Callable[[int, int], Optional[tuple]]] = None,
           hi_rows: Optional[set] = None, hl_cols: Optional[set] = None,
           hl_label: Optional[str] = None, star_cells: Optional[set] = None) -> float:
    """Lightweight banded table drawn with primitives (full control over colours).
    `emph_rows` (row indices) are shaded with an accent tint and bolded — e.g. an AVG row.
    `hi_rows` get a stronger GOLD band framed by rules + bold — a stand-out row (e.g. signal).
    `glyphs(r, c) -> (text, color) | None` draws a small LEFT-aligned glyph in a cell with
    its OWN colour (e.g. a ▲/▼ trend arrow), independent of the right-aligned value's colour.
    `hl_cols` (table column indices) draws a WARN-orange box around those columns over the full
    table height + `hl_label` above it; `star_cells` (set of (r, c)) append a ★ to those values."""
    width = x1 - x0
    emph = emph_rows or set()
    hi = hi_rows or set()
    stars = star_cells or set()
    y_top = y
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
        if r in hi:                                          # stand-out gold band, framed top & bottom
            ax.add_patch(plt.Rectangle((x0, y - row_h), width, row_h, transform=ax.transAxes,
                                       facecolor=HILITE, edgecolor="none", zorder=0))
            ax.add_line(plt.Line2D([x0, x1], [y, y], color=HILITE_RULE, lw=1.4, zorder=3))
            ax.add_line(plt.Line2D([x0, x1], [y - row_h, y - row_h], color=HILITE_RULE, lw=1.4, zorder=3))
        elif r in emph:
            ax.add_patch(plt.Rectangle((x0, y - row_h), width, row_h, transform=ax.transAxes,
                                       facecolor="#cdd8e6", edgecolor="none", zorder=0))
        elif r % 2 == 0:
            ax.add_patch(plt.Rectangle((x0, y - row_h), width, row_h, transform=ax.transAxes,
                                       facecolor=LIGHT, edgecolor="none", zorder=0))
        for c, val in enumerate(row):
            cx, a = _cell_x(xs, c, align)
            col = text_color(r, c, val) if text_color else "#1f2a3a"
            fw = "bold" if (c == 0 or r in emph or r in hi) else "normal"
            tval = ax.text(cx, y - row_h / 2, val, color=col, fontsize=fontsize,
                           va="center", ha=a, fontweight=fw, zorder=2)
            if (r, c) in stars and val:                      # ring the driving number with a dotted oval
                try:
                    bb = tval.get_window_extent(renderer=ax.figure.canvas.get_renderer())
                    inv = ax.transAxes.inverted()
                    ex0, _ = inv.transform((bb.x0, 0)); ex1, _ = inv.transform((bb.x1, 0))
                    ax.add_patch(Ellipse(((ex0 + ex1) / 2, y - row_h / 2),
                                         (ex1 - ex0) + 0.012, row_h * 0.82, transform=ax.transAxes,
                                         fill=False, edgecolor=WARN, lw=1.1, linestyle=":", zorder=5))
                except Exception:
                    pass
            g = glyphs(r, c) if glyphs else None
            if g and g[0]:                                   # trend arrow, own colour, hugging the value
                gx, gha = xs[c] + 0.006, "left"
                if a == "right":                             # place just LEFT of the right-aligned value
                    try:
                        bb = tval.get_window_extent(renderer=ax.figure.canvas.get_renderer())
                        inv = ax.transAxes.inverted()
                        w_ax = inv.transform((bb.x1, 0))[0] - inv.transform((bb.x0, 0))[0]
                        gx, gha = cx - w_ax - 0.004, "right"
                    except Exception:
                        pass
                ax.text(gx, y - row_h / 2, g[0], color=g[1], fontsize=fontsize,
                        va="center", ha=gha, fontweight="bold", zorder=2)
        y -= row_h
    ax.add_line(plt.Line2D([x0, x1], [y, y], color=RULE, lw=0.8))
    if hl_cols:                                              # WARN box around the flagged columns
        bx0, bx1 = xs[min(hl_cols)], xs[max(hl_cols) + 1]
        ax.add_patch(plt.Rectangle((bx0, y), bx1 - bx0, y_top - y, transform=ax.transAxes,
                                   facecolor="none", edgecolor=WARN, lw=2.0, zorder=4))
        if hl_label:
            ax.text(bx1, y_top + 0.006, hl_label, color=WARN, fontsize=7.6, fontweight="bold",
                    va="bottom", ha="right", zorder=5)
    return y - 0.012


def _cell_x(xs, c, align):
    a = align[c] if c < len(align) else "right"
    pad = 0.008
    if a == "left":
        return xs[c] + pad, "left"
    if a == "center":
        return (xs[c] + xs[c + 1]) / 2, "center"
    return xs[c + 1] - pad, "right"


# ── Shared "current book" (held positions) table — used by EOD cover & midday report ──
def enrich_holdings(d: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Per-holding rich fields (rank moves, score path, days, %NAV, today) computed from a
    build_report dict. Picklable plain values, so the cover-series can carry them too."""
    pos = d.get("positions")
    if pos is None or pos.empty:
        return []
    rows_prior = d.get("rows") or []
    rows_live = d.get("rows_cur") or []
    prior_rank = {r["ticker"]: r["rank"] for r in rows_prior}
    prior_score = {r["ticker"]: r["score"] for r in rows_prior}
    prior_chg = {r["ticker"]: r.get("prior_rank_chg") for r in rows_prior}
    live_rank = {r["ticker"]: r["rank"] for r in rows_live}
    live_score = {r["ticker"]: r["score"] for r in rows_live}
    entry_score = d.get("entry_scores") or {}
    retf, mark, nav = d.get("ret"), d.get("mark"), (d.get("pv") or 0.0)
    out = []
    for _, p in pos.iterrows():
        t = p["ticker"]
        sh = int(p["shares"]); now_px = float(p["current_price"]); val = now_px * sh
        try:
            days = max(0, round((mark - pd.Timestamp(p["entry_date"]).date()).days * 5 / 7))
        except Exception:
            days = None
        pr, lv = prior_rank.get(t), live_rank.get(t)
        out.append({
            "ticker": t, "shares": sh, "entry": float(p["entry_price"]), "now": now_px,
            "value": val, "navpct": (val / nav) if nav else None, "days": days,
            "unreal": now_px / float(p["entry_price"]) - 1,
            "today": (retf(t) if retf else None),
            "prior_rank": pr, "live_rank": lv,
            "d_today": (pr - lv) if (pr is not None and lv is not None) else None,
            "d_prior": prior_chg.get(t),
            "entry_score": entry_score.get(t), "prior_score": prior_score.get(t),
            "live_score": live_score.get(t),
        })
    out.sort(key=lambda h: (h["today"] if h["today"] is not None else 0))
    return out


def render_current_book(ax, y, holdings, *, npos, pv, cash, univ, held_dw):
    """Render the rich held-positions table (Prior/Live rank, Δ today, Δ prior, entry→
    yesterday→today score path, days, entry, now, %NAV, unreal, today, Signal Today) + TOTAL."""
    y = _section(ax, y, f"Current book — today's moves (worst first)  ·  {npos} positions  "
                        f"(portfolio {_money(pv)}, cash {_money(cash)})")
    if not holdings:
        ax.text(0.075, y, "No open positions.", color=MIDGREY, fontsize=8.0, va="top")
        return y - 0.024

    def s2(x):
        return f"{x:.2f}" if x is not None else "—"

    hrows, tot_now, tot_cost = [], 0.0, 0.0
    for h in holdings:
        tot_now += h["value"]; tot_cost += h["entry"] * h["shares"]
        path = f"{s2(h['entry_score'])}→{s2(h['prior_score'])}→{s2(h['live_score'])}"
        hrows.append([h["ticker"], ("—" if h["prior_rank"] is None else str(h["prior_rank"])),
                      ("—" if h["live_rank"] is None else str(h["live_rank"])),
                      _rk_icon(h["d_today"]), _rk_icon(h["d_prior"]), path,
                      ("—" if h["days"] is None else str(h["days"])),
                      _money(h["entry"], 2), _money(h["now"], 2), _pct(h["navpct"]),
                      _pct(h["unreal"]), _pct(h["today"]), _signal_today(h["today"], univ)])
    book_unreal = (tot_now / tot_cost - 1) if tot_cost else None
    hrows.append(["TOTAL", "", "", "", "", "", "", "", "", _pct((tot_now / pv) if pv else None),
                  _pct(book_unreal), _pct(held_dw), ""])
    cols = ["Ticker", "Prior #", "Live #", "Δ today", "Δ prior", "Score E→Y→T", "Days",
            "Entry", "Now", "% NAV", "Unreal %", "Today %", "Signal Today"]
    widths = [0.07, 0.04, 0.04, 0.048, 0.048, 0.155, 0.042, 0.078, 0.078, 0.062, 0.068, 0.068, 0.203]
    align = ["left", "center", "center", "center", "center", "right", "right",
             "right", "right", "right", "right", "right", "left"]

    def cb(r, c, v):
        if c in (3, 4):
            return _rk_color(v)
        if c == 5:
            return _score_trend_color(v)
        if c in (10, 11):
            return _ret_color(_parse_pct(v))
        if c == 12:
            return _SIG_COLORS.get(v, "#1f2a3a")
        return "#1f2a3a"
    return _table(ax, y, cols, hrows, widths, align=align, row_h=0.018, fontsize=6.0,
                  header_fontsize=5.9, emph_rows={len(hrows) - 1}, text_color=cb)


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

    # ── Recommendations — mirror the actual QUEUED transactions ──
    recs: List[str] = []
    ns = d.get("next_session") or {}
    qbuys = ns.get("buys") or []
    qsells = ns.get("sells") or []

    if qbuys:
        recs.append("QUEUED BUYS (decide tonight → next open): " +
                    "; ".join(f"{b['ticker']} {b['shares']} sh ~{_money(b['value'])} [{b['reason']}]"
                              for b in qbuys) + ".")
    else:
        recs.append("No buys queued — " + (ns.get("buy_reason") or "no unheld name qualified for entry."))

    if qsells:
        recs.append("QUEUED SELLS (next open): " +
                    "; ".join(f"{s['ticker']} {s['shares']} sh [{s['reason']}]" for s in qsells) + ".")
    elif ns.get("sell_reason"):
        recs.append("No sells queued — " + ns["sell_reason"])

    # Rank surgers below the gate (watchlist, not actionable yet)
    surgers = sorted([r for r in rows_cur if (r.get("rank_chg") or 0) >= 8 and
                      (entry_thr is None or r["score"] < entry_thr)],
                     key=lambda r: -(r.get("rank_chg") or 0))[:4]
    if surgers:
        recs.append("WATCHLIST — climbing fast but still below the entry bar: " +
                    ", ".join(f"{r['ticker']} (▲{r['rank_chg']}, {r['score']:.2f})" for r in surgers) +
                    ". No action; revisit if they push above the gate.")

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
def _cover_spec(d: Dict[str, Any], comm: Dict[str, List[str]]) -> Dict[str, Any]:
    """Flat, picklable bundle of everything the cover page needs (for the parallel
    cover-series harness — closures/DataFrames in `d` are not picklable)."""
    one_d = (d.get("stats") or {}).get("1D", {})
    pos = d.get("positions")
    holdings = enrich_holdings(d)                 # rich per-holding fields (picklable)
    rankings = [{"rank": r["rank"], "ticker": r["ticker"], "score": round(float(r["score"]), 3),
                 "gate": bool(r["clears_gate"]), "held": bool(r["held"])}
                for r in (d.get("rows_cur") or [])]
    return {
        "scenario": d["scenario"], "mark": d["mark"], "rank_close": d["rank_close"],
        "pv": d.get("pv"), "cash": d.get("cash"), "port_1d": one_d.get("port"),
        "signal_strength": d.get("signal_strength"), "exposure_mult": d.get("exposure_mult"),
        "univ_avg": d.get("univ_avg"), "held_dw": d.get("held_dw"),
        "n_positions": 0 if (pos is None or pos.empty) else len(pos),
        "next_session": d.get("next_session") or {}, "holdings": holdings, "rankings": rankings,
        "observations": comm["observations"], "recommendations": comm["recommendations"],
        "mark_note": d.get("mark_note"),
    }


def _render_cover(pdf, spec: Dict[str, Any], page: int = 1):
    """Render one cover page from a picklable spec (used by both build_pdf and the series)."""
    fig, ax = _new_page(pdf)
    _banner(ax, spec["scenario"], spec["mark"], spec["rank_close"],
            (f"Extended-hours mark · {spec['mark_note']}" if spec.get("mark_note")
             else "Systematic momentum portfolio · daily update"))

    pv, cash, port_1d, em = spec.get("pv"), spec.get("cash"), spec.get("port_1d"), spec.get("exposure_mult")
    y = _cards(ax, 0.905, [
        ("Portfolio value", _money(pv), NAVY),
        ("Cash balance", _money(cash), NAVY),
        ("Session return", _pct(port_1d), _ret_color(port_1d)),
        ("Signal spread", _pct(spec.get("signal_strength")), _ret_color(spec.get("signal_strength"))),
        ("Exposure", (f"{em:.2f}×" if em is not None else "—"),
         (RED if (em or 1) < 0.999 else GREEN)),
    ])

    # Held book — same rich table as the midday report (single source of truth)
    y = render_current_book(ax, y - 0.004, spec.get("holdings") or [],
                            npos=spec.get("n_positions", 0), pv=pv, cash=cash,
                            univ=spec.get("univ_avg"), held_dw=spec.get("held_dw"))

    # Queued decision for next session (decide at today's close → fill next open)
    y = _section(ax, y - 0.006, "Queued for next session  (after today's close → next open)")
    ns = spec.get("next_session") or {}
    y = _queued_block(ax, y, ns, fontsize=7.6, lh=0.0148, gap=0.004, width=112)

    # Book AFTER today's queued trades (current book + queued buys)
    qbuys = ns.get("buys") or []
    if qbuys:
        after = {}
        for h in (spec.get("holdings") or []):
            after[h["ticker"]] = [h["shares"], h["value"]]
        for b in qbuys:
            if b["ticker"] in after:
                after[b["ticker"]][0] += b["shares"]; after[b["ticker"]][1] += b["value"]
            else:
                after[b["ticker"]] = [b["shares"], b["value"]]
        rows_a = sorted(([t, str(int(s)), _money(v)] for t, (s, v) in after.items()),
                        key=lambda r: -float(r[2].replace("$", "").replace(",", "")))
        tot = sum(v for _, (_, v) in after.items())
        rows_a.append(["TOTAL (invested)", "", _money(tot)])
        y = _section(ax, y - 0.006, "Current book AFTER today's trades")
        y = _table(ax, y, ["Ticker", "Shares", "Market value"], rows_a, [0.30, 0.22, 0.30],
                   align=["left", "right", "right"])

    y = _section(ax, y - 0.006, "Market commentary")
    y = _bullets(ax, y, spec["observations"], width=114, lh=0.0146, gap=0.004, fontsize=7.5)

    y = _section(ax, y - 0.006, "Recommendations — tonight → next open")
    y = _bullets(ax, y, spec["recommendations"], width=114, lh=0.0146, gap=0.004, fontsize=7.5)

    _footer(ax, page)
    pdf.savefig(fig); plt.close(fig)


def _page_cover(pdf, d, cfg, comm):
    _render_cover(pdf, _cover_spec(d, comm), page=1)


def _page_signals(pdf, d):
    fig, ax = _new_page(pdf)
    _banner(ax, d["scenario"], d["mark"], d["rank_close"], "Signal performance & benchmarks")
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
    _banner(ax, d["scenario"], d["mark"], d["rank_close"], f"Current composite ranking (scored on {d['mark']}) — sets up next session")
    y = 0.90
    rows_cur = d.get("rows_cur") or []
    tn = d["top_n"]
    # Trend measures, mirroring the midday report: score then→now, prior-day rank move, Signal Today.
    rows_prior = d.get("rows") or []
    prior_score = {r["ticker"]: r["score"] for r in rows_prior}
    prior_chg = {r["ticker"]: r.get("prior_rank_chg") for r in rows_prior}
    today_ret = {r["ticker"]: r.get("return") for r in rows_prior}
    univ = d.get("univ_avg")

    def _s2(x):
        return f"{x:.2f}" if x is not None else "—"

    def mk(rows):
        out = []
        for r in rows:
            t = r["ticker"]
            then_now = f"{_s2(prior_score.get(t))}→{_s2(r['score'])}"
            out.append([str(r["rank"]), t, then_now, ("✓" if r["clears_gate"] else "—"),
                        (_money(r["price"], 2) if r.get("price") is not None else "—"),
                        _rk_icon(r.get("rank_chg")), _rk_icon(prior_chg.get(t)),
                        _signal_today(today_ret.get(t), univ), ("HELD" if r["held"] else "")])
        return out

    def rk_color(r, c, v):
        if c == 2:
            return _score_trend_color(v)
        if c == 3:
            return GREEN if v == "✓" else MIDGREY
        if c in (5, 6):
            return _rk_color(v)
        if c == 7:
            return _SIG_COLORS.get(v, "#1f2a3a")
        if c == 8 and v == "HELD":
            return ACCENT
        return "#1f2a3a"

    cols = ["#", "Ticker", "Score then→now", "Gate", f"Px @ {d['mark']}",
            "Δ today", "Δ prior", "Signal Today", "Held"]
    cw = [0.05, 0.11, 0.16, 0.06, 0.135, 0.075, 0.075, 0.185, 0.15]
    aln = ["center", "left", "right", "center", "right", "center", "center", "left", "center"]

    y = _section(ax, y, f"Top {tn} — highest buy scores")
    y = _table(ax, y, cols, mk(rows_cur[:tn]), cw, align=aln, fontsize=7.0, header_fontsize=6.8,
               text_color=rk_color)

    y = _section(ax, y - 0.015, f"Bottom {tn} — lowest buy scores")
    y = _table(ax, y, cols, mk(rows_cur[-tn:]), cw, align=aln, fontsize=7.0, header_fontsize=6.8,
               text_color=rk_color)

    ax.text(0.06, y - 0.01, f"{d.get('n_gate_cur')}/{d['n']} clear the buy gate now. Score then→now = "
            f"{d['rank_close']}→live (green up / red down). Δ today = rank move at the live price; "
            "Δ prior = rank move on the prior day. Signal Today = return vs universe avg.",
            color=MIDGREY, fontsize=7.0, va="top", style="italic")

    _footer(ax, 5)
    pdf.savefig(fig); plt.close(fig)


def _page_attribution_eod(pdf, d, cfg):
    """EOD page 3 — the attribution table + takeaways (reused from midday), built off the
    official close that `d` carries (not after-hours). Degrades gracefully without intraday."""
    import midday_pdf as MP
    fig, ax = _new_page(pdf)
    _banner(ax, d["scenario"], d["mark"], d["rank_close"], "Attribution — session breakdown (official close)")
    MP.attribution_body(ax, d)
    _footer(ax, 3)
    pdf.savefig(fig); plt.close(fig)


def _page_paths_eod(pdf, d, cfg):
    """EOD page 4 — intraday return paths (reused from midday), ending at the official close."""
    import midday_pdf as MP
    fig, ax = _new_page(pdf)
    _banner(ax, d["scenario"], d["mark"], d["rank_close"], "Intraday return paths — to the official close")
    MP.paths_body(ax, d)
    _footer(ax, 4)
    pdf.savefig(fig); plt.close(fig)


def _page_activity(pdf, d):
    fig, ax = _new_page(pdf)
    _banner(ax, d["scenario"], d["mark"], d["rank_close"], "Recent activity")
    y = 0.90
    # (Held book lives on the cover now.)

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

    _footer(ax, 6)
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
        _page_cover(pdf, d, cfg, comm)              # 1
        _page_signals(pdf, d)                       # 2
        _page_attribution_eod(pdf, d, cfg)          # 3
        _page_paths_eod(pdf, d, cfg)                # 4
        _page_rankings(pdf, d)                      # 5
        _page_activity(pdf, d)                      # 6
    return out_path


def run(scenario: Optional[str] = None, start: Optional[date] = None, end: Optional[date] = None,
        output: Optional[Path] = None, account: Optional[str] = None, prepost: bool = False) -> Path:
    """Standalone EOD PDF. With `account`, serve the FROZEN/living ledger (scenario/start/end
    default to the account's base/inception/live-through); else re-run the scenario backtest.

    `prepost` marks the latest bar to the after-hours print (live session only)."""
    sys.path.insert(0, str(Path(__file__).parent))
    import rank_report
    from scenarios import build_config, load_scenario
    from backtest import load_config as _load_cfg

    root = Path(__file__).parent.parent
    if account:
        from account import load_manifest
        man = load_manifest(account)
        scenario = scenario or man["scenario"]
        start = start or date.fromisoformat(man["inception"])
        end = end or date.fromisoformat(man.get("live_through", man["frozen_through"]))
    if not scenario:
        raise ValueError("pdf_report.run needs --scenario or --account")
    end = end or date.today()                       # default to today (EOD); start to that year's Jan 1
    start = start or date(end.year, 1, 1)
    cfg = build_config(_load_cfg(root / "config"), load_scenario(scenario))
    d = rank_report.build_report(scenario, start, end, cfg=cfg, account=account,
                                 write_snapshot=False if account else None, with_intraday=True,
                                 prepost=prepost)
    if output:
        out = Path(output)
    elif account:
        # account-mode: render into the account's own reports/ folder (alongside the ledger)
        out = root / "accounts" / account / "reports" / f"eod_{scenario}_{d['mark'].isoformat()}.pdf"
    else:
        out = root / "reports" / f"eod_{scenario}_{d['mark'].isoformat()}.pdf"
    return build_pdf(d, cfg, out)


# ── Cover-series harness (one cover page per date over a horizon) ─────────────────
# For backtesting an agent's read-and-act loop: render the EOD cover page for every
# trading day in [start, end] into one combined PDF, plus return the per-date specs.
# Each date is reconstructed with NO look-ahead (rank_report.build_report(..., fast=True)
# is windowed on data <= that date; fast mode skips snapshot/intraday I/O & network).

_MAX_SERIES_WORKERS = 8
_S_PDATA = None
_S_CFG = None
_S_SCENARIO = None
_S_START = None
_S_TOPN = None


def _series_pool_init(pdata, cfg, scenario, start, top_n):
    global _S_PDATA, _S_CFG, _S_SCENARIO, _S_START, _S_TOPN
    _S_PDATA, _S_CFG, _S_SCENARIO, _S_START, _S_TOPN = pdata, cfg, scenario, start, top_n


def _series_worker(d_iso: str):
    """Build one date's cover spec from the shared (initializer-set) price panel."""
    import pandas as pd
    import rank_report
    D = date.fromisoformat(d_iso)
    sub = _S_PDATA.loc[:pd.Timestamp(D)]
    try:
        rep = rank_report.build_report(_S_SCENARIO, _S_START, D, top_n=_S_TOPN,
                                       cfg=_S_CFG, pdata=sub, fast=True)
        return (d_iso, _cover_spec(rep, _commentary(rep, _S_CFG)), None)
    except Exception as exc:                       # one bad date must not sink the batch
        return (d_iso, None, f"{type(exc).__name__}: {exc}")


def run_cover_series(scenario: str, start: date, end: date,
                     out_path: Optional[Path] = None, *, sim_start: Optional[date] = None,
                     workers: Optional[int] = None, top_n: int = 10,
                     warmup_days: int = 200) -> Dict[str, Any]:
    """Render the EOD COVER PAGE for every trading day in [start, end] — one page per
    date — into a single combined PDF, for backtesting an agent's ability to read the
    daily output and act.

    Parallelized across dates (process pool; the price panel is shared once via the pool
    initializer, not pickled per task). Each page is a faithful, no-look-ahead
    reconstruction of what the cover would have shown on that date.

    sim_start: the model's inception used for the backtest warmup (default = `start`).
      Pass an earlier date so the volatility governor / momentum signals are mature on
      the first pages instead of warming up across the early horizon.

    Returns a single combined dict: {pdf, pages, dates, specs, errors} — `specs` is the
    list of per-date cover bundles (commentary, recommendations, queued decision, metrics)
    in date order, so the agent harness can consume the data directly as well as the PDF.
    """
    import pandas as pd
    sys.path.insert(0, str(Path(__file__).parent))
    from scenarios import build_config, load_scenario
    from backtest import load_config as _load_cfg, fetch_backtest_data

    root = Path(__file__).parent.parent
    cfg = build_config(_load_cfg(root / "config"), load_scenario(scenario))
    sim_start = sim_start or start
    pdata = fetch_backtest_data(cfg["tickers"], sim_start, end, warmup_days=warmup_days)

    close = pdata["Close"]
    dates = [ts.date().isoformat() for ts in close.index if start <= ts.date() <= end]
    if not dates:
        raise ValueError(f"No trading days in [{start}, {end}].")

    n = workers or max(1, min(_MAX_SERIES_WORKERS, (os.cpu_count() or 2) - 1, len(dates)))
    specs: Dict[str, Any] = {}
    errors: Dict[str, str] = {}
    initargs = (pdata, cfg, scenario, sim_start, top_n)

    if n > 1 and len(dates) > 1:
        import multiprocessing as mp
        with mp.Pool(n, initializer=_series_pool_init, initargs=initargs) as pool:
            for d_iso, spec, err in pool.imap_unordered(_series_worker, dates):
                (specs if spec is not None else errors)[d_iso] = spec if spec is not None else err
    else:
        _series_pool_init(*initargs)
        for d_iso in dates:
            _, spec, err = _series_worker(d_iso)
            (specs if spec is not None else errors)[d_iso] = spec if spec is not None else err

    ordered = sorted(specs)
    out_path = Path(out_path) if out_path else (
        root / "reports" / f"eod_series_{scenario}_{start.isoformat()}_{end.isoformat()}.pdf")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(out_path) as pdf:
        for i, d_iso in enumerate(ordered, 1):
            _render_cover(pdf, specs[d_iso], page=i)

    return {"pdf": str(out_path), "pages": len(ordered), "dates": ordered,
            "specs": [specs[k] for k in ordered], "errors": errors}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Professional end-of-day PDF report for a scenario.")
    ap.add_argument("--scenario")
    ap.add_argument("--start")
    ap.add_argument("--end")
    ap.add_argument("--account", help="render from a frozen/living account ledger instead of a fresh backtest")
    ap.add_argument("--out")
    ap.add_argument("--series", action="store_true",
                    help="render the COVER page for every date in [start, end] into one combined PDF")
    ap.add_argument("--sim-start", help="backtest warmup inception for --series (default = start)")
    ap.add_argument("--workers", type=int, help="parallel workers for --series")
    ap.add_argument("--prepost", action="store_true",
                    help="mark the latest bar to the after-hours print (live session only)")
    a = ap.parse_args(argv)
    if a.account:
        out = run(a.scenario, date.fromisoformat(a.start) if a.start else None,
                  date.fromisoformat(a.end) if a.end else None,
                  Path(a.out) if a.out else None, account=a.account, prepost=a.prepost)
        print(f"Wrote {out}")
    elif a.series:
        res = run_cover_series(
            a.scenario, date.fromisoformat(a.start), date.fromisoformat(a.end),
            Path(a.out) if a.out else None,
            sim_start=date.fromisoformat(a.sim_start) if a.sim_start else None,
            workers=a.workers)
        print(f"Wrote {res['pages']} cover pages → {res['pdf']}")
        if res["errors"]:
            print(f"  ({len(res['errors'])} date(s) skipped: {', '.join(sorted(res['errors'])[:5])}…)")
    else:
        out = run(a.scenario, date.fromisoformat(a.start), date.fromisoformat(a.end),
                  Path(a.out) if a.out else None, prepost=a.prepost)
        print(f"Wrote {out}")


if __name__ == "__main__":
    main()
