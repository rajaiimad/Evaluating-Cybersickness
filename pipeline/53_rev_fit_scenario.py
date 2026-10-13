"""Step 53 (revision). Model fits for the scenario information analysis (about 10 minutes on 16 CPUs).

Question: how much of the detectors' advantage over elapsed time at matched time comes from knowing the scenario
(which game and which experimental condition is running), which a developer knows without sensing the user?

Feature sets
  F76    the primary 76 features (refitted here so that both arms of every contrast come from this environment;
         step 50 shows that the RF and the LR of this environment differ slightly from the shipped fits)
  F66    F76 without the 7 condition indicators and the 3 trailing means of the camera field of view (field of view
         is constant within a recording and takes two values, one per game)
  SCEN   elapsed time + the 7 condition indicators + the field of view (CameraFieldOfView_mean30): a "time and
         scenario" reference that uses no sensing of the user
Detectors: RF, GB, LR on F76 and F66 (RF+GB is their mean); LR and GB on SCEN. MLP not refitted (slowest and least
stable across seeds, Section V-A).

Designs: LOGO (22 folds) and LPGO (the 216 pairs of step 15), same scaling, hyperparameters and seeds as the primary
run. One BLAS thread per worker.

Outputs: outputs/predictions/rev/P_scen_logo.csv and outputs/predictions/rev/lpgo_scen/pair_<g>_<h>.csv"""
import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_k] = "1"
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
import itertools
from joblib import Parallel, delayed
from csp.design import *          # noqa: F401,F403
from csp.paths import PRED

REV = PRED / "rev"; LP = REV / "lpgo_scen"; LP.mkdir(parents=True, exist_ok=True)
FOV = ["CameraFieldOfView_mean30", "CameraFieldOfView_mean120", "CameraFieldOfView_mean300"]
F76 = PRIMARY
F66 = [c for c in PRIMARY if c not in cond and c not in FOV]
SCEN = ["elapsed_in_session"] + cond + ["CameraFieldOfView_mean30"]
assert len(F66) == 66 and len(SCEN) == 9


def rf1():
    return RandomForestClassifier(n_estimators=300, min_samples_leaf=2, class_weight="balanced_subsample",
                                  n_jobs=1, random_state=42)


FITS = [("RF", F76, rf1), ("GB", F76, gb), ("LR", F76, lr),
        ("RF no scenario", F66, rf1), ("GB no scenario", F66, gb), ("LR no scenario", F66, lr),
        ("LR time and scenario", SCEN, lr), ("GB time and scenario", SCEN, gb)]
HASPOS = set(np.unique(pid[y == 1]))
PAIRS = [(g, h) for g, h in itertools.combinations(np.unique(pid), 2) if g in HASPOS or h in HASPOS]


def fit_all(tr, te):
    probs = {}
    for name, feats, fn in FITS:
        Xa = X[feats].values.astype(float); sc = RobustScaler().fit(Xa[tr])
        m = fn().fit(sc.transform(Xa[tr]), y[tr]); probs[name] = m.predict_proba(sc.transform(Xa[te]))[:, 1]
    probs["RF+GB"] = (probs["RF"] + probs["GB"]) / 2
    probs["RF+GB no scenario"] = (probs["RF no scenario"] + probs["GB no scenario"]) / 2
    return probs


def frame(probs, te, **extra):
    return pd.concat([pd.DataFrame(dict(**extra, model=n, participant=pid[te], session=sess[te], y=y[te],
                                        sev=sev[te], t=t_el[te], proba=p)) for n, p in probs.items()], ignore_index=True)


def logo_fold(k, g):
    tr, te = np.where(pid != g)[0], np.where(pid == g)[0]
    assert not set(sess[tr]) & set(sess[te])
    return frame(fit_all(tr, te), te, fold=k)


def pair(g, h):
    f = LP / f"pair_{g}_{h}.csv"
    if f.exists(): return
    te = np.where((pid == g) | (pid == h))[0]; tr = np.where((pid != g) & (pid != h))[0]
    assert not {g, h} & set(pid[tr]) and not set(sess[tr]) & set(sess[te])
    frame(fit_all(tr, te), te, pair_g=g, pair_h=h).to_csv(f, index=False)


if __name__ == "__main__":
    T0 = time.time(); nj = int(os.environ.get("CSP_JOBS", "14"))
    f = REV / "P_scen_logo.csv"
    if not f.exists():
        parts = Parallel(n_jobs=nj)(delayed(logo_fold)(k, g) for k, g in enumerate(np.unique(pid)))
        pd.concat(parts, ignore_index=True).to_csv(f, index=False); print("LOGO", f"{time.time() - T0:.0f}s", flush=True)
    Parallel(n_jobs=nj, verbose=5)(delayed(pair)(g, h) for g, h in PAIRS)
    assert len(list(LP.glob("pair_*.csv"))) == 216
    print("done", f"{time.time() - T0:.0f}s", flush=True)
