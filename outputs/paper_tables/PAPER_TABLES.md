# Tables of the paper, regenerated from outputs/tables


## Table I

| Property | Value |
|---|---|
| Windows | 9,390 |
| Recordings / reconstructed descriptor derived groups | 35 / 22 |
| Groups with no positive window | 6 |
| Groups containing both classes | 16 of 22 |
| Negative windows (st = 0) | 5,243 |
| Positive windows (st ≥ 1); prevalence | 4,147; 0.44 |
| Severity 1 / 2 / 3 windows | 2,656 / 670 / 821 |
| Groups with any severity 3 window | 7 |
| Positive episodes | 31 |
| Features, primary / full (Appendix A) | 76 / 99 |

## Table II

| Detector | Fold MCC ± 95% half width | Fold recall | Fold specificity | Fold alarm rate | Atime LPGO [95% CI] | Fold AUC ± 95% half width | Pooled MCC | Pooled alarm rate | False alarm rate, all 22 groups | Alarm, no sickness groups |
|---|---|---|---|---|---|---|---|---|---|---|
| RF | 0.448 ± 0.183 | 0.613 | 0.882 | 0.403 | 0.653 [0.513, 0.792] | 0.897 ± 0.091 | 0.316 | 0.338 | 0.141 | 0.248 |
| GB | 0.461 ± 0.182 | 0.624 | 0.893 | 0.398 | 0.621 [0.481, 0.765] | 0.872 ± 0.097 | 0.326 | 0.324 | 0.144 | 0.298 |
| RF+GB | 0.462 ± 0.185 | 0.622 | 0.895 | 0.395 | 0.640 [0.495, 0.788] | 0.891 ± 0.095 | 0.325 | 0.323 | 0.141 | 0.292 |
| LR | 0.197 ± 0.137 | 0.417 | 0.839 | 0.339 | 0.535 [0.432, 0.650] | 0.818 ± 0.102 | 0.148 | 0.375 | 0.189 | 0.342 |
| MLP | 0.288 ± 0.157 | 0.465 | 0.850 | 0.351 | 0.585 [0.484, 0.708] | 0.829 ± 0.109 | 0.221 | 0.318 | 0.152 | 0.152 |
| Clock (Atime: elapsed time) | 0.365 ± 0.171 | 0.552 | 0.869 | 0.400 | 0.530 [0.521, 0.544] | 0.866 ± 0.103 | 0.268 | 0.386 | 0.165 | 0.338 |

## Table III

| Detector | MCC | ΔMCC [95% CI] | t test p | Corrected p | Wilcoxon p | BH p | ΔAtime LPGO [95% CI] | Randomization p (BH) | ΔAtime pooled [95% CI] |
|---|---|---|---|---|---|---|---|---|---|
| RF | 0.448 | +0.083 [−0.063, 0.229] | 0.244 | 0.394 | 0.464 | 0.464 | +0.123 [−0.014, 0.260] | 0.045 (0.153) | +0.110 [−0.035, 0.239] |
| GB | 0.461 | +0.097 [−0.059, 0.252] | 0.204 | 0.353 | 0.464 | 0.464 | +0.091 [−0.046, 0.228] | 0.116 (0.194) | +0.088 [−0.052, 0.220] |
| RF+GB | 0.462 | +0.097 [−0.059, 0.254] | 0.204 | 0.352 | 0.464 | 0.464 | +0.110 [−0.030, 0.251] | 0.061 (0.153) | +0.105 [−0.046, 0.236] |
| LR | 0.197 | −0.167 [−0.366, 0.032] | 0.093 | 0.214 | 0.093 | 0.464 | +0.005 [−0.099, 0.117] | 0.455 (0.455) | −0.013 [−0.134, 0.105] |
| MLP | 0.288 | −0.076 [−0.169, 0.017] | 0.100 | 0.225 | 0.193 | 0.464 | +0.056 [−0.041, 0.172] | 0.169 (0.212) | +0.008 [−0.088, 0.123] |

## Table S24

| Detector | Primary rule alarm rate | Primary rule S3 missed | Matched 0.44 S3 missed | Matched 0.44 recall | Matched 0.44 specificity | Asev | Δ vs clock [95% CI] | Δ equal weights [95% CI] | Groups above clock |
|---|---|---|---|---|---|---|---|---|---|
| RF | 0.338 | 413 | 279 | 0.604 | 0.690 | 0.779 | +0.078 [−0.112, 0.311] | −0.084 [−0.291, 0.121] | 1 of 6 |
| GB | 0.324 | 420 | 330 | 0.609 | 0.694 | 0.813 | +0.112 [−0.098, 0.515] | +0.033 [−0.146, 0.267] | 2 of 6 |
| RF+GB | 0.323 | 421 | 305 | 0.619 | 0.702 | 0.800 | +0.099 [−0.057, 0.380] | −0.045 [−0.267, 0.185] | 1 of 6 |
| LR | 0.375 | 253 | 124 | 0.544 | 0.642 | 0.852 | +0.151 [−0.031, 0.472] | +0.062 [−0.104, 0.268] | 3 of 6 |
| MLP | 0.318 | 450 | 265 | 0.553 | 0.650 | 0.864 | +0.162 [−0.084, 0.516] | −0.012 [−0.217, 0.235] | 2 of 6 |
| Clock | 0.386 | 328 | 267 | 0.603 | 0.689 | 0.702 | — | — | — |

## Table IV

| Signal | δ | Fold MCC mean Δ | Fold MCC detected | Atime pooled mean Δ | Atime pooled detected | Atime pooled declared worse | Atime LPGO mean Δ | Atime LPGO detected | Atime LPGO detected, null threshold |
|---|---|---|---|---|---|---|---|---|---|
| state | 0 | 0.000 | 0.5% | −0.086 | 0% | 100% | −0.001 | 0% | 2.5% |
|  | 0.05 | 0.000 | 3.5% | −0.079 | 0% | 100% | +0.005 | 16% | 54% |
|  | 0.1 | +0.002 | 16% | −0.060 | 0% | 95% | +0.024 | 78% | 99% |
|  | 0.15 | +0.004 | 36% | −0.028 | 0% | 32% | +0.055 | 99% | 100% |
|  | 0.2 | +0.007 | 57% | +0.013 | 11% | 1.0% | +0.093 | 100% | 100% |
|  | 0.3 | +0.016 | 89% | +0.122 | 100% | 0% | +0.188 | 100% | 100% |
| trait | 0 | −0.011 | 0% | −0.078 | 1.5% | 36% | −0.019 | 5.0% | 2.5% |
|  | 0.5 | −0.010 | 0% | −0.049 | 4.5% | 28% | +0.007 | 7.0% | 4.0% |
|  | 1 | −0.004 | 0.5% | +0.013 | 8.5% | 15% | +0.061 | 15% | 11% |
|  | 1.5 | +0.005 | 1.0% | +0.090 | 24% | 3.0% | +0.128 | 38% | 33% |
|  | 2 | +0.007 | 0.5% | +0.131 | 43% | 0.5% | +0.162 | 56% | 49% |
|  | 3 | +0.022 | 0% | +0.154 | 47% | 0% | +0.178 | 60% | 58% |

