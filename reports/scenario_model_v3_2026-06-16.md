# Scenario — model_v3

model_v2's 83-name universe and uniform exit rule, plus score-conditional exits: stop-loss only below a 0.90 composite score, and max-hold suppressed until the score falls below 0.80 — so still-strong names are given room to run.

**Universe (83):** CRWD, ORCL, COIN, NFLX, PANW, GOOGL, BAC, MSFT, AVGO, AMZN, COST, ASML, AAPL, JPM, TSM, GS, META, TSLA, MU, AMD, NVDA, LLY, VST, AXON, GE, PLTR, OXY, INTC, BA, PFE, PYPL, SEDG, PLUG, ADBE, CRM, NOW, INTU, SAP, WDAY, SNOW, DDOG, NET, MDB, ZS, FTNT, TEAM, OKTA, TWLO, HUBS, SNPS, CDNS, QCOM, TXN, AMAT, LRCX, KLAC, NXPI, MRVL, ADI, MCHP, ON, ARM, ANET, CSCO, IBM, DELL, SMCI, VRT, APP, SHOP, UBER, ABNB, MELI, SE, SPOT, DASH, RBLX, PINS, SNAP, TTD, NU, HOOD, SOFI

---

# AI Paper Trader — Backtest Report
**Period:** 2026-01-01 → 2026-06-16  |  **Generated:** 2026-06-16

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Ending Balance | $170,188.27 | $110,550.40 | $120,003.70 | $123,564.80 |
| Total Return | +70.19% | +10.55% | +20.00% | +23.56% |
| Max Drawdown | -14.00% | -8.88% | -11.72% | -16.42% |
| Excess vs SPY | +59.64% | — | — | — |
| Excess vs QQQ | +50.18% | — | — | — |
| Excess vs Equal-Wt | +46.62% | — | — | — |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $170,188.27 |
| **IRR (annualized, money-weighted)** | **+272.57%** |
| Total Return (on full $ portfolio) | +70.19% |
| Total Capital Deployed (all entries) | $285,245.12 |
| Avg Capital Deployed (snapshot) | $108,909.01 (+108.91% of portfolio) |
| Peak Capital Deployed (snapshot) | $165,287.14 (+165.29% of portfolio) |
| Time Invested | +99.12% of trading days |
| Trading Days | 114 |
| Total Trades | 46 (28 buys, 18 sells) |
| Win Rate | +77.78% |
| Average Win | $2,675.02 |
| Average Loss | $-1,940.22 |
| Profit Factor | 4.83 |
| Avg Holding Period | 50.7 approx. trading days |
| Largest Winner | $10,701.71 |
| Largest Loser | $-3,292.49 |
| Open Positions at End | 10 |
| Total Slippage Cost | $480.91 (+0.48% of start) |
| Avg Slippage / Trade | $10.45 |

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
| 2026-06-15 | SELL | SEDG | 192 | $60.13 | $11,544.92 | rotation_funded | $930.16 | 20.0 |
| 2026-06-16 | BUY | KLAC | 57 | $244.47 | $13,934.74 | momentum_score=0.9307 | — | — |

## Open Positions at End of Period

| Ticker | Shares | Entry Price | Final Price | Unrealized P&L | Entry Date |
|--------|--------|------------|------------|----------------|------------|
| DELL | 62 | $153.23 | $408.57 | $15,831.12 | 2026-03-02 |
| MRVL | 75 | $131.43 | $292.57 | $12,085.78 | 2026-04-13 |
| ARM | 46 | $216.10 | $402.38 | $8,569.06 | 2026-04-27 |
| DDOG | 60 | $200.14 | $234.38 | $2,054.41 | 2026-05-12 |
| PANW | 48 | $247.80 | $279.70 | $1,531.32 | 2026-05-18 |
| CRWD | 19 | $617.50 | $682.30 | $1,231.35 | 2026-05-19 |
| FTNT | 92 | $130.13 | $145.87 | $1,448.08 | 2026-05-20 |
| SNOW | 54 | $261.40 | $239.34 | $-1,191.30 | 2026-06-02 |
| OKTA | 114 | $124.77 | $115.59 | $-1,047.06 | 2026-06-03 |
| KLAC | 57 | $244.47 | $244.22 | $-13.92 | 2026-06-16 |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2026-01-02 | $100,000.00 | — | +0.00% | +0.00% | +0.00% | +0.00% |
| 2026-01-05 | $99,983.56 | -0.02% | -0.02% | +0.67% | +0.79% | +1.66% |
| 2026-01-06 | $100,914.16 | +0.93% | +0.91% | +1.26% | +1.68% | +3.20% |
| 2026-01-07 | $100,321.38 | -0.59% | +0.32% | +0.94% | +1.78% | +2.89% |
| 2026-01-08 | $99,482.07 | -0.84% | -0.52% | +0.93% | +1.20% | +1.38% |
| 2026-06-10 | $156,818.50 | -2.22% | +56.82% | +6.48% | +13.28% | +15.99% |
| 2026-06-11 | $165,518.17 | +5.55% | +65.52% | +8.29% | +17.11% | +20.62% |
| 2026-06-12 | $167,068.91 | +0.94% | +67.07% | +8.87% | +17.80% | +21.55% |
| 2026-06-15 | $172,979.52 | +3.54% | +72.98% | — | +21.50% | +25.56% |
| 2026-06-16 | $170,188.27 | -1.61% | +70.19% | +10.55% | +20.00% | +23.56% |


