"""
midday_pdf.py — Intraday "Midday Pulse" PDF for a scenario (sibling of pdf_report's EOD).

Same look as the end-of-day report, but built for a mid-session run on provisional prices.
It focuses on:
  • current book movements (how each holding is moving TODAY, vs prior close),
  • how well the signal is working SO FAR (top-vs-bottom spread intraday, advancers,
    held book vs SPY/QQQ), and
  • what is NOT behaving as expected (leaders fading, laggards bid, held detractors,
    governor de-risking) — the diagnostic the EOD report doesn't emphasize.

Reads the same rank_report.build_report data (mark = latest/provisional bar, rank_close =
last completed close, so every "return" is today's intraday move). 2 pages, concise.
Read-only w.r.t. data/.

    python src/midday_pdf.py --scenario model_v4 --start 2026-01-01 --end 2026-06-17
"""
from __future__ import annotations

import argparse
import sys
import textwrap
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib
matplotlib.use("Agg")
from matplotlib.backends.backend_pdf import PdfPages

sys.path.insert(0, str(Path(__file__).parent))
import pdf_report as P            # shared palette + table/cell helpers + render_current_book
# Shared signal/rank cell helpers live in pdf_report (single source of truth for both reports).
from pdf_report import _SIG_COLORS, _signal_today, _rk_icon, _rk_color, _score_trend_color


def _caption(ax, y, text, *, x=0.06, width=116, fontsize=7.0, color=None,
             style="italic", weight="normal", lh=0.0145):
    """Draw a text callout WRAPPED to `width` chars so it never runs off the page; returns
    the y below the last line. Used for the italic notes and verdict lines."""
    for line in textwrap.wrap(text, width=width):
        ax.text(x, y, line, color=(color or P.MIDGREY), fontsize=fontsize, va="top",
                style=style, fontweight=weight)
        y -= lh
    return y


def _footer(ax, page):
    ax.add_line(P.plt.Line2D([0.06, 0.94], [0.035, 0.035], color=P.RULE, lw=0.8))
    ax.text(0.06, 0.022, "Paper-trading research only — not investment advice. Intraday/provisional "
            "prices; figures settle at the close.", color=P.MIDGREY, fontsize=6.5, va="center")
    ax.text(0.94, 0.022, f"midday-pulse · p.{page}", color=P.MIDGREY, fontsize=6.5,
            va="center", ha="right")


def _banner(ax, scenario, mark, rank_close, note=None):
    ax.add_patch(P.plt.Rectangle((0, 0.93), 1, 0.07, transform=ax.transAxes,
                                 facecolor=P.NAVY, edgecolor="none"))
    ax.text(0.06, 0.965, f"{scenario}  —  Midday Pulse", color="white", fontsize=15,
            fontweight="bold", va="center")
    sub = (f"Extended-hours mark · {note} · is the signal working?" if note
           else "Intraday snapshot · provisional prices · is the signal working so far?")
    ax.text(0.06, 0.943, sub, color="#b9c6d8", fontsize=8.5, va="center")
    ax.text(0.94, 0.958, mark.isoformat(), color="white", fontsize=11, fontweight="bold",
            va="center", ha="right")
    ax.text(0.94, 0.940, (note if note else f"vs prior close {rank_close}"),
            color="#b9c6d8", fontsize=7.5, va="center", ha="right")


