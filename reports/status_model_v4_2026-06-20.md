# Status & Rank Report — model_v4
**Ranked as of close:** 2026-06-17  |  **Marked to:** 2026-06-18 (latest; may be provisional)  |  **Buy gate:** 0.7  |  **Generated:** 2026-06-20

> Two rankings, clearly separated: **(A) Prior-close ranking** — composite scores fixed at the prior close (2026-06-17) and marked forward to the latest price (shows how those picks did this session); and **(B) Current ranking** — composite scores recomputed on the latest prices (2026-06-18), i.e. the standing that sets up the next session. ✓ = clears the buy gate.

## Signal strength (session: ranking-close → latest)

| Metric | Value |
|--------|-------|
| **Top 10 − Bottom 10 spread** | **+6.26%** |
| Top 10 avg | +5.14% |
| Bottom 10 avg | -1.11% |
| Universe avg (all 83) | +1.69% |
| Held book (equal-wt / $-wt) | +3.59% / +3.67% |
| Advancers | 52/83 |
| Names clearing buy gate | 19/83 |

_Positive spread ⇒ higher-scored names out-returned lower-scored names this session (momentum signal working). One session is mostly market beta; read the spread, not the level._

## Risk budget (volatility targeting)

| Metric | Value |
|--------|-------|
| Forecast volatility (annualized, 126d) | +35.84% |
| Vol target | +35.00% |
| Exposure multiplier | 0.98× |
| Effective vs base exposure | 98% of budget |

_Scales gross exposure by clip(target / forecast vol, floor, cap); currently **de-risked to 98% (forecast vol above the +35.00% target)**. Affects position sizing only — not the composite scores._

## Today's transactions (2026-06-18)

| Action | Ticker | Shares | Price | Reason | Realized P&L |
|--------|--------|------:|------:|--------|------:|
| BUY | AMAT | 2488 | 617.73 | momentum_score=0.9482 | — |

_Buys fill at the latest close; exits / vol-trims fill same day. `vol_trim` = volatility-governor de-risk sale (if enabled)._

## Recent trade log (last 10)

| Date | Action | Ticker | Shares | Price | Reason | Realized P&L |
|------|--------|--------|------:|------:|--------|------:|
| 2026-05-20 | SELL | ASML | 760 | 1548.58 | rotation_funded | $145,834 |
| 2026-05-21 | BUY | CRWD | 1969 | 648.88 | momentum_score=0.9331 | — |
| 2026-06-01 | SELL | COST | 931 | 945.16 | rotation_funded | $-47,311 |
| 2026-06-02 | BUY | SNOW | 5502 | 261.40 | momentum_score=0.9639 | — |
| 2026-06-02 | SELL | INTC | 16502 | 107.82 | rotation_funded | $748,856 |
| 2026-06-03 | BUY | OKTA | 11753 | 124.77 | momentum_score=0.9084 | — |
| 2026-06-15 | SELL | QCOM | 6418 | 220.59 | rotation_funded | $282,740 |
| 2026-06-16 | BUY | KLAC | 5937 | 237.57 | momentum_score=0.9331 | — |
| 2026-06-17 | SELL | CSCO | 11009 | 117.21 | rotation_funded | $-12,281 |
| 2026-06-18 | BUY | AMAT | 2488 | 617.73 | momentum_score=0.9482 | — |

## A) Ranking at PRIOR CLOSE (2026-06-17) — scores fixed at that close, marked to the latest price (2026-06-18, may be intraday) — _scores loaded from saved ranking snapshot (authoritative for that date)_

_These are the scores that set up the most recent session; `Return` shows how each did from the prior close to the latest price (the latest bar may be a provisional intraday price, not an official close)._

### Top 10 (highest buy scores @ prior close)

| # | Ticker | Score | Gate | 2026-06-17 close | 2026-06-18 latest | Return | Held |
|---|--------|------:|:----:|------:|------:|-------:|:----:|
| 1 | HOOD | 0.970 | ✓ | 105.20 | 108.15 | +2.80% |  |
| 2 | AMAT | 0.950 | ✓ | 592.92 | 617.11 | +4.08% | HELD |
| 3 | ARM | 0.920 | ✓ | 418.88 | 439.46 | +4.91% | HELD |
| 4 | LRCX | 0.890 | ✓ | 374.18 | 389.04 | +3.97% |  |
| 5 | MRVL | 0.880 | ✓ | 289.54 | 310.58 | +7.27% | HELD |
| 6 | MU | 0.870 | ✓ | 1043.19 | 1133.99 | +8.70% |  |
| 7 | KLAC | 0.860 | ✓ | 238.73 | 259.56 | +8.73% | HELD |
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

## A2) Intraday return progression — 2026-06-18 (vs prior close 2026-06-17)

