"""Offline verifier for the two designed-search benchmarks (standard library only, no network).

    python3 verify_designed.py anxiety_eating_benchmark_2026-11-13
    python3 verify_designed.py ethnicity_adherence_benchmark_2026-11-13
"""
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
J = lambda p: json.loads((ROOT / p).read_text())  # noqa: E731
checks = []


def ok(cond, msg):
    checks.append((bool(cond), msg))
    if not cond:
        print("FAIL:", msg)


def wid(x):
    return x["id"].rsplit("/", 1)[-1]


man = J("freeze_manifest.json")
for f, h in man["sha256"].items():
    ok(hashlib.sha256((ROOT / f).read_bytes()).hexdigest() == h, f"frozen file unchanged: {f}")
ok(man["candidate_queries_executed"] is False and man["benchmark_list_opened"] is False, "manifest: nothing scored or opened before freeze")
r = subprocess.run([sys.executable, "build_queries.py", "--check"], cwd=ROOT, capture_output=True, text=True)
ok(r.returncode == 0, "builder reproduces frozen queries")
for p in (ROOT / "development").glob("*.json"):
    d = json.loads(p.read_text())
    ok(set(d) <= {"label", "oql", "validated_utc", "valid", "count", "errors"}, f"development {p.stem}: counts only, no result lists")
src = J("results/benchmark_source.json")
m = J("results/benchmark_matches.json")
r = subprocess.run([sys.executable, "adjudicate.py"], cwd=ROOT, capture_output=True, text=True)
ok(r.returncode == 0 and J("results/benchmark_matches.json") == m, "adjudication reproduces benchmark_matches.json")
ids = sorted({x["openalex_id"] for x in m["records"] if x["openalex_id"]})
ok(len(src["studies"]) == src["stated_included_studies"], "study count equals the stated number included")
ok(all(x["citation_title_agreement"] >= 0.9 for x in m["records"] if x["decision"] == "accepted_auto"), "every automatic match agrees with its citation")
obs = J("results/run_observations.json")["arms"]
for q in sorted((ROOT / "queries").glob("*.oql")):
    arm = q.stem
    first = J(f"archives/{arm}/unrestricted_cursor_001.json")
    ok(first["request"]["method"] == "POST" and first["request"]["body"]["oql"] == q.read_text().strip(), f"{arm}: frozen OQL sent by POST")
    oqo, count = first["response"]["meta"]["x_query"]["oqo"], first["response"]["meta"]["count"]
    ok(oqo["filter_rows"] == J(f"validation/{arm}.query.json")["oqo"]["filter_rows"], f"{arm}: executed filters equal pre-freeze validation")
    rt = J(f"archives/{arm}/oqo_roundtrip.json")
    ok(rt["response"]["meta"]["count"] == count == obs[arm]["count"], f"{arm}: OQO round-trip count equal")
    found, seen = set(), []
    for p in sorted((ROOT / f"archives/{arm}").glob("benchmark_membership_*.json")):
        d = json.loads(p.read_text())
        body = d["request"]["body"]["oqo"]
        batch = [f["value"] for f in body["filter_rows"][-1]["filters"]]
        ok(body["filter_rows"][:-1] == oqo["filter_rows"] and len(batch) <= 100, f"{arm}/{p.stem}: only an ID restriction added")
        got = {wid(x) for x in d["response"]["results"]}
        ok(d["response"]["meta"]["count"] == len(got) and got <= set(batch), f"{arm}/{p.stem}: complete batch")
        seen += batch
        found |= got
    ok(sorted(seen) == ids and sorted(found) == obs[arm]["recovered_ids"], f"{arm}: all IDs tested once; recovered IDs reproduced")
s = J("results/summary.json")
with open(ROOT / "results/per_study_retrieval.csv") as f:
    rows = list(csv.DictReader(f))
ok(len(rows) == len(src["studies"]), "matrix: one row per study")
for arm, v in s["arms"].items():
    k = sum(int(r[arm]) for r in rows)
    ok(k == v["studies_recovered"] and v["meets_recall_threshold"] == (k >= s["recall_threshold_studies"]) and v["count_at_most_screened"] == (v["api_count"] <= s["original_screened"]), f"{arm}: {k} studies and threshold flags")
if (ROOT / "results/facet_diagnostics.json").exists():
    fac = J("results/facet_diagnostics.json")
    ok(fac["ids"] == ids, "facet diagnostics cover exactly the matched IDs")
for p in (ROOT / "archives/diagnostics").glob("*.json"):
    body = json.loads(p.read_text())["request"]["body"]["oql"]
    ok(set(body.split("openalex id is (", 1)[1].split(")", 1)[0].split(" or ")) <= set(ids), f"diagnostic {p.stem} restricted to matched IDs")
key_file = ROOT.parent / ".env.txt"
if key_file.exists():
    key = key_file.read_text().strip()
    ok(not [p for p in ROOT.rglob("*") if p.is_file() and key in p.read_text(errors="ignore")], "API key absent from every file")
sums = (ROOT / "SHA256SUMS").read_text().splitlines()
ok(not [ln for ln in sums if hashlib.sha256((ROOT / ln.split("  ", 1)[1]).read_bytes()).hexdigest() != ln.split("  ", 1)[0]], f"SHA256SUMS matches {len(sums)} files")
failed = [c for c in checks if not c[0]]
print(f"{len(checks) - len(failed)}/{len(checks)} checks passed")
sys.exit(1 if failed else 0)