def _anomalies(d: Dict[str, Any], cfg: Dict[str, Any]) -> List[str]:
    rows = d.get("rows") or []
    tn = d["top_n"]
    ss, top_avg, bot_avg = d.get("signal_strength"), d.get("top_avg"), d.get("bot_avg")
    out: List[str] = []

    if ss is not None:
        if ss < 0:
            out.append(f"Momentum is INVERTING intraday: top-{tn} {P._pct(top_avg)} vs bottom-{tn} "
                       f"{P._pct(bot_avg)} (spread {P._pct(ss)}). Higher-scored names are lagging the "
                       f"laggards — the signal is NOT working so far today.")
        else:
            out.append(f"Signal working so far: top-{tn} {P._pct(top_avg)} is beating bottom-{tn} "
                       f"{P._pct(bot_avg)} (spread {P._pct(ss)}).")

    top = [r for r in rows[:tn] if r.get("return") is not None]
    faders = sorted([r for r in top if r["return"] < 0], key=lambda r: r["return"])[:4]
    if faders:
        out.append("Leaders fading (high score, DOWN today): "
                   + ", ".join(f"{r['ticker']} {P._pct(r['return'])}" for r in faders) + ".")

    bot = [r for r in rows[-tn:] if r.get("return") is not None]
    pops = sorted([r for r in bot if r["return"] > 0], key=lambda r: -r["return"])[:4]
    if pops:
        out.append("Laggards bid (low score, UP today): "
                   + ", ".join(f"{r['ticker']} {P._pct(r['return'])}" for r in pops) + ".")

    pos, retf = d.get("positions"), d.get("ret")
    if pos is not None and not pos.empty and retf:
        hr = [(p["ticker"], retf(p["ticker"])) for _, p in pos.iterrows() if retf(p["ticker"]) is not None]
        worst = [kv for kv in sorted(hr, key=lambda kv: kv[1]) if kv[1] < 0][:4]
        if worst:
            out.append("Biggest held detractors today: "
                       + ", ".join(f"{t} {P._pct(r)}" for t, r in worst) + ".")

    em, fv, tv = d.get("exposure_mult"), d.get("forecast_vol"), d.get("target_vol")
    if em is not None and tv is not None and em < 0.999:
        out.append(f"Vol governor de-risked to {em:.2f}× (forecast vol {P._pct(fv, signed=False)} > "
                   f"{P._pct(tv, signed=False)} target) — new buys are sized down.")

    if len(out) <= 1:
        out.append("Nothing notably off — moves broadly track scores so far.")
    return out


def _arrow(prev, cur):
    """Trend arrow + colour, cur vs the prior value: ▲ green up / ▼ red down.
    (FLAT classification disabled for now — re-enable the block below to show a grey – when the
    move is within ±2%, i.e. cur/prev in 0.98–1.02.)"""
    # if prev != 0 and 0.98 <= cur / prev <= 1.02:
    #     return "–", P.MIDGREY                      # FLAT (±2%) — commented out for now
    return ("▲", P.GREEN) if cur > prev else ("▼", P.RED)


def _cell_trends(seq):
    """Per-cell (arrows, colors) for a value sequence: each entry vs the prior non-empty one.
    First/empty entries get no arrow and neutral color (nothing to compare)."""
    arrows, colors, prev = [], [], None
    for s in seq:
        if s is None or prev is None:
            arrows.append(""); colors.append("#1f2a3a")
        else:
            ic, col = _arrow(prev, s); arrows.append(ic); colors.append(col)
        if s is not None:
            prev = s
    return arrows, colors


def _row(label, seq, *, trend=False):
    """One series row → (label, cells, value_colors, arrow_glyphs). Value colour = SIGN of the
    value (green +/red −). With trend=True each cell also carries a ▲/▼ arrow whose direction
    AND colour come from the change vs the prior cell (green up / red down) — the two encodings
    are independent: a positive value that ticked down shows green text with a red ▼."""
    cells = [P._pct(s) for s in seq]
    vcolors = [P._ret_color(s) for s in seq]
    if trend:
        arrows, acolors = _cell_trends(seq)
        gl = [(arrows[j], acolors[j]) for j in range(len(seq))]
    else:
        gl = [None] * len(seq)
    return label, cells, vcolors, gl


def _render_rows(ax, y, cols, cw, specs, emph, *, row_h, fs, hfs, header_rows=frozenset()):
    """Render row-specs (label, cells, value_colors, arrow_glyphs) via the shared table: value
    text uses its sign colour; the arrow glyph hugs the value in its own colour. `header_rows`
    are group sub-headers — their label is drawn in the accent colour (and they're emphasised)."""
    rows = [[s[0]] + list(s[1]) for s in specs]
    vcolors = [s[2] for s in specs]
    glyphs = [s[3] for s in specs]

    def tcol(r, c, v):
        if c == 0:
            return P.ACCENT if r in header_rows else "#1f2a3a"
        vc = vcolors[r]
        return vc[c - 1] if (c - 1) < len(vc) else "#1f2a3a"

    def gly(r, c):
        if c == 0:
            return None
        g = glyphs[r]
        return g[c - 1] if (g and (c - 1) < len(g)) else None
    return P._table(ax, y, cols, rows, cw, align=["left"] + ["right"] * (len(cols) - 1),
                    row_h=row_h, fontsize=fs, header_fontsize=hfs, emph_rows=emph,
                    text_color=tcol, glyphs=gly)


