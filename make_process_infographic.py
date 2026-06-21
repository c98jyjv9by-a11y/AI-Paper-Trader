"""
make_process_infographic.py — a concise, NON-TECHNICAL visual walkthrough of the whole pipeline:
model_v4 (the stock-picking model) -> safe order building -> Alpaca PAPER submission -> the daily
automated cycle -> what moving to REAL money would take.

Pure presentation (matplotlib/PdfPages). No model/account state is touched.
Output: reports/model_v4_process_infographic.pdf
"""
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch, Circle

ROOT = Path(__file__).parent
OUT = ROOT / "reports" / "model_v4_process_infographic.pdf"

# ── palette ─────────────────────────────────────────────────────────────────────────
NAVY = "#1f3a5f"; BLUE = "#2e86de"; TEAL = "#16a085"; GREEN = "#27ae60"
AMBER = "#e8901a"; RED = "#c0392b"; GRAY = "#5d6d7e"; LIGHT = "#eef2f7"; PAPER = "#f7f9fc"


def _fig():
    fig = plt.figure(figsize=(8.5, 11)); ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 10); ax.set_ylim(0, 13); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 10, 13, boxstyle="square,pad=0", fc=PAPER, ec="none"))
    return fig, ax


def T(ax, x, y, s, fs=11, c=NAVY, b=False, ha="center", va="center", it=False):
    ax.text(x, y, s, fontsize=fs, color=c, ha=ha, va=va,
            fontweight="bold" if b else "normal", fontstyle="italic" if it else "normal",
            parse_math=False)


def box(ax, x, y, w, h, fc, ec="none", lw=0, r=0.12):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.02,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, mutation_aspect=1.0))


def chip(ax, x, y, w, h, title, lines, fc, tc="white", title_fs=12, body_fs=9.5, ec="none", lw=0):
    box(ax, x, y, w, h, fc, ec=ec, lw=lw)
    T(ax, x + w / 2, y + h - 0.34, title, fs=title_fs, c=tc, b=True)
    for i, ln in enumerate(lines):
        T(ax, x + w / 2, y + h - 0.74 - i * 0.34, ln, fs=body_fs, c=tc)


def numdot(ax, x, y, n, c, r=0.28):
    ax.add_patch(Circle((x, y), r, fc=c, ec="none"))
    T(ax, x, y, str(n), fs=13, c="white", b=True)


def arrow(ax, x1, y1, x2, y2, c=GRAY, lw=2.4, style="-|>"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=c, lw=lw, shrinkA=2, shrinkB=2))


def header(ax, kicker, title):
    box(ax, 0, 11.55, 10, 1.45, NAVY, r=0.0)
    T(ax, 0.6, 12.45, kicker, fs=10.5, c="#9fc2e8", b=True, ha="left")
    T(ax, 0.6, 11.95, title, fs=19, c="white", b=True, ha="left")


def footer(ax, pg):
    T(ax, 0.6, 0.35, "model_v4 paper-trading system  ·  research tool, not financial advice",
      fs=8, c=GRAY, ha="left")
    T(ax, 9.4, 0.35, f"{pg}", fs=8, c=GRAY, ha="right")


pages = []

# ══ PAGE 1 — BIG PICTURE ═════════════════════════════════════════════════════════════
fig, ax = _fig()
box(ax, 0, 9.4, 10, 3.6, NAVY, r=0.0)
T(ax, 5, 12.3, "How the model_v4 system works", fs=24, c="white", b=True)
T(ax, 5, 11.65, "From a stock-picking model to simulated broker trades —", fs=13, c="#cfe0f3")
T(ax, 5, 11.25, "and what it would take to use real money", fs=13, c="#cfe0f3")
box(ax, 3.0, 10.25, 4.0, 0.62, AMBER)
T(ax, 5, 10.56, "PAPER TRADING ONLY", fs=13, c="white", b=True)
T(ax, 5, 10.05, "fake money · real prices & timing · no capital at risk", fs=9.5, c="#ffe4c2")

