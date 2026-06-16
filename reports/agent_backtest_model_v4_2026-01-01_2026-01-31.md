# Agent backtest — model_v4
**Window:** 2026-01-05 → 2026-01-30  |  **Decider:** deterministic rules (--no-llm)  |  **Packet:** `eod_series_model_v4_2026-01-01_2026-01-31.pdf`

_The agent reads one daily page at a time (no look-ahead) and emits structured trades; the harness owns all fills (next-open, with slippage) and accounting._
_Start: seeded with the first page held book (level with the model)._

## Scorecard

| Setting | Final | Return | Max DD | Trades | Divergences | vs Model |
|---------|------:|------:|------:|------:|-----------:|--------:|
| strict | $106,135 | +6.13% | -4.84% | 9 | 0 | +0.00% |
| balanced | $106,135 | +6.13% | -4.84% | 9 | 0 | +0.00% |
| discretionary | $105,374 | +5.37% | -3.97% | 5 | 4 | -0.76% |

**Benchmarks (same window):** model_v4 +6.15% · SPY +0.62% · QQQ +0.63%.
_`vs Model` = setting return minus the strict (follow-the-model) return — the net effect of the agent's divergences. Positive = its deviations helped._

## strict — divergences (0)
_None — followed the model exactly._

## balanced — divergences (0)
_None — followed the model exactly._

## discretionary — divergences (4)
- **2026-01-05** — skipped: BUY ASML
- **2026-01-06** — skipped: BUY MCHP
- **2026-01-07** — skipped: BUY SNPS
- **2026-01-08** — skipped: BUY ADI

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
| 2026-01-06 | BUY | ASML | 6 | 1237.85 | balanced-rule: follow within exposure budget |
| 2026-01-06 | BUY | LRCX | 43 | 206.71 | balanced-rule: follow within exposure budget |
| 2026-01-07 | BUY | MCHP | 115 | 73.14 | balanced-rule: follow within exposure budget |
| 2026-01-07 | BUY | ON | 138 | 61.89 | balanced-rule: follow within exposure budget |
| 2026-01-08 | BUY | INTC | 200 | 41.11 | balanced-rule: follow within exposure budget |
| 2026-01-08 | BUY | SNPS | 16 | 514.49 | balanced-rule: follow within exposure budget |
| 2026-01-09 | BUY | ADI | 28 | 299.17 | balanced-rule: follow within exposure budget |
| 2026-01-09 | BUY | KLAC | 64 | 139.64 | balanced-rule: follow within exposure budget |
| 2026-01-12 | BUY | AMAT | 29 | 306.48 | balanced-rule: follow within exposure budget |

### discretionary (5 trades)

| Date | Action | Ticker | Shares | Price | Reason |
|------|--------|--------|------:|------:|--------|
| 2026-01-06 | BUY | LRCX | 43 | 206.71 | discretionary-rule: concentrate in highest-conviction buy |
| 2026-01-07 | BUY | ON | 138 | 61.89 | discretionary-rule: concentrate in highest-conviction buy |
| 2026-01-08 | BUY | INTC | 200 | 41.11 | discretionary-rule: concentrate in highest-conviction buy |
| 2026-01-09 | BUY | KLAC | 64 | 139.64 | discretionary-rule: concentrate in highest-conviction buy |
| 2026-01-12 | BUY | AMAT | 29 | 306.48 | discretionary-rule: concentrate in highest-conviction buy |

_Paper-trading research only — not investment advice._