"""Second matching pass for references not auto-accepted: two broader OpenAlex searches each.

(a) title.search on the first 6 significant title words; (b) search= on the first
author's surname plus those words. Archived under archives/matching/.
"""
import json
import urllib.parse

import match_benchmark as mb

SKIP = {"BT-924"}  # legend text parsed as an entry; see reconciliation
# Auto-accepts found wrong on audit against the full citation (Part 2 matched to Part 3;
# a 2011 maize paper matched to a 2023 soybean paper); searched again here.
RECHECK = {"BT-904", "BT-911"}


def main():
    mb.pilot_credentials.load_key()
    raw = json.loads((mb.ROOT / "results/matching_raw.json").read_text())
    src = {s["ref_id"]: s for s in json.loads((mb.ROOT / "results/benchmark_source.json").read_text())["records"]}
    stop = {"the", "of", "and", "a", "an", "in", "on", "for", "to", "with", "von", "der", "die", "und", "des", "zum", "auf", "im", "de", "la", "le", "en", "y"}
    for r in raw:
        if (r["status"] == "accepted_auto" and r["ref_id"] not in RECHECK) or r["ref_id"] in SKIP or ("second_pass_candidates" in r and r["ref_id"] not in RECHECK):
            continue
        s = src[r["ref_id"]]
        words = [w for w in mb.norm(s["citation"].split(":", 1)[-1]).split() if w not in stop and len(w) > 2][:8 if r["ref_id"] in RECHECK else 6]
        surname = mb.norm(s["authors"].split(",")[0]).split()[0]
        found = {}
        for label, q in ((f"oa_title6_{r['ref_id']}", "filter=title.search:" + urllib.parse.quote(" ".join(words))),
                         (f"oa_search_{r['ref_id']}", "search=" + urllib.parse.quote(surname + " " + " ".join(words)))):
            res = mb.get(label, f"https://api.openalex.org/works?per_page=5&select={mb.OA_FIELDS}&{q}", auth=True) or {}
            for x in res.get("results", []):
                c = mb.slim(x)
                c["title_similarity"] = mb.sim(s["title"], c["title"])
                c["via"] = "second_pass_" + label.split("_")[1]
                found.setdefault(c["openalex_id"], c)
        r["second_pass_candidates"] = list(found.values())
        for c in sorted(found.values(), key=lambda c: -c["title_similarity"])[:2]:
            print(r["ref_id"], c["openalex_id"], c["title_similarity"], c["publication_date"], c["type"], (c["source"] or "")[:25], "|", (c["title"] or "")[:90], "|", c["first_author"])
    (mb.ROOT / "results/matching_raw.json").write_text(json.dumps(raw, indent=1) + "\n")


if __name__ == "__main__":
    main()
