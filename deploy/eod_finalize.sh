#!/bin/bash
# Post-close FINALIZE for the 9 paper broker accounts — reconcile + reports + model_v4 refresh + commit.
# Scheduled by com.mv4.eod at 15:05 local Central (= 16:05 ET, 5 min AFTER the close) so the ledger
# marks, EOD PDFs, and the model_v4 ranking refresh all use the OFFICIAL CLOSE. The day's TRADES run
# 20 min BEFORE the close (com.mv4.preclose / preclose_trade.sh, 15:40 ET) for the model_v4 + daily
# books; the CALENDAR books trade at 10:00 (com.mv4.calendar_rebalance). This step only READS the broker
# (fills already happened) and writes ledgers/reports. launchd reruns a missed job on wake. Push stays manual.
set -u
cd /Users/david/PyCharmMiscProject/ai-paper-trader || exit 1
ulimit -n 10240 2>/dev/null || true        # launchd's ~256 fd default is too low for the model_v4 refresh
PY=/Users/david/PyCharmMiscProject/.venv/bin/python
ACCTS="topten copymodel rampup monthly10 weekly10 combo20 zscore1d_daily zscore5d_weekly zscore10d_biweekly"
TODAY="$(TZ=America/New_York date +%F)"
echo "===== EOD FINALIZE $TODAY  (run $(date)) ====="

# 1) reconcile every account (capture the day's fills -> ledger + slippage, at the OFFICIAL close) + EOD PDF
for a in $ACCTS; do
  $PY src/broker_sync.py --reconcile --account "$a" 2>&1 | grep -iE "RECONCILED|error" | tail -1
  $PY run.py eod --account "$a" >/dev/null 2>&1
done

# 2) refresh model_v4 scenario through today's OFFICIAL close (scores/rankings for tomorrow's decision)
$PY run.py scenario model_v4 --start 2000-01-03 --end "$TODAY" --no-sensitivity --no-charts 2>&1 | grep -iE "Report|error" | tail -1

# 3) consolidated EOD PDF across all 9 accounts
$PY run.py eod-accounts 2>&1 | grep -iE "wrote|error" | tail -1

# 4) commit the day's ledgers + tracked research outputs (push stays manual / user-run)
git add accounts/ backtests/ && git commit -q -m "EOD $TODAY: reconcile + model_v4 refresh + reports (trades ran pre-close)" \
  && echo "committed" || echo "nothing to commit"
echo "===== EOD FINALIZE $TODAY done ($(date)) ====="
