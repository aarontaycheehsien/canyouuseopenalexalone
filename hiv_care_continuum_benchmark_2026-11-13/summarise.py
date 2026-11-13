"""Offline: build results/summary.json and results/per_study_retrieval.csv from archived evidence."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCREENED, THRESHOLD = 10_281, 181  # 181 = smallest whole number above 95% of 190


def main():
    m = json.loads((ROOT / "results/benchmark_matches.json").read_text())
    obs = json.loads((ROOT / "results/run_observations.json").read_text())
    fac = json.loads((ROOT / "results/facet_diagnostics.json").read_text())["facets"]
    recs = m["records"]
    s = {"benchmark": "Haw et al. 2025, doi:10.1002/jia2.26526", "studies": len(recs), "in_openalex": m["in_openalex"],
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
                          "export_matches_membership": (sorted(e["benchmark_ids_in_export"]) == sorted(found)) if e.get("attempted") else None, "evidence": "complete cursor export plus restricted membership" if e.get("complete") else "restricted membership only (count above the 20,000 export cap)"}
    cited = next(r for r in recs if r["ref_id"] == "HIV-098")["cited_reference_openalex_id"]
    for arm, o in obs["arms"].items():
        # sensitivity: score the review's literal reference 98 (a 1980 paper, outside the date window) instead
        k = s["arms"][arm]["recovered"] - rows["HIV-098"][arm] + int(cited in o["recovered_ids"])
        s["arms"][arm]["recovered_if_reference_98_taken_literally"] = k
    probes = json.loads((ROOT / "results/posthoc_probes.json").read_text())
    s["posthoc"] = {"children_block_failures": probes["children_summary"],
                    "hiv_block_failures": len(probes["hiv_block_failures"]),
                    "hiv_failures_with_immunodeficiency": len(probes["hiv_failures_with_immunodeficiency"]),
                    "has_abstract": len(fac["has_abstract"]["matching_ids"]),
                    "A_without_age_block": probes["A_without_age_block"],
                    "age_block_translation_sensitivity": {k: v for k, v in probes["age_block_translation_sensitivity"].items() if k != "ids"}}
    for r in recs:
        for f, v in fac.items():
            rows[r["ref_id"]]["facet_" + f] = ("" if not r["openalex_id"] else int(r["openalex_id"] in v["matching_ids"]))
        rows[r["ref_id"]]["citation"] = r["citation"]
    out = list(rows.values())
    with open(ROOT / "results/per_study_retrieval.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    (ROOT / "results/summary.json").write_text(json.dumps(s, indent=1) + "\n")
    print(json.dumps(s, indent=1))


if __name__ == "__main__":
    main()
