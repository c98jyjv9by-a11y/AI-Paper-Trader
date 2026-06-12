# AI Paper Trader — Backtest Report
**Period:** 2021-01-01 → 2026-06-12  |  **Generated:** 2026-06-12

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Total Return | -5.40% | +116.05% | +140.62% | +87.99% |
| Max Drawdown | -8.11% | -24.50% | -35.12% | -58.45% |
| Excess vs SPY | -121.45% | — | — | — |
| Excess vs QQQ | -146.02% | — | — | — |
| Excess vs Equal-Wt | -93.39% | — | — | — |
| 1-Year Return | +1.78% | +24.27% | +35.82% | +100.49% |
| 2-Year Return | +0.26% | +41.84% | +56.89% | +117.73% |
| 3-Year Return | +0.70% | +79.62% | +107.88% | +234.91% |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $94,599.83 |
| Trading Days | 1367 |
| Total Trades | 444 (223 buys, 221 sells) |
| Win Rate | +35.29% |
| Average Win | $790.18 |
| Average Loss | $-468.14 |
| Profit Factor | 0.92 |
| Avg Holding Period | 10.1 approx. trading days |
| Largest Winner | $1,562.02 |
| Largest Loser | $-1,506.38 |
| Open Positions at End | 2 |
| Total Slippage Cost | $2,060.06 (+2.06% of start) |
| Avg Slippage / Trade | $4.64 |

## Strategy Parameters Used

| Parameter | Value |
|-----------|-------|
| Starting Portfolio | $100,000.00 |
| Max Position Size | 5% |
| Max Total Exposure | 75% |
| Max New Trades / Day | 1 |
| Stop Loss | 8% |
| Take Profit | 15% |
| Max Holding Period | 30 trading days |
| Slippage | 0.10% per fill |

## Ticker Universe

`TQQQ`, `SQQQ`

## Trade Log (last 20 trades)

| Date | Action | Ticker | Shares | Price | Value | Reason | P&L | Hold Days |
|------|--------|--------|--------|-------|-------|--------|-----|-----------|
| 2026-04-08 | SELL | SQQQ | 52 | $69.13 | $3,594.80 | stop_loss | $-594.86 | 5.7 |
| 2026-04-09 | BUY | SQQQ | 67 | $67.93 | $4,551.17 | momentum_score=0.825 | $nan | — |
| 2026-04-13 | SELL | TQQQ | 108 | $50.61 | $5,465.80 | take_profit | $781.49 | 7.9 |
| 2026-04-14 | BUY | TQQQ | 92 | $53.46 | $4,918.63 | momentum_score=0.825 | $nan | — |
| 2026-04-14 | SELL | SQQQ | 67 | $61.96 | $4,151.19 | stop_loss | $-399.98 | 3.6 |
| 2026-04-21 | BUY | SQQQ | 82 | $57.65 | $4,727.10 | momentum_score=0.725 | $nan | — |
| 2026-04-24 | SELL | TQQQ | 92 | $62.50 | $5,749.76 | take_profit | $831.13 | 7.1 |
| 2026-04-24 | SELL | SQQQ | 82 | $52.45 | $4,300.69 | stop_loss | $-426.41 | 2.1 |
| 2026-04-27 | BUY | TQQQ | 75 | $62.70 | $4,702.69 | momentum_score=0.825 | $nan | — |
| 2026-05-05 | BUY | SQQQ | 93 | $48.64 | $4,523.39 | momentum_score=0.725 | $nan | — |
| 2026-05-08 | SELL | TQQQ | 75 | $76.20 | $5,715.28 | take_profit | $1,012.58 | 7.9 |
| 2026-05-08 | SELL | SQQQ | 93 | $42.53 | $3,955.05 | stop_loss | $-568.34 | 2.1 |
| 2026-05-11 | BUY | TQQQ | 62 | $77.04 | $4,776.29 | momentum_score=0.825 | $nan | — |
| 2026-05-13 | BUY | SQQQ | 109 | $42.03 | $4,581.49 | momentum_score=0.725 | $nan | — |
| 2026-05-28 | SELL | SQQQ | 109 | $38.43 | $4,189.03 | stop_loss | $-392.45 | 10.7 |
| 2026-06-04 | BUY | SQQQ | 127 | $37.80 | $4,800.32 | momentum_score=0.725 | $nan | — |
| 2026-06-10 | SELL | TQQQ | 62 | $69.20 | $4,290.44 | stop_loss | $-485.85 | 21.4 |
| 2026-06-10 | SELL | SQQQ | 127 | $45.20 | $5,741.00 | take_profit | $940.68 | 4.3 |
| 2026-06-11 | BUY | SQQQ | 104 | $40.87 | $4,250.56 | momentum_score=1.0 | $nan | — |
| 2026-06-12 | BUY | TQQQ | 62 | $77.60 | $4,811.05 | momentum_score=0.7 | $nan | — |

## Open Positions at End of Period

| Ticker | Shares | Entry Price | Final Price | Unrealized P&L | Entry Date |
|--------|--------|------------|------------|----------------|------------|
| SQQQ | 104 | $40.87 | $40.04 | $-86.40 | 2026-06-11 |
| TQQQ | 62 | $77.60 | $77.52 | $-4.81 | 2026-06-12 |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2021-01-04 | $100,000.00 | +nan% | +0.00% | +0.00% | +0.00% | +0.00% |
| 2021-01-05 | $99,995.32 | -0.00% | -0.00% | +0.69% | +0.82% | +0.02% |
| 2021-01-06 | $100,184.10 | +0.19% | +0.18% | +1.29% | -0.57% | -0.08% |
| 2021-01-07 | $100,165.96 | -0.02% | +0.17% | +2.80% | +1.83% | -0.32% |
| 2021-01-08 | $100,197.97 | +0.03% | +0.20% | +3.38% | +3.14% | -0.01% |
| 2026-06-08 | $94,628.36 | -0.05% | -5.37% | +115.32% | +138.86% | +85.02% |
| 2026-06-09 | $94,649.33 | +0.02% | -5.35% | +114.68% | +136.11% | +78.92% |
| 2026-06-10 | $94,691.04 | +0.04% | -5.31% | +111.30% | +131.40% | +68.28% |
| 2026-06-11 | $94,686.80 | -0.00% | -5.31% | +114.89% | +139.21% | +84.38% |
| 2026-06-12 | $94,599.83 | -0.09% | -5.40% | +116.05% | +140.62% | +87.99% |


