"""Post-hoc facet diagnostics over all benchmark references held in OpenAlex.

Each block of the frozen string is run alone (title-abstract-keywords, and title-abstract
for comparison), plus the date ceiling and abstract presence, restricted to the matched
IDs in batches of at most 100. Explanatory only; no repaired query replaces a frozen arm.
"""
import json
import re

import build_queries as bq
import run_test as rt

ROOT = rt.ROOT


def main():
    rt.pilot_credentials.load_key()
    m = json.loads((ROOT / "results/benchmark_matches.json").read_text())
    ids = sorted({r["openalex_id"] for r in m["records"] if r["openalex_id"]})
    oql = bq.build()["A_core_title_abstract_keywords"]
    inner = re.search(r"title-abstract-keywords has \((.*)\)$", oql).group(1)
    blocks = re.split(r"\) AND \(", inner.strip("()"))
    names = ["maize", "field_method", "gm_trait"]
    facets = {"date_ceiling": f"date <= ({bq.CEILING})", "has_abstract": "has abstract"}
    for n, b in zip(names, blocks):
        facets[f"tak_{n}"] = f"title-abstract-keywords has ({b})"
        facets[f"ta_{n}"] = f"title-abstract has ({b})"
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
    (ROOT / "results/facet_diagnostics.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
