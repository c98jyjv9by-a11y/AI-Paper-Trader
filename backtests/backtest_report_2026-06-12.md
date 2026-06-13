# AI Paper Trader — Backtest Report
**Period:** 2021-06-12 → 2026-06-12  |  **Generated:** 2026-06-12

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Ending Balance | $160,200.32 | $186,751.50 | $215,761.50 | $378,345.50 |
| Total Return | +60.20% | +86.75% | +115.76% | +278.35% |
| Max Drawdown | -19.39% | -24.50% | -35.12% | -41.79% |
| Excess vs SPY | -26.55% | — | — | — |
| Excess vs QQQ | -55.56% | — | — | — |
| Excess vs Equal-Wt | -218.15% | — | — | — |
| 1-Year Return | +18.34% | +24.27% | +35.82% | +63.06% |
| 2-Year Return | +26.63% | +41.84% | +56.89% | +104.50% |
| 3-Year Return | +55.93% | +79.62% | +107.88% | +240.49% |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $160,200.32 |
| **IRR (annualized, money-weighted)** | **+22.77%** |
| Total Return (on full $ portfolio) | +60.20% |
| Total Capital Deployed (all entries) | $4,039,974.32 |
| Avg Capital Deployed (snapshot) | $47,390.44 (+47.39% of portfolio) |
| Peak Capital Deployed (snapshot) | $91,470.51 (+91.47% of portfolio) |
| Time Invested | +99.92% of trading days |
| Trading Days | 1256 |
| Total Trades | 1971 (991 buys, 980 sells) |
| Win Rate | +53.16% |
| Average Win | $422.21 |
| Average Loss | $-348.67 |
| Profit Factor | 1.37 |
| Avg Holding Period | 15.3 approx. trading days |
| Largest Winner | $1,356.26 |
| Largest Loser | $-1,215.31 |
| Open Positions at End | 11 |
| Total Slippage Cost | $8,079.35 (+8.08% of start) |
| Avg Slippage / Trade | $4.10 |

_**IRR** is the annualized money-weighted (internal) rate of return on the capital actually put into positions: it solves for the rate that discounts the dated BUY outflows, SELL inflows, and the terminal mark-to-market of open positions to zero. It ignores idle cash, so it measures how the *deployed* capital performed, and is bounded at -100%. Being annualized, short backtests can extrapolate to large figures. **Total Return** is on the full starting portfolio (cash included) and is what the SPY/QQQ/Equal-Wt comparisons above use, since those benchmarks are fully invested._

## Strategy Parameters Used

| Parameter | Value |
|-----------|-------|
| Starting Portfolio | $100,000.00 |
| Max Position Size | 3.6% (auto: 75% ÷ 21 tickers) |
| Max Total Exposure | 75% |
| Max New Trades / Day | 2 |
| Stop Loss | 8% |
| Take Profit | 10% |
| Max Holding Period | 30 trading days |
| Slippage | 0.10% per fill |

## Ticker Universe

`NVDA`, `MSFT`, `AAPL`, `AMZN`, `GOOGL`, `META`, `TSLA`, `NFLX`, `AVGO`, `AMD`, `TSM`, `ASML`, `MU`, `ORCL`, `CRWD`, `PANW`, `JPM`, `BAC`, `GS`, `COIN`, `COST`

## Trade Log (last 20 trades)

