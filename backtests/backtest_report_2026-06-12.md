# AI Paper Trader — Backtest Report
**Period:** 2021-01-01 → 2026-06-12  |  **Generated:** 2026-06-12

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Ending Balance | $147,443.81 | $216,052.60 | $240,619.00 | $408,464.00 |
| Total Return | +47.44% | +116.05% | +140.62% | +308.46% |
| Max Drawdown | -20.25% | -24.50% | -35.12% | -41.24% |
| Excess vs SPY | -68.61% | — | — | — |
| Excess vs QQQ | -93.18% | — | — | — |
| Excess vs Equal-Wt | -261.02% | — | — | — |
| 1-Year Return | +12.25% | +24.27% | +35.82% | +55.52% |
| 2-Year Return | +18.41% | +41.84% | +56.89% | +94.62% |
| 3-Year Return | +43.09% | +79.62% | +107.88% | +216.34% |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $147,443.81 |
| **IRR (annualized, money-weighted)** | **+17.86%** |
| Total Return (on full $ portfolio) | +47.44% |
| Total Capital Deployed (all entries) | $3,999,661.26 |
| Avg Capital Deployed (snapshot) | $45,116.01 (+45.12% of portfolio) |
| Peak Capital Deployed (snapshot) | $78,724.83 (+78.72% of portfolio) |
| Time Invested | +99.93% of trading days |
| Trading Days | 1367 |
| Total Trades | 2293 (1152 buys, 1141 sells) |
| Win Rate | +51.62% |
| Average Win | $354.32 |
| Average Loss | $-292.82 |
| Profit Factor | 1.29 |
| Avg Holding Period | 16.0 approx. trading days |
| Largest Winner | $1,171.32 |
| Largest Loser | $-1,056.79 |
| Open Positions at End | 11 |
| Total Slippage Cost | $7,999.97 (+8.00% of start) |
| Avg Slippage / Trade | $3.49 |

_**IRR** is the annualized money-weighted (internal) rate of return on the capital actually put into positions: it solves for the rate that discounts the dated BUY outflows, SELL inflows, and the terminal mark-to-market of open positions to zero. It ignores idle cash, so it measures how the *deployed* capital performed, and is bounded at -100%. Being annualized, short backtests can extrapolate to large figures. **Total Return** is on the full starting portfolio (cash included) and is what the SPY/QQQ/Equal-Wt comparisons above use, since those benchmarks are fully invested._

## Strategy Parameters Used

| Parameter | Value |
|-----------|-------|
| Starting Portfolio | $100,000.00 |
| Max Position Size | 3.1% (auto: 75% ÷ 24 tickers) |
| Max Total Exposure | 75% |
| Max New Trades / Day | 2 |
| Stop Loss | 8% |
| Take Profit | 10% |
| Max Holding Period | 30 trading days |
| Slippage | 0.10% per fill |

## Ticker Universe

`NVDA`, `MSFT`, `AAPL`, `AMZN`, `GOOGL`, `META`, `TSLA`, `NFLX`, `AVGO`, `AMD`, `TSM`, `ASML`, `MU`, `CRM`, `ORCL`, `NOW`, `ADBE`, `CRWD`, `PANW`, `JPM`, `BAC`, `GS`, `COIN`, `COST`

## Trade Log (last 20 trades)

| Date | Action | Ticker | Shares | Price | Value | Reason | P&L | Hold Days |
|------|--------|--------|--------|-------|-------|--------|-----|-----------|
| 2026-06-03 | BUY | CRWD | 6 | $748.36 | $4,490.15 | momentum_score=0.7812 | — | — |
| 2026-06-03 | SELL | NOW | 37 | $117.78 | $4,357.94 | stop_loss | $-673.91 | 1.4 |
| 2026-06-04 | BUY | ASML | 2 | $1,759.23 | $3,518.45 | momentum_score=0.7229 | — | — |
| 2026-06-04 | SELL | GS | 4 | $1,091.52 | $4,366.07 | take_profit | $426.80 | 10.0 |
| 2026-06-04 | SELL | AVGO | 9 | $418.49 | $3,766.42 | stop_loss | $-550.96 | 0.7 |
| 2026-06-05 | BUY | GS | 4 | $1,039.72 | $4,158.87 | momentum_score=0.8062 | — | — |
| 2026-06-05 | SELL | TSLA | 10 | $390.61 | $3,906.09 | stop_loss | $-432.75 | 17.1 |
| 2026-06-05 | SELL | AMD | 9 | $465.91 | $4,193.22 | stop_loss | $-346.32 | 7.1 |
| 2026-06-05 | SELL | ORCL | 20 | $213.47 | $4,269.33 | stop_loss | $-698.64 | 2.9 |
| 2026-06-05 | SELL | CRM | 22 | $185.00 | $4,069.93 | stop_loss | $-341.58 | 2.1 |
| 2026-06-05 | SELL | PANW | 15 | $271.78 | $4,076.67 | stop_loss | $-385.49 | 2.1 |
| 2026-06-05 | SELL | CRWD | 6 | $670.35 | $4,022.09 | stop_loss | $-468.05 | 1.4 |
| 2026-06-09 | BUY | MU | 4 | $936.83 | $3,747.30 | momentum_score=0.7396 | — | — |
| 2026-06-10 | BUY | JPM | 14 | $309.45 | $4,332.29 | momentum_score=0.8 | — | — |
| 2026-06-10 | BUY | TSM | 10 | $408.20 | $4,082.03 | momentum_score=0.7896 | — | — |
| 2026-06-10 | SELL | AMZN | 16 | $237.76 | $3,804.19 | stop_loss+max_holding_period | $-408.66 | 30.0 |
| 2026-06-11 | BUY | BAC | 83 | $55.22 | $4,582.86 | momentum_score=0.7271 | — | — |
| 2026-06-11 | BUY | NFLX | 55 | $81.35 | $4,474.32 | momentum_score=0.7042 | — | — |
| 2026-06-11 | SELL | META | 6 | $567.86 | $3,407.17 | max_holding_period | $-267.96 | 30.0 |
| 2026-06-12 | BUY | PANW | 16 | $279.90 | $4,478.39 | momentum_score=0.7125 | — | — |

