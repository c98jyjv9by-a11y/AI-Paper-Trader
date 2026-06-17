# Agent backtest — model_v4
**Window:** 2026-01-05 → 2026-01-30  |  **Decider:** claude-sonnet-4-6  |  **Packet:** `eod_series_model_v4_2026-01-01_2026-01-31.pdf`

_The agent reads one daily page at a time (no look-ahead) and emits structured trades; the harness owns all fills (next-open, with slippage) and accounting._
_Start: seeded with the first page held book (level with the model).  Extra context sources: macro._

## Scorecard

| Setting | Final | Return | Max DD | Trades | Divergences | vs Model |
|---------|------:|------:|------:|------:|-----------:|--------:|
| strict | $106,135 | +6.13% | -4.84% | 9 | 0 | +0.00% |
| balanced | $106,135 | +6.13% | -4.84% | 9 | 0 | +0.00% |
| discretionary | $105,462 | +5.46% | -2.60% | 11 | 7 | -0.67% |

**Benchmarks (same window):** model_v4 +6.15% · SPY +0.62% · QQQ +0.63%.
_`vs Model` = setting return minus the strict (follow-the-model) return — the net effect of the agent's divergences. Positive = its deviations helped._

## strict — divergences (0)
_None — followed the model exactly._

## balanced — divergences (0)
_None — followed the model exactly._

## discretionary — divergences (7)
- **2026-01-06** — resized: BUY MCHP, BUY ON
- **2026-01-07** — skipped: BUY INTC, BUY SNPS
- **2026-01-08** — skipped: BUY ADI, BUY KLAC
- **2026-01-09** — added: BUY MCHP
- **2026-01-21** — added: BUY AMD
- **2026-01-28** — added: BUY TXN, SELL AMD
- **2026-01-29** — added: BUY META, BUY TXN

## Trade logs

### strict (9 trades)

| Date | Action | Ticker | Shares | Price | Reason |
|------|--------|--------|------:|------:|--------|
| 2026-01-06 | BUY | ASML | 6 | 1237.85 | strict: model momentum_score=0.9536 |
| 2026-01-06 | BUY | LRCX | 43 | 206.71 | strict: model momentum_score=0.9361 |
| 2026-01-07 | BUY | MCHP | 115 | 73.14 | strict: model momentum_score=0.9566 |
| 2026-01-07 | BUY | ON | 138 | 61.89 | strict: model momentum_score=0.9229 |
| 2026-01-08 | BUY | INTC | 200 | 41.11 | strict: model momentum_score=0.8825 |
| 2026-01-08 | BUY | SNPS | 16 | 514.49 | strict: model momentum_score=0.8554 |
| 2026-01-09 | BUY | ADI | 28 | 299.17 | strict: model momentum_score=0.8506 |
| 2026-01-09 | BUY | KLAC | 64 | 139.64 | strict: model momentum_score=0.7994 |
| 2026-01-12 | BUY | AMAT | 29 | 306.48 | strict: model momentum_score=0.9036 |

### balanced (9 trades)

