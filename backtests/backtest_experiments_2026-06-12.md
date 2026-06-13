# AI Paper Trader — Strategy Experiments
**Period:** 2021-06-12 → 2026-06-12  |  **Generated:** 2026-06-12

> ⚠️ **All results are IN-SAMPLE** on a single historical window. No profile is claimed superior. Validate out-of-sample before trusting any of these.

---

## Returns & Risk

| Profile | Total Return | Annualized | Max DD | Sharpe | vs SPY | vs QQQ |
|---------|--------------|------------|--------|--------|--------|--------|
| baseline | +60.20% | +9.92% | -19.39% | 0.97 | -26.55% | -55.56% |
| trend_reweighted | +52.64% | +8.86% | -19.51% | 0.91 | -34.11% | -63.12% |
| trend_reweighted_aggressive | +49.86% | +8.46% | -19.82% | 0.86 | -36.89% | -65.90% |
| score_weighted_sizing | +77.71% | +12.23% | -23.74% | 0.96 | -9.04% | -38.05% |
| higher_take_profit | +77.49% | +12.20% | -22.77% | 1.01 | -9.26% | -38.27% |
| high_take_profit | +86.12% | +13.27% | -23.64% | 1.06 | -0.63% | -29.64% |
| no_fixed_take_profit_trailing_stop | +87.25% | +13.41% | -23.13% | 1.11 | +0.50% | -28.51% |
| no_fixed_take_profit_wide_trailing_stop | +102.54% | +15.21% | -23.95% | 1.13 | +15.79% | -13.22% |
| vol_adjusted_momentum | +45.40% | +7.80% | -21.94% | 0.78 | -41.35% | -70.36% |
| qqq_trend_filter | +48.51% | +8.26% | -12.82% | 0.97 | -38.24% | -67.25% |
| stop_cooldown_5d | +46.25% | +7.93% | -21.32% | 0.82 | -40.50% | -69.51% |
| regime_voladj_higher_tp | +61.51% | +10.10% | -17.00% | 1.06 | -25.24% | -54.25% |
| _SPY (buy & hold)_ | +86.75% | +13.35% | -24.50% | — | — | — |
| _QQQ (buy & hold)_ | +115.76% | +16.68% | -35.12% | — | — | — |
| _Equal-Wt Hold_ | +278.35% | +30.60% | -41.79% | — | — | — |

## Trading Activity

| Profile | Trades | / month | Win Rate | Avg Win | Avg Loss | Profit Factor | Avg Hold | Slippage |
|---------|--------|---------|----------|---------|----------|---------------|----------|----------|
| baseline | 1971 | 32.86 | +53.16% | $422 | $-349 | 1.37 | 15.35 | $8,079 |
| trend_reweighted | 1834 | 30.57 | +51.75% | $427 | $-340 | 1.35 | 15.06 | $7,400 |
| trend_reweighted_aggressive | 1843 | 30.72 | +51.04% | $425 | $-333 | 1.33 | 15.25 | $7,370 |
| score_weighted_sizing | 1969 | 32.82 | +53.01% | $552 | $-454 | 1.37 | 15.36 | $10,505 |
| higher_take_profit | 1446 | 24.11 | +48.18% | $637 | $-387 | 1.53 | 24.61 | $6,212 |
| high_take_profit | 1292 | 21.54 | +45.85% | $750 | $-391 | 1.62 | 28.19 | $5,673 |
| no_fixed_take_profit_trailing_stop | 1177 | 19.62 | +41.44% | $779 | $-313 | 1.76 | 28.58 | $5,060 |
| no_fixed_take_profit_wide_trailing_stop | 1051 | 17.52 | +41.81% | $931 | $-369 | 1.81 | 34.47 | $4,693 |
| vol_adjusted_momentum | 1844 | 30.74 | +51.31% | $406 | $-329 | 1.30 | 15.85 | $7,253 |
| qqq_trend_filter | 1465 | 24.42 | +53.78% | $418 | $-343 | 1.42 | 16.28 | $5,976 |
| stop_cooldown_5d | 1887 | 31.46 | +52.18% | $399 | $-333 | 1.31 | 15.54 | $7,381 |
| regime_voladj_higher_tp | 1051 | 17.52 | +49.14% | $619 | $-372 | 1.61 | 26.34 | $4,429 |

