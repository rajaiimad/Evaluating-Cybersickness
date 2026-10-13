"""Step 51 (revision). Power and effect size intervals of the primary MCC comparison, from saved predictions.

The reported minimum detectable difference (MDD) and the number of two class groups needed (step 24) use the
standard deviation of the paired fold differences without the Nadeau and Bengio correction, while the corrected
paired t test of Table IV inflates the variance by (1/J + rho) / (1/J), rho = mean n_test / n_train. This step reports
both bases and adds 95% intervals for every detector minus clock difference (plain paired t and corrected).

Smoothing window disclosure: detector minus clock fold MCC at every window of the sweep (Table S1 rows plus w = 61),
and the window at which each detector's gap is largest.

Outputs: outputs/tables/T_rev_power.csv, outputs/tables/T_rev_window_gap.csv"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from csp.inference import *       # noqa: F401,F403


def n_needed_var(var1, delta, power=0.80, alpha=0.05):
    """Groups needed when the variance of the mean difference with n units is var1 * c(n) / n; here c is constant."""
    for n in range(3, 20000):
        if (sps.t.ppf(1 - alpha / 2, n - 1) + sps.t.ppf(power, n - 1)) * np.sqrt(var1 / n) <= delta: return n
    return np.nan


if __name__ == "__main__":
    prim = load("primary"); prim["hard"] = np.nan; ck_ = load("primary_clock"); ck_["hard"] = np.nan
    PFs = fold_mcc(prim); ck = fold_mcc(ck_)["Clock"]; J = len(ck)
    sizes = d.groupby("participant").size(); ntot = len(d)
    rho = np.mean([sizes[g] / (ntot - sizes[g]) for g in ck.index]); infl = (1 / J + rho) / (1 / J)
    tq = sps.t.ppf(0.975, J - 1); mult = (tq + sps.t.ppf(0.80, J - 1)) / np.sqrt(J)
    rows = []
    for m in SUP:
        dl = PFs[m].loc[ck.index] - ck; sd = dl.std(ddof=1); se = sd / np.sqrt(J); se_nb = np.sqrt((1 / J + rho)) * sd
        rows.append(dict(model=m, dmcc=dl.mean(), sd_diff=sd, ci_lo=dl.mean() - tq * se, ci_hi=dl.mean() + tq * se,
                         ci_nb_lo=dl.mean() - tq * se_nb, ci_nb_hi=dl.mean() + tq * se_nb,
                         mde=mult * sd, mde_nb=mult * sd * np.sqrt(infl),
                         n010=n_needed(sd, 0.10), n010_nb=n_needed_var(sd ** 2 * infl, 0.10),
                         n_folds=J, rho=rho, inflation=infl))
    T = pd.DataFrame(rows); T.to_csv(TABLES / "T_rev_power.csv", index=False)
    print(T.round(3).to_string())
    # the plain column must equal the reported values of step 24
    PS = pd.read_csv(TABLES / "T_primary_stats.csv").set_index("model")
    for r in rows:
        assert abs(r["mde"] - PS.loc[r["model"], "mde"]) < 1e-12 and r["n010"] == PS.loc[r["model"], "n010"]

    # smoothing window: gap to the clock at each w
    S1 = pd.read_csv(TABLES / "T_smoothing_paired_vs_clock.csv")
    print(S1.head().to_string())
    S1.to_csv(TABLES / "T_rev_window_gap.csv", index=False)
