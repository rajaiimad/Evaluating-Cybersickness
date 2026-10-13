"""Step 56 (revision). Severity ranking conditioned on elapsed time, from the shipped primary predictions.

A_sev (Section III-F, eq. 17) compares severity 3 with severity 1 windows of the same group at any times. Severity 3
windows tend to come later, so a score that only tracks time can rank them well. Here only pairs in the same 30 s
bin of elapsed time and the same group are compared (A_sev,time), the same matching as the time matched AUC, with the
smoothed score; elapsed time itself is the reference. Also reported: the reported A_sev without group 14 (the six
recording group that is the reconstruction most likely to combine several people, Section III-A).
The equal group weight summary uses only groups with at least MIN_PAIRS matched pairs (one group has a single pair),
and each per group row gives the share of its matched pairs whose two windows come from the same recording.

Output: outputs/tables/T_rev_severity.csv"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from csp.inference import *       # noqa: F401,F403


MIN_PAIRS = 30


def pairs_score(s3, s1):
    dd = s3[:, None] - s1[None, :]; return (dd > 0).sum() + 0.5 * (dd == 0).sum(), dd.size


if __name__ == "__main__":
    prim = load("primary"); ck_ = load("primary_clock")
    ALL = pd.concat([prim, ck_], ignore_index=True); per = {}
    for name, g in ALL.groupby("model", sort=False):
        g = g.reset_index(drop=True); s = trailing(g.proba.values, g.session.values, W)
        if name == "Clock": s = g.t.values.astype(float)          # elapsed time itself as the reference
        b = (g.t.values // 30).astype(int); pg = {}
        for grp, idx in g.groupby("participant").groups.items():
            idx = np.asarray(idx); num = den = same = 0.0
            for bb in np.unique(b[idx]):
                k = idx[b[idx] == bb]; m3 = g.sev.values[k] == 3; m1 = g.sev.values[k] == 1
                s3 = s[k][m3]; s1 = s[k][m1]
                if len(s3) and len(s1):
                    n_, d_ = pairs_score(s3, s1); num += n_; den += d_
                    r3, r1 = g.session.values[k][m3], g.session.values[k][m1]
                    same += sum((r3 == r).sum() * (r1 == r).sum() for r in np.unique(r3))
            if den: pg[grp] = (num, den, same)
        per[name] = pg
    groups = sorted(per["Clock"]); print("groups with matched severity 3 and 1 pairs:", groups,
                                         [int(per["Clock"][k][1]) for k in groups])
    NUM = {m: np.array([per[m].get(k, (np.nan, 0))[0] for k in groups]) for m in per}
    DEN = np.array([per["Clock"][k][1] for k in groups])
    rng = np.random.default_rng(0); MB = np.array([np.bincount(rng.integers(0, len(groups), len(groups)),
                                                               minlength=len(groups)) for _ in range(4000)])
    pooled = lambda m, w: (w * NUM[m]).sum(-1) / (w * DEN).sum(-1)
    rows = []
    for m in SUP:
        bp = pooled(m, MB) - pooled("Clock", MB)
        rows.append(dict(analysis="time matched A_sev", model=m, a_sev=pooled(m, np.ones(len(groups))),
                         ref=pooled("Clock", np.ones(len(groups))),
                         diff=pooled(m, np.ones(len(groups))) - pooled("Clock", np.ones(len(groups))),
                         lo=np.percentile(bp, 2.5), hi=np.percentile(bp, 97.5), groups=len(groups), pairs=int(DEN.sum()),
                         largest_group=groups[int(np.argmax(DEN))], largest_share=DEN.max() / DEN.sum()))
        big = DEN >= MIN_PAIRS
        eq = lambda mm: np.nanmean((NUM[mm] / DEN)[big])
        rows.append(dict(analysis="time matched A_sev, equal group weights", model=m, a_sev=eq(m), ref=eq("Clock"),
                         diff=eq(m) - eq("Clock"), groups=int(big.sum()),
                         groups_above=int(((NUM[m] / DEN > NUM["Clock"] / DEN + 1e-12) & big).sum())))
        keep = np.array([k != 10 for k in groups], float)
        rows.append(dict(analysis="time matched A_sev without group 10", model=m, a_sev=pooled(m, keep),
                         ref=pooled("Clock", keep), diff=pooled(m, keep) - pooled("Clock", keep),
                         groups=int(keep.sum()), pairs=int((keep * DEN).sum())))
    for k, g_ in enumerate(groups):
        rows.append(dict(analysis="time matched A_sev by group", model="per group", group=g_, pairs=int(DEN[k]),
                         same_recording_share=per["Clock"][g_][2] / DEN[k],
                         **{m: NUM[m][k] / DEN[k] for m in SUP + ["Clock"]}))
    # reported A_sev without group 14
    AS = pd.read_csv(TABLES / "T_asev_by_group.csv")
    for m in SUP:
        a = AS[(AS.model == m) & (AS.group != 14)]; c = AS[(AS.model == "Clock") & (AS.group != 14)]
        am = (a.a_sev * a.pairs).sum() / a.pairs.sum(); cm = (c.a_sev * c.pairs).sum() / c.pairs.sum()
        rows.append(dict(analysis="A_sev without group 14", model=m, a_sev=am, ref=cm, diff=am - cm,
                         groups=a.group.nunique(), pairs=int(a.pairs.sum())))
    T = pd.DataFrame(rows); T.to_csv(TABLES / "T_rev_severity.csv", index=False); print(T.round(3).to_string())
