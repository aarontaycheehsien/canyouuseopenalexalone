"""Offline: build results/summary.json and results/per_reference_retrieval.csv from archived evidence."""
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCREENED, SCREENED_ALL, THRESHOLD = 12_967, 13_096, 158  # 158 = smallest whole number above 95% of 166


def group(labels):
    return "DB_only" if labels == ["DB"] else ("DB_and_N" if "DB" in labels else "N_only")


def main():
    m = json.loads((ROOT / "results/benchmark_matches.json").read_text())
    obs = json.loads((ROOT / "results/run_observations.json").read_text())
    fac = json.loads((ROOT / "results/facet_diagnostics.json").read_text())["facets"]
    den = [r for r in m["records"] if r["decision"] != "excluded_not_a_reference"]
    n, cov = len(den), [r for r in den if r["openalex_id"]]
    s = {"benchmark": "Meissle, Naranjo & Romeis 2022, doi:10.1186/s13750-022-00272-0", "references": n,
         "in_openalex": len(cov), "openalex_coverage": round(len(cov) / n, 4), "recall_threshold": THRESHOLD,
         "screened_database_after_dedup": SCREENED, "screened_all_sources": SCREENED_ALL, "arms": {}}
    for arm, o in obs["arms"].items():
        found = set(o["recovered_ids"])
        k = sum(1 for r in cov if r["openalex_id"] in found)
        by = defaultdict(lambda: [0, 0, 0])
        for r in den:
            g = by[group(r["labels"])]
            g[0] += 1; g[1] += bool(r["openalex_id"]); g[2] += bool(r["openalex_id"] and r["openalex_id"] in found)
        e = o["export"]
        s["arms"][arm] = {"api_count": o["count"], "oqo_roundtrip_count_equal": o["count"] == o["oqo_roundtrip_count"],
                          "cursor_page2_consistent": o.get("cursor_page2_consistent"),
                          "recovered": k, "recall_all": round(k / n, 4), "recall_among_covered": round(k / len(cov), 4),
                          "meets_recall_threshold": k >= THRESHOLD, "count_at_most_screened": o["count"] <= SCREENED,
                          "ratio_to_screened": round(o["count"] / SCREENED, 3),
                          "complete_unrestricted_export": bool(e.get("complete")),
                          "export_matches_membership": sorted(e.get("benchmark_ids_in_export", [])) == sorted(found) if e.get("attempted") else None,
                          "by_source_label": {g: {"references": v[0], "in_openalex": v[1], "recovered": v[2]} for g, v in sorted(by.items())}}
    rows = []
    for r in den:
        oid = r["openalex_id"]
        row = {"ref_id": r["ref_id"], "labels": " ".join(r["labels"]), "group": group(r["labels"]), "year": r["year"],
               "openalex_id": oid or "", "openalex_type": r.get("openalex_type") or "", "in_openalex": int(bool(oid))}
        for arm, o in obs["arms"].items():
            row[arm] = int(bool(oid) and oid in o["recovered_ids"])
        for f, v in fac.items():
            row["facet_" + f] = "" if not oid else int(oid in v["matching_ids"])
        row["citation"] = r["citation"]
        rows.append(row)
    with open(ROOT / "results/per_reference_retrieval.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    (ROOT / "results/summary.json").write_text(json.dumps(s, indent=1) + "\n")
    print(json.dumps(s, indent=1))


if __name__ == "__main__":
    main()
