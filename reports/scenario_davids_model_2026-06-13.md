# Scenario — davids_model

Trimmed to the only OOS-robust tickers (MSFT, ORCL, CRWD), each with its out-of-sample-best exit rule. Composite ranking drives entries; per-ticker entry filters not yet wired. In-sample-selected — validate before trusting.

**Universe (3):** MSFT, ORCL, CRWD

---

# AI Paper Trader — Backtest Report
**Period:** 2024-01-01 → 2026-06-13  |  **Generated:** 2026-06-13

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Ending Balance | $192,272.44 | $161,253.10 | $181,382.10 | $188,656.00 |
| Total Return | +92.27% | +61.25% | +81.38% | +88.66% |
| Max Drawdown | -33.08% | -18.76% | -22.77% | -41.83% |
| Excess vs SPY | +31.02% | — | — | — |
| Excess vs QQQ | +10.89% | — | — | — |
| Excess vs Equal-Wt | +3.62% | — | — | — |
| 1-Year Return | +8.80% | +24.27% | +35.82% | +8.57% |
| 2-Year Return | +53.87% | +41.84% | +56.89% | +45.87% |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $192,272.44 |
| **IRR (annualized, money-weighted)** | **+44.25%** |
| Total Return (on full $ portfolio) | +92.27% |
| Total Capital Deployed (all entries) | $2,259,464.16 |
| Avg Capital Deployed (snapshot) | $116,342.50 (+116.34% of portfolio) |
| Peak Capital Deployed (snapshot) | $200,086.77 (+200.09% of portfolio) |
| Time Invested | +98.70% of trading days |
| Trading Days | 614 |
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
| Stop Loss | 8% |
| Take Profit | 10% |
| Max Holding Period | 30 trading days |
| Slippage | 0.10% per fill |

## Ticker Universe

`MSFT`, `ORCL`, `CRWD`

## Trade Log (last 20 trades)

| Date | Action | Ticker | Shares | Price | Value | Reason | P&L | Hold Days |
|------|--------|--------|--------|-------|-------|--------|-----|-----------|
| 2026-02-27 | BUY | ORCL | 307 | $145.04 | $44,526.91 | momentum_score=0.65 | — | — |
| 2026-02-27 | BUY | CRWD | 120 | $372.35 | $44,682.24 | momentum_score=0.6333 | — | — |
| 2026-03-24 | SELL | MSFT | 123 | $371.56 | $45,702.19 | stop_loss | $-4,955.26 | 30.0 |
| 2026-04-14 | BUY | MSFT | 122 | $392.65 | $47,903.63 | momentum_score=0.6333 | — | — |
| 2026-04-16 | SELL | ORCL | 307 | $178.16 | $54,695.64 | take_profit | $10,168.73 | 34.3 |
| 2026-04-17 | BUY | ORCL | 284 | $175.24 | $49,766.77 | momentum_score=1.0 | — | — |
| 2026-04-21 | SELL | CRWD | 120 | $449.16 | $53,899.25 | take_profit | $9,217.01 | 37.9 |
| 2026-04-22 | BUY | CRWD | 116 | $467.15 | $54,189.02 | momentum_score=0.6833 | — | — |
| 2026-05-13 | SELL | CRWD | 116 | $562.01 | $65,192.86 | take_profit | $11,003.84 | 15.0 |
| 2026-05-14 | BUY | CRWD | 99 | $580.53 | $57,472.47 | momentum_score=1.0 | — | — |
| 2026-05-29 | SELL | ORCL | 284 | $225.55 | $64,057.39 | take_profit | $14,290.62 | 30.0 |
| 2026-05-29 | SELL | CRWD | 99 | $730.27 | $72,296.63 | take_profit | $14,824.16 | 10.7 |
| 2026-06-01 | BUY | ORCL | 287 | $248.40 | $71,290.25 | momentum_score=0.7833 | — | — |
| 2026-06-01 | BUY | CRWD | 88 | $782.95 | $68,899.79 | momentum_score=0.65 | — | — |
| 2026-06-01 | SELL | MSFT | 122 | $460.06 | $56,127.26 | take_profit | $8,223.63 | 34.3 |
| 2026-06-02 | BUY | MSFT | 141 | $441.75 | $62,286.93 | momentum_score=0.45 | — | — |
| 2026-06-05 | SELL | ORCL | 287 | $213.47 | $61,264.83 | stop_loss | $-10,025.43 | 2.9 |
| 2026-06-05 | SELL | CRWD | 88 | $670.35 | $58,990.71 | stop_loss | $-9,909.08 | 2.9 |
| 2026-06-09 | SELL | MSFT | 141 | $403.01 | $56,823.93 | stop_loss | $-5,463.00 | 5.0 |
| 2026-06-12 | BUY | CRWD | 83 | $683.48 | $56,729.07 | momentum_score=0.7667 | — | — |

