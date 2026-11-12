"""Offline: build results/summary.json and results/per_study_retrieval.csv from archived evidence."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCREENED, THRESHOLD = 12_117, 42  # 42 = smallest whole number above 95% of 44


def main():
    m = json.loads((ROOT / "results/benchmark_matches.json").read_text())
    obs = json.loads((ROOT / "results/run_observations.json").read_text())
    fac = json.loads((ROOT / "results/facet_diagnostics.json").read_text())["facets"]
    recs = m["records"]
    s = {"benchmark": "Bao et al. 2024, doi:10.1007/s40279-024-02040-1", "studies": len(recs), "in_openalex": m["in_openalex"],
         "recall_threshold": THRESHOLD, "original_screened": SCREENED, "arms": {}}
    rows = {r["ref_id"]: {"ref_id": r["ref_id"], "study_label": r["study_label"], "openalex_id": r["openalex_id"]} for r in recs}
    for arm, o in obs["arms"].items():
        found = set(o["recovered_ids"])
        k = 0
        for r in recs:
            hit = r["openalex_id"] in found
            rows[r["ref_id"]][arm] = int(hit)
            k += hit
        e = o["export"]
        s["arms"][arm] = {"api_count": o["count"], "oqo_roundtrip_count_equal": o["count"] == o["oqo_roundtrip_count"],
                          "cursor_page2_consistent": o.get("cursor_page2_consistent"), "recovered": k,
                          "recall": round(k / len(recs), 4), "meets_recall_threshold": k >= THRESHOLD,
                          "count_at_most_screened": o["count"] <= SCREENED, "ratio_to_screened": round(o["count"] / SCREENED, 3),
                          "complete_unrestricted_export": bool(e.get("complete")),
                          "export_matches_membership": sorted(e.get("benchmark_ids_in_export", [])) == sorted(found)}
    for r in recs:
        for f, v in fac.items():
            rows[r["ref_id"]]["facet_" + f] = int(r["openalex_id"] in v["matching_ids"])
        rows[r["ref_id"]]["citation"] = r["citation"]
    out = list(rows.values())
    with open(ROOT / "results/per_study_retrieval.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    (ROOT / "results/summary.json").write_text(json.dumps(s, indent=1) + "\n")
    print(json.dumps(s, indent=1))


if __name__ == "__main__":
    main()
