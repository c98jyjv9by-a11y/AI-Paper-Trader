# Hedge-overlay screen — model_v4 book + single-signal hedges (walk-forward + per-episode)
Window 2016-06-21 → 2026-06-18 · 9 yearly folds · hedge size 50% of book · cost 5bps/flip · hold-while-signal-true.

**Unhedged book** — ret +2156.0%, Sharpe +1.24, maxDD +39.5%.

**Auto-detected drawdown episodes (>10%):** 2017-12 (-10% book DD), 2018-02 (-11% book DD), 2018-12 (-28% book DD), 2019-10 (-9% book DD), 2020-03 (-33% book DD), 2020-09 (-11% book DD), 2022-10 (-38% book DD), 2023-10 (-17% book DD), 2024-02 (-6% book DD), 2024-04 (-11% book DD), 2024-08 (-20% book DD), 2025-04 (-37% book DD), 2026-06 (-11% book DD)

_wf_ = mean across yearly folds; wf_pos% = share of years the hedge reduced DD. ep_hit% = share of episodes the hedge made the drawdown shallower. vsRand = DD reduction beyond a random hedge at the same frequency (value of TIMING). giveup = full-sample return sacrificed (− = added)._

## Best by walk-forward risk-adjusted improvement (mean fold ΔSharpe)

| Signal | Hedge | on% | wf ΔSharpe | wf ΔMaxDD | wf pos% | ep hit% | ep ΔMaxDD | vsRand | giveup |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|
| vol>20 & qqq<50dma | long_PSQ | 12 | +0.00 | +2.6% | 44 | 38 | +1.8% | +2.9% | +97.1% |
| vol>20 & qqq<50dma | short_QQQ | 12 | -0.00 | +2.5% | 44 | 38 | +1.8% | +3.4% | +122.7% |
| vol>15 | long_PSQ | 34 | -0.02 | +4.2% | 67 | 54 | +2.9% | +5.2% | +513.3% |
| vol>20 | long_PSQ | 19 | -0.03 | +2.9% | 44 | 38 | +1.9% | +2.1% | +310.4% |
| vol>20 | short_QQQ | 19 | -0.04 | +2.8% | 44 | 38 | +1.9% | +3.3% | +344.2% |
| vol>20 & qqq<50dma | short_SMH | 12 | -0.04 | +2.3% | 44 | 38 | +1.7% | +3.4% | +278.8% |
| vol>15 | short_QQQ | 34 | -0.04 | +4.1% | 78 | 54 | +2.9% | +5.3% | +591.7% |
| vol>20 & spread20_neg | long_PSQ | 12 | -0.05 | +1.5% | 44 | 31 | +0.9% | +3.1% | +354.9% |
| vol>25 | long_PSQ | 10 | -0.05 | +1.9% | 44 | 31 | +1.3% | +3.2% | +323.3% |
| vol>20 & spread20_neg | short_SMH | 12 | -0.05 | +1.9% | 44 | 31 | +1.2% | +3.7% | +353.7% |
| vol>20 & spread20_neg | short_QQQ | 12 | -0.05 | +1.5% | 44 | 31 | +0.9% | +3.2% | +377.4% |
| qqq<50dma | long_PSQ | 27 | -0.05 | +3.3% | 67 | 62 | +2.1% | +5.4% | +505.6% |

## Best by per-episode hit-rate (then episode ΔMaxDD)

| Signal | Hedge | on% | wf ΔSharpe | wf ΔMaxDD | wf pos% | ep hit% | ep ΔMaxDD | vsRand | giveup |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|
| spread5_neg | long_PSQ | 52 | -0.15 | +2.9% | 89 | 92 | +2.6% | -0.4% | +1098.5% |
| losers_leading | long_PSQ | 50 | -0.27 | +1.4% | 67 | 92 | +1.4% | -5.8% | +1293.7% |
| losers_leading | short_SMH | 50 | -0.39 | +2.3% | 78 | 92 | +2.1% | -3.9% | +1597.9% |
| spread5_neg | short_QQQ | 52 | -0.19 | +2.8% | 89 | 92 | +2.5% | +2.2% | +1198.4% |
| losers_leading | short_QQQ | 50 | -0.31 | +1.1% | 67 | 85 | +1.3% | -5.7% | +1373.7% |
| dd60>5% | short_QQQ | 27 | -0.10 | +2.5% | 67 | 77 | +1.9% | +5.8% | +722.9% |
| spread5_neg | short_SMH | 52 | -0.25 | +3.6% | 78 | 77 | +3.6% | +4.0% | +1434.5% |
| dd60>5% | long_PSQ | 27 | -0.09 | +2.7% | 67 | 77 | +2.0% | +4.9% | +660.5% |
| dd60>5% | short_SMH | 27 | -0.25 | +1.9% | 56 | 62 | +1.4% | +5.0% | +1204.9% |
| losers_leading | long_SOXS | 50 | -1.05 | -7.8% | 22 | 62 | -2.1% | -2.2% | +2165.0% |
| qqq<50dma | long_PSQ | 27 | -0.05 | +3.3% | 67 | 62 | +2.1% | +5.4% | +505.6% |
| vol>15 | long_PSQ | 34 | -0.02 | +4.2% | 67 | 54 | +2.9% | +5.2% | +513.3% |