T(ax, 5, 8.95, "The whole journey in five steps", fs=15, c=NAVY, b=True)
steps = [
    (BLUE, "Rank", "Score ~83 AI &", "chip stocks daily"),
    (TEAL, "Choose", "Pick the strongest", "+ a crash hedge"),
    (GREEN, "Build", "Turn picks into", "safe limit orders"),
    (NAVY, "Submit", "Send to the", "paper broker"),
    (AMBER, "Measure", "Record fills &", "real-world costs"),
]
y = 6.7; w = 1.62; gap = 0.25; x0 = (10 - (5 * w + 4 * gap)) / 2
for i, (c, t, l1, l2) in enumerate(steps):
    x = x0 + i * (w + gap)
    chip(ax, x, y, w, 1.5, t, [l1, l2], c, title_fs=12, body_fs=8.6)
    numdot(ax, x + 0.0, y + 1.5, i + 1, c)
    if i < 4:
        arrow(ax, x + w + 0.02, y + 0.75, x + w + gap - 0.02, y + 0.75, c=GRAY, lw=2.2)

box(ax, 0.8, 3.6, 8.4, 2.4, LIGHT)
T(ax, 5, 5.6, "In one sentence", fs=14, c=NAVY, b=True)
T(ax, 5, 5.05, "Every day the model decides which trending tech stocks to hold (and when to",
  fs=11, c=GRAY)
T(ax, 5, 4.68, "hedge), those decisions become carefully-priced orders, and a simulated broker",
  fs=11, c=GRAY)
T(ax, 5, 4.31, "account fills them with real market prices — so we learn how the strategy would",
  fs=11, c=GRAY)
T(ax, 5, 3.94, "actually behave before a single real dollar is ever involved.", fs=11, c=GRAY)

footer(ax, "Overview")
pages.append(fig)

# ══ PAGE 2 — THE MODEL (BRAIN) ═══════════════════════════════════════════════════════
fig, ax = _fig()
header(ax, "STEPS 1–2  ·  THE MODEL", "What model_v4 decides")

# funnel
box(ax, 0.7, 9.0, 4.3, 1.9, BLUE)
T(ax, 2.85, 10.55, "~83 stocks", fs=13, c="white", b=True)
T(ax, 2.85, 10.1, "AI · semiconductors · tech", fs=10, c="#e8f1fb")
T(ax, 2.85, 9.6, "scored 0 to 1 every day on", fs=10, c="#e8f1fb")
T(ax, 2.85, 9.27, "momentum (who's trending up)", fs=10, c="#e8f1fb")
arrow(ax, 5.1, 9.95, 5.9, 9.95, c=NAVY, lw=2.6)
box(ax, 6.0, 9.2, 3.3, 1.5, TEAL)
T(ax, 7.65, 10.35, "The strongest names", fs=12, c="white", b=True)
T(ax, 7.65, 9.9, "score above 0.70 = buy", fs=9.5, c="#dff3ee")
T(ax, 7.65, 9.55, "above 0.90 = conviction add", fs=9.5, c="#dff3ee")

T(ax, 5, 8.5, "Built-in risk brakes", fs=14, c=NAVY, b=True)
cards = [
    (GREEN, "Spread out", ["Money split evenly across", "holdings — never more", "than ~75% invested"]),
    (AMBER, "Volatility governor", ["Automatically invests LESS", "when markets get wild,", "more when they calm"]),
    (RED, "Stop-loss", ["Exits a holding that falls", "too far and is no longer", "one of the leaders"]),
]
w = 2.9; gap = 0.3; x0 = (10 - (3 * w + 2 * gap)) / 2; y = 6.4
for i, (c, t, ls) in enumerate(cards):
    chip(ax, x0 + i * (w + gap), y, w, 1.7, t, ls, c, title_fs=12, body_fs=9)

# hedge
box(ax, 0.8, 3.5, 8.4, 2.3, NAVY)
T(ax, 5, 5.45, "The crash hedge (a shield, not a bet)", fs=14, c="white", b=True)
T(ax, 5, 4.92, "When the market jumps hard AND turbulence spikes at the same time — a classic",
  fs=10.5, c="#cfe0f3")
