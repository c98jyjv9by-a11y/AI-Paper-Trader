# Scenario — model_v2

Full 21-name universe with one uniform exit rule applied to every ticker (stop 15%, no take-profit, no trailing stop, 60-day max hold) plus the trough-based anti-falling-knife re-entry gate. Composite ranking drives entries.

**Universe (83):** CRWD, ORCL, COIN, NFLX, PANW, GOOGL, BAC, MSFT, AVGO, AMZN, COST, ASML, AAPL, JPM, TSM, GS, META, TSLA, MU, AMD, NVDA, LLY, VST, AXON, GE, PLTR, OXY, INTC, BA, PFE, PYPL, SEDG, PLUG, ADBE, CRM, NOW, INTU, SAP, WDAY, SNOW, DDOG, NET, MDB, ZS, FTNT, TEAM, OKTA, TWLO, HUBS, SNPS, CDNS, QCOM, TXN, AMAT, LRCX, KLAC, NXPI, MRVL, ADI, MCHP, ON, ARM, ANET, CSCO, IBM, DELL, SMCI, VRT, APP, SHOP, UBER, ABNB, MELI, SE, SPOT, DASH, RBLX, PINS, SNAP, TTD, NU, HOOD, SOFI

---

# AI Paper Trader — Backtest Report
**Period:** 2019-01-01 → 2026-06-13  |  **Generated:** 2026-06-13

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Ending Balance | $1,224,505.83 | $330,573.90 | $487,257.30 | $868,253.00 |
| Total Return | +1124.51% | +230.57% | +387.26% | +768.25% |
| Max Drawdown | -41.18% | -33.72% | -35.12% | -51.45% |
| Excess vs SPY | +893.93% | — | — | — |
| Excess vs QQQ | +737.25% | — | — | — |
| Excess vs Equal-Wt | +356.25% | — | — | — |
| 1-Year Return | +117.21% | +24.27% | +35.82% | +46.79% |
| 2-Year Return | +168.78% | +41.84% | +56.89% | +64.84% |
| 3-Year Return | +327.23% | +79.62% | +107.88% | +149.63% |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $1,224,505.83 |
| **IRR (annualized, money-weighted)** | **+43.03%** |
| Total Return (on full $ portfolio) | +1124.51% |
| Total Capital Deployed (all entries) | $8,911,648.12 |
| Avg Capital Deployed (snapshot) | $323,219.30 (+323.22% of portfolio) |
| Peak Capital Deployed (snapshot) | $1,252,015.87 (+1252.02% of portfolio) |
| Time Invested | +99.95% of trading days |
| Trading Days | 1872 |
| Total Trades | 625 (318 buys, 307 sells) |
| Win Rate | +52.12% |
| Average Win | $8,905.33 |
| Average Loss | $-4,449.24 |
| Profit Factor | 2.18 |
| Avg Holding Period | 65.6 approx. trading days |
| Largest Winner | $92,583.13 |
| Largest Loser | $-14,504.57 |
| Open Positions at End | 11 |
| Total Slippage Cost | $17,730.77 (+17.73% of start) |
| Avg Slippage / Trade | $28.37 |

_**IRR** is the annualized money-weighted (internal) rate of return on the capital actually put into positions: it solves for the rate that discounts the dated BUY outflows, SELL inflows, and the terminal mark-to-market of open positions to zero. It ignores idle cash, so it measures how the *deployed* capital performed, and is bounded at -100%. Being annualized, short backtests can extrapolate to large figures. **Total Return** is on the full starting portfolio (cash included) and is what the SPY/QQQ/Equal-Wt comparisons above use, since those benchmarks are fully invested._

## Strategy Parameters Used

| Parameter | Value |
|-----------|-------|
| Starting Portfolio | $100,000.00 |
| Max Position Size | 8.5% |
| Max Total Exposure | 90% |
| Max New Trades / Day | 2 |
| Stop Loss | 15.0% |
| Take Profit | none |
| Trailing Stop | none |
| Max Holding Period | 90 trading days |
| Slippage | 0.10% per fill |

## Ticker Universe