## Table S2

| Group | Primary | Full |
|---|---|---|
| Trailing mean | 30 | 30 |
| Trailing standard deviation | 27 | 30 |
| First difference | 9 | 10 |
| Cumulative exposure | 2 | 2 |
| Elapsed time | 1 | 1 |
| Condition indicators | 7 | 7 |
| Descriptor indicators | 0 | 19 |
| Total | 76 | 99 |

## Table S5

| Family | Detector | Contrast | Estimate | Test | p | BH p (all) |
|---|---|---|---|---|---|---|
| Fold AUC (smoothed score) | RF | fold AUC minus clock | +0.031 | Wilcoxon | 0.753 | 0.820 |
| Fold AUC (smoothed score) | GB | fold AUC minus clock | +0.006 | Wilcoxon | 0.312 | 0.820 |
| Fold AUC (smoothed score) | RF+GB | fold AUC minus clock | +0.025 | Wilcoxon | 0.753 | 0.820 |
| Fold AUC (smoothed score) | LR | fold AUC minus clock | −0.048 | Wilcoxon | 0.392 | 0.820 |
| Fold AUC (smoothed score) | MLP | fold AUC minus clock | −0.036 | Wilcoxon | 0.676 | 0.820 |
| Smoothing window w = 1 | RF | fold MCC minus clock | +0.033 | Wilcoxon | 0.860 | 0.884 |
| Smoothing window w = 1 | GB | fold MCC minus clock | +0.026 | Wilcoxon | 0.597 | 0.820 |
| Smoothing window w = 1 | RF+GB | fold MCC minus clock | +0.030 | Wilcoxon | 0.597 | 0.820 |
| Smoothing window w = 1 | LR | fold MCC minus clock | −0.140 | Wilcoxon | 0.175 | 0.820 |
| Smoothing window w = 1 | MLP | fold MCC minus clock | −0.084 | Wilcoxon | 0.051 | 0.820 |
| Smoothing window w = 15 | RF | fold MCC minus clock | +0.047 | Wilcoxon | 0.632 | 0.820 |
| Smoothing window w = 15 | GB | fold MCC minus clock | +0.056 | Wilcoxon | 0.528 | 0.820 |
| Smoothing window w = 15 | RF+GB | fold MCC minus clock | +0.056 | Wilcoxon | 0.528 | 0.820 |
| Smoothing window w = 15 | LR | fold MCC minus clock | −0.161 | Wilcoxon | 0.130 | 0.820 |
| Smoothing window w = 15 | MLP | fold MCC minus clock | −0.067 | Wilcoxon | 0.175 | 0.820 |
| Smoothing window w = 31 | RF | fold MCC minus clock | +0.069 | Wilcoxon | 0.528 | 0.820 |
| Smoothing window w = 31 | GB | fold MCC minus clock | +0.076 | Wilcoxon | 0.464 | 0.820 |
| Smoothing window w = 31 | RF+GB | fold MCC minus clock | +0.072 | Wilcoxon | 0.495 | 0.820 |
| Smoothing window w = 31 | LR | fold MCC minus clock | −0.163 | Wilcoxon | 0.159 | 0.820 |
| Smoothing window w = 31 | MLP | fold MCC minus clock | −0.052 | Wilcoxon | 0.323 | 0.820 |
| Smoothing window w = 121 | RF | fold MCC minus clock | +0.033 | Wilcoxon | 0.860 | 0.884 |
| Smoothing window w = 121 | GB | fold MCC minus clock | +0.077 | Wilcoxon | 0.562 | 0.820 |
| Smoothing window w = 121 | RF+GB | fold MCC minus clock | +0.065 | Wilcoxon | 0.632 | 0.820 |
| Smoothing window w = 121 | LR | fold MCC minus clock | −0.120 | Wilcoxon | 0.375 | 0.820 |
| Smoothing window w = 121 | MLP | fold MCC minus clock | −0.048 | Wilcoxon | 0.256 | 0.820 |
| Smoothing window w = 201 | RF | fold MCC minus clock | +0.018 | Wilcoxon | 0.860 | 0.884 |
| Smoothing window w = 201 | GB | fold MCC minus clock | +0.087 | Wilcoxon | 0.274 | 0.820 |
| Smoothing window w = 201 | RF+GB | fold MCC minus clock | +0.056 | Wilcoxon | 0.669 | 0.820 |
| Smoothing window w = 201 | LR | fold MCC minus clock | −0.075 | Wilcoxon | 0.562 | 0.820 |
| Smoothing window w = 201 | MLP | fold MCC minus clock | −0.053 | Wilcoxon | 0.632 | 0.820 |
| w chosen on validation groups | RF | fold MCC minus clock | +0.006 | Wilcoxon | 0.900 | 0.900 |
| w chosen on validation groups | GB | fold MCC minus clock | +0.041 | Wilcoxon | 0.900 | 0.900 |
| w chosen on validation groups | RF+GB | fold MCC minus clock | +0.023 | Wilcoxon | 0.860 | 0.884 |
| w chosen on validation groups | LR | fold MCC minus clock | −0.163 | Wilcoxon | 0.044 | 0.820 |
| w chosen on validation groups | MLP | fold MCC minus clock | −0.035 | Wilcoxon | 0.433 | 0.820 |
| Training seed 1 | RF | fold MCC minus clock | +0.069 | Wilcoxon | 0.464 | 0.820 |
| Training seed 1 | RF+GB | fold MCC minus clock | +0.093 | Wilcoxon | 0.433 | 0.820 |
| Training seed 1 | MLP | fold MCC minus clock | +0.005 | Wilcoxon | 0.669 | 0.820 |
| Training seed 2 | RF | fold MCC minus clock | +0.078 | Wilcoxon | 0.375 | 0.820 |
| Training seed 2 | RF+GB | fold MCC minus clock | +0.092 | Wilcoxon | 0.464 | 0.820 |
| Training seed 2 | MLP | fold MCC minus clock | −0.061 | Wilcoxon | 0.105 | 0.820 |
| 99 features (descriptors included) | RF | fold MCC minus clock | +0.071 | Wilcoxon | 0.495 | 0.820 |
| 99 features (descriptors included) | GB | fold MCC minus clock | +0.035 | Wilcoxon | 0.744 | 0.820 |
| 99 features (descriptors included) | RF+GB | fold MCC minus clock | +0.042 | Wilcoxon | 0.744 | 0.820 |
| 99 features (descriptors included) | LR | fold MCC minus clock | −0.035 | Wilcoxon | 0.706 | 0.820 |
| 99 features (descriptors included) | MLP | fold MCC minus clock | 0.000 | Wilcoxon | 0.632 | 0.820 |
| Leave one recording out | RF | fold MCC minus clock | −0.013 | Wilcoxon | 0.732 | 0.820 |
| Leave one recording out | GB | fold MCC minus clock | −0.044 | Wilcoxon | 0.407 | 0.820 |
| Leave one recording out | RF+GB | fold MCC minus clock | −0.039 | Wilcoxon | 0.493 | 0.820 |
| Leave one recording out | LR | fold MCC minus clock | −0.111 | Wilcoxon | 0.290 | 0.820 |
| Leave one recording out | MLP | fold MCC minus clock | −0.040 | Wilcoxon | 0.458 | 0.820 |
| Merged grouping (20 groups) | RF | fold MCC minus clock | +0.079 | Wilcoxon | 0.528 | 0.820 |
| Merged grouping (20 groups) | GB | fold MCC minus clock | +0.093 | Wilcoxon | 0.495 | 0.820 |
| Merged grouping (20 groups) | RF+GB | fold MCC minus clock | +0.094 | Wilcoxon | 0.495 | 0.820 |
| Merged grouping (20 groups) | LR | fold MCC minus clock | −0.169 | Wilcoxon | 0.093 | 0.820 |
| Merged grouping (20 groups) | MLP | fold MCC minus clock | −0.089 | Wilcoxon | 0.093 | 0.820 |
| Episode recall, primary rule | RF | observed minus shifted alarms | +0.029 | circular shift, one sided | 0.376 | 0.820 |
| Episode recall, primary rule | GB | observed minus shifted alarms | +0.037 | circular shift, one sided | 0.300 | 0.820 |
| Episode recall, primary rule | RF+GB | observed minus shifted alarms | +0.038 | circular shift, one sided | 0.266 | 0.820 |
| Episode recall, primary rule | LR | observed minus shifted alarms | +0.008 | circular shift, one sided | 0.560 | 0.820 |
| Episode recall, primary rule | MLP | observed minus shifted alarms | +0.098 | circular shift, one sided | 0.040 | 0.820 |
| Episode recall, primary rule | Clock | observed minus shifted alarms | +0.042 | circular shift, one sided | 0.310 | 0.820 |
| Episode recall, matched alarm rate 0.44 | RF | observed minus shifted alarms | +0.054 | circular shift, one sided | 0.210 | 0.820 |
| Episode recall, matched alarm rate 0.44 | GB | observed minus shifted alarms | −0.007 | circular shift, one sided | 0.720 | 0.820 |
| Episode recall, matched alarm rate 0.44 | RF+GB | observed minus shifted alarms | +0.033 | circular shift, one sided | 0.358 | 0.820 |
| Episode recall, matched alarm rate 0.44 | LR | observed minus shifted alarms | +0.002 | circular shift, one sided | 0.636 | 0.820 |
| Episode recall, matched alarm rate 0.44 | MLP | observed minus shifted alarms | +0.058 | circular shift, one sided | 0.186 | 0.820 |
| Episode recall, matched alarm rate 0.44 | Clock | observed minus shifted alarms | +0.008 | circular shift, one sided | 0.548 | 0.820 |
| Within group severity ranking | RF | severity ranking minus clock | +0.078 | group bootstrap, two sided | 0.652 | 0.820 |
| Within group severity ranking | GB | severity ranking minus clock | +0.112 | group bootstrap, two sided | 0.640 | 0.820 |
| Within group severity ranking | RF+GB | severity ranking minus clock | +0.099 | group bootstrap, two sided | 0.652 | 0.820 |
| Within group severity ranking | LR | severity ranking minus clock | +0.151 | group bootstrap, two sided | 0.517 | 0.820 |
| Within group severity ranking | MLP | severity ranking minus clock | +0.162 | group bootstrap, two sided | 0.633 | 0.820 |

