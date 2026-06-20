# Status & Rank Report — model_v4
**Ranked as of close:** 2026-06-17  |  **Marked to:** 2026-06-18 (latest; may be provisional)  |  **Buy gate:** 0.7  |  **Generated:** 2026-06-20

> Two rankings, clearly separated: **(A) Prior-close ranking** — composite scores fixed at the prior close (2026-06-17) and marked forward to the latest price (shows how those picks did this session); and **(B) Current ranking** — composite scores recomputed on the latest prices (2026-06-18), i.e. the standing that sets up the next session. ✓ = clears the buy gate.

## Signal strength (session: ranking-close → latest)

| Metric | Value |
|--------|-------|
| **Top 10 − Bottom 10 spread** | **+6.26%** |
| Top 10 avg | +5.14% |
| Bottom 10 avg | -1.11% |
| Universe avg (all 83) | +1.71% |
| Held book (equal-wt / $-wt) | +4.77% / +4.75% |
| Advancers | 51/83 |
| Names clearing buy gate | 19/83 |

_Positive spread ⇒ higher-scored names out-returned lower-scored names this session (momentum signal working). One session is mostly market beta; read the spread, not the level._

## Risk budget (volatility targeting)

| Metric | Value |
|--------|-------|
| Forecast volatility (annualized, 126d) | — |
| Vol target | +35.00% |
| Exposure multiplier | 1.00× |
| Effective vs base exposure | 100% of budget |

_Scales gross exposure by clip(target / forecast vol, floor, cap); currently **at full risk budget (calm — forecast ≤ target)**. Affects position sizing only — not the composite scores._

## Today's transactions (2026-06-18)

| Action | Ticker | Shares | Price | Reason | Realized P&L |
|--------|--------|------:|------:|--------|------:|
| BUY | MRVL | 27 | 310.58 | ramp-up entry: score 0.94 (>= 0.90), 8.5% size | — |
| BUY | SOXS | 546 | 3.59 | hedge: HALF gate (5.9% of post-buy book MV) | — |

_Buys fill at the latest close; exits / vol-trims fill same day. `vol_trim` = volatility-governor de-risk sale (if enabled)._

## Recent trade log (last 10)

| Date | Action | Ticker | Shares | Price | Reason | Realized P&L |
|------|--------|--------|------:|------:|--------|------:|
| 2026-06-17 | BUY | HOOD | 80 | 105.31 | seed_top3 | — |
| 2026-06-17 | BUY | AMAT | 14 | 593.51 | seed_top3 | — |
| 2026-06-17 | BUY | ARM | 20 | 419.30 | seed_top3 | — |
| 2026-06-18 | BUY | MRVL | 27 | 310.58 | ramp-up entry: score 0.94 (>= 0.90), 8.5% size | — |
| 2026-06-18 | BUY | SOXS | 546 | 3.59 | hedge: HALF gate (5.9% of post-buy book MV) | — |

## A) Ranking at PRIOR CLOSE (2026-06-17) — scores fixed at that close, marked to the latest price (2026-06-18, may be intraday) — _scores loaded from saved ranking snapshot (authoritative for that date)_

_These are the scores that set up the most recent session; `Return` shows how each did from the prior close to the latest price (the latest bar may be a provisional intraday price, not an official close)._

### Top 10 (highest buy scores @ prior close)

| # | Ticker | Score | Gate | 2026-06-17 close | 2026-06-18 latest | Return | Held |
|---|--------|------:|:----:|------:|------:|-------:|:----:|
| 1 | HOOD | 0.970 | ✓ | 105.20 | 108.15 | +2.80% | HELD |
| 2 | AMAT | 0.950 | ✓ | 592.92 | 617.11 | +4.08% | HELD |
| 3 | ARM | 0.920 | ✓ | 418.88 | 439.46 | +4.91% | HELD |
| 4 | LRCX | 0.890 | ✓ | 374.18 | 389.04 | +3.97% |  |
| 5 | MRVL | 0.880 | ✓ | 289.54 | 310.58 | +7.27% | HELD |
| 6 | MU | 0.870 | ✓ | 1043.19 | 1133.99 | +8.70% |  |
| 7 | KLAC | 0.860 | ✓ | 238.73 | 259.56 | +8.73% |  |
| 8 | ASML | 0.830 | ✓ | 1867.83 | 1929.68 | +3.31% |  |
| 9 | SOFI | 0.810 | ✓ | 17.42 | 17.91 | +2.81% |  |
| 10 | AMD | 0.800 | ✓ | 512.48 | 537.37 | +4.86% |  |
| | | | | | | **AVG +5.14%** | |

### Bottom 10 (lowest buy scores @ prior close)

