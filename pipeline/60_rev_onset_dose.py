"""Step 60 (revision). Three checks that the time matched AUC cannot give.

1. Onset timing within each recording (no refit; shipped primary LOGO predictions and the clock). For each of the 26
   recordings that become positive, onset = elapsed time of the first positive window; first alarm = elapsed time of
   the first window predicted positive by the primary rule (trailing mean over w = 61 windows, tau = 0.5), from the
   start of the recording. Onset error = first alarm minus onset (negative: alarm before onset); a recording without
   any alarm counts as a miss, with error = recording end minus onset. Per detector: median absolute error, share of
   alarms before onset, share of misses. Detector minus clock: absolute error averaged within each group, paired over
   the groups with an onset recording (Wilcoxon; 95% group bootstrap interval, 10,000 draws, seed 0).
2. Dose reference. LR and GB on elapsed time and the two cumulative exposure features (expanding mean rotation and
   acceleration): a reference that knows how much provocative motion the recording has delivered so far but nothing
   else. LOGO and the 216 LPGO pairs, as in steps 15 and 53. Fold MCC against the clock; LPGO time matched AUC minus
   elapsed time (full, within, between); detector minus dose reference, with the detectors' F76 refits of step 53.
3. Label threshold. y2 = severity >= 2. Episode and two class group counts, and LOGO fold MCC of RF, GB, their mean
   (RF+GB), LR (76 features) and the clock refitted on y2, paired over the two class groups (paired t interval).

Usage: python pipeline/60_rev_onset_dose.py        (fits are skipped when their outputs exist)
Outputs: outputs/tables/T_rev_onset.csv, T_rev_onset_paired.csv, T_rev_dose.csv, T_rev_dose_contrast.csv,
         T_rev_label2.csv; predictions in outputs/predictions/rev/ (P_dose_logo.csv, lpgo_dose/, P_label2_logo.csv)."""
import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_k] = "1"
import sys, pathlib, itertools, time; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from joblib import Parallel, delayed
from csp.design import X, PRIMARY, y, sev, t_el, pid, sess, gb, lr
from sklearn.ensemble import RandomForestClassifier
from csp.inference import *       # noqa: F401,F403
from csp.revision import ATimeParts, load_pair_dir
from csp.paths import PRED
from sklearn.preprocessing import RobustScaler

REV = PRED / "rev"; LP = REV / "lpgo_dose"; LP.mkdir(parents=True, exist_ok=True)
DOSE = ["elapsed_in_session", "cum_rotation", "cum_accel"]
assert all(c in PRIMARY for c in DOSE)
FITS = [("LR dose", lr), ("GB dose", gb)]
HASPOS = set(np.unique(pid[y == 1]))
PAIRS = [(g, h) for g, h in itertools.combinations(np.unique(pid), 2) if g in HASPOS or h in HASPOS]
assert len(PAIRS) == 216
XD = X[DOSE].values.astype(float)


def rf1(): return RandomForestClassifier(n_estimators=300, min_samples_leaf=2, class_weight="balanced_subsample",
                                         n_jobs=1, random_state=42)


def fit(tr, te, Xa, yy, fits):
    sc = RobustScaler().fit(Xa[tr])
    return {n: f().fit(sc.transform(Xa[tr]), yy[tr]).predict_proba(sc.transform(Xa[te]))[:, 1] for n, f in fits}


def frame(probs, te, yy, **extra):
    return pd.concat([pd.DataFrame(dict(**extra, model=n, participant=pid[te], session=sess[te], y=yy[te], sev=sev[te],
                                        t=t_el[te], proba=p)) for n, p in probs.items()], ignore_index=True)


def logo(Xa, yy, fits, k, g):
    tr, te = np.where(pid != g)[0], np.where(pid == g)[0]
    assert not set(sess[tr]) & set(sess[te])
    return frame(fit(tr, te, Xa, yy, fits), te, yy, fold=k)


def pair(g, h):
    f = LP / f"pair_{g}_{h}.csv"
    if f.exists(): return
    te = np.where((pid == g) | (pid == h))[0]; tr = np.where((pid != g) & (pid != h))[0]
    assert not {g, h} & set(pid[tr]) and not set(sess[tr]) & set(sess[te])
    frame(fit(tr, te, XD, y, FITS), te, y, pair_g=g, pair_h=h).to_csv(f, index=False)


