"""Noetel holdout: match the 218 supplied citations to OpenAlex works (network; archived).

    python3 noetel_match.py /path/to/references.csv      # writes results/noetel_source.json, noetel_matches.json

Order (12 November protocol): DOI, then PMID (numeric accession number), then title search.
A DOI or PMID match is accepted only if the returned work's title agrees with the citation
(normalised similarity >= 0.80); a title-search match needs similarity >= 0.93, publication year
within one year when the citation gives one, and the first author's surname in the byline.
Anything else is left for adjudication (results/noetel_adjudication.json), and unmatched rows stay
in the denominator. Abstracts are not copied into the repository.
"""
import csv
import difflib
import json
import re
import sys
import unicodedata
from pathlib import Path

import netlib

ROOT = Path(__file__).resolve().parent
API = "https://api.openalex.org"
SEL = "id,doi,title,publication_year,authorships,ids"


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s).split())


def sim(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def doi_of(s):
    m = re.search(r"10\.\d{4,9}/\S+", s or "")
    return m.group(0).rstrip(".").lower() if m else None


def work(key):
    st, r = netlib.get("noetel_match", f"{API}/works/{key}", {"select": SEL})
    return r if st == 200 else None


def surname(authors):
    first = (authors or "").split(";")[0]
    return norm(first.split(",")[0]).split(" ")[-1] if first else ""


def byline_has(w, sn):
    return any(sn and sn in norm(a["author"]["display_name"]) for a in w.get("authorships", []))


def main(csv_path):
    rows = list(csv.DictReader(open(csv_path, encoding="utf-8-sig", errors="replace")))
    source, recs = [], []
    for i, r in enumerate(rows):
        c = {"row": i + 1, "covidence": r["Covidence #"], "study": r["Study"], "title": r["Title"],
             "first_author": (r["Authors"] or "").split(";")[0].strip(), "year": r["Published Year"],
             "journal": r["Journal"], "doi": doi_of(r["DOI"]), "accession": r["Accession Number"].strip()}
        source.append(c)
        rec = {"row": c["row"], "openalex_id": None, "method": None, "title_similarity": None, "decision": "unmatched", "candidates": []}
        tried = []
        if c["doi"]:
            tried.append(("doi", f"doi:{c['doi']}"))
        if re.fullmatch(r"\d{6,9}", c["accession"]):
            tried.append(("pmid", f"pmid:{c['accession']}"))
        for method, key in tried:
            w = work(key)
            if w:
                s = sim(c["title"], w["title"])
                rec["candidates"].append({"id": w["id"].rsplit("/", 1)[-1], "via": method, "title": w["title"],
                                          "year": w["publication_year"], "similarity": round(s, 3)})
                if s >= 0.80:
                    rec.update(openalex_id=w["id"].rsplit("/", 1)[-1], method=method, title_similarity=round(s, 3), decision="accepted_auto")
                    break
        if not rec["openalex_id"]:
            q = norm(c["title"])[:250]
            st, res = netlib.get("noetel_match", f"{API}/works", {"search": q, "per_page": 5, "select": SEL})
            sn = surname(r["Authors"])
            for w in (res or {}).get("results", []) if st == 200 else []:
                s = sim(c["title"], w["title"])
                yr_ok = not c["year"] or (w["publication_year"] and abs(int(c["year"]) - w["publication_year"]) <= 1)
                cand = {"id": w["id"].rsplit("/", 1)[-1], "via": "title_search", "title": w["title"], "year": w["publication_year"],
                        "similarity": round(s, 3), "year_ok": bool(yr_ok), "author_ok": byline_has(w, sn)}
                rec["candidates"].append(cand)
                if s >= 0.93 and yr_ok and cand["author_ok"] and not rec["openalex_id"]:
                    rec.update(openalex_id=cand["id"], method="title_search", title_similarity=cand["similarity"], decision="accepted_auto")
        if not rec["openalex_id"] and rec["candidates"]:
            rec["decision"] = "needs_adjudication"
        recs.append(rec)
    (ROOT / "results/noetel_source.json").write_text(json.dumps({"citations": source}, indent=1) + "\n")
    (ROOT / "results/noetel_matches_auto.json").write_text(json.dumps({"records": recs}, indent=1) + "\n")
    from collections import Counter
    print(Counter((r["decision"], r["method"]) for r in recs))


if __name__ == "__main__":
    main(sys.argv[1])
