# Scenario — model_v2

Full 21-name universe with one uniform exit rule applied to every ticker (stop 15%, no take-profit, no trailing stop, 60-day max hold) plus the trough-based anti-falling-knife re-entry gate. Composite ranking drives entries.

**Universe (33):** CRWD, ORCL, COIN, NFLX, PANW, GOOGL, BAC, MSFT, AVGO, AMZN, COST, ASML, AAPL, JPM, TSM, GS, META, TSLA, MU, AMD, NVDA, LLY, VST, AXON, GE, PLTR, OXY, INTC, BA, PFE, PYPL, SEDG, PLUG

---

# AI Paper Trader — Backtest Report
**Period:** 2023-01-01 → 2026-06-13  |  **Generated:** 2026-06-13

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Ending Balance | $419,554.63 | $203,179.10 | $278,006.50 | $473,878.40 |
| Total Return | +319.55% | +103.18% | +178.01% | +373.88% |
| Max Drawdown | -28.09% | -18.76% | -22.77% | -30.94% |
| Excess vs SPY | +216.38% | — | — | — |
| Excess vs QQQ | +141.55% | — | — | — |
| Excess vs Equal-Wt | -54.32% | — | — | — |
| 1-Year Return | +64.99% | +24.27% | +35.82% | +36.66% |
| 2-Year Return | +98.67% | +41.84% | +56.89% | +103.53% |
| 3-Year Return | +221.45% | +79.62% | +107.88% | +242.73% |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $419,554.63 |
| **IRR (annualized, money-weighted)** | **+56.99%** |
| Total Return (on full $ portfolio) | +319.55% |
| Total Capital Deployed (all entries) | $2,605,886.83 |
| Avg Capital Deployed (snapshot) | $206,148.64 (+206.15% of portfolio) |
| Peak Capital Deployed (snapshot) | $423,471.84 (+423.47% of portfolio) |
| Time Invested | +99.88% of trading days |
| Trading Days | 864 |
| Total Trades | 269 (140 buys, 129 sells) |
| Win Rate | +62.02% |
| Average Win | $4,908.42 |
| Average Loss | $-3,018.04 |
| Profit Factor | 2.66 |
| Avg Holding Period | 71.1 approx. trading days |
| Largest Winner | $31,472.93 |
| Largest Loser | $-5,325.32 |
| Open Positions at End | 11 |
| Total Slippage Cost | $5,119.62 (+5.12% of start) |
| Avg Slippage / Trade | $19.03 |

_**IRR** is the annualized money-weighted (internal) rate of return on the capital actually put into positions: it solves for the rate that discounts the dated BUY outflows, SELL inflows, and the terminal mark-to-market of open positions to zero. It ignores idle cash, so it measures how the *deployed* capital performed, and is bounded at -100%. Being annualized, short backtests can extrapolate to large figures. **Total Return** is on the full starting portfolio (cash included) and is what the SPY/QQQ/Equal-Wt comparisons above use, since those benchmarks are fully invested._

## Strategy Parameters Used

| Parameter | Value |
|-----------|-------|
| Starting Portfolio | $100,000.00 |
| Max Position Size | 8.5% |
| Max Total Exposure | 90% |
| Max New Trades / Day | 3 |
| Stop Loss | 15.0% |
| Take Profit | none |
| Trailing Stop | none |
| Max Holding Period | 90 trading days |
| Slippage | 0.10% per fill |

## Ticker Universe

`CRWD`, `ORCL`, `COIN`, `NFLX`, `PANW`, `GOOGL`, `BAC`, `MSFT`, `AVGO`, `AMZN`, `COST`, `ASML`, `AAPL`, `JPM`, `TSM`, `GS`, `META`, `TSLA`, `MU`, `AMD`, `NVDA`, `LLY`, `VST`, `AXON`, `GE`, `PLTR`, `OXY`, `INTC`, `BA`, `PFE`, `PYPL`, `SEDG`, `PLUG`

