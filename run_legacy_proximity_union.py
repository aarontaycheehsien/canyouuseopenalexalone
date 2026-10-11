#!/usr/bin/env python3
"""Execute nine frozen legacy-proximity OQL branches and deduplicate their work IDs.

Uses standard library only; no API key. Results written under stansfield_pilot/
legacy_union_proximity_run/. Failed or incomplete branches never count as zero.
"""
from __future__ import annotations

import csv
import datetime as dt
import gzip
import hashlib
import json
import os
from pathlib import Path
import random
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "stansfield_pilot/queries/legacy_union_proximity_wildcards.oql"
OUT = ROOT / "stansfield_pilot/legacy_union_proximity_run"
OUT.mkdir(exist_ok=True, parents=True)
BASE = "https://api.openalex.org"
PER_PAGE = 100
MAX_REQUESTS = int(os.environ.get("OPENALEX_MAX_REQUESTS", "850"))
REQUEST_COUNT = 0
LOG = []
RUN_START = dt.datetime.now(dt.timezone.utc).isoformat()


def stamp():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def save(name, obj):
    p = OUT / name
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_gz(path, records):
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(records, f, separators=(",", ":"))


def split_branches(text):
    prefix = "works where"
    if not text.startswith(prefix):
        raise ValueError("OQL does not start with 'works where'")
    start = len(prefix)
    depth = 0
    quoted = False
    escape = False
    output = []
    i = start
    while i < len(text):
        ch = text[i]
        if ch == '"' and not escape:
            quoted = not quoted
        if not quoted:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth < 0:
                    raise ValueError("Unbalanced parentheses")
            if depth == 0:
                import re
                m = re.match(r"\s+or\s+\(", text[i:])
                if m:
                    output.append(text[start:i].strip())
                    i += len(m.group()) - 1
                    start = i
                    continue
        escape = (ch == "\\" and not escape)
        if ch != "\\":
            escape = False
        i += 1
    if depth or quoted:
        raise ValueError("Unbalanced parenthesis or quotation mark")
    output.append(text[start:].strip())
    if len(output) != 9:
        raise ValueError(f"Expected 9 branches, found {len(output)}")
    return output


def call(endpoint, payload, *, max_attempts=4):
    global REQUEST_COUNT
    last = None
    data = json.dumps(payload).encode("utf-8")
    for attempt in range(max_attempts):
        if REQUEST_COUNT >= MAX_REQUESTS:
            raise RuntimeError(f"Request cap of {MAX_REQUESTS} reached")
        req = Request(BASE + endpoint, data=data, method="POST", headers={
            "Content-Type": "application/json", "User-Agent": "OpenAlex-legacy-union-proximity-study/1.0"
        })
        REQUEST_COUNT += 1
        started = time.monotonic()
        try:
            with urlopen(req, timeout=85) as response:
                obj = json.load(response)
                status = response.status
                headers = dict(response.headers)
        except HTTPError as e:
            status = e.code
            headers = dict(e.headers)
            body = e.read().decode("utf-8", errors="replace")
            try:
                obj = json.loads(body)
            except ValueError:
                obj = {"error_body": body[:1500]}
        except (URLError, TimeoutError, OSError) as e:
            status = None
            headers = {}
            obj = {"network_error": str(e)[:350]}
        took = round(time.monotonic() - started, 2)
        LOG.append({"time_utc": stamp(), "endpoint": endpoint, "status": status,
                    "seconds": took, "attempt": attempt + 1,
                    "remaining": headers.get("X-RateLimit-Remaining"),
                    "cost": (obj.get("meta") or {}).get("cost") if isinstance(obj, dict) else None})
        if status == 200:
            return obj
        last = {"status": status, "error": obj}
        if status not in (429, 500, 502, 503, 504) and status is not None:
            break
        if status == 429:
            break  # quota exhaustion: do not stall beyond today's budget
        time.sleep(min(3 * (attempt + 1), 12))
    raise RuntimeError(json.dumps(last)[:1200])


def save_progress(counts):
    save("branches_summary.json", counts)
    save("request_log.json", LOG)
    save("execution_status.json", {
        "started_utc": RUN_START, "updated_utc": stamp(), "request_count": REQUEST_COUNT,
        "max_requests": MAX_REQUESTS,
        "complete_branches": sum(x.get("status") == "complete" for x in counts),
        "total_branches": 9,
        "complete": len(counts) == 9 and all(x.get("status") == "complete" for x in counts),
    })


