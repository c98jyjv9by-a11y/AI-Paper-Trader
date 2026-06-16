# Scenario — levi_test

Full 21-name universe with one uniform exit rule applied to every ticker (stop 15%, no take-profit, no trailing stop, 60-day max hold) plus the trough-based anti-falling-knife re-entry gate. Composite ranking drives entries.

**Universe (83):** CRWD, ORCL, COIN, NFLX, PANW, GOOGL, BAC, MSFT, AVGO, AMZN, COST, ASML, AAPL, JPM, TSM, GS, META, TSLA, MU, AMD, NVDA, LLY, VST, AXON, GE, PLTR, OXY, INTC, BA, PFE, PYPL, SEDG, PLUG, ADBE, CRM, NOW, INTU, SAP, WDAY, SNOW, DDOG, NET, MDB, ZS, FTNT, TEAM, OKTA, TWLO, HUBS, SNPS, CDNS, QCOM, TXN, AMAT, LRCX, KLAC, NXPI, MRVL, ADI, MCHP, ON, ARM, ANET, CSCO, IBM, DELL, SMCI, VRT, APP, SHOP, UBER, ABNB, MELI, SE, SPOT, DASH, RBLX, PINS, SNAP, TTD, NU, HOOD, SOFI

---

# AI Paper Trader — Backtest Report
**Period:** 2025-01-01 → 2026-06-15  |  **Generated:** 2026-06-15

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Ending Balance | $184,725.21 | $130,983.10 | $146,740.90 | $172,636.30 |
| Total Return | +84.73% | +30.98% | +46.74% | +72.64% |
| Max Drawdown | -33.19% | -18.76% | -22.77% | -29.49% |
| Excess vs SPY | +53.74% | — | — | — |
| Excess vs QQQ | +37.98% | — | — | — |
| Excess vs Equal-Wt | +12.09% | — | — | — |
| 1-Year Return | +89.56% | +27.89% | +41.87% | +56.28% |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $184,725.21 |
| **IRR (annualized, money-weighted)** | **+57.93%** |
| Total Return (on full $ portfolio) | +84.73% |
| Total Capital Deployed (all entries) | $804,583.74 |
| Avg Capital Deployed (snapshot) | $106,146.14 (+106.15% of portfolio) |
| Peak Capital Deployed (snapshot) | $188,928.31 (+188.93% of portfolio) |
| Time Invested | +99.72% of trading days |
| Trading Days | 363 |
| Total Trades | 157 (84 buys, 73 sells) |
| Win Rate | +49.32% |
| Average Win | $2,754.22 |
| Average Loss | $-1,479.46 |
| Profit Factor | 1.81 |
| Avg Holding Period | 50.3 approx. trading days |
| Largest Winner | $22,984.09 |
| Largest Loser | $-3,413.68 |
| Open Positions at End | 11 |
| Total Slippage Cost | $1,518.87 (+1.52% of start) |
| Avg Slippage / Trade | $9.67 |

_**IRR** is the annualized money-weighted (internal) rate of return on the capital actually put into positions: it solves for the rate that discounts the dated BUY outflows, SELL inflows, and the terminal mark-to-market of open positions to zero. It ignores idle cash, so it measures how the *deployed* capital performed, and is bounded at -100%. Being annualized, short backtests can extrapolate to large figures. **Total Return** is on the full starting portfolio (cash included) and is what the SPY/QQQ/Equal-Wt comparisons above use, since those benchmarks are fully invested._

## Strategy Parameters Used

| Parameter | Value |
|-----------|-------|
| Starting Portfolio | $100,000.00 |
| Max Position Size | 8.5% |
| Max Total Exposure | 90% |
| Max New Trades / Day | 2 |
| Stop Loss | 20.0% |
| Take Profit | none |
| Trailing Stop | none |
| Max Holding Period | 60 trading days |
| Slippage | 0.10% per fill |

## Ticker Universe

