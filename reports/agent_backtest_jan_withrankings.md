# Agent backtest — model_v4
**Window:** 2026-01-05 → 2026-01-30  |  **Decider:** claude-haiku-4-5-20251001  |  **Packet:** `eod_series_model_v4_2026-01-01_2026-01-31.pdf`

_The agent reads one daily page at a time (no look-ahead) and emits structured trades; the harness owns all fills (next-open, with slippage) and accounting._
_Start: seeded with the first page held book (level with the model)._

## Scorecard

| Setting | Final | Return | Max DD | Trades | Divergences | vs Model |
|---------|------:|------:|------:|------:|-----------:|--------:|
| strict | $106,135 | +6.13% | -4.84% | 9 | 0 | +0.00% |
| balanced | $105,652 | +5.65% | -5.30% | 12 | 3 | -0.48% |
| discretionary | $104,354 | +4.35% | -2.60% | 12 | 9 | -1.78% |

**Benchmarks (same window):** model_v4 +6.15% · SPY +0.62% · QQQ +0.63%.
_`vs Model` = setting return minus the strict (follow-the-model) return — the net effect of the agent's divergences. Positive = its deviations helped._

## strict — divergences (0)
_None — followed the model exactly._

## balanced — divergences (3)
- **2026-01-12** — added: BUY SEDG
- **2026-01-22** — added: BUY PLUG
- **2026-01-23** — added: BUY AMD

## discretionary — divergences (9)
- **2026-01-07** — skipped: BUY INTC, BUY SNPS
- **2026-01-08** — skipped: BUY ADI, BUY KLAC
- **2026-01-09** — skipped: BUY AMAT
- **2026-01-12** — added: BUY SEDG
- **2026-01-13** — added: BUY BA
- **2026-01-22** — added: BUY PLUG
- **2026-01-23** — added: BUY AMD
- **2026-01-26** — added: BUY ANET, SELL INTC, SELL ON, SELL PLUG
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

### balanced (12 trades)

| Date | Action | Ticker | Shares | Price | Reason |
|------|--------|--------|------:|------:|--------|
| 2026-01-06 | BUY | ASML | 6 | 1237.85 | Momentum score 0.9536 clears entry gate on 3rd consecutive day; aligns with model queue and constructive stance. |
| 2026-01-06 | BUY | LRCX | 43 | 206.71 | Momentum score 0.9361 clears entry gate on 3rd consecutive day; aligns with model queue and constructive stance. |
| 2026-01-07 | BUY | MCHP | 115 | 73.14 | Momentum score 0.9566 (3rd+ consecutive day above 0.90 gate); queued by model and fits balanced approach; ~8.5% allocation fits within budget. |
| 2026-01-07 | BUY | ON | 138 | 61.89 | Momentum score 0.9229 (3rd+ consecutive day above 0.90 gate); queued by model; second triggered buy within daily cap; ~8.5% allocation within budget. |
| 2026-01-08 | BUY | INTC | 200 | 41.11 | Momentum score 0.88 clears buy gate; model queued; constructive net stance with full budget allocation supports entry. |
| 2026-01-08 | BUY | SNPS | 16 | 514.49 | Momentum score 0.86 clears buy gate; model queued; balanced setting defers to model's ranked buys. |
| 2026-01-09 | BUY | ADI | 28 | 299.17 | Ranks #3 at 0.851 score, clears buy gate; momentum_score 0.8506 supports entry; model queued |
| 2026-01-09 | BUY | KLAC | 64 | 139.64 | Ranks #7 at 0.799 score, clears buy gate; momentum_score 0.7994 supports entry; model queued |
| 2026-01-12 | BUY | AMAT | 29 | 306.48 | Momentum score 0.904 clears the >0.90 entry gate on the 3rd consecutive day; model queued, sufficient cash ($16,433 > $8,721), and constructive stance warrants execution. |
| 2026-01-13 | BUY | SEDG | 26 | 34.31 | SEDG (0.948) clears buy gate on 3rd consecutive day; aligns with model queue rec and balanced setting; sized ~8.5% of book per governor |
| 2026-01-23 | BUY | PLUG | 22 | 2.50 | Model queued PLUG (score 0.934, cleared >0.90 gate for 3rd consecutive day); sized at ~8.5% of book per exposure cap; balanced setting defers to model's buy signal |
| 2026-01-26 | BUY | AMD | 26 | 251.31 | AMD clears entry gate at 0.93 composite score on 3rd consecutive day; constructive stance + normal sizing at ~8.5% of book; governor permits full exposure. |

