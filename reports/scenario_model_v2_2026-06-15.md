# Scenario — model_v2

Full 21-name universe with one uniform exit rule applied to every ticker (stop 15%, no take-profit, no trailing stop, 60-day max hold) plus the trough-based anti-falling-knife re-entry gate. Composite ranking drives entries.

**Universe (83):** CRWD, ORCL, COIN, NFLX, PANW, GOOGL, BAC, MSFT, AVGO, AMZN, COST, ASML, AAPL, JPM, TSM, GS, META, TSLA, MU, AMD, NVDA, LLY, VST, AXON, GE, PLTR, OXY, INTC, BA, PFE, PYPL, SEDG, PLUG, ADBE, CRM, NOW, INTU, SAP, WDAY, SNOW, DDOG, NET, MDB, ZS, FTNT, TEAM, OKTA, TWLO, HUBS, SNPS, CDNS, QCOM, TXN, AMAT, LRCX, KLAC, NXPI, MRVL, ADI, MCHP, ON, ARM, ANET, CSCO, IBM, DELL, SMCI, VRT, APP, SHOP, UBER, ABNB, MELI, SE, SPOT, DASH, RBLX, PINS, SNAP, TTD, NU, HOOD, SOFI

---

# AI Paper Trader — Backtest Report
**Period:** 2023-01-01 → 2026-03-18  |  **Generated:** 2026-06-15

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Ending Balance | $288,531.94 | $180,684.50 | $228,987.50 | $370,029.10 |
| Total Return | +188.53% | +80.68% | +128.99% | +270.03% |
| Max Drawdown | -32.39% | -18.76% | -22.77% | -35.32% |
| Excess vs SPY | +107.85% | — | — | — |
| Excess vs QQQ | +59.54% | — | — | — |
| Excess vs Equal-Wt | -81.50% | — | — | — |
| 1-Year Return | +26.43% | +19.28% | +26.00% | +38.23% |
| 2-Year Return | +42.37% | +31.62% | +36.97% | +69.92% |
| 3-Year Return | +150.79% | +75.65% | +103.66% | +214.43% |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $288,531.94 |
| **IRR (annualized, money-weighted)** | **+42.91%** |
| Total Return (on full $ portfolio) | +188.53% |
| Total Capital Deployed (all entries) | $2,171,025.71 |
| Avg Capital Deployed (snapshot) | $190,776.04 (+190.78% of portfolio) |
| Peak Capital Deployed (snapshot) | $318,631.18 (+318.63% of portfolio) |
| Time Invested | +99.88% of trading days |
| Trading Days | 804 |
| Total Trades | 250 (130 buys, 120 sells) |
| Win Rate | +56.67% |
| Average Win | $4,857.48 |
| Average Loss | $-3,015.69 |
| Profit Factor | 2.11 |
| Avg Holding Period | 70.0 approx. trading days |
| Largest Winner | $23,846.08 |
| Largest Loser | $-5,454.30 |
| Open Positions at End | 10 |
| Total Slippage Cost | $4,269.84 (+4.27% of start) |
| Avg Slippage / Trade | $17.08 |

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
| 2025-12-15 | SELL | APP | 47 | $674.49 | $31,701.02 | max_holding_period | $9,796.88 | 90.0 |
| 2025-12-16 | BUY | NXPI | 108 | $228.79 | $24,709.58 | momentum_score=0.844 | — | — |
| 2025-12-16 | SELL | MU | 173 | $232.09 | $40,150.91 | max_holding_period | $18,060.11 | 90.0 |
| 2025-12-17 | BUY | TWLO | 182 | $139.36 | $25,363.37 | momentum_score=0.9295 | — | — |
| 2025-12-17 | BUY | OKTA | 277 | $88.51 | $24,516.83 | momentum_score=0.8452 | — | — |
| 2025-12-18 | SELL | PLUG | 12884 | $2.26 | $29,088.21 | max_holding_period | $7,808.99 | 90.0 |
| 2025-12-19 | BUY | META | 37 | $658.86 | $24,377.99 | momentum_score=0.8373 | — | — |
| 2025-12-19 | SELL | INTC | 891 | $36.78 | $32,773.83 | max_holding_period | $10,868.95 | 90.0 |
| 2025-12-22 | BUY | LRCX | 146 | $175.23 | $25,582.89 | momentum_score=0.9422 | — | — |
| 2026-01-12 | SELL | AVGO | 63 | $351.12 | $22,120.64 | max_holding_period | $447.22 | 90.0 |
| 2026-01-13 | BUY | SEDG | 732 | $34.34 | $25,140.03 | momentum_score=0.9476 | — | — |
| 2026-02-02 | SELL | TSLA | 55 | $421.39 | $23,176.35 | max_holding_period | $-1,224.58 | 90.0 |
| 2026-02-03 | BUY | TXN | 115 | $224.30 | $25,793.99 | momentum_score=0.9554 | — | — |
| 2026-02-03 | SELL | TWLO | 182 | $109.39 | $19,909.07 | stop_loss | $-5,454.30 | 34.3 |
| 2026-02-04 | BUY | ADI | 81 | $318.89 | $25,829.75 | momentum_score=0.8355 | — | — |
| 2026-02-20 | SELL | OKTA | 277 | $74.22 | $20,557.75 | stop_loss | $-3,959.08 | 46.4 |
| 2026-02-23 | BUY | OXY | 498 | $51.99 | $25,893.16 | momentum_score=0.9398 | — | — |
| 2026-03-12 | SELL | NXPI | 108 | $190.04 | $20,524.59 | stop_loss | $-4,184.99 | 61.4 |
| 2026-03-12 | SELL | TXN | 115 | $188.90 | $21,723.51 | stop_loss | $-4,070.48 | 26.4 |
| 2026-03-13 | BUY | PLTR | 154 | $151.10 | $23,269.54 | momentum_score=0.8542 | — | — |

