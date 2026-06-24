"""
Build reports/model_v4_guidebook.pdf — a concise, non-technical guide to model_v4,
the hedge overlay, and the tracker account. Plain matplotlib text pages.
"""
import textwrap
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.backends.backend_pdf import PdfPages

OUT = Path(__file__).parent.parent / "reports" / "model_v4_guidebook.pdf"
NAVY, GREEN, RED, GREY, INK = "#0b3d91", "#0a5d00", "#8a1a1a", "#666666", "#1f2a3a"


def _page():
    fig = plt.figure(figsize=(8.5, 11)); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    return fig, ax


def T(ax, x, y, s, **kw):
    ax.text(x, y, s, transform=ax.transAxes, va="top", parse_math=False, **kw)


def header(ax, y, s, color=NAVY):
    T(ax, 0.07, y, s, fontsize=13.5, fontweight="bold", color=color)
    return y - 0.030


def bullets(ax, y, items, x=0.085, width=92, fs=9.7, lh=0.0175, gap=0.010, lead="•  "):
    for it in items:
        wrapped = textwrap.wrap(it, width=width) or [""]
        T(ax, x, y, lead + wrapped[0], fontsize=fs, color=INK)
        y -= lh
        for cont in wrapped[1:]:
            T(ax, x + 0.018, y, cont, fontsize=fs, color=INK); y -= lh
        y -= gap
    return y - 0.004


def box(ax, y, title, lines, h=None, fc="#eef4fb", ec=NAVY, fs=9.4):
    n = sum(len(textwrap.wrap(l, 86)) or 1 for l in lines)
    h = h or (0.034 + n * 0.0165)
    ax.add_patch(FancyBboxPatch((0.07, y - h), 0.86, h, boxstyle="round,pad=0.006",
                                transform=ax.transAxes, facecolor=fc, edgecolor=ec, lw=1.1))
    T(ax, 0.085, y - 0.020, title, fontsize=10, fontweight="bold", color=ec)
    yy = y - 0.040
    for l in lines:
        for w in (textwrap.wrap(l, 86) or [""]):
            T(ax, 0.095, yy, w, fontsize=fs, color=INK); yy -= 0.0165
    return y - h - 0.012


def footer(ax, n):
    T(ax, 0.07, 0.035, "model_v4 guidebook", fontsize=7.5, color=GREY, style="italic")
    ax.text(0.93, 0.035, f"{n}", transform=ax.transAxes, fontsize=7.5, color=GREY, ha="right")


