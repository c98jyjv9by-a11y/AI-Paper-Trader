# Scenario — model_v4

RECOMMENDED config. model_v3 (83-name universe, score-conditional exits, persistence buy >0.90, rotation funding) plus Barroso volatility targeting (~35% annualized, tuned to v3's vol profile) that shrinks gross exposure when forecast vol is high — dominated v3 on return, drawdown, Sharpe and PF in 2018-2026 validation.

**Universe (83):** CRWD, ORCL, COIN, NFLX, PANW, GOOGL, BAC, MSFT, AVGO, AMZN, COST, ASML, AAPL, JPM, TSM, GS, META, TSLA, MU, AMD, NVDA, LLY, VST, AXON, GE, PLTR, OXY, INTC, BA, PFE, PYPL, SEDG, PLUG, ADBE, CRM, NOW, INTU, SAP, WDAY, SNOW, DDOG, NET, MDB, ZS, FTNT, TEAM, OKTA, TWLO, HUBS, SNPS, CDNS, QCOM, TXN, AMAT, LRCX, KLAC, NXPI, MRVL, ADI, MCHP, ON, ARM, ANET, CSCO, IBM, DELL, SMCI, VRT, APP, SHOP, UBER, ABNB, MELI, SE, SPOT, DASH, RBLX, PINS, SNAP, TTD, NU, HOOD, SOFI

---

# AI Paper Trader — Backtest Report
**Period:** 2000-01-01 → 2026-06-18  |  **Generated:** 2026-06-20

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Ending Balance | $18,222,850.47 | $819,397.90 | $926,615.50 | $10,135,203.50 |
| Total Return | +18122.85% | +719.40% | +826.62% | +10035.20% |
| Max Drawdown | -57.95% | -55.19% | -82.96% | -64.51% |
| Excess vs SPY | +17403.45% | — | — | — |
| Excess vs QQQ | +17296.23% | — | — | — |
| Excess vs Equal-Wt | +8087.65% | — | — | — |
| 1-Year Return | +85.04% | +26.75% | +40.68% | +51.11% |
| 2-Year Return | +115.92% | +41.29% | +56.25% | +60.83% |
| 3-Year Return | +245.08% | +77.96% | +106.00% | +245.40% |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $18,222,850.47 |
| **IRR (annualized, money-weighted)** | **+22.85%** |
| Total Return (on full $ portfolio) | +18122.85% |
| Total Capital Deployed (all entries) | $248,885,937.56 |
| Avg Capital Deployed (snapshot) | $1,983,334.76 (+1983.33% of portfolio) |
| Peak Capital Deployed (snapshot) | $17,863,694.02 (+17863.69% of portfolio) |
| Time Invested | +99.98% of trading days |
| Trading Days | 6655 |
| Total Trades | 2516 (1263 buys, 1253 sells) |
| Win Rate | +47.73% |
| Average Win | $49,216.59 |
| Average Loss | $-24,997.28 |
| Profit Factor | 1.80 |
| Avg Holding Period | 57.1 approx. trading days |
| Largest Winner | $1,301,071.61 |
| Largest Loser | $-292,942.73 |
| Open Positions at End | 10 |
| Total Slippage Cost | $498,203.06 (+498.20% of start) |
| Avg Slippage / Trade | $198.01 |

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
| Stop-loss only if score < | 0.9 |
| Max-hold only if score < | 0.8 |
| Score-decay sell | none |
| Persistence buy | > 0.9 for 3d  (rotate-funded) |
| Vol target (annualized) | 35% — scale exposure by target/forecast vol |
| Slippage | 0.10% per fill |

## Ticker Universe

`CRWD`, `ORCL`, `COIN`, `NFLX`, `PANW`, `GOOGL`, `BAC`, `MSFT`, `AVGO`, `AMZN`, `COST`, `ASML`, `AAPL`, `JPM`, `TSM`, `GS`, `META`, `TSLA`, `MU`, `AMD`, `NVDA`, `LLY`, `VST`, `AXON`, `GE`, `PLTR`, `OXY`, `INTC`, `BA`, `PFE`, `PYPL`, `SEDG`, `PLUG`, `ADBE`, `CRM`, `NOW`, `INTU`, `SAP`, `WDAY`, `SNOW`, `DDOG`, `NET`, `MDB`, `ZS`, `FTNT`, `TEAM`, `OKTA`, `TWLO`, `HUBS`, `SNPS`, `CDNS`, `QCOM`, `TXN`, `AMAT`, `LRCX`, `KLAC`, `NXPI`, `MRVL`, `ADI`, `MCHP`, `ON`, `ARM`, `ANET`, `CSCO`, `IBM`, `DELL`, `SMCI`, `VRT`, `APP`, `SHOP`, `UBER`, `ABNB`, `MELI`, `SE`, `SPOT`, `DASH`, `RBLX`, `PINS`, `SNAP`, `TTD`, `NU`, `HOOD`, `SOFI`

## Trade Log (last 20 trades)

| Date | Action | Ticker | Shares | Price | Value | Reason | P&L | Hold Days |
|------|--------|--------|--------|-------|-------|--------|-----|-----------|
| 2026-04-15 | SELL | SEDG | 19004 | $37.79 | $718,202.97 | stop_loss | $-170,741.44 | 16.4 |
| 2026-04-16 | BUY | SNAP | 168589 | $6.03 | $1,015,917.31 | momentum_score=0.9813 | — | — |
| 2026-04-24 | SELL | OXY | 16926 | $56.80 | $961,405.26 | rotation_funded | $-4,118.10 | 27.9 |
| 2026-04-27 | BUY | ARM | 4800 | $216.10 | $1,037,260.32 | momentum_score=0.9753 | — | — |
| 2026-04-30 | SELL | MU | 3469 | $516.64 | $1,792,233.87 | max_holding_period | $797,566.46 | 90.7 |
| 2026-05-01 | BUY | QCOM | 6418 | $176.53 | $1,133,001.63 | momentum_score=0.962 | — | — |
| 2026-05-14 | SELL | LRCX | 4958 | $298.64 | $1,480,659.60 | max_holding_period | $485,198.31 | 90.0 |
| 2026-05-15 | BUY | PANW | 5339 | $243.07 | $1,297,765.68 | momentum_score=0.9313 | — | — |
| 2026-05-15 | BUY | CSCO | 11009 | $118.33 | $1,302,675.15 | momentum_score=0.9277 | — | — |
| 2026-05-19 | SELL | SNAP | 168589 | $5.54 | $934,724.85 | rotation_funded | $-81,192.46 | 23.6 |
| 2026-05-20 | SELL | ASML | 760 | $1,548.58 | $1,176,920.72 | rotation_funded | $145,833.74 | 85.0 |
| 2026-05-21 | BUY | CRWD | 1969 | $648.88 | $1,277,641.18 | momentum_score=0.9331 | — | — |
| 2026-06-01 | SELL | COST | 931 | $945.16 | $879,947.59 | rotation_funded | $-47,310.91 | 44.3 |
| 2026-06-02 | BUY | SNOW | 5502 | $261.40 | $1,438,229.40 | momentum_score=0.9639 | — | — |
| 2026-06-02 | SELL | INTC | 16502 | $107.82 | $1,779,280.29 | rotation_funded | $748,855.81 | 37.9 |
| 2026-06-03 | BUY | OKTA | 11753 | $124.77 | $1,466,477.05 | momentum_score=0.9084 | — | — |
| 2026-06-15 | SELL | QCOM | 6418 | $220.59 | $1,415,741.49 | rotation_funded | $282,739.86 | 32.1 |
| 2026-06-16 | BUY | KLAC | 5937 | $237.57 | $1,410,437.06 | momentum_score=0.9331 | — | — |
| 2026-06-17 | SELL | CSCO | 11009 | $117.21 | $1,290,394.61 | rotation_funded | $-12,280.54 | 23.6 |
| 2026-06-18 | BUY | AMAT | 2488 | $617.73 | $1,536,905.02 | momentum_score=0.9482 | — | — |

## Open Positions at End of Period

| Ticker | Shares | Entry Price | Final Price | Unrealized P&L | Entry Date |
|--------|--------|------------|------------|----------------|------------|
| DELL | 6254 | $164.25 | $409.50 | $1,533,816.01 | 2026-03-23 |
| MRVL | 8496 | $128.62 | $310.58 | $1,545,944.90 | 2026-04-10 |
| ON | 14467 | $72.12 | $121.62 | $716,086.12 | 2026-04-14 |
| ARM | 4800 | $216.10 | $439.46 | $1,072,147.68 | 2026-04-27 |
| PANW | 5339 | $243.07 | $287.78 | $238,691.74 | 2026-05-15 |
| CRWD | 1969 | $648.88 | $684.86 | $70,848.16 | 2026-05-21 |
| SNOW | 5502 | $261.40 | $232.29 | $-160,169.82 | 2026-06-02 |
| OKTA | 11753 | $124.77 | $117.81 | $-81,856.12 | 2026-06-03 |
| KLAC | 5937 | $237.57 | $259.56 | $130,570.66 | 2026-06-16 |
| AMAT | 2488 | $617.73 | $617.11 | $-1,535.34 | 2026-06-18 |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2000-01-03 | $100,000.00 | — | +0.00% | +0.00% | +0.00% | +0.00% |
| 2000-01-04 | $99,984.62 | -0.02% | -0.02% | -3.91% | -6.86% | -4.76% |
| 2000-01-05 | $99,301.48 | -0.68% | -0.70% | -3.74% | -9.23% | -4.19% |
| 2000-01-06 | $97,186.84 | -2.13% | -2.81% | -5.29% | -15.47% | -4.96% |
| 2000-01-07 | $99,229.54 | +2.10% | -0.77% | +0.21% | -5.01% | +3.22% |
| 2026-06-12 | $17,316,026.64 | +1.11% | +17216.03% | +711.83% | +802.49% | +9761.79% |
| 2026-06-15 | $18,090,897.91 | +4.47% | +17990.90% | +726.15% | +830.84% | +10082.01% |
| 2026-06-16 | $17,520,056.58 | -3.16% | +17420.06% | +721.22% | +813.15% | +9854.32% |
| 2026-06-17 | $17,680,913.31 | +0.92% | +17580.91% | +710.97% | +803.96% | +9756.90% |
| 2026-06-18 | $18,222,850.47 | +3.07% | +18122.85% | +719.40% | +826.62% | +10035.20% |


## Signal Predictiveness

_Cross-section of 366,410 (date, ticker) signal observations. Correlations are Pearson vs forward returns._

| Signal | vs fwd 5d | vs fwd 10d | vs fwd 20d |
|--------|-----------|------------|------------|
| return_1d | -0.03 | -0.02 | -0.01 |
| return_5d | -0.04 | -0.02 | -0.01 |
| return_20d | -0.01 | -0.00 | 0.00 |
| vol_ratio | 0.00 | 0.00 | 0.01 |
| vol_adj_mom_20d | -0.01 | -0.00 | -0.01 |
| composite_score | -0.01 | -0.01 | -0.00 |

**Forward returns by composite-score quintile** (5 = highest-ranked):

| Quintile | N | Avg fwd 5d | Win 5d | Avg fwd 10d | Win 10d | Avg fwd 20d | Win 20d |
|----------|---|-----------|--------|-------------|---------|-------------|---------|
| Q1 | 76116 | +0.58% | +53.32% | +1.08% | +54.48% | +2.14% | +55.99% |
| Q2 | 71527 | +0.55% | +54.08% | +0.99% | +55.12% | +1.85% | +56.82% |
| Q3 | 72355 | +0.47% | +54.10% | +0.90% | +55.24% | +1.81% | +56.77% |
| Q4 | 71527 | +0.40% | +53.81% | +0.89% | +55.20% | +1.78% | +56.80% |
| Q5 | 74885 | +0.44% | +53.38% | +0.94% | +54.55% | +2.00% | +56.37% |

**Top-minus-bottom quintile spread:** 5d -0.14%  |  10d -0.14%  |  20d -0.14%  (positive ⇒ higher-ranked names outperform lower-ranked names).

## Entry vs Exit Attribution

_Buy the top 2 ranked names each day, hold a fixed period, **no** stop-loss / take-profit / max-holding. Next-day entry, slippage applied._

| Hold period | Raw avg return / trade | Raw win rate | N trades |
|-------------|------------------------|--------------|----------|
| 5d | +0.28% | +50.82% | 13296 |
| 10d | +0.98% | +52.29% | 13286 |
| 20d | +2.14% | +55.30% | 13266 |
| 30d | +3.24% | +55.96% | 13246 |

**Full strategy (with exit rules):** total return +18122.85%, win rate +47.73%, avg hold 57.14 trading days.

The raw signal (buy top names, hold fixed, no stops) is **positive across holding periods** (avg +1.66% per trade, 54% win rate). That points to genuine signal quality — higher-ranked names tend to rise even without exit rules.

## P&L Attribution

**Top 5 contributors:**

| Ticker | P&L |
|--------|-----|
| APP | $1,980,513.62 |
| DELL | $1,647,726.17 |
| MU | $1,528,445.43 |
| MRVL | $1,381,725.96 |
| PLTR | $1,330,774.60 |

**Worst 5 contributors:**

| Ticker | P&L |
|--------|-----|
| SEDG | $-1,010,486.07 |
| NET | $-654,429.89 |
| SOFI | $-579,470.56 |
| OKTA | $-330,367.12 |
| PFE | $-232,479.23 |

**P&L by asset group:**

| Group | P&L |
|-------|-----|
| semiconductors | $2,559,917.50 |
| mega_cap_growth | $1,608,768.55 |
| financial_crypto_beta | $488,970.64 |
| software_cybersecurity | $409,351.26 |
| _(ungrouped)_ | $13,055,842.70 |

## Turnover and Re-entry Diagnostics

| Metric | Value |
|--------|-------|
| Total trades | 2516 |
| Trades / month | 7.92 |
| Avg holding period | 57.14 trading days |
| Stop-loss → re-entry ≤5d | 1 |

**Most-entered tickers:** `PLUG`×46, `AMD`×37, `AXON`×35, `LLY`×33, `NVDA`×32, `NFLX`×32, `MRVL`×30, `PFE`×28

**Most re-entered after a stop-loss:** `SAP`×1

## Exposure and Benchmark Capture

| Metric | Value |
|--------|-------|
| Avg exposure | +91.31% |
| Max exposure | +98.98% |
| Avg cash (drag) | +8.69% |
| Correlation to SPY | 0.71 |
| Correlation to QQQ | 0.73 |
| Beta to SPY | 1.03 |
| Beta to QQQ | 0.76 |
| Up-capture vs QQQ | 0.94 |
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

**Baseline (as configured):** +18122.85% return  |  -57.95% max drawdown  |  +47.73% win rate  |  1.80 profit factor

### Run-wide parameters

#### Max Total Exposure  (baseline: 90%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 50% | +2512.53% | +1793.13% | -7522.67% | -48.32% | 1232 | +47.39% | 1.65 |
| 70% | +7044.00% | +6324.61% | -2991.20% | -50.64% | 1673 | +49.46% | 1.76 |
| 90% ◀ baseline | +18122.85% | +17403.45% | +8087.65% | -57.95% | 2516 | +47.73% | 1.80 |
| 100% | +15819.24% | +15099.84% | +5784.04% | -61.97% | 2734 | +48.38% | 1.92 |

#### Max Position Size  (baseline: 8.50%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 4.25% | +7544.98% | +6825.59% | -2490.22% | -58.18% | 4129 | +49.44% | 1.84 |
| 8.50% ◀ baseline | +18122.85% | +17403.45% | +8087.65% | -57.95% | 2516 | +47.73% | 1.80 |
| 12.75% | +53583.22% | +52863.82% | +43548.02% | -62.36% | 2128 | +47.97% | 1.79 |
| 17.00% | +13512.42% | +12793.02% | +3477.22% | -68.46% | 1915 | +49.11% | 1.73 |
| 25.50% | +7594.61% | +6875.22% | -2440.59% | -64.11% | 1940 | +49.79% | 1.36 |

#### Max New Trades / Day  (baseline: 2)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 1 | +34300.55% | +33581.15% | +24265.35% | -56.67% | 2479 | +49.15% | 1.98 |
| 2 ◀ baseline | +18122.85% | +17403.45% | +8087.65% | -57.95% | 2516 | +47.73% | 1.80 |
| 3 | +30363.33% | +29643.94% | +20328.13% | -60.71% | 2503 | +48.36% | 2.03 |
| 5 | +22348.73% | +21629.33% | +12313.52% | -59.98% | 2576 | +47.54% | 1.97 |

#### Min Composite Score  (baseline: 0.70)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| none | +12253.86% | +11534.46% | +2218.65% | -64.11% | 2572 | +47.31% | 1.83 |
| 0.60 | +12253.86% | +11534.46% | +2218.65% | -64.11% | 2572 | +47.31% | 1.83 |
| 0.70 ◀ baseline | +18122.85% | +17403.45% | +8087.65% | -57.95% | 2516 | +47.73% | 1.80 |

#### Slippage  (baseline: 0.10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 0.05% | +28107.04% | +27387.64% | +18071.84% | -61.56% | 2507 | +50.68% | 1.99 |
| 0.10% ◀ baseline | +18122.85% | +17403.45% | +8087.65% | -57.95% | 2516 | +47.73% | 1.80 |
| 0.20% | +16278.43% | +15559.04% | +6243.23% | -62.43% | 2550 | +48.11% | 1.77 |
| 0.50% | +8762.25% | +8042.85% | -1272.96% | -63.70% | 2513 | +47.20% | 1.77 |

#### Re-entry Recovery Gate  (baseline: 10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +31097.93% | +30378.53% | +21062.73% | -62.03% | 2526 | +48.13% | 1.86 |
| 0% | +31097.93% | +30378.53% | +21062.73% | -62.03% | 2526 | +48.13% | 1.86 |
| 5% | +14802.39% | +14082.99% | +4767.18% | -65.01% | 2540 | +48.30% | 2.05 |
| 10% ◀ baseline | +18122.85% | +17403.45% | +8087.65% | -57.95% | 2516 | +47.73% | 1.80 |

#### Stop-loss only if score <  (baseline: 0.90)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +21491.83% | +20772.44% | +11456.63% | -60.21% | 2518 | +49.76% | 1.81 |
| 0.85 | +17845.64% | +17126.24% | +7810.43% | -57.95% | 2550 | +48.74% | 2.00 |
| 0.90 ◀ baseline | +18122.85% | +17403.45% | +8087.65% | -57.95% | 2516 | +47.73% | 1.80 |
| 0.95 | +12297.73% | +11578.33% | +2262.53% | -59.49% | 2536 | +48.85% | 1.78 |

#### Max-hold only if score <  (baseline: 0.80)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +8452.15% | +7732.75% | -1583.05% | -57.69% | 2552 | +48.47% | 1.83 |
| 0.70 | +13285.62% | +12566.22% | +3250.42% | -60.43% | 2523 | +48.29% | 1.59 |
| 0.80 ◀ baseline | +18122.85% | +17403.45% | +8087.65% | -57.95% | 2516 | +47.73% | 1.80 |
| 0.90 | +15069.09% | +14349.69% | +5033.88% | -61.86% | 2543 | +48.30% | 1.79 |

#### Score-decay sell threshold  (baseline: off)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off ◀ baseline | +18122.85% | +17403.45% | +8087.65% | -57.95% | 2516 | +47.73% | 1.80 |
| 0.40 | +10227.05% | +9507.65% | +191.84% | -56.69% | 4379 | +46.32% | 1.68 |
| 0.50 | +6484.51% | +5765.11% | -3550.69% | -63.61% | 6643 | +45.40% | 1.56 |
| 0.60 | +2037.56% | +1318.17% | -7997.64% | -75.78% | 10957 | +44.90% | 1.35 |

#### Persistence-buy threshold  (baseline: 0.90)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +13143.95% | +12424.55% | +3108.75% | -62.52% | 2166 | +49.44% | 1.75 |
| 0.80 | +20939.61% | +20220.21% | +10904.40% | -60.45% | 4914 | +47.55% | 1.67 |
| 0.85 | +22487.31% | +21767.91% | +12452.10% | -63.95% | 3333 | +47.23% | 1.71 |
| 0.90 ◀ baseline | +18122.85% | +17403.45% | +8087.65% | -57.95% | 2516 | +47.73% | 1.80 |

#### Vol-target (annualized)  (baseline: 35%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +18723.54% | +18004.14% | +8688.34% | -63.10% | 2579 | +48.02% | 1.70 |
| 15% | +8844.02% | +8124.62% | -1191.19% | -51.18% | 2187 | +51.10% | 1.93 |
| 20% | +12241.29% | +11521.90% | +2206.09% | -60.01% | 2307 | +48.13% | 2.41 |
| 25% | +10986.05% | +10266.65% | +950.84% | -67.16% | 2448 | +47.33% | 1.81 |
| 30% | +14276.62% | +13557.22% | +4241.42% | -61.80% | 2465 | +46.82% | 1.89 |
| 35% ◀ baseline | +18122.85% | +17403.45% | +8087.65% | -57.95% | 2516 | +47.73% | 1.80 |

#### Signal Weight Profile  (baseline: baseline)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| baseline ◀ baseline | +18122.85% | +17403.45% | +8087.65% | -57.95% | 2516 | +47.73% | 1.80 |
| no_1d | +18088.92% | +17369.52% | +8053.72% | -62.60% | 2818 | +48.36% | 1.95 |
| less_1d | +18122.85% | +17403.45% | +8087.65% | -57.95% | 2516 | +47.73% | 1.80 |
| more_volume | +19288.09% | +18568.70% | +9252.89% | -63.11% | 2347 | +49.53% | 1.86 |

### Best 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | max_position_pct | 12.75% | +53583.22% | +43548.02% | -62.36% | 1.79 |
| 2 | max_new_trades_per_day | 1 | +34300.55% | +24265.35% | -56.67% | 1.98 |
| 3 | reentry_recover_pct | off | +31097.93% | +21062.73% | -62.03% | 1.86 |
| 4 | reentry_recover_pct | 0% | +31097.93% | +21062.73% | -62.03% | 1.86 |
| 5 | max_new_trades_per_day | 3 | +30363.33% | +20328.13% | -60.71% | 2.03 |

### Worst 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | score_exit_below | 0.60 | +2037.56% | -7997.64% | -75.78% | 1.35 |
| 2 | max_total_exposure | 50% | +2512.53% | -7522.67% | -48.32% | 1.65 |
| 3 | score_exit_below | 0.50 | +6484.51% | -3550.69% | -63.61% | 1.56 |
| 4 | max_total_exposure | 70% | +7044.00% | -2991.20% | -50.64% | 1.76 |
| 5 | max_position_pct | 4.25% | +7544.98% | -2490.22% | -58.18% | 1.84 |

### Robustness Notes

The baseline outperforms 76% of all variants. This is broadly consistent across parameter dimensions, suggesting the baseline settings are reasonably competitive in-sample.

The widest in-sample return spread belongs to `max_position_pct` (46038.2 pp range across its variants); `signal_weights` shows the narrowest spread (1199.2 pp), suggesting the strategy is least sensitive to that parameter in this period.

Improvements that appear in only one or two variants should be treated with skepticism — isolated peaks are more likely to reflect in-sample noise than genuine edge. Prefer settings that perform consistently across the full sweep.
