"""status_check.py — one-shot, read-only ops dashboard for the live broker fleet.

`python run.py status`  (or `python src/status_check.py`). Prints, in one view:
  - each Alpaca broker account: key state (ok / placeholder / MISSING) + live equity + cash
  - launchd agents loaded (com.mv4.*)
  - the last line of each /tmp/mv4_*.log
  - git working-tree state + HEAD

Replaces the ad-hoc `grep .env` / `launchctl list | grep mv4` / per-account equity checks. No trading,
no writes; the only network is the read-only Alpaca account fetch (best-effort, per account)."""
import glob
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import broker_adapter as ba

PLACEHOLDERS = {"", "...", "xxx", "changeme", "placeholder", "your_key_here", "todo", "tbd"}
MODE_ABBR = {"model_v4": "model", "score_gate_rampup": "rampup",
             "score_rebalance": "rebal", "zscore_reversal": "z-rev"}


def _key_state(env_name: str) -> str:
    if not env_name:
        return "no-env"
    v = (os.environ.get(env_name) or "").strip()
    if not v:
        return "MISSING"
    if v.lower() in PLACEHOLDERS or len(v) < 12:
        return "placeholder"
    return "set"


def _broker_accounts():
    """(name, broker_keys, mode) for each account that has broker/ + a manifest with broker_keys."""
    try:
        from account import load_manifest
    except Exception:
        def load_manifest(_):
            return None
    out = []
    for d in sorted(p for p in (ROOT / "accounts").iterdir() if (p / "broker").is_dir()):
        m = load_manifest(d.name) or {}
        bk = m.get("broker_keys") or {}
        if not bk.get("key_env"):
            continue                                # e.g. the frictionless `tracker` sim — not Alpaca
        out.append((d.name, bk, (m.get("target_mode") or {}).get("kind", "?")))
    return out


def _equity(name):
    try:
        a = ba.AlpacaPaper(account=name).account() or {}
        return float(a.get("equity")), float(a.get("cash"))
    except Exception as e:
        return None, str(e).splitlines()[0][:46]


def _cmd(args) -> str:
    try:
        return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=15).stdout.strip()
    except Exception:
        return ""


def run() -> None:
    ba._load_env()
    print("\n=== BROKER FLEET STATUS ===  (read-only)\n")
    accts = _broker_accounts()
    print("%-20s %-7s %-18s %14s %14s" % ("account", "mode", "keys", "equity", "cash"))
    print("-" * 76)
    keyed = tot_eq = 0
    for name, bk, mode in accts:
        ks, ss = _key_state(bk.get("key_env")), _key_state(bk.get("secret_env"))
        keys = "ok" if ks == "set" and ss == "set" else f"id:{ks} sec:{ss}"
        if keys == "ok":
            keyed += 1
        eq, cash = _equity(name)
        if eq is None:
            print("%-20s %-7s %-18s %14s   %s" % (name, MODE_ABBR.get(mode, mode), keys, "—", cash))
        else:
            tot_eq += eq
            print("%-20s %-7s %-18s %14s %14s" % (name, MODE_ABBR.get(mode, mode), keys,
                                                  f"${eq:,.0f}", f"${cash:,.0f}"))
    print("-" * 76)
    print("%-20s %d accounts · %d fully-keyed · $%s total equity" % (
        "TOTAL", len(accts), keyed, f"{tot_eq:,.0f}"))

    print("\n=== launchd agents ===")
    mv4 = sorted(l.split()[-1] for l in _cmd(["launchctl", "list"]).splitlines() if "mv4" in l)
    print("  loaded:", ", ".join(mv4) or "(none — agents not bootstrapped)")

    print("\n=== last log line ===")
    logs = sorted(glob.glob("/tmp/mv4_*.log"))
    if not logs:
        print("  (no /tmp/mv4_*.log yet)")
    for lg in logs:
        lines = Path(lg).read_text(errors="replace").splitlines() if Path(lg).exists() else []
        print("  %-22s %s" % (Path(lg).name, (lines[-1][:88] if lines else "(empty)")))

    print("\n=== git ===")
    n = len([l for l in _cmd(["git", "status", "--porcelain"]).splitlines() if l.strip()])
    print("  working tree:", "clean" if n == 0 else f"{n} uncommitted file(s)")
    print("  HEAD:", _cmd(["git", "log", "--oneline", "-1"]) or "(n/a)")
    print()


if __name__ == "__main__":
    run()
