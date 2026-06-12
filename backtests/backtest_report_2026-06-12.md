# AI Paper Trader — Backtest Report
**Period:** 2021-01-01 → 2026-06-12  |  **Generated:** 2026-06-12

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Ending Balance | $148,870.44 | $216,052.60 | $240,619.00 | $408,464.00 |
| Total Return | +48.87% | +116.05% | +140.62% | +308.46% |
| Max Drawdown | -19.47% | -24.50% | -35.12% | -41.24% |
| Excess vs SPY | -67.18% | — | — | — |
| Excess vs QQQ | -91.75% | — | — | — |
| Excess vs Equal-Wt | -259.59% | — | — | — |
| 1-Year Return | +12.21% | +24.27% | +35.82% | +55.52% |
| 2-Year Return | +16.57% | +41.84% | +56.89% | +94.62% |
| 3-Year Return | +44.60% | +79.62% | +107.88% | +216.34% |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $148,870.44 |
| **IRR (annualized, money-weighted)** | **+18.89%** |
| Total Return (on full $ portfolio) | +48.87% |
| Total Capital Deployed (all entries) | $4,003,595.96 |
| Avg Capital Deployed (snapshot) | $43,992.46 (+43.99% of portfolio) |
| Peak Capital Deployed (snapshot) | $81,116.90 (+81.12% of portfolio) |
| Time Invested | +99.93% of trading days |
| Trading Days | 1367 |
| Total Trades | 2371 (1191 buys, 1180 sells) |
| Win Rate | +51.44% |
| Average Win | $350.12 |
| Average Loss | $-285.90 |
| Profit Factor | 1.30 |
| Avg Holding Period | 15.6 approx. trading days |
| Largest Winner | $1,965.74 |
| Largest Loser | $-1,003.95 |
| Open Positions at End | 11 |
| Total Slippage Cost | $8,010.08 (+8.01% of start) |
| Avg Slippage / Trade | $3.38 |

_**IRR** is the annualized money-weighted (internal) rate of return on the capital actually put into positions: it solves for the rate that discounts the dated BUY outflows, SELL inflows, and the terminal mark-to-market of open positions to zero. It ignores idle cash, so it measures how the *deployed* capital performed, and is bounded at -100%. Being annualized, short backtests can extrapolate to large figures. **Total Return** is on the full starting portfolio (cash included) and is what the SPY/QQQ/Equal-Wt comparisons above use, since those benchmarks are fully invested._

## Strategy Parameters Used

| Parameter | Value |
|-----------|-------|
| Starting Portfolio | $100,000.00 |
| Max Position Size | 3.0% (auto: 75% ÷ 25 tickers) |
| Max Total Exposure | 75% |
| Max New Trades / Day | 2 |
| Stop Loss | 8% |
| Take Profit | 10% |
| Max Holding Period | 30 trading days |
| Slippage | 0.10% per fill |

## Ticker Universe

`NVDA`, `MSFT`, `AAPL`, `AMZN`, `GOOGL`, `META`, `TSLA`, `NFLX`, `AVGO`, `AMD`, `TSM`, `ASML`, `MU`, `ARM`, `CRM`, `ORCL`, `NOW`, `ADBE`, `CRWD`, `PANW`, `JPM`, `BAC`, `GS`, `COIN`, `COST`

## Trade Log (last 20 trades)