### discretionary (12 trades)

| Date | Action | Ticker | Shares | Price | Reason |
|------|--------|--------|------:|------:|--------|
| 2026-01-06 | BUY | ASML | 6 | 1237.85 | Momentum score 0.954 clears entry gate; 3rd consecutive day above 0.90 threshold; sized at ~8.5% of book per model guidance; risk-on session validates construct. |
| 2026-01-06 | BUY | LRCX | 43 | 206.71 | Momentum score 0.936 clears entry gate; 3rd consecutive day above 0.90 threshold; cash available supports position; aligns with model queue and discretionary judgment. |
| 2026-01-07 | BUY | MCHP | 115 | 73.14 | Momentum score 0.957 clears 0.90 gate; 3rd consecutive day above bar; ~8.5% of book allocation fits cash position ($8,525 @ $74.13); risk-on session validates entry. |
| 2026-01-07 | BUY | ON | 138 | 61.89 | Momentum score 0.923 clears 0.90 gate; 3rd consecutive day above bar; ~8.5% of book allocation fits cash position ($8,532 @ $61.82); spreads remain constructive. |
| 2026-01-13 | BUY | SEDG | 44 | 34.31 | Composite score 0.948 clears >0.90 entry gate on 3rd consecutive day; constructive net stance and governor at full budget justify buy signal (~8.5% of book sizing with $50k+ cash available). |
| 2026-01-14 | BUY | BA | 29 | 242.61 | BA cleared >0.90 entry gate (0.926) on the 3rd consecutive day; normalizes exposure given portfolio is only 52% invested vs 90% target; strong aerospace fundamentals and no negatives in commentary. |
| 2026-01-23 | BUY | PLUG | 26 | 2.50 | PLUG clears entry gate at 0.934 composite score on 3rd consecutive day above 0.90; sized ~8.5% of book; constructive stance with normal governor exposure. |
| 2026-01-26 | BUY | AMD | 27 | 251.31 | AMD clears >0.90 entry gate (0.926) on 3rd consecutive day; top-ranked non-held name; sized ~8.5% of book (~$8,800) at ~$326/sh; constructive stance with room in volatility budget. |
| 2026-01-27 | BUY | ANET | 28 | 146.69 | ANET clears buy gate at 0.902 (>0.90) for 3rd consecutive day; highest-ranked unheld name; sized ~8.5% of book aligns with constructive stance and full governor budget. |
| 2026-01-27 | SELL | ON | 138 | 62.63 | ON score 0.578 approaching stop threshold (0.90 gate); session -1.37% and unreal -1.33%; low composite ranking (#32); de-risk ahead of potential auto-stop and redeploy capital to higher-conviction names. |
| 2026-01-27 | SELL | PLUG | 26 | 2.41 | PLUG crashed -8.00% session (momentum-reversal selloff) and scores 0.546 (well below entry bar); universe commentary flags it as hardest hit; exit speculative position and redeploy. |
| 2026-01-29 | BUY | TXN | 27 | 216.45 | TXN clears buy gate at 0.944 composite score (3rd consecutive day above 0.90); sized at ~8.5% of book ($8,650 approx); strong entry signal in constructive market environment |

_Paper-trading research only — not investment advice._