# Ticker-Level Active vs Buy-and-Hold
**Train (in-sample):** 2021-06-12 → 2024-06-12  |  **Test (out-of-sample):** 2024-06-12 → 2026-06-12  |  **Generated:** 2026-06-12

> Per ticker, the best rule from a **fixed grid** (stop×tp×trail×hold×entry-filter = 144 combos) is chosen on TRAIN and compared to buy-and-hold of that ticker. Eligible tickers form a portfolio, validated on the disjoint TEST window. No unlimited optimisation.

---

## Pass / Fail

| Test | Result | Detail |
|------|--------|--------|
| Ticker active rules beat ticker BH (TRAIN) | ✅ 16/21 | excess > 0 in-sample |
| Tickers passing active eligibility | ✅ 13/21 | full eligibility gate |
| Portfolio beat EW-eligible BH (TRAIN) | ❌ | +58.81% vs +87.48% |
| Portfolio improved Sharpe vs EW-eligible (TRAIN) | ✅ | 1.62 vs 0.80 |
| Portfolio reduced drawdown vs EW-eligible (TRAIN) | ✅ | -10.64% vs -53.96% |
| Portfolio beat EW-eligible BH (TEST/OOS) | ❌ | +12.88% vs +74.97% |
| Portfolio improved Sharpe vs EW-eligible (TEST/OOS) | ❌ | 0.79 vs 1.11 |
| Portfolio reduced drawdown vs EW-eligible (TEST/OOS) | ✅ | -8.34% vs -28.23% |
| **Performance survived out-of-sample** | ❌ | TEST portfolio vs EW-eligible BH |

## Per-Ticker Active vs Buy-and-Hold (TRAIN, in-sample)

| Ticker | Eligible | Best Rule | Active Ret | BH Ret | Excess | Active DD | BH DD | Active Sharpe | BH Sharpe | Trades | Win% | PF | Slippage |
|--------|----------|-----------|-----------|--------|--------|-----------|-------|---------------|-----------|--------|------|----|----------|
| COIN | ✅ | composite | sl 7.5% | tp null | trail null | hold 30d | +388.61% | +6.63% | +381.98% | -46.39% | -90.90% | 1.12 | 0.47 | 25 | +33.33% | 2.73 | +7.57% |
| NFLX | ✅ | above_50ma | sl 7.5% | tp 20% | trail null | hold 60d | +176.30% | +30.04% | +146.26% | -25.29% | -75.95% | 1.20 | 0.44 | 20 | +57.89% | 2.59 | +6.40% |
| NVDA | ✅ | above_50ma | sl 7.5% | tp null | trail null | hold 30d | +729.49% | +596.09% | +133.40% | -42.62% | -66.34% | 1.84 | 1.47 | 24 | +58.33% | 4.01 | +13.62% |
| META | ✅ | qqq_above_50ma | sl 10.0% | tp 20% | trail 10% | hold 60d | +176.58% | +51.25% | +125.33% | -37.25% | -76.74% | 1.15 | 0.53 | 20 | +57.89% | 2.81 | +5.44% |
| CRWD | ✅ | ret20_pos | sl 10.0% | tp 15% | trail 10% | hold 30d | +160.77% | +65.88% | +94.90% | -37.52% | -67.69% | 1.01 | 0.59 | 32 | +54.84% | 2.08 | +7.72% |
| TSLA | ✅ | composite | sl 7.5% | tp 15% | trail 15% | hold 30d | +65.73% | -13.89% | +79.63% | -32.92% | -73.63% | 0.64 | 0.20 | 24 | +58.33% | 1.70 | +7.31% |
| AMZN | ✅ | above_50ma | sl 7.5% | tp 15% | trail null | hold 30d | +59.47% | +10.46% | +49.01% | -27.42% | -56.15% | 0.75 | 0.28 | 20 | +63.16% | 2.29 | +4.55% |
| AMD | ✅ | above_50ma | sl 7.5% | tp 20% | trail null | hold 30d | +137.26% | +96.49% | +40.77% | -46.81% | -65.45% | 0.93 | 0.69 | 25 | +45.83% | 2.07 | +8.75% |
| MSFT | ✅ | above_50ma | sl 7.5% | tp null | trail 10% | hold 30d | +99.53% | +74.10% | +25.43% | -23.27% | -37.15% | 1.22 | 0.81 | 20 | +63.16% | 2.91 | +5.31% |
| TSM | ✅ | above_50ma | sl 10.0% | tp 15% | trail null | hold 30d | +75.01% | +51.31% | +23.69% | -34.49% | -56.47% | 0.81 | 0.57 | 21 | +55.00% | 2.15 | +4.18% |
| GOOGL | ✅ | qqq_above_50ma | sl 7.5% | tp 20% | trail null | hold 30d | +59.33% | +45.37% | +13.96% | -33.10% | -44.32% | 0.75 | 0.55 | 23 | +45.45% | 1.92 | +4.98% |
| BAC | ✅ | composite | sl 10.0% | tp 15% | trail 10% | hold 30d | +8.07% | +2.88% | +5.19% | -38.06% | -46.64% | 0.23 | 0.17 | 20 | +63.16% | 1.24 | +3.79% |
| ASML | ✅ | above_50ma | sl 10.0% | tp 15% | trail 10% | hold 30d | +55.63% | +55.05% | +0.58% | -44.59% | -56.86% | 0.64 | 0.56 | 22 | +57.14% | 1.53 | +4.68% |
| COST | ❌ | ret20_pos | sl 7.5% | tp 15% | trail 10% | hold 60d | +158.08% | +130.69% | +27.39% | -19.66% | -31.40% | 1.76 | 1.29 | 14 | +69.23% | 9.75 | +4.14% |
| ORCL | ❌ | ret20_pos | sl 10.0% | tp 15% | trail null | hold 60d | +100.04% | +78.00% | +22.04% | -28.76% | -40.36% | 1.00 | 0.77 | 15 | +57.14% | 3.00 | +4.21% |
| AAPL | ❌ | composite | sl 10.0% | tp null | trail null | hold 60d | +78.12% | +66.09% | +12.03% | -24.07% | -30.91% | 0.97 | 0.76 | 9 | +75.00% | 3.04 | +2.07% |
| MU | ❌ | composite | sl 7.5% | tp 15% | trail 15% | hold 60d | +72.54% | +78.05% | -5.51% | -42.98% | -49.63% | 0.72 | 0.67 | 18 | +52.94% | 1.62 | +3.43% |
| GS | ❌ | composite | sl 10.0% | tp null | trail 15% | hold 60d | +24.76% | +30.40% | -5.64% | -29.91% | -32.84% | 0.46 | 0.48 | 10 | +44.44% | 1.45 | +1.89% |
| JPM | ❌ | qqq_above_50ma | sl 10.0% | tp null | trail 10% | hold 60d | +23.11% | +32.23% | -9.12% | -27.92% | -38.77% | 0.46 | 0.51 | 13 | +66.67% | 1.95 | +2.44% |
| AVGO | ❌ | ret20_pos | sl 10.0% | tp 15% | trail 10% | hold 60d | +231.26% | +240.43% | -9.18% | -32.87% | -35.16% | 1.50 | 1.39 | 19 | +55.56% | 4.18 | +6.49% |
| PANW | ❌ | qqq_above_50ma | sl 7.5% | tp null | trail 15% | hold 60d | +150.72% | +161.02% | -10.30% | -33.33% | -36.00% | 1.00 | 0.95 | 16 | +40.00% | 2.41 | +4.99% |

