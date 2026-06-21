"""
make_infographic_poster.py — ONE combined single-page infographic poster covering the whole
pipeline: model_v4 -> safe order building -> Alpaca PAPER submission -> daily cycle -> a real
run (screenshots) -> what real money would take. Non-technical.

Pure presentation (matplotlib). Output: reports/model_v4_infographic_poster.pdf
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch, Circle

ROOT = Path(__file__).parent
OUT = ROOT / "reports" / "model_v4_infographic_poster.pdf"
EX = ROOT / "examples"

NAVY = "#1f3a5f"; BLUE = "#2e86de"; TEAL = "#16a085"; GREEN = "#27ae60"
AMBER = "#e8901a"; RED = "#c0392b"; GRAY = "#5d6d7e"; LIGHT = "#eef2f7"; PAPER = "#f7f9fc"

W = 10.0
_imgs = sorted(EX.glob("Screenshot*.png"))
img1 = mpimg.imread(_imgs[0]) if _imgs else None
img2 = mpimg.imread(_imgs[1]) if len(_imgs) > 1 else None
imgH1 = 0.86 * W * (img1.shape[0] / img1.shape[1]) if img1 is not None else 0
imgH2 = 0.86 * W * (img2.shape[0] / img2.shape[1]) if img2 is not None else 0
H = 38.0 + imgH1 + imgH2          # base layout height + the two screenshot heights


def T(ax, x, y, s, fs=11, c=NAVY, b=False, ha="center", va="center", it=False):
    ax.text(x, y, s, fontsize=fs, color=c, ha=ha, va=va, parse_math=False,
            fontweight="bold" if b else "normal", fontstyle="italic" if it else "normal")


def box(ax, x, y, w, h, fc, ec="none", lw=0, r=0.12):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.02,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, mutation_aspect=1.0))


def chip(ax, x, y, w, h, title, lines, fc, tc="white", tfs=12, bfs=9.2):
    box(ax, x, y, w, h, fc)
    T(ax, x + w / 2, y + h - 0.32, title, fs=tfs, c=tc, b=True)
    for i, ln in enumerate(lines):
        T(ax, x + w / 2, y + h - 0.68 - i * 0.32, ln, fs=bfs, c=tc)


def numdot(ax, x, y, n, c, r=0.26):
    ax.add_patch(Circle((x, y), r, fc=c, ec="white", lw=1.5)); T(ax, x, y, str(n), fs=12, c="white", b=True)


def arrow(ax, x1, y1, x2, y2, c=GRAY, lw=2.2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=c, lw=lw, shrinkA=2, shrinkB=2))


def slabel(ax, y, title, c=BLUE):
    box(ax, 0.6, y - 0.06, 0.13, 0.52, c, r=0.04)
    T(ax, 0.95, y + 0.2, title, fs=15, c=NAVY, b=True, ha="left")


def place(fig, img, top, wfrac=0.86, ec=GRAY):
    h, w = img.shape[0], img.shape[1]
    hfrac = wfrac * W * (h / w) / H
    a = fig.add_axes([0.5 - wfrac / 2, top - hfrac, wfrac, hfrac])
    a.imshow(img); a.set_xticks([]); a.set_yticks([])
    for sp in a.spines.values():
        sp.set_edgecolor(ec); sp.set_linewidth(1.1)
    return (top - hfrac) * H          # bottom in y-units


fig = plt.figure(figsize=(W, H)); ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
ax.add_patch(FancyBboxPatch((0, 0), W, H, boxstyle="square,pad=0", fc=PAPER, ec="none"))

cy = H

# ── HEADER ───────────────────────────────────────────────────────────────────────────
box(ax, 0, cy - 3.0, W, 3.0, NAVY, r=0.0)
T(ax, 5, cy - 1.0, "How the model_v4 system works", fs=24, c="white", b=True)
T(ax, 5, cy - 1.72, "From a stock-picking model to simulated broker trades —", fs=12.5, c="#cfe0f3")
T(ax, 5, cy - 2.12, "and what it would take to use real money", fs=12.5, c="#cfe0f3")
box(ax, 3.05, cy - 2.78, 3.9, 0.56, AMBER)
T(ax, 5, cy - 2.5, "PAPER TRADING ONLY · no real capital at risk", fs=11, c="white", b=True)
cy -= 3.4

# ── JOURNEY ───────────────────────────────────────────────────────────────────────────
T(ax, 5, cy - 0.1, "The whole journey in five steps", fs=15, c=NAVY, b=True)
cy -= 0.6
steps = [(BLUE, "Rank", ["Score ~83 AI &", "chip stocks daily"]),
         (TEAL, "Choose", ["Pick the strongest", "+ a crash hedge"]),
         (GREEN, "Build", ["Turn picks into", "safe limit orders"]),
         (NAVY, "Submit", ["Send to the", "paper broker"]),
         (AMBER, "Measure", ["Record fills &", "real-world costs"])]
w = 1.62; gap = 0.25; x0 = (W - (5 * w + 4 * gap)) / 2
for i, (c, t, ls) in enumerate(steps):
    x = x0 + i * (w + gap)
    chip(ax, x, cy - 1.5, w, 1.5, t, ls, c, tfs=12, bfs=8.4)
    numdot(ax, x, cy, i + 1, c)
    if i < 4:
        arrow(ax, x + w + 0.02, cy - 0.75, x + w + gap - 0.02, cy - 0.75)
cy -= 1.9

# ── THE MODEL ─────────────────────────────────────────────────────────────────────────
slabel(ax, cy - 0.4, "1–2 · What the model decides", BLUE); cy -= 0.9
box(ax, 0.7, cy - 1.35, 4.3, 1.35, BLUE)
T(ax, 2.85, cy - 0.4, "~83 stocks scored 0–1", fs=12, c="white", b=True)
T(ax, 2.85, cy - 0.78, "AI · semiconductors · tech,", fs=9.3, c="#e8f1fb")
T(ax, 2.85, cy - 1.1, "every day, on momentum", fs=9.3, c="#e8f1fb")
arrow(ax, 5.15, cy - 0.67, 5.9, cy - 0.67, c=NAVY, lw=2.4)
box(ax, 6.0, cy - 1.2, 3.3, 1.05, TEAL)
T(ax, 7.65, cy - 0.48, "Buy the strongest", fs=11.5, c="white", b=True)
T(ax, 7.65, cy - 0.84, "above 0.70 (0.90 = add)", fs=9.2, c="#dff3ee")
cy -= 1.7
T(ax, 5, cy - 0.18, "Built-in risk brakes", fs=12.5, c=NAVY, b=True); cy -= 0.55
cards = [(GREEN, "Spread out", ["Even split, never", "more than ~75% in"]),
         (AMBER, "Vol governor", ["Invests less when", "markets get wild"]),
         (RED, "Stop-loss", ["Exits a holding", "that falls too far"])]
w = 2.9; gap = 0.3; x0 = (W - (3 * w + 2 * gap)) / 2
for i, (c, t, ls) in enumerate(cards):
    chip(ax, x0 + i * (w + gap), cy - 1.4, w, 1.4, t, ls, c, tfs=11.5, bfs=9)
cy -= 1.7
box(ax, 0.7, cy - 1.55, 8.6, 1.55, NAVY)
T(ax, 5, cy - 0.42, "The crash hedge — a shield, not a bet", fs=12.5, c="white", b=True)
T(ax, 5, cy - 0.83, "When the market jumps hard AND turbulence spikes (a classic 'pullback coming'", fs=9.6, c="#cfe0f3")
T(ax, 5, cy - 1.15, "warning), it buys a 1-day position that profits if semis drop — cushioning the book.", fs=9.6, c="#cfe0f3")
cy -= 1.95

# ── DECISION -> PAPER TRADE ───────────────────────────────────────────────────────────
slabel(ax, cy - 0.4, "3–4 · From a decision to a (paper) trade", TEAL); cy -= 0.95
flow = [(BLUE, "Decide at close", ["Model picks on the", "day's closing prices"]),
        (TEAL, "Build safe orders", ["Limit orders with a", "price 'collar' guardrail"]),
        (NAVY, "Send to broker", ["Alpaca paper: fake", "$100k, real market"])]
w = 2.9; gap = 0.3; x0 = (W - (3 * w + 2 * gap)) / 2
for i, (c, t, ls) in enumerate(flow):
    chip(ax, x0 + i * (w + gap), cy - 1.45, w, 1.45, t, ls, c)
    if i < 2:
        arrow(ax, x0 + (i + 1) * w + i * gap + 0.02, cy - 0.72,
              x0 + (i + 1) * (w + gap) - 0.02, cy - 0.72)
cy -= 1.75
box(ax, 0.7, cy - 1.5, 8.6, 1.5, LIGHT)
T(ax, 5, cy - 0.38, "The collar: a guardrail sized to each stock's normal swing", fs=12, c=NAVY, b=True)
box(ax, 1.5, cy - 1.18, 3.3, 0.62, GREEN); T(ax, 3.15, cy - 0.87, "Calm stock → tight (~1%)", fs=9.5, c="white", b=True)
box(ax, 5.2, cy - 1.18, 3.3, 0.62, AMBER); T(ax, 6.85, cy - 0.87, "Jumpy hedge → wide (~6%)", fs=9.5, c="white", b=True)
T(ax, 5, cy - 1.38, "If the open gaps past the collar, the order simply doesn't fill — we skip it.", fs=9, c=GRAY, it=True)
cy -= 1.7
box(ax, 0.7, cy - 1.5, 8.6, 1.5, NAVY)
T(ax, 5, cy - 0.36, "Safety rails (always on)", fs=12, c="white", b=True)
rails = ["PAPER ONLY — refuses any non-paper account", "SUBMIT OFF BY DEFAULT — must be armed each time",
         "EVERY ACTION LOGGED", "BROKER IS THE SOURCE OF TRUTH"]
for i, r in enumerate(rails):
    rx = 1.1 + (i % 2) * 4.5; ry = cy - 0.78 - (i // 2) * 0.4
    T(ax, rx, ry, "✓", fs=12, c=GREEN, b=True, ha="left"); T(ax, rx + 0.35, ry, r, fs=9, c="#e8f1fb", ha="left")
cy -= 1.9

# ── DAILY CYCLE ───────────────────────────────────────────────────────────────────────
slabel(ax, cy - 0.4, "The daily rhythm — automatic, every weekday", AMBER); cy -= 0.95
box(ax, 0.7, cy - 0.62, 8.6, 0.62, AMBER)
T(ax, 5, cy - 0.33, "SET-AND-FORGET:  a scheduler (cron) runs all three steps by itself, Mon–Fri — you just review the results",
  fs=9.2, c="white", b=True)
cy -= 1.45
ax.plot([1.4, 8.6], [cy, cy], color=GRAY, lw=3, zorder=1)
marks = [(2.0, BLUE, "Pre-open", "~9:25a ET", "SUBMIT", ["Send the day's", "orders"]),
         (5.0, TEAL, "Just after open", "~10:05a ET", "RETRY", ["Re-price unfilled", "once, else skip"]),
         (8.0, NAVY, "After close", "~4:10p ET", "RECONCILE", ["Record fills,", "measure slippage"])]
for x, c, when, tm, what, ls in marks:
    ax.add_patch(Circle((x, cy), 0.15, fc=c, ec="white", lw=2, zorder=3))
    T(ax, x, cy + 0.52, when, fs=9.0, c=GRAY, b=True)
    T(ax, x, cy + 0.27, tm, fs=8.6, c=c, b=True)
    arrow(ax, x, cy - 0.16, x, cy - 0.42, c=c, lw=1.8)
    chip(ax, x - 1.35, cy - 2.05, 2.7, 1.55, what, ls, c, tfs=12, bfs=9)
cy -= 2.45
box(ax, 0.7, cy - 0.95, 8.6, 0.95, LIGHT)
T(ax, 5, cy - 0.37, "'Slippage' = expected price − actual price (the hidden cost of trading).", fs=10, c=NAVY, b=True)
T(ax, 5, cy - 0.72, "We measure the TRUE cost to confirm the edge survives real-world frictions.", fs=9.4, c=GRAY)
cy -= 1.35

# ── PROOF (screenshots) ───────────────────────────────────────────────────────────────
slabel(ax, cy - 0.4, "Proof · a real run, end to end", GREEN); cy -= 0.95
if img1 is not None:
    T(ax, 0.7, cy - 0.05, "1.  Preview (dry-run, sends nothing) → then submit live", fs=11.5, c=NAVY, b=True, ha="left")
    cy = place(fig, img1, (cy - 0.45) / H) - 0.35
if img2 is not None:
    T(ax, 0.7, cy - 0.05, "2.  The orders land ACCEPTED in the paper brokerage account", fs=11.5, c=NAVY, b=True, ha="left")
    cy = place(fig, img2, (cy - 0.45) / H) - 0.4
box(ax, 0.7, cy - 1.15, 8.6, 1.15, "#e9f7ef")
T(ax, 5, cy - 0.4, "What this proves", fs=11.5, c=GREEN, b=True)
T(ax, 5, cy - 0.74, "The model's picks became priced orders a real brokerage accepted —", fs=9.5, c="#1e6b3a")
T(ax, 5, cy - 1.0, "while every dollar stays simulated. Real money only follows the checkpoints below.", fs=9.5, c="#1e6b3a", b=True)
cy -= 1.55

# ── TOWARD REAL MONEY ─────────────────────────────────────────────────────────────────
slabel(ax, cy - 0.4, "Next steps · what real money would take", RED); cy -= 1.05
box(ax, 0.7, cy - 0.85, 2.1, 0.85, AMBER); T(ax, 1.75, cy - 0.35, "PAPER", fs=12, c="white", b=True)
T(ax, 1.75, cy - 0.68, "where we are", fs=8.5, c="#ffe9cf")
arrow(ax, 2.95, cy - 0.42, 7.0, cy - 0.42, c=GRAY, lw=3)
box(ax, 7.2, cy - 0.85, 2.1, 0.85, RED); T(ax, 8.25, cy - 0.35, "REAL", fs=12, c="white", b=True)
T(ax, 8.25, cy - 0.68, "only if it earns it", fs=8.5, c="#ffd9d2")
cy -= 1.2
checks = [("Prove it over time", "Many months across calm AND turbulent markets — not a lucky stretch."),
          ("Confirm costs don't kill it", "Real slippage must stay small enough the live book still beats benchmarks."),
          ("Start tiny", "Begin with money you could lose entirely; scale only after live matches paper."),
          ("Hard risk limits", "Set a max loss, position caps, and a 'stop everything' rule in advance."),
          ("Know the real-world rules", "Taxes, account types, and brokerage regulations differ for real money.")]
for i, (t, d) in enumerate(checks):
    yy = cy - i * 0.86
    numdot(ax, 1.0, yy - 0.3, i + 1, NAVY, r=0.24)
    box(ax, 1.45, yy - 0.72, 7.85, 0.72, "white", ec=LIGHT, lw=1.3)
    T(ax, 1.7, yy - 0.27, t, fs=11, c=NAVY, b=True, ha="left")
    T(ax, 1.7, yy - 0.55, d, fs=8.8, c=GRAY, ha="left")
cy -= (5 * 0.86 + 0.15)
box(ax, 0.7, cy - 1.2, 8.6, 1.2, "#fbeae8")
T(ax, 5, cy - 0.36, "Important", fs=11.5, c=RED, b=True)
T(ax, 5, cy - 0.66, "A personal research tool, not financial advice. Simulated/past results don't", fs=9.2, c=RED)
T(ax, 5, cy - 0.94, "guarantee future returns. Only risk what you can afford to lose; consider a pro.", fs=9.2, c=RED)
cy -= 1.5

T(ax, 5, 0.3, "model_v4 paper-trading system  ·  research tool, not financial advice", fs=8, c=GRAY)

OUT.parent.mkdir(parents=True, exist_ok=True)
with PdfPages(OUT) as pdf:
    pdf.savefig(fig)
fig.savefig("/tmp/poster.png", dpi=70)
plt.close(fig)
print("wrote", OUT.relative_to(ROOT), f"(1 page, {H:.1f} in tall, end cursor y={cy:.2f})")
