"""Step 70 (revision). Level of the within game randomization test under a true null.

The randomization test of step 59 is approximate: the seven shorter recordings receive the first windows of a randomly
drawn long recording (so a donor trajectory can occur twice, in training and test), and its p value uses sequential
Monte Carlo stopping. This step measures how often the same procedure rejects when there is nothing to find.

Detector: the control detector of step 16 (class balanced LR on elapsed time and one feature z, LOGO and LPGO scoring,
primary rule w = 61, tau = 0.5). In each null dataset z is pure noise, independent of the labels:
  trait     one N(0, 1) draw per recording, constant within it (the case the fold MCC cannot see)
  state_ar  stationary AR(1) noise within each recording, phi = 0.9, unit variance (step 55)
The randomization test is then run on z exactly as step 59 runs it on the telemetry: within each game the long recordings
are permuted, each shorter recording receives the first windows of a random long recording of its game (a shorter
donor repeats its last row), elapsed time stays the recipient's; replicates are added until H = 10 reach the observed
statistic or CAP = 200 are run (p = H / n or (1 + k) / (1 + CAP)). Statistics: the LPGO time-matched AUC minus elapsed
time (dl) and the fold MCC minus the clock (dmcc), both one sided. The level at 5% is the share of null datasets with
p <= 0.05, with an exact binomial interval; a valid test gives about 5%.

Limit: the detector is the light control learner, not RF, GB or the MLP (one replicate of those takes over 20 minutes),
so the check calibrates the procedure, not each learner.

Usage: python pipeline/70_rev_perm_level.py [summary]   (M datasets per kind, default 100; CSP_JOBS workers)
Outputs: outputs/tables/CTRL_PERM_LEVEL.csv (one row per null dataset), outputs/tables/T_rev_perm_level.csv"""
import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_k] = "1"
import sys, time, pathlib, importlib.util; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from joblib import Parallel, delayed
from scipy.stats import binomtest

HERE = pathlib.Path(__file__).resolve().parent


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file); mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod); return mod


C16 = _load("ctrl16", "16_controls.py"); C55 = _load("ctrl55", "55_rev_controls.py"); C59 = _load("perm59", "59_rev_perm_strat.py")
from csp.inference import *       # noqa: F401,F403

H, CAP, M = 10, 200, int(os.environ.get("M", 100))


def null_z(kind, m):
    rng = np.random.default_rng([2030, {"trait": 2, "state_ar": 3}[kind], m])
    return C55.synth(kind, 0.0, rng)


def reassign(z, kind, m, rep):
    """The step 59 scheme applied to the column z."""
    rng = np.random.default_rng([2031, {"trait": 2, "state_ar": 3}[kind], m, rep]); zp = z.copy()
    for game in sorted(C59.STRATA):
        long_, short = C59.STRATA[game]; src = dict(zip(long_, rng.permutation(long_)))
        for s in short: src[s] = long_[rng.integers(len(long_))]
        for s in long_ + short:
            ix = C59.RECS[s]; blk = z[C59.RECS[src[s]]]
            if len(blk) < len(ix): blk = np.concatenate([blk, np.repeat(blk[-1:], len(ix) - len(blk))])
            zp[ix] = blk[:len(ix)]
    return zp


def stat(z):
    """Point statistics of the control detector on [elapsed time, z] (no bootstrap needed for the test)."""
    Xa = np.column_stack([C16.t_all, z]); p = C16.logo_proba(Xa, C16.lr_); ps = C16.lpo_scores(Xa, C16.lr_)
    s = trailing(p, C16.sess, W); pred = (s >= TAU).astype(int)
    fm = pd.Series({g: rates(*counts(C16.y_all[C16.pid == g], pred[C16.pid == g]))["mcc"] for g in C16.TWO})
    dmcc = (fm - C16.CKF.loc[fm.index]).mean()
    dl = C16.AT.value(C16.AT.tables_lpo(s, ps), C16.ONES) - C16.REF_E0
    return dl, dmcc


def seq_p(obs, draw):
    """Besag and Clifford sequential p, as in step 59: stop at H exceedances or CAP replicates."""
    k, n = 0, 0
    while n < CAP:
        n += 1; k += draw(n - 1) >= obs
        if k >= H: return H / n, n
    return (1 + k) / (1 + CAP), n


def one(kind, m):
    z = null_z(kind, m); dl0, dm0 = stat(z); cache = {}

    def rep(r):
        if r not in cache: cache[r] = stat(reassign(z, kind, m, r))
        return cache[r]
    p_dl, n_dl = seq_p(dl0, lambda r: rep(r)[0]); p_mcc, n_mcc = seq_p(dm0, lambda r: rep(r)[1])
    return dict(kind=kind, m=m, dl=dl0, dmcc=dm0, p_dl=p_dl, n_dl=n_dl, p_mcc=p_mcc, n_mcc=n_mcc, replicates=len(cache))


def summarise(R):
    rows = []
    for kind, g in R.groupby("kind"):
        for stat_ in ("dl", "mcc"):
            for a in (0.05, 0.10):
                k = int((g[f"p_{stat_}"] <= a).sum()); ci = binomtest(k, len(g)).proportion_ci(method="exact")
                rows.append(dict(kind=kind, statistic={"dl": "time-matched AUC", "mcc": "fold MCC"}[stat_], alpha=a,
                                 datasets=len(g), rejections=k, level=k / len(g), lo=ci.low, hi=ci.high,
                                 mean_replicates=g.replicates.mean()))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    out = TABLES / "CTRL_PERM_LEVEL.csv"
    if not (len(sys.argv) > 1 and sys.argv[1] == "summary"):
        done = set()
        if out.exists(): done = {(r.kind, int(r.m)) for r in pd.read_csv(out).itertuples()}
        todo = [(k, m) for m in range(M) for k in ("trait", "state_ar") if (k, m) not in done]
        nj = int(os.environ.get("CSP_JOBS", "15")); T0 = time.time(); print(len(todo), "null datasets to run", flush=True)
        for i in range(0, len(todo), nj):
            rows = Parallel(n_jobs=nj)(delayed(one)(*t) for t in todo[i:i + nj])
            R = pd.read_csv(out) if out.exists() else pd.DataFrame()
            pd.concat([R, pd.DataFrame(rows)], ignore_index=True).to_csv(out, index=False)
            print(min(i + nj, len(todo)), "/", len(todo), f"{time.time() - T0:.0f}s", flush=True)
    S = summarise(pd.read_csv(out)); S.to_csv(TABLES / "T_rev_perm_level.csv", index=False); print(S.round(3).to_string())
