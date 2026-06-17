# Agent backtest — model_v4
**Window:** 2026-01-05 → 2026-01-30  |  **Decider:** claude-sonnet-4-6  |  **Packet:** `eod_series_model_v4_2026-01-01_2026-01-31.pdf`

_The agent reads one daily page at a time (no look-ahead) and emits structured trades; the harness owns all fills (next-open, with slippage) and accounting._
_Start: seeded with the first page held book (level with the model).  Extra context sources: macro,news._

## Scorecard

| Setting | Final | Return | Max DD | Trades | Divergences | vs Model |
|---------|------:|------:|------:|------:|-----------:|--------:|
| strict | $106,135 | +6.13% | -4.84% | 9 | 0 | +0.00% |
| balanced | $106,007 | +6.01% | -4.91% | 10 | 1 | -0.13% |
| discretionary | $105,467 | +5.47% | -1.91% | 16 | 7 | -0.67% |

**Benchmarks (same window):** model_v4 +6.15% · SPY +0.62% · QQQ +0.63%.
_`vs Model` = setting return minus the strict (follow-the-model) return — the net effect of the agent's divergences. Positive = its deviations helped._

## strict — divergences (0)
_None — followed the model exactly._

## balanced — divergences (1)
- **2026-01-13** — added: BUY BA

## discretionary — divergences (7)
- **2026-01-07** — skipped: BUY INTC, BUY SNPS
- **2026-01-08** — skipped: BUY ADI, BUY KLAC
- **2026-01-13** — added: BUY BA, SELL ON, SELL MCHP
- **2026-01-21** — added: BUY AMD, SELL BA
- **2026-01-23** — added: BUY AMD, SELL TSM
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

### balanced (10 trades)

