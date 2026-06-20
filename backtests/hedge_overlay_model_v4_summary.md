# Hedge overlay on model_v4 — up-shock + vol-surge 1-day hedge

Standalone overlay; **model_v4 is not modified**. Source panel: `model_v4_timeseries.csv` (2016-06-20 to 2026-06-18).

## Rule (configurable in `HedgeConfig`)

```
if  qqq_trl_1d >= +0.020            (up-shock)
AND z(spy_vol_trl_5d, 63d) >= 1.00     (vol-surge supporting signal)
then BUY soxs, sized INVERSE-VOL: weight = 0.50 * sigma_book / sigma_soxs
     (20d trailing vols, hedge $-vol targeted at 50% of book $-vol, cap 60% notional);
     avg fire-day weight ~ 14% of book.  Hold 1 day, exit next close (cost 10bp).
```

Key finding: **no single factor works alone** — a QQQ up-day by itself bounces; the edge is the *interaction* (up-shock while vol already elevated). Best supporting signal in the sensitivity sweep was 5-day realized-vol z (`spy_vol_trl_5d`).

## Window summary
```
FULL        days=2513 on= 68 ( 2.7%) | bookSh +1.24 hedSh +1.36 dSh +0.11 | bookDD -39.5% dDD -0.6% | onBook -0.44% SOXS+ 57% sleeve +26.85%
COVID       days=1561 on= 47 ( 3.0%) | bookSh +1.22 hedSh +1.26 dSh +0.04 | bookDD -39.5% dDD -0.6% | onBook 0.07% SOXS+ 51% sleeve +5.34%
TRAIN(<oos) days=1896 on= 52 ( 2.7%) | bookSh +1.18 hedSh +1.31 dSh +0.13 | bookDD -38.1% dDD +1.7% | onBook -0.58% SOXS+ 60% sleeve +21.62%
OOS         days= 617 on= 16 ( 2.6%) | bookSh +1.42 hedSh +1.50 dSh +0.08 | bookDD -39.5% dDD -0.6% | onBook -0.00% SOXS+ 50% sleeve +5.22%
```

## Yearly walk-forward
```
year   days   on |  bookSh   hedSh     dSh |  bookDD     dDD |  onBook%  paid%  sleeve%
2016    136    1 |   +2.73   +2.72   -0.01 |   -6.0%   +0.0% |    -0.17      0   -0.13%
2017    251    0 |   +1.82   +1.82   +0.00 |  -10.8%   +0.0% |       na     na   +0.00%
2018    251    8 |   +0.71   +0.80   +0.09 |  -28.9%   -0.1% |    -0.69     62   +2.14%
2019    252    4 |   +2.53   +2.64   +0.10 |  -10.1%   +1.6% |    -0.80     75   +1.47%
2020    253   11 |   +1.44   +1.99   +0.56 |  -33.8%  +10.8% |    -2.03     73  +17.21%
2021    252    7 |   +0.49   +0.58   +0.09 |  -21.6%   +1.7% |    -0.41     71   +2.41%
2022    251   16 |   -0.76   -0.82   -0.06 |  -31.8%   +0.4% |     0.15     50   -1.05%
2023    250    5 |   +2.23   +2.22   -0.01 |  -16.8%   -0.2% |     0.33     40   -0.43%
2024    252    6 |   +2.12   +2.20   +0.08 |  -20.4%   +2.1% |     0.60     67   +1.90%
2025    250    6 |   -0.15   -0.04   +0.11 |  -37.1%   -0.6% |    -0.44     50   +3.58%
2026    115    4 |   +3.01   +3.03   +0.02 |  -12.1%   +0.0% |    -0.24     25   -0.25%
```

Years with active hedge & ΔSharpe>0: **7/10**.

## Caveats

- Edge concentrates in genuine vol-spike episodes (2018–2021); marginal in calm years, slightly negative in the 2022 grind-bear. It is a Sharpe-adder + single-day-blow softener, **not** an all-time-max-drawdown reducer.

- Decide-at-close / fill-next-close; sized small. Re-validate after any model/universe change.
