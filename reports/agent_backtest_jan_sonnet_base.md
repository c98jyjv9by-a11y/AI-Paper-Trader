# Agent backtest — model_v4
**Window:** 2026-01-05 → 2026-01-30  |  **Decider:** claude-sonnet-4-6  |  **Packet:** `eod_series_model_v4_2026-01-01_2026-01-31.pdf`

_The agent reads one daily page at a time (no look-ahead) and emits structured trades; the harness owns all fills (next-open, with slippage) and accounting._
_Start: seeded with the first page held book (level with the model).  Extra context sources: none._

## Scorecard

| Setting | Final | Return | Max DD | Trades | Divergences | vs Model |
|---------|------:|------:|------:|------:|-----------:|--------:|
| strict | $106,135 | +6.13% | -4.84% | 9 | 0 | +0.00% |
| balanced | $106,135 | +6.13% | -4.84% | 9 | 0 | +0.00% |
| discretionary | $104,562 | +4.56% | -2.73% | 19 | 7 | -1.57% |

**Benchmarks (same window):** model_v4 +6.15% · SPY +0.62% · QQQ +0.63%.
_`vs Model` = setting return minus the strict (follow-the-model) return — the net effect of the agent's divergences. Positive = its deviations helped._

## strict — divergences (0)
_None — followed the model exactly._

## balanced — divergences (0)
_None — followed the model exactly._