def main():
    source = INPUT.read_text(encoding="utf-8").strip()
    branches = split_branches(source)
    sha256 = hashlib.sha256(source.encode("utf-8")).hexdigest()
    save("run_manifest.json", {
        "input": str(INPUT.relative_to(ROOT)), "input_sha256": sha256,
        "run_start_utc": RUN_START, "branch_count": len(branches),
        "per_page": PER_PAGE, "no_api_key_used": True,
        "method": "nine separate OQL POST searches with cursor pagination and ID union",
    })
    stats = []
    all_ids = set()
    for index, expression in enumerate(branches, 1):
        label = f"branch_{index:02d}"
        query = "works where " + expression
        rec = {"line": index, "query_sha256": hashlib.sha256(query.encode()).hexdigest(),
               "has_proximity": "within " in query,
               "status": "started", "started_utc": stamp()}
        current_ids = set()
        pages = 0
        try:
            # Avoid extra expensive validation requests: each execution validates OQL.
            cursor = "*"
            expected = None
            seen_cursors = set()
            while cursor:
                if cursor in seen_cursors:
                    raise RuntimeError("Repeated cursor token")
                seen_cursors.add(cursor)
                reply = call("/", {"oql": query, "per_page": PER_PAGE,
                                   "cursor": cursor, "select": "id"})
                meta = reply.get("meta", {})
                count = meta.get("count")
                if not isinstance(count, int):
                    raise RuntimeError("No numeric meta.count")
                if expected is None:
                    expected = count
                elif expected != count:
                    raise RuntimeError(f"Count changed from {expected} to {count}")
                records = reply.get("results")
                if not isinstance(records, list):
                    raise RuntimeError("No results list")
                for work in records:
                    work_id = str(work.get("id", "")).rsplit("/", 1)[-1]
                    if not work_id.startswith("W") or not work_id[1:].isdigit():
                        raise RuntimeError(f"Unexpected work ID: {work_id}")
                    if work_id in current_ids:
                        raise RuntimeError(f"Duplicate work ID: {work_id}")
                    current_ids.add(work_id)
                pages += 1
                cursor = meta.get("next_cursor")
                if not records and cursor:
                    raise RuntimeError("Empty page with continuation cursor")
                if pages % 20 == 0:
                    print(f"{label} pages={pages} records={len(current_ids)} of expected={expected}", flush=True)
            if expected != len(current_ids):
                raise RuntimeError(f"Expected {expected} but enumerated {len(current_ids)} unique IDs")
            rec.update(status="complete", total_unique=len(current_ids),
                       api_reported_count=expected, pages=pages)
            write_gz(OUT / (label + "_ids.json.gz"), sorted(current_ids))
            all_ids.update(current_ids)
        except Exception as e:
            rec.update(status="failed", error=str(e)[:1500], partial_unique=len(current_ids),
                       pages=pages)
            if current_ids:
                write_gz(OUT / (label + "_partial_ids.json.gz"), sorted(current_ids))
            print(f"{label} FAILED: {e}", flush=True)
        rec["finished_utc"] = stamp()
        stats.append(rec)
        save_progress(stats)
        print(f"{label} status={rec['status']} unique={rec.get('total_unique', rec.get('partial_unique'))}", flush=True)

    complete = all(s["status"] == "complete" for s in stats)
    if complete:
        union = sorted(all_ids)
        write_gz(OUT / "merged_work_ids.json.gz", union)
        (OUT / "merged_work_ids.txt").write_text("\n".join(union) + "\n", encoding="utf-8")
        old_path = ROOT / ("stansfield_pilot/cursor_study_2026-10-04/"
                           "legacy_union_normalized/default/ordered_ids.json")
        if old_path.exists():
            old = set(json.loads(old_path.read_text(encoding="utf-8")))
            new = set(union)
            legacy = {"legacy_total": len(old), "new_total": len(new),
                      "overlap": len(old & new), "legacy_only": len(old - new),
                      "new_only": len(new - old), "jaccard": len(old & new) / len(old | new)}
            save("legacy_comparison.json", legacy)

        gold_path = ROOT / "stansfield_pilot/reference_retrieval.csv"
        if gold_path.exists():
            by_cohort = {}
            with gold_path.open(encoding="utf-8-sig", newline="") as f:
                reference = list(csv.DictReader(f))
            for cohort, subset in [("primary", [x for x in reference if x["primary"] == "True"]),
                                   ("secondary", reference)]:
                matched = [r for r in subset if r["current_openalex_id"] in all_ids]
                by_cohort[cohort] = {"denominator": len(subset), "recovered": len(matched),
                                     "recall": len(matched) / len(subset),
                                     "missed": [{"title": r["title"], "openalex_id": r["current_openalex_id"]}
                                                for r in subset if r["current_openalex_id"] not in all_ids]}
            save("reference_recall.json", by_cohort)
    save("final_summary.json", {"completed_utc": stamp(), "complete": complete,
                                 "union_unique": len(all_ids) if complete else None,
                                 "complete_branches": sum(s["status"] == "complete" for s in stats),
                                 "failed_branches": [s["line"] for s in stats if s["status"] != "complete"],
                                 "requests": REQUEST_COUNT,
                                 "note": "Union is withheld if any branch failed; incomplete branches are not zero."})
    save_progress(stats)
    print(json.dumps(json.loads((OUT/"final_summary.json").read_text()), indent=2), flush=True)


if __name__ == "__main__":
    main()
