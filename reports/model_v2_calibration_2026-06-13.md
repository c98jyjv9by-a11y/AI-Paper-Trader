# Per-Ticker Signal Calibration — Timing vs Buy-and-Hold
**Period:** 2019-01-01 → 2026-06-13  |  **Generated:** 2026-06-13

> **Out-of-sample, walk-forward.** Calibration objective: **sharpe** (the rule chosen on each 252-day train window maximises this), reported ONLY on the following 63-day test window, stepped quarterly. Comparison is timed vs buy-and-hold of the same ticker over the same out-of-sample span.

---

## Does timing beat holding? (out-of-sample)

- **0 / 21 tickers** had positive OOS timed-minus-hold outperformance.
- Median OOS outperformance: **-258.24%**.

> ⚠️ With ~25 names tested, roughly half would beat hold by chance even with no skill. Treat a result as real only if outperformance is large, the per-fold parameters are stable, and it survives a fresh out-of-sample period. Few trades per ticker = high variance.

## Per-Ticker Results (out-of-sample)

| Ticker | Timed Ret | Hold Ret | Outperf | Test-win rate | OOS Trades | % In-Market | Param Stability | Modal Rule (fast/slow/trail) |
|--------|-----------|----------|---------|---------------|------------|-------------|-----------------|------------------------------|
| COIN | -14.13% | +41.23% | -55.36% | +50.00% | 90 | +32.94% | +37.50% | 20/50/none |
| META | +141.24% | +201.90% | -60.66% | +40.00% | 163 | +42.73% | +44.00% | 10/50/none |
| BAC | +10.03% | +72.32% | -62.29% | +20.00% | 186 | +44.00% | +48.00% | 10/50/none |
| AMZN | +45.36% | +146.21% | -100.84% | +28.00% | 168 | +49.02% | +48.00% | 20/50/none |
| MSFT | +29.87% | +145.19% | -115.32% | +36.00% | 190 | +50.67% | +28.00% | 10/100/none |
| JPM | +7.13% | +162.04% | -154.90% | +20.00% | 203 | +48.83% | +44.00% | 20/50/none |
| ORCL | +22.26% | +180.49% | -158.23% | +36.00% | 176 | +45.14% | +44.00% | 20/50/none |
| AAPL | +79.31% | +259.79% | -180.48% | +28.00% | 127 | +49.52% | +40.00% | 20/100/none |
| NFLX | +11.18% | +209.42% | -198.24% | +28.00% | 194 | +46.86% | +36.00% | 10/100/none |
| COST | +72.53% | +287.79% | -215.26% | +24.00% | 166 | +54.48% | +56.00% | 20/50/none |
| GS | +88.88% | +347.12% | -258.24% | +28.00% | 182 | +49.59% | +68.00% | 10/100/none |
| ASML | +143.15% | +405.59% | -262.44% | +36.00% | 175 | +48.63% | +36.00% | 20/100/none |
| AMD | +52.92% | +381.96% | -329.04% | +40.00% | 154 | +39.94% | +36.00% | 10/100/none |
| GOOGL | +37.02% | +369.24% | -332.23% | +28.00% | 182 | +52.83% | +48.00% | 20/50/none |
| PANW | -8.58% | +325.61% | -334.19% | +20.00% | 162 | +49.90% | +52.00% | 20/50/none |
| CRWD | +22.49% | +358.55% | -336.07% | +34.78% | 146 | +47.07% | +43.48% | 20/50/none |
| TSM | +115.78% | +581.52% | -465.74% | +28.00% | 166 | +48.32% | +52.00% | 20/50/none |
| MU | +88.21% | +680.27% | -592.06% | +32.00% | 176 | +42.48% | +56.00% | 20/100/none |
| TSLA | +474.20% | +1104.92% | -630.72% | +44.00% | 142 | +43.62% | +24.00% | 20/50/none |
| AVGO | +63.33% | +1182.31% | -1118.97% | +16.00% | 223 | +53.27% | +32.00% | 20/50/none |
| NVDA | +546.64% | +2980.18% | -2433.54% | +24.00% | 184 | +55.43% | +32.00% | 20/100/none |

## Risk-Adjusted & Exposure-Matched (out-of-sample)

_A timing strategy sits in cash part of the time, so compare risk-adjusted and against an **exposure-matched** hold (same % time in market, rest cash). 'Beats exp-matched' is the fair test of whether *when* you were in beat simply being in that fraction of the time._

