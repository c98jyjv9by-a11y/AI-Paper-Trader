# Adaptive Rotating-Signal Backtest

Per-ticker weekly signal rotation — each name trades its recently-best signal or sits in cash. **High-turnover, small-sample, overfit-prone — validate out-of-sample and against a fixed-signal baseline.**

---

## Signal Rotation Log

_5-day rebalance, 63-day lookback, top 5, min edge +0.0%._

| Metric | Value |
|--------|-------|
| Rebalances | 251 |
| Avg names held (target) | 4.7 / 5 |
| Days fully in cash | 1.0% |
| Cumulative turnover (buys ÷ start) | 17.8× |

**Signal usage (how often each was the assigned signal):**

| Signal | Times chosen | Share |
|--------|--------------|-------|
| trend_50 | 302 | 26% |
| mom20_pos | 301 | 26% |
| dip_5 | 277 | 23% |
| trend_20 | 270 | 23% |
| near_52w_high | 29 | 2% |

**Sample rotation timeline (date → ticker:signal):**

- 2021-06-14 — ASML:trend_20, GOOGL:trend_50, META:trend_50, NVDA:trend_20, ORCL:trend_50
- 2021-06-21 — AAPL:trend_20, CRWD:trend_20, GOOGL:trend_50, META:trend_50, NVDA:trend_20
- 2021-06-28 — ASML:mom20_pos, CRWD:trend_20, GOOGL:trend_50, META:trend_50, NVDA:trend_20
- 2026-05-29 — AMD:mom20_pos, CRWD:trend_20, MU:mom20_pos, ORCL:trend_50, PANW:trend_50
- 2026-06-05 — AMD:mom20_pos, CRWD:trend_20, MU:mom20_pos, ORCL:trend_50, PANW:trend_50

---

# AI Paper Trader — Backtest Report
**Period:** 2021-06-13 → 2026-06-13  |  **Generated:** 2026-06-13

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Ending Balance | $128,104.20 | $186,751.50 | $215,761.40 | $378,345.50 |
| Total Return | +28.10% | +86.75% | +115.76% | +278.35% |
| Max Drawdown | -11.89% | -24.50% | -35.12% | -41.79% |
| Excess vs SPY | -58.65% | — | — | — |
| Excess vs QQQ | -87.66% | — | — | — |
| Excess vs Equal-Wt | -250.24% | — | — | — |
| 1-Year Return | +13.42% | +24.27% | +35.82% | +63.06% |
| 2-Year Return | +18.26% | +41.84% | +56.89% | +104.50% |
| 3-Year Return | +30.63% | +79.62% | +107.88% | +240.49% |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $128,104.20 |
| **IRR (annualized, money-weighted)** | **+23.88%** |
| Total Return (on full $ portfolio) | +28.10% |
| Total Capital Deployed (all entries) | $1,775,835.45 |
| Avg Capital Deployed (snapshot) | $18,193.61 (+18.19% of portfolio) |
| Peak Capital Deployed (snapshot) | $33,148.11 (+33.15% of portfolio) |
| Time Invested | +98.96% of trading days |
| Trading Days | 1256 |
| Total Trades | 976 (490 buys, 486 sells) |
| Win Rate | +48.35% |
| Average Win | $299.40 |
| Average Loss | $-206.43 |
| Profit Factor | 1.36 |
| Avg Holding Period | nan approx. trading days |
| Largest Winner | $3,768.34 |
| Largest Loser | $-1,109.39 |
| Open Positions at End | 4 |
| Total Slippage Cost | $3,553.32 (+3.55% of start) |
| Avg Slippage / Trade | $3.64 |

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
| 2026-04-24 | SELL | NFLX | 43 | $92.35 | $3,970.95 | rebalance | $-275.68 | nan |
| 2026-04-24 | BUY | MU | 8 | $497.22 | $3,977.73 | signal=mom20_pos | — | — |
| 2026-04-24 | BUY | AVGO | 10 | $423.18 | $4,231.83 | signal=trend_50 | — | — |
| 2026-05-01 | SELL | ASML | 2 | $1,425.59 | $2,851.19 | rebalance | $-101.88 | nan |
| 2026-05-01 | BUY | GOOGL | 11 | $385.85 | $4,244.30 | signal=trend_20 | — | — |
| 2026-05-08 | SELL | TSM | 11 | $410.31 | $4,513.38 | rebalance | $442.24 | nan |
| 2026-05-08 | SELL | AVGO | 10 | $429.57 | $4,295.70 | rebalance | $63.87 | nan |
| 2026-05-08 | SELL | GOOGL | 11 | $400.16 | $4,401.76 | rebalance | $157.46 | nan |
| 2026-05-08 | BUY | ASML | 2 | $1,593.61 | $3,187.22 | signal=mom20_pos | — | — |
| 2026-05-08 | BUY | NVDA | 20 | $215.16 | $4,303.29 | signal=dip_5 | — | — |
| 2026-05-08 | BUY | PANW | 22 | $208.09 | $4,577.93 | signal=trend_50 | — | — |
| 2026-05-15 | SELL | ASML | 2 | $1,500.31 | $3,000.62 | rebalance | $-186.61 | nan |
| 2026-05-15 | SELL | NVDA | 20 | $224.83 | $4,496.65 | rebalance | $193.37 | nan |
| 2026-05-15 | BUY | GOOGL | 11 | $396.94 | $4,366.34 | signal=trend_20 | — | — |
| 2026-05-15 | BUY | CRWD | 7 | $594.67 | $4,162.72 | signal=trend_20 | — | — |
| 2026-05-22 | SELL | GOOGL | 11 | $382.36 | $4,205.95 | rebalance | $-160.39 | nan |
| 2026-05-22 | BUY | COIN | 23 | $185.18 | $4,259.03 | signal=dip_5 | — | — |
| 2026-06-01 | SELL | COIN | 23 | $182.43 | $4,195.83 | rebalance | $-63.19 | nan |
| 2026-06-01 | BUY | ORCL | 20 | $248.40 | $4,967.96 | signal=trend_50 | — | — |
| 2026-06-08 | SELL | ORCL | 20 | $211.61 | $4,232.16 | stop_loss | $-735.80 | nan |

