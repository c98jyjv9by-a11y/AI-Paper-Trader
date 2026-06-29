# Options research strategy — planning notes

**Status:** research proposal only. **Nothing here is wired in.** The project's standing constraint is
**equities/ETFs, no options** (see `CLAUDE.md` Key constraints), so adopting any of this is a deliberate
scope change, not an incremental tweak. These notes scope *what to study* and *how to validate* before
any of that decision is on the table.

---

## 1. What we already have (the foundation these build on)

Two live research-strategy account families already run pure signal rules (no model_v4 entry/exit, no
overlay/hedge), driven close-to-close by the launchd agents:

**(A) Momentum top-rank — `score_rebalance`** (`monthly10`, `weekly10`, `combo20`)
- Rank the 83-name model_v4 universe by the **trailing 60-day average composite score**, hold the
  **top-10 equal-weight to 90% gross**, rebalance on the first trading day of the month / week.
- `combo20` is staggered: top-10 / 60d anchored to month-start + bottom-10 / 5d refreshed weekly.
- Edge: persistent momentum in semis/AI/tech. Backtests well close-to-close.

**(B) Z-score reversal — `zscore_reversal`** (`zscore10d_biweekly`, `zscore5d_weekly`, `zscore1d_daily`)
- Rank by the per-ticker **z-score of the composite vs its own 60-day baseline**, averaged over
  `avg_window` days; **buy the 10 LOWEST-z names** (most-fallen vs their own norm) equal-weight.
- **Regime filter:** to CASH when QQQ < its 200-day MA.
- `10d/biweekly` is the IC- and cost-validated winner (gross Sharpe ~1.3, net ~+34%/yr @ 10bp).

**The key cross-cutting insight (from `make_latency_edge.py`):** the momentum books decide on the
**close** and backtest frictionless close-to-close, but **live underperforms** — by the time the close
score is computed and you can buy, part of the predicted move (especially the **overnight** leg) has
already happened. The z-score books exist to attack exactly this signal-latency leak by trading the
freshest read. **Options are interesting precisely because they change the timing/convexity tradeoff of
how we express these same two signals.**

---

## 2. Why options at all (the thesis)

Three properties of options map onto specific weaknesses of the current books:

1. **Defined-risk convexity instead of linear leverage.** The `LevEtf` work already showed 3× ETFs add
   "leverage, not alpha" and *worsen tail risk* (worst-day −9%→−22% in `make_model_v4_reverse`; SQQQ
   tranches *hurt* in stress in `make_model_v4_defense`). Long options give convex upside with a
   **premium-capped** downside — structurally different from the inverse/3× ETFs we've already rejected.
2. **Timing tolerance.** A multi-week option captures multi-day drift, so a one-day-late entry costs a
   fraction of the move rather than (per the latency analysis) ~80% of it. Options may let us harvest the
   momentum/reversion edge *without* needing a perfect close-to-fill glue.
