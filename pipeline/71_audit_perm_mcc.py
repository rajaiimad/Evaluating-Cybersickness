"""Step 71 (audit). Fold-MCC randomization test with a fixed replicate budget, separate from step 59.

Why: step 59 stops each learner's replicates by the Besag and Clifford rule on the time-matched statistic (dl) and
then reports the fold-MCC p-value (1 + k) / (1 + n) over the same n replicates. The fold-MCC p-values of RF, GB and
RF+GB in Table S9 / S20 are all k = 0, so they equal 1 / (1 + n) and their size is set by the dl stopping rule.
This step recomputes the fold-MCC test with a budget fixed in advance, independent of either statistic.

Prespecified before running (audit of 23 October 2026):
  statistic  dmcc = fold-mean MCC of the detector minus that of the clock, over the 16 two-class groups, at the primary
             rule (w = 61, tau = 0.5), LOGO fits; identical to C16.evaluate()["dmcc"]
  direction  one sided, upper tail (H1: the observed dmcc exceeds the null)
  budget     B = 1000 replicates per detector (rep 0 .. 999), no stopping
  p-value    (1 + #{null >= observed}) / (1 + B); ties count as exceedances
  multiplicity  Benjamini and Hochberg over the five detectors
  observed   replicate -1 (identity), refitted here, as in step 59
Null mechanisms:
  donor    the step 59 scheme unchanged (permuted() of step 59, same seeds [2029, rep]); reps 0..199 must reproduce the
           dmcc stored by step 59 (reproduction check)
  longonly sensitivity, an exact permutation: within each game only the long recordings are permuted; the seven
           shorter recordings keep their own telemetry, so no trajectory is duplicated and the identity is a member of
           the permutation set. It tests the narrower null that the long trajectories are exchangeable within a game.
           Seeds [2032, rep].
Only LOGO fits are needed for dmcc (no LPGO pair models), which makes 1000 replicates feasible.

Usage: python pipeline/71_audit_perm_mcc.py [donor|longonly|summary]   (B and CSP_JOBS from the environment)
Outputs (new files only): outputs/tables/AUDIT_PERM_MCC_<mech>.csv (one row per replicate and learner),
                          outputs/tables/T_audit_perm_mcc.csv (summary)"""
import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_k] = "1"
import sys, time, pathlib, importlib.util
from joblib import Parallel, delayed

HERE = pathlib.Path(__file__).resolve().parent
_s = importlib.util.spec_from_file_location("perm59", HERE / "59_rev_perm_strat.py"); C59 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C59)
C16 = C59.C16
from csp.inference import *       # noqa: F401,F403

B = int(os.environ.get("B", 1000))
UNITS = C59.UNITS


def permuted_longonly(rep):
    if rep < 0: return C59.XF
    rng = np.random.default_rng([2032, rep]); Xp = C59.XF.copy()
    for game in sorted(C59.STRATA):
        long_, _ = C59.STRATA[game]; src = dict(zip(long_, rng.permutation(long_)))
        for s in long_:
            ix = C59.RECS[s]; blk = C59.XF[C59.RECS[src[s]]]
            if len(blk) < len(ix): blk = np.vstack([blk, np.repeat(blk[-1:], len(ix) - len(blk), axis=0)])
            Xp[ix] = blk[:len(ix)]
    Xp[:, C59.KEEP] = C59.XF[:, C59.KEEP]
    return Xp


MECH = {"donor": C59.permuted, "longonly": permuted_longonly}


def dmcc_of(p):
    s = trailing(p, C16.sess, W); pred = (s >= TAU).astype(int)
    fm = pd.Series({g: rates(*counts(C16.y_all[C16.pid == g], pred[C16.pid == g]))["mcc"] for g in C16.TWO})
    return (fm - C16.CKF.loc[fm.index]).mean()


def one(mech, unit, rep):
    Xa = MECH[mech](rep); base = [n for n in UNITS[unit] if n != "RF+GB"]
    p = {n: np.empty(len(Xa)) for n in base}
    for tr, te in C16.FOLDS:
        for n, v in C59.fit_proba(Xa, tr, te, base).items(): p[n][te] = v
    if unit == "trees": p["RF+GB"] = (p["RF"] + p["GB"]) / 2
    return [dict(mech=mech, learner=n, rep=rep, dmcc=dmcc_of(p[n]), source="step71") for n in UNITS[unit]]


def summarise():
    rows = []
    for mech in MECH:
        f = TABLES / f"AUDIT_PERM_MCC_{mech}.csv"
        if not f.exists(): continue
        R = pd.read_csv(f)
        for l in ["RF", "GB", "RF+GB", "LR", "MLP"]:
            g = R[R.learner == l]; obs = g[g.rep < 0].dmcc.iloc[0]; nul = g[(g.rep >= 0) & (g.rep < B)].dmcc.values
            k = int((nul >= obs).sum())
            rows.append(dict(mech=mech, learner=l, B=len(nul), observed=obs, null_mean=nul.mean(), null_sd=nul.std(ddof=1),
                             null_q95=np.quantile(nul, 0.95), null_max=nul.max(), exceed=k, p=(1 + k) / (1 + len(nul))))
    S = pd.DataFrame(rows)
    S["p_bh"] = np.concatenate([C59.bh(g.p.values) for _, g in S.groupby("mech", sort=False)])
    return S


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "donor"
    if mode != "summary":
        out = TABLES / f"AUDIT_PERM_MCC_{mode}.csv"
        if mode == "donor" and not out.exists():
            # the step 59 replicates are the same seeds and the same fits; reps -1 and 0 were refitted here and matched to
            # within 1e-16 for every learner, so they are reused (marked source=step59) and the rest are fitted below
            P = pd.read_csv(TABLES / "CTRL_PERM_STRAT.csv")[["learner", "rep", "dmcc"]]
            P.insert(0, "mech", "donor"); P["source"] = "step59"; P.to_csv(out, index=False)
        done =set(map(tuple, pd.read_csv(out)[["learner", "rep"]].values)) if out.exists() else set()
        todo = [(mode, u, r) for r in range(-1, B) for u in UNITS if (UNITS[u][0], r) not in done]
        todo.sort(key=lambda g: (g[2], {"MLP": 0, "trees": 1, "LR": 2}[g[1]]))
        nj = int(os.environ.get("CSP_JOBS", "15")); T0 = time.time(); print(len(todo), "tasks", flush=True); buf = []
        for k, rows in enumerate(Parallel(n_jobs=nj, return_as="generator_unordered")(delayed(one)(*g) for g in todo)):
            buf += rows
            if len(buf) >= 60 or k + 1 == len(todo):
                R = pd.read_csv(out) if out.exists() else pd.DataFrame()
                pd.concat([R, pd.DataFrame(buf)], ignore_index=True).to_csv(out, index=False); buf = []
                print(k + 1, "/", len(todo), f"{time.time() - T0:.0f}s", flush=True)
    S = summarise(); S.to_csv(TABLES / "T_audit_perm_mcc.csv", index=False); print(S.round(4).to_string())
