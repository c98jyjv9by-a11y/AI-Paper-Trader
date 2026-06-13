# Scenario — model_v2

Full 21-name universe with one uniform exit rule applied to every ticker (stop 15%, no take-profit, no trailing stop, 60-day max hold) plus the trough-based anti-falling-knife re-entry gate. Composite ranking drives entries.

**Universe (21):** CRWD, ORCL, COIN, NFLX, PANW, GOOGL, BAC, MSFT, AVGO, AMZN, COST, ASML, AAPL, JPM, TSM, GS, META, TSLA, MU, AMD, NVDA

---

# AI Paper Trader — Backtest Report
**Period:** 2023-01-01 → 2026-06-13  |  **Generated:** 2026-06-13

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Ending Balance | $364,565.04 | $203,179.10 | $278,006.50 | $517,036.10 |
| Total Return | +264.57% | +103.18% | +178.01% | +417.04% |
| Max Drawdown | -23.68% | -18.76% | -22.77% | -29.93% |
| Excess vs SPY | +161.39% | — | — | — |
| Excess vs QQQ | +86.56% | — | — | — |
| Excess vs Equal-Wt | -152.47% | — | — | — |
| 1-Year Return | +45.79% | +24.27% | +35.82% | +56.60% |
| 2-Year Return | +74.54% | +41.84% | +56.89% | +90.94% |
| 3-Year Return | +166.87% | +79.62% | +107.88% | +245.68% |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $364,565.04 |
| **IRR (annualized, money-weighted)** | **+59.23%** |
| Total Return (on full $ portfolio) | +264.57% |
| Total Capital Deployed (all entries) | $3,014,831.01 |
| Avg Capital Deployed (snapshot) | $178,859.00 (+178.86% of portfolio) |
| Peak Capital Deployed (snapshot) | $326,388.55 (+326.39% of portfolio) |
| Time Invested | +99.88% of trading days |
| Trading Days | 864 |
| Total Trades | 648 (334 buys, 314 sells) |
| Win Rate | +64.01% |
| Average Win | $1,732.38 |
| Average Loss | $-1,239.43 |
| Profit Factor | 2.49 |
| Avg Holding Period | 51.8 approx. trading days |
| Largest Winner | $10,920.59 |
| Largest Loser | $-2,482.79 |
| Open Positions at End | 20 |
| Total Slippage Cost | $5,967.89 (+5.97% of start) |
| Avg Slippage / Trade | $9.21 |

_**IRR** is the annualized money-weighted (internal) rate of return on the capital actually put into positions: it solves for the rate that discounts the dated BUY outflows, SELL inflows, and the terminal mark-to-market of open positions to zero. It ignores idle cash, so it measures how the *deployed* capital performed, and is bounded at -100%. Being annualized, short backtests can extrapolate to large figures. **Total Return** is on the full starting portfolio (cash included) and is what the SPY/QQQ/Equal-Wt comparisons above use, since those benchmarks are fully invested._

## Strategy Parameters Used

| Parameter | Value |
|-----------|-------|
| Starting Portfolio | $100,000.00 |
| Max Position Size | 4.3% (auto: 90% ÷ 21 tickers) |
| Max Total Exposure | 90% |
| Max New Trades / Day | 5 |
| Stop Loss | 15.0% |
| Take Profit | none |
| Trailing Stop | none |
| Max Holding Period | 60 trading days |
| Slippage | 0.10% per fill |

## Ticker Universe

`CRWD`, `ORCL`, `COIN`, `NFLX`, `PANW`, `GOOGL`, `BAC`, `MSFT`, `AVGO`, `AMZN`, `COST`, `ASML`, `AAPL`, `JPM`, `TSM`, `GS`, `META`, `TSLA`, `MU`, `AMD`, `NVDA`

## Trade Log (last 20 trades)

