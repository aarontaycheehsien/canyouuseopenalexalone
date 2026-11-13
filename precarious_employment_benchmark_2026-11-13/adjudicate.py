"""Offline: write results/benchmark_matches.json from matching_raw.json (48 auto-accepted after citation audit; 2 not in OpenAlex)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    raw = json.loads((ROOT / "results/matching_raw.json").read_text())
    src = {r["ref_id"]: r for r in json.loads((ROOT / "results/benchmark_source.json").read_text())["records"]}
    NOT_FOUND = {"PE-052": "American Sociological Association conference paper (2015); no OpenAlex record in either pass.",
                 "PE-059": "Dissertation cited by its Dissertation Abstracts International volume (2009); no OpenAlex record in either pass."}
    recs = []
    for r in raw:
        c = next((c for c in r["candidates"] if c["openalex_id"] == r["openalex_id"]), {})
        recs.append({"ref_id": r["ref_id"], "study_label": r["study_label"], "citation": src[r["ref_id"]]["citation"],
                     "openalex_id": r["openalex_id"], "decision": "not_in_openalex" if r["ref_id"] in NOT_FOUND else r["status"], "note": NOT_FOUND.get(r["ref_id"]), "via": c.get("via"),
                     "citation_title_agreement": c.get("citation_title_agreement"), "openalex_title": c.get("title"),
                     "openalex_type": c.get("type"), "openalex_language": c.get("language"),
                     "openalex_publication_date": c.get("publication_date"), "is_retracted": c.get("is_retracted")})
    ids = [r["openalex_id"] for r in recs if r["openalex_id"]]
    out = {"studies": len(recs), "in_openalex": len(ids), "distinct_openalex_ids": len(set(ids)),
           "outside_date_window": [r["ref_id"] for r in recs if (r["openalex_publication_date"] or "") > "2019-03-31"],
           "not_english_in_openalex": [r["ref_id"] for r in recs if r["openalex_language"] not in ("en", None)],
           "not_type_article_in_openalex": [(r["ref_id"], r["openalex_type"]) for r in recs if r["openalex_type"] != "article"],
           "records": recs}
    (ROOT / "results/benchmark_matches.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print({k: v for k, v in out.items() if k != "records"})


if __name__ == "__main__":
    main()
