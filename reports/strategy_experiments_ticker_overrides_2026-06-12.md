# Strategy Experiments — Grouped Ticker Overrides
**Period:** 2021-06-12 → 2026-06-12  |  **Generated:** 2026-06-12

> ⚠️ **IN-SAMPLE only**, one historical window. No profile is claimed superior. Group assumptions are broad behaviour buckets, not fitted parameters. Validate out-of-sample before acting.

---

## Strategy vs Buy-and-Hold Test

_Does each active strategy beat passively owning the same universe — including on an exposure-adjusted basis? ✅/❌ per profile._

| Test | baseline | trailing_stop_baseline | grouped_ticker_overrides_v1 | grouped_ticker_overrides_conservative | grouped_ticker_overrides_aggressive | grouped_signal_weights_only | grouped_signals_plus_exits |
|------|---|---|---|---|---|---|---|
| Beat SPY | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Beat QQQ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Beat equal-weight BH | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Beat capital-matched EW | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Lower DD than EW BH | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Higher Sharpe than EW BH | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Positive quintile spread | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

_Equal-weight BH of the universe: return +278.35%, max DD -41.79%, Sharpe 1.09. Capital-matched targets each profile's own average exposure._

## Returns & Risk

| Profile | Ending Bal | Total Ret | Annualized | Max DD | Sharpe | Calmar | Avg Exp | Peak Exp | β QQQ | ρ QQQ | Up-cap | Down-cap |
|---------|-----------|-----------|------------|--------|--------|--------|---------|----------|-------|-------|--------|----------|
| baseline | $160,200 | +60.20% | +9.92% | -19.39% | 0.97 | 0.51 | +40.39% | +66.08% | 0.39 | 0.86 | 0.45 | 0.43 |
| trailing_stop_baseline | $202,539 | +102.54% | +15.21% | -23.95% | 1.13 | 0.64 | +51.70% | +77.74% | 0.50 | 0.86 | 0.59 | 0.55 |
| grouped_ticker_overrides_v1 | $200,735 | +100.74% | +15.01% | -29.09% | 1.04 | 0.52 | +55.19% | +79.68% | 0.55 | 0.86 | 0.64 | 0.61 |
| grouped_ticker_overrides_conservative | $188,273 | +88.27% | +13.54% | -22.71% | 1.11 | 0.60 | +47.26% | +74.64% | 0.46 | 0.86 | 0.53 | 0.50 |
| grouped_ticker_overrides_aggressive | $203,892 | +103.89% | +15.37% | -31.79% | 0.98 | 0.48 | +59.32% | +79.64% | 0.61 | 0.87 | 0.70 | 0.68 |
| grouped_signal_weights_only | $142,118 | +42.12% | +7.31% | -19.92% | 0.75 | 0.37 | +38.70% | +59.54% | 0.39 | 0.87 | 0.43 | 0.43 |
| grouped_signals_plus_exits | $176,503 | +76.50% | +12.07% | -28.44% | 0.89 | 0.42 | +52.28% | +76.65% | 0.53 | 0.87 | 0.60 | 0.59 |
| _SPY buy & hold_ | $186,752 | +86.75% | +13.35% | -24.50% | — | 0.55 | — | — | — | — | — | — |
| _QQQ buy & hold_ | $215,761 | +115.76% | +16.68% | -35.12% | — | 0.48 | — | — | — | — | — | — |
| _Equal-weight BH (100%)_ | $378,346 | +278.35% | +30.60% | -41.79% | 1.09 | 0.73 | — | — | — | — | — | — |
| _EW BH 75% / 25% cash_ | $308,759 | +208.76% | +25.38% | -33.18% | 1.11 | 0.76 | — | — | — | — | — | — |
| _EW BH capital-matched to trailing_stop_baseline (+51.70%)_ | $243,910 | +143.91% | +19.59% | -24.20% | 1.12 | 0.81 | — | — | — | — | — | — |
| _EW BH capital-matched to grouped_ticker_overrides_v1 (+55.19%)_ | $253,612 | +153.61% | +20.53% | -25.61% | 1.12 | 0.80 | — | — | — | — | — | — |
| _EW BH capital-matched to grouped_ticker_overrides_conservative (+47.26%)_ | $231,538 | +131.54% | +18.35% | -22.36% | 1.12 | 0.82 | — | — | — | — | — | — |
| _EW BH capital-matched to grouped_ticker_overrides_aggressive (+59.32%)_ | $265,114 | +165.11% | +21.61% | -27.25% | 1.12 | 0.79 | — | — | — | — | — | — |
| _EW BH capital-matched to grouped_signal_weights_only (+38.70%)_ | $207,721 | +107.72% | +15.80% | -18.71% | 1.13 | 0.84 | — | — | — | — | — | — |
| _EW BH capital-matched to grouped_signals_plus_exits (+52.28%)_ | $245,509 | +145.51% | +19.75% | -24.43% | 1.12 | 0.81 | — | — | — | — | — | — |