`CRWD`, `ORCL`, `COIN`, `NFLX`, `PANW`, `GOOGL`, `BAC`, `MSFT`, `AVGO`, `AMZN`, `COST`, `ASML`, `AAPL`, `JPM`, `TSM`, `GS`, `META`, `TSLA`, `MU`, `AMD`, `NVDA`, `LLY`, `VST`, `AXON`, `GE`, `PLTR`, `OXY`, `INTC`, `BA`, `PFE`, `PYPL`, `SEDG`, `PLUG`, `ADBE`, `CRM`, `NOW`, `INTU`, `SAP`, `WDAY`, `SNOW`, `DDOG`, `NET`, `MDB`, `ZS`, `FTNT`, `TEAM`, `OKTA`, `TWLO`, `HUBS`, `SNPS`, `CDNS`, `QCOM`, `TXN`, `AMAT`, `LRCX`, `KLAC`, `NXPI`, `MRVL`, `ADI`, `MCHP`, `ON`, `ARM`, `ANET`, `CSCO`, `IBM`, `DELL`, `SMCI`, `VRT`, `APP`, `SHOP`, `UBER`, `ABNB`, `MELI`, `SE`, `SPOT`, `DASH`, `RBLX`, `PINS`, `SNAP`, `TTD`, `NU`, `HOOD`, `SOFI`

## Trade Log (last 20 trades)

| Date | Action | Ticker | Shares | Price | Value | Reason | P&L | Hold Days |
|------|--------|--------|--------|-------|-------|--------|-----|-----------|
| 2026-03-25 | SELL | CSCO | 745 | $81.31 | $60,574.16 | max_holding_period | $2,739.74 | 90.0 |
| 2026-03-25 | SELL | GOOGL | 201 | $290.47 | $58,383.57 | max_holding_period | $-415.04 | 90.0 |
| 2026-03-26 | BUY | DELL | 347 | $175.45 | $60,882.19 | momentum_score=0.9759 | — | — |
| 2026-03-26 | SELL | META | 91 | $546.99 | $49,776.32 | stop_loss | $-10,180.37 | 69.3 |
| 2026-03-27 | BUY | ARM | 400 | $144.27 | $57,709.64 | momentum_score=0.9482 | — | — |
| 2026-03-27 | SELL | NVDA | 304 | $167.16 | $50,815.94 | max_holding_period | $-3,548.62 | 90.0 |
| 2026-03-30 | BUY | AMD | 305 | $196.24 | $59,851.98 | momentum_score=0.7898 | — | — |
| 2026-04-23 | SELL | ABNB | 447 | $141.73 | $63,352.46 | max_holding_period | $3,399.03 | 90.0 |
| 2026-04-24 | BUY | ON | 761 | $98.50 | $74,957.28 | momentum_score=0.9735 | — | — |
| 2026-04-27 | SELL | LRCX | 358 | $259.21 | $92,797.36 | max_holding_period | $30,066.70 | 90.0 |
| 2026-04-28 | BUY | INTC | 892 | $84.60 | $75,467.21 | momentum_score=0.9873 | — | — |
| 2026-05-11 | SELL | MU | 192 | $794.53 | $152,550.66 | max_holding_period | $92,583.13 | 90.0 |
| 2026-05-12 | BUY | QCOM | 373 | $209.75 | $78,235.11 | momentum_score=0.9729 | — | — |
| 2026-05-12 | BUY | MU | 111 | $767.35 | $85,175.47 | momentum_score=0.9645 | — | — |
| 2026-05-19 | SELL | SEDG | 1784 | $54.48 | $97,184.29 | max_holding_period | $35,914.06 | 90.0 |
| 2026-05-20 | BUY | CRWD | 141 | $650.76 | $91,757.17 | momentum_score=0.9175 | — | — |
| 2026-06-05 | SELL | TXN | 301 | $284.77 | $85,717.24 | max_holding_period | $21,100.13 | 90.0 |
| 2026-06-08 | BUY | MRVL | 374 | $289.14 | $108,137.95 | momentum_score=0.9458 | — | — |
| 2026-06-10 | SELL | ADI | 202 | $392.28 | $79,240.01 | max_holding_period | $14,825.08 | 90.0 |
| 2026-06-11 | BUY | KLAC | 441 | $241.41 | $106,459.69 | momentum_score=0.8843 | — | — |