## Signal Predictiveness

_Cross-section of 9,379 (date, ticker) signal observations. Correlations are Pearson vs forward returns._

| Signal | vs fwd 5d | vs fwd 10d | vs fwd 20d |
|--------|-----------|------------|------------|
| return_1d | 0.01 | 0.00 | 0.04 |
| return_5d | -0.01 | 0.05 | 0.10 |
| return_20d | 0.06 | 0.11 | 0.18 |
| vol_ratio | 0.00 | -0.02 | 0.01 |
| vol_adj_mom_20d | 0.07 | 0.11 | 0.15 |
| composite_score | 0.05 | 0.08 | 0.11 |

**Forward returns by composite-score quintile** (5 = highest-ranked):

| Quintile | N | Avg fwd 5d | Win 5d | Avg fwd 10d | Win 10d | Avg fwd 20d | Win 20d |
|----------|---|-----------|--------|-------------|---------|-------------|---------|
| Q1 | 1921 | +0.50% | +49.22% | +0.80% | +48.36% | +2.38% | +51.63% |
| Q2 | 1808 | +0.57% | +51.38% | +0.82% | +50.54% | +1.72% | +50.47% |
| Q3 | 1921 | +0.07% | +47.81% | +0.65% | +47.17% | +1.80% | +46.62% |
| Q4 | 1808 | +0.46% | +48.91% | +1.72% | +49.52% | +4.25% | +51.86% |
| Q5 | 1921 | +1.70% | +54.13% | +3.48% | +55.54% | +7.52% | +56.07% |

**Top-minus-bottom quintile spread:** 5d +1.20%  |  10d +2.68%  |  20d +5.14%  (positive ⇒ higher-ranked names outperform lower-ranked names).

## Entry vs Exit Attribution

_Buy the top 2 ranked names each day, hold a fixed period, **no** stop-loss / take-profit / max-holding. Next-day entry, slippage applied._

| Hold period | Raw avg return / trade | Raw win rate | N trades |
|-------------|------------------------|--------------|----------|
| 5d | +2.30% | +56.02% | 216 |
| 10d | +4.70% | +60.19% | 206 |
| 20d | +12.29% | +63.44% | 186 |
| 30d | +18.16% | +65.66% | 166 |

**Full strategy (with exit rules):** total return +70.19%, win rate +77.78%, avg hold 50.72 trading days.

The raw signal (buy top names, hold fixed, no stops) is **positive across holding periods** (avg +9.36% per trade, 61% win rate). That points to genuine signal quality — higher-ranked names tend to rise even without exit rules.

## P&L Attribution

**Top 5 contributors:**

| Ticker | P&L |
|--------|-----|
| DELL | $15,831.12 |
| MRVL | $12,085.78 |
| MU | $10,701.71 |
| ARM | $8,569.06 |
| ON | $7,044.21 |

**Worst 5 contributors:**

| Ticker | P&L |
|--------|-----|
| ZS | $-3,292.49 |
| SNPS | $-1,540.54 |
| TXN | $-1,359.70 |
| SNOW | $-1,191.30 |
| OKTA | $-1,047.06 |

**P&L by asset group:**