## Portfolio vs Benchmarks — TRAIN (in-sample)

| Strategy | Total Return | Max DD | Sharpe |
|----------|--------------|--------|--------|
| **Active portfolio** (+31.29% avg exp) | +58.81% | -10.64% | 1.62 |
| SPY | +33.06% | -24.50% | 0.64 |
| QQQ | +40.28% | -35.12% | 0.61 |
| EW buy-hold (full universe) | +98.17% | -41.46% | 0.96 |
| EW buy-hold (eligible only) | +87.48% | -53.96% | 0.80 |
| EW eligible, capital-matched | +27.37% | -20.38% | 0.87 |

## Portfolio vs Benchmarks — TEST (out-of-sample)

| Strategy | Total Return | Max DD | Sharpe |
|----------|--------------|--------|--------|
| **Active portfolio** (+30.80% avg exp) | +12.88% | -8.34% | 0.79 |
| SPY | +40.35% | -18.76% | 1.10 |
| QQQ | +53.80% | -22.77% | 1.10 |
| EW buy-hold (full universe) | +94.67% | -27.11% | 1.37 |
| EW buy-hold (eligible only) | +74.97% | -28.23% | 1.11 |
| EW eligible, capital-matched | +23.09% | -9.89% | 1.10 |

## Interpretation

- 13/21 tickers cleared the full active-eligibility gate in-sample. Eligible names then form the portfolio.
- **The TEST block is the verdict.** If the portfolio's TEST row does not beat EW-eligible buy-and-hold, the in-sample eligibility did not generalise — i.e. it was grid-search luck.
- All TRAIN numbers are in-sample by construction (best-of-grid). Re-run with the second split to confirm; a real edge survives both.
