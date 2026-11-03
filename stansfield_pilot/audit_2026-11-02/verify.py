"""Recalculate the reported recall from archived API responses, offline."""
import csv
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent

def check(condition, message):
    if not condition:
        raise ValueError(message)

def work_ids(records):
    return [record["id"].rsplit("/", 1)[-1] for record in records]

def read_json(archive, path):
    return json.loads(archive.read(path))

def verify():
    for line in (ROOT / "SHA256SUMS").read_text().splitlines():
        checksum, path = line.split("  ", 1)
        check(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == checksum, path)
    indexed = set((ROOT / "benchmark/benchmark_130_verified_ids.txt").read_text().splitlines())
    with (ROOT / "results/per_study_retrieval.csv").open() as f:
        matrix = list(csv.DictReader(f))
    check(len(matrix) == 133 and len(indexed) == 130, "benchmark sizes")
    check({r["openalex_id"] for r in matrix if r["openalex_id"]} == indexed, "matrix IDs")
    original = {r["openalex_id"] for r in matrix if r["original"] == "True" and r["openalex_id"]}
    check(len(original) == 128, "original indexed benchmark")
    totals = json.loads((ROOT / "results/recall_summary.json").read_text())
    with zipfile.ZipFile(next((ROOT / "archives").glob("*full_130*"))) as full, \
         zipfile.ZipFile(next((ROOT / "archives").glob("*live_query*"))) as initial:
        for row in totals:
            strategy = row["strategy"]
            member = read_json(full, "verified_" + strategy + "_benchmark.json")
            total = read_json(full, strategy + "_total.json")
            check(member["status"] == total["status"] == 200, strategy + " request status")
            matches = set(work_ids(member["response"]["results"]))
            check(len(matches) == member["response"]["meta"]["count"] and matches <= indexed, strategy)
            check(matches == {r["openalex_id"] for r in matrix if r[strategy] == "Retrieved"}, strategy + " matrix")
            check(len(matches) == row["expanded_130_found"] and len(matches & original) == row["original_128_found"], strategy + " recall")
            check(total["response"]["meta"]["count"] == row["retrieved_records"], strategy + " total")
            source = read_json(initial, "responses/" + strategy + ".json")
            query = source.get("query") or source["request"]["oql"]
            check(query == (ROOT / "queries" / (strategy + ".oql")).read_text().rstrip("\n"), strategy + " query")
            check(source["response"]["meta"]["x_query"]["oqo"] == total["request"]["oqo"], strategy + " executed query")
            print(f"{strategy:35s} {row['retrieved_records']:6,d} records  {len(matches):3d}/130")
        pages = sorted(n for n in full.namelist() if n.startswith("unrestricted_final_pages/page_"))
        rows = [r for n in pages for r in read_json(full, n)["response"]["results"]]
        ids = work_ids(rows)
        check((len(pages), len(ids), len(set(ids))) == (20, 3892, 3891), "numbered pages")
        check(indexed <= set(ids), "unrestricted benchmark intersection")
        print("Unrestricted export contains all 130 verified benchmark IDs.")
        for test, expected in [("Felfeli_proximity", 1), ("Felfeli_screening_block", 0), ("Felfeli_screen_star", 0)]:
            check(read_json(initial, "responses/" + test + ".json")["response"]["meta"]["count"] == expected, test)

if __name__ == "__main__":
    verify()
