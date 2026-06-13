# Per-Ticker Signal Calibration — Timing vs Buy-and-Hold
**Period:** 2018-06-12 → 2023-06-12  |  **Generated:** 2026-06-12

> **Out-of-sample, walk-forward.** Calibration objective: **total_return** (the rule chosen on each 252-day train window maximises this), reported ONLY on the following 63-day test window, stepped quarterly. Comparison is timed vs buy-and-hold of the same ticker over the same out-of-sample span.

---

## Does timing beat holding? (out-of-sample)

- **3 / 21 tickers** had positive OOS timed-minus-hold outperformance.
- Median OOS outperformance: **-69.72%**.

> ⚠️ With ~25 names tested, roughly half would beat hold by chance even with no skill. Treat a result as real only if outperformance is large, the per-fold parameters are stable, and it survives a fresh out-of-sample period. Few trades per ticker = high variance.

## Per-Ticker Results (out-of-sample)

| Ticker | Timed Ret | Hold Ret | Outperf | Test-win rate | OOS Trades | % In-Market | Param Stability | Modal Rule (fast/slow/trail) |
|--------|-----------|----------|---------|---------------|------------|-------------|-----------------|------------------------------|
| META | +63.91% | +25.99% | +37.92% | +46.67% | 92 | +38.62% | +46.67% | 10/100/none |
| COIN | -47.86% | -53.99% | +6.12% | +50.00% | 31 | +23.81% | +50.00% | 10/50/none |
| AMZN | +22.79% | +18.02% | +4.77% | +33.33% | 81 | +40.21% | +66.67% | 20/50/none |
| GS | +64.85% | +73.00% | -8.14% | +40.00% | 95 | +42.33% | +60.00% | 10/100/none |
| BAC | -13.39% | +8.31% | -21.70% | +33.33% | 107 | +38.20% | +53.33% | 10/50/none |
| NFLX | -19.68% | +8.85% | -28.53% | +20.00% | 122 | +41.38% | +40.00% | 20/50/none |
| TSM | +94.93% | +125.21% | -30.28% | +40.00% | 99 | +46.67% | +66.67% | 20/50/none |
| MU | +17.01% | +47.58% | -30.58% | +33.33% | 86 | +37.25% | +86.67% | 20/100/none |
| JPM | -8.89% | +42.30% | -51.19% | +26.67% | 119 | +43.92% | +33.33% | 10/50/none |
| ASML | +147.42% | +214.81% | -67.39% | +33.33% | 100 | +51.75% | +53.33% | 20/100/none |
| COST | +22.85% | +92.57% | -69.72% | +26.67% | 108 | +53.54% | +86.67% | 20/50/none |
| CRWD | -12.64% | +59.00% | -71.64% | +33.33% | 70 | +42.06% | +41.67% | 20/100/none |
| GOOGL | -9.19% | +83.30% | -92.49% | +20.00% | 118 | +51.22% | +66.67% | 20/50/none |
| ORCL | -12.72% | +93.12% | -105.84% | +13.33% | 114 | +45.19% | +53.33% | 20/50/none |
| MSFT | +20.34% | +136.86% | -116.52% | +40.00% | 135 | +56.19% | +33.33% | 20/100/none |
| AMD | +76.89% | +225.59% | -148.70% | +26.67% | 102 | +39.68% | +40.00% | 10/100/none |
| AAPL | +107.77% | +258.88% | -151.11% | +46.67% | 88 | +56.08% | +73.33% | 20/50/none |
| AVGO | +0.17% | +165.81% | -165.64% | +20.00% | 144 | +54.18% | +33.33% | 10/100/none |
| PANW | -10.99% | +171.04% | -182.03% | +26.67% | 87 | +51.53% | +40.00% | 20/50/none |
| TSLA | +756.94% | +1003.95% | -247.02% | +46.67% | 80 | +50.16% | +26.67% | 20/100/15% |
| NVDA | +266.84% | +661.78% | -394.93% | +33.33% | 113 | +56.61% | +40.00% | 20/100/none |

## Risk-Adjusted & Exposure-Matched (out-of-sample)

_A timing strategy sits in cash part of the time, so compare risk-adjusted and against an **exposure-matched** hold (same % time in market, rest cash). 'Beats exp-matched' is the fair test of whether *when* you were in beat simply being in that fraction of the time._

