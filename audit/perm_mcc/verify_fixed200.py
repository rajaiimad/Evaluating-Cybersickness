"""Audit check 1: the fixed-200 fold-MCC randomization results, reproduced from the saved outputs.

Fixed budget B = 200 (the CAP of step 59), replicates 0..199 of the donor null, for every detector.
  a. completeness: each learner has exactly the replicates -1..199, no duplicates, in outputs/tables/AUDIT_PERM_MCC_donor.csv
  b. provenance: rows copied from step 59 (source=step59) equal outputs/tables/CTRL_PERM_STRAT.csv exactly
  c. refits: a fixed sample of replicates is refitted from scratch with the step 71 code and compared with the saved
     value (step 59 rows and step 71 rows, every learner)
  d. p = (1 + k) / (1 + B), k = #{null >= observed}, computed twice (pandas count and numpy rank), BH over five
Writes outputs/tables/T_audit_perm_mcc_fixed200.csv and audit/perm_mcc/verify_fixed200.txt.

Usage: python audit/perm_mcc/verify_fixed200.py [--no-refit]"""
import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_k] = "1"
import sys, pathlib, importlib.util
import numpy as np, pandas as pd
from joblib import Parallel, delayed

ROOT = pathlib.Path(__file__).resolve().parents[2]; T = ROOT / "outputs" / "tables"; B = 200
OUT = []
pr = lambda *a: (print(*a, flush=True), OUT.append(" ".join(str(x) for x in a)))
LEARNERS = ["RF", "GB", "RF+GB", "LR", "MLP"]
UNIT = {"RF": "trees", "GB": "trees", "RF+GB": "trees", "LR": "LR", "MLP": "MLP"}
# fixed before looking at any refit: two step 59 replicates and two step 71 replicates per unit where both exist
SAMPLE = {"trees": [37, 199, 230, 287], "LR": [11, 28, 95, 180], "MLP": [23, 59, 120, 199]}


def bh(p):
    p = np.asarray(p, float); o = np.argsort(p); q = p[o] * len(p) / np.arange(1, len(p) + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]; out = np.empty_like(q); out[o] = np.minimum(q, 1); return out


A = pd.read_csv(T / "AUDIT_PERM_MCC_donor.csv"); S59 = pd.read_csv(T / "CTRL_PERM_STRAT.csv")
pr("a/b. completeness and provenance")
for l in LEARNERS:
    g = A[(A.learner == l) & (A.rep < B)]
    assert not g.duplicated(["learner", "rep"]).any(), l
    assert sorted(g.rep) == list(range(-1, B)), (l, len(g))
    m = g[g.source == "step59"].merge(S59[S59.learner == l][["rep", "dmcc"]], on="rep", suffixes=("", "_59"))
    assert (m.dmcc == m.dmcc_59).all(), l
    pr(f"  {l:6s} reps -1..{B - 1} complete; {len(m)} rows from step 59 identical to CTRL_PERM_STRAT.csv; "
       f"{(g.source == 'step71').sum()} rows fitted by step 71")

if "--no-refit" not in sys.argv:
    pr("c. refits from scratch")
    sys.argv = ["x"]
    s = importlib.util.spec_from_file_location("a71", ROOT / "pipeline" / "71_audit_perm_mcc.py"); M = importlib.util.module_from_spec(s)
    cwd = os.getcwd(); os.chdir(ROOT); s.loader.exec_module(M)
    jobs = [(u, r) for u, reps in SAMPLE.items() for r in reps]
    res = Parallel(n_jobs=len(jobs))(delayed(M.one)("donor", u, r) for u, r in jobs); os.chdir(cwd)
    worst = 0.0
    for rows in res:
        for x in rows:
            row = A[(A.learner == x["learner"]) & (A.rep == x["rep"])].iloc[0]; d = abs(x["dmcc"] - row.dmcc); worst = max(worst, d)
            pr(f"  {x['learner']:6s} rep {x['rep']:3d} ({row.source}): refit {x['dmcc']:+.6f} saved {row.dmcc:+.6f} |diff| {d:.1e}")
    assert worst < 1e-9, worst
    pr(f"  largest difference {worst:.1e}")

pr("d. fixed-200 p-values")
rows = []
for l in LEARNERS:
    g = A[A.learner == l]; obs = g[g.rep == -1].dmcc.iloc[0]; nul = g[(g.rep >= 0) & (g.rep < B)].sort_values("rep").dmcc.values
    k1 = int((nul >= obs).sum())
    k2 = int(len(nul) - np.searchsorted(np.sort(nul), obs, side="left"))       # same count by rank
    assert k1 == k2, (l, k1, k2)
    rows.append(dict(learner=l, B=len(nul), observed=obs, null_mean=nul.mean(), null_max=nul.max(), exceed=k1,
                     p=(1 + k1) / (1 + len(nul))))
F = pd.DataFrame(rows); F["p_bh"] = bh(F.p.values)
S = pd.read_csv(T / "T_rev_perm_strat.csv").set_index("learner")
F["reps_seq"] = [int(S.loc[l, "reps"]) for l in F.learner]; F["p_seq"] = [S.loc[l, "p_perm_mcc"] for l in F.learner]
for r in F.itertuples():
    pr(f"  {r.learner:6s} observed {r.observed:+.4f} null mean {r.null_mean:+.4f} null max {r.null_max:+.4f} k {r.exceed:3d}/{r.B} "
       f"p {r.p:.4f} BH {r.p_bh:.4f} | sequential: {r.reps_seq} replicates, p {r.p_seq:.4f}")
F.to_csv(T / "T_audit_perm_mcc_fixed200.csv", index=False)
(pathlib.Path(__file__).with_suffix(".txt")).write_text("\n".join(OUT) + "\n", encoding="utf-8")