`CRWD`, `ORCL`, `COIN`, `NFLX`, `PANW`, `GOOGL`, `BAC`, `MSFT`, `AVGO`, `AMZN`, `COST`, `ASML`, `AAPL`, `JPM`, `TSM`, `GS`, `META`, `TSLA`, `MU`, `AMD`, `NVDA`, `LLY`, `VST`, `AXON`, `GE`, `PLTR`, `OXY`, `INTC`, `BA`, `PFE`, `PYPL`, `SEDG`, `PLUG`, `ADBE`, `CRM`, `NOW`, `INTU`, `SAP`, `WDAY`, `SNOW`, `DDOG`, `NET`, `MDB`, `ZS`, `FTNT`, `TEAM`, `OKTA`, `TWLO`, `HUBS`, `SNPS`, `CDNS`, `QCOM`, `TXN`, `AMAT`, `LRCX`, `KLAC`, `NXPI`, `MRVL`, `ADI`, `MCHP`, `ON`, `ARM`, `ANET`, `CSCO`, `IBM`, `DELL`, `SMCI`, `VRT`, `APP`, `SHOP`, `UBER`, `ABNB`, `MELI`, `SE`, `SPOT`, `DASH`, `RBLX`, `PINS`, `SNAP`, `TTD`, `NU`, `HOOD`, `SOFI`

## Trade Log (last 20 trades)

| Date | Action | Ticker | Shares | Price | Value | Reason | P&L | Hold Days |
|------|--------|--------|--------|-------|-------|--------|-----|-----------|
| 2026-04-10 | SELL | NET | 49 | $166.82 | $8,174.33 | stop_loss | $-2,273.11 | 21.4 |
| 2026-04-22 | SELL | ASML | 7 | $1,439.07 | $10,073.51 | max_holding_period | $137.95 | 60.0 |
| 2026-04-23 | BUY | ARM | 56 | $204.81 | $11,469.62 | momentum_score=0.9687 | — | — |
| 2026-04-27 | SELL | LRCX | 47 | $259.21 | $12,182.89 | max_holding_period | $1,022.60 | 60.0 |
| 2026-04-28 | BUY | INTC | 132 | $84.60 | $11,167.79 | momentum_score=0.9873 | — | — |
| 2026-05-01 | SELL | TXN | 47 | $279.32 | $13,128.03 | max_holding_period | $2,762.60 | 60.0 |
| 2026-05-04 | BUY | TWLO | 62 | $189.86 | $11,771.30 | momentum_score=0.9512 | — | — |
| 2026-05-08 | SELL | VRT | 45 | $339.63 | $15,283.35 | max_holding_period | $4,721.46 | 60.0 |
| 2026-05-11 | BUY | DDOG | 60 | $202.52 | $12,151.34 | momentum_score=0.9717 | — | — |
| 2026-05-11 | BUY | MU | 16 | $796.13 | $12,738.00 | momentum_score=0.9428 | — | — |
| 2026-05-12 | SELL | AMAT | 30 | $430.23 | $12,907.02 | max_holding_period | $2,149.15 | 60.0 |
| 2026-05-13 | BUY | MDB | 38 | $303.30 | $11,525.51 | momentum_score=0.9018 | — | — |
| 2026-05-19 | SELL | OXY | 204 | $60.36 | $12,313.54 | max_holding_period | $1,803.83 | 60.0 |
| 2026-05-20 | BUY | CRWD | 19 | $650.76 | $12,364.44 | momentum_score=0.9175 | — | — |
| 2026-06-03 | SELL | MRVL | 109 | $301.35 | $32,846.96 | max_holding_period | $22,984.09 | 60.0 |
| 2026-06-04 | BUY | MRVL | 53 | $316.75 | $16,787.56 | momentum_score=0.9867 | — | — |
| 2026-06-04 | BUY | OKTA | 130 | $123.60 | $16,068.45 | momentum_score=0.8867 | — | — |
| 2026-06-05 | SELL | PLTR | 65 | $135.39 | $8,800.64 | max_holding_period | $-1,020.92 | 60.0 |
| 2026-06-10 | SELL | MRVL | 53 | $252.34 | $13,373.88 | stop_loss | $-3,413.68 | 4.3 |
| 2026-06-11 | BUY | KLAC | 66 | $241.41 | $15,932.74 | momentum_score=0.8843 | — | — |