- **6 / 21** tickers had a higher timed Sharpe than buy-and-hold.
- **6 / 21** tickers beat their exposure-matched hold (the fair return test).

| Ticker | Timed Ret | Exp-Matched Hold | Beats Exp-Matched | Timed Sharpe | Hold Sharpe | Timed MaxDD | Hold MaxDD | Timed Calmar | Hold Calmar |
|--------|-----------|------------------|-------------------|--------------|-------------|-------------|------------|--------------|-------------|
| META | +63.91% | +10.04% | ✅ | 0.69 | 0.37 | -28.58% | -76.74% | 0.50 | 0.08 |
| COIN | -47.86% | -12.85% | ❌ | -0.83 | -0.06 | -52.30% | -78.98% | -0.92 | -0.69 |
| AMZN | +22.79% | +7.25% | ✅ | 0.37 | 0.31 | -37.70% | -56.15% | 0.15 | 0.08 |
| GS | +64.85% | +30.90% | ✅ | 0.89 | 0.59 | -22.10% | -45.62% | 0.66 | 0.35 |
| BAC | -13.39% | +3.17% | ❌ | -0.16 | 0.25 | -34.10% | -48.95% | -0.11 | 0.04 |
| NFLX | -19.68% | +3.66% | ❌ | -0.09 | 0.30 | -49.92% | -75.95% | -0.12 | 0.03 |
| TSM | +94.93% | +58.43% | ✅ | 0.87 | 0.76 | -34.09% | -56.47% | 0.58 | 0.44 |
| MU | +17.01% | +17.72% | ❌ | 0.29 | 0.46 | -30.06% | -49.63% | 0.14 | 0.22 |
| JPM | -8.89% | +18.58% | ❌ | -0.06 | 0.44 | -36.20% | -43.63% | -0.07 | 0.23 |
| ASML | +147.42% | +111.16% | ✅ | 1.11 | 0.92 | -24.46% | -56.86% | 1.14 | 0.64 |
| COST | +22.85% | +49.57% | ❌ | 0.44 | 0.81 | -21.01% | -31.40% | 0.27 | 0.62 |
| CRWD | -12.64% | +24.82% | ❌ | 0.02 | 0.56 | -52.62% | -67.69% | -0.08 | 0.25 |
| GOOGL | -9.19% | +42.66% | ❌ | -0.05 | 0.65 | -38.76% | -44.32% | -0.07 | 0.40 |
| ORCL | -12.72% | +42.08% | ❌ | -0.13 | 0.71 | -27.67% | -40.36% | -0.13 | 0.48 |
| MSFT | +20.34% | +76.90% | ❌ | 0.37 | 0.86 | -27.73% | -37.15% | 0.19 | 0.71 |
| AMD | +76.89% | +89.52% | ❌ | 0.64 | 0.85 | -35.59% | -65.45% | 0.47 | 0.58 |
| AAPL | +107.77% | +145.19% | ❌ | 1.04 | 1.16 | -25.02% | -31.43% | 0.87 | 1.31 |
| AVGO | +0.17% | +89.84% | ❌ | 0.11 | 0.88 | -31.85% | -48.30% | 0.00 | 0.63 |
| PANW | -10.99% | +88.15% | ❌ | -0.02 | 0.86 | -57.08% | -47.03% | -0.05 | 0.66 |
| TSLA | +756.94% | +503.57% | ✅ | 1.45 | 1.27 | -41.44% | -73.63% | 1.90 | 1.24 |
| NVDA | +266.84% | +374.66% | ❌ | 1.21 | 1.28 | -33.31% | -66.34% | 1.27 | 1.10 |

## Interpretation

- **3/21** beat buy-and-hold OOS; median edge -69.72%. Most names did worse timed than held — the rule mostly costs return via whipsaws/cash drag.
- **Stable candidates** (>+5% OOS edge AND ≥50% param stability): `COIN`. These are the only ones worth a dedicated out-of-sample retest; everything else is likely noise.
- **Fair (exposure-matched) verdict:** 6/21 names beat their exposure-matched hold and 6/21 improved Sharpe vs holding. Even adjusting for time-in-market, the timing rule does not broadly add value here.

- **Next:** re-run on a later, non-overlapping window. A genuine per-ticker edge persists; an overfit one evaporates. All results here are still in-sample at the universe-selection level (we chose these tickers), so treat survivors as hypotheses, not conclusions.
