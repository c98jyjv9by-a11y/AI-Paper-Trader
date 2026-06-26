#!/bin/bash
# Full end-of-day flow for the 9 paper broker accounts. Scheduled by the launchd agent com.mv4.eod
# at 15:15 local (Central) = 16:15 ET, Mon-Fri. launchd reruns a MISSED job on wake, so this survives
# the machine sleeping (unlike cron / background waiters). Idempotent; paper only; push stays manual.
set -u
cd /Users/david/PyCharmMiscProject/ai-paper-trader || exit 1
PY=/Users/david/PyCharmMiscProject/.venv/bin/python
ACCTS="topten copymodel rampup monthly10 weekly10 combo20 zscore1d_daily zscore5d_weekly zscore10d_biweekly"
TODAY="$(TZ=America/New_York date +%F)"
echo "===== EOD $TODAY  (run $(date)) ====="

# 1) reconcile every account (fills -> ledger + slippage) + render its EOD PDF
for a in $ACCTS; do
  echo "-- $a --"
  $PY src/broker_sync.py --reconcile --account "$a" 2>&1 | grep -iE "RECONCILED|error" | tail -1
  $PY run.py eod --account "$a" >/dev/null 2>&1
done

# 2) overlay flatten safety-net (model_v4 books only — clear any unsold TQQQ at the close)
for a in topten copymodel rampup; do
  BROKER_ADAPTER_ALLOW_SUBMIT=yes $PY src/broker_sync.py --flatten-overlay --account "$a" --submit 2>&1 | grep -iE "FLATTEN|error" | tail -1
done

# 3) refresh model_v4 scenario through today's close (scores/rankings for tomorrow's open)
$PY run.py scenario model_v4 --start 2000-01-03 --end "$TODAY" --no-sensitivity --no-charts 2>&1 | grep -iE "Report|error" | tail -1

# 4) consolidated EOD PDF across all 9 accounts
$PY run.py eod-accounts 2>&1 | grep -iE "wrote|error" | tail -1

# 5) commit the day's ledgers + tracked research outputs (push stays manual / user-run)
git add accounts/ backtests/ && git commit -q -m "EOD $TODAY: reconcile all + model_v4 refresh + reports" \
  && echo "committed" || echo "nothing to commit"
echo "===== EOD $TODAY done ($(date)) ====="
