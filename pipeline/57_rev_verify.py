"""Step 57 (revision). Checks of the revised manuscript and Supporting Information (R1 .docx files) against the code.

  1. every number of reference/paper_numbers.csv (quoted in the first submission) still appears in the R1 text, or is
     listed in reference/paper_numbers_removed.csv with the reason it was removed
  2. every number of reference/paper_numbers_revision.csv (quoted in text added in revision) is recomputed from
     outputs/tables, formatted as printed, and found in the R1 text at its location
  3. consistency: figure captions numbered 1 to 4 once each and every figure reference in range; references numbered
     1..N in order, each cited, cited in order of first citation; no leftover placeholder; no wording that the revision
     removed ("prespecified", "Severity Aware", "scikit learn", the old repository URL, "per five minute recording")

  4. Supporting Information tables cited in the main text in the order of their printed numbers, printed in that order
  5. every claim of the response letter tagged <!-- check: "..." --> is found verbatim in the R1 text

Usage: python pipeline/57_rev_verify.py [--fill] [work folder with Cybersickness_IEEE_R1.docx and
       Cybersickness_supporting_information_R1.docx, default ../revision_R1]"""
import sys, pathlib, re, csv, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
FILL = "--fill" in sys.argv; sys.argv = [a for a in sys.argv if a != "--fill"]
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
import docx
from docx.oxml.ns import qn
import numpy as np, pandas as pd
from csp.paths import ROOT, TABLES, REFERENCE

WORK = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / "revision_R1"
fails = []


def report(ok, what):
    print(("PASS  " if ok else "FAIL  ") + what)
    if not ok: fails.append(what)


def paras(path):
    D = docx.Document(str(path)); out = []
    for el in D.element.body.iter(qn("w:p")):
        out.append("".join(n.text or "" for n in el.iter() if n.tag in (qn("w:t"), qn("m:t"))))
    return out


MS = paras(WORK / "Cybersickness_IEEE_R1.docx"); SI = paras(WORK / "Cybersickness_supporting_information_R1.docx")
TEXT = "\n".join(MS + SI)
norm = lambda s: re.sub(r"(?<=[A-Za-z])-(?=[A-Za-z])", " ", s.replace("−", "-").replace("–", "-"))   # compound modifier hyphens are style
NT = norm(TEXT)

# 1. original quoted numbers
removed = {r["id"]: r["reason"] for r in csv.DictReader(open(REFERENCE / "paper_numbers_removed.csv", encoding="utf-8"))} \
    if (REFERENCE / "paper_numbers_removed.csv").exists() else {}
miss = []
for r in csv.DictReader(open(REFERENCE / "paper_numbers.csv", encoding="utf-8")):
    if norm(r["printed"]) not in NT and r["id"] not in removed: miss.append(f"{r['id']} {r['printed']} ({r['location']})")
report(not miss, f"{len(miss)} first submission numbers missing from the R1 text without a stated reason"
       + ("" if not miss else ": " + "; ".join(miss[:12])))

# 2. revision numbers
DET = ["RF", "GB", "RF+GB", "LR", "MLP"]


def T(n, idx="model"):
    t = pd.read_csv(TABLES / f"{n}.csv"); return t.set_index(idx) if idx else t


def f2(x): return f"{x:.2f}"
def f3(x): return f"{x:.3f}"
def sg(x): return ("+" if x >= 0 else "-") + f"{abs(x):.3f}"
def pct1(x): return f"{100 * x:.1f}%"


NS = dict(np=np, pd=pd, DET=DET, f2=f2, f3=f3, sg=sg, pct1=pct1, PW=T("T_rev_power"), PA=T("T_rev_tm_parts"),
          LM=T("T_rev_tm_learner", "contrast"), COV=T("T_rev_tm_coverage", None), SC=T("T_rev_scenario"),
          SCC=T("T_rev_scenario_contrast", "contrast"), SV=T("T_rev_severity", None), UN=T("T_rev_tm_units", None),
          GAP=T("T_rev_window_gap", None), BI=T("T_rev_tm_bins", None),
          CTL=T("T_rev_controls", None) if (TABLES / "T_rev_controls.csv").exists() else None)
if NS["CTL"] is not None:
    NS["ctl"] = lambda l, k, d: NS["CTL"][(NS["CTL"].learner == l) & (NS["CTL"].kind == k) & ((NS["CTL"].delta - d).abs() < 1e-9)].iloc[0]