## Open Positions at End of Period

| Ticker | Shares | Entry Price | Final Price | Unrealized P&L | Entry Date |
|--------|--------|------------|------------|----------------|------------|
| DELL | 57 | $183.63 | $409.07 | $12,850.32 | 2026-03-25 |
| COST | 9 | $995.98 | $979.45 | $-148.78 | 2026-03-31 |
| ARM | 56 | $204.81 | $412.55 | $11,633.18 | 2026-04-23 |
| INTC | 132 | $84.60 | $127.86 | $5,709.73 | 2026-04-28 |
| TWLO | 62 | $189.86 | $202.00 | $752.70 | 2026-05-04 |
| DDOG | 60 | $202.52 | $233.09 | $1,834.06 | 2026-05-11 |
| MU | 16 | $796.13 | $1,087.99 | $4,669.84 | 2026-05-11 |
| MDB | 38 | $303.30 | $354.18 | $1,933.33 | 2026-05-13 |
| CRWD | 19 | $650.76 | $692.91 | $800.85 | 2026-05-20 |
| OKTA | 130 | $123.60 | $118.12 | $-712.85 | 2026-06-04 |
| KLAC | 66 | $241.41 | $256.42 | $990.98 | 2026-06-11 |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2025-01-02 | $100,000.00 | — | +0.00% | +0.00% | +0.00% | +0.00% |
| 2025-01-03 | $99,982.62 | -0.02% | -0.02% | +1.25% | +1.64% | +2.62% |
| 2025-01-06 | $100,488.04 | +0.51% | +0.49% | +1.83% | +2.80% | +4.71% |
| 2025-01-07 | $100,517.77 | +0.03% | +0.52% | +0.68% | +0.97% | +2.94% |
| 2025-01-08 | $98,006.04 | -2.50% | -1.99% | +0.83% | +0.99% | +2.33% |
| 2026-06-09 | $171,496.56 | -2.89% | +71.50% | +27.90% | +39.61% | +61.69% |
| 2026-06-10 | $168,249.66 | -1.89% | +68.25% | +25.88% | +36.82% | +57.31% |
| 2026-06-11 | $176,086.85 | +4.66% | +76.09% | +28.02% | +41.44% | +65.11% |
| 2026-06-12 | $179,019.06 | +1.67% | +79.02% | +28.71% | +42.27% | +66.53% |
| 2026-06-15 | $184,725.21 | +3.19% | +84.73% | +30.98% | +46.74% | +72.64% |


## Signal Predictiveness

_Cross-section of 30,046 (date, ticker) signal observations. Correlations are Pearson vs forward returns._

| Signal | vs fwd 5d | vs fwd 10d | vs fwd 20d |
|--------|-----------|------------|------------|
| return_1d | -0.01 | -0.01 | 0.01 |
| return_5d | -0.02 | 0.01 | 0.03 |
| return_20d | 0.02 | 0.04 | 0.06 |
| vol_ratio | 0.00 | 0.00 | -0.00 |
| vol_adj_mom_20d | 0.02 | 0.04 | 0.05 |
| composite_score | 0.00 | 0.02 | 0.03 |

**Forward returns by composite-score quintile** (5 = highest-ranked):

| Quintile | N | Avg fwd 5d | Win 5d | Avg fwd 10d | Win 10d | Avg fwd 20d | Win 20d |
|----------|---|-----------|--------|-------------|---------|-------------|---------|
| Q1 | 6154 | +0.73% | +52.91% | +1.26% | +52.97% | +2.24% | +52.75% |
| Q2 | 5792 | +0.55% | +53.40% | +1.06% | +53.67% | +1.80% | +52.35% |
| Q3 | 6154 | +0.51% | +52.73% | +1.20% | +52.94% | +2.26% | +52.22% |
| Q4 | 5792 | +0.47% | +52.36% | +1.33% | +53.70% | +2.84% | +54.35% |
| Q5 | 6154 | +0.80% | +54.19% | +1.69% | +54.86% | +3.48% | +54.43% |

**Top-minus-bottom quintile spread:** 5d +0.07%  |  10d +0.44%  |  20d +1.23%  (positive ⇒ higher-ranked names outperform lower-ranked names).