## Open Positions at End of Period

| Ticker | Shares | Entry Price | Final Price | Unrealized P&L | Entry Date |
|--------|--------|------------|------------|----------------|------------|
| GOOGL | 11 | $383.40 | $359.68 | $-260.97 | 2026-05-04 |
| AAPL | 15 | $287.53 | $291.13 | $53.96 | 2026-05-06 |
| NVDA | 21 | $215.16 | $205.19 | $-209.46 | 2026-05-08 |
| ASML | 2 | $1,759.23 | $1,863.55 | $208.65 | 2026-06-04 |
| GS | 4 | $1,039.72 | $1,062.75 | $92.13 | 2026-06-05 |
| MU | 4 | $936.83 | $981.61 | $179.14 | 2026-06-09 |
| JPM | 14 | $309.45 | $320.72 | $157.79 | 2026-06-10 |
| TSM | 10 | $408.20 | $423.93 | $157.27 | 2026-06-10 |
| BAC | 83 | $55.22 | $56.02 | $66.80 | 2026-06-11 |
| NFLX | 55 | $81.35 | $80.34 | $-55.62 | 2026-06-11 |
| PANW | 16 | $279.90 | $279.62 | $-4.47 | 2026-06-12 |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2021-01-04 | $100,000.00 | — | +0.00% | +0.00% | +0.00% | +0.00% |
| 2021-01-05 | $99,994.01 | -0.01% | -0.01% | +0.69% | +0.82% | +0.94% |
| 2021-01-06 | $99,979.08 | -0.01% | -0.02% | +1.29% | -0.57% | -0.03% |
| 2021-01-07 | $100,346.22 | +0.37% | +0.35% | +2.80% | +1.83% | +3.04% |
| 2021-01-08 | $100,198.99 | -0.15% | +0.20% | +3.38% | +3.14% | +3.76% |
| 2026-06-08 | $147,135.91 | +0.08% | +47.14% | +115.32% | +138.86% | +309.58% |
| 2026-06-09 | $146,952.54 | -0.12% | +46.95% | +114.68% | +136.11% | +305.06% |
| 2026-06-10 | $146,139.14 | -0.55% | +46.14% | +111.30% | +131.40% | +293.38% |
| 2026-06-11 | $147,358.46 | +0.83% | +47.36% | +114.89% | +139.21% | +308.18% |
| 2026-06-12 | $147,443.81 | +0.06% | +47.44% | +116.05% | +140.62% | +308.46% |


## Signal Predictiveness

_Cross-section of 32,695 (date, ticker) signal observations. Correlations are Pearson vs forward returns._

| Signal | vs fwd 5d | vs fwd 10d | vs fwd 20d |
|--------|-----------|------------|------------|
| return_1d | -0.01 | -0.00 | 0.01 |
| return_5d | -0.02 | 0.01 | 0.02 |
| return_20d | 0.02 | 0.02 | -0.00 |
| vol_ratio | 0.01 | 0.02 | 0.02 |
| composite_score | 0.00 | 0.00 | 0.00 |

**Forward returns by composite-score quintile** (5 = highest-ranked):

