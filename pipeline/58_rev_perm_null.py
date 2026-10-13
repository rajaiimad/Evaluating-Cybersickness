"""Step 58 (revision). Recording permutation null for the real detectors (RF and GB with the 76 primary features).

Question: is the observed LPGO time matched advantage of a real detector over elapsed time larger than what the same
learner, with features of the same structure, reaches when its features carry no information about the labels of the
recording they are attached to?

Null construction (one replicate): the 76 feature trajectories of the recordings are permuted between recordings.
Each recording receives the trajectory of another recording, from its first window, truncated to its own length
(features are trailing statistics, so a prefix of a trajectory is itself a valid trajectory); the 28 recordings of
302 or 303 windows are permuted among themselves (a 302 window trajectory given to a 303 window recording repeats its
last row), and each of the 7 shorter recordings receives the prefix of a randomly drawn long recording. Elapsed time is
then reset to each recording's own timestamps. Labels, groups, folds, smoothing rule, LOGO and LPGO scoring and the
bootstrap are those of the primary analysis. The permutation keeps the within recording structure of the telemetry,
the condition indicators and the field of view, and breaks their link to the labels of the recording.

For each replicate and learner: LPGO time matched AUC minus elapsed time (full, within, between). The one sided
permutation p of the observed difference is (1 + number of null replicates at least as large) / (1 + replicates).

Usage: python pipeline/58_rev_perm_null.py [summary]       (REPS environment variable, default 40 per learner)
Outputs: outputs/tables/CTRL_PERM.csv (one row per replicate), outputs/tables/T_rev_perm_null.csv (summary)."""
import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_k] = "1"
import sys, time, pathlib, importlib.util; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from joblib import Parallel, delayed
from sklearn.ensemble import RandomForestClassifier

_spec = importlib.util.spec_from_file_location("ctrl16", pathlib.Path(__file__).resolve().parent / "16_controls.py")
C16 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(C16)
from csp.design import X as XD, PRIMARY
from csp.revision import ATimeParts
from csp.inference import *       # noqa: F401,F403

XF = XD[PRIMARY].values.astype(float)[C16.PERM]                 # canonical row order, like y_all, sess, t_all
TCOL = PRIMARY.index("elapsed_in_session")
assert np.allclose(XF[:, TCOL], C16.t_all)
RECS = {s: np.where(C16.sess == s)[0] for s in np.unique(C16.sess)}
LONG = [s for s, ix in RECS.items() if len(ix) >= 302]; SHORT = [s for s in RECS if s not in LONG]
assert len(LONG) == 28 and len(SHORT) == 7
AP = ATimeParts(C16.y_all, C16.t_all, C16.pid); ONES = np.ones(len(AP.ug))
REFP = np.array(AP.parts(AP.tables(C16.t_all), ONES))


def rf1(): return RandomForestClassifier(n_estimators=300, min_samples_leaf=2, class_weight="balanced_subsample",
                                         n_jobs=1, random_state=42)


LEARN = {"GB": C16.gb_, "RF": rf1}


def permuted(rng):
    Xp = np.empty_like(XF); src = dict(zip(LONG, rng.permutation(LONG)))
    for s in SHORT: src[s] = LONG[rng.integers(len(LONG))]
    for s, ix in RECS.items():
        blk = XF[RECS[src[s]]]
        if len(blk) < len(ix): blk = np.vstack([blk, np.repeat(blk[-1:], len(ix) - len(blk), axis=0)])
        Xp[ix] = blk[:len(ix)]
    Xp[:, TCOL] = C16.t_all                                    # each recording keeps its own elapsed time
    return Xp


def one(learner, rep):
    Xp = permuted(np.random.default_rng([2028, rep]))      # same permutation for both learners
    make = LEARN[learner]; p = C16.logo_proba(Xp, make); ps = C16.lpo_scores(Xp, make)
    r = C16.evaluate(p, ps)
    parts = np.array(AP.parts(AP.tables(trailing(p, C16.sess, W), ps), ONES)) - REFP
    return dict(learner=learner, rep=rep, dl=r["dl"], dl_lo=r["dl_lo"], dl_hi=r["dl_hi"], dmcc=r["dmcc"],
                d_within=parts[1], d_between=parts[2])


def summarise(R):
    obs = pd.read_csv(TABLES / "T_rev_tm_parts.csv").set_index("model")
    pw = pd.read_csv(TABLES / "T_rev_power.csv").set_index("model")
    rows = []
    for l, g in R.groupby("learner"):
        o = obs.loc[l]
        rows.append(dict(learner=l, reps=len(g), null_mean=g.dl.mean(), null_sd=g.dl.std(), null_q975=g.dl.quantile(0.975),
                         observed=o.d_full, p_perm=(1 + (g.dl >= o.d_full).sum()) / (1 + len(g)),
                         null_between_q975=g.d_between.quantile(0.975), observed_between=o.d_between,
                         p_perm_between=(1 + (g.d_between >= o.d_between).sum()) / (1 + len(g)),
                         null_within_q975=g.d_within.quantile(0.975), observed_within=o.d_within,
                         p_perm_within=(1 + (g.d_within >= o.d_within).sum()) / (1 + len(g)),
                         null_dmcc_mean=g.dmcc.mean(), observed_dmcc=pw.loc[l, "dmcc"],
                         p_perm_mcc=(1 + (g.dmcc >= pw.loc[l, "dmcc"]).sum()) / (1 + len(g)), null_above=(g.dl_lo > 0).mean(), null_below=(g.dl_hi < 0).mean()))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    out = TABLES / "CTRL_PERM.csv"
    if len(sys.argv) > 1 and sys.argv[1] == "summary":
        S = summarise(pd.read_csv(out)); S.to_csv(TABLES / "T_rev_perm_null.csv", index=False); print(S.round(3).to_string())
        sys.exit(0)
    reps = int(os.environ.get("REPS", "40")); done = set()
    if out.exists(): done = {(r.learner, int(r.rep)) for r in pd.read_csv(out).itertuples()}
    todo = [(l, k) for k in range(reps) for l in ("GB", "RF") if (l, k) not in done]
    print(len(todo), "replicates to run", flush=True); T0 = time.time(); nj = int(os.environ.get("CSP_JOBS", "15"))
    todo.sort(key=lambda g: g[0] != "RF")                    # longest fits first, results saved as they finish
    for k, row in enumerate(Parallel(n_jobs=nj, return_as="generator_unordered")(delayed(one)(*g) for g in todo)):
        R = pd.read_csv(out) if out.exists() else pd.DataFrame()
        pd.concat([R, pd.DataFrame([row])], ignore_index=True).to_csv(out, index=False)
        print(k + 1, "/", len(todo), row["learner"], row["rep"], f"{time.time() - T0:.0f}s", flush=True)
    S = summarise(pd.read_csv(out)); S.to_csv(TABLES / "T_rev_perm_null.csv", index=False); print(S.round(3).to_string())
