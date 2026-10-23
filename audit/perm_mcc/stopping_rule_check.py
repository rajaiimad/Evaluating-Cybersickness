"""Audit of step 59: is the fold-MCC p-value valid when the number of replicates is set by a stopping rule on dl?

Part A (existing replicates, no new fits): from outputs/tables/CTRL_PERM_STRAT.csv
  - reproduce the reported p_perm_mcc of T_rev_perm_strat.csv
  - correlation of dl and dmcc across null replicates, per learner
  - for GB and RF+GB, whose shared tree unit ran 200 replicates because the RF did, the fold-MCC p at the full 200
    replicates (a fixed budget, independent of their own dl stopping)
Part B (simulation of the procedure under an exact null): observed and null replicates are i.i.d. draws of a pair
  (dl, dmcc) with correlation rho; replicates are drawn until H = 10 have dl >= observed dl or CAP = 200 are drawn
  (step 59), and the fold-MCC p is (1 + #{dmcc >= observed dmcc}) / (1 + n) over the same n (step 59). Under a valid
  procedure P(p <= a) <= a. Each rho uses 200,000 simulated datasets, seed 71.

Usage: python audit/perm_mcc/stopping_rule_check.py      Output: audit/perm_mcc/stopping_rule_check.txt"""
import pathlib, sys
import numpy as np, pandas as pd
from scipy.stats import binomtest

ROOT = pathlib.Path(__file__).resolve().parents[2]; T = ROOT / "outputs" / "tables"
H, CAP = 10, 200
out = []
pr = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))

R = pd.read_csv(T / "CTRL_PERM_STRAT.csv"); S = pd.read_csv(T / "T_rev_perm_strat.csv").set_index("learner")
pr("Part A. Existing step 59 replicates")
for l in ["RF", "GB", "RF+GB", "LR", "MLP"]:
    g = R[R.learner == l]; o = g[g.rep < 0].iloc[0]; nul = g[g.rep >= 0].sort_values("rep")
    n = int(S.loc[l, "reps"]); h = nul.head(n); k = int((h.dmcc >= o.dmcc).sum()); p = (1 + k) / (1 + n)
    assert abs(p - S.loc[l, "p_perm_mcc"]) < 1e-12, (l, p, S.loc[l, "p_perm_mcc"])
    rho = np.corrcoef(nul.dl, nul.dmcc)[0, 1]
    kall = int((nul.dmcc >= o.dmcc).sum()); nall = len(nul)
    pr(f"  {l:6s} n(dl stop)={n:3d} k_mcc={k} p_mcc={p:.4f} (reported {S.loc[l,'p_perm_mcc']:.4f}, = 1/(1+n): {k == 0}) | "
       f"replicates on file={nall} k_all={kall} p_all={(1 + kall) / (1 + nall):.4f} | corr(dl,dmcc) null={rho:+.3f} | "
       f"observed dmcc={o.dmcc:+.4f}, null max={nul.dmcc.max():+.4f}, null mean={nul.dmcc.mean():+.4f}")

pr("")
pr("Part B. Simulated level of the step 59 fold-MCC p under an exact null (200,000 datasets per rho)")
rng = np.random.default_rng(71); M = 200_000
for rho in [0.0, 0.3, 0.6, 0.9, 1.0]:
    L = np.linalg.cholesky(np.array([[1, rho], [rho, 1]]) + 1e-12 * np.eye(2))
    Z = rng.standard_normal((M, CAP + 1, 2)) @ L.T          # column 0: observed, 1..CAP: null replicates
    dl, mc = Z[..., 0], Z[..., 1]
    ex_dl = np.cumsum(dl[:, 1:] >= dl[:, :1], axis=1); hit = ex_dl >= H
    n = np.where(hit.any(1), hit.argmax(1) + 1, CAP)
    ex_mc = np.cumsum(mc[:, 1:] >= mc[:, :1], axis=1); k = ex_mc[np.arange(M), n - 1]
    p = (1 + k) / (1 + n)
    res = []
    for a in (0.01, 0.05, 0.10):
        r = int((p <= a).sum()); ci = binomtest(r, M).proportion_ci(method="exact")
        res.append(f"P(p<={a:.2f}) = {r / M:.4f} [{ci.low:.4f}, {ci.high:.4f}]")
    pr(f"  rho={rho:.1f}: " + "; ".join(res) + f"; mean n = {n.mean():.1f}")
(pathlib.Path(__file__).with_suffix(".txt")).write_text("\n".join(out) + "\n", encoding="utf-8")
