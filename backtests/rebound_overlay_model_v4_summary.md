# Rebound overlay on model_v4 — down-shock + momentum-crash 1-day TQQQ buy

Standalone overlay; **model_v4 is not modified**. Source panel: `model_v4_timeseries.csv` (2016-06-20 to 2026-06-18); TQQQ from prices.

## Rule (configurable in `ReboundConfig`)
```
FIRE (combo):  qqq_trl_1d <= -0.025  AND  spread_trl_1d < +0.00  AND  z(qqq_vol_trl_5d,63d) >= 0.25
then BUY TQQQ @ 50% of the held book for 1 day (round-trip 10bp), exit next close.
```

Key filter: **`spread_trl_1d < 0`** (the strategy's momentum signal inverting) selects the mean-reverting setups and skips trend-continuation sell-offs. Small, robust, tail-neutral.

## Window summary
```
FULL        days=2513 on= 34 ( 1.4%) | bookSh +1.24 rebSh +1.30 dSh +0.06 | bookDD -39.5% dDD +0.5% | TQQQ+ 65% sleeve +27.43%
COVID       days=1561 on= 19 ( 1.2%) | bookSh +1.22 rebSh +1.25 dSh +0.03 | bookDD -39.5% dDD +0.5% | TQQQ+ 58% sleeve +9.86%
TRAIN(<oos) days=1896 on= 26 ( 1.4%) | bookSh +1.18 rebSh +1.23 dSh +0.06 | bookDD -38.1% dDD -0.9% | TQQQ+ 65% sleeve +19.86%
OOS         days= 617 on=  8 ( 1.3%) | bookSh +1.42 rebSh +1.50 dSh +0.08 | bookDD -39.5% dDD +0.8% | TQQQ+ 62% sleeve +7.57%
```
## Yearly walk-forward
```
2016   on=0   dSh +0.00 sleeve +0.00%
2017   on=2   dSh -0.01 sleeve +0.26%
2018   on=6   dSh +0.36 sleeve +12.10%
2019   on=3   dSh +0.10 sleeve +3.26%
2020   on=9   dSh +0.05 sleeve +5.62%
2021   on=2   dSh +0.01 sleeve +0.21%
2022   on=4   dSh -0.04 sleeve -1.59%
2023   on=0   dSh +0.00 sleeve +0.00%
2024   on=2   dSh +0.01 sleeve +0.26%
2025   on=5   dSh +0.16 sleeve +5.16%
2026   on=1   dSh +0.09 sleeve +2.15%
```
- Decide-at-close / fill-next-close; sized small. Re-validate after any model/universe change.
