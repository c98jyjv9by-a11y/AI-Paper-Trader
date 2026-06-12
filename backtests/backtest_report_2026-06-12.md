# AI Paper Trader — Backtest Report
**Period:** 2021-01-01 → 2026-06-12  |  **Generated:** 2026-06-12

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Ending Balance | $164,495.48 | $216,052.60 | $240,619.00 | $458,954.30 |
| Total Return | +64.50% | +116.05% | +140.62% | +358.95% |
| Max Drawdown | -19.42% | -24.50% | -35.12% | -39.53% |
| Excess vs SPY | -51.56% | — | — | — |
| Excess vs QQQ | -76.12% | — | — | — |
| Excess vs Equal-Wt | -294.46% | — | — | — |
| 1-Year Return | +18.27% | +24.27% | +35.82% | +62.69% |
| 2-Year Return | +26.60% | +41.84% | +56.89% | +104.52% |
| 3-Year Return | +55.16% | +79.62% | +107.88% | +242.17% |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $164,495.48 |
| **IRR (annualized, money-weighted)** | **+22.21%** |
| Total Return (on full $ portfolio) | +64.50% |
| Total Capital Deployed (all entries) | $4,404,833.32 |
| Avg Capital Deployed (snapshot) | $48,047.84 (+48.05% of portfolio) |
| Peak Capital Deployed (snapshot) | $93,602.02 (+93.60% of portfolio) |
| Time Invested | +99.93% of trading days |
| Trading Days | 1367 |
| Total Trades | 2113 (1062 buys, 1051 sells) |
| Win Rate | +52.90% |
| Average Win | $427.99 |
| Average Loss | $-350.97 |
| Profit Factor | 1.37 |
| Avg Holding Period | 15.5 approx. trading days |
| Largest Winner | $1,417.91 |
| Largest Loser | $-1,268.15 |
| Open Positions at End | 11 |
| Total Slippage Cost | $8,812.54 (+8.81% of start) |
| Avg Slippage / Trade | $4.17 |

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
| 2026-06-04 | SELL | GS | 6 | $1,091.52 | $6,549.10 | take_profit | $640.20 | 10.0 |
| 2026-06-04 | SELL | AVGO | 12 | $418.49 | $5,021.89 | stop_loss | $-734.62 | 0.7 |
| 2026-06-05 | BUY | GS | 5 | $1,039.72 | $5,198.59 | momentum_score=0.8048 | — | — |
| 2026-06-05 | SELL | TSLA | 13 | $390.61 | $5,077.92 | stop_loss | $-562.57 | 17.1 |
| 2026-06-05 | SELL | AMD | 12 | $465.91 | $5,590.96 | stop_loss | $-461.76 | 7.1 |
| 2026-06-05 | SELL | ORCL | 26 | $213.47 | $5,550.12 | stop_loss | $-908.23 | 2.9 |
| 2026-06-05 | SELL | PANW | 21 | $271.78 | $5,707.34 | stop_loss | $-609.05 | 2.9 |
| 2026-06-05 | SELL | CRWD | 7 | $670.35 | $4,692.44 | stop_loss | $-695.59 | 2.1 |
| 2026-06-08 | SELL | AMZN | 21 | $244.97 | $5,144.47 | stop_loss | $-427.36 | 27.9 |
| 2026-06-09 | BUY | MU | 6 | $936.83 | $5,620.96 | momentum_score=0.7024 | — | — |
| 2026-06-09 | SELL | MSFT | 13 | $403.01 | $5,239.09 | stop_loss | $-503.68 | 5.0 |
| 2026-06-10 | BUY | JPM | 18 | $309.45 | $5,570.09 | momentum_score=0.8024 | — | — |
| 2026-06-10 | BUY | TSM | 13 | $408.20 | $5,306.64 | momentum_score=0.7738 | — | — |
| 2026-06-11 | BUY | BAC | 106 | $55.22 | $5,852.81 | momentum_score=0.719 | — | — |
| 2026-06-11 | BUY | NFLX | 70 | $81.35 | $5,694.59 | momentum_score=0.7048 | — | — |
| 2026-06-11 | SELL | META | 8 | $567.86 | $4,542.89 | max_holding_period | $-357.28 | 30.0 |
| 2026-06-11 | SELL | ASML | 3 | $1,897.58 | $5,692.74 | take_profit | $791.76 | 11.4 |
| 2026-06-12 | BUY | ASML | 3 | $1,865.41 | $5,596.24 | momentum_score=0.9357 | — | — |
| 2026-06-12 | BUY | PANW | 20 | $279.90 | $5,597.99 | momentum_score=0.7048 | — | — |

