# Scenario — model_v4

RECOMMENDED config. model_v3 (83-name universe, score-conditional exits, persistence buy >0.90, rotation funding) plus Barroso volatility targeting (~35% annualized, tuned to v3's vol profile) that shrinks gross exposure when forecast vol is high — dominated v3 on return, drawdown, Sharpe and PF in 2018-2026 validation.

**Universe (83):** CRWD, ORCL, COIN, NFLX, PANW, GOOGL, BAC, MSFT, AVGO, AMZN, COST, ASML, AAPL, JPM, TSM, GS, META, TSLA, MU, AMD, NVDA, LLY, VST, AXON, GE, PLTR, OXY, INTC, BA, PFE, PYPL, SEDG, PLUG, ADBE, CRM, NOW, INTU, SAP, WDAY, SNOW, DDOG, NET, MDB, ZS, FTNT, TEAM, OKTA, TWLO, HUBS, SNPS, CDNS, QCOM, TXN, AMAT, LRCX, KLAC, NXPI, MRVL, ADI, MCHP, ON, ARM, ANET, CSCO, IBM, DELL, SMCI, VRT, APP, SHOP, UBER, ABNB, MELI, SE, SPOT, DASH, RBLX, PINS, SNAP, TTD, NU, HOOD, SOFI

---

# AI Paper Trader — Backtest Report
**Period:** 2015-01-01 → 2020-01-01  |  **Generated:** 2026-06-16

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Ending Balance | $336,453.23 | $172,894.90 | $216,443.50 | $310,842.50 |
| Total Return | +236.45% | +72.89% | +116.44% | +210.84% |
| Max Drawdown | -27.75% | -19.35% | -22.80% | -28.55% |
| Excess vs SPY | +163.56% | — | — | — |
| Excess vs QQQ | +120.01% | — | — | — |
| Excess vs Equal-Wt | +25.61% | — | — | — |
| 1-Year Return | +40.81% | +31.09% | +38.41% | +50.13% |
| 2-Year Return | +63.34% | +25.23% | +38.79% | +55.87% |
| 3-Year Return | +125.76% | +51.85% | +82.23% | +122.14% |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $336,453.23 |
| **IRR (annualized, money-weighted)** | **+29.60%** |
| Total Return (on full $ portfolio) | +236.45% |
| Total Capital Deployed (all entries) | $4,085,792.32 |
| Avg Capital Deployed (snapshot) | $182,249.83 (+182.25% of portfolio) |
| Peak Capital Deployed (snapshot) | $333,574.35 (+333.57% of portfolio) |
| Time Invested | +99.92% of trading days |
| Trading Days | 1258 |
| Total Trades | 491 (251 buys, 240 sells) |
| Win Rate | +51.67% |
| Average Win | $3,241.05 |
| Average Loss | $-1,635.07 |
| Profit Factor | 2.12 |
| Avg Holding Period | 56.2 approx. trading days |
| Largest Winner | $23,028.66 |
| Largest Loser | $-5,577.64 |
| Open Positions at End | 11 |
| Total Slippage Cost | $8,078.27 (+8.08% of start) |
| Avg Slippage / Trade | $16.45 |

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
| 2019-10-28 | BUY | TSLA | 1266 | $21.87 | $27,686.41 | momentum_score=0.9944 | — | — |
| 2019-11-01 | SELL | SEDG | 297 | $83.11 | $24,682.72 | rotation_funded | $-751.05 | 16.4 |
| 2019-11-04 | BUY | GE | 548 | $52.91 | $28,995.72 | momentum_score=0.9569 | — | — |
| 2019-11-04 | SELL | MU | 706 | $48.32 | $34,111.17 | max_holding_period | $6,465.69 | 90.0 |
| 2019-11-05 | BUY | SPOT | 180 | $150.52 | $27,093.67 | momentum_score=0.975 | — | — |
| 2019-11-26 | SELL | TSM | 724 | $47.41 | $34,326.36 | max_holding_period | $6,041.64 | 90.0 |
| 2019-11-27 | BUY | AXON | 373 | $75.65 | $28,215.81 | momentum_score=0.9604 | — | — |
| 2019-11-27 | BUY | ZS | 556 | $52.11 | $28,974.33 | momentum_score=0.9132 | — | — |
| 2019-12-05 | SELL | LRCX | 1285 | $24.51 | $31,493.68 | rotation_funded | $4,182.93 | 62.1 |
| 2019-12-06 | BUY | SHOP | 754 | $36.50 | $27,518.36 | momentum_score=0.9243 | — | — |
| 2019-12-13 | SELL | VST | 1316 | $20.64 | $27,163.95 | rotation_funded | $125.02 | 82.1 |
| 2019-12-13 | SELL | ZS | 556 | $45.93 | $25,539.30 | rotation_funded | $-3,435.02 | 11.4 |
| 2019-12-16 | BUY | MU | 559 | $51.68 | $28,890.96 | momentum_score=0.9181 | — | — |
| 2019-12-16 | BUY | TSM | 542 | $51.86 | $28,106.22 | momentum_score=0.909 | — | — |
| 2019-12-20 | SELL | PLUG | 10400 | $2.94 | $30,545.84 | rotation_funded | $2,957.76 | 70.0 |
| 2019-12-23 | BUY | LLY | 230 | $121.72 | $27,995.81 | momentum_score=0.9292 | — | — |
| 2019-12-24 | SELL | ORCL | 522 | $48.64 | $25,388.15 | rotation_funded | $-1,693.11 | 52.9 |
| 2019-12-26 | BUY | SMCI | 11981 | $2.38 | $28,543.53 | momentum_score=0.9042 | — | — |
| 2019-12-26 | SELL | GE | 548 | $54.30 | $29,758.98 | rotation_funded | $763.25 | 37.1 |
| 2019-12-27 | BUY | AMD | 618 | $46.23 | $28,567.79 | momentum_score=0.9403 | — | — |

## Open Positions at End of Period

| Ticker | Shares | Entry Price | Final Price | Unrealized P&L | Entry Date |
|--------|--------|------------|------------|----------------|------------|
| ASML | 120 | $227.08 | $279.40 | $6,277.85 | 2019-09-09 |
| AAPL | 482 | $53.07 | $70.72 | $8,505.32 | 2019-10-03 |
| TSLA | 1266 | $21.87 | $27.89 | $7,620.69 | 2019-10-28 |
| SPOT | 180 | $150.52 | $149.55 | $-174.67 | 2019-11-05 |
| AXON | 373 | $75.65 | $73.28 | $-882.37 | 2019-11-27 |
| SHOP | 754 | $36.50 | $39.76 | $2,459.17 | 2019-12-06 |
| MU | 559 | $51.68 | $52.45 | $429.09 | 2019-12-16 |
| TSM | 542 | $51.86 | $51.77 | $-44.44 | 2019-12-16 |
| LLY | 230 | $121.72 | $121.86 | $31.74 | 2019-12-23 |
| SMCI | 11981 | $2.38 | $2.40 | $234.83 | 2019-12-26 |
| AMD | 618 | $46.23 | $45.86 | $-226.31 | 2019-12-27 |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2015-01-02 | $100,000.00 | — | +0.00% | +0.00% | +0.00% | +0.00% |
| 2015-01-05 | $99,983.36 | -0.02% | -0.02% | -1.81% | -1.47% | -1.69% |
| 2015-01-06 | $99,596.88 | -0.39% | -0.40% | -2.73% | -2.79% | -3.13% |
| 2015-01-07 | $100,025.04 | +0.43% | +0.03% | -1.52% | -1.53% | -2.39% |
| 2015-01-08 | $101,529.05 | +1.50% | +1.53% | +0.23% | +0.35% | -0.23% |
| 2019-12-24 | $336,885.02 | +0.43% | +236.89% | +72.56% | +115.74% | +212.43% |
| 2019-12-26 | $339,062.11 | +0.65% | +239.06% | +73.47% | +117.64% | +214.12% |
| 2019-12-27 | $339,024.56 | -0.01% | +239.02% | +73.43% | +117.46% | +213.20% |
| 2019-12-30 | $335,127.94 | -1.15% | +235.13% | +72.48% | +116.04% | +210.05% |
| 2019-12-31 | $336,453.23 | +0.40% | +236.45% | +72.89% | +116.44% | +210.84% |


## Signal Predictiveness

_Cross-section of 77,224 (date, ticker) signal observations. Correlations are Pearson vs forward returns._

| Signal | vs fwd 5d | vs fwd 10d | vs fwd 20d |
|--------|-----------|------------|------------|
| return_1d | -0.02 | -0.02 | -0.02 |
| return_5d | -0.03 | -0.04 | -0.03 |
| return_20d | -0.03 | -0.04 | -0.04 |
| vol_ratio | 0.01 | 0.00 | 0.01 |
| vol_adj_mom_20d | -0.03 | -0.03 | -0.04 |
| composite_score | -0.01 | -0.02 | -0.02 |

**Forward returns by composite-score quintile** (5 = highest-ranked):

| Quintile | N | Avg fwd 5d | Win 5d | Avg fwd 10d | Win 10d | Avg fwd 20d | Win 20d |
|----------|---|-----------|--------|-------------|---------|-------------|---------|
| Q1 | 15996 | +0.62% | +55.84% | +1.30% | +57.39% | +2.50% | +59.81% |
| Q2 | 15189 | +0.54% | +56.82% | +1.07% | +57.76% | +2.09% | +59.73% |
| Q3 | 15104 | +0.48% | +56.76% | +0.98% | +57.82% | +1.94% | +59.70% |
| Q4 | 15189 | +0.55% | +56.83% | +1.08% | +59.16% | +2.02% | +60.22% |
| Q5 | 15746 | +0.48% | +55.51% | +0.93% | +57.10% | +1.97% | +59.08% |

**Top-minus-bottom quintile spread:** 5d -0.14%  |  10d -0.37%  |  20d -0.53%  (positive ⇒ higher-ranked names outperform lower-ranked names).

## Entry vs Exit Attribution

_Buy the top 2 ranked names each day, hold a fixed period, **no** stop-loss / take-profit / max-holding. Next-day entry, slippage applied._

| Hold period | Raw avg return / trade | Raw win rate | N trades |
|-------------|------------------------|--------------|----------|
| 5d | +0.17% | +51.68% | 2504 |
| 10d | +0.69% | +53.49% | 2494 |
| 20d | +1.53% | +57.24% | 2474 |
| 30d | +2.69% | +57.46% | 2454 |

**Full strategy (with exit rules):** total return +236.45%, win rate +51.67%, avg hold 56.25 trading days.

The raw signal (buy top names, hold fixed, no stops) is **positive across holding periods** (avg +1.27% per trade, 55% win rate). That points to genuine signal quality — higher-ranked names tend to rise even without exit rules.

## P&L Attribution

**Top 5 contributors:**

| Ticker | P&L |
|--------|-----|
| TWLO | $23,206.35 |
| AMD | $23,159.67 |
| NVDA | $20,309.83 |
| AXON | $18,687.83 |
| SE | $15,672.84 |

**Worst 5 contributors:**

| Ticker | P&L |
|--------|-----|
| ZS | $-12,018.51 |
| QCOM | $-5,312.56 |
| PFE | $-3,874.54 |
| NOW | $-3,864.19 |
| GE | $-3,813.86 |

**P&L by asset group:**

| Group | P&L |
|-------|-----|
| mega_cap_growth | $48,681.30 |
| semiconductors | $30,249.11 |
| financial_crypto_beta | $-512.02 |
| software_cybersecurity | $-6,482.15 |
| _(ungrouped)_ | $164,517.03 |

## Turnover and Re-entry Diagnostics

| Metric | Value |
|--------|-------|
| Total trades | 491 |
| Trades / month | 8.19 |
| Avg holding period | 56.25 trading days |
| Stop-loss → re-entry ≤5d | 0 |

**Most-entered tickers:** `AMD`×12, `LLY`×9, `MU`×9, `MRVL`×7, `NFLX`×7, `HUBS`×7, `SHOP`×7, `PLUG`×7

## Exposure and Benchmark Capture

| Metric | Value |
|--------|-------|
| Avg exposure | +93.56% |
| Max exposure | +99.03% |
| Avg cash (drag) | +6.44% |
| Correlation to SPY | 0.74 |
| Correlation to QQQ | 0.77 |
| Beta to SPY | 1.15 |
| Beta to QQQ | 0.94 |
| Up-capture vs QQQ | 1.02 |
| Down-capture vs QQQ | 0.91 |

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

**Baseline (as configured):** +236.45% return  |  -27.75% max drawdown  |  +51.67% win rate  |  2.12 profit factor

### Run-wide parameters

#### Max Total Exposure  (baseline: 90%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 50% | +86.78% | +13.89% | -124.06% | -15.49% | 208 | +54.46% | 2.05 |
| 70% | +99.18% | +26.28% | -111.67% | -24.89% | 292 | +53.52% | 1.81 |
| 90% ◀ baseline | +236.45% | +163.56% | +25.61% | -27.75% | 491 | +51.67% | 2.12 |
| 100% | +231.25% | +158.35% | +20.41% | -28.15% | 509 | +53.82% | 2.11 |

#### Max Position Size  (baseline: 8.50%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 4.25% | +220.84% | +147.95% | +10.00% | -23.10% | 702 | +57.48% | 2.21 |
| 8.50% ◀ baseline | +236.45% | +163.56% | +25.61% | -27.75% | 491 | +51.67% | 2.12 |
| 12.75% | +324.21% | +251.32% | +113.37% | -31.57% | 429 | +51.66% | 2.23 |
| 17.00% | +163.79% | +90.90% | -47.05% | -31.30% | 429 | +50.94% | 1.69 |
| 25.50% | +91.54% | +18.65% | -119.30% | -28.79% | 439 | +49.54% | 1.40 |

#### Max New Trades / Day  (baseline: 2)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 1 | +278.47% | +205.58% | +67.63% | -23.80% | 475 | +53.88% | 2.47 |
| 2 ◀ baseline | +236.45% | +163.56% | +25.61% | -27.75% | 491 | +51.67% | 2.12 |
| 3 | +243.44% | +170.54% | +32.60% | -26.10% | 469 | +51.53% | 2.21 |
| 5 | +348.50% | +275.61% | +137.66% | -27.55% | 477 | +58.80% | 2.73 |

#### Min Composite Score  (baseline: 0.70)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| none | +236.45% | +163.56% | +25.61% | -27.75% | 491 | +51.67% | 2.12 |
| 0.60 | +236.45% | +163.56% | +25.61% | -27.75% | 491 | +51.67% | 2.12 |
| 0.70 ◀ baseline | +236.45% | +163.56% | +25.61% | -27.75% | 491 | +51.67% | 2.12 |

#### Slippage  (baseline: 0.10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 0.05% | +245.89% | +172.99% | +35.05% | -27.01% | 491 | +54.17% | 2.18 |
| 0.10% ◀ baseline | +236.45% | +163.56% | +25.61% | -27.75% | 491 | +51.67% | 2.12 |
| 0.20% | +185.15% | +112.26% | -25.69% | -28.30% | 495 | +50.41% | 1.78 |
| 0.50% | +141.30% | +68.41% | -69.54% | -28.73% | 494 | +47.11% | 1.61 |

#### Re-entry Recovery Gate  (baseline: 10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +236.45% | +163.56% | +25.61% | -27.75% | 491 | +51.67% | 2.12 |
| 0% | +236.45% | +163.56% | +25.61% | -27.75% | 491 | +51.67% | 2.12 |
| 5% | +236.45% | +163.56% | +25.61% | -27.75% | 491 | +51.67% | 2.12 |
| 10% ◀ baseline | +236.45% | +163.56% | +25.61% | -27.75% | 491 | +51.67% | 2.12 |

#### Stop-loss only if score <  (baseline: 0.90)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +236.45% | +163.56% | +25.61% | -27.75% | 491 | +51.67% | 2.12 |
| 0.85 | +236.45% | +163.56% | +25.61% | -27.75% | 491 | +51.67% | 2.12 |
| 0.90 ◀ baseline | +236.45% | +163.56% | +25.61% | -27.75% | 491 | +51.67% | 2.12 |
| 0.95 | +236.45% | +163.56% | +25.61% | -27.75% | 491 | +51.67% | 2.12 |

#### Max-hold only if score <  (baseline: 0.80)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +212.40% | +139.51% | +1.56% | -26.75% | 489 | +53.97% | 2.15 |
| 0.70 | +220.61% | +147.71% | +9.77% | -27.23% | 493 | +53.53% | 2.09 |
| 0.80 ◀ baseline | +236.45% | +163.56% | +25.61% | -27.75% | 491 | +51.67% | 2.12 |
| 0.90 | +205.27% | +132.38% | -5.57% | -27.64% | 495 | +53.72% | 2.02 |

#### Score-decay sell threshold  (baseline: off)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off ◀ baseline | +236.45% | +163.56% | +25.61% | -27.75% | 491 | +51.67% | 2.12 |
| 0.40 | +154.45% | +81.56% | -56.39% | -27.50% | 862 | +48.12% | 1.62 |
| 0.50 | +188.17% | +115.27% | -22.67% | -32.41% | 1245 | +46.76% | 1.61 |
| 0.60 | +151.59% | +78.70% | -59.25% | -29.80% | 2073 | +46.51% | 1.44 |

#### Persistence-buy threshold  (baseline: 0.90)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +284.05% | +211.16% | +73.21% | -19.45% | 364 | +62.71% | 2.38 |
| 0.80 | +255.78% | +182.88% | +44.93% | -28.29% | 1085 | +48.60% | 1.91 |
| 0.85 | +228.51% | +155.62% | +17.67% | -28.65% | 674 | +51.81% | 1.90 |
| 0.90 ◀ baseline | +236.45% | +163.56% | +25.61% | -27.75% | 491 | +51.67% | 2.12 |

#### Vol-target (annualized)  (baseline: 35%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +236.45% | +163.56% | +25.61% | -27.75% | 491 | +51.67% | 2.12 |
| 15% | +161.87% | +88.98% | -48.97% | -19.93% | 377 | +53.01% | 2.11 |
| 20% | +170.58% | +97.69% | -40.26% | -25.70% | 447 | +53.67% | 2.03 |
| 25% | +260.87% | +187.98% | +50.03% | -27.75% | 491 | +52.50% | 2.28 |
| 30% | +236.45% | +163.56% | +25.61% | -27.75% | 491 | +51.67% | 2.12 |
| 35% ◀ baseline | +236.45% | +163.56% | +25.61% | -27.75% | 491 | +51.67% | 2.12 |

#### Signal Weight Profile  (baseline: baseline)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| baseline ◀ baseline | +236.45% | +163.56% | +25.61% | -27.75% | 491 | +51.67% | 2.12 |
| no_1d | +182.97% | +110.07% | -27.88% | -31.29% | 552 | +52.77% | 1.78 |
| less_1d | +236.45% | +163.56% | +25.61% | -27.75% | 491 | +51.67% | 2.12 |
| more_volume | +217.49% | +144.60% | +6.65% | -25.31% | 438 | +55.14% | 2.05 |

### Best 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | max_new_trades_per_day | 5 | +348.50% | +137.66% | -27.55% | 2.73 |
| 2 | max_position_pct | 12.75% | +324.21% | +113.37% | -31.57% | 2.23 |
| 3 | score_entry_above | off | +284.05% | +73.21% | -19.45% | 2.38 |
| 4 | max_new_trades_per_day | 1 | +278.47% | +67.63% | -23.80% | 2.47 |
| 5 | target_vol | 25% | +260.87% | +50.03% | -27.75% | 2.28 |

### Worst 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | max_total_exposure | 50% | +86.78% | -124.06% | -15.49% | 2.05 |
| 2 | max_position_pct | 25.50% | +91.54% | -119.30% | -28.79% | 1.40 |
| 3 | max_total_exposure | 70% | +99.18% | -111.67% | -24.89% | 1.81 |
| 4 | slippage | 0.50% | +141.30% | -69.54% | -28.73% | 1.61 |
| 5 | score_exit_below | 0.60 | +151.59% | -59.25% | -29.80% | 1.44 |

### Robustness Notes

The baseline outperforms 84% of all variants. This is broadly consistent across parameter dimensions, suggesting the baseline settings are reasonably competitive in-sample.

The widest in-sample return spread belongs to `max_position_pct` (232.7 pp range across its variants); `min_composite_score` shows the narrowest spread (0.0 pp), suggesting the strategy is least sensitive to that parameter in this period.

Improvements that appear in only one or two variants should be treated with skepticism — isolated peaks are more likely to reflect in-sample noise than genuine edge. Prefer settings that perform consistently across the full sweep.
