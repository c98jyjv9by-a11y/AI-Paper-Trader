# AI Paper Trader

Local Python paper-trading research agent. Recommends trades on U.S. equities and ETFs using momentum signals. **No live orders are ever placed.**

## Active model & current state (read this first)

**`model_v4` is THE active model.** It is the only model version in `config/scenarios/`; every
account uses it. Older/experimental versions (v2, v3, v5, v6) and one-off scripts live in
`archive/` (see `archive/README.md`) and are not wired into anything.

- **Model** — `config/scenarios/model_v4.yaml`. 83-name semis/AI/tech momentum book; composite
  score 0–1, buy gate 0.70 (+ persistence buy at >0.90 for 3 days); equal-weight full deployment,
  max total exposure 0.75, ≤2 new trades/day; Barroso vol governor (target 0.35); score-gated
  7.5% stop; 30-day max hold suppressed until score<0.80. **Do NOT change v4's ticker list** —
  broad-universe runs (`make_cycle_test.py`) are test-only.
- **Hedge overlay** — `src/hedge_overlay.py`. A standalone **overlay that sits ON TOP of model_v4
  and never modifies it.** Signal: QQQ 1-day up-shock + SPY 5d-vol z-spike → buy long **SOXS**
  (−3× inverse semis, 1-day hold, **never shorting**) sized inverse-vol; two-gate hybrid
  (soft=half / hard=full). Validated as the only working "June-16-pullback" hedge.
- **Accounts** — `accounts/<name>/` is an append-only ledger system (immutable frozen core +
  `continuation/` living layer; SHA-256 manifest integrity via `account-verify`). Active accounts:
  `primary` (main paper book), `tracker` (frictionless ramp-up sim, assumes 10bp cost),
  `alpaca_tracker` (**broker-driven** go-forward book — ledger synced from real Alpaca paper fills).
- **Broker integration (Alpaca paper, paper-only + submit-guarded)** —
  `src/broker_adapter.py` (REST client; refuses non-paper host; `submit`/`cancel` inert unless
  `confirm=True` AND env `BROKER_ADAPTER_ALLOW_SUBMIT=yes`),
  `src/broker_sync.py` (reconcile-to-target **limit** orders with **data-driven per-instrument
  collars** from the 2y overnight-gap distribution → `backtests/collars.csv`; realized-slippage
  log; broker→ledger sync; `create_broker_account`), and
  `src/broker_cron.py` (cron wrapper: phases open/retry/close/auto, self-guards on the ET market
  clock; **dry-run unless `--live`**). Schedule: `deploy/mv4_crontab.txt` (times in CT = ET−1).
  Daily flow: `open` (submit) → `retry` (re-price unfilled at the wider collar, then skip) →
  `close` (reconcile fills/slippage + render EOD).
- **Research artifacts** — `reports/` (dated EOD/status PDFs+md) and `backtests/` (dated
  CSVs/md) are generated outputs; regenerate, don't hand-edit. Current report/PDF tooling:
  `make_model_v4_guide.py`, `make_hedge_recommendation.py`, `make_rolling_chart.py`,
  `make_cycle_test.py`.

**Standing constraints:** paper trading only (no live orders); never mutate the base live-state
files `data/{trade_log.csv,positions.csv,portfolio_state.json}`; API keys live ONLY in gitignored
`.env` (never commit — verify with `git ls-files | grep -E '(^|/)\.env$|llm_cache'`); commit only
when asked; pushes to GitHub must be run by the user (they fail in the agent environment).

## Running

All runners share one entry point — `python run.py <command>` (see `python run.py -h`):

