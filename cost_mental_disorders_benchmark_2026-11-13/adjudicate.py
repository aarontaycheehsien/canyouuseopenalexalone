"""Offline: apply documented manual adjudications and write results/benchmark_matches.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANUAL = {
    "CM-004": ("W1994862314", "Same article; OpenAlex title adds the subtitle 'An Estimate for New Cases in 1998'."),
    "CM-063": ("W2409636602", "Same article (Psychiatrische Praxis 2001) indexed under its German title; the review gives an English translation."),
    "CM-064": ("W2067570300", "Exact title, journal and year; first-pass score lowered by the citation's missing colon."),
    "CM-068": ("W2474139704", "Same article (Psychiatrische Praxis) indexed under its German title; online 2016, issue 2017."),
    "CM-092": ("W1983592245", "Exact title, journal and year; citation lacks pages."),
    "CM-096": ("W2154819218", "Same article (Gaceta Sanitaria) indexed under its Spanish title; online 2011, issue 2012."),
    "CM-139": ("W16959066", "Same article (Wiener Klinische Wochenschrift 2007) indexed under its German title."),
    "CM-059": ("W1519564083", "Second pass: identical title, 2011, PubMed-sourced record."),
    "CM-088": ("W63887507", "Second pass: identical title, 2014. A second OpenAlex record of the same article (W2186561620) also exists; either counts."),
    "CM-089": ("W1519125454", "Second pass: identical title, 2006, Estudios de Economia Aplicada; OpenAlex's first-author name is wrong."),
    "CM-099": ("W114073249", "Second pass: same title ('Economic burden of schizophrenia ...'), 2012."),
    "CM-137": ("W1911106437", "Second pass: identical title, 2008, Slovenian Medical Journal."),
}
ALTERNATES = {"CM-088": ["W2186561620"]}
NOT_FOUND = {
    "CM-076": "Portuguese university working paper (2003); no OpenAlex record found in either pass.",
    "CM-127": "Danish Ministry of Health report (1999); no OpenAlex record found in either pass.",
}


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
        rec = {"ref_id": r["ref_id"], "citation": s["citation"], "year": s["year"]}
        if r["ref_id"] in NOT_FOUND:
            oid, dec, note = None, "not_in_openalex", NOT_FOUND[r["ref_id"]]
        elif r["status"] == "accepted_auto":
            oid, dec, note = r["openalex_id"], "accepted_auto", None
        else:
            (oid, note), dec = MANUAL[r["ref_id"]], "accepted_manual"
        rec.update(openalex_id=oid, alternate_openalex_ids=ALTERNATES.get(r["ref_id"], []), decision=dec)
        if note:
            rec["note"] = note
        if oid:
            c = allc[oid]
            rec.update(openalex_title=c["title"], openalex_type=c.get("type"), openalex_language=c.get("language"),
                       openalex_publication_date=c.get("publication_date"), is_retracted=c.get("is_retracted"))
        recs.append(rec)
    ids = [r["openalex_id"] for r in recs if r["openalex_id"]]
    out = {"references": len(recs), "in_openalex": len(ids), "distinct_openalex_ids": len(set(ids)),
           "not_in_openalex": [r["ref_id"] for r in recs if not r["openalex_id"]],
           "outside_date_window": [r["ref_id"] for r in recs if r.get("openalex_publication_date") and not ("1980-01-01" <= r["openalex_publication_date"] <= "2019-06-30")],
           "records": recs}
    (ROOT / "results/benchmark_matches.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print({k: v for k, v in out.items() if k != "records"})


if __name__ == "__main__":
    main()