T(ax, 5, 4.56, '"a pullback may be coming" warning — the system buys a ONE-DAY position (SOXS)',
  fs=10.5, c="#cfe0f3")
T(ax, 5, 4.20, "that profits if semiconductors drop, cushioning the portfolio. It sits ON TOP of",
  fs=10.5, c="#cfe0f3")
T(ax, 5, 3.84, "the model without changing how the model picks stocks.", fs=10.5, c="#cfe0f3")

box(ax, 0.8, 2.5, 8.4, 0.7, LIGHT)
T(ax, 5, 2.85, "Result: hold the trend when it's working, automatically pull back when it isn't.",
  fs=11, c=NAVY, b=True)
footer(ax, "The model")
pages.append(fig)

# ══ PAGE 3 — DECISION -> PAPER TRADE ═════════════════════════════════════════════════
fig, ax = _fig()
header(ax, "STEPS 3–4  ·  THE PIPELINE", "Turning a decision into a (paper) trade")

flow = [
    (BLUE, "Decide at close", ["The model picks using the", "day's closing prices..."]),
    (TEAL, "Build safe orders", ["...and trades at the NEXT", "morning's open"]),
    (NAVY, "Send to paper broker", ["Alpaca paper account:", "fake $100k, real market"]),
]
y = 9.0; w = 2.9; gap = 0.3; x0 = (10 - (3 * w + 2 * gap)) / 2
for i, (c, t, ls) in enumerate(flow):
    chip(ax, x0 + i * (w + gap), y, w, 1.6, t, ls, c)
    if i < 2:
        arrow(ax, x0 + (i + 1) * w + i * gap + 0.02, y + 0.8,
              x0 + (i + 1) * (w + gap) - 0.02, y + 0.8, c=GRAY)

# the collar idea
box(ax, 0.8, 5.7, 8.4, 2.7, LIGHT)
T(ax, 5, 8.05, "The key safety idea: a price 'collar'", fs=14, c=NAVY, b=True)
T(ax, 5, 7.55, "Every order is a LIMIT order with a guardrail sized to how much each stock",
  fs=10.5, c=GRAY)
T(ax, 5, 7.19, "normally moves overnight — so we never overpay on a bad opening jump.", fs=10.5, c=GRAY)
# two examples
box(ax, 1.4, 6.05, 3.3, 0.95, GREEN)
T(ax, 3.05, 6.72, "Calm stock", fs=11, c="white", b=True)
T(ax, 3.05, 6.34, "tight collar (~1%)", fs=9.5, c="#dff3ee")
box(ax, 5.3, 6.05, 3.3, 0.95, AMBER)
T(ax, 6.95, 6.72, "Jumpy hedge (SOXS)", fs=11, c="white", b=True)
T(ax, 6.95, 6.34, "wide collar (~6%)", fs=9.5, c="#ffe9cf")
T(ax, 5, 5.85, "If the open gaps past the collar, the order simply doesn't fill — we skip it.",
  fs=9.5, c=GRAY, it=True)

# safety rails
box(ax, 0.8, 2.4, 8.4, 2.9, NAVY)
T(ax, 5, 4.95, "Safety rails (always on)", fs=14, c="white", b=True)
rails = [
    "PAPER ONLY — the connection physically refuses any non-paper account",
    "SUBMIT IS OFF BY DEFAULT — sending real orders must be explicitly armed each time",
    "EVERY ACTION LOGGED — orders, fills, and costs are all recorded",
    "BROKER IS THE TRUTH — the ledger is rebuilt from what actually filled",
]
for i, r in enumerate(rails):
    T(ax, 1.2, 4.45 - i * 0.46, "✓", fs=13, c=GREEN, b=True, ha="left")
    T(ax, 1.6, 4.45 - i * 0.46, r, fs=10.2, c="#e8f1fb", ha="left")
footer(ax, "Decision to trade")
pages.append(fig)

# ══ PAGE 4 — DAILY CYCLE ═════════════════════════════════════════════════════════════
fig, ax = _fig()
header(ax, "THE DAILY RHYTHM", "What happens automatically, every weekday")

