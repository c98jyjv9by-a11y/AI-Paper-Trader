# Scenario — LevEtf

2-ticker leveraged-ETF scenario (TQQQ +3x QQQ / SQQQ -3x QQQ) running model_v4's rules, pre-adapted for 3x leverage: auto per-name sizing, 25% stop, 0.60 vol target. Isolated from model_v4 (separate universe + separate outputs).

**Universe (2):** TQQQ, SQQQ

---

# AI Paper Trader — Backtest Report
**Period:** 2018-06-22 → 2026-06-22  |  **Generated:** 2026-06-22

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Ending Balance | $125,436.53 | $306,020.10 | $442,415.90 | $567,446.20 |
| Total Return | +25.44% | +206.02% | +342.42% | +467.45% |
| Max Drawdown | -45.61% | -33.72% | -35.12% | -80.97% |
| Excess vs SPY | -180.58% | — | — | — |
| Excess vs QQQ | -316.98% | — | — | — |
| Excess vs Equal-Wt | -442.01% | — | — | — |
| 1-Year Return | +27.86% | +26.65% | +40.75% | +129.40% |
| 2-Year Return | -1.97% | +39.73% | +53.81% | +119.03% |
| 3-Year Return | -2.96% | +75.22% | +102.84% | +308.99% |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $125,436.53 |
| **IRR (annualized, money-weighted)** | **+3.87%** |
| Total Return (on full $ portfolio) | +25.44% |
| Total Capital Deployed (all entries) | $2,587,276.21 |
| Avg Capital Deployed (snapshot) | $89,649.28 (+89.65% of portfolio) |
| Peak Capital Deployed (snapshot) | $141,076.75 (+141.08% of portfolio) |
| Time Invested | +99.20% of trading days |
| Trading Days | 2009 |
| Total Trades | 101 (51 buys, 50 sells) |
| Win Rate | +34.00% |
| Average Win | $22,269.37 |
| Average Loss | $-11,931.25 |
| Profit Factor | 0.96 |
| Avg Holding Period | 66.4 approx. trading days |
| Largest Winner | $70,307.15 |
| Largest Loser | $-21,500.05 |
| Open Positions at End | 1 |
| Total Slippage Cost | $5,112.73 (+5.11% of start) |
| Avg Slippage / Trade | $50.62 |

_**IRR** is the annualized money-weighted (internal) rate of return on the capital actually put into positions: it solves for the rate that discounts the dated BUY outflows, SELL inflows, and the terminal mark-to-market of open positions to zero. It ignores idle cash, so it measures how the *deployed* capital performed, and is bounded at -100%. Being annualized, short backtests can extrapolate to large figures. **Total Return** is on the full starting portfolio (cash included) and is what the SPY/QQQ/Equal-Wt comparisons above use, since those benchmarks are fully invested._

## Strategy Parameters Used

| Parameter | Value |
|-----------|-------|
| Starting Portfolio | $100,000.00 |
| Max Position Size | 45.0% (auto: 90% ÷ 2 tickers) |
| Max Total Exposure | 90% |
| Max New Trades / Day | 2 |
| Stop Loss | 25.0% |
| Take Profit | none |
| Trailing Stop | none |
| Max Holding Period | 90 trading days |
| Stop-loss only if score < | 0.9 |
| Max-hold only if score < | 0.8 |
| Score-decay sell | none |
| Persistence buy | > 0.9 for 3d  (rotate-funded) |
| Vol target (annualized) | 60% — scale exposure by target/forecast vol |
| Slippage | 0.10% per fill |

## Ticker Universe

`TQQQ`, `SQQQ`

## Trade Log (last 20 trades)

