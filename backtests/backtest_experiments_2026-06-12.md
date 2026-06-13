# AI Paper Trader — Strategy Experiments
**Period:** 2021-01-01 → 2026-06-12  |  **Generated:** 2026-06-12

> ⚠️ **All results are IN-SAMPLE** on a single historical window. No profile is claimed superior. Validate out-of-sample before trusting any of these.

---

## Returns & Risk

| Profile | Total Return | Annualized | Max DD | Sharpe | vs SPY | vs QQQ |
|---------|--------------|------------|--------|--------|--------|--------|
| baseline | +65.15% | +9.69% | -19.42% | 0.96 | -50.90% | -75.47% |
| trend_reweighted | +54.00% | +8.29% | -19.49% | 0.87 | -62.05% | -86.61% |
| trend_reweighted_aggressive | +51.04% | +7.90% | -19.81% | 0.82 | -65.01% | -89.58% |
| score_weighted_sizing | +84.78% | +11.98% | -23.53% | 0.96 | -31.28% | -55.84% |
| higher_take_profit | +87.44% | +12.28% | -22.37% | 1.03 | -28.61% | -53.18% |
| high_take_profit | +93.72% | +12.96% | -24.23% | 1.06 | -22.33% | -46.90% |
| no_fixed_take_profit_trailing_stop | +94.43% | +13.04% | -23.46% | 1.10 | -21.62% | -46.18% |
| no_fixed_take_profit_wide_trailing_stop | +109.38% | +14.59% | -24.12% | 1.11 | -6.67% | -31.24% |
| vol_adjusted_momentum | +47.60% | +7.44% | -21.96% | 0.76 | -68.46% | -93.02% |
| qqq_trend_filter | +50.76% | +7.86% | -12.63% | 0.94 | -65.29% | -89.86% |
| stop_cooldown_5d | +49.65% | +7.71% | -21.41% | 0.81 | -66.41% | -90.97% |
| regime_voladj_higher_tp | +61.49% | +9.24% | -16.84% | 0.99 | -54.56% | -79.13% |
| _SPY (buy & hold)_ | +116.05% | +15.26% | -24.50% | — | — | — |
| _QQQ (buy & hold)_ | +140.62% | +17.57% | -35.12% | — | — | — |
| _Equal-Wt Hold_ | +358.95% | +32.43% | -39.53% | — | — | — |

## Trading Activity

| Profile | Trades | / month | Win Rate | Avg Win | Avg Loss | Profit Factor | Avg Hold | Slippage |
|---------|--------|---------|----------|---------|----------|---------------|----------|----------|
| baseline | 2115 | 32.38 | +52.95% | $428 | $-351 | 1.37 | 15.53 | $8,838 |
| trend_reweighted | 1974 | 30.23 | +51.53% | $422 | $-337 | 1.33 | 15.27 | $7,960 |
| trend_reweighted_aggressive | 1985 | 30.39 | +50.81% | $420 | $-330 | 1.32 | 15.40 | $7,909 |
| score_weighted_sizing | 2113 | 32.35 | +52.81% | $562 | $-459 | 1.37 | 15.55 | $11,541 |
| higher_take_profit | 1550 | 23.73 | +48.31% | $663 | $-403 | 1.54 | 25.06 | $6,939 |
| high_take_profit | 1382 | 21.16 | +45.91% | $765 | $-402 | 1.62 | 28.64 | $6,219 |
| no_fixed_take_profit_trailing_stop | 1261 | 19.31 | +41.53% | $790 | $-320 | 1.75 | 28.95 | $5,558 |
| no_fixed_take_profit_wide_trailing_stop | 1131 | 17.32 | +41.32% | $952 | $-374 | 1.79 | 34.84 | $5,142 |
| vol_adjusted_momentum | 1978 | 30.29 | +51.57% | $403 | $-331 | 1.29 | 16.04 | $7,845 |
| qqq_trend_filter | 1585 | 24.27 | +53.49% | $415 | $-340 | 1.41 | 16.50 | $6,492 |
| stop_cooldown_5d | 2029 | 31.07 | +51.88% | $403 | $-334 | 1.30 | 15.70 | $8,052 |
| regime_voladj_higher_tp | 1147 | 17.56 | +48.33% | $609 | $-365 | 1.56 | 26.32 | $4,770 |

