#!/bin/bash
# Daily yfinance option-chain capture — builds the historical chain we otherwise don't have, so an
# options strategy can eventually be backtested. Snapshots the model_v4 universe (83 tickers) + the
# SPY/QQQ benchmarks, calls AND puts, every expiry within 31 days (1 month and under), into
# data/options/options_<date>.csv.gz. Scheduled by com.mv4.options_snapshot at 15:15 local Central
# (= 16:15 ET, ~10 min after the close / EOD trade flow) Mon-Fri; launchd reruns a missed job on wake.
# Read-only w.r.t. the broker — pure data capture. Push stays manual.
set -u
cd /Users/david/PyCharmMiscProject/ai-paper-trader || exit 1
ulimit -n 10240 2>/dev/null || true        # 83+2 tickers x several expiries opens many sockets
PY=/Users/david/PyCharmMiscProject/.venv/bin/python
TODAY="$(TZ=America/New_York date +%F)"
echo "===== OPTIONS SNAPSHOT $TODAY  (run $(date)) ====="

$PY run.py options-snapshot --max-dte 31 2>&1 | tail -3

# commit the day's snapshot (history must persist); base live-state files are untouched. Push manual.
git add data/options/ && git commit -q -m "Options snapshot $TODAY" && echo "committed" || echo "nothing to commit"
