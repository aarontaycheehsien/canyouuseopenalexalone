"""Offline: build results/summary.json and results/per_reference_retrieval.csv from archived evidence.

A reference counts as recovered if its OpenAlex record, or a documented alternate
record of the same article, is in the arm's restricted-membership result.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCREENED, THRESHOLD = 13_579, 136  # 136 = smallest whole number above 95% of 143


def main():
    m = json.loads((ROOT / "results/benchmark_matches.json").read_text())
    obs = json.loads((ROOT / "results/run_observations.json").read_text())
    fac = json.loads((ROOT / "results/facet_diagnostics.json").read_text())["facets"]
    recs = m["records"]
    n = len(recs)
    cov = [r for r in recs if r["openalex_id"]]
    keys = lambda r: [r["openalex_id"], *r.get("alternate_openalex_ids", [])] if r["openalex_id"] else []  # noqa: E731
    s = {"benchmark": "Christensen et al. 2020, doi:10.1017/S204579602000075X", "references": n, "in_openalex": len(cov),
         "openalex_coverage": round(len(cov) / n, 4), "recall_threshold": THRESHOLD, "original_screened": SCREENED, "arms": {}}
    rows = {r["ref_id"]: {"ref_id": r["ref_id"], "year": r["year"], "openalex_id": r["openalex_id"] or "",
                          "in_openalex": int(bool(r["openalex_id"])), "openalex_language": r.get("openalex_language") or ""} for r in recs}
    for arm, o in obs["arms"].items():
        found = set(o["recovered_ids"])
        k = 0
        for r in recs:
            hit = any(i in found for i in keys(r))
            rows[r["ref_id"]][arm] = int(hit)
            k += hit
        s["arms"][arm] = {"api_count": o["count"], "oqo_roundtrip_count_equal": o["count"] == o["oqo_roundtrip_count"],
                          "cursor_page2_consistent": o.get("cursor_page2_consistent"), "recovered": k,
                          "recall_all": round(k / n, 4), "recall_among_covered": round(k / len(cov), 4),
                          "meets_recall_threshold": k >= THRESHOLD, "count_at_most_screened": o["count"] <= SCREENED,
                          "ratio_to_screened": round(o["count"] / SCREENED, 2),
                          "complete_unrestricted_export": False,
                          "evidence": "restricted membership of the identical executed OQO; count above the frozen 20,000 export cap"}
    for r in recs:
        for f, v in fac.items():
            rows[r["ref_id"]]["facet_" + f] = "" if not r["openalex_id"] else int(any(i in v["matching_ids"] for i in keys(r)))
        rows[r["ref_id"]]["citation"] = r["citation"]
    out = list(rows.values())
    with open(ROOT / "results/per_reference_retrieval.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    (ROOT / "results/summary.json").write_text(json.dumps(s, indent=1) + "\n")
    print(json.dumps(s, indent=1))


if __name__ == "__main__":
    main()