## Open Positions at End of Period

| Ticker | Shares | Entry Price | Final Price | Unrealized P&L | Entry Date |
|--------|--------|------------|------------|----------------|------------|
| OXY | 1243 | $51.99 | $56.54 | $5,650.31 | 2026-02-23 |
| DELL | 347 | $175.45 | $395.57 | $76,380.60 | 2026-03-26 |
| ARM | 400 | $144.27 | $380.81 | $94,614.36 | 2026-03-27 |
| AMD | 305 | $196.24 | $511.57 | $96,176.87 | 2026-03-30 |
| ON | 761 | $98.50 | $116.79 | $13,919.91 | 2026-04-24 |
| INTC | 892 | $84.60 | $124.57 | $35,649.23 | 2026-04-28 |
| QCOM | 373 | $209.75 | $211.72 | $736.45 | 2026-05-12 |
| MU | 111 | $767.35 | $981.61 | $23,783.24 | 2026-05-12 |
| CRWD | 141 | $650.76 | $682.80 | $4,517.63 | 2026-05-20 |
| MRVL | 374 | $289.14 | $279.70 | $-3,530.15 | 2026-06-08 |
| KLAC | 441 | $241.41 | $254.54 | $5,792.45 | 2026-06-11 |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2019-01-02 | $100,000.00 | — | +0.00% | +0.00% | +0.00% | +0.00% |
| 2019-01-03 | $99,983.37 | -0.02% | -0.02% | -2.39% | -3.27% | -3.81% |
| 2019-01-04 | $100,655.64 | +0.67% | +0.66% | +0.88% | +0.87% | +0.65% |
| 2019-01-07 | $102,209.92 | +1.54% | +2.21% | +1.68% | +2.07% | +3.14% |
| 2019-01-08 | $102,379.87 | +0.17% | +2.38% | +2.63% | +3.00% | +4.06% |
| 2026-06-08 | $1,192,534.07 | +2.85% | +1092.53% | +229.45% | +383.70% | +769.10% |
| 2026-06-09 | $1,150,481.27 | -3.53% | +1050.48% | +228.48% | +378.13% | +753.39% |
| 2026-06-10 | $1,109,707.66 | -3.54% | +1009.71% | +223.30% | +368.58% | +720.62% |
| 2026-06-11 | $1,185,868.06 | +6.86% | +1085.87% | +228.80% | +384.41% | +763.00% |
| 2026-06-12 | $1,224,505.83 | +3.26% | +1124.51% | +230.57% | +387.26% | +768.25% |


## Signal Predictiveness

_Cross-section of 147,718 (date, ticker) signal observations. Correlations are Pearson vs forward returns._

| Signal | vs fwd 5d | vs fwd 10d | vs fwd 20d |
|--------|-----------|------------|------------|
| return_1d | -0.02 | -0.01 | -0.00 |
| return_5d | -0.04 | -0.00 | -0.00 |
| return_20d | -0.01 | -0.00 | -0.00 |
| vol_ratio | 0.00 | 0.00 | 0.00 |
| vol_adj_mom_20d | -0.00 | -0.00 | -0.00 |
| composite_score | -0.01 | -0.00 | 0.00 |

**Forward returns by composite-score quintile** (5 = highest-ranked):

| Quintile | N | Avg fwd 5d | Win 5d | Avg fwd 10d | Win 10d | Avg fwd 20d | Win 20d |
|----------|---|-----------|--------|-------------|---------|-------------|---------|
| Q1 | 30433 | +0.74% | +54.28% | +1.41% | +55.92% | +2.84% | +57.32% |
| Q2 | 28773 | +0.75% | +55.30% | +1.33% | +56.37% | +2.42% | +57.78% |
| Q3 | 29418 | +0.61% | +54.64% | +1.19% | +56.05% | +2.34% | +57.20% |
| Q4 | 28773 | +0.52% | +54.22% | +1.20% | +55.93% | +2.52% | +57.67% |
| Q5 | 30321 | +0.65% | +54.50% | +1.37% | +55.65% | +2.77% | +57.21% |

