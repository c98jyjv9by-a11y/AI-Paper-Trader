# Scenario — model_v4

RECOMMENDED config. model_v3 (83-name universe, score-conditional exits, persistence buy >0.90, rotation funding) plus Barroso volatility targeting (~35% annualized, tuned to v3's vol profile) that shrinks gross exposure when forecast vol is high — dominated v3 on return, drawdown, Sharpe and PF in 2018-2026 validation.

**Universe (83):** CRWD, ORCL, COIN, NFLX, PANW, GOOGL, BAC, MSFT, AVGO, AMZN, COST, ASML, AAPL, JPM, TSM, GS, META, TSLA, MU, AMD, NVDA, LLY, VST, AXON, GE, PLTR, OXY, INTC, BA, PFE, PYPL, SEDG, PLUG, ADBE, CRM, NOW, INTU, SAP, WDAY, SNOW, DDOG, NET, MDB, ZS, FTNT, TEAM, OKTA, TWLO, HUBS, SNPS, CDNS, QCOM, TXN, AMAT, LRCX, KLAC, NXPI, MRVL, ADI, MCHP, ON, ARM, ANET, CSCO, IBM, DELL, SMCI, VRT, APP, SHOP, UBER, ABNB, MELI, SE, SPOT, DASH, RBLX, PINS, SNAP, TTD, NU, HOOD, SOFI

---

# AI Paper Trader — Backtest Report
**Period:** 2026-01-01 → 2026-06-18  |  **Generated:** 2026-06-18

---

## Results Summary

| Metric | Strategy | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|-----|
| Ending Balance | $178,854.76 | $109,741.60 | $120,892.10 | $125,464.90 |
| Total Return | +78.85% | +9.74% | +20.89% | +25.46% |
| Max Drawdown | -14.09% | -8.88% | -11.72% | -16.42% |
| Excess vs SPY | +69.11% | — | — | — |
| Excess vs QQQ | +57.96% | — | — | — |
| Excess vs Equal-Wt | +53.39% | — | — | — |

_Benchmarks: **SPY** and **QQQ** are buy-and-hold of those ETFs. **Equal-Wt Hold** is a synthetic equal-weight buy-and-hold of the strategy's own universe (not the unrelated EWH ETF)._

| Metric | Value |
|--------|-------|
| Starting Value | $100,000.00 |
| Ending Value | $178,854.76 |
| **IRR (annualized, money-weighted)** | **+314.12%** |
| Total Return (on full $ portfolio) | +78.85% |
| Total Capital Deployed (all entries) | $240,236.67 |
| Avg Capital Deployed (snapshot) | $109,555.59 (+109.56% of portfolio) |
| Peak Capital Deployed (snapshot) | $165,041.85 (+165.04% of portfolio) |
| Time Invested | +99.14% of trading days |
| Trading Days | 116 |
| Total Trades | 40 (25 buys, 15 sells) |
| Win Rate | +73.33% |
| Average Win | $3,051.15 |
| Average Loss | $-1,903.36 |
| Profit Factor | 4.41 |
| Avg Holding Period | 56.8 approx. trading days |
| Largest Winner | $10,701.71 |
| Largest Loser | $-3,145.06 |
| Open Positions at End | 10 |
| Total Slippage Cost | $397.12 (+0.40% of start) |
| Avg Slippage / Trade | $9.93 |

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
| 2026-04-10 | SELL | OXY | 181 | $57.65 | $10,433.89 | rotation_funded | $1,109.10 | 32.1 |
| 2026-04-13 | BUY | MRVL | 75 | $131.43 | $9,857.35 | momentum_score=0.9596 | — | — |
| 2026-04-24 | SELL | ASML | 6 | $1,453.07 | $8,718.41 | rotation_funded | $1,283.88 | 77.1 |
| 2026-04-27 | BUY | ARM | 46 | $216.10 | $9,940.41 | momentum_score=0.9753 | — | — |
| 2026-04-28 | SELL | LRCX | 43 | $250.80 | $10,784.49 | rotation_funded | $1,893.23 | 80.0 |
| 2026-04-29 | BUY | INTC | 123 | $94.84 | $11,665.90 | momentum_score=0.9404 | — | — |
| 2026-05-07 | SELL | KLAC | 64 | $175.92 | $11,259.14 | rotation_funded | $2,313.24 | 84.3 |
| 2026-05-08 | BUY | QCOM | 56 | $218.50 | $12,236.12 | momentum_score=0.912 | — | — |
| 2026-05-11 | SELL | TSM | 26 | $403.19 | $10,482.97 | max_holding_period | $2,139.20 | 90.0 |
| 2026-05-12 | BUY | DDOG | 59 | $200.14 | $11,808.25 | momentum_score=0.9042 | — | — |
| 2026-05-15 | SELL | MU | 26 | $723.94 | $18,822.32 | max_holding_period | $10,701.71 | 92.9 |
| 2026-05-15 | SELL | ON | 138 | $113.00 | $15,593.57 | max_holding_period | $7,044.21 | 91.4 |
| 2026-05-15 | SELL | ADI | 28 | $415.93 | $11,646.13 | max_holding_period | $3,260.96 | 90.0 |
| 2026-05-18 | BUY | PANW | 46 | $247.80 | $11,398.69 | momentum_score=0.9295 | — | — |
| 2026-05-18 | BUY | SEDG | 183 | $55.29 | $10,117.19 | momentum_score=0.9952 | — | — |
| 2026-05-18 | SELL | AMAT | 29 | $412.64 | $11,966.66 | max_holding_period | $3,069.96 | 90.0 |
| 2026-05-19 | BUY | CRWD | 18 | $617.50 | $11,114.94 | momentum_score=0.9373 | — | — |
| 2026-05-19 | BUY | ZS | 64 | $175.43 | $11,227.21 | momentum_score=0.9325 | — | — |
| 2026-05-20 | BUY | FTNT | 89 | $130.13 | $11,581.57 | momentum_score=0.906 | — | — |
| 2026-05-27 | SELL | ZS | 64 | $126.28 | $8,082.15 | stop_loss | $-3,145.06 | 5.7 |

## Open Positions at End of Period

| Ticker | Shares | Entry Price | Final Price | Unrealized P&L | Entry Date |
|--------|--------|------------|------------|----------------|------------|
| DELL | 62 | $153.23 | $427.91 | $17,030.20 | 2026-03-02 |
| MRVL | 75 | $131.43 | $326.07 | $14,597.90 | 2026-04-13 |
| ARM | 46 | $216.10 | $430.50 | $9,862.59 | 2026-04-27 |
| INTC | 123 | $94.84 | $134.18 | $4,838.23 | 2026-04-29 |
| QCOM | 56 | $218.50 | $225.62 | $398.60 | 2026-05-08 |
| DDOG | 59 | $200.14 | $222.63 | $1,326.92 | 2026-05-12 |
| PANW | 46 | $247.80 | $285.23 | $1,721.89 | 2026-05-18 |
| SEDG | 183 | $55.29 | $58.58 | $602.03 | 2026-05-18 |
| CRWD | 18 | $617.50 | $679.03 | $1,107.60 | 2026-05-19 |
| FTNT | 89 | $130.13 | $146.08 | $1,419.55 | 2026-05-20 |

## Equity Curve (first and last 5 days)

| Date | Portfolio Value | Daily Ret | Cumulative Ret | SPY Ret | QQQ Ret | EqWt Ret |
|------|----------------|----------|----------------|---------|---------|---------|
| 2026-01-02 | $100,000.00 | — | +0.00% | +0.00% | +0.00% | +0.00% |
| 2026-01-05 | $99,983.56 | -0.02% | -0.02% | +0.67% | +0.79% | +1.66% |
| 2026-01-06 | $100,914.17 | +0.93% | +0.91% | +1.26% | +1.68% | +3.20% |
| 2026-01-07 | $100,321.50 | -0.59% | +0.32% | +0.94% | +1.78% | +2.89% |
| 2026-01-08 | $99,482.26 | -0.84% | -0.52% | +0.93% | +1.20% | +1.38% |
| 2026-06-12 | $169,791.26 | +2.11% | +69.79% | +8.87% | +17.80% | +21.55% |
| 2026-06-15 | $175,959.30 | +3.63% | +75.96% | +10.79% | +21.50% | +25.56% |
| 2026-06-16 | $169,583.47 | -3.62% | +69.58% | +10.13% | +19.19% | +22.35% |
| 2026-06-17 | $172,009.38 | +1.43% | +72.01% | +8.76% | +17.99% | +21.92% |
| 2026-06-18 | $178,854.76 | +3.98% | +78.85% | +9.74% | +20.89% | +25.46% |


## Signal Predictiveness

_Cross-section of 9,545 (date, ticker) signal observations. Correlations are Pearson vs forward returns._

| Signal | vs fwd 5d | vs fwd 10d | vs fwd 20d |
|--------|-----------|------------|------------|
| return_1d | 0.02 | 0.01 | 0.05 |
| return_5d | -0.01 | 0.04 | 0.09 |
| return_20d | 0.06 | 0.10 | 0.18 |
| vol_ratio | 0.00 | -0.02 | 0.01 |
| vol_adj_mom_20d | 0.07 | 0.10 | 0.15 |
| composite_score | 0.05 | 0.07 | 0.11 |

**Forward returns by composite-score quintile** (5 = highest-ranked):

| Quintile | N | Avg fwd 5d | Win 5d | Avg fwd 10d | Win 10d | Avg fwd 20d | Win 20d |
|----------|---|-----------|--------|-------------|---------|-------------|---------|
| Q1 | 1955 | +0.52% | +49.39% | +0.78% | +48.39% | +2.42% | +51.84% |
| Q2 | 1840 | +0.57% | +51.24% | +0.72% | +50.12% | +1.79% | +50.59% |
| Q3 | 1955 | +0.07% | +47.85% | +0.51% | +46.61% | +1.97% | +47.06% |
| Q4 | 1840 | +0.50% | +49.10% | +1.60% | +49.17% | +4.14% | +51.43% |
| Q5 | 1955 | +1.77% | +54.43% | +3.29% | +54.99% | +7.63% | +56.50% |

**Top-minus-bottom quintile spread:** 5d +1.25%  |  10d +2.51%  |  20d +5.21%  (positive ⇒ higher-ranked names outperform lower-ranked names).

## Entry vs Exit Attribution

_Buy the top 2 ranked names each day, hold a fixed period, **no** stop-loss / take-profit / max-holding. Next-day entry, slippage applied._

| Hold period | Raw avg return / trade | Raw win rate | N trades |
|-------------|------------------------|--------------|----------|
| 5d | +2.33% | +56.36% | 220 |
| 10d | +4.60% | +60.00% | 210 |
| 20d | +12.01% | +63.68% | 190 |
| 30d | +18.16% | +65.29% | 170 |

**Full strategy (with exit rules):** total return +78.85%, win rate +73.33%, avg hold 56.76 trading days.

The raw signal (buy top names, hold fixed, no stops) is **positive across holding periods** (avg +9.28% per trade, 61% win rate). That points to genuine signal quality — higher-ranked names tend to rise even without exit rules.

## P&L Attribution

**Top 5 contributors:**

| Ticker | P&L |
|--------|-----|
| DELL | $17,030.20 |
| MRVL | $14,597.90 |
| MU | $10,701.71 |
| ARM | $9,862.59 |
| ON | $7,044.21 |

**Worst 5 contributors:**

| Ticker | P&L |
|--------|-----|
| ZS | $-3,145.06 |
| SNPS | $-1,540.54 |
| TXN | $-1,359.70 |
| SEDG | $-966.11 |
| MCHP | $260.13 |

**P&L by asset group:**

| Group | P&L |
|-------|-----|
| semiconductors | $20,564.30 |
| software_cybersecurity | $2,829.49 |
| _(ungrouped)_ | $55,460.96 |

## Turnover and Re-entry Diagnostics

| Metric | Value |
|--------|-------|
| Total trades | 40 |
| Trades / month | 7.25 |
| Avg holding period | 56.76 trading days |
| Stop-loss → re-entry ≤5d | 0 |

**Most-entered tickers:** `INTC`×2, `SEDG`×2, `MU`×1, `TSM`×1, `ASML`×1, `LRCX`×1, `MCHP`×1, `ON`×1

## Exposure and Benchmark Capture

| Metric | Value |
|--------|-------|
| Avg exposure | +89.30% |
| Max exposure | +97.61% |
| Avg cash (drag) | +10.70% |
| Correlation to SPY | 0.67 |
| Correlation to QQQ | 0.76 |
| Beta to SPY | 2.03 |
| Beta to QQQ | 1.58 |
| Up-capture vs QQQ | 1.97 |
| Down-capture vs QQQ | 1.49 |

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

**Baseline (as configured):** +78.85% return  |  -14.09% max drawdown  |  +73.33% win rate  |  4.41 profit factor

### Run-wide parameters

#### Max Total Exposure  (baseline: 90%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 50% | +41.46% | +31.72% | +15.99% | -11.73% | 24 | +66.67% | 6.63 |
| 70% | +43.81% | +34.07% | +18.34% | -12.90% | 31 | +63.64% | 5.71 |
| 90% ◀ baseline | +78.85% | +69.11% | +53.39% | -14.09% | 40 | +73.33% | 4.41 |
| 100% | +90.36% | +80.62% | +64.90% | -13.48% | 45 | +77.78% | 5.49 |

#### Max Position Size  (baseline: 8.50%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 4.25% | +62.84% | +53.10% | +37.37% | -15.80% | 81 | +48.39% | 2.58 |
| 8.50% ◀ baseline | +78.85% | +69.11% | +53.39% | -14.09% | 40 | +73.33% | 4.41 |
| 12.75% | +89.21% | +79.47% | +63.75% | -14.45% | 36 | +80.00% | 4.60 |
| 17.00% | +72.28% | +62.53% | +46.81% | -12.07% | 45 | +70.00% | 4.64 |
| 25.50% | +101.76% | +92.02% | +76.29% | -14.96% | 54 | +60.00% | 3.61 |

#### Max New Trades / Day  (baseline: 2)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 1 | +80.00% | +70.26% | +54.53% | -15.63% | 41 | +68.75% | 5.58 |
| 2 ◀ baseline | +78.85% | +69.11% | +53.39% | -14.09% | 40 | +73.33% | 4.41 |
| 3 | +91.32% | +81.58% | +65.85% | -14.15% | 40 | +66.67% | 4.67 |
| 5 | +76.58% | +66.83% | +51.11% | -14.46% | 45 | +50.00% | 2.32 |

#### Min Composite Score  (baseline: 0.70)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| none | +78.85% | +69.11% | +53.39% | -14.09% | 40 | +73.33% | 4.41 |
| 0.60 | +78.85% | +69.11% | +53.39% | -14.09% | 40 | +73.33% | 4.41 |
| 0.70 ◀ baseline | +78.85% | +69.11% | +53.39% | -14.09% | 40 | +73.33% | 4.41 |

#### Slippage  (baseline: 0.10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| 0.05% | +76.04% | +66.30% | +50.58% | -14.58% | 43 | +70.59% | 3.36 |
| 0.10% ◀ baseline | +78.85% | +69.11% | +53.39% | -14.09% | 40 | +73.33% | 4.41 |
| 0.20% | +78.40% | +68.66% | +52.94% | -14.11% | 40 | +73.33% | 4.34 |
| 0.50% | +76.92% | +67.18% | +51.45% | -14.10% | 40 | +73.33% | 4.19 |

#### Re-entry Recovery Gate  (baseline: 10%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +78.85% | +69.11% | +53.39% | -14.09% | 40 | +73.33% | 4.41 |
| 0% | +78.85% | +69.11% | +53.39% | -14.09% | 40 | +73.33% | 4.41 |
| 5% | +78.85% | +69.11% | +53.39% | -14.09% | 40 | +73.33% | 4.41 |
| 10% ◀ baseline | +78.85% | +69.11% | +53.39% | -14.09% | 40 | +73.33% | 4.41 |

#### Stop-loss only if score <  (baseline: 0.90)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +78.85% | +69.11% | +53.39% | -14.09% | 40 | +73.33% | 4.41 |
| 0.85 | +78.85% | +69.11% | +53.39% | -14.09% | 40 | +73.33% | 4.41 |
| 0.90 ◀ baseline | +78.85% | +69.11% | +53.39% | -14.09% | 40 | +73.33% | 4.41 |
| 0.95 | +78.85% | +69.11% | +53.39% | -14.09% | 40 | +73.33% | 4.41 |

#### Max-hold only if score <  (baseline: 0.80)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +85.45% | +75.70% | +59.98% | -13.57% | 40 | +73.33% | 4.67 |
| 0.70 | +78.33% | +68.59% | +52.87% | -14.13% | 40 | +73.33% | 4.34 |
| 0.80 ◀ baseline | +78.85% | +69.11% | +53.39% | -14.09% | 40 | +73.33% | 4.41 |
| 0.90 | +79.85% | +70.10% | +54.38% | -14.09% | 40 | +73.33% | 4.62 |

#### Score-decay sell threshold  (baseline: off)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off ◀ baseline | +78.85% | +69.11% | +53.39% | -14.09% | 40 | +73.33% | 4.41 |
| 0.40 | +82.10% | +72.36% | +56.63% | -14.22% | 51 | +63.64% | 2.06 |
| 0.50 | +59.90% | +50.16% | +34.43% | -15.28% | 95 | +41.86% | 2.09 |
| 0.60 | +72.43% | +62.69% | +46.97% | -13.66% | 121 | +48.21% | 3.02 |

#### Persistence-buy threshold  (baseline: 0.90)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +56.07% | +46.33% | +30.61% | -16.01% | 40 | +60.00% | 4.57 |
| 0.80 | +78.06% | +68.32% | +52.60% | -15.02% | 114 | +50.94% | 2.65 |
| 0.85 | +55.38% | +45.64% | +29.92% | -14.37% | 89 | +57.50% | 2.30 |
| 0.90 ◀ baseline | +78.85% | +69.11% | +53.39% | -14.09% | 40 | +73.33% | 4.41 |

#### Vol-target (annualized)  (baseline: 35%)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| off | +76.04% | +66.30% | +50.57% | -14.00% | 48 | +78.95% | 5.03 |
| 15% | +36.18% | +26.44% | +10.72% | -15.50% | 39 | +64.29% | 5.16 |
| 20% | +37.81% | +28.06% | +12.34% | -15.50% | 38 | +64.29% | 4.60 |
| 25% | +46.30% | +36.56% | +20.84% | -15.50% | 37 | +69.23% | 5.23 |
| 30% | +56.46% | +46.72% | +31.00% | -15.66% | 40 | +60.00% | 2.79 |
| 35% ◀ baseline | +78.85% | +69.11% | +53.39% | -14.09% | 40 | +73.33% | 4.41 |

#### Signal Weight Profile  (baseline: baseline)

| Value | Return | vs SPY | vs EqWt | Max DD | Trades | Win Rate | PF |
|-------|--------|--------|--------|--------|--------|----------|-----|
| baseline ◀ baseline | +78.85% | +69.11% | +53.39% | -14.09% | 40 | +73.33% | 4.41 |
| no_1d | +81.26% | +71.52% | +55.80% | -14.70% | 64 | +64.29% | 3.03 |
| less_1d | +78.85% | +69.11% | +53.39% | -14.09% | 40 | +73.33% | 4.41 |
| more_volume | +85.46% | +75.72% | +60.00% | -15.62% | 41 | +60.00% | 4.48 |

### Best 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | max_position_pct | 25.50% | +101.76% | +76.29% | -14.96% | 3.61 |
| 2 | max_new_trades_per_day | 3 | +91.32% | +65.85% | -14.15% | 4.67 |
| 3 | max_total_exposure | 100% | +90.36% | +64.90% | -13.48% | 5.49 |
| 4 | max_position_pct | 12.75% | +89.21% | +63.75% | -14.45% | 4.60 |
| 5 | signal_weights | more_volume | +85.46% | +60.00% | -15.62% | 4.48 |

### Worst 5 Variants by Total Return

| Rank | Parameter | Value | Return | vs EqWt | Max DD | PF |
|------|-----------|-------|--------|--------|--------|-----|
| 1 | target_vol | 15% | +36.18% | +10.72% | -15.50% | 5.16 |
| 2 | target_vol | 20% | +37.81% | +12.34% | -15.50% | 4.60 |
| 3 | max_total_exposure | 50% | +41.46% | +15.99% | -11.73% | 6.63 |
| 4 | max_total_exposure | 70% | +43.81% | +18.34% | -12.90% | 5.71 |
| 5 | target_vol | 25% | +46.30% | +20.84% | -15.50% | 5.23 |

### Robustness Notes

The baseline outperforms 80% of all variants. This is broadly consistent across parameter dimensions, suggesting the baseline settings are reasonably competitive in-sample.

The widest in-sample return spread belongs to `max_total_exposure` (48.9 pp range across its variants); `min_composite_score` shows the narrowest spread (0.0 pp), suggesting the strategy is least sensitive to that parameter in this period.

Improvements that appear in only one or two variants should be treated with skepticism — isolated peaks are more likely to reflect in-sample noise than genuine edge. Prefer settings that perform consistently across the full sweep.
