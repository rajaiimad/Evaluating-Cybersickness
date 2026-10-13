"""Step 59 (revision). Within game randomization null for all five detectors, with sequential stopping.

Question: does a detector's LPGO time matched advantage over elapsed time exceed what the same learner reaches when
its user telemetry carries no information about the recording it is attached to, while elapsed time and the scenario
(game, condition indicators, field of view) stay those of the recording?

Null hypothesis: within each game, the 65 feature trajectories (all primary features except elapsed time, the 7
condition indicators and the 3 field of view means: 63 telemetry features and the 2 cumulative exposure features)
are exchangeable between recordings. Under it, any advantage over
elapsed time comes from time and scenario alone.

Null construction (one replicate), within each game (race: 17 recordings of 302 or 303 windows and 3 shorter ones;
flight: 11 and 4 shorter): the long recordings are permuted among themselves (self assignment allowed, as in any
permutation of the group), and each shorter recording receives the first windows of a randomly drawn long recording
of the same game. Features are trailing statistics, so the first n windows of a trajectory are a valid trajectory of
length n. A 302 window donor given to a 303 window recording repeats its last row (the only case where a donor is
shorter than its recipient). Elapsed time, the condition indicators and the field of view stay those of the
recipient. Labels, groups, folds, smoothing rule, LOGO and LPGO scoring and the bootstrap are those of the primary
analysis. Replicate -1 is the identity: the observed statistic, refitted in the same environment as the null.

Sequential Monte Carlo (Besag and Clifford, 1991): replicates are added in rounds of ROUND per learner until H null
replicates reach the observed difference (p = H / replicates run) or CAP replicates are run (p = (1 + k) / (1 + CAP)).
A Clopper Pearson 95% interval on the exceedance share gives the Monte Carlo uncertainty of p.
Learners: RF, GB and RF+GB (mean of the RF and GB probabilities of the same replicate) share a replicate; LR and MLP
run separately.

Usage: python pipeline/59_rev_perm_strat.py [summary]      (H = 10, CAP = 200, ROUND = 15 unless set in the environment)
Outputs: outputs/tables/CTRL_PERM_STRAT.csv (one row per replicate and learner), outputs/tables/T_rev_perm_strat.csv."""
import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_k] = "1"
import sys, time, pathlib, importlib.util; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from joblib import Parallel, delayed
from scipy.stats import beta
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import RobustScaler

_spec = importlib.util.spec_from_file_location("ctrl16", pathlib.Path(__file__).resolve().parent / "16_controls.py")
C16 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(C16)
from csp.design import X as XD, PRIMARY, GroupEarlyStopMLP, d as DD
from csp.revision import ATimeParts
from csp.inference import *       # noqa: F401,F403

H, CAP, ROUND = (int(os.environ.get(k, v)) for k, v in (("H", 10), ("CAP", 200), ("ROUND", 15)))
XF = XD[PRIMARY].values.astype(float)[C16.PERM]                 # canonical row order, like y_all, sess, t_all
COND = [c for c in PRIMARY if c.startswith(("StaticFrame_", "CameraAutoMovement_", "RegionOfInterest_"))]
FOV = ["CameraFieldOfView_mean30", "CameraFieldOfView_mean120", "CameraFieldOfView_mean300"]
KEEP = [PRIMARY.index(c) for c in ["elapsed_in_session"] + COND + FOV]
assert len(COND) == 7 and len(KEEP) == 11 and np.allclose(XF[:, PRIMARY.index("elapsed_in_session")], C16.t_all)
GAME = DD.CameraFieldOfView.values[C16.PERM].round(1)           # one field of view per game, constant per recording
RECS = {s: np.where(C16.sess == s)[0] for s in np.unique(C16.sess)}
assert all(len(np.unique(GAME[ix])) == 1 for ix in RECS.values())
STRATA = {}
for s, ix in RECS.items():
    st = STRATA.setdefault(GAME[ix[0]], ([], [])); st[0 if len(ix) >= 302 else 1].append(s)