**Top-minus-bottom quintile spread:** 5d -0.09%  |  10d -0.05%  |  20d -0.07%  (positive ⇒ higher-ranked names outperform lower-ranked names).

## Entry vs Exit Attribution

_Buy the top 2 ranked names each day, hold a fixed period, **no** stop-loss / take-profit / max-holding. Next-day entry, slippage applied._

| Hold period | Raw avg return / trade | Raw win rate | N trades |
|-------------|------------------------|--------------|----------|
| 5d | +0.61% | +52.17% | 3732 |
| 10d | +1.58% | +54.33% | 3722 |
| 20d | +3.14% | +56.00% | 3702 |
| 30d | +5.08% | +56.49% | 3682 |

**Full strategy (with exit rules):** total return +1124.51%, win rate +52.12%, avg hold 65.65 trading days.

The raw signal (buy top names, hold fixed, no stops) is **positive across holding periods** (avg +2.60% per trade, 55% win rate). That points to genuine signal quality — higher-ranked names tend to rise even without exit rules.

## P&L Attribution

**Top 5 contributors:**

| Ticker | P&L |
|--------|-----|
| MU | $168,498.76 |
| PLTR | $100,746.00 |
| AMD | $91,501.09 |
| ARM | $88,312.19 |
| DELL | $63,040.58 |

**Worst 5 contributors:**

| Ticker | P&L |
|--------|-----|
| MRVL | $-17,486.19 |
| MELI | $-15,791.18 |
| OKTA | $-15,544.43 |
| BA | $-12,380.28 |
| TTD | $-12,236.92 |

**P&L by asset group:**

| Group | P&L |
|-------|-----|
| semiconductors | $348,853.38 |
| mega_cap_growth | $55,450.86 |
| financial_crypto_beta | $32,413.27 |
| software_cybersecurity | $32,130.73 |
| _(ungrouped)_ | $655,657.71 |

## Turnover and Re-entry Diagnostics

| Metric | Value |
|--------|-------|
| Total trades | 625 |
| Trades / month | 6.99 |
| Avg holding period | 65.65 trading days |
| Stop-loss → re-entry ≤5d | 0 |

**Most-entered tickers:** `PLUG`×9, `SMCI`×8, `OXY`×8, `AMD`×8, `SOFI`×8, `AXON`×7, `SEDG`×7, `MRVL`×7

## Exposure and Benchmark Capture

| Metric | Value |
|--------|-------|
| Avg exposure | +93.27% |
| Max exposure | +99.38% |
| Avg cash (drag) | +6.73% |
| Correlation to SPY | 0.74 |
| Correlation to QQQ | 0.80 |
| Beta to SPY | 1.12 |
| Beta to QQQ | 0.99 |
| Up-capture vs QQQ | 1.11 |
| Down-capture vs QQQ | 1.01 |

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

**Baseline (as configured):** +1124.51% return  |  -41.18% max drawdown  |  +52.12% win rate  |  2.18 profit factor

### Run-wide parameters

#### Max Total Exposure  (baseline: 90%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 50% | +312.68% | +82.11% | -455.57% | -24.62% | 338 | +51.50% | 1.93 |
| 70% | +516.96% | +286.39% | -251.29% | -31.20% | 497 | +47.35% | 1.77 |
| 90% ◀ baseline | +1124.51% | +893.93% | +356.25% | -41.18% | 625 | +52.12% | 2.18 |
| 100% | +960.81% | +730.23% | +192.55% | -38.90% | 617 | +51.82% | 1.85 |

#### Max Position Size  (baseline: 8.50%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 4.25% | +662.60% | +432.03% | -105.65% | -40.92% | 1209 | +49.08% | 1.91 |
| 8.50% ◀ baseline | +1124.51% | +893.93% | +356.25% | -41.18% | 625 | +52.12% | 2.18 |
| 12.75% | +582.95% | +352.37% | -185.31% | -42.69% | 407 | +50.50% | 1.65 |
| 17.00% | +554.53% | +323.96% | -213.72% | -58.37% | 296 | +45.21% | 1.73 |
| 25.50% | +287.27% | +56.69% | -480.98% | -49.82% | 183 | +45.56% | 1.59 |

