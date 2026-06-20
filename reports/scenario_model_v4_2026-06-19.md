# Scenario — model_v4

RECOMMENDED config. model_v3 (83-name universe, score-conditional exits, persistence buy >0.90, rotation funding) plus Barroso volatility targeting (~35% annualized, tuned to v3's vol profile) that shrinks gross exposure when forecast vol is high — dominated v3 on return, drawdown, Sharpe and PF in 2018-2026 validation.

**Universe (83):** CRWD, ORCL, COIN, NFLX, PANW, GOOGL, BAC, MSFT, AVGO, AMZN, COST, ASML, AAPL, JPM, TSM, GS, META, TSLA, MU, AMD, NVDA, LLY, VST, AXON, GE, PLTR, OXY, INTC, BA, PFE, PYPL, SEDG, PLUG, ADBE, CRM, NOW, INTU, SAP, WDAY, SNOW, DDOG, NET, MDB, ZS, FTNT, TEAM, OKTA, TWLO, HUBS, SNPS, CDNS, QCOM, TXN, AMAT, LRCX, KLAC, NXPI, MRVL, ADI, MCHP, ON, ARM, ANET, CSCO, IBM, DELL, SMCI, VRT, APP, SHOP, UBER, ABNB, MELI, SE, SPOT, DASH, RBLX, PINS, SNAP, TTD, NU, HOOD, SOFI

---

# AI Paper Trader — Backtest Report
**Period:** 2014-01-01 → 2026-06-18  |  **Generated:** 2026-06-19

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Ending Balance | $1,602,984.84 | $503,878.50 | $936,976.30 | $3,188,133.10 |
| Total Return | +1502.98% | +403.88% | +836.98% | +3088.13% |
| Max Drawdown | -47.05% | -33.72% | -35.12% | -44.54% |
| Excess vs SPY | +1099.11% | — | — | — |
| Excess vs QQQ | +666.01% | — | — | — |
| Excess vs Equal-Wt | -1585.15% | — | — | — |
| 1-Year Return | +97.98% | +26.75% | +40.68% | +57.37% |
| 2-Year Return | +132.09% | +41.29% | +56.25% | +76.10% |
| 3-Year Return | +238.56% | +77.96% | +106.00% | +212.95% |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $1,602,984.84 |
| **IRR (annualized, money-weighted)** | **+27.09%** |
| Total Return (on full $ portfolio) | +1502.98% |
| Total Capital Deployed (all entries) | $23,771,144.05 |
| Avg Capital Deployed (snapshot) | $377,081.15 (+377.08% of portfolio) |
| Peak Capital Deployed (snapshot) | $1,533,553.30 (+1533.55% of portfolio) |
| Time Invested | +99.97% of trading days |
| Trading Days | 3134 |
| Total Trades | 1317 (663 buys, 654 sells) |
| Win Rate | +47.71% |
| Average Win | $8,342.06 |
| Average Loss | $-4,512.95 |
| Profit Factor | 1.69 |
| Avg Holding Period | 51.2 approx. trading days |
| Largest Winner | $99,093.37 |
| Largest Loser | $-21,328.98 |
| Open Positions at End | 9 |
| Total Slippage Cost | $47,604.20 (+47.60% of start) |
| Avg Slippage / Trade | $36.15 |

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
| 2026-05-07 | BUY | MU | 163 | $647.28 | $105,506.09 | momentum_score=0.9066 | — | — |
| 2026-05-07 | SELL | PLUG | 30752 | $3.13 | $96,158.43 | rotation_funded | $5,965.89 | 15.7 |
| 2026-05-08 | BUY | QCOM | 518 | $218.50 | $113,184.09 | momentum_score=0.912 | — | — |
| 2026-05-11 | SELL | AVGO | 238 | $428.00 | $101,864.38 | rotation_funded | $11,148.11 | 19.3 |
| 2026-05-12 | BUY | DDOG | 558 | $200.14 | $111,678.06 | momentum_score=0.9042 | — | — |
| 2026-05-13 | SELL | LRCX | 407 | $294.94 | $120,039.28 | max_holding_period | $37,460.24 | 90.0 |
| 2026-05-13 | SELL | ASML | 68 | $1,580.00 | $107,439.89 | max_holding_period | $24,112.56 | 90.0 |
| 2026-05-14 | BUY | PANW | 495 | $238.45 | $118,031.86 | momentum_score=0.9139 | — | — |
| 2026-05-14 | BUY | PLUG | 28481 | $3.79 | $108,051.22 | momentum_score=0.9042 | — | — |
| 2026-05-19 | SELL | DELL | 582 | $235.02 | $136,784.38 | rotation_funded | $51,350.91 | 54.3 |
| 2026-05-20 | BUY | CRWD | 174 | $650.76 | $113,232.26 | momentum_score=0.9175 | — | — |
| 2026-06-01 | SELL | INTC | 1414 | $109.22 | $154,438.07 | rotation_funded | $62,181.36 | 35.0 |
| 2026-06-01 | SELL | ON | 1087 | $120.80 | $131,308.62 | rotation_funded | $36,742.99 | 29.3 |
| 2026-06-02 | BUY | DELL | 291 | $435.75 | $126,801.88 | momentum_score=0.9765 | — | — |
| 2026-06-02 | BUY | SNOW | 484 | $261.40 | $126,518.18 | momentum_score=0.9639 | — | — |
| 2026-06-02 | SELL | QCOM | 518 | $239.71 | $124,171.70 | rotation_funded | $10,987.61 | 17.9 |
| 2026-06-03 | BUY | OKTA | 1039 | $124.77 | $129,640.91 | momentum_score=0.9084 | — | — |
| 2026-06-05 | SELL | PLUG | 28481 | $3.22 | $91,617.68 | stop_loss | $-16,433.54 | 15.7 |
| 2026-06-10 | SELL | DELL | 291 | $369.46 | $107,512.92 | stop_loss | $-19,288.96 | 5.7 |
| 2026-06-11 | BUY | KLAC | 529 | $241.41 | $127,703.35 | momentum_score=0.8843 | — | — |

## Open Positions at End of Period

| Ticker | Shares | Entry Price | Final Price | Unrealized P&L | Entry Date |
|--------|--------|------------|------------|----------------|------------|
| ARM | 583 | $137.10 | $439.46 | $176,277.63 | 2026-03-30 |
| MRVL | 779 | $109.43 | $310.58 | $156,692.27 | 2026-04-07 |
| MU | 163 | $647.28 | $1,133.99 | $79,334.28 | 2026-05-07 |
| DDOG | 558 | $200.14 | $223.00 | $12,755.94 | 2026-05-12 |
| PANW | 495 | $238.45 | $287.78 | $24,419.24 | 2026-05-14 |
| CRWD | 174 | $650.76 | $684.86 | $5,933.38 | 2026-05-20 |
| SNOW | 484 | $261.40 | $232.29 | $-14,089.82 | 2026-06-02 |
| OKTA | 1039 | $124.77 | $117.81 | $-7,236.32 | 2026-06-03 |
| KLAC | 529 | $241.41 | $259.56 | $9,603.89 | 2026-06-11 |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2014-01-02 | $100,000.00 | — | +0.00% | +0.00% | +0.00% | +0.00% |
| 2014-01-03 | $99,981.92 | -0.02% | -0.02% | -0.02% | -0.72% | +0.36% |
| 2014-01-06 | $100,828.33 | +0.85% | +0.83% | -0.31% | -1.09% | +0.41% |
| 2014-01-07 | $105,436.61 | +4.57% | +5.44% | +0.31% | -0.17% | +2.10% |
| 2014-01-08 | $108,184.54 | +2.61% | +8.18% | +0.33% | +0.05% | +3.67% |
| 2026-06-12 | $1,515,353.29 | +1.18% | +1415.35% | +399.23% | +812.58% | +2984.05% |
| 2026-06-15 | $1,586,671.32 | +4.71% | +1486.67% | +408.03% | +841.25% | +3095.83% |
| 2026-06-16 | $1,523,780.69 | -3.96% | +1423.78% | +405.00% | +823.36% | +2989.73% |
| 2026-06-17 | $1,543,788.14 | +1.31% | +1443.79% | +398.69% | +814.06% | +2982.17% |
| 2026-06-18 | $1,602,984.84 | +3.83% | +1502.98% | +403.88% | +836.98% | +3088.13% |


## Signal Predictiveness

_Cross-section of 220,695 (date, ticker) signal observations. Correlations are Pearson vs forward returns._

| Signal | vs fwd 5d | vs fwd 10d | vs fwd 20d |
|--------|-----------|------------|------------|
| return_1d | -0.02 | -0.02 | -0.01 |
| return_5d | -0.04 | -0.02 | -0.01 |
| return_20d | -0.01 | -0.01 | -0.01 |
| vol_ratio | 0.00 | 0.00 | 0.00 |
| vol_adj_mom_20d | -0.01 | -0.01 | -0.01 |
| composite_score | -0.01 | -0.01 | -0.00 |

**Forward returns by composite-score quintile** (5 = highest-ranked):

| Quintile | N | Avg fwd 5d | Win 5d | Avg fwd 10d | Win 10d | Avg fwd 20d | Win 20d |
|----------|---|-----------|--------|-------------|---------|-------------|---------|
| Q1 | 45573 | +0.66% | +54.49% | +1.29% | +55.86% | +2.59% | +57.59% |
| Q2 | 43141 | +0.63% | +55.37% | +1.17% | +56.46% | +2.23% | +58.07% |
| Q3 | 43712 | +0.56% | +55.26% | +1.09% | +56.41% | +2.16% | +57.90% |
| Q4 | 43141 | +0.51% | +54.93% | +1.09% | +56.50% | +2.23% | +58.00% |
| Q5 | 45128 | +0.57% | +54.49% | +1.15% | +55.60% | +2.43% | +57.37% |

**Top-minus-bottom quintile spread:** 5d -0.09%  |  10d -0.14%  |  20d -0.16%  (positive ⇒ higher-ranked names outperform lower-ranked names).

## Entry vs Exit Attribution

_Buy the top 2 ranked names each day, hold a fixed period, **no** stop-loss / take-profit / max-holding. Next-day entry, slippage applied._

| Hold period | Raw avg return / trade | Raw win rate | N trades |
|-------------|------------------------|--------------|----------|
| 5d | +0.38% | +51.47% | 6256 |
| 10d | +1.11% | +53.55% | 6246 |
| 20d | +2.43% | +56.39% | 6226 |
| 30d | +4.01% | +57.04% | 6206 |

**Full strategy (with exit rules):** total return +1502.98%, win rate +47.71%, avg hold 51.25 trading days.

The raw signal (buy top names, hold fixed, no stops) is **positive across holding periods** (avg +1.98% per trade, 55% win rate). That points to genuine signal quality — higher-ranked names tend to rise even without exit rules.

## P&L Attribution

**Top 5 contributors:**

| Ticker | P&L |
|--------|-----|
| APP | $193,614.15 |
| ARM | $150,918.38 |
| MRVL | $145,820.97 |
| PLTR | $83,740.63 |
| MU | $70,136.02 |

**Worst 5 contributors:**

| Ticker | P&L |
|--------|-----|
| VRT | $-33,363.05 |
| PFE | $-27,547.50 |
| SNOW | $-27,459.99 |
| SOFI | $-23,867.28 |
| SEDG | $-23,732.52 |

**P&L by asset group:**

| Group | P&L |
|-------|-----|
| semiconductors | $226,228.59 |
| mega_cap_growth | $154,336.25 |
| financial_crypto_beta | $121,325.05 |
| software_cybersecurity | $34,519.80 |
| _(ungrouped)_ | $966,574.94 |

## Turnover and Re-entry Diagnostics

| Metric | Value |
|--------|-------|
| Total trades | 1317 |
| Trades / month | 8.81 |
| Avg holding period | 51.25 trading days |
| Stop-loss → re-entry ≤5d | 0 |

**Most-entered tickers:** `MU`×20, `PLUG`×18, `AMD`×17, `SMCI`×17, `SEDG`×17, `AVGO`×14, `TSLA`×14, `MRVL`×13

## Exposure and Benchmark Capture

| Metric | Value |
|--------|-------|
| Avg exposure | +91.57% |
| Max exposure | +99.13% |
| Avg cash (drag) | +8.43% |
| Correlation to SPY | 0.70 |
| Correlation to QQQ | 0.77 |
| Beta to SPY | 1.14 |
| Beta to QQQ | 1.00 |
| Up-capture vs QQQ | 1.10 |
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

**Baseline (as configured):** +1502.98% return  |  -47.05% max drawdown  |  +47.71% win rate  |  1.69 profit factor

### Run-wide parameters

#### Max Total Exposure  (baseline: 90%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 50% | +332.90% | -70.98% | -2755.24% | -25.64% | 594 | +47.96% | 1.63 |
| 70% | +1422.15% | +1018.27% | -1665.99% | -33.00% | 791 | +52.30% | 1.76 |
| 90% ◀ baseline | +1502.98% | +1099.11% | -1585.15% | -47.05% | 1317 | +47.71% | 1.69 |
| 100% | +2720.11% | +2316.23% | -368.02% | -44.89% | 1383 | +50.58% | 1.93 |

#### Max Position Size  (baseline: 8.50%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 4.25% | +1545.12% | +1141.24% | -1543.01% | -41.97% | 1921 | +52.58% | 1.74 |
| 8.50% ◀ baseline | +1502.98% | +1099.11% | -1585.15% | -47.05% | 1317 | +47.71% | 1.69 |
| 12.75% | +3562.26% | +3158.38% | +474.13% | -42.12% | 1160 | +49.39% | 1.72 |
| 17.00% | +1137.80% | +733.92% | -1950.33% | -52.21% | 1097 | +51.47% | 1.61 |
| 25.50% | +972.10% | +568.22% | -2116.03% | -47.08% | 1172 | +52.57% | 1.43 |

#### Max New Trades / Day  (baseline: 2)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 1 | +2357.70% | +1953.82% | -730.44% | -37.17% | 1195 | +50.08% | 1.85 |
| 2 ◀ baseline | +1502.98% | +1099.11% | -1585.15% | -47.05% | 1317 | +47.71% | 1.69 |
| 3 | +2515.57% | +2111.70% | -572.56% | -39.03% | 1247 | +49.60% | 1.67 |
| 5 | +2617.45% | +2213.57% | -470.68% | -39.43% | 1261 | +51.36% | 1.90 |

#### Min Composite Score  (baseline: 0.70)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| none | +1502.98% | +1099.11% | -1585.15% | -47.05% | 1317 | +47.71% | 1.69 |
| 0.60 | +1502.98% | +1099.11% | -1585.15% | -47.05% | 1317 | +47.71% | 1.69 |
| 0.70 ◀ baseline | +1502.98% | +1099.11% | -1585.15% | -47.05% | 1317 | +47.71% | 1.69 |

#### Slippage  (baseline: 0.10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 0.05% | +2413.94% | +2010.06% | -674.20% | -42.98% | 1270 | +51.43% | 1.89 |
| 0.10% ◀ baseline | +1502.98% | +1099.11% | -1585.15% | -47.05% | 1317 | +47.71% | 1.69 |
| 0.20% | +2104.46% | +1700.59% | -983.67% | -44.18% | 1275 | +51.34% | 1.81 |
| 0.50% | +1149.46% | +745.58% | -1938.67% | -47.52% | 1305 | +48.61% | 1.53 |

#### Re-entry Recovery Gate  (baseline: 10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +2778.05% | +2374.17% | -310.09% | -39.77% | 1290 | +50.00% | 2.10 |
| 0% | +2778.05% | +2374.17% | -310.09% | -39.77% | 1290 | +50.00% | 2.10 |
| 5% | +1636.49% | +1232.61% | -1451.64% | -45.17% | 1316 | +48.55% | 1.82 |
| 10% ◀ baseline | +1502.98% | +1099.11% | -1585.15% | -47.05% | 1317 | +47.71% | 1.69 |

#### Stop-loss only if score <  (baseline: 0.90)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +1502.98% | +1099.11% | -1585.15% | -47.05% | 1317 | +47.71% | 1.69 |
| 0.85 | +1502.98% | +1099.11% | -1585.15% | -47.05% | 1317 | +47.71% | 1.69 |
| 0.90 ◀ baseline | +1502.98% | +1099.11% | -1585.15% | -47.05% | 1317 | +47.71% | 1.69 |
| 0.95 | +1502.98% | +1099.11% | -1585.15% | -47.05% | 1317 | +47.71% | 1.69 |

#### Max-hold only if score <  (baseline: 0.80)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +1806.16% | +1402.28% | -1281.97% | -39.54% | 1268 | +50.72% | 1.72 |
| 0.70 | +2743.10% | +2339.22% | -345.04% | -40.43% | 1276 | +50.87% | 1.92 |
| 0.80 ◀ baseline | +1502.98% | +1099.11% | -1585.15% | -47.05% | 1317 | +47.71% | 1.69 |
| 0.90 | +2638.40% | +2234.52% | -449.73% | -37.54% | 1264 | +52.47% | 1.98 |

#### Score-decay sell threshold  (baseline: off)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off ◀ baseline | +1502.98% | +1099.11% | -1585.15% | -47.05% | 1317 | +47.71% | 1.69 |
| 0.40 | +1697.43% | +1293.55% | -1390.71% | -43.22% | 2119 | +47.49% | 1.63 |
| 0.50 | +1417.22% | +1013.34% | -1670.91% | -49.58% | 3117 | +45.82% | 1.52 |
| 0.60 | +1244.58% | +840.70% | -1843.55% | -50.55% | 5045 | +44.96% | 1.39 |

#### Persistence-buy threshold  (baseline: 0.90)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +2760.87% | +2356.99% | -327.27% | -41.61% | 981 | +55.46% | 2.01 |
| 0.80 | +3120.68% | +2716.80% | +32.55% | -48.53% | 3024 | +48.31% | 1.70 |
| 0.85 | +2340.88% | +1937.00% | -747.26% | -46.03% | 1867 | +49.73% | 1.74 |
| 0.90 ◀ baseline | +1502.98% | +1099.11% | -1585.15% | -47.05% | 1317 | +47.71% | 1.69 |

#### Vol-target (annualized)  (baseline: 35%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +2866.06% | +2462.18% | -222.07% | -42.39% | 1318 | +48.01% | 1.95 |
| 15% | +1435.70% | +1031.82% | -1652.44% | -33.64% | 1027 | +52.94% | 2.14 |
| 20% | +1768.25% | +1364.37% | -1319.88% | -34.13% | 1085 | +54.09% | 1.85 |
| 25% | +2385.30% | +1981.43% | -702.83% | -33.69% | 1155 | +50.61% | 1.86 |
| 30% | +2362.86% | +1958.98% | -725.28% | -39.90% | 1208 | +51.00% | 1.76 |
| 35% ◀ baseline | +1502.98% | +1099.11% | -1585.15% | -47.05% | 1317 | +47.71% | 1.69 |

#### Signal Weight Profile  (baseline: baseline)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| baseline ◀ baseline | +1502.98% | +1099.11% | -1585.15% | -47.05% | 1317 | +47.71% | 1.69 |
| no_1d | +2633.55% | +2229.67% | -454.58% | -42.61% | 1449 | +50.56% | 1.85 |
| less_1d | +1502.98% | +1099.11% | -1585.15% | -47.05% | 1317 | +47.71% | 1.69 |
| more_volume | +2817.49% | +2413.61% | -270.65% | -38.72% | 1128 | +53.13% | 1.81 |

### Best 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | max_position_pct | 12.75% | +3562.26% | +474.13% | -42.12% | 1.72 |
| 2 | score_entry_above | 0.80 | +3120.68% | +32.55% | -48.53% | 1.70 |
| 3 | target_vol | off | +2866.06% | -222.07% | -42.39% | 1.95 |
| 4 | signal_weights | more_volume | +2817.49% | -270.65% | -38.72% | 1.81 |
| 5 | reentry_recover_pct | off | +2778.05% | -310.09% | -39.77% | 2.10 |

### Worst 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | max_total_exposure | 50% | +332.90% | -2755.24% | -25.64% | 1.63 |
| 2 | max_position_pct | 25.50% | +972.10% | -2116.03% | -47.08% | 1.43 |
| 3 | max_position_pct | 17.00% | +1137.80% | -1950.33% | -52.21% | 1.61 |
| 4 | slippage | 0.50% | +1149.46% | -1938.67% | -47.52% | 1.53 |
| 5 | score_exit_below | 0.60 | +1244.58% | -1843.55% | -50.55% | 1.39 |

### Robustness Notes

48% of variants beat the baseline. Improvements are mixed — some directions help, others hurt — which is consistent with a strategy that has modest but not dominant in-sample edge.

The widest in-sample return spread belongs to `max_position_pct` (2590.2 pp range across its variants); `min_composite_score` shows the narrowest spread (0.0 pp), suggesting the strategy is least sensitive to that parameter in this period.

Improvements that appear in only one or two variants should be treated with skepticism — isolated peaks are more likely to reflect in-sample noise than genuine edge. Prefer settings that perform consistently across the full sweep.
