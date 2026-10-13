"""Step 52 (revision). What the time matched AUC measures, from the shipped predictions (no model is fitted).

  T_rev_tm_coverage.csv   bins, kept bins, windows and pairs in kept bins, share of within group pairs, for bin widths
                          15, 30, 60 s and minimum counts 10, 20, 40 per bin
  T_rev_tm_parts.csv      for every detector of the primary panel, the time only RF and GB and elapsed time: the full
                          LPGO time matched AUC and its within group part (LOGO scores; one model scores both windows)
                          and between group part (LPGO scores), each minus elapsed time, with 95% group bootstrap
                          intervals (the 1,000 shared draws of step 24)
  T_rev_tm_learner.csv    learner matched contrast: RF minus RF on elapsed time only, GB minus GB on elapsed time only
                          (full, within, between)
  T_rev_tm_bins.csv       detector minus elapsed time (full LPGO) under the other bin widths and minimum counts
  T_rev_tm_units.csv      within group part and pooled measure under LORO (recordings) and the merged grouping (the
                          LPGO pair models exist only for the primary grouping)"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from csp.inference import *       # noqa: F401,F403
from csp.revision import ATimeParts
from csp.paths import LPGO


def order_frame(P):
    """Rows of a prediction file ordered by group, then dataset order (canonical order)."""
    return pd.concat([P[P.participant == g] for g in np.unique(P.participant)]).reset_index(drop=True)


def boot_parts(AP, C, M):
    e = np.array(AP.parts(C, np.ones(len(AP.ug)))); b = np.array([AP.parts(C, m_) for m_ in M]); return e, b


if __name__ == "__main__":
    ck_ = load("primary_clock"); ck_["hard"] = np.nan; clk = order_frame(ck_)
    prim = load("primary"); tonly = load("ablation_time")
    y_, t_, g_ = clk.y.values, clk.t.values.astype(float), clk.participant.values
    # LOGO smoothed scores in canonical order
    S = {m: aligned_scores(prim[prim.model == m], clk)[m] for m in SUP}
    for m in ["RF", "GB"]:
        S[m + " time only"] = aligned_scores(tonly[tonly.model == m], clk)[m]
    # LPGO scores, all files loaded once
    L = pd.concat([pd.read_csv(f) for f in sorted(LPGO.glob("pair_*.csv"))], ignore_index=True)
    key_c = pd.Series(np.arange(len(clk)), index=pd.MultiIndex.from_arrays([clk.participant.values,
                                                                             clk.groupby("participant").cumcount().values]))
    PS = {m: {} for m in SUP + ["RF time only", "GB time only"]}
    for (g, h, m), P in L.groupby(["pair_g", "pair_h", "model"], sort=False):
        if m not in PS: continue
        i = P.groupby("participant").cumcount().values
        idx = key_c.loc[list(zip(P.participant.values, i))].values
        assert np.allclose(t_[idx], P.t.values) and (y_[idx] == P.y.values).all()
        v = np.full(len(clk), np.nan); v[idx] = trailing(P.proba.values, P.session.values, W); PS[m][(g, h)] = v
    assert all(len(v) == 216 for v in PS.values())

    # coverage
    cov = []
    for bs in (15, 30, 60):
        for mn in (10, 20, 40):
            cov.append(dict(bin_s=bs, min_n=mn, **ATimeParts(y_, t_, g_, bs, mn).coverage()))
    pd.DataFrame(cov).to_csv(TABLES / "T_rev_tm_coverage.csv", index=False); print(pd.DataFrame(cov).to_string())

    AP = ATimeParts(y_, t_, g_); M = boot_multiplicities(AP.ug, 1000, 0)
    Cref = AP.tables(t_); eref, bref = boot_parts(AP, Cref, M)
    # the full LPGO value must reproduce Table III / IV (step 24 and 25 tables)
    LP = pd.read_csv(TABLES / "T_lpgo_atime.csv")
    print(LP.head(8).to_string())
    rows, CT = [], {}
    for m in SUP + ["RF time only", "GB time only"]:
        C = AP.tables(S[m], PS[m]); CT[m] = C; e, b = boot_parts(AP, C, M); dd = b - bref
        r = dict(model=m)
        for j, part in enumerate(["full", "within", "between"]):
            r[part] = e[j]; r[part + "_ref"] = eref[j]; r["d_" + part] = e[j] - eref[j]
            r["d_" + part + "_lo"] = np.nanpercentile(dd[:, j], 2.5); r["d_" + part + "_hi"] = np.nanpercentile(dd[:, j], 97.5)
        rows.append(r)
    T = pd.DataFrame(rows); T.to_csv(TABLES / "T_rev_tm_parts.csv", index=False); print(T.round(3).to_string())

    lm = []
    for m in ["RF", "GB"]:
        e, b = boot_parts(AP, CT[m], M); e0, b0 = boot_parts(AP, CT[m + " time only"], M); dd = b - b0
        r = dict(contrast=f"{m} minus {m} on elapsed time only")
        for j, part in enumerate(["full", "within", "between"]):
            r["d_" + part] = e[j] - e0[j]; r["d_" + part + "_lo"] = np.nanpercentile(dd[:, j], 2.5)
            r["d_" + part + "_hi"] = np.nanpercentile(dd[:, j], 97.5)
        lm.append(r)
    pd.DataFrame(lm).to_csv(TABLES / "T_rev_tm_learner.csv", index=False); print(pd.DataFrame(lm).round(3).to_string())

    bins = []
    for bs in (15, 30, 60):
        for mn in (10, 20, 40):
            A2 = ATimeParts(y_, t_, g_, bs, mn); one = np.ones(len(A2.ug)); r0 = A2.parts(A2.tables(t_), one)[0]
            for m in SUP:
                bins.append(dict(bin_s=bs, min_n=mn, model=m, full=A2.parts(A2.tables(S[m], PS[m]), one)[0],
                                 ref=r0, d_full=A2.parts(A2.tables(S[m], PS[m]), one)[0] - r0))
    B = pd.DataFrame(bins); B.to_csv(TABLES / "T_rev_tm_bins.csv", index=False)
    print(B.pivot_table(index=["bin_s", "min_n"], columns="model", values="d_full").round(3).to_string())

    # other units: LORO (recording = unit) and merged grouping; within part and pooled measure from LOGO-type scores
    un = []
    for tag, ctag, unitcol in [("loro", "loro_clock", "session"), ("merged", "merged_clock", "fold")]:
        P = load(tag); Pc = load(ctag)
        for m in SUP:
            Q = P[P.model == m].sort_values(["session"], kind="stable").reset_index(drop=True)
            Qc = Pc.sort_values(["session"], kind="stable").reset_index(drop=True)
            assert np.allclose(Q.t.values, Qc.t.values)
            s = trailing(Q.proba.values, Q.session.values, W); unit = Q[unitcol].values
            A3 = ATimeParts(Q.y.values, Q.t.values, unit); M3 = boot_multiplicities(A3.ug, 1000, 0)
            e, b = boot_parts(A3, A3.tables(s), M3); er, br = boot_parts(A3, A3.tables(Q.t.values.astype(float)), M3)
            dd = b - br
            un.append(dict(design=tag, model=m, d_pooled=e[0] - er[0], d_pooled_lo=np.nanpercentile(dd[:, 0], 2.5),
                           d_pooled_hi=np.nanpercentile(dd[:, 0], 97.5), d_within=e[1] - er[1],
                           d_within_lo=np.nanpercentile(dd[:, 1], 2.5), d_within_hi=np.nanpercentile(dd[:, 1], 97.5),
                           within_share=A3.coverage()["within_share"]))
    U = pd.DataFrame(un); U.to_csv(TABLES / "T_rev_tm_units.csv", index=False); print(U.round(3).to_string())
