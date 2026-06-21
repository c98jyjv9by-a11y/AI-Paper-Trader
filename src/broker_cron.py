"""
broker_cron.py — cron-ready wrapper around the daily broker session.

Runs ONE phase of the trading day, self-guards on the market calendar (via the Alpaca clock),
and appends a timestamped line to accounts/<name>/broker/cron.log. Designed to be dropped into
crontab with three fixed ET times (or one --phase auto job that self-selects).

Phases:
  open    build the reconcile-to-target plan and SUBMIT it (limit orders, data-driven collars).
          Skipped (exit 0) if it isn't a valid pre-open window (weekend/holiday/market open).
  retry   cancel anything still unfilled and resubmit at the wider retry collar; log skips.
          Skipped if the market isn't open.
  close   pull real fills, log realized slippage, sync the ledger from the broker (source of
          truth), and render the EOD PDF. Always safe to run (read + local sync).
  auto    pick open / retry / close from the current ET clock.

SAFETY: submission stays inert unless --live is passed (which sets BROKER_ADAPTER_ALLOW_SUBMIT=yes
for this process). Without --live every phase is a dry run. Keys are read from .env.

Examples (crontab, times in the server's local TZ — set CRON_TZ or use ET below):
    # m h  dom mon dow  command   (assuming the box is on US/Eastern)
    CRON_TZ=America/New_York
    25 9   * * 1-5  cd /path/ai-paper-trader && python src/broker_cron.py --phase open  --account alpaca_tracker --live >> /tmp/mv4.log 2>&1
    5  10  * * 1-5  cd /path/ai-paper-trader && python src/broker_cron.py --phase retry --account alpaca_tracker --live >> /tmp/mv4.log 2>&1
    10 16  * * 1-5  cd /path/ai-paper-trader && python src/broker_cron.py --phase close --account alpaca_tracker        >> /tmp/mv4.log 2>&1

Single-job alternative (run every 15 min on weekdays; it self-selects + de-dupes per phase/day):
    */15 9-16 * * 1-5  cd /path/ai-paper-trader && python src/broker_cron.py --phase auto --account alpaca_tracker --live >> /tmp/mv4.log 2>&1
"""
from __future__ import annotations

import sys
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))
import broker_adapter as ba
import broker_sync as bs


def _log(name: str, msg: str) -> None:
    """Append a timestamped line to the account's cron log and echo to stdout (cron captures it)."""
    line = f"{datetime.now().isoformat(timespec='seconds')}  {msg}"
    print(line, flush=True)
    f = bs._broker_dir(name) / "cron.log"
    with f.open("a") as fh:
        fh.write(line + "\n")


def _already_done(name: str, phase: str, asof: str) -> bool:
    """For --phase auto: has this phase already run for this trading day? (idempotent re-runs)."""
    f = bs._broker_dir(name) / "cron.log"
    if not f.exists():
        return False
    tag = f"PHASE={phase} asof={asof} "
    return any(tag in ln and "OK" in ln for ln in f.read_text().splitlines())


def _pick_phase(clk: dict) -> str:
    """Self-select the phase from the ET clock: closed+open-imminent -> open; open -> retry;
    otherwise -> close (end-of-day sync). 'auto' callers de-dupe per phase/day via the log."""
    if clk.get("is_open"):
        return "retry"
    win = bs.submit_window(clk)
    return "open" if win["ok"] else "close"


def run_phase(name: str, phase: str, live: bool = False, prequeue: bool = False) -> int:
    """Run one phase. Returns a process exit code (0 ok/skip, 1 error)."""
    ba._load_env()
    if live:
        import os
        os.environ[ba.SUBMIT_ENV] = "yes"          # explicit opt-in to live paper submission
    cli = ba.AlpacaPaper()
    clk = cli.clock()
    asof = clk.get("timestamp", bs._utcnow())[:10]

    if phase == "auto":
        phase = _pick_phase(clk)
        if _already_done(name, phase, asof):
            _log(name, f"PHASE={phase} asof={asof}  SKIP (already done today)")
            return 0

    mode = "LIVE" if live else "dry-run"
    try:
        if phase == "open":
            r = bs.submit_session(name, cli=cli, submit=live, prequeue=prequeue)
            if r.get("blocked"):
                _log(name, f"PHASE=open asof={asof}  SKIP — {r['reason']}")
                return 0
            _log(name, f"PHASE=open asof={asof}  OK ({mode}) — {r['n_orders']} orders, "
                       f"{r['submitted']} submitted")
            for o in r.get("orders", []):
                pl = o["_plan"]
                _log(name, f"    {o['side'].upper():4} {o['symbol']:6} qty {o['qty']:>5} "
                           f"limit ${o['limit_price']:<8.2f} collar {pl['collar']*100:.1f}% "
                           f"(tgt {pl['target']}/now {pl['current']})")

        elif phase == "retry":
            if not clk.get("is_open"):
                _log(name, f"PHASE=retry asof={asof}  SKIP — market not open")
                return 0
            r = bs.retry_unfilled(name, cli=cli)
            _log(name, f"PHASE=retry asof={asof}  OK ({mode}) — canceled {r['canceled']}, "
                       f"resubmitted {r['resubmitted']}, still unfilled {r['still_unfilled']}")

        elif phase == "close":
            r = bs.reconcile_session(name, cli=cli)
            _log(name, f"PHASE=close asof={asof}  OK — {r['fills']} fills, "
                       f"avg slippage {r['avg_slippage_bps']} bps, equity ${r['equity']:,.0f}, "
                       f"{r['positions']} positions")
            eod = subprocess.run([sys.executable, "run.py", "eod", "--account", name],
                                 cwd=str(ROOT), capture_output=True, text=True)
            _log(name, f"PHASE=close asof={asof}  EOD render {'OK' if eod.returncode == 0 else 'FAILED'}")
            if eod.returncode != 0:
                _log(name, f"    eod stderr: {eod.stderr.strip()[:300]}")
        else:
            _log(name, f"unknown phase '{phase}'")
            return 1
    except Exception as e:                          # never let cron see a stack trace silently
        _log(name, f"PHASE={phase} asof={asof}  ERROR — {type(e).__name__}: {e}")
        return 1
    return 0


def _cli(argv=None):
    p = argparse.ArgumentParser(description="Cron wrapper for the daily broker session")
    p.add_argument("--account", required=True)
    p.add_argument("--phase", required=True, choices=["open", "retry", "close", "auto"])
    p.add_argument("--live", action="store_true",
                   help="actually submit (sets BROKER_ADAPTER_ALLOW_SUBMIT=yes); omit for a dry run")
    p.add_argument("--prequeue", action="store_true",
                   help="allow submitting outside the pre-open window (weekend/holiday)")
    a = p.parse_args(argv)
    return run_phase(a.account, a.phase, live=a.live, prequeue=a.prequeue)


if __name__ == "__main__":
    sys.exit(_cli())
