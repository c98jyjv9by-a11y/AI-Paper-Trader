# AI Paper Trader

Local Python paper-trading research agent. Recommends trades on U.S. equities and ETFs using momentum signals. **No live orders are ever placed.**

## Active model & current state (read this first)

**`model_v4` is THE active model.** It is the only model version in `config/scenarios/`; every
account uses it. Older/experimental versions (v2, v3, v5, v6) and one-off scripts live in
`archive/` (see `archive/README.md`) and are not wired into anything.

- **Model** — `config/scenarios/model_v4.yaml`. 83-name semis/AI/tech momentum book; composite
  score 0–1, buy gate 0.70 (+ persistence buy at >0.90 for 3 days); 8.5% per-name cap,
  max total exposure 0.90, ≤2 new trades/day; Barroso vol governor (target 0.35); score-gated
  15% stop (fires only when score<0.90), no take-profit (let winners run), 90-day max hold
  suppressed until score<0.80. **Do NOT change v4's ticker list** —
  broad-universe runs (`research/make_cycle_test.py`) are test-only.
- **Hedge overlay** — `src/hedge_overlay.py`. A standalone **overlay that sits ON TOP of model_v4
  and never modifies it.** Signal: QQQ 1-day up-shock + SPY 5d-vol z-spike → buy long **SOXS**
  (−3× inverse semis, 1-day hold, **never shorting**) sized inverse-vol; two-gate hybrid
  (soft=half / hard=full). Validated as the only working "June-16-pullback" hedge.
- **Rebound overlay** — `src/rebound_overlay.py`. The standalone **mirror image** of the hedge (sits ON
  TOP of model_v4, never modifies it). Trigger (`ReboundConfig`, tuned via `research/make_model_v4_rebound_sweep.py`):
  **QQQ −1d ≤ −2.5% AND `spread_trl_1d` < 0 (momentum signal inverting) AND z(**QQQ** 5d vol) ≥ 0.25 → buy
  TQQQ (+3×) at 50% of book, 1-day hold.** The `spread < 0` filter is the key — it selects the
  mean-reverting momentum-crash setups and skips trend-continuation knives. Small, robust, **tail-neutral**
  Sharpe-adder (ΔSharpe +0.06 full / +0.07 train / +0.03 test, MaxDD −39% vs −40%, worst-day unchanged,
  ~3 fires/yr, 64% win). Surfaced in EOD reports as a **separate "Rebound overlay" status line** with its
  1-day session P&L (`build_report` → `d["rebound"]` via `rebound_overlay.recommend`; NOT folded into the
  book rollups, unlike the hedge). **Fully LIVE:** `rebound_overlay.live_signal()` computes the trigger
  from yfinance + the newest `rankings_*.csv` (QQQ 1d, SPY 5d-vol z, top10−bottom10 spread), so it works on
  any date; `recommend(live='auto')` uses the panel when it covers the date else falls back to live. **The
  live broker accounts trade it:** `broker_sync._rebound_target` (wired into `compute_targets` for the
  `model_v4`/`score_gate_rampup` modes) ADDS a `REBOUND_SYM`=**TQQQ** buy to the target when it fires (full
  weight × held book). **Funding** (`rebound_funding`, default `trim`): cash first, then ROTATE — exit AT MOST
  `rebound_trim_max` (default **2**) holdings, the lowest by **5-day avg score** (`_avg_scores`, across all daily
  ranking snapshots whether held or not), to raise the shortfall; rest from cash, **overlay capped** if cash + 2
  exits fall short (bounds turnover to 2 names). The trim sweep (`research/make_trim_funding_test.py`) confirmed ~50% stays
  near-optimal funded by rotation (costing ~0.02 ΔSharpe vs free cash). Set `cash` to cap the sleeve at available
  cash instead (no book sale). When it stops firing TQQQ
  leaves the target so the reconcile flattens it next session
  (= the 1-day exit) — the TQQQ **sell is forced to `cls` (market-on-close), even in `--extended-hours` mode**,
  so the exit only ever happens at the close, never intraday. If a `cls` exit doesn't fully fill (e.g. submitted
  after the ~15:50 ET LOC cutoff, partial, or rejected), **`broker_sync.py --flatten-overlay --account <a> [--submit]`**
  (`flatten_overlay`) cancels any working TQQQ order and MARKETABLE-exits the remaining live position (day-ext,
  ~3% through the bid) — the after-hours safety net to fully clear the sleeve. The model decision never sees TQQQ (excluded like the hedge), so it isn't stop-managed.
  On by default for the trackers; opt out with manifest `rebound: false`. `python src/rebound_overlay.py
  [--recommend [--live …]]`. Tuning analysis in `research/make_model_v4_rebound*.py` / `research/make_model_v4_{reverse,defense}.py`.
