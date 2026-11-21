"""Offline verifier for the post-hoc truncation and proximity arms (no network, no API key).

    python3 adapted_proximity_wildcard_2026-11-13/verify.py

Checks that adapt.py regenerates every adapted query and plan.json, that every archived request
carries no credential, and that replaying run_adapted.py from the archives alone (any request
missing from the archives is a failure) reproduces results/adapted_results.json exactly.
Requires nltk (PorterStemmer) for adapt.py.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import adapt  # noqa: E402
import run_adapted  # noqa: E402

checks = []


def ok(cond, msg):
    checks.append((bool(cond), msg))
    if not cond:
        print("FAIL:", msg)


# 1. Queries and plan regenerate from the frozen benchmark queries.
plan = json.loads((ROOT / "queries/plan.json").read_text())
regen = []
for b in adapt.BENCHMARKS:
    for q in sorted((adapt.REPO / b / "queries").glob("*.oql")):
        src = q.read_text().strip()
        new = adapt.adapt(src)
        name = f"{b.split('_benchmark')[0]}__{q.stem}"
        ok((ROOT / "queries" / f"{name}.oql").read_text() == new + "\n", f"adapt.py reproduces queries/{name}.oql")
        regen.append({"benchmark": b, "arm": q.stem, "name": name, "frozen_chars": len(src), "adapted_chars": len(new)})
ok(regen == plan, f"adapt.py reproduces plan.json ({len(plan)} arms)")

# 2. Archives hold no credential and only POSTs to the OpenAlex API.
key = os.environ.get("OPENALEX_API_KEY") or ""
env = adapt.REPO / ".env.txt"
if not key and env.exists():
    key = env.read_text(encoding="utf-8-sig").strip().split("=")[-1].strip().strip("\"'")
archives = sorted((ROOT / "archives").rglob("*.json"))
bad = []
for p in archives:
    text = p.read_text()
    d = json.loads(text)
    if "headers" in d.get("request", {}) or "Bearer" in text or (key and key in text):
        bad.append(p.name)
ok(not bad, f"no credential or headers in {len(archives)} archived files")

# 3. Replay the runner from archives only.
missing = []


def archived_call(label, url, body):
    dest = ROOT / "archives" / f"{label}.json"
    if not dest.exists():
        missing.append(label)
        raise SystemExit(f"FAIL: request not archived: {label}")
    d = json.loads(dest.read_text())
    if d["request"]["body"] != body or d["request"]["url"] != url:
        missing.append(label)
        raise SystemExit(f"FAIL: archived request differs from the one the runner would send: {label}")
    return d["status"], d["response"]


out = ROOT / "results/adapted_results.json"
published = out.read_bytes()
run_adapted.call = archived_call
run_adapted.pilot_credentials.load_key = lambda: None
run_adapted.print = lambda *a, **k: None
try:
    run_adapted.main()
    replayed = out.read_bytes()
finally:
    out.write_bytes(published)
ok(not missing, "every request the runner makes is archived with an identical body")
ok(replayed == published, "archive replay reproduces results/adapted_results.json byte for byte")

# 4. Internal consistency of the published rows.
rows = json.loads(published)
for r in rows:
    if not r["valid"]:
        continue
    lost = set(r["lost_vs_frozen"])
    ok(r["adapted_recovered"] <= r["units_in_openalex"] <= r["unit_denominator"], f"{r['name']}: recovered within denominator")
    ok(lost.isdisjoint(r["adapted_recovered_ids"]), f"{r['name']}: lost IDs not among adapted recoveries")

failed = [c for c in checks if not c[0]]
print(f"{len(checks) - len(failed)}/{len(checks)} checks passed")
sys.exit(1 if failed else 0)