def _held_sleeves(d):
    """Held names split into momentum vs decoupled by their PRIOR-CLOSE score rank (held
    constant — the classification doesn't drift intraday), with current-value weights (so the
    sleeves sum to held_dw). Returns (holds, mom_wt, dec_wt) where holds=[{t,w,mom}]."""
    pos, gate = d.get("positions"), (d.get("min_score") or 0.70)
    pscore = {r["ticker"]: r["score"] for r in (d.get("rows") or [])}   # prior-close score, fixed
    holds = []
    if pos is not None and not pos.empty:
        vals = {p["ticker"]: float(p["shares"]) * float(p["current_price"]) for _, p in pos.iterrows()}
        tot = sum(vals.values()) or 1.0
        for t, v in vals.items():
            sc = pscore.get(t)
            holds.append({"t": t, "w": v / tot, "mom": (sc is not None and sc >= gate)})
    return holds, sum(h["w"] for h in holds if h["mom"]), sum(h["w"] for h in holds if not h["mom"])


def _attribution_table(ax, y, d, cps, intra, retf, top, bottom):
    """Step-by-step attribution, read top-down: benchmarks → leaders vs laggards → their spread
    (the momentum signal) → the held book split into the names still ranked high (Momentum) vs
    those that have decoupled, summing to Book. Sleeve rows are contributions (weight×return)."""
    cols = ["Series"] + [lbl for _, lbl in cps] + ["Latest"]
    n = len(cps)
    rem = 1 - 0.20 - 0.10
    cw = ([0.20] + [rem / n] * n + [0.10]) if n else [0.55, 0.45]

    def at(t, h):
        return (intra or {}).get(t, {}).get(h)

    def avg_seq(names):                               # equal-weight avg-return path for a name set
        out = []
        for h, _ in cps:
            v = [at(t, h) for t in names]; v = [x for x in v if x is not None]
            out.append(sum(v) / len(v) if v else None)
        lv = [retf(t) for t in names if retf and retf(t) is not None]
        out.append(sum(lv) / len(lv) if lv else None)
        return out

    holds, mom_wt, dec_wt = _held_sleeves(d)

    def _vals(h):                                     # (ticker, return) for held names with data at column h
        g = (lambda t: retf(t)) if h is None else (lambda t: at(t, h))
        return [(hd, g(hd["t"])) for hd in holds if (g(hd["t"]) is not None)]

    def ew_contrib(mom):                              # EQUAL-WEIGHT contribution of one pool (each name 1/N)
        out = []
        for h in [hh for hh, _ in cps] + [None]:
            av = _vals(h); n = len(av)
            s = sum(r for hd, r in av if hd["mom"] == mom)
            out.append(s / n if n else None)
        return out

    def dw_path():                                    # dollar-weighted book return (= held_dw at Latest)
        out = []
        for h in [hh for hh, _ in cps] + [None]:
            av = _vals(h)
            den = sum(hd["w"] for hd, _ in av)
            out.append(sum(hd["w"] * r for hd, r in av) / den if den else None)
        return out

    tt, bb = avg_seq(top), avg_seq(bottom)
    sig = [(tt[j] - bb[j]) if (tt[j] is not None and bb[j] is not None) else None for j in range(len(tt))]
    spy = [at("SPY", h) for h, _ in cps] + [retf("SPY") if retf else None]
    qqq = [at("QQQ", h) for h, _ in cps] + [retf("QQQ") if retf else None]
    ncol = len(cols) - 1

    def hdr(label):                                   # group sub-header row (label only)
        return (label, [""] * ncol, ["#1f2a3a"] * ncol, [None] * ncol)

    specs, header_rows, emph = [], set(), set()

    def add(spec, *, header=False, emph_row=False):
        specs.append(spec); i = len(specs) - 1
        if header:
            header_rows.add(i); emph.add(i)
        if emph_row:
            emph.add(i)

    # — every data row gets the ▲/▼ trend arrow (change vs the prior hour) —
    add(hdr("MARKET BENCHMARKS"), header=True)
    add(_row("SPY", spy, trend=True))
    add(_row("QQQ", qqq, trend=True))
    add(hdr("TOP / BOTTOM 10 — by prior-close score"), header=True)
    add(_row(f"Top {len(top)} avg", tt, trend=True))
    add(_row(f"Bottom {len(bottom)} avg", bb, trend=True))
    add(hdr("SIGNAL — is the ranking predicting?"), header=True)
    add(_row("Signal (Spread)", sig, trend=True), emph_row=True)
    if holds:
        n_mom = sum(1 for h in holds if h["mom"]); n_dec = len(holds) - n_mom
        mseq, dseq, dwseq = ew_contrib(True), ew_contrib(False), dw_path()
        # Sizing effect = the plug from actually dollar-weighting vs the equal-weight pools.
        siz = [(dwseq[j] - ((mseq[j] or 0.0) + (dseq[j] or 0.0))) if dwseq[j] is not None else None
               for j in range(len(dwseq))]
        add(hdr("HELD BOOK — equal-weight pools + sizing plug = Book"), header=True)
        add(_row(f"  Momentum ({n_mom})", mseq, trend=True))
        add(_row(f"  Decoupled ({n_dec})", dseq, trend=True))
        add(_row("  Sizing effect", siz, trend=True))
        add(_row("Book ($-wt) = Σ", dwseq, trend=True), emph_row=True)
    return _render_rows(ax, y, cols, cw, specs, emph, row_h=0.0185, fs=7.3, hfs=7.0,
                        header_rows=header_rows)