## Open Positions at End of Period

| Ticker | Shares | Entry Price | Final Price | Unrealized P&L | Entry Date |
|--------|--------|------------|------------|----------------|------------|
| CSCO | 309 | $76.62 | $77.18 | $173.60 | 2025-11-18 |
| GOOGL | 82 | $292.53 | $307.51 | $1,228.02 | 2025-11-19 |
| NVDA | 125 | $178.83 | $180.19 | $169.90 | 2025-11-21 |
| GS | 29 | $880.32 | $801.95 | $-2,272.71 | 2025-12-12 |
| META | 37 | $658.86 | $615.68 | $-1,597.83 | 2025-12-19 |
| LRCX | 146 | $175.23 | $224.71 | $7,224.77 | 2025-12-22 |
| SEDG | 732 | $34.34 | $44.88 | $7,712.13 | 2026-01-13 |
| ADI | 81 | $318.89 | $307.75 | $-902.24 | 2026-02-04 |
| OXY | 498 | $51.99 | $58.11 | $3,046.42 | 2026-02-23 |
| PLTR | 154 | $151.10 | $152.77 | $257.04 | 2026-03-13 |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2023-01-03 | $100,000.00 | — | +0.00% | +0.00% | +0.00% | +0.00% |
| 2023-01-04 | $99,982.46 | -0.02% | -0.02% | +0.77% | +0.48% | +1.73% |
| 2023-01-05 | $99,480.93 | -0.50% | -0.52% | -0.38% | -1.10% | -0.89% |
| 2023-01-06 | $99,536.18 | +0.06% | -0.46% | +1.91% | +1.63% | +1.45% |
| 2023-01-09 | $99,847.66 | +0.31% | -0.15% | +1.85% | +2.29% | +3.37% |
| 2026-03-12 | $279,207.50 | -2.14% | +179.21% | +81.95% | +129.90% | +268.45% |
| 2026-03-13 | $279,525.77 | +0.11% | +179.53% | +80.92% | +128.53% | +267.34% |
| 2026-03-16 | $285,027.95 | +1.97% | +185.03% | +82.76% | +131.10% | +271.61% |
| 2026-03-17 | $289,040.27 | +1.41% | +189.04% | +83.24% | +132.22% | +275.03% |
| 2026-03-18 | $288,531.94 | -0.18% | +188.53% | +80.68% | +128.99% | +270.03% |


## Signal Predictiveness

_Cross-section of 66,454 (date, ticker) signal observations. Correlations are Pearson vs forward returns._

| Signal | vs fwd 5d | vs fwd 10d | vs fwd 20d |
|--------|-----------|------------|------------|
| return_1d | -0.02 | -0.00 | -0.01 |
| return_5d | -0.01 | 0.00 | -0.00 |
| return_20d | -0.01 | -0.01 | -0.00 |
| vol_ratio | 0.00 | 0.02 | 0.01 |
| vol_adj_mom_20d | -0.01 | -0.01 | 0.00 |
| composite_score | -0.00 | 0.00 | 0.01 |

**Forward returns by composite-score quintile** (5 = highest-ranked):