## Trade Log (last 20 trades)

| Date | Action | Ticker | Shares | Price | Value | Reason | P&L | Hold Days |
|------|--------|--------|--------|-------|-------|--------|-----|-----------|
| 2026-03-16 | BUY | OXY | 471 | $57.04 | $26,867.63 | momentum_score=0.7667 | — | — |
| 2026-03-26 | SELL | META | 42 | $546.99 | $22,973.68 | stop_loss | $-4,813.31 | 67.1 |
| 2026-03-27 | BUY | NFLX | 291 | $93.52 | $27,215.31 | momentum_score=0.8909 | — | — |
| 2026-04-23 | SELL | GS | 31 | $926.29 | $28,714.88 | max_holding_period | $1,783.46 | 90.0 |
| 2026-04-24 | BUY | AMD | 95 | $348.16 | $33,074.99 | momentum_score=0.8818 | — | — |
| 2026-04-27 | SELL | MU | 105 | $524.04 | $55,023.72 | max_holding_period | $25,976.66 | 90.0 |
| 2026-04-28 | BUY | INTC | 351 | $84.60 | $29,696.18 | momentum_score=0.9909 | — | — |
| 2026-04-28 | BUY | MU | 56 | $504.79 | $28,268.48 | momentum_score=0.8106 | — | — |
| 2026-04-28 | SELL | GE | 89 | $288.91 | $25,713.06 | max_holding_period | $-2,324.24 | 90.0 |
| 2026-04-29 | BUY | GOOGL | 84 | $350.08 | $29,406.79 | momentum_score=0.7894 | — | — |
| 2026-05-04 | SELL | NVDA | 147 | $198.05 | $29,113.45 | max_holding_period | $1,451.18 | 90.0 |
| 2026-05-04 | SELL | TSM | 93 | $400.27 | $37,225.20 | max_holding_period | $9,355.63 | 90.0 |
| 2026-05-05 | BUY | ORCL | 168 | $185.54 | $31,169.95 | momentum_score=0.8167 | — | — |
| 2026-05-05 | BUY | COIN | 149 | $197.95 | $29,494.21 | momentum_score=0.7773 | — | — |
| 2026-06-03 | SELL | COIN | 149 | $163.06 | $24,295.46 | stop_loss | $-5,198.74 | 20.7 |
| 2026-06-04 | BUY | CRWD | 50 | $719.81 | $35,990.45 | momentum_score=0.8606 | — | — |
| 2026-06-04 | SELL | ASML | 20 | $1,755.71 | $35,114.25 | max_holding_period | $6,083.73 | 90.0 |
| 2026-06-05 | BUY | ASML | 21 | $1,643.38 | $34,511.02 | momentum_score=0.8379 | — | — |
| 2026-06-09 | SELL | AAPL | 107 | $290.26 | $31,057.77 | max_holding_period | $2,248.09 | 90.0 |
| 2026-06-10 | BUY | LLY | 30 | $1,137.51 | $34,125.19 | momentum_score=0.847 | — | — |

## Open Positions at End of Period

