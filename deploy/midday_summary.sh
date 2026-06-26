#!/bin/bash
# Midday summary (informational ONLY — no trading). Scheduled by com.mv4.midday at 11:30 local Central
# (= 12:30 ET) Mon-Fri. Renders the model_v4 cross-book intraday Pulse + an all-9-account intraday
# snapshot (to a midday-named file so it doesn't clobber the EOD one). launchd reruns on wake. Read-only.
set -u
cd /Users/david/PyCharmMiscProject/ai-paper-trader || exit 1
PY=/Users/david/PyCharmMiscProject/.venv/bin/python
TODAY="$(TZ=America/New_York date +%F)"
echo "===== MIDDAY $TODAY  (run $(date)) ====="
# model_v4 cross-book intraday Pulse (scenario + topten/copymodel/rampup; renders each book's PDF)
$PY run.py midday-summary 2>&1 | grep -iE "wrote|report|midday|error" | tail -3
# all-9-account intraday snapshot (separate file; intraday marks)
$PY run.py eod-accounts --out "reports/midday_accounts_$TODAY.pdf" 2>&1 | grep -iE "wrote|error" | tail -1
echo "===== MIDDAY $TODAY done ($(date)) ====="
