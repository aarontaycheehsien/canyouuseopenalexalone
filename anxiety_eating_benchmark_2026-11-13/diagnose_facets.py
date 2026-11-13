"""Post-hoc: each concept of the designed arms (text part, keyword part, both) and the mechanical
blocks, run alone, restricted to the 53 matched IDs. Explanatory only."""
import json
import re

import build_queries as bq
import run_test as rt

ROOT = rt.ROOT


def main():
    rt.pilot_credentials.load_key()
    m = json.loads((ROOT / "results/benchmark_matches.json").read_text())
    ids = sorted(r["openalex_id"] for r in m["records"] if r["openalex_id"])
    concepts = {"anxiety": (bq.ANX_TEXT, bq.ANX_KW), "eating": (bq.ED_TEXT, bq.ED_KW), "youth": (bq.YOUTH_TEXT, bq.YOUTH_KW),
                "prospective": (bq.DESIGN_TEXT, bq.DESIGN_KW)}
    facets = {"date": f"date <= ({bq.DATE_TO})", "has_abstract": "has abstract"}
    for k, (t, kw) in concepts.items():
        facets[f"{k}_text"] = f"title-abstract has {t}"
        facets[f"{k}_keywords"] = f"({kw})"
        facets[f"{k}_either"] = bq.concept(t, kw)
    mq = bq.arm_m()
    for i, blk in enumerate(re.findall(r"title-abstract-keywords has (\((?:[^()]|\([^()]*\))*\))", mq)):
        facets[f"M_block{i + 1}"] = f"title-abstract-keywords has {blk}"
    out = {"ids": ids, "facets": {}}
    for name, cond in facets.items():
        r = rt.post(f"diagnostics/{name}", {"oql": f"get works where openalex id is ({' or '.join(ids)}) and {cond}", "per_page": 100, "select": "id"})
        got = sorted(x["id"].rsplit("/", 1)[-1] for x in r["results"])
        assert r["meta"]["count"] == len(got)
        out["facets"][name] = {"condition": cond, "matching_ids": got}
        print(f"{name:22s} {len(got)}", flush=True)
    (ROOT / "results/facet_diagnostics.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