| Date | Action | Ticker | Shares | Price | Value | Reason | P&L | Hold Days |
|------|--------|--------|--------|-------|-------|--------|-----|-----------|
| 2026-06-03 | BUY | AVGO | 9 | $479.71 | $4,317.38 | momentum_score=0.814 | — | — |
| 2026-06-03 | SELL | NOW | 36 | $117.78 | $4,240.16 | stop_loss | $-655.70 | 1.4 |
| 2026-06-04 | BUY | CRWD | 6 | $719.81 | $4,318.85 | momentum_score=0.836 | — | — |
| 2026-06-04 | SELL | AVGO | 9 | $418.49 | $3,766.42 | stop_loss | $-550.96 | 0.7 |
| 2026-06-05 | BUY | GS | 4 | $1,039.72 | $4,158.87 | momentum_score=0.792 | — | — |
| 2026-06-05 | SELL | TSLA | 9 | $390.61 | $3,515.48 | stop_loss | $-389.47 | 17.1 |
| 2026-06-05 | SELL | AMD | 9 | $465.91 | $4,193.22 | stop_loss | $-346.32 | 7.1 |
| 2026-06-05 | SELL | ORCL | 20 | $213.47 | $4,269.33 | stop_loss | $-698.64 | 2.9 |
| 2026-06-05 | SELL | ARM | 11 | $342.59 | $3,768.46 | stop_loss | $-665.78 | 2.1 |
| 2026-06-05 | SELL | CRM | 21 | $185.00 | $3,884.93 | stop_loss | $-326.05 | 2.1 |
| 2026-06-08 | SELL | AMZN | 16 | $244.97 | $3,919.60 | stop_loss | $-325.60 | 27.9 |
| 2026-06-08 | SELL | CRWD | 6 | $658.13 | $3,948.79 | stop_loss | $-370.07 | 2.9 |
| 2026-06-09 | BUY | MU | 4 | $936.83 | $3,747.30 | momentum_score=0.738 | — | — |
| 2026-06-10 | BUY | JPM | 14 | $309.45 | $4,332.29 | momentum_score=0.796 | — | — |
| 2026-06-10 | BUY | TSM | 10 | $408.20 | $4,082.03 | momentum_score=0.786 | — | — |
| 2026-06-11 | BUY | BAC | 80 | $55.22 | $4,417.22 | momentum_score=0.726 | — | — |
| 2026-06-11 | BUY | NFLX | 53 | $81.35 | $4,311.62 | momentum_score=0.704 | — | — |
| 2026-06-11 | SELL | META | 6 | $567.86 | $3,407.17 | max_holding_period | $-267.96 | 30.0 |
| 2026-06-11 | SELL | ASML | 2 | $1,897.58 | $3,795.16 | take_profit | $527.84 | 11.4 |
| 2026-06-12 | BUY | ASML | 2 | $1,865.41 | $3,730.83 | momentum_score=0.916 | — | — |

## Open Positions at End of Period

| Ticker | Shares | Entry Price | Final Price | Unrealized P&L | Entry Date |
|--------|--------|------------|------------|----------------|------------|
| GOOGL | 11 | $383.40 | $359.68 | $-260.97 | 2026-05-04 |
| AAPL | 15 | $287.53 | $291.13 | $53.96 | 2026-05-06 |
| NVDA | 20 | $215.16 | $205.19 | $-199.49 | 2026-05-08 |
| PANW | 15 | $280.71 | $279.62 | $-16.36 | 2026-06-03 |
| GS | 4 | $1,039.72 | $1,062.75 | $92.13 | 2026-06-05 |
| MU | 4 | $936.83 | $981.61 | $179.14 | 2026-06-09 |
| JPM | 14 | $309.45 | $320.72 | $157.79 | 2026-06-10 |
| TSM | 10 | $408.20 | $423.93 | $157.27 | 2026-06-10 |
| BAC | 80 | $55.22 | $56.02 | $64.38 | 2026-06-11 |
| NFLX | 53 | $81.35 | $80.34 | $-53.60 | 2026-06-11 |
| ASML | 2 | $1,865.41 | $1,863.55 | $-3.73 | 2026-06-12 |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2021-01-04 | $100,000.00 | — | +0.00% | +0.00% | +0.00% | +0.00% |
| 2021-01-05 | $99,994.12 | -0.01% | -0.01% | +0.69% | +0.82% | +0.94% |
| 2021-01-06 | $99,976.99 | -0.02% | -0.02% | +1.29% | -0.57% | -0.03% |
| 2021-01-07 | $100,329.77 | +0.35% | +0.33% | +2.80% | +1.83% | +3.04% |
| 2021-01-08 | $100,190.75 | -0.14% | +0.19% | +3.38% | +3.14% | +3.76% |
| 2026-06-08 | $148,172.01 | -0.04% | +48.17% | +115.32% | +138.86% | +309.58% |
| 2026-06-09 | $147,918.42 | -0.17% | +47.92% | +114.68% | +136.11% | +305.06% |
| 2026-06-10 | $147,256.14 | -0.45% | +47.26% | +111.30% | +131.40% | +293.38% |
| 2026-06-11 | $148,712.18 | +0.99% | +48.71% | +114.89% | +139.21% | +308.18% |
| 2026-06-12 | $148,870.44 | +0.11% | +48.87% | +116.05% | +140.62% | +308.46% |


## Sensitivity Analysis

> One parameter is varied at a time; all others remain at baseline values.
> Do not select parameters based on in-sample performance alone — see Robustness Notes below.

**Baseline:** +48.87% return  |  -19.47% max drawdown  |  +51.44% win rate  |  1.30 profit factor

