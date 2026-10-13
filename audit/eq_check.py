"""Independent check of equations (1) to (13) and (S1) to (S5): each quantity is recomputed from the raw file and the
saved predictions by literal implementation of the printed formula (explicit loops, no project function), then
compared with what the project code produced. Usage: eq_check.py <repository>"""
import sys, pathlib, itertools
import numpy as np, pandas as pd
REPO = pathlib.Path(sys.argv[1]); TB = REPO / "outputs" / "tables"; PR = REPO / "outputs" / "predictions"
raw = pd.read_csv(REPO / "data" / "raw" / "dataset.csv")
demo = ["UserGenere", "UserAge", "UserExperience", "UserFlicker", "UserGlassesUse", "UserVisionProblems", "UserEyeDominance"]
rec = np.r_[0, np.cumsum(np.diff(raw.TimeStamp.values) < 0)]; grp = raw.groupby(demo, sort=False).ngroup().values
s = raw.DiscomfortLevel.values; t = raw.TimeStamp.values
print("severity values present:", sorted(np.unique(s)))

# (1)
y = np.where(s >= 1, 1, 0); print("(1) positives", y.sum(), "| windows", len(y))

# (2) (3) (4): literal loops for every channel and horizon, compared with the feature matrix of the project code
sys.path.insert(0, str(REPO / "src"))
from csp.design import X as XF, PRIMARY, cols            # the features the models were fitted on
CH = ["CameraFieldOfView", "PlayerSpeed", "PlayerAcceleration", "CameraRotationX", "CameraRotationY", "CameraRotationZ",
      "PlayerPositionX", "PlayerPositionY", "PlayerPositionZ", "GameFps"]
dm = ds = dd = 0.0; scale = 0.0
for c in CH:
    x = raw[c].values.astype(float)
    for W in (30, 120, 300):
        mu = np.empty(len(x)); sg = np.empty(len(x))
        for r in np.unique(rec):
            ix = np.where(rec == r)[0]
            for pos, i in enumerate(ix, 1):                       # pos = t = 1, 2, ...
                n = min(W, pos); seg = x[i - n + 1:i + 1]
                mu[i] = seg.sum() / n
                sg[i] = 0.0 if n == 1 else np.sqrt(((seg - mu[i]) ** 2).sum() / (n - 1))
        dm = max(dm, np.abs(mu - XF[f"{c}_mean{W}"].values).max() / max(1.0, np.abs(mu).max()))
        ds = max(ds, np.abs(sg - XF[f"{c}_sd{W}"].values).max() / max(1.0, np.abs(sg).max()))
    df = np.zeros(len(x))
    for r in np.unique(rec):
        ix = np.where(rec == r)[0]; df[ix[1:]] = x[ix[1:]] - x[ix[:-1]]
    dd = max(dd, np.abs(df - XF[f"{c}_diff"].values).max() / max(1.0, np.abs(df).max()))
print(f"(2) trailing mean: largest relative difference from the code {dm:.1e}")
print(f"(3) trailing sd:   largest relative difference from the code {ds:.1e}")
print(f"(4) difference:    largest relative difference from the code {dd:.1e}   (features are stored in single precision, about 1e-7)")
fov = [c for c in cols if c.startswith("CameraFieldOfView") and c not in PRIMARY]
print("    field of view features dropped from the primary set:", fov, "| values per recording:",
      int(raw.groupby(rec).CameraFieldOfView.nunique().max()), "| distinct values:", raw.CameraFieldOfView.nunique())
print("    primary features:", len(PRIMARY), "| full:", len(cols))

# (5) against RobustScaler for one fold
from sklearn.preprocessing import RobustScaler
Xa = XF[PRIMARY].values.astype(float); tr = grp != 0
med = np.median(Xa[tr], axis=0); iqr = np.percentile(Xa[tr], 75, axis=0) - np.percentile(Xa[tr], 25, axis=0)
z = (Xa - med) / np.where(iqr == 0, 1.0, iqr); zs = RobustScaler().fit(Xa[tr]).transform(Xa)
print(f"(5) scaling: largest difference from RobustScaler {np.abs(z - zs).max():.1e} | features with zero training IQR in this fold: {(iqr == 0).sum()}")

