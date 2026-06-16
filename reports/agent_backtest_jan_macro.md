# Agent backtest — model_v4
**Window:** 2026-01-05 → 2026-01-30  |  **Decider:** claude-haiku-4-5-20251001  |  **Packet:** `eod_series_model_v4_2026-01-01_2026-01-31.pdf`

_The agent reads one daily page at a time (no look-ahead) and emits structured trades; the harness owns all fills (next-open, with slippage) and accounting._
_Start: seeded with the first page held book (level with the model).  Extra context sources: macro._

## Scorecard

| Setting | Final | Return | Max DD | Trades | Divergences | vs Model |
|---------|------:|------:|------:|------:|-----------:|--------:|
| strict | $106,135 | +6.13% | -4.84% | 9 | 0 | +0.00% |
| balanced | $105,609 | +5.61% | -5.11% | 12 | 6 | -0.53% |
| discretionary | $104,501 | +4.50% | -3.48% | 11 | 7 | -1.63% |

**Benchmarks (same window):** model_v4 +6.15% · SPY +0.62% · QQQ +0.63%.
_`vs Model` = setting return minus the strict (follow-the-model) return — the net effect of the agent's divergences. Positive = its deviations helped._

## strict — divergences (0)
_None — followed the model exactly._

## balanced — divergences (6)
- **2026-01-12** — added: BUY SEDG
- **2026-01-20** — added: BUY BA
- **2026-01-22** — added: BUY PLUG
- **2026-01-23** — added: BUY AMD
- **2026-01-26** — added: BUY ANET
- **2026-01-28** — added: BUY TXN

## discretionary — divergences (7)
- **2026-01-07** — skipped: BUY INTC, BUY SNPS
- **2026-01-08** — skipped: BUY ADI, BUY KLAC
- **2026-01-12** — added: BUY SEDG
- **2026-01-13** — added: BUY BA
- **2026-01-23** — added: BUY AMD
- **2026-01-26** — added: BUY ANET
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

### balanced (12 trades)

| Date | Action | Ticker | Shares | Price | Reason |
|------|--------|--------|------:|------:|--------|
| 2026-01-06 | BUY | ASML | 6 | 1237.85 | Momentum score 0.9536 clears >0.90 entry gate on 3rd consecutive qualifying day; sized ~8.5% of book per model guidance |
| 2026-01-06 | BUY | LRCX | 43 | 206.71 | Momentum score 0.9361 clears >0.90 entry gate on 3rd consecutive qualifying day; sized ~8.5% of book per model guidance |
| 2026-01-07 | BUY | MCHP | 115 | 73.14 | Momentum score 0.957 clears >0.90 entry gate on 3rd consecutive day; sized ~8.5% of book per model recommendation. |
| 2026-01-07 | BUY | ON | 138 | 61.89 | Momentum score 0.923 clears >0.90 entry gate on 3rd consecutive day; sized ~8.5% of book per model recommendation. |
| 2026-01-08 | BUY | INTC | 200 | 41.11 | Model queued; momentum_score 0.8825 clears buy gate; ranked #3 in composite; constructive net stance supports full-budget entry. |
| 2026-01-08 | BUY | SNPS | 16 | 514.49 | Model queued; momentum_score 0.8554 clears buy gate; ranked #5 in composite; sufficient cash available ($50k covers ~$8.3k entry). |
| 2026-01-09 | BUY | ADI | 28 | 299.17 | Momentum score 0.8506 clears entry bar; ranks #3 in composite; balanced-mode adherence to queued buy. |
| 2026-01-09 | BUY | KLAC | 64 | 139.64 | Momentum score 0.7994 clears entry bar; ranks #7 in composite; balanced-mode adherence to queued buy. |
| 2026-01-12 | BUY | AMAT | 29 | 306.48 | Momentum score 0.904 clears >0.90 entry bar on 3rd consecutive day; aligned with queued recommendation; capital available ($16,433 vs. $8,721 cost); supports full-budget constructive stance. |
| 2026-01-13 | BUY | SEDG | 22 | 34.31 | Score 0.948 clears buy gate on day 3+; sized ~8.5% allocation (~$7,370 target); constructive net stance and governor at full budget warrant entry. |
| 2026-01-21 | BUY | BA | 27 | 250.07 | BA cleared the 0.90 entry gate on the 3rd consecutive day; composite score 0.903; sized at ~8.5% of book per model governor (27 sh @ ~$251 = ~$6,777, within available cash). |
| 2026-01-23 | BUY | PLUG | 8 | 2.50 | Score 0.934 clears entry gate and meets 3-day threshold; governer permits sized entry; aligns with model queue (constructive stance, full budget available) |

### discretionary (11 trades)

| Date | Action | Ticker | Shares | Price | Reason |
|------|--------|--------|------:|------:|--------|
| 2026-01-06 | BUY | ASML | 6 | 1237.85 | Momentum score 0.954 clears 0.90 gate on 3rd consecutive day; model queued entry with strong institutional tailwind in semiconductors. |
| 2026-01-06 | BUY | LRCX | 43 | 206.71 | Momentum score 0.936 clears 0.90 gate on 3rd consecutive day; model queued entry aligns with ranked #2 position and positive equipment cycle. |
| 2026-01-07 | BUY | MCHP | 115 | 73.14 | Momentum score 0.957 clears >0.90 entry gate; 3rd consecutive day above threshold; within 8.5% position cap and available cash. |
| 2026-01-07 | BUY | ON | 138 | 61.89 | Momentum score 0.923 clears >0.90 entry gate; 3rd consecutive day above threshold; within 8.5% position cap and available cash. |
| 2026-01-12 | BUY | AMAT | 29 | 306.48 | Score 0.904 clears >0.90 gate and momentum is working; portfolio has cash ($50.2k) to support ~8.5% sized entry (~$8.7k); risk-on session backdrop and positive spread support new positioning in semiconductor momentum. |
| 2026-01-13 | BUY | SEDG | 28 | 34.31 | SEDG scores 0.948 (clears 0.90 gate on 3rd consecutive day); strong buy signal. Sizing ~8.5% of book (~$8,600); current cash $41,338 permits this purchase. |
| 2026-01-14 | BUY | BA | 29 | 242.61 | BA scores 0.926 (above 0.90 entry gate) on its 3rd consecutive day; cleared for entry at ~8.5% sizing (~$8.6k); strong industrial momentum (+5.0% sector 20d) supports disciplined buy. |
| 2026-01-26 | BUY | AMD | 27 | 251.31 | AMD clears >0.90 entry gate (0.926) on 3rd consecutive day; discretionary buy justified by strong score, tech sector weakness creates tactical entry opportunity, and portfolio has sufficient dry powder (33.3k cash, book at 93% invested within full volatility budget). |
| 2026-01-27 | BUY | ANET | 29 | 146.69 | Scored 0.902—clears buy gate on 3rd consecutive day above 0.90; sector-agnostic quality play in soft market; sized ~8.5% of book (~$9,000 dry powder available) |
| 2026-01-30 | BUY | META | 25 | 715.22 | META clears entry gate (0.911 composite) and has held score >0.90 for 3+ consecutive days; top-ranked non-held name with constructive risk backdrop; sized at ~8.5% of current book. |
| 2026-01-30 | BUY | TXN | 20 | 214.46 | TXN clears entry gate (0.905 composite) and qualifies as 3-day persistence buy; second-strongest non-held entry candidate; sized within daily cap (max 2 new/day). |

_Paper-trading research only — not investment advice._