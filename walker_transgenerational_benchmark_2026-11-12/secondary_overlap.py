"""Secondary, descriptive: overlap with the SYNERGY Walker_2018 record set.

    python3 walker_transgenerational_benchmark_2026-11-12/secondary_overlap.py SYNERGY_IDS_CSV

The CSV is SYNERGY's datasets/Howard_2016/Walker_2018_ids.csv (2023 OpenAlex IDs
for an earlier or partial export of the same PubMed screening). Only the
openalex_id column is read; screening labels are not used. The IDs are uploaded
to a private collection in the key owner's OpenAlex account (collection
management costs no credits), then each frozen arm's executed OQO is re-posted
with one added collection filter and per_page=1, so only counts are retrieved.
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

import run_test as rt

ROOT = rt.ROOT
NAME = "canyouuseopenalexalone Walker 2018 SYNERGY screened set"


def main(csv_path):
    rt.pilot_credentials.load_key()
    raw = Path(csv_path).read_bytes()
    prov = json.loads((ROOT / "source_provenance.json").read_text())["synergy_walker_2018_ids"]
    assert hashlib.sha256(raw).hexdigest() == prov["sha256"]
    rows = list(csv.DictReader(raw.decode().splitlines()))
    ids = sorted({r["openalex_id"].rsplit("/", 1)[-1] for r in rows if r.get("openalex_id")})
    print("rows", len(rows), "distinct OpenAlex IDs", len(ids))
    created = rt.post("synergy/collection_create", {"display_name": NAME, "entity_type": "works",
                      "description": "Benchmark audit set; private.", "access": "private",
                      "member_ids": ids[:10000]}, path="/collections")
    col = created["id"].rsplit("/", 1)[-1]
    for b in range(10000, len(ids), 10000):
        rt.post(f"synergy/collection_add_{b // 10000:02d}", {"member_ids": ids[b:b + 10000]}, path=f"/collections/{col}/members")
    coll_filter = {"column_id": "collection", "value": col, "operator": "in collection"}
    resolvable = rt.post("synergy/set_resolvable_count", {"oqo": {"get_rows": "works", "filter_rows": [coll_filter]}, "per_page": 1, "select": "id"})
    out = {"synergy_rows": len(rows), "distinct_ids_uploaded": len(ids), "collection_id": col,
           "set_works_resolving_today": resolvable["meta"]["count"], "arms": {}}
    for f in sorted((ROOT / "queries").glob("*.oql")):
        arm = f.stem
        first = json.loads((ROOT / "archives" / arm / "unrestricted_cursor_001.json").read_text())["response"]
        oqo = json.loads(json.dumps(first["meta"]["x_query"]["oqo"]))
        oqo["filter_rows"].append(coll_filter)
        r = rt.post(f"synergy/{arm}_overlap_count", {"oqo": oqo, "per_page": 1, "select": "id"})
        out["arms"][arm] = {"arm_count": first["meta"]["count"], "overlap_with_set": r["meta"]["count"]}
        print(arm, out["arms"][arm])
    (ROOT / "results" / "secondary_synergy_overlap.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main(sys.argv[1])