| Date | Action | Ticker | Shares | Price | Value | Reason | P&L | Hold Days |
|------|--------|--------|--------|-------|-------|--------|-----|-----------|
| 2026-04-16 | BUY | AVGO | 34 | $398.87 | $13,561.53 | momentum_score=0.8143 | — | — |
| 2026-05-05 | SELL | PANW | 79 | $183.80 | $14,519.88 | max_holding_period | $1,431.52 | 60.0 |
| 2026-05-05 | SELL | ORCL | 84 | $185.16 | $15,553.83 | max_holding_period | $2,156.43 | 60.0 |
| 2026-05-05 | SELL | MSFT | 32 | $410.08 | $13,122.57 | max_holding_period | $-56.60 | 60.0 |
| 2026-05-06 | BUY | ORCL | 77 | $194.22 | $14,955.25 | momentum_score=0.6452 | — | — |
| 2026-05-08 | BUY | PANW | 74 | $208.09 | $15,398.50 | momentum_score=0.8452 | — | — |
| 2026-05-08 | BUY | MSFT | 34 | $414.64 | $14,097.66 | momentum_score=0.5286 | — | — |
| 2026-05-12 | SELL | COIN | 78 | $207.43 | $16,179.73 | max_holding_period | $3,217.22 | 60.0 |
| 2026-05-15 | BUY | COIN | 72 | $195.63 | $14,085.03 | momentum_score=0.7357 | — | — |
| 2026-05-18 | SELL | AMZN | 61 | $264.60 | $16,140.30 | max_holding_period | $3,606.31 | 60.0 |
| 2026-05-21 | SELL | NFLX | 157 | $89.21 | $14,006.08 | max_holding_period | $712.17 | 60.0 |
| 2026-05-26 | SELL | TSLA | 31 | $433.16 | $13,427.85 | max_holding_period | $912.43 | 60.7 |
| 2026-05-27 | BUY | TSLA | 36 | $440.80 | $15,868.81 | momentum_score=0.6286 | — | — |
| 2026-05-27 | SELL | CRWD | 32 | $644.71 | $20,630.87 | max_holding_period | $7,572.06 | 60.0 |
| 2026-05-27 | SELL | JPM | 42 | $298.98 | $12,557.19 | max_holding_period | $34.32 | 60.0 |
| 2026-05-28 | BUY | CRWD | 24 | $671.67 | $16,120.10 | momentum_score=0.6524 | — | — |
| 2026-05-29 | BUY | AMZN | 57 | $270.91 | $15,441.91 | momentum_score=0.5167 | — | — |
| 2026-06-03 | SELL | COIN | 72 | $163.06 | $11,740.09 | stop_loss | $-2,344.94 | 13.6 |
| 2026-06-05 | BUY | JPM | 52 | $312.68 | $16,259.48 | momentum_score=0.5857 | — | — |
| 2026-06-09 | BUY | NFLX | 188 | $81.49 | $15,320.38 | momentum_score=0.5095 | — | — |

## Open Positions at End of Period

