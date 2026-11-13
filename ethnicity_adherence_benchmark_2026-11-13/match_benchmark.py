"""Match the 41 cited references of the 41 included studies to OpenAlex. Explicit live runner.

DOIs, then PMIDs, from the article's reference list resolve by free OpenAlex single-entity
lookups; an article without either is searched by title (key required). Every accepted match is
audited against the full citation. Responses are archived under archives/matching/.
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
FIELDS = "id,doi,display_name,publication_date,ids,type,authorships,primary_location,is_retracted,language"


def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def partial(a, b):
    a, b = norm(a), norm(b)
    if len(a) > len(b):
        a, b = b, a
    return max(difflib.SequenceMatcher(None, a, b[i:i + len(a)]).ratio() for i in range(0, max(1, len(b) - len(a) + 1), 2)) if a else 0


def get(label, url, auth=False):
    dest = ARCH / (label + ".json")
    if dest.exists():
        old = json.loads(dest.read_text())
        if old["status"] == 200:
            return old["response"]
    headers = {"User-Agent": "OpenAlex-transfer-benchmark/1.0"}
    if auth:
        headers["Authorization"] = "Bearer " + os.environ["OPENALEX_API_KEY"]
    started = datetime.now(timezone.utc).isoformat()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as r:
            status, raw = r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        status, raw = e.code, e.read().decode(errors="replace")
    resp = json.loads(raw) if raw.strip().startswith("{") else {"non_json_response": raw[:2000]}
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({"url": url, "requested_utc": started, "status": status, "response": resp}, indent=1))
    time.sleep(0.25)
    return resp if status == 200 else None


def slim(x):
    loc = (x.get("primary_location") or {}).get("source") or {}
    return {"openalex_id": x["id"].rsplit("/", 1)[-1], "doi": x.get("doi"), "title": x.get("display_name"),
            "publication_date": x.get("publication_date"), "type": x.get("type"), "language": x.get("language"),
            "source": loc.get("display_name"), "is_retracted": x.get("is_retracted"),
            "first_author": ((x.get("authorships") or [{}])[0].get("author") or {}).get("display_name")}


def main():
    pilot_credentials.load_key()
    src = json.loads((ROOT / "results/benchmark_source.json").read_text())["records"]
    out = []
    for s in src:
        cands = []
        if s["doi"]:
            r = get(f"oa_doi_{s['ref_id']}", "https://api.openalex.org/works/doi:" + urllib.parse.quote(s["doi"]) + f"?select={FIELDS}")
            if r and r.get("id"):
                cands.append({**slim(r), "via": "reference_doi"})
        if not cands and s["pmid"]:
            r = get(f"oa_pmid_{s['ref_id']}", f"https://api.openalex.org/works/pmid:{s['pmid']}?select={FIELDS}")
            if r and r.get("id"):
                cands.append({**slim(r), "via": "reference_pmid"})
        if not cands:
            words = " ".join(norm(s["title"]).split()[:12])
            r = get(f"oa_title_{s['ref_id']}", f"https://api.openalex.org/works?per_page=5&select={FIELDS}&filter=title.search:" + urllib.parse.quote(words), auth=True) or {}
            cands += [{**slim(x), "via": "openalex_title_search"} for x in r.get("results", [])]
        for c in cands:
            c["citation_title_agreement"] = round(partial(c["title"], s["citation"]), 3)
        best = max(cands, key=lambda c: c["citation_title_agreement"], default=None)
        ok = best is not None and best["citation_title_agreement"] >= 0.9
        out.append({"ref_id": s["ref_id"], "study_label": s["study_label"], "candidates": cands,
                    "status": "accepted_auto" if ok else ("needs_manual" if cands else "no_candidate"),
                    "openalex_id": best["openalex_id"] if ok else None})
        print(s["ref_id"], s["study_label"], out[-1]["status"], out[-1]["openalex_id"], best and best["citation_title_agreement"], flush=True)
    (ROOT / "results/matching_raw.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
