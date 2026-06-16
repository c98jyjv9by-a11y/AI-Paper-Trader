"""
context_providers.py — Pluggable information sources for the agent harness.

Each provider returns a per-day TEXT block injected into the agent's prompt, computed
strictly as-of that date (NO look-ahead). agent_backtest can enable any combination
(`--context macro,news`) so you can A/B which sources actually improve decisions.

Providers
  • macro    — market/sector regime from price data (VIX, SPY/QQQ vs MA, sector 20d,
               universe breadth). Key-free and fully point-in-time. WORKING.
  • news     — per-ticker headlines + sentiment (Finnhub, date-bounded). Needs
               FINNHUB_API_KEY; point-in-time-safe via from/to date params.
  • social   — Reddit/WSB mention volume + sentiment. STUB: historical point-in-time
               data is hard (Pushshift gone) — wire a feed or run forward-live.
  • analyst  — consensus ratings / price targets. STUB: historical PIT is paywalled —
               wire a vendor or run forward-live.

The look-ahead contract: block(day, ...) may use data with timestamp <= `day` only.
"""
from __future__ import annotations

import os
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


def _env_key(name: str) -> Optional[str]:
    """Env var, falling back to the gitignored repo .env (KEY=VALUE)."""
    v = os.environ.get(name)
    if v:
        return v
    env = Path(__file__).parent.parent / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            if line.startswith(f"{name}=") and not line.startswith("#"):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


class ContextProvider:
    name = "base"

    def prepare(self, universe: List[str], start: date, end: date, close: pd.DataFrame) -> None:
        """Prefetch any data once before the day loop. `close` = universe close panel."""

    def block(self, day: date, universe: List[str], holdings: List[str]) -> str:
        """Return a text block describing this source as-of `day` (data <= day only)."""
        return ""


# ── Macro / sector regime (key-free, fully point-in-time) ─────────────────────────
class MacroProvider(ContextProvider):
    name = "macro"
    SECTORS = {"XLK": "Tech", "XLF": "Financials", "XLE": "Energy",
               "XLV": "Healthcare", "XLY": "ConsDisc", "XLI": "Industrials"}

    def prepare(self, universe, start, end, close):
        self._uni = close
        from backtest import fetch_backtest_data
        extras = ["^VIX"] + list(self.SECTORS)
        try:
            self._x = fetch_backtest_data(extras, start, end)["Close"]
        except Exception:
            self._x = pd.DataFrame()

    def block(self, day, universe, holdings):
        ts = pd.Timestamp(day)
        uc = self._uni.loc[:ts] if self._uni is not None else pd.DataFrame()
        x = self._x.loc[:ts] if not self._x.empty else pd.DataFrame()
        L = ["MARKET / MACRO CONTEXT (as of close — no look-ahead):"]
        for sym in ("SPY", "QQQ"):
            if sym in uc.columns:
                s = uc[sym].dropna()
                if len(s) >= 50:
                    ma = s.iloc[-50:].mean()
                    L.append(f"  {sym} {s.iloc[-1]:.0f} {'ABOVE' if s.iloc[-1] > ma else 'BELOW'} "
                             f"50d MA ({s.iloc[-1]/ma - 1:+.1%})")
        if "^VIX" in x.columns:
            v = x["^VIX"].dropna()
            if len(v) >= 21:
                L.append(f"  VIX {v.iloc[-1]:.1f} (20d chg {v.iloc[-1]/v.iloc[-21] - 1:+.0%})")
        secs = []
        for sym, nm in self.SECTORS.items():
            if sym in x.columns:
                s = x[sym].dropna()
                if len(s) >= 21:
                    secs.append((nm, s.iloc[-1] / s.iloc[-21] - 1))
        if secs:
            secs.sort(key=lambda kv: -kv[1])
            L.append("  Sector 20d: " + ", ".join(f"{n} {r:+.1%}" for n, r in secs))
        above = tot = 0
        for t in universe:
            if t in uc.columns:
                s = uc[t].dropna()
                if len(s) >= 50:
                    tot += 1
                    above += int(s.iloc[-1] > s.iloc[-50:].mean())
        if tot:
            L.append(f"  Breadth: {above}/{tot} universe names above their 50d MA ({above/tot:.0%})")
        return "\n".join(L)


# ── News + sentiment (Finnhub, date-bounded → point-in-time-safe) ─────────────────
class NewsProvider(ContextProvider):
    name = "news"

    def __init__(self, lookback_days: int = 3, max_names: int = 8):
        self.lookback_days = lookback_days
        self.max_names = max_names
        self.key = _env_key("FINNHUB_API_KEY")

    def block(self, day, universe, holdings):
        if not self.key:
            return "NEWS: (no FINNHUB_API_KEY configured — skipped)"
        try:
            import requests
        except ImportError:
            return "NEWS: (requests not installed — skipped)"
        names = list(dict.fromkeys(list(holdings) + universe))[: self.max_names]
        frm = (day - timedelta(days=self.lookback_days)).isoformat()
        to = day.isoformat()                       # inclusive, <= decision date (no look-ahead)
        out = ["NEWS (last few days, per name):"]
        for t in names:
            try:
                r = requests.get("https://finnhub.io/api/v1/company-news",
                                 params={"symbol": t, "from": frm, "to": to, "token": self.key},
                                 timeout=10)
                arts = r.json() if r.ok else []
            except Exception:
                arts = []
            if arts:
                heads = "; ".join(a.get("headline", "")[:90] for a in arts[:2])
                out.append(f"  {t}: {heads}")
        return "\n".join(out) if len(out) > 1 else "NEWS: (no headlines in window)"


# ── Stubs: real point-in-time history needs a feed or forward-live capture ─────────
class SocialProvider(ContextProvider):
    name = "social"

    def block(self, day, universe, holdings):
        return ("SOCIAL/REDDIT HYPE: (stub — no point-in-time feed configured. Wire a "
                "mention/sentiment source or run forward-live to populate this.)")


class AnalystProvider(ContextProvider):
    name = "analyst"

    def block(self, day, universe, holdings):
        return ("ANALYST RATINGS/TARGETS: (stub — historical point-in-time is paywalled. "
                "Wire a vendor or run forward-live to populate this.)")


_REGISTRY = {p.name: p for p in [MacroProvider, NewsProvider, SocialProvider, AnalystProvider]}


def build_providers(names: List[str], universe: List[str], start: date, end: date,
                    close: pd.DataFrame) -> List[ContextProvider]:
    """Instantiate + prepare the named providers. Unknown names raise."""
    providers = []
    for n in names:
        n = n.strip().lower()
        if not n or n == "none":
            continue
        if n not in _REGISTRY:
            raise ValueError(f"Unknown context provider '{n}'. Known: {', '.join(_REGISTRY)}")
        p = _REGISTRY[n]()
        p.prepare(universe, start, end, close)
        providers.append(p)
    return providers
