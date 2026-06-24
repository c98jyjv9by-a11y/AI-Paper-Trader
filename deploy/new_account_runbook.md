# Runbook — set up a new broker-driven paper account

For an AI agent/session creating a new Alpaca **paper** account on a strategy. Do the steps in order.
Everything is paper-only and submit-guarded; **never** place a live order without the env guard, and
**never** commit `.env`.

---

## 0. Decide four things first
1. **Account name** — short lowercase, no spaces (e.g. `monthly10`, `weekly10`, `combo20`).
2. **Strategy = `target_mode`** (see the table in §2).
3. **Starting cash** — default `100000`.
4. **Key env-var names** — convention `APCA_API_KEY_ID_<SUFFIX>` / `APCA_API_SECRET_KEY_<SUFFIX>`
   (e.g. `APCA_API_KEY_ID_MONTHLY10`). One pair per account so each uses its own Alpaca creds.

---

## 1. Add the keys to `.env`
Append the pair (real keys, or `PLACEHOLDER_REPLACE_ME` to wire up now and fill later). Use a bash
append so you don't read existing secrets into context:
```bash
cd ai-paper-trader
cat >> .env <<'EOF'

APCA_API_KEY_ID_<SUFFIX>=PLACEHOLDER_REPLACE_ME
APCA_API_SECRET_KEY_<SUFFIX>=PLACEHOLDER_REPLACE_ME
EOF
git ls-files | grep -E '(^|/)\.env$' && echo "WARNING: .env is tracked!" || echo "OK: .env gitignored"
```
Placeholder keys are fine for **creating** the account (no network), but Alpaca calls (dry-run/submit)
**fail at auth** until real paper keys are in place.

---

## 2. Pick the `target_mode`
| `kind` | What it does | Key params |
|---|---|---|
| `model_v4` | Follow model_v4's own buy/sell rules on the book (seeded with the live book+cash) | — |
| `score_gate_rampup` | Buy >`min_score` names, sell per model_v4, until `graduate_at` of cash deployed → full model_v4 | `min_score, size_pct, graduate_at` |
| `score_rebalance` (single) | Rank universe by trailing-`lookback_days`-avg score; hold top_n (+bottom_n) equal-weight to `gross`; rebalance on first trading day of each week/month | `lookback_days, top_n, bottom_n, rebalance, gross` |
| `score_rebalance` (staggered split) | Top sleeve `top_lookback_days`-score anchored to month start, re-traded monthly; bottom sleeve `bottom_lookback_days`-score re-sized weekly; account rebalances `rebalance` | `top_n, top_lookback_days, top_refresh, bottom_n, bottom_lookback_days, rebalance, gross` |
| seed-only: `top_n` / `model_equal` / `score_gate` | Initial basket then evolves; rarely used standalone now | see `broker_sync.py --help` |

`score_rebalance` accounts carry **no** model_v4 rules and **no** hedge/rebound overlay.

---

## 3. Create the account
Local only (writes the ledger + manifest; no network). Use the CLI for simple modes:
```bash
# example: monthly top-10, 60-day score
python src/broker_sync.py --create-account --account <name> --target-mode score_rebalance \
  --rebalance monthly --top-n 10 --lookback-days 60 \
  --key-env APCA_API_KEY_ID_<SUFFIX> --secret-env APCA_API_SECRET_KEY_<SUFFIX>
```
CLI flags for `score_rebalance`: `--rebalance {daily|weekly|monthly} --top-n N --bottom-n N --lookback-days N`.
Starting cash: add `--starting 100000` if not the default.

**Staggered split (combo-style) configs aren't fully expressible on the CLI** — create with the simple
flags, then overwrite `target_mode` in the manifest directly:
```bash
python - <<'PY'
import json, glob
f = glob.glob('accounts/<name>/*.json')[0]   # the manifest
m = json.load(open(f))
m['target_mode'] = {'kind':'score_rebalance','rebalance':'weekly','gross':0.9,
  'top_n':10,'top_lookback_days':60,'top_refresh':'monthly',
  'bottom_n':10,'bottom_lookback_days':5,'bottom_refresh':'weekly'}
json.dump(m, open(f,'w'), indent=2)
PY
```

