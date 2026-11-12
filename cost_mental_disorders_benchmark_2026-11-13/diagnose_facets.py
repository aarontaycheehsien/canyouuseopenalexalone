"""Post-hoc facet diagnostics over all benchmark references held in OpenAlex.

Each component of the frozen string is run alone in title-abstract and in
title-abstract-keywords, plus the date window and abstract presence, restricted to
the matched IDs (with alternates) in batches of at most 100. Explanatory only.
"""
import json

import build_queries as bq
import run_test as rt

ROOT = rt.ROOT


def main():
    rt.pilot_credentials.load_key()
    m = json.loads((ROOT / "results/benchmark_matches.json").read_text())
    ids = sorted({i for r in m["records"] if r["openalex_id"] for i in [r["openalex_id"], *r.get("alternate_openalex_ids", [])]})
    _, blocks = bq.build()
    groups = " OR ".join(v for k, v in blocks.items() if k.startswith("group_"))
    parts = {"cost_terms": blocks["cost_#1"], "disorder_terms": f"({groups})", "excluded_animal_or_trial": '("animal*" OR "trial*")'}
    facets = {"date_window": f"date >= ({bq.DATE_FROM}) and date <= ({bq.DATE_TO})", "has_abstract": "has abstract"}
    for field, tag in (("title-abstract", "ta"), ("title-abstract-keywords", "tak")):
        for name, s in parts.items():
            facets[f"{tag}_{name}"] = f"{field} has {s}"
    out = {"ids": ids, "facets": {}}
    for name, cond in facets.items():
        hits = []
        for i in range(0, len(ids), 100):
            batch = ids[i:i + 100]
            r = rt.post(f"diagnostics/{name}_{i // 100 + 1}", {"oql": f"get works where openalex id is ({' or '.join(batch)}) and {cond}", "per_page": 100, "select": "id"})
            got = [x["id"].rsplit("/", 1)[-1] for x in r["results"]]
            assert r["meta"]["count"] == len(got)
            hits += got
        out["facets"][name] = {"condition": cond, "matching_ids": sorted(hits)}
        print(name, len(hits), flush=True)
    (ROOT / "results/facet_diagnostics.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