| Date | Action | Ticker | Shares | Price | Reason |
|------|--------|--------|------:|------:|--------|
| 2026-01-06 | BUY | ASML | 6 | 1237.85 | Top-ranked momentum name (0.954) clearing the buy gate for 3rd consecutive day; model queued, balanced setting defaults to following — governor at full 1.00x budget supports full sizing. |
| 2026-01-06 | BUY | LRCX | 43 | 206.71 | 2nd-ranked momentum name (0.936) clearing the buy gate; model queued, balanced setting defaults to following — risk-on session with momentum working confirms constructive stance. |
| 2026-01-07 | BUY | MCHP | 115 | 73.14 | Model queue: MCHP ranks #3 with momentum score 0.957, clearing the >0.90 entry gate on its 3rd consecutive day above the bar; sized ~8.5% of book at full 1.00× governor with sufficient cash available. |
| 2026-01-07 | BUY | ON | 138 | 61.89 | Model queue: ON ranks #4 with momentum score 0.923, clearing the >0.90 entry gate on its 3rd consecutive day above the bar; risk-on session confirms momentum working, cash is sufficient after MCHP fill. |
| 2026-01-08 | BUY | INTC | 200 | 41.11 | Follows model queue: INTC ranks #3 with momentum score 0.882, clearing the buy gate; ~$8,534 cost is within cash budget. |
| 2026-01-08 | BUY | SNPS | 16 | 514.49 | Follows model queue: SNPS ranks #5 with momentum score 0.855, clearing the buy gate; ~$8,324 cost keeps total spend within the ~$50,235 cash available. |
| 2026-01-09 | BUY | ADI | 28 | 299.17 | Model queued buy with strong momentum score (0.851, #3 ranked); clears the buy gate and cash is sufficient (~$8,336 at quoted price). |
| 2026-01-09 | BUY | KLAC | 64 | 139.64 | Model queued buy with solid momentum score (0.799, #7 ranked); clears the buy gate and remaining cash covers ~$8,464 at quoted price. |
| 2026-01-12 | BUY | AMAT | 29 | 306.48 | Model queued buy with momentum score 0.9036, clearing the >0.90 entry gate on 3rd consecutive day above bar; balanced setting defaults to following model recommendation; cash available ($16,433) comfortably covers ~$8,721 cost. |
| 2026-01-14 | BUY | BA | 14 | 242.61 | BA is the only model buy candidate clearing the >0.90 entry gate (score 0.926, ranked #2 universe-wide); sized ~8.5% of book (~$7,400) within available cash of $7,537 — follows the model's recommendation to add triggered entries at full governor sizing. |

### discretionary (16 trades)

| Date | Action | Ticker | Shares | Price | Reason |
|------|--------|--------|------:|------:|--------|
| 2026-01-06 | BUY | ASML | 6 | 1237.85 | Top-ranked name (0.954) with confirmed 3-day momentum trigger; semiconductor equipment leadership aligns with AI capex tailwinds; VIX low at 14.9 and governor at full 1.0x budget support full sizing. |
| 2026-01-06 | BUY | LRCX | 43 | 206.71 | Second-ranked name (0.936) with confirmed entry trigger; LRCX benefits from same semiconductor equipment cycle as ASML; price fits within remaining cash after ASML purchase (~$8,373 remaining is sufficient for 43 shares at ~$194.72). |
| 2026-01-07 | BUY | MCHP | 115 | 73.14 | Top-ranked unowned name (0.957, cleared buy gate for 3rd consecutive day), semiconductor momentum is strong (MU +10% session, AI memory cycle), risk-on environment with VIX at 14.8 and SPY above 50d MA — fully endorsed by both model and macro context. |
| 2026-01-07 | BUY | ON | 138 | 61.89 | 4th-ranked composite score (0.923), also cleared the buy gate; semiconductor sector strength is broad-based and the volatility governor is at full 1.00x budget — follow model queue with conviction given risk-on tape and positive breadth. |
| 2026-01-12 | BUY | AMAT | 29 | 306.48 | Top-ranked unowned name (0.904, #5) clearing the buy gate on 3rd consecutive day above threshold; momentum is working in this session, semiconductor equipment peers (LRCX, KLAC, ASML) all surging, and cash is ample to fund at ~$8.7k within position-size budget. |
| 2026-01-14 | BUY | BA | 14 | 242.61 | BA ranks #2 in composite at 0.926, clearing the buy gate; Industrials sector is the top performer (+5.0% 20d), and with ~$41K cash I have ample room to size ~$8-9K into this high-conviction name. |
| 2026-01-14 | SELL | ON | 138 | 60.58 | ON scores only 0.504 (well below the 0.90 entry threshold and near stop-loss territory at 0.50), carries a -4.1% unrealized loss, and is ranked #40 in the universe — weak conviction holding consuming capital better deployed elsewhere. |
| 2026-01-14 | SELL | MCHP | 115 | 73.87 | MCHP scores 0.578, ranked #30, and sits just above its automatic stop (0.58 composite) — near flat on cost basis with risk of further score deterioration; prudent to exit before stop fires. |
| 2026-01-22 | BUY | AMD | 9 | 253.73 | AMD ranks #3 composite (0.935), clears the >0.90 buy gate, and is not yet held; semiconductors are in a strong risk-on session with INTC/MU leading — AMD is a natural add. ~$850/sh × 9 ≈ $7,650, well within cash available and roughly 7-8% of total book value. |
| 2026-01-22 | SELL | BA | 14 | 251.41 | BA ranks only #18 composite (0.731) and is well below the 0.90 buy gate; it is a clear underperformer vs. the semiconductor-heavy book. Exiting frees ~$3,400 cash to redeploy into higher-ranked names and removes the lowest-conviction holding from the portfolio. |
| 2026-01-26 | BUY | AMD | 5 | 251.31 | AMD tops the composite ranking at 0.926, clearing the buy gate, and has strong momentum with Cathie Wood backing and AI narrative tailwinds; adding to existing 9-share position at discretion given solid score and available cash. |
| 2026-01-26 | SELL | TSM | 13 | 331.00 | TSM composite score has dropped to 0.587 (below 0.63 stop-loss zone, near armed-stop territory at 0.59), a contrarian downgrade note just published, and the session showed +2.29% — a good exit price on half the position to reduce risk while the score is deteriorating. |
| 2026-01-29 | BUY | TXN | 5 | 216.45 | TXN ranks #1 in composite with a 0.944 score, clearing the buy gate; semiconductor cycle tailwind aligns with our existing semi book; ~$800 estimated cost fits well within $59K cash reserve. |
| 2026-01-29 | SELL | AMD | 14 | 252.18 | AMD scores only 0.530 (rank #36), below the buy gate and among the weakest names in our held book; not in the model portfolio and no momentum thesis — reallocating capital to higher-conviction names. |
| 2026-01-30 | BUY | META | 8 | 715.22 | Top composite score (0.911) and clears the buy gate; strong momentum name in a risk-off session where high-scored names outperformed — sizing ~8.5% of book (~$8,500 at ~$1,050 est.) within cash available. |
| 2026-01-30 | BUY | TXN | 35 | 214.46 | Already held 5 shares at a profit; second-highest composite score (0.905), clears buy gate, positive news flow on momentum, and strong sector (Energy/Industrials/Tech rotation); adding to bring position to meaningful size within cash budget. |

_Paper-trading research only — not investment advice._