## Exit Attribution

| Profile | Take-profit | Stop-loss | Trailing-stop | Max-hold | Gave back gains | Largest Win | Largest Loss |
|---------|-------------|-----------|---------------|----------|-----------------|-------------|--------------|
| baseline | 385 | 390 | 0 | 215 | 73 | $1,356 | $-1,215 |
| trend_reweighted | 360 | 367 | 0 | 192 | 80 | $1,775 | $-1,162 |
| trend_reweighted_aggressive | 360 | 374 | 0 | 195 | 104 | $1,704 | $-1,162 |
| score_weighted_sizing | 384 | 389 | 0 | 216 | 73 | $2,064 | $-1,728 |
| higher_take_profit | 269 | 355 | 0 | 93 | 127 | $1,480 | $-1,135 |
| high_take_profit | 183 | 327 | 0 | 132 | 129 | $2,307 | $-1,268 |
| no_fixed_take_profit_trailing_stop | 0 | 205 | 354 | 131 | 124 | $7,606 | $-1,058 |
| no_fixed_take_profit_wide_trailing_stop | 0 | 242 | 121 | 196 | 113 | $7,763 | $-1,123 |
| vol_adjusted_momentum | 344 | 377 | 0 | 208 | 95 | $1,526 | $-1,162 |
| qqq_trend_filter | 281 | 272 | 0 | 186 | 52 | $1,238 | $-1,215 |
| stop_cooldown_5d | 360 | 379 | 0 | 211 | 73 | $1,295 | $-1,162 |
| regime_voladj_higher_tp | 197 | 249 | 0 | 75 | 89 | $1,595 | $-952 |

## Signal Quality (composite-score quintile spread)

_Top-minus-bottom quintile forward-return spread; positive ⇒ higher-ranked names outperform._

| Profile | Spread 5d | Spread 10d | Spread 20d |
|---------|-----------|------------|------------|
| baseline | +0.01% | +0.01% | -0.01% |
| trend_reweighted | +0.18% | +0.08% | -0.11% |
| trend_reweighted_aggressive | +0.17% | +0.18% | -0.17% |
| score_weighted_sizing | +0.01% | +0.01% | -0.01% |
| higher_take_profit | +0.01% | +0.01% | -0.01% |
| high_take_profit | +0.01% | +0.01% | -0.01% |
| no_fixed_take_profit_trailing_stop | +0.01% | +0.01% | -0.01% |
| no_fixed_take_profit_wide_trailing_stop | +0.01% | +0.01% | -0.01% |
| vol_adjusted_momentum | +0.10% | +0.14% | -0.29% |
| qqq_trend_filter | +0.01% | +0.01% | -0.01% |
| stop_cooldown_5d | +0.01% | +0.01% | -0.01% |
| regime_voladj_higher_tp | +0.10% | +0.14% | -0.29% |

## P&L by Group

| Profile | financial_crypto_beta | mega_cap_growth | semiconductors | software_cybersecurity |
|---------|-----|-----|-----|-----|
| baseline | $3,254 | $17,379 | $17,998 | $3,958 |
| trend_reweighted | $2,347 | $7,845 | $19,088 | $6,912 |
| trend_reweighted_aggressive | $4,001 | $9,785 | $17,506 | $5,586 |
| score_weighted_sizing | $3,370 | $22,488 | $23,992 | $5,695 |
| higher_take_profit | $4,174 | $20,770 | $22,842 | $8,247 |
| high_take_profit | $6,074 | $21,767 | $24,567 | $9,717 |
| no_fixed_take_profit_trailing_stop | $9,229 | $20,835 | $28,146 | $5,892 |
| no_fixed_take_profit_wide_trailing_stop | $8,526 | $24,239 | $29,893 | $11,892 |
| vol_adjusted_momentum | $1,557 | $9,816 | $16,459 | $5,217 |
| qqq_trend_filter | $3,952 | $13,100 | $16,943 | $4,781 |
| stop_cooldown_5d | $2,649 | $14,641 | $14,373 | $1,833 |
| regime_voladj_higher_tp | $6,128 | $14,875 | $23,771 | $6,091 |

## Top / Bottom P&L Contributors