## Sensitivity Analysis

> One parameter is varied at a time; all others remain at baseline values.
> Do not select parameters based on in-sample performance alone — see Robustness Notes below.

**Baseline:** -5.40% return  |  -8.11% max drawdown  |  +35.29% win rate  |  0.92 profit factor

### Stop Loss  (baseline: 7.5%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 3.0% | -12.08% | -128.14% | -100.08% | -15.40% | 670 | +21.86% | 0.82 |
| 5.0% | -9.96% | -126.01% | -97.95% | -13.40% | 522 | +26.92% | 0.85 |
| 7.5% ◀ baseline | -5.40% | -121.45% | -93.39% | -8.11% | 444 | +35.29% | 0.92 |
| 10.0% | -6.17% | -122.23% | -94.17% | -6.89% | 378 | +40.43% | 0.91 |

### Take Profit  (baseline: 15%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 8% | -8.27% | -124.33% | -96.27% | -11.85% | 604 | +46.84% | 0.89 |
| 10% | -6.22% | -122.27% | -94.21% | -8.10% | 528 | +43.73% | 0.91 |
| 15% ◀ baseline | -5.40% | -121.45% | -93.39% | -8.11% | 444 | +35.29% | 0.92 |

### Max Holding Days  (baseline: 30)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 5 | -8.49% | -124.54% | -96.48% | -10.44% | 832 | +45.06% | 0.88 |
| 15 | -6.90% | -122.95% | -94.89% | -8.74% | 518 | +38.76% | 0.90 |
| 30 ◀ baseline | -5.40% | -121.45% | -93.39% | -8.11% | 444 | +35.29% | 0.92 |
| 60 | -5.43% | -121.48% | -93.42% | -7.33% | 430 | +34.58% | 0.92 |

### Max New Trades / Day  (baseline: 1)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 1 ◀ baseline | -5.40% | -121.45% | -93.39% | -8.11% | 444 | +35.29% | 0.92 |
| 2 | -5.05% | -121.11% | -93.05% | -8.11% | 444 | +35.29% | 0.93 |
| 3 | -5.05% | -121.11% | -93.05% | -8.11% | 444 | +35.29% | 0.93 |
| 5 | -5.05% | -121.11% | -93.05% | -8.11% | 444 | +35.29% | 0.93 |

### Min Composite Score  (baseline: 0.70)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| none | -5.34% | -121.40% | -93.34% | -7.34% | 506 | +35.71% | 0.93 |
| 0.60 | -3.12% | -119.17% | -91.11% | -5.96% | 474 | +36.44% | 0.96 |
| 0.70 ◀ baseline | -5.40% | -121.45% | -93.39% | -8.11% | 444 | +35.29% | 0.92 |
| 0.80 | -4.72% | -120.77% | -92.71% | -8.03% | 387 | +36.27% | 0.92 |

### Signal Weight Profile  (baseline: baseline)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| baseline ◀ baseline | -5.40% | -121.45% | -93.39% | -8.11% | 444 | +35.29% | 0.92 |
| no_1d | -3.28% | -119.34% | -91.28% | -5.92% | 410 | +36.76% | 0.95 |
| less_1d | -4.45% | -120.50% | -92.45% | -7.12% | 414 | +36.41% | 0.93 |
| more_volume | -5.40% | -121.45% | -93.39% | -8.11% | 444 | +35.29% | 0.92 |

### Best 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs SPY | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|--------|-----|
| 1 | min_composite_score | 0.60 | -3.12% | -119.17% | -91.11% | -5.96% | 0.96 |
| 2 | signal_weights | no_1d | -3.28% | -119.34% | -91.28% | -5.92% | 0.95 |
| 3 | signal_weights | less_1d | -4.45% | -120.50% | -92.45% | -7.12% | 0.93 |
| 4 | min_composite_score | 0.80 | -4.72% | -120.77% | -92.71% | -8.03% | 0.92 |
| 5 | max_new_trades_per_day | 2 | -5.05% | -121.11% | -93.05% | -8.11% | 0.93 |

### Worst 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs SPY | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|--------|-----|
| 1 | stop_loss | 3.0% | -12.08% | -128.14% | -100.08% | -15.40% | 0.82 |
| 2 | stop_loss | 5.0% | -9.96% | -126.01% | -97.95% | -13.40% | 0.85 |
| 3 | max_holding_days | 5 | -8.49% | -124.54% | -96.48% | -10.44% | 0.88 |
| 4 | take_profit | 8% | -8.27% | -124.33% | -96.27% | -11.85% | 0.89 |
| 5 | max_holding_days | 15 | -6.90% | -122.95% | -94.89% | -8.74% | 0.90 |

### Robustness Notes

35% of variants beat the baseline. Improvements are mixed — some directions help, others hurt — which is consistent with a strategy that has modest but not dominant in-sample edge.

The widest in-sample return spread belongs to `stop_loss` (6.7 pp range across its variants); `max_new_trades_per_day` shows the narrowest spread (0.3 pp), suggesting the strategy is least sensitive to that parameter in this period.

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