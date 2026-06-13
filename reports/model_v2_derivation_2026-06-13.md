# model_v2 — All-Ticker Best-Config Derivation
**Universe:** 21 names  |  **Train (fit):** 2019-01-01 → 2026-06-13  |  **Test (in-sample read):** 2023-01-01 → 2026-06-13  |  **Objective:** sharpe  |  **Generated:** 2026-06-13

> Every ticker is grid-searched over the full train window for its best stop/tp/trail/hold rule and written into `model_v2` with that config. **Train contains test**, so the TEST columns are an in-sample read, not out-of-sample validation.

## Factor screen verdict

- Surviving factors (rank-IC): **reversal_21**.

## Per-ticker best config (sorted by in-sample TEST excess vs hold)

| Ticker | Best rule (filter / sl / tp / trail / hold) | TRAIN excess | TRAIN Sharpe | TEST excess | TEST act ret | TEST hold ret | Eligible |
|--------|---------------------------------------------|--------------|--------------|-------------|--------------|---------------|----------|
| CRWD | ret20_pos / 7.5% / 15% / null / 30d | -60.2% | 1.05 | +115.2% | +676.3% | +561.1% | · |
| ORCL | ret20_pos / 10.0% / 15% / null / 60d | +217.0% | 0.95 | +109.7% | +239.3% | +129.7% | ✅ |
| COIN | composite / 10.0% / null / null / 60d | +266.7% | 0.66 | +81.8% | +457.3% | +375.5% | ✅ |
| NFLX | composite / 7.5% / 15% / null / 60d | +270.7% | 0.89 | +15.0% | +187.4% | +172.4% | ✅ |
| PANW | qqq_above_50ma / 7.5% / null / 15% / 60d | -170.4% | 0.97 | +10.9% | +314.9% | +303.9% | · |
| GOOGL | above_50ma / 10.0% / 20% / null / 30d | +59.8% | 1.22 | +10.6% | +317.8% | +307.2% | ✅ |
| BAC | ret20_pos / 10.0% / 15% / null / 60d | -8.3% | 0.63 | +8.3% | +91.1% | +82.8% | · |
| MSFT | above_50ma / 7.5% / 20% / 10% / 30d | +96.7% | 1.12 | +5.1% | +72.8% | +67.7% | ✅ |
| AVGO | above_50ma / 7.5% / 15% / 15% / 60d | -281.4% | 1.25 | -4.4% | +619.1% | +623.5% | · |
| AMZN | qqq_above_50ma / 10.0% / 15% / null / 60d | +20.0% | 0.72 | -4.4% | +173.5% | +178.0% | ✅ |
| COST | ret20_pos / 10.0% / 20% / 10% / 60d | -9.6% | 1.24 | -13.6% | +112.9% | +126.4% | · |
| ASML | above_50ma / 10.0% / 15% / 15% / 60d | -370.3% | 1.08 | -15.3% | +234.5% | +249.7% | · |
| AAPL | qqq_above_50ma / 10.0% / 20% / null / 60d | -109.6% | 1.18 | -16.8% | +119.9% | +136.7% | · |
| JPM | qqq_above_50ma / 10.0% / null / 15% / 60d | +4.9% | 0.94 | -38.0% | +120.0% | +158.0% | ✅ |
| TSM | ret20_pos / 7.5% / 15% / null / 60d | +222.4% | 1.34 | -59.6% | +443.5% | +503.1% | ✅ |
| GS | composite / 10.0% / null / 15% / 60d | -217.4% | 1.03 | -76.8% | +157.4% | +234.2% | · |
| META | qqq_above_50ma / 10.0% / null / null / 60d | +461.4% | 1.06 | -83.4% | +274.7% | +358.1% | ✅ |
| TSLA | composite / 10.0% / 15% / 10% / 30d | +1075.7% | 1.28 | -218.2% | +57.8% | +276.0% | ✅ |
| MU | qqq_above_50ma / 10.0% / null / 15% / 60d | -647.1% | 1.20 | -356.7% | +1521.2% | +1878.0% | · |
| AMD | qqq_above_50ma / 10.0% / 15% / null / 30d | -906.2% | 1.09 | -387.2% | +311.9% | +699.1% | · |
| NVDA | above_50ma / 10.0% / null / null / 60d | -2198.1% | 1.34 | -692.1% | +644.5% | +1336.6% | · |

## Summary

- **21/21** tickers fitted and written to `model_v2`.
- In-sample TEST read: **8/21** names' fitted rule beat their own buy-and-hold on 2023-2026 (in-sample — optimistic).

## Honest caveats

- **This is a best-fit, not a validated, model.** Train (2019-2026) contains the test window, so every per-ticker number here is in-sample. The real test is a fresh, disjoint period.
- The earlier ≥2-OOS-test build kept only MSFT/NFLX/ORCL; this build keeps everyone by request. Most of these names' timing rules lose to buy-and-hold out-of-sample (see the prior derivation).
- Composite-ranker entries still decide which fitted name is actually bought each day; per-ticker entry filters shown are informational (not wired into the engine).

Run it:

```bash
python run.py scenario model_v2 --start 2023-01-01 --end 2026-06-13
```
