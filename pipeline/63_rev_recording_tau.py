"""Step 63 (revision). Two sensitivity analyses of the primary comparison, from saved predictions (no model is fitted).

1. Per recording scoring. Fold MCC is computed within a held out group, and seven groups hold several recordings, so a
   group value mixes the timing within a recording with differences between the recordings of the group. Here the MCC
   of the primary rule (w = 61, tau = 0.5) is computed within each of the 26 recordings that contain both classes, from
   the primary LOGO predictions (the models are those of the primary analysis; only the scoring unit changes).
   Detector minus clock: mean over the 26 recordings, and mean over the 16 groups of the group's recording mean, with
   a paired t interval and a Wilcoxon test over the groups (recordings of one group are not independent).
2. Threshold chosen on validation groups. The primary threshold 0.5 was never validated. In each LOGO fold the
   threshold is chosen from {0.3, 0.4, 0.5, 0.6, 0.7} by the pooled MCC on the three validation groups of step 13
   (models refitted on the other 18 training groups; ties: the value closest to 0.5), with w = 61 ("tau") and jointly
   with w from {1, 15, 31, 61, 121, 201} ("w and tau"; ties: closest to the primary rule), and applied to the held out
   group. Every model, the clock included, gets its own chosen rule. Detector minus clock over the 16 two class
   folds: paired t interval, Wilcoxon, Benjamini-Hochberg over the five detectors within each variant.

Both analyses were added after the primary analysis; the primary rule is unchanged.

Outputs: outputs/tables/T_rev_recording.csv, T_rev_tau_val.csv, T_rev_tau_val_choices.csv"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from csp.inference import *       # noqa: F401,F403
from csp.data import counts, rates
from csp.paths import PRED

WGRID, TGRID = [1, 15, 31, 61, 121, 201], [0.3, 0.4, 0.5, 0.6, 0.7]


def mcc_of(yy, pp): return rates(*counts(yy, pp))["mcc"]


def paired(dl):
    J = len(dl); se = dl.std(ddof=1) / np.sqrt(J); h = sps.t.ppf(0.975, J - 1) * se
    return dict(n=J, d=dl.mean(), lo=dl.mean() - h, hi=dl.mean() + h, p_t=2 * sps.t.sf(abs(dl.mean() / se), J - 1),
                p_w=sps.wilcoxon(dl).pvalue, higher=int((dl > 1e-12).sum()))


def recording_table(P):
    by = {m: g.reset_index(drop=True) for m, g in P.groupby("model", sort=False)}; R = {}
    for m, g in by.items():
        pred = decisions(g); r = {}
        for s_, idx in g.groupby("session").groups.items():
            yy = g.y.values[idx]
            if 0 < yy.sum() < len(yy): r[s_] = (g.participant.values[idx[0]], mcc_of(yy, pred[idx]))
        R[m] = pd.DataFrame(r, index=["participant", "mcc"]).T
    ck = R["Clock"]; rows = []
    for m in SUP:
        dr = (R[m].mcc - ck.mcc).astype(float); dg = dr.groupby(ck.participant).mean()
        pg = paired(dg)
        rows.append(dict(model=m, recordings=len(dr), mcc_rec=R[m].mcc.mean(), clock_rec=ck.mcc.mean(), d_rec=dr.mean(),
                         rec_higher=int((dr > 1e-12).sum()), p_w_rec=sps.wilcoxon(dr).pvalue,
                         groups=pg["n"], d_grp=pg["d"], lo=pg["lo"], hi=pg["hi"], p_t=pg["p_t"], p_w=pg["p_w"],
                         groups_higher=pg["higher"]))
    T = pd.DataFrame(rows); T["p_w_bh"] = bh(T.p_w.values); return T


def tau_table(P, V):
    parts = sorted(P.participant.unique()); fold_of = {p: i for i, p in enumerate(parts)}; rows, choices = [], []
    for variant, grid in (("tau", [(W, t) for t in TGRID]), ("w and tau", [(w, t) for w in WGRID for t in TGRID])):
        F, AL = {}, {}
        for m in SUP + ["Clock"]:
            vm = V[V.model == m]; pm = P[P.model == m]; fm = {}; al = []
            for grp, gt in pm.groupby("participant"):
                gv = vm[vm.fold == fold_of[grp]]
                val = {(w, t): mcc_of(gv.y.values, (trailing(gv.proba.values, gv.session.values, w) >= t).astype(int)) for w, t in grid}
                wb, tb = max(grid, key=lambda k: (val[k], -abs(k[1] - TAU), -abs(k[0] - W)))   # ties: closest to the primary rule
                choices.append(dict(variant=variant, model=m, group=grp, w=wb, tau=tb, val_mcc=val[(wb, tb)]))
                pp = (trailing(gt.proba.values, gt.session.values, wb) >= tb).astype(int); al.append(pp)
                yy = gt.y.values
                if 0 < yy.sum() < len(yy): fm[grp] = mcc_of(yy, pp)
            F[m] = pd.Series(fm); AL[m] = np.concatenate(al).mean()
        C = pd.DataFrame(choices); C = C[C.variant == variant]
        for m in SUP + ["Clock"]:
            c = C[C.model == m]; r = dict(variant=variant, model=m, mcc=F[m].mean(), alarm=AL[m], tau_median=c.tau.median(),
                                          tau_05=int((c.tau == 0.5).sum()), primary_rule=int(((c.tau == 0.5) & (c.w == W)).sum()))
            if m != "Clock": r.update(paired(F[m] - F["Clock"]))
            rows.append(r)
    T = pd.DataFrame(rows)
    for v in T.variant.unique():
        k = (T.variant == v) & (T.model != "Clock"); T.loc[k, "p_w_bh"] = bh(T.loc[k, "p_w"].values)
    return T, pd.DataFrame(choices)


if __name__ == "__main__":
    P = pd.concat([load("primary"), load("primary_clock")], ignore_index=True); P["hard"] = np.nan
    R = recording_table(P); R.to_csv(TABLES / "T_rev_recording.csv", index=False); print(R.round(3).to_string())
    V = pd.read_csv(PRED / "P_nested_val.csv")
    T, C = tau_table(P, V); T.to_csv(TABLES / "T_rev_tau_val.csv", index=False); C.to_csv(TABLES / "T_rev_tau_val_choices.csv", index=False)
    print(T.round(3).to_string())
    # the choice of w alone at tau = 0.5 must reproduce step 13
    NW = pd.read_csv(TABLES / "T_nested_w_choices.csv")
    parts = sorted(P.participant.unique()); fold_of = {p: i for i, p in enumerate(parts)}
    for m in SUP + ["Clock"]:
        vm = V[V.model == m]
        for grp in parts:
            gv = vm[vm.fold == fold_of[grp]]
            val = {w: mcc_of(gv.y.values, (trailing(gv.proba.values, gv.session.values, w) >= TAU).astype(int)) for w in WGRID}
            wb = max(WGRID, key=lambda w: (val[w], -abs(w - 61)))
            assert wb == NW[(NW.model == m) & (NW.group == grp)].w.iloc[0], (m, grp)
    print("validation choice of w at tau = 0.5 reproduces step 13")