| Date | Action | Ticker | Shares | Price | Value | Reason | P&L | Hold Days |
|------|--------|--------|--------|-------|-------|--------|-----|-----------|
| 2024-12-18 | SELL | TQQQ | 1662 | $40.47 | $67,252.83 | max_holding_period | $15,154.12 | 90.0 |
| 2024-12-19 | BUY | SQQQ | 370 | $142.87 | $52,860.24 | momentum_score=0.8 | — | — |
| 2024-12-19 | BUY | TQQQ | 1286 | $39.97 | $51,405.41 | momentum_score=0.7 | — | — |
| 2025-03-10 | SELL | TQQQ | 1286 | $29.58 | $38,040.39 | stop_loss | $-13,365.01 | 57.9 |
| 2025-03-26 | BUY | TQQQ | 1447 | $31.50 | $45,582.53 | momentum_score=0.7 | — | — |
| 2025-04-04 | SELL | TQQQ | 1447 | $20.38 | $29,492.75 | stop_loss | $-16,089.77 | 6.4 |
| 2025-04-28 | SELL | SQQQ | 370 | $149.27 | $55,229.20 | max_holding_period | $2,368.96 | 92.9 |
| 2025-04-29 | BUY | TQQQ | 1493 | $27.27 | $40,716.80 | momentum_score=0.875 | — | — |
| 2025-05-12 | BUY | SQQQ | 303 | $119.50 | $36,209.26 | momentum_score=0.8 | — | — |
| 2025-07-17 | SELL | SQQQ | 303 | $88.79 | $26,902.13 | stop_loss | $-9,307.13 | 47.1 |
| 2025-09-02 | SELL | TQQQ | 1493 | $43.32 | $64,669.74 | max_holding_period | $23,952.95 | 90.0 |
| 2025-09-04 | BUY | TQQQ | 1048 | $45.62 | $47,804.62 | momentum_score=0.825 | — | — |
| 2025-10-13 | BUY | SQQQ | 615 | $72.90 | $44,832.82 | momentum_score=0.8 | — | — |
| 2026-01-08 | SELL | TQQQ | 1048 | $54.05 | $56,640.73 | max_holding_period | $8,836.11 | 90.0 |
| 2026-01-09 | BUY | TQQQ | 898 | $55.72 | $50,039.79 | momentum_score=0.775 | — | — |
| 2026-02-26 | SELL | SQQQ | 615 | $69.44 | $42,702.89 | max_holding_period | $-2,129.93 | 97.1 |
| 2026-02-27 | BUY | SQQQ | 679 | $70.35 | $47,767.04 | momentum_score=0.725 | — | — |
| 2026-03-26 | SELL | TQQQ | 898 | $41.19 | $36,987.54 | stop_loss | $-13,052.25 | 54.3 |
| 2026-04-06 | BUY | TQQQ | 1056 | $44.14 | $46,616.17 | momentum_score=0.7 | — | — |
| 2026-04-24 | SELL | SQQQ | 679 | $52.45 | $35,611.85 | stop_loss | $-12,155.19 | 40.0 |

## Open Positions at End of Period

| Ticker | Shares | Entry Price | Final Price | Unrealized P&L | Entry Date |
|--------|--------|------------|------------|----------------|------------|
| TQQQ | 1056 | $44.14 | $82.58 | $40,588.31 | 2026-04-06 |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2018-06-22 | $100,000.00 | — | +0.00% | +0.00% | +0.00% | +0.00% |
| 2018-06-25 | $99,929.84 | -0.07% | -0.07% | -1.36% | -2.25% | +0.02% |
| 2018-06-26 | $100,101.82 | +0.17% | +0.10% | -1.14% | -1.85% | -0.02% |
| 2018-06-27 | $99,483.72 | -0.62% | -0.52% | -1.96% | -3.19% | +0.15% |
| 2018-06-28 | $99,764.82 | +0.28% | -0.24% | -1.40% | -2.36% | -0.10% |
| 2026-06-15 | $127,559.09 | +6.22% | +27.56% | +209.51% | +346.04% | +481.25% |
| 2026-06-16 | $122,638.13 | -3.86% | +22.64% | +207.67% | +337.57% | +449.24% |
| 2026-06-17 | $120,114.29 | -2.06% | +20.11% | +203.83% | +333.16% | +432.82% |
| 2026-06-18 | $125,742.77 | +4.69% | +25.74% | +206.99% | +344.02% | +469.44% |
| 2026-06-22 | $125,436.53 | -0.24% | +25.44% | +206.02% | +342.42% | +467.45% |


