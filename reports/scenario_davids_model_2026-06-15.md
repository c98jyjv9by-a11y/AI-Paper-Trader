# Scenario — davids_model

Trimmed to the only OOS-robust tickers (MSFT, ORCL, CRWD), each with its out-of-sample-best exit rule. Composite ranking drives entries; per-ticker entry filters not yet wired. In-sample-selected — validate before trusting.

**Universe (3):** MSFT, ORCL, CRWD

---

# AI Paper Trader — Backtest Report
**Period:** 2026-01-01 → 2026-06-18  |  **Generated:** 2026-06-15

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Ending Balance | $101,953.80 | $110,791.10 | $121,499.60 | $112,234.60 |
| Total Return | +1.95% | +10.79% | +21.50% | +12.23% |
| Max Drawdown | -24.03% | -8.88% | -11.72% | -25.94% |
| Excess vs SPY | -8.84% | — | — | — |
| Excess vs QQQ | -19.55% | — | — | — |
| Excess vs Equal-Wt | -10.28% | — | — | — |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $101,953.80 |
| **IRR (annualized, money-weighted)** | **+6.04%** |
| Total Return (on full $ portfolio) | +1.95% |
| Total Capital Deployed (all entries) | $463,225.36 |
| Avg Capital Deployed (snapshot) | $66,116.12 (+66.12% of portfolio) |
| Peak Capital Deployed (snapshot) | $104,960.22 (+104.96% of portfolio) |
| Time Invested | +93.81% of trading days |
| Trading Days | 113 |
| Total Trades | 31 (16 buys, 15 sells) |
| Win Rate | +40.00% |
| Average Win | $5,939.95 |
| Average Loss | $-3,788.96 |
| Profit Factor | 1.05 |
| Avg Holding Period | 18.5 approx. trading days |
| Largest Winner | $7,786.43 |
| Largest Loser | $-5,294.76 |
| Open Positions at End | 1 |
| Total Slippage Cost | $897.89 (+0.90% of start) |
| Avg Slippage / Trade | $28.96 |

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
| 2026-02-27 | BUY | ORCL | 162 | $145.04 | $23,496.29 | momentum_score=0.7333 | — | — |
| 2026-02-27 | BUY | CRWD | 63 | $372.35 | $23,458.18 | momentum_score=0.5 | — | — |
| 2026-03-24 | SELL | MSFT | 64 | $371.56 | $23,780.00 | stop_loss | $-2,578.35 | 30.0 |
| 2026-04-14 | BUY | MSFT | 64 | $392.65 | $25,129.77 | momentum_score=0.65 | — | — |
| 2026-04-16 | SELL | ORCL | 162 | $178.16 | $28,862.20 | take_profit | $5,365.91 | 34.3 |
| 2026-04-17 | BUY | ORCL | 150 | $175.24 | $26,285.26 | momentum_score=1.0 | — | — |
| 2026-04-21 | SELL | CRWD | 63 | $449.16 | $28,297.11 | take_profit | $4,838.93 | 37.9 |
| 2026-04-22 | BUY | CRWD | 61 | $467.15 | $28,495.95 | momentum_score=0.6667 | — | — |
| 2026-05-13 | SELL | CRWD | 61 | $562.01 | $34,282.45 | take_profit | $5,786.50 | 15.0 |
| 2026-05-14 | BUY | CRWD | 52 | $580.53 | $30,187.56 | momentum_score=1.0 | — | — |
| 2026-05-29 | SELL | ORCL | 150 | $225.55 | $33,833.13 | take_profit | $7,547.87 | 30.0 |
| 2026-05-29 | SELL | CRWD | 52 | $730.27 | $37,973.99 | take_profit | $7,786.43 | 10.7 |
| 2026-06-01 | BUY | ORCL | 151 | $248.40 | $37,508.11 | momentum_score=0.8 | — | — |
| 2026-06-01 | BUY | CRWD | 46 | $782.95 | $36,015.80 | momentum_score=0.7333 | — | — |
| 2026-06-01 | SELL | MSFT | 64 | $460.06 | $29,443.81 | take_profit | $4,314.04 | 34.3 |
| 2026-06-02 | BUY | MSFT | 74 | $441.75 | $32,689.60 | momentum_score=0.4 | — | — |
| 2026-06-05 | SELL | ORCL | 151 | $213.47 | $32,233.41 | stop_loss | $-5,274.70 | 2.9 |
| 2026-06-05 | SELL | CRWD | 46 | $670.35 | $30,836.05 | stop_loss | $-5,179.75 | 2.9 |
| 2026-06-09 | SELL | MSFT | 74 | $403.01 | $29,822.49 | stop_loss | $-2,867.11 | 5.0 |
| 2026-06-12 | BUY | CRWD | 44 | $683.48 | $30,073.24 | momentum_score=0.8667 | — | — |