# timeline
ax.plot([1.2, 8.8], [9.4, 9.4], color=GRAY, lw=3, zorder=1)
marks = [
    (1.8, BLUE, "Pre-open", "SUBMIT", ["The day's orders are", "sent to the broker"]),
    (5.0, TEAL, "After the open", "RETRY", ["Anything unfilled is", "re-priced once a little", "wider — else skipped"]),
    (8.2, NAVY, "After the close", "RECONCILE", ["Record real fills,", "measure slippage,", "update + report"]),
]
for x, c, when, what, ls in marks:
    ax.add_patch(Circle((x, 9.4), 0.16, fc=c, ec="white", lw=2, zorder=3))
    T(ax, x, 9.95, when, fs=10, c=GRAY, b=True)
    chip(ax, x - 1.35, 6.9, 2.7, 1.95, what, ls, c, title_fs=13, body_fs=9)
    arrow(ax, x, 9.2, x, 8.9, c=c, lw=2)

box(ax, 0.8, 4.7, 8.4, 1.7, LIGHT)
T(ax, 5, 6.0, "What 'slippage' means (and why we measure it)", fs=13, c=NAVY, b=True)
T(ax, 5, 5.5, "Slippage = the gap between the price we expected and the price we actually got.",
  fs=10.5, c=GRAY)
T(ax, 5, 5.14, "It's the hidden real-world cost of trading. The simulation assumes a small fixed",
  fs=10.5, c=GRAY)
T(ax, 5, 4.78, "cost; this pipeline measures the TRUE cost so we know if the edge survives it.",
  fs=10.5, c=GRAY)

box(ax, 0.8, 2.5, 8.4, 1.8, NAVY)
T(ax, 5, 3.95, "Two books, side by side", fs=13, c="white", b=True)
T(ax, 5, 3.45, "A frictionless simulation (assumes ~0.1% cost)  vs.  the live paper book (real",
  fs=10.5, c="#cfe0f3")
T(ax, 5, 3.09, "fills & costs). Comparing them answers the only question that matters before",
  fs=10.5, c="#cfe0f3")
T(ax, 5, 2.73, "real money: does the strategy still win once trading frictions are real?", fs=10.5,
  c="#cfe0f3", b=True)
footer(ax, "Daily cycle")
pages.append(fig)

# ══ PAGE 5 — A REAL RUN (screenshots) ════════════════════════════════════════════════
EX = ROOT / "examples"
_imgs = sorted(EX.glob("Screenshot*.png"))


def place(fig, img, cx, top, wfrac, ec=GRAY):
    """Place an image preserving aspect: cx/top in figure fraction, width = wfrac of page width."""
    h, w = img.shape[0], img.shape[1]
    hfrac = wfrac * 8.5 * (h / w) / 11.0
    a = fig.add_axes([cx - wfrac / 2, top - hfrac, wfrac, hfrac])
    a.imshow(img); a.set_xticks([]); a.set_yticks([])
    for sp in a.spines.values():
        sp.set_edgecolor(ec); sp.set_linewidth(1.2)
    return top - hfrac


if len(_imgs) >= 2:
    img1 = mpimg.imread(_imgs[0])   # terminal: dry-run then live
    img2 = mpimg.imread(_imgs[1])   # Alpaca paper Orders page
    fig, ax = _fig()
    header(ax, "PROOF · SEEN IN PRACTICE", "A real run, end to end")

    T(ax, 0.6, 11.0, "1.  Preview (dry-run), then submit for real", fs=13, c=NAVY, b=True, ha="left")
    T(ax, 0.6, 10.62, "Top command = a dry-run: it prints the plan and sends NOTHING. Bottom = the same",
      fs=9.3, c=GRAY, ha="left")
    T(ax, 0.6, 10.32, "command with --live, which submits the 3 limit-on-open orders to the paper broker.",
      fs=9.3, c=GRAY, ha="left")
    place(fig, img1, 0.5, 0.775, 0.86)

    T(ax, 0.6, 7.75, "2.  The orders land in the (paper) brokerage account", fs=13, c=NAVY, b=True, ha="left")
    T(ax, 0.6, 7.37, "Alpaca shows all three orders ACCEPTED and queued for the next open (note the blue",
      fs=9.3, c=GRAY, ha="left")
    T(ax, 0.6, 7.07, '"no real money is being used" banner). These are the exact prices the model chose.',
      fs=9.3, c=GRAY, ha="left")
    place(fig, img2, 0.5, 0.515, 0.86)

    box(ax, 0.8, 1.65, 8.4, 1.45, "#e9f7ef")
    T(ax, 5, 2.82, "What this proves", fs=12.5, c=GREEN, b=True)
    T(ax, 5, 2.40, "The full loop works on real market infrastructure — the model's picks became",
      fs=10, c="#1e6b3a")
    T(ax, 5, 2.07, "priced orders that a brokerage accepted — while every dollar stays simulated.",
      fs=10, c="#1e6b3a")
    T(ax, 5, 1.74, "Real money would only follow after the checkpoints on the next page.", fs=10,
      c="#1e6b3a", b=True)
    footer(ax, "A real run")
    pages.append(fig)

