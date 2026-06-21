# Archive — inactive model versions & one-off scripts

Nothing here is wired into the live system. **The active model is `model_v4`** (see
`config/scenarios/model_v4.yaml` and the "Active model & current state" section of `../CLAUDE.md`).
These files are kept only for lineage/reference.

## `scenarios/` — superseded model versions
Each is a self-contained scenario YAML (no inheritance — the loader does a direct
`config/scenarios/<name>.yaml` lookup, so files here are simply invisible to it).

| File | What it was |
|---|---|
| `model_v2.yaml` | Earlier momentum config (lower-vol book, vol target ~0.25). |
| `model_v3.yaml` | 83-name universe + score-conditional exits + persistence buy; vol target 0.35. **v4 was built directly on v3.** |
| `model_v5.yaml` | v4 **+ a fast shock overlay** (sizes down new buys after a volatile session). Experimental, never adopted. |
| `model_v6.yaml` | Iteration of the v5 shock-overlay idea. Experimental, never adopted. |

Note: v5/v6 are *newer* than v4 but were experiments that didn't beat v4 out-of-sample, so
v4 remains the production model. The validated volatility hedge lives separately as an overlay
(`src/hedge_overlay.py`), not as a model version.

## `scripts/`
| File | What it was |
|---|---|
| `derive_model_v2.py` | One-off script that derived the model_v2 parameters. Historical. |

## Reactivating one
Move it back to `config/scenarios/` (and, for a script, to the repo root):
```bash
git mv archive/scenarios/model_v3.yaml config/scenarios/model_v3.yaml
```
Then `python run.py scenario model_v3 --start … --end …`. Validate any change on the
2018–2026 out-of-sample window before adopting it (see the project's OOS-validation note).
