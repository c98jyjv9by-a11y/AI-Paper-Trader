# AI Paper Trader — Strategy Experiments
**Period:** 2018-06-22 → 2026-06-22  |  **Generated:** 2026-06-22

> ⚠️ **All results are IN-SAMPLE** on a single historical window. No profile is claimed superior. Validate out-of-sample before trusting any of these.

---

## Returns & Risk

| Profile | Total Return | Annualized | Max DD | Sharpe | vs SPY | vs QQQ |
|---------|--------------|------------|--------|--------|--------|--------|
| baseline | +25.44% | +2.88% | -45.61% | 0.25 | -180.58% | -316.97% |
| trend_reweighted | +26.84% | +3.03% | -51.60% | 0.25 | -179.18% | -315.57% |
| trend_reweighted_aggressive | +0.95% | +0.12% | -52.88% | 0.16 | -205.07% | -341.47% |
| score_weighted_sizing | +10.21% | +1.23% | -6.05% | 0.46 | -195.81% | -332.20% |
| higher_take_profit | -18.06% | -2.47% | -61.18% | -0.03 | -224.08% | -360.47% |
| high_take_profit | +16.84% | +1.97% | -59.99% | 0.20 | -189.18% | -325.58% |
| no_fixed_take_profit_trailing_stop | -65.48% | -12.49% | -80.68% | -0.34 | -271.50% | -407.90% |
| no_fixed_take_profit_wide_trailing_stop | -59.75% | -10.79% | -69.15% | -0.25 | -265.77% | -402.16% |
| vol_adjusted_momentum | +0.95% | +0.12% | -52.88% | 0.16 | -205.07% | -341.47% |
| qqq_trend_filter | -22.95% | -3.22% | -62.42% | 0.04 | -228.97% | -365.36% |
| stop_cooldown_5d | +15.26% | +1.80% | -45.46% | 0.21 | -190.76% | -327.16% |
| regime_voladj_higher_tp | +136.99% | +11.43% | -35.41% | 0.66 | -69.03% | -205.43% |
| _SPY (buy & hold)_ | +206.02% | +15.06% | -33.72% | — | — | — |
| _QQQ (buy & hold)_ | +342.42% | +20.51% | -35.12% | — | — | — |
| _Equal-Wt Hold_ | +467.45% | +24.33% | -80.97% | — | — | — |

## Trading Activity

| Profile | Trades | / month | Win Rate | Avg Win | Avg Loss | Profit Factor | Avg Hold | Slippage |
|---------|--------|---------|----------|---------|----------|---------------|----------|----------|
| baseline | 101 | 1.05 | +34.00% | $22,270 | $-11,931 | 0.96 | 66.38 | $5,113 |
| trend_reweighted | 97 | 1.01 | +33.33% | $20,324 | $-10,338 | 0.98 | 68.02 | $4,638 |
| trend_reweighted_aggressive | 88 | 0.92 | +37.21% | $15,213 | $-9,752 | 0.92 | 71.06 | $3,673 |
| score_weighted_sizing | 96 | 1.00 | +36.17% | $2,221 | $-1,033 | 1.22 | 65.53 | $436 |
| higher_take_profit | 264 | 2.75 | +58.78% | $7,888 | $-11,564 | 0.97 | 24.16 | $12,112 |
| high_take_profit | 226 | 2.35 | +54.46% | $11,258 | $-12,971 | 1.04 | 29.26 | $11,831 |
| no_fixed_take_profit_trailing_stop | 425 | 4.43 | +32.55% | $3,171 | $-1,997 | 0.77 | 13.97 | $8,462 |
| no_fixed_take_profit_wide_trailing_stop | 273 | 2.84 | +33.09% | $5,170 | $-3,230 | 0.79 | 23.12 | $6,568 |
| vol_adjusted_momentum | 88 | 0.92 | +37.21% | $15,213 | $-9,752 | 0.92 | 71.06 | $3,673 |
| qqq_trend_filter | 91 | 0.95 | +37.78% | $9,890 | $-7,546 | 0.80 | 68.26 | $2,846 |
| stop_cooldown_5d | 105 | 1.09 | +34.62% | $20,130 | $-11,305 | 0.94 | 64.24 | $4,929 |
| regime_voladj_higher_tp | 164 | 1.71 | +65.43% | $13,197 | $-19,207 | 1.30 | 29.43 | $13,641 |

## Exit Attribution

| Profile | Take-profit | Stop-loss | Trailing-stop | Max-hold | Gave back gains | Largest Win | Largest Loss |
|---------|-------------|-----------|---------------|----------|-----------------|-------------|--------------|
| baseline | 0 | 24 | 0 | 25 | 24 | $70,307 | $-21,500 |
| trend_reweighted | 0 | 22 | 0 | 25 | 24 | $71,524 | $-19,697 |
| trend_reweighted_aggressive | 0 | 20 | 0 | 22 | 19 | $49,446 | $-15,634 |
| score_weighted_sizing | 0 | 23 | 0 | 24 | 19 | $7,885 | $-1,662 |
| higher_take_profit | 74 | 45 | 0 | 13 | 20 | $14,648 | $-18,690 |
| high_take_profit | 57 | 38 | 0 | 18 | 25 | $18,120 | $-26,235 |
| no_fixed_take_profit_trailing_stop | 0 | 0 | 206 | 6 | 47 | $19,950 | $-8,769 |
| no_fixed_take_profit_wide_trailing_stop | 0 | 0 | 122 | 14 | 37 | $23,306 | $-8,184 |
| vol_adjusted_momentum | 0 | 20 | 0 | 22 | 19 | $49,446 | $-15,634 |
| qqq_trend_filter | 0 | 21 | 0 | 23 | 17 | $37,534 | $-18,498 |
| stop_cooldown_5d | 0 | 26 | 0 | 25 | 23 | $70,307 | $-20,143 |
| regime_voladj_higher_tp | 50 | 20 | 0 | 12 | 13 | $25,430 | $-31,921 |