def _attribution_takeaways(d, retf, top, bottom):
    """Plain-English bullets summarizing the latest attribution: signal verdict, sleeve split,
    and the mix effect (Book − Top-N)."""
    def lat_avg(names):
        v = [retf(t) for t in names if retf and retf(t) is not None]
        return sum(v) / len(v) if v else None
    t, b = lat_avg(top), lat_avg(bottom)
    sig = (t - b) if (t is not None and b is not None) else None
    book = d.get("held_dw")
    out = []
    if sig is not None:
        out.append(f"Momentum signal {'WORKING' if sig > 0 else 'INVERTED'} today: "
                   f"Top-{len(top)} {P._pct(t)} vs Bottom-{len(bottom)} {P._pct(b)} → spread {P._pct(sig)}.")
    holds, _mw, _dw = _held_sleeves(d)
    avail = [h for h in holds if retf and retf(h["t"]) is not None]
    if avail:
        n = len(avail)
        mc = sum(retf(h["t"]) for h in avail if h["mom"]) / n          # equal-weight contributions
        dc = sum(retf(h["t"]) for h in avail if not h["mom"]) / n
        siz = (book - (mc + dc)) if book is not None else None          # sizing plug
        out.append(f"Book {P._pct(book)} = Momentum (eq-wt) {P._pct(mc)} + Decoupled {P._pct(dc)} "
                   f"+ Sizing {P._pct(siz)} — Sizing is what dollar-weighting (letting winners run) "
                   f"added vs holding the names equal-weight.")
    if book is not None and t is not None:
        diff = book - t
        out.append(f"Mix effect: Book − Top-{len(top)} = {P._pct(diff)} — "
                   + ("the blend CUSHIONED vs a pure-momentum book today."
                      if diff > 0 else "the blend gave up some upside vs a pure-momentum book today."))
    return out or ["(insufficient data for attribution)"]


