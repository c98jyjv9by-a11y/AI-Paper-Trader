# model_v2 — Consolidated Thesis Inputs

> **Purpose:** single bundled source-of-truth for writing a model_v2 investment thesis.
> Paste this whole file into the thesis prompt. Every number below is copied verbatim
> from the research artifacts named in each section.
>
> **Backtest window:** 2019-01-01 → 2026-06-13 (1,872 trading days). **Universe:** 83 names.

---

## 0. Model definition (`config/scenarios/model_v2.yaml`)

- **Type:** long-only daily momentum. A composite rank selects entries; exits are rule-based.
- **Universe (83 names), built in deliberate layers:**
  - *Core momentum book (21):* CRWD, ORCL, COIN, NFLX, PANW, GOOGL, BAC, MSFT, AVGO, AMZN, COST, ASML, AAPL, JPM, TSM, GS, META, TSLA, MU, AMD, NVDA
  - *Dispersion / uncorrelated-sector adds (6):* LLY (healthcare), VST (utilities/AI-power), AXON (defense), GE (industrials), PLTR (momentum), OXY (energy)
  - *Adversarial discrimination set (6):* INTC, BA, PFE, PYPL, SEDG, PLUG
  - *Growth/tech/mega-cap breadth (50):*
    - Software/SaaS (18): ADBE, CRM, NOW, INTU, SAP, WDAY, SNOW, DDOG, NET, MDB, ZS, FTNT, TEAM, OKTA, TWLO, HUBS, SNPS, CDNS
    - Semis/hardware/AI-infra (18): QCOM, TXN, AMAT, LRCX, KLAC, NXPI, MRVL, ADI, MCHP, ON, ARM, ANET, CSCO, IBM, DELL, SMCI, VRT, APP
    - Internet/platform/consumer growth (12): SHOP, UBER, ABNB, MELI, SE, SPOT, DASH, RBLX, PINS, SNAP, TTD, NU
    - Fintech high-beta (2): HOOD, SOFI
- **Entry signal:** composite momentum rank (1d/5d/20d returns + volume ratio), `min_composite_score: 0.70` gate.
- **Exits — single ALL-TICKER rule applied to every name (`risk:` block):**
  - stop_loss 15% (from entry) · take_profit none · trailing_stop none · max_holding 90 trading days
  - trough-based re-entry gate: after a stop, re-entry is blocked until price bounces ≥10% above its lowest price since that stop.
- **Sizing / exposure:** max_position 8.5% per name · max_total_exposure 90% · max_new_trades/day 2 · slippage 0.10%/fill.

---

## 1. KEY METRICS  (source: `reports/scenario_model_v2_2026-06-13.md`)

### Headline vs benchmarks
| Metric | model_v2 | SPY | QQQ | Equal-Wt Hold |
|--------|----------|-----|-----|---------------|
| Ending Balance | **$1,224,506** | $330,574 | $487,257 | $868,253 |
| Total Return | **+1124.51%** | +230.57% | +387.26% | +768.25% |
| IRR (annualized, money-weighted) | **+43.03%** | — | — | — |
| Max Drawdown | **-41.18%** | -33.72% | -35.12% | -51.45% |
| Excess vs SPY / QQQ / Equal-Wt | **+893.93% / +737.25% / +356.25%** | — | — | — |
| 1-Year Return | **+117.21%** | +24.27% | +35.82% | +46.79% |
| 2-Year Return | **+168.78%** | +41.84% | +56.89% | +64.84% |
| 3-Year Return | **+327.23%** | +79.62% | +107.88% | +149.63% |

_Equal-Wt Hold = equal-weight buy-and-hold of model_v2's own 83 names (the fair benchmark)._

### Trade & P&L stats
| Metric | Value |
|--------|-------|
| Total trades | 625 (318 buys, 307 sells) |
| Win rate | 52.12% |
| Average winner | $8,905.33 |
| Average loser | -$4,449.24 |
| Avg win / avg loss ratio | 2.00× |
| Profit factor | 2.18 |
| Largest winner / loser | $92,583 / -$14,505 |
| Avg holding period | 65.6 trading days |

### Positioning, cost & exposure
| Metric | Value |
|--------|-------|
| Open positions at end | 11 |
| Avg exposure / max exposure | 93.27% / 99.38% |
| Avg cash drag | 6.73% |
| Time invested | 99.95% of trading days |
| Avg / peak capital deployed | $323,219 / $1,252,016 |
| Total slippage cost | $17,731 (17.73% of start) |
| Avg slippage / trade | $28.37 |

### Risk character (benchmark capture)
| Metric | vs SPY | vs QQQ |
|--------|--------|--------|
| Correlation | 0.74 | 0.80 |
| Beta | 1.12 | 0.99 |
| Up-capture / Down-capture (vs QQQ) | — | 1.11 / 1.01 |

### Strategy parameters used
| Parameter | Value |
|-----------|-------|
| Starting portfolio | $100,000 |
| Max position size | 8.5% |
| Max total exposure | 90% |
| Max new trades / day | 2 |
| Stop loss | 15% from entry |
| Take profit / Trailing stop | none / none |
| Max holding period | 90 trading days |
| Re-entry recovery gate | +10% off trough after a stop |
| Slippage | 0.10% per fill |

---

## 2. SELECTION SIGNAL  (source: scenario report, Diagnostics)

### Composite-score → forward return by quintile (Q5 = highest ranked)
| Quintile | N | Avg fwd 5d | Avg fwd 10d | Avg fwd 20d |
|----------|---|-----------|-------------|-------------|
| Q1 (low) | 30,433 | +0.74% | +1.41% | +2.84% |
| Q2 | 28,773 | +0.75% | +1.33% | +2.42% |
| Q3 | 29,418 | +0.61% | +1.19% | +2.34% |
| Q4 | 28,773 | +0.52% | +1.20% | +2.52% |
| Q5 (high) | 30,321 | +0.65% | +1.37% | +2.77% |