## Trading Activity

| Profile | Trades | / month | Win Rate | Avg Win | Avg Loss | PF | Avg Hold | Slippage | Largest Win | Largest Loss |
|---------|--------|---------|----------|---------|----------|----|----------|----------|-------------|--------------|
| baseline | 1971 | 32.86 | +53.16% | $422 | $-349 | 1.37 | 15.35 | $8,079 | $1,356 | $-1,215 |
| trailing_stop_baseline | 1051 | 17.52 | +41.81% | $931 | $-369 | 1.81 | 34.47 | $4,693 | $7,763 | $-1,123 |
| grouped_ticker_overrides_v1 | 1128 | 18.80 | +46.42% | $835 | $-405 | 1.78 | 31.86 | $5,293 | $8,734 | $-1,382 |
| grouped_ticker_overrides_conservative | 1169 | 19.49 | +46.72% | $700 | $-342 | 1.80 | 30.23 | $4,843 | $6,374 | $-1,106 |
| grouped_ticker_overrides_aggressive | 1043 | 17.39 | +44.47% | $944 | $-420 | 1.80 | 35.22 | $4,889 | $10,674 | $-1,469 |
| grouped_signal_weights_only | 1844 | 30.74 | +51.09% | $401 | $-326 | 1.29 | 15.72 | $7,136 | $1,526 | $-1,162 |
| grouped_signals_plus_exits | 1084 | 18.07 | +44.51% | $766 | $-373 | 1.65 | 31.36 | $4,604 | $8,264 | $-1,077 |

## Signal Effectiveness

_Does composite ranking actually sort winners from losers? Exit/sizing-only profiles share the baseline's ranking (identical spreads); the per-group `signal_weights` profiles re-rank and should move the spread if they help._

| Profile | corr 5d | corr 10d | corr 20d | Spread 5d | Spread 10d | Spread 20d |
|---------|---------|----------|----------|-----------|------------|------------|
| baseline | 0.00 | 0.01 | 0.00 | +0.01% | +0.01% | -0.01% |
| trailing_stop_baseline | 0.00 | 0.01 | 0.00 | +0.01% | +0.01% | -0.01% |
| grouped_ticker_overrides_v1 | 0.00 | 0.01 | 0.00 | +0.01% | +0.01% | -0.01% |
| grouped_ticker_overrides_conservative | 0.00 | 0.01 | 0.00 | +0.01% | +0.01% | -0.01% |
| grouped_ticker_overrides_aggressive | 0.00 | 0.01 | 0.00 | +0.01% | +0.01% | -0.01% |
| grouped_signal_weights_only | 0.01 | 0.01 | -0.00 | +0.18% | +0.22% | -0.06% |
| grouped_signals_plus_exits | 0.01 | 0.01 | -0.00 | +0.18% | +0.22% | -0.06% |

**Baseline avg forward return / win rate by composite quintile (5 = top):**

| Quintile | Avg fwd 20d | Win 20d |
|----------|-------------|---------|
| Q1 | +2.72% | +57.91% |
| Q2 | +2.40% | +59.16% |
| Q3 | +2.22% | +56.88% |
| Q4 | +2.42% | +57.65% |
| Q5 | +2.71% | +55.83% |

## P&L Attribution

| Profile | financial_crypto_beta | mega_cap_growth | semiconductors | software_cybersecurity | Top-3 share | Semis share |
|---------|---|---|---|---|---|---|
| baseline | $3,254 | $17,379 | $17,998 | $3,958 | +39.31% | +29.90% |
| trailing_stop_baseline | $8,526 | $24,239 | $29,893 | $11,892 | +31.21% | +29.15% |
| grouped_ticker_overrides_v1 | $11,311 | $23,599 | $59,104 | $6,722 | +35.89% | +58.67% |
| grouped_ticker_overrides_conservative | $14,496 | $22,894 | $44,060 | $6,823 | +31.67% | +49.91% |
| grouped_ticker_overrides_aggressive | $9,998 | $19,437 | $69,579 | $4,878 | +44.53% | +66.97% |
| grouped_signal_weights_only | $4,623 | $12,932 | $20,278 | $4,285 | +37.83% | +48.15% |
| grouped_signals_plus_exits | $3,902 | $16,806 | $47,595 | $8,200 | +41.43% | +62.21% |

