AI Paper Trader

A local Python CLI tool for running a simple, auditable paper-trading strategy on U.S. equities and ETFs.

The project fetches market data, calculates momentum signals, ranks trade candidates, applies risk controls, tracks simulated positions, and generates daily Markdown reports. It is designed for research, strategy testing, and paper-trading analysis only.

This project does not place real trades. It is not financial advice.

⸻

Overview

AI Paper Trader is a local paper-trading research agent. Each run:

1. Loads a fixed ticker universe from config/universe.yaml
2. Loads strategy and risk assumptions from config/strategy.yaml
3. Fetches recent historical price data
4. Calculates momentum signals
5. Ranks trade candidates
6. Evaluates exits for existing paper positions
7. Generates new paper trade recommendations
8. Updates local CSV/JSON state files
9. Produces a daily Markdown report

The current strategy is a long-only momentum strategy using price and volume signals.

⸻

Current Strategy

The signal engine ranks tickers using:

* 1-day return
* 5-day return
* 20-day return
* Volume ratio versus 20-day average volume

Each signal is percentile-ranked and combined into a composite score.

Default ranking weights:

1_day_return: 20%
5_day_return: 30%
20_day_return: 30%
volume_ratio: 20%

The strategy is intentionally simple so that assumptions, trade selection, and performance can be audited.

⸻

Risk Controls

Default risk assumptions are stored in config/strategy.yaml.

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

This means:

* Starting paper portfolio: $100,000
* Max single position: 5%
* Max total long exposure: 30%
* Max new trades per day: 3
* Stop loss: -5%
* Take profit: +10%
* Max holding period: 10 trading days
* Slippage assumption: 0.10% per trade

⸻

Project Structure

ai-paper-trader/
├── config/
│   ├── universe.yaml
│   └── strategy.yaml
├── data/
│   ├── trade_log.csv
│   ├── positions.csv
│   └── portfolio_state.json
├── reports/
│   └── report_YYYY-MM-DD.md
├── src/
│   ├── main.py
│   ├── market_data.py
│   ├── signals.py
│   ├── risk.py
│   ├── portfolio.py
│   ├── report.py
│   └── logger.py
├── tests/
│   ├── test_risk.py
│   └── test_signals.py
├── requirements.txt
├── .env.example
├── CLAUDE.md
└── README.md

⸻

File Descriptions

File	Purpose
src/main.py	Main orchestrator and CLI entry point
src/market_data.py	Fetches price data using yfinance
src/signals.py	Calculates momentum signals and ranks candidates
src/risk.py	Pure risk functions for sizing, slippage, exposure, stops, and holding-period checks
src/portfolio.py	Loads and saves portfolio state, evaluates exits, and generates entries
src/report.py	Builds and saves Markdown reports
src/logger.py	Appends trades to the audit log
config/universe.yaml	Fixed ticker universe
config/strategy.yaml	Strategy, signal, risk, and data assumptions
data/trade_log.csv	Append-only trade recommendation/action log
data/positions.csv	Current open paper positions
data/portfolio_state.json	Current paper cash balance and starting value
reports/	Generated daily reports
tests/	Unit tests for risk and signal logic

⸻

Installation

1. Clone the repository

git clone https://github.com/YOUR_USERNAME/ai-paper-trader.git
cd ai-paper-trader

2. Create a virtual environment

python -m venv .venv

Activate it:

source .venv/bin/activate

On Windows:

.venv\Scripts\activate

3. Install dependencies

pip install -r requirements.txt

⸻

Usage

Run the daily paper-trading agent:

python src/main.py

The script will:

* Fetch market data
* Calculate signals
* Evaluate current positions
* Generate new paper trade recommendations
* Update local state files
* Save a Markdown report in reports/

Example output:

Report saved to reports/report_2026-06-12.md

⸻

Reports

Each run creates a daily Markdown report under reports/.

A typical report includes:

* Market data summary
* Ranked momentum candidates
* Buy recommendations
* Sell recommendations for existing positions
* Open positions
* Risk summary
* Trade log summary
* Data limitations
* Catalyst/news placeholder

News and catalyst scoring are currently disabled unless a future verified news source is added.

⸻

Data Files

trade_log.csv

Append-only audit log of recommendations and exits.

Columns:

date, action, ticker, shares, price_with_slippage, trade_value, reason, pnl, portfolio_value_after

positions.csv

Current open paper positions.

Columns:

ticker, shares, entry_price, entry_date, current_price

portfolio_state.json

Stores cash and starting value.

Example:

{
  "cash": 85000.0,
  "starting_value": 100000.0
}

⸻

Configuration

Ticker Universe

Edit config/universe.yaml to change the approved trading universe.

Example:

tickers:
  - SPY
  - QQQ
  - NVDA
  - MSFT
  - AAPL

Strategy Assumptions

Edit config/strategy.yaml to change risk limits, signal settings, or market data settings.

Example:

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
data:
  period: "60d"
  interval: "1d"

⸻

Testing

Run the test suite:

pytest

Current tests cover:

* Position sizing
* Slippage
* Exposure calculation
* Stop-loss triggers
* Take-profit triggers
* Holding-period checks
* Signal calculation
* Candidate ranking

⸻

Current Limitations

This is an early-stage paper-trading research tool.

Known limitations:

* Uses yfinance, which may have missing, delayed, or adjusted data issues
* No live brokerage integration
* No real trade execution
* No short selling
* No options
* No news or catalyst scoring yet
* Fixed ticker universe
* Long-only strategy
* Holding-period logic may be approximate depending on implementation
* CSV/JSON state files are simple and should be handled carefully
* Backtesting support may need further development before strategy conclusions are reliable

⸻

Planned Improvements

Potential next improvements:

* Add dry-run versus commit mode
* Add historical backtesting
* Add benchmark comparison versus SPY and QQQ
* Add performance metrics such as drawdown, win rate, average win/loss, and profit factor
* Add richer data quality checks
* Add actual trading-day calendar logic
* Add verified news/catalyst scoring
* Add rejected-trade explanations
* Add better portfolio accounting and equity curve tracking
* Add Makefile commands for daily workflow

⸻

Backtesting Roadmap

A future backtesting module should:

* Reuse config/strategy.yaml
* Reuse the existing signal engine
* Replay historical dates one day at a time
* Avoid look-ahead bias
* Apply slippage, sizing, exposure caps, stop loss, take profit, and holding-period rules
* Generate:
    * backtest_trades.csv
    * backtest_equity_curve.csv
    * backtest_report_YYYY-MM-DD.md

The goal is to test whether the strategy logic and assumptions are reasonable before relying on daily paper-trading recommendations.

⸻

Disclaimer

This project is for educational and research purposes only.

It does not provide financial advice, investment advice, or trading recommendations for real-money portfolios. The system is intended for paper trading and strategy analysis only. Past performance, simulated or otherwise, does not guarantee future results.

Use at your own risk.
