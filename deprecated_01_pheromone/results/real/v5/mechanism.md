# Defense v5 mechanism check, seeds 201-210

Reported only, no value is picked. Source: `runs/v5_check/`, `tools/v5_mechanism.py`.
act_* counts calls where Count reaches confirm_k. sus_* counts every failure. Do not compare act_* with the legacy sus_cls numbers.

| d | arm | n | sus_src | sus_dec | act_src | act_dec | cone_abort | food | replay inexact |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | k1t10 | 10 | 11.90 | 0.00 | 11.90 | 0.00 | 27.60 | 68.40 | 0 |
| 0 | k2t10 | 10 | 13.80 | 0.00 | 1.80 | 0.00 | 3.70 | 75.70 | 0 |
| 2 | k1t10 | 10 | 4.80 | 36.60 | 4.80 | 36.60 | 103.30 | 44.90 | 0 |
| 2 | k2t10 | 10 | 6.30 | 56.50 | 0.30 | 18.80 | 48.30 | 42.40 | 0 |

Paired mean per seed, k2t10 minus k1t10:

| d | metric | mean difference |
| --- | --- | --- |
| 0 | act_cls_src | -10.10 |
| 2 | act_cls_dec | -17.80 |
