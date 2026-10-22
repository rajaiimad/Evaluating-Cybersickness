"""Step 66 (revision). A more flexible time-only reference: the spline clock.

The clock is a logistic regression on elapsed time, so its probability is monotone in time. Reviewers asked whether a
stronger time-only reference would change the comparison. The spline clock is the same class-balanced logistic
regression on a cubic B-spline basis of elapsed time (5 knots, set before fitting, linear extrapolation), fitted under
LOGO with the scaling, folds and rule (w = 61, tau = 0.5) of the primary analysis. It uses no telemetry.

Outputs: outputs/predictions/P_rev_spline_clock.csv; outputs/tables/T_rev_spline_clock.csv (fold-mean MCC and alarm rate
of the clock and the spline clock, and paired comparisons of each detector and of the clock with the spline clock:
mean difference, 95% t interval, paired t and Wilcoxon p, Benjamini-Hochberg over the five detectors)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import SplineTransformer
from sklearn.linear_model import LogisticRegression
from csp import design
from csp.inference import *       # noqa: F401,F403


def spline_clock():
    return make_pipeline(SplineTransformer(n_knots=5, degree=3, extrapolation="linear"),
                         LogisticRegression(class_weight="balanced", max_iter=1000))


if __name__ == "__main__":
    design.run("rev_spline_clock", design.pid, ["elapsed_in_session"], {"Spline clock": spline_clock})
    prim = load("primary"); ck_ = load("primary_clock"); sp = load("rev_spline_clock")
    for P in (prim, ck_, sp): P["hard"] = np.nan
    S, PF = summarise(pd.concat([prim, ck_, sp], ignore_index=True), tm=False)
    ref = PF["Spline clock"]; idx = ref.index
    rows = []
    for m in SUP + ["Clock"]:
        x = PF[m].loc[idx]; dl = x - ref; h = dl.std(ddof=1) / np.sqrt(len(dl)) * sps.t.ppf(0.975, len(dl) - 1)
        rows.append(dict(model=m, mcc=x.mean(), ref_mcc=ref.mean(), d=dl.mean(), lo=dl.mean() - h, hi=dl.mean() + h,
                         p_t=sps.ttest_rel(x, ref).pvalue, p_w=sps.wilcoxon(x, ref).pvalue if (dl.abs() > 1e-12).any() else 1.0,
                         higher=int((dl > 1e-12).sum()), lower=int((dl < -1e-12).sum()), n=len(dl)))
    T = pd.DataFrame(rows); T["p_w_bh5"] = np.nan; det = T.model.isin(SUP); T.loc[det, "p_w_bh5"] = bh(T.loc[det, "p_w"].values)
    A = S.set_index("model")[["mcc", "alarm", "pooled_mcc"]].loc[["Clock", "Spline clock"]]
    T["ref_alarm"] = A.loc["Spline clock", "alarm"]; T["clock_alarm"] = A.loc["Clock", "alarm"]
    T.to_csv(TABLES / "T_rev_spline_clock.csv", index=False)
    print(A.round(3).to_string()); print(T.round(3).to_string())