| Date | Action | Ticker | Shares | Price | Reason |
|------|--------|--------|------:|------:|--------|
| 2026-01-06 | BUY | ASML | 6 | 1237.85 | Model queued buy with top momentum score (0.9536), clears entry gate on 3rd consecutive day above bar; ~8.5% book sizing aligns with full 1.00x governor budget. |
| 2026-01-06 | BUY | LRCX | 43 | 206.71 | Model queued buy with strong momentum score (0.9361), clears entry gate on 3rd consecutive day above bar; risk-on session confirms momentum regime; sized within cash available. |
| 2026-01-07 | BUY | MCHP | 115 | 73.14 | Top-ranked unowned name (0.957, rank #3) clearing the >0.90 entry gate on 3rd consecutive day; model queued, sizing fits ~8.5% book budget, governor at full 1.00×. |
| 2026-01-07 | BUY | ON | 138 | 61.89 | Second-ranked unowned buy candidate (0.923, rank #4) clearing the entry bar; model queued, within per-name cap and max 2 new names/day rule, governor at full 1.00×. |
| 2026-01-08 | BUY | INTC | 200 | 41.11 | Model queue + #3 composite ranking (0.882, above buy gate); momentum inversion is a one-day anomaly and INTC's score has been climbing fast (▲32 rank); cash is ample. |
| 2026-01-08 | BUY | SNPS | 16 | 514.49 | Model queue + #5 composite ranking (0.855, above buy gate); solid momentum score clears the entry bar and position size fits within remaining cash budget. |
| 2026-01-09 | BUY | ADI | 28 | 299.17 | Model queued buy; ADI ranks #3 with momentum score 0.851, clears the buy gate, and cash is sufficient (~$8,336 at quoted price). |
| 2026-01-09 | BUY | KLAC | 64 | 139.64 | Model queued buy; KLAC ranks #7 with momentum score 0.799, clears the buy gate; cost ~$8,464 is within remaining cash after ADI purchase. |
| 2026-01-12 | BUY | AMAT | 29 | 306.48 | Model queued BUY aligns with composite rank #5 (score 0.904, above 0.90 gate, 3rd consecutive day above bar); governor at full 1.00× budget, risk-on session, sufficient cash ($16,433 > ~$8,721 estimated cost). |

### discretionary (11 trades)

| Date | Action | Ticker | Shares | Price | Reason |
|------|--------|--------|------:|------:|--------|
| 2026-01-06 | BUY | ASML | 6 | 1237.85 | Top-ranked name (0.954) with confirmed 3-day trigger, strong momentum, full governor budget, and fits within available cash at ~$7,351. |
| 2026-01-06 | BUY | LRCX | 43 | 206.71 | Second-ranked name (0.936) with confirmed 3-day trigger, semiconductor equipment sector momentum aligns with TSM/MU holdings, fits within remaining cash at ~$8,373. |
| 2026-01-07 | BUY | MCHP | 90 | 73.14 | Top composite score (0.957) with 3rd-consecutive-day confirmation; semiconductor momentum strong — sizing ~$6,700 (~6.6% of book) to stay within cash limits while respecting the position-cap spirit. |
| 2026-01-07 | BUY | ON | 100 | 61.89 | Score 0.923 clears buy gate with 3rd-day confirmation; semiconductor/power-chip theme aligns with MCHP — sizing ~$6,200 (~6.1% of book), risk-on environment and neutral vol governor support entry. |
| 2026-01-12 | BUY | AMAT | 29 | 306.48 | AMAT ranks #5 with a strong 0.904 composite score, clears the buy gate on its 3rd consecutive day above the bar, momentum is working (session spread +2.14%), VIX is low at 14.5, and the volatility governor is at full 1.00x — standard entry size is justified. |
| 2026-01-12 | BUY | MCHP | 25 | 72.60 | Already held at a profit; adding to bring MCHP position closer to ~8.5% book size — score is 0.883 (just below gate but strong), semiconductor sector showing broad strength today, and I am underweight relative to the model's 115-sh position. |
| 2026-01-22 | BUY | AMD | 10 | 253.73 | AMD ranks #3 with composite score 0.935, clearing the buy gate; semiconductor momentum is strong across the book today; ~$8.5k sizing fits within available cash ($43,706) and aligns with per-name cap. |
| 2026-01-29 | BUY | TXN | 7 | 216.45 | Top-ranked unowned name (0.944 composite) clearing the buy gate for 3+ consecutive days; semiconductor sector momentum is strong (INTC +11%, MCHP +6.8% session); ~$7k position fits within cash budget without over-extending. |
| 2026-01-29 | SELL | AMD | 10 | 252.18 | AMD ranks 37th (0.530 composite) with no buy gate clearance, well below the 0.90 threshold; position is a legacy hold dragging on portfolio quality — rotating proceeds to support stronger-ranked names or cash buffer given 93% model investment level warning. |
| 2026-01-30 | BUY | META | 22 | 715.22 | Top composite score (0.911) clearing the buy gate; strong momentum in a risk-off session where higher-scored names outperformed; sizing ~8.5% of book (~$22 × ~$640 ≈ $14,080 — adjusting to fit within available cash of $42,169 while leaving buffer; using ~25 shares worth). Actually fitting ~22 shares at estimated ~$630 = ~$13,860, keeping cash buffer. |
| 2026-01-30 | BUY | TXN | 43 | 214.46 | Second-ranked composite score (0.905) clearing the buy gate; semiconductor/analog leader with strong ranking; ~43 sh × ~$210 ≈ $9,030 brings allocation to ~8.5% of book; already hold 7 sh at $216.67 avg, adding to a winner with solid score momentum. |

_Paper-trading research only — not investment advice._