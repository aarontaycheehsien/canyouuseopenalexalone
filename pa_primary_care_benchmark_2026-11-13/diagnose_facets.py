"""Post-hoc facet diagnostics over the 48 matched references (one batch).

Each block of the frozen string, in title-abstract and in title-abstract-keywords, plus
the date ceiling and abstract presence, run alone and
restricted to the matched IDs. Explanatory only; no repaired query replaces a frozen arm.
"""
import json

import build_queries as bq
import run_test as rt

ROOT = rt.ROOT


def main():
    rt.pilot_credentials.load_key()
    m = json.loads((ROOT / "results/benchmark_matches.json").read_text())
    ids = sorted(r["openalex_id"] for r in m["records"] if r["openalex_id"])
    _, b = bq.build()
    slug = lambda s: s.lower().replace(" ", "_")  # noqa: E731
    facets = {"date_ceiling": f"date <= ({bq.DATE_TO})", "has_abstract": "has abstract"}
    for name, q in b["blocks"].items():
        facets[f"ta_{slug(name)}"] = f"title-abstract has {q}"
        facets[f"tak_{slug(name)}"] = f"title-abstract-keywords has {q}"
    out = {"ids": ids, "facets": {}}
    for name, cond in facets.items():
        hits = []
        for k in range(0, len(ids), 100):
            batch = ids[k:k + 100]
            r = rt.post(f"diagnostics/{name}_{k // 100 + 1}", {"oql": f"get works where openalex id is ({' or '.join(batch)}) and {cond}", "per_page": 100, "select": "id"})
            got = [x["id"].rsplit("/", 1)[-1] for x in r["results"]]
            assert r["meta"]["count"] == len(got) and set(got) <= set(batch)
            hits += got
        out["facets"][name] = {"condition": cond, "matching_ids": sorted(hits)}
        print(name, len(hits), flush=True)
    (ROOT / "results/facet_diagnostics.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
