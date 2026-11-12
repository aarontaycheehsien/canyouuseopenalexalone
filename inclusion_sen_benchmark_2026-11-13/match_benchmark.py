"""Match the 94 included studies to OpenAlex works. Explicit live runner.

Routes per study (responses archived under archives/matching/):
  1. DOI from the reference list -> OpenAlex single-entity lookup (free).
  2. OpenAlex title search (filter title.search, key required) -> candidates.
  3. Crossref bibliographic query -> DOIs -> OpenAlex lookup.
Candidates are scored on title similarity, year and first-author surname;
anything short of strong agreement, or any thesis/report matched to a journal
article, is left for manual adjudication. Re-running reuses archived responses.
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
FIELDS = "id,doi,display_name,publication_date,ids,type,authorships,primary_location,is_retracted"
GREY = re.compile(r"dissertation|thes[ie]s|proquest|pqdt|position paper|universitetsforlag", re.I)


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
    if isinstance(resp, dict) and isinstance(resp.get("message"), dict):  # Crossref: drop abstracts
        for it in resp["message"].get("items", []):
            it.pop("abstract", None)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({"url": url, "requested_utc": started, "status": status, "response": resp}, indent=1))
    time.sleep(0.25)
    return resp if status == 200 else None


def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", re.sub(r"<[^>]+>", " ", t or "").lower()).strip()


def sim(a, b):
    return round(difflib.SequenceMatcher(None, norm(a), norm(b)).ratio(), 3)


def cand(r):
    loc = (r.get("primary_location") or {}).get("source") or {}
    return {"openalex_id": r["id"].rsplit("/", 1)[-1], "doi": r.get("doi"), "title": r.get("display_name"),
            "publication_date": r.get("publication_date"), "type": r.get("type"),
            "first_author": ((r.get("authorships") or [{}])[0].get("author") or {}).get("display_name"),
            "source": loc.get("display_name"), "source_type": loc.get("type"), "is_retracted": r.get("is_retracted")}


def main():
    pilot_credentials.load_key()
    src = json.loads((ROOT / "results" / "benchmark_source.json").read_text())["records"]
    out = []
    for s in src:
        cands = {}
        if s["reference_doi"]:
            r = get(f"oa_doi_{s['study']}", "https://api.openalex.org/works/doi:" + urllib.parse.quote(s["reference_doi"]) + f"?select={FIELDS}")
            if r and r.get("id"):
                cands[r["id"]] = {**cand(r), "via": "reference_doi"}
        words = " ".join(w for w in norm(s["title"]).split()[:14])
        r = get(f"oa_title_{s['study']}", "https://api.openalex.org/works?per_page=5&select=" + FIELDS +
                "&filter=title.search:" + urllib.parse.quote(words), auth=True)
        for x in (r or {}).get("results", []):
            cands.setdefault(x["id"], {**cand(x), "via": "openalex_title_search"})
        q = urllib.parse.quote(f"{s['title']} {s['authors'].split(';')[0]} {s['year']}")
        r = get(f"crossref_{s['study']}", f"https://api.crossref.org/works?rows=3&query.bibliographic={q}")
        for it in ((r or {}).get("message") or {}).get("items", []):
            if it.get("DOI") and sim(s["title"], (it.get("title") or [""])[0]) >= 0.8:
                x = get(f"oa_doi_{s['study']}_{re.sub(r'[^A-Za-z0-9]+', '_', it['DOI'])[:60]}",
                        "https://api.openalex.org/works/doi:" + urllib.parse.quote(it["DOI"]) + f"?select={FIELDS}")
                if x and x.get("id"):
                    cands.setdefault(x["id"], {**cand(x), "via": "crossref_doi"})
        surname = norm(s["authors"].split(";")[0].split(",")[0]).split()
        decided = None
        for c in sorted(cands.values(), key=lambda c: -sim(s["title"], c["title"])):
            c["title_similarity"] = sim(s["title"], c["title"])
            yr_ok = bool(c["publication_date"]) and s["year"].isdigit() and abs(int(c["publication_date"][:4]) - int(s["year"])) <= 3
            au_ok = bool(surname) and any(w in norm(c["first_author"]) for w in surname[:2])
            grey_vs_journal = bool(GREY.search(s["outlet"])) and c["type"] == "article" and (c["source_type"] == "journal")
            c["auto_checks"] = {"year_within_3": yr_ok, "first_author": au_ok, "thesis_matched_to_journal_article": grey_vs_journal}
            if decided is None and c["title_similarity"] >= 0.9 and yr_ok and au_ok and not grey_vs_journal:
                decided = c
        out.append({"study": s["study"], "study_id": s["study_id"], "outlet": s["outlet"], "source_title": s["title"],
                    "year": s["year"], "candidates": list(cands.values()),
                    "status": "accepted_auto" if decided else ("needs_manual" if cands else "no_candidate"),
                    "openalex_id": decided["openalex_id"] if decided else None})
        print(s["study"], out[-1]["status"], out[-1]["openalex_id"], flush=True)
    (ROOT / "results" / "matching_raw.json").write_text(json.dumps(out, indent=1) + "\n")
    from collections import Counter
    print(Counter(o["status"] for o in out))


if __name__ == "__main__":
    main()
