# Reproducibility audit

**Date:** 13 October 2026. **Machine:** Windows 11, 16 CPUs, Python 3.13.0, scikit-learn 1.6.0, numpy 2.2.1, pandas 2.2.3, scipy 1.15.0 (the environment of the revision analyses, `requirements-revision.txt`). The environment of the primary run (Python 3.11.15, scikit-learn 1.8.0) was not available.

## 1. Summary

| Part of the results | Status |
|---|---|
| Every table, figure and quoted number, computed **from the saved predictions** | **Reproduced by rerunning the code** (fast path, all checks pass) |
| Model fits added in revision: scenario, dose and label threshold analyses (steps 53, 54, 60; Tables S12, S13, S16 label rows) | **Reproduced by refitting from the raw data**: all 435 prediction files and 8 result tables identical (difference 0) |
| Replicate based experiments (steps 16, 55, 58, 59; Tables III, IV, S8, S9, S18 to S20) | **Reproduced for a sample**: 16 replicates refitted, 20 rows, each identical to the saved row (largest difference 1e-16). The other 4,254 of the 4,274 saved replicate rows were checked only as saved outputs |
| Primary model fits (steps 10 to 15; Tables II, III, S15 and everything derived from them) | **Not refitted in this audit.** Checked against saved outputs: the 233 prediction files match the checksums recorded at the first submission, and the fitting code is unchanged since that release. An earlier full refit in the primary environment is recorded in `docs/AUDIT.md`, section 3 |
| Primary fits in a different environment (step 50) | Rerun here: gradient boosting and the clock reproduce the saved probabilities (2e-11, 2e-16); the random forest and the logistic regression do not (0.067, 0.020). This is the documented effect of the library versions, not a reproduction |

No numerical result changed. No analysis code was changed. Two verification scripts and one metadata file received small corrections (Section 4).

## 2. Identification of the code

- The audit was run on a file by file copy of this repository (checked with a recursive comparison of `src`, `pipeline`, `tools`, `data`, `reference`, `run_all.py` and the requirement files: no difference). The logs it names (`logs/…`) and the Word documents are kept by the authors.
- Before this audit the repository had one commit, `2dbc62d`, the release of the first submission. Compared with it, the files that fit the primary models and compute the primary statistics (`src/csp/data.py`, `design.py`, `metrics.py`, `metrics_extra.py`, `inference.py`, `paths.py`, steps 00 to 26) are **unmodified**. Modified since: `pipeline/30_figures.py` (one line), `31_paper_tables.py` and `tools/extract_paper_tables.py` (table numbers of the revised paper), `40_verify.py`, `run_all.py` (new steps added to the lists).
- `docs/ANALYSIS_HISTORY.md` records how the repository was derived from the authors' original scripts before the first submission. That derivation was not re-examined here.
- **Steps 50 to 62 and `src/csp/revision.py`, `si_revision.py` were never committed.** No recorded earlier version exists, so "the version that produced the results" cannot be established from history for these files. Their summary and table code was edited during the revision after the long runs had finished (for example, columns were added to the summary of step 59). Whether the fitting code still produces the saved results was therefore tested directly (checks 6 and 7).

## 3. Checks performed

| No. | Check | How | Result |
|---|---|---|---|
| 1 | Raw data | `python pipeline/00_get_data.py` | SHA-256 of `dataset.csv` and both archives equal the recorded values |
| 2 | Primary predictions unchanged | `sha256sum -c reference/predictions_sha256.txt` | 233 of 233 files OK |
| 3 | Package equals repository | recursive comparison | no difference in code, data, reference files, predictions |
| 4 | **Fast path rerun in the audited copy** | `python run_all.py` (25 steps, no model fitted) | `ALL CHECKS PASSED`, 95 checks: every result table within 1e-9 of its frozen copy; every printed table of the final Word files equal cell by cell to its regenerated table; 268 quoted numbers reproduced. Log: `logs/audit_fast_path.log` |
| 5 | Fast path into an empty output folder | `CSP_OUTPUTS=<fresh> python run_all.py`, then table by table comparison | 66 result tables: 52 identical, 14 differ in the last digits, largest difference 4.5e-14 (`audit/fast_path_vs_original_tables.txt`). Step 40 in that folder: `ALL CHECKS PASSED` after the fix of Section 4, item 1 |
| 6 | **Refit of steps 53, 54, 60 from the raw data** | fresh output folder holding only the primary predictions and tables; steps run unchanged | `P_scen_logo.csv`, `P_dose_logo.csv`, `P_label2_logo.csv`, 216 + 216 pair files: largest difference from the saved predictions **0**. Tables `T_rev_scenario`, `_contrast`, `T_rev_refit_vs_shipped`, `T_rev_dose`, `_contrast`, `T_rev_label2`, `T_rev_onset`, `_paired`: difference **0** (`audit/refit_53_54_60_result.txt`) |
| 7 | **Rerun of a sample of replicates** | `python audit/rerun_sample.py`: calls the unchanged function `one()` of steps 16, 55, 58, 59 | 16 replicates, 20 rows, all identical to the saved rows (`audit/rerun_sample_result.csv`): step 59 identity replicate (the observed statistic) and replicate 0 for RF, GB, RF+GB, LR and MLP; step 58 replicate 0 for GB and RF; step 55 five replicates over the three learners and both signals; step 16 three replicates |
| 8 | Final documents against the code | `python pipeline/57_rev_verify.py manuscript` | `ALL REVISION CHECKS PASSED`: 70 numbers added in revision recomputed and found in the text; figures, references and Supporting Information tables numbered in order. The response letter check is skipped (letter not in the audited copy) |
| 9 | Environment check | `python pipeline/50_env_check.py` | Ends with its assertion error, as designed outside the primary environment. Differences: RF 0.067, GB 1.7e-11, LR 0.020, clock 2.2e-16 (`audit/step50_rerun_T_rev_env_check.csv`) |
| 10 | Equations of the manuscript against the code | `python audit/eq_check.py .`: literal recomputation of equations (1) to (13) and (S1) to (S5) | every recomputed quantity equals the code output (`audit/eq_check_out.txt`) |

