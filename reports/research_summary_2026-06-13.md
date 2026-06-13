# Research Suite — Consolidated Summary
**Train:** 2020-04-01 → 2022-02-01  |  **Test (OOS):** 2022-02-02 → 2026-06-13  |  **Generated:** 2026-06-13

> One run of the whole stack over a single train/test split. All TRAIN figures are in-sample; TEST is the out-of-sample verdict. For full per-stage detail, run that stage's own command (e.g. `run.py screen …`) — this suite summarises, it does not write the individual reports.

---

## Headline verdict

**A candidate signal cleared the out-of-sample screen** (reversal_21). There may be a real edge to build on — validate it end-to-end next.

## Most salient takeaway per stage

| Stage | Window | Salient result |
|-------|--------|----------------|
| Backtest | full | Strategy +121.91% vs EW-Hold +853.28% (SPY +227.81%, QQQ +309.69%); IRR +38.79%; max DD -19.52%; **20d quintile spread +0.06%**. Beat EW-Hold: ❌ |
| Experiments | full | 12 profiles; best `no_fixed_take_profit_wide_trailing_stop` +198.98%; beat EW-Hold: 0/12 |
| Ticker-experiments | full | 0/6 profiles beat capital-matched EW; 20d quintile spread +0.06% |
| Calibrate | train | 0/20 tickers beat hold OOS-in-folds; 1/20 candidate criteria: AMD |
| Evaluate (calibrated) | test | 5/20 beat hold; 9/20 beat exposure-matched hold |
| Evaluate (seed) | test | 3/21 beat hold; 7/21 beat exposure-matched hold |
| Active portfolio | test | 1/20 eligible; OOS +5.70% vs EW-eligible +316.72% / capital-matched +6.32%; beat capital-matched: ❌ |
| Signal screen | train+test | 1/14 factors survive OOS (candidates: reversal_21) |

## Signal screen — top 5 by OOS 20d rank IC

| Factor | OOS IC | t-stat |
|--------|--------|--------|
| reversal_21 | +0.035 | +3.9 |
| reversal_5 | +0.008 | +1.0 |
| vol_trend | +0.005 | +0.7 |
| accel_21_63 | +0.002 | +0.2 |
| mom_252_21 | -0.008 | -0.9 |

_IC ≈ 0 = no signal; |IC| ≳ 0.03 interesting, ≳ 0.05 strong._

## Recommended next step

- Build the next strategy around the surviving factor(s) (reversal_21): wire into the ranker, then re-run `active`/`evaluate` to confirm it survives end-to-end.