## Signal Predictiveness

_Cross-section of 4,016 (date, ticker) signal observations. Correlations are Pearson vs forward returns._

| Signal | vs fwd 5d | vs fwd 10d | vs fwd 20d |
|--------|-----------|------------|------------|
| return_1d | -0.05 | -0.03 | -0.01 |
| return_5d | -0.04 | 0.01 | 0.01 |
| return_20d | 0.01 | 0.01 | -0.00 |
| vol_ratio | -0.02 | -0.02 | -0.03 |
| vol_adj_mom_20d | 0.03 | 0.05 | 0.06 |
| composite_score | 0.01 | 0.03 | 0.01 |

## Entry vs Exit Attribution

_Buy the top 2 ranked names each day, hold a fixed period, **no** stop-loss / take-profit / max-holding. Next-day entry, slippage applied._

| Hold period | Raw avg return / trade | Raw win rate | N trades |
|-------------|------------------------|--------------|----------|
| 5d | -0.09% | +50.65% | 2549 |
| 10d | +0.01% | +52.34% | 2541 |
| 20d | -0.44% | +50.85% | 2531 |
| 30d | -0.76% | +48.95% | 2517 |

**Full strategy (with exit rules):** total return +25.44%, win rate +34.00%, avg hold 66.38 trading days.

The raw signal is **flat-to-negative** without exit rules (avg -0.32% per trade) even though the full strategy is positive. That suggests the stop-loss / take-profit / max-holding rules — not the signal — are doing most of the work. Treat the edge as risk-management, not prediction.

## P&L Attribution

**Top 5 contributors:**

| Ticker | P&L |
|--------|-----|
| TQQQ | $181,062.99 |
| SQQQ | $-155,626.55 |

**Worst 5 contributors:**

| Ticker | P&L |
|--------|-----|
| SQQQ | $-155,626.55 |
| TQQQ | $181,062.99 |

**P&L by asset group:**

| Group | P&L |
|-------|-----|
| leveraged_etfs | $25,436.44 |

## Turnover and Re-entry Diagnostics

| Metric | Value |
|--------|-------|
| Total trades | 101 |
| Trades / month | 1.05 |
| Avg holding period | 66.38 trading days |
| Stop-loss → re-entry ≤5d | 1 |

**Most-entered tickers:** `TQQQ`×28, `SQQQ`×23

**Most re-entered after a stop-loss:** `SQQQ`×1

## Exposure and Benchmark Capture

| Metric | Value |
|--------|-------|
| Avg exposure | +76.03% |
| Max exposure | +99.96% |
| Avg cash (drag) | +23.97% |
| Correlation to SPY | -0.25 |
| Correlation to QQQ | -0.17 |
| Beta to SPY | -0.39 |
| Beta to QQQ | -0.21 |
| Up-capture vs QQQ | 0.21 |
| Down-capture vs QQQ | 0.18 |

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

**Baseline (as configured):** +25.44% return  |  -45.61% max drawdown  |  +34.00% win rate  |  0.96 profit factor

### Run-wide parameters

#### Max Total Exposure  (baseline: 90%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 50% | +33.07% | -172.95% | -434.38% | -32.38% | 108 | +33.96% | 1.04 |
| 70% | +12.21% | -193.81% | -455.24% | -47.51% | 110 | +31.48% | 0.95 |
| 90% ◀ baseline | +25.44% | -180.58% | -442.01% | -45.61% | 101 | +34.00% | 0.96 |
| 100% | -1.59% | -207.61% | -469.04% | -55.74% | 99 | +34.69% | 0.94 |

