# Hedge overlay on model_v4 — up-shock + vol-surge 1-day hedge

Standalone overlay; **model_v4 is not modified**. Source panel: `model_v4_timeseries.csv` (2016-06-20 to 2026-06-18).

## Rule (configurable in `HedgeConfig`)

```
if  qqq_trl_1d >= +0.020            (up-shock)
AND z(spy_vol_trl_5d, 63d) >= 1.00     (vol-surge supporting signal)
then BUY short_smh @ 30% notional for 1 day (round-trip cost 10bp), exit next close.
```

Key finding: **no single factor works alone** — a QQQ up-day by itself bounces; the edge is the *interaction* (up-shock while vol already elevated). Best supporting signal in the sensitivity sweep was 5-day realized-vol z (`spy_vol_trl_5d`).

## Window summary
```
FULL        days=2513 on= 68 ( 2.7%) | bookSh +1.24 hedSh +1.30 dSh +0.06 | bookDD -39.5% dDD -0.4% | onBook -0.44% SOXS+ 56% sleeve +11.91%
COVID       days=1561 on= 47 ( 3.0%) | bookSh +1.22 hedSh +1.23 dSh +0.01 | bookDD -39.5% dDD -0.4% | onBook 0.07% SOXS+ 49% sleeve +0.19%
TRAIN(<oos) days=1896 on= 52 ( 2.7%) | bookSh +1.18 hedSh +1.24 dSh +0.07 | bookDD -38.1% dDD +0.8% | onBook -0.58% SOXS+ 60% sleeve +10.17%
OOS         days= 617 on= 16 ( 2.6%) | bookSh +1.42 hedSh +1.46 dSh +0.03 | bookDD -39.5% dDD -0.4% | onBook -0.00% SOXS+ 44% sleeve +1.73%
```

## Yearly walk-forward
```
year   days   on |  bookSh   hedSh     dSh |  bookDD     dDD |  onBook%  paid%  sleeve%
2016    136    1 |   +2.73   +2.72   -0.02 |   -6.0%   -0.0% |    -0.17      0   -0.15%
2017    251    0 |   +1.82   +1.82   +0.00 |  -10.8%   +0.0% |       na     na   +0.00%
2018    251    8 |   +0.71   +0.73   +0.02 |  -28.9%   -0.7% |    -0.69     62   +0.29%
2019    252    4 |   +2.53   +2.60   +0.06 |  -10.1%   +1.2% |    -0.80     75   +0.73%
2020    253   11 |   +1.44   +1.77   +0.33 |  -33.8%   +6.7% |    -2.03     73  +10.01%
2021    252    7 |   +0.49   +0.53   +0.04 |  -21.6%   +1.2% |    -0.41     71   +1.16%
2022    251   16 |   -0.76   -0.82   -0.06 |  -31.8%   +0.1% |     0.15     50   -1.17%
2023    250    5 |   +2.23   +2.21   -0.02 |  -16.8%   -0.2% |     0.33     40   -0.69%
2024    252    6 |   +2.12   +2.14   +0.02 |  -20.4%   +1.5% |     0.60     50   +0.10%
2025    250    6 |   -0.15   -0.08   +0.07 |  -37.1%   -0.3% |    -0.44     50   +2.16%
2026    115    4 |   +3.01   +3.01   -0.00 |  -12.1%   +0.0% |    -0.24     25   -0.52%
```

Years with active hedge & ΔSharpe>0: **6/10**.

## Caveats

- Edge concentrates in genuine vol-spike episodes (2018–2021); marginal in calm years, slightly negative in the 2022 grind-bear. It is a Sharpe-adder + single-day-blow softener, **not** an all-time-max-drawdown reducer.

- Decide-at-close / fill-next-close; sized small. Re-validate after any model/universe change.