| Ticker | Shares | Entry Price | Final Price | Unrealized P&L | Entry Date |
|--------|--------|------------|------------|----------------|------------|
| GS | 15 | $828.45 | $1,062.75 | $3,514.50 | 2026-03-23 |
| AMD | 60 | $220.49 | $511.57 | $17,464.78 | 2026-03-25 |
| ASML | 8 | $1,327.93 | $1,863.55 | $4,284.97 | 2026-03-26 |
| TSM | 35 | $325.67 | $423.93 | $3,438.98 | 2026-03-26 |
| NVDA | 69 | $171.21 | $205.19 | $2,344.50 | 2026-03-26 |
| AAPL | 47 | $246.65 | $291.13 | $2,090.59 | 2026-03-30 |
| GOOGL | 42 | $297.51 | $359.68 | $2,611.15 | 2026-04-01 |
| COST | 12 | $1,014.50 | $982.35 | $-385.83 | 2026-04-02 |
| MU | 33 | $366.61 | $981.61 | $20,295.13 | 2026-04-02 |
| BAC | 248 | $50.07 | $56.02 | $1,475.58 | 2026-04-07 |
| META | 20 | $629.02 | $566.98 | $-1,240.77 | 2026-04-09 |
| AVGO | 34 | $398.87 | $382.07 | $-571.15 | 2026-04-16 |
| ORCL | 77 | $194.22 | $184.13 | $-777.24 | 2026-05-06 |
| PANW | 74 | $208.09 | $279.62 | $5,293.38 | 2026-05-08 |
| MSFT | 34 | $414.64 | $390.74 | $-812.50 | 2026-05-08 |
| TSLA | 36 | $440.80 | $406.43 | $-1,237.33 | 2026-05-27 |
| CRWD | 24 | $671.67 | $682.80 | $267.10 | 2026-05-28 |
| AMZN | 57 | $270.91 | $238.55 | $-1,844.56 | 2026-05-29 |
| JPM | 52 | $312.68 | $320.72 | $417.96 | 2026-06-05 |
| NFLX | 188 | $81.49 | $80.34 | $-216.46 | 2026-06-09 |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2023-01-03 | $100,000.00 | — | +0.00% | +0.00% | +0.00% | +0.00% |
| 2023-01-04 | $99,978.65 | -0.02% | -0.02% | +0.77% | +0.48% | +2.14% |
| 2023-01-05 | $99,826.35 | -0.15% | -0.17% | -0.38% | -1.10% | -0.12% |
| 2023-01-06 | $100,852.03 | +1.03% | +0.85% | +1.91% | +1.63% | +2.44% |
| 2023-01-09 | $101,821.02 | +0.96% | +1.82% | +1.85% | +2.29% | +4.40% |
| 2026-06-08 | $363,639.13 | +1.42% | +263.64% | +102.49% | +175.98% | +415.37% |
| 2026-06-09 | $359,887.90 | -1.03% | +259.89% | +101.89% | +172.80% | +408.98% |
| 2026-06-10 | $352,745.26 | -1.98% | +252.75% | +98.71% | +167.35% | +394.43% |
| 2026-06-11 | $363,285.58 | +2.99% | +263.29% | +102.09% | +176.38% | +416.73% |
| 2026-06-12 | $364,565.04 | +0.35% | +264.56% | +103.18% | +178.01% | +417.04% |


## Signal Predictiveness

_Cross-section of 18,123 (date, ticker) signal observations. Correlations are Pearson vs forward returns._

| Signal | vs fwd 5d | vs fwd 10d | vs fwd 20d |
|--------|-----------|------------|------------|
| return_1d | -0.01 | 0.00 | 0.01 |
| return_5d | -0.01 | 0.02 | 0.03 |
| return_20d | 0.02 | 0.03 | 0.00 |
| vol_ratio | 0.01 | 0.03 | 0.02 |
| vol_adj_mom_20d | 0.00 | 0.00 | -0.01 |
| composite_score | 0.00 | 0.00 | 0.01 |

**Forward returns by composite-score quintile** (5 = highest-ranked):

| Quintile | N | Avg fwd 5d | Win 5d | Avg fwd 10d | Win 10d | Avg fwd 20d | Win 20d |
|----------|---|-----------|--------|-------------|---------|-------------|---------|
| Q1 | 4315 | +1.09% | +57.39% | +2.11% | +60.54% | +4.24% | +63.36% |
| Q2 | 3452 | +1.07% | +58.12% | +2.10% | +60.80% | +3.81% | +63.92% |
| Q3 | 3452 | +0.82% | +56.17% | +1.81% | +58.78% | +3.60% | +61.64% |
| Q4 | 3452 | +0.90% | +57.01% | +1.87% | +58.52% | +3.73% | +61.82% |
| Q5 | 3452 | +1.05% | +55.27% | +1.97% | +56.73% | +4.19% | +58.98% |

**Top-minus-bottom quintile spread:** 5d -0.04%  |  10d -0.14%  |  20d -0.06%  (positive ⇒ higher-ranked names outperform lower-ranked names).

## Entry vs Exit Attribution

_Buy the top 5 ranked names each day, hold a fixed period, **no** stop-loss / take-profit / max-holding. Next-day entry, slippage applied._

