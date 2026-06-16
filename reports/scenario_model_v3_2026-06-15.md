# Scenario — model_v3

model_v2's 83-name universe and uniform exit rule, plus score-conditional exits: stop-loss only below a 0.90 composite score, and max-hold suppressed until the score falls below 0.80 — so still-strong names are given room to run.

**Universe (83):** CRWD, ORCL, COIN, NFLX, PANW, GOOGL, BAC, MSFT, AVGO, AMZN, COST, ASML, AAPL, JPM, TSM, GS, META, TSLA, MU, AMD, NVDA, LLY, VST, AXON, GE, PLTR, OXY, INTC, BA, PFE, PYPL, SEDG, PLUG, ADBE, CRM, NOW, INTU, SAP, WDAY, SNOW, DDOG, NET, MDB, ZS, FTNT, TEAM, OKTA, TWLO, HUBS, SNPS, CDNS, QCOM, TXN, AMAT, LRCX, KLAC, NXPI, MRVL, ADI, MCHP, ON, ARM, ANET, CSCO, IBM, DELL, SMCI, VRT, APP, SHOP, UBER, ABNB, MELI, SE, SPOT, DASH, RBLX, PINS, SNAP, TTD, NU, HOOD, SOFI

---

# AI Paper Trader — Backtest Report
**Period:** 2026-01-01 → 2026-06-15  |  **Generated:** 2026-06-15

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Ending Balance | $172,991.08 | $110,791.10 | $121,499.60 | $125,557.70 |
| Total Return | +72.99% | +10.79% | +21.50% | +25.56% |
| Max Drawdown | -14.00% | -8.88% | -11.72% | -16.42% |
| Excess vs SPY | +62.20% | — | — | — |
| Excess vs QQQ | +51.49% | — | — | — |
| Excess vs Equal-Wt | +47.43% | — | — | — |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $172,991.08 |
| **IRR (annualized, money-weighted)** | **+290.56%** |
| Total Return (on full $ portfolio) | +72.99% |
| Total Capital Deployed (all entries) | $271,310.38 |
| Avg Capital Deployed (snapshot) | $108,561.99 (+108.56% of portfolio) |
| Peak Capital Deployed (snapshot) | $165,287.14 (+165.29% of portfolio) |
| Time Invested | +99.12% of trading days |
| Trading Days | 113 |
| Total Trades | 44 (27 buys, 17 sells) |
| Win Rate | +76.47% |
| Average Win | $2,809.24 |
| Average Loss | $-1,940.22 |
| Profit Factor | 4.71 |
| Avg Holding Period | 52.5 approx. trading days |
| Largest Winner | $10,701.71 |
| Largest Loser | $-3,292.49 |
| Open Positions at End | 10 |
| Total Slippage Cost | $455.43 (+0.46% of start) |
| Avg Slippage / Trade | $10.35 |

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
| Slippage | 0.10% per fill |

## Ticker Universe

`CRWD`, `ORCL`, `COIN`, `NFLX`, `PANW`, `GOOGL`, `BAC`, `MSFT`, `AVGO`, `AMZN`, `COST`, `ASML`, `AAPL`, `JPM`, `TSM`, `GS`, `META`, `TSLA`, `MU`, `AMD`, `NVDA`, `LLY`, `VST`, `AXON`, `GE`, `PLTR`, `OXY`, `INTC`, `BA`, `PFE`, `PYPL`, `SEDG`, `PLUG`, `ADBE`, `CRM`, `NOW`, `INTU`, `SAP`, `WDAY`, `SNOW`, `DDOG`, `NET`, `MDB`, `ZS`, `FTNT`, `TEAM`, `OKTA`, `TWLO`, `HUBS`, `SNPS`, `CDNS`, `QCOM`, `TXN`, `AMAT`, `LRCX`, `KLAC`, `NXPI`, `MRVL`, `ADI`, `MCHP`, `ON`, `ARM`, `ANET`, `CSCO`, `IBM`, `DELL`, `SMCI`, `VRT`, `APP`, `SHOP`, `UBER`, `ABNB`, `MELI`, `SE`, `SPOT`, `DASH`, `RBLX`, `PINS`, `SNAP`, `TTD`, `NU`, `HOOD`, `SOFI`

## Trade Log (last 20 trades)

