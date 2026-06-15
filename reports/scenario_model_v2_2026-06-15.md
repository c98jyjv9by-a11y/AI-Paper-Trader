# Scenario — model_v2

Full 21-name universe with one uniform exit rule applied to every ticker (stop 15%, no take-profit, no trailing stop, 60-day max hold) plus the trough-based anti-falling-knife re-entry gate. Composite ranking drives entries.

**Universe (83):** CRWD, ORCL, COIN, NFLX, PANW, GOOGL, BAC, MSFT, AVGO, AMZN, COST, ASML, AAPL, JPM, TSM, GS, META, TSLA, MU, AMD, NVDA, LLY, VST, AXON, GE, PLTR, OXY, INTC, BA, PFE, PYPL, SEDG, PLUG, ADBE, CRM, NOW, INTU, SAP, WDAY, SNOW, DDOG, NET, MDB, ZS, FTNT, TEAM, OKTA, TWLO, HUBS, SNPS, CDNS, QCOM, TXN, AMAT, LRCX, KLAC, NXPI, MRVL, ADI, MCHP, ON, ARM, ANET, CSCO, IBM, DELL, SMCI, VRT, APP, SHOP, UBER, ABNB, MELI, SE, SPOT, DASH, RBLX, PINS, SNAP, TTD, NU, HOOD, SOFI

---

# AI Paper Trader — Backtest Report
**Period:** 2023-01-01 → 2026-06-15  |  **Generated:** 2026-06-15

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Ending Balance | $518,681.78 | $206,761.90 | $286,739.70 | $466,019.60 |
| Total Return | +418.68% | +106.76% | +186.74% | +366.02% |
| Max Drawdown | -32.39% | -18.76% | -22.77% | -35.32% |
| Excess vs SPY | +311.92% | — | — | — |
| Excess vs QQQ | +231.94% | — | — | — |
| Excess vs Equal-Wt | +52.66% | — | — | — |
| 1-Year Return | +114.37% | +27.89% | +41.87% | +40.46% |
| 2-Year Return | +163.09% | +44.00% | +60.71% | +107.47% |
| 3-Year Return | +274.42% | +82.46% | +113.60% | +229.20% |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $518,681.78 |
| **IRR (annualized, money-weighted)** | **+66.06%** |
| Total Return (on full $ portfolio) | +418.68% |
| Total Capital Deployed (all entries) | $2,431,955.69 |
| Avg Capital Deployed (snapshot) | $202,102.80 (+202.10% of portfolio) |
| Peak Capital Deployed (snapshot) | $506,075.70 (+506.08% of portfolio) |
| Time Invested | +99.88% of trading days |
| Trading Days | 865 |
| Total Trades | 268 (139 buys, 129 sells) |
| Win Rate | +56.59% |
| Average Win | $5,007.96 |
| Average Loss | $-2,966.99 |
| Profit Factor | 2.20 |
| Avg Holding Period | 70.7 approx. trading days |
| Largest Winner | $23,846.08 |
| Largest Loser | $-5,454.30 |
| Open Positions at End | 10 |
| Total Slippage Cost | $4,776.43 (+4.78% of start) |
| Avg Slippage / Trade | $17.82 |

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
| Slippage | 0.10% per fill |

## Ticker Universe

`CRWD`, `ORCL`, `COIN`, `NFLX`, `PANW`, `GOOGL`, `BAC`, `MSFT`, `AVGO`, `AMZN`, `COST`, `ASML`, `AAPL`, `JPM`, `TSM`, `GS`, `META`, `TSLA`, `MU`, `AMD`, `NVDA`, `LLY`, `VST`, `AXON`, `GE`, `PLTR`, `OXY`, `INTC`, `BA`, `PFE`, `PYPL`, `SEDG`, `PLUG`, `ADBE`, `CRM`, `NOW`, `INTU`, `SAP`, `WDAY`, `SNOW`, `DDOG`, `NET`, `MDB`, `ZS`, `FTNT`, `TEAM`, `OKTA`, `TWLO`, `HUBS`, `SNPS`, `CDNS`, `QCOM`, `TXN`, `AMAT`, `LRCX`, `KLAC`, `NXPI`, `MRVL`, `ADI`, `MCHP`, `ON`, `ARM`, `ANET`, `CSCO`, `IBM`, `DELL`, `SMCI`, `VRT`, `APP`, `SHOP`, `UBER`, `ABNB`, `MELI`, `SE`, `SPOT`, `DASH`, `RBLX`, `PINS`, `SNAP`, `TTD`, `NU`, `HOOD`, `SOFI`