## Table S15

| Analysis | Detector | Fold MCC ± 95% half width | Fold recall | Pooled MCC | Pooled alarm rate | False alarm rate, all units | Alarm, no sickness groups | S3 missed (of 821) |
|---|---|---|---|---|---|---|---|---|
| 99 features (descriptors included), LOGO | RF | 0.435 ± 0.179 | 0.597 | 0.311 | 0.307 | 0.146 | 0.261 | 412 |
|  | GB | 0.400 ± 0.185 | 0.562 | 0.272 | 0.321 | 0.162 | 0.306 | 451 |
|  | RF+GB | 0.407 ± 0.183 | 0.568 | 0.280 | 0.319 | 0.159 | 0.300 | 431 |
|  | LR | 0.330 ± 0.139 | 0.489 | 0.176 | 0.349 | 0.319 | 0.677 | 370 |
|  | MLP * | 0.365 ± 0.142 | 0.551 | 0.282 | 0.297 | 0.125 | 0.126 | 436 |
| 76 features, leave one recording out | RF | 0.338 ± 0.139 | 0.515 | 0.317 | 0.335 | 0.120 | 0.248 | 471 |
|  | GB | 0.307 ± 0.152 | 0.520 | 0.255 | 0.369 | 0.159 | 0.298 | 426 |
|  | RF+GB | 0.312 ± 0.151 | 0.522 | 0.260 | 0.366 | 0.156 | 0.292 | 428 |
|  | LR | 0.240 ± 0.108 | 0.479 | 0.183 | 0.378 | 0.203 | 0.342 | 246 |
|  | MLP | 0.311 ± 0.139 | 0.515 | 0.238 | 0.348 | 0.179 | 0.152 | 345 |
|  | Clock | 0.351 ± 0.146 | 0.560 | 0.266 | 0.386 | 0.154 | 0.338 | 330 |

## Table S22

