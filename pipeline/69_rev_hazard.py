"""Step 69 (revision). Onset as a time-to-event problem: does telemetry add to an elapsed-time baseline hazard?

Most recordings change label once, so the question "beyond elapsed time" can be asked of the onset itself. Discrete-time
hazard models (one row per window at risk) are fitted under LOGO with the primary groups:
  risk set   the windows of each recording up to and including its first window at severity >= 1; recordings that
             never become positive contribute all their windows (censored at their end)
  baseline   logistic regression on a cubic B-spline of elapsed time (5 knots, linear extrapolation): the hazard of a
             first report given time only
  telemetry  the same plus the 76 primary features (robust scaling; L2 penalty of scikit-learn, C = 1), and GB on the 76
             features (HistGradientBoosting with the panel's hyperparameters, no class weights)
No class weights: the models estimate a hazard, not a decision. Each held-out group is scored by its held-out
log-likelihood per window at risk; models are compared with the baseline by the paired difference over the 22 groups
(t interval, Wilcoxon test). A positive difference means that the model predicts the timing of first reports better
than elapsed time does.

Output: outputs/tables/T_rev_hazard.csv"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import SplineTransformer, RobustScaler
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from csp import design
from csp.inference import *       # noqa: F401,F403

X = design.X[design.PRIMARY]; y = design.y; pid = design.pid; sess = design.sess; t = design.X.elapsed_in_session.values
first = pd.Series(y).groupby(sess).transform(lambda s: s.cummax().shift(fill_value=0)).values   # 1 after the first positive
risk = first == 0
Xr, yr, gr = X[risk].reset_index(drop=True), y[risk], pid[risk]
TCOL = list(X.columns).index("elapsed_in_session")
spline = lambda: SplineTransformer(n_knots=5, degree=3, extrapolation="linear")
MODELS = {
    "Time (spline)": lambda: make_pipeline(ColumnTransformer([("t", spline(), [TCOL])]), LogisticRegression(max_iter=2000)),
    "LR, time and 76 features": lambda: make_pipeline(ColumnTransformer([("t", spline(), [TCOL]), ("x", RobustScaler(), list(range(X.shape[1])))]),
                                                      LogisticRegression(max_iter=5000)),
    "GB, 76 features": lambda: HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=31, l2_regularization=1.0,
                                                              random_state=42)}

if __name__ == "__main__":
    ll = {m: {} for m in MODELS}
    for g in np.unique(gr):
        tr, te = gr != g, gr == g
        for m, make in MODELS.items():
            p = np.clip(make().fit(Xr.values[tr], yr[tr]).predict_proba(Xr.values[te])[:, 1], 1e-6, 1 - 1e-6)
            ll[m][g] = np.mean(yr[te] * np.log(p) + (1 - yr[te]) * np.log(1 - p))
    F = pd.DataFrame(ll); base = F["Time (spline)"]; rows = []
    for m in MODELS:
        dl = F[m] - base; h = sps.t.ppf(0.975, len(dl) - 1) * dl.std(ddof=1) / np.sqrt(len(dl)) if m != "Time (spline)" else np.nan
        rows.append(dict(model=m, groups=len(dl), windows_at_risk=int(risk.sum()), events=int(yr.sum()), loglik=F[m].mean(),
                         d=dl.mean(), lo=dl.mean() - h, hi=dl.mean() + h, better=int((dl > 1e-12).sum()),
                         p_w=sps.wilcoxon(dl).pvalue if (dl.abs() > 1e-12).any() else np.nan))
    T = pd.DataFrame(rows); T.to_csv(TABLES / "T_rev_hazard.csv", index=False); print(T.round(4).to_string())
