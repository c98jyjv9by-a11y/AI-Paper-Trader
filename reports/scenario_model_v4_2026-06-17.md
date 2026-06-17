# Scenario — model_v4

RECOMMENDED config. model_v3 (83-name universe, score-conditional exits, persistence buy >0.90, rotation funding) plus Barroso volatility targeting (~35% annualized, tuned to v3's vol profile) that shrinks gross exposure when forecast vol is high — dominated v3 on return, drawdown, Sharpe and PF in 2018-2026 validation.

**Universe (83):** CRWD, ORCL, COIN, NFLX, PANW, GOOGL, BAC, MSFT, AVGO, AMZN, COST, ASML, AAPL, JPM, TSM, GS, META, TSLA, MU, AMD, NVDA, LLY, VST, AXON, GE, PLTR, OXY, INTC, BA, PFE, PYPL, SEDG, PLUG, ADBE, CRM, NOW, INTU, SAP, WDAY, SNOW, DDOG, NET, MDB, ZS, FTNT, TEAM, OKTA, TWLO, HUBS, SNPS, CDNS, QCOM, TXN, AMAT, LRCX, KLAC, NXPI, MRVL, ADI, MCHP, ON, ARM, ANET, CSCO, IBM, DELL, SMCI, VRT, APP, SHOP, UBER, ABNB, MELI, SE, SPOT, DASH, RBLX, PINS, SNAP, TTD, NU, HOOD, SOFI

---

# AI Paper Trader — Backtest Report
**Period:** 2026-01-01 → 2026-06-17  |  **Generated:** 2026-06-17

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Ending Balance | $174,399.01 | $110,099.80 | $119,701.60 | $124,524.10 |
| Total Return | +74.40% | +10.10% | +19.70% | +24.52% |
| Max Drawdown | -14.09% | -8.88% | -11.72% | -16.42% |
| Excess vs SPY | +64.30% | — | — | — |
| Excess vs QQQ | +54.70% | — | — | — |
| Excess vs Equal-Wt | +49.87% | — | — | — |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $174,399.01 |
| **IRR (annualized, money-weighted)** | **+293.11%** |
| Total Return (on full $ portfolio) | +74.40% |
| Total Capital Deployed (all entries) | $240,242.93 |
| Avg Capital Deployed (snapshot) | $109,123.91 (+109.12% of portfolio) |
| Peak Capital Deployed (snapshot) | $165,041.85 (+165.04% of portfolio) |
| Time Invested | +99.13% of trading days |
| Trading Days | 115 |
| Total Trades | 40 (25 buys, 15 sells) |
| Win Rate | +73.33% |
| Average Win | $3,051.27 |
| Average Loss | $-1,903.36 |
| Profit Factor | 4.41 |
| Avg Holding Period | 56.8 approx. trading days |
| Largest Winner | $10,701.71 |
| Largest Loser | $-3,145.06 |
| Open Positions at End | 10 |
| Total Slippage Cost | $397.13 (+0.40% of start) |
| Avg Slippage / Trade | $9.93 |

_**IRR** is the annualized money-weighted (internal) rate of return on the capital actually put into positions: it solves for the rate that discounts the dated BUY outflows, SELL inflows, and the terminal mark-to-market of open positions to zero. It ignores idle cash, so it measures how the *deployed* capital performed, and is bounded at -100%. Being annualized, short backtests can extrapolate to large figures. **Total Return** is on the full starting portfolio (cash included) and is what the SPY/QQQ/Equal-Wt comparisons above use, since those benchmarks are fully invested._

## Strategy Parameters Used

| Parameter | Value |
|-----------|-------|
| Starting Portfolio | $100,000.00 |
| Max Position Size | 8.5% |
| Max Total Exposure | 90% |
| Max New Trades / Day | 2 |
| Stop Loss | 15.0% |
| Take Profit | none |
| Trailing Stop | none |
| Max Holding Period | 90 trading days |
| Stop-loss only if score < | 0.9 |
| Max-hold only if score < | 0.8 |
| Score-decay sell | none |
| Persistence buy | > 0.9 for 3d  (rotate-funded) |
| Vol target (annualized) | 35% — scale exposure by target/forecast vol |
| Slippage | 0.10% per fill |

## Ticker Universe

`CRWD`, `ORCL`, `COIN`, `NFLX`, `PANW`, `GOOGL`, `BAC`, `MSFT`, `AVGO`, `AMZN`, `COST`, `ASML`, `AAPL`, `JPM`, `TSM`, `GS`, `META`, `TSLA`, `MU`, `AMD`, `NVDA`, `LLY`, `VST`, `AXON`, `GE`, `PLTR`, `OXY`, `INTC`, `BA`, `PFE`, `PYPL`, `SEDG`, `PLUG`, `ADBE`, `CRM`, `NOW`, `INTU`, `SAP`, `WDAY`, `SNOW`, `DDOG`, `NET`, `MDB`, `ZS`, `FTNT`, `TEAM`, `OKTA`, `TWLO`, `HUBS`, `SNPS`, `CDNS`, `QCOM`, `TXN`, `AMAT`, `LRCX`, `KLAC`, `NXPI`, `MRVL`, `ADI`, `MCHP`, `ON`, `ARM`, `ANET`, `CSCO`, `IBM`, `DELL`, `SMCI`, `VRT`, `APP`, `SHOP`, `UBER`, `ABNB`, `MELI`, `SE`, `SPOT`, `DASH`, `RBLX`, `PINS`, `SNAP`, `TTD`, `NU`, `HOOD`, `SOFI`

## Trade Log (last 20 trades)

| Date | Action | Ticker | Shares | Price | Value | Reason | P&L | Hold Days |
|------|--------|--------|--------|-------|-------|--------|-----|-----------|
| 2026-04-10 | SELL | OXY | 181 | $57.65 | $10,433.89 | rotation_funded | $1,109.10 | 32.1 |
| 2026-04-13 | BUY | MRVL | 75 | $131.43 | $9,857.35 | momentum_score=0.9596 | — | — |
| 2026-04-24 | SELL | ASML | 6 | $1,453.07 | $8,718.41 | rotation_funded | $1,283.88 | 77.1 |
| 2026-04-27 | BUY | ARM | 46 | $216.10 | $9,940.41 | momentum_score=0.9753 | — | — |
| 2026-04-28 | SELL | LRCX | 43 | $250.98 | $10,792.09 | rotation_funded | $1,894.57 | 80.0 |
| 2026-04-29 | BUY | INTC | 123 | $94.84 | $11,665.90 | momentum_score=0.9404 | — | — |
| 2026-05-07 | SELL | KLAC | 64 | $175.92 | $11,259.14 | rotation_funded | $2,313.24 | 84.3 |
| 2026-05-08 | BUY | QCOM | 56 | $218.50 | $12,236.12 | momentum_score=0.912 | — | — |
| 2026-05-11 | SELL | TSM | 26 | $403.19 | $10,482.97 | max_holding_period | $2,139.20 | 90.0 |
| 2026-05-12 | BUY | DDOG | 59 | $200.14 | $11,808.25 | momentum_score=0.9042 | — | — |
| 2026-05-15 | SELL | MU | 26 | $723.94 | $18,822.32 | max_holding_period | $10,701.71 | 92.9 |
| 2026-05-15 | SELL | ON | 138 | $113.00 | $15,593.57 | max_holding_period | $7,044.21 | 91.4 |
| 2026-05-15 | SELL | ADI | 28 | $415.93 | $11,646.13 | max_holding_period | $3,260.96 | 90.0 |
| 2026-05-18 | BUY | PANW | 46 | $247.80 | $11,398.69 | momentum_score=0.9295 | — | — |
| 2026-05-18 | BUY | SEDG | 183 | $55.29 | $10,117.19 | momentum_score=0.9952 | — | — |
| 2026-05-18 | SELL | AMAT | 29 | $412.64 | $11,966.66 | max_holding_period | $3,069.96 | 90.0 |
| 2026-05-19 | BUY | CRWD | 18 | $617.50 | $11,114.94 | momentum_score=0.9373 | — | — |
| 2026-05-19 | BUY | ZS | 64 | $175.43 | $11,227.21 | momentum_score=0.9325 | — | — |
| 2026-05-20 | BUY | FTNT | 89 | $130.13 | $11,581.57 | momentum_score=0.906 | — | — |
| 2026-05-27 | SELL | ZS | 64 | $126.28 | $8,082.15 | stop_loss | $-3,145.06 | 5.7 |

## Open Positions at End of Period

| Ticker | Shares | Entry Price | Final Price | Unrealized P&L | Entry Date |
|--------|--------|------------|------------|----------------|------------|
| DELL | 62 | $153.23 | $423.61 | $16,763.29 | 2026-03-02 |
| MRVL | 75 | $131.43 | $294.92 | $12,261.64 | 2026-04-13 |
| ARM | 46 | $216.10 | $423.71 | $9,550.48 | 2026-04-27 |
| INTC | 123 | $94.84 | $121.83 | $3,319.19 | 2026-04-29 |
| QCOM | 56 | $218.50 | $218.94 | $24.52 | 2026-05-08 |
| DDOG | 59 | $200.14 | $232.58 | $1,913.97 | 2026-05-12 |
| PANW | 46 | $247.80 | $280.74 | $1,515.35 | 2026-05-18 |
| SEDG | 183 | $55.29 | $58.37 | $563.60 | 2026-05-18 |
| CRWD | 18 | $617.50 | $687.75 | $1,264.56 | 2026-05-19 |
| FTNT | 89 | $130.13 | $144.42 | $1,271.81 | 2026-05-20 |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2026-01-02 | $100,000.00 | — | +0.00% | +0.00% | +0.00% | +0.00% |
| 2026-01-05 | $99,983.56 | -0.02% | -0.02% | +0.67% | +0.79% | +1.66% |
| 2026-01-06 | $100,914.16 | +0.93% | +0.91% | +1.26% | +1.68% | +3.20% |
| 2026-01-07 | $100,321.38 | -0.59% | +0.32% | +0.94% | +1.78% | +2.89% |
| 2026-01-08 | $99,482.07 | -0.84% | -0.52% | +0.93% | +1.20% | +1.38% |
| 2026-06-11 | $166,278.46 | +6.48% | +66.28% | +8.29% | +17.11% | +20.62% |
| 2026-06-12 | $169,792.60 | +2.11% | +69.79% | +8.87% | +17.80% | +21.55% |
| 2026-06-15 | $175,960.64 | +3.63% | +75.96% | +10.79% | +21.50% | +25.56% |
| 2026-06-16 | $169,584.81 | -3.62% | +69.58% | +10.13% | +19.19% | +22.35% |
| 2026-06-17 | $174,399.01 | +2.84% | +74.40% | +10.10% | +19.70% | +24.52% |


## Signal Predictiveness

_Cross-section of 9,462 (date, ticker) signal observations. Correlations are Pearson vs forward returns._

| Signal | vs fwd 5d | vs fwd 10d | vs fwd 20d |
|--------|-----------|------------|------------|
| return_1d | 0.01 | 0.01 | 0.04 |
| return_5d | -0.02 | 0.04 | 0.10 |
| return_20d | 0.06 | 0.10 | 0.17 |
| vol_ratio | 0.00 | -0.02 | 0.01 |
| vol_adj_mom_20d | 0.07 | 0.11 | 0.15 |
| composite_score | 0.05 | 0.08 | 0.11 |

**Forward returns by composite-score quintile** (5 = highest-ranked):

| Quintile | N | Avg fwd 5d | Win 5d | Avg fwd 10d | Win 10d | Avg fwd 20d | Win 20d |
|----------|---|-----------|--------|-------------|---------|-------------|---------|
| Q1 | 1938 | +0.56% | +49.52% | +0.81% | +48.52% | +2.45% | +51.83% |
| Q2 | 1824 | +0.61% | +51.48% | +0.78% | +50.48% | +1.79% | +50.66% |
| Q3 | 1938 | +0.08% | +47.81% | +0.59% | +46.78% | +1.91% | +46.75% |
| Q4 | 1824 | +0.49% | +49.03% | +1.69% | +49.35% | +4.18% | +51.71% |
| Q5 | 1938 | +1.75% | +54.22% | +3.38% | +55.18% | +7.59% | +56.22% |

**Top-minus-bottom quintile spread:** 5d +1.19%  |  10d +2.57%  |  20d +5.14%  (positive ⇒ higher-ranked names outperform lower-ranked names).

## Entry vs Exit Attribution

_Buy the top 2 ranked names each day, hold a fixed period, **no** stop-loss / take-profit / max-holding. Next-day entry, slippage applied._

| Hold period | Raw avg return / trade | Raw win rate | N trades |
|-------------|------------------------|--------------|----------|
| 5d | +2.36% | +56.42% | 218 |
| 10d | +4.64% | +60.10% | 208 |
| 20d | +12.07% | +63.30% | 188 |
| 30d | +17.87% | +64.88% | 168 |

**Full strategy (with exit rules):** total return +74.40%, win rate +73.33%, avg hold 56.76 trading days.

The raw signal (buy top names, hold fixed, no stops) is **positive across holding periods** (avg +9.24% per trade, 61% win rate). That points to genuine signal quality — higher-ranked names tend to rise even without exit rules.

## P&L Attribution

**Top 5 contributors:**

| Ticker | P&L |
|--------|-----|
| DELL | $16,763.29 |
| MRVL | $12,261.64 |
| MU | $10,701.71 |
| ARM | $9,550.48 |
| ON | $7,044.21 |

**Worst 5 contributors:**

| Ticker | P&L |
|--------|-----|
| ZS | $-3,145.06 |
| SNPS | $-1,540.54 |
| TXN | $-1,359.70 |
| SEDG | $-1,004.54 |
| QCOM | $24.52 |

**P&L by asset group:**

| Group | P&L |
|-------|-----|
| semiconductors | $20,252.19 |
| software_cybersecurity | $2,779.91 |
| _(ungrouped)_ | $51,366.90 |

## Turnover and Re-entry Diagnostics

| Metric | Value |
|--------|-------|
| Total trades | 40 |
| Trades / month | 7.29 |
| Avg holding period | 56.76 trading days |
| Stop-loss → re-entry ≤5d | 0 |

**Most-entered tickers:** `INTC`×2, `SEDG`×2, `MU`×1, `TSM`×1, `ASML`×1, `LRCX`×1, `MCHP`×1, `ON`×1

## Exposure and Benchmark Capture

| Metric | Value |
|--------|-------|
| Avg exposure | +89.29% |
| Max exposure | +97.61% |
| Avg cash (drag) | +10.71% |
| Correlation to SPY | 0.68 |
| Correlation to QQQ | 0.77 |
| Beta to SPY | 2.07 |
| Beta to QQQ | 1.60 |
| Up-capture vs QQQ | 2.01 |
| Down-capture vs QQQ | 1.55 |

_Beta ≈ 1 with high correlation ⇒ performance is mostly market exposure; low beta with a positive quintile spread ⇒ more genuine selection alpha._

## Suggested Next Config Tests

_Ideas to test next — not yet implemented._

- **QQQ trend filter** — only take entries while QQQ is above its 50-day moving average.
- **Volatility-adjusted momentum** — rank on `return_20d / realized_vol_20d` instead of raw return.
- **Moving-average confirmation** — require price above both its 20-day and 50-day moving averages.
- **Overextension filter** — skip names too far above their 20-day moving average (avoid chasing).
- **Cooldown after stop-loss** — block re-entry into a name for 5 trading days after a stop-out.
- **Separate leveraged-ETF rules** — smaller max position size and shorter max holding for leveraged ETFs.


## Limitations & Assumptions

1. **Entry fills at next-day close.** Signals fire at day T's close; orders fill at day T+1's close. This approximates next-morning execution but uses close rather than true open prices.
2. **Exit fills at same-day close.** Stop-loss, take-profit, and max-holding-period triggers are detected and filled on the same close. In practice you may fill at the next open, which could be worse.
3. **Holding period is approximate.** Uses calendar days × 5/7; does not consult an actual trading-day calendar.
4. **No commissions.** Only the configured slippage (0.10%) is deducted per fill.
5. **No partial fills, no market impact.** All orders assumed fully filled.
6. **Survivorship bias possible.** Universe is fixed; tickers that were delisted during the test period may not appear in yfinance data.
7. **Past results do not predict future performance.**

---
_This report is for research purposes only. No real trades are placed._

## Sensitivity Analysis

> One parameter is varied at a time; everything else stays at the scenario's configured values. **Run-wide** params apply to the whole backtest. **Ticker** params overwrite that exit field for *every* `ticker_groups` name at once — a uniform stand-in for the per-ticker mix, with the real heterogeneous config shown as the `as-configured` baseline row.
> In-sample only — do not pick parameters off these tables; see Robustness Notes.

**Baseline (as configured):** +74.40% return  |  -14.09% max drawdown  |  +73.33% win rate  |  4.41 profit factor

### Run-wide parameters

#### Max Total Exposure  (baseline: 90%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 50% | +41.04% | +30.94% | +16.51% | -11.73% | 24 | +66.67% | 6.63 |
| 70% | +43.72% | +33.62% | +19.19% | -12.90% | 31 | +63.64% | 5.71 |
| 90% ◀ baseline | +74.40% | +64.30% | +49.87% | -14.09% | 40 | +73.33% | 4.41 |
| 100% | +86.26% | +76.16% | +61.74% | -13.48% | 45 | +77.78% | 5.49 |

#### Max Position Size  (baseline: 8.50%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 4.25% | +60.57% | +50.47% | +36.04% | -15.80% | 81 | +48.39% | 2.58 |
| 8.50% ◀ baseline | +74.40% | +64.30% | +49.87% | -14.09% | 40 | +73.33% | 4.41 |
| 12.75% | +86.77% | +76.67% | +62.24% | -14.45% | 36 | +80.00% | 4.60 |
| 17.00% | +69.05% | +58.95% | +44.52% | -12.07% | 43 | +68.42% | 4.42 |
| 25.50% | +88.51% | +78.41% | +63.98% | -15.88% | 54 | +60.00% | 3.22 |

#### Max New Trades / Day  (baseline: 2)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 1 | +80.06% | +69.96% | +55.54% | -15.63% | 41 | +68.75% | 5.58 |
| 2 ◀ baseline | +74.40% | +64.30% | +49.87% | -14.09% | 40 | +73.33% | 4.41 |
| 3 | +86.73% | +76.63% | +62.21% | -14.15% | 40 | +66.67% | 4.69 |
| 5 | +72.55% | +62.45% | +48.03% | -14.65% | 45 | +50.00% | 2.26 |

#### Min Composite Score  (baseline: 0.70)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| none | +74.40% | +64.30% | +49.87% | -14.09% | 40 | +73.33% | 4.41 |
| 0.60 | +74.40% | +64.30% | +49.87% | -14.09% | 40 | +73.33% | 4.41 |
| 0.70 ◀ baseline | +74.40% | +64.30% | +49.87% | -14.09% | 40 | +73.33% | 4.41 |

#### Slippage  (baseline: 0.10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 0.05% | +72.74% | +62.64% | +48.21% | -14.58% | 43 | +70.59% | 3.36 |
| 0.10% ◀ baseline | +74.40% | +64.30% | +49.87% | -14.09% | 40 | +73.33% | 4.41 |
| 0.20% | +73.95% | +63.85% | +49.42% | -14.11% | 40 | +73.33% | 4.34 |
| 0.50% | +72.51% | +62.41% | +47.98% | -14.10% | 40 | +73.33% | 4.20 |

#### Re-entry Recovery Gate  (baseline: 10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +74.40% | +64.30% | +49.87% | -14.09% | 40 | +73.33% | 4.41 |
| 0% | +74.40% | +64.30% | +49.87% | -14.09% | 40 | +73.33% | 4.41 |
| 5% | +74.40% | +64.30% | +49.87% | -14.09% | 40 | +73.33% | 4.41 |
| 10% ◀ baseline | +74.40% | +64.30% | +49.87% | -14.09% | 40 | +73.33% | 4.41 |

#### Stop-loss only if score <  (baseline: 0.90)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +74.40% | +64.30% | +49.87% | -14.09% | 40 | +73.33% | 4.41 |
| 0.85 | +74.40% | +64.30% | +49.87% | -14.09% | 40 | +73.33% | 4.41 |
| 0.90 ◀ baseline | +74.40% | +64.30% | +49.87% | -14.09% | 40 | +73.33% | 4.41 |
| 0.95 | +74.40% | +64.30% | +49.87% | -14.09% | 40 | +73.33% | 4.41 |

#### Max-hold only if score <  (baseline: 0.80)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +79.53% | +69.43% | +55.01% | -13.57% | 40 | +73.33% | 4.67 |
| 0.70 | +73.88% | +63.78% | +49.35% | -14.13% | 40 | +73.33% | 4.34 |
| 0.80 ◀ baseline | +74.40% | +64.30% | +49.87% | -14.09% | 40 | +73.33% | 4.41 |
| 0.90 | +75.47% | +65.37% | +50.95% | -14.09% | 40 | +73.33% | 4.62 |

#### Score-decay sell threshold  (baseline: off)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off ◀ baseline | +74.40% | +64.30% | +49.87% | -14.09% | 40 | +73.33% | 4.41 |
| 0.40 | +76.22% | +66.12% | +51.69% | -14.22% | 51 | +63.64% | 2.06 |
| 0.50 | +56.90% | +46.80% | +32.38% | -15.28% | 94 | +41.86% | 2.10 |
| 0.60 | +65.69% | +55.59% | +41.17% | -13.66% | 121 | +48.21% | 3.02 |

#### Persistence-buy threshold  (baseline: 0.90)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +57.21% | +47.11% | +32.69% | -16.01% | 40 | +60.00% | 4.57 |
| 0.80 | +75.40% | +65.30% | +50.88% | -15.02% | 113 | +51.92% | 2.94 |
| 0.85 | +50.15% | +40.05% | +25.62% | -14.37% | 87 | +56.41% | 2.22 |
| 0.90 ◀ baseline | +74.40% | +64.30% | +49.87% | -14.09% | 40 | +73.33% | 4.41 |

#### Vol-target (annualized)  (baseline: 35%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +72.35% | +62.25% | +47.82% | -14.00% | 46 | +77.78% | 4.83 |
| 15% | +35.63% | +25.53% | +11.11% | -15.50% | 39 | +64.29% | 5.16 |
| 20% | +37.55% | +27.45% | +13.02% | -15.50% | 38 | +64.29% | 4.60 |
| 25% | +46.04% | +35.94% | +21.52% | -15.50% | 37 | +69.23% | 5.23 |
| 30% | +54.53% | +44.43% | +30.01% | -15.66% | 40 | +60.00% | 2.79 |
| 35% ◀ baseline | +74.40% | +64.30% | +49.87% | -14.09% | 40 | +73.33% | 4.41 |

#### Signal Weight Profile  (baseline: baseline)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| baseline ◀ baseline | +74.40% | +64.30% | +49.87% | -14.09% | 40 | +73.33% | 4.41 |
| no_1d | +75.53% | +65.43% | +51.00% | -14.70% | 64 | +64.29% | 3.03 |
| less_1d | +74.40% | +64.30% | +49.87% | -14.09% | 40 | +73.33% | 4.41 |
| more_volume | +81.55% | +71.45% | +57.02% | -15.62% | 41 | +60.00% | 4.48 |

### Best 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | max_position_pct | 25.50% | +88.51% | +63.98% | -15.88% | 3.22 |
| 2 | max_position_pct | 12.75% | +86.77% | +62.24% | -14.45% | 4.60 |
| 3 | max_new_trades_per_day | 3 | +86.73% | +62.21% | -14.15% | 4.69 |
| 4 | max_total_exposure | 100% | +86.26% | +61.74% | -13.48% | 5.49 |
| 5 | signal_weights | more_volume | +81.55% | +57.02% | -15.62% | 4.48 |

### Worst 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | target_vol | 15% | +35.63% | +11.11% | -15.50% | 5.16 |
| 2 | target_vol | 20% | +37.55% | +13.02% | -15.50% | 4.60 |
| 3 | max_total_exposure | 50% | +41.04% | +16.51% | -11.73% | 6.63 |
| 4 | max_total_exposure | 70% | +43.72% | +19.19% | -12.90% | 5.71 |
| 5 | target_vol | 25% | +46.04% | +21.52% | -15.50% | 5.23 |

### Robustness Notes

The baseline outperforms 78% of all variants. This is broadly consistent across parameter dimensions, suggesting the baseline settings are reasonably competitive in-sample.

The widest in-sample return spread belongs to `max_total_exposure` (45.2 pp range across its variants); `min_composite_score` shows the narrowest spread (0.0 pp), suggesting the strategy is least sensitive to that parameter in this period.

Improvements that appear in only one or two variants should be treated with skepticism — isolated peaks are more likely to reflect in-sample noise than genuine edge. Prefer settings that perform consistently across the full sweep.
