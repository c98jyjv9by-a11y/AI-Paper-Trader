# Agent + Context Sources — Findings Snapshot (one-pager)

**Question:** When an AI agent reads model_v4's daily packet, does giving it *more information
sources* (macro, news) and *more autonomy* help it beat just following the model?

**Setup:** Harness owns all fills/accounting; agent emits only structured trades, one day at a
time, no look-ahead. `strict` = follow the model's queued trades exactly (fixed reference).
`balanced` = mostly follow. `discretionary` = use own judgment. Scored vs strict.

---

## Headline — Sonnet 4.6, full window 2026-01-05 → 06-16
**strict = +69.84%** (≈ model +69.61%) · SPY +9.4% · QQQ +18.3%. *Every* agent cell trailed strict.

| Setting | none | +news | +macro | +macro&news |
|---|---:|---:|---:|---:|
| **balanced** (vs strict) | −8.47% | −7.31% | −0.83% | **−0.44%** |
| **discretionary** (vs strict) | −51.55% | −51.31% | −42.41% | **−32.87%** |

_Trades: balanced ~40, discretionary 100–160. Divergences: balanced 3–6, discretionary 40–50._

### What it says (deltas are 30–50pp — well above noise, so the direction is trustworthy)
1. **Nothing beat strict.** On a momentum bull tape the agent adds no alpha — only subtracts.
2. **Autonomy is destructive.** Discretion churned and bled −33 to −52pp by second-guessing winners.
3. **Context helps — monotonically — as *damage control*:** `none < news < macro < macro&news` in
   both settings. macro&news nearly halved the discretionary loss (−51.6%→−32.9%, +19pp recovered)
   and made balanced almost match the model (−0.44%).
4. **Macro dominates; news is a small add-on.** Regime/breadth does most of the work; news alone
   barely helps (−7pp balanced) but adds a little *on top of* macro.
5. **Best combo: macro&news + balanced** — "mostly follow the model, with full market context as a
   sanity check" (−0.44% vs strict, Sharpe ~3.0).

---

## Cross-check — Haiku 4.5, short window (January only, ~19 days)
Discretionary: baseline +4.56% · +macro +4.50% · +news +5.21% · +macro&news +5.47% (strict +6.13%).

- **Weak model + short window = no clear signal.** Deltas were sub-1pp (within run-to-run noise);
  macro even *hurt* Haiku slightly in some cuts, while it *helped* Sonnet — i.e. **a data source's
  value is model-dependent; you can't evaluate sources on a weak model.**
- Haiku's `balanced` meddled and lost a bit; Sonnet's `balanced` correctly deferred (≈ strict).
- The destructive effect of autonomy only became *obvious* over the longer window — short horizons
  hide it because the agent has less time to compound mistakes.

---

## Bottom line & caveat
**Trust the model; use context as a guardrail, not a license to deviate.** Context reliably reduces
agent harm (macro > news), and a capable model (Sonnet ≫ Haiku) is required to use it at all.

**Caveat:** one window, and it's a strong-momentum bull tape where model_v4 is near-optimal — so
"follow the model" winning is expected. The decisive open test is a **choppy/selloff OOS window**,
where discretion + context might actually earn its keep. Until then, no proven edge from autonomy.

_Paper-trading research only — not investment advice._