| Detector | PPV π=0.44 | PPV π=0.10 | PPV π=0.01 | NPV π=0.44 | NPV π=0.10 | NPV π=0.01 | FA per 1,000 negatives | Alarm onsets per recording |
|---|---|---|---|---|---|---|---|---|
| RF | 0.660 | 0.215 | 0.024 | 0.672 | 0.935 | 0.994 | 205 | 0.69 |
| GB | 0.674 | 0.226 | 0.026 | 0.672 | 0.935 | 0.994 | 189 | 0.66 |
| RF+GB | 0.674 | 0.226 | 0.026 | 0.671 | 0.935 | 0.994 | 188 | 0.60 |
| LR | 0.535 | 0.140 | 0.015 | 0.617 | 0.919 | 0.992 | 312 | 0.86 |
| MLP | 0.601 | 0.175 | 0.019 | 0.635 | 0.925 | 0.993 | 227 | 1.03 |
| Clock | 0.608 | 0.180 | 0.020 | 0.665 | 0.934 | 0.994 | 270 | 0.86 |

## Table S23

| Detector | Posterior = 1 share | π=0.10 alarm | π=0.10 recall | π=0.10 no alarm groups | π=0.01 alarm | π=0.01 recall | π=0.01 no alarm groups |
|---|---|---|---|---|---|---|---|
| RF | 0.175 | 0.176 | 0.244 | 12 | 0.175 | 0.242 | 12 |
| GB | 0.165 | 0.174 | 0.216 | 12 | 0.165 | 0.216 | 12 |
| RF+GB | 0.176 | 0.183 | 0.233 | 11 | 0.177 | 0.232 | 11 |
| LR | 0.109 | 0.114 | 0.157 | 14 | 0.109 | 0.153 | 14 |
| MLP | 0.144 | 0.144 | 0.200 | 14 | 0.144 | 0.199 | 14 |
| Clock | 0.056 | 0.056 | 0.055 | 14 | 0.056 | 0.055 | 14 |

## Table S3

| Detector | Primary alarm | Primary episode recall | Primary shifted | Primary latency (s) | Primary pre onset | Matched episode recall | Matched shifted | Matched latency (s) | Matched pre onset |
|---|---|---|---|---|---|---|---|---|---|
| RF | 0.338 | 0.613 | 0.584 | 41.0 | 0.161 | 0.742 | 0.687 | 13.0 | 0.323 |
| GB | 0.324 | 0.548 | 0.511 | 28.0 | 0.226 | 0.581 | 0.588 | 0.0 | 0.355 |
| RF+GB | 0.323 | 0.548 | 0.510 | 31.0 | 0.194 | 0.677 | 0.645 | 3.0 | 0.323 |
| LR | 0.375 | 0.677 | 0.670 | 54.0 | 0.226 | 0.742 | 0.740 | 25.0 | 0.258 |
| MLP | 0.318 | 0.774 | 0.676 | 18.0 | 0.290 | 0.806 | 0.749 | 15.0 | 0.387 |
| Clock | 0.386 | 0.774 | 0.732 | 68.5 | 0.226 | 0.774 | 0.766 | 51.5 | 0.226 |

## Table S25

| Group | Recordings | Pairs | RF | GB | RF+GB | LR | MLP | Clock |
|---|---|---|---|---|---|---|---|---|
| 10 | 3 | 28,812 | 0.752 | 0.965 | 0.824 | 0.922 | 0.977 | 0.403 |
| 11 | 2 | 1,848 | 0.214 | 0.545 | 0.346 | 0.214 | 0.123 | 0.452 |
| 12 | 1 | 5,856 | 0.824 | 0.866 | 0.860 | 0.978 | 0.918 | 0.909 |
| 14 | 6 | 53,940 | 0.803 | 0.732 | 0.792 | 0.819 | 0.822 | 0.836 |
| 17 | 1 | 3,393 | 0.876 | 0.876 | 0.876 | 0.916 | 0.876 | 0.876 |
| 19 | 1 | 110 | 0.500 | 0.691 | 0.509 | 1.000 | 0.691 | 1.000 |

## Table S18

| Signal | δ | Replicates | Detected, MCC Wilcoxon | Detected, MCC t test | Mean Δ fold AUC | Mean Atime pooled | Mean Atime LPGO | Below reference, pooled | Below reference, LPGO |
|---|---|---|---|---|---|---|---|---|---|
| state | 0 | 200 | 1.0% | 0.5% | 0.000 | 0.444 | 0.528 | 100% | 5.0% |
| state | 0.05 | 200 | 3.0% | 3.5% | 0.000 | 0.451 | 0.535 | 100% | 0% |
| state | 0.1 | 200 | 18% | 16% | −0.001 | 0.470 | 0.554 | 95% | 0% |
| state | 0.15 | 200 | 39% | 36% | 0.000 | 0.502 | 0.584 | 32% | 0% |
| state | 0.2 | 200 | 61% | 57% | 0.000 | 0.543 | 0.622 | 1.0% | 0% |
| state | 0.3 | 200 | 90% | 89% | +0.003 | 0.651 | 0.718 | 0% | 0% |
| trait | 0 | 200 | 0% | 0% | −0.005 | 0.452 | 0.511 | 36% | 30% |
| trait | 0.5 | 200 | 0% | 0% | −0.003 | 0.481 | 0.537 | 28% | 26% |
| trait | 1 | 200 | 1.5% | 0.5% | −0.001 | 0.543 | 0.591 | 15% | 13% |
| trait | 1.5 | 200 | 1.0% | 1.0% | +0.007 | 0.620 | 0.658 | 3.0% | 2.5% |
| trait | 2 | 200 | 0.5% | 0.5% | +0.010 | 0.661 | 0.692 | 0.5% | 0.5% |
| trait | 3 | 200 | 0% | 0% | +0.018 | 0.683 | 0.708 | 0% | 0% |

## Table S10

| Detector | ΔMCC | 95% CI | 95% CI, corrected | MDD | MDD, corrected | Groups for 0.10 | Groups for 0.10, corrected |
|---|---|---|---|---|---|---|---|
| RF | +0.083 | [−0.063, 0.229] | [−0.119, 0.284] | 0.205 | 0.283 | 61 | 115 |
| GB | +0.097 | [−0.059, 0.252] | [−0.118, 0.311] | 0.218 | 0.302 | 69 | 130 |
| RF+GB | +0.097 | [−0.059, 0.254] | [−0.119, 0.314] | 0.220 | 0.304 | 70 | 132 |
| LR | −0.167 | [−0.366, 0.032] | [−0.442, 0.108] | 0.280 | 0.387 | 112 | 211 |
| MLP | −0.076 | [−0.169, 0.017] | [−0.204, 0.052] | 0.130 | 0.180 | 26 | 48 |