- **baseline** — top: `NVDA` $8,914, `MU` $8,871, `AMD` $5,878  |  worst: `BAC` $-334, `MSFT` $-143, `AAPL` $-115
- **trend_reweighted** — top: `MU` $8,171, `CRWD` $6,548, `AMD` $6,393  |  worst: `AAPL` $-1,008, `AMZN` $-611, `BAC` $-542
- **trend_reweighted_aggressive** — top: `MU` $8,197, `AMD` $5,777, `CRWD` $5,206  |  worst: `BAC` $-369, `AMZN` $-285, `AAPL` $-23
- **score_weighted_sizing** — top: `MU` $12,130, `NVDA` $11,326, `AMD` $8,245  |  worst: `BAC` $-1,090, `MSFT` $-317, `AAPL` $-306
- **higher_take_profit** — top: `MU` $10,097, `AMD` $8,334, `NVDA` $8,299  |  worst: `MSFT` $-896, `BAC` $457, `AMZN` $804
- **high_take_profit** — top: `MU` $9,778, `AMD` $9,066, `NVDA` $7,639  |  worst: `MSFT` $-806, `JPM` $833, `BAC` $852
- **no_fixed_take_profit_trailing_stop** — top: `AMD` $12,692, `MU` $10,697, `NVDA` $6,298  |  worst: `MSFT` $-79, `JPM` $1,233, `AMZN` $1,339
- **no_fixed_take_profit_wide_trailing_stop** — top: `AMD` $12,024, `MU` $11,502, `PANW` $8,481  |  worst: `MSFT` $-738, `JPM` $1,181, `BAC` $1,548
- **vol_adjusted_momentum** — top: `MU` $7,594, `AMD` $5,919, `NVDA` $5,719  |  worst: `BAC` $-1,521, `MSFT` $-837, `AMZN` $-558
- **qqq_trend_filter** — top: `MU` $7,383, `AMD` $6,046, `TSM` $5,042  |  worst: `MSFT` $-1,664, `AMZN` $-674, `ORCL` $-15
- **stop_cooldown_5d** — top: `NVDA` $7,821, `MU` $7,023, `AMD` $4,727  |  worst: `MSFT` $-1,077, `BAC` $-605, `ORCL` $-484
- **regime_voladj_higher_tp** — top: `MU` $12,434, `AMD` $6,598, `META` $4,744  |  worst: `ORCL` $-1,229, `AMZN` $-1,119, `COST` $969

_(Full per-ticker P&L is in `backtest_experiments_<date>.csv`.)_

## Interpretation

**Trend reweighting:** did **not** widen the 20d quintile spread beyond baseline (-0.01%); any return change came from exposure/timing, not better ranking.

**Score-weighted sizing:** return moved +17.51% vs baseline while max drawdown moved -4.35% (more negative = worse) and the single-name P&L concentration is +14.95%. If return rose mainly alongside higher concentration/drawdown, that is added **risk**, not added skill.

**higher_take_profit:** return +17.29% vs baseline, average win changed $215, largest winner $1,480, gave-back trades 127 (baseline 73). Higher avg/largest win with fewer give-backs ⇒ the old take-profit was clipping winners early.

**high_take_profit:** return +25.92% vs baseline, average win changed $327, largest winner $2,307, gave-back trades 129 (baseline 73). Higher avg/largest win with fewer give-backs ⇒ the old take-profit was clipping winners early.

**no_fixed_take_profit_trailing_stop:** return +27.05% and max drawdown -3.73% vs baseline, with 354 trailing-stop exits. Better return *and* no worse drawdown would favour letting winners run; better return with deeper drawdown is just more risk.

**no_fixed_take_profit_wide_trailing_stop:** return +42.34% and max drawdown -4.55% vs baseline, with 121 trailing-stop exits. Better return *and* no worse drawdown would favour letting winners run; better return with deeper drawdown is just more risk.

**Source / overfitting check:** the highest in-sample return is `no_fixed_take_profit_wide_trailing_stop` (+102.54%). Treat ranking by in-sample return with suspicion — prefer profiles that improve the quintile spread *and* hold up across tickers/groups.

**All figures above are in-sample.** No profile is recommended as superior; differences of this size are well within noise for a single historical window. Validate any promising profile on a separate out-of-sample period before acting.
