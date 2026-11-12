"""Match the 257 included references to OpenAlex works. Explicit live runner.

Route per reference, all responses archived under archives/matching/:
  1. NCBI ECitMatch (journal, year, volume, first page, first author) -> PMID.
  2. If no PMID: PubMed esearch on the title words with the year -> candidate PMIDs.
  3. If still none: Crossref bibliographic query -> candidate DOIs.
  4. OpenAlex single-entity lookup by PMID or DOI (free endpoint).
Every candidate is scored by title similarity; acceptance rules are applied in
adjudicate(), and anything not auto-accepted is left for manual adjudication in
results/matching_adjudication.json. Re-running reuses archived responses.
"""
import difflib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARCH = ROOT / "archives" / "matching"
UA = "OpenAlex-transfer-benchmark/1.0 (systematic-review search evaluation)"


def now():
    return datetime.now(timezone.utc).isoformat()


def get(label, url, parse_json=True):
    dest = ARCH / (label + ".json")
    if dest.exists():
        old = json.loads(dest.read_text())
        if old["status"] == 200:
            return old["response"]
    headers = {"User-Agent": UA}
    for attempt in range(4):
        started = now()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as r:
                status, raw = r.status, r.read().decode()
        except urllib.error.HTTPError as e:
            status, raw = e.code, e.read().decode(errors="replace")
        except OSError as e:
            status, raw = 0, json.dumps({"transport_error": type(e).__name__})
        if status not in (0, 429, 500, 502, 503) :
            break
        time.sleep(2 + 3 * attempt)
    try:
        resp = json.loads(raw) if parse_json else raw
    except ValueError:
        resp = {"non_json_response": raw[:2000]}
    dest.parent.mkdir(parents=True, exist_ok=True)
    # API keys are never placed in URLs by this script.
    dest.write_text(json.dumps({"url": url, "requested_utc": started, "status": status, "response": resp}, indent=1))
    time.sleep(0.35)
    return resp if status == 200 else None


def norm(t):
    t = re.sub(r"<[^>]+>", " ", t or "").lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def sim(a, b):
    return round(difflib.SequenceMatcher(None, norm(a), norm(b)).ratio(), 3)


OA_FIELDS = "id,doi,display_name,publication_date,publication_year,ids,type,authorships,primary_location,is_retracted"


def openalex(label, key):
    r = get(label, f"https://api.openalex.org/works/{key}?select={OA_FIELDS}")
    if r and r.get("id"):
        return {"openalex_id": r["id"].rsplit("/", 1)[-1], "doi": r.get("doi"), "pmid": (r.get("ids") or {}).get("pmid"),
                "title": r.get("display_name"), "publication_date": r.get("publication_date"), "type": r.get("type"),
                "first_author": ((r.get("authorships") or [{}])[0].get("author") or {}).get("display_name"),
                "source": ((r.get("primary_location") or {}).get("source") or {}).get("display_name"),
                "is_retracted": r.get("is_retracted")}
    return None


def ecitmatch(rows):
    lines = []
    for r in rows:
        if r["volume"] and r["first_page"]:
            first = r["authors"].split(",")[0].strip()
            j = r["journal"].replace("|", " ")
            lines.append(f"{j}|{r['year']}|{r['volume']}|{r['first_page']}|{first}|{r['ref_id']}|")
    found = {}
    for i in range(0, len(lines), 50):
        batch = "\r".join(lines[i:i + 50])
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/ecitmatch.cgi?db=pubmed&retmode=xml&bdata=" + urllib.parse.quote(batch)
        raw = get(f"ecitmatch_{i // 50:02d}", url, parse_json=False) or ""
        for line in raw.splitlines():
            p = line.split("|")
            if len(p) >= 7 and p[6].strip().isdigit():
                found[p[5]] = p[6].strip()
    return found


def esearch_title(r):
    words = [w for w in norm(r["title"]).split() if len(w) > 3][:12]
    term = " AND ".join(f"{w}[ti]" for w in words) + f" AND {r['year']}[dp]"
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax=5&term=" + urllib.parse.quote(term)
    res = get(f"esearch_{r['ref_id']}", url) or {}
    return (res.get("esearchresult") or {}).get("idlist", [])


def crossref(r):
    q = urllib.parse.quote(f"{r['title']} {r['authors'].split(',')[0]} {r['year']}")
    res = get(f"crossref_{r['ref_id']}", f"https://api.crossref.org/works?rows=3&query.bibliographic={q}") or {}
    return [i.get("DOI") for i in (res.get("message") or {}).get("items", []) if i.get("DOI")]


def adjudicate(r, cand):
    """Auto-accept only strong agreement; everything else goes to manual review."""
    s = sim(r["title"], cand["title"])
    year_ok = (cand.get("publication_date") or "")[:4] in {r["year"], str(int(r["year"]) - 1), str(int(r["year"]) + 1)}
    author_ok = norm(r["authors"].split(",")[0].split()[0]) in norm(cand.get("first_author") or "") if r["authors"] else False
    if s >= 0.9 and year_ok:
        return "accepted_auto", s
    if s >= 0.75 and year_ok and author_ok:
        return "accepted_auto", s
    return "needs_manual", s


def main():
    src = json.loads((ROOT / "results" / "benchmark_source.json").read_text())["records"]
    pmids = ecitmatch(src)
    out = []
    for r in src:
        route, cands = None, []
        if r["ref_id"] in pmids:
            route = "ecitmatch_pmid"
            c = openalex(f"oa_pmid_{r['ref_id']}", f"pmid:{pmids[r['ref_id']]}")
            if c:
                cands.append({**c, "via": f"pmid:{pmids[r['ref_id']]}"})
        if not cands:
            for p in esearch_title(r)[:3]:
                c = openalex(f"oa_pmid_{r['ref_id']}_{p}", f"pmid:{p}")
                if c:
                    route = "esearch_title_pmid"
                    cands.append({**c, "via": f"pmid:{p}"})
        if not cands or max(sim(r["title"], c["title"]) for c in cands) < 0.75:
            for d in crossref(r)[:3]:
                c = openalex(f"oa_doi_{r['ref_id']}_{re.sub(r'[^A-Za-z0-9]+', '_', d)[:60]}", "doi:" + d)
                if c:
                    route = route or "crossref_doi"
                    cands.append({**c, "via": f"doi:{d}"})
        decided = None
        for c in sorted(cands, key=lambda c: -sim(r["title"], c["title"])):
            status, s = adjudicate(r, c)
            c["title_similarity"] = s
            if status == "accepted_auto" and decided is None:
                decided = c
        out.append({"ref_id": r["ref_id"], "stream": r["stream"], "source_title": r["title"], "year": r["year"],
                    "route": route, "candidates": cands,
                    "status": "accepted_auto" if decided else ("needs_manual" if cands else "no_candidate"),
                    "openalex_id": decided["openalex_id"] if decided else None})
        print(r["ref_id"], out[-1]["status"], out[-1]["openalex_id"], flush=True)
    (ROOT / "results" / "matching_raw.json").write_text(json.dumps(out, indent=1) + "\n")
    from collections import Counter
    print(Counter(o["status"] for o in out))


if __name__ == "__main__":
    main()
