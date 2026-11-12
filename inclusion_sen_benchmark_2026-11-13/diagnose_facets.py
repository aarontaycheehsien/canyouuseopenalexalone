"""Post-hoc facet diagnostics over all benchmark studies held in OpenAlex.

Each facet of the frozen arms is run alone, restricted to the 79 matched IDs,
so the table shows which facet removes which study. Explanatory only; no
repaired query replaces a frozen arm.
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
    idlist = "(" + " or ".join(ids) + ")"
    prox = " OR ".join(f'("{a}" and "need*" within 5 words of each other)' for a in ("special*", "additional*", "educational*"))
    facets = {
        "date_window": f"date >= ({bq.DATE_FROM}) and date <= ({bq.DATE_TO})",
        "has_abstract": "has abstract",
        "population_title_abstract": f"title-abstract has {bq.q(bq.POP)}",
        "population_title_only": f"title has {bq.q(bq.POP)}",
        "need_A_ebsco": f"(title has {bq.q(bq.NEED)} or abstract has ({prox}))",
        "need_B_title_only": f"title has {bq.q(bq.NEED)}",
        "need_C_title_abstract": f"title-abstract has {bq.q(bq.NEED)}",
        "intervention": f"title-abstract has {bq.q(bq.INTERVENTION)}",
        "method": f"title-abstract has {bq.q(bq.METHOD)}",
    }
    out = {"ids": ids, "facets": {}}
    for name, cond in facets.items():
        r = rt.post(f"diagnostics/{name}", {"oql": f"get works where openalex id is {idlist} and {cond}", "per_page": 100, "select": "id"})
        hits = sorted(x["id"].rsplit("/", 1)[-1] for x in r["results"])
        assert r["meta"]["count"] == len(hits)
        out["facets"][name] = {"condition": cond, "matching_ids": hits}
        print(name, len(hits), flush=True)
    (ROOT / "results/facet_diagnostics.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
