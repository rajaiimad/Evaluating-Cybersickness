"""Step 62 (revision). The primary rule over thresholds as well as windows, from saved predictions (no model is fitted).

The primary rule (trailing mean over w = 61 windows, threshold tau = 0.5) was fixed in the initial analysis. Step 51
reports the detector minus clock fold MCC at six windows with tau = 0.5; the threshold was never varied. This step
computes the same difference for w in {1, 15, 31, 61, 121, 201} and tau in {0.3, 0.4, 0.5, 0.6, 0.7}, over the 16 two
class folds of the primary LOGO predictions, and the rank of the primary rule among the 30 combinations for each
detector (1 = most favorable to the detector). Descriptive: the cells are computed on the held out folds and are not
tested, and no rule is chosen from them.

Output: outputs/tables/T_rev_tau_grid.csv (model, w, tau, mcc, clock, dmcc, alarm, clock_alarm, rank_primary)"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from csp.inference import *       # noqa: F401,F403
from csp.data import counts, rates

WGRID, TGRID = [1, 15, 31, 61, 121, 201], [0.3, 0.4, 0.5, 0.6, 0.7]


def fold_mcc_at(g, w, tau):
    """Fold MCC of one model's predictions at the rule (w, tau), over the groups with both classes."""
    g = g.reset_index(drop=True); pred = decisions(g, w, tau); out = {}
    for u, idx in g.groupby("participant").groups.items():
        yy = g.y.values[idx]
        if 0 < yy.sum() < len(yy): out[u] = rates(*counts(yy, pred[idx]))["mcc"]
    return pd.Series(out)


if __name__ == "__main__":
    P = pd.concat([load("primary"), load("primary_clock")], ignore_index=True); P["hard"] = np.nan
    by = {m: g for m, g in P.groupby("model", sort=False)}; rows = []
    for w in WGRID:
        for tau in TGRID:
            ck = fold_mcc_at(by["Clock"], w, tau); ca = decisions(by["Clock"].reset_index(drop=True), w, tau).mean()
            for m in SUP:
                f = fold_mcc_at(by[m], w, tau).loc[ck.index]
                rows.append(dict(model=m, w=w, tau=tau, mcc=f.mean(), clock=ck.mean(), dmcc=(f - ck).mean(),
                                 alarm=decisions(by[m].reset_index(drop=True), w, tau).mean(), clock_alarm=ca))
    T = pd.DataFrame(rows)
    prim = T[(T.w == W) & (T.tau == TAU)].set_index("model").dmcc
    T["rank_primary"] = T.model.map({m: int((T[T.model == m].dmcc > prim[m]).sum()) + 1 for m in SUP})
    T.to_csv(TABLES / "T_rev_tau_grid.csv", index=False)
    # the tau = 0.5 column must reproduce the window sweep of step 51
    G = pd.read_csv(TABLES / "T_rev_window_gap.csv")
    for r in G.itertuples():
        x = T[(T.model == r.model) & (T.w == r.w) & (T.tau == 0.5)].dmcc.iloc[0]; assert abs(x - r.diff) < 1e-9, (r.model, r.w)
    print(T.pivot_table(index=["model", "w"], columns="tau", values="dmcc").round(3).to_string())
    print(T.groupby("model").agg(lo=("dmcc", "min"), hi=("dmcc", "max"), rank=("rank_primary", "first")).round(3))
