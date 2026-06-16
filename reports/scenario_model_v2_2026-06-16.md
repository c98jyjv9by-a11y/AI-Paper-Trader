# Scenario — model_v2

Full 21-name universe with one uniform exit rule applied to every ticker (stop 15%, no take-profit, no trailing stop, 60-day max hold) plus the trough-based anti-falling-knife re-entry gate. Composite ranking drives entries.

**Universe (83):** CRWD, ORCL, COIN, NFLX, PANW, GOOGL, BAC, MSFT, AVGO, AMZN, COST, ASML, AAPL, JPM, TSM, GS, META, TSLA, MU, AMD, NVDA, LLY, VST, AXON, GE, PLTR, OXY, INTC, BA, PFE, PYPL, SEDG, PLUG, ADBE, CRM, NOW, INTU, SAP, WDAY, SNOW, DDOG, NET, MDB, ZS, FTNT, TEAM, OKTA, TWLO, HUBS, SNPS, CDNS, QCOM, TXN, AMAT, LRCX, KLAC, NXPI, MRVL, ADI, MCHP, ON, ARM, ANET, CSCO, IBM, DELL, SMCI, VRT, APP, SHOP, UBER, ABNB, MELI, SE, SPOT, DASH, RBLX, PINS, SNAP, TTD, NU, HOOD, SOFI

---

# AI Paper Trader — Backtest Report
**Period:** 2026-01-01 → 2026-06-16  |  **Generated:** 2026-06-16

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Ending Balance | $156,524.82 | $110,610.50 | $120,180.00 | $123,761.70 |
| Total Return | +56.52% | +10.61% | +20.18% | +23.76% |
| Max Drawdown | -15.99% | -8.88% | -11.72% | -16.42% |
| Excess vs SPY | +45.91% | — | — | — |
| Excess vs QQQ | +36.34% | — | — | — |
| Excess vs Equal-Wt | +32.76% | — | — | — |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $156,524.82 |
| **IRR (annualized, money-weighted)** | **+199.54%** |
| Total Return (on full $ portfolio) | +56.52% |
| Total Capital Deployed (all entries) | $270,192.59 |
| Avg Capital Deployed (snapshot) | $108,900.13 (+108.90% of portfolio) |
| Peak Capital Deployed (snapshot) | $165,189.35 (+165.19% of portfolio) |
| Time Invested | +99.12% of trading days |
| Trading Days | 114 |
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
| Stop-loss only if score < | none |
| Max-hold only if score < | none |
| Score-decay sell | none |
| Persistence buy | none |
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
| OXY | 150 | $57.04 | $53.71 | $-500.07 | 2026-03-16 |
| QCOM | 53 | $209.75 | $220.97 | $595.05 | 2026-05-12 |
| MU | 15 | $767.35 | $1,054.97 | $4,314.43 | 2026-05-12 |
| MDB | 39 | $303.30 | $348.87 | $1,777.11 | 2026-05-13 |
| CRWD | 22 | $563.13 | $681.09 | $2,595.06 | 2026-05-13 |
| ON | 108 | $118.49 | $122.17 | $397.61 | 2026-05-14 |
| PANW | 55 | $238.45 | $279.27 | $2,245.20 | 2026-05-14 |
| CSCO | 108 | $118.33 | $119.75 | $153.01 | 2026-05-15 |
| SEDG | 248 | $61.82 | $58.12 | $-918.05 | 2026-05-15 |
| DELL | 42 | $317.37 | $409.79 | $3,881.77 | 2026-05-28 |
| KLAC | 59 | $213.78 | $245.69 | $1,882.83 | 2026-06-10 |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2026-01-02 | $100,000.00 | — | +0.00% | +0.00% | +0.00% | +0.00% |
| 2026-01-05 | $99,983.56 | -0.02% | -0.02% | +0.67% | +0.79% | +1.66% |
| 2026-01-06 | $100,914.16 | +0.93% | +0.91% | +1.26% | +1.68% | +3.20% |
| 2026-01-07 | $100,321.38 | -0.59% | +0.32% | +0.94% | +1.78% | +2.89% |
| 2026-01-08 | $99,482.07 | -0.84% | -0.52% | +0.93% | +1.20% | +1.38% |
| 2026-06-10 | $145,509.82 | -2.02% | +45.51% | +6.48% | +13.28% | +15.99% |
| 2026-06-11 | $154,004.15 | +5.84% | +54.00% | +8.29% | +17.11% | +20.62% |
| 2026-06-12 | $155,333.43 | +0.86% | +55.33% | +8.87% | +17.80% | +21.55% |
| 2026-06-15 | $159,445.82 | +2.65% | +59.45% | — | +21.50% | +25.56% |
| 2026-06-16 | $156,524.82 | -1.83% | +56.52% | +10.61% | +20.18% | +23.76% |


