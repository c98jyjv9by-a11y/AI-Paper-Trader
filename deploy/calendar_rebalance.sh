#!/bin/bash
# 10:00 Chicago rebalance for the CALENDAR books — submits them mid-morning (market OPEN) on their own
# rebalance day instead of at the open auction. Each book SELF-GATES via _is_rebalance_day off today's
# bar, so: weekly (weekly10, zscore5d_weekly, combo20) fire on Mondays, biweekly (zscore10d_biweekly)
# on the first Monday of an even ISO week, monthly (monthly10) on the month's first trading day — every
# one at 10:00 local. Fired every weekday (see com.mv4.calendar_rebalance.plist); non-rebalance days
# no-op via the gate. Replaces the old pre-open auction job (deploy/preopen_rebalance.sh, retired).
# The DAILY z-score book + the model_v4 accounts still trade at the close (eod_finalize.sh).
#
# Market is OPEN at 10:00, so orders are MARKETABLE fill-now day limits (--extended-hours), not opg.
# Idempotent per ET date (a once-daily lock) AND at the broker (client_order_id is unique per day/
# side/symbol). Gated on the broker clock being OPEN, so a host-TZ change can't fire it pre-market.
# launchd reruns a missed job on wake. Paper only; submit is env-guarded.
set -u
cd /Users/david/PyCharmMiscProject/ai-paper-trader || exit 1
ulimit -n 10240 2>/dev/null || true        # launchd's ~256 fd default is too low for the 83-ticker fetch
PY=/Users/david/PyCharmMiscProject/.venv/bin/python
ACCTS="monthly10 weekly10 combo20 zscore5d_weekly zscore10d_biweekly"
ETDATE="$(TZ=America/New_York date +%F)"
LOCK="/tmp/mv4_calendar_rebal_${ETDATE}.done"

if [ -f "$LOCK" ]; then echo "CALENDAR-REBAL $ETDATE: already ran today — skip"; exit 0; fi

# Only trade while the market is OPEN (broker clock, TZ-independent) — guards against a host-TZ drift
# firing this outside regular hours. The per-book _is_rebalance_day gate decides whether each actually trades.
GATE=$($PY - <<'PYEOF'
import sys, warnings
sys.path.insert(0, "src"); warnings.filterwarnings("ignore")
try:
    from broker_adapter import AlpacaPaper
    print("OK" if AlpacaPaper(account="weekly10").clock().get("is_open") else "SKIP")
except Exception:
    print("SKIP")
PYEOF
)
if [ "$GATE" != "OK" ]; then echo "CALENDAR-REBAL $ETDATE: market not open (broker clock) — skip"; exit 0; fi

echo "===== CALENDAR-REBAL $ETDATE  (run $(date)) ====="
for a in $ACCTS; do
  echo "-- rebalance $a --"
  BROKER_ADAPTER_ALLOW_SUBMIT=yes $PY src/broker_sync.py --submit-plan --account "$a" --submit --extended-hours 2>&1 \
    | grep -iE "PLAN|submitted|blocked|error" | head -2
done
touch "$LOCK"                              # mark done so any backup fire today no-ops
echo "===== CALENDAR-REBAL $ETDATE done ($(date)) ====="