#### Max Position Size  (baseline: 45.00%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 22.50% | +29.90% | -176.12% | -437.54% | -29.30% | 108 | +33.96% | 1.04 |
| 45.00% ◀ baseline | +25.44% | -180.58% | -442.01% | -45.61% | 101 | +34.00% | 0.96 |
| 67.50% | -87.06% | -293.08% | -554.51% | -91.16% | 83 | +29.27% | 0.53 |
| 90.00% | -93.27% | -299.29% | -560.71% | -95.44% | 79 | +30.77% | 0.55 |
| 135.00% | +0.00% | -206.02% | -467.45% | +0.00% | 0 | +0.00% | — |

#### Max New Trades / Day  (baseline: 2)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 1 | -3.42% | -209.44% | -470.86% | -58.03% | 101 | +32.00% | 0.91 |
| 2 ◀ baseline | +25.44% | -180.58% | -442.01% | -45.61% | 101 | +34.00% | 0.96 |
| 3 | +25.44% | -180.58% | -442.01% | -45.61% | 101 | +34.00% | 0.96 |
| 5 | +25.44% | -180.58% | -442.01% | -45.61% | 101 | +34.00% | 0.96 |

#### Min Composite Score  (baseline: 0.70)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| none | +15.30% | -190.72% | -452.14% | -46.69% | 103 | +33.33% | 0.94 |
| 0.60 | -17.99% | -224.01% | -485.43% | -61.63% | 107 | +32.08% | 0.87 |
| 0.70 ◀ baseline | +25.44% | -180.58% | -442.01% | -45.61% | 101 | +34.00% | 0.96 |

#### Slippage  (baseline: 0.10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 0.05% | +31.77% | -174.25% | -435.68% | -42.91% | 101 | +34.00% | 0.97 |
| 0.10% ◀ baseline | +25.44% | -180.58% | -442.01% | -45.61% | 101 | +34.00% | 0.96 |
| 0.20% | +22.13% | -183.89% | -445.32% | -45.69% | 103 | +35.29% | 0.96 |
| 0.50% | +8.00% | -198.02% | -459.45% | -50.55% | 103 | +35.29% | 0.93 |

#### Re-entry Recovery Gate  (baseline: 10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +36.31% | -169.71% | -431.13% | -47.73% | 105 | +34.62% | 0.99 |
| 0% | +36.31% | -169.71% | -431.13% | -47.73% | 105 | +34.62% | 0.99 |
| 5% | +43.23% | -162.79% | -424.22% | -46.45% | 105 | +34.62% | 1.00 |
| 10% ◀ baseline | +25.44% | -180.58% | -442.01% | -45.61% | 101 | +34.00% | 0.96 |

#### Stop-loss only if score <  (baseline: 0.90)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +25.44% | -180.58% | -442.01% | -45.61% | 101 | +34.00% | 0.96 |
| 0.85 | +25.44% | -180.58% | -442.01% | -45.61% | 101 | +34.00% | 0.96 |
| 0.90 ◀ baseline | +25.44% | -180.58% | -442.01% | -45.61% | 101 | +34.00% | 0.96 |
| 0.95 | +25.44% | -180.58% | -442.01% | -45.61% | 101 | +34.00% | 0.96 |

#### Max-hold only if score <  (baseline: 0.80)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +31.32% | -174.70% | -436.13% | -54.05% | 101 | +40.00% | 0.97 |
| 0.70 | -24.17% | -230.19% | -491.61% | -73.88% | 97 | +31.25% | 0.85 |
| 0.80 ◀ baseline | +25.44% | -180.58% | -442.01% | -45.61% | 101 | +34.00% | 0.96 |
| 0.90 | +42.87% | -163.15% | -424.58% | -52.21% | 101 | +36.00% | 0.99 |

