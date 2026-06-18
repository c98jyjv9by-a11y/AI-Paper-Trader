# Context-source sensitivity matrix — model_v4
**Window:** 2026-01-05 → 2026-06-16  |  **Model:** claude-sonnet-4-6  |  **Repeats/cell:** 1

**Reference — strict (follow the model):** +69.84%.  Benchmarks: model +69.61% · SPY +9.40% · QQQ +18.25%.

_Each cell = a behavior setting given a combination of context sources. `vs strict` is the headline: positive ⇒ that context helped the agent beat just following the model. strict is context-invariant, so it is the fixed reference, not a row._

| Sources | Setting | Return | vs strict | Max DD | Sharpe | Trades | Diverg. |
|---------|---------|------:|--------:|------:|------:|------:|-------:|
| macro+news | balanced | +69.39% | -0.44% | -14.11% | 2.95 | 40 | 4 |
| macro | balanced | +69.01% | -0.83% | -12.43% | 3.02 | 40 | 4 |
| news | balanced | +62.53% | -7.31% | -12.80% | 2.85 | 39 | 6 |
| none | balanced | +61.36% | -8.47% | -14.64% | 2.81 | 35 | 3 |
| macro+news | discretionary | +36.97% | -32.87% | -12.85% | 2.36 | 134 | 48 |
| macro | discretionary | +27.42% | -42.41% | -10.60% | 2.20 | 100 | 40 |
| news | discretionary | +18.52% | -51.31% | -5.14% | 2.20 | 141 | 50 |
| none | discretionary | +18.28% | -51.55% | -8.62% | 1.97 | 160 | 49 |

_Highest `vs strict` per setting = the most valuable context combo. Sub-noise deltas (Sig? = ·) are not trustworthy on one window — re-validate OOS._

_Paper-trading research only — not investment advice._