## Exit Attribution

| Profile | Take-profit | Stop-loss | Trailing-stop | Max-hold | Gave back gains | Largest Win | Largest Loss |
|---------|-------------|-----------|---------------|----------|-----------------|-------------|--------------|
| baseline | 410 | 416 | 0 | 237 | 79 | $1,418 | $-1,268 |
| trend_reweighted | 381 | 395 | 0 | 214 | 84 | $1,775 | $-1,215 |
| trend_reweighted_aggressive | 383 | 404 | 0 | 214 | 107 | $1,704 | $-1,215 |
| score_weighted_sizing | 409 | 415 | 0 | 238 | 79 | $2,064 | $-1,782 |
| higher_take_profit | 288 | 377 | 0 | 104 | 138 | $1,548 | $-1,238 |
| high_take_profit | 192 | 349 | 0 | 145 | 134 | $2,422 | $-1,321 |
| no_fixed_take_profit_trailing_stop | 0 | 218 | 378 | 146 | 135 | $7,868 | $-1,101 |
| no_fixed_take_profit_wide_trailing_stop | 0 | 260 | 128 | 216 | 128 | $8,013 | $-1,145 |
| vol_adjusted_momentum | 366 | 400 | 0 | 230 | 99 | $1,595 | $-1,215 |
| qqq_trend_filter | 297 | 294 | 0 | 209 | 57 | $1,238 | $-1,215 |
| stop_cooldown_5d | 384 | 405 | 0 | 233 | 79 | $1,295 | $-1,215 |
| regime_voladj_higher_tp | 207 | 276 | 0 | 86 | 98 | $1,595 | $-952 |

## Signal Quality (composite-score quintile spread)

_Top-minus-bottom quintile forward-return spread; positive ⇒ higher-ranked names outperform._

| Profile | Spread 5d | Spread 10d | Spread 20d |
|---------|-----------|------------|------------|
| baseline | +0.00% | -0.05% | -0.13% |
| trend_reweighted | +0.14% | +0.02% | -0.23% |
| trend_reweighted_aggressive | +0.14% | +0.12% | -0.31% |
| score_weighted_sizing | +0.00% | -0.05% | -0.13% |
| higher_take_profit | +0.00% | -0.05% | -0.13% |
| high_take_profit | +0.00% | -0.05% | -0.13% |
| no_fixed_take_profit_trailing_stop | +0.00% | -0.05% | -0.13% |
| no_fixed_take_profit_wide_trailing_stop | +0.00% | -0.05% | -0.13% |
| vol_adjusted_momentum | +0.06% | +0.06% | -0.42% |
| qqq_trend_filter | +0.00% | -0.05% | -0.13% |
| stop_cooldown_5d | +0.00% | -0.05% | -0.13% |
| regime_voladj_higher_tp | +0.06% | +0.06% | -0.42% |

## P&L by Group

| Profile | financial_crypto_beta | mega_cap_growth | semiconductors | software_cybersecurity |
|---------|-----|-----|-----|-----|
| baseline | $3,617 | $19,027 | $18,023 | $4,824 |
| trend_reweighted | $2,709 | $8,940 | $18,588 | $5,176 |
| trend_reweighted_aggressive | $4,499 | $10,654 | $17,152 | $3,552 |
| score_weighted_sizing | $3,939 | $25,172 | $24,239 | $6,656 |
| higher_take_profit | $5,527 | $24,449 | $23,870 | $7,762 |
| high_take_profit | $7,124 | $24,183 | $24,600 | $9,639 |
| no_fixed_take_profit_trailing_stop | $10,112 | $23,553 | $28,407 | $6,370 |
| no_fixed_take_profit_wide_trailing_stop | $9,255 | $27,213 | $31,150 | $10,285 |
| vol_adjusted_momentum | $1,985 | $10,255 | $16,283 | $3,185 |
| qqq_trend_filter | $4,191 | $14,127 | $16,585 | $4,636 |
| stop_cooldown_5d | $2,979 | $16,029 | $13,998 | $2,162 |
| regime_voladj_higher_tp | $6,808 | $15,945 | $22,484 | $3,524 |

## Top / Bottom P&L Contributors