def _intraday_table(ax, y, title, tickers, intra, cps, retf):
    y = P._section(ax, y, title)
    if not tickers:
        ax.text(0.075, y, "(none)", color=P.MIDGREY, fontsize=7.2, va="top")
        return y - 0.018
    cols = ["Ticker"] + [lbl for _, lbl in cps] + ["Latest"]
    n = len(cps)
    rem = 1 - 0.13 - 0.13
    cw = ([0.13] + [rem / n] * n + [0.13]) if n else [0.5, 0.5]
    by_cp = {hhmm: [] for hhmm, _ in cps}
    lat = []
    specs = []
    for t in tickers:
        rec = (intra or {}).get(t, {})
        seq = [rec.get(h) for h, _ in cps] + [retf(t) if retf else None]
        specs.append(_row(t, seq))                    # value sign-coloured, no arrows
        for h, _ in cps:
            if rec.get(h) is not None:
                by_cp[h].append(rec.get(h))
        if seq[-1] is not None:
            lat.append(seq[-1])
    # AVG row: value sign-coloured + a per-cell ▲/▼/– arrow for change vs the prior checkpoint.
    avg_seq = [sum(by_cp[h]) / len(by_cp[h]) if by_cp[h] else None for h, _ in cps] \
        + [sum(lat) / len(lat) if lat else None]
    specs.append(_row("AVG", avg_seq, trend=True))
    return _render_rows(ax, y, cols, cw, specs, {len(specs) - 1}, row_h=0.016, fs=6.8, hfs=6.5)


def _cps_for(d):
    from rank_report import _CHECKPOINTS
    intra = d.get("intraday") or {}
    rows = d.get("rows") or []
    tn = d["top_n"]
    top = [r["ticker"] for r in rows[:tn]]
    bottom = [r["ticker"] for r in rows[-tn:]]
    pos = d.get("positions")
    held = sorted(pos["ticker"]) if (pos is not None and not pos.empty) else []
    allt = list(dict.fromkeys(top + bottom + held))
    cps = [cp for cp in _CHECKPOINTS if any(intra.get(t, {}).get(cp[0]) is not None for t in allt)]
    return cps, top, bottom, held


def _page_attribution(pdf, d, cfg):
    """Page 3 — the attribution table read top-down, plus the main takeaways."""
    fig, ax = P._new_page(pdf)
    _banner(ax, d["scenario"], d["mark"], d["rank_close"], d.get("mark_note"))
    y = P._section(ax, 0.90, "Attribution — how today's book return breaks down (vs prior close)")
    cps, top, bottom, _held = _cps_for(d)
    retf = d.get("ret")
    y = _caption(ax, y,
                 "What each row tells you  ·  MARKET: SPY / QQQ.  TOP / BOTTOM 10: avg return of the "
                 "names scored highest / lowest at the prior close.  SIGNAL (Spread = Top − Bottom): "
                 "positive means the ranking is predicting well.  HELD BOOK: your names split ONCE by "
                 "their prior-close score — Momentum (cleared the gate) vs Decoupled (didn't), held "
                 "constant. Pools are EQUAL-WEIGHT contributions (each name 1/N) that sum to the "
                 "equal-weight book; Sizing effect = the plug from actually dollar-weighting (winners "
                 "bigger); Momentum + Decoupled + Sizing = Book ($-wt).  "
                 "Value colour = +/− ; ▲/▼ beside every number = change vs the prior hour "
                 "(green up / red down).", width=112)
    y -= 0.01
    y = _attribution_table(ax, y, d, cps, d.get("intraday") or {}, retf, top, bottom)
    y = P._section(ax, y - 0.01, "Main takeaways")
    P._bullets(ax, y, _attribution_takeaways(d, retf, top, bottom),
               width=112, lh=0.019, gap=0.007, fontsize=8.8)
    _footer(ax, 3)
    pdf.savefig(fig); P.plt.close(fig)


def _page_paths(pdf, d, cfg):
    """Page 4 — the intraday return paths (Top / Bottom / Held), each with an AVG-trend row."""
    fig, ax = P._new_page(pdf)
    _banner(ax, d["scenario"], d["mark"], d["rank_close"], d.get("mark_note"))
    y = P._section(ax, 0.90, "Intraday return paths — 1-hour intervals (vs prior close, Chicago time)")
    intra = d.get("intraday")
    tn = d["top_n"]
    cps, top, bottom, held = _cps_for(d)
    retf = d.get("ret")
    if not intra:
        ax.text(0.075, y, "Intraday 30-min data unavailable for this session yet "
                "(run later in the session, or the feed has no intraday bars).",
                color=P.MIDGREY, fontsize=8.4, va="top")
        _footer(ax, 4); pdf.savefig(fig); P.plt.close(fig)
        return
    y = _caption(ax, y, "Each holding's path vs the prior close at each elapsed hour. AVG = group "
                 "mean; value colour = +/− ; ▲/▼ on AVG = change vs the prior hour (green up / "
                 "red down).", width=112)
    y -= 0.008
    y = _intraday_table(ax, y, f"Prior Top {tn} (by EOD score)", top, intra, cps, retf)
    y = _intraday_table(ax, y - 0.006, f"Prior Bottom {tn} (by EOD score)", bottom, intra, cps, retf)
    y = _intraday_table(ax, y - 0.006, f"Currently held ({len(held)})", held, intra, cps, retf)
    _footer(ax, 4)
    pdf.savefig(fig); P.plt.close(fig)