# (6) to (11): primary rule, fold MCC, BA, episode recall from the saved probabilities
P = pd.concat([pd.read_csv(PR / "P_primary.csv"), pd.read_csv(PR / "P_primary_clock.csv")], ignore_index=True)
TP_ = pd.read_csv(TB / "T_primary.csv").set_index("model"); EP = pd.read_csv(TB / "T_episodes.csv"); EP = EP.set_index("model") if "model" in EP else EP
SM = {}
for m, g in P.groupby("model", sort=False):
    g = g.reset_index(drop=True); q = g.proba.values; qb = np.empty(len(q))
    for r in g.session.unique():
        ix = np.where(g.session.values == r)[0]
        for pos, i in enumerate(ix, 1):
            n = min(61, pos); qb[i] = q[i - n + 1:i + 1].sum() / n                      # (8)
    yh = np.where(qb >= 0.5, 1, 0)                                                    # (9)
    SM[m] = (g, qb, yh)
    mcc, ba = [], []
    for u in g.participant.unique():
        ix = g.participant.values == u; yy, pp = g.y.values[ix], yh[ix]
        if 0 < yy.sum() < len(yy):
            TP = ((pp == 1) & (yy == 1)).sum(); TN = ((pp == 0) & (yy == 0)).sum(); FP = ((pp == 1) & (yy == 0)).sum(); FN = ((pp == 0) & (yy == 1)).sum()
            den = np.sqrt(float(TP + FP) * (TP + FN) * (TN + FN) * (TN + FP))
            mcc.append(0.0 if den == 0 else (TP * TN - FP * FN) / den)                 # (11)
            ba.append(0.5 * (TP / (TP + FN) + TN / (TN + FP)))                        # (10)
    E = det = 0                                                                        # (7)
    for r in g.session.unique():
        ix = np.where(g.session.values == r)[0]; yy, pp = g.y.values[ix], yh[ix]
        st = [i for i in range(len(yy)) if yy[i] == 1 and (i == 0 or yy[i - 1] == 0)]
        for a in st:
            b = a
            while b + 1 < len(yy) and yy[b + 1] == 1: b += 1
            E += 1; det += int(pp[a:b + 1].max() == 1)
    print(f"(8)-(11) {m:6} fold MCC {np.mean(mcc):.6f} (code {TP_.loc[m, 'mcc']:.6f}) | BA {np.mean(ba):.6f} (code {TP_.loc[m, 'bal_acc']:.6f})"
          f" | (7) episode recall {det}/{E} = {det / E:.6f} (code {EP.loc[m, 'ep_recall'] if m in EP.index else float('nan'):.6f})")


def psi(u, v): return 1.0 if u > v else (0.5 if u == v else 0.0)