## Table S6

| Threshold | w | RF | GB | RF+GB | LR | MLP | Clock fold MCC | Clock alarm rate |
|---|---|---|---|---|---|---|---|---|
| 0.3 | 1 | −0.021 | −0.013 | −0.008 | −0.078 | −0.061 | 0.442 | 0.795 |
| 0.3 | 15 | −0.008 | −0.014 | −0.008 | −0.088 | −0.062 | 0.447 | 0.770 |
| 0.3 | 31 | −0.005 | −0.013 | −0.002 | −0.112 | −0.051 | 0.455 | 0.742 |
| 0.3 | 61 | +0.013 | −0.012 | −0.004 | −0.154 | −0.029 | 0.461 | 0.690 |
| 0.3 | 121 | +0.001 | −0.006 | +0.003 | −0.142 | −0.030 | 0.448 | 0.612 |
| 0.3 | 201 | −0.020 | −0.028 | −0.007 | −0.171 | −0.075 | 0.448 | 0.612 |
| 0.4 | 1 | −0.032 | −0.019 | −0.018 | −0.131 | −0.100 | 0.450 | 0.624 |
| 0.4 | 15 | −0.015 | 0.000 | −0.002 | −0.136 | −0.069 | 0.443 | 0.601 |
| 0.4 | 31 | −0.003 | +0.013 | +0.009 | −0.165 | −0.033 | 0.439 | 0.576 |
| 0.4 | 61 | +0.017 | +0.027 | +0.019 | −0.178 | −0.043 | 0.427 | 0.529 |
| 0.4 | 121 | +0.058 | +0.039 | +0.042 | −0.160 | −0.028 | 0.384 | 0.435 |
| 0.4 | 201 | +0.026 | +0.029 | +0.023 | −0.128 | −0.047 | 0.334 | 0.314 |
| 0.5 | 1 | +0.033 | +0.026 | +0.030 | −0.140 | −0.084 | 0.401 | 0.481 |
| 0.5 | 15 | +0.047 | +0.056 | +0.056 | −0.161 | −0.067 | 0.391 | 0.459 |
| 0.5 | 31 | +0.069 | +0.076 | +0.072 | −0.163 | −0.052 | 0.383 | 0.434 |
| 0.5 | 61 (primary rule) | +0.083 | +0.097 | +0.097 | −0.167 | −0.076 | 0.365 | 0.386 |
| 0.5 | 121 | +0.033 | +0.077 | +0.065 | −0.120 | −0.048 | 0.319 | 0.290 |
| 0.5 | 201 | +0.018 | +0.087 | +0.056 | −0.075 | −0.053 | 0.234 | 0.162 |
| 0.6 | 1 | +0.031 | +0.085 | +0.087 | −0.128 | −0.074 | 0.344 | 0.339 |
| 0.6 | 15 | +0.055 | +0.116 | +0.109 | −0.121 | −0.052 | 0.329 | 0.317 |
| 0.6 | 31 | +0.051 | +0.145 | +0.143 | −0.114 | −0.033 | 0.316 | 0.291 |
| 0.6 | 61 | +0.025 | +0.162 | +0.149 | −0.094 | −0.028 | 0.289 | 0.242 |
| 0.6 | 121 | +0.038 | +0.146 | +0.124 | −0.032 | −0.018 | 0.217 | 0.144 |
| 0.6 | 201 | +0.076 | +0.186 | +0.141 | +0.091 | +0.047 | 0.065 | 0.015 |
| 0.7 | 1 | −0.013 | +0.186 | +0.147 | −0.027 | −0.009 | 0.240 | 0.185 |
| 0.7 | 15 | +0.008 | +0.220 | +0.156 | −0.025 | −0.006 | 0.223 | 0.162 |
| 0.7 | 31 | +0.024 | +0.258 | +0.181 | −0.001 | +0.010 | 0.204 | 0.136 |
| 0.7 | 61 | +0.056 | +0.274 | +0.201 | +0.047 | +0.026 | 0.161 | 0.089 |
| 0.7 | 121 | +0.148 | +0.342 | +0.290 | +0.146 | +0.098 | 0.004 | 0.002 |
| 0.7 | 201 | +0.053 | +0.199 | +0.140 | +0.118 | +0.046 | 0.000 | 0.000 |

## Table S4

| Model or contrast | Full | Within group | Between group |
|---|---|---|---|
| RF | +0.123 [−0.014, 0.260] | +0.035 [−0.205, 0.414] | +0.127 [−0.005, 0.259] |
| GB | +0.091 [−0.046, 0.228] | −0.055 [−0.298, 0.382] | +0.098 [−0.018, 0.228] |
| RF+GB | +0.110 [−0.030, 0.251] | −0.011 [−0.278, 0.410] | +0.116 [−0.012, 0.249] |
| LR | +0.005 [−0.099, 0.117] | +0.032 [−0.185, 0.283] | +0.004 [−0.104, 0.111] |
| MLP | +0.056 [−0.041, 0.172] | −0.002 [−0.087, 0.229] | +0.058 [−0.040, 0.179] |
| RF time only | −0.070 [−0.172, 0.034] | −0.155 [−0.343, 0.073] | −0.066 [−0.161, 0.037] |
| GB time only | +0.006 [−0.015, 0.025] | −0.044 [−0.083, −0.015] | +0.008 [−0.013, 0.029] |
| RF minus RF on elapsed time only | +0.193 [0.036, 0.359] | +0.190 [0.003, 0.736] | +0.194 [0.020, 0.354] |
| GB minus GB on elapsed time only | +0.086 [−0.044, 0.221] | −0.011 [−0.260, 0.445] | +0.090 [−0.032, 0.214] |

## Table S14

