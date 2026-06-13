# Signal Screen — Cross-Sectional Factor Predictiveness
**Train:** 2022-06-13 → 2024-06-13  |  **Test (OOS):** 2024-06-13 → 2026-06-13  |  **Generated:** 2026-06-13

> Rank IC = daily Spearman corr of factor ranks vs forward-return ranks across the universe (headline horizon 20d). A factor is a **candidate** only if its IC is positive in BOTH train and test and significant out-of-sample (|t| > 2). No trading — pure predictiveness.

---

## Verdict

- **No factor showed positive, significant out-of-sample predictive power.**
- On this universe/period the cross-section looks efficient for these signals — consistent with the dead momentum composite. Building another ranking strategy here would chase noise. The productive moves are a **different universe** (more dispersion / less-efficient names) or a **different data source** (fundamentals, estimates, alt-data) — price/volume factors alone are not separating these names.

## Factor Leaderboard (ranked by OOS 20d rank IC)

| Factor | IC train | **IC test** | IC t (test) | LS train | LS test | Candidate |
|--------|----------|-------------|-------------|----------|---------|-----------|
| reversal_21 | +0.043 | **+0.024** | +1.7 | +1.50% | -0.75% | ❌ |
| vol_adj_mom_63 | -0.030 | **+0.024** | +1.8 | -1.75% | +1.24% | ❌ |
| mom_63 | -0.031 | **+0.007** | +0.5 | -0.82% | +1.01% | ❌ |
| vol_trend | +0.005 | **+0.006** | +0.5 | +1.03% | -0.14% | ❌ |
| reversal_5 | +0.010 | **+0.004** | +0.3 | -0.39% | -0.48% | ❌ |
| accel_21_63 | +0.013 | **-0.005** | -0.3 | +0.86% | -0.48% | ❌ |
| mom_252 | -0.033 | **-0.016** | -1.1 | -2.23% | -0.51% | ❌ |
| mom_252_21 | -0.025 | **-0.017** | -1.2 | -1.49% | -0.50% | ❌ |
| mom_21 | -0.043 | **-0.024** | -1.7 | -1.86% | +0.53% | ❌ |
| high_52w_prox | -0.082 | **-0.031** | -2.0 | -3.90% | -0.85% | ❌ |
| dist_50ma | -0.040 | **-0.037** | -2.6 | -1.86% | +0.26% | ❌ |
| dist_200ma | -0.016 | **-0.039** | -2.5 | -0.70% | +0.45% | ❌ |
| low_vol | -0.061 | **-0.045** | -3.3 | -3.77% | -3.65% | ❌ |
| mom_126 | -0.001 | **-0.052** | -3.4 | -0.29% | -0.35% | ❌ |

_IC ≈ 0.00 means no signal; |IC| ≳ 0.03 is interesting, ≳ 0.05 strong. LS = top-quintile minus bottom-quintile average forward return (per day). Per-horizon detail (5/10/20/60d) is in the CSV._
