"""Per-account ORDER HISTORY + P&L report, combined for every broker account into ONE PDF.

For each Alpaca paper account it pulls the LIVE broker state and renders:
  • a P&L summary (equity / cash / starting; total, unrealized, and realized-estimate P&L),
  • the current positions with per-name unrealized P&L,
  • the full order history submitted to Alpaca (time, side, symbol, qty, status, fill price, value),
paginated as needed. A cover page rolls every account's P&L into one table.

P&L sourcing (broker = truth):
  • unrealized $ per position = (current_price - avg_entry) * qty   (% = Alpaca unrealized_plpc),
  • total P&L = equity - starting_value (manifest); realized P&L ≈ total - Σ unrealized
    (exact for a paper account funded once with no deposits/withdrawals).

    python run.py order-history [--accounts a b c] [--status all|closed|open] [--end YYYY-MM-DD] [--out FILE]
"""
import glob
import json
import textwrap
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["text.parse_math"] = False     # treat '$' / '%' literally everywhere (money strings)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from broker_adapter import AlpacaPaper
from eod_accounts import BLURBS, DEFAULT_ACCOUNTS, _blurb, _money, _pct

ROOT = Path(__file__).resolve().parent.parent
GREEN, RED, GREY = "#1a7f37", "#c0392b", "#777"
ORDERS_PER_PAGE = 34          # order rows per page (+ header + TOTAL row); wraps to more pages beyond this


_CT = ZoneInfo("America/Chicago")
_UTC = ZoneInfo("UTC")


def _ts(s):
    """ISO (UTC) timestamp -> 'MM-DD HH:MM' in Chicago Central time, or '—'."""
    if not s:
        return "—"
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        dt = (dt.replace(tzinfo=_UTC) if dt.tzinfo is None else dt).astimezone(_CT)
        return dt.strftime("%m-%d %H:%M")
    except Exception:
        return s[:16] if len(s) >= 16 else "—"


def _annotate_trade_pnl(orders, price_now=None):
    """Per-order P&L via running AVERAGE-COST accounting (matches Alpaca's avg_entry_price). Walks FILLED
    orders oldest->newest, maintaining {qty, cost} per symbol:
      • a SELL realizes (fill_px - avg_entry) x qty -> `rlz`,
      • a BUY of a STILL-HELD symbol marks to market (current_px - fill_px) x qty -> `unrlz`
        (a BUY of a name no longer held gets no `unrlz` — its outcome shows on the SELL rows).
    `ret` is the single return that pairs with whichever applies (realized return for sells, unrealized
    return for held buys). Annotates each order dict in place with `rlz` / `unrlz` / `ret` (None when N/A).
    `price_now` = {symbol: current price} for currently-held names. Accurate when the full opening history
    is within the pulled window (true for these young books)."""
    price_now = price_now or {}
    books = {}
    for o in orders:
        o["rlz"] = o["unrlz"] = o["ret"] = None
    # Any order with a filled qty + price counts — INCLUDING partial fills that ended 'expired'/'canceled'
    # (filled_qty is the actually-executed share count; realize on that, not on the terminal status).
    fills = [o for o in orders if o.get("fill_price") and o.get("filled_qty")]
    for o in sorted(fills, key=lambda x: (x.get("filled_at") or x.get("submitted_at") or "")):
        sym, q, px = o["symbol"], o["filled_qty"], o["fill_price"]
        b = books.setdefault(sym, {"qty": 0.0, "cost": 0.0})
        if (o.get("side") or "").lower() == "buy":
            b["qty"] += q; b["cost"] += q * px
            cur = price_now.get(sym)
            if cur:                                            # mark the buy to market only if still held
                o["unrlz"] = (cur - px) * q
                o["ret"] = (cur / px - 1) if px > 0 else None
        else:                                                  # sell -> realize vs running average cost
            avg = (b["cost"] / b["qty"]) if b["qty"] > 1e-9 else px
            o["rlz"] = (px - avg) * q
            o["ret"] = (px / avg - 1) if avg > 0 else None
            b["qty"] -= q; b["cost"] -= avg * q
            if b["qty"] <= 1e-9:                               # flat (or rounding) -> reset the book
                b["qty"], b["cost"] = 0.0, 0.0
    return orders


