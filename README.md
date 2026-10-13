# Evaluating Cybersickness Detectors Against an Elapsed Time Baseline: code and results

Code, data, saved predictions and result tables for

**"Evaluating Cybersickness Detectors Against an Elapsed Time Baseline: A Group Disjoint Protocol With Positive and
Negative Controls"** (R. Darabee, M. Muniandy, W. K. Cheng, E. H. Sumiea, O. Shindi), revised manuscript (R1) and its
Supporting Information. The manuscript is under review; the two documents are not part of this repository.

This repository holds the analysis code as it stood when the final manuscript was built, with the saved predictions
and every result table. What was verified, and how, is in `REPRODUCIBILITY_AUDIT.md`; read it before relying on any
statement of reproducibility.

```bash
git clone https://github.com/rajaiimad/Evaluating-Cybersickness.git
cd Evaluating-Cybersickness
```

## 1. Contents

```
Evaluating-Cybersickness/
├── README.md                    this file
├── REPRODUCIBILITY_AUDIT.md     checks performed, discrepancies, corrections, limitations
├── run_all.py                   runs the pipeline in order (fast path or --full)
├── requirements.txt             environment of the primary model fits (Python 3.11)
├── requirements-revision.txt    environment of the analyses added in revision (Python 3.13)
├── environment.yml              conda version of requirements.txt
├── data/raw/                    the public dataset, unchanged, with its licence and checksums
├── src/csp/                     library: data and units, features, designs, detectors, metrics, statistics
├── pipeline/                    numbered steps; each file states its inputs, method and outputs in its docstring
├── outputs/
│   ├── predictions/             window level held out probabilities of every model fit (primary run)
│   │   ├── lpgo/                one file per pair of held out groups (216)
│   │   └── rev/                 fits added in revision (scenario, dose and label threshold analyses)
│   ├── tables/                  every result table (CSV), including one row per replicate of the controls and the
│   │                            randomization tests (CTRL_*.csv)
│   ├── paper_tables/            the tables of the manuscript and Supporting Information as printed
│   └── figures/                 the figures
├── reference/                   frozen copies used by the checks: result tables, printed tables, quoted numbers,
│                                checksums of the primary predictions
├── docs/                        method to code map, results map, code audit of the first submission, history
├── tools/                       extract_paper_tables.py (reads the printed tables from the Word files)
└── audit/                       harness and results of the reproduction checks
```

Size: about 240 MB, almost all of it saved predictions.

## 2. Installation

Python 3.11 or newer, CPU only. No GPU and no compiled code of our own.

```bash
python -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -r requirements.txt        # or: pip install -r requirements-revision.txt   (see "Two environments")
```

### Two environments

The results were produced in two software environments, and this cannot be undone after the fact:

| | Primary run | Revision run |
|---|---|---|
| Steps | 00 to 31, 40 | 50 to 62 |
| Python | 3.11.15 | 3.13.0 |
| scikit-learn / numpy / pandas / scipy | 1.8.0 / 2.4.4 / 3.0.2 / 1.17.1 | 1.6.0 / 2.2.1 / 2.2.3 / 1.15.0 |
| File | `requirements.txt` | `requirements-revision.txt` |
| Threads | 2 (pinned by `run_all.py`) | one BLAS thread per worker process |

Consequences:

- Everything that is computed **from saved predictions** (all tables, figures and checks) gives the same values in
  both environments.
- **Refitting the primary models** gives the saved predictions only in the primary environment. In the revision
  environment, gradient boosting and the clock are reproduced exactly; the random forest and the logistic regression
  differ slightly (step 50 measures this: largest difference in a predicted probability 0.067 and 0.013). This is why
  every contrast added in revision refits both of its arms in the revision environment (manuscript, Section IV-B;
  Supporting Information Note S2), and why Table S12 shows refitted values that differ from Table II in the third
  decimal.
- **Refitting the analyses added in revision** gives the saved values in the revision environment.

## 3. Dataset

The analysis uses `dataset.csv` of the public UFFCSData repository (Porcino et al.),
https://github.com/tmp1986/UFFCSData, at commit `b5128e681786b81501d269a73e860d57c495d0aa`. The file and the two
archives of the repository are included unchanged in `data/raw/` under their licence (AGPL-3.0,
`data/raw/UFFCSData_LICENSE`); `data/raw/README.md` gives sizes and SHA-256 checksums.