| Quintile | N | Avg fwd 5d | Win 5d | Avg fwd 10d | Win 10d | Avg fwd 20d | Win 20d |
|----------|---|-----------|--------|-------------|---------|-------------|---------|
| Q1 | 13651 | +0.78% | +54.24% | +1.52% | +55.89% | +2.92% | +56.89% |
| Q2 | 12848 | +0.75% | +55.11% | +1.39% | +56.75% | +2.58% | +58.10% |
| Q3 | 13456 | +0.72% | +54.88% | +1.35% | +56.22% | +2.62% | +57.62% |
| Q4 | 12848 | +0.65% | +54.18% | +1.39% | +56.11% | +2.73% | +57.67% |
| Q5 | 13651 | +0.74% | +54.88% | +1.56% | +55.99% | +3.23% | +57.91% |

**Top-minus-bottom quintile spread:** 5d -0.04%  |  10d +0.04%  |  20d +0.31%  (positive ⇒ higher-ranked names outperform lower-ranked names).

## Entry vs Exit Attribution

_Buy the top 2 ranked names each day, hold a fixed period, **no** stop-loss / take-profit / max-holding. Next-day entry, slippage applied._

| Hold period | Raw avg return / trade | Raw win rate | N trades |
|-------------|------------------------|--------------|----------|
| 5d | +0.73% | +53.32% | 1596 |
| 10d | +1.66% | +54.04% | 1586 |
| 20d | +3.29% | +55.43% | 1566 |
| 30d | +5.80% | +57.37% | 1546 |

**Full strategy (with exit rules):** total return +188.53%, win rate +56.67%, avg hold 70.01 trading days.

The raw signal (buy top names, hold fixed, no stops) is **positive across holding periods** (avg +2.87% per trade, 55% win rate). That points to genuine signal quality — higher-ranked names tend to rise even without exit rules.

## P&L Attribution

**Top 5 contributors:**

| Ticker | P&L |
|--------|-----|
| PLTR | $42,447.59 |
| MU | $21,645.10 |
| SPOT | $15,581.89 |
| HOOD | $15,124.71 |
| APP | $12,967.11 |

**Worst 5 contributors:**

| Ticker | P&L |
|--------|-----|
| AMD | $-11,420.70 |
| OKTA | $-11,056.14 |
| TSLA | $-10,904.44 |
| TXN | $-8,079.45 |
| DELL | $-7,349.27 |

**P&L by asset group:**

| Group | P&L |
|-------|-----|
| mega_cap_growth | $21,949.01 |
| financial_crypto_beta | $19,449.64 |
| software_cybersecurity | $16,839.59 |
| semiconductors | $10,192.42 |
| _(ungrouped)_ | $120,101.29 |

## Turnover and Re-entry Diagnostics

| Metric | Value |
|--------|-------|
| Total trades | 250 |
| Trades / month | 6.49 |
| Avg holding period | 70.01 trading days |
| Stop-loss → re-entry ≤5d | 0 |

**Most-entered tickers:** `PLTR`×6, `AMD`×5, `APP`×4, `NU`×4, `SMCI`×4, `TSLA`×4, `SPOT`×4, `HOOD`×4

## Exposure and Benchmark Capture

| Metric | Value |
|--------|-------|
| Avg exposure | +93.45% |
| Max exposure | +98.44% |
| Avg cash (drag) | +6.55% |
| Correlation to SPY | 0.75 |
| Correlation to QQQ | 0.81 |
| Beta to SPY | 1.45 |
| Beta to QQQ | 1.19 |
| Up-capture vs QQQ | 1.31 |
| Down-capture vs QQQ | 1.30 |

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

**Baseline (as configured):** +188.53% return  |  -32.39% max drawdown  |  +56.67% win rate  |  2.11 profit factor

### Run-wide parameters

#### Max Total Exposure  (baseline: 90%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 50% | +96.35% | +15.66% | -173.68% | -17.91% | 146 | +54.29% | 2.34 |
| 70% | +127.63% | +46.95% | -142.40% | -26.66% | 197 | +55.79% | 2.11 |
| 90% ◀ baseline | +188.53% | +107.85% | -81.50% | -32.39% | 250 | +56.67% | 2.11 |
| 100% | +208.06% | +127.37% | -61.97% | -32.88% | 255 | +55.28% | 2.07 |