- **baseline** — top: `NVDA` $8,914, `MU` $8,871, `AMD` $5,878, `NFLX` $4,944, `TSM` $4,691
  worst: `BAC` $-334, `MSFT` $-143, `AAPL` $-115, `ORCL` $296, `AMZN` $642
- **trailing_stop_baseline** — top: `AMD` $12,024, `MU` $11,502, `PANW` $8,481, `TSM` $6,992, `NVDA` $6,940
  worst: `MSFT` $-738, `JPM` $1,181, `BAC` $1,548, `META` $2,239, `ORCL` $2,780
- **grouped_ticker_overrides_v1** — top: `AMD` $14,379, `MU` $12,985, `NVDA` $8,793, `TSM` $8,164, `AVGO` $7,427
  worst: `MSFT` $-644, `BAC` $497, `ORCL` $1,692, `CRWD` $1,799, `AMZN` $1,808
- **grouped_ticker_overrides_conservative** — top: `AMD` $11,942, `MU` $9,635, `NVDA` $6,382, `COIN` $6,145, `TSM` $5,827
  worst: `MSFT` $-152, `BAC` $679, `AMZN` $1,354, `CRWD` $1,773, `ORCL` $1,819
- **grouped_ticker_overrides_aggressive** — top: `MU` $17,520, `AMD` $15,292, `NVDA` $13,446, `AVGO` $9,966, `ASML` $8,139
  worst: `AMZN` $104, `MSFT` $291, `BAC` $712, `CRWD` $946, `AAPL` $1,088
- **grouped_signal_weights_only** — top: `MU` $7,028, `NVDA` $4,594, `NFLX` $4,308, `COST` $3,334, `COIN` $3,142
  worst: `BAC` $-1,518, `AMZN` $-537, `ORCL` $58, `AAPL` $154, `JPM` $722
- **grouped_signals_plus_exits** — top: `MU` $13,109, `AMD` $11,696, `AVGO` $6,893, `NVDA` $5,658, `ASML` $5,358
  worst: `BAC` $-269, `MSFT` $197, `ORCL` $365, `AMZN` $449, `JPM` $528

_(Full per-ticker P&L in the CSV.)_

## Ticker-Level Behaviour (baseline — basis for group assumptions)

_MFE = peak unrealized gain; MAE = worst unrealized drawdown; giveback = MFE − realized._