def _page1(pdf, d, cfg):
    fig, ax = P._new_page(pdf)
    _banner(ax, d["scenario"], d["mark"], d["rank_close"], d.get("mark_note"))
    one = (d.get("stats") or {}).get("1D", {})
    port = one.get("port")
    y = P._cards(ax, 0.905, [
        ("Portfolio (intraday)", P._money(d.get("pv")), P.NAVY),
        ("Cash", P._money(d.get("cash")), P.NAVY),
        ("Session so far", P._pct(port), P._ret_color(port)),
        ("Signal spread", P._pct(d.get("signal_strength")), P._ret_color(d.get("signal_strength"))),
    ])

    # Market update — portfolio vs benchmark returns across windows
    y = P._section(ax, y - 0.005, "Market update — returns by window")
    brows = [[w, P._pct(s.get("port")), P._pct(s.get("spy")), P._pct(s.get("qqq"))]
             for w, s in (d.get("stats") or {}).items()]
    y = P._table(ax, y, ["Window", d["scenario"], "SPY", "QQQ"], brows,
                 [0.34, 0.22, 0.22, 0.22], align=["left", "right", "right", "right"],
                 row_h=0.021, fontsize=7.8, header_fontsize=7.4,
                 text_color=lambda r, c, v: (P._ret_color(P._parse_pct(v)) if c >= 1 else "#1f2a3a"))

    tn = d["top_n"]
    y = P._section(ax, y - 0.01, "Is the signal working so far?  (prior-close picks, intraday move)")
    spread = d.get("signal_strength")
    verdict = "—" if spread is None else ("WORKING" if spread > 0 else "INVERTED")
    vs_spy = (port - one.get("spy")) if (port is not None and one.get("spy") is not None) else None
    vs_qqq = (port - one.get("qqq")) if (port is not None and one.get("qqq") is not None) else None
    mrows = [
        [f"Top {tn} − Bottom {tn} spread  ({verdict})", P._pct(spread)],
        [f"Top {tn} avg (today)", P._pct(d.get("top_avg"))],
        [f"Bottom {tn} avg (today)", P._pct(d.get("bot_avg"))],
        [f"Universe avg (all {d['n']})", P._pct(d.get("univ_avg"))],
        ["Held book (equal-wt / $-wt)", f"{P._pct(d.get('held_avg'))}  /  {P._pct(d.get('held_dw'))}"],
        ["Advancers", f"{d.get('advancers')}/{d['n']}"],
        ["Portfolio vs SPY / vs QQQ (today)", f"{P._pct(vs_spy)}  /  {P._pct(vs_qqq)}"],
    ]
    y = P._table(ax, y, ["Metric", "Value"], mrows, [0.62, 0.38], align=["left", "right"],
                 text_color=lambda r, c, v: (P._ret_color(P._parse_pct(v))
                                             if c == 1 and "%" in v and "/" not in v else "#1f2a3a"))

    src = (f"EOD snapshot {d['rank_close']}" if d.get("snapshot_used")
           else f"recomputed from {d['rank_close']} close (no EOD snapshot found)")
    y = _caption(ax, y - 0.004, f"Prior top/bottom ranking source: {src}.", width=112, fontsize=7.2)
    y -= 0.008

    y = P._section(ax, y - 0.008, "What's NOT behaving as expected")
    y = P._bullets(ax, y, _anomalies(d, cfg), width=110, lh=0.0162, gap=0.006, fontsize=8.6)

    _footer(ax, 1)
    pdf.savefig(fig); P.plt.close(fig)


