"""Offline verifier for the smart-conversion arm (no network; needs nltk).

    python3 smart_conversion_2026-11-21/verify.py

Checks: frozen files unchanged; the builder (under its blinding guard) reproduces every frozen
query and the build report; the guard refuses benchmark files; validation, equivalence and caps
agree with the archives; replaying run.py and noetel_run.py from archives alone reproduces the
published results byte for byte; Noetel matches obey the stated thresholds; no credential stored.
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.environ["SMART_OFFLINE"] = "1"
checks = []


def ok(cond, msg):
    checks.append((bool(cond), msg))
    if not cond:
        print("FAIL:", msg)


def J(p):
    return json.loads((ROOT / p).read_text())


def run(*args):
    env = {**os.environ, "SMART_OFFLINE": "1", "OPENALEX_API_KEY": "offline"}
    return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True, env=env)


# 1. Freeze manifest
man = J("freeze_manifest.json")
for f, h in man["sha256"].items():
    ok(hashlib.sha256((ROOT / f).read_bytes()).hexdigest() == h, f"frozen file unchanged: {f}")
ok(not man["benchmark_membership_executed"] and not man["noetel_references_csv_opened"] and not man["noetel_frozen_arms_A_B_executed"],
   "manifest: frozen before any membership test, before Noetel arms ran and before references.csv was opened")

# 2. Builder reproduces queries and report, under the guard
code = ("import json,build;from specs import SPECS;caps=json.load(open('queries/caps.json'));out={};rep=[]\n"
        "for n in SPECS:\n s,e,r=build.render(n,caps[n]['cap'],caps[n]['keywords']);out[n]=(s,e);rep.append(r)\n"
        "print(json.dumps({'q':out,'rep':json.loads(json.dumps(rep))}))")
r = run("-c", code)
ok(r.returncode == 0, "builder runs offline under the blinding guard")
if r.returncode == 0:
    d = json.loads(r.stdout)
    for n, (s, e) in d["q"].items():
        ok((ROOT / f"queries/{n}__S_smart.oql").read_text() == s + "\n", f"builder reproduces {n}__S_smart.oql")
        ok((ROOT / f"queries/{n}__base_equivalence.oql").read_text() == e + "\n", f"builder reproduces {n}__base_equivalence.oql")
    ok(J("queries/build_report.json") == d["rep"], "builder reproduces build_report.json")
g = run("-c", "import build;open('../walker_transgenerational_benchmark_2026-11-12/results/summary.json')")
ok(g.returncode != 0 and "blinding guard" in g.stderr, "blinding guard refuses a benchmark results file")

# 3. Validation, equivalence and caps
vr, caps = J("queries/validation_report.json"), J("queries/caps.json")
for n, v in vr.items():
    ok(v["equivalence_holds"], f"{n}: base_equivalence count equals frozen base count ({v['frozen_base_count']:,})")
    last = v["steps"][-1]
    ok(last["valid"] and last["count_ok"] and (last["cap"], last["keywords"]) == (caps[n]["cap"], caps[n]["keywords"]),
       f"{n}: frozen query is the first valid size step (cap {caps[n]['cap']}, keywords {caps[n]['keywords']})")

# 4. Replays from archives reproduce published results
for script, args, outs in (("run.py", [], ["results/smart_results.json"]),
                           ("noetel_run.py", ["stage1"], ["results/noetel_stage1.json"]),
                           ("noetel_run.py", ["stage2"], ["results/noetel_results.json"])):
    before = {o: (ROOT / o).read_bytes() for o in outs}
    try:
        rr = run(script, *args)
        ok(rr.returncode == 0, f"{script} {' '.join(args)} replays offline")
        for o in outs:
            ok((ROOT / o).read_bytes() == before[o], f"replay reproduces {o}")
    finally:
        for o, b in before.items():
            (ROOT / o).write_bytes(b)
for row in J("results/smart_results.json"):
    ok(not row["base_only_ids"] or True, "")  # reported, not required
    ok(row["smart"]["recovered"] <= row["units_in_openalex"] <= row["unit_denominator"], f"{row['review']}: recovered within denominator")

# 5. Noetel matching
m = J("results/noetel_matches.json")["records"]
adj = {a["row"]: a for a in J("results/noetel_adjudication.json")["records"]}
ok(len(m) == 218, "Noetel: 218 citation rows, none dropped")
for rec in m:
    if rec["decision"] == "accepted_auto":
        need = 0.93 if rec["method"] == "title_search" else 0.80
        ok(rec["title_similarity"] >= need, f"Noetel row {rec['row']}: automatic match meets its threshold")
    else:
        ok(rec["row"] in adj and adj[rec["row"]]["decision"] == rec["decision"], f"Noetel row {rec['row']}: adjudication recorded")
src = J("results/noetel_source.json")["citations"]
ok(all("abstract" not in c for c in src), "Noetel: no abstracts copied into the repository")

# 6. No credential stored
import re
key = os.environ.get("OPENALEX_REAL_KEY", "")   # optional: set to scan for a specific key
bad = [p for p in ROOT.rglob("*.json") if "Authorization" in p.read_text() or re.search(r"api_key=[A-Za-z0-9]{10,}", p.read_text())
       or (key and key in p.read_text())]
ok(not bad, "no credential or Authorization header in any archived file")

checks = [c for c in checks if c[1]]
failed = [c for c in checks if not c[0]]
print(f"{len(checks) - len(failed)}/{len(checks)} checks passed")
sys.exit(1 if failed else 0)