- **Accounts** — `accounts/<name>/` is an append-only ledger system (immutable frozen core +
  `continuation/` living layer; SHA-256 manifest integrity via `account-verify`). Active accounts:
  `primary` (main paper book), `tracker` (frictionless ramp-up sim, assumes 10bp cost). **Broker-driven**
  go-forward books (ledger synced from real Alpaca paper fills): **NINE Alpaca paper accounts**, each with
  its own keys, in two groups (per-mode order rules are detailed in the **Broker-integration** bullet below).
  **(A) Model-driven** — follow model_v4 itself: `topten` (seeded top-10; keys `APCA_*_NEW`) and `copymodel`
  (seeded model-equal; keys `APCA_*_EXACT`), both `target_mode.kind=model_v4` → **follow model_v4's own
  buy/sell rules** (`next_session_decision` **seeded with the live broker book + cash** via `_model_v4_decision`,
  so the exposure cap / rotation funding / exits are real — not a from-inception sim); their
  `top_n` / `model_equal` / `score_gate` modes were only the **initial seed**, which now persists and evolves
  under model_v4. `rampup` (`score_gate_rampup`: **buy** only names scoring >0.9 (8.5% each) but **sell** only
  per model_v4's exit rules, until 75% of starting cash is deployed (Σ broker buys/starting), then full
  model_v4; keys `APCA_*_RAMP_UP`). These three also carry the **1-day rebound TQQQ overlay**; none trade the
  SQQQ hedge. **(B) Research strategy books** — pure signal rules, NO model_v4 entry/exit logic and NO
  overlay/hedge: three `score_rebalance` momentum books — `monthly10` and `weekly10` (top-10 by 60-day-avg
  composite score, equal-weight to 90% gross, rebalanced on the first trading day of each month / week) and
  `combo20` (staggered: top-10 / 60-day refreshed monthly + bottom-10 / 5-day refreshed weekly); and three
  regime-filtered `zscore_reversal` mean-reversion books — `zscore10d_biweekly` (the validated 10d/biweekly
  config), `zscore5d_weekly`, `zscore1d_daily` (buy the 10 names most-fallen vs their own z-norm, equal-weight,
  to CASH when QQQ < its 200-day MA). Keys `APCA_*_{MONTHLY10,WEEKLY10,COMBO20,ZSCORE10D_BIWEEKLY,ZSCORE5D_WEEKLY,ZSCORE1D_DAILY}`.
  Live broker books, driven by **launchd agents** (`deploy/com.mv4.{eod,midday}.plist`): trading is a single
  **close-to-close** event at 16:05 ET (`com.mv4.eod` → `deploy/eod_finalize.sh`) — compute each book off the
  close and **execute immediately** (post-market, fills now in the paper sim) so order execution is glued to
  when the score was computed; plus a 12:30 ET midday info report (`com.mv4.midday`). (The old per-phase
  `archive/mv4_crontab.txt` open/retry/close cron is superseded; agents raise the fd `ulimit` for the launchd
  environment.)
