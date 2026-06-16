# Agent backtest — model_v4
**Window:** 2026-01-05 → 2026-01-30  |  **Decider:** claude-haiku-4-5-20251001  |  **Packet:** `eod_series_model_v4_2026-01-01_2026-01-31.pdf`

_The agent reads one daily page at a time (no look-ahead) and emits structured trades; the harness owns all fills (next-open, with slippage) and accounting._
_Start: seeded with the first page held book (level with the model)._

## Scorecard

| Setting | Final | Return | Max DD | Trades | Divergences | vs Model |
|---------|------:|------:|------:|------:|-----------:|--------:|
| strict | $106,135 | +6.13% | -4.84% | 9 | 0 | +0.00% |
| balanced | $106,040 | +6.04% | -4.90% | 11 | 2 | -0.09% |
| discretionary | $104,559 | +4.56% | -3.35% | 10 | 7 | -1.58% |

**Benchmarks (same window):** model_v4 +6.15% · SPY +0.62% · QQQ +0.63%.
_`vs Model` = setting return minus the strict (follow-the-model) return — the net effect of the agent's divergences. Positive = its deviations helped._

## strict — divergences (0)
_None — followed the model exactly._

## balanced — divergences (2)
- **2026-01-12** — added: BUY SEDG
- **2026-01-13** — added: BUY BA

## discretionary — divergences (7)
- **2026-01-07** — skipped: BUY INTC, BUY SNPS
- **2026-01-08** — skipped: BUY ADI, BUY KLAC
- **2026-01-12** — added: BUY SEDG
- **2026-01-13** — added: BUY BA
- **2026-01-22** — added: BUY PLUG
- **2026-01-23** — added: BUY AMD
- **2026-01-28** — added: BUY TXN

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

### balanced (11 trades)

| Date | Action | Ticker | Shares | Price | Reason |
|------|--------|--------|------:|------:|--------|
| 2026-01-06 | BUY | ASML | 6 | 1237.85 | Model momentum_score 0.9536 clears entry bar >0.90; triggered on 3rd consecutive day; sized ~8.5% of book per mandate. |
| 2026-01-06 | BUY | LRCX | 43 | 206.71 | Model momentum_score 0.9361 clears entry bar >0.90; triggered on 3rd consecutive day; sized ~8.5% of book per mandate. |
| 2026-01-07 | BUY | MCHP | 115 | 73.14 | Momentum score 0.9566 clears >0.90 entry bar; 3rd consecutive day above threshold; sized ~8.5% of book. |
| 2026-01-07 | BUY | ON | 138 | 61.89 | Momentum score 0.9229 clears >0.90 entry bar; 3rd consecutive day above threshold; sized ~8.5% of book. |
| 2026-01-08 | BUY | INTC | 200 | 41.11 | Model queued buy with strong momentum_score=0.8825; cash available ($50,235) exceeds cost (~$8,534); balanced setting defers to model recommendation |
| 2026-01-08 | BUY | SNPS | 16 | 514.49 | Model queued buy with strong momentum_score=0.8554; cash sufficient after INTC fill; balanced setting defers to model recommendation |
| 2026-01-09 | BUY | ADI | 28 | 299.17 | Model queued buy with momentum score 0.8506; balanced setting defers to queue by default. |
| 2026-01-09 | BUY | KLAC | 64 | 139.64 | Model queued buy with momentum score 0.7994; balanced setting defers to queue by default. |
| 2026-01-12 | BUY | AMAT | 29 | 306.48 | Model momentum_score=0.9036 clears >0.90 entry threshold; constructive stance & normal sizing justified by full budget governor & non-negative spread |
| 2026-01-13 | BUY | SEDG | 9 | 34.31 | Score >0.90 for 3 consecutive days; 8.5% sizing at full governor; within cash constraints |
| 2026-01-14 | BUY | BA | 7 | 242.61 | BA scored >0.90 for 3rd consecutive day; model recommends entry at ~8.5% of book sizing; ~$7,175 outlay fits within cash |

### discretionary (10 trades)

| Date | Action | Ticker | Shares | Price | Reason |
|------|--------|--------|------:|------:|--------|
| 2026-01-06 | BUY | ASML | 6 | 1237.85 | Momentum score 0.9536 triggers entry; 3rd consecutive day above 0.90 bar confirmed in model queue; positioned in risk-on session with positive spread backdrop |
| 2026-01-06 | BUY | LRCX | 43 | 206.71 | Momentum score 0.9361 triggers entry; 3rd consecutive day above 0.90 bar confirmed in model queue; semiconductor strength aligns with session momentum |
| 2026-01-07 | BUY | MCHP | 115 | 73.14 | Momentum score 0.956 clears 0.90 gate on 3rd consecutive day; high conviction signal with normalized vol environment and strong session spread (+3.17%) |
| 2026-01-07 | BUY | ON | 138 | 61.89 | Momentum score 0.923 clears 0.90 gate on 3rd consecutive day; sized within 2-new-per-day and per-name cap with full governor multiplier |
| 2026-01-12 | BUY | AMAT | 29 | 306.48 | Momentum score 0.9036 clears >0.90 entry threshold; 3rd consecutive day signal triggered; sized ~8.5% of book per model framework; risk-on environment supports semiconductor exposure. |
| 2026-01-13 | BUY | SEDG | 35 | 34.31 | SEDG score 0.95 clears 3-day entry gate; buy candidate recommended by model; sized ~8.5% of portfolio (~$8,600 target). |
| 2026-01-14 | BUY | BA | 28 | 242.61 | BA scored 0.93 (above 0.90 entry gate) for 3rd consecutive day; discretionary approval aligned with model's constructive stance and full-budget governor positioning; allocation ~8.5% of book (~$8,600 target, 28 sh @ $307) |
| 2026-01-23 | BUY | PLUG | 89 | 2.50 | Entry score 0.93 clears >0.90 gate on 3rd consecutive day; sized ~8.5% of book; constructive stance and full governor budget support new entry |
| 2026-01-26 | BUY | AMD | 28 | 251.31 | AMD score 0.93 (>0.90 threshold) triggered on 3rd consecutive day; sized ~8.5% of book value at 1.00× governor; constructive stance with governor near full budget. |
| 2026-01-29 | BUY | TXN | 22 | 216.45 | TXN cleared >0.90 entry score on 3rd consecutive day; discretionary alignment with model recommendation. Sized ~8.5% of portfolio within position cap; fits cash constraints and governs exposure properly. |

_Paper-trading research only — not investment advice._