with PdfPages(OUT) as pdf:
    # ============ PAGE 1 — cover + overview ============
    fig, ax = _page()
    T(ax, 0.07, 0.93, "model_v4", fontsize=30, fontweight="bold", color=NAVY)
    T(ax, 0.07, 0.875, "A Plain-English Guide", fontsize=16, color=INK)
    T(ax, 0.07, 0.845, "How the strategy picks, sizes, holds and hedges — and how the tracker follows it.",
      fontsize=10.5, color=GREY, style="italic")
    y = 0.80
    y = header(ax, y, "In one sentence")
    y = bullets(ax, y, [
        "model_v4 is a systematic momentum strategy: every day it ranks a fixed list of "
        "semiconductor / AI / tech-growth stocks by recent strength, owns the strongest ones, "
        "automatically turns risk up or down as markets get calmer or choppier, and sells "
        "losers and stale names by rule — no discretion, no emotion."])
    y = box(ax, y - 0.004, "The essentials at a glance", [
        "Universe:  ~83 semiconductor / AI / tech-growth stocks (a fixed list).",
        "Style:  momentum — buy strength, hold winners, cut laggards.",
        "Cadence:  decisions once a day after the close; orders fill the next morning.",
        "Risk control:  a volatility 'governor' shrinks exposure when markets get wild.",
        "Optional add-on:  a 1-day hedge that softens sharp next-day pullbacks.",
        "Everything is simulated — these are recommendations, never live orders.",
    ])
    y = header(ax, y - 0.006, "What's in this guide")
    y = bullets(ax, y, [
        "How it chooses what to own  (the score, the ranking, the buy rules).",
        "How it controls risk and decides to sell.",
        "The hedge overlay — what it is, when it fires, and what to expect.",
        "The tracker account — a $100k paper account that follows model_v4.",
        "A quick glossary and the key reminders.",
    ], gap=0.006)
    footer(ax, 1); pdf.savefig(fig); plt.close(fig)

    # ============ PAGE 2 — how it chooses ============
    fig, ax = _page()
    y = header(ax, 0.93, "1.  How it chooses what to own")
    y = bullets(ax, y, [
        "The score.  Each stock gets a single 'momentum score' from 0 to 1 that blends several "
        "measures of how strong and steady its recent price trend is. Higher means stronger.",
        "The ranking.  After every close, all ~83 names are re-scored and ranked best to worst. "
        "The list naturally shifts as leadership rotates.",
        "The buy gate.  A name must score at least 0.70 to be considered at all — a basic "
        "quality filter that keeps weak names out.",
        "Patience on new buys.  A brand-new position must score above 0.90 for three days in a "
        "row before it's bought. This avoids chasing a single hot day that fizzles.",
    ])
    y = box(ax, y, "How much of each name?", [
        "Roughly equal-weight: the book spreads across its holdings rather than betting big on one.",
        "Fully invested up to ~75% of the portfolio (the rest is a cash buffer).",
        "At most 2 new buys per day — steady, low-churn turnover.",
    ], fc="#f3f7ee", ec=GREEN)
    y = header(ax, y - 0.006, "Why momentum?")
    y = bullets(ax, y, [
        "Strong stocks have tended to keep outperforming over the following weeks — the strategy "
        "simply rides that, holding leaders until they weaken.",
        "The trade-off is that momentum can reverse sharply in panicky markets. That's exactly "
        "what the volatility governor (next page) and the hedge overlay are there to manage.",
    ])
    footer(ax, 2); pdf.savefig(fig); plt.close(fig)

    # ============ PAGE 3 — risk + selling ============
    fig, ax = _page()
    y = header(ax, 0.93, "2.  How it controls risk and sells")
    y = box(ax, y, "The volatility governor — the main safety dial", [
        "model_v4 watches its own recent volatility and compares it to a 35% target.",
        "If the book is wilder than target, it automatically holds LESS (e.g. ~82% of normal);",
        "when things calm down, it scales back up to full. It happens by rule, every day —",
        "the single biggest reason the strategy rides out turbulent markets.",
    ], fc="#fdf6e9", ec="#a06a00")
    y = header(ax, y - 0.004, "The selling rules (all automatic)")
    y = bullets(ax, y, [
        "Stop-loss (7.5%):  a holding is cut if it falls 7.5% — but only if its score has ALSO "
        "dropped below 0.90. A strong name that merely dips is not dumped.",
        "Max holding (30 days):  positions are time-limited, but the clock is suppressed until "
        "the score falls below 0.80 — so genuine leaders are allowed to keep running.",
        "No 'score-decay' dumping:  the strategy deliberately does NOT sell just because a score "
        "drifts down (testing showed that sold names that later recovered).",
    ])
    y = box(ax, y - 0.002, "The daily rhythm", [
        "Decide at the close  →  fill at the next morning's open.",
        "No intraday trading and no overnight surprises — one clean decision per day.",
    ])
    y = header(ax, y - 0.004, "What this adds up to")
    y = bullets(ax, y, [
        "A concentrated but rules-bound book that leans into winners, trims risk automatically "
        "when markets shake, and avoids panic-selling names that are still trending."])
    footer(ax, 3); pdf.savefig(fig); plt.close(fig)

    # ============ PAGE 4 — hedge overlay ============
    fig, ax = _page()
    y = header(ax, 0.93, "3.  The hedge overlay  (optional pullback protection)")
    y = bullets(ax, y, [
        "The idea.  When the market jumps hard AND volatility is already high, the very next day "
        "often gives some of it back. The overlay buys a small, one-day 'insurance' position to "
        "soften that pullback — then closes it out the next day."])
    y = box(ax, y, "When it fires — two gates", [
        "SOFT signal:  QQQ up >= 1.5% and volatility elevated   ->   buy a HALF-size hedge.",
        "STRONG signal:  QQQ up >= 2.0% and volatility high      ->   buy a FULL-size hedge.",
        "Neither one true  ->  no hedge that day (it sits out most days).",
    ], fc="#eef4fb", ec=NAVY)
    y = header(ax, y - 0.004, "What it buys, and how much")
    y = bullets(ax, y, [
        "Instrument:  SOXS — a fund that rises about 3x when semiconductors fall. It is BOUGHT "
        "(a normal long purchase); there is no short-selling.",
        "Sizing:  scaled to the portfolio's risk and current value — roughly 12-14% of invested "
        "value on a full signal, about half that on a soft one. A bigger book buys a bigger hedge "
        "automatically.",
        "Holding period:  exactly one day. It is sold at the next close, every time.",
    ])
    y = box(ax, y - 0.002, "What to expect (the honest version)", [
        "It modestly improves risk-adjusted returns and roughly HALVES the worst single-day drops",
        "(e.g. it turned a recent -3.8% day into about -1.8%).",
        "It earns its keep in volatile, spike-prone years and does little in calm ones.",
        "It is a shock-absorber for bad days — NOT a cure for long, grinding declines.",
    ], fc="#f3f7ee", ec=GREEN)
    footer(ax, 4); pdf.savefig(fig); plt.close(fig)

    # ============ PAGE 5 — the tracker ============
    fig, ax = _page()
    y = header(ax, 0.93, "4.  The tracker account")
    y = bullets(ax, y, [
        "What it is.  A separate $100,000 paper account that follows model_v4's picks and the "
        "hedge, kept as a locked, auditable record (an original 'frozen' core plus a daily "
        "'living' log that can't silently overwrite history)."])
    y = box(ax, y, "Ramp-up phase (where it is now)", [
        "Because it started underfunded, it is still building its book. Each day at the close it:",
        "  •  BUYS any name scoring above 0.90 that it doesn't already own (~8.5% each), and",
        "  •  adds the hedge when the hedge signal fires.",
        "It does NOT sell during ramp-up. Once fully invested, model_v4's normal sell rules take over.",
    ], fc="#fdf6e9", ec="#a06a00")
    y = header(ax, y - 0.004, "The daily report")
    y = bullets(ax, y, [
        "Every evening the tracker produces a one-glance report with three tables:",
    ], gap=0.004)
    y = bullets(ax, y, [
        "1.  Book BEFORE today's trades — where the day started.",
        "2.  Today's trades — exactly what it bought (and the hedge).",
        "3.  Book AFTER today's trades — each holding's share of value, plus cash left.",
    ], x=0.105, gap=0.004, lead="")
    y = box(ax, y - 0.002, "How it moves forward", [
        "One command rolls the account ahead a day, applies the rules, re-prices the book, and",
        "files the report in the account's own folder. The frozen history is integrity-checked,",
        "so the locked record stays trustworthy over time.",
    ])
    footer(ax, 5); pdf.savefig(fig); plt.close(fig)

    # ============ PAGE 6 — glossary + reminders ============
    fig, ax = _page()
    y = header(ax, 0.93, "5.  Quick glossary")
    y = bullets(ax, y, [
        "Composite score — a 0-to-1 strength rating; higher = stronger momentum.",
        "Buy gate — the minimum score (0.70) a name needs to be eligible.",
        "Volatility governor — the rule that shrinks exposure when markets get choppy.",
        "QQQ — the Nasdaq-100 (big tech) index; its daily move is the hedge trigger.",
        "SOXS — a fund that rises ~3x when semiconductors fall (the hedge instrument).",
        "Decide-at-close / fill-next-open — trades are chosen after the close and executed the "
        "next morning.",
    ], gap=0.007)
    y = box(ax, y - 0.004, "Important reminders", [
        "Paper trading only — everything here is a simulation / recommendation, never a live order.",
        "The hedge is a one-day position — it must be closed out the next session.",
        "Results are based on limited history and partly in-sample; treat the exact numbers as "
        "indicative, and re-check before relying on them.",
        "The strategy is concentrated in semis / AI / tech — it is built to ride that theme, which "
        "also means it moves a lot.",
    ], fc="#fbeeee", ec=RED)
    y = header(ax, y - 0.006, "The whole thing in four lines")
    y = bullets(ax, y, [
        "Rank the strongest tech/semis names; own the leaders.",
        "Automatically hold less when markets get volatile.",
        "Sell losers and stale names by rule, not by gut.",
        "On sharp up-days in jumpy markets, add a one-day hedge to soften the next-day dip.",
    ], gap=0.004)
    footer(ax, 6); pdf.savefig(fig); plt.close(fig)

print("wrote", OUT)
