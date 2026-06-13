# Ticker-Level Active vs Buy-and-Hold
**Train (in-sample):** 2021-06-12 → 2025-06-12  |  **Test (out-of-sample):** 2025-06-12 → 2026-06-12  |  **Generated:** 2026-06-12

> Per ticker, the best rule from a **fixed grid** (stop×tp×trail×hold×entry-filter = 144 combos) is chosen on TRAIN and compared to buy-and-hold of that ticker. Eligible tickers form a portfolio, validated on the disjoint TEST window. No unlimited optimisation.

---

## Pass / Fail

| Test | Result | Detail |
|------|--------|--------|
| Ticker active rules beat ticker BH (TRAIN) | ✅ 15/21 | excess > 0 in-sample |
| Tickers passing active eligibility | ✅ 14/21 | full eligibility gate |
| Portfolio beat EW-eligible BH (TRAIN) | ❌ | +75.65% vs +108.34% |
| Portfolio improved Sharpe vs EW-eligible (TRAIN) | ✅ | 1.47 vs 0.74 |
| Portfolio reduced drawdown vs EW-eligible (TRAIN) | ✅ | -11.98% vs -50.40% |
| Portfolio beat EW-eligible BH (TEST/OOS) | ❌ | +20.50% vs +60.45% |
| Portfolio improved Sharpe vs EW-eligible (TEST/OOS) | ✅ | 2.05 vs 2.01 |
| Portfolio reduced drawdown vs EW-eligible (TEST/OOS) | ✅ | -5.73% vs -16.67% |
| **Performance survived out-of-sample** | ❌ | TEST portfolio vs EW-eligible BH |

## Per-Ticker Active vs Buy-and-Hold (TRAIN, in-sample)

