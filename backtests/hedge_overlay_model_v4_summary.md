# Hedge overlay on model_v4 — up-shock + vol-surge 1-day hedge

Standalone overlay; **model_v4 is not modified**. Source panel: `model_v4_timeseries.csv` (2016-06-20 to 2026-06-18).

## Rule (configurable in `HedgeConfig`)

```
SOFT gate (half size):  qqq_trl_1d >= +0.015  AND  z(spy_vol_trl_5d,63d) >= 0.75
HARD gate (full size):  qqq_trl_1d >= +0.020  AND  z(spy_vol_trl_5d,63d) >= 1.00
soft-only fires use 50% of the full inverse-vol size.
then BUY soxs, sized INVERSE-VOL: weight = 0.50 * sigma_book / sigma_soxs
     (20d trailing vols, hedge $-vol targeted at 50% of book $-vol, cap 60% notional);
     avg fire-day weight ~ 12% of book.  Hold 1 day, exit next close (cost 10bp).
```

Key finding: **no single factor works alone** — a QQQ up-day by itself bounces; the edge is the *interaction* (up-shock while vol already elevated). Best supporting signal in the sensitivity sweep was 5-day realized-vol z (`spy_vol_trl_5d`).

## Window summary
```
FULL        days=2513 on=107 ( 4.3%) | bookSh +1.24 hedSh +1.37 dSh +0.13 | bookDD -39.5% dDD +0.0% | onBook -0.31% SOXS+ 57% sleeve +30.22%
COVID       days=1561 on= 72 ( 4.6%) | bookSh +1.22 hedSh +1.28 dSh +0.07 | bookDD -39.5% dDD +0.0% | onBook -0.13% SOXS+ 54% sleeve +8.91%
TRAIN(<oos) days=1896 on= 83 ( 4.4%) | bookSh +1.18 hedSh +1.32 dSh +0.15 | bookDD -38.1% dDD +3.7% | onBook -0.38% SOXS+ 58% sleeve +23.79%
OOS         days= 617 on= 24 ( 3.9%) | bookSh +1.42 hedSh +1.52 dSh +0.09 | bookDD -39.5% dDD +0.0% | onBook -0.05% SOXS+ 54% sleeve +6.43%
```

## Yearly walk-forward
```
year   days   on |  bookSh   hedSh     dSh |  bookDD     dDD |  onBook%  paid%  sleeve%
2016    136    1 |   +2.73   +2.72   -0.01 |   -6.0%   +0.0% |    -0.17      0   -0.13%
2017    251    1 |   +1.82   +1.81   -0.01 |  -10.8%   +0.0% |     0.33      0   -0.10%
2018    251   14 |   +0.71   +0.81   +0.10 |  -28.9%   -0.2% |    -0.01     57   +2.30%
2019    252    8 |   +2.53   +2.62   +0.09 |  -10.1%   +1.4% |    -0.39     62   +1.08%
2020    253   18 |   +1.44   +1.96   +0.53 |  -33.8%  +10.8% |    -1.03     61  +15.79%
2021    252   11 |   +0.49   +0.69   +0.20 |  -21.6%   +2.5% |    -0.90     73   +5.14%
2022    251   23 |   -0.76   -0.77   -0.00 |  -31.8%   +1.5% |    -0.19     57   +0.72%
2023    250    7 |   +2.23   +2.20   -0.03 |  -16.8%   -0.2% |     0.64     43   -1.01%
2024    252    9 |   +2.12   +2.19   +0.07 |  -20.4%   +2.1% |     1.13     56   +1.66%
2025    250   10 |   -0.15   -0.00   +0.15 |  -37.1%   +0.1% |    -0.83     60   +4.73%
2026    115    5 |   +3.01   +3.05   +0.04 |  -12.1%   +0.3% |    -0.61     40   +0.03%
```

Years with active hedge & ΔSharpe>0: **7/11**.

## Caveats

- Edge concentrates in genuine vol-spike episodes (2018–2021); marginal in calm years, slightly negative in the 2022 grind-bear. It is a Sharpe-adder + single-day-blow softener, **not** an all-time-max-drawdown reducer.

- Decide-at-close / fill-next-close; sized small. Re-validate after any model/universe change.