## Entry vs Exit Attribution

_Buy the top 2 ranked names each day, hold a fixed period, **no** stop-loss / take-profit / max-holding. Next-day entry, slippage applied._

| Hold period | Raw avg return / trade | Raw win rate | N trades |
|-------------|------------------------|--------------|----------|
| 5d | +0.75% | +51.96% | 714 |
| 10d | +1.43% | +54.26% | 704 |
| 20d | +3.86% | +54.68% | 684 |
| 30d | +5.68% | +54.82% | 664 |

**Full strategy (with exit rules):** total return +84.73%, win rate +49.32%, avg hold 50.33 trading days.

The raw signal (buy top names, hold fixed, no stops) is **positive across holding periods** (avg +2.93% per trade, 54% win rate). That points to genuine signal quality — higher-ranked names tend to rise even without exit rules.

## P&L Attribution

**Top 5 contributors:**

| Ticker | P&L |
|--------|-----|
| MRVL | $19,643.64 |
| DELL | $12,850.32 |
| INTC | $10,682.16 |
| ARM | $9,583.12 |
| SEDG | $5,566.88 |

**Worst 5 contributors:**

| Ticker | P&L |
|--------|-----|
| OKTA | $-4,779.37 |
| SNAP | $-4,537.92 |
| SHOP | $-2,550.29 |
| TTD | $-2,405.11 |
| NET | $-2,276.08 |

**P&L by asset group:**

| Group | P&L |
|-------|-----|
| semiconductors | $13,725.21 |
| mega_cap_growth | $2,150.68 |
| financial_crypto_beta | $1,035.70 |
| software_cybersecurity | $800.85 |
| _(ungrouped)_ | $67,012.82 |

## Turnover and Re-entry Diagnostics

| Metric | Value |
|--------|-------|
| Total trades | 157 |
| Trades / month | 9.02 |
| Avg holding period | 50.33 trading days |
| Stop-loss → re-entry ≤5d | 0 |

**Most-entered tickers:** `PLUG`×4, `MU`×4, `SEDG`×3, `ARM`×3, `KLAC`×3, `SNAP`×3, `OKTA`×3, `TSLA`×3

## Exposure and Benchmark Capture

| Metric | Value |
|--------|-------|
| Avg exposure | +91.55% |
| Max exposure | +98.66% |
| Avg cash (drag) | +8.45% |
| Correlation to SPY | 0.74 |
| Correlation to QQQ | 0.79 |
| Beta to SPY | 1.43 |
| Beta to QQQ | 1.21 |
| Up-capture vs QQQ | 1.35 |
| Down-capture vs QQQ | 1.26 |

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

**Baseline (as configured):** +84.73% return  |  -33.19% max drawdown  |  +49.32% win rate  |  1.81 profit factor

### Run-wide parameters

#### Max Total Exposure  (baseline: 90%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 50% | +21.00% | -9.98% | -51.63% | -23.16% | 90 | +57.14% | 1.76 |
| 70% | +66.25% | +35.26% | -6.39% | -27.03% | 131 | +50.82% | 2.28 |
| 90% ◀ baseline | +84.73% | +53.74% | +12.09% | -33.19% | 157 | +49.32% | 1.81 |
| 100% | +91.06% | +60.07% | +18.42% | -31.49% | 157 | +56.16% | 2.26 |

#### Max Position Size  (baseline: 8.50%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 4.25% | +77.72% | +46.74% | +5.09% | -27.12% | 306 | +51.41% | 1.80 |
| 8.50% ◀ baseline | +84.73% | +53.74% | +12.09% | -33.19% | 157 | +49.32% | 1.81 |
| 12.75% | +53.65% | +22.67% | -18.99% | -36.07% | 104 | +56.25% | 1.89 |
| 17.00% | +25.84% | -5.15% | -46.80% | -33.55% | 77 | +47.22% | 1.29 |
| 25.50% | +61.97% | +30.98% | -10.67% | -32.69% | 45 | +57.14% | 1.40 |