assert sorted((len(a), len(b)) for a, b in STRATA.values()) == [(11, 4), (17, 3)]
AP = ATimeParts(C16.y_all, C16.t_all, C16.pid); ONES = np.ones(len(AP.ug))
REFP = np.array(AP.parts(AP.tables(C16.t_all), ONES))
UNITS = {"trees": ("RF", "GB", "RF+GB"), "LR": ("LR",), "MLP": ("MLP",)}


def rf1(): return RandomForestClassifier(n_estimators=300, min_samples_leaf=2, class_weight="balanced_subsample",
                                         n_jobs=1, random_state=42)


MAKE = {"RF": lambda tr: rf1(), "GB": lambda tr: C16.gb_(), "LR": lambda tr: C16.lr_(),
        "MLP": lambda tr: GroupEarlyStopMLP(C16.pid[tr])}


def permuted(rep):
    if rep < 0: return XF
    rng = np.random.default_rng([2029, rep]); Xp = XF.copy()
    for game in sorted(STRATA):
        long_, short = STRATA[game]; src = dict(zip(long_, rng.permutation(long_)))
        for s in short: src[s] = long_[rng.integers(len(long_))]
        for s in long_ + short:
            ix = RECS[s]; blk = XF[RECS[src[s]]]
            if len(blk) < len(ix): blk = np.vstack([blk, np.repeat(blk[-1:], len(ix) - len(blk), axis=0)])
            Xp[ix] = blk[:len(ix)]
    Xp[:, KEEP] = XF[:, KEEP]                                    # time and scenario stay the recipient's
    return Xp


def fit_proba(Xa, tr, te, names):
    sc = RobustScaler().fit(Xa[tr]); Xtr, Xte = sc.transform(Xa[tr]), sc.transform(Xa[te])
    return {n: MAKE[n](tr).fit(Xtr, C16.y_all[tr]).predict_proba(Xte)[:, 1] for n in names}


def one(unit, rep):
    Xa = permuted(rep); base = [n for n in UNITS[unit] if n != "RF+GB"]
    p = {n: np.empty(len(Xa)) for n in base}; ps = {n: {} for n in base}
    for tr, te in C16.FOLDS:
        for n, v in fit_proba(Xa, tr, te, base).items(): p[n][te] = v
    for key, (tr, te) in C16.PAIR_IDX.items():
        for n, v in fit_proba(Xa, tr, te, base).items():
            s = np.full(len(Xa), np.nan); s[te] = trailing(v, C16.sess[te], W); ps[n][key] = s
    if unit == "trees":                                         # trailing mean is linear: smoothing commutes with the mean
        p["RF+GB"] = (p["RF"] + p["GB"]) / 2; ps["RF+GB"] = {k: (ps["RF"][k] + ps["GB"][k]) / 2 for k in ps["RF"]}
    rows = []
    for n in UNITS[unit]:
        r = C16.evaluate(p[n], ps[n])
        parts = np.array(AP.parts(AP.tables(trailing(p[n], C16.sess, W), ps[n]), ONES)) - REFP
        rows.append(dict(learner=n, rep=rep, dl=r["dl"], dl_lo=r["dl_lo"], dl_hi=r["dl_hi"], dmcc=r["dmcc"],
                         d_within=parts[1], d_between=parts[2]))
    return rows


def mc_p(null, obs):
    """Sequential (Besag and Clifford) p for the full difference, with a Clopper Pearson interval on k / n."""
    v = null.values; k = np.cumsum(v >= obs); hit = np.where(k >= H)[0]
    n, kk = (hit[0] + 1, H) if len(hit) else (len(v), k[-1] if len(v) else 0)
    p = kk / n if len(hit) else (1 + kk) / (1 + n)
    lo = beta.ppf(0.025, kk, n - kk + 1) if kk else 0.0; hi = beta.ppf(0.975, kk + 1, n - kk) if kk < n else 1.0
    return p, n, kk, lo, hi, bool(len(hit))