After checks 4 and 9 the files they had rewritten in `outputs/` were replaced by the original files, so `outputs/` in this repository is byte for byte the authors' original.

## 4. Discrepancies found and corrections made

| No. | Finding | Correction |
|---|---|---|
| 1 | `pipeline/40_verify.py` stopped with `UnicodeEncodeError` on Windows when `CSP_OUTPUTS` points to a separate folder and the output is written to a file: the report line for the prediction differences contains a "Δ". The documented full path check therefore could not finish on Windows. | One line added (`sys.stdout.reconfigure(encoding="utf-8")`). No computation is affected. Applied in the repository too. |
| 2 | `pipeline/57_rev_verify.py` reported a failure when the authors' response letter is absent. | The letter check is skipped when the file is absent. Applied in the repository too. |
| 3 | `CITATION.cff` carried the title of the first submission. | Title of the revised paper. Applied in the repository too. |
| 4 | `run_all.py` (docstring) and the repository `README` say that `--full` takes about 3.5 hours. Since steps 53, 55, 58 and 59 were added to the full list, a run into an empty folder takes more than a day. | Code left as it is. Stated in `README.md`, Section 4.3, with a way to skip the long steps. |
| 5 | `docs/RESULTS_MAP.md`, the docstrings of steps 30 and 31 and parts of `docs/AUDIT.md` use the table and figure numbers of earlier drafts (for example "Table VI" for the controls, now Table IV). The code writes the tables under the final numbers; only the descriptions are out of date. | Left unchanged, to keep the original files. `README.md`, Section 5, gives the map for the final documents. |
| 6 | The saved `T_rev_env_check.csv` shows 0.013 for the logistic regression; the rerun of check 9 gives 0.020. | Not an error: the logistic regression on 76 features depends on the number of BLAS threads (`docs/AUDIT.md`, section 3), and the rerun did not pin the threads. The original file is kept; the rerun is in `audit/`. |
| 7 | `logs/rev60.log` ends with a Python traceback. | It is the log of an earlier failed attempt of step 60 in the authors' session. The step ran correctly afterwards, and check 6 reproduces its outputs exactly. Kept for the record. |
| 8 | `outputs/tables/CTRL_PERM_STRAT.csv` holds more replicates than Table S9 reports (GB 200, RF+GB 200, LR 29, MLP 60, against 86, 163, 22, 59). | Not an error: replicates run in batches, and the sequential rule uses those up to the tenth exceedance. The summary of step 59 applies the rule; the reported values follow it. |
| 9 | Windows path length. Inside a deep folder, relative paths longer than 260 characters fail (seen twice during this audit with `..\..` paths). | None needed inside the audited copy when commands are run from its root. Place the audited copy in a short path. |

## 5. What "reproduced" means here, and what it does not

- **Rerun and identical:** checks 4 to 8 and 10. These are results of executing the audited copyd code in this audit.
- **Checked against existing outputs only:** the primary model fits, and all replicates of steps 16, 55, 58 and 59 outside the sample of check 7. For these, the audit shows that the saved files are the ones the tables are computed from and that they are unchanged since they were recorded; it does not show again that the code produces them.
- The sample of check 7 was chosen by hand, not at random, and covers 16 of 3,872 replicate computations (20 of 4,274 saved rows; one computation of the tree ensembles gives three rows). It includes the five observed statistics of the randomization test, which enter Table III directly.

## 6. Remaining limitations

1. **Primary environment.** A refit of the primary models with Python 3.11 and scikit-learn 1.8 was not done here. Anyone with that environment can run `CSP_OUTPUTS=<fresh> python run_all.py --full` after copying the three `CTRL_*.csv` replicate files of the revision into the fresh folder (README, Section 4.3); step 40 then prints the difference of every prediction file.
2. **No version history for the revision code.** Checks 6 and 7 show that the present code gives the saved results for everything that was rerun; for the replicates that were not rerun, this rests on the code being deterministic and seeded per replicate.
3. **Two environments.** The paper's results come from two sets of library versions. The repository records both, but a single environment reproduces only one of the two groups of fits exactly.
4. **Long experiments.** A complete rerun of steps 55, 58 and 59 (about 25 to 40 hours on 16 CPUs) was not done.
5. **Thread dependence** of the logistic regression: exact reproduction of its primary fits needs 2 threads (1 thread for the pair models after the first 14), as `run_all.py` and step 15 set.
6. **No archived release yet.** The code is public in this repository; it has not been archived with a DOI.
7. **Scope.** The audit concerns computational reproducibility. It does not address the methodological limitations stated in the manuscript (one dataset, reconstructed groups, exploratory randomization test).