| Hold period | Raw avg return / trade | Raw win rate | N trades |
|-------------|------------------------|--------------|----------|
| 5d | +0.75% | +53.08% | 4290 |
| 10d | +1.75% | +56.20% | 4265 |
| 20d | +3.84% | +59.19% | 4215 |
| 30d | +5.45% | +62.26% | 4165 |

**Full strategy (with exit rules):** total return +264.57%, win rate +64.01%, avg hold 51.84 trading days.

The raw signal (buy top names, hold fixed, no stops) is **positive across holding periods** (avg +2.95% per trade, 58% win rate). That points to genuine signal quality — higher-ranked names tend to rise even without exit rules.

## P&L Attribution

**Top 5 contributors:**

| Ticker | P&L |
|--------|-----|
| MU | $42,490.77 |
| AMD | $23,289.49 |
| NVDA | $21,494.99 |
| TSM | $19,085.12 |
| COIN | $18,406.75 |

**Worst 5 contributors:**

| Ticker | P&L |
|--------|-----|
| MSFT | $1,189.90 |
| COST | $4,077.90 |
| META | $5,415.34 |
| BAC | $5,437.81 |
| ORCL | $5,471.48 |

**P&L by asset group:**

| Group | P&L |
|-------|-----|
| semiconductors | $83,163.93 |
| mega_cap_growth | $59,171.18 |
| financial_crypto_beta | $31,116.60 |
| software_cybersecurity | $27,466.01 |
| _(ungrouped)_ | $63,647.10 |

## Turnover and Re-entry Diagnostics

| Metric | Value |
|--------|-------|
| Total trades | 648 |
| Trades / month | 15.67 |
| Avg holding period | 51.84 trading days |
| Stop-loss → re-entry ≤5d | 21 |

**Most-entered tickers:** `COIN`×21, `TSLA`×20, `MU`×18, `ORCL`×17, `META`×16, `NVDA`×16, `AMD`×16, `CRWD`×16

**Most re-entered after a stop-loss:** `MU`×3, `PANW`×3, `TSLA`×2, `AMD`×2, `NVDA`×2

## Exposure and Benchmark Capture

| Metric | Value |
|--------|-------|
| Avg exposure | +82.27% |
| Max exposure | +93.52% |
| Avg cash (drag) | +17.73% |
| Correlation to SPY | 0.84 |
| Correlation to QQQ | 0.91 |
| Beta to SPY | 1.10 |
| Beta to QQQ | 0.91 |
| Up-capture vs QQQ | 1.03 |
| Down-capture vs QQQ | 0.96 |

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

**Baseline (as configured):** +264.57% return  |  -23.68% max drawdown  |  +64.01% win rate  |  2.49 profit factor

### Run-wide parameters

#### Max Total Exposure  (baseline: 90%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 50% | +109.99% | +6.81% | -307.04% | -13.22% | 646 | +63.26% | 2.70 |
| 70% | +177.13% | +73.95% | -239.91% | -18.64% | 646 | +63.26% | 2.59 |
| 90% ◀ baseline | +264.57% | +161.39% | -152.47% | -23.68% | 648 | +64.01% | 2.49 |
| 100% | +304.68% | +201.50% | -112.36% | -27.07% | 643 | +62.82% | 2.36 |

#### Max Position Size  (baseline: 4.29%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 2.14% | +95.14% | -8.04% | -321.90% | -11.97% | 650 | +63.81% | 2.73 |
| 4.29% ◀ baseline | +264.57% | +161.39% | -152.47% | -23.68% | 648 | +64.01% | 2.49 |
| 6.43% | +256.45% | +153.27% | -160.59% | -26.47% | 486 | +63.56% | 2.19 |
| 8.57% | +311.19% | +208.01% | -105.85% | -28.55% | 362 | +65.91% | 2.34 |
| 12.86% | +201.43% | +98.25% | -215.61% | -30.66% | 245 | +61.34% | 1.95 |

