"""Step 67 (revision). Threshold-free added value over the clock: Brier score and log loss.

Fold MCC compares decisions at one operating rule. A proper scoring rule compares the probabilities themselves, the
usual way to ask whether a model adds predictive value to a base model. The smoothed probabilities of the primary rule
(trailing mean over w = 61 windows, primary LOGO fits, no refit) are scored within each of the 22 held-out groups; each
detector is compared with the clock by the paired difference over the groups (95% t interval, Wilcoxon test,
Benjamini-Hochberg over the five detectors). Lower is better for both scores. The detectors and the clock use balanced
class weights (the MLP none), so the scores also reflect calibration, which the threshold rule ignores.

Output: outputs/tables/T_rev_proper_scores.csv"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from sklearn.metrics import log_loss
from csp.inference import *       # noqa: F401,F403

if __name__ == "__main__":
    P = pd.concat([load("primary"), load("primary_clock")], ignore_index=True); S = {}
    for m, g in P.groupby("model"):
        s = np.clip(trailing(g.proba.values, g.session.values, W), 1e-6, 1 - 1e-6); g = g.assign(s=s)
        S[m] = {u: (((h.s - h.y) ** 2).mean(), log_loss(h.y, h.s, labels=[0, 1])) for u, h in g.groupby("participant")}
    rows = []
    for k, score in enumerate(("brier", "log_loss")):
        F = pd.DataFrame({m: {u: v[k] for u, v in r.items()} for m, r in S.items()})
        assert len(F) == 22
        for m in SUP:
            dl = F[m] - F.Clock; h = sps.t.ppf(0.975, len(dl) - 1) * dl.std(ddof=1) / np.sqrt(len(dl))
            rows.append(dict(score=score, model=m, value=F[m].mean(), clock=F.Clock.mean(), d=dl.mean(), lo=dl.mean() - h,
                             hi=dl.mean() + h, better=int((dl < 0).sum()), n=len(dl), p_w=sps.wilcoxon(dl).pvalue))
    T = pd.DataFrame(rows); T["p_w_bh5"] = T.groupby("score").p_w.transform(lambda p: bh(p.values))
    T.to_csv(TABLES / "T_rev_proper_scores.csv", index=False); print(T.round(3).to_string())
