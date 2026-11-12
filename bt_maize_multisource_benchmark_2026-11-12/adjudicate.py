"""Offline: apply documented manual adjudications and write results/benchmark_matches.json."""
import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANUAL = {
    "BT-604": ("W2110264982", "Crossref DOI; same title and journal; OpenAlex dates the 2012 online version, citation gives the 2014 issue."),
    "BT-658": ("W2507343013", "Exact title and journal; online 2016, issue 2018."),
    "BT-962": ("W2901074737", "Same article indexed under its Spanish title in Temas Agrarios 2018; the review gives an English translation."),
    "BT-600": ("W1129058325", "Second pass: RWTH Aachen dissertation with the identical German title; the review appends an English translation."),
    "BT-612": ("W3005875314", "University of Potsdam dissertation with the identical German title (the review appends an English translation). Surfaced by the second-pass search for BT-652, not BT-612's own."),
    "BT-617": ("W2336681352", "Second pass: identical title, 2003, Bollettino di Zoologia Agraria (hosted by Riviste UNIMI)."),
}
REJECTED_AUTO = {
    "BT-904": "Auto-accept rejected on audit: the candidate is Part 3 (wet season, 2016), the review cites Part 2 (dry season, 2012). Part 2 not found in a further search.",
    "BT-911": "Auto-accept rejected on audit: the candidate is a 2023 soybean study; the review cites a 2011 maize study (truncated title matched). Not found in a further search.",
}
ARTIFACT = {"BT-924": "Legend text from Additional file 2 ('References excluded at the full text stage are labelled with EX...') parsed as an entry. Removing it leaves 46 N-only entries and 166 in total, matching the article."}


def main():
    raw = json.loads((ROOT / "results/matching_raw.json").read_text())
    src = {r["ref_id"]: r for r in json.loads((ROOT / "results/benchmark_source.json").read_text())["records"]}
    allc = {}
    for r in raw:
        for c in r["candidates"] + r.get("second_pass_candidates", []):
            allc.setdefault(c["openalex_id"], c)
    recs = []
    for r in raw:
        s = src[r["ref_id"]]
        rec = {"ref_id": r["ref_id"], "labels": s["labels"], "database_codes": s.get("database_codes"),
               "source_title": s["title"], "year": s["year"], "citation": s["citation"]}
        if r["ref_id"] in ARTIFACT:
            rec.update(openalex_id=None, decision="excluded_not_a_reference", note=ARTIFACT[r["ref_id"]])
            recs.append(rec)
            continue
        if r["ref_id"] in REJECTED_AUTO:
            oid, dec, note = None, "not_in_openalex", REJECTED_AUTO[r["ref_id"]]
        elif r["status"] == "accepted_auto":
            oid, dec, note = r["openalex_id"], "accepted_auto", None
        elif r["ref_id"] in MANUAL:
            (oid, note), dec = MANUAL[r["ref_id"]], "accepted_manual"
        else:
            oid, dec, note = None, "not_in_openalex", "No adequate candidate after Crossref, PubMed, OpenAlex title search and a broader second pass; candidates kept in matching_raw.json."
        rec.update(openalex_id=oid, decision=dec)
        if note:
            rec["note"] = note
        if oid:
            c = allc[oid]
            rec.update(openalex_title=c["title"], openalex_type=c["type"], openalex_language=c.get("language"),
                       openalex_source=c["source"], openalex_publication_date=c["publication_date"],
                       is_retracted=c.get("is_retracted"))
        recs.append(rec)
    den = [r for r in recs if r["decision"] != "excluded_not_a_reference"]
    ids = [r["openalex_id"] for r in den if r["openalex_id"]]
    grp = lambda r: "DB_only" if r["labels"] == ["DB"] else ("DB_and_N" if "DB" in r["labels"] else "N_only")  # noqa: E731
    out = {"denominator": len(den), "in_openalex": len(ids), "distinct_openalex_ids": len(set(ids)),
           "many_to_one": {i: [r["ref_id"] for r in den if r["openalex_id"] == i] for i in sorted(set(ids)) if ids.count(i) > 1},
           "not_in_openalex": [r["ref_id"] for r in den if not r["openalex_id"]],
           "openalex_date_after_ceiling": [r["ref_id"] for r in den if (r.get("openalex_publication_date") or "") > "2019-08-23"],
           "label_composition": dict(collections.Counter(grp(r) for r in den)),
           "records": recs}
    (ROOT / "results/benchmark_matches.json").write_text(json.dumps(out, indent=1) + "\n")
    print({k: v for k, v in out.items() if k != "records"})


if __name__ == "__main__":
    main()