```bash
python pipeline/00_get_data.py         # verifies the checksums and downloads any missing file from the pinned commit
```

The file has no participant or recording identifier. `src/csp/data.py` recovers 35 recordings (runs between timestamp
resets) and 22 reconstructed groups (combinations of seven participant descriptors) and asserts both counts every
time the data are loaded. `outputs/tables/T_recovered_units.csv` lists the rows of every recording.

## 4. Running the workflow

All commands are run from this folder. On Windows, keep the repository in a short path: paths longer than 260 characters fail.

### 4.1 Fast path: every table, figure and check from the saved predictions (about 10 minutes)

```bash
python run_all.py
```

It runs steps 01, 02, 12, 13, 16 (summary), 20 to 26, 51, 52, 54, 55 (summary), 56, 58 (summary), 59 (summary), 60,
61, 62, 30, 31 and 40. No model is fitted: steps that fit models find their prediction or replicate files and only
score them. The run ends with `ALL CHECKS PASSED` when

1. every result table equals its frozen copy in `reference/tables` (tolerance 1e-9),
2. every regenerated printed table equals, cell by cell, the table extracted from the final Word files
   (`reference/paper_tables`), and
3. the 268 numbers quoted in the text since the first submission are recomputed and equal the printed values.

### 4.2 Checks of the final documents

Two scripts compare the code with the Word files of the manuscript and the Supporting Information, which are not in
this repository while the paper is under review:

```bash
pip install python-docx
python tools/extract_paper_tables.py <manuscript.docx> <supporting_information.docx>
python pipeline/40_verify.py
python pipeline/57_rev_verify.py <folder with Cybersickness_IEEE_R1.docx and Cybersickness_supporting_information_R1.docx>
```

The first command reads the printed tables from the Word files into `reference/paper_tables`; the copies in this
repository were read from the final documents. Step 57 recomputes the 70 numbers added in revision and looks for each
in the text, and checks the numbering of figures, references and Supporting Information tables. Without the documents,
the fast path of 4.1 still checks every printed table and the 268 quoted numbers against `reference/`.

### 4.3 Full path: refit the models from the raw data

```bash
CSP_OUTPUTS=/tmp/csp_refit python run_all.py --full       # Windows: set CSP_OUTPUTS=C:\temp\csp_refit
```

Use a fresh output folder so that the saved outputs stay available for comparison; step 40 then also reports the
largest difference between the new and the saved predictions of every file. `--full` can be restarted: a step skips
every fit whose prediction file or replicate row exists. In another environment than the primary one, pass a
tolerance, for example `--tol 1e-3`, and read the differences per table.

Running time. The steps of the primary run (00 to 31) take about 3.5 hours on 2 CPUs; in the primary environment they
reproduce the saved predictions to about 1e-16 (`docs/AUDIT.md`, section 3). Since the revision, `--full` also
contains the fitting steps added in revision, and with an empty output folder it runs all of them:

| Step | What it fits | Time on 16 CPUs |
|---|---|---|
| 53 | detectors without the scenario indicators, time and scenario reference; LOGO and 216 pair models | 15 min |
| 55 | controls with the GB, LR and RF learners, autocorrelated state signal (1,100 replicates) | about 4 h |
| 58 | coarse randomization (all 76 features, both games), RF and GB, 40 replicates each | about 5 h |
| 59 | within game randomization test, five detectors, sequential stopping at 10 exceedances or 200 replicates | 15 to 30 h |
| 60 | dose reference (LOGO and 216 pair models) and detectors on the label at severity 2 or more | about 10 min |

A complete `--full` run therefore takes more than a day. To avoid the long steps, copy `outputs/tables/CTRL_REV.csv`,
`CTRL_PERM.csv` and `CTRL_PERM_STRAT.csv` into `<fresh folder>/tables` before starting: steps 55, 58 and 59 then find
their replicates and only summarize them. `CSP_JOBS` sets the number of worker processes of steps 53, 55, 58, 59 and
60. Step 50 (comparison of refits in the current environment with the saved primary predictions) is not part of
`run_all.py`; run it by hand with `python pipeline/50_env_check.py`. It ends with an assertion error when the
environment is not the primary one, after writing its table.

