"""Post-evaluation diagnostics; never alter either frozen candidate."""
import json
from run_test import ROOT, now, post, save


def main():
    summary = json.loads((ROOT / "results/summary.json").read_text())
    misses = set().union(*(set(s["missed_reference_ids"]) for s in summary))
    rows = json.loads((ROOT / "results/benchmark_matches.json").read_text())["records"]
    target = [r for r in rows if r["reference_id"] in misses]
    restrict = {"join": "or", "filters": [{"column_id": "ids.openalex", "value": r["openalex_id"]} for r in target]}
    a = json.loads((ROOT / "validation/A_fuller_source_union.json").read_text())["response"]["oqo"]["filter_rows"]
    b = json.loads((ROOT / "validation/B_compact_three_concepts.json").read_text())["response"]["oqo"]["filter_rows"]
    branches = a[2]["filters"]
    cases = {"date": a[0], "A_population": a[1], "A_routes": a[2],
             "B_population": b[1], "B_prediction": b[2], "B_biomarkers": b[3],
             "A_long_prediction": branches[0]["filters"][0],
             "A_long_biomarkers": branches[0]["filters"][1],
             "A_short_prediction": branches[1]["filters"][0],
             "A_short_biomarkers": branches[1]["filters"][1],
             "A_no_prediction_biomarkers": {"join": "or", "filters": branches[2:]}}
    results = []
    for name, clause in cases.items():
        v = post("diagnostics/" + name, {"oqo": {"get_rows": "works", "filter_rows": [restrict, clause]},
                                         "per_page": 200, "select": "id,display_name"})
        ids = {w["id"] for w in v["results"]}
        assert len(ids) == v["meta"]["count"]
        row = {"clause": name, "matches": {r["reference_id"]: r["openalex_id"] in ids for r in target}}
        results.append(row)
        print(name, "failed:", [ref for ref, found in row["matches"].items() if not found], flush=True)
    save(ROOT / "results/clause_diagnostics.json", {"phase": "post-freeze, after primary membership evaluation; no repair",
                                                      "completed_utc": now(), "results": results})


if __name__ == "__main__":
    main()
