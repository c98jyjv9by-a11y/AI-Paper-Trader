# Hedge overlay on model_v4 — up-shock + vol-surge 1-day hedge

Standalone overlay; **model_v4 is not modified**. Source panel: `model_v4_timeseries.csv` (2016-06-20 to 2026-06-18).

## Rule (configurable in `HedgeConfig`)

```
if  qqq_trl_1d >= +0.015            (up-shock)
AND z(spy_vol_trl_5d, 63d) >= 0.75     (vol-surge supporting signal)
then BUY soxs, sized INVERSE-VOL: weight = 0.50 * sigma_book / sigma_soxs
     (20d trailing vols, hedge $-vol targeted at 50% of book $-vol, cap 60% notional);
     avg fire-day weight ~ 14% of book.  Hold 1 day, exit next close (cost 10bp).
```

Key finding: **no single factor works alone** — a QQQ up-day by itself bounces; the edge is the *interaction* (up-shock while vol already elevated). Best supporting signal in the sensitivity sweep was 5-day realized-vol z (`spy_vol_trl_5d`).

## Window summary
```
FULL        days=2513 on=107 ( 4.3%) | bookSh +1.24 hedSh +1.39 dSh +0.15 | bookDD -39.5% dDD +0.6% | onBook -0.31% SOXS+ 57% sleeve +33.59%
COVID       days=1561 on= 72 ( 4.6%) | bookSh +1.22 hedSh +1.30 dSh +0.09 | bookDD -39.5% dDD +0.6% | onBook -0.13% SOXS+ 54% sleeve +12.48%
TRAIN(<oos) days=1896 on= 83 ( 4.4%) | bookSh +1.18 hedSh +1.34 dSh +0.16 | bookDD -38.1% dDD +5.7% | onBook -0.38% SOXS+ 58% sleeve +25.95%
OOS         days= 617 on= 24 ( 3.9%) | bookSh +1.42 hedSh +1.54 dSh +0.11 | bookDD -39.5% dDD +0.6% | onBook -0.05% SOXS+ 54% sleeve +7.64%
```

## Yearly walk-forward
```
year   days   on |  bookSh   hedSh     dSh |  bookDD     dDD |  onBook%  paid%  sleeve%
2016    136    1 |   +2.73   +2.72   -0.01 |   -6.0%   +0.0% |    -0.17      0   -0.13%
2017    251    1 |   +1.82   +1.81   -0.01 |  -10.8%   -0.0% |     0.33      0   -0.20%
2018    251   14 |   +0.71   +0.82   +0.11 |  -28.9%   -0.4% |    -0.01     57   +2.47%
2019    252    8 |   +2.53   +2.61   +0.07 |  -10.1%   +1.1% |    -0.39     62   +0.70%
2020    253   18 |   +1.44   +1.93   +0.49 |  -33.8%  +10.8% |    -1.03     61  +14.36%
2021    252   11 |   +0.49   +0.80   +0.31 |  -21.6%   +3.4% |    -0.90     73   +7.86%
2022    251   23 |   -0.76   -0.71   +0.05 |  -31.8%   +2.6% |    -0.19     57   +2.48%
2023    250    7 |   +2.23   +2.18   -0.05 |  -16.8%   -0.1% |     0.64     43   -1.60%
2024    252    9 |   +2.12   +2.18   +0.06 |  -20.4%   +2.1% |     1.13     56   +1.43%
2025    250   10 |   -0.15   +0.04   +0.19 |  -37.1%   +0.7% |    -0.83     60   +5.89%
2026    115    5 |   +3.01   +3.07   +0.06 |  -12.1%   +0.5% |    -0.61     40   +0.32%
```

Years with active hedge & ΔSharpe>0: **8/11**.

## Caveats

- Edge concentrates in genuine vol-spike episodes (2018–2021); marginal in calm years, slightly negative in the 2022 grind-bear. It is a Sharpe-adder + single-day-blow softener, **not** an all-time-max-drawdown reducer.

- Decide-at-close / fill-next-close; sized small. Re-validate after any model/universe change.
