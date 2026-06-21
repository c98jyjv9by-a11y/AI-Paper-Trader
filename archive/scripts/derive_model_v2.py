"""
derive_model_v2.py — Calibrate every ticker's best config and build the `model_v2` scenario.

Modes:
  * Ticker calibration (literal): walk-forward SMA calibration over the full window
    → standard MD + dated criteria YAML.
  * Best-config-per-ticker: grid-search each ticker's stop/tp/trail/hold rule on the
    full TRAIN window (per-ticker valid start, so short-history names like COIN/CRWD
    are included), read its TEST-window performance, and write EVERY ticker into
    config/scenarios/model_v2.yaml with its best available config.

Windows (per the user):
  * TRAIN = 2019-01-01 → 2026-06-13  (full history — "best config available")
  * TEST  = 2023-01-01 → 2026-06-13  (a SUBSET of train → the test read is IN-SAMPLE)

This build trades robustness for coverage: it keeps all names with their best in-sample
fit, NOT only the OOS-robust few. Treat the per-ticker configs as best-fit, not validated.

Read-only w.r.t. live state: writes only to reports/, backtests/, config/.

    python derive_model_v2.py
"""
import sys
from datetime import date
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent / "src"))

from backtest import load_config, fetch_backtest_data
from signal_calibration import (
    calibrate_universe, evaluate_criteria, load_criteria,
    render_report as render_calib, render_evaluation, export_criteria, results_csv as calib_csv,
)
from active_experiment import (
    compute_entry_signals, grid_search_ticker, evaluate_ticker_rule, _idx_window, ENTRY_FILTERS,
)
from signal_screen import screen_factors, render_report as render_screen, results_csv as screen_csv, _is_real
from logger import setup_logging
import logging

log = logging.getLogger("derive_model_v2")

# ─── Windows / objective (locked with the user) ───────────────────────────────
TRAIN = (date(2019, 1, 1), date(2026, 6, 13))   # full history
TEST = (date(2023, 1, 1), date(2026, 6, 13))    # subset of train → in-sample read
OBJECTIVE = "sharpe"
SCENARIO = "model_v2"
REENTRY_RECOVER_PCT = 0.05    # carried over from davids_model (anti-falling-knife gate)
_MIN_TRAIN_BARS = 120         # need at least this much history to fit a rule


def _trail_yaml(v):
    return "null" if v is None else f"{v}"


def _tp_yaml(v):
    return "null" if v is None else f"{v}"