#### Max New Trades / Day  (baseline: 5)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 1 | +233.92% | +130.74% | -183.12% | -23.75% | 633 | +65.15% | 2.49 |
| 2 | +238.75% | +135.57% | -178.28% | -24.95% | 652 | +64.24% | 2.37 |
| 3 | +255.23% | +152.05% | -161.81% | -23.94% | 654 | +63.41% | 2.41 |
| 5 ◀ baseline | +264.57% | +161.39% | -152.47% | -23.68% | 648 | +64.01% | 2.49 |

#### Min Composite Score  (baseline: none)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| none ◀ baseline | +264.57% | +161.39% | -152.47% | -23.68% | 648 | +64.01% | 2.49 |
| 0.60 | +237.85% | +134.67% | -179.19% | -23.26% | 621 | +66.23% | 2.53 |
| 0.70 | +214.05% | +110.87% | -202.99% | -18.88% | 549 | +65.79% | 2.71 |

#### Slippage  (baseline: 0.10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 0.05% | +268.03% | +164.85% | -149.01% | -24.05% | 646 | +64.54% | 2.57 |
| 0.10% ◀ baseline | +264.57% | +161.39% | -152.47% | -23.68% | 648 | +64.01% | 2.49 |
| 0.20% | +251.29% | +148.11% | -165.74% | -24.23% | 650 | +62.22% | 2.33 |
| 0.50% | +226.07% | +122.89% | -190.96% | -24.69% | 652 | +61.08% | 2.21 |

#### Re-entry Recovery Gate  (baseline: 5%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +264.65% | +161.47% | -152.39% | -24.45% | 653 | +63.41% | 2.46 |
| 0% | +264.65% | +161.47% | -152.39% | -24.45% | 653 | +63.41% | 2.46 |
| 5% ◀ baseline | +264.57% | +161.39% | -152.47% | -23.68% | 648 | +64.01% | 2.49 |
| 10% | +257.39% | +154.21% | -159.65% | -20.96% | 631 | +63.07% | 2.61 |

#### Signal Weight Profile  (baseline: baseline)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| baseline ◀ baseline | +264.57% | +161.39% | -152.47% | -23.68% | 648 | +64.01% | 2.49 |
| no_1d | +258.19% | +155.01% | -158.85% | -24.90% | 640 | +65.27% | 2.47 |
| less_1d | +247.22% | +144.05% | -169.81% | -26.28% | 640 | +64.95% | 2.44 |
| more_volume | +264.57% | +161.39% | -152.47% | -23.68% | 648 | +64.01% | 2.49 |

### Best 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | max_position_pct | 8.57% | +311.19% | -105.85% | -28.55% | 2.34 |
| 2 | max_total_exposure | 100% | +304.68% | -112.36% | -27.07% | 2.36 |
| 3 | slippage | 0.05% | +268.03% | -149.01% | -24.05% | 2.57 |
| 4 | reentry_recover_pct | off | +264.65% | -152.39% | -24.45% | 2.46 |
| 5 | reentry_recover_pct | 0% | +264.65% | -152.39% | -24.45% | 2.46 |

### Worst 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | max_position_pct | 2.14% | +95.14% | -321.90% | -11.97% | 2.73 |
| 2 | max_total_exposure | 50% | +109.99% | -307.04% | -13.22% | 2.70 |
| 3 | max_total_exposure | 70% | +177.13% | -239.91% | -18.64% | 2.59 |
| 4 | max_position_pct | 12.86% | +201.43% | -215.61% | -30.66% | 1.95 |
| 5 | min_composite_score | 0.70 | +214.05% | -202.99% | -18.88% | 2.71 |

### Robustness Notes

The baseline outperforms 82% of all variants. This is broadly consistent across parameter dimensions, suggesting the baseline settings are reasonably competitive in-sample.

The widest in-sample return spread belongs to `max_position_pct` (216.1 pp range across its variants); `reentry_recover_pct` shows the narrowest spread (7.3 pp), suggesting the strategy is least sensitive to that parameter in this period.

Improvements that appear in only one or two variants should be treated with skepticism — isolated peaks are more likely to reflect in-sample noise than genuine edge. Prefer settings that perform consistently across the full sweep.
