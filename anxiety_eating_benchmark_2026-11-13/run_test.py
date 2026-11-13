"""Execute the frozen arms by OQL POST. Explicit live runner; nothing runs on import.

    OPENALEX_API_KEY=... python3 anxiety_eating_benchmark_2026-11-13/run_test.py
(or a single-line key in the repository's git-ignored .env.txt)

Every request is POST https://api.openalex.org/ with a JSON body. Bodies, status
codes, responses and UTC timestamps are archived; headers and the key are not.
Existing successful responses are reused, so a rerun never silently replaces
evidence. A new live replication should use a fresh output directory.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import pilot_credentials  # noqa: E402  (reads the key without printing it)

ARCH = ROOT / "archives"
EXPORT_CAP = 20_000          # frozen in PROTOCOL.md (budget-limited)
SKIP_EXPORT = os.environ.get("SKIP_EXPORT") == "1"  # defer exports to after the daily budget reset
SELECT = "id,doi,display_name,publication_date"
UA = "OpenAlex-transfer-benchmark/1.0 (OQL POST evaluation)"


def now():
    return datetime.now(timezone.utc).isoformat()


def post(label, body, path="/"):
    dest = ARCH / (label + ".json")
    request = {"method": "POST", "path": path, "body": body}
    if dest.exists():
        old = json.loads(dest.read_text())
        assert old["request"] == request, f"archived request differs: {dest}"
        if old["status"] in (200, 201, 202):
            return old["response"]
        raise RuntimeError(f"previous failure preserved at {dest}; use a new output label")
    headers = {"Content-Type": "application/json", "User-Agent": UA,
               "Authorization": "Bearer " + os.environ["OPENALEX_API_KEY"]}
    attempts = []
    for attempt in range(4):
        started = now()
        try:
            req = urllib.request.Request("https://api.openalex.org" + path, data=json.dumps(body).encode(), headers=headers)
            with urllib.request.urlopen(req, timeout=120) as r:
                status, raw = r.status, r.read().decode()
        except urllib.error.HTTPError as e:
            status, raw = e.code, e.read().decode(errors="replace")
        except OSError as e:
            status, raw = 0, json.dumps({"transport_error": type(e).__name__})
        try:
            response = json.loads(raw)
        except ValueError:
            response = {"non_json_response": raw[:5000]}
        attempts.append({"started_utc": started, "finished_utc": now(), "status": status, "response": response})
        if status not in (0, 429, 500, 502, 503, 504):
            break
        time.sleep(3 * (attempt + 1))
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({"request": request, **attempts[-1], "attempts": attempts[:-1]}, indent=1))
    if status not in (200, 201, 202):
        raise RuntimeError(f"HTTP {status}; response preserved at {dest}")
    return response


def restrict(oqo, ids):
    oqo = json.loads(json.dumps(oqo))
    oqo["filter_rows"].append({"join": "or", "filters": [{"column_id": "ids.openalex", "value": i} for i in ids]})
    return oqo


def main():
    pilot_credentials.load_key()
    matches = json.loads((ROOT / "results" / "benchmark_matches.json").read_text())
    ids = sorted({i for m in matches["records"] if m["openalex_id"] for i in [m["openalex_id"], *m.get("alternate_openalex_ids", [])]})
    summary = {"run_started_utc": now(), "matched_distinct_ids": len(ids), "arms": {}}
    for f in sorted((ROOT / "queries").glob("*.oql")):
        arm, oql = f.stem, f.read_text().strip()
        first = post(f"{arm}/unrestricted_cursor_001",
                     {"oql": oql, "per_page": 100, "sort": "publication_date:asc", "select": SELECT, "cursor": "*"})
        count, oqo = first["meta"]["count"], first["meta"]["x_query"]["oqo"]
        print(arm, "count", count, flush=True)
        # POST execution check: the echoed OQO, re-posted, must give the same count.
        rt = post(f"{arm}/oqo_roundtrip", {"oqo": oqo, "per_page": 1, "select": "id"})
        # POST cursor continuation check (page 2), kept whether or not a full export follows.
        p2 = post(f"{arm}/unrestricted_cursor_002",
                  {"oql": oql, "per_page": 100, "sort": "publication_date:asc", "select": SELECT, "cursor": first["meta"]["next_cursor"]})
        # Membership: identical executed OQO + AND restriction to matched IDs, <=100 per batch.
        found = []
        for b in range(0, len(ids), 100):
            batch = ids[b:b + 100]
            r = post(f"{arm}/benchmark_membership_{b // 100 + 1:02d}", {"oqo": restrict(oqo, batch), "per_page": 100, "select": SELECT})
            got = [x["id"].rsplit("/", 1)[-1] for x in r["results"]]
            assert r["meta"]["count"] == len(got) and set(got) <= set(batch)
            found += got
        arm_sum = {"count": count, "oqo_roundtrip_count": rt["meta"]["count"], "recovered_ids": sorted(found),
                   "first_page_ids": [x["id"].rsplit("/", 1)[-1] for x in first["results"]],
                   "cursor_page2_consistent": p2["meta"]["count"] == count and not ({x["id"] for x in p2["results"]} & {x["id"] for x in first["results"]}),
                   "export": {"attempted": count <= EXPORT_CAP and not SKIP_EXPORT, "eligible": count <= EXPORT_CAP}}
        if count <= EXPORT_CAP and not SKIP_EXPORT:
            rows, cursor, page, counts = list(first["results"]) + list(p2["results"]), p2["meta"].get("next_cursor"), 2, [count, p2["meta"]["count"]]
            while cursor:
                page += 1
                v = post(f"{arm}/unrestricted_cursor_{page:03d}",
                         {"oql": oql, "per_page": 100, "sort": "publication_date:asc", "select": SELECT, "cursor": cursor})
                counts.append(v["meta"]["count"])
                rows += v["results"]
                cursor = v["meta"].get("next_cursor")
                if not v["results"]:
                    break
            exported = [x["id"].rsplit("/", 1)[-1] for x in rows]
            arm_sum["export"].update({"pages": page, "rows": len(exported), "distinct": len(set(exported)),
                                      "counts_consistent": len(set(counts)) == 1,
                                      "complete": len(set(counts)) == 1 and len(exported) == len(set(exported)) == count,
                                      "benchmark_ids_in_export": sorted(set(exported) & set(ids))})
            (ROOT / "results" / f"{arm}_export_ids.json").write_text(json.dumps(sorted(set(exported))) + "\n")
        summary["arms"][arm] = arm_sum
        print(arm, "recovered", len(found), "of", len(ids), "export", arm_sum["export"], flush=True)
    summary["run_finished_utc"] = now()
    (ROOT / "results" / "run_observations.json").write_text(json.dumps(summary, indent=1) + "\n")


if __name__ == "__main__":
    main()
