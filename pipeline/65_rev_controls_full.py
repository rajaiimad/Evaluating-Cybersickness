"""Step 65 (revision). Positive controls inside the real detectors: RF and GB on their 76 primary features plus one
synthetic feature z.

Steps 16 and 55 add z to a learner that sees only [elapsed time, z]. Reviewers asked whether the protocol would detect
an advantage of a real detector, which also carries 75 telemetry and condition features. Here z is appended to the 76
primary features of the panel, and RF and GB are refitted with the hyperparameters, folds (LOGO and the LPGO pair
models), smoothing rule (w = 61, tau = 0.5) and statistics of the primary analysis (csp.inference, via step 16).

  trait      z_r = delta * 1[recording r ever reaches severity >= 1] + e_r, one N(0, 1) draw per recording (step 16)
  state_ar   z_t = delta * y_t + e_t, e_t stationary AR(1) within each recording, phi = 0.9, unit variance (step 55)

Detection rules, as in the paper: fold MCC against the clock (paired t test p < 0.05 with a positive difference), and the
LPGO time-matched AUC minus elapsed time (lower 95% group bootstrap limit above zero).

delta = 0 is not a null of the usual kind: the 76 real features are the same in every replicate, so the replicates
differ only by the noise of z and the delta = 0 cells reproduce the real detector itself. They measure how much the
real detector's statistics vary with the noise of z, so their 97.5th percentile is a one sided 2.5% threshold for an
added signal (as the null threshold of step 16): power_cal_lpo and power_cal_mcc count the replicates whose LPGO
difference from elapsed time, or fold MCC difference from the clock, exceeds the threshold of the same learner. These
rates answer: if the real detector carried an extra signal of this strength, how often would it be detected beyond the
detector's own value? The bootstrap rule (power_lpo) and the t test rule (power_t) are reported beside them.

Usage: python pipeline/65_rev_controls_full.py [pilot|summary]
  (no argument) run the grid (resumable; environment: GRID_GB, GRID_RF as "kind:delta,delta;kind:delta", REPS_GB, REPS_RF)
  pilot         one replicate of each learner at trait delta = 0, timed
  summary       recompute the summary from CTRL_FULL.csv
Outputs: outputs/tables/CTRL_FULL.csv (one row per replicate), outputs/tables/T_rev_controls_full.csv (summary)."""
import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_k] = "1"
import sys, time, pathlib, importlib.util; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from joblib import Parallel, delayed
from sklearn.ensemble import RandomForestClassifier

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("ctrl16", HERE / "16_controls.py")
C16 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(C16)
_spec = importlib.util.spec_from_file_location("ctrl55", HERE / "55_rev_controls.py")
C55 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(C55)
from csp.inference import *       # noqa: F401,F403
from csp import design

# the 76 primary features in the canonical row order of the controls (groups ascending, dataset order within a group)
assert len(design.X) == len(C16.PERM) and (design.y[C16.PERM] == C16.y_all).all() and (design.pid[C16.PERM] == C16.pid).all()
X76 = design.X[design.PRIMARY].values.astype(float)[C16.PERM]
assert X76.shape[1] == 76


def rf1(): return RandomForestClassifier(n_estimators=300, min_samples_leaf=2, class_weight="balanced_subsample",
                                         n_jobs=1, random_state=42)


LEARN = {"GB": C16.gb_, "RF": rf1}


def one(learner, kind, delta, rep):
    rng = np.random.default_rng([2028, {"state_ar": 3, "trait": 2}[kind], int(round(delta * 1000)), rep])
    Xa = np.column_stack([X76, C55.synth(kind, delta, rng)]); make = LEARN[learner]
    r = C16.evaluate(C16.logo_proba(Xa, make), C16.lpo_scores(Xa, make))
    return dict(learner=learner, kind=kind, delta=delta, rep=rep, **r)


def parse(s):
    return [(k, float(v)) for part in s.split(";") for k, vs in [part.split(":")] for v in vs.split(",")]


def grid():
    G = []
    for learner, spec, reps in (("GB", os.environ.get("GRID_GB", "trait:0,1.5,3;state_ar:0,0.25"), int(os.environ.get("REPS_GB", 40))),
                                ("RF", os.environ.get("GRID_RF", "trait:0,1.5"), int(os.environ.get("REPS_RF", 30)))):
        if spec:
            for rep in range(reps):
                G += [(learner, k, d_, rep) for k, d_ in parse(spec)]
    return G


def summarise(R):
    R = R.copy(); R["flag_t"] = (R.p_t < 0.05) & (R.dmcc > 0); R["flag_lpo"] = R.dl_lo > 0; R["below_lpo"] = R.dl_hi < 0
    null = R[R.delta == 0].groupby(["learner", "kind"])
    thr = pd.DataFrame(dict(thr_lpo=null.dl.quantile(0.975), thr_mcc=null.dmcc.quantile(0.975))).reset_index()
    R = R.merge(thr, on=["learner", "kind"]); R["cal_lpo"] = R.dl > R.thr_lpo; R["cal_mcc"] = R.dmcc > R.thr_mcc
    return R.groupby(["learner", "kind", "delta"]).agg(
        reps=("rep", "size"), dmcc=("dmcc", "mean"), dmcc_sd=("dmcc", "std"), power_t=("flag_t", "mean"),
        dl=("dl", "mean"), dl_sd=("dl", "std"), power_lpo=("flag_lpo", "mean"), below_lpo=("below_lpo", "mean"),
        thr_lpo=("thr_lpo", "first"), thr_mcc=("thr_mcc", "first"), power_cal_lpo=("cal_lpo", "mean"),
        power_cal_mcc=("cal_mcc", "mean")).reset_index()


if __name__ == "__main__":
    out = TABLES / "CTRL_FULL.csv"; mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    if mode == "pilot":
        for learner in ("GB", "RF"):
            t0 = time.time(); r = one(learner, "trait", 0.0, 999)
            print(learner, {k: round(v, 3) for k, v in r.items() if isinstance(v, float)}, f"{time.time() - t0:.0f}s", flush=True)
        sys.exit(0)
    if mode == "run":
        done = set()
        if out.exists():
            R0 = pd.read_csv(out); done = {(r.learner, r.kind, round(r.delta, 6), int(r.rep)) for r in R0.itertuples()}
        todo = [g for g in grid() if (g[0], g[1], round(g[2], 6), g[3]) not in done]
        print(len(todo), "replicates to run", flush=True); nj = int(os.environ.get("CSP_JOBS", "15")); T0 = time.time()
        for i in range(0, len(todo), nj):                        # checkpoint after every batch
            rows = Parallel(n_jobs=nj)(delayed(one)(*g) for g in todo[i:i + nj])
            R = pd.read_csv(out) if out.exists() else pd.DataFrame()
            pd.concat([R, pd.DataFrame(rows)], ignore_index=True).to_csv(out, index=False)
            print(min(i + nj, len(todo)), "/", len(todo), f"{time.time() - T0:.0f}s", flush=True)
    S = summarise(pd.read_csv(out)); S.to_csv(TABLES / "T_rev_controls_full.csv", index=False); print(S.round(3).to_string())
