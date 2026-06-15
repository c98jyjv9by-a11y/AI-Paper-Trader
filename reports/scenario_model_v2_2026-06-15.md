# Scenario — model_v2

Full 21-name universe with one uniform exit rule applied to every ticker (stop 15%, no take-profit, no trailing stop, 60-day max hold) plus the trough-based anti-falling-knife re-entry gate. Composite ranking drives entries.

**Universe (83):** CRWD, ORCL, COIN, NFLX, PANW, GOOGL, BAC, MSFT, AVGO, AMZN, COST, ASML, AAPL, JPM, TSM, GS, META, TSLA, MU, AMD, NVDA, LLY, VST, AXON, GE, PLTR, OXY, INTC, BA, PFE, PYPL, SEDG, PLUG, ADBE, CRM, NOW, INTU, SAP, WDAY, SNOW, DDOG, NET, MDB, ZS, FTNT, TEAM, OKTA, TWLO, HUBS, SNPS, CDNS, QCOM, TXN, AMAT, LRCX, KLAC, NXPI, MRVL, ADI, MCHP, ON, ARM, ANET, CSCO, IBM, DELL, SMCI, VRT, APP, SHOP, UBER, ABNB, MELI, SE, SPOT, DASH, RBLX, PINS, SNAP, TTD, NU, HOOD, SOFI

---

# AI Paper Trader — Backtest Report
**Period:** 2026-03-01 → 2026-06-13  |  **Generated:** 2026-06-15

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Ending Balance | $140,366.23 | $108,362.10 | $118,773.50 | $126,231.50 |
| Total Return | +40.37% | +8.36% | +18.77% | +26.23% |
| Max Drawdown | -14.33% | -7.68% | -8.48% | -11.04% |
| Excess vs SPY | +32.00% | — | — | — |
| Excess vs QQQ | +21.59% | — | — | — |
| Excess vs Equal-Wt | +14.13% | — | — | — |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $140,366.23 |
| **IRR (annualized, money-weighted)** | **+283.91%** |
| Total Return (on full $ portfolio) | +40.37% |
| Total Capital Deployed (all entries) | $170,832.93 |
| Avg Capital Deployed (snapshot) | $97,493.52 (+97.49% of portfolio) |
| Peak Capital Deployed (snapshot) | $147,085.52 (+147.09% of portfolio) |
| Time Invested | +98.63% of trading days |
| Trading Days | 73 |
| Total Trades | 31 (20 buys, 11 sells) |
| Win Rate | +0.00% |
| Average Win | $0.00 |
| Average Loss | $-1,484.89 |
| Profit Factor | 0.00 |
| Avg Holding Period | 21.0 approx. trading days |
| Largest Winner | $-1,221.76 |
| Largest Loser | $-1,789.17 |
| Open Positions at End | 9 |
| Total Slippage Cost | $244.53 (+0.24% of start) |
| Avg Slippage / Trade | $7.89 |

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
| 2026-03-18 | SELL | TTD | 283 | $23.53 | $6,658.00 | stop_loss | $-1,636.53 | 8.6 |
| 2026-03-19 | BUY | SEDG | 177 | $45.71 | $8,089.91 | momentum_score=0.9729 | — | — |
| 2026-03-24 | SELL | AXON | 14 | $456.14 | $6,386.01 | stop_loss | $-1,599.31 | 14.3 |
| 2026-03-25 | BUY | ARM | 58 | $157.23 | $9,119.17 | momentum_score=0.8705 | — | — |
| 2026-03-25 | SELL | NOW | 67 | $102.96 | $6,898.11 | stop_loss | $-1,279.37 | 11.4 |
| 2026-03-26 | BUY | AMD | 36 | $203.97 | $7,343.06 | momentum_score=0.8946 | — | — |
| 2026-03-26 | SELL | COIN | 40 | $173.21 | $6,928.26 | stop_loss | $-1,308.36 | 15.0 |
| 2026-03-26 | SELL | APP | 16 | $390.82 | $6,253.10 | stop_loss | $-1,789.17 | 14.3 |
| 2026-03-27 | BUY | OXY | 122 | $65.08 | $7,940.33 | momentum_score=0.9036 | — | — |
| 2026-03-31 | BUY | COST | 7 | $995.98 | $6,971.87 | momentum_score=0.8886 | — | — |
| 2026-04-09 | SELL | PLTR | 53 | $130.36 | $6,909.05 | stop_loss | $-1,390.03 | 22.1 |
| 2026-04-14 | SELL | OXY | 122 | $55.07 | $6,718.58 | stop_loss | $-1,221.76 | 12.9 |
| 2026-04-15 | BUY | SNAP | 1500 | $6.05 | $9,069.00 | momentum_score=0.9256 | — | — |
| 2026-04-15 | SELL | SEDG | 177 | $37.79 | $6,689.22 | stop_loss | $-1,400.69 | 19.3 |
| 2026-04-16 | BUY | HOOD | 95 | $86.94 | $8,259.00 | momentum_score=0.9157 | — | — |
| 2026-04-28 | SELL | SPOT | 15 | $433.77 | $6,506.49 | stop_loss | $-1,783.59 | 38.6 |
| 2026-04-29 | BUY | INTC | 103 | $94.84 | $9,769.00 | momentum_score=0.9404 | — | — |
| 2026-04-29 | SELL | HOOD | 95 | $71.13 | $6,757.24 | stop_loss | $-1,501.76 | 9.3 |
| 2026-06-03 | SELL | NFLX | 87 | $81.44 | $7,085.15 | stop_loss | $-1,423.25 | 65.7 |
| 2026-06-04 | BUY | OKTA | 102 | $123.60 | $12,607.56 | momentum_score=0.8867 | — | — |