_Return from the prior close to each **hourly Chicago-time checkpoint** (9:00, 10:00, 11:00 … up to whatever has traded so far), using 30-min bars. The far-right **Latest** column is the most recent price (≈the 15:00 CT close). Watch the spread between the top and bottom AVG rows build through the session._

### Top 10 @ prior close — intraday path

| Ticker | 9:00 CT | 10:00 CT | 11:00 CT | 12:00 CT | 13:00 CT | 14:00 CT | Latest (≈15:00 CT close) |
|--------|------:|------:|------:|------:|------:|------:|------:|
| HOOD | -0.67% | +3.44% | +0.54% | +2.11% | +1.33% | +0.29% | +2.80% |
| AMAT | +7.30% | +6.52% | +5.90% | +4.61% | +4.02% | +4.04% | +4.08% |
| ARM | +5.32% | +6.74% | +6.08% | +1.92% | +1.46% | +3.20% | +4.91% |
| LRCX | +6.78% | +6.25% | +5.82% | +5.65% | +5.81% | +5.49% | +3.97% |
| MRVL | +6.97% | +11.25% | +11.87% | +12.06% | +12.29% | +11.75% | +7.27% |
| MU | +6.05% | +8.14% | +7.82% | +8.17% | +8.93% | +9.34% | +8.70% |
| KLAC | +7.18% | +6.63% | +8.52% | +8.61% | +8.82% | +9.61% | +8.73% |
| ASML | +2.52% | +3.61% | +2.95% | +2.75% | +2.59% | +2.92% | +3.31% |
| SOFI | +0.86% | +2.87% | +2.12% | +1.82% | +2.32% | +2.07% | +2.81% |
| AMD | +3.51% | +4.15% | +4.39% | +4.24% | +4.26% | +3.66% | +4.86% |
| **AVG** | +4.58% | +5.96% | +5.60% | +5.19% | +5.18% | +5.24% | +5.14% |

### Bottom 10 @ prior close — intraday path

| Ticker | 9:00 CT | 10:00 CT | 11:00 CT | 12:00 CT | 13:00 CT | 14:00 CT | Latest (≈15:00 CT close) |
|--------|------:|------:|------:|------:|------:|------:|------:|
| CRM | -2.44% | -1.54% | -1.64% | -1.64% | -1.15% | -1.46% | -2.09% |
| ADBE | -1.52% | -0.37% | -1.16% | -1.24% | -0.60% | -0.07% | -0.57% |
| SAP | -2.04% | -1.84% | -2.37% | -2.62% | -2.36% | -2.25% | -2.25% |
| TTD | -0.72% | +0.83% | +0.30% | +0.36% | +0.66% | +0.50% | +1.93% |
| TWLO | -3.93% | -1.63% | -1.67% | -1.39% | -0.58% | -1.13% | -1.03% |
| WDAY | -0.80% | -1.89% | -2.57% | -3.01% | -2.57% | -2.83% | -4.02% |
| OXY | -3.00% | -2.82% | -3.07% | -3.24% | -2.98% | -2.64% | -2.30% |
| ZS | -2.73% | -0.88% | -1.33% | -0.92% | +0.48% | +0.51% | +0.38% |
| HUBS | -0.26% | +3.12% | +1.33% | +0.89% | +0.37% | +0.53% | -0.38% |
| INTU | -2.03% | -0.90% | -2.02% | -2.02% | -1.49% | -1.41% | -0.77% |
| **AVG** | -1.95% | -0.79% | -1.42% | -1.48% | -1.02% | -1.03% | -1.11% |

### Held positions — intraday path

| Ticker | 9:00 CT | 10:00 CT | 11:00 CT | 12:00 CT | 13:00 CT | 14:00 CT | Latest (≈15:00 CT close) |
|--------|------:|------:|------:|------:|------:|------:|------:|
| AMAT | +7.30% | +6.52% | +5.90% | +4.61% | +4.02% | +4.04% | +4.08% |
| ARM | +5.32% | +6.74% | +6.08% | +1.92% | +1.46% | +3.20% | +4.91% |
| CRWD | -2.19% | -0.51% | -1.38% | -1.15% | +0.00% | -0.61% | +0.28% |
| DELL | +1.88% | +3.17% | +1.02% | +1.67% | +1.97% | -0.44% | -2.34% |
| KLAC | +7.18% | +6.63% | +8.52% | +8.61% | +8.82% | +9.61% | +8.73% |
| MRVL | +6.97% | +11.25% | +11.87% | +12.06% | +12.29% | +11.75% | +7.27% |
| OKTA | -4.31% | -1.80% | -0.87% | +1.89% | +4.64% | +4.07% | +4.23% |
| ON | +5.57% | +6.40% | +6.37% | +6.71% | +6.76% | +6.24% | +7.70% |
| PANW | -0.29% | +0.24% | +0.57% | +1.03% | +1.55% | +1.30% | +2.00% |
| SNOW | -3.84% | -2.24% | -2.10% | -1.66% | -0.53% | -1.30% | -0.95% |
| **AVG** | +2.36% | +3.64% | +3.60% | +3.57% | +4.10% | +3.79% | +3.59% |

