# Per-Ticker Criteria Evaluation — Timing vs Buy-and-Hold
**Criteria:** `ticker_timing_criteria_2026-06-12.yaml`  |  **Period:** 2023-06-12 → 2026-06-12  |  **Generated:** 2026-06-12

> Applies a **fixed** per-ticker rule as given — **no parameter search**. Use a period **disjoint** from where the criteria were calibrated for a true out-of-sample read; over the calibration period this is in-sample.

---

## Summary

- **0 / 21** tickers beat buy-and-hold (total return).
- **6 / 21** beat their exposure-matched hold (the fair test).
- Median outperformance: **-93.75%**.

## Per-Ticker (fixed criteria)

| Ticker | Rule (fast/slow/trail) | Timed Ret | Hold Ret | Outperf | Beats Exp-Matched | Timed Sharpe | Hold Sharpe | Timed MaxDD | Hold MaxDD | % In-Mkt | Trades |
|--------|------------------------|-----------|----------|---------|-------------------|--------------|-------------|-------------|------------|----------|--------|
| MSFT | 20/100/none | +14.96% | +21.17% | -6.21% | ✅ | 0.41 | 0.40 | -14.06% | -33.91% | +47.49% | 54 |
| ORCL | 20/50/none | +49.35% | +63.83% | -14.48% | ✅ | 0.59 | 0.57 | -25.89% | -58.25% | +46.15% | 60 |
| META | 10/100/none | +47.31% | +80.51% | -33.20% | ✅ | 0.71 | 0.75 | -27.36% | -34.15% | +45.95% | 82 |
| AAPL | 20/50/none | +26.68% | +60.62% | -33.94% | ❌ | 0.60 | 0.74 | -13.62% | -33.36% | +51.06% | 44 |
| TSLA | 20/100/15% | +24.87% | +61.63% | -36.77% | ✅ | 0.40 | 0.58 | -44.09% | -53.77% | +38.69% | 56 |
| NFLX | 20/50/none | +42.48% | +89.49% | -47.01% | ❌ | 0.66 | 0.80 | -30.38% | -43.35% | +53.58% | 56 |
| COST | 20/50/none | +43.06% | +96.27% | -53.21% | ❌ | 0.89 | 1.24 | -16.56% | -20.74% | +55.84% | 78 |
| AMZN | 20/50/none | +16.38% | +88.47% | -72.09% | ❌ | 0.35 | 0.84 | -25.66% | -30.88% | +55.97% | 80 |
| BAC | 10/50/none | +33.79% | +107.31% | -73.52% | ❌ | 0.69 | 1.11 | -14.49% | -27.51% | +51.19% | 95 |
| COIN | 10/50/none | +138.45% | +216.02% | -77.57% | ✅ | 0.84 | 0.87 | -47.89% | -66.39% | +34.22% | 86 |
| JPM | 10/50/none | +49.80% | +143.55% | -93.75% | ❌ | 1.04 | 1.42 | -19.24% | -24.42% | +56.63% | 103 |
| GOOGL | 20/50/none | +92.87% | +193.49% | -100.62% | ❌ | 1.07 | 1.36 | -23.43% | -29.81% | +60.08% | 64 |
| AMD | 10/100/none | +216.32% | +337.95% | -121.63% | ✅ | 1.27 | 1.20 | -35.55% | -63.00% | +38.13% | 74 |
| ASML | 20/100/none | +40.51% | +175.16% | -134.64% | ❌ | 0.57 | 1.06 | -29.17% | -45.48% | +50.84% | 71 |
| PANW | 20/50/none | +8.06% | +144.06% | -136.00% | ❌ | 0.25 | 0.94 | -47.26% | -36.01% | +51.86% | 67 |
| GS | 10/100/none | +24.93% | +220.65% | -195.72% | ❌ | 0.52 | 1.57 | -23.42% | -30.90% | +56.98% | 122 |
| TSM | 20/50/none | +97.85% | +314.88% | -217.03% | ❌ | 0.92 | 1.43 | -20.86% | -36.82% | +63.00% | 67 |
| AVGO | 10/100/none | +60.17% | +340.86% | -280.69% | ❌ | 0.63 | 1.29 | -26.19% | -41.15% | +51.12% | 104 |
| CRWD | 20/100/none | +71.30% | +352.28% | -280.98% | ❌ | 0.79 | 1.37 | -28.10% | -44.44% | +53.35% | 59 |
| NVDA | 20/100/none | +34.92% | +352.67% | -317.75% | ❌ | 0.48 | 1.36 | -46.83% | -36.88% | +58.24% | 82 |
| MU | 20/100/none | +333.55% | +1330.42% | -996.87% | ❌ | 1.37 | 1.86 | -53.27% | -57.63% | +57.68% | 71 |

## Interpretation

- 0/21 beat hold and 6/21 cleared the exposure-matched bar. If this window is disjoint from calibration, the survivors are the criteria worth keeping.
- Compare this against the **seed** criteria over the same window to see whether calibration actually improved on the broad-bucket defaults.
