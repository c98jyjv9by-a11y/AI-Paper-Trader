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


def _footer(ax, page):
    ax.add_line(P.plt.Line2D([0.06, 0.94], [0.035, 0.035], color=P.RULE, lw=0.8))
    ax.text(0.06, 0.022, "Paper-trading research only — not investment advice. Intraday/provisional "
            "prices; figures settle at the close.", color=P.MIDGREY, fontsize=6.5, va="center")
    ax.text(0.94, 0.022, f"midday-pulse · p.{page}", color=P.MIDGREY, fontsize=6.5,
            va="center", ha="right")


def _banner(ax, scenario, mark, rank_close):
    ax.add_patch(P.plt.Rectangle((0, 0.93), 1, 0.07, transform=ax.transAxes,
                                 facecolor=P.NAVY, edgecolor="none"))
    ax.text(0.06, 0.965, f"{scenario}  —  Midday Pulse", color="white", fontsize=15,
            fontweight="bold", va="center")
    ax.text(0.06, 0.943, "Intraday snapshot · provisional prices · is the signal working so far?",
            color="#b9c6d8", fontsize=8.5, va="center")
    ax.text(0.94, 0.958, mark.isoformat(), color="white", fontsize=11, fontweight="bold",
            va="center", ha="right")
    ax.text(0.94, 0.940, f"vs prior close {rank_close}", color="#b9c6d8", fontsize=7.5,
            va="center", ha="right")


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


def _intraday_table(ax, y, title, tickers, intra, cps, retf):
    y = P._section(ax, y, title)
    if not tickers:
        ax.text(0.075, y, "(none)", color=P.MIDGREY, fontsize=7.2, va="top")
        return y - 0.018
    labels = [lbl for _, lbl in cps]
    cols = ["Ticker"] + labels + ["Latest"]
    n = len(cps)
    rem = 1 - 0.13 - 0.13
    cw = [0.13] + ([rem / n] * n if n else []) + [0.13] if n else [0.5, 0.5]
    by_cp = {hhmm: [] for hhmm, _ in cps}
    lat = []
    rows = []
    for t in tickers:
        rec = (intra or {}).get(t, {})
        latest = retf(t) if retf else None
        row = [t] + [P._pct(rec.get(hhmm)) for hhmm, _ in cps] + [P._pct(latest)]
        rows.append(row)
        for hhmm, _ in cps:
            v = rec.get(hhmm)
            if v is not None:
                by_cp[hhmm].append(v)
        if latest is not None:
            lat.append(latest)
    avg = ["AVG"] + [P._pct(sum(by_cp[h]) / len(by_cp[h]) if by_cp[h] else None) for h, _ in cps] \
          + [P._pct(sum(lat) / len(lat) if lat else None)]
    rows.append(avg)
    aln = ["left"] + ["right"] * (len(cols) - 1)
    return P._table(ax, y, cols, rows, cw, align=aln, row_h=0.0162, fontsize=6.8,
                    header_fontsize=6.6, emph_rows={len(rows) - 1},
                    text_color=lambda r, c, v: (P._ret_color(P._parse_pct(v)) if c >= 1 else "#1f2a3a"))


def _page3(pdf, d, cfg):
    from rank_report import _CHECKPOINTS
    fig, ax = P._new_page(pdf)
    _banner(ax, d["scenario"], d["mark"], d["rank_close"])
    y = 0.90
    y = P._section(ax, y, "Intraday return paths — 1-hour intervals (vs prior close, Chicago time)")
    intra = d.get("intraday")
    rows = d.get("rows") or []
    tn = d["top_n"]
    top = [r["ticker"] for r in rows[:tn]]
    bottom = [r["ticker"] for r in rows[-tn:]]
    pos = d.get("positions")
    held = sorted(pos["ticker"]) if (pos is not None and not pos.empty) else []
    retf = d.get("ret")

    if not intra:
        ax.text(0.075, y, "Intraday 30-min data unavailable for this session yet "
                "(run later in the session, or the feed has no intraday bars).",
                color=P.MIDGREY, fontsize=8.4, va="top")
        _footer(ax, 3); pdf.savefig(fig); P.plt.close(fig)
        return

    allt = list(dict.fromkeys(top + bottom + held))
    cps = [cp for cp in _CHECKPOINTS if any(intra.get(t, {}).get(cp[0]) is not None for t in allt)]
    ax.text(0.06, y, f"Return vs the {d['rank_close']} close at each elapsed hour; AVG = group mean. "
            "Prior ranking from the EOD snapshot.", color=P.MIDGREY, fontsize=7.0, va="top", style="italic")
    y -= 0.02
    y = _intraday_table(ax, y, f"Prior Top {tn} (by EOD score)", top, intra, cps, retf)
    y = _intraday_table(ax, y - 0.006, f"Prior Bottom {tn} (by EOD score)", bottom, intra, cps, retf)
    y = _intraday_table(ax, y - 0.006, f"Currently held ({len(held)})", held, intra, cps, retf)
    _footer(ax, 3)
    pdf.savefig(fig); P.plt.close(fig)


def _page1(pdf, d, cfg):
    fig, ax = P._new_page(pdf)
    _banner(ax, d["scenario"], d["mark"], d["rank_close"])
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
    ax.text(0.06, y - 0.004, f"Prior top/bottom ranking source: {src}.",
            color=P.MIDGREY, fontsize=7.2, va="top", style="italic")
    y -= 0.022

    y = P._section(ax, y - 0.008, "What's NOT behaving as expected")
    y = P._bullets(ax, y, _anomalies(d, cfg), width=110, lh=0.0162, gap=0.006, fontsize=8.6)

    _footer(ax, 1)
    pdf.savefig(fig); P.plt.close(fig)


def _page2(pdf, d, cfg):
    fig, ax = P._new_page(pdf)
    _banner(ax, d["scenario"], d["mark"], d["rank_close"])
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
    ax.text(0.075, y, f"● Signal {verdict}.  ({held_top}/{tn} prior top-{tn} still in the live top-{tn}.)",
            color=vcol, fontsize=8.4, fontweight="bold", va="top")
    y -= 0.024
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
    ax.text(0.06, y - 0.008, f"Δ today = rank move at the live price (vs {d['rank_close']} EOD); "
            f"Δ prior = rank move on the prior day (vs the day before). Signal Today = today's return "
            "vs the universe avg (≥+2% Very Good · ≥+0.5% Moderate Good · ±0.5% Mixed · ≤−2% Very Bad).",
            color=P.MIDGREY, fontsize=7.0, va="top", style="italic")

    _footer(ax, 2)
    pdf.savefig(fig); P.plt.close(fig)


def build_pdf(d: Dict[str, Any], cfg: Dict[str, Any], out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(out_path) as pdf:
        _page1(pdf, d, cfg)
        _page2(pdf, d, cfg)
        _page3(pdf, d, cfg)
    return out_path


def run(scenario: str, start: date, end: date, output: Optional[Path] = None) -> Path:
    import rank_report
    from scenarios import build_config, load_scenario
    from backtest import load_config as _load_cfg
    root = Path(__file__).parent.parent
    cfg = build_config(_load_cfg(root / "config"), load_scenario(scenario))
    # Load the prior EOD ranking snapshot (authoritative prior top/bottom + scores) and
    # compute intraday paths, but DON'T write a provisional snapshot for the in-progress day.
    d = rank_report.build_report(scenario, start, end, cfg=cfg, write_snapshot=False)
    out = output or (root / "reports" / f"midday_{scenario}_{d['mark'].isoformat()}.pdf")
    return build_pdf(d, cfg, out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Midday Pulse PDF for a scenario.")
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
