"""Offline verifier for the frozen exercise-for-depression protocol (no network, no API key).

    python3 exercise_transfer_benchmark_2026-11-12/verify.py

This benchmark was frozen but never executed: there are no searches, matches or results to check.
The verifier confirms only the freeze: every frozen file still has its manifest hash, nothing was
run or inspected before the freeze, and build_queries.py regenerates both frozen queries.
"""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
checks = []


def ok(cond, msg):
    checks.append((bool(cond), msg))
    if not cond:
        print("FAIL:", msg)


man = json.loads((ROOT / "freeze_manifest.json").read_text())
for f, h in man["sha256"].items():
    ok(hashlib.sha256((ROOT / f).read_bytes()).hexdigest() == h, f"frozen file unchanged: {f}")
ok(man["benchmark_titles_inspected"] is False and man["candidate_queries_executed"] is False,
   "manifest: no benchmark titles inspected and no query executed before freeze")
frozen_queries = sorted(p.name for p in (ROOT / "queries").glob("*.oql"))
ok(frozen_queries == sorted(Path(f).name for f in man["sha256"] if f.startswith("queries/")),
   "every query file is covered by the manifest")

with tempfile.TemporaryDirectory() as tmp:
    shutil.copy(ROOT / "build_queries.py", tmp)
    (Path(tmp) / "queries").mkdir()
    r = subprocess.run([sys.executable, "build_queries.py"], cwd=tmp, capture_output=True, text=True)
    ok(r.returncode == 0, "build_queries.py runs")
    for q in frozen_queries:
        built = Path(tmp) / "queries" / q
        ok(built.exists() and built.read_bytes() == (ROOT / "queries" / q).read_bytes(), f"builder reproduces queries/{q}")

ok(not (ROOT / "results").exists() and not (ROOT / "archives").exists(),
   "no results or archives present (protocol frozen, not executed)")

failed = [c for c in checks if not c[0]]
print(f"{len(checks) - len(failed)}/{len(checks)} checks passed")
sys.exit(1 if failed else 0)
