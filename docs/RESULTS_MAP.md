# Results map

Every table, figure and quoted number of the paper, with the step that produces it and the file it is read from.
All files are under `outputs/`. `pipeline/40_verify.py` checks every entry below against the printed paper.

## Main text

| Item | Content | Produced by | Read from |
|---|---|---|---|
| Table I | Evaluation designs of published studies | literature (no computation) | — |
| Table II | Dataset composition and recovered units | step 01 | `tables/T_dataset_facts.csv` |
| Table III | Primary comparison (fold, threshold free, pooled, all groups) | steps 20, 25 | `tables/T_primary.csv`, `tables/T_lpgo_atime.csv` |
| Table IV | Paired comparison with the clock and with elapsed time | steps 24, 25 | `tables/T_primary_stats.csv`, `tables/T_lpgo_atime.csv` |
| Table V | Severity errors under three levels of control | steps 20, 24 | `tables/T_severity.csv`, `tables/T_asev_paired.csv` |
| Table VI | Positive and negative controls | step 16 | `tables/T_controls.csv` (replicates: `tables/CTRL_LR.csv`) |
| Table VII | Reporting checklist | text (no computation) | — |
| Table VIII | Feature list (counts) | step 31 (counted from `csp.design`) | `paper_tables/Table_VIII.csv` |
| Fig. 1 | Evaluation protocol | step 30 | `figures/fig1_protocol.png` |
| Fig. 2 | Random window splitting against group disjoint evaluation | steps 20, 24, 30 | `tables/T_leakage.csv`, `tables/T_leakage_loro.csv` → `figures/fig2_leakage.png` |
| Fig. 3 | Primary comparison panel | steps 20, 25, 30 | `tables/T_primary.csv`, `tables/T_lpgo_atime.csv`, `predictions/P_primary*.csv` → `figures/fig3_primary.png` |
| Fig. 4 | Severity at controlled operating points | steps 20, 24, 30 | `tables/CURVE_s3_vs_alarm.csv`, `tables/T_asev_*.csv` → `figures/fig4_severity.png` |
| Fig. 5 | Smoothing window and nested feature analysis | steps 20, 30 | `tables/T_smoothing.csv`, `tables/T_ablation.csv`, `tables/T_original99.csv` → `figures/fig5_temporal.png` |
| Fig. 6 | Positive and negative controls | steps 16, 25, 30 | `tables/T_lpgo_atime.csv`, `tables/T_controls.csv` → `figures/fig6_controls.png` |

Figure numbers follow the order of the figures in the manuscript (protocol, leakage, primary, severity, temporal,
controls). See docs/AUDIT.md, item P1: the submitted manuscript labels two figures "Fig. 2".

## Supporting Information

Supporting Information tables are numbered in the order of their first citation in the main text; the mapping from
the internal names used in the code (order in which the analyses were added) is `csp.si_revision.SI_ORDER`.

| Item | Content | Produced by | Read from |
|---|---|---|---|
| Table S2 | 73 secondary tests with one BH adjustment | step 26 | `tables/T_secondary_tests.csv` |
| Table S11 | 99 features and LORO sensitivity | step 20 | `tables/T_original99.csv`, `tables/T_full99_mlp.csv`, `tables/T_loro.csv`, `tables/T_constants.csv` |
| Table S12 | A_sev per group | steps 21, 24 | `tables/T_asev_by_group.csv`, `tables/T_s3_by_group.csv` |
| Table S14 | PPV, NPV, false alarms, alarm onsets | step 20 | `tables/T_deploy.csv`, `tables/T_primary.csv` |
| Table S15 | Prior shift transfer after calibration | step 13 | `tables/T_prior_shift.csv` |
| Table S16 | Control details | step 16 | `tables/T_controls.csv` |
| Table S17 | Episodes with the shifted reference | steps 20, 21 | `tables/T_episodes.csv`, `tables/T_episode_random_reference.csv` |
| Tables S1, S3 to S10, S13, S18 | analyses added after the primary analysis was fixed | steps 51 to 60 | see the table under Revision R1 below |
| Note S1 | Closed form bootstrap | `src/csp/inference.py` (`ATime`) | equality with the resampling estimator asserted in step 24 |

## Numbers quoted in the text

`reference/paper_numbers.csv` lists 268 numbers quoted in the abstract and Sections III to VI, each with its
location and the expression that recomputes it from `outputs/tables`. The main sources:

| Section | Quantity | File |
|---|---|---|
| III-A | windows, prevalence, label changes, archive facts, 7.2 min, group spans, restarts | `T_dataset_facts.csv`, `T_archive_facts.csv` |
| III-B | zero IQR features per fold | `T_dataset_facts.csv` |
| V-A | leakage demonstration (0.995, 0.989, 1.000 against 0.670, 0.325, 0.730; LORO 0.307) | `T_leakage.csv`, `T_leakage_loro.csv` |
| V-A | fold MCC, paired tests, MDE, groups needed, seeds | `T_primary.csv`, `T_primary_stats.csv`, `T_sup_seeds.csv` |
| V-A | fold AUC, time matched AUC (LPGO and pooled) | `T_primary.csv`, `T_primary_stats.csv`, `T_lpgo_atime.csv` |
| V-A | 99 features, LORO, merged grouping, LORO by group type | `T_original99.csv`, `T_loro.csv`, `T_merged.csv`, `T_loro_by_grouptype.csv`, `T_constants.csv` |
| V-B | severity 3 misses, six recording group, A_sev | `T_severity.csv`, `T_s3_by_group.csv`, `T_s3_without_big_group.csv`, `T_asev_paired.csv`, `T_asev_by_group.csv` |
| V-C | persistence rules, smoothing sweep, nested w, episodes, nested features | `T_constants.csv`, `T_smoothing*.csv`, `T_nested_w*.csv`, `T_episodes.csv`, `T_episode_random_reference.csv`, `T_ablation.csv` |
| V-D | PPV at low prevalence, false alarms per 1,000, onsets, prior shift | `T_deploy.csv`, `T_primary.csv`, `T_prior_shift.csv` |
| V-E, VI-C | time only controls, detection rates, calibrated thresholds, half widths, null spread | `T_lpgo_atime.csv`, `T_controls.csv`, `CTRL_LR.csv` |
| V | 73 secondary tests, 2 unadjusted p < 0.05, none after BH | `T_secondary_tests.csv` |

## Revision R1

Numbers added in revision are listed in `reference/paper_numbers_revision.csv` and checked by step 57 against the
revised .docx files.

| Section | Quantity | File |
|---|---|---|
| Abstract, V-A, VI-C | intervals of ΔMCC, MDD and groups needed with plain and corrected variance (Table IV, Table S7) | `T_rev_power.csv` |
| IV-B, V-C | detector minus clock at each smoothing window (Table S3) | `T_rev_window_gap.csv` |
| III-F, V-A | share of between group pairs, within and between parts, learner matched contrasts (Table S1) | `T_rev_tm_parts.csv`, `T_rev_tm_learner.csv`, `T_rev_tm_coverage.csv` |
| V-A | bins and minimum counts, LORO and merged grouping (Table S10) | `T_rev_tm_bins.csv`, `T_rev_tm_units.csv` |
| V-A | scenario information and the time and scenario reference (Table S8) | `T_rev_scenario.csv`, `T_rev_scenario_contrast.csv`, `T_rev_refit_vs_shipped.csv` |
| V-E, VI-C | controls with the RF and GB learners, AR(1) state signal, calibrated thresholds (Table S5) | `T_rev_controls.csv`, `CTRL_REV.csv` |
| V-B | severity ranking matched on elapsed time (Table S13) | `T_rev_severity.csv` |
| Appendix B | refits of the revision environment against the shipped values | `T_rev_env_check.csv`, `T_rev_refit_vs_shipped.csv` |
| IV-C, V-E, Abstract | within game permutation test of all five detectors (primary) and the all feature variant (Table S6) | `T_rev_perm_strat.csv`, `CTRL_PERM_STRAT.csv`, `T_rev_perm_null.csv`, `CTRL_PERM.csv` |
| V-F, Abstract | onset error within recordings, detector minus clock (Table S18) | `T_rev_onset.csv`, `T_rev_onset_paired.csv` |
| V-A | dose reference (Table S9) | `T_rev_dose.csv`, `T_rev_dose_contrast.csv` |
| V-C | label at severity 2 or more | `T_rev_label2.csv` |
| V-B | influence of single groups on the time matched advantage | `T_rev_influence.csv` |
| V-D | interval of the 33% detection rate of the one feature control | `T_rev_control_ci.csv` |
| V-D | critical values and bootstrap coverage in the null replicates of the randomization test | `T_rev_perm_strat.csv` (`null_q95`, `null_above_k`) |
| V-E | minimum detectable difference of the onset error | `T_rev_onset_paired.csv` (`mdd`) |
| IV-B | inventory of the added interval estimates and tests (Table S4) | built from the tables above in `csp.si_revision` |