### Stop Loss  (baseline: 7.5%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 3.0% | +34.67% | -81.39% | -273.80% | -14.87% | 2942 | +35.08% | 1.23 |
| 5.0% | +45.14% | -70.91% | -263.32% | -17.64% | 2615 | +44.13% | 1.28 |
| 7.5% ◀ baseline | +48.87% | -67.18% | -259.59% | -19.47% | 2371 | +51.44% | 1.30 |
| 10.0% | +49.04% | -67.01% | -259.42% | -22.69% | 2215 | +55.58% | 1.31 |

### Take Profit  (baseline: 10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 8% | +49.10% | -66.95% | -259.36% | -18.58% | 2526 | +55.12% | 1.30 |
| 10% ◀ baseline | +48.87% | -67.18% | -259.59% | -19.47% | 2371 | +51.44% | 1.30 |
| 15% | +53.57% | -62.48% | -254.89% | -20.28% | 2050 | +48.82% | 1.35 |

### Max Holding Days  (baseline: 30)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 5 | +11.70% | -104.35% | -296.76% | -13.18% | 3734 | +50.19% | 1.09 |
| 15 | +43.54% | -72.51% | -264.92% | -17.39% | 2739 | +52.75% | 1.29 |
| 30 ◀ baseline | +48.87% | -67.18% | -259.59% | -19.47% | 2371 | +51.44% | 1.30 |
| 60 | +62.22% | -53.84% | -246.25% | -21.79% | 2195 | +51.28% | 1.36 |

### Max New Trades / Day  (baseline: 2)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 1 | +35.86% | -80.19% | -272.60% | -17.85% | 2020 | +51.19% | 1.26 |
| 2 ◀ baseline | +48.87% | -67.18% | -259.59% | -19.47% | 2371 | +51.44% | 1.30 |
| 3 | +57.25% | -58.80% | -251.22% | -20.54% | 2427 | +51.99% | 1.34 |
| 5 | +57.67% | -58.38% | -250.79% | -20.63% | 2442 | +52.18% | 1.34 |

### Min Composite Score  (baseline: 0.70)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| none | +87.13% | -28.92% | -221.33% | -26.16% | 3236 | +52.89% | 1.35 |
| 0.60 | +61.36% | -54.69% | -247.11% | -26.39% | 2978 | +51.21% | 1.29 |
| 0.70 ◀ baseline | +48.87% | -67.18% | -259.59% | -19.47% | 2371 | +51.44% | 1.30 |
| 0.80 | +35.29% | -80.76% | -273.18% | -14.88% | 1677 | +52.27% | 1.31 |

### Signal Weight Profile  (baseline: baseline)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| baseline ◀ baseline | +48.87% | -67.18% | -259.59% | -19.47% | 2371 | +51.44% | 1.30 |
| no_1d | +47.44% | -68.61% | -261.03% | -19.89% | 2307 | +51.52% | 1.30 |
| less_1d | +47.16% | -68.89% | -261.30% | -19.83% | 2291 | +51.62% | 1.30 |
| more_volume | +48.87% | -67.18% | -259.59% | -19.47% | 2371 | +51.44% | 1.30 |

### Best 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs SPY | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|--------|-----|
| 1 | min_composite_score | none | +87.13% | -28.92% | -221.33% | -26.16% | 1.35 |
| 2 | max_holding_days | 60 | +62.22% | -53.84% | -246.25% | -21.79% | 1.36 |
| 3 | min_composite_score | 0.60 | +61.36% | -54.69% | -247.11% | -26.39% | 1.29 |
| 4 | max_new_trades_per_day | 5 | +57.67% | -58.38% | -250.79% | -20.63% | 1.34 |
| 5 | max_new_trades_per_day | 3 | +57.25% | -58.80% | -251.22% | -20.54% | 1.34 |

### Worst 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs SPY | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|--------|-----|
| 1 | max_holding_days | 5 | +11.70% | -104.35% | -296.76% | -13.18% | 1.09 |
| 2 | stop_loss | 3.0% | +34.67% | -81.39% | -273.80% | -14.87% | 1.23 |
| 3 | min_composite_score | 0.80 | +35.29% | -80.76% | -273.18% | -14.88% | 1.31 |
| 4 | max_new_trades_per_day | 1 | +35.86% | -80.19% | -272.60% | -17.85% | 1.26 |
| 5 | max_holding_days | 15 | +43.54% | -72.51% | -264.92% | -17.39% | 1.29 |

### Robustness Notes

35% of variants beat the baseline. Improvements are mixed — some directions help, others hurt — which is consistent with a strategy that has modest but not dominant in-sample edge.

The widest in-sample return spread belongs to `min_composite_score` (51.8 pp range across its variants); `signal_weights` shows the narrowest spread (1.7 pp), suggesting the strategy is least sensitive to that parameter in this period.

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