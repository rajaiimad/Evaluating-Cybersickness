"""Supporting Information Tables S8 to S18 and S22 to S25 (analyses added after the primary analysis was fixed): label, title, header, rows, note and column widths,
built from outputs/tables. Used by pipeline/31_paper_tables.py (regenerated tables for 40_verify) and by
tools/revision/revise_si.py (the printed tables)."""
import re
import numpy as np, pandas as pd
from csp.paths import TABLES as TAB

# Supporting Information tables are printed in order of first citation in the main text. Internal names (the order in
# which the analyses were added; file and function names of the code) map to printed numbers here, and nowhere else.
import json as _json, pathlib as _pl
_ORDER_FILE = _pl.Path(__file__).resolve().parents[2] / "reference" / "si_order.json"          # written by condense_manuscript.py
SI_ORDER = _json.loads(_ORDER_FILE.read_text(encoding="utf-8"))["tables"]
SI_NUM = {k: f"S{i + 1}" for i, k in enumerate(SI_ORDER)}
_REF = re.compile(r"\b(Tables?|TABLE) S(\d+)\b(?:(\s+and\s+)S(\d+)\b)?")


def si_relabel(text):
    """Internal SI table names to printed numbers in a string (‘Table S10’, ‘Tables S8 and S12’, ‘TABLE S8’)."""
    assert not re.search(r"Tables? S\d+ to S\d+", text), text
    def r(m):
        out = f"{m.group(1)} {SI_NUM['S' + m.group(2)]}"
        return out + (f"{m.group(3)}{SI_NUM['S' + m.group(4)]}" if m.group(4) else "")
    return _REF.sub(r, text)

SUP = ["RF", "GB", "RF+GB", "LR", "MLP"]


def f3(x):
    return "" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.3f}".replace("-", "−")
def s3(x): return "0.000" if abs(x) < 0.0005 else ("+" if x >= 0 else "−") + f"{abs(x):.3f}"
def ci(lo, hi): return f"[{f3(lo)}, {f3(hi)}]"
def pc(x):   # half up, as the main tables (pipeline/31_paper_tables.py): 0.105 prints as 11%, not 10%
    from decimal import Decimal, ROUND_HALF_UP
    return f"{Decimal(str(round(100 * x, 6))).quantize(Decimal('1'), ROUND_HALF_UP)}%"


