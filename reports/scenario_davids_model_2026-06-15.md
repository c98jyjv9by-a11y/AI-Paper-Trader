# Scenario — davids_model

Trimmed to the only OOS-robust tickers (MSFT, ORCL, CRWD), each with its out-of-sample-best exit rule. Composite ranking drives entries; per-ticker entry filters not yet wired. In-sample-selected — validate before trusting.

**Universe (3):** MSFT, ORCL, CRWD

---

# AI Paper Trader — Backtest Report
**Period:** 2024-01-01 → 2026-06-15  |  **Generated:** 2026-06-15

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Ending Balance | $193,111.59 | $164,096.60 | $187,080.00 | $193,651.40 |
| Total Return | +93.11% | +64.10% | +87.08% | +93.65% |
| Max Drawdown | -33.08% | -18.76% | -22.77% | -41.83% |
| Excess vs SPY | +29.01% | — | — | — |
| Excess vs QQQ | +6.03% | — | — | — |
| Excess vs Equal-Wt | -0.54% | — | — | — |
| 1-Year Return | +9.63% | +27.89% | +41.87% | +8.63% |
| 2-Year Return | +54.31% | +44.00% | +60.71% | +47.91% |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $193,111.59 |
| **IRR (annualized, money-weighted)** | **+44.49%** |
| Total Return (on full $ portfolio) | +93.11% |
| Total Capital Deployed (all entries) | $2,259,464.08 |
| Avg Capital Deployed (snapshot) | $116,246.84 (+116.25% of portfolio) |
| Peak Capital Deployed (snapshot) | $200,086.77 (+200.09% of portfolio) |
| Time Invested | +98.70% of trading days |
| Trading Days | 615 |
| Total Trades | 93 (47 buys, 46 sells) |
| Win Rate | +50.00% |
| Average Win | $10,102.83 |
| Average Loss | $-6,088.52 |
| Profit Factor | 1.66 |
| Avg Holding Period | 35.9 approx. trading days |
| Largest Winner | $29,940.90 |
| Largest Loser | $-10,025.43 |
| Open Positions at End | 1 |
| Total Slippage Cost | $4,554.57 (+4.55% of start) |
| Avg Slippage / Trade | $48.97 |

_**IRR** is the annualized money-weighted (internal) rate of return on the capital actually put into positions: it solves for the rate that discounts the dated BUY outflows, SELL inflows, and the terminal mark-to-market of open positions to zero. It ignores idle cash, so it measures how the *deployed* capital performed, and is bounded at -100%. Being annualized, short backtests can extrapolate to large figures. **Total Return** is on the full starting portfolio (cash included) and is what the SPY/QQQ/Equal-Wt comparisons above use, since those benchmarks are fully invested._

## Strategy Parameters Used

| Parameter | Value |
|-----------|-------|
| Starting Portfolio | $100,000.00 |
| Max Position Size | 30.0% (auto: 90% ÷ 3 tickers) |
| Max Total Exposure | 90% |
| Max New Trades / Day | 3 |
| Stop Loss | 7.5% |
| Take Profit | 10.0% |
| Trailing Stop | none |
| Max Holding Period | 30 trading days |
| Slippage | 0.10% per fill |

## Ticker Universe

`MSFT`, `ORCL`, `CRWD`

## Trade Log (last 20 trades)

| Date | Action | Ticker | Shares | Price | Value | Reason | P&L | Hold Days |
|------|--------|--------|--------|-------|-------|--------|-----|-----------|
| 2026-02-27 | BUY | ORCL | 307 | $145.04 | $44,526.91 | momentum_score=0.7333 | — | — |
| 2026-02-27 | BUY | CRWD | 120 | $372.35 | $44,682.24 | momentum_score=0.5 | — | — |
| 2026-03-24 | SELL | MSFT | 123 | $371.56 | $45,702.19 | stop_loss | $-4,955.26 | 30.0 |
| 2026-04-14 | BUY | MSFT | 122 | $392.65 | $47,903.63 | momentum_score=0.65 | — | — |
| 2026-04-16 | SELL | ORCL | 307 | $178.16 | $54,695.64 | take_profit | $10,168.73 | 34.3 |
| 2026-04-17 | BUY | ORCL | 284 | $175.24 | $49,766.77 | momentum_score=1.0 | — | — |
| 2026-04-21 | SELL | CRWD | 120 | $449.16 | $53,899.25 | take_profit | $9,217.01 | 37.9 |
| 2026-04-22 | BUY | CRWD | 116 | $467.15 | $54,189.02 | momentum_score=0.6667 | — | — |
| 2026-05-13 | SELL | CRWD | 116 | $562.01 | $65,192.86 | take_profit | $11,003.84 | 15.0 |
| 2026-05-14 | BUY | CRWD | 99 | $580.53 | $57,472.47 | momentum_score=1.0 | — | — |
| 2026-05-29 | SELL | ORCL | 284 | $225.55 | $64,057.39 | take_profit | $14,290.62 | 30.0 |
| 2026-05-29 | SELL | CRWD | 99 | $730.27 | $72,296.63 | take_profit | $14,824.16 | 10.7 |
| 2026-06-01 | BUY | ORCL | 287 | $248.40 | $71,290.25 | momentum_score=0.8 | — | — |
| 2026-06-01 | BUY | CRWD | 88 | $782.95 | $68,899.79 | momentum_score=0.7333 | — | — |
| 2026-06-01 | SELL | MSFT | 122 | $460.06 | $56,127.26 | take_profit | $8,223.63 | 34.3 |
| 2026-06-02 | BUY | MSFT | 141 | $441.75 | $62,286.93 | momentum_score=0.4 | — | — |
| 2026-06-05 | SELL | ORCL | 287 | $213.47 | $61,264.83 | stop_loss | $-10,025.43 | 2.9 |
| 2026-06-05 | SELL | CRWD | 88 | $670.35 | $58,990.71 | stop_loss | $-9,909.08 | 2.9 |
| 2026-06-09 | SELL | MSFT | 141 | $403.01 | $56,823.93 | stop_loss | $-5,463.00 | 5.0 |
| 2026-06-12 | BUY | CRWD | 83 | $683.48 | $56,729.07 | momentum_score=0.8667 | — | — |