| Ticker | Trades | Total P&L | Win% | PF | Avg Hold | Avg MFE | Med MFE | Avg MAE | Med MAE | Avg Giveback | SL/TP/Trail/Hold | Stop→re-entry |
|--------|--------|-----------|------|----|----------|---------|---------|---------|---------|--------------|------------------|---------------|
| NVDA | 59 | $9,173 | +62.71% | 2.06 | 12.61 | +8.75% | +10.46% | -5.00% | -4.83% | +4.67% | 22/34/0/5 | 6 |
| MU | 60 | $8,602 | +58.33% | 1.85 | 11.46 | +7.88% | +10.14% | -4.96% | -3.72% | +4.97% | 23/33/0/5 | 3 |
| AMD | 70 | $5,878 | +50.00% | 1.42 | 9.21 | +8.12% | +9.66% | -5.65% | -6.18% | +6.17% | 33/35/0/2 | 8 |
| NFLX | 43 | $5,013 | +67.44% | 2.08 | 16.13 | +7.09% | +8.13% | -4.46% | -3.60% | +4.07% | 12/20/0/13 | 2 |
| TSM | 45 | $4,487 | +55.56% | 1.70 | 17.43 | +7.05% | +8.05% | -5.22% | -5.32% | +4.97% | 16/19/0/12 | 2 |
| AVGO | 51 | $3,249 | +52.94% | 1.35 | 15.95 | +7.04% | +6.09% | -5.76% | -6.48% | +5.30% | 21/21/0/9 | 6 |
| META | 40 | $3,160 | +57.50% | 1.53 | 15.77 | +7.44% | +8.03% | -4.84% | -4.23% | +5.20% | 14/18/0/8 | 1 |
| COST | 34 | $3,055 | +64.71% | 2.18 | 24.96 | +5.82% | +5.59% | -3.47% | -2.45% | +3.32% | 7/9/0/18 | 1 |
| GOOGL | 35 | $2,946 | +57.14% | 1.62 | 20.38 | +6.73% | +6.93% | -4.32% | -3.05% | +5.07% | 11/10/0/15 | 2 |
| PANW | 44 | $2,761 | +52.27% | 1.39 | 18.46 | +7.09% | +7.31% | -5.25% | -3.95% | +5.83% | 15/16/0/14 | 4 |
| COIN | 88 | $2,756 | +45.45% | 1.14 | 5.16 | +7.41% | +4.91% | -6.27% | -8.05% | +6.53% | 48/40/0/0 | 16 |
| GS | 36 | $2,477 | +55.56% | 1.58 | 20.45 | +6.10% | +5.68% | -4.51% | -4.35% | +4.68% | 11/12/0/13 | 1 |
| TSLA | 57 | $2,308 | +50.88% | 1.20 | 11.00 | +7.53% | +7.87% | -6.10% | -6.48% | +6.42% | 27/26/0/4 | 6 |
| ASML | 44 | $2,038 | +47.73% | 1.28 | 15.17 | +6.80% | +8.38% | -5.72% | -5.89% | +6.04% | 20/17/0/7 | 5 |
| CRWD | 56 | $1,203 | +48.21% | 1.11 | 12.68 | +6.70% | +8.42% | -6.11% | -7.28% | +6.27% | 28/23/0/5 | 4 |
| AMZN | 38 | $642 | +57.89% | 1.14 | 20.23 | +5.26% | +4.40% | -4.96% | -4.82% | +4.94% | 13/9/0/16 | 2 |
| JPM | 34 | $629 | +50.00% | 1.16 | 21.66 | +4.74% | +2.84% | -4.91% | -5.73% | +4.47% | 12/7/0/15 | 4 |
| ORCL | 40 | $296 | +47.50% | 1.04 | 17.77 | +6.59% | +6.69% | -5.34% | -4.70% | +6.23% | 18/13/0/9 | 1 |
| MSFT | 33 | $-143 | +48.48% | 0.97 | 22.50 | +5.23% | +4.91% | -4.53% | -4.27% | +5.12% | 11/7/0/15 | 2 |
| AAPL | 34 | $-184 | +47.06% | 0.96 | 21.18 | +5.25% | +4.65% | -5.28% | -5.87% | +5.75% | 13/8/0/14 | 3 |
| BAC | 39 | $-417 | +46.15% | 0.93 | 20.31 | +5.48% | +4.24% | -4.84% | -5.66% | +5.60% | 15/8/0/16 | 3 |

## Interpretation

**Ticker-specific assumptions:** best grouped profile is `grouped_ticker_overrides_aggressive` (+103.89%, +43.69% vs baseline). Grouped exits mainly widen winner-capture and lengthen holds; they change *exits/sizing*, not the ranking.

**Fair (exposure-adjusted) test:** no active profile beat its capital-matched equal-weight benchmark. At equal exposure, simply owning the universe did as well or better — the active selection is **not** clearly adding value here; most of any return difference is exposure timing.

**Ticker-specific signal weights:** did **not** widen the 20d quintile spread beyond baseline (-0.01%). Per-group ranking did not improve cross-sectional selection here, so the universe-wide signal is no worse than group-specific weighting.

**Signal alpha:** the 20d top-minus-bottom quintile spread is -0.01% (≤ 0), so higher-ranked names did **not** clearly outperform lower-ranked ones. The active strategy is not demonstrating signal alpha, even where total return improves — gains are coming from exits/exposure, not ranking.

**Concentration / overfitting:** P&L is concentrated — `grouped_ticker_overrides_aggressive` draws +44.53% of net P&L from its top 3 names and +66.97% from semiconductors. Edge that lives in a few names on one window is a classic overfitting risk; prefer broad-based results.

**Out-of-sample next:** re-run the grouped profiles on a disjoint period (and ideally a different universe slice). Watch whether (a) they still beat the capital-matched benchmark and (b) the quintile spread stays positive. Until then, treat every ranking here as in-sample and provisional.
