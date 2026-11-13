"""Offline: write results/benchmark_matches.json from matching_raw.json (37 included articles).

* 26 auto-accepted (DOI, PMID or title search; citation title agreement >= 0.9).
* CH-033 (Miller 2017, Int J Emerg Serv) accepted from the second pass: the printed PMID belongs to
  a different Miller paper (2018, fire personnel); the title search finds the cited article exactly.
* Not in OpenAlex after both passes (10): six Annals of Emergency Dispatch and Response articles
  (CH-028, -030, -031, -039, -043, -044), J Soc Behav Pers 1997 (CH-022), a Spanish-language report
  (CH-038), a French-language journal article (CH-051), Florida Public Health Review (CH-053).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANUAL = {"CH-033": ("W2598686106", "Second-pass title search: exact title; printed PMID belongs to a different paper.")}
NOT_FOUND = {'CH-022': 'Not in OpenAlex after both passes.', 'CH-028': 'Not in OpenAlex after both passes.', 'CH-030': 'Not in OpenAlex after both passes.', 'CH-031': 'Not in OpenAlex after both passes.', 'CH-038': 'Not in OpenAlex after both passes.', 'CH-039': 'Not in OpenAlex after both passes.', 'CH-043': 'Not in OpenAlex after both passes.', 'CH-044': 'Not in OpenAlex after both passes.', 'CH-051': 'Not in OpenAlex after both passes.', 'CH-053': 'Not in OpenAlex after both passes.'}


def main():
    raw = json.loads((ROOT / "results/matching_raw.json").read_text())
    src = json.loads((ROOT / "results/benchmark_source.json").read_text())
    by = {r["ref_id"]: r for r in src["records"]}
    recs = []
    for r in raw:
        oid, decision, note = r["openalex_id"], r["status"], None
        if r["ref_id"] in MANUAL:
            oid, note = MANUAL[r["ref_id"]]
            decision = "accepted_manual"
        if r["ref_id"] in NOT_FOUND:
            oid, note, decision = None, NOT_FOUND[r["ref_id"]], "not_in_openalex"
        assert decision in ("accepted_auto", "accepted_manual", "not_in_openalex"), (r["ref_id"], decision)
        c = next((c for c in r["candidates"] if c["openalex_id"] == oid), {})
        if oid and not c:
            for p in sorted((ROOT / "archives/matching").glob(f"oa_*_{r['ref_id']}.json")):
                for x in json.loads(p.read_text())["response"].get("results", []):
                    if x["id"].rsplit("/", 1)[-1] == oid:
                        c = {"via": "second_pass", "citation_title_agreement": None, "title": x.get("display_name"), "type": x.get("type"),
                             "language": x.get("language"), "publication_date": x.get("publication_date"), "is_retracted": x.get("is_retracted")}
        recs.append({"ref_id": r["ref_id"], "study_ids": by[r["ref_id"]]["study_ids"], "study_label": r["study_label"],
                     "citation": by[r["ref_id"]]["citation"], "openalex_id": oid, "decision": decision, "note": note,
                     "via": c.get("via"), "citation_title_agreement": c.get("citation_title_agreement"),
                     "openalex_title": c.get("title"), "openalex_type": c.get("type"), "openalex_language": c.get("language"),
                     "openalex_publication_date": c.get("publication_date"), "is_retracted": c.get("is_retracted")})
    ids = [r["openalex_id"] for r in recs if r["openalex_id"]]
    found_studies = sorted({s for r in recs if r["openalex_id"] for s in r["study_ids"]})
    out = {"references": len(recs), "studies": len(src["studies"]), "references_in_openalex": len(ids),
           "distinct_openalex_ids": len(set(ids)), "studies_in_openalex": len(found_studies),
           "outside_date_window": [(r["ref_id"], r["openalex_publication_date"]) for r in recs if r["openalex_id"] and r["openalex_publication_date"] > "2024-01-07"],
           "not_english_in_openalex": [(r["ref_id"], r["openalex_language"]) for r in recs if r["openalex_id"] and r["openalex_language"] not in ("en", None)],
           "not_type_article_in_openalex": [(r["ref_id"], r["openalex_type"]) for r in recs if r["openalex_id"] and r["openalex_type"] != "article"],
           "records": recs}
    (ROOT / "results/benchmark_matches.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print({k: v for k, v in out.items() if k != "records"})


if __name__ == "__main__":
    main()