## Open Positions at End of Period

| Ticker | Shares | Entry Price | Final Price | Unrealized P&L | Entry Date |
|--------|--------|------------|------------|----------------|------------|
| CRWD | 83 | $683.48 | $682.80 | $-56.67 | 2026-06-12 |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2024-01-02 | $100,000.00 | — | +0.00% | +0.00% | +0.00% | +0.00% |
| 2024-01-03 | $99,911.14 | -0.09% | -0.09% | -0.82% | -1.06% | -0.88% |
| 2024-01-04 | $99,890.64 | -0.02% | -0.11% | -1.14% | -1.57% | -0.90% |
| 2024-01-05 | $100,134.65 | +0.24% | +0.13% | -1.00% | -1.45% | -0.63% |
| 2024-01-08 | $102,920.53 | +2.78% | +2.92% | +0.41% | +0.59% | +2.48% |
| 2026-06-08 | $193,560.52 | -0.36% | +93.56% | +60.70% | +80.06% | +96.46% |
| 2026-06-09 | $192,329.11 | -0.64% | +92.33% | +60.23% | +77.98% | +91.85% |
| 2026-06-10 | $192,329.11 | +0.00% | +92.33% | +57.71% | +74.43% | +90.17% |
| 2026-06-11 | $192,329.11 | +0.00% | +92.33% | +60.39% | +80.32% | +89.79% |
| 2026-06-12 | $192,272.44 | -0.03% | +92.27% | +61.25% | +81.38% | +88.66% |


## Signal Predictiveness

_Cross-section of 1,839 (date, ticker) signal observations. Correlations are Pearson vs forward returns._

| Signal | vs fwd 5d | vs fwd 10d | vs fwd 20d |
|--------|-----------|------------|------------|
| return_1d | 0.00 | 0.00 | 0.01 |
| return_5d | -0.04 | 0.01 | 0.02 |
| return_20d | 0.01 | 0.05 | 0.07 |
| vol_ratio | -0.00 | 0.02 | 0.01 |
| vol_adj_mom_20d | 0.03 | 0.06 | 0.07 |
| composite_score | -0.00 | 0.00 | 0.03 |

## Entry vs Exit Attribution

_Buy the top 3 ranked names each day, hold a fixed period, **no** stop-loss / take-profit / max-holding. Next-day entry, slippage applied._

| Hold period | Raw avg return / trade | Raw win rate | N trades |
|-------------|------------------------|--------------|----------|
| 5d | +0.47% | +52.80% | 1824 |
| 10d | +1.18% | +52.57% | 1809 |
| 20d | +2.41% | +54.75% | 1779 |
| 30d | +3.45% | +57.18% | 1749 |

**Full strategy (with exit rules):** total return +92.27%, win rate +50.00%, avg hold 35.86 trading days.

The raw signal (buy top names, hold fixed, no stops) is **positive across holding periods** (avg +1.88% per trade, 54% win rate). That points to genuine signal quality — higher-ranked names tend to rise even without exit rules.

## P&L Attribution

**Top 5 contributors:**

| Ticker | P&L |
|--------|-----|
| CRWD | $59,525.42 |
| ORCL | $31,126.29 |
| MSFT | $1,620.72 |

**Worst 5 contributors:**

| Ticker | P&L |
|--------|-----|
| MSFT | $1,620.72 |
| ORCL | $31,126.29 |
| CRWD | $59,525.42 |

**P&L by asset group:**

| Group | P&L |
|-------|-----|
| crowdstrike | $59,525.42 |
| oracle | $31,126.29 |
| msft | $1,620.72 |

## Turnover and Re-entry Diagnostics

