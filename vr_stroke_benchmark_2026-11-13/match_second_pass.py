"""Second matching pass for references with no plausible first-pass candidate.

Two OpenAlex searches each (key required, archived under archives/matching/):
(a) title.search on the first 6 significant title words; (b) search= on the first
author's surname plus those words.
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
TARGETS = {"VR-31", "VR-42"}
# PA-051: ATS meeting abstracts carry DOIs of this pattern; tried first (free lookup)
DOI_GUESS = {}
STOP = {"the", "of", "and", "a", "an", "in", "on", "for", "to", "with", "de", "la", "le", "en", "y", "i", "af", "der", "die", "und"}


def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def get(label, url):
    dest = ARCH / (label + ".json")
    if dest.exists():
        old = json.loads(dest.read_text())
        if old["status"] == 200:
            return old["response"]
    started = datetime.now(timezone.utc).isoformat()
    req = urllib.request.Request(url, headers={"User-Agent": "OpenAlex-transfer-benchmark/1.0",
                                               "Authorization": "Bearer " + os.environ["OPENALEX_API_KEY"]})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            status, raw = r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        status, raw = e.code, e.read().decode(errors="replace")
    resp = json.loads(raw) if raw.strip().startswith("{") else {"non_json_response": raw[:2000]}
    dest.write_text(json.dumps({"url": url, "requested_utc": started, "status": status, "response": resp}, indent=1))
    time.sleep(0.3)
    return resp if status == 200 else None


def slim(x):
    loc = (x.get("primary_location") or {}).get("source") or {}
    return {"openalex_id": x["id"].rsplit("/", 1)[-1], "doi": x.get("doi"), "pmid": (x.get("ids") or {}).get("pmid"),
            "title": x.get("display_name"), "publication_date": x.get("publication_date"), "type": x.get("type"),
            "language": x.get("language"), "source": loc.get("display_name"), "is_retracted": x.get("is_retracted"),
            "first_author": ((x.get("authorships") or [{}])[0].get("author") or {}).get("display_name")}


def main():
    pilot_credentials.load_key()
    raw = json.loads((ROOT / "results/matching_raw.json").read_text())
    src = {s["ref_id"]: s for s in json.loads((ROOT / "results/benchmark_source.json").read_text())["records"]}
    for r in raw:
        if r["ref_id"] not in TARGETS:
            continue
        s = src[r["ref_id"]]
        words = [w for w in norm(s["title"]).split() if w not in STOP and len(w) > 2][:6]
        surname = norm(s["study_label"].split()[0])
        found = {}
        if r["ref_id"] in DOI_GUESS:
            x = get(f"oa_doiguess_{r['ref_id']}", "https://api.openalex.org/works/doi:" + DOI_GUESS[r["ref_id"]] + f"?select={FIELDS}")
            if x and x.get("id"):
                c = slim(x)
                c["title_similarity"] = round(difflib.SequenceMatcher(None, norm(s["title"]), norm(c["title"])).ratio(), 3)
                c["via"] = "second_pass_doiguess"
                found[c["openalex_id"]] = c
        for label, q in ((f"oa_title6_{r['ref_id']}", "filter=title.search:" + urllib.parse.quote(" ".join(words))),
                         (f"oa_search_{r['ref_id']}", "search=" + urllib.parse.quote(surname + " " + " ".join(words)))):
            res = get(label, f"https://api.openalex.org/works?per_page=5&select={FIELDS}&{q}") or {}
            for x in res.get("results", []):
                c = slim(x)
                c["title_similarity"] = round(difflib.SequenceMatcher(None, norm(s["title"]), norm(c["title"])).ratio(), 3)
                c["via"] = "second_pass_" + label.split("_")[1]
                found.setdefault(c["openalex_id"], c)
        r["second_pass_candidates"] = list(found.values())
        for c in sorted(found.values(), key=lambda c: -c["title_similarity"])[:2]:
            print(r["ref_id"], c["openalex_id"], c["title_similarity"], c["publication_date"], c["type"], (c["source"] or "")[:25], "|", (c["title"] or "")[:90], "|", c["first_author"])
    (ROOT / "results/matching_raw.json").write_text(json.dumps(raw, indent=1) + "\n")


if __name__ == "__main__":
    main()