## Signal Predictiveness

_Cross-section of 9,379 (date, ticker) signal observations. Correlations are Pearson vs forward returns._

| Signal | vs fwd 5d | vs fwd 10d | vs fwd 20d |
|--------|-----------|------------|------------|
| return_1d | 0.01 | 0.01 | 0.04 |
| return_5d | -0.01 | 0.05 | 0.10 |
| return_20d | 0.06 | 0.11 | 0.18 |
| vol_ratio | 0.00 | -0.02 | 0.01 |
| vol_adj_mom_20d | 0.07 | 0.11 | 0.15 |
| composite_score | 0.05 | 0.08 | 0.11 |

**Forward returns by composite-score quintile** (5 = highest-ranked):

| Quintile | N | Avg fwd 5d | Win 5d | Avg fwd 10d | Win 10d | Avg fwd 20d | Win 20d |
|----------|---|-----------|--------|-------------|---------|-------------|---------|
| Q1 | 1921 | +0.50% | +49.22% | +0.80% | +48.36% | +2.38% | +51.63% |
| Q2 | 1808 | +0.57% | +51.38% | +0.82% | +50.54% | +1.72% | +50.47% |
| Q3 | 1921 | +0.07% | +47.81% | +0.65% | +47.17% | +1.80% | +46.62% |
| Q4 | 1808 | +0.46% | +48.91% | +1.72% | +49.52% | +4.25% | +51.86% |
| Q5 | 1921 | +1.71% | +54.13% | +3.48% | +55.60% | +7.52% | +56.07% |

**Top-minus-bottom quintile spread:** 5d +1.20%  |  10d +2.68%  |  20d +5.14%  (positive ⇒ higher-ranked names outperform lower-ranked names).

## Entry vs Exit Attribution

_Buy the top 2 ranked names each day, hold a fixed period, **no** stop-loss / take-profit / max-holding. Next-day entry, slippage applied._

| Hold period | Raw avg return / trade | Raw win rate | N trades |
|-------------|------------------------|--------------|----------|
| 5d | +2.31% | +56.02% | 216 |
| 10d | +4.70% | +60.19% | 206 |
| 20d | +12.29% | +63.44% | 186 |
| 30d | +18.16% | +65.66% | 166 |

**Full strategy (with exit rules):** total return +56.52%, win rate +60.00%, avg hold 62.67 trading days.

The raw signal (buy top names, hold fixed, no stops) is **positive across holding periods** (avg +9.36% per trade, 61% win rate). That points to genuine signal quality — higher-ranked names tend to rise even without exit rules.

## P&L Attribution

**Top 5 contributors:**

| Ticker | P&L |
|--------|-----|
| MU | $16,851.73 |
| INTC | $14,932.60 |
| ON | $7,800.26 |
| KLAC | $4,458.32 |
| DELL | $3,881.77 |

**Worst 5 contributors:**

| Ticker | P&L |
|--------|-----|
| ZS | $-3,439.91 |
| SEDG | $-2,473.27 |
| PLUG | $-1,792.19 |
| SNPS | $-1,540.54 |
| TXN | $-1,359.70 |

**P&L by asset group:**

| Group | P&L |
|-------|-----|
| semiconductors | $16,851.73 |
| software_cybersecurity | $4,840.26 |
| _(ungrouped)_ | $34,832.85 |

## Turnover and Re-entry Diagnostics

| Metric | Value |
|--------|-------|
| Total trades | 41 |
| Trades / month | 7.52 |
| Avg holding period | 62.67 trading days |
| Stop-loss → re-entry ≤5d | 0 |

