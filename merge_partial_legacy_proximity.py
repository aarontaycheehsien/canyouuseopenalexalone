#!/usr/bin/env python3
"""Merge persisted complete/partial OpenAlex branches without any API requests."""
from __future__ import annotations
import csv
import datetime as dt
import gzip
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
FOLDER=ROOT/"stansfield_pilot/legacy_union_proximity_run"
stats=json.loads((FOLDER/"branches_summary.json").read_text(encoding="utf-8"))
if len(stats)!=9:raise RuntimeError("Expected nine branches")
all_ids=set()
by_branch={}
for row in stats:
    n=row["line"]
    partial=(row["status"]!="complete")
    file=FOLDER/f"branch_{n:02d}{'_partial' if partial else ''}_ids.json.gz"
    if not file.exists():raise RuntimeError(f"Missing {file}")
    with gzip.open(file,"rt",encoding="utf-8") as f:
        values=json.load(f)
    ids=set(values)
    if len(ids)!=len(values):raise RuntimeError(f"Duplicate IDs in {file}")
    by_branch[n]=ids
    all_ids.update(ids)
old_path=ROOT/"stansfield_pilot/cursor_study_2026-10-04/legacy_union_normalized/default/ordered_ids.json"
old=set(json.loads(old_path.read_text(encoding="utf-8")))
gold_path=ROOT/"stansfield_pilot/reference_retrieval.csv"
with gold_path.open(encoding="utf-8-sig",newline="") as f:refs=list(csv.DictReader(f))
known={}
for key, subset in [
  ("primary", [r for r in refs if r["primary"]=="True"]),
  ("secondary", refs),
]:
    original_known={r["current_openalex_id"] for r in subset if r["current_openalex_id"] in old}
    current_known={r["current_openalex_id"] for r in subset if r["current_openalex_id"] in all_ids}
    known[key]={"denominator":len(subset),
                "observed_recovered_lower_bound":len(current_known),
                "observed_recall_lower_bound":len(current_known)/len(subset),
                "already_in_original_legacy":len(current_known&original_known),
                "observed_additional_known_vs_legacy":len(current_known-original_known),
                "observed_missed": [
                  {"title":r["title"],"openalex_id":r["current_openalex_id"]}
                  for r in subset if r["current_openalex_id"] not in all_ids],
               }
result={
  "created_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
  "status":"PARTIAL_NOT_COMPLETE",
  "meaning":"lower bounds only: five of nine branches failed before completion",
  "all_observed_unique_work_ids":len(all_ids),
  "original_legacy_unique":len(old),
  "observed_overlap_with_original_legacy":len(all_ids&old),
  "observed_new_only":len(all_ids-old),
  "original_legacy_not_yet_observed":len(old-all_ids),
  "branch_counts":[{"line":n,"observed_unique":len(ids),
                    "status":stats[n-1]["status"]} for n,ids in by_branch.items()],
  "reference_recovery":known,
}
(FOLDER/"partial_merged_work_ids.txt").write_text("\n".join(sorted(all_ids))+"\n",encoding="utf-8")
with gzip.open(FOLDER/"partial_merged_work_ids.json.gz","wt",encoding="utf-8") as f:
    json.dump(sorted(all_ids),f,separators=(",",":"))
(FOLDER/"partial_merge_summary.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,indent=2))
