#!/bin/bash
# Pre-close trade — the day's single trading event for the close-traded books, run 20 min BEFORE the
# close (14:40 local Central = 15:40 ET) so orders fill in regular-hours liquidity near the close
# instead of the thin post-market session. Trades the model_v4 accounts + the DAILY z-score book only;
# the CALENDAR books rebalance at 10:00 (com.mv4.calendar_rebalance), and the post-close reconcile +
# reports + model_v4 refresh + commit run at 16:05 (com.mv4.eod / eod_finalize.sh) off the official close.
# Idempotent per ET date (once-daily lock) AND at the broker (client_order_id unique per day/side/symbol;
# cadence books also self-guard to one run/day). launchd reruns a missed job on wake. Paper only; submit env-guarded.
set -u
cd /Users/david/PyCharmMiscProject/ai-paper-trader || exit 1
ulimit -n 10240 2>/dev/null || true        # launchd's ~256 fd default is too low for the 83-ticker fetch
PY=/Users/david/PyCharmMiscProject/.venv/bin/python
TRADE_ACCTS="topten copymodel rampup zscore1d_daily"
ETDATE="$(TZ=America/New_York date +%F)"
LOCK="/tmp/mv4_preclose_${ETDATE}.done"
if [ -f "$LOCK" ]; then echo "PRE-CLOSE $ETDATE: already ran today — skip"; exit 0; fi

# only trade while the market is OPEN (broker clock, TZ-independent) — guards against a host-TZ drift
GATE=$($PY - <<'PYEOF'
import sys, warnings
sys.path.insert(0, "src"); warnings.filterwarnings("ignore")
try:
    from broker_adapter import AlpacaPaper
    print("OK" if AlpacaPaper(account="topten").clock().get("is_open") else "SKIP")
except Exception:
    print("SKIP")
PYEOF
)
if [ "$GATE" != "OK" ]; then echo "PRE-CLOSE $ETDATE: market not open (broker clock) — skip"; exit 0; fi

echo "===== PRE-CLOSE TRADE $ETDATE  (run $(date)) ====="
for a in $TRADE_ACCTS; do
  echo "-- trade $a --"
  BROKER_ADAPTER_ALLOW_SUBMIT=yes $PY src/broker_sync.py --submit-plan --account "$a" --submit --extended-hours 2>&1 \
    | grep -iE "PLAN|submitted|blocked|error" | head -2
done
touch "$LOCK"
echo "===== PRE-CLOSE TRADE $ETDATE done ($(date)) ====="