## Open Positions at End of Period

| Ticker | Shares | Entry Price | Final Price | Unrealized P&L | Entry Date |
|--------|--------|------------|------------|----------------|------------|
| GOOGL | 14 | $383.40 | $359.68 | $-332.14 | 2026-05-04 |
| AAPL | 20 | $287.53 | $291.13 | $71.95 | 2026-05-06 |
| NVDA | 27 | $215.16 | $205.19 | $-269.31 | 2026-05-08 |
| GS | 5 | $1,039.72 | $1,062.75 | $115.16 | 2026-06-05 |
| MU | 6 | $936.83 | $981.61 | $268.70 | 2026-06-09 |
| JPM | 18 | $309.45 | $320.72 | $202.87 | 2026-06-10 |
| TSM | 13 | $408.20 | $423.93 | $204.45 | 2026-06-10 |
| BAC | 106 | $55.22 | $56.02 | $85.31 | 2026-06-11 |
| NFLX | 70 | $81.35 | $80.34 | $-70.79 | 2026-06-11 |
| ASML | 3 | $1,865.41 | $1,863.55 | $-5.59 | 2026-06-12 |
| PANW | 20 | $279.90 | $279.62 | $-5.59 | 2026-06-12 |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2021-01-04 | $100,000.00 | — | +0.00% | +0.00% | +0.00% | +0.00% |
| 2021-01-05 | $99,993.13 | -0.01% | -0.01% | +0.69% | +0.82% | +1.00% |
| 2021-01-06 | $99,973.47 | -0.02% | -0.03% | +1.29% | -0.57% | +0.45% |
| 2021-01-07 | $100,388.83 | +0.42% | +0.39% | +2.80% | +1.83% | +3.78% |
| 2021-01-08 | $100,219.23 | -0.17% | +0.22% | +3.38% | +3.14% | +4.26% |
| 2026-06-08 | $163,887.68 | +0.07% | +63.89% | +115.32% | +138.86% | +358.87% |
| 2026-06-09 | $163,564.72 | -0.20% | +63.56% | +114.68% | +136.11% | +354.25% |
| 2026-06-10 | $162,597.05 | -0.59% | +62.60% | +111.30% | +131.40% | +341.01% |
| 2026-06-11 | $164,317.91 | +1.06% | +64.32% | +114.89% | +139.21% | +358.42% |
| 2026-06-12 | $164,495.48 | +0.11% | +64.50% | +116.05% | +140.62% | +358.95% |


## Signal Predictiveness

_Cross-section of 28,597 (date, ticker) signal observations. Correlations are Pearson vs forward returns._

| Signal | vs fwd 5d | vs fwd 10d | vs fwd 20d |
|--------|-----------|------------|------------|
| return_1d | -0.01 | -0.00 | 0.01 |
| return_5d | -0.02 | 0.01 | 0.02 |
| return_20d | 0.02 | 0.02 | 0.00 |
| vol_ratio | 0.01 | 0.02 | 0.02 |
| composite_score | 0.00 | 0.00 | 0.00 |

**Forward returns by composite-score quintile** (5 = highest-ranked):

| Quintile | N | Avg fwd 5d | Win 5d | Avg fwd 10d | Win 10d | Avg fwd 20d | Win 20d |
|----------|---|-----------|--------|-------------|---------|-------------|---------|
| Q1 | 6741 | +0.66% | +53.86% | +1.29% | +56.54% | +2.75% | +58.38% |
| Q2 | 5464 | +0.64% | +55.43% | +1.32% | +57.11% | +2.47% | +59.78% |
| Q3 | 5464 | +0.48% | +54.11% | +1.10% | +55.75% | +2.26% | +57.42% |
| Q4 | 5464 | +0.62% | +55.58% | +1.25% | +55.88% | +2.39% | +58.11% |
| Q5 | 5464 | +0.66% | +53.98% | +1.25% | +54.97% | +2.62% | +56.14% |

