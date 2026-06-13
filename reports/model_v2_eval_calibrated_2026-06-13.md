# Per-Ticker Criteria Evaluation — Timing vs Buy-and-Hold
**Criteria:** `ticker_timing_criteria_2026-06-13.yaml`  |  **Period:** 2023-01-01 → 2026-06-13  |  **Generated:** 2026-06-13

> Applies a **fixed** per-ticker rule as given — **no parameter search**. Use a period **disjoint** from where the criteria were calibrated for a true out-of-sample read; over the calibration period this is in-sample.

---

## Summary

- **0 / 21** tickers beat buy-and-hold (total return).
- **3 / 21** beat their exposure-matched hold (the fair test).
- Median outperformance: **-200.52%**.

## Per-Ticker (fixed criteria)

| Ticker | Rule (fast/slow/trail) | Timed Ret | Hold Ret | Outperf | Beats Exp-Matched | Timed Sharpe | Hold Sharpe | Timed MaxDD | Hold MaxDD | % In-Mkt | Trades |
|--------|------------------------|-----------|----------|---------|-------------------|--------------|-------------|-------------|------------|----------|--------|
| MSFT | 10/100/none | +35.21% | +67.74% | -32.53% | ✅ | 0.65 | 0.74 | -10.20% | -33.91% | +46.18% | 96 |
| NFLX | 10/100/none | +128.24% | +172.39% | -44.14% | ✅ | 1.18 | 1.02 | -26.17% | -43.35% | +49.77% | 116 |
| ORCL | 20/50/none | +80.93% | +129.66% | -48.73% | ✅ | 0.72 | 0.75 | -25.89% | -58.25% | +50.12% | 72 |
| BAC | 10/50/none | +32.35% | +82.83% | -50.48% | ❌ | 0.62 | 0.82 | -14.49% | -29.97% | +48.03% | 101 |
| COST | 20/50/none | +47.89% | +126.44% | -78.55% | ❌ | 0.86 | 1.29 | -16.56% | -20.74% | +55.32% | 92 |
| AAPL | 20/100/none | +53.52% | +136.72% | -83.21% | ❌ | 0.89 | 1.12 | -12.11% | -33.36% | +52.78% | 50 |
| JPM | 20/50/none | +39.74% | +158.04% | -118.30% | ❌ | 0.72 | 1.31 | -19.89% | -24.42% | +61.34% | 85 |
| AMZN | 20/50/none | +48.13% | +177.97% | -129.84% | ❌ | 0.63 | 1.10 | -25.66% | -30.88% | +58.10% | 88 |
| TSLA | 20/50/none | +109.17% | +275.98% | -166.81% | ❌ | 0.77 | 0.95 | -36.09% | -53.77% | +46.64% | 70 |
| META | 10/50/none | +177.81% | +358.10% | -180.29% | ❌ | 1.20 | 1.34 | -28.99% | -34.15% | +51.39% | 98 |
| GOOGL | 20/50/none | +106.65% | +307.17% | -200.52% | ❌ | 1.01 | 1.51 | -25.88% | -29.81% | +60.30% | 78 |
| GS | 10/100/none | +30.67% | +234.19% | -203.51% | ❌ | 0.53 | 1.39 | -23.42% | -30.90% | +52.66% | 134 |
| ASML | 20/100/none | +31.98% | +249.73% | -217.74% | ❌ | 0.43 | 1.10 | -29.17% | -45.48% | +52.43% | 85 |
| PANW | 20/50/none | +55.82% | +303.93% | -248.11% | ❌ | 0.58 | 1.22 | -47.26% | -36.01% | +54.63% | 71 |
| COIN | 20/50/none | +83.73% | +375.54% | -291.81% | ❌ | 0.59 | 0.95 | -60.07% | -66.39% | +39.47% | 74 |
| TSM | 20/50/none | +159.10% | +503.12% | -344.02% | ❌ | 1.09 | 1.56 | -20.86% | -36.82% | +61.69% | 71 |
| CRWD | 20/50/none | +132.89% | +561.12% | -428.22% | ❌ | 0.95 | 1.42 | -27.37% | -44.44% | +57.18% | 67 |
| AMD | 10/100/none | +225.75% | +699.08% | -473.33% | ❌ | 1.10 | 1.37 | -35.55% | -63.00% | +41.67% | 98 |
| AVGO | 20/50/none | +82.55% | +623.51% | -540.96% | ❌ | 0.66 | 1.46 | -30.96% | -41.15% | +61.34% | 82 |
| NVDA | 20/100/none | +208.87% | +1336.58% | -1127.70% | ❌ | 1.08 | 1.84 | -46.83% | -36.88% | +63.19% | 92 |
| MU | 20/100/none | +316.07% | +1877.97% | -1561.90% | ❌ | 1.18 | 1.82 | -53.27% | -57.63% | +57.87% | 89 |

## Interpretation

- 0/21 beat hold and 3/21 cleared the exposure-matched bar. If this window is disjoint from calibration, the survivors are the criteria worth keeping.
- Compare this against the **seed** criteria over the same window to see whether calibration actually improved on the broad-bucket defaults.