| Quintile | N | Avg fwd 5d | Win 5d | Avg fwd 10d | Win 10d | Avg fwd 20d | Win 20d |
|----------|---|-----------|--------|-------------|---------|-------------|---------|
| Q1 | 6830 | +0.59% | +53.39% | +1.16% | +55.53% | +2.54% | +57.34% |
| Q2 | 6741 | +0.57% | +54.90% | +1.14% | +56.42% | +2.11% | +58.02% |
| Q3 | 5553 | +0.47% | +54.47% | +1.00% | +55.54% | +2.01% | +57.04% |
| Q4 | 6741 | +0.49% | +54.83% | +1.07% | +55.51% | +1.96% | +56.82% |
| Q5 | 6830 | +0.57% | +53.55% | +1.10% | +54.61% | +2.39% | +56.02% |

**Top-minus-bottom quintile spread:** 5d -0.02%  |  10d -0.06%  |  20d -0.15%  (positive ⇒ higher-ranked names outperform lower-ranked names).

## Entry vs Exit Attribution

_Buy the top 2 ranked names each day, hold a fixed period, **no** stop-loss / take-profit / max-holding. Next-day entry, slippage applied._

| Hold period | Raw avg return / trade | Raw win rate | N trades |
|-------------|------------------------|--------------|----------|
| 5d | +0.43% | +51.19% | 2684 |
| 10d | +0.98% | +52.92% | 2674 |
| 20d | +2.51% | +55.35% | 2654 |
| 30d | +3.26% | +56.49% | 2634 |

**Full strategy (with exit rules):** total return +47.44%, win rate +51.62%, avg hold 16.02 trading days.

The raw signal (buy top names, hold fixed, no stops) is **positive across holding periods** (avg +1.79% per trade, 54% win rate). That points to genuine signal quality — higher-ranked names tend to rise even without exit rules.

## P&L Attribution

**Top 5 contributors:**

| Ticker | P&L |
|--------|-----|
| NVDA | $7,102.66 |
| MU | $6,952.08 |
| AMD | $4,985.35 |
| TSM | $4,374.03 |
| AVGO | $3,924.33 |

**Worst 5 contributors:**

| Ticker | P&L |
|--------|-----|
| ADBE | $-1,660.67 |
| NOW | $-1,483.34 |
| CRM | $-880.62 |
| BAC | $-511.60 |
| AAPL | $-94.75 |

**P&L by asset group:**

| Group | P&L |
|-------|-----|
| mega_cap_growth | $16,943.80 |
| semiconductors | $15,861.76 |
| financial_crypto_beta | $1,329.28 |
| software_cybersecurity | $-1,012.32 |
| _(ungrouped)_ | $14,321.30 |

## Turnover and Re-entry Diagnostics

| Metric | Value |
|--------|-------|
| Total trades | 2293 |
| Trades / month | 35.11 |
| Avg holding period | 16.02 trading days |
| Stop-loss → re-entry ≤5d | 86 |

**Most-entered tickers:** `COIN`×86, `AMD`×72, `NVDA`×66, `MU`×65, `TSLA`×59, `CRWD`×59, `AVGO`×56, `ASML`×50

**Most re-entered after a stop-loss:** `COIN`×16, `NVDA`×8, `AMD`×7, `AVGO`×6, `PANW`×5

## Exposure and Benchmark Capture

| Metric | Value |
|--------|-------|
| Avg exposure | +39.32% |
| Max exposure | +66.80% |
| Avg cash (drag) | +60.68% |
| Correlation to SPY | 0.80 |
| Correlation to QQQ | 0.86 |
| Beta to SPY | 0.46 |
| Beta to QQQ | 0.37 |
| Up-capture vs QQQ | 0.41 |
| Down-capture vs QQQ | 0.41 |

_Beta ≈ 1 with high correlation ⇒ performance is mostly market exposure; low beta with a positive quintile spread ⇒ more genuine selection alpha._

## Suggested Next Config Tests

_Ideas to test next — not yet implemented._

- **QQQ trend filter** — only take entries while QQQ is above its 50-day moving average.
- **Volatility-adjusted momentum** — rank on `return_20d / realized_vol_20d` instead of raw return.
- **Moving-average confirmation** — require price above both its 20-day and 50-day moving averages.
- **Overextension filter** — skip names too far above their 20-day moving average (avoid chasing).
- **Cooldown after stop-loss** — block re-entry into a name for 5 trading days after a stop-out.
- **Separate leveraged-ETF rules** — smaller max position size and shorter max holding for leveraged ETFs.



## Sensitivity Analysis

> One parameter is varied at a time; all others remain at baseline values.
> Do not select parameters based on in-sample performance alone — see Robustness Notes below.

**Baseline:** +47.44% return  |  -20.25% max drawdown  |  +51.62% win rate  |  1.29 profit factor