#### Max New Trades / Day  (baseline: 2)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 1 | +90.19% | +59.21% | +17.55% | -30.17% | 154 | +55.56% | 2.48 |
| 2 ◀ baseline | +84.73% | +53.74% | +12.09% | -33.19% | 157 | +49.32% | 1.81 |
| 3 | +83.41% | +52.43% | +10.78% | -31.73% | 155 | +52.78% | 2.12 |
| 5 | +87.89% | +56.90% | +15.25% | -30.76% | 158 | +48.65% | 1.62 |

#### Min Composite Score  (baseline: 0.70)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| none | +84.73% | +53.74% | +12.09% | -33.19% | 157 | +49.32% | 1.81 |
| 0.60 | +84.73% | +53.74% | +12.09% | -33.19% | 157 | +49.32% | 1.81 |
| 0.70 ◀ baseline | +84.73% | +53.74% | +12.09% | -33.19% | 157 | +49.32% | 1.81 |

#### Slippage  (baseline: 0.10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 0.05% | +109.46% | +78.48% | +36.83% | -33.10% | 155 | +51.39% | 2.34 |
| 0.10% ◀ baseline | +84.73% | +53.74% | +12.09% | -33.19% | 157 | +49.32% | 1.81 |
| 0.20% | +88.21% | +57.22% | +15.57% | -33.10% | 161 | +46.67% | 1.79 |
| 0.50% | +49.43% | +18.44% | -23.21% | -33.58% | 162 | +41.33% | 1.61 |

#### Re-entry Recovery Gate  (baseline: 10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +84.73% | +53.74% | +12.09% | -33.19% | 157 | +49.32% | 1.81 |
| 0% | +84.73% | +53.74% | +12.09% | -33.19% | 157 | +49.32% | 1.81 |
| 5% | +84.73% | +53.74% | +12.09% | -33.19% | 157 | +49.32% | 1.81 |
| 10% ◀ baseline | +84.73% | +53.74% | +12.09% | -33.19% | 157 | +49.32% | 1.81 |

#### Signal Weight Profile  (baseline: baseline)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| baseline ◀ baseline | +84.73% | +53.74% | +12.09% | -33.19% | 157 | +49.32% | 1.81 |
| no_1d | +116.92% | +85.94% | +44.28% | -31.16% | 155 | +56.94% | 2.68 |
| less_1d | +84.73% | +53.74% | +12.09% | -33.19% | 157 | +49.32% | 1.81 |
| more_volume | +55.10% | +24.12% | -17.53% | -30.56% | 154 | +50.70% | 1.99 |

### Best 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | signal_weights | no_1d | +116.92% | +44.28% | -31.16% | 2.68 |
| 2 | slippage | 0.05% | +109.46% | +36.83% | -33.10% | 2.34 |
| 3 | max_total_exposure | 100% | +91.06% | +18.42% | -31.49% | 2.26 |
| 4 | max_new_trades_per_day | 1 | +90.19% | +17.55% | -30.17% | 2.48 |
| 5 | slippage | 0.20% | +88.21% | +15.57% | -33.10% | 1.79 |

### Worst 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | max_total_exposure | 50% | +21.00% | -51.63% | -23.16% | 1.76 |
| 2 | max_position_pct | 17.00% | +25.84% | -46.80% | -33.55% | 1.29 |
| 3 | slippage | 0.50% | +49.43% | -23.21% | -33.58% | 1.61 |
| 4 | max_position_pct | 12.75% | +53.65% | -18.99% | -36.07% | 1.89 |
| 5 | signal_weights | more_volume | +55.10% | -17.53% | -30.56% | 1.99 |

### Robustness Notes

The baseline outperforms 79% of all variants. This is broadly consistent across parameter dimensions, suggesting the baseline settings are reasonably competitive in-sample.

The widest in-sample return spread belongs to `max_total_exposure` (70.1 pp range across its variants); `min_composite_score` shows the narrowest spread (0.0 pp), suggesting the strategy is least sensitive to that parameter in this period.

Improvements that appear in only one or two variants should be treated with skepticism — isolated peaks are more likely to reflect in-sample noise than genuine edge. Prefer settings that perform consistently across the full sweep.