| Metric | Value |
|--------|-------|
| Total trades | 93 |
| Trades / month | 3.17 |
| Avg holding period | 35.86 trading days |
| Stop-loss → re-entry ≤5d | 11 |

**Most-entered tickers:** `CRWD`×19, `ORCL`×18, `MSFT`×10

**Most re-entered after a stop-loss:** `ORCL`×5, `CRWD`×5, `MSFT`×1

## Exposure and Benchmark Capture

| Metric | Value |
|--------|-------|
| Avg exposure | +75.28% |
| Max exposure | +93.01% |
| Avg cash (drag) | +24.72% |
| Correlation to SPY | 0.57 |
| Correlation to QQQ | 0.62 |
| Beta to SPY | 0.93 |
| Beta to QQQ | 0.77 |
| Up-capture vs QQQ | 0.91 |
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

## Sensitivity Analysis

> One parameter is varied at a time; everything else stays at the scenario's configured values. **Run-wide** params apply to the whole backtest. **Ticker** params overwrite that exit field for *every* `ticker_groups` name at once — a uniform stand-in for the per-ticker mix, with the real heterogeneous config shown as the `as-configured` baseline row.
> In-sample only — do not pick parameters off these tables; see Robustness Notes.

**Baseline (as configured):** +92.27% return  |  -33.08% max drawdown  |  +50.00% win rate  |  1.66 profit factor

### Run-wide parameters

#### Max Total Exposure  (baseline: 90%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 50% | +48.67% | -12.58% | -39.98% | -19.57% | 93 | +50.00% | 1.80 |
| 70% | +70.38% | +9.12% | -18.28% | -26.54% | 93 | +50.00% | 1.73 |
| 90% ◀ baseline | +92.27% | +31.02% | +3.62% | -33.08% | 93 | +50.00% | 1.66 |
| 100% | +110.13% | +48.87% | +21.47% | -36.42% | 91 | +51.11% | 1.72 |

#### Max New Trades / Day  (baseline: 3)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 1 | +105.55% | +44.30% | +16.89% | -32.99% | 91 | +51.11% | 1.81 |
| 2 | +92.32% | +31.07% | +3.66% | -33.13% | 93 | +50.00% | 1.66 |
| 3 ◀ baseline | +92.27% | +31.02% | +3.62% | -33.08% | 93 | +50.00% | 1.66 |
| 5 | +92.27% | +31.02% | +3.62% | -33.08% | 93 | +50.00% | 1.66 |

#### Min Composite Score  (baseline: none)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| none ◀ baseline | +92.27% | +31.02% | +3.62% | -33.08% | 93 | +50.00% | 1.66 |
| 0.60 | +96.79% | +35.54% | +8.14% | -33.48% | 94 | +50.00% | 1.72 |
| 0.70 | +75.48% | +14.23% | -13.18% | -33.34% | 90 | +47.73% | 1.63 |

#### Slippage  (baseline: 0.10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 0.05% | +114.70% | +53.45% | +26.05% | -30.35% | 93 | +52.17% | 1.81 |
| 0.10% ◀ baseline | +92.27% | +31.02% | +3.62% | -33.08% | 93 | +50.00% | 1.66 |
| 0.20% | +93.55% | +32.30% | +4.89% | -33.05% | 93 | +50.00% | 1.67 |
| 0.50% | +73.94% | +12.69% | -14.72% | -34.46% | 95 | +48.94% | 1.50 |

#### Re-entry Recovery Gate  (baseline: 5%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +66.57% | +5.32% | -22.08% | -37.38% | 115 | +44.64% | 1.40 |
| 0% | +66.57% | +5.32% | -22.08% | -37.38% | 115 | +44.64% | 1.40 |
| 5% ◀ baseline | +92.27% | +31.02% | +3.62% | -33.08% | 93 | +50.00% | 1.66 |
| 10% | +100.91% | +39.65% | +12.25% | -27.74% | 81 | +52.50% | 1.93 |

#### Signal Weight Profile  (baseline: baseline)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| baseline ◀ baseline | +92.27% | +31.02% | +3.62% | -33.08% | 93 | +50.00% | 1.66 |
| no_1d | +92.27% | +31.02% | +3.62% | -33.08% | 93 | +50.00% | 1.66 |
| less_1d | +92.27% | +31.02% | +3.62% | -33.08% | 93 | +50.00% | 1.66 |
| more_volume | +92.27% | +31.02% | +3.62% | -33.08% | 93 | +50.00% | 1.66 |