| Setting | RF | GB | RF+GB | LR | MLP |
|---|---|---|---|---|---|
| 15 s bins, at least 10 | +0.132 | +0.101 | +0.118 | +0.012 | +0.063 |
| 15 s bins, at least 20 | +0.132 | +0.101 | +0.118 | +0.012 | +0.063 |
| 15 s bins, at least 40 | +0.134 | +0.103 | +0.120 | +0.015 | +0.066 |
| 30 s bins, at least 10 | +0.123 | +0.091 | +0.110 | +0.005 | +0.056 |
| 30 s bins, at least 20 (primary) | +0.123 | +0.091 | +0.110 | +0.005 | +0.056 |
| 30 s bins, at least 40 | +0.123 | +0.091 | +0.110 | +0.005 | +0.056 |
| 60 s bins, at least 10 | +0.100 | +0.068 | +0.088 | −0.011 | +0.035 |
| 60 s bins, at least 20 | +0.100 | +0.068 | +0.088 | −0.011 | +0.035 |
| 60 s bins, at least 40 | +0.100 | +0.068 | +0.088 | −0.011 | +0.035 |
| LORO, pooled | +0.103 | +0.055 | +0.081 | −0.011 | −0.002 |
| LORO, within unit | −0.034 | −0.268 | −0.132 | −0.232 | −0.169 |
| Merged grouping, pooled | +0.110 | +0.085 | +0.104 | −0.016 | +0.004 |
| Merged grouping, within unit | +0.035 | −0.055 | −0.011 | +0.032 | −0.002 |

## Table S12

| Model | Fold MCC | ΔMCC | Wilcoxon p | ΔAtime LPGO [95% CI] | Within | Between |
|---|---|---|---|---|---|---|
| RF | 0.448 | +0.083 | 0.464 | +0.124 [−0.012, 0.262] | +0.033 | +0.129 |
| GB | 0.461 | +0.097 | 0.464 | +0.091 [−0.046, 0.228] | −0.055 | +0.098 |
| RF+GB | 0.463 | +0.098 | 0.464 | +0.110 [−0.031, 0.252] | −0.014 | +0.116 |
| LR | 0.197 | −0.168 | 0.093 | +0.005 [−0.099, 0.117] | +0.031 | +0.004 |
| RF no scenario | 0.446 | +0.081 | 0.427 | +0.114 [−0.024, 0.255] | +0.038 | +0.117 |
| GB no scenario | 0.457 | +0.092 | 0.348 | +0.090 [−0.046, 0.228] | −0.047 | +0.096 |
| RF+GB no scenario | 0.455 | +0.090 | 0.404 | +0.102 [−0.040, 0.247] | −0.013 | +0.107 |
| LR no scenario | 0.208 | −0.157 | 0.117 | +0.012 [−0.091, 0.127] | +0.033 | +0.011 |
| LR time and scenario | 0.363 | −0.001 | 0.980 | −0.054 [−0.158, 0.060] | +0.134 | −0.063 |
| GB time and scenario | 0.396 | +0.032 | 0.252 | +0.006 [−0.059, 0.072] | +0.064 | +0.003 |

## Table S8

| Learner | Signal | δ | Replicates | Mean ΔAtime LPGO | Detected | Below | Detected, null threshold | MCC t test |
|---|---|---|---|---|---|---|---|---|
| GB | state, AR(1) noise | 0 | 100 | −0.016 | 6% | 17% | 3% | 3% |
| GB | state, AR(1) noise | 0.1 | 50 | −0.021 | 2% | 18% | 2% | 6% |
| GB | state, AR(1) noise | 0.25 | 50 | +0.028 | 22% | 4% | 12% | 8% |
| GB | state, AR(1) noise | 0.5 | 50 | +0.132 | 92% | 0% | 78% | 24% |
| GB | trait | 0 | 100 | −0.033 | 5% | 20% | 3% | 0% |
| GB | trait | 1 | 50 | +0.014 | 14% | 8% | 4% | 0% |
| GB | trait | 2 | 50 | +0.072 | 22% | 4% | 22% | 0% |
| GB | trait | 3 | 50 | +0.139 | 48% | 0% | 42% | 0% |
| LR | state, AR(1) noise | 0 | 100 | −0.009 | 2% | 34% | 3% | 1% |
| LR | state, AR(1) noise | 0.1 | 50 | +0.001 | 6% | 22% | 8% | 2% |
| LR | state, AR(1) noise | 0.25 | 50 | +0.058 | 36% | 0% | 46% | 0% |
| LR | state, AR(1) noise | 0.5 | 50 | +0.157 | 94% | 0% | 100% | 20% |
| LR | trait | 0 | 100 | −0.009 | 4% | 23% | 3% | 0% |
| LR | trait | 1 | 50 | +0.072 | 18% | 12% | 10% | 0% |
| LR | trait | 2 | 50 | +0.145 | 44% | 0% | 26% | 4% |
| LR | trait | 3 | 50 | +0.181 | 70% | 0% | 42% | 0% |
| RF | state, AR(1) noise | 0 | 50 | −0.021 | 2% | 16% | 4% | 2% |
| RF | trait | 0 | 50 | −0.035 | 4% | 14% | 4% | 0% |

## Table S26

| Group | Pairs | Same recording | RF | GB | RF+GB | LR | MLP | Elapsed time |
|---|---|---|---|---|---|---|---|---|
| Group 10 | 3,510 | 4% | 0.964 | 0.964 | 0.964 | 0.964 | 0.964 | 0.403 |
| Group 11 | 330 | 0% | 0.000 | 1.000 | 0.464 | 0.000 | 0.000 | 0.567 |
| Group 12 | 149 | 100% | 0.000 | 0.000 | 0.000 | 1.000 | 0.866 | 0.302 |
| Group 14 | 2,081 | 2% | 0.510 | 0.650 | 0.653 | 0.986 | 0.358 | 0.508 |
| Group 17 | 329 | 100% | 0.416 | 0.416 | 0.416 | 0.736 | 0.416 | 0.416 |
| Group 19 | 1 | 100% | 0.000 | 1.000 | 0.000 | 1.000 | 1.000 | 1.000 |
| Pooled | 6,400 |  | 0.716 | 0.813 | 0.786 | 0.910 | 0.686 | 0.444 |
| Equal weights, 5 groups |  |  | 0.378 | 0.606 | 0.499 | 0.737 | 0.521 | 0.439 |

## Table S9

| Detector | Observed, primary fits [bootstrap CI] | Observed, refit | Replicates | Null mean | Null 97.5% | p [Monte Carlo 95% CI] | BH p | p between | p within | p, all features reassigned | One feature thresholds (trait / state) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RF | +0.123 [−0.014, 0.260] | +0.124 | 200 | −0.024 | 0.135 | 0.045 [0.017, 0.077] | 0.153 | 0.035 | 0.433 | 0.073 | 0.101 / 0.066 |
| GB | +0.091 [−0.046, 0.228] | +0.091 | 86 | −0.033 | 0.145 | 0.116 [0.057, 0.203] | 0.194 | 0.126 | 0.644 | 0.098 | 0.159 / 0.089 |
| RF+GB | +0.110 [−0.030, 0.251] | +0.112 | 163 | −0.026 | 0.126 | 0.061 [0.030, 0.110] | 0.153 | 0.049 | 0.573 |  |  |
| LR | +0.005 [−0.099, 0.117] | +0.005 | 22 | −0.006 | 0.169 | 0.455 [0.244, 0.678] | 0.455 | 0.435 | 0.565 |  |  |
| MLP | +0.056 [−0.041, 0.172] | +0.061 | 59 | −0.029 | 0.139 | 0.169 [0.084, 0.290] | 0.212 | 0.167 | 0.467 |  |  |

