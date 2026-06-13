# Per-Ticker Signal Calibration — Timing vs Buy-and-Hold
**Period:** 2021-06-12 → 2026-06-12  |  **Generated:** 2026-06-12

> **Out-of-sample, walk-forward.** Each ticker's rule is calibrated on a 252-day train window and reported ONLY on the following 63-day test window, stepped quarterly. Headline metric: timed total return vs buy-and-hold of the same ticker over the same out-of-sample span.

---

## Does timing beat holding? (out-of-sample)

- **0 / 21 tickers** had positive OOS timed-minus-hold outperformance.
- Median OOS outperformance: **-154.83%**.

> ⚠️ With ~25 names tested, roughly half would beat hold by chance even with no skill. Treat a result as real only if outperformance is large, the per-fold parameters are stable, and it survives a fresh out-of-sample period. Few trades per ticker = high variance.

## Per-Ticker Results (out-of-sample)

| Ticker | Timed Ret | Hold Ret | Outperf | Test-win rate | OOS Trades | % In-Market | Param Stability | Modal Rule (fast/slow/trail) |
|--------|-----------|----------|---------|---------------|------------|-------------|-----------------|------------------------------|
| TSLA | +18.35% | +50.41% | -32.06% | +53.33% | 83 | +36.19% | +33.33% | 20/100/none |
| MSFT | +6.88% | +48.65% | -41.77% | +33.33% | 104 | +45.82% | +40.00% | 10/50/none |
| BAC | +14.77% | +64.71% | -49.95% | +40.00% | 105 | +48.36% | +40.00% | 10/50/none |
| COST | +42.19% | +97.84% | -55.65% | +33.33% | 98 | +51.96% | +53.33% | 20/100/none |
| AMZN | +30.60% | +88.79% | -58.20% | +33.33% | 99 | +51.64% | +53.33% | 20/50/none |
| AAPL | +21.11% | +81.62% | -60.50% | +40.00% | 71 | +48.04% | +53.33% | 20/100/none |
| ORCL | +72.44% | +153.51% | -81.07% | +26.67% | 108 | +46.14% | +40.00% | 20/50/none |
| META | +153.40% | +263.67% | -110.28% | +40.00% | 99 | +47.51% | +53.33% | 10/100/none |
| COIN | -23.68% | +123.15% | -146.82% | +33.33% | 95 | +35.03% | +33.33% | 20/50/none |
| AMD | +191.14% | +338.17% | -147.03% | +40.00% | 77 | +42.75% | +40.00% | 20/50/none |
| GS | +55.86% | +210.69% | -154.83% | +26.67% | 113 | +53.33% | +66.67% | 10/100/none |
| GOOGL | +74.00% | +232.47% | -158.47% | +26.67% | 85 | +51.85% | +80.00% | 20/100/none |
| JPM | +24.90% | +188.88% | -163.98% | +20.00% | 114 | +57.67% | +60.00% | 20/50/none |
| ASML | +6.21% | +172.53% | -166.32% | +33.33% | 113 | +46.88% | +33.33% | 20/100/none |
| PANW | -14.47% | +158.01% | -172.48% | +20.00% | 85 | +49.21% | +73.33% | 20/50/none |
| CRWD | +8.45% | +185.70% | -177.26% | +33.33% | 91 | +47.51% | +60.00% | 20/50/none |
| NFLX | +62.56% | +286.54% | -223.98% | +33.33% | 110 | +52.91% | +46.67% | 10/100/none |
| TSM | +89.74% | +370.29% | -280.56% | +26.67% | 90 | +54.18% | +60.00% | 20/50/none |
| AVGO | +71.61% | +710.33% | -638.72% | +20.00% | 136 | +51.85% | +53.33% | 10/50/none |
| MU | +288.09% | +1151.15% | -863.07% | +13.33% | 109 | +47.72% | +46.67% | 10/100/none |
| NVDA | +185.93% | +1064.54% | -878.61% | +20.00% | 114 | +57.25% | +40.00% | 20/100/none |

## Interpretation

- **0/21** beat buy-and-hold OOS; median edge -154.83%. Most names did worse timed than held — the rule mostly costs return via whipsaws/cash drag.
- **No ticker** combined a >+5% OOS edge with stable per-fold parameters. That is the signature of curve-fitting: the 'best' train parameters keep changing and don't carry to test data — i.e. there is no reliable per-ticker timing edge here.
- **Time-in-market matters:** timed strategies sit in cash part of the time, so even when timed return ≈ hold return, the timed version took less risk. (You chose total-return as the headline; ask me to add Sharpe/Calmar and exposure-adjusted comparison if you want the risk-adjusted verdict.)

- **Next:** re-run on a later, non-overlapping window. A genuine per-ticker edge persists; an overfit one evaporates. All results here are still in-sample at the universe-selection level (we chose these tickers), so treat survivors as hypotheses, not conclusions.