def run_fits(nj):
    f = REV / "P_dose_logo.csv"
    if not f.exists():
        pd.concat(Parallel(n_jobs=nj)(delayed(logo)(XD, y, FITS, k, g) for k, g in enumerate(np.unique(pid))),
                  ignore_index=True).to_csv(f, index=False)
    Parallel(n_jobs=nj)(delayed(pair)(g, h) for g, h in PAIRS)
    assert len(list(LP.glob("pair_*.csv"))) == 216
    f = REV / "P_label2_logo.csv"
    if not f.exists():
        y2 = (sev >= 2).astype(int); XF = X[PRIMARY].values.astype(float); XT = X[["elapsed_in_session"]].values.astype(float)
        a = Parallel(n_jobs=nj)(delayed(logo)(XF, y2, [("RF", rf1), ("GB", gb), ("LR", lr)], k, g)
                                for k, g in enumerate(np.unique(pid)))
        b = Parallel(n_jobs=nj)(delayed(logo)(XT, y2, [("Clock", lr)], k, g) for k, g in enumerate(np.unique(pid)))
        pd.concat(a + b, ignore_index=True).to_csv(f, index=False)


def first_alarm(g):
    """Onset error per recording with an onset, for one model's predictions (primary rule)."""
    g = g.reset_index(drop=True); pred = decisions(g); rows = []
    for s, idx in g.groupby("session").groups.items():
        idx = np.asarray(idx); yy, tt = g.y.values[idx], g.t.values[idx]
        if yy.max() == 0: continue
        on = tt[np.argmax(yy == 1)]; al = np.where(pred[idx] == 1)[0]
        miss = len(al) == 0; first = tt[-1] if miss else tt[al[0]]
        rows.append(dict(session=s, participant=g.participant.values[idx[0]], onset=on, alarm=first, err=first - on,
                         miss=miss))
    return pd.DataFrame(rows)


def onset_tables():
    P = pd.concat([load("primary"), load("primary_clock")], ignore_index=True)
    E = {m: first_alarm(g) for m, g in P.groupby("model", sort=False)}
    rows = [dict(model=m, recordings=len(e), median_abs_err=e.err.abs().median(), mean_abs_err=e.err.abs().mean(),
                 median_err=e.err.median(), before_onset=(e.err < 0).mean(), missed=e.miss.mean())
            for m, e in E.items()]
    T = pd.DataFrame(rows); T.to_csv(TABLES / "T_rev_onset.csv", index=False); print(T.round(3).to_string())
    ck = E["Clock"].groupby("participant").err.apply(lambda v: v.abs().mean())
    rng_ = np.random.default_rng(0); ug = ck.index.values
    draws = [rng_.choice(len(ug), len(ug)) for _ in range(10000)]
    pr = []
    for m in SUP:
        dm = E[m].groupby("participant").err.apply(lambda v: v.abs().mean()) - ck; dm = dm.loc[ug].values
        bs = np.array([dm[i].mean() for i in draws])
        J = len(dm); mdd = (sps.t.ppf(0.975, J - 1) + sps.t.ppf(0.80, J - 1)) * dm.std(ddof=1) / np.sqrt(J)
        pr.append(dict(model=m, groups=J, d_abs_err=dm.mean(), lo=np.percentile(bs, 2.5), hi=np.percentile(bs, 97.5),
                       p_w=sps.wilcoxon(dm).pvalue, groups_better=int((dm < 0).sum()), mdd=mdd))
    T2 = pd.DataFrame(pr); T2["p_w_bh"] = bh(T2.p_w.values)
    T2.to_csv(TABLES / "T_rev_onset_paired.csv", index=False); print(T2.round(3).to_string())


