"""Unit tests for the pure OCC option-symbol helpers."""
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import options_symbols as osym


def test_to_occ_call_round_strike():
    assert osym.to_occ("AAPL", "2024-12-20", 150, "call") == "AAPL241220C00150000"


def test_to_occ_put_fractional_strike():
    assert osym.to_occ("SPY", date(2026, 1, 16), 7.5, "p") == "SPY260116P00007500"


def test_to_occ_right_aliases():
    a = osym.to_occ("QQQ", "2025-03-21", 400, "C")
    b = osym.to_occ("QQQ", "2025-03-21", 400, "call")
    assert a == b == "QQQ250321C00400000"


@pytest.mark.parametrize("bad", [
    ("", "2024-12-20", 150, "call"),       # empty underlying
    ("AAPL", "2024-12-20", 0, "call"),     # non-positive strike
    ("AAPL", "2024-12-20", 150, "x"),      # bad right
])
def test_to_occ_rejects_garbage(bad):
    with pytest.raises(ValueError):
        osym.to_occ(*bad)


def test_roundtrip():
    occ = osym.to_occ("AAPL", "2024-12-20", 150, "call")
    p = osym.parse_occ(occ)
    assert p["underlying"] == "AAPL"
    assert p["expiry"] == date(2024, 12, 20)
    assert p["strike"] == 150.0
    assert p["right"] == "call"
    assert p["multiplier"] == 100
    assert p["occ"] == occ


def test_parse_fractional_strike():
    p = osym.parse_occ("SPY260116P00007500")
    assert p["strike"] == 7.5
    assert p["right"] == "put"


def test_is_occ_distinguishes_equities():
    assert osym.is_occ("AAPL241220C00150000")
    assert not osym.is_occ("AAPL")
    assert not osym.is_occ("BRK.B")
    assert not osym.is_occ("")


def test_underlying_of():
    assert osym.underlying_of("AAPL241220C00150000") == "AAPL"
    assert osym.underlying_of("AAPL") == "AAPL"
    assert osym.underlying_of("spy") == "SPY"


def test_dte():
    occ = osym.to_occ("AAPL", "2024-12-20", 150, "call")
    assert osym.dte(occ, asof=date(2024, 12, 1)) == 19
    assert osym.dte("2024-12-20", asof=date(2024, 12, 20)) == 0
    assert osym.dte(date(2024, 12, 20), asof=date(2024, 12, 25)) == -5


def test_occ_label():
    assert osym.occ_label("AAPL241220C00150000") == "AAPL 2024-12-20 150C"
    assert osym.occ_label("SPY260116P00007500") == "SPY 2026-01-16 7.5P"
    assert osym.occ_label("AAPL") == "AAPL"