**Top-minus-bottom quintile spread:** 5d +0.00%  |  10d -0.05%  |  20d -0.13%  (positive ⇒ higher-ranked names outperform lower-ranked names).

## Entry vs Exit Attribution

_Buy the top 2 ranked names each day, hold a fixed period, **no** stop-loss / take-profit / max-holding. Next-day entry, slippage applied._

| Hold period | Raw avg return / trade | Raw win rate | N trades |
|-------------|------------------------|--------------|----------|
| 5d | +0.42% | +51.13% | 2662 |
| 10d | +1.07% | +53.05% | 2652 |
| 20d | +2.65% | +55.43% | 2632 |
| 30d | +3.46% | +56.81% | 2612 |

**Full strategy (with exit rules):** total return +64.50%, win rate +52.90%, avg hold 15.52 trading days.

The raw signal (buy top names, hold fixed, no stops) is **positive across holding periods** (avg +1.90% per trade, 54% win rate). That points to genuine signal quality — higher-ranked names tend to rise even without exit rules.

## P&L Attribution

**Top 5 contributors:**

| Ticker | P&L |
|--------|-----|
| NVDA | $9,906.06 |
| MU | $8,741.64 |
| AMD | $6,233.52 |
| TSM | $5,054.35 |
| NFLX | $4,583.78 |

**Worst 5 contributors:**

| Ticker | P&L |
|--------|-----|
| AAPL | $-566.44 |
| BAC | $-165.32 |
| MSFT | $136.13 |
| AMZN | $223.99 |
| ORCL | $413.63 |

**P&L by asset group:**

| Group | P&L |
|-------|-----|
| mega_cap_growth | $18,951.43 |
| semiconductors | $17,972.51 |
| software_cybersecurity | $4,859.45 |
| financial_crypto_beta | $3,237.76 |
| _(ungrouped)_ | $19,474.24 |

## Turnover and Re-entry Diagnostics

| Metric | Value |
|--------|-------|
| Total trades | 2113 |
| Trades / month | 32.35 |
| Avg holding period | 15.52 trading days |
| Stop-loss → re-entry ≤5d | 84 |

**Most-entered tickers:** `COIN`×88, `AMD`×72, `MU`×65, `NVDA`×64, `CRWD`×62, `TSLA`×61, `AVGO`×54, `ASML`×52

**Most re-entered after a stop-loss:** `COIN`×16, `TSLA`×7, `AMD`×7, `ASML`×6, `AVGO`×6

## Exposure and Benchmark Capture

| Metric | Value |
|--------|-------|
| Avg exposure | +40.34% |
| Max exposure | +66.06% |
| Avg cash (drag) | +59.66% |
| Correlation to SPY | 0.80 |
| Correlation to QQQ | 0.85 |
| Beta to SPY | 0.48 |
| Beta to QQQ | 0.38 |
| Up-capture vs QQQ | 0.43 |
| Down-capture vs QQQ | 0.42 |

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

**Baseline:** +64.50% return  |  -19.42% max drawdown  |  +52.90% win rate  |  1.37 profit factor

### Stop Loss  (baseline: 7.5%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 3.0% | +43.39% | -72.66% | -315.56% | -15.89% | 2610 | +35.94% | 1.27 |
| 5.0% | +60.12% | -55.93% | -298.83% | -17.33% | 2312 | +45.26% | 1.35 |
| 7.5% ◀ baseline | +64.50% | -51.56% | -294.46% | -19.42% | 2113 | +52.90% | 1.37 |
| 10.0% | +70.22% | -45.84% | -288.74% | -22.20% | 1965 | +57.36% | 1.42 |