## Open Positions at End of Period

| Ticker | Shares | Entry Price | Final Price | Unrealized P&L | Entry Date |
|--------|--------|------------|------------|----------------|------------|
| DELL | 55 | $144.88 | $395.57 | $13,788.12 | 2026-03-03 |
| PLUG | 3811 | $2.48 | $2.76 | $1,057.55 | 2026-03-04 |
| MRVL | 90 | $93.35 | $279.70 | $16,771.81 | 2026-03-10 |
| ARM | 58 | $157.23 | $380.81 | $12,967.81 | 2026-03-25 |
| AMD | 36 | $203.97 | $511.57 | $11,073.46 | 2026-03-26 |
| COST | 7 | $995.98 | $982.35 | $-95.42 | 2026-03-31 |
| SNAP | 1500 | $6.05 | $5.26 | $-1,179.00 | 2026-04-15 |
| INTC | 103 | $94.84 | $124.57 | $3,061.71 | 2026-04-29 |
| OKTA | 102 | $123.60 | $116.29 | $-745.98 | 2026-06-04 |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2026-03-02 | $100,000.00 | — | +0.00% | +0.00% | +0.00% | +0.00% |
| 2026-03-03 | $99,983.54 | -0.02% | -0.02% | -0.88% | -1.07% | -0.95% |
| 2026-03-04 | $100,154.83 | +0.17% | +0.15% | -0.18% | +0.44% | +1.03% |
| 2026-03-05 | $99,436.32 | -0.72% | -0.56% | -0.74% | +0.13% | +1.83% |
| 2026-03-06 | $98,700.71 | -0.74% | -1.30% | -2.04% | -1.37% | +0.70% |
| 2026-06-08 | $139,469.48 | +3.25% | +39.47% | +7.99% | +17.91% | +27.44% |
| 2026-06-09 | $133,540.44 | -4.25% | +33.54% | +7.68% | +16.55% | +24.61% |
| 2026-06-10 | $128,747.38 | -3.59% | +28.75% | +5.98% | +14.22% | +21.33% |
| 2026-06-11 | $136,825.31 | +6.27% | +36.83% | +7.78% | +18.08% | +25.51% |
| 2026-06-12 | $140,366.23 | +2.59% | +40.37% | +8.36% | +18.77% | +26.23% |


## Signal Predictiveness

_Cross-section of 5,976 (date, ticker) signal observations. Correlations are Pearson vs forward returns._

| Signal | vs fwd 5d | vs fwd 10d | vs fwd 20d |
|--------|-----------|------------|------------|
| return_1d | 0.01 | 0.01 | 0.05 |
| return_5d | -0.04 | 0.04 | 0.09 |
| return_20d | 0.04 | 0.11 | 0.13 |
| vol_ratio | 0.01 | 0.02 | 0.08 |
| vol_adj_mom_20d | 0.05 | 0.09 | 0.09 |
| composite_score | 0.04 | 0.09 | 0.12 |

**Forward returns by composite-score quintile** (5 = highest-ranked):