## Trade Log (last 20 trades)

| Date | Action | Ticker | Shares | Price | Value | Reason | P&L | Hold Days |
|------|--------|--------|--------|-------|-------|--------|-----|-----------|
| 2026-03-12 | SELL | TXN | 115 | $188.90 | $21,723.51 | stop_loss | $-4,070.48 | 26.4 |
| 2026-03-13 | BUY | PLTR | 154 | $151.10 | $23,269.54 | momentum_score=0.8542 | — | — |
| 2026-03-24 | SELL | CSCO | 309 | $80.34 | $24,826.23 | max_holding_period | $1,150.65 | 90.0 |
| 2026-03-25 | BUY | DELL | 141 | $183.63 | $25,891.24 | momentum_score=0.9928 | — | — |
| 2026-03-25 | SELL | GOOGL | 82 | $290.47 | $23,818.17 | max_holding_period | $-169.32 | 90.0 |
| 2026-03-26 | BUY | ARM | 160 | $154.95 | $24,792.77 | momentum_score=0.9717 | — | — |
| 2026-03-26 | SELL | META | 37 | $546.99 | $20,238.72 | stop_loss | $-4,139.27 | 69.3 |
| 2026-03-27 | BUY | MRVL | 251 | $94.93 | $23,826.78 | momentum_score=0.9181 | — | — |
| 2026-03-27 | SELL | NVDA | 125 | $167.16 | $20,894.71 | max_holding_period | $-1,459.14 | 90.0 |
| 2026-03-30 | BUY | AMD | 120 | $196.24 | $23,548.32 | momentum_score=0.7898 | — | — |
| 2026-04-10 | SELL | PLTR | 154 | $127.93 | $19,701.51 | stop_loss | $-3,568.03 | 20.0 |
| 2026-04-13 | BUY | INTC | 411 | $65.25 | $26,815.78 | momentum_score=0.9036 | — | — |
| 2026-04-17 | SELL | GS | 29 | $920.97 | $26,707.99 | max_holding_period | $1,178.86 | 90.0 |
| 2026-04-20 | BUY | ON | 321 | $85.65 | $27,492.24 | momentum_score=0.959 | — | — |
| 2026-04-27 | SELL | LRCX | 146 | $259.21 | $37,844.73 | max_holding_period | $12,261.84 | 90.0 |
| 2026-04-28 | BUY | TXN | 112 | $263.92 | $29,559.49 | momentum_score=0.8855 | — | — |
| 2026-05-19 | SELL | SEDG | 732 | $54.48 | $39,876.07 | max_holding_period | $14,736.04 | 90.0 |
| 2026-05-20 | BUY | CRWD | 55 | $650.76 | $35,791.81 | momentum_score=0.9175 | — | — |
| 2026-06-10 | SELL | ADI | 81 | $392.28 | $31,774.46 | max_holding_period | $5,944.71 | 90.0 |
| 2026-06-11 | BUY | KLAC | 179 | $241.41 | $43,211.53 | momentum_score=0.8843 | — | — |

## Open Positions at End of Period