| Date | Action | Ticker | Shares | Price | Value | Reason | P&L | Hold Days |
|------|--------|--------|--------|-------|-------|--------|-----|-----------|
| 2026-04-28 | SELL | LRCX | 43 | $250.98 | $10,792.09 | rotation_funded | $1,894.57 | 80.0 |
| 2026-04-29 | BUY | INTC | 123 | $94.84 | $11,665.90 | momentum_score=0.9404 | — | — |
| 2026-05-07 | SELL | KLAC | 64 | $175.92 | $11,259.14 | rotation_funded | $2,313.24 | 84.3 |
| 2026-05-08 | BUY | QCOM | 56 | $218.50 | $12,236.12 | momentum_score=0.912 | — | — |
| 2026-05-11 | SELL | TSM | 26 | $403.19 | $10,482.97 | max_holding_period | $2,139.20 | 90.0 |
| 2026-05-12 | BUY | DDOG | 60 | $200.14 | $12,008.39 | momentum_score=0.9042 | — | — |
| 2026-05-15 | SELL | MU | 26 | $723.94 | $18,822.32 | max_holding_period | $10,701.71 | 92.9 |
| 2026-05-15 | SELL | ON | 138 | $113.00 | $15,593.57 | max_holding_period | $7,044.21 | 91.4 |
| 2026-05-15 | SELL | ADI | 28 | $415.93 | $11,646.13 | max_holding_period | $3,260.96 | 90.0 |
| 2026-05-18 | BUY | PANW | 48 | $247.80 | $11,894.28 | momentum_score=0.9295 | — | — |
| 2026-05-18 | BUY | SEDG | 192 | $55.29 | $10,614.76 | momentum_score=0.9952 | — | — |
| 2026-05-18 | SELL | AMAT | 29 | $412.64 | $11,966.66 | max_holding_period | $3,069.96 | 90.0 |
| 2026-05-19 | BUY | CRWD | 19 | $617.50 | $11,732.44 | momentum_score=0.9373 | — | — |
| 2026-05-19 | BUY | ZS | 67 | $175.43 | $11,753.49 | momentum_score=0.9325 | — | — |
| 2026-05-20 | BUY | FTNT | 92 | $130.13 | $11,971.96 | momentum_score=0.906 | — | — |
| 2026-05-27 | SELL | ZS | 67 | $126.28 | $8,461.00 | stop_loss | $-3,292.49 | 5.7 |
| 2026-06-01 | SELL | INTC | 123 | $109.22 | $13,434.15 | rotation_funded | $1,768.25 | 23.6 |
| 2026-06-02 | BUY | SNOW | 54 | $261.40 | $14,115.66 | momentum_score=0.9639 | — | — |
| 2026-06-02 | SELL | QCOM | 56 | $239.71 | $13,423.97 | rotation_funded | $1,187.85 | 17.9 |
| 2026-06-03 | BUY | OKTA | 114 | $124.77 | $14,224.32 | momentum_score=0.9084 | — | — |

## Open Positions at End of Period

| Ticker | Shares | Entry Price | Final Price | Unrealized P&L | Entry Date |
|--------|--------|------------|------------|----------------|------------|
| DELL | 62 | $153.23 | $409.07 | $15,862.12 | 2026-03-02 |
| MRVL | 75 | $131.43 | $308.88 | $13,308.65 | 2026-04-13 |
| ARM | 46 | $216.10 | $412.55 | $9,036.89 | 2026-04-27 |
| DDOG | 60 | $200.14 | $233.09 | $1,977.01 | 2026-05-12 |
| PANW | 48 | $247.80 | $284.54 | $1,763.64 | 2026-05-18 |
| SEDG | 192 | $55.29 | $60.19 | $941.72 | 2026-05-18 |
| CRWD | 19 | $617.50 | $692.91 | $1,432.85 | 2026-05-19 |
| FTNT | 92 | $130.13 | $149.49 | $1,781.12 | 2026-05-20 |
| SNOW | 54 | $261.40 | $240.78 | $-1,113.54 | 2026-06-02 |
| OKTA | 114 | $124.77 | $118.12 | $-758.64 | 2026-06-03 |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2026-01-02 | $100,000.00 | — | +0.00% | +0.00% | +0.00% | +0.00% |
| 2026-01-05 | $99,983.56 | -0.02% | -0.02% | +0.67% | +0.79% | +1.66% |
| 2026-01-06 | $100,914.16 | +0.93% | +0.91% | +1.26% | +1.68% | +3.20% |
| 2026-01-07 | $100,321.38 | -0.59% | +0.32% | +0.94% | +1.78% | +2.89% |
| 2026-01-08 | $99,482.07 | -0.84% | -0.52% | +0.93% | +1.20% | +1.38% |
| 2026-06-09 | $160,374.98 | -3.56% | +60.38% | +8.18% | +15.59% | +19.20% |
| 2026-06-10 | $156,818.50 | -2.22% | +56.82% | +6.48% | +13.28% | +15.99% |
| 2026-06-11 | $165,518.17 | +5.55% | +65.52% | +8.29% | +17.11% | +20.62% |
| 2026-06-12 | $167,068.91 | +0.94% | +67.07% | +8.87% | +17.80% | +21.55% |
| 2026-06-15 | $172,991.08 | +3.54% | +72.99% | +10.79% | +21.50% | +25.56% |


