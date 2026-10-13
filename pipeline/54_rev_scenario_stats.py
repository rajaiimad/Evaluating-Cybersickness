"""Step 54 (revision). Statistics of the scenario information analysis (fits of step 53).

  T_rev_scenario.csv   for each model: fold mean MCC at the primary rule and its difference with the clock (paired t,
                       Wilcoxon, 16 two class folds); LPGO time matched AUC minus elapsed time, full and its within
                       and between group parts, with 95% group bootstrap intervals (1,000 shared draws, seed 0)
  T_rev_scenario_contrast.csv   with scenario minus without scenario (F76 minus F66) for RF, GB, RF+GB, LR, and each
                       detector minus the "GB time and scenario" reference, on the LPGO time matched AUC
  T_rev_refit_vs_shipped.csv    the F76 refits of this environment against the shipped primary values"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from csp.inference import *       # noqa: F401,F403
from csp.revision import ATimeParts, load_pair_dir
from csp.paths import PRED

MODELS = ["RF", "GB", "RF+GB", "LR", "RF no scenario", "GB no scenario", "RF+GB no scenario", "LR no scenario",
          "LR time and scenario", "GB time and scenario"]

if __name__ == "__main__":
    ck_ = load("primary_clock"); ck_["hard"] = np.nan
    clk = pd.concat([ck_[ck_.participant == g] for g in np.unique(ck_.participant)]).reset_index(drop=True)
    y_, t_, g_ = clk.y.values, clk.t.values.astype(float), clk.participant.values
    P = pd.read_csv(PRED / "rev" / "P_scen_logo.csv"); P["hard"] = np.nan
    S = {m: aligned_scores(P[P.model == m], clk)[m] for m in MODELS}
    PS = load_pair_dir(PRED / "rev" / "lpgo_scen", MODELS, clk); assert all(len(v) == 216 for v in PS.values())
    ckF = fold_mcc(ck_)["Clock"]; F = fold_mcc(P)
    AP = ATimeParts(y_, t_, g_); M = boot_multiplicities(AP.ug, 1000, 0); one = np.ones(len(AP.ug))
    ref = np.array(AP.parts(AP.tables(t_), one)); refb = np.array([AP.parts(AP.tables(t_), m_) for m_ in M])
    E, EB = {}, {}
    rows = []
    for m in MODELS:
        C = AP.tables(S[m], PS[m]); E[m] = np.array(AP.parts(C, one)); EB[m] = np.array([AP.parts(C, m_) for m_ in M])
        x = F[m].loc[ckF.index]; dl = x - ckF; dd = EB[m] - refb
        r = dict(model=m, mcc=x.mean(), dmcc=dl.mean(), p_t=sps.ttest_rel(x, ckF).pvalue, p_w=sps.wilcoxon(dl).pvalue)
        for j, part in enumerate(["full", "within", "between"]):
            r["tm_" + part] = E[m][j]; r["d_" + part] = E[m][j] - ref[j]
            r["d_" + part + "_lo"] = np.nanpercentile(dd[:, j], 2.5); r["d_" + part + "_hi"] = np.nanpercentile(dd[:, j], 97.5)
        rows.append(r)
    T = pd.DataFrame(rows); T.to_csv(TABLES / "T_rev_scenario.csv", index=False); print(T.round(3).to_string())
    con = []
    pairs = [(m, m + " no scenario", "with minus without scenario") for m in ["RF", "GB", "RF+GB", "LR"]] + \
            [(m, "GB time and scenario", "minus GB time and scenario") for m in ["RF", "GB", "RF+GB", "LR"]] + \
            [(m, "LR time and scenario", "minus LR time and scenario") for m in ["RF", "GB", "RF+GB", "LR"]]
    for a, b, lab in pairs:
        dd = EB[a] - EB[b]
        con.append(dict(contrast=f"{a} {lab}", d_full=E[a][0] - E[b][0], lo=np.nanpercentile(dd[:, 0], 2.5),
                        hi=np.nanpercentile(dd[:, 0], 97.5), d_between=E[a][2] - E[b][2],
                        d_within=E[a][1] - E[b][1]))
    C_ = pd.DataFrame(con); C_.to_csv(TABLES / "T_rev_scenario_contrast.csv", index=False); print(C_.round(3).to_string())
    # refit (this environment) against shipped values for F76
    LP = pd.read_csv(TABLES / "T_lpgo_atime.csv").set_index("model"); PR = pd.read_csv(TABLES / "T_primary.csv").set_index("model")
    rv = [dict(model=m, mcc_refit=T.set_index("model").loc[m, "mcc"], mcc_shipped=PR.loc[m, "mcc"],
               tm_lpgo_refit=E[m][0], tm_lpgo_shipped=LP.loc[m, "tm_lpo"]) for m in ["RF", "GB", "RF+GB", "LR"]]
    pd.DataFrame(rv).to_csv(TABLES / "T_rev_refit_vs_shipped.csv", index=False); print(pd.DataFrame(rv).round(4).to_string())
