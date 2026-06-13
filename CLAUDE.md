# AI Paper Trader

Local Python paper-trading research agent. Recommends trades on U.S. equities and ETFs using momentum signals. **No live orders are ever placed.**

## Running

All runners share one entry point — `python run.py <command>` (see `python run.py -h`):

```bash
cd ai-paper-trader
pip install -r requirements.txt

python run.py agent                                          # live daily agent
python run.py backtest           --start … --end …           # backtest + diagnostics + sensitivity
python run.py experiments        --start … --end …           # strategy experiment profiles
python run.py ticker-experiments --start … --end …           # grouped ticker overrides vs capital-matched BH
python run.py calibrate          --start … --end …           # per-ticker timing vs buy-and-hold (walk-forward)
python run.py evaluate           --start … --end … [--criteria FILE]  # score a fixed criteria file (no re-fitting)
python run.py active --train-start … --train-end … --test-start … --test-end …  # ticker active-vs-BH grid + portfolio, OOS
python run.py screen --train-start … --train-end … --test-start … --test-end …  # factor screen: rank candidate signals by OOS rank-IC
python run.py suite  --train-start … --train-end … --test-start … --test-end …  # run the whole stack once -> one consolidated summary report
python run.py scenario davids_model --start … --end …                            # run a named scenario (config/scenarios/<name>.yaml)
python run.py adaptive --start … --end … [--rebalance-days N --lookback-days N --top-n N]  # per-ticker weekly rotating-signal backtest
```

Named scenarios live in `config/scenarios/<name>.yaml` (trimmed universe + per-ticker `ticker_groups`
overrides on the base config); `src/scenarios.py` loads + overlays them and runs a scenario-tagged
backtest. `davids_model` = the OOS-robust trimmed universe (MSFT/ORCL/CRWD) with per-ticker exits.

Per-ticker timing criteria live in `config/ticker_timing_criteria.yaml` (seed). `calibrate` writes a
dated, data-derived `config/ticker_timing_criteria_<date>.yaml`; `evaluate` applies any such file
over a chosen (ideally held-out) window.

Dispatch lives in `src/cli.py`; each module also exposes `run(start, end[, output])` and is still
runnable directly (e.g. `python src/backtest.py …`).

## Testing

```bash
pytest tests/ -v
```

## Project layout

| Path | Purpose |
|------|---------|
| `config/universe.yaml` | Fixed ticker universe |
| `config/strategy.yaml` | All risk and signal parameters |
| `data/positions.csv` | Open paper positions (updated each run) |
| `data/portfolio_state.json` | Cash balance (updated each run) |
| `data/trade_log.csv` | Append-only audit log of every recommendation |
| `reports/` | Daily Markdown reports |
| `src/` | Application source — one module per concern |
| `tests/` | pytest unit tests |

## Module map

- `main.py` — orchestrator; run this
- `market_data.py` — yfinance wrapper
- `signals.py` — momentum signal calculation and ranking
- `risk.py` — pure functions: sizing, slippage, exit triggers, exposure
- `portfolio.py` — state I/O, exit evaluation, entry generation
- `report.py` — Markdown report builder
- `logger.py` — logging setup + trade log appender

## Key constraints

- Paper trading only — recommendations, not live orders
- U.S. equities and ETFs; no options
- Fixed universe defined in `config/universe.yaml`
- All recommendations logged to `data/trade_log.csv`