NS["pc0"] = lambda x: f"{100 * x:.0f}%"
NS["PN"] = T("T_rev_perm_null", "learner")
NS["oc"] = lambda sub: NS["OCT"][NS["OCT"].subset == sub].set_index("model")
NS["lv"] = lambda k, st: NS["LV"][(NS["LV"].kind == k) & (NS["LV"].statistic == st) & (NS["LV"].alpha == 0.05)].iloc[0]
NS["ci3"] = lambda lo, hi: f"[{lo:.3f}, {hi:.3f}]"
NS["cf"] = lambda l, d_: NS["CF"][(NS["CF"].learner == l) & (NS["CF"].kind == "trait") & (NS["CF"].delta == d_)].iloc[0]
NS.update(PS=T("T_rev_perm_strat", "learner"), ON=T("T_rev_onset"), OP=T("T_rev_onset_paired"), DS=T("T_rev_dose"),
          DC=T("T_rev_dose_contrast", "contrast"), L2=T("T_rev_label2"), TC=T("T_controls", None), LPA=T("T_lpgo_atime"),
          INF=pd.read_csv(TABLES / "T_rev_influence.csv", dtype={"group": str}).set_index("group"),
          CCI=T("T_rev_control_ci", "delta"), PR=T("T_primary"), O99=T("T_original99"),
          JSE=T("T_rev_influence_se"), TG=T("T_rev_tau_grid", None), RC=T("T_rev_recording"), TV=T("T_rev_tau_val", None),
          SVT=T("T_severity"), TR=["RF", "GB", "RF+GB"], LOR=T("T_loro"),
          RAW=T("T_rev_raw_unused_facts", "name").value, SPL=T("T_rev_spline_clock"), CF=T("T_rev_controls_full", None), PSC=T("T_rev_proper_scores", None), OCT=T("T_rev_october", None), OF=T("T_rev_october_facts", "name").value, HZ=T("T_rev_hazard"), LV=T("T_rev_perm_level", None),
          FX=T("T_audit_perm_mcc_fixed200", "learner"))