3. **IV monetization on the reversion side.** Names that just fell (the z-score book's buy list) have
   **spiked implied vol**. Selling that IV (short puts) is a second, orthogonal edge stacked on top of
   the mean-reversion directional bet.

---

## 3. Candidate strategies (ranked by fit / conviction)

### S1 — Cash-secured puts / put-credit spreads on the z-score reversal names ★ best fit
**Map:** the `zscore_reversal` book buys the 10 most-fallen-vs-own-norm names betting on reversion. A
fallen name has elevated IV → **sell a put** (cash-secured, or as a defined-risk put-credit spread) at/below
the current price on each of those 10 names, same regime gate (QQQ > 200d MA, else stay flat/CASH),
matched to the book's cadence (start with the validated **10d/biweekly**, ~2-week tenor).
- **Why it fits:** monetizes the IV spike *and* expresses the same "buy-the-dip" thesis. If assigned, you
  own the name the book wanted anyway, at a lower basis; if not, you keep premium. Two stacked edges.
- **Risks / caveats:** short-put tail risk in a regime break — the QQQ<200dMA filter is doing real work and
  must be honored; assignment/early-exercise mechanics; defined-risk spread variant trades premium for a
  capped loss (preferable for a first cut).

### S2 — Long calls / call-debit spreads as a stock replacement on the momentum top-rank names
**Map:** instead of (or alongside) buying the top-10 equal-weight, buy **ATM/slightly-ITM calls** (or
call-debit spreads to cut IV cost) on the top-N, sized to replicate the book's notional with far less
capital, freeing cash and capping downside at premium.
- **Why it fits:** momentum names have high expected drift; convexity + defined downside; the latency
  tolerance argument (§2.2) is strongest here since the momentum book is the one that bleeds live.
- **Variants:** deep-ITM, low-theta calls = a near-linear stock proxy with less capital (cleanest, lowest
  IV-decay drag); call-debit spreads = cheapest but cap upside (tension with model_v4's "let winners run").
- **Risks / caveats:** these names carry **rich IV** (expensive premium = drag), **theta** over the
  monthly hold, and **earnings IV crush**. Net edge is far from obvious — this must clear backtest before
  belief.

### S3 — Defined-risk put hedge replacing the SQQQ inverse-ETF overlay
**Map:** `make_model_v4_defense` found that defending with an **inverse ETF hurts** (SQQQ sells the bottom,
only 39% of fires win) and that the *only* thing that worked was **exposure reduction to cash**. A **long
QQQ/SPY put** is the third option: defined cost, positive convexity in a crash, no "sell the bottom"
behavior.
- **Why it fits:** directly tests the open question left by the defense study — is convex defined-risk
  insurance better than the cash de-risk governor? Applies to the model_v4 book, not the research books,
  but flows from the same research line.
- **Risks / caveats:** premium bleed in calm markets (the classic long-put cost); needs an entry rule so
  it isn't always-on. Compare head-to-head vs the cash governor on volatile windows.

### Rejected for now — covered calls on momentum "stayers"
Selling OTM calls on top-rank names held month-over-month harvests premium but **caps the upside on
momentum winners**, contradicting model_v4's core "let winners run / no take-profit" tenet. Don't pursue
unless framed as deliberate income-vs-growth tradeoff.

---

## 4. The hard part: feasibility & data (read before writing any code)

**This is the gating risk, not the strategy design.** The existing research stack is frictionless
close-to-close on a cached daily price/score panel. Options need fundamentally different inputs:

- **No historical options data in the repo, and yfinance only serves *current* chains** (no history). A
  real OOS backtest over 2018–2026 (required by our validation norm) is impossible from current sources.
  Two paths:
  1. **Model option prices** (Black–Scholes / Black-76) from the daily close + a **historical-vol or
     IV-proxy** input we *do* have/can derive. Cheap, fully reproducible, but only as good as the IV
     model — and IV ≠ realized vol, especially post-drop (the exact regime S1 trades). Document the bias.
  2. **Paid/licensed historical options data** (e.g. ORATS / historical chains). Accurate, costs money +
     new dependency.
  - Recommendation: start with **(1)** for *direction-of-effect* and sweep robustness; treat magnitudes as
     unreliable until cross-checked. This mirrors how `LevEtf`/sensitivity work is caveated as in-sample.
- **Greeks / IV-crush / earnings calendar** modeling needed for any honest call backtest (S2).
- **Live/paper execution:** Alpaca paper supports options, but the current `broker_sync` reconcile is
  equities-only — options would need real adapter work. **Do not scope live until the backtest earns it.**
- **Costs:** options spreads + per-contract commissions are much heavier than the 10bp equity assumption.
  Bake a conservative cost model in from day one (the latency study already shows how easily live erodes a
  paper edge).

---

## 5. Validation protocol (non-negotiable, per project norms)

Memory + CLAUDE.md are explicit: **sensitivity runs on a short bull window; validate any lead on
2018–2026 OOS before adopting** ([[validate-sensitivity-oos]]). And the cautionary precedent: the
`make_levetf_shock` strategy looked great 2018–2022 (Sharpe 1.2) and **lost 2022–2026 — it did not survive
OOS.** Apply the same bar here:

1. **Direction first:** does the option overlay beat the underlying equity book *gross* on the full
   2020–2026 span (z-books start 2020 per the 60-day z warm-up)?
2. **Train/test split** (e.g. 2020–22 vs 2023–26, as `make_weekly_60d_split` does) — reject anything that
   only works in one regime.
3. **Cost & IV-model sensitivity:** re-run under pessimistic spread/commission and an alternate IV
   assumption. An edge that dies under realistic friction is the latency leak in a new costume.
4. **Net Sharpe / MaxDD / worst-day vs the equity book** — convexity must show up as *better tails*, or
   the whole "options not 3× ETF" thesis fails.
5. Summarize findings in `CLAUDE.md` per the research convention; keep magnitudes flagged in-sample until
   step 3 passes.

---

## 6. Proposed research scripts (follow `research/` conventions)

All reuse `_common.load_ctx()` (`ROOT, cfg, px, close, S, Z`), run standalone, write PDFs to `reports/`:

| script (proposed) | what it would answer |
|---|---|
| `make_options_pricer.py` | shared BS/Black-76 pricer + IV-proxy from trailing realized vol; the dependency every other script imports. Validate against a few live yfinance chain quotes. |
| `make_zscore_putwrite.py` | **S1** — cash-secured-put / put-credit-spread backtest on the bottom-10 z names, 10d/biweekly, QQQ>200dMA gate; net vs the `zscore10d_biweekly` equity book. |
| `make_momentum_calls.py` | **S2** — ATM vs deep-ITM calls vs call-debit spreads as a replacement for the `monthly10`/`weekly10` book; sweep strike/tenor; IV-crush + earnings flagged. |
| `make_puthedge_defense.py` | **S3** — long QQQ/SPY put vs the cash de-risk governor vs SQQQ tranche on the model_v4 book (extends `make_model_v4_defense`). |
| `make_options_iv_sanity.py` | how well the modeled IV proxy tracks reality where chains exist — the credibility check for every magnitude above. |

---

## 7. Open questions / decision gates

- **Gate 0 (feasibility):** can `make_options_iv_sanity` show the modeled IV is good enough that the
  backtest means anything? If not, everything downstream is theater — stop or buy data.
- Strike/tenor selection rule for S1/S2 (fixed delta? fixed % OTM? matched to the rebalance cadence?).
- For S2, does convexity actually beat just holding the stock once rich IV + theta are paid? (Prior is
  *skeptical* — momentum names are expensive to be long via options.)
- For S1, is the put-credit-spread (defined risk) version's capped premium still worth it vs the naked
  cash-secured put's better capital efficiency under the regime filter?
- Scope discipline: keep all of this **research-only** behind the existing no-options constraint until a
  strategy clears §5. Don't let a promising in-sample number trigger live-execution scope creep.

**Suggested first step:** build `make_options_pricer.py` + `make_options_iv_sanity.py` (Gate 0), then
prototype **S1** (`make_zscore_putwrite.py`) — it's the highest-conviction fit because it stacks IV
monetization on a signal we've *already* validated.

---

## 8. S1 first results — `make_zscore_putwrite.py` (PROTOTYPE, modeled premiums)

Built S1 as a self-contained prototype: same validated signal (10d-avg z / bottom-10 / biweekly /
QQQ>200dMA → else cash), only the expression changes (stock long → short put). Premiums are
**BS-modeled** with an IV proxy = 20d realized vol × 1.15; option cost = 10% of premium. 2020+, MODELED.

| expression | gross ann / Sharpe | net ann / Sharpe | worst period |
|---|---|---|---|
| EQUITY (baseline book) | +38.3% / 1.32 | **+34.5% / 1.22** | −14.0% |
| CSP ATM | +29.4% / 1.86 | +20.0% / 1.36 | −10.9% |
| CSP 3% OTM | +22.8% / 1.86 | +16.7% / 1.43 | −9.8% |
| CSP 5% OTM | +18.4% / 1.80 | +13.9% / **1.43** | **−8.9%** |
| PCS 3% OTM / 5% wide | +231% / 1.77 | −31.8% / 0.30 | −68.4% |

**Reads:**
- **Harness is sound** — the EQUITY row reproduces the known `zscore10d_biweekly` book (~+34% net,
  Sharpe 1.22), so the date loop / signal / regime gate are wired right.
- **CSP delivers the expected put-write tradeoff:** *lower* absolute return (you cap the convex upside,
  keep premium) but materially *higher* risk-adjusted return (net Sharpe 1.36–1.43 vs 1.22) and *smaller*
  worst-period drawdown (−9% vs −14%). That is exactly the S1 thesis — and it shows up **even though** the
  realized-vol IV proxy likely *understates* true post-drop premium, so the real edge could be larger.
- **PCS as written is NOT credible** — return-on-margin (denominator = the 5% spread width) is
  leverage-inflated, and the crude both-legs premium-haircut cost dominates a tiny margin base → the
  −68% worst period and net collapse are artifacts of the sizing/cost convention, not a real finding.
  Needs a proper margin + per-contract-cost model before it means anything.

**Next steps to make S1 believable (in priority order):**
1. **Gate 0** — `make_options_iv_sanity.py`: check the realized-vol IV proxy vs a sample of live chains;
   re-run S1 with a skew/level-corrected IV. This is the dominant uncertainty.
2. **Train/test split** (2020–22 vs 2023–26) per §5 — confirm the CSP Sharpe lift survives OOS.
3. **Cost sensitivity** — sweep SPREAD_FRAC (5–20%) and add a per-contract \$ cost; the CSP edge must
   survive realistic option friction.
4. **Fix the PCS accounting** (real margin + commissions) before drawing any conclusion on defined-risk
   spreads; until then, the **cash-secured put is the credible S1 result.**