- **baseline** — top: `NVDA` $9,924, `MU` $8,792, `AMD` $6,178  |  worst: `AAPL` $-553, `BAC` $-160, `MSFT` $141
- **trend_reweighted** — top: `MU` $7,891, `AMD` $6,426, `CRWD` $5,494  |  worst: `AAPL` $-1,439, `AMZN` $-1,079, `PANW` $-318
- **trend_reweighted_aggressive** — top: `MU` $8,476, `AMD` $5,607, `CRWD` $4,336  |  worst: `PANW` $-784, `AMZN` $-688, `AAPL` $-399
- **score_weighted_sizing** — top: `NVDA` $12,614, `MU` $12,251, `AMD` $8,604  |  worst: `BAC` $-951, `AAPL` $-803, `MSFT` $27
- **higher_take_profit** — top: `MU` $11,005, `NVDA` $10,088, `AMD` $8,173  |  worst: `MSFT` $-435, `BAC` $895, `AMZN` $959
- **high_take_profit** — top: `MU` $10,500, `AMD` $8,850, `NVDA` $8,765  |  worst: `MSFT` $-849, `JPM` $996, `AMZN` $1,452
- **no_fixed_take_profit_trailing_stop** — top: `AMD` $13,300, `MU` $10,556, `NVDA` $7,356  |  worst: `MSFT` $78, `AMZN` $1,388, `JPM` $1,410
- **no_fixed_take_profit_wide_trailing_stop** — top: `AMD` $12,688, `MU` $12,231, `NVDA` $8,687  |  worst: `MSFT` $-793, `JPM` $1,338, `BAC` $1,958
- **vol_adjusted_momentum** — top: `MU` $7,488, `AMD` $6,049, `NVDA` $5,958  |  worst: `BAC` $-1,343, `PANW` $-1,270, `MSFT` $-911
- **qqq_trend_filter** — top: `MU` $7,284, `AMD` $5,967, `NVDA` $5,654  |  worst: `MSFT` $-1,740, `AMZN` $-1,119, `NFLX` $39
- **stop_cooldown_5d** — top: `NVDA` $8,746, `MU` $6,790, `AMD` $4,776  |  worst: `MSFT` $-664, `BAC` $-459, `AAPL` $-365
- **regime_voladj_higher_tp** — top: `MU` $12,068, `AMD` $6,178, `META` $5,386  |  worst: `AMZN` $-1,204, `ORCL` $-409, `AAPL` $797

_(Full per-ticker P&L is in `backtest_experiments_<date>.csv`.)_

## Interpretation

**Trend reweighting:** did **not** widen the 20d quintile spread beyond baseline (-0.13%); any return change came from exposure/timing, not better ranking.

**Score-weighted sizing:** return moved +19.63% vs baseline while max drawdown moved -4.11% (more negative = worse) and the single-name P&L concentration is +14.29%. If return rose mainly alongside higher concentration/drawdown, that is added **risk**, not added skill.

**higher_take_profit:** return +22.30% vs baseline, average win changed $235, largest winner $1,548, gave-back trades 138 (baseline 79). Higher avg/largest win with fewer give-backs ⇒ the old take-profit was clipping winners early.

**high_take_profit:** return +28.57% vs baseline, average win changed $337, largest winner $2,422, gave-back trades 134 (baseline 79). Higher avg/largest win with fewer give-backs ⇒ the old take-profit was clipping winners early.

**no_fixed_take_profit_trailing_stop:** return +29.29% and max drawdown -4.04% vs baseline, with 378 trailing-stop exits. Better return *and* no worse drawdown would favour letting winners run; better return with deeper drawdown is just more risk.

**no_fixed_take_profit_wide_trailing_stop:** return +44.23% and max drawdown -4.70% vs baseline, with 128 trailing-stop exits. Better return *and* no worse drawdown would favour letting winners run; better return with deeper drawdown is just more risk.

**Source / overfitting check:** the highest in-sample return is `no_fixed_take_profit_wide_trailing_stop` (+109.38%). Treat ranking by in-sample return with suspicion — prefer profiles that improve the quintile spread *and* hold up across tickers/groups.

**All figures above are in-sample.** No profile is recommended as superior; differences of this size are well within noise for a single historical window. Validate any promising profile on a separate out-of-sample period before acting.