## Open Positions at End of Period

| Ticker | Shares | Entry Price | Final Price | Unrealized P&L | Entry Date |
|--------|--------|------------|------------|----------------|------------|
| AMD | 15 | $278.67 | $511.57 | $3,493.52 | None |
| MU | 8 | $497.22 | $981.61 | $3,875.15 | None |
| PANW | 22 | $208.09 | $279.62 | $1,573.71 | None |
| CRWD | 7 | $594.67 | $682.80 | $616.88 | None |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2021-06-14 | $100,000.00 | — | +0.00% | +0.00% | +0.00% | +0.00% |
| 2021-06-15 | $99,982.79 | -0.02% | -0.02% | -0.18% | -0.65% | -0.98% |
| 2021-06-16 | $99,703.14 | -0.28% | -0.30% | -0.74% | -1.02% | -1.42% |
| 2021-06-17 | $99,971.64 | +0.27% | -0.03% | -0.77% | +0.24% | -0.39% |
| 2021-06-18 | $99,663.32 | -0.31% | -0.34% | -2.11% | -0.55% | -1.65% |
| 2026-06-08 | $127,066.51 | +0.62% | +27.07% | +86.11% | +114.19% | +277.84% |
| 2026-06-09 | $126,512.25 | -0.44% | +26.51% | +85.57% | +111.72% | +273.48% |
| 2026-06-10 | $125,892.59 | -0.49% | +25.89% | +82.64% | +107.49% | +262.61% |
| 2026-06-11 | $127,930.61 | +1.62% | +27.93% | +85.75% | +114.50% | +277.75% |
| 2026-06-12 | $128,104.20 | +0.14% | +28.10% | +86.75% | +115.76% | +278.35% |


## Signal Predictiveness

_No signal history captured — diagnostics unavailable._

## Entry vs Exit Attribution

_No raw-hold trades available._

## P&L Attribution

**Top 5 contributors:**

| Ticker | P&L |
|--------|-----|
| MU | $6,860.55 |
| NVDA | $6,374.71 |
| AMD | $4,549.48 |
| CRWD | $3,240.05 |
| TSLA | $2,625.81 |

**Worst 5 contributors:**

| Ticker | P&L |
|--------|-----|
| NFLX | $-1,572.90 |
| AMZN | $-1,340.20 |
| TSM | $-1,030.66 |
| JPM | $-168.14 |
| AVGO | $-114.67 |

**P&L by asset group:**

| Group | P&L |
|-------|-----|
| mega_cap_growth | $12,829.26 |
| semiconductors | $11,295.36 |
| software_cybersecurity | $4,851.30 |
| financial_crypto_beta | $15.86 |
| _(ungrouped)_ | $-887.69 |

## Turnover and Re-entry Diagnostics

| Metric | Value |
|--------|-------|
| Total trades | 976 |
| Trades / month | 16.27 |
| Avg holding period | — trading days |
| Stop-loss → re-entry ≤5d | 25 |

**Most-entered tickers:** `CRWD`×32, `AMD`×32, `TSLA`×32, `AVGO`×31, `COIN`×30, `PANW`×30, `NVDA`×28, `ASML`×27

**Most re-entered after a stop-loss:** `CRWD`×3, `TSM`×3, `COIN`×3, `AMD`×2, `PANW`×2

## Exposure and Benchmark Capture

| Metric | Value |
|--------|-------|
| Avg exposure | +17.22% |
| Max exposure | +25.39% |
| Avg cash (drag) | +82.78% |
| Correlation to SPY | 0.64 |
| Correlation to QQQ | 0.73 |
| Beta to SPY | 0.22 |
| Beta to QQQ | 0.19 |
| Up-capture vs QQQ | 0.23 |
| Down-capture vs QQQ | 0.22 |

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