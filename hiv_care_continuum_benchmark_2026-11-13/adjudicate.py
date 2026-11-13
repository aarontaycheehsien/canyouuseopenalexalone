"""Offline: write results/benchmark_matches.json from matching_raw.json.

189 matches auto-accepted (citation title agreement >= 0.9); one accepted manually after
audit: HIV-214 (Zijenah 2022) resolves by the reference's own DOI, and its lower agreement
(0.838) comes only from the spacing of "Option B+Combination" against "Option B + Combination".

One reference-list error is corrected: Table S3 lists "Dunlop 2022" (retention; South Africa; urban;
2004-2018; 168 months; n = 7630), but its paired reference, no. 98, is Dunlop, Darougar and Treharne
(1980) on chlamydia serotypes. The intended article is Dunlop, Lilian, Tait et al. (2022), S Afr Med J,
on the Johannesburg paediatric HIV programme 2004-2018 (archives/matching/correction_*.json). The
cited 1980 record is kept as a sensitivity result in the summary.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANUAL = {"HIV-098": ("W4229335117", "Reference-list error: ref 98 is a 1980 chlamydia paper (W2021119369). Table S3 attributes (South Africa, urban, 2004-2018, 168 months, n=7630) identify Dunlop et al. 2022, S Afr Med J, doi:10.7196/samj.2022.v112i5.16277."),
          "HIV-214": ("W4224226383", "Reference DOI resolves to this record; same authors, journal and year. Agreement below 0.9 only from spacing around '+' in the title.")}


def main():
    raw = json.loads((ROOT / "results/matching_raw.json").read_text())
    src = {r["ref_id"]: r for r in json.loads((ROOT / "results/benchmark_source.json").read_text())["records"]}
    recs = []
    for r in raw:
        oid, note, decision = r["openalex_id"], None, r["status"]
        if r["ref_id"] in MANUAL:
            oid, note = MANUAL[r["ref_id"]]
            decision = "accepted_manual"
        c = next((c for c in r["candidates"] if c["openalex_id"] == oid), {})
        if r["ref_id"] == "HIV-098":
            x = json.loads((ROOT / "archives/matching/correction_doi_HIV-098.json").read_text())["response"]
            c = {"via": "reference_list_error_corrected", "citation_title_agreement": None, "title": x["display_name"], "type": x["type"],
                 "language": x["language"], "publication_date": x["publication_date"], "is_retracted": x["is_retracted"]}
            decision = "corrected_reference_error"
            cited_as = r["openalex_id"]
        recs.append({"ref_id": r["ref_id"], "study_label": r["study_label"], "citation": src[r["ref_id"]]["citation"],
                     "openalex_id": oid, "decision": decision, "note": note, "via": c.get("via"),
                     "citation_title_agreement": c.get("citation_title_agreement"), "openalex_title": c.get("title"),
                     "openalex_type": c.get("type"), "openalex_language": c.get("language"),
                     "openalex_publication_date": c.get("publication_date"), "is_retracted": c.get("is_retracted"),
                     **({"cited_reference_openalex_id": cited_as} if r["ref_id"] == "HIV-098" else {})})
    assert all(r["openalex_id"] for r in recs)
    ids = [r["openalex_id"] for r in recs]
    out = {"studies": len(recs), "in_openalex": len(ids), "distinct_openalex_ids": len(set(ids)),
           "outside_date_window": [(r["ref_id"], r["openalex_publication_date"]) for r in recs
                                   if not "2010-01-01" <= (r["openalex_publication_date"] or "") <= "2023-06-01"],
           "not_english_in_openalex": [(r["ref_id"], r["openalex_language"]) for r in recs if r["openalex_language"] not in ("en", None)],
           "not_type_article_in_openalex": [(r["ref_id"], r["openalex_type"]) for r in recs if r["openalex_type"] != "article"],
           "records": recs}
    (ROOT / "results/benchmark_matches.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print({k: v for k, v in out.items() if k != "records"})


if __name__ == "__main__":
    main()