## Table S21

| Detector | Median |error| (s) | Median error (s) | Alarm before onset | No alarm | Δ mean |error| vs clock (s) [95% CI] | MDD (s) | Groups better | Wilcoxon p | BH p |
|---|---|---|---|---|---|---|---|---|---|
| RF | 79 | +47 | 23% | 23% | −10 [−34, +14] | 38 | 8 of 16 | 0.495 | 0.597 |
| GB | 73 | +46 | 31% | 31% | −17 [−40, +7] | 37 | 9 of 16 | 0.211 | 0.529 |
| RF+GB | 74 | +46 | 27% | 31% | −8 [−33, +16] | 39 | 8 of 16 | 0.597 | 0.597 |
| LR | 101 | +57 | 31% | 19% | +23 [+1, +46] | 36 | 6 of 16 | 0.105 | 0.523 |
| MLP | 85 | +62 | 27% | 15% | +10 [−13, +34] | 37 | 8 of 16 | 0.562 | 0.597 |
| Clock | 104 | +87 | 23% | 8% |  |  |  |  |  |

## Table S13

| Model or contrast | Fold MCC | ΔMCC | Wilcoxon p | ΔAtime LPGO [95% CI] | Within | Between |
|---|---|---|---|---|---|---|
| LR dose | 0.394 | +0.029 | 0.632 | −0.024 [−0.144, 0.108] | −0.027 | −0.023 |
| GB dose | 0.287 | −0.078 | 0.175 | −0.053 [−0.202, 0.091] | −0.057 | −0.053 |
| RF minus LR dose |  | +0.054 | 0.528 | +0.148 [−0.017, 0.308] |  |  |
| RF minus GB dose |  | +0.161 | 0.159 | +0.178 [0.027, 0.337] |  |  |
| GB minus LR dose |  | +0.067 | 0.433 | +0.115 [−0.065, 0.281] |  |  |
| GB minus GB dose |  | +0.174 | 0.175 | +0.145 [−0.020, 0.307] |  |  |
| RF+GB minus LR dose |  | +0.069 | 0.433 | +0.134 [−0.035, 0.295] |  |  |
| RF+GB minus GB dose |  | +0.176 | 0.175 | +0.163 [0.004, 0.322] |  |  |
| LR minus LR dose |  | −0.197 | 0.023 | +0.029 [−0.127, 0.189] |  |  |
| LR minus GB dose |  | −0.090 | 0.744 | +0.058 [−0.100, 0.222] |  |  |

## Table S16

| Analysis | Model | Fold mean MCC | Reference | Difference [95% CI] | Wilcoxon p | Two class units |
|---|---|---|---|---|---|---|
| Label at severity 2 or more | RF | 0.123 | 0.088 | +0.035 [−0.147, 0.218] | 0.734 | 9 groups |
| Label at severity 2 or more | GB | 0.203 | 0.088 | +0.115 [−0.166, 0.397] | 0.426 | 9 groups |
| Label at severity 2 or more | RF+GB | 0.161 | 0.088 | +0.073 [−0.165, 0.312] | 0.496 | 9 groups |
| Label at severity 2 or more | LR | 0.254 | 0.088 | +0.166 [−0.038, 0.370] | 0.164 | 9 groups |
| Label persistence rule | Previous label | 0.971 | 0.365 | +0.607 |  | 16 groups |
| Label persistence rule | Majority of the previous 61 labels | 0.714 | 0.365 | +0.349 |  | 16 groups |
| Merged grouping (20 groups) | RF | 0.446 | 0.448 | −0.001 |  | 16 groups |
| Merged grouping (20 groups) | GB | 0.461 | 0.461 | 0.000 |  | 16 groups |
| Merged grouping (20 groups) | RF+GB | 0.462 | 0.462 | 0.000 |  | 16 groups |
| Merged grouping (20 groups) | LR | 0.199 | 0.197 | +0.001 |  | 16 groups |
| Merged grouping (20 groups) | MLP | 0.279 | 0.288 | −0.009 |  | 16 groups |
| Merged grouping (20 groups) | Clock | 0.368 | 0.365 | +0.003 |  | 16 groups |
| Smoothing window chosen on validation groups | RF | 0.375 | 0.369 | +0.006 |  | 16 groups |
| Smoothing window chosen on validation groups | GB | 0.410 | 0.369 | +0.041 |  | 16 groups |
| Smoothing window chosen on validation groups | RF+GB | 0.393 | 0.369 | +0.023 |  | 16 groups |
| Smoothing window chosen on validation groups | LR | 0.206 | 0.369 | −0.163 |  | 16 groups |
| Smoothing window chosen on validation groups | MLP | 0.334 | 0.369 | −0.035 |  | 16 groups |
| Seed 1 | RF | 0.433 | 0.365 | +0.069 |  | 16 groups |
| Seed 1 | RF+GB | 0.458 | 0.365 | +0.093 |  | 16 groups |
| Seed 1 | MLP | 0.369 | 0.365 | +0.005 |  | 16 groups |
| Seed 2 | RF | 0.442 | 0.365 | +0.078 |  | 16 groups |
| Seed 2 | RF+GB | 0.457 | 0.365 | +0.092 |  | 16 groups |
| Seed 2 | MLP | 0.304 | 0.365 | −0.061 |  | 16 groups |

## Table S11