---

## 4. Verify the manifest
```bash
python -c "import json,glob; m=json.load(open(glob.glob('accounts/<name>/*.json')[0])); \
print('target_mode',m.get('target_mode')); print('keys',m.get('broker_keys')); \
print('ramp_up?', 'ramp_up' in m, '| start', m.get('starting_value'))"
```
Expect: correct `target_mode`, `broker_keys` pointing at your env vars, **no `ramp_up`** (for
model_v4 / score_gate_rampup / score_rebalance the create flow strips it), and the right starting value.

---

## 5. ⚠️ RUN THE LIVE PATH FOR REAL — don't trust mocked tests alone
**The #1 mistake:** unit tests mock the scoring/calendar functions and pass green while a real wiring
bug (e.g. an unimported function) sits latent and only throws on the first live rebalance. Always
exercise the real path once with a fake broker client (real scoring, no Alpaca needed):
```bash
python -c "
import sys; sys.path.insert(0,'src'); import warnings; warnings.filterwarnings('ignore')
import broker_sync as bs
class FC:
    def account(self): return {'equity':100000.0}
    def latest_prices(self, syms): return {s:{'mid':100.0} for s in syms}
import json,glob; tm=json.load(open(glob.glob('accounts/<name>/*.json')[0]))['target_mode']
t,_ = bs._score_rebalance_targets('<name>', FC(), {}, tm)
print('produced %d target names:'%len(t), sorted(t)[:12])
"
```
It should print real tickers and not raise. (For non-score_rebalance modes, run the dry-run in §7 once
real keys are set.)

---

## 6. Tests (if you added/changed mode logic)
Add unit tests in `tests/test_broker_sync.py` (mock `load_manifest`, `_recent_trading_days`,
`_is_rebalance_day`, `_lookback_avg_scores`, and a fake client). Then:
```bash
python -m pytest tests/test_broker_sync.py tests/test_cli.py -q
```
Green except the one known pre-existing `test_pdf_report` failure.

---

## 7. Dry-run, then submit, then reconcile (needs REAL keys)
Always one line per command — **do not** use `\` line-continuation with env vars (a stray char makes
zsh drop the env vars → silent dry-run / wrong behavior).
```bash
# dry-run (nothing sent)
for a in <name>; do python src/broker_sync.py --submit-plan --account "$a"; done

# LIVE submit (env guard inline, single line)
for a in <name>; do BROKER_ADAPTER_ALLOW_SUBMIT=yes python src/broker_sync.py --submit-plan --account "$a" --submit; done

# reconcile after fills (pulls real fills + slippage into the ledger)
for a in <name>; do python src/broker_sync.py --reconcile --account "$a"; done
```
**Confirm the submit actually sent:** the output must NOT say `DRY-RUN (nothing sent)`.

Off-cadence "fire today" deploy (force a rebalance now + score as-of today's intraday bar; for
score_rebalance, also anchors the combo top sleeve to today): prefix `BROKER_REBALANCE_FORCE_TODAY=1`.
A brand-new empty account deploys on its first run regardless of the calendar anyway.

---

## 8. (Optional) wire into cron
Add the account to `deploy/mv4_crontab.txt` (open/retry/close/reconcile phases via `broker_cron.py`,
which is dry-run unless `--live`). Times are CT = ET−1.

---

## Gotchas / standing rules
- **Buys fill ASAP** (marketable day-ext, the default); pass `--auction` for next-open/close auction orders.
- **Single-line commands** for anything with env vars — `\` continuations silently drop them.
- **Placeholder keys** → Alpaca auth fails; swap in real paper keys before dry-run/submit.
- **`.env` is gitignored** and holds keys only — never commit it; commit only when asked; pushes are run by the user.
- **Never** mutate `data/{trade_log.csv,positions.csv,portfolio_state.json}` (base live-state).
- Paper only — no live orders without `BROKER_ADAPTER_ALLOW_SUBMIT=yes`.
- New score_rebalance strategies should be validated in backtest first (see `research/make_freq_compare.py` /
  the `research/make_zscore_*` family) before being trusted live — frictionless backtests are survivorship-biased.
