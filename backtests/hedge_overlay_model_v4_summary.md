# Hedge overlay on model_v4 — up-shock + vol-surge 1-day hedge

Standalone overlay; **model_v4 is not modified**. Source panel: `model_v4_timeseries.csv` (2016-06-20 to 2026-06-18).

## Rule (configurable in `HedgeConfig`)

```
if  qqq_trl_1d >= +0.020            (up-shock)
AND z(spy_vol_trl_5d, 63d) >= 1.00     (vol-surge supporting signal)
then BUY short_smh, sized INVERSE-VOL: weight = 0.50 * sigma_book / sigma_short_smh
     (20d trailing vols, hedge $-vol targeted at 50% of book $-vol, cap 60% notional);
     avg fire-day weight ~ 44% of book.  Hold 1 day, exit next close (cost 10bp).
```

Key finding: **no single factor works alone** — a QQQ up-day by itself bounces; the edge is the *interaction* (up-shock while vol already elevated). Best supporting signal in the sensitivity sweep was 5-day realized-vol z (`spy_vol_trl_5d`).

## Window summary
```
FULL        days=2513 on= 68 ( 2.7%) | bookSh +1.24 hedSh +1.35 dSh +0.11 | bookDD -39.5% dDD -0.6% | onBook -0.44% SOXS+ 56% sleeve +24.73%
COVID       days=1561 on= 47 ( 3.0%) | bookSh +1.22 hedSh +1.25 dSh +0.03 | bookDD -39.5% dDD -0.6% | onBook 0.07% SOXS+ 49% sleeve +3.21%
TRAIN(<oos) days=1896 on= 52 ( 2.7%) | bookSh +1.18 hedSh +1.30 dSh +0.13 | bookDD -38.1% dDD +1.4% | onBook -0.58% SOXS+ 60% sleeve +21.21%
OOS         days= 617 on= 16 ( 2.6%) | bookSh +1.42 hedSh +1.48 dSh +0.06 | bookDD -39.5% dDD -0.6% | onBook -0.00% SOXS+ 44% sleeve +3.51%
```

## Yearly walk-forward
```
year   days   on |  bookSh   hedSh     dSh |  bookDD     dDD |  onBook%  paid%  sleeve%
2016    136    1 |   +2.73   +2.72   -0.02 |   -6.0%   -0.0% |    -0.17      0   -0.16%
2017    251    0 |   +1.82   +1.82   +0.00 |  -10.8%   +0.0% |       na     na   +0.00%
2018    251    8 |   +0.71   +0.80   +0.09 |  -28.9%   -0.1% |    -0.69     62   +2.06%
2019    252    4 |   +2.53   +2.64   +0.10 |  -10.1%   +1.6% |    -0.80     75   +1.44%
2020    253   11 |   +1.44   +1.99   +0.55 |  -33.8%  +10.6% |    -2.03     73  +17.10%
2021    252    7 |   +0.49   +0.57   +0.08 |  -21.6%   +1.8% |    -0.41     71   +2.17%
2022    251   16 |   -0.76   -0.82   -0.05 |  -31.8%   +0.4% |     0.15     50   -0.94%
2023    250    5 |   +2.23   +2.22   -0.01 |  -16.8%   -0.3% |     0.33     40   -0.46%
2024    252    6 |   +2.12   +2.16   +0.04 |  -20.4%   +1.9% |     0.60     50   +0.49%
2025    250    6 |   -0.15   -0.04   +0.11 |  -37.1%   -0.4% |    -0.44     50   +3.45%
2026    115    4 |   +3.01   +3.02   +0.01 |  -12.1%   +0.0% |    -0.24     25   -0.43%
```

Years with active hedge & ΔSharpe>0: **7/10**.

## Caveats

- Edge concentrates in genuine vol-spike episodes (2018–2021); marginal in calm years, slightly negative in the 2022 grind-bear. It is a Sharpe-adder + single-day-blow softener, **not** an all-time-max-drawdown reducer.

- Decide-at-close / fill-next-close; sized small. Re-validate after any model/universe change.