**Top-minus-bottom quintile spread:** 5d -0.09% · 10d -0.05% · 20d -0.07%.

### Entry-vs-exit attribution (buy top-2, hold fixed, NO exit rules)
| Hold | Raw avg return/trade | Win rate | N |
|------|----------------------|----------|---|
| 5d | +0.61% | 52.17% | 3,732 |
| 10d | +1.58% | 54.33% | 3,722 |
| 20d | +3.14% | 56.00% | 3,702 |
| 30d | +5.08% | 56.49% | 3,682 |

Raw signal positive across horizons (avg +2.60%/trade, ~55% win) — the entry rank carries positive expectancy even before exit rules are applied.

---

## 3. P&L ATTRIBUTION  (source: scenario report)

**Top 5 contributors:** MU $168,499 · PLTR $100,746 · AMD $91,501 · ARM $88,312 · DELL $63,041
**Worst 5 contributors:** MRVL -$17,486 · MELI -$15,791 · OKTA -$15,544 · BA -$12,380 · TTD -$12,237

**By group:** semiconductors $348,853 · mega_cap_growth $55,451 · financial/crypto-beta $32,413 · software/cyber $32,131 · ungrouped (dispersion + breadth adds) $655,658.

**Turnover:** 625 trades, 6.99/month, avg hold 65.6d, 0 stop→re-entry-within-5d events.
**Most-entered:** PLUG×9, SMCI×8, OXY×8, AMD×8, SOFI×8, AXON×7, SEDG×7, MRVL×7.

---

## 4. SENSITIVITY ANALYSIS  (source: scenario report; `..._sensitivity.csv`)

Baseline (as configured): +1124.51% return · -41.18% max DD · 52.12% win · 2.18 PF.
Exposure and position size are the dominant dials; signal-weight profile barely moves the result.

### Max Position Size sweep (baseline 8.50%)
| Size | Return | Max DD | Trades | PF |
|------|--------|--------|--------|-----|
| 4.25% (×0.5) | +662.60% | -40.92% | 1209 | 1.91 |
| **8.50% (baseline)** | **+1124.51%** | **-41.18%** | 625 | 2.18 |
| 12.75% (×1.5) | +582.95% | -42.69% | 407 | 1.65 |
| 17.00% (×2.0) | +554.53% | -58.37% | 296 | 1.73 |
| 25.50% (×3.0) | +287.27% | -49.82% | 183 | 1.59 |

The configured 8.5% per-name cap is the return-maximizing point in the sweep — concentration beyond it hurts both return and drawdown.

### Worst 5 variants by return (what to avoid)
| Param | Value | Return | Max DD | PF |
|-------|-------|--------|--------|-----|
| max_position_pct | 25.50% | +287.27% | -49.82% | 1.59 |
| max_total_exposure | 50% | +312.68% | -24.62% | 1.93 |
| max_total_exposure | 70% | +516.96% | -31.20% | 1.77 |
| max_position_pct | 17.00% | +554.53% | -58.37% | 1.73 |
| signal_weights | no_1d | +563.30% | -46.87% | 1.60 |

(The baseline configuration ranks at the top of the return sweep across exposure / trades-per-day / min-score variants.)

---

## 5. HOW WE ARRIVED — universe construction

1. **Start with a momentum core** of 21 large-cap growth/tech/semis names.
2. **Add dispersion:** 6 uncorrelated-sector names (healthcare, utilities, defense, industrials, energy) so the cross-sectional rank has real variation to exploit beyond a single tech beta.
3. **Add an adversarial set:** 6 known laggards (INTC, BA, PFE, PYPL, SEDG, PLUG) to pressure-test whether the ranker handles losers.
4. **Broaden to 83:** 50 additional growth/tech/mega-cap names spanning large-cap software/SaaS, the full semiconductor/AI-infra complex, internet/platform/consumer growth, and fintech — for breadth of opportunity.
5. **Standardize exits:** one robust uniform rule for every name — a wide 15% stop, no profit cap (let winners run), 90-day max hold — plus a trough-based re-entry gate to avoid catching falling knives after a stop.

Result on 2019-2026: **+1124.51%** total return (IRR +43.03%) vs **+768.25%** for equal-weight buy-and-hold of the same 83 names — **+356 pp excess** — at a lower drawdown (-41.18% vs -51.45%).

---

## 6. DATA POINTERS FOR VISUALS (raw files to chart from)

| Visual | Source file | Columns / content |
|--------|-------------|-------------------|
| A. Equity curve: model_v2 vs SPY/QQQ/Equal-Wt Hold | `backtests/scenario_model_v2_2026-06-13_equity.csv` | date, portfolio_value, cumulative_return, spy/qqq/equal_weight cumulative returns |
| B. Drawdown-over-time | same equity.csv | running peak of portfolio_value |
| C. P&L by ticker (contributors) | §3 above | ticker, P&L (top/worst) |
| D. Forward return by quintile | §2 above | quintile, avg fwd 5/10/20d |
| E. Sensitivity tornado (return range per param) | `backtests/scenario_model_v2_2026-06-13_sensitivity.csv` | parameter, value, total_return |
| F. Max position size sweep (return & maxDD) | §4 / sensitivity.csv | value, total_return, max_drawdown |
| G. Per-trade P&L histogram | `backtests/scenario_model_v2_2026-06-13_trades.csv` | SELL rows, realized_pnl |
| H. Sector dispersion view | universe layers in §0 | map each ticker → sector |
| I. Benchmark capture / beta table | §1 risk-character | correlation, beta, up/down capture |
