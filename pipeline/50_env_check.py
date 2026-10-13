"""Step 50 (revision). Environment check for the revision analyses (steps 51 to 58).

The revision analyses were run in a newer Python environment than the reported run (README). This step refits the
primary LOGO models of RF, GB, LR and the clock in the current environment and compares their held out probabilities
with the shipped predictions (outputs/predictions/P_primary.csv, P_primary_clock.csv). It writes
outputs/tables/T_rev_env_check.csv (largest absolute difference per model, fit time per fold) and fails if a
difference exceeds 1e-6. The MLP is not refitted here (it is not used by the revision analyses).

Run: python pipeline/50_env_check.py"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
import platform, sklearn, scipy
from csp.design import *          # noqa: F401,F403
from csp.paths import TABLES

if __name__ == "__main__":
    ship = pd.read_csv(PRED / "P_primary.csv"); shipc = pd.read_csv(PRED / "P_primary_clock.csv")
    rows = []
    for name, feats, fn, ref in [("RF", PRIMARY, rf, ship), ("GB", PRIMARY, gb, ship), ("LR", PRIMARY, lr, ship),
                                 ("Clock", ["elapsed_in_session"], lr, shipc)]:
        Xa = X[feats].values.astype(float); t0 = time.time(); dmax = 0.0
        for k, g in enumerate(np.unique(pid)):
            tr, te = np.where(pid != g)[0], np.where(pid == g)[0]
            sc = RobustScaler().fit(Xa[tr]); m = fn().fit(sc.transform(Xa[tr]), y[tr])
            p = m.predict_proba(sc.transform(Xa[te]))[:, 1]
            r = ref[(ref.model == name) & (ref.fold == k)]
            assert (r.participant.values == g).all() and np.allclose(r.t.values, t_el[te])
            dmax = max(dmax, float(np.abs(r.proba.values - p).max()))
        rows.append(dict(model=name, max_abs_diff=dmax, seconds_per_fold=(time.time() - t0) / 22,
                         python=platform.python_version(), sklearn=sklearn.__version__, numpy=np.__version__,
                         pandas=pd.__version__, scipy=scipy.__version__))
        print(rows[-1], flush=True)
    T = pd.DataFrame(rows); T.to_csv(TABLES / "T_rev_env_check.csv", index=False)
    assert (T.max_abs_diff <= 1e-6).all(), "the current environment does not reproduce the shipped predictions"
    print("environment reproduces the shipped primary predictions")
