"""Step 61 (revision). Two checks from saved outputs; no model is fitted.

1. Influence of single groups on the LPGO time matched advantage. The measure is pair weighted and 95% of its pairs
   compare two groups, so groups with many windows in the kept bins supply most of the evidence. For every
   reconstructed group: its number of recordings, the share of the matched pairs (kept bins) that involve one of its
   windows, and each detector's LPGO time matched AUC minus elapsed time with that group removed (multiplicity 0 in
   the closed form of csp.revision.ATimeParts; the bins are kept by the paper's rule on the remaining groups).
2. Uncertainty of the detection rate of the trait control at delta = 1.5 under the null threshold (the "33%" of the
   main text). The threshold is the 97.5th percentile of the 200 null replicates, so it is itself estimated. The null
   and the signal replicates are resampled with replacement (10,000 draws, seed 0), the threshold and the detection
   share are recomputed in every draw, and the 2.5th and 97.5th percentiles are reported. The same is done for the
   bootstrap rule (lower limit of the interval above zero), which has no threshold, and for delta = 1, 2 and 3.

Outputs: outputs/tables/T_rev_influence.csv, T_rev_influence_se.csv, T_rev_control_ci.csv"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from csp.inference import *       # noqa: F401,F403
from csp.revision import ATimeParts, load_pair_dir
from csp.paths import LPGO


def influence():
    ck_ = load("primary_clock"); ck_["hard"] = np.nan
    clk = pd.concat([ck_[ck_.participant == g] for g in np.unique(ck_.participant)]).reset_index(drop=True)
    prim = load("primary"); y_, t_, g_ = clk.y.values, clk.t.values.astype(float), clk.participant.values
    S = {m: aligned_scores(prim[prim.model == m], clk)[m] for m in SUP}
    PS = load_pair_dir(LPGO, SUP, clk); assert all(len(PS[m]) == 216 for m in SUP)
    AP = ATimeParts(y_, t_, g_); G = len(AP.ug); one = np.ones(G)
    Cref = AP.tables(t_); C = {m: AP.tables(S[m], PS[m]) for m in SUP}
    full = {m: AP.parts(C[m], one)[0] - AP.parts(Cref, one)[0] for m in SUP}
    LP = pd.read_csv(TABLES / "T_lpgo_atime.csv").set_index("model")          # must reproduce the reported differences
    assert all(abs(full[m] - LP.loc[m, "d_lpo"]) < 1e-9 for m in SUP)
    P, N = AP.npos.sum(1), AP.nneg.sum(1); keep = (P >= AP.min_n) & (N >= AP.min_n); tot = (P * N)[keep].sum()
    nrec = clk.groupby("participant").session.nunique()
    rows = [dict(group="all", recordings=int(nrec.sum()), two_class=int(sum(0 < y_[g_ == g].mean() < 1 for g in AP.ug)),
                 pair_share=1.0, **full)]
    for i, g in enumerate(AP.ug):
        m_ = one.copy(); m_[i] = 0
        share = 1 - ((P - AP.npos[:, i]) * (N - AP.nneg[:, i]))[keep].sum() / tot
        ref = AP.parts(Cref, m_)[0]
        rows.append(dict(group=int(g), recordings=int(nrec.loc[g]), two_class=int(0 < y_[g_ == g].mean() < 1),
                         pair_share=share, **{m: AP.parts(C[m], m_)[0] - ref for m in SUP}))
    T = pd.DataFrame(rows); T.to_csv(TABLES / "T_rev_influence.csv", index=False); print(T.round(3).to_string())
    L = T[T.group != "all"]; n = len(L)
    for m in SUP: print(m, "without one group:", round(L[m].min(), 3), "to", round(L[m].max(), 3))
    # jackknife standard error of the difference from its leave one group out values (no refit, like the bootstrap)
    SE = pd.DataFrame([dict(model=m, jk_se=np.sqrt((n - 1) / n * ((L[m] - L[m].mean()) ** 2).sum()),
                            boot_se=(LP.loc[m, "d_lpo_hi"] - LP.loc[m, "d_lpo_lo"]) / (2 * 1.96)) for m in SUP])
    SE.to_csv(TABLES / "T_rev_influence_se.csv", index=False); print(SE.round(3).to_string())


def control_ci(B=10000, seed=0):
    R = pd.read_csv(TABLES / "CTRL_LR.csv"); R = R[R.kind == "trait"]; nul = R[R.delta == 0].dl.values
    rng = np.random.default_rng(seed); rows = []
    for dlt in (1.0, 1.5, 2.0, 3.0):
        g = R[(R.delta - dlt).abs() < 1e-9]; dl, lo = g.dl.values, g.dl_lo.values; n = len(dl)
        thr = np.percentile(nul, 97.5); cal, bt = [], []
        for _ in range(B):
            i = rng.integers(0, n, n); t = np.percentile(nul[rng.integers(0, len(nul), len(nul))], 97.5)
            cal.append((dl[i] > t).mean()); bt.append((lo[i] > 0).mean())
        rows.append(dict(kind="trait", delta=dlt, reps=n, null_reps=len(nul), threshold=thr, mean_dl=dl.mean(),
                         power_cal=(dl > thr).mean(), cal_lo=np.percentile(cal, 2.5), cal_hi=np.percentile(cal, 97.5),
                         power_boot=(lo > 0).mean(), boot_lo=np.percentile(bt, 2.5), boot_hi=np.percentile(bt, 97.5)))
    T = pd.DataFrame(rows); T.to_csv(TABLES / "T_rev_control_ci.csv", index=False); print(T.round(3).to_string())
    TC = pd.read_csv(TABLES / "T_controls.csv"); TC = TC[TC.kind == "trait"].set_index("delta")      # reported rates
    assert all(abs(r["power_cal"] - TC.loc[r["delta"], "power_cal"]) < 1e-9 for r in rows)


if __name__ == "__main__":
    influence(); control_ci()
