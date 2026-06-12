# AI Paper Trader

A local Python agent that researches U.S. equity and ETF momentum and recommends paper trades. It never places real orders.

## Quickstart

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the agent (fetches live prices, writes report + trade log)
python src/main.py

# 3. Read today's report
open reports/report_$(date +%Y-%m-%d).md
```

## What it does each run

1. Loads the ticker universe from `config/universe.yaml`
2. Downloads 60 days of daily OHLCV data via yfinance
3. Calculates momentum signals (1-day, 5-day, 20-day returns; volume ratio)
4. Ranks all tickers by a composite momentum score
5. Scans open positions for stop-loss / take-profit / max-holding-period exits
6. Recommends up to 3 new entries from the top-ranked candidates
7. Appends all recommendations to `data/trade_log.csv`
8. Writes a Markdown report to `reports/report_YYYY-MM-DD.md`

## Risk rules (defaults)

| Rule | Value |
|------|-------|
| Starting portfolio | $100,000 |
| Max single position | 5 % |
| Max total exposure | 30 % |
| Max new trades / day | 3 |
| Stop loss | 5 % |
| Take profit | 10 % |
| Max holding period | 10 trading days |
| Slippage assumption | 0.10 % |

All parameters are adjustable in `config/strategy.yaml`.

## Running tests

```bash
pytest tests/ -v
```

## Adding a news / catalyst source

Set `NEWS_API_KEY` in a `.env` file (copy `.env.example`). The report will
note that catalyst scoring is disabled until a key is configured.

## Disclaimer

**This tool is for research and paper trading only. It does not place real trades and is not financial advice.**