| Ticker | Shares | Entry Price | Final Price | Unrealized P&L | Entry Date |
|--------|--------|------------|------------|----------------|------------|
| SEDG | 755 | $35.14 | $60.80 | $19,377.00 | 2026-02-18 |
| OXY | 471 | $57.04 | $56.54 | $-237.29 | 2026-03-16 |
| NFLX | 291 | $93.52 | $80.34 | $-3,836.37 | 2026-03-27 |
| AMD | 95 | $348.16 | $511.57 | $15,524.16 | 2026-04-24 |
| INTC | 351 | $84.60 | $124.57 | $14,027.89 | 2026-04-28 |
| MU | 56 | $504.79 | $981.61 | $26,701.68 | 2026-04-28 |
| GOOGL | 84 | $350.08 | $359.68 | $806.33 | 2026-04-29 |
| ORCL | 168 | $185.54 | $184.13 | $-236.11 | 2026-05-05 |
| CRWD | 50 | $719.81 | $682.80 | $-1,850.45 | 2026-06-04 |
| ASML | 21 | $1,643.38 | $1,863.55 | $4,623.53 | 2026-06-05 |
| LLY | 30 | $1,137.51 | $1,133.00 | $-135.19 | 2026-06-10 |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2023-01-03 | $100,000.00 | — | +0.00% | +0.00% | +0.00% | +0.00% |
| 2023-01-04 | $99,973.87 | -0.03% | -0.03% | +0.77% | +0.48% | +2.24% |
| 2023-01-05 | $99,816.75 | -0.16% | -0.18% | -0.38% | -1.10% | +0.33% |
| 2023-01-06 | $100,954.28 | +1.14% | +0.95% | +1.91% | +1.63% | +2.84% |
| 2023-01-09 | $100,791.47 | -0.16% | +0.79% | +1.85% | +2.29% | +4.29% |
| 2026-06-08 | $416,766.68 | +3.02% | +316.77% | +102.49% | +175.98% | +374.97% |
| 2026-06-09 | $406,120.35 | -2.55% | +306.12% | +101.89% | +172.80% | +368.37% |
| 2026-06-10 | $397,008.27 | -2.24% | +297.01% | +98.71% | +167.35% | +356.05% |
| 2026-06-11 | $415,334.59 | +4.62% | +315.33% | +102.09% | +176.38% | +374.15% |
| 2026-06-12 | $419,554.63 | +1.02% | +319.55% | +103.18% | +178.01% | +373.88% |


## Signal Predictiveness

_Cross-section of 28,479 (date, ticker) signal observations. Correlations are Pearson vs forward returns._

| Signal | vs fwd 5d | vs fwd 10d | vs fwd 20d |
|--------|-----------|------------|------------|
| return_1d | -0.01 | -0.00 | 0.00 |
| return_5d | -0.01 | -0.01 | 0.01 |
| return_20d | -0.00 | 0.01 | 0.01 |
| vol_ratio | 0.01 | 0.02 | 0.02 |
| vol_adj_mom_20d | -0.00 | 0.00 | 0.01 |
| composite_score | 0.01 | 0.01 | 0.02 |

**Forward returns by composite-score quintile** (5 = highest-ranked):

| Quintile | N | Avg fwd 5d | Win 5d | Avg fwd 10d | Win 10d | Avg fwd 20d | Win 20d |
|----------|---|-----------|--------|-------------|---------|-------------|---------|
| Q1 | 6041 | +0.88% | +53.92% | +1.60% | +56.16% | +3.21% | +58.46% |
| Q2 | 5178 | +0.93% | +56.09% | +1.91% | +58.76% | +3.28% | +61.04% |
| Q3 | 6041 | +0.77% | +55.46% | +1.72% | +57.31% | +3.30% | +59.60% |
| Q4 | 5178 | +0.74% | +56.00% | +1.48% | +57.03% | +3.26% | +59.48% |
| Q5 | 6041 | +0.92% | +54.71% | +1.77% | +55.77% | +3.68% | +58.12% |

**Top-minus-bottom quintile spread:** 5d +0.04%  |  10d +0.17%  |  20d +0.48%  (positive ⇒ higher-ranked names outperform lower-ranked names).

## Entry vs Exit Attribution

_Buy the top 3 ranked names each day, hold a fixed period, **no** stop-loss / take-profit / max-holding. Next-day entry, slippage applied._

| Hold period | Raw avg return / trade | Raw win rate | N trades |
|-------------|------------------------|--------------|----------|
| 5d | +0.96% | +54.46% | 2543 |
| 10d | +1.84% | +55.02% | 2528 |
| 20d | +3.95% | +57.53% | 2498 |
| 30d | +5.48% | +59.40% | 2468 |