- **1 / 21** tickers had a higher timed Sharpe than buy-and-hold.
- **1 / 21** tickers beat their exposure-matched hold (the fair return test).

| Ticker | Timed Ret | Exp-Matched Hold | Beats Exp-Matched | Timed Sharpe | Hold Sharpe | Timed MaxDD | Hold MaxDD | Timed Calmar | Hold Calmar |
|--------|-----------|------------------|-------------------|--------------|-------------|-------------|------------|--------------|-------------|
| COIN | -14.13% | +13.58% | ❌ | 0.19 | 0.54 | -67.95% | -78.98% | -0.06 | 0.12 |
| META | +141.24% | +86.27% | ✅ | 0.71 | 0.63 | -28.84% | -76.74% | 0.53 | 0.26 |
| BAC | +10.03% | +31.82% | ❌ | 0.18 | 0.43 | -31.19% | -48.48% | 0.05 | 0.19 |
| AMZN | +45.36% | +71.66% | ❌ | 0.39 | 0.58 | -40.77% | -56.15% | 0.15 | 0.28 |
| MSFT | +29.87% | +73.56% | ❌ | 0.33 | 0.63 | -28.38% | -37.15% | 0.15 | 0.42 |
| JPM | +7.13% | +79.11% | ❌ | 0.15 | 0.65 | -38.67% | -43.06% | 0.03 | 0.39 |
| ORCL | +22.26% | +81.48% | ❌ | 0.26 | 0.61 | -30.60% | -58.25% | 0.11 | 0.31 |
| AAPL | +79.31% | +128.66% | ❌ | 0.61 | 0.81 | -29.16% | -33.36% | 0.34 | 0.69 |
| NFLX | +11.18% | +98.13% | ❌ | 0.19 | 0.64 | -60.64% | -75.95% | 0.03 | 0.27 |
| COST | +72.53% | +156.77% | ❌ | 0.66 | 1.04 | -21.12% | -31.40% | 0.44 | 0.78 |
| GS | +88.88% | +172.13% | ❌ | 0.66 | 0.89 | -31.81% | -45.62% | 0.34 | 0.60 |
| ASML | +143.15% | +197.26% | ❌ | 0.69 | 0.82 | -38.95% | -56.86% | 0.40 | 0.53 |
| AMD | +52.92% | +152.54% | ❌ | 0.37 | 0.73 | -47.46% | -65.45% | 0.15 | 0.44 |
| GOOGL | +37.02% | +195.05% | ❌ | 0.35 | 0.93 | -45.40% | -44.32% | 0.12 | 0.64 |
| PANW | -8.58% | +162.50% | ❌ | 0.08 | 0.77 | -48.11% | -46.80% | -0.03 | 0.57 |
| CRWD | +22.49% | +168.76% | ❌ | 0.27 | 0.77 | -48.02% | -67.69% | 0.08 | 0.46 |
| TSM | +115.78% | +280.98% | ❌ | 0.61 | 0.98 | -37.05% | -56.47% | 0.36 | 0.65 |
| MU | +88.21% | +288.95% | ❌ | 0.48 | 0.90 | -55.02% | -57.63% | 0.20 | 0.69 |
| TSLA | +474.20% | +481.96% | ❌ | 0.89 | 0.93 | -43.89% | -73.63% | 0.75 | 0.68 |
| AVGO | +63.33% | +629.81% | ❌ | 0.42 | 1.15 | -35.76% | -48.30% | 0.23 | 1.06 |
| NVDA | +546.64% | +1651.87% | ❌ | 1.04 | 1.31 | -51.53% | -66.34% | 0.69 | 1.12 |

## Interpretation

- **0/21** beat buy-and-hold OOS; median edge -258.24%. Most names did worse timed than held — the rule mostly costs return via whipsaws/cash drag.
- **No ticker** combined a >+5% OOS edge with stable per-fold parameters. That is the signature of curve-fitting: the 'best' train parameters keep changing and don't carry to test data — i.e. there is no reliable per-ticker timing edge here.
- **Fair (exposure-matched) verdict:** 1/21 names beat their exposure-matched hold and 1/21 improved Sharpe vs holding. Even adjusting for time-in-market, the timing rule does not broadly add value here.

- **Next:** re-run on a later, non-overlapping window. A genuine per-ticker edge persists; an overfit one evaporates. All results here are still in-sample at the universe-selection level (we chose these tickers), so treat survivors as hypotheses, not conclusions.