# Overlay sleeves are identified by symbol (excluded from the model decision, managed standalone).
_OVERLAY_REASON = {"TQQQ": ("rebound overlay buy", "rebound 1-day exit"),
                   "SQQQ": ("hedge overlay buy", "hedge exit")}
# Per-strategy (buy_reason, sell_reason) — the RULE that governs that order, by the account's target_mode.
_KIND_REASON = {
    "model_v4":          ("model entry (gate/persist)", "model exit (stop/rotate/hold)"),
    "score_gate_rampup": ("ramp-up buy (score>0.90)",   "model exit (stop/rotate/hold)"),
    "score_rebalance":   ("rebalance add (top-N score)", "rebalance drop (out of book)"),
    "zscore_reversal":   ("z-reversal entry (low-z)",    "z-reversal rebalance / to-cash"),
}


def _reason(side, sym, kind):
    """Brief GOVERNING-RULE label for an order, derived from the account strategy + side + symbol.
    Alpaca/plan files store no per-order reason, but each book is a deterministic rule, so the rule
    that produced a given buy/sell is well-defined. Overlay sleeves are flagged by symbol."""
    is_buy = (side or "").lower() == "buy"
    if sym in _OVERLAY_REASON:
        return _OVERLAY_REASON[sym][0 if is_buy else 1]
    b, s = _KIND_REASON.get(kind, ("buy", "sell"))
    return b if is_buy else s


def _collect(name, today, status="all", limit=500):
    """LIVE broker pull for one account: account, positions (+unrealized $), full order history, P&L."""
    try:
        cli = AlpacaPaper(account=name)
        a = cli.account()
        eq, cash = float(a.get("equity") or 0.0), float(a.get("cash") or 0.0)
        pos = cli.positions() or []
        for p in pos:                                          # derive unrealized $ from the broker fields
            p["unrealized_pl"] = (p["price"] - p["avg_entry"]) * p["qty"]
            p["cost_basis"] = p["avg_entry"] * p["qty"]
        orders = _annotate_trade_pnl(cli.orders(status=status, limit=limit) or [],   # newest-first; +per-trade P&L
                                     price_now={p["ticker"]: p["price"] for p in pos})
        man = json.load(open(glob.glob(str(ROOT / "accounts" / name / "*.json"))[0]))
        start = float(man.get("starting_value") or eq)
        unreal = sum(p["unrealized_pl"] for p in pos)
        total = eq - start
        return {"name": name, "eq": eq, "cash": cash, "start": start, "pos": pos, "orders": orders,
                "kind": (man.get("target_mode") or {}).get("kind"),
                "unreal": unreal, "total_pnl": total, "realized_est": total - unreal,
                "tot_ret": (eq / start - 1 if start else 0.0), "err": None}
    except Exception as exc:
        return {"name": name, "err": str(exc)[:80]}


# ── rendering ───────────────────────────────────────────────────────────────────
def _new_page(pdf, title, sub=None):
    fig = plt.figure(figsize=(11, 8.5))
    fig.suptitle(title, fontsize=13, weight="bold")
    if sub:
        fig.text(0.5, 0.945, sub, ha="center", fontsize=8.5, color="#555")
    return fig


def _table(fig, rect, cols, cells, colw, fontsize=7.5):
    ax = fig.add_axes(rect); ax.axis("off")
    if not cells:
        ax.text(0.0, 0.95, "— none —", fontsize=8, color=GREY, va="top")
        return ax, None
    t = ax.table(cellText=cells, colLabels=cols, colWidths=colw, loc="upper center", cellLoc="center")
    t.auto_set_font_size(False); t.set_fontsize(fontsize); t.scale(1, 1.4)
    for j in range(len(cols)):
        t[0, j].set_facecolor("#34495e"); t[0, j].set_text_props(color="white", weight="bold")
    return ax, t


