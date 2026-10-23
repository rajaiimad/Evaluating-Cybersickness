"""Audit check 2: does the simulation of stopping_rule_check.py evaluate the actual step 59 procedure, under relevant nulls?

C1. Same procedure: the simulated rule (stop at H = 10 exceedances of dl or CAP = 200; fold-MCC p = (1 + k) / (1 + n)
    over the same n, ties counted as exceedances) is applied to the saved step 59 replicates, in replicate order, and
    must reproduce the reported replicate count, time-matched p and fold-MCC p of every learner (it is also compared
    with step 59's own mc_p()).
C2. Relevant nulls: the observed value and the null replicates are drawn i.i.d. from the empirical joint distribution
    of (dl, dmcc) in each learner's saved null replicates (resampling pairs), which keeps the real marginals, ties and
    dependence. 100,000 datasets per learner.
C3. Other dependence: Gaussian copula with rho = -0.5, and a t copula (3 df, rho = 0.7) with tail dependence.
All of C2 and C3 assume an exact null (observed exchangeable with the replicates): they evaluate the stopping rule, not
the donor approximation of the null. Seed 72.

Usage: python audit/perm_mcc/stopping_rule_check2.py      Output: audit/perm_mcc/stopping_rule_check2.txt"""
import pathlib, importlib.util, sys
import numpy as np, pandas as pd
from scipy.stats import binomtest, t as tdist

ROOT = pathlib.Path(__file__).resolve().parents[2]; T = ROOT / "outputs" / "tables"; H, CAP = 10, 200
OUT = []
pr = lambda *a: (print(*a, flush=True), OUT.append(" ".join(str(x) for x in a)))


def rule(dl_obs, dl_null, mc_obs, mc_null):
    """The simulated procedure for one dataset (null arrays in replicate order)."""
    k = np.cumsum(dl_null >= dl_obs); hit = np.where(k >= H)[0]
    n = hit[0] + 1 if len(hit) else min(len(dl_null), CAP)
    p_dl = H / n if len(hit) else (1 + k[n - 1]) / (1 + n)
    return n, p_dl, (1 + int((mc_null[:n] >= mc_obs).sum())) / (1 + n)


def rule_vec(dl, mc):
    """Vectorised rule; column 0 observed, 1..CAP null."""
    ex = np.cumsum(dl[:, 1:] >= dl[:, :1], axis=1); hit = ex >= H
    n = np.where(hit.any(1), hit.argmax(1) + 1, CAP)
    k = np.cumsum(mc[:, 1:] >= mc[:, :1], axis=1)[np.arange(len(n)), n - 1]
    return (1 + k) / (1 + n), n


def level(p, label, n):
    s = []
    for a in (0.01, 0.05, 0.10):
        r = int((p <= a).sum()); ci = binomtest(r, len(p)).proportion_ci(method="exact")
        s.append(f"P(p<={a:.2f}) = {r / len(p):.4f} [{ci.low:.4f}, {ci.high:.4f}]")
    pr(f"  {label}: " + "; ".join(s) + f"; mean n = {n.mean():.1f}")


sys.argv = ["x"]
_s = importlib.util.spec_from_file_location("perm59", ROOT / "pipeline" / "59_rev_perm_strat.py")
C59 = importlib.util.module_from_spec(_s); _s.loader.exec_module(C59)
R = pd.read_csv(T / "CTRL_PERM_STRAT.csv"); S = pd.read_csv(T / "T_rev_perm_strat.csv").set_index("learner")
pr("C1. The simulated rule on the saved step 59 replicates")
for l in ["RF", "GB", "RF+GB", "LR", "MLP"]:
    g = R[R.learner == l]; o = g[g.rep < 0].iloc[0]; nul = g[g.rep >= 0].sort_values("rep")
    n, p_dl, p_mc = rule(o.dl, nul.dl.values, o.dmcc, nul.dmcc.values)
    n59 = C59.mc_p(nul.dl, o.dl)[1]
    ok = (n == S.loc[l, "reps"] == n59 and abs(p_dl - S.loc[l, "p_perm"]) < 1e-12 and abs(p_mc - S.loc[l, "p_perm_mcc"]) < 1e-12)
    assert ok, l
    pr(f"  {l:6s} n {n} (reported {int(S.loc[l, 'reps'])}, mc_p {n59}); p dl {p_dl:.4f} (reported {S.loc[l, 'p_perm']:.4f}); "
       f"p fold MCC {p_mc:.4f} (reported {S.loc[l, 'p_perm_mcc']:.4f}): identical")

rng = np.random.default_rng(72); M = 100_000
pr("C2. Exact null drawn from each learner's empirical joint null distribution of (dl, dmcc)")
for l in ["RF", "GB", "RF+GB", "LR", "MLP"]:
    g = R[(R.learner == l) & (R.rep >= 0)]; P = g[["dl", "dmcc"]].values
    idx = rng.integers(len(P), size=(M, CAP + 1)); p, n = rule_vec(P[idx, 0], P[idx, 1])
    level(p, f"{l:6s} ({len(P)} pairs, corr {np.corrcoef(P.T)[0, 1]:+.2f})", n)
pr("C3. Other dependence structures")
for label, rho, df in (("Gaussian rho -0.5", -0.5, None), ("t copula 3 df rho 0.7", 0.7, 3)):
    L = np.linalg.cholesky(np.array([[1, rho], [rho, 1]])); Z = rng.standard_normal((M, CAP + 1, 2)) @ L.T
    if df: Z = Z / np.sqrt(rng.chisquare(df, size=(M, CAP + 1, 1)) / df)
    p, n = rule_vec(Z[..., 0], Z[..., 1]); level(p, label, n)
(pathlib.Path(__file__).with_suffix(".txt")).write_text("\n".join(OUT) + "\n", encoding="utf-8")
