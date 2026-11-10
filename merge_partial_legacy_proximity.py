#!/usr/bin/env python3
"""Merge validated saved OpenAlex branches without any API requests."""
from __future__ import annotations

import csv
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import re

from run_legacy_proximity_union import split_branches

ROOT = Path(__file__).resolve().parent
PRODUCTS = ("partial_merged_work_ids.txt", "partial_merged_work_ids.json.gz",
            "partial_merge_summary.json")


def merge(root=ROOT):
    folder = root / "stansfield_pilot/legacy_union_proximity_run"
    # Failed validation must not leave an earlier derived result looking current.
    for name in PRODUCTS:
        (folder / name).unlink(missing_ok=True)
    stats = json.loads((folder / "branches_summary.json").read_text(encoding="utf-8"))
    if (not isinstance(stats, list) or len(stats) != 9
            or any(not isinstance(row, dict) or type(row.get("line")) is not int
                   for row in stats)
            or {row["line"] for row in stats} != set(range(1, 10))):
        raise RuntimeError("Expected each branch 1 through 9 exactly once")
    stats = sorted(stats, key=lambda row: row["line"])
    manifest = json.loads((folder / "run_manifest.json").read_text(encoding="utf-8"))
    source = (root / "stansfield_pilot/queries/legacy_union_proximity_wildcards.oql").read_text(
        encoding="utf-8").strip()
    if hashlib.sha256(source.encode("utf-8")).hexdigest() != manifest["input_sha256"]:
        raise RuntimeError("Query does not match the saved run manifest")
    branches = split_branches(source)
    all_ids = set()
    by_branch = {}
    for row in stats:
        n = row["line"]
        if row.get("status") not in ("complete", "failed"):
            raise RuntimeError(f"Branch {n} has no terminal status")
        query_hash = hashlib.sha256(("works where " + branches[n - 1]).encode()).hexdigest()
        if row.get("query_sha256") != query_hash:
            raise RuntimeError(f"Branch {n} query hash does not match")
        partial = row["status"] != "complete"
        file = folder / f"branch_{n:02d}{'_partial' if partial else ''}_ids.json.gz"
        if not file.exists():
            raise RuntimeError(f"Missing {file}")
        with gzip.open(file, "rt", encoding="utf-8") as f:
            values = json.load(f)
        if (not isinstance(values, list)
                or any(not isinstance(v, str) or not re.fullmatch(r"W[0-9]+", v)
                       for v in values)):
            raise RuntimeError(f"Invalid work IDs in {file}")
        ids = set(values)
        if len(ids) != len(values):
            raise RuntimeError(f"Duplicate IDs in {file}")
        expected = row.get("partial_unique" if partial else "total_unique")
        if type(expected) is not int or expected != len(ids):
            raise RuntimeError(f"Branch {n} saved ID count does not match its summary")
        if not partial and row.get("api_reported_count") != len(ids):
            raise RuntimeError(f"Branch {n} saved ID count does not match the API count")
        by_branch[n] = ids
        all_ids.update(ids)

    old_path = root / ("stansfield_pilot/cursor_study_2026-10-04/"
                       "legacy_union_normalized/default/ordered_ids.json")
    old = set(json.loads(old_path.read_text(encoding="utf-8")))
    with (root / "stansfield_pilot/reference_retrieval.csv").open(
            encoding="utf-8-sig", newline="") as f:
        refs = list(csv.DictReader(f))
    known = {}
    for key, subset in [("primary", [r for r in refs if r["primary"] == "True"]),
                        ("secondary", refs)]:
        original_known = {r["current_openalex_id"] for r in subset
                          if r["current_openalex_id"] in old}
        current_known = {r["current_openalex_id"] for r in subset
                         if r["current_openalex_id"] in all_ids}
        known[key] = {
            "denominator": len(subset),
            "observed_recovered_lower_bound": len(current_known),
            "observed_recall_lower_bound": len(current_known) / len(subset),
            "already_in_original_legacy": len(current_known & original_known),
            "observed_additional_known_vs_legacy": len(current_known - original_known),
            "observed_missed": [{"title": r["title"], "openalex_id": r["current_openalex_id"]}
                                for r in subset if r["current_openalex_id"] not in all_ids],
        }
    failed = sum(row["status"] != "complete" for row in stats)
    result = {
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "PARTIAL_NOT_COMPLETE" if failed else "COMPLETE",
        "meaning": (f"lower bounds only: {failed} of nine branches failed before completion"
                    if failed else "all nine branches completed; observed counts are complete"),
        "source_run_start_utc": manifest["run_start_utc"],
        "input_sha256": manifest["input_sha256"],
        "all_observed_unique_work_ids": len(all_ids),
        "original_legacy_unique": len(old),
        "observed_overlap_with_original_legacy": len(all_ids & old),
        "observed_new_only": len(all_ids - old),
        "original_legacy_not_yet_observed": len(old - all_ids),
        "branch_counts": [{"line": row["line"], "observed_unique": len(by_branch[row["line"]]),
                           "status": row["status"]} for row in stats],
        "reference_recovery": known,
    }
    (folder / "partial_merged_work_ids.txt").write_text(
        "".join(work_id + "\n" for work_id in sorted(all_ids)), encoding="utf-8")
    with gzip.open(folder / "partial_merged_work_ids.json.gz", "wt", encoding="utf-8") as f:
        json.dump(sorted(all_ids), f, separators=(",", ":"))
    (folder / "partial_merge_summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(merge(), indent=2))
