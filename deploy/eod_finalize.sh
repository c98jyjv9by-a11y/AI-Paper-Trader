#!/bin/bash
# Close-to-close end-of-day flow for the 9 paper broker accounts — the SINGLE daily trading event.
# Scheduled by com.mv4.eod at 15:05 local Central (= 16:05 ET, 5 min after the close). It computes each
# account's rebalance off the CLOSE and executes it immediately (--extended-hours / post-market, fills
# now in the paper sim) so order execution is glued to when the score was computed, then reconciles,
# reports, and commits. The open/retry agents are removed — trading happens once, at the close.
# launchd reruns a missed job on wake. Paper only; push stays manual.
# NOTE: the rebound (TQQQ) overlay's 1-day cls-at-close exit doesn't cleanly fit a post-close trade —
# revisit before it next fires (idle today). No overlay-flatten step here (it would clear a fresh buy).
set -u
cd /Users/david/PyCharmMiscProject/ai-paper-trader || exit 1
ulimit -n 10240 2>/dev/null || true        # launchd starts with a ~256 fd limit; the model_v4 decision
                                           # + 83-ticker fetch opens more, so raise it (Errno 24 fix)
PY=/Users/david/PyCharmMiscProject/.venv/bin/python
ACCTS="topten copymodel rampup monthly10 weekly10 combo20 zscore1d_daily zscore5d_weekly zscore10d_biweekly"
# Close-traded books: the model_v4 accounts + the DAILY z-score book. The CALENDAR books (weekly10,
# combo20, zscore5d_weekly, zscore10d_biweekly, monthly10) now rebalance at the OPEN via
# deploy/preopen_rebalance.sh (com.mv4.preopen, 1 hr before open) — they are NOT traded here, only
# reconciled + reported below (their open fills are captured by step 2's reconcile).
TRADE_ACCTS="topten copymodel rampup zscore1d_daily"
TODAY="$(TZ=America/New_York date +%F)"
echo "===== EOD $TODAY  (run $(date)) ====="

# 1) TRADE: rebalance the close-traded books off the close, executed NOW (post-market, fills immediately)
for a in $TRADE_ACCTS; do
  echo "-- trade $a --"
  BROKER_ADAPTER_ALLOW_SUBMIT=yes $PY src/broker_sync.py --submit-plan --account "$a" --submit --extended-hours 2>&1 \
    | grep -iE "PLAN|submitted|blocked|error" | head -2
done

# 2) reconcile every account (capture the fills -> ledger + slippage) + render its EOD PDF
for a in $ACCTS; do
  $PY src/broker_sync.py --reconcile --account "$a" 2>&1 | grep -iE "RECONCILED|error" | tail -1
  $PY run.py eod --account "$a" >/dev/null 2>&1
done

# 3) refresh model_v4 scenario through today's close (scores/rankings for tomorrow's close decision)
$PY run.py scenario model_v4 --start 2000-01-03 --end "$TODAY" --no-sensitivity --no-charts 2>&1 | grep -iE "Report|error" | tail -1

# 4) consolidated EOD PDF across all 9 accounts
$PY run.py eod-accounts 2>&1 | grep -iE "wrote|error" | tail -1

# 5) commit the day's ledgers + tracked research outputs (push stays manual / user-run)
git add accounts/ backtests/ && git commit -q -m "EOD $TODAY: close rebalance + reconcile + model_v4 refresh + reports" \
  && echo "committed" || echo "nothing to commit"
echo "===== EOD $TODAY done ($(date)) ====="