- **Why the z-score books exist — a SIGNAL-LATENCY play (not merely "mean reversion").** The momentum books
  (model_v4 + the `score_rebalance` books) decide purely on the **close** score/rank. That backtests well —
  the backtest is frictionless close-to-close, capturing the full move from close T to close T+1 — but **live
  underperforms**: by the time the close score is computed and you can actually buy, **part of the predicted
  move has already happened** (trade friction + signal delay), so realized return < backtest. The strategy is
  right about *which* names, just too late to capture the move. The `zscore_reversal` books target exactly that
  leak: instead of the raw close score, they rank by the per-ticker **normalized spread of the LATEST score vs
  the name's own 60-day baseline** — `z = (latest score − 60d mean) / 60d std` — read off the **freshest price
  available** (the live intraday bar while the market is open, the last *completed* close otherwise — see
  `_valid_before`/`_drop_phantom`; never a phantom overnight bar). Normalizing per name makes the spread
  comparable across the universe (a jumpy-score name needs a bigger move to register than a stable one).
  **Buying the lowest-z names bets on harvesting the timing divergence the delayed close-only books miss** —
  acting on the fresh read before a close-only strategy can. The three cadences test that timing edge at three
  speeds: **`1d/daily`** = the purest "trade the freshest signal" (most turnover/cost), **`5d/weekly`** and
  **`10d/biweekly`** = average the spread to trade less noise/friction (10d/biweekly was the IC- and
  cost-validated winner). The **close-to-close EOD agent applies the same principle to every book** — compute
  off the latest price and fill at once — to collapse the signal-to-fill gap so live tracks the backtest.
  `src/midday_summary.py` (`run.py midday-summary`) rolls the model_v4 scenario + the three **model-driven**
  accounts (the default; `--accounts` to override) into one cross-book INTRADAY table
  (`reports/midday_summary_<date>.md`) and renders each book's midday
  PDF; `src/eod_summary.py` (`run.py eod-summary`) is the EOD sibling — marks to the official close,
  **sells the overlay hedge at the close**, renders each book's EOD PDF into `reports/eod/`, and writes
  a consolidated one-page **PDF** (`reports/eod_summary_<date>.pdf`, `.md` alongside) with grouped tables
  (model_v4 reference vs live accounts) incl. a realized **Hedge P&L** column. `src/snapshot.py` (`run.py snapshot
  [--end …] [--accounts …]`) renders the daily **snapshot** PDF (`reports/snapshot_<date>.pdf`) across ALL broker
  accounts: **page 1** is a summary table (the order-history cover, re-cut) showing each account's **current-day P&L
  so far** (equity − prior-close equity) + **Day %**, then **Since-Inception P&L + %** and **inception-aligned QQQ/SPY**
  (each account's own start→today window), plus **#positions / #orders / #days-trading** and a TOTAL row. **Account
  returns (Day % / Incep %) are on INVESTED capital — P&L ÷ (equity − cash), cash EXCLUDED** (matches eod_accounts'
  "Day % inv") so they're comparable to the fully-invested benchmarks. **Below TOTAL sit three benchmark rows — QQQ,
  SPY, and the equal-weight model_v4 Universe average** — each with its daily return (prior-close→now) and its
  since-inception return (starting-weighted across the fleet). **Page 2 = "Orders Today, totals by account"**: a
  per-account roll-up (orders / buys / sells / filled / traded $ / realized / unrealized) of the current session
  window — no per-ticker detail. **Page 3+ = "Orders Today"** per-account detail: every order whose submission falls in
  the CURRENT session window — from the **prior trading day's market close (16:00 ET) through now** (so the post-close
  EOD-agent fills + the pre-open auction orders are included) — shown with the SAME per-order stats columns as the
  order-history report (Score@sub / Trail 1/5/10/20/60d / Pattern / Rlz / Unrlz / Ret / **Held** / Reason). The order-row
  builders + coloring are **shared** with `account_orders_report.py` (`_order_builders`, `_order_total_row`,
  `_color_orders`, `ORDER_COLS/ORDER_RAW`) so the two reports never drift. **`Held` = days the order's shares were/are
  held** (a held BUY → its fill date→today; a SELL → the position's entry→the sell), computed in `_annotate_trade_pnl`
  and shown in BOTH this report and the order-history report. (The old "performance snapshot — 3 ways to implement
  model_v4" view is replaced by this report.)
  `src/intraday_check.py` (`run.py intraday-check [--accounts …] [--extended-hours] [--summary] [--qqq/--spread/--vol-z
  what-if]`) is the one-shot **intraday trade-determination** check: live overlay signals (rebound + hedge — fire/idle
  + gate values) and the **dry-run order plan** for each account (model reconcile + overlay buy with its funding), read-only.
  Each planned order is ENRICHED beneath its line with the ticker's composite **score + cross-sectional rank**,
  trailing **1/5/20/60d AVG score**, a **trend type** (uptrend/downtrend/rising/falling/flat from the score stack),
  trailing **1/5/20/60d price return**, and the **logged reason** (`_build_enrichment`: one `_score_panel` +
  one price fetch per run, only when something trades); churn-suppressed trims show as `HOLD …` lines.
  `src/eod_accounts.py` (`run.py eod-accounts [--accounts …] [--end …] [--out …]`) renders a consolidated
  **EOD PDF across ALL broker accounts** (`reports/eod_accounts_<date>.pdf`): a summary table (equity, day P&L $/%,
  total %, #positions, #trades) + a brief **per-strategy description** + a page of **today's fills** per account,
  pulled from each account's LIVE broker state. The EOD summary table also carries a **TOTAL** row and
  **QQQ/SPY** benchmark rows, **Cash** + **Days-since-inception** columns, and a **Day % on invested**
  (P&L ÷ equity−cash). `src/positions_report.py` (`run.py positions-report [--accounts …] [--end …] [--out …]`)
  renders a **positions + queued-orders PDF across all broker accounts** (`reports/positions_report_<date>.pdf`):
  one page per account with a **current-positions** table (qty / entry / last / market value / unrealized P&L)
  and the **queued orders** the live reconcile would send now (dry-run, latest prices, with each order's
  clarified TRIM/EXIT/OPEN/ADD reason + churn-suppressed trims) — **every ticker enriched** with the same
  per-ticker analytics as `intraday-check` (composite score + cross-sectional rank, trailing 1/5/20/60d avg
  score, trend type, trailing 1/5/20/60d return; one shared `_build_enrichment` panel + price fetch). For a
  book NOT on its rebalance day (weekly/biweekly/monthly off-cadence) it shows **"WHAT'S LIKELY NEXT"** — the
  plan it would send at its next rebalance, computed off the latest data by forcing the calendar gate
  (`BROKER_REBALANCE_FORCE_TODAY`) — so the report always answers "what trades are coming". All these previews
  call `submit_session(..., log=False)`, a **READ-ONLY** mode that skips the plan-json / decisions.csv /
  suppressed.csv writes so reports + `intraday-check` never pollute the durable per-trade audit log (a real
  submit always logs).
  `src/account_orders_report.py` renders an **order-history + P&L PDF across all
  broker accounts**: every order labeled with its **governing rule** (model entry/exit, ramp-up buy,
  rebalance add/drop, z-reversal entry/to-cash, overlay sleeve by symbol — Alpaca stores no per-order
  reason, but each book is a fixed rule set), plus each book's open-position return vs **inception-aligned**
  QQQ/SPY.
- **Broker integration (Alpaca paper, paper-only + submit-guarded)** —
  `src/broker_adapter.py` (REST client; refuses non-paper host; `submit`/`cancel` inert unless
  `confirm=True` AND env `BROKER_ADAPTER_ALLOW_SUBMIT=yes`),
  `src/broker_sync.py` (reconcile-to-target **limit** orders with **data-driven per-instrument
  collars** from the 2y overnight-gap distribution → `backtests/collars.csv`; realized-slippage
  log; broker→ledger sync; `create_broker_account`. **Churn deadband** (`MIN_RESIZE_SHARES`, default
  **1**, per-account manifest override `min_resize_shares`): in `submit_session`, a resize of a name being
  KEPT (both sides held) of ≤ the threshold is snapped away (no order) so the daily 1-share rebalance churn
  is skipped — **full exits (target 0) and fresh opens (current 0) are NEVER suppressed**; each skip is
  recorded to `accounts/<name>/broker/suppressed.csv` + the plan json + surfaced as a `HOLD …` line in
  `intraday-check`. **Action-clarified reasons**: each order's decision reason is led with what it ACTUALLY
  does (`_action_label` → TRIM / EXIT / OPEN / ADD) ahead of the strategy rationale, so a SELL of a name
  still in the basket reads "TRIM to target weight — …" not "entry"; flows to `decisions.csv` (logged) +
  `intraday-check` (shown). **Quote-sanity fallback** (`_sanitize_quotes`): a
  ONE-SIDED (missing bid/ask — the after-hours trap) or STALE (>25% off the last close) broker quote has
  its mid replaced by the yfinance last close — applied to BOTH order PRICING (limits) and dollars→shares
  SIZING, so neither a limit nor a share-count is built off an un-fillable/mis-priced quote. **Phantom-bar
  guard** (`_valid_before`/`_drop_phantom`, fleet-wide across the model_v4 / score_rebalance /
  zscore_reversal scoring paths): market OPEN → the live bar drives the rank; market CLOSED → any bar
  dated on/after the next session (a fabricated overnight bar) is dropped so scoring ranks off the last
  completed close. The target book is per-account via manifest
  `target_mode`. **Live steady-state modes:** `{kind:model_v4}` → **follow model_v4's own buy/sell
  rules on the account's own book** (`_model_v4_decision` runs `next_session_decision` seeded with the
  live broker book + cash) — used by `topten`/`copymodel`; and `{kind:score_gate_rampup,min_score,
  size_pct,graduate_at}` → **buy >min_score names, sell only per model_v4 exits, until graduate_at of
  starting cash is deployed, then full model_v4** — used by `rampup`; and **`{kind:score_rebalance,
  lookback_days,top_n,bottom_n,rebalance,gross}`** → rank the scenario universe by the **trailing
  `lookback_days`-day AVG composite score**, hold the **top_n (+ optional bottom_n) names equal-weight**
  to `gross` of equity, and **rebalance only on the first trading day of each week/month** (off-rebalance
  days hold; no model_v4 rules, no hedge/rebound overlay; calendar-gated via `_recent_trading_days` +
  `_is_rebalance_day`, scored live via `_lookback_avg_scores`). A **STAGGERED split** variant
  (`top_lookback_days/top_refresh` + `bottom_lookback_days` present → `_combo_targets`) runs two
  independent sleeves: **top_n by the `top_lookback_days`-avg score anchored to the month start (names match
  the monthly book), re-sized ONLY on the month's first weekly rebalance — held/untouched the other weeks**;
  PLUS **bottom_n by the `bottom_lookback_days`-avg score, re-sized every (weekly) rebalance**. Used by the
  research accounts **`monthly10`** (monthly / top-10 / 60-day), **`weekly10`** (weekly / top-10 / 60-day),
  **`combo20`** (STAGGERED: top-10 / 60-day refreshed monthly + bottom-10 / **5-day** refreshed weekly, account
  rebalances weekly) — the 60-day-lookback momentum sweep winners (keys `APCA_*_{MONTHLY10,WEEKLY10,COMBO20}`,
  live in `.env`). One-off override **`BROKER_REBALANCE_FORCE_TODAY=1`**
  forces a rebalance TODAY regardless of the calendar gate and scores as-of today's intraday bar (also anchors
  the combo top sleeve to today instead of the month start) — for an off-cadence "fire now" run. And
  **`{kind:zscore_reversal, zscore_lookback, avg_window, n, rebalance, regime_ma, gross}`** (`_zscore_reversal_targets`)
  → a **mean-reversion** book: BUY the `n` LOWEST-signal names where signal = the `avg_window`-day avg of the
  per-ticker `zscore_lookback`-day z-score of the composite (most-fallen vs their own norm), equal-weight,
  rebalanced on `rebalance` (incl. **biweekly** = first trading day of even ISO weeks); **REGIME FILTER**:
  go to CASH when QQQ < its `regime_ma`-day MA (`_qqq_above_ma`). IC-swept + cost/regime-backtested
  (`research/make_zscore_*` — IC sweep, variant/cadence sweep, regime-filter). Signal-edge analysis:
  `research/make_latency_edge.py` (the close signal's forward return splits OVERNIGHT, lost to open-
  execution, vs INTRADAY, captured — sizing why a close-only book bleeds ~80% of its paper edge live),
  `make_zscore_corr_horizon.py` (trailing-avg-z → fwd-return Pearson heatmap), `make_zscore_buckets_horizon.py`
  (fwd return by absolute z-bucket) and `make_zscore_rankgroups_horizon.py` (by cross-sectional z-rank
  group — the bottom-10 the book buys is the best group, cleanest at the 10d window).
  `research/make_zscore_open_vs_close.py` (OPEN- vs CLOSE-execution, signal/picks held fixed, only the fill
  point varies → `backtests/zscore_open_vs_close_<date>.md`): vs the IDEALIZED decision-close fill, open
  (next-session-open) execution is ~neutral on return (weekly −0.9%/yr, biweekly +1.7%/yr) but **worse on
  tails** — worst period weekly −16.5%→−19.5%, biweekly −13.8%→−20.2% (weekend-gap exposure) — and slightly
  lower Sharpe. CAVEAT: the idealized close fill isn't achievable live (the latency thesis — `make_latency_edge`),
  so vs REALISTIC live close fills open execution may still win; the backtest bounds the downside, it doesn't
  prove open is better. The 10d-avg-z /
  biweekly / QQQ>200dMA config is best (gross Sharpe ~1.3, net ~+34%/yr @ 10bp, 2022 −46%→−24%). Used by
  matched-cadence accounts **`zscore10d_biweekly`** (the validated
  10d/biweekly config), **`zscore5d_weekly`** (5d/weekly), **`zscore1d_daily`** (1d/daily) — all regime-filtered,
  keys `APCA_*_{ZSCORE10D_BIWEEKLY,ZSCORE5D_WEEKLY,ZSCORE1D_DAILY}` live in `.env`. **Seed-only modes** (the initial
  basket, no longer the live steady state): `{kind:top_n,n,size_pct}` (hold the N highest current-scored
  names), `{kind:model_equal,source,gross}` (equal-weight a source account's holdings), `{kind:score_gate,
  min_score,size_pct}` (hold every name whose current score ≥ min_score). Seed modes accumulate (dropouts
  reconciled to 0); same reconcile/submit/cron path. Create via `broker_sync.py --create-account
  --target-mode {top_n|model_equal|score_gate|model_v4|score_gate_rampup|score_rebalance}
  [--graduate-at … | --lookback-days/--top-n/--bottom-n/--rebalance …] …`. **To set up a NEW paper
  account, follow the step-by-step runbook `deploy/new_account_runbook.md`** (keys → create → verify
  → run-the-live-path-for-real → dry-run → submit → reconcile, with the gotchas). Also:
  **Scheduling — ACTIVE = launchd. TWO trading events/day, split by cadence.** **(1) PRE-OPEN** —
  `com.mv4.preopen` runs `deploy/preopen_rebalance.sh` ~1 hr before the open — rebalances
  the **CALENDAR books** (`weekly10`, `combo20`, `zscore5d_weekly`, `zscore10d_biweekly`, `monthly10`) **AT
  THE OPEN**: scored off the last completed close and submitted as **limit-on-open** (`opg`, via
  `--submit-plan … --auction` + `BROKER_REBALANCE_PREOPEN=1`) so every leg fills in the **9:30 ET opening
  auction**. **TZ-robust schedule:** launchd fires at 07:30/08:00/08:30 **local** (brackets the ET pre-open
  whether the host is on ET/CT/MT), and the script gates the actual trade on the **broker clock** (market
  closed, next open today, ≤100 min away) + a once-per-ET-day lock — so exactly one in-window run trades and
  a host-TZ change can't fire it at the wrong moment. `BROKER_REBALANCE_PREOPEN=1` makes `_recent_trading_days()` append the UPCOMING session, so the
  rebalance gate + combo month-anchor evaluate the session about to open (scoring still uses the last
  completed close via `_valid_before`) — each book **self-gates** to its own first-of-period day and no-ops
  otherwise, and `submit_session` forces every leg's tif to `opg`. **(2) CLOSE** — `com.mv4.eod` runs
  `deploy/eod_finalize.sh` at **16:05 ET** — trades only the **close books** (the model_v4 accounts +
  `zscore1d_daily`) off the CLOSE via `--submit-plan … --extended-hours` (fills now), then **reconciles +
  reports ALL 9** (the calendar books' open fills are captured here) → refresh model_v4 → `eod-accounts` PDF
  → git commit. `com.mv4.midday` (12:30 ET) runs `deploy/midday_summary.sh` (read-only). The agents raise the
  fd `ulimit` (launchd's ~256 default broke the model_v4 decision) and rerun a missed job on wake; install
  via `cp deploy/com.mv4.*.plist ~/Library/LaunchAgents/ + launchctl bootstrap gui/$(id -u) …`. The **open
  (9:35) + retry (10:05) intraday-topup agents were REMOVED** — no mid-session trading. **Legacy/superseded (moved to `archive/`):** `archive/broker_cron.py`
  (open/retry/close/midday/auto wrapper, dry-run unless `--live`) + `archive/mv4_crontab.txt` remain for
  reference only. (`--submit-plan … --extended-hours` = the EOD agent's FILL-NOW pass: marketable
  `extended_hours` day orders for the current session, crossing the spread at the wider retry collar.)
  `run.py midday --account <name>` renders the intraday Midday Pulse PDF from the account's own ledger
  (read-only; `--prepost` for extended-hours marks). **On-demand `run.py midday`/`eod`/`midday-summary` renders for the
  scenario AND every account go to the unified `reports/midday/` & `reports/eod/` folders (named by
  book: `midday_<account|scenario>_<date>.pdf`). The hash-verified ledger copies under
  `accounts/<name>/reports/` (written by account-freeze/continue) are separate and unchanged.**
  For a LIVE midday render of a broker account, `broker_sync.apply_live_broker_marks()` **rebuilds the
  held book from the Alpaca positions** (source of truth — so names held at the broker but not yet
  reconciled into the ledger still show), each with `entry_price`←avg_entry (what was paid),
  `current_price`←live; pv/cash←account, held-DW recomputed, and the **portfolio 1-day return =
  equity / last_equity − 1** — so intraday returns reflect actual fills, not the (possibly 1-day-old)
  ledger equity curve. Windowed benchmark returns (1D/5D/MTD) anchor to the **price calendar**, so
  SPY/QQQ stay correct even for a brand-new account. It also **strips the synthetic overlay hedge**
  (`d["hedge"]=None`, removes the injected hedge BUY/SELL, recomputes held_avg/held_dw from the real
  positions) — accounts don't trade the model_v4 hedge, so it must not show a hedge line or hedge P&L.
  Applied on every live account render (midday/EOD `run` + the summaries); the model_v4 *scenario*
  keeps the hedge (it's part of that book).
- **Hedge in model_v4 reports** — `build_report` surfaces `d["hedge"]` = the overlay hedge (**SQQQ**,
  −3x inverse QQQ) suggested **as of the PRIOR close** (`_hedge_as_of(rank_close)` — the hedge ACTIVE
  over the session being viewed, since it's a 1-day overlay suggested at close → held next session),
  NOT the latest close. PURCHASE price = that prior close; `now` = the mark; `today` = the move
  between them. The EOD/midday reports show it as a flagged **held-book line item** (labeled just
  "hedge" — no ticker) and an **attribution line** (OVERLAY HEDGE section + contribution). The
  intraday-paths page leads with an **SPY/QQQ benchmarks** table. The hedge return is **folded into
  the held-book TOTAL** in BOTH rollups: `held_dw` (dollar-weighted — value-weighted by hedge notional)
  and `held_avg` (equal-weight — one extra line item); `held_dw_book` keeps the pre-hedge book return
  for the attribution waterfall (Book $-wt → +hedge contribution → Book incl. hedge = `held_dw`). A
  fired hedge is treated as a **real prior-close trade**: cash ↓ by the purchase cost, pv += its
  mark-to-market P&L, and the buy appears in the transactions (`recent_trades` + the midday tx table).
  The PORTFOLIO/"Session so far" returns (`stats[*]["port"]`) are also **hedge-inclusive** — each
  window's endpoint is scaled to the hedge-inclusive pv — so the session return lines up with the
  Portfolio card and the held-book TOTAL (the residual gap to held_dw is just cash, which the
  portfolio return includes and the held-book return excludes). **EOD exit:** the hedge is a 1-day
  overlay sold at the session close — `build_report(at_close=True)` (passed by the EOD render
  `pdf_report.run`) books a **hedge SELL at the close** with realized P&L, returns the proceeds to
  cash, and flattens it (held-book line shows "SOLD at close"); guarded by `_close_is_final(mark)`
  so it only sells when the official close is available (past dates, or ≥16:00 ET today) — never on
  a mid-session provisional bar, and never in the midday report (which keeps the hedge held).
  The hedge instrument is **fetched intraday** (anchored to its prior close), so the attribution Hedge
  row shows a full intraday path, not just the closing mark. (The
  up-shock+vol GATE still comes from `hedge_overlay.recommend`. The hedge instrument is **SQQQ** by
  default — `HedgeConfig.hedge_ticker` (the held/shown/traded ETF) is decoupled from `HedgeConfig.product`
  (the inverse-vol SIZING-PANEL key, still `soxs`), so the displayed/traded hedge is SQQQ without needing
  to rebuild the sizing panel; `broker_sync.HEDGE_SYM` is `SQQQ` too.)
- **Research artifacts** — `reports/` (dated EOD/status PDFs+md) and `backtests/` (dated
  CSVs/md) are generated outputs; regenerate, don't hand-edit. Current report/PDF tooling:
  `research/make_model_v4_guide.py`, `research/make_hedge_recommendation.py`, `research/make_rolling_chart.py`,
  `research/make_cycle_test.py`, `research/make_levetf_corr_tails.py` (the **corr_tails-by-horizon** report, rebuilt to ask
  *which trailing **model_v4 metrics** (scores/spread/baskets/vol from `model_v4_timeseries.csv`) predict
  forward **TQQQ** and **SQQQ** moves* — analysed separately per ETF, target = the ETF's own price return;
  correlation heatmap + tail UP/DN-gap call-outs → `reports/corr_tails_levetf.pdf`. The original model_v4
  corr_tails generator was a lost one-off). `research/make_levetf_volstate.py` backtests the **vol-state tilt** that
  finding implies (TQQQ-or-cash by QQQ realized-vol z-score; the robust rule is **risk-OFF** — hold TQQQ in
  calm, cash in vol spikes — not buy-the-stress; never hold SQQQ) → `reports/levetf_volstate.pdf`.
  `research/make_levetf_shock.py` backtests a 1-day vol-gated **shock-reversal** (buy TQQQ if QQQ −1d<−2% & rel-vol≥0.75;
  buy SQQQ if +2% & rel-vol≥0.75; hold 1d) → `reports/levetf_shock.pdf` — strong in 2018-2022 (Sharpe 1.2) but
  loses in 2022-2026 (regime-dependent, does NOT survive OOS). `research/make_model_v4_defense.py` compares two
  same-day sell-off defenses on the model_v4 book — **A** a fast (10d) de-risk-to-cash governor vs **B** a
  structural 1-day SQQQ tranche (QQQ −2% & <200d MA & vol-z≥0.75) — vs no overlay → `reports/model_v4_defense.pdf`.
  Finding: **A** (cash) is the only one that defends (volatile-window Sharpe 0.74→0.82, MaxDD −34%→−29%,
  worst-day −9%→−6%); **B** (inverse ETF) *hurts* in stress and only 39% of fires win — buying SQQQ into
  sell-offs sells the bottom. Defend with exposure reduction, not inverse ETFs.
  `research/make_model_v4_reverse.py` tests the hedge **in reverse** (down-shock → buy TQQQ for the rebound) as a
  model_v4 overlay, sweeping the TQQQ hold length → `reports/model_v4_reverse.pdf`. The 1-day bounce edge is
  real (60% win, +1.24%/bet) and boosts raw return, but it's **leverage, not alpha** — full-sample Sharpe is
  flat and tail risk worsens (worst-day −9%→−22%); **1-day hold is best, longer holds are strictly worse**
  (Sharpe degrades monotonically to +0.90, MaxDD blows to −65% at 20d) — the rebound is a next-day effect.

**Standing constraints:** paper trading only (no live orders); never mutate the base live-state
files `data/{trade_log.csv,positions.csv,portfolio_state.json}`; API keys live ONLY in gitignored
`.env` (never commit — verify with `git ls-files | grep -E '(^|/)\.env$|llm_cache'`); commit only
when asked; pushes to GitHub must be run by the user (they fail in the agent environment).

## Running

All runners share one entry point — `python run.py <command>` (see `python run.py -h`):

```bash
cd ai-paper-trader
pip install -r requirements.txt
# Optional dev tool: `brew install poppler` to preview the generated report PDFs locally
# (pdftoppm — required for the Read tool to rasterize reports/*.pdf; not needed to RUN anything).

python run.py account-freeze --name primary --scenario model_v4 --start … --end …  # freeze a scenario's trades+state over a window into an IMMUTABLE account ledger (accounts/<name>/: trades/equity/positions/rankings + rendered reports + manifest hashes); survives model/config changes & price revisions. account-verify --name <n> checks integrity. Reports read it via build_report(..., account=<n>)
python run.py account-continue --name primary --end … [--scenario <model>]          # extend a living account forward from its latest state (seeds cash/positions/governor; resets transient streak state at the seam). Appends under continuation/, leaves the frozen core untouched, AND renders+archives that day's EOD+status reports; --scenario defaults to the account base (pass current model to "follow active")
python run.py eod  [--account <name> | --scenario <s> --start … --end …] [--prepost]  # render the end-of-day PDF — from a frozen/living account ledger, or a fresh scenario run. --prepost marks the latest bar to the after-hours print (live session only)
python run.py midday [--account <name> | --scenario <s> --start … --end …] [--prepost] # render the intraday Midday Pulse PDF — account mode marks the locked book to today's provisional price; --prepost marks to the latest extended-hours (pre/post-market) print (VWAP of last few 1-min bars, stamped "HH:MM ET post-market")
python run.py agent                                          # live daily agent
python run.py status                                         # read-only ops dashboard: per broker account keys (ok/placeholder/MISSING)+live equity/cash, launchd agents loaded, last /tmp/mv4_*.log line, git tree state (src/status_check.py)
python run.py backtest           --start … --end …           # backtest + diagnostics + sensitivity
python run.py experiments        --start … --end …           # strategy experiment profiles
python run.py ticker-experiments --start … --end …           # grouped ticker overrides vs capital-matched BH
python run.py calibrate          --start … --end …           # per-ticker timing vs buy-and-hold (walk-forward)
python run.py evaluate           --start … --end … [--criteria FILE]  # score a fixed criteria file (no re-fitting)
python run.py active --train-start … --train-end … --test-start … --test-end …  # ticker active-vs-BH grid + portfolio, OOS
python run.py screen --train-start … --train-end … --test-start … --test-end …  # factor screen: rank candidate signals by OOS rank-IC
python run.py suite  --train-start … --train-end … --test-start … --test-end …  # run the whole stack once -> one consolidated summary report
python run.py scenario davids_model --start … --end …                            # run a named scenario (config/scenarios/<name>.yaml); incl. sensitivity + auto charts + auto status&rank report; --no-sensitivity / --no-charts / --no-status to skip
python run.py rank <name> [--start … --end …] [--top N]                          # status & rank report: top/bottom ranks + signal strength + held book vs SPY/QQQ (dated md + csv)
python src/pdf_report.py --scenario <name> --start … --end …                     # professional end-of-day PDF update (auto-generated commentary + recommendations, rankings, holdings, activity); also auto-written on every scenario run as reports/eod_<name>_<date>.pdf
python src/pdf_report.py --scenario <name> --start … --end … --series [--sim-start … --workers N]  # one EOD COVER page per trading day over [start,end] into a single combined PDF (parallelized, no look-ahead) — for backtesting an agent's read-and-act loop; run_cover_series() also returns the per-date specs
python src/midday_pdf.py --scenario <name> --start … --end …                     # intraday "Midday Pulse" PDF (2 pages): current book moves today, is the signal working so far (top-vs-bottom spread intraday), what's NOT behaving as expected, signal scoreboard. Provisional prices; writes reports/midday_<name>_<date>.pdf
python src/agent_backtest.py --scenario <name> --start … --end … [--no-llm --settings strict,balanced,discretionary --model … --context macro,news]  # backtest an AI agent reading the daily packet and acting under 3 settings; harness owns all fills/accounting, agent emits only structured trades; scores each setting vs the model & SPY/QQQ + logs divergences (writes reports/agent_backtest_*.md). LLM path needs ANTHROPIC_API_KEY; --no-llm uses deterministic stand-ins. --context injects info sources (macro=key-free; news needs FINNHUB_API_KEY)
python src/context_matrix.py --scenario <name> --start … --end … [--sources macro,news --settings balanced,discretionary --model … --repeats N --max-combo-size K --oos-window S:E]  # context-source SENSITIVITY MATRIX: sweeps the power set of context sources × behavior settings, reports return-vs-strict per combo (strict = fixed reference). Builds specs once + caches fetches. Writes reports/context_matrix_*.md/.csv/.json; --repeats adds a noise band, --oos-window re-checks top combos on a disjoint range
python run.py adaptive --start … --end … [--rebalance-days N --lookback-days N --top-n N]  # per-ticker weekly rotating-signal backtest (auto-writes per-ticker charts; --no-charts to skip)
```

`src/scenario_charts.py` renders per-ticker annotated price charts (▲buys/▼sells + reasons, held-period
shading, active-vs-buy-and-hold) — used standalone (`python src/scenario_charts.py --scenario <name> [--since …]`)
and auto-invoked by the `adaptive` command (reusing the already-fetched price panel).

Named scenarios live in `config/scenarios/<name>.yaml` (trimmed universe + per-ticker `ticker_groups`
overrides on the base config); `src/scenarios.py` loads + overlays them and runs a scenario-tagged
backtest. `davids_model` = the OOS-robust trimmed universe (MSFT/ORCL/CRWD) with per-ticker exits.
`model_v4_rebalance` = model_v4's universe+ranker but a **daily top-10 rebalance** replaces the
entry/exit logic: a scenario `rebalance: {top_n: 10}` block flips `run_backtest` into rebalance mode —
each close the book = today's top-10; dropouts are sold and entrants bought equal-weight
(`max_total_exposure / N`) as a next-close swap; **stayers are never sold or trimmed** (membership-only);
model_v4's stops/persistence/vol-targeting are bypassed. Always holds 10 positions.
`LevEtf` = a 2-ticker **leveraged-ETF** scenario (TQQQ +3× / SQQQ −3× QQQ) running model_v4's rules
pre-adapted for 3× leverage (`max_position_pct: auto` → ~0.45/name, `stop_loss: 0.25`, `target_vol: 0.60`);
fully isolated from model_v4 (own universe + name-tagged outputs). Studied via the standard exercise
(`scenario LevEtf` + `experiments --scenario LevEtf`) over 2018-2026 — the momentum rules get whipsawed
on the inverse 3× pair (baseline +25% vs QQQ +342%). The `experiments` command now takes an optional
`--scenario <name>` to overlay a scenario's universe/rules (default off = base config).

Per-ticker timing criteria live in `config/ticker_timing_criteria.yaml` (seed). `calibrate` writes a
dated, data-derived `config/ticker_timing_criteria_<date>.yaml`; `evaluate` applies any such file
over a chosen (ideally held-out) window.

Dispatch lives in `src/cli.py`; each module also exposes `run(start, end[, output])` and is still
runnable directly (e.g. `python src/backtest.py …`).

## Testing

```bash
pytest tests/ -v
```

## Project layout

| Path | Purpose |
|------|---------|
| `config/universe.yaml` | Fixed ticker universe |
| `config/strategy.yaml` | All risk and signal parameters |
| `data/positions.csv` | Open paper positions (updated each run) |
| `data/portfolio_state.json` | Cash balance (updated each run) |
| `data/trade_log.csv` | Append-only audit log of every recommendation |
| `reports/` | Daily Markdown reports |
| `src/` | Application source — one module per concern |
| `tests/` | pytest unit tests |

## Module map

- `main.py` — orchestrator; run this
- `market_data.py` — yfinance wrapper
- `signals.py` — momentum signal calculation and ranking
- `risk.py` — pure functions: sizing, slippage, exit triggers, exposure
- `portfolio.py` — state I/O, exit evaluation, entry generation
- `report.py` — Markdown report builder
- `logger.py` — logging setup + trade log appender

## Key constraints

- Paper trading only — recommendations, not live orders
- U.S. equities and ETFs; no options
- Fixed universe defined in `config/universe.yaml`
- All recommendations logged to `data/trade_log.csv`