ok_n, bad = 0, []
ROWS = list(csv.DictReader(open(REFERENCE / "paper_numbers_revision.csv", encoding="utf-8")))
if FILL:                                    # write the printed form of every expression (run once after a rebuild)
    for r in ROWS: r["printed"] = str(eval(r["expr"], NS))
    with open(REFERENCE / "paper_numbers_revision.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "location", "printed", "expr"]); w.writeheader(); w.writerows(ROWS)
for r in ROWS:
    if r["id"] in removed: continue                     # moved out of the text, reason in paper_numbers_removed.csv
    try:
        got = str(eval(r["expr"], NS))
    except Exception as e:
        bad.append(f"{r['id']}: {e}"); continue
    if norm(got) != norm(r["printed"]): bad.append(f"{r['id']}: printed {r['printed']} recomputed {got}"); continue
    if norm(r["printed"]) not in NT: bad.append(f"{r['id']}: {r['printed']} not found in the R1 text"); continue
    ok_n += 1
report(not bad, f"{ok_n} revision numbers recomputed and found in the R1 text" + ("" if not bad else ": " + "; ".join(bad[:10])))

sys.path.insert(0, str(ROOT / "src"))
from csp.si_revision import SI_ORDER as SI_ORDER_N
# 3. consistency of the revised manuscript
caps = [int(m.group(1)) for p in MS for m in [re.match(r"Fig\. (\d)\.\s", p)] if m]
report(caps == [1, 2, 3, 4, 5], f"figure captions in order {caps}")
refs_fig = [int(x) for p in MS if not re.match(r"Fig\. \d\.\s", p) for x in re.findall(r"Fig\. (\d)", p)]
report(all(1 <= x <= 5 for x in refs_fig) and set(refs_fig) == {1, 2, 3, 4, 5}, f"figure references in range ({len(refs_fig)})")
k = MS.index("References"); body = "\n".join(MS[:k]); rl = [p for p in MS[k + 1:] if re.match(r"\[\d+\]", p)]
nums = [int(re.match(r"\[(\d+)\]", p).group(1)) for p in rl]
report(nums == list(range(1, len(nums) + 1)), f"reference list numbered 1..{len(nums)}")
order = []
for m in re.finditer(r"\[(\d+)\](?:\s*[–-]\s*\[(\d+)\])?", body):
    a, b = int(m.group(1)), m.group(2)
    for x in (range(a, int(b) + 1) if b else [a]):
        if x not in order: order.append(x)
report(order == list(range(1, len(nums) + 1)), "every reference cited, in order of first citation")
for bad_s in ["prespecified", "Severity Aware", "scikit learn", "github.com/rajaiimad/cybersickness-safety.",
              "per five minute recording", "[R:", "⟦", "reconstructed group terminology", ".No detector", "RF.(a)",
              "within chance", "confirmed that", "close to zero", "fewer than half", "first submission",
              "earlier version", "In revision", "added in revision", "the elapsed time reference", "between people",
              "fixed before the comparisons,", "calibrated rates", "calibrated test", "Atime,w", "−0.000", "+0.000",
              "timed onset within a recording better", "66 telemetry trajectories", "S@", "Appendix",
              "permutation test", "permutation null", "permutation p", "matched exposure", "main text Table S",
              "(main text, Note", "statistic of the main text", "reported in the main text"]:
    report(bad_s not in TEXT, f"no '{bad_s}'")
report(not re.search(r"(?<![\d.])8\.6%", TEXT), "no '8.6%' (the withdrawn conditional figure)")
# pointers of the Supporting Information into the main text: sections that exist, main tables I to V, figures 1 to 4
SIT = "\n".join(SI); LAST = {"III": "F", "IV": "C", "V": "E", "VI": "C"}
bad_p = [m.group(0) for m in re.finditer(r"Section (VI|V|IV|III|II|I)-([A-G])", SIT) if m.group(2) > LAST.get(m.group(1), "@")]
bad_p += [m.group(0) for m in re.finditer(r"Table (VI{1,3}|IX|X)\b", SIT)] + [m.group(0) for m in re.finditer(r"Fig\. ([5-9])", SIT)]
report(not bad_p, f"Supporting Information pointers to the main text exist {bad_p[:5]}")
si_cited = {int(x) for x in re.findall(r"Table S(\d+)", SIT)}
report(si_cited <= set(range(1, len(SI_ORDER_N) + 1)), "Supporting Information cites only tables that it contains")

# 4. Supporting Information table order
sys.path.insert(0, str(ROOT / "src"))
from csp.si_revision import SI_ORDER
first = []
for p_ in MS[:k]:
    if p_.startswith("Additional supporting information"): continue
    for m in re.finditer(r"Tables? (S\d+)(?: and (S\d+))?", p_):
        for x in m.groups():
            if x and x not in first: first.append(x)
report(first == [f"S{i + 1}" for i in range(len(SI_ORDER))], f"SI tables first cited in printed order ({len(first)})")
si_labels = [int(m.group(1)) for p_ in SI for m in [re.fullmatch(r"TABLE S(\d+)", p_.strip())] if m]
report(si_labels == list(range(1, len(SI_ORDER) + 1)), "SI tables printed in numeric order")

# 6. the randomization test: Table III and Table S9 print the same p and adjusted p, and both equal the saved output
def table_with(path, header):
    for t in docx.Document(str(path)).tables:
        h = [c.text.strip() for c in t.rows[0].cells]
        if header in h: return h, [[c.text.strip() for c in r.cells] for r in t.rows[1:]]
    return None, []


PS_ = NS["PS"]; o_ = PS_.p_perm.sort_values()
bh = (o_ * len(o_) / np.arange(1, len(o_) + 1))[::-1].cummin()[::-1].clip(upper=1)   # Benjamini–Hochberg
h3, r3 = table_with(WORK / "Cybersickness_IEEE_R1.docx", "Randomization p (BH)")
h9, r9 = table_with(WORK / "Cybersickness_supporting_information_R1.docx", "Adjusted p (BH)")
bad_r = []
if h3 and h9:
    t3 = {r[0]: re.match(r"([\d.]+) \(([\d.]+)\)", r[h3.index("Randomization p (BH)")]).groups() for r in r3}
    t9 = {r[0]: (r[h9.index("p [Monte Carlo 95% CI]")].split(" ")[0], r[h9.index("Adjusted p (BH)")]) for r in r9}
    for d in DET:
        want = (f3(PS_.loc[d, "p_perm"]), f3(bh[d]))
        if not (t3.get(d) == t9.get(d) == want): bad_r.append(f"{d}: Table III {t3.get(d)}, Table S9 {t9.get(d)}, output {want}")
    if not np.allclose(bh[DET], PS_.loc[DET, "p_perm_bh"]): bad_r.append("BH recomputed from p_perm differs from p_perm_bh")
report(bool(h3 and h9) and not bad_r, "randomization p and BH p identical in Table III, Table S9 and T_rev_perm_strat"
       + ("" if h3 and h9 else ": table not found") + ("" if not bad_r else ": " + "; ".join(bad_r)))
# wording: analyses with a rule chosen on validation groups are sensitivity analyses, not a validated rule
for bad_s in ["validated rule", "validated threshold", "Validated threshold", "validated-threshold", "validated smoothing"]:
    report(bad_s not in TEXT, f"no '{bad_s}'")
# participant independence is never claimed, only denied
pi = [TEXT[max(0, m.start() - 60):m.end()] for m in re.finditer(r"participant[- ]independen", TEXT, re.I)
      if not re.search(r"(?:\bnot|rather than)(?:\s+[A-Za-z]+){0,3}\s+$", TEXT[max(0, m.start() - 60):m.start()])]   # negation governs the phrase
report(not pi, "participant independence appears only as a negated claim" + ("" if not pi else ": " + "; ".join(pi)))

# 5. response letter claims
LET = WORK / "Response_to_reviewers_R1.md"
claims = re.findall(r'<!-- check: "([^"]+)" -->', LET.read_text(encoding="utf-8")) if LET.exists() else []
miss = [c for c in claims if norm(c) not in NT]
if LET.exists():
    report(claims and not miss, f"{len(claims)} response letter claims found verbatim in the R1 text" + ("" if not miss else ": " + "; ".join(miss[:5])))
else:
    print("SKIP  no Response_to_reviewers_R1.md in the work folder: the response letter check is not run")
print("\nALL REVISION CHECKS PASSED" if not fails else f"\n{len(fails)} REVISION CHECKS FAILED")
sys.exit(1 if fails else 0)
