# Scenario — davids_model

Trimmed to the only OOS-robust tickers (MSFT, ORCL, CRWD), each with its out-of-sample-best exit rule. Composite ranking drives entries; per-ticker entry filters not yet wired. In-sample-selected — validate before trusting.

**Universe (3):** MSFT, ORCL, CRWD

---

# AI Paper Trader — Backtest Report
**Period:** 2019-01-01 → 2026-06-13  |  **Generated:** 2026-06-13

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Ending Balance | $533,412.79 | $330,573.90 | $487,257.40 | $434,703.80 |
| Total Return | +433.41% | +230.57% | +387.26% | +334.70% |
| Max Drawdown | -37.01% | -33.72% | -35.12% | -46.41% |
| Excess vs SPY | +202.84% | — | — | — |
| Excess vs QQQ | +46.16% | — | — | — |
| Excess vs Equal-Wt | +98.71% | — | — | — |
| 1-Year Return | +3.46% | +24.27% | +35.82% | -12.44% |
| 2-Year Return | +48.56% | +41.84% | +56.89% | +16.20% |
| 3-Year Return | +113.24% | +79.62% | +107.88% | +46.50% |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $533,412.79 |
| **IRR (annualized, money-weighted)** | **+31.26%** |
| Total Return (on full $ portfolio) | +433.41% |
| Total Capital Deployed (all entries) | $21,488,191.47 |
| Avg Capital Deployed (snapshot) | $230,454.83 (+230.45% of portfolio) |
| Peak Capital Deployed (snapshot) | $587,118.13 (+587.12% of portfolio) |
| Time Invested | +99.95% of trading days |
| Trading Days | 1872 |
| Total Trades | 517 (260 buys, 257 sells) |
| Win Rate | +52.53% |
| Average Win | $10,063.05 |
| Average Loss | $-7,585.83 |
| Profit Factor | 1.47 |
| Avg Holding Period | 21.1 approx. trading days |
| Largest Winner | $55,856.60 |
| Largest Loser | $-28,259.83 |
| Open Positions at End | 3 |
| Total Slippage Cost | $42,921.35 (+42.92% of start) |
| Avg Slippage / Trade | $83.02 |

_**IRR** is the annualized money-weighted (internal) rate of return on the capital actually put into positions: it solves for the rate that discounts the dated BUY outflows, SELL inflows, and the terminal mark-to-market of open positions to zero. It ignores idle cash, so it measures how the *deployed* capital performed, and is bounded at -100%. Being annualized, short backtests can extrapolate to large figures. **Total Return** is on the full starting portfolio (cash included) and is what the SPY/QQQ/Equal-Wt comparisons above use, since those benchmarks are fully invested._

## Strategy Parameters Used

| Parameter | Value |
|-----------|-------|
| Starting Portfolio | $100,000.00 |
| Max Position Size | 30.0% (auto: 90% ÷ 3 tickers) |
| Max Total Exposure | 90% |
| Max New Trades / Day | 3 |
| Stop Loss | 8% |
| Take Profit | 10% |
| Max Holding Period | 30 trading days |
| Slippage | 0.10% per fill |

## Ticker Universe

`MSFT`, `ORCL`, `CRWD`

## Trade Log (last 20 trades)

| Date | Action | Ticker | Shares | Price | Value | Reason | P&L | Hold Days |
|------|--------|--------|--------|-------|-------|--------|-----|-----------|
| 2026-04-22 | SELL | CRWD | 326 | $466.21 | $151,985.54 | take_profit | $20,724.18 | 6.4 |
| 2026-04-23 | BUY | CRWD | 316 | $445.84 | $140,883.99 | momentum_score=0.6667 | — | — |
| 2026-05-08 | SELL | MSFT | 342 | $413.81 | $141,522.54 | max_holding_period | $19,649.17 | 30.0 |
| 2026-05-08 | SELL | CRWD | 316 | $527.24 | $166,608.54 | take_profit | $25,724.55 | 10.7 |
| 2026-05-11 | BUY | CRWD | 294 | $542.80 | $159,583.88 | momentum_score=0.9 | — | — |
| 2026-05-11 | BUY | MSFT | 375 | $412.18 | $154,567.46 | momentum_score=0.45 | — | — |
| 2026-05-20 | SELL | CRWD | 294 | $649.46 | $190,941.21 | take_profit | $31,357.33 | 6.4 |
| 2026-05-21 | BUY | CRWD | 252 | $648.88 | $163,517.31 | momentum_score=1.0 | — | — |
| 2026-05-29 | SELL | ORCL | 811 | $225.55 | $182,924.46 | take_profit | $38,146.11 | 30.7 |
| 2026-06-01 | BUY | ORCL | 809 | $248.40 | $200,954.06 | momentum_score=0.7833 | — | — |
| 2026-06-01 | SELL | CRWD | 252 | $781.39 | $196,909.73 | take_profit | $33,392.42 | 7.9 |
| 2026-06-02 | BUY | CRWD | 239 | $769.72 | $183,962.84 | momentum_score=0.65 | — | — |
| 2026-06-05 | SELL | ORCL | 809 | $213.47 | $172,694.24 | stop_loss | $-28,259.83 | 2.9 |
| 2026-06-05 | SELL | CRWD | 239 | $670.35 | $160,213.41 | stop_loss+trailing_stop | $-23,749.43 | 2.1 |
| 2026-06-08 | BUY | CRWD | 249 | $659.45 | $164,202.75 | momentum_score=0.8 | — | — |
| 2026-06-08 | BUY | ORCL | 782 | $212.03 | $165,808.87 | momentum_score=0.7167 | — | — |
| 2026-06-08 | SELL | MSFT | 375 | $411.33 | $154,248.11 | trailing_stop | $-319.35 | 20.0 |
| 2026-06-09 | BUY | MSFT | 404 | $403.81 | $163,140.61 | momentum_score=0.7667 | — | — |
| 2026-06-11 | SELL | ORCL | 782 | $183.92 | $143,822.23 | stop_loss | $-21,986.63 | 2.1 |
| 2026-06-12 | BUY | ORCL | 872 | $184.31 | $160,721.90 | momentum_score=0.6667 | — | — |

