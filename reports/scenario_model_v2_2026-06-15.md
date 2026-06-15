# Scenario — model_v2

Full 21-name universe with one uniform exit rule applied to every ticker (stop 15%, no take-profit, no trailing stop, 60-day max hold) plus the trough-based anti-falling-knife re-entry gate. Composite ranking drives entries.

**Universe (83):** CRWD, ORCL, COIN, NFLX, PANW, GOOGL, BAC, MSFT, AVGO, AMZN, COST, ASML, AAPL, JPM, TSM, GS, META, TSLA, MU, AMD, NVDA, LLY, VST, AXON, GE, PLTR, OXY, INTC, BA, PFE, PYPL, SEDG, PLUG, ADBE, CRM, NOW, INTU, SAP, WDAY, SNOW, DDOG, NET, MDB, ZS, FTNT, TEAM, OKTA, TWLO, HUBS, SNPS, CDNS, QCOM, TXN, AMAT, LRCX, KLAC, NXPI, MRVL, ADI, MCHP, ON, ARM, ANET, CSCO, IBM, DELL, SMCI, VRT, APP, SHOP, UBER, ABNB, MELI, SE, SPOT, DASH, RBLX, PINS, SNAP, TTD, NU, HOOD, SOFI

---

# AI Paper Trader — Backtest Report
**Period:** 2026-01-01 → 2026-06-18  |  **Generated:** 2026-06-15

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Ending Balance | $159,445.82 | $110,791.10 | $121,499.60 | $125,556.20 |
| Total Return | +59.45% | +10.79% | +21.50% | +25.56% |
| Max Drawdown | -15.99% | -8.88% | -11.72% | -16.42% |
| Excess vs SPY | +48.65% | — | — | — |
| Excess vs QQQ | +37.95% | — | — | — |
| Excess vs Equal-Wt | +33.89% | — | — | — |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $159,445.82 |
| **IRR (annualized, money-weighted)** | **+215.48%** |
| Total Return (on full $ portfolio) | +59.45% |
| Total Capital Deployed (all entries) | $270,192.59 |
| Avg Capital Deployed (snapshot) | $108,520.57 (+108.52% of portfolio) |
| Peak Capital Deployed (snapshot) | $165,189.35 (+165.19% of portfolio) |
| Time Invested | +99.12% of trading days |
| Trading Days | 113 |
| Total Trades | 41 (26 buys, 15 sells) |
| Win Rate | +60.00% |
| Average Win | $5,680.83 |
| Average Loss | $-1,837.77 |
| Profit Factor | 4.64 |
| Avg Holding Period | 62.7 approx. trading days |
| Largest Winner | $14,932.60 |
| Largest Loser | $-3,439.91 |
| Open Positions at End | 11 |
| Total Slippage Cost | $445.03 (+0.45% of start) |
| Avg Slippage / Trade | $10.85 |

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
| 2026-05-12 | BUY | MU | 15 | $767.35 | $11,510.20 | momentum_score=0.9645 | — | — |
| 2026-05-12 | SELL | ASML | 6 | $1,519.42 | $9,116.51 | max_holding_period | $1,681.99 | 90.0 |
| 2026-05-12 | SELL | LRCX | 43 | $288.95 | $12,424.88 | max_holding_period | $3,527.36 | 90.0 |
| 2026-05-13 | BUY | MDB | 39 | $303.30 | $11,828.82 | momentum_score=0.9018 | — | — |
| 2026-05-13 | BUY | CRWD | 22 | $563.13 | $12,388.92 | momentum_score=0.8867 | — | — |
| 2026-05-13 | SELL | ON | 138 | $115.59 | $15,952.01 | max_holding_period | $7,402.65 | 90.0 |
| 2026-05-14 | BUY | ON | 108 | $118.49 | $12,796.75 | momentum_score=0.9145 | — | — |
| 2026-05-14 | BUY | PANW | 55 | $238.45 | $13,114.65 | momentum_score=0.9139 | — | — |
| 2026-05-14 | SELL | INTC | 200 | $115.81 | $23,162.82 | max_holding_period | $14,932.60 | 90.0 |
| 2026-05-15 | BUY | CSCO | 108 | $118.33 | $12,779.45 | momentum_score=0.9277 | — | — |
| 2026-05-15 | BUY | SEDG | 248 | $61.82 | $15,331.81 | momentum_score=0.9108 | — | — |
| 2026-05-15 | SELL | ADI | 28 | $415.93 | $11,646.13 | max_holding_period | $3,260.96 | 90.0 |
| 2026-05-15 | SELL | KLAC | 64 | $180.02 | $11,521.40 | max_holding_period | $2,575.49 | 90.0 |
| 2026-05-18 | BUY | PLUG | 3280 | $3.45 | $11,327.48 | momentum_score=0.85 | — | — |
| 2026-05-18 | SELL | AMAT | 29 | $412.64 | $11,966.66 | max_holding_period | $3,069.96 | 90.0 |
| 2026-05-19 | BUY | ZS | 70 | $175.43 | $12,279.76 | momentum_score=0.9325 | — | — |
| 2026-05-27 | SELL | ZS | 70 | $126.28 | $8,839.85 | stop_loss | $-3,439.91 | 5.7 |
| 2026-05-28 | BUY | DELL | 42 | $317.37 | $13,329.41 | momentum_score=0.8946 | — | — |
| 2026-06-09 | SELL | PLUG | 3280 | $2.91 | $9,535.29 | stop_loss | $-1,792.19 | 15.7 |
| 2026-06-10 | BUY | KLAC | 59 | $213.78 | $12,612.88 | momentum_score=0.8952 | — | — |