## B) CURRENT composite ranking (scored on latest prices 2026-06-18) — sets up the next session

_Recomputed on the current/provisional prices. 19/83 names clear the buy gate now. `Δrank vs prior` = move vs the prior-close ranking (▲ = ranked higher now)._

### Top 10 (highest buy scores @ current prices)

| # | Ticker | Score | Gate | 2026-06-18 px | Δrank vs prior | Held |
|---|--------|------:|:----:|------:|:-------------:|:----:|
| 1 | ARM | 0.977 | ✓ | 439.46 | ▲2 | HELD |
| 2 | MRVL | 0.944 | ✓ | 310.58 | ▲3 | HELD |
| 3 | AMAT | 0.881 | ✓ | 617.11 | ▼1 | HELD |
| 4 | KLAC | 0.871 | ✓ | 259.56 | ▲3 | HELD |
| 5 | RBLX | 0.857 | ✓ | 51.53 | ▲6 |  |
| 6 | INTC | 0.838 | ✓ | 133.99 | ▲6 |  |
| 7 | LRCX | 0.834 | ✓ | 389.04 | ▼3 |  |
| 8 | TSM | 0.833 | ✓ | 462.12 | ▲12 |  |
| 9 | QCOM | 0.828 | ✓ | 226.11 | ▲5 |  |
| 10 | MU | 0.805 | ✓ | 1133.99 | ▼4 |  |

### Bottom 10 (lowest buy scores @ current prices)

| # | Ticker | Score | Gate | 2026-06-18 px | Δrank vs prior | Held |
|---|--------|------:|:----:|------:|:-------------:|:----:|
| 74 | CRM | 0.249 | — | 151.78 | • |  |
| 75 | TEAM | 0.233 | — | 82.72 | ▼7 |  |
| 76 | SMCI | 0.214 | — | 30.66 | ▼7 |  |
| 77 | ADBE | 0.198 | — | 195.16 | ▼2 |  |
| 78 | INTU | 0.172 | — | 267.00 | ▲5 |  |
| 79 | HUBS | 0.163 | — | 176.03 | ▲3 |  |
| 80 | OXY | 0.162 | — | 51.82 | • |  |
| 81 | NOW | 0.152 | — | 95.04 | ▼14 |  |
| 82 | SNAP | 0.117 | — | 4.66 | ▼9 |  |
| 83 | SAP | 0.111 | — | 155.22 | ▼7 |  |

## Group returns (ranking-close → latest)

| Group | Avg return |
|-------|-----------:|
| Top 10 | +5.14% |
| Universe (all 83) | +1.69% |
| Held book (equal-wt) | +3.59% |
| Bottom 10 | -1.11% |

## Held book — 10 positions  (portfolio $18,222,850, cash $530,261)

| Ticker | Shares | Entry | Now | Unreal % | Return |
|--------|-------:|------:|----:|---------:|-------:|
| AMAT | 2488 | 617.73 | 617.11 | -0.10% | +4.08% |
| ARM | 4800 | 216.10 | 439.46 | +103.36% | +4.91% |
| CRWD | 1969 | 648.88 | 684.86 | +5.55% | +0.28% |
| DELL | 6254 | 164.25 | 409.50 | +149.32% | -2.34% |
| KLAC | 5937 | 237.57 | 259.56 | +9.26% | +8.73% |
| MRVL | 8496 | 128.62 | 310.58 | +141.47% | +7.27% |
| OKTA | 11753 | 124.77 | 117.81 | -5.58% | +4.23% |
| ON | 14467 | 72.12 | 121.62 | +68.63% | +7.70% |
| PANW | 5339 | 243.07 | 287.78 | +18.39% | +2.00% |
| SNOW | 5502 | 261.40 | 232.29 | -11.14% | -0.95% |

## Portfolio vs benchmarks

| Window | model_v4 | SPY | QQQ | vs SPY | vs QQQ |
|--------|------:|----:|----:|-------:|-------:|
| 1D | +3.07% | +1.04% | +2.51% | +2.03% | +0.56% |
| 5D | +6.40% | +1.48% | +3.28% | +4.92% | +3.13% |
| MTD | +0.48% | -1.30% | -0.29% | +1.78% | +0.77% |
| Since 2000-01-01 | +18122.85% | +719.40% | +826.62% | +17403.45% | +17296.23% |

_Ranking is reproducible from price history (composite of 1d/5d/20d returns + volume ratio); the latest mark may be a provisional intraday bar that settles at the close._