| Groups used | Recordings | Both classes | Share of pairs | RF | GB | RF+GB | LR | MLP |
|---|---|---|---|---|---|---|---|---|
| All 22 groups | 35 |  |  | +0.123 | +0.091 | +0.110 | +0.005 | +0.056 |
| Without group 0 | 2 | no | 8.1% | +0.096 | +0.071 | +0.083 | −0.015 | +0.034 |
| Without group 1 | 1 | yes | 5.4% | +0.127 | +0.097 | +0.114 | +0.022 | +0.065 |
| Without group 2 | 3 | yes | 18.7% | +0.119 | +0.090 | +0.105 | +0.026 | +0.078 |
| Without group 3 | 1 | no | 0.4% | +0.124 | +0.093 | +0.111 | +0.007 | +0.058 |
| Without group 4 | 2 | yes | 11.3% | +0.120 | +0.093 | +0.107 | +0.002 | +0.045 |
| Without group 5 | 1 | yes | 5.8% | +0.113 | +0.082 | +0.101 | +0.009 | +0.051 |
| Without group 6 | 2 | yes | 14.3% | +0.097 | +0.064 | +0.082 | −0.001 | +0.043 |
| Without group 7 | 1 | no | 6.7% | +0.102 | +0.071 | +0.090 | −0.008 | +0.036 |
| Without group 8 | 1 | yes | 8.4% | +0.103 | +0.078 | +0.091 | +0.005 | +0.036 |
| Without group 9 | 1 | yes | 6.8% | +0.145 | +0.109 | +0.130 | −0.009 | +0.058 |
| Without group 10 | 3 | yes | 13.8% | +0.131 | +0.091 | +0.115 | −0.023 | +0.052 |
| Without group 11 | 2 | yes | 12.6% | +0.119 | +0.081 | +0.101 | 0.000 | +0.050 |
| Without group 12 | 1 | yes | 6.4% | +0.134 | +0.097 | +0.117 | +0.010 | +0.058 |
| Without group 13 | 1 | yes | 8.2% | +0.120 | +0.084 | +0.105 | +0.010 | +0.079 |
| Without group 14 | 6 | yes | 29.4% | +0.162 | +0.138 | +0.155 | +0.023 | +0.081 |
| Without group 15 | 1 | yes | 7.3% | +0.145 | +0.106 | +0.130 | +0.025 | +0.069 |
| Without group 16 | 1 | no | 6.7% | +0.152 | +0.119 | +0.139 | +0.011 | +0.063 |
| Without group 17 | 1 | yes | 5.6% | +0.124 | +0.094 | +0.112 | +0.011 | +0.051 |
| Without group 18 | 1 | no | 1.3% | +0.121 | +0.089 | +0.108 | +0.003 | +0.052 |
| Without group 19 | 1 | yes | 5.5% | +0.117 | +0.086 | +0.106 | −0.004 | +0.046 |
| Without group 20 | 1 | yes | 5.9% | +0.111 | +0.077 | +0.097 | −0.001 | +0.058 |
| Without group 21 | 1 | no | 6.8% | +0.127 | +0.103 | +0.120 | +0.011 | +0.064 |

## Table S20

| Detector | Replicates | Null 95% | Null 97.5% | Observed, refit | Bootstrap CI above zero | Bootstrap CI below zero | Observed ΔMCC | Null mean ΔMCC | p, fold MCC |
|---|---|---|---|---|---|---|---|---|---|
| RF | 200 | 0.110 | 0.135 | +0.124 | 10 of 200 (5.0%) | 27 of 200 (13.5%) | +0.090 | −0.133 | 0.005 |
| GB | 86 | 0.126 | 0.145 | +0.091 | 6 of 86 (7.0%) | 16 of 86 (18.6%) | +0.097 | −0.114 | 0.011 |
| RF+GB | 163 | 0.117 | 0.126 | +0.112 | 8 of 163 (4.9%) | 22 of 163 (13.5%) | +0.097 | −0.113 | 0.006 |
| LR | 22 | 0.129 | 0.169 | +0.005 | 2 of 22 (9.1%) | 2 of 22 (9.1%) | −0.167 | −0.077 | 0.913 |
| MLP | 59 | 0.131 | 0.139 | +0.061 | 3 of 59 (5.1%) | 9 of 59 (15.3%) | −0.029 | −0.082 | 0.200 |

## Table S17

| Model | Atime pooled | Pooled minus elapsed time [95% CI] | Atime LPGO | LPGO minus elapsed time [95% CI] | Pooled minus LPGO |
|---|---|---|---|---|---|
| Clock (LR on elapsed time) | 0.444 | −0.086 [−0.129, −0.048] | 0.530 | 0.000 [−0.001, 0.002] | −0.086 |
| RF on elapsed time | 0.400 | −0.130 [−0.236, −0.016] | 0.459 | −0.070 [−0.172, 0.034] | −0.060 |
| GB on elapsed time | 0.399 | −0.131 [−0.176, −0.085] | 0.536 | +0.006 [−0.015, 0.025] | −0.137 |

## Table S19

| δ | Replicates | Mean ΔAtime LPGO | Detected, bootstrap rule [95% CI] | Detected, null threshold [95% CI] |
|---|---|---|---|---|
| 1 | 200 | +0.061 | 15% [10%, 20%] | 10% [4%, 23%] |
| 1.5 | 200 | +0.128 | 38% [32%, 45%] | 33% [21%, 50%] |
| 2 | 200 | +0.162 | 56% [48%, 62%] | 49% [34%, 70%] |
| 3 | 200 | +0.178 | 60% [53%, 67%] | 58% [42%, 77%] |

## Table S7

| Family | Estimates | Excluding zero (or BH p < 0.05) | Which | Role |
|---|---|---|---|---|
| Detector minus clock, fold MCC (Table S10) | 5 | 0 | none | interval of the primary comparison |
| Parts of Atime (Table S4) | 21 | 1 | GB time only, within | descriptive |
| Learner matched contrasts (Table S4) | 2 | 1 | RF minus RF on elapsed time only | exploratory |
| Scenario check (Table S12) | 22 | 2 | RF+GB with minus without scenario; RF minus LR time and scenario | sensitivity |
| Time matched severity (Table S26) | 5 | 1 | GB | exploratory, not interpreted |
| Onset error (Table S21) | 5 | 1 | LR | exploratory |
| Dose reference (Table S13) | 10 | 2 | RF minus GB dose; RF+GB minus GB dose; fold MCC, Wilcoxon p < 0.05: LR minus LR dose | sensitivity |
| Label threshold check (Table S16) | 4 | 0 | none | sensitivity |
| Influence of single groups (Table S11) | 110 | not applicable | no interval or test | descriptive |
| Controls with the detectors' own learners (Table S8) | 18 | not applicable | detection rates on synthetic signals | check of what the protocol detects |
| Within game randomization test (Table S9) | 5 | 0 | none | exploratory, BH over the five detectors |
| Parts of the randomization test (Table S9) | 10 | 2 | unadjusted p < 0.05: RF between, RF+GB between | descriptive, unadjusted |
