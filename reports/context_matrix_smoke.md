# Context-source sensitivity matrix — model_v4
**Window:** 2026-06-09 → 2026-06-16  |  **Model:** claude-sonnet-4-6  |  **Repeats/cell:** 1

**Reference — strict (follow the model):** +0.51%.  Benchmarks: model +0.53% · SPY +1.80% · QQQ +3.11%.

_Each cell = a behavior setting given a combination of context sources. `vs strict` is the headline: positive ⇒ that context helped the agent beat just following the model. strict is context-invariant, so it is the fixed reference, not a row._

| Sources | Setting | Return | vs strict | Max DD | Sharpe | Trades | Diverg. |
|---------|---------|------:|--------:|------:|------:|------:|-------:|
| none | discretionary | +3.27% | +2.76% | -2.92% | 4.06 | 12 | 5 |
| macro | discretionary | +2.16% | +1.65% | -2.22% | 3.60 | 12 | 4 |

_Highest `vs strict` per setting = the most valuable context combo. Sub-noise deltas (Sig? = ·) are not trustworthy on one window — re-validate OOS._

_Paper-trading research only — not investment advice._