```bash
cd ai-paper-trader
pip install -r requirements.txt

python run.py account-freeze --name primary --scenario model_v4 --start … --end …  # freeze a scenario's trades+state over a window into an IMMUTABLE account ledger (accounts/<name>/: trades/equity/positions/rankings + rendered reports + manifest hashes); survives model/config changes & price revisions. account-verify --name <n> checks integrity. Reports read it via build_report(..., account=<n>)
python run.py account-continue --name primary --end … [--scenario <model>]          # extend a living account forward from its latest state (seeds cash/positions/governor; resets transient streak state at the seam). Appends under continuation/, leaves the frozen core untouched, AND renders+archives that day's EOD+status reports; --scenario defaults to the account base (pass current model to "follow active")
python run.py eod  [--account <name> | --scenario <s> --start … --end …] [--prepost]  # render the end-of-day PDF — from a frozen/living account ledger, or a fresh scenario run. --prepost marks the latest bar to the after-hours print (live session only)
python run.py midday [--account <name> | --scenario <s> --start … --end …] [--prepost] # render the intraday Midday Pulse PDF — account mode marks the locked book to today's provisional price; --prepost marks to the latest extended-hours (pre/post-market) print (VWAP of last few 1-min bars, stamped "HH:MM ET post-market")
python run.py agent                                          # live daily agent
python run.py backtest           --start … --end …           # backtest + diagnostics + sensitivity
python run.py experiments        --start … --end …           # strategy experiment profiles
python run.py ticker-experiments --start … --end …           # grouped ticker overrides vs capital-matched BH
python run.py calibrate          --start … --end …           # per-ticker timing vs buy-and-hold (walk-forward)
python run.py evaluate           --start … --end … [--criteria FILE]  # score a fixed criteria file (no re-fitting)
python run.py active --train-start … --train-end … --test-start … --test-end …  # ticker active-vs-BH grid + portfolio, OOS
python run.py screen --train-start … --train-end … --test-start … --test-end …  # factor screen: rank candidate signals by OOS rank-IC
python run.py suite  --train-start … --train-end … --test-start … --test-end …  # run the whole stack once -> one consolidated summary report
python run.py scenario davids_model --start … --end …                            # run a named scenario (config/scenarios/<name>.yaml); incl. sensitivity + auto charts + auto status&rank report; --no-sensitivity / --no-charts / --no-status to skip
python run.py rank <name> [--start … --end …] [--top N]                          # status & rank report: top/bottom ranks + signal strength + held book vs SPY/QQQ (dated md + csv)
python src/pdf_report.py --scenario <name> --start … --end …                     # professional end-of-day PDF update (auto-generated commentary + recommendations, rankings, holdings, activity); also auto-written on every scenario run as reports/eod_<name>_<date>.pdf
python src/pdf_report.py --scenario <name> --start … --end … --series [--sim-start … --workers N]  # one EOD COVER page per trading day over [start,end] into a single combined PDF (parallelized, no look-ahead) — for backtesting an agent's read-and-act loop; run_cover_series() also returns the per-date specs
python src/midday_pdf.py --scenario <name> --start … --end …                     # intraday "Midday Pulse" PDF (2 pages): current book moves today, is the signal working so far (top-vs-bottom spread intraday), what's NOT behaving as expected, signal scoreboard. Provisional prices; writes reports/midday_<name>_<date>.pdf
python src/agent_backtest.py --scenario <name> --start … --end … [--no-llm --settings strict,balanced,discretionary --model … --context macro,news]  # backtest an AI agent reading the daily packet and acting under 3 settings; harness owns all fills/accounting, agent emits only structured trades; scores each setting vs the model & SPY/QQQ + logs divergences (writes reports/agent_backtest_*.md). LLM path needs ANTHROPIC_API_KEY; --no-llm uses deterministic stand-ins. --context injects info sources (macro=key-free; news needs FINNHUB_API_KEY)
python src/context_matrix.py --scenario <name> --start … --end … [--sources macro,news --settings balanced,discretionary --model … --repeats N --max-combo-size K --oos-window S:E]  # context-source SENSITIVITY MATRIX: sweeps the power set of context sources × behavior settings, reports return-vs-strict per combo (strict = fixed reference). Builds specs once + caches fetches. Writes reports/context_matrix_*.md/.csv/.json; --repeats adds a noise band, --oos-window re-checks top combos on a disjoint range
python run.py adaptive --start … --end … [--rebalance-days N --lookback-days N --top-n N]  # per-ticker weekly rotating-signal backtest (auto-writes per-ticker charts; --no-charts to skip)
```

`src/scenario_charts.py` renders per-ticker annotated price charts (▲buys/▼sells + reasons, held-period
shading, active-vs-buy-and-hold) — used standalone (`python src/scenario_charts.py --scenario <name> [--since …]`)
and auto-invoked by the `adaptive` command (reusing the already-fetched price panel).

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