## Open Positions at End of Period

| Ticker | Shares | Entry Price | Final Price | Unrealized P&L | Entry Date |
|--------|--------|------------|------------|----------------|------------|
| CRWD | 44 | $683.48 | $692.91 | $414.80 | 2026-06-12 |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2026-01-02 | $100,000.00 | — | +0.00% | +0.00% | +0.00% | +0.00% |
| 2026-01-05 | $99,910.73 | -0.09% | -0.09% | +0.67% | +0.79% | -0.32% |
| 2026-01-06 | $100,560.09 | +0.65% | +0.56% | +1.26% | +1.68% | +0.41% |
| 2026-01-07 | $102,090.85 | +1.52% | +2.09% | +0.94% | +1.78% | +2.11% |
| 2026-01-08 | $100,273.77 | -1.78% | +0.27% | +0.93% | +1.20% | +0.09% |
| 2026-06-09 | $101,539.00 | -0.63% | +1.54% | +8.18% | +15.59% | +11.22% |
| 2026-06-10 | $101,539.00 | +0.00% | +1.54% | +6.48% | +13.28% | +10.22% |
| 2026-06-11 | $101,539.00 | +0.00% | +1.54% | +8.29% | +17.11% | +10.00% |
| 2026-06-12 | $101,508.96 | -0.03% | +1.51% | +8.87% | +17.80% | +9.39% |
| 2026-06-15 | $101,953.80 | +0.44% | +1.95% | +10.79% | +21.50% | +12.23% |


## Signal Predictiveness

_Cross-section of 336 (date, ticker) signal observations. Correlations are Pearson vs forward returns._

| Signal | vs fwd 5d | vs fwd 10d | vs fwd 20d |
|--------|-----------|------------|------------|
| return_1d | 0.07 | -0.05 | 0.06 |
| return_5d | -0.11 | -0.02 | 0.09 |
| return_20d | 0.00 | 0.12 | 0.31 |
| vol_ratio | -0.07 | -0.09 | -0.10 |
| vol_adj_mom_20d | 0.03 | 0.13 | 0.29 |
| composite_score | -0.09 | -0.09 | -0.03 |

## Entry vs Exit Attribution

_Buy the top 3 ranked names each day, hold a fixed period, **no** stop-loss / take-profit / max-holding. Next-day entry, slippage applied._

| Hold period | Raw avg return / trade | Raw win rate | N trades |
|-------------|------------------------|--------------|----------|
| 5d | +0.44% | +47.66% | 321 |
| 10d | +1.54% | +49.02% | 306 |
| 20d | +4.19% | +49.28% | 276 |
| 30d | +7.34% | +55.69% | 246 |

**Full strategy (with exit rules):** total return +1.95%, win rate +40.00%, avg hold 18.48 trading days.

The raw signal (buy top names, hold fixed, no stops) is **positive across holding periods** (avg +3.38% per trade, 50% win rate). That points to genuine signal quality — higher-ranked names tend to rise even without exit rules.

## P&L Attribution

**Top 5 contributors:**

| Ticker | P&L |
|--------|-----|
| CRWD | $4,203.61 |
| ORCL | $1,406.53 |
| MSFT | $-3,656.33 |

**Worst 5 contributors:**

| Ticker | P&L |
|--------|-----|
| MSFT | $-3,656.33 |
| ORCL | $1,406.53 |
| CRWD | $4,203.61 |

**P&L by asset group:**

| Group | P&L |
|-------|-----|
| crowdstrike | $4,203.61 |
| oracle | $1,406.53 |
| msft | $-3,656.33 |

## Turnover and Re-entry Diagnostics

| Metric | Value |
|--------|-------|
| Total trades | 31 |
| Trades / month | 5.62 |
| Avg holding period | 18.48 trading days |
| Stop-loss → re-entry ≤5d | 4 |

**Most-entered tickers:** `CRWD`×7, `ORCL`×5, `MSFT`×4

**Most re-entered after a stop-loss:** `CRWD`×3, `ORCL`×1

## Exposure and Benchmark Capture

| Metric | Value |
|--------|-------|
| Avg exposure | +71.61% |
| Max exposure | +92.39% |
| Avg cash (drag) | +28.39% |
| Correlation to SPY | 0.39 |
| Correlation to QQQ | 0.43 |
| Beta to SPY | 0.90 |
| Beta to QQQ | 0.68 |
| Up-capture vs QQQ | 0.70 |
| Down-capture vs QQQ | 0.92 |

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