def summarise(R):
    O = R[R.rep < 0].set_index("learner"); N = R[R.rep >= 0].sort_values("rep"); rows = []
    for l in ["RF", "GB", "RF+GB", "LR", "MLP"]:
        if l not in O.index: continue
        g = N[N.learner == l]; o = O.loc[l]; p, n, k, lo, hi, stopped = mc_p(g.dl, o.dl); g = g.head(n)
        rows.append(dict(learner=l, reps=n, stopped_at_h=stopped, exceed=k, observed=o.dl, null_mean=g.dl.mean(),
                         null_sd=g.dl.std(), null_q95=g.dl.quantile(0.95), null_q975=g.dl.quantile(0.975), p_perm=p, p_mc_lo=lo, p_mc_hi=hi,
                         observed_between=o.d_between, p_perm_between=(1 + (g.d_between >= o.d_between).sum()) / (1 + n),
                         observed_within=o.d_within, p_perm_within=(1 + (g.d_within >= o.d_within).sum()) / (1 + n),
                         observed_dmcc=o.dmcc, null_dmcc_mean=g.dmcc.mean(),
                         p_perm_mcc=(1 + (g.dmcc >= o.dmcc).sum()) / (1 + n),
                         null_above=(g.dl_lo > 0).mean(), null_below=(g.dl_hi < 0).mean(),
                         null_above_k=int((g.dl_lo > 0).sum()), null_below_k=int((g.dl_hi < 0).sum())))
    S = pd.DataFrame(rows); S["p_perm_bh"] = bh(S.p_perm.values) if len(S) else []
    return S


def bh(p):
    p = np.asarray(p, float); o = np.argsort(p); q = p[o] * len(p) / np.arange(1, len(p) + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]; out = np.empty_like(q); out[o] = np.minimum(q, 1); return out


def active(R):
    """Units with a learner that has neither reached H exceedances nor CAP replicates."""
    out = []
    for unit, names in UNITS.items():
        if R.empty or not set(names) <= set(R[R.rep < 0].learner): out.append(unit); continue
        O = R[R.rep < 0].set_index("learner"); N = R[R.rep >= 0].sort_values("rep")
        if any(not mc_p(N[N.learner == l].dl, O.loc[l, "dl"])[5] and (N.learner == l).sum() < CAP for l in names):
            out.append(unit)
    return out


if __name__ == "__main__":
    out = TABLES / "CTRL_PERM_STRAT.csv"
    if len(sys.argv) > 1 and sys.argv[1] == "summary":
        S = summarise(pd.read_csv(out)); S.to_csv(TABLES / "T_rev_perm_strat.csv", index=False); print(S.round(3).T.to_string())
        sys.exit(0)
    nj = int(os.environ.get("CSP_JOBS", "15")); T0 = time.time()
    while True:
        R = pd.read_csv(out) if out.exists() else pd.DataFrame(columns=["learner", "rep"])
        units = active(R)
        if not units: break
        todo = []
        for u in units:
            done = set(R[R.learner == UNITS[u][0]].rep.astype(int))
            nxt = [r for r in range(-1, CAP) if r not in done][:ROUND + (-1 not in done)]
            todo += [(u, r) for r in nxt]
        if not todo: break
        todo.sort(key=lambda g: (g[1], {"MLP": 0, "trees": 1, "LR": 2}[g[0]]))   # identity first, slow units first
        print(len(todo), "tasks:", units, flush=True)
        for k, rows in enumerate(Parallel(n_jobs=nj, return_as="generator_unordered")(delayed(one)(*g) for g in todo)):
            R = pd.read_csv(out) if out.exists() else pd.DataFrame()
            pd.concat([R, pd.DataFrame(rows)], ignore_index=True).to_csv(out, index=False)
            print(k + 1, "/", len(todo), rows[0]["learner"], rows[0]["rep"], f"{time.time() - T0:.0f}s", flush=True)
    S = summarise(pd.read_csv(out)); S.to_csv(TABLES / "T_rev_perm_strat.csv", index=False); print(S.round(3).T.to_string())