| Ticker | Shares | Entry Price | Final Price | Unrealized P&L | Entry Date |
|--------|--------|------------|------------|----------------|------------|
| OXY | 498 | $51.99 | $54.46 | $1,227.92 | 2026-02-23 |
| DELL | 141 | $183.63 | $409.07 | $31,787.63 | 2026-03-25 |
| ARM | 160 | $154.95 | $412.55 | $41,215.23 | 2026-03-26 |
| MRVL | 251 | $94.93 | $308.88 | $53,702.10 | 2026-03-27 |
| AMD | 120 | $196.24 | $547.26 | $42,122.88 | 2026-03-30 |
| INTC | 411 | $65.25 | $127.86 | $25,734.68 | 2026-04-13 |
| ON | 321 | $85.65 | $125.90 | $12,921.66 | 2026-04-20 |
| TXN | 112 | $263.92 | $313.34 | $5,534.59 | 2026-04-28 |
| CRWD | 55 | $650.76 | $692.91 | $2,318.24 | 2026-05-20 |
| KLAC | 179 | $241.41 | $256.42 | $2,687.65 | 2026-06-11 |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2023-01-03 | $100,000.00 | — | +0.00% | +0.00% | +0.00% | +0.00% |
| 2023-01-04 | $99,982.46 | -0.02% | -0.02% | +0.77% | +0.48% | +1.73% |
| 2023-01-05 | $99,480.93 | -0.50% | -0.52% | -0.38% | -1.10% | -0.89% |
| 2023-01-06 | $99,536.18 | +0.06% | -0.46% | +1.91% | +1.63% | +1.45% |
| 2023-01-09 | $99,847.65 | +0.31% | -0.15% | +1.85% | +2.29% | +3.37% |
| 2026-06-09 | $464,416.28 | -3.54% | +364.42% | +101.89% | +172.80% | +344.03% |
| 2026-06-10 | $449,845.16 | -3.14% | +349.85% | +98.71% | +167.35% | +330.54% |
| 2026-06-11 | $479,025.03 | +6.49% | +379.02% | +102.09% | +176.38% | +345.37% |
| 2026-06-12 | $494,591.03 | +3.25% | +394.59% | +103.18% | +178.01% | +348.40% |
| 2026-06-15 | $518,681.78 | +4.87% | +418.68% | +106.76% | +186.74% | +366.02% |


## Signal Predictiveness

_Cross-section of 71,517 (date, ticker) signal observations. Correlations are Pearson vs forward returns._

| Signal | vs fwd 5d | vs fwd 10d | vs fwd 20d |
|--------|-----------|------------|------------|
| return_1d | -0.01 | -0.00 | -0.00 |
| return_5d | -0.01 | 0.01 | 0.01 |
| return_20d | -0.00 | 0.01 | 0.02 |
| vol_ratio | 0.00 | 0.02 | 0.02 |
| vol_adj_mom_20d | -0.00 | 0.00 | 0.01 |
| composite_score | 0.00 | 0.01 | 0.02 |

**Forward returns by composite-score quintile** (5 = highest-ranked):

| Quintile | N | Avg fwd 5d | Win 5d | Avg fwd 10d | Win 10d | Avg fwd 20d | Win 20d |
|----------|---|-----------|--------|-------------|---------|-------------|---------|
| Q1 | 14688 | +0.86% | +54.41% | +1.64% | +55.93% | +3.21% | +57.22% |
| Q2 | 13824 | +0.82% | +55.20% | +1.50% | +56.73% | +2.80% | +58.03% |
| Q3 | 14493 | +0.76% | +54.88% | +1.49% | +56.14% | +2.89% | +57.45% |
| Q4 | 13824 | +0.70% | +54.12% | +1.56% | +56.12% | +3.12% | +57.86% |
| Q5 | 14688 | +0.92% | +55.13% | +1.91% | +56.49% | +3.86% | +58.21% |

**Top-minus-bottom quintile spread:** 5d +0.06%  |  10d +0.27%  |  20d +0.65%  (positive ⇒ higher-ranked names outperform lower-ranked names).

## Entry vs Exit Attribution

_Buy the top 2 ranked names each day, hold a fixed period, **no** stop-loss / take-profit / max-holding. Next-day entry, slippage applied._