## Signal Predictiveness

_Cross-section of 9,296 (date, ticker) signal observations. Correlations are Pearson vs forward returns._

| Signal | vs fwd 5d | vs fwd 10d | vs fwd 20d |
|--------|-----------|------------|------------|
| return_1d | 0.01 | 0.00 | 0.04 |
| return_5d | -0.01 | 0.06 | 0.10 |
| return_20d | 0.06 | 0.12 | 0.17 |
| vol_ratio | 0.00 | -0.02 | 0.02 |
| vol_adj_mom_20d | 0.07 | 0.12 | 0.15 |
| composite_score | 0.04 | 0.08 | 0.11 |

**Forward returns by composite-score quintile** (5 = highest-ranked):

| Quintile | N | Avg fwd 5d | Win 5d | Avg fwd 10d | Win 10d | Avg fwd 20d | Win 20d |
|----------|---|-----------|--------|-------------|---------|-------------|---------|
| Q1 | 1904 | +0.51% | +49.24% | +0.81% | +48.26% | +2.31% | +51.42% |
| Q2 | 1792 | +0.57% | +51.33% | +0.85% | +50.67% | +1.61% | +50.13% |
| Q3 | 1904 | +0.02% | +47.44% | +0.69% | +47.29% | +1.75% | +46.43% |
| Q4 | 1792 | +0.47% | +48.90% | +1.82% | +49.70% | +4.21% | +51.95% |
| Q5 | 1904 | +1.67% | +53.87% | +3.63% | +56.03% | +7.55% | +56.04% |

**Top-minus-bottom quintile spread:** 5d +1.15%  |  10d +2.83%  |  20d +5.24%  (positive ⇒ higher-ranked names outperform lower-ranked names).

## Entry vs Exit Attribution

_Buy the top 2 ranked names each day, hold a fixed period, **no** stop-loss / take-profit / max-holding. Next-day entry, slippage applied._

| Hold period | Raw avg return / trade | Raw win rate | N trades |
|-------------|------------------------|--------------|----------|
| 5d | +2.29% | +56.07% | 214 |
| 10d | +4.82% | +60.78% | 204 |
| 20d | +12.33% | +63.04% | 184 |
| 30d | +18.22% | +65.24% | 164 |

**Full strategy (with exit rules):** total return +72.99%, win rate +76.47%, avg hold 52.52 trading days.

The raw signal (buy top names, hold fixed, no stops) is **positive across holding periods** (avg +9.41% per trade, 61% win rate). That points to genuine signal quality — higher-ranked names tend to rise even without exit rules.

## P&L Attribution

**Top 5 contributors:**

| Ticker | P&L |
|--------|-----|
| DELL | $15,862.12 |
| MRVL | $13,308.65 |
| MU | $10,701.71 |
| ARM | $9,036.89 |
| ON | $7,044.21 |

**Worst 5 contributors:**

| Ticker | P&L |
|--------|-----|
| ZS | $-3,292.49 |
| SNPS | $-1,540.54 |
| TXN | $-1,359.70 |
| SNOW | $-1,113.54 |
| OKTA | $-758.64 |

**P&L by asset group:**

| Group | P&L |
|-------|-----|
| semiconductors | $19,738.60 |
| software_cybersecurity | $3,196.48 |
| _(ungrouped)_ | $50,055.98 |