**Most-entered tickers:** `MU`×2, `ON`×2, `KLAC`×2, `SEDG`×2, `TSM`×1, `ASML`×1, `LRCX`×1, `MCHP`×1

## Exposure and Benchmark Capture

| Metric | Value |
|--------|-------|
| Avg exposure | +90.37% |
| Max exposure | +98.77% |
| Avg cash (drag) | +9.63% |
| Correlation to SPY | 0.71 |
| Correlation to QQQ | 0.79 |
| Beta to SPY | 2.05 |
| Beta to QQQ | 1.56 |
| Up-capture vs QQQ | 1.84 |
| Down-capture vs QQQ | 1.56 |

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

**Baseline (as configured):** +56.52% return  |  -15.99% max drawdown  |  +60.00% win rate  |  4.64 profit factor

### Run-wide parameters

#### Max Total Exposure  (baseline: 90%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 50% | +43.70% | +33.09% | +19.94% | -11.73% | 24 | +66.67% | 9.17 |
| 70% | +45.58% | +34.97% | +21.82% | -12.90% | 31 | +63.64% | 7.46 |
| 90% ◀ baseline | +56.52% | +45.91% | +32.76% | -15.99% | 41 | +60.00% | 4.64 |
| 100% | +55.74% | +45.13% | +31.98% | -15.99% | 40 | +64.29% | 5.33 |

#### Max Position Size  (baseline: 8.50%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 4.25% | +61.48% | +50.87% | +37.72% | -16.31% | 80 | +50.00% | 2.82 |
| 8.50% ◀ baseline | +56.52% | +45.91% | +32.76% | -15.99% | 41 | +60.00% | 4.64 |
| 12.75% | +81.39% | +70.78% | +57.63% | -15.39% | 22 | +85.71% | 31.75 |
| 17.00% | +55.52% | +44.91% | +31.76% | -14.97% | 16 | +80.00% | 15.00 |
| 25.50% | +80.31% | +69.70% | +56.55% | -16.31% | 10 | +100.00% | — |

#### Max New Trades / Day  (baseline: 2)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 1 | +64.05% | +53.44% | +40.29% | -17.85% | 42 | +56.25% | 3.47 |
| 2 ◀ baseline | +56.52% | +45.91% | +32.76% | -15.99% | 41 | +60.00% | 4.64 |
| 3 | +61.10% | +50.49% | +37.33% | -16.13% | 37 | +53.85% | 5.24 |
| 5 | +64.31% | +53.70% | +40.55% | -18.40% | 41 | +40.00% | 1.84 |

#### Min Composite Score  (baseline: 0.70)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| none | +56.52% | +45.91% | +32.76% | -15.99% | 41 | +60.00% | 4.64 |
| 0.60 | +56.52% | +45.91% | +32.76% | -15.99% | 41 | +60.00% | 4.64 |
| 0.70 ◀ baseline | +56.52% | +45.91% | +32.76% | -15.99% | 41 | +60.00% | 4.64 |

#### Slippage  (baseline: 0.10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 0.05% | +56.79% | +46.18% | +33.03% | -15.97% | 41 | +60.00% | 4.67 |
| 0.10% ◀ baseline | +56.52% | +45.91% | +32.76% | -15.99% | 41 | +60.00% | 4.64 |
| 0.20% | +55.99% | +45.38% | +32.23% | -16.02% | 41 | +60.00% | 4.59 |
| 0.50% | +54.91% | +44.30% | +31.14% | -16.01% | 41 | +60.00% | 4.58 |

#### Re-entry Recovery Gate  (baseline: 10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +56.52% | +45.91% | +32.76% | -15.99% | 41 | +60.00% | 4.64 |
| 0% | +56.52% | +45.91% | +32.76% | -15.99% | 41 | +60.00% | 4.64 |
| 5% | +56.52% | +45.91% | +32.76% | -15.99% | 41 | +60.00% | 4.64 |
| 10% ◀ baseline | +56.52% | +45.91% | +32.76% | -15.99% | 41 | +60.00% | 4.64 |

