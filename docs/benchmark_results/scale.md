### Scale — cost as the portal grows

The four-task portal workload, 10 records per page, ours against the baseline. Wall-clock is hardware-dependent; page loads are not.

| Records per module | Ours: page loads | Baseline: page loads | Ours: s | Baseline: s | Ours: score | Baseline: score | Baseline: records read ÷ needed |
|---|---|---|---|---|---|---|---|
| 20 | 33 | 440 | 5.0 | 40.6 | 1.000 | 0.042 | 33.3× |
| 40 | 59 | 880 | 5.8 | 112.4 | 1.000 | 0.042 | 66.7× |
| 80 | 111 | 1760 | 23.7 | 310.1 | 1.000 | 0.042 | 133.3× |
| 160 | 215 | 3520 | 44.6 | 703.4 | 1.000 | 0.042 | 266.7× |
