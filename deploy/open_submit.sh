#!/bin/bash
# Morning open: submit each account's rebalance for the live session. Scheduled by com.mv4.open at
# 8:35 local Central (= 9:35 ET, ~5 min after the open) so the rank uses LIVE prices (the phantom-bar
# guard uses the live bar while the market is open). Plain --submit (no --prequeue): it only fires
# inside a valid market window, so if the machine wakes AFTER the close the rebalance is safely skipped
# rather than filling thin off-hours. launchd reruns a missed job on wake. Paper only.
set -u
cd /Users/david/PyCharmMiscProject/ai-paper-trader || exit 1
PY=/Users/david/PyCharmMiscProject/.venv/bin/python
ACCTS="topten copymodel rampup monthly10 weekly10 combo20 zscore1d_daily zscore5d_weekly zscore10d_biweekly"
TODAY="$(TZ=America/New_York date +%F)"
echo "===== OPEN $TODAY  (run $(date)) ====="
for a in $ACCTS; do
  echo "-- $a --"
  BROKER_ADAPTER_ALLOW_SUBMIT=yes $PY src/broker_sync.py --submit-plan --account "$a" --submit 2>&1 \
    | grep -iE "PLAN|BUY|SELL|submitted|blocked|error" | head -6
done
echo "===== OPEN $TODAY done ($(date)) ====="