| # | Ticker | Score | Gate | 2026-06-17 close | 2026-06-18 latest | Return | Held |
|---|--------|------:|:----:|------:|------:|-------:|:----:|
| 74 | CRM | 0.220 | — | 155.02 | 151.78 | -2.09% |  |
| 75 | ADBE | 0.210 | — | 196.28 | 195.16 | -0.57% |  |
| 76 | SAP | 0.210 | — | 158.79 | 155.22 | -2.25% |  |
| 77 | TTD | 0.200 | — | 18.16 | 18.51 | +1.93% |  |
| 78 | TWLO | 0.190 | — | 188.11 | 186.17 | -1.03% |  |
| 79 | WDAY | 0.190 | — | 121.83 | 116.93 | -4.02% |  |
| 80 | OXY | 0.180 | — | 53.04 | 51.82 | -2.30% |  |
| 81 | ZS | 0.170 | — | 124.38 | 124.85 | +0.38% |  |
| 82 | HUBS | 0.150 | — | 176.71 | 176.03 | -0.38% |  |
| 83 | INTU | 0.130 | — | 269.08 | 267.00 | -0.77% |  |
| | | | | | | **AVG -1.11%** | |

## B) CURRENT composite ranking (scored on latest prices 2026-06-18) — sets up the next session

_Recomputed on the current/provisional prices. 19/83 names clear the buy gate now. `Δrank vs prior` = move vs the prior-close ranking (▲ = ranked higher now)._

### Top 10 (highest buy scores @ current prices)

| # | Ticker | Score | Gate | 2026-06-18 px | Δrank vs prior | Held |
|---|--------|------:|:----:|------:|:-------------:|:----:|
| 1 | ARM | 0.977 | ✓ | 439.46 | ▲2 | HELD |
| 2 | MRVL | 0.944 | ✓ | 310.58 | ▲3 | HELD |
| 3 | AMAT | 0.881 | ✓ | 617.11 | ▼1 | HELD |
| 4 | KLAC | 0.871 | ✓ | 259.56 | ▲3 |  |
| 5 | RBLX | 0.857 | ✓ | 51.53 | ▲6 |  |
| 6 | INTC | 0.838 | ✓ | 133.99 | ▲6 |  |
| 7 | LRCX | 0.834 | ✓ | 389.04 | ▼3 |  |
| 8 | TSM | 0.833 | ✓ | 462.12 | ▲12 |  |
| 9 | QCOM | 0.828 | ✓ | 226.11 | ▲5 |  |
| 10 | MU | 0.808 | ✓ | 1133.99 | ▼4 |  |

### Bottom 10 (lowest buy scores @ current prices)

| # | Ticker | Score | Gate | 2026-06-18 px | Δrank vs prior | Held |
|---|--------|------:|:----:|------:|:-------------:|:----:|
| 74 | CRM | 0.250 | — | 151.78 | • |  |
| 75 | TEAM | 0.233 | — | 82.72 | ▼7 |  |
| 76 | SMCI | 0.217 | — | 30.66 | ▼7 |  |
| 77 | ADBE | 0.198 | — | 195.16 | ▼2 |  |
| 78 | INTU | 0.173 | — | 267.00 | ▲5 |  |
| 79 | HUBS | 0.166 | — | 176.03 | ▲3 |  |
| 80 | OXY | 0.163 | — | 51.82 | • |  |
| 81 | NOW | 0.155 | — | 95.04 | ▼14 |  |
| 82 | SNAP | 0.117 | — | 4.66 | ▼9 |  |
| 83 | SAP | 0.115 | — | 155.22 | ▼7 |  |

## Group returns (ranking-close → latest)

| Group | Avg return |
|-------|-----------:|
| Top 10 | +5.14% |
| Universe (all 83) | +1.71% |
| Held book (equal-wt) | +4.77% |
| Bottom 10 | -1.11% |

## Held book — 5 positions  (portfolio $100,961, cash $64,535)

| Ticker | Shares | Entry | Now | Unreal % | Return |
|--------|-------:|------:|----:|---------:|-------:|
| AMAT | 14 | 593.51 | 617.11 | +3.98% | +4.08% |
| ARM | 20 | 419.30 | 439.46 | +4.81% | +4.91% |
| HOOD | 80 | 105.31 | 108.15 | +2.70% | +2.80% |
| MRVL | 27 | 310.58 | 310.58 | +0.00% | +7.27% |
| SOXS | 546 | 3.59 | 3.59 | +0.00% | — |

## Portfolio vs benchmarks

| Window | model_v4 | SPY | QQQ | vs SPY | vs QQQ |
|--------|------:|----:|----:|-------:|-------:|
| 1D | +0.99% | +1.04% | +2.51% | -0.05% | -1.52% |
| 5D | +0.96% | -0.22% | +1.47% | +1.18% | -0.51% |
| MTD | — | -1.30% | -0.29% | — | — |
| Since 2026-06-17 | +0.96% | +1.04% | +2.51% | -0.08% | -1.55% |

_Ranking is reproducible from price history (composite of 1d/5d/20d returns + volume ratio); the latest mark may be a provisional intraday bar that settles at the close._
