"""Second matching pass for studies with no candidate: two broader OpenAlex searches each.

(a) title.search on the first 6 significant title words; (b) search= on surname plus
6 title words. Responses archived under archives/matching/ like the first pass.
"""
import json
import urllib.parse
import match_benchmark as mb


def main():
    mb.pilot_credentials.load_key()
    raw = json.loads((mb.ROOT / "results/matching_raw.json").read_text())
    src = {s["study"]: s for s in json.loads((mb.ROOT / "results/benchmark_source.json").read_text())["records"]}
    stop = {"the", "of", "and", "a", "an", "in", "on", "for", "to", "with", "between", "study", "among"}
    for r in raw:
        if r["status"] != "no_candidate":
            continue
        s = src[r["study"]]
        words = [w for w in mb.norm(s["title"]).split() if w not in stop][:6]
        surname = mb.norm(s["authors"].split(";")[0].split(",")[0]).split()[0]
        found = {}
        for label, url in (
            (f"oa_title6_{r['study']}", "filter=title.search:" + urllib.parse.quote(" ".join(words))),
            (f"oa_search_{r['study']}", "search=" + urllib.parse.quote(surname + " " + " ".join(words))),
        ):
            res = mb.get(label, f"https://api.openalex.org/works?per_page=5&select={mb.FIELDS}&{url}", auth=True)
            for x in (res or {}).get("results", []):
                c = mb.cand(x)
                c["title_similarity"] = mb.sim(s["title"], c["title"])
                c["via"] = "second_pass_" + label.split("_")[1]
                found.setdefault(c["openalex_id"], c)
        r["second_pass_candidates"] = list(found.values())
        best = max(found.values(), key=lambda c: c["title_similarity"], default=None)
        print(r["study"], s["study_id"], "|", best and (best["openalex_id"], best["title_similarity"], best["type"], best["first_author"], (best["title"] or "")[:80]))
    (mb.ROOT / "results/matching_raw.json").write_text(json.dumps(raw, indent=1) + "\n")


if __name__ == "__main__":
    main()
