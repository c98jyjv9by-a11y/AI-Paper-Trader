# z-reversal WEEKLY books — OPEN vs CLOSE execution  (2026-06-29)

Signal + picks held fixed at the decision close; only the FILL point varies (decision close vs next-session open). Regime filter: cash when QQQ < 200-day MA. 2020+.


## zscore5d_weekly  (5d-avg z, weekly)
FILL    | GROSS ann / Sharpe  |  turn | NET ann @5bp/10bp      |   worst
------------------------------------------------------------------------------
CLOSE   |   +27.3% /  1.03     |   48% |    +24.2% /    +21.2%   | -16.5%
OPEN    |   +26.4% /  0.93     |   48% |    +23.4% /    +20.4%   | -19.5%
Δ O-C   |    -0.9% / -0.11     |      |            /     -0.9%   |

Annual gross return by year:
            2020    2021    2022    2023    2024    2025    2026
  CLOSE     +88%     +9%    -22%    +69%    +42%    +16%     +8%
  OPEN      +93%    +10%    -23%    +73%    +41%     +9%     +6%

## zscore10d_biweekly  (10d-avg z, biweekly)
FILL    | GROSS ann / Sharpe  |  turn | NET ann @5bp/10bp      |   worst
------------------------------------------------------------------------------
CLOSE   |   +38.3% /  1.32     |   54% |    +36.4% /    +34.5%   | -13.8%
OPEN    |   +40.0% /  1.27     |   54% |    +38.1% /    +36.1%   | -20.2%
Δ O-C   |    +1.7% / -0.05     |      |            /     +1.6%   |

Annual gross return by year:
            2020    2021    2022    2023    2024    2025    2026
  CLOSE    +126%    +46%    -24%    +49%    +38%    +32%    +20%
  OPEN     +126%    +52%    -27%    +56%    +43%    +31%    +19%

Δ O-C = OPEN minus CLOSE. Positive = open execution HELPS; negative = the decision-close fill (which live can't fully capture) was richer. Net uses round-trip turnover cost; turnover is identical across fills, so the gross gap drives the verdict.
