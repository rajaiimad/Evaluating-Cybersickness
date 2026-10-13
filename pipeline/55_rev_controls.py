"""Step 55 (revision). Controls run through the detectors' own learners, with an autocorrelated state signal.

The controls of step 16 use a class balanced logistic regression on [elapsed time, z]. Two limits were raised: (i) the
learner is almost the clock itself, so its detection rates and null intervals may not transfer to the RF and GB, and
(ii) the state signal has independent noise in every window, which the 61 window smoothing averages away. This step
repeats the controls with the RF and GB learners of the panel (same hyperparameters and seeds) on [elapsed time, z],
and replaces the state signal by one with autocorrelated noise:

  state_ar   z_t = delta * y_t + e_t, e_t a stationary AR(1) process within each recording, phi = 0.9, unit variance
             (the effective number of independent noise values in a 61 window mean is about 3 instead of 61)
  trait      as in step 16

For each replicate: fold MCC against the clock, the LPGO time matched AUC minus elapsed time with its 95% group
bootstrap interval, and its within group and between group parts (csp.revision.ATimeParts). delta = 0 is the null
(no information beyond elapsed time); the 97.5th percentile of the null replicates of each learner and signal gives a
calibrated one sided 2.5% threshold, which is also applied to the real detectors (step 56).

Grid (environment variables can change it): learners LR, GB, RF; trait delta 0, 1, 2, 3; state_ar delta 0, 0.1, 0.25,
0.5; 100 replicates at delta = 0, 50 otherwise (RF: null cells only, 50 replicates each). Seeds [2027, signal, 1000 delta, replicate].

Usage: python pipeline/55_rev_controls.py [summary]   (summary: only recompute the summary from CTRL_REV.csv)
Outputs: outputs/tables/CTRL_REV.csv (one row per replicate), outputs/tables/T_rev_controls.csv (summary)."""
import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_k] = "1"
import sys, time, pathlib, importlib.util; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from joblib import Parallel, delayed
from sklearn.ensemble import RandomForestClassifier

_spec = importlib.util.spec_from_file_location("ctrl16", pathlib.Path(__file__).resolve().parent / "16_controls.py")
C16 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(C16)
from csp.revision import ATimeParts
from csp.inference import *       # noqa: F401,F403

AP = ATimeParts(C16.y_all, C16.t_all, C16.pid); ONES = np.ones(len(AP.ug))
REFP = np.array(AP.parts(AP.tables(C16.t_all), ONES))


def rf1(): return RandomForestClassifier(n_estimators=300, min_samples_leaf=2, class_weight="balanced_subsample",
                                         n_jobs=1, random_state=42)


LEARN = {"LR": C16.lr_, "GB": C16.gb_, "RF": rf1}
PHI = 0.9


def ar1_noise(rng):
    e = np.empty(len(C16.y_all)); sess = C16.sess
    for s in np.unique(sess):
        idx = np.where(sess == s)[0]; z = rng.standard_normal(len(idx)); v = np.empty(len(idx))
        v[0] = z[0]
        for i in range(1, len(idx)): v[i] = PHI * v[i - 1] + np.sqrt(1 - PHI ** 2) * z[i]
        e[idx] = v
    return e


def synth(kind, delta, rng):
    if kind == "state_ar": return delta * C16.y_all + ar1_noise(rng)
    return C16.synthetic("trait", delta, rng)


def one(learner, kind, delta, rep):
    rng = np.random.default_rng([2027, {"state_ar": 3, "trait": 2}[kind], int(round(delta * 1000)), rep])
    Xa = np.column_stack([C16.t_all, synth(kind, delta, rng)]); make = LEARN[learner]
    p = C16.logo_proba(Xa, make); ps = C16.lpo_scores(Xa, make)
    r = C16.evaluate(p, ps)
    parts = np.array(AP.parts(AP.tables(trailing(p, C16.sess, W), ps), ONES)) - REFP
    return dict(learner=learner, kind=kind, delta=delta, rep=rep, **r, d_within=parts[1], d_between=parts[2])


def grid():
    G = []
    for learner in os.environ.get("LEARNERS", "LR GB RF").split():
        for kind, deltas in [("trait", [0, 1, 2, 3]), ("state_ar", [0, 0.1, 0.25, 0.5])]:
            for delta in deltas:
                if learner == "RF" and delta != 0: continue
                for rep in range(100 if (delta == 0 and learner != "RF") else 50):
                    G.append((learner, kind, float(delta), rep))
    return G


def summarise(R):
    R = R.copy(); R["flag_lpo"] = R.dl_lo > 0; R["below_lpo"] = R.dl_hi < 0; R["flag_t"] = (R.p_t < 0.05) & (R.dmcc > 0)
    R["hw"] = (R.dl_hi - R.dl_lo) / 2
    cal = R[R.delta == 0].groupby(["learner", "kind"]).dl.quantile(0.975).rename("t_cal")
    sdn = R[R.delta == 0].groupby(["learner", "kind"]).dl.std().rename("null_sd")
    hwn = R[R.delta == 0].groupby(["learner", "kind"]).hw.mean().rename("null_mean_se")
    R = R.merge(cal.reset_index(), on=["learner", "kind"]); R["flag_cal"] = R.dl > R.t_cal
    S = R.groupby(["learner", "kind", "delta"]).agg(reps=("rep", "size"), dl=("dl", "mean"), d_within=("d_within", "mean"),
                                                     d_between=("d_between", "mean"), dmcc=("dmcc", "mean"),
                                                     power_lpo=("flag_lpo", "mean"), below_lpo=("below_lpo", "mean"),
                                                     power_cal=("flag_cal", "mean"), power_t=("flag_t", "mean"),
                                                     hw=("hw", "mean")).reset_index()
    S = S.merge(cal.reset_index(), on=["learner", "kind"]).merge(sdn.reset_index(), on=["learner", "kind"])
    S = S.merge(hwn.reset_index(), on=["learner", "kind"]); S["null_mean_se"] = S.null_mean_se / 1.96
    return S


if __name__ == "__main__":
    out = TABLES / "CTRL_REV.csv"; done = set()
    if len(sys.argv) > 1 and sys.argv[1] == "summary":           # fast path: summarise the shipped replicates
        S = summarise(pd.read_csv(out)); S.to_csv(TABLES / "T_rev_controls.csv", index=False); print(S.round(3).to_string())
        sys.exit(0)
    if out.exists():
        R0 = pd.read_csv(out); done = {(r.learner, r.kind, round(r.delta, 6), int(r.rep)) for r in R0.itertuples()}
    todo = [g for g in grid() if (g[0], g[1], round(g[2], 6), g[3]) not in done]
    print(len(todo), "replicates to run", flush=True); nj = int(os.environ.get("CSP_JOBS", "15")); T0 = time.time()
    for i in range(0, len(todo), 60):                       # checkpoint every 60 replicates
        rows = Parallel(n_jobs=nj)(delayed(one)(*g) for g in todo[i:i + 60])
        R = pd.read_csv(out) if out.exists() else pd.DataFrame()
        R = pd.concat([R, pd.DataFrame(rows)], ignore_index=True); R.to_csv(out, index=False)
        print(min(i + 60, len(todo)), "/", len(todo), f"{time.time() - T0:.0f}s", flush=True)
    S = summarise(pd.read_csv(out)); S.to_csv(TABLES / "T_rev_controls.csv", index=False); print(S.round(3).to_string())