**Full strategy (with exit rules):** total return +319.55%, win rate +62.02%, avg hold 71.12 trading days.

The raw signal (buy top names, hold fixed, no stops) is **positive across holding periods** (avg +3.06% per trade, 57% win rate). That points to genuine signal quality — higher-ranked names tend to rise even without exit rules.

## P&L Attribution

**Top 5 contributors:**

| Ticker | P&L |
|--------|-----|
| MU | $67,896.29 |
| PLTR | $45,070.92 |
| NVDA | $34,490.83 |
| AMD | $23,332.28 |
| INTC | $19,745.75 |

**Worst 5 contributors:**

| Ticker | P&L |
|--------|-----|
| COIN | $-12,916.46 |
| BA | $-7,251.07 |
| PLUG | $-6,174.83 |
| TSLA | $-5,287.51 |
| OXY | $-3,999.44 |

**P&L by asset group:**

| Group | P&L |
|-------|-----|
| semiconductors | $110,495.30 |
| mega_cap_growth | $66,212.76 |
| software_cybersecurity | $15,036.55 |
| financial_crypto_beta | $-9,693.37 |
| _(ungrouped)_ | $137,503.39 |

## Turnover and Re-entry Diagnostics

| Metric | Value |
|--------|-------|
| Total trades | 269 |
| Trades / month | 6.50 |
| Avg holding period | 71.12 trading days |
| Stop-loss → re-entry ≤5d | 2 |

**Most-entered tickers:** `META`×7, `MU`×7, `AMD`×7, `GE`×6, `ASML`×6, `AMZN`×6, `TSLA`×6, `INTC`×6

**Most re-entered after a stop-loss:** `INTC`×2

## Exposure and Benchmark Capture

| Metric | Value |
|--------|-------|
| Avg exposure | +92.42% |
| Max exposure | +98.37% |
| Avg cash (drag) | +7.58% |
| Correlation to SPY | 0.78 |
| Correlation to QQQ | 0.84 |
| Beta to SPY | 1.25 |
| Beta to QQQ | 1.02 |
| Up-capture vs QQQ | 1.15 |
| Down-capture vs QQQ | 1.06 |

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

**Baseline (as configured):** +319.55% return  |  -28.09% max drawdown  |  +62.02% win rate  |  2.66 profit factor

### Run-wide parameters

#### Max Total Exposure  (baseline: 90%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 50% | +117.17% | +13.99% | -256.71% | -18.03% | 154 | +60.81% | 2.59 |
| 70% | +213.03% | +109.85% | -160.85% | -25.23% | 218 | +60.00% | 2.56 |
| 90% ◀ baseline | +319.55% | +216.38% | -54.32% | -28.09% | 269 | +62.02% | 2.66 |
| 100% | +261.53% | +158.35% | -112.35% | -34.34% | 279 | +57.46% | 2.13 |

#### Max Position Size  (baseline: 8.50%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 4.25% | +219.08% | +115.90% | -154.80% | -24.20% | 508 | +57.61% | 2.42 |
| 8.50% ◀ baseline | +319.55% | +216.38% | -54.32% | -28.09% | 269 | +62.02% | 2.66 |
| 12.75% | +374.44% | +271.26% | +0.57% | -30.39% | 181 | +58.62% | 2.62 |
| 17.00% | +141.89% | +38.71% | -231.99% | -29.89% | 137 | +48.48% | 1.62 |
| 25.50% | +143.00% | +39.82% | -230.88% | -37.17% | 90 | +41.86% | 1.70 |

#### Max New Trades / Day  (baseline: 3)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 1 | +336.52% | +233.34% | -37.36% | -25.78% | 258 | +62.10% | 2.89 |
| 2 | +293.46% | +190.28% | -80.42% | -30.27% | 255 | +60.66% | 2.61 |
| 3 ◀ baseline | +319.55% | +216.38% | -54.32% | -28.09% | 269 | +62.02% | 2.66 |
| 5 | +299.53% | +196.35% | -74.35% | -29.24% | 269 | +59.69% | 2.56 |