| Quintile | N | Avg fwd 5d | Win 5d | Avg fwd 10d | Win 10d | Avg fwd 20d | Win 20d |
|----------|---|-----------|--------|-------------|---------|-------------|---------|
| Q1 | 1224 | +1.58% | +53.63% | +3.09% | +55.84% | +7.91% | +62.82% |
| Q2 | 1152 | +1.51% | +54.14% | +2.80% | +56.35% | +6.49% | +59.43% |
| Q3 | 1224 | +0.93% | +51.82% | +3.20% | +54.81% | +7.62% | +58.60% |
| Q4 | 1152 | +1.09% | +50.83% | +3.78% | +56.05% | +9.41% | +64.39% |
| Q5 | 1224 | +2.75% | +56.66% | +6.58% | +63.40% | +13.82% | +66.59% |

**Top-minus-bottom quintile spread:** 5d +1.16%  |  10d +3.48%  |  20d +5.91%  (positive ⇒ higher-ranked names outperform lower-ranked names).

## Entry vs Exit Attribution

_Buy the top 2 ranked names each day, hold a fixed period, **no** stop-loss / take-profit / max-holding. Next-day entry, slippage applied._

| Hold period | Raw avg return / trade | Raw win rate | N trades |
|-------------|------------------------|--------------|----------|
| 5d | +3.48% | +54.48% | 134 |
| 10d | +8.42% | +70.97% | 124 |
| 20d | +21.57% | +75.00% | 104 |
| 30d | +33.26% | +79.76% | 84 |

**Full strategy (with exit rules):** total return +40.37%, win rate +0.00%, avg hold 21.05 trading days.

The raw signal (buy top names, hold fixed, no stops) is **positive across holding periods** (avg +16.68% per trade, 70% win rate). That points to genuine signal quality — higher-ranked names tend to rise even without exit rules.

## P&L Attribution

**Top 5 contributors:**

| Ticker | P&L |
|--------|-----|
| MRVL | $16,771.81 |
| DELL | $13,788.12 |
| ARM | $12,967.81 |
| AMD | $11,073.46 |
| INTC | $3,061.71 |

**Worst 5 contributors:**

| Ticker | P&L |
|--------|-----|
| APP | $-1,789.17 |
| SPOT | $-1,783.59 |
| TTD | $-1,636.53 |
| AXON | $-1,599.31 |
| HOOD | $-1,501.76 |

**P&L by asset group:**

| Group | P&L |
|-------|-----|
| semiconductors | $24,041.27 |
| software_cybersecurity | $-1,279.37 |
| financial_crypto_beta | $-2,810.12 |
| _(ungrouped)_ | $20,414.46 |

## Turnover and Re-entry Diagnostics

| Metric | Value |
|--------|-------|
| Total trades | 31 |
| Trades / month | 9.07 |
| Avg holding period | 21.05 trading days |
| Stop-loss → re-entry ≤5d | 0 |

**Most-entered tickers:** `DELL`×1, `NFLX`×1, `PLUG`×1, `AXON`×1, `COIN`×1, `SPOT`×1, `TTD`×1, `APP`×1

## Exposure and Benchmark Capture

| Metric | Value |
|--------|-------|
| Avg exposure | +88.74% |
| Max exposure | +98.03% |
| Avg cash (drag) | +11.26% |
| Correlation to SPY | 0.68 |
| Correlation to QQQ | 0.78 |
| Beta to SPY | 1.95 |
| Beta to QQQ | 1.55 |
| Up-capture vs QQQ | 1.74 |
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

## Sensitivity Analysis

> One parameter is varied at a time; everything else stays at the scenario's configured values. **Run-wide** params apply to the whole backtest. **Ticker** params overwrite that exit field for *every* `ticker_groups` name at once — a uniform stand-in for the per-ticker mix, with the real heterogeneous config shown as the `as-configured` baseline row.
> In-sample only — do not pick parameters off these tables; see Robustness Notes.

**Baseline (as configured):** +40.37% return  |  -14.33% max drawdown  |  +0.00% win rate  |  0.00 profit factor

### Run-wide parameters

#### Max Total Exposure  (baseline: 90%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 50% | +21.42% | +13.06% | -4.81% | -12.23% | 16 | +0.00% | 0.00 |
| 70% | +37.73% | +29.37% | +11.50% | -12.21% | 22 | +0.00% | 0.00 |
| 90% ◀ baseline | +40.37% | +32.00% | +14.13% | -14.33% | 31 | +0.00% | 0.00 |
| 100% | +42.72% | +34.36% | +16.49% | -14.02% | 29 | +0.00% | 0.00 |