def main() -> None:
    setup_logging()
    run_date = date.today()
    root = Path(__file__).parent
    reports, backtests, cfgdir = root / "reports", root / "backtests", root / "config"
    for d in (reports, backtests):
        d.mkdir(parents=True, exist_ok=True)
    tag = run_date.isoformat()

    config = load_config(cfgdir)
    tickers = config["tickers"]
    slippage = config["risk"].get("slippage", 0.001)
    log.info("=== model_v2 (all-ticker best config): %d tickers, train %s→%s, test %s→%s, objective=%s ===",
             len(tickers), TRAIN[0], TRAIN[1], TEST[0], TEST[1], OBJECTIVE)

    price_data = fetch_backtest_data(tickers, TRAIN[0], TEST[1], warmup_days=420)
    close = price_data["Close"]

    # ── Stage 1: literal walk-forward ticker calibration over the full window ──
    log.info("Stage 1/3: ticker calibration (walk-forward, objective=%s) over full window", OBJECTIVE)
    calib = calibrate_universe(price_data, tickers, TRAIN[0], TRAIN[1], slippage, OBJECTIVE)
    (reports / f"model_v2_calibration_{tag}.md").write_text(
        render_calib(calib, run_date, TRAIN[0], TRAIN[1], OBJECTIVE))
    calib_csv(calib).to_csv(backtests / f"model_v2_calibration_{tag}.csv", index=False)
    criteria_path = cfgdir / f"ticker_timing_criteria_{tag}.yaml"
    export_criteria(calib, criteria_path, run_date)
    calibrated_criteria = load_criteria(criteria_path)
    # In-sample read of the calibrated SMA rule on the TEST window (for the MD only)
    eval_cal = evaluate_criteria(price_data, calibrated_criteria, TEST[0], TEST[1], slippage)
    (reports / f"model_v2_eval_calibrated_{tag}.md").write_text(
        render_evaluation(eval_cal, criteria_path.name, run_date, TEST[0], TEST[1]))
    calib_csv(eval_cal).to_csv(backtests / f"model_v2_eval_calibrated_{tag}.csv", index=False)

    # ── Stage 2: per-ticker best engine config (grid, per-ticker valid start) ──
    log.info("Stage 2/3: per-ticker grid search for best engine config (this is the slow stage)")
    full = _idx_window(close, TRAIN[0], TEST[1])
    tr = _idx_window(close, TRAIN[0], TRAIN[1])
    te = _idx_window(close, TEST[0], TEST[1])
    if not (full and tr and te):
        raise SystemExit("Train/test windows not found in the fetched data.")
    signals = compute_entry_signals(price_data, config, tickers, full[0], full[1])

    per_ticker = []
    for t in tickers:
        if t not in close.columns:
            continue
        carr = close[t].to_numpy()
        entry_t = {f: signals[f][t] for f in ENTRY_FILTERS if t in signals[f]}
        valid = np.where(~np.isnan(carr[: tr[1] + 1]))[0]      # first real price in train
        if valid.size == 0:
            log.info("%s: no price history in train window — skipped", t)
            continue
        a = max(tr[0], int(valid[0]))
        if tr[1] - a < _MIN_TRAIN_BARS:
            log.info("%s: only %d train bars (<%d) — skipped", t, tr[1] - a, _MIN_TRAIN_BARS)
            continue
        gs = grid_search_ticker(carr, entry_t, a, tr[1], slippage)
        if gs is None:
            continue
        gs["ticker"] = t
        gs["train_start_offset"] = a - tr[0]
        # In-sample read on TEST window
        gs["test"] = evaluate_ticker_rule(carr, entry_t[gs["rule"]["filter"]], te[0], te[1],
                                           gs["rule"], slippage)
        per_ticker.append(gs)

    # ── Stage 3: factor screen (context — is there any signal?) ────────────────
    log.info("Stage 3/3: factor rank-IC screen")
    screen_rows = screen_factors(close, price_data["Volume"], (TRAIN[0], TRAIN[1]), TEST)
    (reports / f"model_v2_screen_{tag}.md").write_text(render_screen(screen_rows, run_date, (TRAIN[0], TRAIN[1]), TEST))
    screen_csv(screen_rows).to_csv(backtests / f"model_v2_screen_{tag}.csv", index=False)
    screen_survivors = [r["factor"] for r in screen_rows if _is_real(r)]

    # ── Emit model_v2.yaml with ALL fitted tickers ─────────────────────────────
    per_ticker.sort(key=lambda r: (r["test"]["excess"] if r.get("test") and r["test"].get("excess") is not None else -9),
                    reverse=True)
    names = [r["ticker"] for r in per_ticker]
    n = len(names)
    groups = []
    for r in per_ticker:
        rule = r["rule"]
        groups.append(
            f"  {r['ticker'].lower()}:\n"
            f"    tickers: [{r['ticker']}]\n"
            f"    stop_loss: {rule['stop']}\n"
            f"    take_profit: {_tp_yaml(rule['tp'])}\n"
            f"    trailing_stop: {_trail_yaml(rule['trail'])}\n"
            f"    max_holding_days: {rule['hold']}"
        )
    scen = f"""# ─── Scenario: model_v2 ─────────────────────────────────────────────────────
# DATA-DERIVED. Built by derive_model_v2.py on {tag}.
#
# ALL {n} universe tickers, each carrying its BEST-FIT engine exit rule, grid-searched
# on the full {TRAIN[0]} → {TRAIN[1]} history (per-ticker valid start). The chosen rule is
# whatever maximised the active-eligibility/Sharpe objective over that window.
#
# ⚠️ IN-SAMPLE: train (2019→2026) CONTAINS the {TEST[0]}→{TEST[1]} test window, so these are
# best-fit parameters, NOT out-of-sample-validated. Expect optimistic in-sample numbers.
# Entries are still driven by the composite ranker; per-ticker ENTRY filters are not
# wired into the engine (informational only — same caveat as davids_model).

name: {SCENARIO}
description: >
  All {n} universe names, each with its best-fit (in-sample, 2019-2026) active-grid exit
  rule. Composite ranking drives entries; per-ticker entry filters not yet wired.
  Best-fit, not OOS-validated — interpret accordingly.

tickers:
{chr(10).join(f"  - {nm}" for nm in names)}

portfolio:
  max_position_pct: auto          # = max_total_exposure / {n}
  max_total_exposure: 0.90
  max_new_trades_per_day: 5

signals:
  min_composite_score: null       # ranker still orders the full universe each day

# Anti-falling-knife re-entry gate (trough-based): after a STOP-LOSS exit, track the
# name's lowest price since that stop and block re-entry until it bounces >={REENTRY_RECOVER_PCT:.0%}
# above that trough. Only fires after stops; it merely UNBLOCKS — the ranker still picks.
risk:
  reentry_recover_pct: {REENTRY_RECOVER_PCT}

# Per-ticker exit/sizing rules (one group per ticker → true per-ticker overrides).
# Parameters are each ticker's best-fit grid rule over the full train window.
ticker_groups:
{chr(10).join(groups)}
"""
    scen_dir = cfgdir / "scenarios"
    scen_dir.mkdir(parents=True, exist_ok=True)
    out = scen_dir / f"{SCENARIO}.yaml"
    out.write_text(scen)

    # ── Derivation report ──────────────────────────────────────────────────────
    def _p(v):
        return "—" if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v*100:+.1f}%"

    def _num(v):
        return "—" if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))) else f"{v:.2f}"

    L = [
        "# model_v2 — All-Ticker Best-Config Derivation",
        f"**Universe:** {len(tickers)} names  |  **Train (fit):** {TRAIN[0]} → {TRAIN[1]}  |  "
        f"**Test (in-sample read):** {TEST[0]} → {TEST[1]}  |  **Objective:** {OBJECTIVE}  |  "
        f"**Generated:** {tag}",
        "",
        "> Every ticker is grid-searched over the full train window for its best stop/tp/trail/hold "
        "rule and written into `model_v2` with that config. **Train contains test**, so the TEST "
        "columns are an in-sample read, not out-of-sample validation.",
        "",
        "## Factor screen verdict",
        "",
        (f"- Surviving factors (rank-IC): **{', '.join(screen_survivors)}**."
         if screen_survivors else
         "- **No factor survived the rank-IC screen** — no broad cross-sectional signal in this "
         "universe. Per-ticker configs below are best-fit timing on each name, not a universe edge."),
        "",
        "## Per-ticker best config (sorted by in-sample TEST excess vs hold)",
        "",
        "| Ticker | Best rule (filter / sl / tp / trail / hold) | TRAIN excess | TRAIN Sharpe | TEST excess | TEST act ret | TEST hold ret | Eligible |",
        "|--------|---------------------------------------------|--------------|--------------|-------------|--------------|---------------|----------|",
    ]
    for r in per_ticker:
        rule, t = r["rule"], r.get("test", {})
        tp = "null" if rule["tp"] is None else f"{rule['tp']:.0%}"
        trail = "null" if rule["trail"] is None else f"{rule['trail']:.0%}"
        L.append(
            f"| {r['ticker']} | {rule['filter']} / {rule['stop']:.1%} / {tp} / {trail} / {rule['hold']}d "
            f"| {_p(r.get('excess'))} | {_num(r.get('active_sharpe'))} "
            f"| {_p(t.get('excess'))} | {_p(t.get('active_return'))} | {_p(t.get('hold_return'))} "
            f"| {'✅' if r.get('eligible') else '·'} |"
        )
    n_test_beat = sum(1 for r in per_ticker if r.get("test", {}).get("excess") is not None and r["test"]["excess"] > 0)
    L += [
        "",
        "## Summary",
        "",
        f"- **{n}/{len(tickers)}** tickers fitted and written to `model_v2`.",
        f"- In-sample TEST read: **{n_test_beat}/{n}** names' fitted rule beat their own buy-and-hold "
        "on 2023-2026 (in-sample — optimistic).",
        "",
        "## Honest caveats",
        "",
        "- **This is a best-fit, not a validated, model.** Train (2019-2026) contains the test window, "
        "so every per-ticker number here is in-sample. The real test is a fresh, disjoint period.",
        "- The earlier ≥2-OOS-test build kept only MSFT/NFLX/ORCL; this build keeps everyone by request. "
        "Most of these names' timing rules lose to buy-and-hold out-of-sample (see the prior derivation).",
        "- Composite-ranker entries still decide which fitted name is actually bought each day; "
        "per-ticker entry filters shown are informational (not wired into the engine).",
        "",
        f"Run it:\n\n```bash\npython run.py scenario {SCENARIO} --start {TEST[0]} --end {TEST[1]}\n```",
        "",
    ]
    deriv = reports / f"model_v2_derivation_{tag}.md"
    deriv.write_text("\n".join(L))

    # ── Console summary ─────────────────────────────────────────────────────────
    print()
    print(f"  Tickers fitted   : {n}/{len(tickers)}  ({', '.join(names)})")
    print(f"  Screen survivors : {', '.join(screen_survivors) or 'none'}")
    print(f"  In-sample TEST   : {n_test_beat}/{n} fitted rules beat own buy-and-hold (optimistic)")
    print(f"  Scenario written : {out}")
    print(f"  Derivation view  : {deriv}")
    print(f"  Calibration MD   : reports/model_v2_calibration_{tag}.md")
    print(f"  Run it           : python run.py scenario {SCENARIO} --start {TEST[0]} --end {TEST[1]}")
    print()


if __name__ == "__main__":
    main()
