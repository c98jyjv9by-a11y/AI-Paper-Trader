# Ticker-Level Active vs Buy-and-Hold
**Train (in-sample):** 2020-01-01 → 2022-12-31  |  **Test (out-of-sample):** 2023-01-01 → 2026-06-13  |  **Generated:** 2026-06-13

> Per ticker, the best rule from a **fixed grid** (stop×tp×trail×hold×entry-filter = 144 combos) is chosen on TRAIN and compared to buy-and-hold of that ticker. Eligible tickers form a portfolio, validated on the disjoint TEST window. No unlimited optimisation.

---

## Pass / Fail

| Test | Result | Detail |
|------|--------|--------|
| Ticker active rules beat ticker BH (TRAIN) | ✅ 20/20 | excess > 0 in-sample |
| Tickers passing active eligibility | ✅ 17/20 | full eligibility gate |
| Portfolio beat EW-eligible BH (TRAIN) | ✅ | +65.71% vs +63.64% |
| Portfolio improved Sharpe vs EW-eligible (TRAIN) | ✅ | 1.67 vs 0.67 |
| Portfolio reduced drawdown vs EW-eligible (TRAIN) | ✅ | -11.33% vs -40.49% |
| Portfolio beat EW-eligible BH (TEST/OOS) | ❌ | +69.38% vs +378.39% |
| Portfolio improved Sharpe vs EW-eligible (TEST/OOS) | ❌ | 1.64 vs 2.06 |
| Portfolio reduced drawdown vs EW-eligible (TEST/OOS) | ✅ | -11.69% vs -26.15% |
| **Performance survived out-of-sample** | ❌ | TEST portfolio vs EW-eligible BH |

## Per-Ticker Active vs Buy-and-Hold (TRAIN, in-sample)