def _render_account(pdf, d):
    name = d["name"]
    label, blurb = _blurb(name)
    title = "%s  —  %s" % (name, label)

    # ── broker error -> a single explanatory page (e.g. placeholder/unset keys) ──
    if d.get("err"):
        fig = _new_page(pdf, title)
        ax = fig.add_axes([0.06, 0.1, 0.88, 0.78]); ax.axis("off")
        ax.text(0.0, 1.0, "Broker unavailable for this account.", fontsize=11, weight="bold",
                color=RED, va="top")
        ax.text(0.0, 0.93, textwrap.fill("Alpaca call failed: %s" % d["err"], 90), fontsize=9,
                color="#333", va="top")
        ax.text(0.0, 0.80, textwrap.fill("This usually means the account's API keys are not set in .env "
                "(several research books ship with placeholder keys). Set real Alpaca paper keys to "
                "populate its order history and P&L.", 95), fontsize=8.5, color=GREY, va="top")
        pdf.savefig(fig); plt.close(fig)
        return

    # ── page 1: P&L summary + positions ──
    fig = _new_page(pdf, title)
    # P&L summary band
    ax = fig.add_axes([0.06, 0.74, 0.88, 0.16]); ax.axis("off")
    pnl_color = GREEN if d["total_pnl"] >= 0 else RED
    line1 = ("Equity %s    Cash %s    Starting %s    Positions %d    Orders %d"
             % (_money(d["eq"]), _money(d["cash"]), _money(d["start"]), len(d["pos"]), len(d["orders"])))
    ax.text(0.0, 1.0, line1, fontsize=9.5, family="monospace", va="top")
    ax.text(0.0, 0.60, "Total P&L  %s (%s)" % (_money(d["total_pnl"]), _pct(d["tot_ret"])),
            fontsize=11, weight="bold", color=pnl_color, va="top")
    ax.text(0.34, 0.60, "Unrealized  %s" % _money(d["unreal"]),
            fontsize=10, color=(GREEN if d["unreal"] >= 0 else RED), va="top")
    ax.text(0.60, 0.60, "Realized (est.)  %s" % _money(d["realized_est"]),
            fontsize=10, color=(GREEN if d["realized_est"] >= 0 else RED), va="top")
    ax.text(0.0, 0.18, textwrap.fill(blurb, 120), fontsize=7.5, color="#444", va="top")

    # positions table — gets the rest of page 1 (holds up to ~24 rows comfortably; combo20 has 20)
    fig.text(0.06, 0.70, "Open positions (%d)" % len(d["pos"]), fontsize=10, weight="bold")
    pcols = ["Symbol", "Qty", "Avg entry", "Price", "Mkt value", "Cost", "Unreal $", "Unreal %"]
    psorted = sorted(d["pos"], key=lambda x: -x["market_value"])
    pcells = [[p["ticker"], "%g" % p["qty"], "$%.2f" % p["avg_entry"], "$%.2f" % p["price"],
               _money(p["market_value"]), _money(p["cost_basis"]), _money(p["unrealized_pl"]),
               _pct(p["unrealized_plpc"])] for p in psorted]
    praw = [10, 7, 10, 9, 11, 10, 10, 9]
    _, pt = _table(fig, [0.06, 0.05, 0.88, 0.62], pcols, pcells, [w / sum(praw) for w in praw])
    if pt is not None:
        for i, p in enumerate(psorted):
            for j in (6, 7):
                pt[i + 1, j].set_text_props(color=(GREEN if p["unrealized_pl"] >= 0 else RED), weight="bold")
    pdf.savefig(fig); plt.close(fig)

    # ── order history — its own page(s), paginated; never shares a page with positions ──
    orders = d["orders"]
    kind = d.get("kind")
    ocols = ["Submitted", "Filled", "Side", "Symbol", "FillQty", "Fill px", "Value", "Rlz $", "Unrlz $", "Ret %", "Status", "Reason"]
    oraw = [9, 9, 4, 6, 5, 7, 7, 7, 7, 6, 7, 14]
    ow = [w / sum(oraw) for w in oraw]
    realized_sum = sum(o["rlz"] for o in orders if o.get("rlz") is not None)
    unrlz_sum = sum(o["unrlz"] for o in orders if o.get("unrlz") is not None)
    value_sum = sum(o["filled_qty"] * o["fill_price"] for o in orders
                    if o.get("fill_price") and o.get("filled_qty"))
    # account-wide TOTAL row (shown atop every page of this history): gross filled value + Σ Rlz/Unrlz
    total_row = ["TOTAL", "", "", "", "", "", _money(value_sum), _money(realized_sum), _money(unrlz_sum), "", "", ""]

    def _orow(o):
        fp = o.get("fill_price")
        val = (o["filled_qty"] * fp) if (fp and o["filled_qty"]) else None
        rlz, unrlz, ret = o.get("rlz"), o.get("unrlz"), o.get("ret")
        return [_ts(o.get("submitted_at")), _ts(o.get("filled_at")), (o.get("side") or "").upper(),
                o.get("symbol", ""), "%g" % o["filled_qty"], ("$%.2f" % fp) if fp else "—",
                _money(val) if val is not None else "—",
                _money(rlz) if rlz is not None else "—",
                _money(unrlz) if unrlz is not None else "—",
                _pct(ret) if ret is not None else "—",
                o.get("status", ""), _reason(o.get("side"), o.get("symbol", ""), kind)]

    def _color_orders(tbl, chunk, offset):                   # `offset` = table row of the first order
        # style the TOTAL header-data row (always at table row 1) once
        for j in range(len(ocols)):
            tbl[1, j].set_facecolor("#dfe6e9"); tbl[1, j].set_text_props(weight="bold")
        tbl[1, 7].set_text_props(color=(GREEN if realized_sum >= 0 else RED), weight="bold")
        tbl[1, 8].set_text_props(color=(GREEN if unrlz_sum >= 0 else RED), weight="bold")
        for i, o in enumerate(chunk):
            r = i + offset
            side = (o.get("side") or "").upper()
            tbl[r, 2].set_text_props(color=(GREEN if side == "BUY" else RED), weight="bold")
            if o.get("rlz") is not None:                       # realized SELL
                tbl[r, 7].set_text_props(color=(GREEN if o["rlz"] >= 0 else RED), weight="bold")
            if o.get("unrlz") is not None:                     # mark-to-market of a held BUY
                tbl[r, 8].set_text_props(color=(GREEN if o["unrlz"] >= 0 else RED), weight="bold")
            if o.get("ret") is not None:
                tbl[r, 9].set_text_props(color=(GREEN if o["ret"] >= 0 else RED), weight="bold")
            if o.get("status") != "filled":
                tbl[r, 10].set_text_props(color=GREY, style="italic")
            tbl[r, 11].set_text_props(color="#555", style="italic")

    rest, page, npages = orders, 1, max(1, (len(orders) + ORDERS_PER_PAGE - 1) // ORDERS_PER_PAGE)
    while rest or page == 1:                                  # always emit at least one (possibly empty) page
        chunk, rest = rest[:ORDERS_PER_PAGE], rest[ORDERS_PER_PAGE:]
        sub = "order history (newest first)" + ("" if npages == 1 else " — page %d/%d" % (page, npages))
        fig = _new_page(pdf, title, sub=sub)
        cells = ([total_row] + [_orow(o) for o in chunk]) if orders else []   # TOTAL row pinned at the top
        _, ot = _table(fig, [0.03, 0.05, 0.94, 0.84], ocols, cells, ow, fontsize=6.0)
        if ot is not None:
            _color_orders(ot, chunk, offset=2)               # order rows start after header(0)+TOTAL(1)
        fig.text(0.03, 0.92, "TOTAL row = account-wide gross filled Value + Σ Rlz/Unrlz.  Rlz/Unrlz = realized "
                 "on SELLs / held BUYs marked to price; Ret %% pairs with whichever applies.  Reason = the rule "
                 "that governs the order (by strategy + side; overlays by symbol).  Times in CT.",
                 fontsize=7, color="#555")
        pdf.savefig(fig); plt.close(fig)
        if not rest:
            break
        page += 1


def _render_cover(pdf, data, accts, today):
    fig = plt.figure(figsize=(11, 8.5))
    fig.suptitle("Account Order History & P&L — all accounts   %s" % today, fontsize=14, weight="bold")
    ax = fig.add_axes([0.05, 0.30, 0.90, 0.55]); ax.axis("off")
    cols = ["Account", "Equity", "Cash", "Starting", "Total P&L", "Total %", "Unreal $", "Realized(est)", "Pos", "Orders"]
    cells, ok = [], []
    for n in accts:
        d = data[n]
        if d.get("err"):
            cells.append([n, "—", "—", "—", "ERR", "—", "—", "—", "—", "—"])
            continue
        ok.append(d)
        cells.append([n, _money(d["eq"]), _money(d["cash"]), _money(d["start"]), _money(d["total_pnl"]),
                      _pct(d["tot_ret"]), _money(d["unreal"]), _money(d["realized_est"]),
                      str(len(d["pos"])), str(len(d["orders"]))])
    if ok:
        agg = {k: sum(d[k] for d in ok) for k in ("eq", "cash", "start", "total_pnl", "unreal", "realized_est")}
        cells.append(["TOTAL", _money(agg["eq"]), _money(agg["cash"]), _money(agg["start"]),
                      _money(agg["total_pnl"]), _pct(agg["eq"] / agg["start"] - 1 if agg["start"] else 0.0),
                      _money(agg["unreal"]), _money(agg["realized_est"]),
                      str(sum(len(d["pos"]) for d in ok)), str(sum(len(d["orders"]) for d in ok))])
    raw = [16, 11, 10, 10, 11, 8, 10, 12, 6, 8]
    t = ax.table(cellText=cells, colLabels=cols, colWidths=[w / sum(raw) for w in raw],
                 loc="upper center", cellLoc="center")
    t.auto_set_font_size(False); t.set_fontsize(8); t.scale(1, 1.5)
    for j in range(len(cols)):
        t[0, j].set_facecolor("#34495e"); t[0, j].set_text_props(color="white", weight="bold")
    for i, n in enumerate(accts):
        d = data[n]
        if d.get("err"):
            t[i + 1, 4].set_text_props(color=RED, weight="bold")
            continue
        for j, v in [(4, d["total_pnl"]), (5, d["tot_ret"]), (6, d["unreal"]), (7, d["realized_est"])]:
            t[i + 1, j].set_text_props(color=(GREEN if v >= 0 else RED), weight="bold")
    if ok:                                                    # shade + bold the TOTAL row
        tr = len(accts) + 1
        for j in range(len(cols)):
            t[tr, j].set_facecolor("#dfe6e9"); t[tr, j].set_text_props(weight="bold")
    fig.text(0.05, 0.24, "Total P&L = equity - starting value.  Unrealized = Σ (price - avg entry) x qty over open "
             "positions.  Realized (est.) = Total - Unrealized (exact for a once-funded paper account).",
             fontsize=7.5, color="#555", wrap=True)
    fig.text(0.05, 0.20, "ERR rows = the account's Alpaca keys are unset/placeholder; see its page for detail.",
             fontsize=7.5, color="#555")
    pdf.savefig(fig); plt.close(fig)


def run(accounts=None, end=None, out=None, status="all", limit=500):
    today = end or date.today().isoformat()
    accts = accounts or DEFAULT_ACCOUNTS
    data = {n: _collect(n, today, status=status, limit=limit) for n in accts}
    out = Path(out) if out else ROOT / "reports" / f"account_orders_{today}.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(out) as pdf:
        _render_cover(pdf, data, accts, today)
        for n in accts:
            _render_account(pdf, data[n])
    return {"pdf": str(out), "data": data}


if __name__ == "__main__":
    print(run()["pdf"])