def _page2(pdf, d, cfg):
    fig, ax = P._new_page(pdf)
    _banner(ax, d["scenario"], d["mark"], d["rank_close"], d.get("mark_note"))
    y = 0.90
    cur = {r["ticker"]: r["score"] for r in (d.get("rows_cur") or [])}
    retf = d.get("ret")
    pos = d.get("positions")

    # Rank maps for the scoreboard (prior EOD ranking, live ranking, prior-day move).
    rows_prior = d.get("rows") or []
    rows_live = d.get("rows_cur") or []
    prior_rank = {r["ticker"]: r["rank"] for r in rows_prior}
    prior_score = {r["ticker"]: r["score"] for r in rows_prior}
    live_rank = {r["ticker"]: r["rank"] for r in rows_live}
    live_score = {r["ticker"]: r["score"] for r in rows_live}
    prior_chg = {r["ticker"]: r.get("prior_rank_chg") for r in rows_prior}

    def _score_then_now(t):                       # scoreboard: yesterday → today (2 scores)
        ps, ls = prior_score.get(t), live_score.get(t)
        if ps is None and ls is None:
            return "—"
        s2 = lambda x: f"{x:.2f}" if x is not None else "—"
        return f"{s2(ps)}→{s2(ls)}"

    # Current book — the shared rich table (identical to the EOD report's held book).
    y = P.render_current_book(ax, y, P.enrich_holdings(d),
                              npos=(0 if pos is None or pos.empty else len(pos)),
                              pv=d.get("pv"), cash=d.get("cash"), univ=d.get("univ_avg"),
                              held_dw=d.get("held_dw"))

    # Today's transactions so far
    tt = d.get("today_trades") or []
    y = P._section(ax, y - 0.012, f"Today's transactions so far ({d['mark']})")
    if not tt:
        ax.text(0.075, y, "No transactions yet today.", color=P.MIDGREY, fontsize=8.6, va="top"); y -= 0.03
    else:
        y = P._table(ax, y, ["Action", "Ticker", "Shares", "Price", "Reason", "Realized P&L"],
                     [[x["action"], x["ticker"], str(x["shares"]), P._money(x["price"], 2), x["reason"],
                       ("—" if x["pnl"] is None else P._money(x["pnl"]))] for x in tt],
                     [0.13, 0.13, 0.12, 0.14, 0.30, 0.18],
                     align=["left", "left", "right", "right", "left", "right"], fontsize=7.6)

    # Signal scoreboard — prior (EOD) ranking vs latest (live) ranking, and is the signal holding?
    tn = d["top_n"]
    rows = d.get("rows") or []                 # prior EOD ranking
    rows_cur = d.get("rows_cur") or []         # ranking recomputed on latest price
    prior_rank = {r["ticker"]: r["rank"] for r in rows}
    prior_score = {r["ticker"]: r["score"] for r in rows}
    latest_rank = {r["ticker"]: r["rank"] for r in rows_cur}
    latest_score = {r["ticker"]: r["score"] for r in rows_cur}
    today_ret = {r["ticker"]: r.get("return") for r in rows}
    big = max(latest_rank.values()) + 1 if latest_rank else 999

    prior_top = [r["ticker"] for r in rows[:tn]]
    held_top = sum(1 for t in prior_top if latest_rank.get(t, big) <= tn)
    frac = held_top / tn if tn else 0
    if frac >= 0.7:
        verdict, vcol = "WORKING — prior leaders are holding the top of the live ranking (momentum persisting)", P.GREEN
    elif frac >= 0.4:
        verdict, vcol = "MIXED — about half the prior leaders are slipping in the live ranking", "#b8860b"
    else:
        verdict, vcol = "BREAKING DOWN — prior leaders are rotating OUT of the live top (signal not holding)", P.RED

    y = P._section(ax, y - 0.012, "Signal scoreboard — prior (EOD) ranking → latest (live) ranking")
    y = _caption(ax, y, f"● Signal {verdict}.  ({held_top}/{tn} prior top-{tn} still in the live "
                 f"top-{tn}.)", x=0.075, width=96, fontsize=8.4, color=vcol, style="normal",
                 weight="bold", lh=0.016)
    y -= 0.008
    univ = d.get("univ_avg")
    srows = []
    for t in prior_top:
        pr, lr = prior_rank.get(t), latest_rank.get(t, None)
        d_today = (pr - lr) if (pr is not None and lr is not None) else None
        srows.append([t, str(pr), ("—" if lr is None else str(lr)), _rk_icon(d_today),
                      _rk_icon(prior_chg.get(t)), _score_then_now(t),
                      P._pct(today_ret.get(t)), _signal_today(today_ret.get(t), univ)])

    def scol(r, c, v):
        if c in (3, 4):
            return _rk_color(v)
        if c == 5:
            return _score_trend_color(v)
        if c == 6:
            return P._ret_color(P._parse_pct(v))
        if c == 7:
            return _SIG_COLORS.get(v, "#1f2a3a")
        return "#1f2a3a"
    y = P._table(ax, y, ["Ticker", "Prior #", "Live #", "Δ today", "Δ prior", "Score then→now", "Today %", "Signal Today"],
                 srows, [0.11, 0.085, 0.085, 0.075, 0.075, 0.20, 0.11, 0.26],
                 align=["left", "center", "center", "center", "center", "right", "right", "left"],
                 row_h=0.022, fontsize=7.6, header_fontsize=7.2, text_color=scol)
    _caption(ax, y - 0.008, f"Δ today = rank move at the live price (vs {d['rank_close']} EOD); "
             f"Δ prior = rank move on the prior day (vs the day before). Signal Today = today's return "
             "vs the universe avg (≥+2% Very Good · ≥+0.5% Moderate Good · ±0.5% Mixed · ≤−2% Very Bad).",
             width=112)

    _footer(ax, 2)
    pdf.savefig(fig); P.plt.close(fig)