#### Max Position Size  (baseline: 8.50%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 4.25% | +38.67% | +30.31% | +12.44% | -12.08% | 43 | +0.00% | 0.00 |
| 8.50% ◀ baseline | +40.37% | +32.00% | +14.13% | -14.33% | 31 | +0.00% | 0.00 |
| 12.75% | +47.39% | +39.03% | +21.16% | -16.99% | 18 | +0.00% | 0.00 |
| 17.00% | +78.25% | +69.89% | +52.02% | -17.55% | 10 | +0.00% | 0.00 |
| 25.50% | +34.25% | +25.89% | +8.02% | -22.49% | 7 | +0.00% | 0.00 |

#### Max New Trades / Day  (baseline: 2)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 1 | +60.69% | +52.33% | +34.46% | -15.85% | 20 | +0.00% | 0.00 |
| 2 ◀ baseline | +40.37% | +32.00% | +14.13% | -14.33% | 31 | +0.00% | 0.00 |
| 3 | +43.38% | +35.01% | +17.15% | -14.86% | 27 | +0.00% | 0.00 |
| 5 | +60.22% | +51.86% | +33.99% | -15.02% | 23 | +0.00% | 0.00 |

#### Min Composite Score  (baseline: 0.70)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| none | +40.37% | +32.00% | +14.13% | -14.33% | 31 | +0.00% | 0.00 |
| 0.60 | +40.37% | +32.00% | +14.13% | -14.33% | 31 | +0.00% | 0.00 |
| 0.70 ◀ baseline | +40.37% | +32.00% | +14.13% | -14.33% | 31 | +0.00% | 0.00 |

#### Slippage  (baseline: 0.10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 0.05% | +40.49% | +32.13% | +14.26% | -14.32% | 31 | +0.00% | 0.00 |
| 0.10% ◀ baseline | +40.37% | +32.00% | +14.13% | -14.33% | 31 | +0.00% | 0.00 |
| 0.20% | +45.68% | +37.31% | +19.44% | -13.99% | 31 | +0.00% | 0.00 |
| 0.50% | +49.39% | +41.03% | +23.16% | -14.45% | 31 | +0.00% | 0.00 |

#### Re-entry Recovery Gate  (baseline: 10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +40.37% | +32.00% | +14.13% | -14.33% | 31 | +0.00% | 0.00 |
| 0% | +40.37% | +32.00% | +14.13% | -14.33% | 31 | +0.00% | 0.00 |
| 5% | +40.37% | +32.00% | +14.13% | -14.33% | 31 | +0.00% | 0.00 |
| 10% ◀ baseline | +40.37% | +32.00% | +14.13% | -14.33% | 31 | +0.00% | 0.00 |

#### Signal Weight Profile  (baseline: baseline)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| baseline ◀ baseline | +40.37% | +32.00% | +14.13% | -14.33% | 31 | +0.00% | 0.00 |
| no_1d | +49.19% | +40.83% | +22.96% | -14.44% | 29 | +0.00% | 0.00 |
| less_1d | +40.37% | +32.00% | +14.13% | -14.33% | 31 | +0.00% | 0.00 |
| more_volume | +56.70% | +48.34% | +30.47% | -13.53% | 23 | +0.00% | 0.00 |

### Best 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | max_position_pct | 17.00% | +78.25% | +52.02% | -17.55% | 0.00 |
| 2 | max_new_trades_per_day | 1 | +60.69% | +34.46% | -15.85% | 0.00 |
| 3 | max_new_trades_per_day | 5 | +60.22% | +33.99% | -15.02% | 0.00 |
| 4 | signal_weights | more_volume | +56.70% | +30.47% | -13.53% | 0.00 |
| 5 | slippage | 0.50% | +49.39% | +23.16% | -14.45% | 0.00 |

### Worst 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | max_total_exposure | 50% | +21.42% | -4.81% | -12.23% | 0.00 |
| 2 | max_position_pct | 25.50% | +34.25% | +8.02% | -22.49% | 0.00 |
| 3 | max_total_exposure | 70% | +37.73% | +11.50% | -12.21% | 0.00 |
| 4 | max_position_pct | 4.25% | +38.67% | +12.44% | -12.08% | 0.00 |
| 5 | signal_weights | less_1d | +40.37% | +14.13% | -14.33% | 0.00 |

### Robustness Notes

39% of variants beat the baseline. Improvements are mixed — some directions help, others hurt — which is consistent with a strategy that has modest but not dominant in-sample edge.

The widest in-sample return spread belongs to `max_position_pct` (44.0 pp range across its variants); `min_composite_score` shows the narrowest spread (0.0 pp), suggesting the strategy is least sensitive to that parameter in this period.

Improvements that appear in only one or two variants should be treated with skepticism — isolated peaks are more likely to reflect in-sample noise than genuine edge. Prefer settings that perform consistently across the full sweep.
