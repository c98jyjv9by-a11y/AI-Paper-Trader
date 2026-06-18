# Frozen paper-trading accounts

A **frozen account** is an immutable, version-controlled record of a scenario's trades and
daily portfolio state over a window. We freeze the **derived ledger** (not the config), so
the record survives later model/config changes **and** yfinance revising old prices. This
is what makes a real, stable paper track record.

> Paper-trading research only — no live orders, ever. Accounts live here under `accounts/`
> and never touch the live-agent files in `data/`.

## Layout — `accounts/<name>/`

| File | What |
|------|------|
| `manifest.json` | metadata + SHA-256 of every frozen file (integrity) |
| `trades.csv` | full BUY/SELL log for the window (authoritative) |
| `equity.csv` | daily total value / cash / exposure_mult / forecast_vol |
| `positions.csv` | open book at `frozen_through` |
| `rankings/` | the daily write-once ranking snapshots in the window |
| `reports/` | rendered status MD + EOD PDF + backtest report for the window |

`accounts/ACTIVE` names the promoted/primary account.

## Commands

```bash
# Freeze a window into an immutable account (refuses to overwrite without --force):
python run.py account-freeze --name primary --scenario model_v4 --start 2026-01-01 --end 2026-06-17

# Verify the frozen files still match their manifest hashes (integrity / drift check):
python run.py account-verify --name primary

# Extend a living account forward (Phase 2), seeded from its latest state. --scenario
# defaults to the account's base; pass the CURRENT model to "follow the active model":
python run.py account-continue --name primary --end 2026-06-30 --scenario model_v4
```

## Daily rhythm (a living account)

```bash
# Intraday — a Midday Pulse on the locked book marked to today's provisional price:
python run.py midday --account primary

# After the close — advance the account one day; this ALSO renders + archives the day's
# EOD + status reports into accounts/primary/reports/:
python run.py account-continue --name primary --end <today> --scenario model_v4
```

You can also render an EOD PDF on demand from the ledger any time: `python run.py eod --account primary`.

## Reading the frozen account in reports

`rank_report.build_report(..., account="primary")` serves the **frozen** trades / equity /
positions instead of recomputing — so a report for the locked window is reproducible
regardless of what `model_v4.yaml` says today or how the price feed has been revised.

## Guarantees & scope

- **Immutable:** `account-freeze` refuses to overwrite an existing account (needs `--force`);
  `manifest.json` hashes + `account-verify` + git detect any drift.
- **Survives change:** because the *derived* ledger is stored (not re-derived), changing or
  switching the model never alters a frozen account.
## Living continuation (Phase 2)

`account-continue` extends an account forward from its latest state, trading with the model
you pass (`--scenario`) — so it **follows the active model** and builds a blended track
record. It writes only under `continuation/` (trades / equity / positions) and records each
run in `manifest.json → segments`; the **frozen core is never modified**, so `account-verify`
still proves the original window is intact. Reads (`build_report(account=...)`) see the
combined frozen + continuation view automatically.

The resume carries over **cash, open positions (with their real entry dates and trailing
peaks → max-hold and trailing-stop clocks keep ticking) and the trailing equity (so the vol
governor stays warm)**. It does *not* carry the engine's transient streak / cooldown /
re-entry state, which resets at the seam — so a continuation is a faithful *forward* run, not
bit-identical to a single uninterrupted backtest over the whole span (expect tiny differences
right after the seam). The locked history is unaffected either way.