# (12) pooled and (13) LPGO for every detector, by explicit sums over pairs
LA = pd.read_csv(TB / "T_lpgo_atime.csv").set_index("model")
g0 = SM["RF"][0]; yy = g0.y.values; tt = g0.t.values; gg = g0.participant.values; b = (tt // 30).astype(int)
keep = [k for k in np.unique(b) if yy[b == k].sum() >= 20 and (1 - yy[b == k]).sum() >= 20]
den = sum(float(yy[b == k].sum()) * float((1 - yy[b == k]).sum()) for k in keep)
within = sum(float(((b == k) & (yy == 1) & (gg == u)).sum()) * float(((b == k) & (yy == 0) & (gg == u)).sum()) for k in keep for u in np.unique(gg))
print(f"(12) bins kept {len(keep)} | windows in kept bins {int(np.isin(b, keep).sum())} | pairs {den:.0f} | between groups {100 * (1 - within / den):.1f}%")


def pair_sum(sp, sn):                                             # sum of psi over all pairs, by sorting (exact)
    v = np.sort(sn); lo = np.searchsorted(v, sp, "left"); hi = np.searchsorted(v, sp, "right"); return lo.sum() + 0.5 * (hi - lo).sum()


# elapsed time itself
num = sum(pair_sum(tt[(b == k) & (yy == 1)], tt[(b == k) & (yy == 0)]) for k in keep)
print(f"(12) elapsed time {num / den:.6f} (code {LA.tm_ref.iloc[0]:.6f})")
# brute force check of psi on one bin
k = keep[0]; sp, sn = SM["RF"][1][(b == k) & (yy == 1)], SM["RF"][1][(b == k) & (yy == 0)]
assert abs(sum(psi(u, v) for u in sp for v in sn) - pair_sum(sp, sn)) < 1e-9
key = lambda g: pd.Series(list(zip(g.participant, g.session, np.round(g.t, 6))))
base = key(g0)
for m in ["RF", "GB", "RF+GB", "LR", "MLP"]:
    g, qb, _ = SM[m]; assert (key(g) == base).all()
    pooled = sum(pair_sum(qb[(b == k) & (yy == 1)], qb[(b == k) & (yy == 0)]) for k in keep) / den
    num = 0.0
    for u in np.unique(gg):                                       # within group pairs: the leave one group out model
        for k in keep:
            num += pair_sum(qb[(b == k) & (yy == 1) & (gg == u)], qb[(b == k) & (yy == 0) & (gg == u)])
    for f in sorted((PR / "lpgo").glob("pair_*.csv")):            # between group pairs: the model trained without both
        L = pd.read_csv(f); L = L[L.model == m].reset_index(drop=True); u, h = int(L.pair_g[0]), int(L.pair_h[0])
        q = L.proba.values; sb = np.empty(len(q))
        for r in L.session.unique():
            ix = np.where(L.session.values == r)[0]
            c = np.cumsum(q[ix]); n = np.minimum(61, np.arange(1, len(ix) + 1)); sb[ix] = (c - np.r_[np.zeros(61), c[:-61]][:len(ix)]) / n
        bb = (L.t.values // 30).astype(int); ly = L.y.values; lg = L.participant.values
        for k in keep:
            for a, c_ in ((u, h), (h, u)):
                num += pair_sum(sb[(bb == k) & (ly == 1) & (lg == a)], sb[(bb == k) & (ly == 0) & (lg == c_)])
    print(f"(12) {m:6} pooled {pooled:.6f} (code {LA.loc[m, 'tm_pooled']:.6f}) | (13) LPGO {num / den:.6f} (code {LA.loc[m, 'tm_lpo']:.6f})")

# (S1): one bootstrap draw by concatenation against the closed form, for elapsed time
rng = np.random.default_rng(0); ug = np.unique(gg); draw = rng.choice(ug, len(ug)); mlt = np.bincount(np.searchsorted(ug, draw), minlength=len(ug))
ix = np.concatenate([np.where(gg == u)[0] for u in draw]); y2, t2, b2 = yy[ix], tt[ix], b[ix]
k2 = [k for k in np.unique(b2) if y2[b2 == k].sum() >= 20 and (1 - y2[b2 == k]).sum() >= 20]
direct = sum(pair_sum(t2[(b2 == k) & (y2 == 1)], t2[(b2 == k) & (y2 == 0)]) for k in k2) / sum(float(y2[b2 == k].sum()) * float((1 - y2[b2 == k]).sum()) for k in k2)
num = dn = 0.0
for k in np.unique(b):
    p_b = np.array([((b == k) & (yy == 1) & (gg == u)).sum() for u in ug], float); n_b = np.array([((b == k) & (yy == 0) & (gg == u)).sum() for u in ug], float)
    if mlt @ p_b < 20 or mlt @ n_b < 20: continue
    C = np.array([[pair_sum(tt[(b == k) & (yy == 1) & (gg == u)], tt[(b == k) & (yy == 0) & (gg == h)]) for h in ug] for u in ug])
    num += mlt @ C @ mlt; dn += (mlt @ p_b) * (mlt @ n_b)
print(f"(S1) first bootstrap draw: concatenated resample {direct:.9f} | closed form {num / dn:.9f}")

# (S2) to (S4) from the pooled operating point of the RF
DP = pd.read_csv(TB / "T_deploy.csv"); r = TP_.loc["RF"]
for pi in (0.44, 0.10, 0.01):
    ppv = r.pooled_rec * pi / (r.pooled_rec * pi + (1 - r.pooled_spec) * (1 - pi)); npv = r.pooled_spec * (1 - pi) / (r.pooled_spec * (1 - pi) + (1 - r.pooled_rec) * pi)
    c = DP[(DP.model == "RF") & (abs(DP.pi - pi) < 1e-9)].iloc[0]
    print(f"(S2)-(S4) RF pi={pi}: PPV {ppv:.4f} ({c.ppv:.4f}) NPV {npv:.4f} ({c.npv:.4f}) FA {1000 * (1 - pi) * (1 - r.pooled_spec):.1f} ({c.fa_per_1000:.1f})")

# (S5)
AS = pd.read_csv(TB / "T_asev_paired.csv").set_index("model")
for m in ["RF", "LR", "Clock"]:
    g, qb, _ = SM[m]; num = dn = 0.0
    for u in g.participant.unique():
        s3 = qb[(g.participant.values == u) & (g.sev.values == 3)]; s1 = qb[(g.participant.values == u) & (g.sev.values == 1)]
        if len(s3) and len(s1): num += pair_sum(s3, s1); dn += len(s3) * len(s1)
    ref = AS.a_sev_clock.iloc[0] if m == "Clock" else AS.loc[m, "a_sev"]
    print(f"(S5) {m:6} A_sev {num / dn:.6f} (code {ref:.6f}) | pairs {dn:.0f}")