| Hold period | Raw avg return / trade | Raw win rate | N trades |
|-------------|------------------------|--------------|----------|
| 5d | +0.99% | +53.90% | 1718 |
| 10d | +2.14% | +55.21% | 1708 |
| 20d | +4.41% | +56.58% | 1688 |
| 30d | +7.11% | +58.33% | 1668 |

**Full strategy (with exit rules):** total return +418.68%, win rate +56.59%, avg hold 70.70 trading days.

The raw signal (buy top names, hold fixed, no stops) is **positive across holding periods** (avg +3.66% per trade, 56% win rate). That points to genuine signal quality — higher-ranked names tend to rise even without exit rules.

## P&L Attribution

**Top 5 contributors:**

| Ticker | P&L |
|--------|-----|
| MRVL | $51,967.49 |
| ARM | $39,787.27 |
| PLTR | $38,622.52 |
| INTC | $36,652.31 |
| AMD | $30,702.18 |

**Worst 5 contributors:**

| Ticker | P&L |
|--------|-----|
| OKTA | $-11,056.14 |
| TSLA | $-10,904.44 |
| SOFI | $-4,944.95 |
| BA | $-4,289.68 |
| NXPI | $-4,184.99 |

**P&L by asset group:**

| Group | P&L |
|-------|-----|
| semiconductors | $93,530.52 |
| financial_crypto_beta | $19,449.64 |
| software_cybersecurity | $19,157.83 |
| mega_cap_growth | $16,381.20 |
| _(ungrouped)_ | $270,162.60 |

## Turnover and Re-entry Diagnostics

| Metric | Value |
|--------|-------|
| Total trades | 268 |
| Trades / month | 6.47 |
| Avg holding period | 70.70 trading days |
| Stop-loss → re-entry ≤5d | 0 |

**Most-entered tickers:** `PLTR`×6, `AMD`×6, `APP`×4, `NU`×4, `SMCI`×4, `TSLA`×4, `SPOT`×4, `HOOD`×4

## Exposure and Benchmark Capture

| Metric | Value |
|--------|-------|
| Avg exposure | +93.44% |
| Max exposure | +98.44% |
| Avg cash (drag) | +6.56% |
| Correlation to SPY | 0.74 |
| Correlation to QQQ | 0.80 |
| Beta to SPY | 1.49 |
| Beta to QQQ | 1.23 |
| Up-capture vs QQQ | 1.38 |
| Down-capture vs QQQ | 1.30 |

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

**Baseline (as configured):** +418.68% return  |  -32.39% max drawdown  |  +56.59% win rate  |  2.20 profit factor

### Run-wide parameters

#### Max Total Exposure  (baseline: 90%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 50% | +185.78% | +79.02% | -180.24% | -17.91% | 158 | +53.25% | 2.35 |
| 70% | +189.90% | +83.14% | -176.12% | -26.66% | 212 | +52.94% | 1.83 |
| 90% ◀ baseline | +418.68% | +311.92% | +52.66% | -32.39% | 268 | +56.59% | 2.20 |
| 100% | +346.54% | +239.78% | -19.48% | -32.88% | 277 | +55.64% | 2.22 |

#### Max Position Size  (baseline: 8.50%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 4.25% | +267.09% | +160.33% | -98.93% | -34.50% | 537 | +52.71% | 2.01 |
| 8.50% ◀ baseline | +418.68% | +311.92% | +52.66% | -32.39% | 268 | +56.59% | 2.20 |
| 12.75% | +272.34% | +165.58% | -93.68% | -37.00% | 173 | +54.22% | 1.83 |
| 17.00% | +177.45% | +70.69% | -188.57% | -26.84% | 137 | +48.48% | 1.60 |
| 25.50% | +110.98% | +4.22% | -255.04% | -32.00% | 83 | +45.00% | 1.58 |