| Ticker | Eligible | Best Rule | Active Ret | BH Ret | Excess | Active DD | BH DD | Active Sharpe | BH Sharpe | Trades | Win% | PF | Slippage |
|--------|----------|-----------|-----------|--------|--------|-----------|-------|---------------|-----------|--------|------|----|----------|
| COIN | ✅ | composite | sl 10.0% | tp null | trail null | hold 30d | +485.12% | +0.82% | +484.31% | -58.57% | -90.90% | 0.98 | 0.44 | 28 | +35.71% | 2.43 | +11.32% |
| NFLX | ✅ | above_50ma | sl 10.0% | tp 20% | trail null | hold 60d | +399.45% | +143.06% | +256.40% | -27.10% | -75.95% | 1.40 | 0.73 | 23 | +68.18% | 3.35 | +9.77% |
| META | ✅ | qqq_above_50ma | sl 7.5% | tp null | trail 10% | hold 60d | +341.89% | +106.86% | +235.03% | -39.69% | -76.74% | 1.29 | 0.63 | 21 | +55.00% | 4.26 | +6.81% |
| CRWD | ✅ | ret20_pos | sl 10.0% | tp 15% | trail 10% | hold 30d | +245.48% | +106.28% | +139.20% | -37.52% | -67.69% | 0.97 | 0.61 | 43 | +54.76% | 1.90 | +13.49% |
| TSLA | ✅ | composite | sl 10.0% | tp null | trail null | hold 30d | +140.17% | +54.99% | +85.19% | -41.86% | -73.63% | 0.73 | 0.49 | 23 | +52.17% | 2.08 | +6.68% |
| AMZN | ✅ | qqq_above_50ma | sl 10.0% | tp 15% | trail null | hold 60d | +106.05% | +26.03% | +80.02% | -40.72% | -56.15% | 0.80 | 0.34 | 21 | +60.00% | 2.03 | +4.89% |
| TSM | ✅ | above_50ma | sl 10.0% | tp 20% | trail null | hold 30d | +158.88% | +91.78% | +67.10% | -31.30% | -56.47% | 0.93 | 0.62 | 25 | +54.17% | 2.93 | +5.97% |
| AMD | ✅ | above_50ma | sl 10.0% | tp 15% | trail 10% | hold 30d | +90.57% | +45.31% | +45.26% | -48.14% | -65.45% | 0.63 | 0.44 | 36 | +48.57% | 1.57 | +12.79% |
| MSFT | ✅ | above_50ma | sl 7.5% | tp 20% | trail 10% | hold 30d | +125.45% | +90.48% | +34.98% | -23.27% | -37.15% | 1.12 | 0.73 | 26 | +60.00% | 2.81 | +7.69% |
| GOOGL | ✅ | qqq_above_50ma | sl 7.5% | tp 15% | trail null | hold 60d | +71.39% | +44.35% | +27.03% | -30.10% | -44.32% | 0.67 | 0.45 | 25 | +50.00% | 1.78 | +6.27% |
| MU | ✅ | qqq_above_50ma | sl 7.5% | tp 20% | trail null | hold 30d | +71.07% | +47.64% | +23.42% | -46.88% | -57.63% | 0.55 | 0.44 | 37 | +47.22% | 1.39 | +7.23% |
| ASML | ✅ | above_50ma | sl 7.5% | tp null | trail null | hold 30d | +28.80% | +15.12% | +13.67% | -46.80% | -56.86% | 0.36 | 0.30 | 25 | +45.83% | 1.25 | +5.22% |
| BAC | ✅ | above_50ma | sl 10.0% | tp null | trail 10% | hold 30d | +27.99% | +19.33% | +8.66% | -29.25% | -46.64% | 0.41 | 0.30 | 23 | +54.55% | 1.41 | +4.45% |
| ORCL | ✅ | ret20_pos | sl 10.0% | tp 15% | trail null | hold 60d | +164.78% | +156.25% | +8.53% | -28.76% | -40.36% | 1.00 | 0.86 | 21 | +55.00% | 2.31 | +6.65% |
| COST | ❌ | above_50ma | sl 10.0% | tp 20% | trail 10% | hold 60d | +211.69% | +174.25% | +37.44% | -18.05% | -31.40% | 1.56 | 1.19 | 17 | +87.50% | 11.19 | +6.05% |
| NVDA | ❌ | above_50ma | sl 7.5% | tp null | trail null | hold 60d | +703.15% | +706.43% | -3.28% | -36.05% | -66.34% | 1.40 | 1.22 | 18 | +52.94% | 4.28 | +13.38% |
| AAPL | ❌ | qqq_above_50ma | sl 7.5% | tp 15% | trail null | hold 30d | +49.68% | +56.00% | -6.32% | -28.66% | -33.36% | 0.61 | 0.53 | 27 | +57.69% | 1.88 | +6.60% |
| JPM | ❌ | qqq_above_50ma | sl 7.5% | tp 20% | trail null | hold 60d | +71.40% | +89.48% | -18.08% | -34.18% | -38.77% | 0.78 | 0.77 | 17 | +68.75% | 2.40 | +3.57% |
| GS | ❌ | composite | sl 10.0% | tp 15% | trail 15% | hold 60d | +66.90% | +85.48% | -18.58% | -30.72% | -32.84% | 0.66 | 0.69 | 17 | +64.71% | 2.06 | +3.53% |
| PANW | ❌ | qqq_above_50ma | sl 7.5% | tp 20% | trail 15% | hold 60d | +172.36% | +222.68% | -50.32% | -33.40% | -36.00% | 0.89 | 0.91 | 25 | +50.00% | 2.21 | +8.88% |
| AVGO | ❌ | above_50ma | sl 10.0% | tp 20% | trail 15% | hold 60d | +426.51% | +490.03% | -63.52% | -38.07% | -41.15% | 1.29 | 1.25 | 24 | +65.22% | 3.94 | +11.25% |

## Portfolio vs Benchmarks — TRAIN (in-sample)

| Strategy | Total Return | Max DD | Sharpe |
|----------|--------------|--------|--------|
| **Active portfolio** (+34.67% avg exp) | +75.65% | -11.98% | 1.47 |
| SPY | +50.28% | -24.50% | 0.65 |
| QQQ | +58.86% | -35.12% | 0.61 |
| EW buy-hold (full universe) | +149.64% | -41.46% | 0.94 |
| EW buy-hold (eligible only) | +108.34% | -50.40% | 0.74 |
| EW eligible, capital-matched | +37.56% | -20.26% | 0.74 |

## Portfolio vs Benchmarks — TEST (out-of-sample)

| Strategy | Total Return | Max DD | Sharpe |
|----------|--------------|--------|--------|
| **Active portfolio** (+36.00% avg exp) | +20.50% | -5.73% | 2.05 |
| SPY | +24.27% | -8.88% | 1.84 |
| QQQ | +35.82% | -11.96% | 1.88 |
| EW buy-hold (full universe) | +54.53% | -14.50% | 2.13 |
| EW buy-hold (eligible only) | +60.45% | -16.67% | 2.01 |
| EW eligible, capital-matched | +21.77% | -7.28% | 1.92 |

## Interpretation

- 14/21 tickers cleared the full active-eligibility gate in-sample. Eligible names then form the portfolio.
- **The TEST block is the verdict.** If the portfolio's TEST row does not beat EW-eligible buy-and-hold, the in-sample eligibility did not generalise — i.e. it was grid-search luck.
- All TRAIN numbers are in-sample by construction (best-of-grid). Re-run with the second split to confirm; a real edge survives both.