## Open Positions at End of Period

| Ticker | Shares | Entry Price | Final Price | Unrealized P&L | Entry Date |
|--------|--------|------------|------------|----------------|------------|
| CRWD | 249 | $659.45 | $682.80 | $5,814.45 | 2026-06-08 |
| MSFT | 404 | $403.81 | $390.74 | $-5,281.65 | 2026-06-09 |
| ORCL | 872 | $184.31 | $184.13 | $-160.54 | 2026-06-12 |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2019-01-02 | $100,000.00 | — | +0.00% | +0.00% | +0.00% | +0.00% |
| 2019-01-03 | $99,941.48 | -0.06% | -0.06% | -2.39% | -3.27% | -2.33% |
| 2019-01-04 | $102,562.66 | +2.62% | +2.56% | +0.88% | +0.87% | +2.05% |
| 2019-01-07 | $103,091.61 | +0.52% | +3.09% | +1.68% | +2.07% | +2.93% |
| 2019-01-08 | $103,595.89 | +0.49% | +3.60% | +2.63% | +3.00% | +3.77% |
| 2026-06-08 | $554,697.50 | -0.42% | +454.70% | +229.45% | +383.70% | +380.03% |
| 2026-06-09 | $546,383.57 | -1.50% | +446.38% | +228.48% | +378.13% | +368.19% |
| 2026-06-10 | $541,080.96 | -0.97% | +441.08% | +223.30% | +368.58% | +359.36% |
| 2026-06-11 | $535,585.50 | -1.02% | +435.59% | +228.80% | +384.41% | +334.45% |
| 2026-06-12 | $533,412.79 | -0.41% | +433.41% | +230.57% | +387.26% | +334.70% |


## Signal Predictiveness

_Cross-section of 5,482 (date, ticker) signal observations. Correlations are Pearson vs forward returns._

| Signal | vs fwd 5d | vs fwd 10d | vs fwd 20d |
|--------|-----------|------------|------------|
| return_1d | -0.00 | -0.02 | -0.00 |
| return_5d | -0.06 | -0.03 | 0.00 |
| return_20d | -0.01 | 0.01 | 0.00 |
| vol_ratio | 0.00 | 0.01 | 0.02 |
| vol_adj_mom_20d | -0.00 | 0.00 | -0.01 |
| composite_score | -0.01 | 0.00 | 0.02 |

## Entry vs Exit Attribution

_Buy the top 3 ranked names each day, hold a fixed period, **no** stop-loss / take-profit / max-holding. Next-day entry, slippage applied._

| Hold period | Raw avg return / trade | Raw win rate | N trades |
|-------------|------------------------|--------------|----------|
| 5d | +0.45% | +54.51% | 5467 |
| 10d | +1.09% | +56.18% | 5452 |
| 20d | +2.35% | +58.98% | 5422 |
| 30d | +3.55% | +61.74% | 5392 |

**Full strategy (with exit rules):** total return +433.41%, win rate +52.53%, avg hold 21.06 trading days.

The raw signal (buy top names, hold fixed, no stops) is **positive across holding periods** (avg +1.86% per trade, 58% win rate). That points to genuine signal quality — higher-ranked names tend to rise even without exit rules.

## P&L Attribution

**Top 5 contributors:**

| Ticker | P&L |
|--------|-----|
| CRWD | $254,392.46 |
| ORCL | $138,700.89 |
| MSFT | $40,319.40 |

**Worst 5 contributors:**

| Ticker | P&L |
|--------|-----|
| MSFT | $40,319.40 |
| ORCL | $138,700.89 |
| CRWD | $254,392.46 |

**P&L by asset group:**

| Group | P&L |
|-------|-----|
| crowdstrike | $254,392.46 |
| oracle | $138,700.89 |
| msft | $40,319.40 |

## Turnover and Re-entry Diagnostics

| Metric | Value |
|--------|-------|
| Total trades | 517 |
| Trades / month | 5.79 |
| Avg holding period | 21.06 trading days |
| Stop-loss → re-entry ≤5d | 65 |

**Most-entered tickers:** `CRWD`×130, `MSFT`×73, `ORCL`×57

**Most re-entered after a stop-loss:** `CRWD`×31, `ORCL`×20, `MSFT`×14

## Exposure and Benchmark Capture

| Metric | Value |
|--------|-------|
| Avg exposure | +83.78% |
| Max exposure | +97.47% |
| Avg cash (drag) | +16.22% |
| Correlation to SPY | 0.67 |
| Correlation to QQQ | 0.73 |
| Beta to SPY | 0.91 |
| Beta to QQQ | 0.81 |
| Up-capture vs QQQ | 0.89 |
| Down-capture vs QQQ | 0.85 |

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