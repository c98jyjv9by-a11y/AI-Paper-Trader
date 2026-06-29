"""
options_symbols.py — pure OCC option-symbol helpers (no I/O, no deps beyond stdlib).

Alpaca options use the OCC contract symbol WITHOUT spaces:

    <UNDERLYING><YYMMDD><C|P><STRIKE*1000, zero-padded to 8 digits>

    AAPL  2024-12-20  call  150     -> "AAPL241220C00150000"
    SPY   2026-01-16  put   7.5     -> "SPY260116P00007500"

These functions are the single source of truth for building/parsing that string so
every layer (targets, orders, ledger, reports) agrees on contract identity. They are
deliberately pure and side-effect free — unit-tested without a broker.
"""
from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any, Dict, Optional, Union

_OCC_RE = re.compile(r"^(?P<u>[A-Z][A-Z0-9]*?)(?P<d>\d{6})(?P<cp>[CP])(?P<k>\d{8})$")
_RIGHT = {"c": "call", "p": "put", "call": "call", "put": "put"}


def _to_date(d: Union[str, date, datetime]) -> date:
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, date):
        return d
    return date.fromisoformat(str(d)[:10])


def to_occ(underlying: str, expiry: Union[str, date, datetime], strike: float,
           right: str) -> str:
    """Build an OCC contract symbol. `right` accepts call/put/c/p (any case)."""
    u = str(underlying).strip().upper()
    if not u or not u[0].isalpha():
        raise ValueError(f"bad underlying {underlying!r}")
    r = _RIGHT.get(str(right).strip().lower())
    if r is None:
        raise ValueError(f"bad right {right!r} (want call/put/c/p)")
    exp = _to_date(expiry)
    k = int(round(float(strike) * 1000))
    if k <= 0:
        raise ValueError(f"bad strike {strike!r}")
    return f"{u}{exp:%y%m%d}{r[0].upper()}{k:08d}"


def is_occ(s: str) -> bool:
    """True if `s` looks like an OCC option contract symbol (vs a bare equity ticker)."""
    return bool(_OCC_RE.match(str(s).strip().upper()))


def parse_occ(occ: str) -> Dict[str, Any]:
    """Parse an OCC symbol into its parts. Returns
    {underlying, expiry (date), strike (float), right ('call'|'put'), multiplier (100), occ}."""
    m = _OCC_RE.match(str(occ).strip().upper())
    if not m:
        raise ValueError(f"not an OCC option symbol: {occ!r}")
    d = m.group("d")
    expiry = date(2000 + int(d[0:2]), int(d[2:4]), int(d[4:6]))
    return {
        "underlying": m.group("u"),
        "expiry": expiry,
        "strike": int(m.group("k")) / 1000.0,
        "right": "call" if m.group("cp") == "C" else "put",
        "multiplier": 100,
        "occ": m.group(0),
    }


def underlying_of(occ: str) -> str:
    """The underlying ticker for an OCC symbol (or the symbol itself if it's a bare equity)."""
    return parse_occ(occ)["underlying"] if is_occ(occ) else str(occ).strip().upper()


def dte(occ_or_expiry: Union[str, date, datetime], asof: Optional[date] = None) -> int:
    """Calendar days from `asof` (default today) to expiry. Accepts an OCC symbol or a date."""
    asof = asof or date.today()
    exp = parse_occ(occ_or_expiry)["expiry"] if is_occ(str(occ_or_expiry)) else _to_date(occ_or_expiry)
    return (exp - asof).days


def occ_label(occ: str) -> str:
    """Human display, e.g. 'AAPL 2024-12-20 150C'. Bare equities pass through unchanged."""
    if not is_occ(occ):
        return str(occ)
    p = parse_occ(occ)
    strike = f"{p['strike']:g}"
    return f"{p['underlying']} {p['expiry'].isoformat()} {strike}{p['right'][0].upper()}"
