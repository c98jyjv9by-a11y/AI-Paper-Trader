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

All share the same signal engine, risk rules, slippage, sizing, and exposure limits from `config/strategy.yaml`. No API keys required. Each command is also runnable directly (e.g. `python src/backtest.py …`); `run.py` just centralises them. Run `python run.py -h` for the full list.

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
```

**Run the tests:**

```bash
pytest
```

---

## Strategy

Long-only momentum. The signal engine ranks every ticker in the universe by a composite score:

| Signal | Weight |
|--------|--------|
| 1-day return | 20% |
| 5-day return | 30% |
| 20-day return | 30% |
| Volume vs. 20-day average | 20% |

Each signal is converted to a 0–1 percentile rank before weighting. The top-ranked candidates are selected subject to all risk controls.

---

## Risk controls

All parameters live in `config/strategy.yaml` and are used identically by both the daily agent and the backtester.

| Parameter | Default |
|-----------|---------|
| Starting portfolio | $100,000 |
| Max single position | 5% of portfolio |
| Max total long exposure | 30% of portfolio |
| Max new trades per day | 3 |
| Stop loss | −5% from entry |
| Take profit | +10% from entry |
| Max holding period | ~10 trading days |
| Slippage | 0.10% per fill |

---

## Project structure

```text
ai-paper-trader/
├── config/
│   ├── universe.yaml          # 25-ticker universe (ETFs + large-caps)
│   └── strategy.yaml          # all risk and signal parameters
├── data/
│   ├── trade_log.csv          # append-only audit log (live agent)
│   ├── positions.csv          # open paper positions (live agent)
│   └── portfolio_state.json   # cash balance (live agent)
├── reports/
│   └── report_YYYY-MM-DD.md   # daily paper-trading reports
├── backtests/
│   ├── backtest_report_YYYY-MM-DD.md
│   ├── backtest_trades_YYYY-MM-DD.csv
│   └── backtest_equity_curve_YYYY-MM-DD.csv
├── src/
│   ├── main.py                # daily paper-trading agent
│   ├── backtest.py            # walk-forward backtesting engine
│   ├── market_data.py         # yfinance wrapper
│   ├── signals.py             # momentum signal calculation and ranking
│   ├── risk.py                # pure functions: sizing, slippage, exit triggers
│   ├── portfolio.py           # state I/O, exit evaluation, entry generation
│   ├── report.py              # Markdown report builder (daily agent)
│   └── logger.py              # logging setup and trade log appender
├── tests/
│   ├── test_risk.py           # 29 tests for risk.py
│   ├── test_signals.py        # 15 tests for signals.py
│   └── test_backtest.py       # 24 tests for backtest.py
├── requirements.txt
├── .env.example
└── CLAUDE.md
```

---

## Daily agent (`src/main.py`)

Each run:

1. Loads `config/universe.yaml` and `config/strategy.yaml`
2. Fetches 60 days of OHLCV data via yfinance
3. Calculates momentum signals and ranks all tickers
4. Loads `data/positions.csv` and refreshes current prices
5. Checks every open position for stop-loss, take-profit, or max-holding-period exits
6. Recommends up to 3 new entries from the top-ranked candidates
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
  max_position_pct: 0.05
  max_total_exposure: 0.30
  max_new_trades_per_day: 3

risk:
  stop_loss: 0.05
  take_profit: 0.10
  max_holding_days: 10
  slippage: 0.001

signals:
  top_candidates: 10
```

Changes to `strategy.yaml` take effect on the next run of either command.

---

## Tests

68 tests, no network calls:

```bash
pytest tests/ -v
```

Coverage: position sizing, slippage, exposure caps, stop-loss/take-profit/holding-period triggers, signal calculation, candidate ranking, no-look-ahead bias, cash mechanics, equity curve invariants, benchmark comparison.

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
