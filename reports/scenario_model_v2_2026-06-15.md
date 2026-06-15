# Scenario — model_v2

Full 21-name universe with one uniform exit rule applied to every ticker (stop 15%, no take-profit, no trailing stop, 60-day max hold) plus the trough-based anti-falling-knife re-entry gate. Composite ranking drives entries.

**Universe (83):** CRWD, ORCL, COIN, NFLX, PANW, GOOGL, BAC, MSFT, AVGO, AMZN, COST, ASML, AAPL, JPM, TSM, GS, META, TSLA, MU, AMD, NVDA, LLY, VST, AXON, GE, PLTR, OXY, INTC, BA, PFE, PYPL, SEDG, PLUG, ADBE, CRM, NOW, INTU, SAP, WDAY, SNOW, DDOG, NET, MDB, ZS, FTNT, TEAM, OKTA, TWLO, HUBS, SNPS, CDNS, QCOM, TXN, AMAT, LRCX, KLAC, NXPI, MRVL, ADI, MCHP, ON, ARM, ANET, CSCO, IBM, DELL, SMCI, VRT, APP, SHOP, UBER, ABNB, MELI, SE, SPOT, DASH, RBLX, PINS, SNAP, TTD, NU, HOOD, SOFI

---

# AI Paper Trader — Backtest Report
**Period:** 2019-01-01 → 2026-06-18  |  **Generated:** 2026-06-15

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Ending Balance | $1,288,420.25 | $336,403.20 | $502,564.00 | $898,492.70 |
| Total Return | +1188.42% | +236.40% | +402.56% | +798.49% |
| Max Drawdown | -41.18% | -33.72% | -35.12% | -51.45% |
| Excess vs SPY | +952.02% | — | — | — |
| Excess vs QQQ | +785.86% | — | — | — |
| Excess vs Equal-Wt | +389.93% | — | — | — |
| 1-Year Return | +129.90% | +27.89% | +41.87% | +54.32% |
| 2-Year Return | +182.85% | +44.00% | +60.71% | +71.11% |
| 3-Year Return | +345.50% | +82.46% | +113.60% | +157.03% |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $1,288,420.25 |
| **IRR (annualized, money-weighted)** | **+43.95%** |
| Total Return (on full $ portfolio) | +1188.42% |
| Total Capital Deployed (all entries) | $8,911,648.16 |
| Avg Capital Deployed (snapshot) | $323,730.59 (+323.73% of portfolio) |
| Peak Capital Deployed (snapshot) | $1,280,868.06 (+1280.87% of portfolio) |
| Time Invested | +99.95% of trading days |
| Trading Days | 1873 |
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
| OXY | 1243 | $51.99 | $54.46 | $3,064.87 | 2026-02-23 |
| DELL | 347 | $175.45 | $409.07 | $81,065.10 | 2026-03-26 |
| ARM | 400 | $144.27 | $412.55 | $107,310.36 | 2026-03-27 |
| AMD | 305 | $196.24 | $547.26 | $107,062.32 | 2026-03-30 |
| ON | 761 | $98.50 | $125.90 | $20,852.62 | 2026-04-24 |
| INTC | 892 | $84.60 | $127.86 | $38,583.91 | 2026-04-28 |
| QCOM | 373 | $209.75 | $220.81 | $4,127.02 | 2026-05-12 |
| MU | 111 | $767.35 | $1,087.99 | $35,591.42 | 2026-05-12 |
| CRWD | 141 | $650.76 | $692.91 | $5,943.14 | 2026-05-20 |
| MRVL | 374 | $289.14 | $308.88 | $7,383.17 | 2026-06-08 |
| KLAC | 441 | $241.41 | $256.42 | $6,621.53 | 2026-06-11 |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2019-01-02 | $100,000.00 | — | +0.00% | +0.00% | +0.00% | +0.00% |
| 2019-01-03 | $99,983.39 | -0.02% | -0.02% | -2.39% | -3.27% | -3.81% |
| 2019-01-04 | $100,655.64 | +0.67% | +0.66% | +0.88% | +0.87% | +0.65% |
| 2019-01-07 | $102,209.90 | +1.54% | +2.21% | +1.68% | +2.07% | +3.14% |
| 2019-01-08 | $102,379.87 | +0.17% | +2.38% | +2.63% | +3.00% | +4.06% |
| 2026-06-09 | $1,150,481.13 | -3.53% | +1050.48% | +228.48% | +378.13% | +753.39% |
| 2026-06-10 | $1,109,707.52 | -3.54% | +1009.71% | +223.30% | +368.58% | +720.62% |
| 2026-06-11 | $1,185,867.92 | +6.86% | +1085.87% | +228.80% | +384.41% | +763.00% |
| 2026-06-12 | $1,224,505.69 | +3.26% | +1124.51% | +230.57% | +387.26% | +768.25% |
| 2026-06-15 | $1,288,420.25 | +5.22% | +1188.42% | +236.40% | +402.56% | +798.49% |