| Group | P&L |
|-------|-----|
| semiconductors | $19,270.77 |
| software_cybersecurity | $2,762.67 |
| _(ungrouped)_ | $48,154.80 |

## Turnover and Re-entry Diagnostics

| Metric | Value |
|--------|-------|
| Total trades | 46 |
| Trades / month | 8.44 |
| Avg holding period | 50.72 trading days |
| Stop-loss → re-entry ≤5d | 0 |

**Most-entered tickers:** `INTC`×2, `KLAC`×2, `SEDG`×2, `MU`×1, `TSM`×1, `ASML`×1, `LRCX`×1, `MCHP`×1

## Exposure and Benchmark Capture

| Metric | Value |
|--------|-------|
| Avg exposure | +89.46% |
| Max exposure | +97.61% |
| Avg cash (drag) | +10.54% |
| Correlation to SPY | 0.67 |
| Correlation to QQQ | 0.75 |
| Beta to SPY | 2.01 |
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

**Baseline (as configured):** +70.19% return  |  -14.00% max drawdown  |  +77.78% win rate  |  4.83 profit factor

### Run-wide parameters

#### Max Total Exposure  (baseline: 90%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 50% | +40.87% | +30.32% | +17.30% | -11.73% | 24 | +66.67% | 6.63 |
| 70% | +43.84% | +33.29% | +20.27% | -12.90% | 31 | +63.64% | 5.71 |
| 90% ◀ baseline | +70.19% | +59.64% | +46.62% | -14.00% | 46 | +77.78% | 4.83 |
| 100% | +83.66% | +73.11% | +60.10% | -13.83% | 46 | +77.78% | 5.51 |

#### Max Position Size  (baseline: 8.50%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 4.25% | +58.86% | +48.31% | +35.29% | -15.80% | 82 | +48.39% | 2.58 |
| 8.50% ◀ baseline | +70.19% | +59.64% | +46.62% | -14.00% | 46 | +77.78% | 4.83 |
| 12.75% | +60.18% | +49.63% | +36.61% | -12.65% | 51 | +77.27% | 5.27 |
| 17.00% | +73.40% | +62.85% | +49.84% | -12.07% | 49 | +63.64% | 4.27 |
| 25.50% | +72.52% | +61.97% | +48.96% | -12.65% | 53 | +64.00% | 3.59 |

#### Max New Trades / Day  (baseline: 2)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 1 | +81.00% | +70.45% | +57.44% | -13.80% | 48 | +73.68% | 6.31 |
| 2 ◀ baseline | +70.19% | +59.64% | +46.62% | -14.00% | 46 | +77.78% | 4.83 |
| 3 | +68.65% | +58.10% | +45.09% | -14.60% | 51 | +70.00% | 5.33 |
| 5 | +62.32% | +51.77% | +38.76% | -14.65% | 54 | +54.55% | 2.58 |

#### Min Composite Score  (baseline: 0.70)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| none | +70.19% | +59.64% | +46.62% | -14.00% | 46 | +77.78% | 4.83 |
| 0.60 | +70.19% | +59.64% | +46.62% | -14.00% | 46 | +77.78% | 4.83 |
| 0.70 ◀ baseline | +70.19% | +59.64% | +46.62% | -14.00% | 46 | +77.78% | 4.83 |

#### Slippage  (baseline: 0.10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 0.05% | +72.07% | +61.52% | +48.51% | -13.41% | 48 | +73.68% | 4.16 |
| 0.10% ◀ baseline | +70.19% | +59.64% | +46.62% | -14.00% | 46 | +77.78% | 4.83 |
| 0.20% | +69.60% | +59.05% | +46.04% | -13.97% | 46 | +77.78% | 4.74 |
| 0.50% | +68.00% | +57.45% | +44.44% | -14.06% | 46 | +77.78% | 4.56 |

#### Re-entry Recovery Gate  (baseline: 10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +70.19% | +59.64% | +46.62% | -14.00% | 46 | +77.78% | 4.83 |
| 0% | +70.19% | +59.64% | +46.62% | -14.00% | 46 | +77.78% | 4.83 |
| 5% | +70.19% | +59.64% | +46.62% | -14.00% | 46 | +77.78% | 4.83 |
| 10% ◀ baseline | +70.19% | +59.64% | +46.62% | -14.00% | 46 | +77.78% | 4.83 |

