"""Offline: build results/summary.json and results/per_study_retrieval.csv from archived evidence."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCREENED, DB_SUM, THRESHOLD = 20_183, 13_791, 90  # 90 = smallest whole number above 95% of 94


def main():
    m = json.loads((ROOT / "results/benchmark_matches.json").read_text())
    obs = json.loads((ROOT / "results/run_observations.json").read_text())
    fac = json.loads((ROOT / "results/facet_diagnostics.json").read_text())["facets"]
    recs, n = m["records"], len(m["records"])
    covered = [r for r in recs if r["openalex_id"]]
    summary = {"benchmark": "Dalgaard et al. 2022, doi:10.1002/cl2.1291", "studies": n, "in_openalex": len(covered),
               "openalex_coverage": round(len(covered) / n, 4), "recall_threshold_studies": THRESHOLD,
               "original_screened_all_sources": SCREENED, "database_strategy_results_sum": DB_SUM, "arms": {}}
    for arm, s in obs["arms"].items():
        found = set(s["recovered_ids"])
        k = sum(1 for r in covered if r["openalex_id"] in found)
        e = s["export"]
        summary["arms"][arm] = {
            "api_count": s["count"], "oqo_roundtrip_count_equal": s["count"] == s["oqo_roundtrip_count"],
            "recovered_studies": k, "recall_all_studies": round(k / n, 4), "recall_among_covered": round(k / len(covered), 4),
            "meets_recall_threshold": k >= THRESHOLD, "count_at_most_screened": s["count"] <= SCREENED,
            "count_ratio_to_screened": round(s["count"] / SCREENED, 2),
            "complete_unrestricted_export": bool(e.get("complete")),
            "export_matches_membership": (sorted(e["benchmark_ids_in_export"]) == sorted(found)) if e.get("attempted") else None,
            "evidence": "complete cursor export plus restricted membership" if e.get("complete") else "restricted membership only (count above the 40,000 export cap)"}
    rows = []
    for r in recs:
        oid = r["openalex_id"]
        row = {"study": r["study"], "study_id": r["study_id"], "outlet": r["outlet"], "openalex_id": oid or "",
               "openalex_type": r.get("openalex_type", ""), "in_openalex": int(bool(oid))}
        for arm, s in obs["arms"].items():
            row[arm] = int(bool(oid) and oid in s["recovered_ids"])
        for f, v in fac.items():
            row["facet_" + f] = "" if not oid else int(oid in v["matching_ids"])
        rows.append(row)
    with open(ROOT / "results/per_study_retrieval.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    (ROOT / "results/summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