| Ticker | Eligible | Best Rule | Active Ret | BH Ret | Excess | Active DD | BH DD | Active Sharpe | BH Sharpe | Trades | Win% | PF | Slippage |
|--------|----------|-----------|-----------|--------|--------|-----------|-------|---------------|-----------|--------|------|----|----------|
| TSLA | ✅ | composite | sl 7.5% | tp 20% | trail 10% | hold 60d | +1265.79% | +329.44% | +936.35% | -35.72% | -73.39% | 2.14 | 1.04 | 28 | +64.29% | 5.39 | +47.66% |
| NVDA | ✅ | composite | sl 10.0% | tp 15% | trail 15% | hold 60d | +316.26% | +144.50% | +171.76% | -26.54% | -66.34% | 1.36 | 0.81 | 27 | +62.96% | 2.70 | +13.87% |
| NFLX | ✅ | above_50ma | sl 10.0% | tp null | trail 10% | hold 30d | +119.84% | -10.59% | +130.43% | -25.95% | -75.95% | 0.88 | 0.20 | 23 | +63.64% | 2.58 | +6.54% |
| TSM | ✅ | qqq_above_50ma | sl 7.5% | tp 15% | trail null | hold 30d | +146.17% | +32.19% | +113.98% | -22.33% | -56.47% | 1.13 | 0.43 | 22 | +59.09% | 3.60 | +9.45% |
| META | ✅ | qqq_above_50ma | sl 7.5% | tp 20% | trail 10% | hold 30d | +39.31% | -42.64% | +81.95% | -34.93% | -76.74% | 0.52 | -0.13 | 24 | +62.50% | 1.69 | +7.15% |
| AMZN | ✅ | composite | sl 10.0% | tp 15% | trail 10% | hold 30d | +39.71% | -11.49% | +51.20% | -31.59% | -56.15% | 0.56 | 0.09 | 21 | +42.86% | 1.65 | +6.80% |
| AMD | ✅ | above_50ma | sl 10.0% | tp 20% | trail 10% | hold 30d | +82.43% | +31.91% | +50.52% | -47.38% | -65.45% | 0.70 | 0.44 | 28 | +50.00% | 1.81 | +10.33% |
| BAC | ✅ | composite | sl 7.5% | tp 20% | trail 10% | hold 30d | +45.94% | -0.48% | +46.42% | -37.68% | -48.48% | 0.63 | 0.20 | 20 | +55.00% | 1.68 | +5.89% |
| AAPL | ✅ | ret20_pos | sl 7.5% | tp 20% | trail 10% | hold 30d | +122.35% | +76.63% | +45.72% | -25.25% | -31.43% | 1.13 | 0.70 | 22 | +59.09% | 2.60 | +8.79% |
| MSFT | ✅ | above_50ma | sl 7.5% | tp null | trail 10% | hold 30d | +94.73% | +53.58% | +41.15% | -20.84% | -37.15% | 1.05 | 0.59 | 23 | +59.09% | 2.90 | +7.69% |
| GOOGL | ✅ | qqq_above_50ma | sl 10.0% | tp 15% | trail 10% | hold 30d | +70.00% | +28.93% | +41.07% | -33.49% | -44.32% | 0.86 | 0.42 | 21 | +66.67% | 2.14 | +7.18% |
| COST | ✅ | ret20_pos | sl 7.5% | tp null | trail 10% | hold 30d | +87.36% | +64.41% | +22.95% | -14.36% | -31.40% | 1.12 | 0.75 | 21 | +66.67% | 2.98 | +6.04% |
| ORCL | ✅ | composite | sl 7.5% | tp null | trail null | hold 30d | +81.61% | +59.27% | +22.34% | -30.00% | -40.36% | 0.85 | 0.63 | 20 | +57.89% | 2.60 | +5.78% |
| MU | ✅ | composite | sl 10.0% | tp 15% | trail null | hold 30d | +12.08% | -8.85% | +20.92% | -46.18% | -49.63% | 0.28 | 0.18 | 20 | +50.00% | 1.27 | +4.58% |
| JPM | ✅ | qqq_above_50ma | sl 7.5% | tp null | trail 15% | hold 30d | +23.11% | +4.16% | +18.95% | -33.87% | -43.06% | 0.40 | 0.22 | 21 | +42.86% | 1.46 | +5.71% |
| PANW | ✅ | qqq_above_50ma | sl 7.5% | tp 15% | trail 10% | hold 30d | +88.87% | +77.83% | +11.04% | -27.95% | -46.80% | 0.83 | 0.66 | 26 | +61.54% | 1.91 | +8.81% |
| CRWD | ✅ | composite | sl 10.0% | tp 20% | trail 15% | hold 30d | +114.90% | +112.97% | +1.94% | -54.72% | -65.90% | 0.84 | 0.72 | 26 | +53.85% | 1.80 | +14.82% |
| GS | ❌ | composite | sl 10.0% | tp null | trail null | hold 60d | +76.78% | +56.74% | +20.04% | -28.18% | -45.62% | 0.85 | 0.59 | 11 | +60.00% | 2.24 | +2.67% |
| AVGO | ❌ | ret20_pos | sl 7.5% | tp null | trail 10% | hold 60d | +106.47% | +92.75% | +13.72% | -32.87% | -48.30% | 1.02 | 0.75 | 14 | +53.85% | 2.85 | +4.46% |
| ASML | ❌ | above_50ma | sl 10.0% | tp 15% | trail 15% | hold 60d | +96.58% | +85.30% | +11.28% | -43.34% | -56.86% | 0.85 | 0.68 | 18 | +58.82% | 2.36 | +6.14% |

## Portfolio vs Benchmarks — TRAIN (in-sample)

| Strategy | Total Return | Max DD | Sharpe |
|----------|--------------|--------|--------|
| **Active portfolio** (+39.87% avg exp) | +65.71% | -11.33% | 1.67 |
| SPY | +23.49% | -33.72% | 0.41 |
| QQQ | +25.40% | -35.12% | 0.40 |
| EW buy-hold (full universe) | +55.81% | -41.46% | 0.61 |
| EW buy-hold (eligible only) | +63.64% | -40.49% | 0.67 |
| EW eligible, capital-matched | +25.37% | -25.86% | 0.55 |

## Portfolio vs Benchmarks — TEST (out-of-sample)

| Strategy | Total Return | Max DD | Sharpe |
|----------|--------------|--------|--------|
| **Active portfolio** (+44.06% avg exp) | +69.38% | -11.69% | 1.64 |
| SPY | +103.18% | -18.76% | 1.44 |
| QQQ | +178.01% | -22.77% | 1.60 |
| EW buy-hold (full universe) | +402.55% | -27.11% | 2.01 |
| EW buy-hold (eligible only) | +378.39% | -26.15% | 2.06 |
| EW eligible, capital-matched | +166.73% | -18.43% | 1.94 |

## Interpretation

- 17/20 tickers cleared the full active-eligibility gate in-sample. Eligible names then form the portfolio.
- **The TEST block is the verdict.** If the portfolio's TEST row does not beat EW-eligible buy-and-hold, the in-sample eligibility did not generalise — i.e. it was grid-search luck.
- All TRAIN numbers are in-sample by construction (best-of-grid). Re-run with the second split to confirm; a real edge survives both.