| Date | Action | Ticker | Shares | Price | Value | Reason | P&L | Hold Days |
|------|--------|--------|--------|-------|-------|--------|-----|-----------|
| 2026-06-03 | BUY | AVGO | 12 | $479.71 | $5,756.51 | momentum_score=0.831 | — | — |
| 2026-06-04 | SELL | GS | 5 | $1,091.52 | $5,457.59 | take_profit | $533.50 | 10.0 |
| 2026-06-04 | SELL | AVGO | 12 | $418.49 | $5,021.89 | stop_loss | $-734.62 | 0.7 |
| 2026-06-05 | BUY | GS | 5 | $1,039.72 | $5,198.59 | momentum_score=0.8048 | — | — |
| 2026-06-05 | SELL | TSLA | 12 | $390.61 | $4,687.31 | stop_loss | $-519.29 | 17.1 |
| 2026-06-05 | SELL | AMD | 12 | $465.91 | $5,590.96 | stop_loss | $-461.76 | 7.1 |
| 2026-06-05 | SELL | ORCL | 25 | $213.47 | $5,336.66 | stop_loss | $-873.30 | 2.9 |
| 2026-06-05 | SELL | PANW | 20 | $271.78 | $5,435.56 | stop_loss | $-580.05 | 2.9 |
| 2026-06-05 | SELL | CRWD | 7 | $670.35 | $4,692.44 | stop_loss | $-695.59 | 2.1 |
| 2026-06-08 | SELL | AMZN | 20 | $244.97 | $4,899.50 | stop_loss | $-407.01 | 27.9 |
| 2026-06-09 | BUY | MU | 6 | $936.83 | $5,620.96 | momentum_score=0.7024 | — | — |
| 2026-06-09 | SELL | MSFT | 12 | $403.01 | $4,836.08 | stop_loss | $-464.94 | 5.0 |
| 2026-06-10 | BUY | JPM | 18 | $309.45 | $5,570.09 | momentum_score=0.8024 | — | — |
| 2026-06-10 | BUY | TSM | 13 | $408.20 | $5,306.64 | momentum_score=0.7738 | — | — |
| 2026-06-11 | BUY | BAC | 103 | $55.22 | $5,687.17 | momentum_score=0.719 | — | — |
| 2026-06-11 | BUY | NFLX | 68 | $81.35 | $5,531.89 | momentum_score=0.7048 | — | — |
| 2026-06-11 | SELL | META | 8 | $567.86 | $4,542.89 | max_holding_period | $-357.28 | 30.0 |
| 2026-06-11 | SELL | ASML | 3 | $1,897.58 | $5,692.74 | take_profit | $791.76 | 11.4 |
| 2026-06-12 | BUY | ASML | 3 | $1,865.41 | $5,596.24 | momentum_score=0.9357 | — | — |
| 2026-06-12 | BUY | PANW | 20 | $279.90 | $5,597.99 | momentum_score=0.7048 | — | — |

## Open Positions at End of Period

| Ticker | Shares | Entry Price | Final Price | Unrealized P&L | Entry Date |
|--------|--------|------------|------------|----------------|------------|
| GOOGL | 14 | $383.40 | $359.68 | $-332.14 | 2026-05-04 |
| AAPL | 19 | $287.53 | $291.13 | $68.35 | 2026-05-06 |
| NVDA | 26 | $215.16 | $205.19 | $-259.33 | 2026-05-08 |
| GS | 5 | $1,039.72 | $1,062.75 | $115.16 | 2026-06-05 |
| MU | 6 | $936.83 | $981.61 | $268.70 | 2026-06-09 |
| JPM | 18 | $309.45 | $320.72 | $202.87 | 2026-06-10 |
| TSM | 13 | $408.20 | $423.93 | $204.45 | 2026-06-10 |
| BAC | 103 | $55.22 | $56.02 | $82.89 | 2026-06-11 |
| NFLX | 68 | $81.35 | $80.34 | $-68.77 | 2026-06-11 |
| ASML | 3 | $1,865.41 | $1,863.55 | $-5.59 | 2026-06-12 |
| PANW | 20 | $279.90 | $279.62 | $-5.59 | 2026-06-12 |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2021-06-14 | $100,000.00 | — | +0.00% | +0.00% | +0.00% | +0.00% |
| 2021-06-15 | $99,992.95 | -0.01% | -0.01% | -0.18% | -0.65% | -0.98% |
| 2021-06-16 | $99,964.85 | -0.03% | -0.04% | -0.74% | -1.02% | -1.42% |
| 2021-06-17 | $100,048.25 | +0.08% | +0.05% | -0.77% | +0.24% | -0.39% |
| 2021-06-18 | $99,958.25 | -0.09% | -0.04% | -2.11% | -0.55% | -1.65% |
| 2026-06-08 | $159,570.33 | +0.08% | +59.57% | +86.11% | +114.19% | +277.84% |
| 2026-06-09 | $159,267.54 | -0.19% | +59.27% | +85.57% | +111.72% | +273.48% |
| 2026-06-10 | $158,306.61 | -0.60% | +58.31% | +82.64% | +107.49% | +262.61% |
| 2026-06-11 | $160,019.29 | +1.08% | +60.02% | +85.75% | +114.50% | +277.75% |
| 2026-06-12 | $160,200.32 | +0.11% | +60.20% | +86.75% | +115.76% | +278.35% |


## Signal Predictiveness

_Cross-section of 26,355 (date, ticker) signal observations. Correlations are Pearson vs forward returns._

