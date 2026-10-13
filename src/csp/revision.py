"""Library for the revision analyses (steps 50 to 58). Nothing here changes a shipped result.

ATimeParts   the time matched AUC of csp.inference.ATime split into its within group part (both windows of a pair from
             the same reconstructed group, so one LOGO model scores both) and its between group part (the two windows
             from different groups, scored by the LPGO model trained without both). The full measure is the pair
             weighted mean of the two parts. Bin width and the minimum number of positive and negative windows per
             bin are parameters (30 s and 20 in the paper). Group bootstrap in closed form: under multiplicities m a
             positive window of g meets a negative window of h m_g m_h times (also for g = h, where copies of the
             same group meet each other), as in csp.inference.ATime.
pair_scores  smoothed LPGO scores per pair of groups from the shipped lpgo/ files."""
import numpy as np, pandas as pd
from csp.paths import LPGO
from csp.metrics import trailing, W


class ATimeParts:
    def __init__(self, y, t, groups, bin_s=30, min_n=20):
        self.y = np.asarray(y).astype(int); self.b = (np.asarray(t, float) // bin_s).astype(int); self.min_n = min_n
        self.ug = np.unique(groups); self.gi = np.searchsorted(self.ug, groups); G = len(self.ug)
        self.bins = np.unique(self.b)
        self.npos = np.zeros((len(self.bins), G)); self.nneg = np.zeros((len(self.bins), G))
        for k, bb in enumerate(self.bins):
            m = self.b == bb
            self.npos[k] = np.bincount(self.gi[m & (self.y == 1)], minlength=G)
            self.nneg[k] = np.bincount(self.gi[m & (self.y == 0)], minlength=G)

    def _pairsum(self, s_pos, s_neg):
        v = np.sort(s_neg); lo = np.searchsorted(v, s_pos, "left"); hi = np.searchsorted(v, s_pos, "right")
        return lo.sum() + 0.5 * (hi - lo).sum()

    def tables(self, s_logo, pair_s=None):
        """C[k, g, h]: sum of pair scores between the positives of g and the negatives of h in bin k. Within group
        pairs (g = h) use s_logo; between group pairs use pair_s[(g, h)] when given, otherwise s_logo (pooled)."""
        G = len(self.ug); C = np.zeros((len(self.bins), G, G)); s_logo = np.asarray(s_logo, float)
        for k, bb in enumerate(self.bins):
            m = self.b == bb
            for g in np.unique(self.gi[m & (self.y == 1)]):
                pm = m & (self.y == 1) & (self.gi == g)
                for h in np.unique(self.gi[m & (self.y == 0)]):
                    nm = m & (self.y == 0) & (self.gi == h)
                    s = s_logo if (g == h or pair_s is None) else pair_s[(self.ug[min(g, h)], self.ug[max(g, h)])]
                    C[k, g, h] = self._pairsum(s[pm], s[nm])
        return C

    def parts(self, C, mult):
        """(full, within, between) for multiplicities mult; bins kept by the paper's rule on the resample."""
        mult = np.asarray(mult, float)
        P = self.npos @ mult; N = self.nneg @ mult; keep = (P >= self.min_n) & (N >= self.min_n)
        diagC = np.einsum("kgg->kg", C); diagN = self.npos * self.nneg
        num_all = np.einsum("g,kgh,h->k", mult, C, mult); den_all = P * N
        num_w = diagC @ (mult ** 2); den_w = diagN @ (mult ** 2)
        num_b = num_all - num_w; den_b = den_all - den_w
        f = lambda n, dd: n[keep].sum() / dd[keep].sum() if dd[keep].sum() > 0 else np.nan
        return f(num_all, den_all), f(num_w, den_w), f(num_b, den_b)

    def coverage(self):
        P = self.npos.sum(1); N = self.nneg.sum(1); keep = (P >= self.min_n) & (N >= self.min_n)
        within = (self.npos * self.nneg).sum(1)
        return dict(bins=len(self.bins), bins_kept=int(keep.sum()), windows_kept=int((P + N)[keep].sum()),
                    windows=int((P + N).sum()), pairs_kept=float((P * N)[keep].sum()),
                    within_share=float(within[keep].sum() / (P * N)[keep].sum()))


def load_pair_dir(folder, models, clk):
    """Smoothed pair model scores {model: {(g, h): array aligned to clk}} from every pair_*.csv in folder.
    clk: canonical order frame (groups ascending, dataset order within a group)."""
    L = pd.concat([pd.read_csv(f) for f in sorted(folder.glob("pair_*.csv"))], ignore_index=True)
    key = pd.Series(np.arange(len(clk)), index=pd.MultiIndex.from_arrays(
        [clk.participant.values, clk.groupby("participant").cumcount().values]))
    out = {m: {} for m in models}
    for (g, h, m), P in L.groupby(["pair_g", "pair_h", "model"], sort=False):
        if m not in out: continue
        idx = key.loc[list(zip(P.participant.values, P.groupby("participant").cumcount().values))].values
        assert np.allclose(clk.t.values[idx], P.t.values) and (clk.y.values[idx] == P.y.values).all()
        v = np.full(len(clk), np.nan); v[idx] = trailing(P.proba.values, P.session.values, W); out[m][(g, h)] = v
    return out


def pair_scores(model, order_df, files=None):
    """Smoothed LPGO scores of `model` aligned to order_df rows (participant, t), NaN outside the pair."""
    key = order_df.participant.astype(int).astype(str) + "_" + order_df.groupby("participant").cumcount().astype(str)
    pos = pd.Series(np.arange(len(order_df)), index=key.values)
    out = {}
    for f in sorted(LPGO.glob("pair_*.csv")) if files is None else files:
        P = pd.read_csv(f); P = P[P.model == model]
        g, h = int(P.pair_g.iloc[0]), int(P.pair_h.iloc[0])
        P = P.copy(); P["i"] = P.groupby("participant").cumcount()
        idx = pos[(P.participant.astype(str) + "_" + P.i.astype(str)).values].values
        assert np.allclose(order_df.t.values[idx], P.t.values) and (order_df.y.values[idx] == P.y.values).all()
        v = np.full(len(order_df), np.nan); v[idx] = trailing(P.proba.values, P.session.values, W)
        out[(g, h)] = v
    return out