# ══ PAGE 6 — TOWARD REAL MONEY ═══════════════════════════════════════════════════════
fig, ax = _fig()
header(ax, "NEXT STEPS", "What it would take to use real money")

# the bridge
box(ax, 0.7, 10.2, 2.2, 0.95, AMBER)
T(ax, 1.8, 10.85, "PAPER", fs=13, c="white", b=True)
T(ax, 1.8, 10.45, "where we are", fs=9, c="#ffe9cf")
arrow(ax, 3.0, 10.65, 7.0, 10.65, c=GRAY, lw=3)
box(ax, 7.1, 10.2, 2.2, 0.95, RED)
T(ax, 8.2, 10.85, "REAL", fs=13, c="white", b=True)
T(ax, 8.2, 10.45, "only if it earns it", fs=9, c="#ffd9d2")
T(ax, 5, 10.05, "cross the bridge only after every checkpoint below is met", fs=9.5, c=GRAY, it=True)

checks = [
    ("Prove it over time", "Run on paper for many months across calm AND turbulent markets — not just a lucky stretch."),
    ("Confirm costs don't kill it", "Real slippage must stay small enough that the live book still beats the benchmarks."),
    ("Start tiny", "Begin with an amount you could lose entirely; scale only after live results match paper."),
    ("Hard risk limits", "Set a maximum loss, position caps, and an automatic 'stop everything' rule in advance."),
    ("Know the real-world rules", "Taxes, account types, and brokerage regulations differ for real-money trading."),
]
y = 9.0
for i, (t, d) in enumerate(checks):
    yy = y - i * 1.12
    numdot(ax, 1.05, yy + 0.35, i + 1, NAVY, r=0.26)
    box(ax, 1.5, yy - 0.12, 7.8, 0.96, "white", ec=LIGHT, lw=1.5)
    T(ax, 1.75, yy + 0.5, t, fs=12, c=NAVY, b=True, ha="left")
    T(ax, 1.75, yy + 0.13, d, fs=9.6, c=GRAY, ha="left")

# caveat
box(ax, 0.8, 1.7, 8.4, 1.5, "#fbeae8")
T(ax, 5, 2.9, "Important", fs=12.5, c=RED, b=True)
T(ax, 5, 2.45, "This is a personal research tool, not financial advice. Simulated and past results",
  fs=10, c=RED)
T(ax, 5, 2.12, "do NOT guarantee future returns. Only risk money you can afford to lose, and",
  fs=10, c=RED)
T(ax, 5, 1.79 + 0.0, "consider speaking with a qualified financial professional first.", fs=10, c=RED)
footer(ax, "Toward real money")
pages.append(fig)

# ── write ─────────────────────────────────────────────────────────────────────────
OUT.parent.mkdir(parents=True, exist_ok=True)
import os
with PdfPages(OUT) as pdf:
    for i, f in enumerate(pages):
        if os.environ.get("INFOG_PNG"):
            f.savefig(f"/tmp/infog_{i+1}.png", dpi=90)
        pdf.savefig(f); plt.close(f)
print("wrote", OUT.relative_to(ROOT), f"({len(pages)} pages)")