#### Stop-loss only if score <  (baseline: off)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off ◀ baseline | +56.52% | +45.91% | +32.76% | -15.99% | 41 | +60.00% | 4.64 |
| 0.85 | +56.52% | +45.91% | +32.76% | -15.99% | 41 | +60.00% | 4.64 |
| 0.90 | +56.52% | +45.91% | +32.76% | -15.99% | 41 | +60.00% | 4.64 |
| 0.95 | +56.52% | +45.91% | +32.76% | -15.99% | 41 | +60.00% | 4.64 |

#### Max-hold only if score <  (baseline: off)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off ◀ baseline | +56.52% | +45.91% | +32.76% | -15.99% | 41 | +60.00% | 4.64 |
| 0.70 | +54.20% | +43.59% | +30.44% | -15.99% | 39 | +64.29% | 5.12 |
| 0.80 | +54.95% | +44.34% | +31.19% | -15.99% | 41 | +60.00% | 4.44 |
| 0.90 | +57.10% | +46.49% | +33.34% | -15.99% | 41 | +60.00% | 4.60 |

#### Score-decay sell threshold  (baseline: off)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off ◀ baseline | +56.52% | +45.91% | +32.76% | -15.99% | 41 | +60.00% | 4.64 |
| 0.40 | +55.90% | +45.29% | +32.14% | -17.03% | 57 | +45.83% | 1.20 |
| 0.50 | +58.47% | +47.86% | +34.71% | -16.24% | 85 | +44.74% | 1.79 |
| 0.60 | +69.55% | +58.94% | +45.79% | -14.58% | 121 | +46.43% | 3.33 |

#### Persistence-buy threshold  (baseline: off)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off ◀ baseline | +56.52% | +45.91% | +32.76% | -15.99% | 41 | +60.00% | 4.64 |
| 0.80 | +57.88% | +47.27% | +34.12% | -15.99% | 39 | +64.29% | 6.70 |
| 0.85 | +56.03% | +45.42% | +32.27% | -15.66% | 39 | +64.29% | 5.24 |
| 0.90 | +51.89% | +41.28% | +28.13% | -15.99% | 41 | +60.00% | 4.56 |

#### Signal Weight Profile  (baseline: baseline)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| baseline ◀ baseline | +56.52% | +45.91% | +32.76% | -15.99% | 41 | +60.00% | 4.64 |
| no_1d | +56.52% | +45.91% | +32.76% | -15.99% | 41 | +60.00% | 4.64 |
| less_1d | +56.52% | +45.91% | +32.76% | -15.99% | 41 | +60.00% | 4.64 |
| more_volume | +63.16% | +52.55% | +39.40% | -14.79% | 39 | +64.29% | 4.54 |

### Best 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | max_position_pct | 12.75% | +81.39% | +57.63% | -15.39% | 31.75 |
| 2 | max_position_pct | 25.50% | +80.31% | +56.55% | -16.31% | — |
| 3 | score_exit_below | 0.60 | +69.55% | +45.79% | -14.58% | 3.33 |
| 4 | max_new_trades_per_day | 5 | +64.31% | +40.55% | -18.40% | 1.84 |
| 5 | max_new_trades_per_day | 1 | +64.05% | +40.29% | -17.85% | 3.47 |

### Worst 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | max_total_exposure | 50% | +43.70% | +19.94% | -11.73% | 9.17 |
| 2 | max_total_exposure | 70% | +45.58% | +21.82% | -12.90% | 7.46 |
| 3 | score_entry_above | 0.90 | +51.89% | +28.13% | -15.99% | 4.56 |
| 4 | max_hold_score_max | 0.70 | +54.20% | +30.44% | -15.99% | 5.12 |
| 5 | slippage | 0.50% | +54.91% | +31.14% | -16.01% | 4.58 |

### Robustness Notes

27% of variants beat the baseline. Improvements are mixed — some directions help, others hurt — which is consistent with a strategy that has modest but not dominant in-sample edge.

The widest in-sample return spread belongs to `max_position_pct` (25.9 pp range across its variants); `min_composite_score` shows the narrowest spread (0.0 pp), suggesting the strategy is least sensitive to that parameter in this period.

Improvements that appear in only one or two variants should be treated with skepticism — isolated peaks are more likely to reflect in-sample noise than genuine edge. Prefer settings that perform consistently across the full sweep.
