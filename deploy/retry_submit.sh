#!/bin/bash
# Morning retry: re-price any order that did NOT fill at the open through the WIDER retry collar.
# Scheduled by com.mv4.retry at 9:05 local Central (= 10:05 ET) Mon-Fri, ~30 min after the open job.
# `--retry` rebuilds the unfilled deltas at the wider collar (and bypasses the auction-window guard,
# since it's an intraday day-limit pass). Only fires inside a market window — if the machine wakes
# off-hours it skips. launchd reruns a missed job on wake. Paper only.
set -u
cd /Users/david/PyCharmMiscProject/ai-paper-trader || exit 1
PY=/Users/david/PyCharmMiscProject/.venv/bin/python
ACCTS="topten copymodel rampup monthly10 weekly10 combo20 zscore1d_daily zscore5d_weekly zscore10d_biweekly"
TODAY="$(TZ=America/New_York date +%F)"
echo "===== RETRY $TODAY  (run $(date)) ====="
for a in $ACCTS; do
  echo "-- $a --"
  BROKER_ADAPTER_ALLOW_SUBMIT=yes $PY src/broker_sync.py --submit-plan --account "$a" --submit --retry 2>&1 \
    | grep -iE "PLAN|BUY|SELL|submitted|blocked|error" | head -6
done
echo "===== RETRY $TODAY done ($(date)) ====="
