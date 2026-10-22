"""Step 64 (revision). The sessions of the raw archive that are not in the merged file dataset.csv.

The raw archive RAW_DATABASE.zip holds 74 session folders; the merged file contains 35 recordings, each matched to one
raw session by step 02 (same length and same first 20 camera rotation values). This step describes the other sessions:
recording dates, number of windows, sessions with at least 250 windows, sessions with at least one window at
discomfort level 1 or more, and sessions that record the three player position channels of the merged file (the
detectors use 21 features computed from them). Nothing here enters any other analysis; the merged file is analyzed as released.

Output: outputs/tables/T_rev_raw_unused.csv (one row per raw session) and T_rev_raw_unused_facts.csv"""
import sys, os, re, pathlib, tempfile, zipfile, xml.etree.ElementTree as ET
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
import numpy as np, pandas as pd
from csp.paths import RAW, TABLES

tmp = pathlib.Path(tempfile.mkdtemp())
for z in ("DATABASE_SELECTED_DATA.zip", "RAW_DATABASE.zip"): zipfile.ZipFile(RAW / z).extractall(tmp)


def rows(p): return pd.DataFrame([{c.tag: c.text for c in e} for e in ET.parse(p).getroot().findall("Data")])
def num(s): return pd.to_numeric(s.astype(str).str.replace(",", "."), errors="coerce")
def sig(df): return (len(df), tuple(np.round(num(df.CameraRotationY).values[:20], 4)))


selected = {sig(rows(tmp / "DATABASE" / f / "FILE.xml")) for f in os.listdir(tmp / "DATABASE")}
pat = re.compile(r"DATA_EXPORT_(Race|Flight)_(\d{4})_(\d{1,2})_(\d{1,2})_")
out = []
for f in sorted(os.listdir(tmp / "RAW_DATABASE")):
    p = tmp / "RAW_DATABASE" / f / "FILE.xml"; m = pat.match(f)
    r = rows(p) if p.exists() else pd.DataFrame()
    lev = num(r.DiscomfortLevel) if len(r) else pd.Series(dtype=float)
    out.append(dict(folder=f, game=m.group(1), date=f"{m.group(2)}-{int(m.group(3)):02d}-{int(m.group(4)):02d}",
                    windows=len(r), in_merged_file=bool(len(r)) and sig(r) in selected, positive_windows=int((lev >= 1).sum()),
                    has_position=bool(len(r)) and all(c in r.columns for c in ("PlayerPositionX", "PlayerPositionY", "PlayerPositionZ"))))
T = pd.DataFrame(out); T.to_csv(TABLES / "T_rev_raw_unused.csv", index=False)
U = T[~T.in_merged_file]
F = dict(raw_sessions=len(T), merged=int(T.in_merged_file.sum()), unused=len(U),
         unused_october=int(U.date.str.startswith("2019-10").sum()), unused_december=int(U.date.str.startswith("2019-12").sum()),
         unused_windows=int(U.windows.sum()), unused_ge250=int((U.windows >= 250).sum()),
         unused_with_positive=int((U.positive_windows > 0).sum()),
         unused_ge250_with_position=int(((U.windows >= 250) & U.has_position).sum()),
         merged_with_position=int(T[T.in_merged_file].has_position.sum()),
         merged_dates=" ".join(sorted(T[T.in_merged_file].date.unique())))
assert F["merged"] == 35 and F["raw_sessions"] == 74
pd.Series(F).rename("value").rename_axis("name").to_csv(TABLES / "T_rev_raw_unused_facts.csv")
print(F)