## Signal Quality (composite-score quintile spread)

_Top-minus-bottom quintile forward-return spread; positive ⇒ higher-ranked names outperform._

| Profile | Spread 5d | Spread 10d | Spread 20d |
|---------|-----------|------------|------------|
| baseline | — | — | — |
| trend_reweighted | — | — | — |
| trend_reweighted_aggressive | — | — | — |
| score_weighted_sizing | — | — | — |
| higher_take_profit | — | — | — |
| high_take_profit | — | — | — |
| no_fixed_take_profit_trailing_stop | — | — | — |
| no_fixed_take_profit_wide_trailing_stop | — | — | — |
| vol_adjusted_momentum | — | — | — |
| qqq_trend_filter | — | — | — |
| stop_cooldown_5d | — | — | — |
| regime_voladj_higher_tp | — | — | — |

## P&L by Group

| Profile | leveraged_etfs |
|---------|-----|
| baseline | $25,442 |
| trend_reweighted | $26,844 |
| trend_reweighted_aggressive | $950 |
| score_weighted_sizing | $10,213 |
| higher_take_profit | $-18,055 |
| high_take_profit | $16,835 |
| no_fixed_take_profit_trailing_stop | $-65,484 |
| no_fixed_take_profit_wide_trailing_stop | $-59,746 |
| vol_adjusted_momentum | $950 |
| qqq_trend_filter | $-22,948 |
| stop_cooldown_5d | $15,257 |
| regime_voladj_higher_tp | $136,988 |

## Top / Bottom P&L Contributors

- **baseline** — top: `TQQQ` $181,069, `SQQQ` $-155,627  |  worst: `SQQQ` $-155,627, `TQQQ` $181,069
- **trend_reweighted** — top: `TQQQ` $205,839, `SQQQ` $-178,995  |  worst: `SQQQ` $-178,995, `TQQQ` $205,839
- **trend_reweighted_aggressive** — top: `TQQQ` $130,400, `SQQQ` $-129,451  |  worst: `SQQQ` $-129,451, `TQQQ` $130,400
- **score_weighted_sizing** — top: `TQQQ` $22,077, `SQQQ` $-11,864  |  worst: `SQQQ` $-11,864, `TQQQ` $22,077
- **higher_take_profit** — top: `TQQQ` $126,885, `SQQQ` $-144,940  |  worst: `SQQQ` $-144,940, `TQQQ` $126,885
- **high_take_profit** — top: `TQQQ` $164,250, `SQQQ` $-147,415  |  worst: `SQQQ` $-147,415, `TQQQ` $164,250
- **no_fixed_take_profit_trailing_stop** — top: `TQQQ` $60,100, `SQQQ` $-125,584  |  worst: `SQQQ` $-125,584, `TQQQ` $60,100
- **no_fixed_take_profit_wide_trailing_stop** — top: `TQQQ` $65,256, `SQQQ` $-125,002  |  worst: `SQQQ` $-125,002, `TQQQ` $65,256
- **vol_adjusted_momentum** — top: `TQQQ` $130,400, `SQQQ` $-129,451  |  worst: `SQQQ` $-129,451, `TQQQ` $130,400
- **qqq_trend_filter** — top: `TQQQ` $81,144, `SQQQ` $-104,092  |  worst: `SQQQ` $-104,092, `TQQQ` $81,144
- **stop_cooldown_5d** — top: `TQQQ` $180,555, `SQQQ` $-165,299  |  worst: `SQQQ` $-165,299, `TQQQ` $180,555
- **regime_voladj_higher_tp** — top: `TQQQ` $252,209, `SQQQ` $-115,221  |  worst: `SQQQ` $-115,221, `TQQQ` $252,209

_(Full per-ticker P&L is in `backtest_experiments_<date>.csv`.)_

## Interpretation

**Score-weighted sizing:** return moved -15.23% vs baseline while max drawdown moved +39.56% (more negative = worse) and the single-name P&L concentration is +65.05%. If return rose mainly alongside higher concentration/drawdown, that is added **risk**, not added skill.

**higher_take_profit:** return -43.50% vs baseline, average win changed $-14,382, largest winner $14,648, gave-back trades 20 (baseline 24). Higher avg/largest win with fewer give-backs ⇒ the old take-profit was clipping winners early.

**high_take_profit:** return -8.61% vs baseline, average win changed $-11,012, largest winner $18,120, gave-back trades 25 (baseline 24). Higher avg/largest win with fewer give-backs ⇒ the old take-profit was clipping winners early.

**no_fixed_take_profit_trailing_stop:** return -90.93% and max drawdown -35.07% vs baseline, with 206 trailing-stop exits. Better return *and* no worse drawdown would favour letting winners run; better return with deeper drawdown is just more risk.

**no_fixed_take_profit_wide_trailing_stop:** return -85.19% and max drawdown -23.54% vs baseline, with 122 trailing-stop exits. Better return *and* no worse drawdown would favour letting winners run; better return with deeper drawdown is just more risk.

**Source / overfitting check:** the highest in-sample return is `regime_voladj_higher_tp` (+136.99%). ⚠️ Its P&L is highly concentrated (top name = +68.64% of total |P&L|), so the in-sample edge may be one or two lucky names — a classic overfitting risk. Treat ranking by in-sample return with suspicion — prefer profiles that improve the quintile spread *and* hold up across tickers/groups.

**All figures above are in-sample.** No profile is recommended as superior; differences of this size are well within noise for a single historical window. Validate any promising profile on a separate out-of-sample period before acting.
