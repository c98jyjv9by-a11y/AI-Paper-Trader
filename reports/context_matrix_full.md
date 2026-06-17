# Context-source sensitivity matrix — model_v4
**Window:** 2026-01-05 → 2026-06-16  |  **Model:** claude-sonnet-4-6  |  **Repeats/cell:** 1

**Reference — strict (follow the model):** +69.84%.  Benchmarks: model +69.61% · SPY +9.40% · QQQ +18.25%.

_Each cell = a behavior setting given a combination of context sources. `vs strict` is the headline: positive ⇒ that context helped the agent beat just following the model. strict is context-invariant, so it is the fixed reference, not a row._

| Sources | Setting | Return | vs strict | Max DD | Sharpe | Trades | Diverg. |
|---------|---------|------:|--------:|------:|------:|------:|-------:|
| none | balanced | +71.32% | +1.49% | -13.67% | 2.96 | 38 | 2 |

_Highest `vs strict` per setting = the most valuable context combo. Sub-noise deltas (Sig? = ·) are not trustworthy on one window — re-validate OOS._

_Paper-trading research only — not investment advice._