#### Max New Trades / Day  (baseline: 2)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 1 | +374.51% | +267.75% | +8.49% | -33.73% | 282 | +54.41% | 2.00 |
| 2 ◀ baseline | +418.68% | +311.92% | +52.66% | -32.39% | 268 | +56.59% | 2.20 |
| 3 | +345.00% | +238.24% | -21.02% | -32.28% | 276 | +57.14% | 2.03 |
| 5 | +395.24% | +288.48% | +29.22% | -32.05% | 282 | +52.21% | 1.95 |

#### Min Composite Score  (baseline: 0.70)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| none | +418.68% | +311.92% | +52.66% | -32.39% | 268 | +56.59% | 2.20 |
| 0.60 | +418.68% | +311.92% | +52.66% | -32.39% | 268 | +56.59% | 2.20 |
| 0.70 ◀ baseline | +418.68% | +311.92% | +52.66% | -32.39% | 268 | +56.59% | 2.20 |

#### Slippage  (baseline: 0.10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 0.05% | +417.97% | +311.21% | +51.95% | -32.26% | 270 | +56.15% | 2.16 |
| 0.10% ◀ baseline | +418.68% | +311.92% | +52.66% | -32.39% | 268 | +56.59% | 2.20 |
| 0.20% | +352.08% | +245.31% | -13.94% | -32.02% | 272 | +56.49% | 1.93 |
| 0.50% | +299.94% | +193.18% | -66.08% | -34.98% | 279 | +53.73% | 2.12 |

#### Re-entry Recovery Gate  (baseline: 10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +418.68% | +311.92% | +52.66% | -32.39% | 268 | +56.59% | 2.20 |
| 0% | +418.68% | +311.92% | +52.66% | -32.39% | 268 | +56.59% | 2.20 |
| 5% | +418.68% | +311.92% | +52.66% | -32.39% | 268 | +56.59% | 2.20 |
| 10% ◀ baseline | +418.68% | +311.92% | +52.66% | -32.39% | 268 | +56.59% | 2.20 |

#### Signal Weight Profile  (baseline: baseline)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| baseline ◀ baseline | +418.68% | +311.92% | +52.66% | -32.39% | 268 | +56.59% | 2.20 |
| no_1d | +344.03% | +237.27% | -21.99% | -34.06% | 275 | +51.52% | 1.95 |
| less_1d | +418.68% | +311.92% | +52.66% | -32.39% | 268 | +56.59% | 2.20 |
| more_volume | +476.08% | +369.32% | +110.06% | -31.27% | 277 | +56.39% | 2.92 |

### Best 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | signal_weights | more_volume | +476.08% | +110.06% | -31.27% | 2.92 |
| 2 | max_total_exposure | 90% | +418.68% | +52.66% | -32.39% | 2.20 |
| 3 | max_position_pct | 8.50% | +418.68% | +52.66% | -32.39% | 2.20 |
| 4 | max_new_trades_per_day | 2 | +418.68% | +52.66% | -32.39% | 2.20 |
| 5 | min_composite_score | none | +418.68% | +52.66% | -32.39% | 2.20 |

### Worst 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | max_position_pct | 25.50% | +110.98% | -255.04% | -32.00% | 1.58 |
| 2 | max_position_pct | 17.00% | +177.45% | -188.57% | -26.84% | 1.60 |
| 3 | max_total_exposure | 50% | +185.78% | -180.24% | -17.91% | 2.35 |
| 4 | max_total_exposure | 70% | +189.90% | -176.12% | -26.66% | 1.83 |
| 5 | max_position_pct | 4.25% | +267.09% | -98.93% | -34.50% | 2.01 |

### Robustness Notes

The baseline outperforms 96% of all variants. This is broadly consistent across parameter dimensions, suggesting the baseline settings are reasonably competitive in-sample.

The widest in-sample return spread belongs to `max_position_pct` (307.7 pp range across its variants); `min_composite_score` shows the narrowest spread (0.0 pp), suggesting the strategy is least sensitive to that parameter in this period.

Improvements that appear in only one or two variants should be treated with skepticism — isolated peaks are more likely to reflect in-sample noise than genuine edge. Prefer settings that perform consistently across the full sweep.
