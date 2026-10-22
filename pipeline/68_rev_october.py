"""Step 68 (revision). Replication on the raw-archive sessions that are not in dataset.csv, with position-free detectors.

24 of the 25 unmerged sessions with at least 250 windows lack the three player position channels (step 64), so the
detectors of the paper cannot be applied to them. This step evaluates position-free variants instead: the 76 primary
features minus the 21 computed from position (55 features), with the learners, hyperparameters, rule (w = 61,
tau = 0.5) and clock of the primary analysis.

  1. December, LOGO: the position-free detectors under the primary design, to show what dropping position costs.
  2. October: every model is fitted once on all 35 December recordings and scored once on the unmerged long sessions.
     Sessions are grouped by their descriptor profile, as in the primary analysis. Per profile with both classes: fold
     MCC of the primary rule against the clock (paired t interval, Wilcoxon test, Benjamini-Hochberg over the five
     detectors), and the time-matched AUC minus elapsed time (one model scores every window, so no pooling bias; group
     bootstrap intervals, descriptive). Results for all sessions and for the sessions whose descriptor profile does not
     occur in December (the others may be the same people recorded again).

The categorical codes of the raw files (for example "background") are mapped to the codes of dataset.csv by matching
the 35 merged raw sessions to their recordings in dataset.csv; the mapping is asserted to be one to one.

Outputs: outputs/predictions/P_rev_nopos.csv, P_rev_october.csv; outputs/tables/T_rev_october.csv,
T_rev_october_facts.csv"""
import sys, io, pathlib, zipfile, xml.etree.ElementTree as ET
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from sklearn.preprocessing import RobustScaler
from csp import design
from csp.data import make_features, DEMO
from csp.paths import RAW, PRED
from csp.inference import *       # noqa: F401,F403

NOPOS = [c for c in design.PRIMARY if not c.startswith("PlayerPosition")]
assert len(NOPOS) == 55
PANEL = {"RF": design.rf, "GB": design.gb, "RF+GB": None, "LR": design.lr, "MLP": lambda g: design.GroupEarlyStopMLP(g)}
COND = ["StaticFrame", "CameraAutoMovement", "RegionOfInterest"]
NUMS = ["TimeStamp", "CameraFieldOfView", "PlayerSpeed", "PlayerAcceleration", "CameraRotationX", "CameraRotationY",
        "CameraRotationZ", "GameFps", "DiscomfortLevel"]
num = lambda s: pd.to_numeric(s.astype(str).str.replace(",", "."), errors="coerce")
z = zipfile.ZipFile(RAW / "RAW_DATABASE.zip")
U = pd.read_csv(TABLES / "T_rev_raw_unused.csv")


def raw(folder):
    return pd.DataFrame([{c.tag: c.text for c in e} for e in ET.parse(io.BytesIO(z.read(f"RAW_DATABASE/{folder}/FILE.xml"))).getroot().findall("Data")])


def sig(rot, n): return (n, tuple(np.round(np.asarray(rot, float)[:20], 4)))


# ---- 1. code mapping from the merged sessions
D = design.d; dsig = {sig(g.CameraRotationY.values, len(g)): s for s, g in D.groupby("session")}
pairs = {c: set() for c in COND}; dec_profiles = set()
for r in U[U.in_merged_file].itertuples():
    R = raw(r.folder); s = dsig[sig(num(R.CameraRotationY).values, len(R))]; g = D[D.session == s]
    for c in COND: pairs[c] |= set(zip(R[c], g[c].values))
    dec_profiles.add(tuple(R[DEMO].iloc[0]))
MAP = {}
for c, p in pairs.items():
    m = dict(p); assert len(m) == len(p) == len({v for _, v in p}), (c, p)   # one to one
    MAP[c] = m

# ---- 2. the unmerged long sessions
rows = []
for k, r in enumerate(U[(~U.in_merged_file) & (U.windows >= 250)].itertuples()):
    R = raw(r.folder); O = pd.DataFrame({c: num(R[c]) for c in NUMS})
    for c in COND:
        assert set(R[c]) <= set(MAP[c]), (c, set(R[c]))
        O[c] = R[c].map(MAP[c]).astype(D[c].dtype)
    for c in ("PlayerPositionX", "PlayerPositionY", "PlayerPositionZ"): O[c] = 0.0   # not used: no position feature in NOPOS
    prof = tuple(R[DEMO].iloc[0]); O["profile"] = "|".join(prof); O["new_profile"] = prof not in dec_profiles
    for c in DEMO: O[c] = 0                                                           # descriptors are not features
    O["session"] = 1000 + k; O["folder"] = r.folder; rows.append(O)
O = pd.concat(rows, ignore_index=True); O["y"] = (O.DiscomfortLevel >= 1).astype(int)
XO = make_features(O).reindex(columns=NOPOS, fill_value=0.0)
assert not XO.isna().any().any()