## discretionary — divergences (7)
- **2026-01-07** — skipped: BUY INTC, BUY SNPS
- **2026-01-08** — skipped: BUY ADI, BUY KLAC
- **2026-01-13** — added: BUY BA
- **2026-01-15** — added: SELL ON, SELL MCHP, BUY AMD, BUY GS, BUY KLAC
- **2026-01-26** — added: SELL BA, SELL GS, BUY ANET
- **2026-01-28** — added: BUY TXN, BUY MCHP
- **2026-01-29** — added: BUY META, SELL AMD, SELL ANET

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
| 2026-01-06 | BUY | ASML | 6 | 1237.85 | Top-ranked momentum score (0.954) clears the >0.90 entry gate on its 3rd consecutive day above the bar; sized at ~8.5% of book per model recommendation with full governor budget (1.00×). |
| 2026-01-06 | BUY | LRCX | 43 | 206.71 | Second-ranked momentum score (0.936) also clears the >0.90 entry gate; model-queued buy aligns with commentary's constructive stance and full volatility budget. |
| 2026-01-07 | BUY | MCHP | 115 | 73.14 | Model queue: top-ranked unowned name (score 0.957, rank #3), cleared buy gate for 3rd consecutive day, sized ~8.5% of book within cash budget. |
| 2026-01-07 | BUY | ON | 138 | 61.89 | Model queue: second-ranked unowned name (score 0.923, rank #4), cleared buy gate for 3rd consecutive day, sized ~8.5% of book within remaining cash budget. |
| 2026-01-08 | BUY | INTC | 200 | 41.11 | Model queued buy; INTC ranks #3 in composite (0.882), clears the buy gate, and momentum score supports entry — following model recommendation. |
| 2026-01-08 | BUY | SNPS | 16 | 514.49 | Model queued buy; SNPS ranks #5 in composite (0.855), clears the buy gate — following model recommendation. |
| 2026-01-09 | BUY | ADI | 28 | 299.17 | Model queued buy; ADI ranks #3 with strong momentum score 0.851, clearing the buy gate — following model recommendation in balanced mode. |
| 2026-01-09 | BUY | KLAC | 64 | 139.64 | Model queued buy; KLAC ranks #7 with momentum score 0.799, clearing the buy gate — following model recommendation in balanced mode. |
| 2026-01-12 | BUY | AMAT | 29 | 306.48 | Model-queued buy; AMAT clears the >0.90 entry gate (score 0.904, ranked #5), momentum is working, governor is at full 1.00×, and cash on hand ($16,433) comfortably covers the ~$8,721 cost — following the model's recommendation. |

### discretionary (19 trades)

| Date | Action | Ticker | Shares | Price | Reason |
|------|--------|--------|------:|------:|--------|
| 2026-01-06 | BUY | ASML | 6 | 1237.85 | Top-ranked by composite score (0.954), cleared buy gate for 3rd consecutive day, strong momentum with full governor budget; aligns with model queue and my own read of the commentary. |
| 2026-01-06 | BUY | LRCX | 43 | 206.71 | Second-ranked by composite score (0.936), also cleared the 3-day entry bar; semiconductor equipment sector showing strength and full volatility budget supports normal sizing. |
| 2026-01-07 | BUY | MCHP | 115 | 73.14 | Ranked #3 with momentum score 0.957, cleared the buy gate on 3rd consecutive day above bar; semiconductor sector is in strong momentum and this is the highest-ranked unowned name — full conviction buy at model-sized allocation. |
| 2026-01-07 | BUY | ON | 138 | 61.89 | Ranked #4 with momentum score 0.923, also cleared the 3-day entry gate; another high-quality semi name with strong momentum in a risk-on session, complementary to existing MCHP buy and held book. |
| 2026-01-12 | BUY | AMAT | 29 | 306.48 | AMAT ranks #5 in composite with a 0.904 score clearing the buy gate on its 3rd consecutive day above the bar; strong semiconductor momentum aligns with my existing semi-heavy book, and the volatility governor is at full 1.00× budget supporting normal sizing. |
| 2026-01-14 | BUY | BA | 9 | 242.61 | BA ranks #2 overall at 0.926, clearing the buy gate — highest-ranked unhedld name; ~$8.5k sizing fits discretionary budget with $41k cash available. |
| 2026-01-16 | SELL | ON | 138 | 60.33 | ON scores 0.582 — below the 0.90 stop-loss threshold, sitting at an unrealized loss, and the model flags it as stop-armed; discretionary exit ahead of further deterioration. |
| 2026-01-16 | SELL | MCHP | 115 | 73.89 | MCHP scores 0.686 — well below the buy gate and flagged as stop-armed (0.69 composite); momentum is fading and I'd rather redeploy into higher-ranked names. |
| 2026-01-16 | BUY | AMD | 10 | 231.83 | AMD ranks #6 at 0.876, clears the buy gate, is not held, and is climbing — strong momentum entry with proceeds from today's exits funding the position. |
| 2026-01-16 | BUY | GS | 8 | 952.76 | GS ranks #7 at 0.869, clears the buy gate, is not held — adding a high-scoring non-semiconductor name for diversification using freed-up capital. |
| 2026-01-16 | BUY | KLAC | 5 | 156.38 | KLAC is the #1 ranked name at 0.970 and not held in my portfolio despite strong model conviction — adding a starter position to align with top-ranked momentum. |
| 2026-01-27 | SELL | BA | 9 | 244.56 | BA scores only 0.685 — below the 0.90 entry bar and declining momentum; no strong fundamental catalyst, and with INTC/TSM/AMAT/SNPS flagged on stop-loss watches I want to reduce lower-conviction holdings and free cash. |
| 2026-01-27 | SELL | GS | 8 | 920.79 | GS ranks 41st at 0.511, well below the buy gate; not a high-conviction holding and freeing cash is prudent given the book is already at elevated concentration in semis. |
| 2026-01-27 | BUY | ANET | 15 | 146.69 | ANET is the top-ranked name in the universe at 0.902, clearing the entry gate; as a discretionary agent I'm acting on day-1 of the signal rather than waiting for a 3-day confirmation, given strong relative momentum and the momentum-reversal commentary suggesting leaders will rebound. |
| 2026-01-29 | BUY | TXN | 7 | 216.45 | TXN ranks #1 in composite with score 0.944, well above the buy gate; semiconductor peer with strong momentum; ~$9K position fits within available cash ($52,581) and aligns with discretionary conviction in semis strength. |
| 2026-01-29 | BUY | MCHP | 110 | 78.50 | MCHP ranks #4 at 0.872 and is climbing fast (+27 rank positions); not yet held in my portfolio; strong semiconductor theme consistency with existing book; sizing ~$8.7K within cash budget after TXN buy. |
| 2026-01-30 | BUY | META | 19 | 715.22 | META clears the >0.90 entry score bar (0.911, ranked #1 in the universe) and is not currently held; discretionary buy aligns with model recommendation and strong composite rank, sized ~8.5% of portfolio (~$9,000 at ~$475/sh est.). |
| 2026-01-30 | SELL | AMD | 10 | 236.73 | AMD scores only 0.602 (#24) and is well below the buy gate; it is not in the model's held book either, suggesting it has drifted out of favor — freeing capital for higher-ranked names is the better discretionary call. |
| 2026-01-30 | SELL | ANET | 15 | 141.74 | ANET scored 0.751 today but was flagged as hardest-hit in the session (-1.33%) and sits outside the top-ranked held names; at a sub-0.90 score with no model hold, rotating out into META is more efficient capital allocation. |

_Paper-trading research only — not investment advice._