### Ticker-level exit parameters (applied uniformly to all names)

#### Ticker Stop-Loss (all names)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| as-configured ◀ baseline | +92.27% | +31.02% | +3.62% | -33.08% | 93 | +50.00% | 1.66 |
| 5.0% | +96.22% | +34.96% | +7.56% | -27.39% | 121 | +38.33% | 1.77 |
| 7.5% | +98.72% | +37.47% | +10.07% | -30.97% | 105 | +46.15% | 1.70 |
| 10.0% | +91.13% | +29.87% | +2.47% | -34.60% | 91 | +51.11% | 1.65 |
| 15.0% | +88.64% | +27.39% | -0.02% | -34.31% | 76 | +59.46% | 1.72 |

#### Ticker Take-Profit (all names)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| as-configured ◀ baseline | +92.27% | +31.02% | +3.62% | -33.08% | 93 | +50.00% | 1.66 |
| off | +69.01% | +7.76% | -19.65% | -42.14% | 27 | +33.33% | 1.62 |
| 15% | +83.16% | +21.91% | -5.50% | -34.09% | 113 | +53.57% | 1.57 |
| 20% | +88.34% | +27.09% | -0.32% | -33.54% | 86 | +50.00% | 1.68 |
| 30% | +76.24% | +14.99% | -12.41% | -32.35% | 75 | +41.67% | 1.67 |

#### Ticker Trailing-Stop (all names)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| as-configured ◀ baseline | +92.27% | +31.02% | +3.62% | -33.08% | 93 | +50.00% | 1.66 |
| off | +92.27% | +31.02% | +3.62% | -33.08% | 93 | +50.00% | 1.66 |
| 10% | +82.07% | +20.82% | -6.59% | -35.34% | 145 | +43.06% | 1.51 |
| 15% | +75.33% | +14.08% | -13.32% | -36.50% | 109 | +42.59% | 1.53 |

#### Ticker Max-Holding (all names)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| as-configured ◀ baseline | +92.27% | +31.02% | +3.62% | -33.08% | 93 | +50.00% | 1.66 |
| 15d | +83.88% | +22.63% | -4.77% | -35.04% | 239 | +54.62% | 1.49 |
| 30d | +55.86% | -5.40% | -32.80% | -34.88% | 144 | +52.11% | 1.41 |
| 60d | +84.85% | +23.60% | -3.81% | -33.36% | 109 | +51.85% | 1.60 |

### Best 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | slippage | 0.05% | +114.70% | +26.05% | -30.35% | 1.81 |
| 2 | max_total_exposure | 100% | +110.13% | +21.47% | -36.42% | 1.72 |
| 3 | max_new_trades_per_day | 1 | +105.55% | +16.89% | -32.99% | 1.81 |
| 4 | reentry_recover_pct | 10% | +100.91% | +12.25% | -27.74% | 1.93 |
| 5 | tk_stop_loss | 7.5% | +98.72% | +10.07% | -30.97% | 1.70 |

### Worst 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | max_total_exposure | 50% | +48.67% | -39.98% | -19.57% | 1.80 |
| 2 | tk_max_holding_days | 30d | +55.86% | -32.80% | -34.88% | 1.41 |
| 3 | reentry_recover_pct | 0% | +66.57% | -22.08% | -37.38% | 1.40 |
| 4 | reentry_recover_pct | off | +66.57% | -22.08% | -37.38% | 1.40 |
| 5 | tk_take_profit | off | +69.01% | -19.65% | -42.14% | 1.62 |

### Robustness Notes

The baseline outperforms 76% of all variants. This is broadly consistent across parameter dimensions, suggesting the baseline settings are reasonably competitive in-sample.

The widest in-sample return spread belongs to `max_total_exposure` (61.5 pp range across its variants); `signal_weights` shows the narrowest spread (0.0 pp), suggesting the strategy is least sensitive to that parameter in this period.

Improvements that appear in only one or two variants should be treated with skepticism — isolated peaks are more likely to reflect in-sample noise than genuine edge. Prefer settings that perform consistently across the full sweep.
