# AI Paper Trader

A local Python CLI tool for running a simple, auditable paper-trading strategy on U.S. equities and ETFs.

> **This project does not place real trades. It is not financial advice.**

---

## What it does

Everything runs through one front door — `python run.py <command>`:

| Command | What it does |
|---------|-------------|
| `run.py agent` | Daily paper-trading agent — fetches live prices, ranks signals, recommends trades, updates positions, writes a report |
| `run.py backtest --start … --end …` | Walk-forward backtest + diagnostics + sensitivity analysis over a historical range |
| `run.py experiments --start … --end …` | Strategy experiment profiles (signal/exit variants) vs benchmarks |
| `run.py ticker-experiments --start … --end …` | Grouped ticker-aware assumptions vs the capital-matched buy-and-hold test |
| `run.py calibrate --start … --end …` | Per-ticker single-name timing vs buy-and-hold, walk-forward (out-of-sample) |
| `run.py evaluate --start … --end … [--criteria FILE]` | Apply a fixed per-ticker criteria file and score timed vs buy-and-hold (no re-fitting) |
| `run.py active --train-start … --train-end … --test-start … --test-end …` | Per-ticker active-vs-buy-and-hold over a fixed rule grid, build a portfolio of eligible tickers, validate out-of-sample |
| `run.py screen --train-start … --train-end … --test-start … --test-end …` | Factor discovery — rank candidate signals by out-of-sample predictive power (rank-IC); no trading |
| `run.py suite --train-start … --train-end … --test-start … --test-end …` | **Runs the whole stack once → one consolidated summary report** with the salient takeaway from every stage + an auto verdict |
| `run.py scenario <name> --start … --end …` | Run a **named scenario** (trimmed universe + per-ticker rules from `config/scenarios/<name>.yaml`), e.g. `davids_model`. `--list` shows available |
| `run.py adaptive --start … --end … [--rebalance-days N --lookback-days N --top-n N] [--no-charts]` | **Adaptive rotating-signal backtest** — weekly, each ticker trades its recently-best signal or sits in cash; reports a signal-rotation log and **auto-writes per-ticker annotated price charts** (buy/sell reasons vs buy-and-hold). High-turnover, overfit-prone — validate OOS. |

All share the same signal engine, risk rules, slippage, sizing, and exposure limits from `config/strategy.yaml`. No API keys required. Each command is also runnable directly (e.g. `python src/backtest.py …`); `run.py` just centralises them. Run `python run.py -h` for the full list.

---

## Research goals & workflow

Beyond the daily agent, this repo is a research harness built around one question:

> **Does an active signal/exit strategy actually beat simply buying and holding the same names — on a fair, exposure-adjusted, out-of-sample basis?**

Everything is labelled **in-sample** until validated out-of-sample, and the tools refuse to crown a "best" parameter set without that validation. The honest progression:

