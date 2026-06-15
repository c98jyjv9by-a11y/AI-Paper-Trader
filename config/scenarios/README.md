# Scenarios — named strategy models

**A scenario *is* a model: a named, self-contained config bundle. Everything else in
the repo is shared machinery that evaluates it.**

A scenario (`config/scenarios/<name>.yaml`, e.g. `davids_model`, `model_v2`) is the
complete *definition* of a strategy as data, not code — its universe of tickers,
portfolio limits, signal settings, general risk rules, and (layered on top) per-ticker
overrides. Because each is a standalone named object, scenarios are:

- **comparable** — run the same backtest on each and diff the reports,
- **borrowable** — copy a block from one into another,
- **versionable** — a file you can commit and diff over time.

## The key nuance: layered overrides (general → specific)

Each exit/sizing field resolves per ticker, per field, in this order:

1. a matching `ticker_groups` entry (most specific — overrides one or more named tickers)
2. else the scenario's `risk:` block (the **all-ticker** layer — applies to every name)
3. else the base `config/strategy.yaml` default

So you set a rule once for everyone in `risk:`, and add `ticker_groups` only for the names
that need something different. That's the "general risk rules down to specific ticker
rules" spectrum in a single file.

```yaml
name: example_model
tickers: [AAPL, MSFT, NVDA]          # replaces the base universe wholesale
portfolio: { max_total_exposure: 0.90, max_new_trades_per_day: 3 }
signals:   { min_composite_score: 0.70 }
risk:                                 # ALL-TICKER rule (layer 2)
  stop_loss: 0.15
  take_profit: null
  max_holding_days: 60
ticker_groups:                        # PER-TICKER overrides (layer 1)
  nvda: { tickers: [NVDA], stop_loss: 0.10, trailing_stop: 0.10 }
```

`tickers` and `ticker_groups` replace the base wholesale; `portfolio`/`signals`/`risk`
deep-merge onto it. `name`/`description` are metadata.

## How a scenario gets evaluated (the shared engine — the *how*, not the *what*)

- `src/scenarios.py` — loads a scenario, overlays it on the base config, runs it, writes outputs.
- `src/backtest.py` — the walk-forward simulator **and** the sensitivity sweep (varies one
  parameter at a time: run-wide knobs + each ticker-level exit param swept uniformly).
- `src/signals.py` / `src/risk.py` — the composite ranking, and the exit/sizing/slippage math.
- `src/diagnostics.py` / `src/scenario_charts.py` — explain *why* (P&L attribution, signal
  predictiveness, capture) and render per-ticker annotated charts.
- **Outputs:** `reports/scenario_<name>_<date>.md` (+ sensitivity, diagnostics, charts) and
  `backtests/scenario_<name>_<date>_*.csv`.

Run one:

```bash
python run.py scenario <name> --start YYYY-MM-DD --end YYYY-MM-DD
#   --no-sensitivity   skip the sensitivity section
#   --no-charts        skip the per-ticker charts
python run.py scenario --list
```

## Where scenarios come from (the research tools feed them)

`calibrate`, `evaluate`, `active`, `screen`, and `suite` do **not** define a model — they
*discover* what should go into one (which tickers survive out-of-sample, which exit params
hold up, whether any signal predicts). Their findings get promoted into a scenario YAML,
which then becomes the thing you backtest and stress-test.

**In one line:** scenarios are competing strategy definitions; backtest + sensitivity +
diagnostics are the common test bench they all run through.