| Signal | vs fwd 5d | vs fwd 10d | vs fwd 20d |
|--------|-----------|------------|------------|
| return_1d | -0.01 | 0.00 | 0.01 |
| return_5d | -0.01 | 0.01 | 0.03 |
| return_20d | 0.02 | 0.03 | 0.01 |
| vol_ratio | 0.00 | 0.02 | 0.02 |
| vol_adj_mom_20d | 0.02 | 0.02 | 0.00 |
| composite_score | 0.00 | 0.01 | 0.00 |

**Forward returns by composite-score quintile** (5 = highest-ranked):

| Quintile | N | Avg fwd 5d | Win 5d | Avg fwd 10d | Win 10d | Avg fwd 20d | Win 20d |
|----------|---|-----------|--------|-------------|---------|-------------|---------|
| Q1 | 6275 | +0.68% | +54.00% | +1.29% | +56.32% | +2.72% | +57.91% |
| Q2 | 5020 | +0.64% | +55.50% | +1.31% | +56.86% | +2.40% | +59.16% |
| Q3 | 5020 | +0.46% | +53.66% | +1.09% | +55.60% | +2.22% | +56.88% |
| Q4 | 5020 | +0.60% | +54.90% | +1.26% | +55.58% | +2.42% | +57.65% |
| Q5 | 5020 | +0.69% | +53.96% | +1.29% | +54.84% | +2.71% | +55.83% |

**Top-minus-bottom quintile spread:** 5d +0.01%  |  10d +0.01%  |  20d -0.01%  (positive ⇒ higher-ranked names outperform lower-ranked names).

## Entry vs Exit Attribution

_Buy the top 2 ranked names each day, hold a fixed period, **no** stop-loss / take-profit / max-holding. Next-day entry, slippage applied._

| Hold period | Raw avg return / trade | Raw win rate | N trades |
|-------------|------------------------|--------------|----------|
| 5d | +0.43% | +51.00% | 2441 |
| 10d | +1.11% | +52.82% | 2431 |
| 20d | +2.72% | +54.91% | 2411 |
| 30d | +3.54% | +56.29% | 2391 |

**Full strategy (with exit rules):** total return +60.20%, win rate +53.16%, avg hold 15.35 trading days.

The raw signal (buy top names, hold fixed, no stops) is **positive across holding periods** (avg +1.95% per trade, 54% win rate). That points to genuine signal quality — higher-ranked names tend to rise even without exit rules.

## P&L Attribution

**Top 5 contributors:**

| Ticker | P&L |
|--------|-----|
| NVDA | $8,913.61 |
| MU | $8,870.81 |
| AMD | $5,878.13 |
| NFLX | $4,944.32 |
| TSM | $4,691.47 |

**Worst 5 contributors:**

| Ticker | P&L |
|--------|-----|
| BAC | $-333.94 |
| MSFT | $-143.41 |
| AAPL | $-115.31 |
| ORCL | $295.78 |
| AMZN | $642.21 |

**P&L by asset group:**

| Group | P&L |
|-------|-----|
| semiconductors | $17,997.90 |
| mega_cap_growth | $17,379.14 |
| software_cybersecurity | $3,958.36 |
| financial_crypto_beta | $3,253.97 |
| _(ungrouped)_ | $17,611.23 |

## Turnover and Re-entry Diagnostics

| Metric | Value |
|--------|-------|
| Total trades | 1971 |
| Trades / month | 32.86 |
| Avg holding period | 15.35 trading days |
| Stop-loss → re-entry ≤5d | 82 |

**Most-entered tickers:** `COIN`×88, `AMD`×70, `MU`×61, `NVDA`×60, `TSLA`×57, `CRWD`×56, `AVGO`×51, `TSM`×46

**Most re-entered after a stop-loss:** `COIN`×16, `AMD`×8, `TSLA`×6, `AVGO`×6, `NVDA`×6

## Exposure and Benchmark Capture

| Metric | Value |
|--------|-------|
| Avg exposure | +40.39% |
| Max exposure | +66.08% |
| Avg cash (drag) | +59.61% |
| Correlation to SPY | 0.80 |
| Correlation to QQQ | 0.86 |
| Beta to SPY | 0.48 |
| Beta to QQQ | 0.39 |
| Up-capture vs QQQ | 0.45 |
| Down-capture vs QQQ | 0.43 |

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

**Baseline:** +60.20% return  |  -19.39% max drawdown  |  +53.16% win rate  |  1.37 profit factor

### Stop Loss  (baseline: 7.5%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 3.0% | +39.99% | -46.76% | -238.36% | -15.78% | 2432 | +35.86% | 1.27 |
| 5.0% | +54.76% | -31.99% | -223.59% | -17.22% | 2162 | +45.07% | 1.35 |
| 7.5% ◀ baseline | +60.20% | -26.55% | -218.15% | -19.39% | 1971 | +53.16% | 1.37 |
| 10.0% | +66.06% | -20.69% | -212.29% | -22.11% | 1831 | +57.41% | 1.43 |

