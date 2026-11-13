"""Offline: build results/summary.json and results/per_study_retrieval.csv from archived evidence.

Primary unit: the study (51). A study is recovered if any of its cited references is retrieved.
Secondary: references (51 distinct; 48 in OpenAlex).
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCREENED, THRESHOLD = 14_566, 49  # 49 = smallest whole number above 95% of 51


def main():
    src = json.loads((ROOT / "results/benchmark_source.json").read_text())
    m = json.loads((ROOT / "results/benchmark_matches.json").read_text())
    obs = json.loads((ROOT / "results/run_observations.json").read_text())
    fac = json.loads((ROOT / "results/facet_diagnostics.json").read_text())["facets"]
    probes = json.loads((ROOT / "results/posthoc_probes.json").read_text())
    refs = {r["ref_id"]: r for r in m["records"]}
    s = {"benchmark": "Kettle et al. 2022, doi:10.1136/bmj-2021-068465", "studies": len(src["studies"]),
         "references": len(refs), "studies_in_openalex": m["studies_in_openalex"], "references_in_openalex": m["references_in_openalex"],
         "recall_threshold_studies": THRESHOLD, "original_screened": SCREENED, "arms": {}}
    rows = {st["study_id"]: {"study_id": st["study_id"], "study_label": st["study_label"], "ref_ids": " ".join(st["ref_ids"]),
                             "openalex_ids": " ".join(refs[r]["openalex_id"] or "" for r in st["ref_ids"]).strip()} for st in src["studies"]}
    hes = refs["PA-044"]["openalex_id"]
    for arm, o in obs["arms"].items():
        found = set(o["recovered_ids"])
        k = 0
        for st in src["studies"]:
            hit = any(refs[r]["openalex_id"] in found for r in st["ref_ids"] if refs[r]["openalex_id"])
            rows[st["study_id"]][arm] = int(hit)
            k += hit
        e = o["export"]
        s["arms"][arm] = {"api_count": o["count"], "oqo_roundtrip_count_equal": o["count"] == o["oqo_roundtrip_count"],
                          "cursor_page2_consistent": o.get("cursor_page2_consistent"),
                          "studies_recovered": k, "study_recall": round(k / len(src["studies"]), 4),
                          "references_recovered": len(found), "reference_recall": round(len(found) / len(refs), 4),
                          "meets_recall_threshold": k >= THRESHOLD, "count_at_most_screened": o["count"] <= SCREENED,
                          "ratio_to_screened": round(o["count"] / SCREENED, 3), "complete_unrestricted_export": bool(e.get("complete")),
                          "export_matches_membership": (sorted(e["benchmark_ids_in_export"]) == sorted(found)) if e.get("attempted") else None,
                          "studies_recovered_if_PA044_scored_as_cited_abstract": k - int(hes in found),
                          "evidence": "complete cursor export plus restricted membership" if e.get("complete") else "restricted membership only"}
    s["posthoc"] = {"has_abstract": len(fac["has_abstract"]["matching_ids"]), "arm_A_missed_references": len(probes["arm_A_missed"]),
                    "rescued_by_omitted_mesh_or_pt_lines": probes["rescued_by_omitted_lines"]}
    for st in src["studies"]:
        ids = [refs[r]["openalex_id"] for r in st["ref_ids"] if refs[r]["openalex_id"]]
        for f, v in fac.items():
            rows[st["study_id"]]["facet_" + f] = "" if not ids else int(any(i in v["matching_ids"] for i in ids))
        rows[st["study_id"]]["citation"] = " || ".join(refs[r]["citation"] for r in st["ref_ids"])
    out = list(rows.values())
    with open(ROOT / "results/per_study_retrieval.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    (ROOT / "results/summary.json").write_text(json.dumps(s, indent=1) + "\n")
    print(json.dumps(s, indent=1))


if __name__ == "__main__":
    main()
