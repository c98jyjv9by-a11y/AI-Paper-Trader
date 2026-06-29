# `research/` — analysis & backtest scripts

One-off scripts that validate the strategy ideas behind `model_v4` and its overlays/accounts. They are
**not** wired into `run.py` — run each directly:

```bash
python research/make_<name>.py
```

Most reuse the cached daily score panel + price data via the shared helper **`_common.load_ctx()`**
(returns `ROOT, cfg, px, close, S, Z`) — new scripts should too, instead of repeating the
ROOT/sys.path/score-panel/z boilerplate. PDF outputs land in `reports/` (gitignored); console-only
scripts print tables. **Findings are summarized in `CLAUDE.md`** — this file is just the map.

> Caveats that apply to ~all of these: frictionless unless noted, survivorship-biased (current universe),
> and z-based ones start 2020+ (60-day z warm-up).

## z-reversal / z-score (the `zscore_*` accounts)
| script | what it answers | output |
|---|---|---|
| `make_zscore_ic_sweep.py` | IC of trailing-avg z vs forward returns (which window×horizon predicts best) | console |
| `make_zscore_corr_horizon.py` | pooled Pearson r, trailing {1,5,10}d avg-z → fwd {1,5,10}d return (no tail filter) | `reports/corr_tails_zscore.pdf` |
| `make_zscore_buckets_horizon.py` | mean fwd return by **absolute** z-bucket (`<-2 … >2`) + universe baseline | `reports/zscore_buckets_horizon.pdf` |
| `make_zscore_rankgroups_horizon.py` | mean fwd return by **cross-sectional** z-rank group (bottom-10 / 3 mids / top-10) + the account cells | `reports/zscore_rankgroups_horizon.pdf` |
| `make_latency_edge.py` | splits the close-signal's fwd return into overnight (lost to open-exec) vs intraday — momentum vs z-reversal | console |
| `make_zscore_reversal_strategy.py` | 5-day z-reversal (mean-reversion) backtest | console |
| `make_zscore_reversal_biweekly.py` | the IC-optimal variant: 10-day avg z, bottom-10, biweekly | console |
| `make_zscore_reversal_filtered.py` | + regime filter (hold only when QQQ > 200d MA) — the validated config | console |
| `make_zscore_bottom_daily.py` | daily-rebalanced bottom-10 on the 60-day z (two ranking signals) | console |
| `make_zscore_bottom_weekly.py` | weekly-rebalanced bottom-10 on the 60-day z | console |
| `make_zscore_daily.py` | daily top-10 by the 60-day z (the high-z side) | console |
| `make_zscore_freq_compare.py` | annual returns trading on the 60-day z ranking | console |
| `make_zscore_returns_report.py` | rank-by-60-day-rolling-z returns report | console |
| `make_zscore_putwrite.py` | **S1 options prototype** — put-WRITING (cash-secured puts / put-credit spreads) on the bottom-10 z names vs the equity book; BS-modeled premiums + realized-vol IV proxy (see `options_strategy_notes.md`) | console |

## Leveraged ETFs (TQQQ / SQQQ — the `LevEtf` scenario)
| script | what it answers | output |
|---|---|---|
| `make_levetf_corr_tails.py` | which trailing model_v4 metrics predict fwd TQQQ/SQQQ moves (corr_tails by horizon) | `reports/corr_tails_levetf.pdf` |
| `make_levetf_volstate.py` | vol-state tilt (TQQQ-or-cash by QQQ realized-vol z) — risk-OFF is the robust rule | `reports/levetf_volstate.pdf` |
| `make_levetf_shock.py` | 1-day vol-gated shock-reversal (regime-dependent; fails OOS) | `reports/levetf_shock.pdf` |

## model_v4 overlays (rebound / hedge / defense)
| script | what it answers | output |
|---|---|---|
| `make_model_v4_rebound.py` | the 3 trigger versions of the 1-day TQQQ rebound overlay | `reports/model_v4_rebound.pdf` |
| `make_model_v4_rebound_sweep.py` | tune the combo rebound trigger (QQQ down & spread<0 & vol-z) | `reports/model_v4_rebound_sweep.pdf` |
| `make_model_v4_reverse.py` | hedge-in-reverse (down-shock → buy TQQQ); sweeps hold length | `reports/model_v4_reverse.pdf` |
| `make_model_v4_defense.py` | two sell-off defenses: cash de-risk vs SQQQ tranche (cash wins) | `reports/model_v4_defense.pdf` |
| `make_trim_funding_test.py` | fund the overlay by trimming the book (rotation) vs free cash | console |
| `make_volfactor_compare.py` | overlays gating on QQQ 5d-vol z instead of the current gate | console |
| `make_hedge_recommendation.py` | the combined hedge-overlay recommendation report | `reports/hedge_overlay_recommendation.pdf` |

## Score / momentum ranker sweeps (model_v4's signal validation)
| script | what it answers | output |
|---|---|---|
| `make_freq_compare.py` | annual returns: weekly vs monthly, top-10 vs bottom-10 | console |
| `make_rebal_sweep.py` | sweep rebalance frequency (daily…quarterly) at 60-day lookback | console |
| `make_weekly_lb_sweep.py` | sweep the score lookback (trailing N-day avg) at weekly rebalance | console |
| `make_weekly_lookback.py` | weekly rebalance ranked by the trailing 20-day avg score | console |
| `make_weekly_60d_split.py` | train/test split (2020-22 vs 2023-26) of the 60-day weekly top-10 | console |
| `make_weekly_top10.py` | weekly top-10 strategy by year | console |
| `make_monthly_score_fwd.py` | rank by prior-month avg score → forward returns, per month | console |
| `make_monthly_spread_history.py` | monthly score-spread table back to 2020 + yearly summary | console |
| `make_cycle_test.py` | 3-year-cycle backtest across three universes (**test-only**) | `backtests/` |
| `make_pit_universe.py` | re-run the winner on a broader existence-gated pool (survivorship check) | console |
| `make_score_leaders.py` | highest avg composite score per ticker (1M / YTD / 1Y / 3Y) | console |
| `make_score_returns_report.py` | rank by 4 score windows as of yesterday's close | console |
| `make_rolling_chart.py` | reproduce the rolling 1-year returns chart | `reports/*.png` |

## Guides / infographics (non-technical)
| script | what it answers | output |
|---|---|---|
| `make_model_v4_guide.py` | concise non-technical guide to model_v4 | `reports/model_v4_guidebook.pdf` |
| `make_infographic_poster.py` | one-page infographic poster of the whole model | `reports/model_v4_infographic_poster.pdf` |
| `make_process_infographic.py` | non-technical visual walkthrough of the pipeline | `reports/model_v4_process_infographic.pdf` |

---
*Shared helper:* `research/_common.py` — `load_ctx(scenario="model_v4", start=…, z_lookback=60)` →
`SimpleNamespace(ROOT, cfg, px, close, S, Z)`. Used by the `*_horizon` + `latency` scripts; prefer it for new ones.