#### Score-decay sell threshold  (baseline: off)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off ◀ baseline | +25.44% | -180.58% | -442.01% | -45.61% | 101 | +34.00% | 0.96 |
| 0.40 | +25.44% | -180.58% | -442.01% | -45.61% | 101 | +34.00% | 0.96 |
| 0.50 | +25.44% | -180.58% | -442.01% | -45.61% | 101 | +34.00% | 0.96 |
| 0.60 | -22.20% | -228.22% | -489.64% | -54.79% | 129 | +28.12% | 0.86 |

#### Persistence-buy threshold  (baseline: 0.90)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +0.30% | -205.72% | -467.14% | -56.49% | 99 | +30.61% | 0.91 |
| 0.80 | +14.10% | -191.93% | -453.35% | -50.53% | 99 | +32.65% | 0.93 |
| 0.85 | +14.10% | -191.93% | -453.35% | -50.53% | 99 | +32.65% | 0.93 |
| 0.90 ◀ baseline | +25.44% | -180.58% | -442.01% | -45.61% | 101 | +34.00% | 0.96 |

#### Vol-target (annualized)  (baseline: 60%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +27.85% | -178.17% | -439.60% | -44.16% | 103 | +35.29% | 0.97 |
| 15% | -29.28% | -235.30% | -496.72% | -53.67% | 107 | +32.08% | 0.75 |
| 20% | -30.34% | -236.36% | -497.79% | -52.44% | 105 | +32.69% | 0.77 |
| 25% | -38.68% | -244.70% | -506.13% | -62.01% | 107 | +32.08% | 0.75 |
| 30% | -34.91% | -240.93% | -502.35% | -60.75% | 103 | +31.37% | 0.77 |
| 60% ◀ baseline | +25.44% | -180.58% | -442.01% | -45.61% | 101 | +34.00% | 0.96 |

#### Signal Weight Profile  (baseline: baseline)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| baseline ◀ baseline | +25.44% | -180.58% | -442.01% | -45.61% | 101 | +34.00% | 0.96 |
| no_1d | +27.75% | -178.27% | -439.69% | -45.68% | 101 | +34.00% | 0.97 |
| less_1d | +25.44% | -180.58% | -442.01% | -45.61% | 101 | +34.00% | 0.96 |
| more_volume | -14.03% | -220.05% | -481.48% | -56.40% | 105 | +32.69% | 0.87 |

### Best 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | reentry_recover_pct | 5% | +43.23% | -424.22% | -46.45% | 1.00 |
| 2 | max_hold_score_max | 0.90 | +42.87% | -424.58% | -52.21% | 0.99 |
| 3 | reentry_recover_pct | off | +36.31% | -431.13% | -47.73% | 0.99 |
| 4 | reentry_recover_pct | 0% | +36.31% | -431.13% | -47.73% | 0.99 |
| 5 | max_total_exposure | 50% | +33.07% | -434.38% | -32.38% | 1.04 |

### Worst 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | max_position_pct | 90.00% | -93.27% | -560.71% | -95.44% | 0.55 |
| 2 | max_position_pct | 67.50% | -87.06% | -554.51% | -91.16% | 0.53 |
| 3 | target_vol | 25% | -38.68% | -506.13% | -62.01% | 0.75 |
| 4 | target_vol | 30% | -34.91% | -502.35% | -60.75% | 0.77 |
| 5 | target_vol | 20% | -30.34% | -497.79% | -52.44% | 0.77 |

### Robustness Notes

The baseline outperforms 80% of all variants. This is broadly consistent across parameter dimensions, suggesting the baseline settings are reasonably competitive in-sample.

The widest in-sample return spread belongs to `max_position_pct` (123.2 pp range across its variants); `stop_loss_score_max` shows the narrowest spread (0.0 pp), suggesting the strategy is least sensitive to that parameter in this period.

Improvements that appear in only one or two variants should be treated with skepticism — isolated peaks are more likely to reflect in-sample noise than genuine edge. Prefer settings that perform consistently across the full sweep.