## Signal Predictiveness

_Cross-section of 147,801 (date, ticker) signal observations. Correlations are Pearson vs forward returns._

| Signal | vs fwd 5d | vs fwd 10d | vs fwd 20d |
|--------|-----------|------------|------------|
| return_1d | -0.02 | -0.01 | -0.00 |
| return_5d | -0.04 | -0.01 | -0.00 |
| return_20d | -0.01 | -0.00 | -0.00 |
| vol_ratio | 0.00 | -0.00 | 0.00 |
| vol_adj_mom_20d | -0.00 | -0.00 | 0.00 |
| composite_score | -0.01 | -0.00 | 0.00 |

**Forward returns by composite-score quintile** (5 = highest-ranked):

| Quintile | N | Avg fwd 5d | Win 5d | Avg fwd 10d | Win 10d | Avg fwd 20d | Win 20d |
|----------|---|-----------|--------|-------------|---------|-------------|---------|
| Q1 | 30450 | +0.74% | +54.29% | +1.41% | +55.91% | +2.85% | +57.33% |
| Q2 | 28789 | +0.75% | +55.29% | +1.33% | +56.36% | +2.43% | +57.78% |
| Q3 | 29435 | +0.61% | +54.65% | +1.19% | +56.04% | +2.34% | +57.20% |
| Q4 | 28789 | +0.52% | +54.23% | +1.20% | +55.92% | +2.52% | +57.68% |
| Q5 | 30338 | +0.65% | +54.51% | +1.36% | +55.62% | +2.77% | +57.21% |

**Top-minus-bottom quintile spread:** 5d -0.08%  |  10d -0.06%  |  20d -0.07%  (positive ⇒ higher-ranked names outperform lower-ranked names).

## Entry vs Exit Attribution

_Buy the top 2 ranked names each day, hold a fixed period, **no** stop-loss / take-profit / max-holding. Next-day entry, slippage applied._

| Hold period | Raw avg return / trade | Raw win rate | N trades |
|-------------|------------------------|--------------|----------|
| 5d | +0.61% | +52.20% | 3734 |
| 10d | +1.57% | +54.30% | 3724 |
| 20d | +3.14% | +56.02% | 3704 |
| 30d | +5.09% | +56.51% | 3684 |

**Full strategy (with exit rules):** total return +1188.42%, win rate +52.12%, avg hold 65.65 trading days.

The raw signal (buy top names, hold fixed, no stops) is **positive across holding periods** (avg +2.60% per trade, 55% win rate). That points to genuine signal quality — higher-ranked names tend to rise even without exit rules.

## P&L Attribution

**Top 5 contributors:**

| Ticker | P&L |
|--------|-----|
| MU | $180,306.94 |
| AMD | $102,386.54 |
| ARM | $101,008.19 |
| PLTR | $100,746.00 |
| DELL | $67,725.08 |

**Worst 5 contributors:**

| Ticker | P&L |
|--------|-----|
| MELI | $-15,791.18 |
| OKTA | $-15,544.43 |
| BA | $-12,380.28 |
| TTD | $-12,236.92 |
| SE | $-9,372.62 |

**P&L by asset group:**

| Group | P&L |
|-------|-----|
| semiconductors | $384,243.01 |
| mega_cap_growth | $55,450.86 |
| software_cybersecurity | $33,556.24 |
| financial_crypto_beta | $32,413.27 |
| _(ungrouped)_ | $682,757.02 |

## Turnover and Re-entry Diagnostics

| Metric | Value |
|--------|-------|
| Total trades | 625 |
| Trades / month | 6.98 |
| Avg holding period | 65.65 trading days |
| Stop-loss → re-entry ≤5d | 0 |

**Most-entered tickers:** `PLUG`×9, `SMCI`×8, `OXY`×8, `AMD`×8, `SOFI`×8, `AXON`×7, `SEDG`×7, `MRVL`×7

## Exposure and Benchmark Capture

| Metric | Value |
|--------|-------|
| Avg exposure | +93.27% |
| Max exposure | +99.41% |
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