def build_pdf(d: Dict[str, Any], cfg: Dict[str, Any], out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(out_path) as pdf:
        _page1(pdf, d, cfg)
        _page2(pdf, d, cfg)
        _page_attribution(pdf, d, cfg)
        _page_paths(pdf, d, cfg)
    return out_path


def run(scenario: Optional[str] = None, start: Optional[date] = None, end: Optional[date] = None,
        output: Optional[Path] = None, account: Optional[str] = None, prepost: bool = False) -> Path:
    """Midday Pulse PDF. With `account`, the held book / equity come from the frozen+living
    ledger (as of its last close), marked to `end` (default today) for the intraday pulse;
    scenario/start default to the account's base/inception. Else a fresh scenario run.

    `prepost` marks the book to the latest extended-hours (pre/post-market) print."""
    import rank_report
    from scenarios import build_config, load_scenario
    from backtest import load_config as _load_cfg
    root = Path(__file__).parent.parent
    if account:
        from account import load_manifest
        man = load_manifest(account)
        scenario = scenario or man["scenario"]
        start = start or date.fromisoformat(man["inception"])
    if not scenario:
        raise ValueError("midday_pdf.run needs --scenario or --account")
    end = end or date.today()                  # intraday report → mark to today's session
    start = start or date(end.year, 1, 1)
    cfg = build_config(_load_cfg(root / "config"), load_scenario(scenario))
    # Use the prior EOD snapshot + intraday paths; never write a provisional snapshot.
    d = rank_report.build_report(scenario, start, end, cfg=cfg, write_snapshot=False,
                                 account=account, prepost=prepost)
    tag = f"{account}_" if account else ""
    out = output or (root / "reports" / f"midday_{tag}{scenario}_{d['mark'].isoformat()}.pdf")
    return build_pdf(d, cfg, out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Midday Pulse PDF for a scenario.")
    ap.add_argument("--scenario")
    ap.add_argument("--start")
    ap.add_argument("--end")
    ap.add_argument("--account", help="render the held book from a frozen/living account ledger")
    ap.add_argument("--prepost", action="store_true",
                    help="mark the book to the latest extended-hours (pre/post-market) print")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    out = run(a.scenario, date.fromisoformat(a.start) if a.start else None,
              date.fromisoformat(a.end) if a.end else None,
              Path(a.out) if a.out else None, account=a.account, prepost=a.prepost)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