## Turnover and Re-entry Diagnostics

| Metric | Value |
|--------|-------|
| Total trades | 44 |
| Trades / month | 8.12 |
| Avg holding period | 52.52 trading days |
| Stop-loss → re-entry ≤5d | 0 |

**Most-entered tickers:** `INTC`×2, `SEDG`×2, `MU`×1, `TSM`×1, `ASML`×1, `LRCX`×1, `MCHP`×1, `ON`×1

## Exposure and Benchmark Capture

| Metric | Value |
|--------|-------|
| Avg exposure | +89.48% |
| Max exposure | +97.61% |
| Avg cash (drag) | +10.52% |
| Correlation to SPY | 0.68 |
| Correlation to QQQ | 0.75 |
| Beta to SPY | 2.00 |
| Beta to QQQ | 1.53 |
| Up-capture vs QQQ | 1.94 |
| Down-capture vs QQQ | 1.52 |

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

**Baseline (as configured):** +72.99% return  |  -14.00% max drawdown  |  +76.47% win rate  |  4.71 profit factor

### Run-wide parameters

#### Max Total Exposure  (baseline: 90%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 50% | +42.42% | +31.63% | +16.87% | -11.73% | 24 | +66.67% | 6.63 |
| 70% | +45.81% | +35.01% | +20.25% | -12.90% | 31 | +63.64% | 5.71 |
| 90% ◀ baseline | +72.99% | +62.20% | +47.43% | -14.00% | 44 | +76.47% | 4.71 |
| 100% | +87.21% | +76.42% | +61.65% | -13.83% | 44 | +76.47% | 5.19 |

#### Max Position Size  (baseline: 8.50%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 4.25% | +61.86% | +51.07% | +36.30% | -15.80% | 82 | +48.39% | 2.58 |
| 8.50% ◀ baseline | +72.99% | +62.20% | +47.43% | -14.00% | 44 | +76.47% | 4.71 |
| 12.75% | +62.46% | +51.67% | +36.90% | -12.65% | 49 | +80.95% | 5.79 |
| 17.00% | +76.00% | +65.21% | +50.44% | -12.07% | 47 | +66.67% | 4.65 |
| 25.50% | +76.21% | +65.42% | +50.65% | -12.65% | 53 | +64.00% | 3.59 |

#### Max New Trades / Day  (baseline: 2)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 1 | +83.68% | +72.89% | +58.12% | -13.80% | 46 | +72.22% | 6.21 |
| 2 ◀ baseline | +72.99% | +62.20% | +47.43% | -14.00% | 44 | +76.47% | 4.71 |
| 3 | +72.62% | +61.83% | +47.06% | -14.60% | 51 | +70.00% | 5.33 |
| 5 | +66.50% | +55.71% | +40.94% | -14.65% | 54 | +54.55% | 2.58 |

#### Min Composite Score  (baseline: 0.70)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| none | +72.99% | +62.20% | +47.43% | -14.00% | 44 | +76.47% | 4.71 |
| 0.60 | +72.99% | +62.20% | +47.43% | -14.00% | 44 | +76.47% | 4.71 |
| 0.70 ◀ baseline | +72.99% | +62.20% | +47.43% | -14.00% | 44 | +76.47% | 4.71 |

#### Slippage  (baseline: 0.10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 0.05% | +75.32% | +64.53% | +49.77% | -13.41% | 46 | +72.22% | 3.92 |
| 0.10% ◀ baseline | +72.99% | +62.20% | +47.43% | -14.00% | 44 | +76.47% | 4.71 |
| 0.20% | +72.42% | +61.63% | +46.86% | -13.97% | 44 | +76.47% | 4.63 |
| 0.50% | +70.87% | +60.08% | +45.32% | -14.06% | 44 | +76.47% | 4.46 |

#### Re-entry Recovery Gate  (baseline: 10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +72.99% | +62.20% | +47.43% | -14.00% | 44 | +76.47% | 4.71 |
| 0% | +72.99% | +62.20% | +47.43% | -14.00% | 44 | +76.47% | 4.71 |
| 5% | +72.99% | +62.20% | +47.43% | -14.00% | 44 | +76.47% | 4.71 |
| 10% ◀ baseline | +72.99% | +62.20% | +47.43% | -14.00% | 44 | +76.47% | 4.71 |