if __name__ == "__main__":
    # December, LOGO, position-free
    design.run("rev_nopos", design.pid, NOPOS, PANEL)
    # October: fit once on December
    f = PRED / "P_rev_october.csv"
    if not f.exists():
        Xd = design.X[NOPOS].values.astype(float); sc = RobustScaler().fit(Xd); Xtr, Xte = sc.transform(Xd), sc.transform(XO.values)
        probs = {}
        for name, fn in PANEL.items():
            if name == "RF+GB": probs[name] = (probs["RF"] + probs["GB"]) / 2; continue
            m = fn(design.pid) if name == "MLP" else fn(); m.fit(Xtr, design.y); probs[name] = m.predict_proba(Xte)[:, 1]
        tD = design.X[["elapsed_in_session"]].values.astype(float); sct = RobustScaler().fit(tD)
        probs["Clock"] = design.lr().fit(sct.transform(tD), design.y).predict_proba(sct.transform(XO[["elapsed_in_session"]].values))[:, 1]
        pd.concat([pd.DataFrame(dict(model=k_, profile=O.profile, new_profile=O.new_profile, session=O.session, y=O.y,
                                     sev=O.DiscomfortLevel, t=O.TimeStamp, proba=v)) for k_, v in probs.items()]).to_csv(f, index=False)
    P = pd.read_csv(f)
    out = []
    for subset, keep in (("all", lambda g: g), ("new profiles", lambda g: g[g.new_profile])):
        Q = keep(P); fm = {}
        for m, g in Q.groupby("model"):
            g = g.reset_index(drop=True); s = trailing(g.proba.values, g.session.values, W); pred = (s >= TAU).astype(int)
            fm[m] = pd.Series({u: rates(*counts(g.y.values[i], pred[i]))["mcc"] for u, i in g.groupby("profile").groups.items()
                               if 0 < g.y.values[i].sum() < len(i)})
            if m == "Clock":
                gk = g
        F = pd.DataFrame(fm); ug = np.array(sorted(gk.profile.unique()))
        AT = ATime(gk.y.values, gk.t.values, gk.profile.values); ones = np.ones(len(AT.ug)); MB = boot_multiplicities(AT.ug, 1000, 0)
        REF = AT.tables(gk.t.values.astype(float)); ref0 = AT.value(REF, ones); refb = np.array([AT.value(REF, m_) for m_ in MB])
        ps = []
        for m in SUP:
            dl = F[m] - F.Clock; h = sps.t.ppf(0.975, len(dl) - 1) * dl.std(ddof=1) / np.sqrt(len(dl))
            g = Q[Q.model == m].reset_index(drop=True); assert (g.y.values == gk.y.values).all()
            C = AT.tables(trailing(g.proba.values, g.session.values, W)); v0 = AT.value(C, ones); vb = np.array([AT.value(C, m_) for m_ in MB]) - refb
            pw = sps.wilcoxon(dl).pvalue if (dl.abs() > 1e-12).any() else 1.0; ps.append(pw)
            out.append(dict(subset=subset, model=m, sessions=Q.session.nunique(), profiles=Q.profile.nunique(), two_class=len(dl),
                            mcc=F[m].mean(), clock=F.Clock.mean(), d=dl.mean(), lo=dl.mean() - h, hi=dl.mean() + h,
                            higher=int((dl > 1e-12).sum()), p_w=pw, tm=v0, tm_ref=ref0, dtm=v0 - ref0,
                            dtm_lo=np.percentile(vb, 2.5), dtm_hi=np.percentile(vb, 97.5)))
        T_ = pd.DataFrame(out); idx = T_.subset == subset; T_.loc[idx, "p_w_bh5"] = bh(np.array(ps)); out = T_.to_dict("records")
    T = pd.DataFrame(out); T.to_csv(TABLES / "T_rev_october.csv", index=False); print(T.round(3).to_string())
    # December position-free against the clock (LOGO)
    nd = load("rev_nopos"); ck = load("primary_clock"); PF = fold_mcc(pd.concat([nd.assign(hard=np.nan), ck.assign(hard=np.nan)], ignore_index=True))
    prim = fold_mcc(load("primary").assign(hard=np.nan))
    facts = dict(oct_sessions=O.session.nunique(), oct_profiles=O.profile.nunique(), oct_new_profile_sessions=O[O.new_profile].session.nunique(),
                 oct_windows=len(O), oct_positive=int(O.y.sum()), nopos_features=len(NOPOS))
    for m in SUP:
        facts[f"dec_nopos_{m}"] = PF[m].mean(); facts[f"dec_primary_{m}"] = prim[m].mean()
    facts["dec_clock"] = PF["Clock"].mean()
    dec = []
    for m in SUP:
        dl = (PF[m] - PF["Clock"]).dropna(); h = sps.t.ppf(0.975, len(dl) - 1) * dl.std(ddof=1) / np.sqrt(len(dl))
        dec.append(dict(subset="december position-free (LOGO)", model=m, sessions=35, profiles=22, two_class=len(dl), mcc=PF[m].loc[dl.index].mean(),
                        clock=PF["Clock"].loc[dl.index].mean(), d=dl.mean(), lo=dl.mean() - h, hi=dl.mean() + h, higher=int((dl > 1e-12).sum()),
                        p_w=sps.wilcoxon(dl).pvalue))
    DEC = pd.DataFrame(dec); DEC["p_w_bh5"] = bh(DEC.p_w.values)
    pd.concat([DEC, T], ignore_index=True).to_csv(TABLES / "T_rev_october.csv", index=False); print(DEC.round(3).to_string())
    pd.Series(facts).rename("value").rename_axis("name").to_csv(TABLES / "T_rev_october_facts.csv"); print(pd.Series(facts).round(3).to_string())