## Open Positions at End of Period

| Ticker | Shares | Entry Price | Final Price | Unrealized P&L | Entry Date |
|--------|--------|------------|------------|----------------|------------|
| OXY | 150 | $57.04 | $54.46 | $-387.57 | 2026-03-16 |
| QCOM | 53 | $209.75 | $220.81 | $586.41 | 2026-05-12 |
| MU | 15 | $767.35 | $1,087.99 | $4,809.65 | 2026-05-12 |
| MDB | 39 | $303.30 | $354.18 | $1,984.20 | 2026-05-13 |
| CRWD | 22 | $563.13 | $692.91 | $2,855.10 | 2026-05-13 |
| ON | 108 | $118.49 | $125.90 | $800.45 | 2026-05-14 |
| PANW | 55 | $238.45 | $284.54 | $2,535.05 | 2026-05-14 |
| CSCO | 108 | $118.33 | $120.17 | $198.91 | 2026-05-15 |
| SEDG | 248 | $61.82 | $60.19 | $-404.69 | 2026-05-15 |
| DELL | 42 | $317.37 | $409.07 | $3,851.53 | 2026-05-28 |
| KLAC | 59 | $213.78 | $256.42 | $2,515.90 | 2026-06-10 |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2026-01-02 | $100,000.00 | — | +0.00% | +0.00% | +0.00% | +0.00% |
| 2026-01-05 | $99,983.56 | -0.02% | -0.02% | +0.67% | +0.79% | +1.66% |
| 2026-01-06 | $100,914.16 | +0.93% | +0.91% | +1.26% | +1.68% | +3.20% |
| 2026-01-07 | $100,321.38 | -0.59% | +0.32% | +0.94% | +1.78% | +2.89% |
| 2026-01-08 | $99,482.07 | -0.84% | -0.52% | +0.93% | +1.20% | +1.38% |
| 2026-06-09 | $148,508.91 | -3.99% | +48.51% | +8.18% | +15.59% | +19.20% |
| 2026-06-10 | $145,509.82 | -2.02% | +45.51% | +6.48% | +13.28% | +15.99% |
| 2026-06-11 | $154,004.15 | +5.84% | +54.00% | +8.29% | +17.11% | +20.62% |
| 2026-06-12 | $155,333.43 | +0.86% | +55.33% | +8.87% | +17.80% | +21.55% |
| 2026-06-15 | $159,445.82 | +2.65% | +59.45% | +10.79% | +21.50% | +25.56% |


## Signal Predictiveness

_Cross-section of 9,296 (date, ticker) signal observations. Correlations are Pearson vs forward returns._