1. **Understand** — `backtest` runs the strategy and emits diagnostics: signal predictiveness (does composite ranking sort winners from losers?), entry-vs-exit attribution, P&L attribution, turnover, and benchmark capture. `sensitivity` shows whether results are robust or a single lucky cell.
2. **Compare** — `experiments` and `ticker-experiments` test signal/exit variants and grouped ticker-aware assumptions against SPY, QQQ, equal-weight buy-and-hold, and the **capital-matched** equal-weight benchmark (own the same names at the strategy's own average exposure — the fair test).
3. **Determine per-ticker criteria** — `calibrate` walk-forward-fits a small per-ticker timing rule and writes a dated `config/ticker_timing_criteria_<date>.yaml` (flagging `candidate: true` only when a ticker beat its exposure-matched hold with stable parameters). `evaluate` then applies a fixed criteria file (seed or calibrated) over a **held-out** window with no re-fitting.
4. **Stress-test the whole idea** — `active` grid-searches a fixed per-ticker rule set, gates each ticker through an explicit eligibility test, builds a portfolio of only eligible tickers, and validates on a disjoint **train/test** split.

The recurring finding so far (on this universe/period): the momentum/timing signal does **not** show durable per-ticker alpha — most edge that appears in-sample is exposure timing or grid-search luck, and trend-timing mostly reduces drawdown at a cost to return in a bull market. The tooling is designed to surface exactly that, rather than hide it.

---

## Quickstart

```bash
git clone https://github.com/YOUR_USERNAME/ai-paper-trader.git
cd ai-paper-trader
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Run the daily agent:**

```bash
python run.py agent
```

**Run a backtest (and the other analyses):**

```bash
python run.py backtest           --start 2024-01-01 --end 2024-12-31
python run.py experiments        --start 2024-01-01 --end 2024-12-31
python run.py ticker-experiments --start 2024-01-01 --end 2024-12-31
python run.py calibrate          --start 2024-01-01 --end 2024-12-31
python run.py evaluate           --start 2025-01-01 --end 2026-06-12   # apply a fixed criteria file
python run.py active --train-start 2021-06-12 --train-end 2024-06-12 \
                     --test-start  2024-06-12 --test-end  2026-06-12   # active-vs-BH, OOS
```

**Run the tests:**

```bash
pytest
```

---

## Strategy

Long-only momentum. The signal engine ranks every ticker in the universe by a composite score; each signal is converted to a 0–1 percentile rank before weighting, and the top-ranked candidates are selected subject to all risk controls. Weights are configurable in `config/strategy.yaml` — current defaults:

| Signal | Weight |
|--------|--------|
| 1-day return | 10% |
| 5-day return | 25% |
| 20-day return | 30% |
| Volume vs. 20-day average | 35% |

Also computed and available as alternative weight inputs: `realized_vol_20d` and `vol_adj_mom_20d` (return-per-unit-of-risk). Weights can be set per behaviour group (see the experiment tools below).

---

## Risk controls

All parameters live in `config/strategy.yaml` and are used identically by the daily agent and every backtest tool. Current defaults:

| Parameter | Default |
|-----------|---------|
| Starting portfolio | $100,000 |
| Max single position | `auto` (= max exposure ÷ #tickers; or a fixed fraction) |
| Max total long exposure | 75% of portfolio |
| Max new trades per day | 2 |
| Stop loss | −7.5% from entry |
| Take profit | +10% from entry (`null` to disable) |
| Trailing stop | off by default (set `risk.trailing_stop`) |
| Max holding period | ~30 trading days |
| Slippage | 0.10% per fill |

Optional, default-off knobs: `entry_filters.qqq_above_ma` (regime filter), `risk.stop_cooldown_days` (no re-entry after a stop), `portfolio.sizing_mode: score_weighted`, and per-group overrides under `ticker_groups`.

---

## Project structure

```text
ai-paper-trader/
├── run.py                     # unified entry point → src/cli.py
├── config/
│   ├── universe.yaml          # 25-ticker universe (large-caps + semis)
│   ├── strategy.yaml          # all risk/signal params, ticker_groups, entry filters
│   └── ticker_timing_criteria.yaml   # seed per-ticker timing rules (see calibrate/evaluate)
├── data/                      # LIVE paper state — only the daily agent writes here
│   ├── trade_log.csv          # append-only audit log
│   ├── positions.csv          # open paper positions
│   └── portfolio_state.json   # cash balance
├── reports/                   # human-readable Markdown reports (per tool, dated)
├── backtests/                 # CSV outputs from every backtest/research tool (dated)
├── src/
│   ├── cli.py                 # subcommand dispatcher (backtest/experiments/…/active/agent)
│   ├── main.py                # daily paper-trading agent
│   ├── market_data.py         # yfinance wrapper
│   ├── signals.py             # momentum signals + (per-group) composite ranking
│   ├── risk.py                # pure functions: sizing, slippage, exit triggers (stop/TP/trail)
│   ├── portfolio.py           # live state I/O, exit evaluation, entry generation
│   ├── report.py              # daily-agent Markdown report
│   ├── logger.py              # logging setup + trade-log appender
│   ├── backtest.py            # walk-forward engine + per-ticker overrides + sensitivity
│   ├── diagnostics.py         # signal predictiveness, P&L attribution, turnover, capture
│   ├── experiments.py         # strategy-variant profiles vs benchmarks
│   ├── ticker_experiments.py  # grouped ticker assumptions vs capital-matched buy-and-hold
│   ├── signal_calibration.py  # per-ticker single-name timing (walk-forward) + evaluate
│   └── active_experiment.py   # ticker active-vs-BH grid + eligible-ticker portfolio (OOS)
├── tests/                     # 177 tests, no network calls (one file per module)
├── requirements.txt
├── .env.example
└── CLAUDE.md
```

---

## Daily agent (`src/main.py`)

Each run:

1. Loads `config/universe.yaml` and `config/strategy.yaml`
2. Fetches recent OHLCV data via yfinance (`data.period`, default 90 days)
3. Calculates momentum signals and ranks all tickers
4. Loads `data/positions.csv` and refreshes current prices
5. Checks every open position for stop-loss, take-profit, trailing-stop, or max-holding exits
6. Recommends new entries (up to `max_new_trades_per_day`) from the top-ranked candidates
7. Saves updated `data/positions.csv` and `data/portfolio_state.json`
8. Appends all recommendations to `data/trade_log.csv`
9. Writes `reports/report_YYYY-MM-DD.md`

State persists across daily runs — each run picks up where the last left off.

---

## Backtester (`src/backtest.py`)

Walks forward one trading day at a time over the requested date range. On each day:

- Signals are computed using **only data available up to that date** (no look-ahead)
- Buy orders queue at day T's signals and **fill at day T+1's close** (next-day execution)
- Exit triggers (stop-loss, take-profit, holding period) fire and fill at day T's close
- Benchmark returns (SPY, QQQ) are tracked close-to-close from the first sim date

**Output files** (written to `backtests/`, named by the date you ran it):

| File | Contents |
|------|----------|
| `backtest_report_YYYY-MM-DD.md` | Full performance report with all metrics |
| `backtest_trades_YYYY-MM-DD.csv` | Every simulated buy and sell |
| `backtest_equity_curve_YYYY-MM-DD.csv` | Daily portfolio value, cash, P&L, benchmark returns |

**Metrics reported:** total return, max drawdown, SPY/QQQ comparison, excess return, win rate, average win/loss, profit factor, average holding period, largest winner/loser, number of trades.

**Execution assumptions** (documented in every report):

- Entry fills at next-day close — not the same close used to rank signals
- Exit fills at same-day close (mild optimism vs. a true next-open fill)
- Holding period uses calendar days × 5/7 (not a real trading-day calendar)
- No commissions beyond the configured slippage

---

## Data files (live agent)

**`data/trade_log.csv`** — append-only audit log:
```
date, action, ticker, shares, price_with_slippage, trade_value, reason, pnl, portfolio_value_after
```

**`data/positions.csv`** — open paper positions:
```
ticker, shares, entry_price, entry_date, current_price
```

**`data/portfolio_state.json`** — cash balance:
```json
{"cash": 85000.0, "starting_value": 100000.0}
```

---

## Configuration

**Ticker universe** — edit `config/universe.yaml`:

```yaml
tickers:
  - SPY
  - QQQ
  - AAPL
  - MSFT
  # add or remove tickers here
```

**Strategy and risk parameters** — edit `config/strategy.yaml`:

```yaml
portfolio:
  starting_value: 100000.0
  max_position_pct: auto          # or a fixed fraction, e.g. 0.05
  max_total_exposure: 0.75
  max_new_trades_per_day: 2

risk:
  stop_loss: 0.075
  take_profit: 0.10               # null disables take-profit
  max_holding_days: 30
  slippage: 0.001
  # trailing_stop: 0.15           # optional
  # stop_cooldown_days: 5         # optional: no re-entry after a stop

signals:
  top_candidates: 10
  min_composite_score: 0.70       # null to disable the quality filter
  weights: { return_1d: 0.10, return_5d: 0.25, return_20d: 0.30, vol_ratio: 0.35 }

# ticker_groups: { … }            # optional per-group exits / sizing / signal_weights
# entry_filters: { qqq_above_ma: 50 }   # optional regime filter
```

Changes take effect on the next run of any command.

---

## Tests

177 tests, no network calls (all use synthetic data):

```bash
pytest tests/ -v
```

Coverage: position sizing, slippage, exposure caps, stop-loss/take-profit/trailing-stop/holding-period triggers, per-ticker overrides and per-group signal weights, signal calculation and ranking, no-look-ahead bias, cash and equity-curve invariants, benchmark/capital-matched comparison, diagnostics (MFE/MAE/giveback, predictiveness, capture), walk-forward calibration and the evaluate/active out-of-sample machinery, and the CLI dispatcher.

---

## Limitations

- **yfinance data** may be delayed, adjusted, or missing for some tickers
- **Long-only, no options, no short selling**
- **Fixed ticker universe** — tickers delisted during a backtest period may silently disappear from results
- **Holding-period approximation** uses calendar days × 5/7 rather than a real trading-day calendar
- **No commissions** — only slippage is modelled
- **No news/catalyst scoring** — the daily report includes a placeholder; enable it by adding a `NEWS_API_KEY` to `.env`
- **Past simulated results do not predict future performance**

---

## Disclaimer

For educational and research purposes only. Not financial advice. Use at your own risk.