#### Max New Trades / Day  (baseline: 2)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 1 | +719.41% | +488.83% | -48.85% | -39.48% | 616 | +47.52% | 1.83 |
| 2 ◀ baseline | +1124.51% | +893.93% | +356.25% | -41.18% | 625 | +52.12% | 2.18 |
| 3 | +940.04% | +709.47% | +171.79% | -39.01% | 606 | +51.68% | 1.76 |
| 5 | +672.96% | +442.39% | -95.29% | -43.97% | 635 | +49.84% | 1.70 |

#### Min Composite Score  (baseline: 0.70)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| none | +1124.51% | +893.93% | +356.25% | -41.18% | 625 | +52.12% | 2.18 |
| 0.60 | +1124.51% | +893.93% | +356.25% | -41.18% | 625 | +52.12% | 2.18 |
| 0.70 ◀ baseline | +1124.51% | +893.93% | +356.25% | -41.18% | 625 | +52.12% | 2.18 |

#### Slippage  (baseline: 0.10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 0.05% | +907.36% | +676.78% | +139.10% | -40.04% | 615 | +51.82% | 2.11 |
| 0.10% ◀ baseline | +1124.51% | +893.93% | +356.25% | -41.18% | 625 | +52.12% | 2.18 |
| 0.20% | +708.01% | +477.44% | -60.24% | -41.07% | 628 | +49.51% | 1.58 |
| 0.50% | +684.79% | +454.21% | -83.47% | -42.41% | 615 | +52.98% | 1.77 |

#### Re-entry Recovery Gate  (baseline: 10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +1124.51% | +893.93% | +356.25% | -41.18% | 625 | +52.12% | 2.18 |
| 0% | +1124.51% | +893.93% | +356.25% | -41.18% | 625 | +52.12% | 2.18 |
| 5% | +1124.51% | +893.93% | +356.25% | -41.18% | 625 | +52.12% | 2.18 |
| 10% ◀ baseline | +1124.51% | +893.93% | +356.25% | -41.18% | 625 | +52.12% | 2.18 |

#### Signal Weight Profile  (baseline: baseline)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| baseline ◀ baseline | +1124.51% | +893.93% | +356.25% | -41.18% | 625 | +52.12% | 2.18 |
| no_1d | +563.30% | +332.72% | -204.95% | -46.87% | 632 | +46.95% | 1.60 |
| less_1d | +1124.51% | +893.93% | +356.25% | -41.18% | 625 | +52.12% | 2.18 |
| more_volume | +900.00% | +669.43% | +131.75% | -38.08% | 617 | +51.32% | 1.94 |

### Best 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | max_total_exposure | 90% | +1124.51% | +356.25% | -41.18% | 2.18 |
| 2 | max_position_pct | 8.50% | +1124.51% | +356.25% | -41.18% | 2.18 |
| 3 | max_new_trades_per_day | 2 | +1124.51% | +356.25% | -41.18% | 2.18 |
| 4 | min_composite_score | none | +1124.51% | +356.25% | -41.18% | 2.18 |
| 5 | min_composite_score | 0.60 | +1124.51% | +356.25% | -41.18% | 2.18 |

### Worst 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | max_position_pct | 25.50% | +287.27% | -480.98% | -49.82% | 1.59 |
| 2 | max_total_exposure | 50% | +312.68% | -455.57% | -24.62% | 1.93 |
| 3 | max_total_exposure | 70% | +516.96% | -251.29% | -31.20% | 1.77 |
| 4 | max_position_pct | 17.00% | +554.53% | -213.72% | -58.37% | 1.73 |
| 5 | signal_weights | no_1d | +563.30% | -204.95% | -46.87% | 1.60 |

### Robustness Notes

The baseline outperforms 100% of all variants. This is broadly consistent across parameter dimensions, suggesting the baseline settings are reasonably competitive in-sample.

The widest in-sample return spread belongs to `max_position_pct` (837.2 pp range across its variants); `min_composite_score` shows the narrowest spread (0.0 pp), suggesting the strategy is least sensitive to that parameter in this period.

Improvements that appear in only one or two variants should be treated with skepticism — isolated peaks are more likely to reflect in-sample noise than genuine edge. Prefer settings that perform consistently across the full sweep.
