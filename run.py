#!/usr/bin/env python
"""
Unified entry point for the AI Paper Trader.

    python run.py backtest            --start 2021-06-12 --end 2026-06-12
    python run.py experiments         --start 2021-06-12 --end 2026-06-12
    python run.py ticker-experiments  --start 2021-06-12 --end 2026-06-12
    python run.py calibrate           --start 2021-06-12 --end 2026-06-12
    python run.py agent               # LIVE daily paper-trading agent

Run `python run.py -h` (or `<command> -h`) for details.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from cli import main

if __name__ == "__main__":
    main()