#### Stop-loss only if score <  (baseline: 0.90)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +70.19% | +59.64% | +46.62% | -14.00% | 46 | +77.78% | 4.83 |
| 0.85 | +70.19% | +59.64% | +46.62% | -14.00% | 46 | +77.78% | 4.83 |
| 0.90 ◀ baseline | +70.19% | +59.64% | +46.62% | -14.00% | 46 | +77.78% | 4.83 |
| 0.95 | +70.19% | +59.64% | +46.62% | -14.00% | 46 | +77.78% | 4.83 |

#### Max-hold only if score <  (baseline: 0.80)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +79.99% | +69.44% | +56.42% | -13.89% | 44 | +82.35% | 8.84 |
| 0.70 | +69.62% | +59.07% | +46.05% | -13.98% | 46 | +77.78% | 4.76 |
| 0.80 ◀ baseline | +70.19% | +59.64% | +46.62% | -14.00% | 46 | +77.78% | 4.83 |
| 0.90 | +71.27% | +60.72% | +47.71% | -14.04% | 46 | +77.78% | 5.06 |

#### Score-decay sell threshold  (baseline: off)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off ◀ baseline | +70.19% | +59.64% | +46.62% | -14.00% | 46 | +77.78% | 4.83 |
| 0.40 | +75.92% | +65.37% | +52.35% | -14.22% | 58 | +70.83% | 4.21 |
| 0.50 | +55.74% | +45.19% | +32.17% | -15.28% | 94 | +45.24% | 2.48 |
| 0.60 | +65.00% | +54.45% | +41.44% | -13.02% | 124 | +47.37% | 2.87 |

#### Persistence-buy threshold  (baseline: 0.90)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +55.05% | +44.50% | +31.48% | -15.99% | 41 | +60.00% | 4.44 |
| 0.80 | +68.01% | +57.46% | +44.45% | -16.40% | 124 | +52.63% | 2.92 |
| 0.85 | +60.98% | +50.43% | +37.41% | -14.93% | 86 | +60.53% | 3.01 |
| 0.90 ◀ baseline | +70.19% | +59.64% | +46.62% | -14.00% | 46 | +77.78% | 4.83 |

#### Signal Weight Profile  (baseline: baseline)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| baseline ◀ baseline | +70.19% | +59.64% | +46.62% | -14.00% | 46 | +77.78% | 4.83 |
| no_1d | +71.92% | +61.37% | +48.35% | -15.10% | 70 | +70.00% | 4.45 |
| less_1d | +70.19% | +59.64% | +46.62% | -14.00% | 46 | +77.78% | 4.83 |
| more_volume | +79.50% | +68.95% | +55.94% | -15.62% | 41 | +60.00% | 4.48 |

### Best 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | max_total_exposure | 100% | +83.66% | +60.10% | -13.83% | 5.51 |
| 2 | max_new_trades_per_day | 1 | +81.00% | +57.44% | -13.80% | 6.31 |
| 3 | max_hold_score_max | off | +79.99% | +56.42% | -13.89% | 8.84 |
| 4 | signal_weights | more_volume | +79.50% | +55.94% | -15.62% | 4.48 |
| 5 | score_exit_below | 0.40 | +75.92% | +52.35% | -14.22% | 4.21 |

### Worst 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | max_total_exposure | 50% | +40.87% | +17.30% | -11.73% | 6.63 |
| 2 | max_total_exposure | 70% | +43.84% | +20.27% | -12.90% | 5.71 |
| 3 | score_entry_above | off | +55.05% | +31.48% | -15.99% | 4.44 |
| 4 | score_exit_below | 0.50 | +55.74% | +32.17% | -15.28% | 2.48 |
| 5 | max_position_pct | 4.25% | +58.86% | +35.29% | -15.80% | 2.58 |

### Robustness Notes

The baseline outperforms 77% of all variants. This is broadly consistent across parameter dimensions, suggesting the baseline settings are reasonably competitive in-sample.

The widest in-sample return spread belongs to `max_total_exposure` (42.8 pp range across its variants); `min_composite_score` shows the narrowest spread (0.0 pp), suggesting the strategy is least sensitive to that parameter in this period.

Improvements that appear in only one or two variants should be treated with skepticism — isolated peaks are more likely to reflect in-sample noise than genuine edge. Prefer settings that perform consistently across the full sweep.
