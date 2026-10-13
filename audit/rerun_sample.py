"""Audit harness (not part of the analysis). Reruns a sample of the replicate based experiments with the unchanged
pipeline code and compares each rerun replicate with the row saved in outputs/tables.

Steps 16, 55, 58 and 59 each compute one replicate with a function one(...). This script imports the step, calls that
function for a few replicates (one process per replicate) and reports the largest absolute difference between the rerun
row and the saved row, over all numeric columns. Nothing in outputs/ is written.

  python audit/rerun_sample.py            run the sample (JOBS processes, default 8) and write audit/rerun_sample_result.csv
  python audit/rerun_sample.py compare    only compare the rows already rerun (audit/rerun_rows/*.json)"""
import importlib.util, json, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; ROWS = ROOT / "audit" / "rerun_rows"
# (step file, saved replicate file, key columns, arguments of one())
TASKS = [
    ("59_rev_perm_strat.py", "CTRL_PERM_STRAT.csv", ["learner", "rep"], ["trees", -1]),   # observed statistic, RF GB RF+GB
    ("59_rev_perm_strat.py", "CTRL_PERM_STRAT.csv", ["learner", "rep"], ["trees", 0]),
    ("59_rev_perm_strat.py", "CTRL_PERM_STRAT.csv", ["learner", "rep"], ["LR", -1]),
    ("59_rev_perm_strat.py", "CTRL_PERM_STRAT.csv", ["learner", "rep"], ["LR", 0]),
    ("59_rev_perm_strat.py", "CTRL_PERM_STRAT.csv", ["learner", "rep"], ["MLP", -1]),
    ("59_rev_perm_strat.py", "CTRL_PERM_STRAT.csv", ["learner", "rep"], ["MLP", 0]),
    ("58_rev_perm_null.py", "CTRL_PERM.csv", ["learner", "rep"], ["GB", 0]),
    ("58_rev_perm_null.py", "CTRL_PERM.csv", ["learner", "rep"], ["RF", 0]),
    ("55_rev_controls.py", "CTRL_REV.csv", ["learner", "kind", "delta", "rep"], ["LR", "trait", 0.0, 0]),
    ("55_rev_controls.py", "CTRL_REV.csv", ["learner", "kind", "delta", "rep"], ["LR", "state_ar", 0.5, 3]),
    ("55_rev_controls.py", "CTRL_REV.csv", ["learner", "kind", "delta", "rep"], ["GB", "trait", 2.0, 1]),
    ("55_rev_controls.py", "CTRL_REV.csv", ["learner", "kind", "delta", "rep"], ["GB", "state_ar", 0.0, 7]),
    ("55_rev_controls.py", "CTRL_REV.csv", ["learner", "kind", "delta", "rep"], ["RF", "trait", 0.0, 2]),
    ("16_controls.py", "CTRL_LR.csv", ["learner", "kind", "delta", "rep"], ["state", 0.1, 0]),
    ("16_controls.py", "CTRL_LR.csv", ["learner", "kind", "delta", "rep"], ["trait", 1.5, 5]),
    ("16_controls.py", "CTRL_LR.csv", ["learner", "kind", "delta", "rep"], ["trait", 0.0, 199]),
]


def name(i): return f"{i:02d}_{TASKS[i][0][:2]}_" + "_".join(str(a) for a in TASKS[i][3])


def run_one(i):
    step, _, _, args = TASKS[i]
    sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "pipeline")); os.chdir(ROOT)
    sys.argv = [step]                                           # the steps read sys.argv at import
    spec = importlib.util.spec_from_file_location("step", ROOT / "pipeline" / step); m = importlib.util.module_from_spec(spec)
    sys.modules["step"] = m; t0 = time.time(); spec.loader.exec_module(m)
    rows = m.one(*args); rows = rows if isinstance(rows, list) else [rows]
    out = [{k: (v if isinstance(v, str) else float(v)) for k, v in r.items()} for r in rows]
    ROWS.mkdir(parents=True, exist_ok=True)
    (ROWS / (name(i) + ".json")).write_text(json.dumps(dict(seconds=time.time() - t0, rows=out)))


def compare():
    import pandas as pd, numpy as np
    res = []
    for i, (step, saved, keys, args) in enumerate(TASKS):
        f = ROWS / (name(i) + ".json")
        if not f.exists(): res.append(dict(step=step, args=str(args), status="not rerun")); continue
        d = json.loads(f.read_text()); S = pd.read_csv(ROOT / "outputs" / "tables" / saved)
        for r in d["rows"]:
            q = S
            for k in keys:
                q = q[np.isclose(q[k], r[k])] if not isinstance(r[k], str) else q[q[k] == r[k]]
            if len(q) != 1: res.append(dict(step=step, args=str(args), learner=r.get("learner"), status=f"{len(q)} saved rows")); continue
            num = [c for c in S.columns if c not in keys and c in r]
            diff = max(abs(float(q.iloc[0][c]) - r[c]) for c in num)
            res.append(dict(step=step, args=str(args), learner=r.get("learner"), columns=len(num), max_abs_diff=diff,
                            seconds=round(d["seconds"]), status="identical to 1e-9" if diff < 1e-9 else "differs"))
    R = pd.DataFrame(res); R.to_csv(ROOT / "audit" / "rerun_sample_result.csv", index=False); print(R.to_string(index=False))


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--task": run_one(int(sys.argv[2])); sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] == "compare": compare(); sys.exit(0)
    jobs = int(os.environ.get("JOBS", "8")); todo = [i for i in range(len(TASKS)) if not (ROWS / (name(i) + ".json")).exists()]
    live = []
    while todo or live:
        live = [(i, p) for i, p in live if p.poll() is None]
        while todo and len(live) < jobs:
            i = todo.pop(0); live.append((i, subprocess.Popen([sys.executable, __file__, "--task", str(i)]))); print("started", name(i), flush=True)
        time.sleep(5)
    compare()