def dose_tables():
    ck_ = load("primary_clock"); ck_["hard"] = np.nan
    clk = pd.concat([ck_[ck_.participant == g] for g in np.unique(ck_.participant)]).reset_index(drop=True)
    y_, t_, g_ = clk.y.values, clk.t.values.astype(float), clk.participant.values
    PD = pd.read_csv(REV / "P_dose_logo.csv"); PD["hard"] = np.nan
    PF = pd.read_csv(REV / "P_scen_logo.csv"); PF["hard"] = np.nan
    det = ["RF", "GB", "RF+GB", "LR"]; refs = [n for n, _ in FITS]
    S = {m: aligned_scores(PD[PD.model == m], clk)[m] for m in refs}
    S.update({m: aligned_scores(PF[PF.model == m], clk)[m] for m in det})
    PS = load_pair_dir(LP, refs, clk); PS.update(load_pair_dir(REV / "lpgo_scen", det, clk))
    assert all(len(PS[m]) == 216 for m in refs + det)
    ckF = fold_mcc(ck_)["Clock"]; F = {**fold_mcc(PD), **fold_mcc(PF)}
    AP = ATimeParts(y_, t_, g_); M = boot_multiplicities(AP.ug, 1000, 0); one = np.ones(len(AP.ug))
    ref = np.array(AP.parts(AP.tables(t_), one)); refb = np.array([AP.parts(AP.tables(t_), m_) for m_ in M])
    E, EB, rows = {}, {}, []
    for m in refs + det:
        C = AP.tables(S[m], PS[m]); E[m] = np.array(AP.parts(C, one)); EB[m] = np.array([AP.parts(C, m_) for m_ in M])
        if m not in refs: continue
        x = F[m].loc[ckF.index]; dl = x - ckF; dd = EB[m] - refb
        r = dict(model=m, mcc=x.mean(), dmcc=dl.mean(), p_t=sps.ttest_rel(x, ckF).pvalue, p_w=sps.wilcoxon(dl).pvalue)
        for j, part in enumerate(["full", "within", "between"]):
            r["tm_" + part] = E[m][j]; r["d_" + part] = E[m][j] - ref[j]
            r["d_" + part + "_lo"] = np.nanpercentile(dd[:, j], 2.5); r["d_" + part + "_hi"] = np.nanpercentile(dd[:, j], 97.5)
        rows.append(r)
    T = pd.DataFrame(rows); T.to_csv(TABLES / "T_rev_dose.csv", index=False); print(T.round(3).to_string())
    con = []
    for a in det:
        for b in refs:
            dd = EB[a] - EB[b]; xa = F[a].loc[ckF.index]; xb = F[b].loc[ckF.index]
            con.append(dict(contrast=f"{a} minus {b}", dmcc=(xa - xb).mean(), p_w=sps.wilcoxon(xa - xb).pvalue,
                            d_full=E[a][0] - E[b][0], lo=np.nanpercentile(dd[:, 0], 2.5), hi=np.nanpercentile(dd[:, 0], 97.5)))
    C_ = pd.DataFrame(con); C_.to_csv(TABLES / "T_rev_dose_contrast.csv", index=False); print(C_.round(3).to_string())


def label2_table():
    P = pd.read_csv(REV / "P_label2_logo.csv"); P["hard"] = np.nan
    y2 = (sev >= 2).astype(int); ep = 0
    for s in np.unique(sess):
        v = y2[sess == s]; ep += int(((np.diff(np.r_[0, v]) == 1)).sum())
    two = [g for g in np.unique(pid) if 0 < y2[pid == g].sum() < (pid == g).sum()]
    key = ["fold", "participant", "session", "y", "sev", "t"]          # RF+GB: mean of the RF and GB probabilities of a fold
    a, b = (P[P.model == m].reset_index(drop=True) for m in ("RF", "GB"))
    assert (a[key].values == b[key].values).all()
    P = pd.concat([P, a.assign(model="RF+GB", proba=(a.proba + b.proba) / 2)], ignore_index=True)
    F = fold_mcc(P); ck = F["Clock"].loc[two]; rows = []; J = len(two)
    for m in ["RF", "GB", "RF+GB", "LR"]:                               # the MLP was not refitted on this label
        dl = F[m].loc[two] - ck; hw = sps.t.ppf(0.975, J - 1) * dl.std(ddof=1) / np.sqrt(J)
        rows.append(dict(model=m, episodes=ep, recordings=int(sum(y2[sess == s].max() for s in np.unique(sess))),
                         two_class_groups=J, mcc=F[m].loc[two].mean(), clock=ck.mean(), dmcc=dl.mean(),
                         lo=dl.mean() - hw, hi=dl.mean() + hw, p_w=sps.wilcoxon(dl).pvalue))
    T = pd.DataFrame(rows); T.to_csv(TABLES / "T_rev_label2.csv", index=False); print(T.round(3).to_string())


if __name__ == "__main__":
    T0 = time.time(); run_fits(int(os.environ.get("CSP_JOBS", "2"))); print("fits", f"{time.time() - T0:.0f}s", flush=True)
    onset_tables(); dose_tables(); label2_table()
