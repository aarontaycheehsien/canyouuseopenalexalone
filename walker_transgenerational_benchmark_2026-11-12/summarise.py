"""Offline: build results/summary.json and results/per_reference_retrieval.csv from archived evidence."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCREENED = 63_754
THRESHOLD = 245  # smallest whole number strictly above 95% of 257


def main():
    m = json.loads((ROOT / "results/benchmark_matches.json").read_text())
    obs = json.loads((ROOT / "results/run_observations.json").read_text())
    pub = {r["ref_id"]: r for r in json.loads((ROOT / "results/pubmed_strategy_rerun.json").read_text())["rows"]}
    syn = json.loads((ROOT / "results/secondary_synergy_overlap.json").read_text())
    recs = m["records"]
    summary = {"benchmark": "Walker et al. 2018, doi:10.1016/j.envint.2017.12.032", "references": len(recs),
               "matched_references": sum(1 for r in recs if r["openalex_id"]), "distinct_openalex_works": m["distinct_openalex_ids"],
               "original_title_abstract_screened": SCREENED, "recall_threshold_references": THRESHOLD, "arms": {}}
    rows = []
    for arm, s in obs["arms"].items():
        found = set(s["recovered_ids"])
        refs = sum(1 for r in recs if r["openalex_id"] in found)
        summary["arms"][arm] = {
            "api_count": s["count"], "oqo_roundtrip_count_equal": s["count"] == s["oqo_roundtrip_count"],
            "recovered_references": refs, "recall_references": round(refs / len(recs), 4),
            "recovered_distinct_works": len(found), "recall_distinct_works": round(len(found) / m["distinct_openalex_ids"], 4),
            "meets_recall_threshold": refs >= THRESHOLD, "count_below_original_screened": s["count"] <= SCREENED,
            "count_ratio_to_original_screened": round(s["count"] / SCREENED, 2),
            "evidence": "benchmark-restricted membership of the identical executed OQO; complete export not attempted (count above the frozen 40,000 cap)",
            "complete_unrestricted_export": False,
            "synergy_set_overlap": syn["arms"][arm]["overlap_with_set"]}
    summary["synergy_set_works_resolving_today"] = syn["set_works_resolving_today"]
    summary["published_pubmed_strategy_rerun_today_references"] = sum(1 for r in pub.values() if r["pubmed_strategy_today"])
    A = set(obs["arms"]["A_faithful_title_abstract"]["recovered_ids"])
    B = set(obs["arms"]["B_title_abstract_keywords"]["recovered_ids"])
    summary["A_equals_B_membership"] = A == B
    for r in recs:
        rows.append({"ref_id": r["ref_id"], "stream": r["stream"], "year": r["year"], "openalex_id": r["openalex_id"],
                     "match_decision": r["decision"], "via": r["via"], "A_faithful_title_abstract": int(r["openalex_id"] in A),
                     "B_title_abstract_keywords": int(r["openalex_id"] in B),
                     "pubmed_strategy_rerun_2026_11_12": int(pub[r["ref_id"]]["pubmed_strategy_today"]),
                     "source_title": r["source_title"]})
    with open(ROOT / "results/per_reference_retrieval.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    (ROOT / "results/summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