### Stop Loss  (baseline: 7.5%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 3.0% | +33.73% | -82.32% | -274.73% | -15.58% | 2852 | +35.14% | 1.22 |
| 5.0% | +39.85% | -76.20% | -268.61% | -18.46% | 2525 | +43.96% | 1.25 |
| 7.5% ◀ baseline | +47.44% | -68.61% | -261.02% | -20.25% | 2293 | +51.62% | 1.29 |
| 10.0% | +46.87% | -69.18% | -261.59% | -23.50% | 2149 | +55.51% | 1.30 |

### Take Profit  (baseline: 10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 8% | +41.77% | -74.28% | -266.69% | -19.39% | 2459 | +54.37% | 1.25 |
| 10% ◀ baseline | +47.44% | -68.61% | -261.02% | -20.25% | 2293 | +51.62% | 1.29 |
| 15% | +50.94% | -65.11% | -257.52% | -21.12% | 1986 | +49.09% | 1.34 |

### Max Holding Days  (baseline: 30)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 5 | +10.76% | -105.30% | -297.71% | -13.60% | 3676 | +50.00% | 1.08 |
| 15 | +37.12% | -78.93% | -271.34% | -18.21% | 2673 | +51.95% | 1.25 |
| 30 ◀ baseline | +47.44% | -68.61% | -261.02% | -20.25% | 2293 | +51.62% | 1.29 |
| 60 | +57.21% | -58.84% | -251.25% | -22.53% | 2124 | +51.47% | 1.33 |

### Max New Trades / Day  (baseline: 2)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 1 | +37.69% | -78.37% | -270.78% | -18.51% | 1996 | +51.31% | 1.27 |
| 2 ◀ baseline | +47.44% | -68.61% | -261.02% | -20.25% | 2293 | +51.62% | 1.29 |
| 3 | +49.05% | -67.00% | -259.41% | -21.44% | 2351 | +51.79% | 1.30 |
| 5 | +48.57% | -67.48% | -259.89% | -21.51% | 2366 | +51.83% | 1.29 |

### Min Composite Score  (baseline: 0.70)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| none | +73.61% | -42.44% | -234.85% | -27.32% | 3160 | +52.45% | 1.29 |
| 0.60 | +52.94% | -63.11% | -255.52% | -27.13% | 2883 | +50.97% | 1.25 |
| 0.70 ◀ baseline | +47.44% | -68.61% | -261.02% | -20.25% | 2293 | +51.62% | 1.29 |
| 0.80 | +32.31% | -83.74% | -276.15% | -15.48% | 1611 | +52.18% | 1.29 |

### Signal Weight Profile  (baseline: baseline)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| baseline ◀ baseline | +47.44% | -68.61% | -261.02% | -20.25% | 2293 | +51.62% | 1.29 |
| no_1d | +45.53% | -70.52% | -262.93% | -20.72% | 2260 | +51.15% | 1.28 |
| less_1d | +43.01% | -73.04% | -265.45% | -20.66% | 2224 | +51.35% | 1.27 |
| more_volume | +47.44% | -68.61% | -261.02% | -20.25% | 2293 | +51.62% | 1.29 |

### Best 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs SPY | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|--------|-----|
| 1 | min_composite_score | none | +73.61% | -42.44% | -234.85% | -27.32% | 1.29 |
| 2 | max_holding_days | 60 | +57.21% | -58.84% | -251.25% | -22.53% | 1.33 |
| 3 | min_composite_score | 0.60 | +52.94% | -63.11% | -255.52% | -27.13% | 1.25 |
| 4 | take_profit | 15% | +50.94% | -65.11% | -257.52% | -21.12% | 1.34 |
| 5 | max_new_trades_per_day | 3 | +49.05% | -67.00% | -259.41% | -21.44% | 1.30 |

### Worst 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs SPY | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|--------|-----|
| 1 | max_holding_days | 5 | +10.76% | -105.30% | -297.71% | -13.60% | 1.08 |
| 2 | min_composite_score | 0.80 | +32.31% | -83.74% | -276.15% | -15.48% | 1.29 |
| 3 | stop_loss | 3.0% | +33.73% | -82.32% | -274.73% | -15.58% | 1.22 |
| 4 | max_holding_days | 15 | +37.12% | -78.93% | -271.34% | -18.21% | 1.25 |
| 5 | max_new_trades_per_day | 1 | +37.69% | -78.37% | -270.78% | -18.51% | 1.27 |

### Robustness Notes

26% of variants beat the baseline. Improvements are mixed — some directions help, others hurt — which is consistent with a strategy that has modest but not dominant in-sample edge.

The widest in-sample return spread belongs to `max_holding_days` (46.5 pp range across its variants); `signal_weights` shows the narrowest spread (4.4 pp), suggesting the strategy is least sensitive to that parameter in this period.

Improvements that appear in only one or two variants should be treated with skepticism — isolated peaks are more likely to reflect in-sample noise than genuine edge. Prefer settings that perform consistently across the full sweep.


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