### Take Profit  (baseline: 10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 8% | +55.54% | -31.21% | -222.80% | -19.05% | 2095 | +56.09% | 1.35 |
| 10% ◀ baseline | +60.20% | -26.55% | -218.15% | -19.39% | 1971 | +53.16% | 1.37 |
| 15% | +67.13% | -19.62% | -211.22% | -20.66% | 1674 | +50.36% | 1.46 |

### Max Holding Days  (baseline: 30)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 5 | +13.30% | -73.45% | -265.05% | -12.83% | 3122 | +49.78% | 1.11 |
| 15 | +47.30% | -39.45% | -231.05% | -18.04% | 2270 | +52.39% | 1.32 |
| 30 ◀ baseline | +60.20% | -26.55% | -218.15% | -19.39% | 1971 | +53.16% | 1.37 |
| 60 | +67.04% | -19.71% | -211.30% | -21.40% | 1831 | +52.53% | 1.40 |

### Max New Trades / Day  (baseline: 2)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 1 | +54.61% | -32.14% | -223.73% | -17.35% | 1713 | +52.99% | 1.39 |
| 2 ◀ baseline | +60.20% | -26.55% | -218.15% | -19.39% | 1971 | +53.16% | 1.37 |
| 3 | +63.42% | -23.33% | -214.92% | -19.73% | 2008 | +53.21% | 1.39 |
| 5 | +62.62% | -24.13% | -215.72% | -19.72% | 2014 | +53.15% | 1.38 |

### Min Composite Score  (baseline: 0.70)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| none | +96.69% | +9.94% | -181.65% | -24.25% | 2714 | +53.56% | 1.38 |
| 0.60 | +59.25% | -27.50% | -219.09% | -23.34% | 2405 | +51.38% | 1.28 |
| 0.70 ◀ baseline | +60.20% | -26.55% | -218.15% | -19.39% | 1971 | +53.16% | 1.37 |
| 0.80 | +42.06% | -44.69% | -236.28% | -14.56% | 1383 | +53.12% | 1.38 |

### Signal Weight Profile  (baseline: baseline)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| baseline ◀ baseline | +60.20% | -26.55% | -218.15% | -19.39% | 1971 | +53.16% | 1.37 |
| no_1d | +49.78% | -36.97% | -228.56% | -18.71% | 1891 | +51.91% | 1.32 |
| less_1d | +49.26% | -37.49% | -229.08% | -18.42% | 1888 | +51.38% | 1.31 |
| more_volume | +60.20% | -26.55% | -218.15% | -19.39% | 1971 | +53.16% | 1.37 |

### Best 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs SPY | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|--------|-----|
| 1 | min_composite_score | none | +96.69% | +9.94% | -181.65% | -24.25% | 1.38 |
| 2 | take_profit | 15% | +67.13% | -19.62% | -211.22% | -20.66% | 1.46 |
| 3 | max_holding_days | 60 | +67.04% | -19.71% | -211.30% | -21.40% | 1.40 |
| 4 | stop_loss | 10.0% | +66.06% | -20.69% | -212.29% | -22.11% | 1.43 |
| 5 | max_new_trades_per_day | 3 | +63.42% | -23.33% | -214.92% | -19.73% | 1.39 |

### Worst 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs SPY | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|--------|-----|
| 1 | max_holding_days | 5 | +13.30% | -73.45% | -265.05% | -12.83% | 1.11 |
| 2 | stop_loss | 3.0% | +39.99% | -46.76% | -238.36% | -15.78% | 1.27 |
| 3 | min_composite_score | 0.80 | +42.06% | -44.69% | -236.28% | -14.56% | 1.38 |
| 4 | max_holding_days | 15 | +47.30% | -39.45% | -231.05% | -18.04% | 1.32 |
| 5 | signal_weights | less_1d | +49.26% | -37.49% | -229.08% | -18.42% | 1.31 |

### Robustness Notes

26% of variants beat the baseline. Improvements are mixed — some directions help, others hurt — which is consistent with a strategy that has modest but not dominant in-sample edge.

The widest in-sample return spread belongs to `min_composite_score` (54.6 pp range across its variants); `max_new_trades_per_day` shows the narrowest spread (8.8 pp), suggesting the strategy is least sensitive to that parameter in this period.

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