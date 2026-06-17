# Agent backtest — model_v4
**Window:** 2026-01-05 → 2026-01-30  |  **Decider:** claude-sonnet-4-6  |  **Packet:** `eod_series_model_v4_2026-01-01_2026-01-31.pdf`

_The agent reads one daily page at a time (no look-ahead) and emits structured trades; the harness owns all fills (next-open, with slippage) and accounting._
_Start: seeded with the first page held book (level with the model).  Extra context sources: news._

## Scorecard

| Setting | Final | Return | Max DD | Trades | Divergences | vs Model |
|---------|------:|------:|------:|------:|-----------:|--------:|
| strict | $106,135 | +6.13% | -4.84% | 9 | 0 | +0.00% |
| balanced | $105,869 | +5.87% | -4.27% | 7 | 1 | -0.27% |
| discretionary | $105,211 | +5.21% | -2.76% | 10 | 6 | -0.92% |

**Benchmarks (same window):** model_v4 +6.15% · SPY +0.62% · QQQ +0.63%.
_`vs Model` = setting return minus the strict (follow-the-model) return — the net effect of the agent's divergences. Positive = its deviations helped._

## strict — divergences (0)
_None — followed the model exactly._

## balanced — divergences (1)
- **2026-01-07** — skipped: BUY INTC, BUY SNPS

## discretionary — divergences (6)
- **2026-01-07** — skipped: BUY INTC, BUY SNPS
- **2026-01-08** — skipped: BUY ADI, BUY KLAC
- **2026-01-21** — added: BUY AMD
- **2026-01-23** — added: BUY AMD
- **2026-01-28** — added: BUY TXN, SELL AMD
- **2026-01-29** — added: BUY META

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

### balanced (7 trades)

| Date | Action | Ticker | Shares | Price | Reason |
|------|--------|--------|------:|------:|--------|
| 2026-01-06 | BUY | ASML | 6 | 1237.85 | Top-ranked name (0.954) clearing the >0.90 entry gate on 3rd consecutive day; momentum is working in today's session and governor is at full 1.00× budget — following model queue. |
| 2026-01-06 | BUY | LRCX | 43 | 206.71 | Second-ranked name (0.936) also clearing the >0.90 entry gate; semiconductor equipment momentum aligns with ASML strength; sized per model at ~8.5% of book — following model queue. |
| 2026-01-07 | BUY | MCHP | 115 | 73.14 | Model-queued buy with top momentum score (0.9566, rank #3), cleared 3-day entry gate, sized at ~8.5% of book within cash budget; following model recommendation. |
| 2026-01-07 | BUY | ON | 138 | 61.89 | Model-queued buy with strong momentum score (0.9229, rank #4), cleared 3-day entry gate, sized at ~8.5% of book within remaining cash budget; following model recommendation. |
| 2026-01-09 | BUY | ADI | 28 | 299.17 | Model queued buy; ADI ranks #3 with a strong momentum score of 0.851, clearing the entry gate — following the model's recommendation in balanced mode. |
| 2026-01-09 | BUY | KLAC | 64 | 139.64 | Model queued buy; KLAC ranks #7 with momentum score 0.799, clearing the entry gate — following the model's recommendation in balanced mode. |
| 2026-01-12 | BUY | AMAT | 29 | 306.48 | Model-queued buy with momentum score 0.9036 clearing the entry gate (>0.90, 3rd consecutive day above bar); governor at full 1.00× budget and session spread is constructive — following model recommendation. |

### discretionary (10 trades)

| Date | Action | Ticker | Shares | Price | Reason |
|------|--------|--------|------:|------:|--------|
| 2026-01-06 | BUY | ASML | 6 | 1237.85 | Top-ranked name (0.954) with confirmed 3-day momentum trigger; semiconductor equipment leader with strong AI tailwinds; fits within cash budget (~$7,351 of $83,536 available). |
| 2026-01-06 | BUY | LRCX | 43 | 206.71 | Second-ranked name (0.936) with confirmed 3-day momentum trigger; LRCX benefits from same semiconductor capex cycle as ASML; ~$8,373 outlay well within remaining cash. |
| 2026-01-07 | BUY | MCHP | 115 | 73.14 | Top composite score (0.957) clearing the buy gate on 3rd consecutive day above threshold; semiconductor momentum strong, aligns with MU/LRCX session strength; ~8.5% book sizing fits within available cash ($67,204 > ~$8,525 at $74.13). |
| 2026-01-07 | BUY | ON | 138 | 61.89 | 4th-ranked composite score (0.923), clears entry gate for 3rd consecutive day; ON is a high-quality semiconductor name benefiting from the same chip momentum tailwind as current holdings; ~8.5% book sizing, cash sufficient after MCHP purchase (~$8,531 remaining capacity). |
| 2026-01-12 | BUY | AMAT | 29 | 306.48 | Top-ranked unowned name clearing the 0.90 buy gate (score 0.904), momentum is working in the semiconductor equipment space alongside LRCX/KLAC already held profitably; fits available cash and ~8.5% book sizing. |
| 2026-01-22 | BUY | AMD | 40 | 253.73 | AMD ranks #3 composite (0.935), clears the buy gate, and the risk-on session with momentum working strongly supports adding a high-ranked semiconductor name; sizing ~$8.5K fits within available cash ($41K). |
| 2026-01-26 | BUY | AMD | 10 | 251.31 | AMD ranks #1 in composite scoring (0.926), already held with solid unrealized gains, Cathie Wood bullish catalyst, and AI narrative strong — adding incrementally given ~$31K cash and discretionary conviction. |
| 2026-01-29 | BUY | TXN | 55 | 216.45 | Top-ranked unowned name (0.944 composite), cleared buy gate for 3+ consecutive days per model; ~$8.5% book sizing aligns with current price ~$170 range; semiconductor cycle momentum and strong fundamentals support entry. |
| 2026-01-29 | SELL | AMD | 50 | 252.18 | AMD scores only 0.530 (rank #36), well below buy gate; not held by the model; position is a legacy discretionary hold with no current composite support — rotating out to fund higher-ranked names and reduce book drift from model. |
| 2026-01-30 | BUY | META | 28 | 715.22 | META clears the >0.90 entry score (#1 ranked at 0.911), strong momentum alignment, and ~$29K cash allows a ~8.5% book-sized position (~28 sh at ~$620); discretionary conviction high given constructive spread and full governor budget. |

_Paper-trading research only — not investment advice._