### 4.4 Rerunning a sample of the replicate based experiments

```bash
python audit/rerun_sample.py           # JOBS=8 by default; about 2 hours
```

It calls the unchanged replicate function of steps 16, 55, 58 and 59 for 16 replicates, among them the observed
statistic of the randomization test for all five detectors, and compares every rerun row with the saved row.

## 5. Which step produces which result

Supporting Information tables are numbered in the order of their first citation. Inside the code they keep the names
of the order in which they were added; `reference/si_order.json` and `csp.si_revision.SI_NUM` hold the mapping. The
table below uses the printed numbers of the final documents. All files are under `outputs/tables` unless stated.

### Manuscript

| Item | Content | Steps | Read from |
|---|---|---|---|
| Table I | Dataset composition | 01 | `T_dataset_facts.csv` |
| Table II | Primary comparison under LOGO | 11, 15 (fits); 20, 25 | `T_primary.csv`, `T_lpgo_atime.csv` |
| Table III | Paired comparison with the clock and with elapsed time | 24, 25, 51, 59 | `T_primary_stats.csv`, `T_rev_power.csv`, `T_lpgo_atime.csv`, `T_rev_perm_strat.csv` |
| Table IV | Positive and negative controls | 16 | `T_controls.csv` (replicates: `CTRL_LR.csv`) |
| Table V | Reporting checklist | text, no computation | |
| Fig. 1 | Protocol | 30 | `figures/fig1_protocol.png` |
| Fig. 2 | Random splitting against group disjoint evaluation | 11; 20, 24, 30 | `T_leakage.csv`, `T_leakage_loro.csv`; `figures/fig2_leakage.png` |
| Fig. 3 | Primary comparison | 20, 25, 30 | `figures/fig3_primary.png` |
| Fig. 4 | Controls | 16, 25, 30 | `figures/fig6_controls.png` |

### Supporting Information

| Item | Content | Steps | Read from |
|---|---|---|---|
| Table S1 | Evaluation designs of published studies | literature, no computation | |
| Table S2 | Feature list | 31 (counted from `csp.design`) | |
| Table S3 | Episode recall, shifted alarm reference, latency | 20, 21 | `T_episodes.csv`, `T_episode_random_reference.csv` |
| Table S4 | Within and between group parts of the time matched AUC | 52 | `T_rev_tm_parts.csv`, `T_rev_tm_learner.csv`, `T_rev_tm_coverage.csv` |
| Table S5 | 73 secondary tests | 26 | `T_secondary_tests.csv` |
| Table S6 | Smoothing windows and thresholds (exploratory grid) | 51, 62 | `T_rev_window_gap.csv`, `T_rev_tau_grid.csv` |
| Table S7 | Inventory of the analyses added after the primary analysis | assembled from the tables below | |
| Table S8 | Controls with the detectors' own learners | 55 | `T_rev_controls.csv` (replicates: `CTRL_REV.csv`) |
| Table S9 | Randomization tests | 59, 58, 55 | `T_rev_perm_strat.csv` (replicates: `CTRL_PERM_STRAT.csv`), `T_rev_perm_null.csv` (`CTRL_PERM.csv`), `T_rev_controls.csv` |
| Table S10 | Intervals, minimum detectable difference, groups needed | 51 | `T_rev_power.csv` |
| Table S11 | Influence of single groups | 61 | `T_rev_influence.csv`, `T_rev_influence_se.csv` |
| Table S12 | Scenario information | 53 (fits), 54 | `T_rev_scenario.csv`, `T_rev_scenario_contrast.csv` |
| Table S13 | Dose reference | 60 | `T_rev_dose.csv`, `T_rev_dose_contrast.csv` |
| Table S14 | Other bins and held out units | 52 | `T_rev_tm_bins.csv`, `T_rev_tm_units.csv` |
| Table S15 | 99 features; recording holdout | 10, 11, 14 (fits); 20 | `T_original99.csv`, `T_full99_mlp.csv`, `T_loro.csv` |
| Table S16 | Label at severity 2 or more; persistence rules; merged grouping; validated window; seeds | 60, 23, 20, 13, 12 | `T_rev_label2.csv`, `T_constants.csv`, `T_merged.csv`, `T_nested_w.csv`, `T_sup_seeds.csv` |
| Table S17 | Time only models (negative controls on the real data) | 25 | `T_lpgo_atime.csv` |
| Table S18 | Further quantities of the controls | 16 | `T_controls.csv` |
| Table S19 | Detection rates of the trait control with intervals | 61 | `T_rev_control_ci.csv` |
| Table S20 | Null replicates of the randomization test | 59 | `T_rev_perm_strat.csv` |
| Table S21 | Onset timing | 60 | `T_rev_onset.csv`, `T_rev_onset_paired.csv` |
| Table S22 | Predictive values across prevalence | 20 | `T_deploy.csv`, `T_primary.csv` |
| Table S23 | Prior shift transfer | 13 | `T_prior_shift.csv` |
| Table S24 | Severity errors | 20, 24 | `T_severity.csv`, `T_asev_paired.csv` |
| Table S25 | Severity ranking per group | 21, 24 | `T_asev_by_group.csv` |
| Table S26 | Severity ranking matched on elapsed time | 56 | `T_rev_severity.csv` |
| Fig. S1 | Smoothing window and nested feature analysis | 20, 30 | `figures/fig5_temporal.png` |
| Fig. S2 | Severity at controlled operating points | 20, 24, 30 | `figures/fig4_severity.png` |