def si_tables():
    T = []

    def _add(label, title, header, rows, note, widths=None):
        T.append(dict(label=label, title=title, header=header, rows=[[str(c) for c in r] for r in rows], note=note,
                      widths=widths))

    # S8 power
    PW = pd.read_csv(TAB / "T_rev_power.csv").set_index("model")
    rows = [[m, s3(r.dmcc), ci(r.ci_lo, r.ci_hi), ci(r.ci_nb_lo, r.ci_nb_hi), f3(r.mde), f3(r.mde_nb), int(r.n010),
             int(r.n010_nb)] for m, r in PW.iterrows()]
    _add("TABLE S8", "Intervals and power of the fold MCC comparison with the clock (16 two class folds)",
                   ["Detector", "ΔMCC", "95% CI", "95% CI, corrected", "MDD", "MDD, corrected", "Groups for 0.10",
                    "Groups for 0.10, corrected"], rows,
                   "ΔMCC: detector minus clock fold MCC at the primary rule. 95% CI: paired t interval. Corrected: variance "
                   f"multiplied by (1/16 + ρ)/(1/16) = {PW.inflation.iloc[0]:.2f}, ρ = mean n_test/n_train = {PW.rho.iloc[0]:.3f} "
                   "(Nadeau and Bengio). MDD: minimum detectable difference at 80% power, two sided 5%, central t "
                   "approximation. Groups for 0.10: two class groups needed to detect a true difference of 0.10.", widths=[1000, 900, 1600, 1600, 900, 1000, 1200, 1400])

    # S9 smoothing window gap
    TG = pd.read_csv(TAB / "T_rev_tau_grid.csv"); rows = []
    for tau in sorted(TG.tau.unique()):
        for w in sorted(TG.w.unique()):
            g = TG[(TG.tau == tau) & (TG.w == w)].set_index("model")
            rows.append([f"{tau:g}", f"{int(w)}" + (" (primary rule)" if (w, tau) == (61, 0.5) else "")]
                        + [s3(g.loc[m, "dmcc"]) for m in SUP] + [f3(g.clock.iloc[0]), f3(g.clock_alarm.iloc[0])])
    rk = TG.groupby("model").rank_primary.first(); a61 = TG[TG.w == 61]
    _add("TABLE S9", "Detector minus clock fold MCC over smoothing windows and thresholds (16 two class folds; exploratory)",
                   ["Threshold", "w"] + SUP + ["Clock fold MCC", "Clock alarm rate"], rows,
                   "The rows with threshold 0.5 are the window sweep: paired tests for those cells are in Table S1 (w = 61: Table "
                   "IV of the main text), and for RF, GB and RF+GB the difference is largest at the primary window w = 61. The "
                   "other thresholds were added after the primary analysis from the saved held out predictions; no model was "
                   "refitted, no cell was tested, and the grid uses the held out groups of the primary analysis, so it must not "
                   "be used to choose a rule. The primary rule (w = 61, threshold 0.5) is unchanged. Rank of the primary rule "
                   "among the 30 combinations (1 = largest difference): "
                   + ", ".join(f"{m} {int(rk[m])}" for m in SUP) + ". A common threshold gives the models different alarm "
                   "rates. At w = 61 the pooled alarm rate falls from "
                   + "; ".join(f"{a61[(a61.model == m) & (a61.tau == 0.3)].alarm.iloc[0]:.3f} to "
                               f"{a61[(a61.model == m) & (a61.tau == 0.7)].alarm.iloc[0]:.3f} ({m})" for m in SUP)
                   + " as the threshold rises from 0.3 to 0.7. The differences at high thresholds grow mainly because the fold "
                   "MCC of the clock falls, not because the detectors improve.",
                   widths=[900, 1500, 900, 900, 900, 900, 900, 1300, 1400])

    # S10 parts and learner matched contrasts
    PA = pd.read_csv(TAB / "T_rev_tm_parts.csv").set_index("model"); LM = pd.read_csv(TAB / "T_rev_tm_learner.csv")
    COV = pd.read_csv(TAB / "T_rev_tm_coverage.csv"); c30 = COV[(COV.bin_s == 30) & (COV.min_n == 20)].iloc[0]
    rows = [[m, s3(r.d_full) + " " + ci(r.d_full_lo, r.d_full_hi), s3(r.d_within) + " " + ci(r.d_within_lo, r.d_within_hi),
             s3(r.d_between) + " " + ci(r.d_between_lo, r.d_between_hi)] for m, r in PA.iterrows()]
    rows += [[r.contrast, s3(r.d_full) + " " + ci(r.d_full_lo, r.d_full_hi), s3(r.d_within) + " " + ci(r.d_within_lo, r.d_within_hi),
              s3(r.d_between) + " " + ci(r.d_between_lo, r.d_between_hi)] for r in LM.itertuples()]
    _add("TABLE S10", "Within group and between group parts of the LPGO time matched AUC, minus elapsed time",
                   ["Model or contrast", "Full", "Within group", "Between group"], rows,
                   f"Ten 30 s bins with at least 20 positive and 20 negative windows ({int(c30.windows_kept):,} of "
                   f"{int(c30.windows):,} windows); {100 * (1 - c30.within_share):.1f}% of the window pairs compare two "
                   "different groups. Within group pairs are scored by one LOGO model, between group pairs by the LPGO model "
                   f"trained without both groups. Elapsed time scores {f3(PA.full_ref.iloc[0])} (full), "
                   f"{f3(PA.within_ref.iloc[0])} (within) and {f3(PA.between_ref.iloc[0])} (between). Intervals: the 1,000 "
                   "shared group bootstrap resamples of Table IV; they omit training variability (main text, Section V-E). "
                   "Last two rows: learner matched contrasts (exploratory), the detector minus the same learner fitted on "
                   "elapsed time alone, both scored with LPGO.", widths=[2600, 2330, 2330, 2340])

    # S11 bins and units
    B = pd.read_csv(TAB / "T_rev_tm_bins.csv"); U = pd.read_csv(TAB / "T_rev_tm_units.csv")
    rows = []
    for (bs, mn), g in B.groupby(["bin_s", "min_n"]):
        g = g.set_index("model"); rows.append([f"{bs} s bins, at least {mn}" + (" (primary)" if (bs, mn) == (30, 20) else "")]
                                              + [s3(g.loc[m, "d_full"]) for m in SUP])
    for des, lab in (("loro", "LORO"), ("merged", "Merged grouping")):
        u = U[U.design == des].set_index("model")
        rows.append([f"{lab}, pooled"] + [s3(u.loc[m, "d_pooled"]) for m in SUP])
        rows.append([f"{lab}, within unit"] + [s3(u.loc[m, "d_within"]) for m in SUP])
    lo_share = U[U.design == "loro"].within_share.iloc[0]
    _add("TABLE S11", "Time matched AUC minus elapsed time with other bins and other held out units",
                   ["Setting"] + SUP, rows,
                   "Rows 1 to 9: LPGO scoring under LOGO with bins of 15, 30 or 60 s and a minimum of 10, 20 or 40 positive "
                   "and negative windows per bin. LORO and merged grouping: no pair models exist, so the pooled measure (every "
                   "window keeps its held out score, biased downward for time only models, main text Section V-E) and the "
                   f"within unit part are shown; under LORO only {100 * lo_share:.1f}% of the pairs fall within one recording. "
                   "Intervals are in outputs/tables/T_rev_tm_units.csv of the code release.")

    # S12 scenario information
    RF_ = pd.read_csv(TAB / "T_rev_refit_vs_shipped.csv")
    REFTOL = np.ceil(1000 * max((RF_.mcc_refit - RF_.mcc_shipped).abs().max(), (RF_.tm_lpgo_refit - RF_.tm_lpgo_shipped).abs().max())) / 1000
    S = pd.read_csv(TAB / "T_rev_scenario.csv").set_index("model"); SC = pd.read_csv(TAB / "T_rev_scenario_contrast.csv")
    rows = [[m, f3(r.mcc), s3(r.dmcc), f"{r.p_w:.3f}", s3(r.d_full) + " " + ci(r.d_full_lo, r.d_full_hi), s3(r.d_within),
             s3(r.d_between)] for m, r in S.iterrows()]
    con = "; ".join(f"{r.contrast}: {s3(r.d_full)} {ci(r.lo, r.hi)}" for r in SC.itertuples())
    _add("TABLE S12", "Scenario information: detectors with and without the condition and game indicators, "
                   "and a time and scenario reference (refitted in the second environment of Appendix B)",
                   ["Model", "Fold MCC", "ΔMCC", "Wilcoxon p", "ΔAtime LPGO [95% CI]", "Within", "Between"], rows,
                   "No scenario: the 76 primary features without the 7 condition indicators and the 3 field of view means (66 "
                   "features). Time and scenario: elapsed time, the 7 condition indicators and the field of view (one feature; "
                   "it identifies the game). RF, GB, RF+GB and LR with 76 features were refitted here so that both arms of each "
                   f"contrast come from one environment; the refits of this table match the reported fold mean MCC and LPGO time matched AUC to within {REFTOL:.3f} "
                   f"(the note on hyperparameters and reproduction gives the bound over all refits of the second environment). Contrasts: {con}.",
                   widths=[2400, 900, 900, 1000, 2200, 1100, 1100])

    # S13 controls with the detectors' own learners (step 55; skipped while it has not run)
    if (TAB / "T_rev_controls.csv").exists():
        C = pd.read_csv(TAB / "T_rev_controls.csv")
        rows = [[r.learner, {"trait": "trait", "state_ar": "state, AR(1) noise"}[r.kind], f"{r.delta:g}", int(r.reps), s3(r.dl),
                 pc(r.power_lpo), pc(r.below_lpo), pc(r.power_cal), pc(r.power_t)] for r in C.itertuples()]
        nul = C[C.delta == 0]
        nn = "; ".join(f"{r.learner} {dict(trait='trait', state_ar='state')[r.kind]}: threshold {f3(r.t_cal)}, null SD {f3(r.null_sd)}, mean bootstrap SE {f3(r.null_mean_se)}"
                       for r in nul.itertuples())
        _add("TABLE S13", "Positive and negative controls run with the detectors' own learners on elapsed time and "
                       "a synthetic feature",
                       ["Learner", "Signal", "δ", "Replicates", "Mean ΔAtime LPGO", "Detected", "Below", "Detected, null threshold",
                        "MCC t test"], rows,
                       "Learners with the hyperparameters of the panel, fitted on elapsed time and z under LOGO and LPGO; GB and LR were "
                       "run with and without a signal, the RF without a signal only (its null thresholds). Trait: "
                       "as in Table VI. State, AR(1) noise: z(t) = δ y(t) + e(t) with e(t) a stationary AR(1) process within each "
                       "recording (φ = 0.9, unit variance). Detected: lower 95% bootstrap limit above zero; Below: upper limit "
                       "below zero; null threshold: LPGO difference above the 97.5th percentile of the same learner's null "
                       f"replicates; MCC t test: paired t p < 0.05 with a positive difference. Null replicates: {nn}. The LR rows repeat the "
                       "trait control of Table VI with the same learner, with independent replicates (100 without and 50 with a "
                       "signal, against 200) and in the second software environment; the two runs differ by replicate noise, so "
                       "the detection rates of Table VI carry the uncertainty stated in Section V-E.",
                       widths=[800, 1500, 600, 900, 1300, 1000, 900, 1300, 1300])

    # S14 time matched severity
    SV = pd.read_csv(TAB / "T_rev_severity.csv")
    pg = SV[SV.analysis == "time matched A_sev by group"]
    rows = [[f"Group {int(r.group)}", f"{int(r.pairs):,}", pc(r.same_recording_share)] + [f3(r[m]) for m in SUP + ["Clock"]]
            for _, r in pg.iterrows()]
    pool = SV[SV.analysis == "time matched A_sev"].set_index("model"); eq = SV[SV.analysis == "time matched A_sev, equal group weights"].set_index("model")
    rows.append(["Pooled", f"{int(pool.pairs.iloc[0]):,}", ""] + [f3(pool.loc[m, "a_sev"]) for m in SUP] + [f3(pool.ref.iloc[0])])
    rows.append([f"Equal weights, {int(eq.groups.iloc[0])} groups", "", ""] + [f3(eq.loc[m, "a_sev"]) for m in SUP] + [f3(eq.ref.iloc[0])])
    _add("TABLE S14", "Severity ranking matched on elapsed time: severity 3 against severity 1 windows of the "
                   "same group in the same 30 s bin (smoothed score, primary design)",
                   ["Group", "Pairs", "Same recording"] + SUP + ["Elapsed time"], rows,
                   "0.5 indicates no ordering. Elapsed time ranks the windows of a bin by time. Same recording: share of the "
                   "group's matched pairs whose two windows come from one recording; in the other pairs the statistic ranks "
                   "one recording against another, which is why several detectors take identical values. Pooled weights each "
                   "group by its pairs. Equal weights: mean over the groups with at least 30 pairs. Pooled differences from "
                   "elapsed time with 4,000 group bootstrap resamples: "
                   + "; ".join(f"{m} {s3(pool.loc[m, 'diff'])} {ci(pool.loc[m, 'lo'], pool.loc[m, 'hi'])}" for m in SUP)
                   + ". With six groups the bootstrap is unreliable and these intervals are not interpreted (Section V-B).",
                   widths=[1300, 800, 900] + [1000] * 6 + [1100])

    # S15 calibrations of the time matched advantage of the real detectors (steps 55, 58, 59)
    PS_ = pd.read_csv(TAB / "T_rev_perm_strat.csv").set_index("learner")
    PN = pd.read_csv(TAB / "T_rev_perm_null.csv").set_index("learner")
    C = pd.read_csv(TAB / "T_rev_controls.csv")
    thr = lambda l, k: C[(C.learner == l) & (C.kind == k) & (C.delta == 0)].t_cal.iloc[0]
    rows = []
    for m in SUP:
        r = PS_.loc[m]
        rows.append([m, s3(PA.loc[m, "d_full"]) + " " + ci(PA.loc[m, "d_full_lo"], PA.loc[m, "d_full_hi"]), s3(r.observed),
                     f"{int(r.reps)}", f3(r.null_mean), f3(r.null_q975), f"{r.p_perm:.3f} [{r.p_mc_lo:.3f}, {r.p_mc_hi:.3f}]",
                     f"{r.p_perm_bh:.3f}", f"{r.p_perm_between:.3f}", f"{r.p_perm_within:.3f}",
                     f"{PN.loc[m, 'p_perm']:.3f}" if m in PN.index else "",
                     (f3(thr(m, "trait")) + " / " + f3(thr(m, "state_ar"))) if m in ("RF", "GB") else ""])
    _add("TABLE S15", "Randomization tests and null thresholds for the time matched advantage of the real detectors: LPGO time matched AUC minus "
                   "elapsed time against refitted randomization nulls and one feature null thresholds",
         ["Detector", "Observed, primary fits [bootstrap CI]", "Observed, refit", "Replicates", "Null mean", "Null 97.5%",
          "p [Monte Carlo 95% CI]", "Adjusted p (BH)", "Between-group p", "Within-group p", "p, all features reassigned",
          "One feature thresholds (trait / state)"], rows,
         "Exploratory test (within game randomization): in each replicate the 65 feature trajectories that are neither elapsed "
         "time, a condition indicator nor a field of view mean (63 telemetry features and the two cumulative exposure "
         "features) are reassigned between recordings of the same game; the recordings of 302 or 303 windows are permuted among themselves and each shorter recording "
         "receives the first windows of a randomly drawn long recording of its game (a 302 window donor given to a 303 "
         "window recording repeats its last row); the donor keeps its own place, so its trajectory occurs twice in the "
         "replicate; elapsed time, the condition indicators and the field of view stay the recording's own. The scheme is "
         "not an exact permutation for the shorter recordings; its level, measured with the control detector on pure noise "
         "data, is close to the nominal 5% (Section V-D of the main text; Table S18), and its calibration for the 76 feature "
         "learners is not established. Each detector is refitted under LOGO and LPGO with the hyperparameters of the panel; RF+GB "
         "averages the RF and GB of the same replicate. Observed, refit: the same code with the identity assignment, in "
         "the environment of the null replicates. Replicates are added until 10 reach the observed value (p = 10 / "
         "replicates) or 200 are run (p = (1 + k) / 201), following Besag and Clifford; Monte Carlo 95% CI: Clopper "
         "Pearson interval of the exceedance share. BH: Benjamini and Hochberg over the five detectors; the test is one sided "
         "at the 5% level. Between-group p, within-group p: the same replicates for the two parts; these ten "
         "values are descriptive, unadjusted and outside the adjusted family. Table III of the main text reports the same "
         "run of this test, with identical adjusted values. p, all features reassigned: a coarser variant in which all 76 "
         "features are reassigned between recordings of both games (40 replicates, RF and GB only; null means "
         + ", ".join(f"{l} {f3(PN.loc[l, 'null_mean'])}" for l in PN.index) + "). One feature thresholds: 97.5th "
         "percentile of the null replicates of the controls run with the detector's own learner on elapsed time and one "
         "synthetic feature (Table S13); they do not apply to detectors with 76 features and are shown for comparison.",
         widths=[700, 1250, 800, 850, 600, 650, 1150, 750, 750, 700, 850, 950])

    # S16 onset timing within recordings (step 60)
    ON = pd.read_csv(TAB / "T_rev_onset.csv").set_index("model"); OP = pd.read_csv(TAB / "T_rev_onset_paired.csv").set_index("model")
    sec = lambda x: f"{x:+.0f}".replace("-", "−")
    rows = []
    for m in SUP + ["Clock"]:
        r = [m, f"{ON.loc[m, 'median_abs_err']:.0f}", sec(ON.loc[m, "median_err"]), pc(ON.loc[m, "before_onset"]), pc(ON.loc[m, "missed"])]
        if m in OP.index:
            o = OP.loc[m]
            r += [f"{sec(o.d_abs_err)} [{sec(o.lo)}, {sec(o.hi)}]", f"{o.mdd:.0f}", f"{int(o.groups_better)} of {int(o.groups)}",
                  f"{o.p_w:.3f}", f"{o.p_w_bh:.3f}"]
        else:
            r += ["", "", "", "", ""]
        rows.append(r)
    _add("TABLE S16", "Onset timing within recordings at the primary rule (26 recordings that become positive)",
         ["Detector", "Median |error| (s)", "Median error (s)", "Alarm before onset", "No alarm",
          "Δ mean |error| vs clock (s) [95% CI]", "MDD (s)", "Groups better", "Wilcoxon p", "BH p"], rows,
         "Error: elapsed time of the first window predicted positive in the recording (trailing mean over 61 windows, "
         "threshold 0.5) minus that of its first positive window; negative values are alarms before onset. A recording "
         "without any alarm is a miss and counts with the error of its last window. Δ: detector minus clock in the mean absolute "
         "error per group, averaged over the groups with an onset recording; interval from 10,000 group bootstrap "
         "resamples; the intervals are unadjusted, and that of LR excludes zero. MDD: minimum detectable difference at 80% "
         "power (two sided 5%, paired t over the 16 groups). Groups better: groups in which the detector's error is smaller "
         "than the clock's. Shipped primary predictions; no refit.", widths=[800, 900, 900, 900, 700, 1700, 700, 900, 800, 700])

    # S17 dose reference (step 60)
    DS = pd.read_csv(TAB / "T_rev_dose.csv").set_index("model"); DC = pd.read_csv(TAB / "T_rev_dose_contrast.csv")
    rows = [[m, f3(r.mcc), s3(r.dmcc), f"{r.p_w:.3f}", s3(r.d_full) + " " + ci(r.d_full_lo, r.d_full_hi), s3(r.d_within),
             s3(r.d_between)] for m, r in DS.iterrows()]
    rows += [[r.contrast, "", s3(r.dmcc), f"{r.p_w:.3f}", s3(r.d_full) + " " + ci(r.lo, r.hi), "", ""] for r in DC.itertuples()]
    _add("TABLE S17", "Dose reference: models on elapsed time and the two cumulative exposure features, and the detectors "
                      "minus these references",
         ["Model or contrast", "Fold MCC", "ΔMCC", "Wilcoxon p", "ΔAtime LPGO [95% CI]", "Within", "Between"], rows,
         "Dose reference: LR or GB on elapsed time and the expanding means of |rotX| + |rotY| + |rotZ| and of |acceleration| "
         "(Table S21), fitted under LOGO and with the 216 LPGO pair models. First rows: ΔMCC against the clock (16 two "
         "class folds) and ΔAtime against elapsed time. Contrast rows: detector (76 features, refitted in the same "
         "environment, Table S12) minus the reference, on fold MCC and on the LPGO time matched AUC. Group bootstrap "
         "intervals omit training variability.", widths=[2400, 900, 900, 1000, 2200, 1100, 1100])


    # S22 label threshold, label persistence and merged grouping (steps 60, 23, 21)
    L2 = pd.read_csv(TAB / "T_rev_label2.csv").set_index("model"); KC = pd.read_csv(TAB / "T_constants.csv").set_index("name").value
    PRI = pd.read_csv(TAB / "T_primary.csv").set_index("model"); MG = pd.read_csv(TAB / "T_merged.csv").set_index("model")
    rows = [["Label at severity 2 or more", m, f3(r.mcc), f3(r.clock), s3(r.dmcc) + " " + ci(r.lo, r.hi), f"{r.p_w:.3f}",
             f"{int(r.two_class_groups)} groups"] for m, r in L2.iterrows()]
    rows += [["Label persistence rule", lab, f3(KC[k]), f3(PRI.loc["Clock", "mcc"]), s3(KC[k] - PRI.loc["Clock", "mcc"]), "", "16 groups"]
             for lab, k in (("Previous label", "persist_prev"), ("Majority of the previous 61 labels", "persist_major61"))]
    rows += [["Merged grouping (20 groups)", m, f3(MG.loc[m, "mcc"]), f3(PRI.loc[m, "mcc"]), s3(MG.loc[m, "mcc"] - PRI.loc[m, "mcc"]), "",
              f"{int(MG.loc[m, 'n_two_class'])} groups"] for m in SUP + ["Clock"]]
    NWT = pd.read_csv(TAB / "T_nested_w.csv").set_index("model"); SDS = pd.read_csv(TAB / "T_sup_seeds.csv")
    rows += [["Smoothing window chosen on validation groups", m, f3(NWT.loc[m, "mcc"]), f3(NWT.loc["Clock", "mcc"]),
              s3(NWT.loc[m, "mcc"] - NWT.loc["Clock", "mcc"]), "", f"{int(NWT.loc[m, 'n'])} groups"] for m in SUP]
    rows += [[f"Seed {int(r.seed)}", r.model, f3(r.mcc), f3(PRI.loc["Clock", "mcc"]), s3(r.mcc - PRI.loc["Clock", "mcc"]), "", "16 groups"]
             for r in SDS[SDS.seed != 42].itertuples() if r.model != "GB"]
    RC = pd.read_csv(TAB / "T_rev_recording.csv").set_index("model"); TV = pd.read_csv(TAB / "T_rev_tau_val.csv")
    rows += [["Per recording scoring, mean over recordings", m, f3(r.mcc_rec), f3(r.clock_rec), s3(r.d_rec), f"{r.p_w_rec:.3f}",
              f"{int(r.recordings)} recordings"] for m, r in RC.iterrows()]
    rows += [["Per recording scoring, mean over groups", m, "", "", s3(r.d_grp) + " " + ci(r.lo, r.hi), f"{r.p_w:.3f}",
              f"{int(r.groups)} groups"] for m, r in RC.iterrows()]
    for v, lab in (("tau", "Threshold chosen on validation groups"), ("w and tau", "Window and threshold chosen on validation groups")):
        tv = TV[TV.variant == v].set_index("model")
        rows += [[lab, m, f3(tv.loc[m, "mcc"]), f3(tv.loc["Clock", "mcc"]), s3(tv.loc[m, "d"]) + " " + ci(tv.loc[m, "lo"], tv.loc[m, "hi"]),
                  f"{tv.loc[m, 'p_w']:.3f}", f"{int(tv.loc[m, 'n'])} groups"] for m in SUP]
    SPL = pd.read_csv(TAB / "T_rev_spline_clock.csv").set_index("model")
    rows += [["Spline clock as reference", m, f3(r.mcc), f3(r.ref_mcc), s3(r.d) + " " + ci(r.lo, r.hi), f"{r.p_w:.3f}",
              f"{int(r.n)} groups"] for m, r in SPL.iterrows()]
    OCT = pd.read_csv(TAB / "T_rev_october.csv")
    for sub, lab, unit in (("december position-free (LOGO)", "Position-free detectors, merged file (LOGO)", "groups"),
                           ("all", "Position-free detectors, unmerged sessions", "profiles"),
                           ("new profiles", "Position-free detectors, unmerged sessions in new profiles", "profiles")):
        rows += [[lab, r.model, f3(r.mcc), f3(r.clock), s3(r.d) + " " + ci(r.lo, r.hi), f"{r.p_w:.3f}", f"{int(r.two_class)} {unit}"]
                 for r in OCT[OCT.subset == sub].itertuples()]
    tvt = TV[TV.variant == "tau"].set_index("model"); tvw = TV[TV.variant == "w and tau"].set_index("model")
    l2 = L2.iloc[0]
    _add("TABLE S22", "Label threshold check, label persistence rules, merged grouping, smoothing window chosen on validation groups, seeds, per recording scoring, threshold chosen on validation groups and a spline clock: MCC",
         ["Analysis", "Model", "Fold mean MCC", "Reference", "Difference [95% CI]", "Wilcoxon p", "Two class units"], rows,
         f"Label at severity 2 or more: detectors and the clock refitted under LOGO on the binary label s ≥ 2 ({int(l2.episodes)} "
         f"positive episodes in {int(l2.recordings)} recordings); reference: the clock on this label; paired t interval and "
         "Wilcoxon test over the groups with both classes, unadjusted. RF+GB is the mean of the RF and GB probabilities; "
         "the MLP, the detector least stable across seeds, was not refitted on this label. Label persistence rules read "
         "the ground truth of the preceding windows and are upper references, not detectors; reference: the clock of the "
         "primary analysis. Merged grouping: LOGO over 20 groups after merging the two cases in which a short recording was "
         "restarted with different descriptors; reference: the same model under the primary grouping of 22 groups, so the difference shows how much the "
         "merge changes each fold mean. Smoothing window chosen on validation groups: the window is chosen in each fold on "
         "three validation groups; reference: the clock with its own chosen window. Seed 1 and seed 2: the stochastic "
         "detectors refitted (GB gives the same predictions at every seed); reference: the clock. Tests of these rows "
         "against the clock are in Table S1. Per recording scoring: the MCC of the primary rule within each of the "
         f"{int(RC.recordings.iloc[0])} recordings with both classes, from the primary LOGO predictions (the models are unchanged; only the "
         "scoring unit changes); reference: the clock scored in the same way. Mean over recordings: Wilcoxon test over "
         "the recordings, which are not independent within a group. Mean over groups: the recording differences are "
         "averaged within each group first; paired t interval and Wilcoxon test over the groups (smallest p adjusted "
         f"over the five detectors {RC.p_w_bh.min():.3f}). Threshold chosen on validation groups: in each fold the threshold is chosen from "
         "0.3, 0.4, 0.5, 0.6 and 0.7 by the pooled MCC on the three validation groups, which are scored by models refitted on "
         "the other 18 training groups, so that the held out group affects neither these models nor the choice; the "
         "window is fixed at 61 or chosen jointly with the threshold from the six values of Table S9. The chosen rule is "
         "applied to the held out group; every model and the "
         "clock get their own chosen rule; reference: the clock with its own chosen rule (pooled alarm rate "
         f"{tvt.loc['Clock', 'alarm']:.3f} and {tvw.loc['Clock', 'alarm']:.3f}; its chosen threshold is 0.3 in the median fold). Paired t interval and Wilcoxon "
         f"test over the 16 folds; smallest p adjusted over the five detectors {tvt.p_w_bh.min():.3f} and {tvw.p_w_bh.min():.3f}. Both analyses were "
         "added after the primary analysis from saved predictions; no model was refitted, and the primary rule is unchanged. "
         "Position-free detectors: the 76 primary features minus the 21 computed from player position (55 features), "
         "with the learners, hyperparameters and rule of the primary analysis, added after the primary analysis. Merged file: LOGO; "
         "reference: the clock of the primary analysis. Unmerged sessions: the 25 raw-archive sessions with at least 250 windows "
         "that are not in the merged file, scored by models fitted once on all 35 merged recordings and grouped by descriptor "
         "profile; reference: the clock fitted on the merged recordings; new profiles: the sessions whose descriptor profile does "
         "not occur in the merged file. Paired t interval and Wilcoxon test over the two class units, unadjusted. "
         "Spline clock as reference: a class balanced logistic regression on a cubic spline basis of elapsed time (five knots set "
         "before fitting, linear extrapolation), fitted under LOGO with the scaling and rule of the primary analysis and "
         f"added after the primary analysis (fold mean MCC {f3(SPL.loc['Clock', 'ref_mcc'])}, alarm rate {f3(SPL.ref_alarm.iloc[0])} averaged over the 16 folds); "
         "paired t interval and Wilcoxon test over the 16 folds, unadjusted; adjusted over the five detectors, "
         f"LR {f3(SPL.loc['LR', 'p_w_bh5'])} and MLP {f3(SPL.loc['MLP', 'p_w_bh5'])}.",
         widths=[2400, 2300, 1000, 900, 1700, 900, 1100])

    # S23 influence of single groups on the time matched advantage (step 61)
    INF = pd.read_csv(TAB / "T_rev_influence.csv", dtype={"group": str})
    rows = [["All 22 groups" if r.group == "all" else f"Without group {r.group}", str(int(r.recordings)),
             "" if r.group == "all" else ("yes" if r.two_class else "no"), "" if r.group == "all" else f"{100 * r.pair_share:.1f}%"]
            + [s3(r[m]) for m in SUP] for _, r in INF.iterrows()]
    one = INF[INF.group != "all"]; JSE = pd.read_csv(TAB / "T_rev_influence_se.csv")
    _add("TABLE S23", "Influence of single groups: LPGO time matched AUC minus elapsed time with each reconstructed group removed in turn",
         ["Groups used", "Recordings", "Both classes", "Share of pairs"] + SUP, rows,
         "First row: the reported differences. Other rows: the same statistic with one group removed (its windows are "
         "dropped from every bin; bins are kept by the same rule on the remaining groups); no model is refitted. "
         "Recordings, both classes: of the removed group. Share of pairs: share of the matched window pairs that involve "
         "a window of the removed group. Range over the 22 removals: "
         + "; ".join(f"{m} {s3(one[m].min())} to {s3(one[m].max())}" for m in SUP) + ". Jackknife standard error of the "
         "difference from these 22 values: " + "; ".join(f"{r.model} {f3(r.jk_se)}" for r in JSE.itertuples())
         + ". It is close to the standard error implied by the group bootstrap intervals ("
         + "; ".join(f"{r.model} {f3(r.boot_se)}" for r in JSE.itertuples()) + "), so the table shows that no single "
         "group produces the point advantage, not that the advantage is established.",
         widths=[1900, 1000, 1000, 1100] + [920] * 5)

    # S24 diagnostics of the null replicates of the randomization test (step 59)
    rows = [[m, f"{int(r.reps)}", f3(r.null_q95), f3(r.null_q975), s3(r.observed),
             f"{int(r.null_above_k)} of {int(r.reps)} ({100 * r.null_above:.1f}%)",
             f"{int(r.null_below_k)} of {int(r.reps)} ({100 * r.null_below:.1f}%)", s3(r.observed_dmcc), s3(r.null_dmcc_mean),
             f"{r.p_perm_mcc:.3f}"] for m, r in PS_.loc[SUP].iterrows()]
    _add("TABLE S24", "Null replicates of the within game randomization test: critical values, coverage of the group bootstrap and fold MCC",
         ["Detector", "Replicates", "Null 95%", "Null 97.5%", "Observed, refit", "Bootstrap CI above zero", "Bootstrap CI below zero",
          "Observed ΔMCC", "Null mean ΔMCC", "p, fold MCC"], rows,
         "Replicates of Table S15. Null 95%, 97.5%: percentiles of the LPGO time matched AUC minus elapsed time in the "
         "null replicates; the 95th percentile is the unadjusted critical value of the one sided test at the 5% level. "
         "With the sequential rule the percentiles of LR and the MLP rest on few replicates. Bootstrap CI above (below) "
         "zero: null replicates whose 95% group bootstrap interval lies wholly above (below) zero, 2.5% expected on each "
         "side if the bootstrap were calibrated. ΔMCC: fold MCC minus the clock, observed (refit) and mean of the null "
         "replicates; p, fold MCC: share of null replicates that reach the observed value, a check that the telemetry "
         "is related to the labels and not a test of information beyond time.",
         widths=[800, 900, 800, 800, 900, 1500, 1500, 900, 900, 800])

    # S25 time only negative controls, pooled against LPGO scoring (step 25)
    LA = pd.read_csv(TAB / "T_lpgo_atime.csv").set_index("model")
    rows = [[lab, f3(LA.loc[k, "tm_pooled"]), s3(LA.loc[k, "d_pooled"]) + " " + ci(LA.loc[k, "d_pooled_lo"], LA.loc[k, "d_pooled_hi"]),
             f3(LA.loc[k, "tm_lpo"]), s3(LA.loc[k, "d_lpo"]) + " " + ci(LA.loc[k, "d_lpo_lo"], LA.loc[k, "d_lpo_hi"]),
             s3(LA.loc[k, "tm_pooled"] - LA.loc[k, "tm_lpo"])]
            for lab, k in (("Clock (LR on elapsed time)", "Clock"), ("RF on elapsed time", "RF time only"), ("GB on elapsed time", "GB time only"))]
    _add("TABLE S25", "Negative controls on the real data: time matched AUC of models fitted on elapsed time alone under pooled and LPGO scoring",
         ["Model", "Atime pooled", "Pooled minus elapsed time [95% CI]", "Atime LPGO", "LPGO minus elapsed time [95% CI]", "Pooled minus LPGO"], rows,
         f"Elapsed time itself scores {f3(LA.tm_ref.iloc[0])}. These models carry no information beyond time, so a difference "
         "from elapsed time that excludes zero is an artifact of the scoring. Pooled: every window keeps the score of its "
         "LOGO model. LPGO: pairs of windows from two groups are scored by the model trained without both. Intervals: 1,000 "
         "group bootstrap resamples.", widths=[2300, 1100, 2300, 1100, 2300, 1200])

    # S26 detection rates of the trait control of the main text with their uncertainty (step 61)
    CC = pd.read_csv(TAB / "T_rev_control_ci.csv"); TCL = pd.read_csv(TAB / "T_controls.csv")
    thr_state = TCL[(TCL.kind == "state") & (TCL.delta == 0)].t_cal.iloc[0]
    rows = [[f"LR control, {r.delta:g}", f"{int(r.reps)}", s3(r.mean_dl), f"{pc(r.power_boot)} [{pc(r.boot_lo)}, {pc(r.boot_hi)}]",
             f"{pc(r.power_cal)} [{pc(r.cal_lo)}, {pc(r.cal_hi)}]"] for r in CC.itertuples()]
    # the same trait signal added to the 76 features of the real RF and GB (step 65), exact binomial intervals
    from scipy.stats import binomtest
    CF = pd.read_csv(TAB / "T_rev_controls_full.csv")

    def cp(p, n):
        k = int(round(p * n)); c = binomtest(k, n).proportion_ci(method="exact"); return f"{pc(k / n)} [{pc(c.low)}, {pc(c.high)}]"
    rows += [[f"{r.learner} with 76 features, {r.delta:g}", f"{int(r.reps)}", s3(r.dl), cp(r.power_lpo, int(r.reps)),
              "reference" if r.delta == 0 else cp(r.power_cal_lpo, int(r.reps))] for r in CF[CF.kind == "trait"].itertuples()]
    cft = CF[CF.kind == "trait"].set_index(["learner", "delta"])
    ft = {(r.learner, r.delta): pc(round(r.power_t * r.reps) / r.reps) for r in CF[CF.kind == "trait"].itertuples()}
    lt = TCL[(TCL.learner == "LR") & (TCL.kind == "trait") & (TCL.delta > 0)].power_t
    _add("TABLE S26", "Detection rates of the trait control with 95% intervals (control detector of Table VI, 200 replicates per row, "
         "and the real RF and GB with the signal added to their 76 features, 20 or 30 replicates per row)",
         ["Detector, δ", "Replicates", "Mean ΔAtime LPGO", "Detected, bootstrap rule [95% CI]", "Detected, null threshold [95% CI]"], rows,
         f"Null thresholds: 97.5th percentile of the LPGO difference in the 200 replicates without a signal, {f3(CC.threshold.iloc[0])} "
         f"for the trait signal and {f3(thr_state)} for the state signal. Intervals: the replicates with a signal and, for "
         "the null threshold, the replicates without a signal are resampled with replacement 10,000 times; the threshold "
         "and the detection rate are recomputed in every draw, so the interval of the null threshold column includes the "
         "uncertainty of the threshold. The null threshold is a one sided 2.5% criterion; the randomization test of the "
         "real detectors is one sided at 5%. RF and GB with 76 features: the trait signal is added as a 77th feature and both "
         "detectors are refitted under LOGO and LPGO with the hyperparameters, rule and statistics of the primary analysis "
         "(added after the primary analysis). The 76 real features are the same in every replicate, so the "
         "replicates without a signal measure how much each real detector varies with the noise of z; their 97.5th "
         f"percentile is the null threshold for an added signal (GB {f3(cft.loc[('GB', 0.0), 'thr_lpo'])}, RF "
         f"{f3(cft.loc[('RF', 0.0), 'thr_lpo'])}), and the rows without a signal are the reference for it; exact binomial "
         "intervals. Fold MCC, with the same construction on the difference from the clock: GB "
         f"{pc(cft.loc[('GB', 1.5), 'power_cal_mcc'])} and {pc(cft.loc[('GB', 3.0), 'power_cal_mcc'])} at δ = 1.5 and 3, RF "
         f"{pc(cft.loc[('RF', 1.5), 'power_cal_mcc'])} at δ = 1.5; with the paired t test rule (p < 0.05 and a positive "
         f"difference) LR control at most {pc(lt.max())}, GB {ft[('GB', 1.5)]} and {ft[('GB', 3.0)]}, RF {ft[('RF', 1.5)]}.",
         widths=[1900, 1000, 1500, 2600, 2600])

    # S18 inventory of the interval estimates and tests of the analyses added after the primary analysis
    inv = []

    def fam(name, items, role):
        ex = [lab for lab, lo, hi in items if lo > 0 or hi < 0]
        inv.append([name, str(len(items)), str(len(ex)), "; ".join(ex) if ex else "none", role])
    fam("Detector minus clock, fold MCC (Table S8)", [(m, PW.loc[m, "ci_lo"], PW.loc[m, "ci_hi"]) for m in SUP],
        "interval of the primary comparison")
    fam("Parts of Atime (Table S10)", [(f"{m}, {pt}", PA.loc[m, f"d_{pt}_lo"], PA.loc[m, f"d_{pt}_hi"]) for m in PA.index
                                     for pt in ("full", "within", "between")], "descriptive")
    fam("Learner matched contrasts (Table S10)", [(r.contrast, r.d_full_lo, r.d_full_hi) for r in LM.itertuples()], "exploratory")
    fam("Scenario check (Table S12)", [(m, S.loc[m, "d_full_lo"], S.loc[m, "d_full_hi"]) for m in S.index]
        + [(r.contrast, r.lo, r.hi) for r in SC.itertuples()], "sensitivity")
    sv = SV[SV.analysis == "time matched A_sev"]
    fam("Time matched severity (Table S14)", [(r.model, r.lo, r.hi) for r in sv.itertuples()], "exploratory, not interpreted")
    fam("Onset error (Table S16)", [(m, OP.loc[m, "lo"], OP.loc[m, "hi"]) for m in OP.index], "exploratory")
    fam("Dose reference (Table S17)", [(m, DS.loc[m, "d_full_lo"], DS.loc[m, "d_full_hi"]) for m in DS.index]
        + [(r.contrast, r.lo, r.hi) for r in DC.itertuples()], "sensitivity")
    lowp = [r.contrast for r in DC.itertuples() if r.p_w < 0.05]
    if lowp: inv[-1][3] += "; fold MCC, Wilcoxon p < 0.05: " + ", ".join(lowp)
    fam("Label threshold check (Table S22)", [(m, L2.loc[m, "lo"], L2.loc[m, "hi"]) for m in L2.index], "sensitivity")
    RC_ = pd.read_csv(TAB / "T_rev_recording.csv"); TV_ = pd.read_csv(TAB / "T_rev_tau_val.csv").dropna(subset=["lo"])
    exr = [r.model for r in RC_.itertuples() if r.lo > 0 or r.hi < 0]
    inv.append(["Per recording scoring (Table S22)", str(2 * len(RC_)), str(len(exr)),
                ("; ".join(exr) if exr else "none") + " (intervals for the five means over groups only)", "sensitivity"])
    fam("Threshold chosen on validation groups (Table S22)", [(f"{r.model} {r.variant}", r.lo, r.hi) for r in TV_.itertuples()], "sensitivity")
    SPL_ = pd.read_csv(TAB / "T_rev_spline_clock.csv")
    fam("Spline clock as reference (Table S22)", [(r.model, r.lo, r.hi) for r in SPL_.itertuples()], "sensitivity")
    OCT_ = pd.read_csv(TAB / "T_rev_october.csv")
    fam("Position-free detectors and unmerged sessions (Table S22)",
        [(f"{r.model}, {r.subset}, fold MCC", r.lo, r.hi) for r in OCT_.itertuples()]
        + [(f"{r.model}, {r.subset}, time matched AUC", r.dtm_lo, r.dtm_hi) for r in OCT_[OCT_.subset != "december position-free (LOGO)"].itertuples()],
        "replication on other recording days")
    HZ = pd.read_csv(TAB / "T_rev_hazard.csv").dropna(subset=["lo"])
    fam("Hazard of the first report (Section V-E of the main text)", [(r.model, r.lo, r.hi) for r in HZ.itertuples()], "sensitivity")
    PSC = pd.read_csv(TAB / "T_rev_proper_scores.csv")
    fam("Proper scores against the clock (Section V-C of the main text)",
        [(f"{r.model} {'Brier score' if r.score == 'brier' else 'log loss'}", r.lo, r.hi) for r in PSC.itertuples()],
        "sensitivity")
    inv.append(["Influence of single groups (Table S23)", str(len(SUP) * len(one)), "not applicable", "no interval or test", "descriptive"])
    inv.append(["Controls with the detectors' own learners (Table S13)", str(len(C)), "not applicable",
                "detection rates on synthetic signals", "check of what the protocol detects"])
    inv.append(["Controls inside the real detectors (Table S26)", str(len(CF)), "not applicable",
                "detection rates on a synthetic signal added to the 76 features", "check of what the protocol detects"])
    sig = list(PS_.index[PS_.p_perm_bh < 0.05])
    LV = pd.read_csv(TAB / "T_rev_perm_level.csv"); lv = LV[LV.alpha == 0.05].set_index(["kind", "statistic"]).level
    inv.append(["Level of the randomization test on null data (Section V-D of the main text)", str(len(lv)), "not applicable",
                f"rejections at 5%: time matched AUC {pc(lv[('trait', 'time-matched AUC')])} and {pc(lv[('state_ar', 'time-matched AUC')])}, "
                f"fold MCC {pc(lv[('trait', 'fold MCC')])} and {pc(lv[('state_ar', 'fold MCC')])}", "check of the test"])
    inv.append(["Within game randomization test (Table S15)", "5", str(len(sig)), ", ".join(sig) or "none",
                "exploratory, BH over the five detectors"])
    part = [f"{m} {pt}" for m in SUP for pt in ("between", "within") if PS_.loc[m, f"p_perm_{pt}"] < 0.05]
    inv.append(["Parts of the randomization test (Table S15)", "10", str(len(part)),
                ("unadjusted p < 0.05: " + ", ".join(part)) if part else "none", "descriptive, unadjusted"])
    _add("TABLE S18", "Interval estimates and tests of the analyses added after the primary analysis was fixed",
         ["Family", "Estimates", "Excluding zero (or BH p < 0.05)", "Which", "Role"], inv,
         "Intervals: 95% group bootstrap intervals that omit training variability (Table S8: paired t). Apart from the "
         "randomization test, these estimates are not adjusted for multiplicity and are not read as evidence on their own; "
         "the intervals that exclude zero and the unadjusted p values below 0.05 are listed so that readers can weigh them.", widths=[2600, 800, 1300, 3700, 1600])
    for t in T:                                      # printed numbers everywhere (label, title, cells, note)
        t["label"] = si_relabel(t["label"]); t["title"] = si_relabel(t["title"]); t["note"] = si_relabel(t["note"])
        t["rows"] = [[si_relabel(c) for c in r] for r in t["rows"]]
    return T