#### Max Position Size  (baseline: 8.50%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 4.25% | +152.57% | +71.89% | -117.46% | -34.50% | 498 | +52.30% | 1.92 |
| 8.50% ◀ baseline | +188.53% | +107.85% | -81.50% | -32.39% | 250 | +56.67% | 2.11 |
| 12.75% | +141.90% | +61.21% | -128.13% | -37.00% | 160 | +55.84% | 1.97 |
| 17.00% | +106.97% | +26.28% | -163.06% | -26.84% | 128 | +48.39% | 1.60 |
| 25.50% | +83.69% | +3.00% | -186.34% | -32.00% | 76 | +45.95% | 1.63 |

#### Max New Trades / Day  (baseline: 2)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 1 | +212.83% | +132.14% | -57.20% | -33.73% | 258 | +54.84% | 2.05 |
| 2 ◀ baseline | +188.53% | +107.85% | -81.50% | -32.39% | 250 | +56.67% | 2.11 |
| 3 | +177.32% | +96.64% | -92.71% | -32.28% | 256 | +58.54% | 2.03 |
| 5 | +206.36% | +125.68% | -63.67% | -32.05% | 262 | +53.97% | 2.01 |

#### Min Composite Score  (baseline: 0.70)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| none | +188.53% | +107.85% | -81.50% | -32.39% | 250 | +56.67% | 2.11 |
| 0.60 | +188.53% | +107.85% | -81.50% | -32.39% | 250 | +56.67% | 2.11 |
| 0.70 ◀ baseline | +188.53% | +107.85% | -81.50% | -32.39% | 250 | +56.67% | 2.11 |

#### Slippage  (baseline: 0.10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 0.05% | +192.44% | +111.75% | -77.59% | -32.26% | 251 | +56.67% | 2.12 |
| 0.10% ◀ baseline | +188.53% | +107.85% | -81.50% | -32.39% | 250 | +56.67% | 2.11 |
| 0.20% | +169.08% | +88.40% | -100.95% | -32.02% | 252 | +57.02% | 2.06 |
| 0.50% | +170.26% | +89.57% | -99.77% | -34.98% | 258 | +53.23% | 1.93 |

#### Re-entry Recovery Gate  (baseline: 10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +188.53% | +107.85% | -81.50% | -32.39% | 250 | +56.67% | 2.11 |
| 0% | +188.53% | +107.85% | -81.50% | -32.39% | 250 | +56.67% | 2.11 |
| 5% | +188.53% | +107.85% | -81.50% | -32.39% | 250 | +56.67% | 2.11 |
| 10% ◀ baseline | +188.53% | +107.85% | -81.50% | -32.39% | 250 | +56.67% | 2.11 |

#### Signal Weight Profile  (baseline: baseline)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| baseline ◀ baseline | +188.53% | +107.85% | -81.50% | -32.39% | 250 | +56.67% | 2.11 |
| no_1d | +189.17% | +108.48% | -80.86% | -34.06% | 253 | +52.89% | 1.99 |
| less_1d | +188.53% | +107.85% | -81.50% | -32.39% | 250 | +56.67% | 2.11 |
| more_volume | +256.25% | +175.57% | -13.78% | -31.27% | 254 | +54.10% | 2.21 |

### Best 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | signal_weights | more_volume | +256.25% | -13.78% | -31.27% | 2.21 |
| 2 | max_new_trades_per_day | 1 | +212.83% | -57.20% | -33.73% | 2.05 |
| 3 | max_total_exposure | 100% | +208.06% | -61.97% | -32.88% | 2.07 |
| 4 | max_new_trades_per_day | 5 | +206.36% | -63.67% | -32.05% | 2.01 |
| 5 | slippage | 0.05% | +192.44% | -77.59% | -32.26% | 2.12 |

### Worst 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | max_position_pct | 25.50% | +83.69% | -186.34% | -32.00% | 1.63 |
| 2 | max_total_exposure | 50% | +96.35% | -173.68% | -17.91% | 2.34 |
| 3 | max_position_pct | 17.00% | +106.97% | -163.06% | -26.84% | 1.60 |
| 4 | max_total_exposure | 70% | +127.63% | -142.40% | -26.66% | 2.11 |
| 5 | max_position_pct | 12.75% | +141.90% | -128.13% | -37.00% | 1.97 |

### Robustness Notes

The baseline outperforms 79% of all variants. This is broadly consistent across parameter dimensions, suggesting the baseline settings are reasonably competitive in-sample.

The widest in-sample return spread belongs to `max_total_exposure` (111.7 pp range across its variants); `min_composite_score` shows the narrowest spread (0.0 pp), suggesting the strategy is least sensitive to that parameter in this period.

Improvements that appear in only one or two variants should be treated with skepticism — isolated peaks are more likely to reflect in-sample noise than genuine edge. Prefer settings that perform consistently across the full sweep.