## Open Positions at End of Period

| Ticker | Shares | Entry Price | Final Price | Unrealized P&L | Entry Date |
|--------|--------|------------|------------|----------------|------------|
| CRWD | 83 | $683.48 | $692.91 | $782.46 | 2026-06-12 |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2024-01-02 | $100,000.00 | — | +0.00% | +0.00% | +0.00% | +0.00% |
| 2024-01-03 | $99,911.14 | -0.09% | -0.09% | -0.82% | -1.06% | -0.88% |
| 2024-01-04 | $99,890.67 | -0.02% | -0.11% | -1.14% | -1.57% | -0.90% |
| 2024-01-05 | $100,134.69 | +0.24% | +0.13% | -1.00% | -1.45% | -0.63% |
| 2024-01-08 | $102,920.56 | +2.78% | +2.92% | +0.41% | +0.59% | +2.48% |
| 2026-06-09 | $192,329.13 | -0.64% | +92.33% | +60.23% | +77.98% | +91.85% |
| 2026-06-10 | $192,329.13 | +0.00% | +92.33% | +57.71% | +74.43% | +90.17% |
| 2026-06-11 | $192,329.13 | +0.00% | +92.33% | +60.39% | +80.32% | +89.79% |
| 2026-06-12 | $192,272.46 | -0.03% | +92.27% | +61.25% | +81.38% | +88.66% |
| 2026-06-15 | $193,111.59 | +0.44% | +93.11% | +64.10% | +87.08% | +93.65% |


## Signal Predictiveness

_Cross-section of 1,842 (date, ticker) signal observations. Correlations are Pearson vs forward returns._

| Signal | vs fwd 5d | vs fwd 10d | vs fwd 20d |
|--------|-----------|------------|------------|
| return_1d | 0.00 | -0.00 | 0.01 |
| return_5d | -0.04 | -0.00 | 0.03 |
| return_20d | 0.01 | 0.04 | 0.07 |
| vol_ratio | -0.00 | 0.01 | 0.01 |
| vol_adj_mom_20d | 0.03 | 0.05 | 0.07 |
| composite_score | -0.00 | 0.01 | 0.03 |

## Entry vs Exit Attribution

_Buy the top 3 ranked names each day, hold a fixed period, **no** stop-loss / take-profit / max-holding. Next-day entry, slippage applied._

| Hold period | Raw avg return / trade | Raw win rate | N trades |
|-------------|------------------------|--------------|----------|
| 5d | +0.46% | +52.76% | 1827 |
| 10d | +1.15% | +52.48% | 1812 |
| 20d | +2.42% | +54.71% | 1782 |
| 30d | +3.47% | +57.19% | 1752 |

**Full strategy (with exit rules):** total return +93.11%, win rate +50.00%, avg hold 35.86 trading days.

The raw signal (buy top names, hold fixed, no stops) is **positive across holding periods** (avg +1.88% per trade, 54% win rate). That points to genuine signal quality — higher-ranked names tend to rise even without exit rules.

## P&L Attribution

**Top 5 contributors:**

| Ticker | P&L |
|--------|-----|
| CRWD | $60,364.55 |
| ORCL | $31,126.31 |
| MSFT | $1,620.72 |

**Worst 5 contributors:**

| Ticker | P&L |
|--------|-----|
| MSFT | $1,620.72 |
| ORCL | $31,126.31 |
| CRWD | $60,364.55 |

**P&L by asset group:**

| Group | P&L |
|-------|-----|
| crowdstrike | $60,364.55 |
| oracle | $31,126.31 |
| msft | $1,620.72 |

## Turnover and Re-entry Diagnostics

| Metric | Value |
|--------|-------|
| Total trades | 93 |
| Trades / month | 3.16 |
| Avg holding period | 35.86 trading days |
| Stop-loss → re-entry ≤5d | 11 |

**Most-entered tickers:** `CRWD`×19, `ORCL`×18, `MSFT`×10

**Most re-entered after a stop-loss:** `ORCL`×5, `CRWD`×5, `MSFT`×1

## Exposure and Benchmark Capture

| Metric | Value |
|--------|-------|
| Avg exposure | +75.20% |
| Max exposure | +93.01% |
| Avg cash (drag) | +24.80% |
| Correlation to SPY | 0.57 |
| Correlation to QQQ | 0.61 |
| Beta to SPY | 0.92 |
| Beta to QQQ | 0.76 |
| Up-capture vs QQQ | 0.90 |
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