#### Stop-loss only if score <  (baseline: 0.90)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +72.99% | +62.20% | +47.43% | -14.00% | 44 | +76.47% | 4.71 |
| 0.85 | +72.99% | +62.20% | +47.43% | -14.00% | 44 | +76.47% | 4.71 |
| 0.90 ◀ baseline | +72.99% | +62.20% | +47.43% | -14.00% | 44 | +76.47% | 4.71 |
| 0.95 | +72.99% | +62.20% | +47.43% | -14.00% | 44 | +76.47% | 4.71 |

#### Max-hold only if score <  (baseline: 0.80)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +83.34% | +72.55% | +57.78% | -13.89% | 43 | +81.25% | 8.66 |
| 0.70 | +72.41% | +61.62% | +46.85% | -13.98% | 44 | +76.47% | 4.64 |
| 0.80 ◀ baseline | +72.99% | +62.20% | +47.43% | -14.00% | 44 | +76.47% | 4.71 |
| 0.90 | +73.81% | +63.01% | +48.25% | -14.04% | 44 | +76.47% | 4.94 |

#### Score-decay sell threshold  (baseline: off)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off ◀ baseline | +72.99% | +62.20% | +47.43% | -14.00% | 44 | +76.47% | 4.71 |
| 0.40 | +79.53% | +68.74% | +53.97% | -14.22% | 56 | +69.57% | 3.71 |
| 0.50 | +60.32% | +49.53% | +34.77% | -15.28% | 94 | +45.24% | 2.48 |
| 0.60 | +70.13% | +59.34% | +44.58% | -13.02% | 123 | +47.37% | 2.87 |

#### Persistence-buy threshold  (baseline: 0.90)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +57.37% | +46.58% | +31.81% | -15.99% | 41 | +60.00% | 4.44 |
| 0.80 | +72.09% | +61.29% | +46.53% | -16.40% | 122 | +51.79% | 2.72 |
| 0.85 | +65.23% | +54.43% | +39.67% | -14.93% | 84 | +62.16% | 3.18 |
| 0.90 ◀ baseline | +72.99% | +62.20% | +47.43% | -14.00% | 44 | +76.47% | 4.71 |

#### Signal Weight Profile  (baseline: baseline)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| baseline ◀ baseline | +72.99% | +62.20% | +47.43% | -14.00% | 44 | +76.47% | 4.71 |
| no_1d | +75.51% | +64.72% | +49.95% | -15.10% | 68 | +68.97% | 4.33 |
| less_1d | +72.99% | +62.20% | +47.43% | -14.00% | 44 | +76.47% | 4.71 |
| more_volume | +83.22% | +72.42% | +57.66% | -15.62% | 41 | +60.00% | 4.48 |

### Best 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | max_total_exposure | 100% | +87.21% | +61.65% | -13.83% | 5.19 |
| 2 | max_new_trades_per_day | 1 | +83.68% | +58.12% | -13.80% | 6.21 |
| 3 | max_hold_score_max | off | +83.34% | +57.78% | -13.89% | 8.66 |
| 4 | signal_weights | more_volume | +83.22% | +57.66% | -15.62% | 4.48 |
| 5 | score_exit_below | 0.40 | +79.53% | +53.97% | -14.22% | 3.71 |

### Worst 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | max_total_exposure | 50% | +42.42% | +16.87% | -11.73% | 6.63 |
| 2 | max_total_exposure | 70% | +45.81% | +20.25% | -12.90% | 5.71 |
| 3 | score_entry_above | off | +57.37% | +31.81% | -15.99% | 4.44 |
| 4 | score_exit_below | 0.50 | +60.32% | +34.77% | -15.28% | 2.48 |
| 5 | max_position_pct | 4.25% | +61.86% | +36.30% | -15.80% | 2.58 |

### Robustness Notes

The baseline outperforms 77% of all variants. This is broadly consistent across parameter dimensions, suggesting the baseline settings are reasonably competitive in-sample.

The widest in-sample return spread belongs to `max_total_exposure` (44.8 pp range across its variants); `min_composite_score` shows the narrowest spread (0.0 pp), suggesting the strategy is least sensitive to that parameter in this period.

Improvements that appear in only one or two variants should be treated with skepticism — isolated peaks are more likely to reflect in-sample noise than genuine edge. Prefer settings that perform consistently across the full sweep.
