"""Post-hoc facet diagnostics over the 44 matched studies (one batch).

Each block of the frozen string, the date ceiling, abstract presence and the arm B
limits are run alone, restricted to the matched IDs. Explanatory only.
"""
import json

import build_queries as bq
import run_test as rt

ROOT = rt.ROOT


def main():
    rt.pilot_credentials.load_key()
    m = json.loads((ROOT / "results/benchmark_matches.json").read_text())
    ids = sorted(r["openalex_id"] for r in m["records"] if r["openalex_id"])
    _, blocks = bq.build()
    facets = {"date_ceiling": f"date <= ({bq.DATE_TO})", "has_abstract": "has abstract",
              "english_article": "language is [English](en) and type is [article](article)"}
    for name, b in blocks.items():
        facets["tak_" + name.lower().replace(" ", "_")] = f"title-abstract-keywords has {b}"
    out = {"ids": ids, "facets": {}}
    for name, cond in facets.items():
        r = rt.post(f"diagnostics/{name}", {"oql": f"get works where openalex id is ({' or '.join(ids)}) and {cond}", "per_page": 100, "select": "id"})
        hits = sorted(x["id"].rsplit("/", 1)[-1] for x in r["results"])
        assert r["meta"]["count"] == len(hits)
        out["facets"][name] = {"condition": cond, "matching_ids": hits}
        print(name, len(hits), flush=True)
    (ROOT / "results/facet_diagnostics.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