| Signal | vs fwd 5d | vs fwd 10d | vs fwd 20d |
|--------|-----------|------------|------------|
| return_1d | 0.01 | 0.00 | 0.04 |
| return_5d | -0.01 | 0.06 | 0.10 |
| return_20d | 0.06 | 0.12 | 0.17 |
| vol_ratio | 0.00 | -0.02 | 0.02 |
| vol_adj_mom_20d | 0.07 | 0.12 | 0.15 |
| composite_score | 0.04 | 0.08 | 0.11 |

**Forward returns by composite-score quintile** (5 = highest-ranked):

| Quintile | N | Avg fwd 5d | Win 5d | Avg fwd 10d | Win 10d | Avg fwd 20d | Win 20d |
|----------|---|-----------|--------|-------------|---------|-------------|---------|
| Q1 | 1904 | +0.51% | +49.24% | +0.81% | +48.26% | +2.31% | +51.42% |
| Q2 | 1792 | +0.57% | +51.33% | +0.85% | +50.67% | +1.61% | +50.13% |
| Q3 | 1904 | +0.02% | +47.44% | +0.69% | +47.29% | +1.75% | +46.43% |
| Q4 | 1792 | +0.47% | +48.90% | +1.82% | +49.70% | +4.21% | +51.95% |
| Q5 | 1904 | +1.67% | +53.87% | +3.63% | +56.03% | +7.55% | +56.04% |

**Top-minus-bottom quintile spread:** 5d +1.15%  |  10d +2.83%  |  20d +5.24%  (positive ⇒ higher-ranked names outperform lower-ranked names).

## Entry vs Exit Attribution

_Buy the top 2 ranked names each day, hold a fixed period, **no** stop-loss / take-profit / max-holding. Next-day entry, slippage applied._

| Hold period | Raw avg return / trade | Raw win rate | N trades |
|-------------|------------------------|--------------|----------|
| 5d | +2.29% | +56.07% | 214 |
| 10d | +4.82% | +60.78% | 204 |
| 20d | +12.33% | +63.04% | 184 |
| 30d | +18.22% | +65.24% | 164 |

**Full strategy (with exit rules):** total return +59.45%, win rate +60.00%, avg hold 62.67 trading days.

The raw signal (buy top names, hold fixed, no stops) is **positive across holding periods** (avg +9.41% per trade, 61% win rate). That points to genuine signal quality — higher-ranked names tend to rise even without exit rules.

## P&L Attribution

**Top 5 contributors:**

| Ticker | P&L |
|--------|-----|
| MU | $17,346.95 |
| INTC | $14,932.60 |
| ON | $8,203.10 |
| KLAC | $5,091.39 |
| DELL | $3,851.53 |

**Worst 5 contributors:**

| Ticker | P&L |
|--------|-----|
| ZS | $-3,439.91 |
| SEDG | $-1,959.91 |
| PLUG | $-1,792.19 |
| SNPS | $-1,540.54 |
| TXN | $-1,359.70 |

**P&L by asset group:**

| Group | P&L |
|-------|-----|
| semiconductors | $17,346.95 |
| software_cybersecurity | $5,390.15 |
| _(ungrouped)_ | $36,708.73 |

## Turnover and Re-entry Diagnostics

| Metric | Value |
|--------|-------|
| Total trades | 41 |
| Trades / month | 7.43 |
| Avg holding period | 62.67 trading days |
| Stop-loss → re-entry ≤5d | 0 |

**Most-entered tickers:** `MU`×2, `ON`×2, `KLAC`×2, `SEDG`×2, `TSM`×1, `ASML`×1, `LRCX`×1, `MCHP`×1

## Exposure and Benchmark Capture

| Metric | Value |
|--------|-------|
| Avg exposure | +90.31% |
| Max exposure | +98.77% |
| Avg cash (drag) | +9.69% |
| Correlation to SPY | 0.71 |
| Correlation to QQQ | 0.78 |
| Beta to SPY | 2.02 |
| Beta to QQQ | 1.56 |
| Up-capture vs QQQ | 1.84 |
| Down-capture vs QQQ | 1.55 |

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