#### Min Composite Score  (baseline: 0.70)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| none | +231.42% | +128.24% | -142.46% | -31.62% | 270 | +56.92% | 2.04 |
| 0.60 | +231.42% | +128.24% | -142.46% | -31.62% | 270 | +56.92% | 2.04 |
| 0.70 ◀ baseline | +319.55% | +216.38% | -54.32% | -28.09% | 269 | +62.02% | 2.66 |

#### Slippage  (baseline: 0.10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 0.05% | +340.34% | +237.16% | -33.53% | -30.00% | 270 | +62.31% | 2.58 |
| 0.10% ◀ baseline | +319.55% | +216.38% | -54.32% | -28.09% | 269 | +62.02% | 2.66 |
| 0.20% | +313.31% | +210.13% | -60.57% | -27.59% | 267 | +62.50% | 2.68 |
| 0.50% | +255.25% | +152.07% | -118.63% | -33.21% | 265 | +61.42% | 2.37 |

#### Re-entry Recovery Gate  (baseline: 10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +314.76% | +211.59% | -59.11% | -27.62% | 270 | +62.31% | 2.60 |
| 0% | +314.76% | +211.59% | -59.11% | -27.62% | 270 | +62.31% | 2.60 |
| 5% | +355.20% | +252.02% | -18.68% | -27.62% | 266 | +62.50% | 2.70 |
| 10% ◀ baseline | +319.55% | +216.38% | -54.32% | -28.09% | 269 | +62.02% | 2.66 |

#### Signal Weight Profile  (baseline: baseline)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| baseline ◀ baseline | +319.55% | +216.38% | -54.32% | -28.09% | 269 | +62.02% | 2.66 |
| no_1d | +249.00% | +145.82% | -124.88% | -28.84% | 269 | +58.46% | 2.08 |
| less_1d | +262.23% | +159.05% | -111.65% | -32.75% | 273 | +56.49% | 2.31 |
| more_volume | +319.55% | +216.38% | -54.32% | -28.09% | 269 | +62.02% | 2.66 |

### Best 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | max_position_pct | 12.75% | +374.44% | +0.57% | -30.39% | 2.62 |
| 2 | reentry_recover_pct | 5% | +355.20% | -18.68% | -27.62% | 2.70 |
| 3 | slippage | 0.05% | +340.34% | -33.53% | -30.00% | 2.58 |
| 4 | max_new_trades_per_day | 1 | +336.52% | -37.36% | -25.78% | 2.89 |
| 5 | max_total_exposure | 90% | +319.55% | -54.32% | -28.09% | 2.66 |

### Worst 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | max_total_exposure | 50% | +117.17% | -256.71% | -18.03% | 2.59 |
| 2 | max_position_pct | 17.00% | +141.89% | -231.99% | -29.89% | 1.62 |
| 3 | max_position_pct | 25.50% | +143.00% | -230.88% | -37.17% | 1.70 |
| 4 | max_total_exposure | 70% | +213.03% | -160.85% | -25.23% | 2.56 |
| 5 | max_position_pct | 4.25% | +219.08% | -154.80% | -24.20% | 2.42 |

### Robustness Notes

The baseline outperforms 86% of all variants. This is broadly consistent across parameter dimensions, suggesting the baseline settings are reasonably competitive in-sample.

The widest in-sample return spread belongs to `max_position_pct` (232.6 pp range across its variants); `reentry_recover_pct` shows the narrowest spread (40.4 pp), suggesting the strategy is least sensitive to that parameter in this period.

Improvements that appear in only one or two variants should be treated with skepticism — isolated peaks are more likely to reflect in-sample noise than genuine edge. Prefer settings that perform consistently across the full sweep.
