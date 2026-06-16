# Agent backtest — model_v4
**Window:** 2026-06-02 → 2026-06-16  |  **Decider:** deterministic rules (--no-llm)  |  **Packet:** `eod_series_model_v4_2026-06-01_2026-06-16.pdf`

_The agent reads one daily page at a time (no look-ahead) and emits structured trades; the harness owns all fills (next-open, with slippage) and accounting._

## Scorecard

| Setting | Final | Return | Max DD | Trades | Divergences | vs Model |
|---------|------:|------:|------:|------:|-----------:|--------:|
| strict | $97,092 | -2.91% | -6.58% | 15 | 0 | +0.00% |
| balanced | $97,092 | -2.91% | -6.58% | 15 | 0 | +0.00% |
| discretionary | $98,230 | -1.77% | -4.50% | 9 | 6 | +1.14% |

**Benchmarks (same window):** model_v4 -5.25% · SPY -1.22% · QQQ -2.18%.
_`vs Model` = setting return minus the strict (follow-the-model) return — the net effect of the agent's divergences. Positive = its deviations helped._

## strict — divergences (0)
_None — followed the model exactly._

## balanced — divergences (0)
_None — followed the model exactly._

## discretionary — divergences (6)
- **2026-06-02** — skipped: BUY OKTA
- **2026-06-03** — skipped: BUY CRWD
- **2026-06-04** — skipped: BUY AXON
- **2026-06-05** — skipped: BUY LLY
- **2026-06-08** — skipped: BUY AMAT
- **2026-06-10** — skipped: BUY SPOT

## Trade logs

### strict (15 trades)

| Date | Action | Ticker | Shares | Price | Reason |
|------|--------|--------|------:|------:|--------|
| 2026-06-03 | BUY | MRVL | 29 | 301.65 | strict: model momentum_score=0.9536 |
| 2026-06-03 | BUY | OKTA | 62 | 124.65 | strict: model momentum_score=0.9084 |
| 2026-06-04 | BUY | ARM | 20 | 393.44 | strict: model momentum_score=0.8693 |
| 2026-06-04 | BUY | CRWD | 11 | 719.09 | strict: model momentum_score=0.85 |
| 2026-06-05 | BUY | TWLO | 35 | 225.99 | strict: model momentum_score=0.8645 |
| 2026-06-05 | BUY | AXON | 16 | 486.12 | strict: model momentum_score=0.8271 |
| 2026-06-08 | BUY | FTNT | 56 | 143.04 | strict: model momentum_score=0.8229 |
| 2026-06-08 | BUY | LLY | 7 | 1149.15 | strict: model momentum_score=0.8181 |
| 2026-06-09 | BUY | AMAT | 16 | 499.21 | strict: model momentum_score=0.8566 |
| 2026-06-09 | BUY | KLAC | 38 | 213.94 | strict: model momentum_score=0.8542 |
| 2026-06-10 | SELL | ARM | 20 | 307.43 | strict: model stop_loss |
| 2026-06-10 | BUY | ASML | 4 | 1734.19 | strict: model momentum_score=0.8795 |
| 2026-06-11 | SELL | MRVL | 29 | 280.71 | strict: model stop_loss |
| 2026-06-11 | BUY | SPOT | 15 | 486.00 | strict: model momentum_score=0.8747 |
| 2026-06-11 | BUY | HOOD | 90 | 92.23 | strict: model momentum_score=0.8669 |

### balanced (15 trades)

| Date | Action | Ticker | Shares | Price | Reason |
|------|--------|--------|------:|------:|--------|
| 2026-06-03 | BUY | MRVL | 29 | 301.65 | balanced-rule: follow within exposure budget |
| 2026-06-03 | BUY | OKTA | 62 | 124.65 | balanced-rule: follow within exposure budget |
| 2026-06-04 | BUY | ARM | 20 | 393.44 | balanced-rule: follow within exposure budget |
| 2026-06-04 | BUY | CRWD | 11 | 719.09 | balanced-rule: follow within exposure budget |
| 2026-06-05 | BUY | TWLO | 35 | 225.99 | balanced-rule: follow within exposure budget |
| 2026-06-05 | BUY | AXON | 16 | 486.12 | balanced-rule: follow within exposure budget |
| 2026-06-08 | BUY | FTNT | 56 | 143.04 | balanced-rule: follow within exposure budget |
| 2026-06-08 | BUY | LLY | 7 | 1149.15 | balanced-rule: follow within exposure budget |
| 2026-06-09 | BUY | AMAT | 16 | 499.21 | balanced-rule: follow within exposure budget |
| 2026-06-09 | BUY | KLAC | 38 | 213.94 | balanced-rule: follow within exposure budget |
| 2026-06-10 | SELL | ARM | 20 | 307.43 | balanced-rule: take model exit |
| 2026-06-10 | BUY | ASML | 4 | 1734.19 | balanced-rule: follow within exposure budget |
| 2026-06-11 | SELL | MRVL | 29 | 280.71 | balanced-rule: take model exit |
| 2026-06-11 | BUY | SPOT | 15 | 486.00 | balanced-rule: follow within exposure budget |
| 2026-06-11 | BUY | HOOD | 90 | 92.23 | balanced-rule: follow within exposure budget |

### discretionary (9 trades)

| Date | Action | Ticker | Shares | Price | Reason |
|------|--------|--------|------:|------:|--------|
| 2026-06-03 | BUY | MRVL | 29 | 301.65 | discretionary-rule: concentrate in highest-conviction buy |
| 2026-06-04 | BUY | ARM | 20 | 393.44 | discretionary-rule: concentrate in highest-conviction buy |
| 2026-06-05 | BUY | TWLO | 35 | 225.99 | discretionary-rule: concentrate in highest-conviction buy |
| 2026-06-08 | BUY | FTNT | 56 | 143.04 | discretionary-rule: concentrate in highest-conviction buy |
| 2026-06-09 | BUY | KLAC | 38 | 213.94 | discretionary-rule: concentrate in highest-conviction buy |
| 2026-06-10 | SELL | ARM | 20 | 307.43 | discretionary-rule: take model exit |
| 2026-06-10 | BUY | ASML | 4 | 1734.19 | discretionary-rule: concentrate in highest-conviction buy |
| 2026-06-11 | SELL | MRVL | 29 | 280.71 | discretionary-rule: take model exit |
| 2026-06-11 | BUY | HOOD | 90 | 92.23 | discretionary-rule: concentrate in highest-conviction buy |

_Paper-trading research only — not investment advice._