Numbers quoted in the text: `reference/paper_numbers.csv` (268) and `reference/paper_numbers_revision.csv` (70) give,
for each number, its location and the expression that recomputes it from `outputs/tables`.

`docs/METHODS_TO_CODE.md` says where each element of the method is implemented. `docs/RESULTS_MAP.md` and the
repository `README` text quoted in `docs/` use the table numbers of earlier drafts in places; the tables above are the
ones that match the final documents.

## 6. Seeds and determinism

Seeds are fixed: 42 for the detectors (1 and 2 for the seed analysis), 0 for the bootstrap and the random split,
`[2026, signal, round(1000 δ), replicate]` for the controls of step 16, `[2027, …]` for step 55, `[2028, replicate]`
for step 58 and `[2029, replicate]` for step 59. The logistic regression on the 76 features
depends slightly on the number of BLAS threads; `run_all.py` pins it to 2, the value of the primary run. The pair
models of step 15 were fitted with 2 threads for the first 14 pairs and 1 thread afterwards, and step 15 reproduces
that setting (`docs/AUDIT.md`, section 3).

## 7. Provenance of the code

The model fitting code of the primary run (`src/csp/data.py`, `design.py`, `metrics.py`, `metrics_extra.py`,
`inference.py`, `paths.py` and steps 00 to 26) is identical to the release of the first submission (the first commit
of this repository, `2dbc62d`). The 233 primary prediction files match the checksums recorded at that release
(`reference/predictions_sha256.txt`). Steps 50 to 62, `src/csp/revision.py` and `si_revision.py` were added in
revision.

Three small changes were made to existing files when the reproducibility audit was prepared. None of them computes a
result:

- `pipeline/40_verify.py`: one line sets the output encoding, because the report stopped with an encoding error on
  Windows when written to a file.
- `pipeline/57_rev_verify.py`: the response letter check is skipped when the letter is absent, instead of failing.
- `CITATION.cff`: title of the revised paper.

The scripts that built the Word documents and the logs of the original runs are kept by the authors and are available
from the corresponding author on request.

## 8. Limitations

- The primary models were not refitted in the primary environment for this repository. That refit was done once, before
  the revision, and is recorded in `docs/AUDIT.md`.
- The steps added in revision (50 to 62) were never committed to version control. Their fitting code could therefore
  not be compared with an earlier recorded version; it was checked by rerunning it (see the audit).
- The long experiments (steps 55, 58 and 59) were rerun for a sample of replicates only.
- Reinforcement learning detectors of the authors' companion manuscript are not part of this paper or this repository.
- The dataset identifies no participants. Everything here inherits that limitation (manuscript, Section VI-C).

## 9. Licence and citation

Code: MIT (`LICENSE`). Data: UFFCSData, AGPL-3.0 (`data/raw/UFFCSData_LICENSE`). Please cite the paper
(`CITATION.cff`).
