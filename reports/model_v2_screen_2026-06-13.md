# Signal Screen — Cross-Sectional Factor Predictiveness
**Train:** 2019-01-01 → 2026-06-13  |  **Test (OOS):** 2023-01-01 → 2026-06-13  |  **Generated:** 2026-06-13

> Rank IC = daily Spearman corr of factor ranks vs forward-return ranks across the universe (headline horizon 20d). A factor is a **candidate** only if its IC is positive in BOTH train and test and significant out-of-sample (|t| > 2). No trading — pure predictiveness.

---

## Verdict

- **1 candidate factor(s) survived OOS:** `reversal_21`.
- These are worth building a strategy around — they actually sort winners from losers out-of-sample. Validate further before sizing real conviction.

## Factor Leaderboard (ranked by OOS 20d rank IC)

| Factor | IC train | **IC test** | IC t (test) | LS train | LS test | Candidate |
|--------|----------|-------------|-------------|----------|---------|-----------|
| reversal_21 | +0.016 | **+0.046** | +4.7 | -0.07% | +0.39% | ✅ |
| vol_trend | -0.016 | **+0.009** | +1.0 | -0.24% | +0.33% | ❌ |
| reversal_5 | +0.008 | **+0.008** | +0.9 | -0.34% | -0.52% | ❌ |
| accel_21_63 | -0.016 | **+0.003** | +0.2 | -0.75% | -0.23% | ❌ |
| vol_adj_mom_63 | +0.021 | **-0.008** | -0.8 | +0.62% | -0.01% | ❌ |
| mom_252_21 | -0.016 | **-0.011** | -1.0 | -0.69% | -0.63% | ❌ |
| mom_63 | +0.013 | **-0.015** | -1.4 | +0.96% | +0.38% | ❌ |
| mom_252 | -0.018 | **-0.019** | -1.7 | -0.55% | -1.13% | ❌ |
| dist_200ma | -0.003 | **-0.031** | -2.7 | +0.80% | -0.09% | ❌ |
| mom_126 | -0.011 | **-0.031** | -2.7 | +0.36% | -0.17% | ❌ |
| mom_21 | -0.016 | **-0.046** | -4.7 | -0.07% | -0.72% | ❌ |
| dist_50ma | -0.014 | **-0.051** | -4.9 | -0.05% | -0.80% | ❌ |
| high_52w_prox | -0.041 | **-0.058** | -5.4 | -1.42% | -2.31% | ❌ |
| low_vol | -0.023 | **-0.062** | -6.0 | -2.18% | -4.19% | ❌ |

_IC ≈ 0.00 means no signal; |IC| ≳ 0.03 is interesting, ≳ 0.05 strong. LS = top-quintile minus bottom-quintile average forward return (per day). Per-horizon detail (5/10/20/60d) is in the CSV._
