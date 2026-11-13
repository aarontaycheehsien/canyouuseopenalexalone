"""Offline: write results/benchmark_matches.json from matching_raw.json (55 included RCTs, titles
from Additional File 3; matched by OpenAlex title search).

* 52 auto-accepted (citation title agreement >= 0.9).
* VR-07 (Brunner 2017, VIRTUES) accepted manually: the multicentre RCT (Neurology 2017), not the
  2014 protocol that shares its title.
* VR-42 (Reinkensmeyer 2012, Pneu-WREX) found in the second pass (archives/matching/oa_*_VR-42.json).
* VR-31 (Li 2021) not identifiable: its title in Additional File 3 is truncated to
  "...ystem on Patients with Stroke: Randomized Controlled Trial", and no candidate matched.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANUAL = {"VR-07": ("W2769477662", "Multicentre RCT (2017), not the 2014 protocol of the same title."),
          "VR-42": ("W313823884", "Second-pass title search; same title, first author and year.")}
NOT_FOUND = {"VR-31": "Title truncated in Additional File 3; not identifiable."}


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
           "outside_date_window": [(r["ref_id"], r["openalex_publication_date"]) for r in recs if r["openalex_id"] and r["openalex_publication_date"] > "2023-03-31"],
           "not_english_in_openalex": [(r["ref_id"], r["openalex_language"]) for r in recs if r["openalex_id"] and r["openalex_language"] not in ("en", None)],
           "not_type_article_in_openalex": [(r["ref_id"], r["openalex_type"]) for r in recs if r["openalex_id"] and r["openalex_type"] != "article"],
           "records": recs}
    (ROOT / "results/benchmark_matches.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print({k: v for k, v in out.items() if k != "records"})


if __name__ == "__main__":
    main()