### Take Profit  (baseline: 10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 8% | +61.20% | -54.86% | -297.76% | -19.10% | 2249 | +56.07% | 1.35 |
| 10% ◀ baseline | +64.50% | -51.56% | -294.46% | -19.42% | 2113 | +52.90% | 1.37 |
| 15% | +69.80% | -46.26% | -289.16% | -20.58% | 1790 | +50.11% | 1.44 |

### Max Holding Days  (baseline: 30)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 5 | +17.04% | -99.02% | -341.92% | -12.78% | 3404 | +50.41% | 1.12 |
| 15 | +51.40% | -64.66% | -307.56% | -17.96% | 2450 | +52.79% | 1.32 |
| 30 ◀ baseline | +64.50% | -51.56% | -294.46% | -19.42% | 2113 | +52.90% | 1.37 |
| 60 | +76.40% | -39.65% | -282.55% | -21.49% | 1965 | +52.61% | 1.41 |

### Max New Trades / Day  (baseline: 2)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 1 | +60.82% | -55.23% | -298.13% | -17.27% | 1843 | +52.94% | 1.40 |
| 2 ◀ baseline | +64.50% | -51.56% | -294.46% | -19.42% | 2113 | +52.90% | 1.37 |
| 3 | +67.77% | -48.28% | -291.18% | -19.68% | 2150 | +52.95% | 1.38 |
| 5 | +66.31% | -49.75% | -292.65% | -19.69% | 2158 | +52.94% | 1.37 |

### Min Composite Score  (baseline: 0.70)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| none | +106.81% | -9.24% | -252.14% | -24.94% | 2912 | +53.55% | 1.38 |
| 0.60 | +63.58% | -52.47% | -295.37% | -23.83% | 2593 | +51.20% | 1.28 |
| 0.70 ◀ baseline | +64.50% | -51.56% | -294.46% | -19.42% | 2113 | +52.90% | 1.37 |
| 0.80 | +41.82% | -74.23% | -317.13% | -14.55% | 1499 | +52.48% | 1.36 |

### Signal Weight Profile  (baseline: baseline)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| baseline ◀ baseline | +64.50% | -51.56% | -294.46% | -19.42% | 2113 | +52.90% | 1.37 |
| no_1d | +53.55% | -62.51% | -305.41% | -18.84% | 2039 | +51.77% | 1.31 |
| less_1d | +51.15% | -64.91% | -307.81% | -18.51% | 2032 | +51.19% | 1.30 |
| more_volume | +64.50% | -51.56% | -294.46% | -19.42% | 2113 | +52.90% | 1.37 |

### Best 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs SPY | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|--------|-----|
| 1 | min_composite_score | none | +106.81% | -9.24% | -252.14% | -24.94% | 1.38 |
| 2 | max_holding_days | 60 | +76.40% | -39.65% | -282.55% | -21.49% | 1.41 |
| 3 | stop_loss | 10.0% | +70.22% | -45.84% | -288.74% | -22.20% | 1.42 |
| 4 | take_profit | 15% | +69.80% | -46.26% | -289.16% | -20.58% | 1.44 |
| 5 | max_new_trades_per_day | 3 | +67.77% | -48.28% | -291.18% | -19.68% | 1.38 |

### Worst 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs SPY | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|--------|-----|
| 1 | max_holding_days | 5 | +17.04% | -99.02% | -341.92% | -12.78% | 1.12 |
| 2 | min_composite_score | 0.80 | +41.82% | -74.23% | -317.13% | -14.55% | 1.36 |
| 3 | stop_loss | 3.0% | +43.39% | -72.66% | -315.56% | -15.89% | 1.27 |
| 4 | signal_weights | less_1d | +51.15% | -64.91% | -307.81% | -18.51% | 1.30 |
| 5 | max_holding_days | 15 | +51.40% | -64.66% | -307.56% | -17.96% | 1.32 |

### Robustness Notes

26% of variants beat the baseline. Improvements are mixed — some directions help, others hurt — which is consistent with a strategy that has modest but not dominant in-sample edge.

The widest in-sample return spread belongs to `min_composite_score` (65.0 pp range across its variants); `max_new_trades_per_day` shows the narrowest spread (7.0 pp), suggesting the strategy is least sensitive to that parameter in this period.

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