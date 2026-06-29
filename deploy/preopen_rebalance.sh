#!/bin/bash
# Pre-open rebalance for the CALENDAR books — rebalances them AT THE OPEN (limit-on-open, fills in the
# 9:30 ET auction) instead of the close. Scored off the last completed close; BROKER_REBALANCE_PREOPEN=1
# makes the gate + combo month-anchor evaluate the UPCOMING session, so each book SELF-GATES to its own
# first-of-period day (weekly=Mon, biweekly=first Mon of an even ISO week, monthly=first trading day of
# the month) and no-ops otherwise. The DAILY z-score book + the model_v4 accounts trade at the close
# (eod_finalize.sh). launchd reruns a missed job on wake. Paper only; submit is env-guarded.
#
# ROBUST TO HOST TIMEZONE: launchd fires at several LOCAL times (see com.mv4.preopen.plist), but the actual
# trade is gated on the BROKER CLOCK (real time, TZ-independent) — only when the market is CLOSED, the next
# open is TODAY (ET), and that open is <=100 min away. A once-per-day lock keyed on the ET date makes the
# multiple fires idempotent: exactly one in-window run trades, the rest skip. So a host-TZ change (CT->ET)
# can't fire it at the wrong moment.
set -u
cd /Users/david/PyCharmMiscProject/ai-paper-trader || exit 1
ulimit -n 10240 2>/dev/null || true        # launchd's ~256 fd default is too low for the 83-ticker fetch
PY=/Users/david/PyCharmMiscProject/.venv/bin/python
ACCTS="monthly10 weekly10 combo20 zscore5d_weekly zscore10d_biweekly"
ETDATE="$(TZ=America/New_York date +%F)"
LOCK="/tmp/mv4_preopen_${ETDATE}.done"

if [ -f "$LOCK" ]; then echo "PRE-OPEN $ETDATE: already ran today — skip"; exit 0; fi

# robust window gate off the broker clock (independent of the host timezone / launchd's local fire time)
GATE=$($PY - <<'PYEOF'
import sys, warnings
sys.path.insert(0, "src"); warnings.filterwarnings("ignore")
from datetime import datetime
try:
    from broker_adapter import AlpacaPaper
    c = AlpacaPaper(account="weekly10").clock()
    now = datetime.fromisoformat(c["timestamp"]); nopen = datetime.fromisoformat(c["next_open"])
    mins = (nopen - now).total_seconds() / 60.0
    print("OK" if ((not c.get("is_open")) and now.date() == nopen.date() and 0 < mins <= 100) else "SKIP")
except Exception:
    print("SKIP")
PYEOF
)
if [ "$GATE" != "OK" ]; then echo "PRE-OPEN $ETDATE: not in pre-open window (broker clock) — skip"; exit 0; fi

echo "===== PRE-OPEN $ETDATE  (run $(date)) ====="
for a in $ACCTS; do
  echo "-- preopen rebalance $a --"
  BROKER_REBALANCE_PREOPEN=1 BROKER_ADAPTER_ALLOW_SUBMIT=yes \
    $PY src/broker_sync.py --submit-plan --account "$a" --submit --auction 2>&1 \
    | grep -iE "PLAN|submitted|blocked|error" | head -2
done
touch "$LOCK"                              # mark done so the later local fires no-op
echo "===== PRE-OPEN $ETDATE done ($(date)) ====="
