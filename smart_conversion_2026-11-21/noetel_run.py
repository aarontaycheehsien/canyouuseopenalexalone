"""Noetel holdout, stage 1 (network; archived): before references.csv is opened, record each arm's
unrestricted count and first 200 results, as the 12 November protocol specifies.

    python3 noetel_run.py stage1
    python3 noetel_run.py stage2     # after matching: ID-restricted membership and scoring
"""
import json
import sys
from pathlib import Path

import netlib

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
EX = REPO / "exercise_transfer_benchmark_2026-11-12"
ARMS = {"A_fuller_source_concepts": EX / "queries/A_fuller_source_concepts.oql",
        "B_compact_three_concepts": EX / "queries/B_compact_three_concepts.oql",
        "S_smart": ROOT / "queries/noetel_exercise__S_smart.oql"}
SCREENED, CITATIONS = 13115, 218


def stage1():
    out = {}
    for arm, p in ARMS.items():
        oql = p.read_text().strip()
        st, r = netlib.post("noetel_first_page", "https://api.openalex.org/", {"oql": oql, "per_page": 200, "select": "id"})
        assert st == 200, (st, r)
        out[arm] = {"count": r["meta"]["count"], "first_page_ids": [x["id"].rsplit("/", 1)[-1] for x in r["results"]]}
        print(arm, out[arm]["count"], flush=True)
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results/noetel_stage1.json").write_text(json.dumps(out, indent=1) + "\n")


def stage2():
    m = json.loads((ROOT / "results/noetel_matches.json").read_text())
    rows = m["records"]
    ids = sorted({r["openalex_id"] for r in rows if r["openalex_id"]})
    res = {"citations": CITATIONS, "matched_citations": sum(1 for r in rows if r["openalex_id"]),
           "unique_matched_works": len(ids), "threshold": 208, "screened": SCREENED, "arms": {}}
    for arm, p in ARMS.items():
        oql = p.read_text().strip()
        found = set()
        for k in range(0, len(ids), 100):
            batch = ids[k:k + 100]
            st, r = netlib.post("noetel_membership", "https://api.openalex.org/",
                                {"oql": oql + " and openalex id is (" + " or ".join(batch) + ")", "per_page": 100, "select": "id"})
            assert st == 200, (st, r)
            got = {x["id"].rsplit("/", 1)[-1] for x in r["results"]}
            assert r["meta"]["count"] == len(got) and got <= set(batch)
            found |= got
        rec = sum(1 for r in rows if r["openalex_id"] in found)
        cnt = json.loads((ROOT / "results/noetel_stage1.json").read_text())[arm]["count"]
        res["arms"][arm] = {"count": cnt, "citations_recovered": rec, "recall_all_citations": round(rec / CITATIONS, 4),
                            "recall_matched_citations": round(rec / res["matched_citations"], 4),
                            "meets_threshold": rec >= 208, "count_at_most_screened": cnt <= SCREENED,
                            "recovered_ids": sorted(found)}
        print(f"{arm:28s} {rec}/{CITATIONS} @ {cnt:,}", flush=True)
    (ROOT / "results/noetel_results.json").write_text(json.dumps(res, indent=1) + "\n")


if __name__ == "__main__":
    {"stage1": stage1, "stage2": stage2}[sys.argv[1]]()
