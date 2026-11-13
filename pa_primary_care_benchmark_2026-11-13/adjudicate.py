"""Offline: write results/benchmark_matches.json from matching_raw.json (51 references of 51 studies).

* 46 references auto-accepted (citation title agreement >= 0.9).
* PA-060 (Steptoe 1999) accepted manually: its own DOI resolves to an OpenAlex record that
  merges the trial with an attached commentary (typed "editorial"), lowering agreement.
* PA-044 (Hesselink 2013): the citation text names a Diabetologia conference abstract
  (56:S165), which is not in OpenAlex, but the printed reference carries the DOI and PMID of
  the same trial's full report (BMC Fam Pract 2013;14:184). The identifier-linked record is
  used; scoring the abstract literally (not in OpenAlex) is a sensitivity result.
* Not in OpenAlex after both passes: PA-026 (West Indian Med J 2020 supplement abstract),
  PA-051 (AJRCCM 2013 meeting abstract A5952; other abstracts of the same trial are not
  cited and are not credited), PA-058 (2007 University of South Carolina thesis).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANUAL = {"PA-060": ("W1601229437", "Own DOI resolves; OpenAlex record merges the trial with its commentary ('editorial')."),
          "PA-044": ("W2110439585", "Citation text is a Diabetologia 2013 abstract (not in OpenAlex); the printed DOI/PMID resolve to the same trial's full report, BMC Fam Pract 2013;14:184.")}
NOT_FOUND = {"PA-026": "West Indian Med J 2020;68:44 supplement abstract; no OpenAlex record in either pass.",
             "PA-051": "Am J Respir Crit Care Med 2013;187:A5952 meeting abstract; ATS abstract DOI pattern returns 404; no record in either pass.",
             "PA-058": "Thesis, University of South Carolina, 2007; no OpenAlex record in either pass."}


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
        recs.append({"ref_id": r["ref_id"], "study_ids": by[r["ref_id"]]["study_ids"], "study_label": r["study_label"],
                     "citation": by[r["ref_id"]]["citation"], "openalex_id": oid, "decision": decision, "note": note,
                     "via": c.get("via"), "citation_title_agreement": c.get("citation_title_agreement"),
                     "openalex_title": c.get("title"), "openalex_type": c.get("type"), "openalex_language": c.get("language"),
                     "openalex_publication_date": c.get("publication_date"), "is_retracted": c.get("is_retracted")})
    ids = [r["openalex_id"] for r in recs if r["openalex_id"]]
    found_studies = sorted({s for r in recs if r["openalex_id"] for s in r["study_ids"]})
    out = {"references": len(recs), "studies": len(src["studies"]), "references_in_openalex": len(ids),
           "distinct_openalex_ids": len(set(ids)), "studies_in_openalex": len(found_studies),
           "outside_date_window": [(r["ref_id"], r["openalex_publication_date"]) for r in recs if r["openalex_id"] and r["openalex_publication_date"] > "2021-04-01"],
           "not_english_in_openalex": [(r["ref_id"], r["openalex_language"]) for r in recs if r["openalex_id"] and r["openalex_language"] not in ("en", None)],
           "not_type_article_in_openalex": [(r["ref_id"], r["openalex_type"]) for r in recs if r["openalex_id"] and r["openalex_type"] != "article"],
           "records": recs}
    (ROOT / "results/benchmark_matches.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print({k: v for k, v in out.items() if k != "records"})


if __name__ == "__main__":
    main()
