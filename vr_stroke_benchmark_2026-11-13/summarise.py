"""Offline: results/summary.json and results/per_study_retrieval.csv. Unit: the trial (55)."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCREENED, THRESHOLD, N = 7381, 53, 55


def main():
    src = json.loads((ROOT / "results/benchmark_source.json").read_text())
    m = json.loads((ROOT / "results/benchmark_matches.json").read_text())
    obs = json.loads((ROOT / "results/run_observations.json").read_text())["arms"]
    fac = json.loads((ROOT / "results/facet_diagnostics.json").read_text())["facets"]
    refs = {r["ref_id"]: r for r in m["records"]}
    s = {"benchmark": "Soleimani et al. 2024, doi:10.1186/s12911-024-02534-y", "studies": N, "references": len(refs),
         "studies_in_openalex": m["studies_in_openalex"], "recall_threshold_studies": THRESHOLD, "original_screened": SCREENED, "arms": {}}
    rows = {st["study_id"]: {"study_id": st["study_id"], "study_label": st["study_label"], "ref_id": st["ref_ids"][0],
                             "openalex_id": refs[st["ref_ids"][0]]["openalex_id"]} for st in src["studies"]}
    for arm, o in obs.items():
        found = set(o["recovered_ids"])
        k = 0
        for row in rows.values():
            row[arm] = int(row["openalex_id"] in found)
            k += row[arm]
        s["arms"][arm] = {"api_count": o["count"], "oqo_roundtrip_count_equal": o["count"] == o["oqo_roundtrip_count"],
                          "cursor_page2_consistent": o.get("cursor_page2_consistent"), "studies_recovered": k,
                          "study_recall": round(k / N, 4), "references_recovered": len(found), "meets_recall_threshold": k >= THRESHOLD,
                          "count_at_most_screened": o["count"] <= SCREENED, "ratio_to_screened": round(o["count"] / SCREENED, 3),
                          "evidence": "restricted membership (no export, by protocol)"}
    s["facets_over_matched_references"] = {k: len(v["matching_ids"]) for k, v in fac.items()}
    for row in rows.values():
        for f, v in fac.items():
            row["facet_" + f] = int(row["openalex_id"] in v["matching_ids"])
    out = list(rows.values())
    with open(ROOT / "results/per_study_retrieval.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    (ROOT / "results/summary.json").write_text(json.dumps(s, indent=1) + "\n")
    print(json.dumps(s["arms"], indent=1))


if __name__ == "__main__":
    main()
