"""Match the included references to OpenAlex. Explicit live runner.

Routes, all responses archived under archives/matching/:
  1. Crossref bibliographic query on the full citation -> candidate DOIs.
  2. PubMed title-word search with the year -> candidate PMIDs.
  3. OpenAlex title search (needs the key; costs search credits).
  Every DOI/PMID candidate is resolved by a free OpenAlex single-entity lookup.
Candidates are scored by title similarity, year and first author; anything not
auto-accepted is left for manual adjudication. Re-runs reuse archives.
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
sys.path.insert(0, str(ROOT.parent))
import pilot_credentials  # noqa: E402

ARCH = ROOT / "archives" / "matching"
UA = "OpenAlex-transfer-benchmark/1.0 (systematic-review search evaluation)"
OA_FIELDS = "id,doi,display_name,publication_date,ids,type,authorships,primary_location,is_retracted,language"


def now():
    return datetime.now(timezone.utc).isoformat()


def get(label, url, auth=False):
    dest = ARCH / (label + ".json")
    if dest.exists():
        old = json.loads(dest.read_text())
        if old["status"] == 200:
            return old["response"]
    headers = {"User-Agent": UA}
    if auth:
        headers["Authorization"] = "Bearer " + os.environ["OPENALEX_API_KEY"]
    for attempt in range(4):
        started = now()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as r:
                status, raw = r.status, r.read().decode()
        except urllib.error.HTTPError as e:
            status, raw = e.code, e.read().decode(errors="replace")
        except OSError as e:
            status, raw = 0, json.dumps({"transport_error": type(e).__name__})
        if status not in (0, 429, 500, 502, 503):
            break
        time.sleep(2 + 3 * attempt)
    try:
        resp = json.loads(raw)
    except ValueError:
        resp = {"non_json_response": raw[:2000]}
    if isinstance(resp, dict) and "message" in resp and isinstance(resp["message"], dict):
        for it in resp["message"].get("items", []):
            it.pop("abstract", None)  # publisher abstracts are not archived
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({"url": url, "requested_utc": started, "status": status, "response": resp}, indent=1))
    time.sleep(0.25)
    return resp if status == 200 else None


def norm(t):
    t = re.sub(r"<[^>]+>", " ", t or "").lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def sim(a, b):
    a, b = norm(a), norm(b)
    full = difflib.SequenceMatcher(None, a, b).ratio()
    pre = difflib.SequenceMatcher(None, a, b[:len(a) + 5]).ratio() if len(b) > len(a) else 0
    return round(max(full, pre), 3)


def slim(r):
    return {"openalex_id": r["id"].rsplit("/", 1)[-1], "doi": r.get("doi"), "pmid": (r.get("ids") or {}).get("pmid"),
            "title": r.get("display_name"), "publication_date": r.get("publication_date"), "type": r.get("type"),
            "language": r.get("language"),
            "first_author": ((r.get("authorships") or [{}])[0].get("author") or {}).get("display_name"),
            "source": ((r.get("primary_location") or {}).get("source") or {}).get("display_name"),
            "is_retracted": r.get("is_retracted")}


def oa_single(label, key):
    r = get(label, f"https://api.openalex.org/works/{key}?select={OA_FIELDS}")
    return slim(r) if r and r.get("id") else None


def decide(r, c):
    s = sim(r["title"], c["title"])
    y = (c.get("publication_date") or "")[:4]
    year_ok = bool(r["year"]) and y.isdigit() and abs(int(y) - int(r["year"])) <= 1
    first = norm(r["authors"].split(",")[0].split()[0]) if r["authors"] else ""
    author_ok = bool(first) and first in norm(c.get("first_author") or "")
    if s >= 0.9 and (year_ok or author_ok):
        return "accepted_auto", s
    if s >= 0.8 and year_ok and author_ok:
        return "accepted_auto", s
    return "needs_manual", s


def main():
    pilot_credentials.load_key()
    src = json.loads((ROOT / "results" / "benchmark_source.json").read_text())["records"]
    out = []
    for r in src:
        cands = {}
        q = urllib.parse.quote(r["citation"][:400])
        cr = get(f"crossref_{r['ref_id']}", f"https://api.crossref.org/works?rows=3&query.bibliographic={q}") or {}
        for it in (cr.get("message") or {}).get("items", []):
            if it.get("DOI"):
                c = oa_single(f"oa_doi_{r['ref_id']}_{re.sub(r'[^A-Za-z0-9]+', '_', it['DOI'])[:60]}", "doi:" + it["DOI"])
                if c:
                    cands[c["openalex_id"]] = {**c, "via": "crossref_doi:" + it["DOI"]}
        best = max([sim(r["title"], c["title"]) for c in cands.values()] or [0])
        if best < 0.9:
            words = [w for w in norm(r["title"]).split() if len(w) > 3][:10]
            if words:
                term = " AND ".join(f"{w}[ti]" for w in words) + (f" AND {r['year']}[dp]" if r["year"] else "")
                es = get(f"esearch_{r['ref_id']}", "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax=3&term=" + urllib.parse.quote(term)) or {}
                for p in (es.get("esearchresult") or {}).get("idlist", []):
                    c = oa_single(f"oa_pmid_{r['ref_id']}_{p}", "pmid:" + p)
                    if c:
                        cands.setdefault(c["openalex_id"], {**c, "via": "pubmed_pmid:" + p})
        best = max([sim(r["title"], c["title"]) for c in cands.values()] or [0])
        if best < 0.9:
            t = re.sub(r"[^\w\s-]", " ", r["title"])[:250]
            res = get(f"oa_titlesearch_{r['ref_id']}", "https://api.openalex.org/works?per_page=5&select=" + OA_FIELDS +
                      "&filter=" + urllib.parse.quote("title.search:" + t), auth=True) or {}
            for x in res.get("results", []):
                c = slim(x)
                cands.setdefault(c["openalex_id"], {**c, "via": "openalex_title_search"})
        accepted = None
        for c in sorted(cands.values(), key=lambda c: -sim(r["title"], c["title"])):
            st, s = decide(r, c)
            c["title_similarity"] = s
            if st == "accepted_auto" and accepted is None:
                accepted = c
        out.append({"ref_id": r["ref_id"], "source_title": r["title"], "year": r["year"], "authors": r["authors"][:80],
                    "candidates": list(cands.values()),
                    "status": "accepted_auto" if accepted else ("needs_manual" if cands else "no_candidate"),
                    "openalex_id": accepted["openalex_id"] if accepted else None})
        print(r["ref_id"], out[-1]["status"], out[-1]["openalex_id"], flush=True)
    (ROOT / "results" / "matching_raw.json").write_text(json.dumps(out, indent=1) + "\n")
    from collections import Counter
    print(Counter(o["status"] for o in out))


if __name__ == "__main__":
    main()
