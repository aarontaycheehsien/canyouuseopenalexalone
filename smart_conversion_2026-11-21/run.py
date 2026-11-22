"""Score the frozen smart arms on the eight existing benchmarks (network; archived).

    python3 run.py           # writes results/smart_results.json

For each review, on the same day: unrestricted count and ID-restricted membership (batches of
at most 100 verified benchmark IDs, only `and openalex id is (...)` appended) for the frozen smart
query and for the frozen base arm, each scored in the review's own unit (studies or references)
with the scoring function the adapted arm used. Runs after the freeze (commit e0a2a03).
"""
import json
import sys
from pathlib import Path

import netlib

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
sys.path.insert(0, str(REPO / "adapted_proximity_wildcard_2026-11-13"))
from run_adapted import DENOM, SCREENED, score, units  # noqa: E402
from specs import SPECS  # noqa: E402

BENCH_DIR = {k: v["base"].split("/")[0] for k, v in SPECS.items() if k != "noetel_exercise"}


def count(oql):
    st, r = netlib.post("count", "https://api.openalex.org/", {"oql": oql, "per_page": 1, "select": "id"})
    assert st == 200, (st, r)
    return r["meta"]["count"]


def membership(oql, ids):
    found = set()
    for k in range(0, len(ids), 100):
        batch = ids[k:k + 100]
        st, r = netlib.post("membership", "https://api.openalex.org/",
                            {"oql": oql + " and openalex id is (" + " or ".join(batch) + ")", "per_page": 100, "select": "id"})
        assert st == 200, (st, r)
        got = {x["id"].rsplit("/", 1)[-1] for x in r["results"]}
        assert r["meta"]["count"] == len(got) and got <= set(batch), "incomplete batch"
        found |= got
    return found


def main():
    rows = []
    for name, bdir in BENCH_DIR.items():
        u = units(REPO / bdir)
        ids = sorted(set().union(*u.values()))
        row = {"review": name, "unit_denominator": DENOM[name], "units_in_openalex": len(u), "screened": SCREENED[name],
               "threshold_units": int(0.95 * DENOM[name]) + 1}
        for arm, oql in (("smart", (ROOT / "queries" / f"{name}__S_smart.oql").read_text().strip()),
                         ("frozen_base", (REPO / SPECS[name]["base"]).read_text().strip())):
            found = membership(oql, ids)
            n = count(oql)
            rec = score(u, found)
            row[arm] = {"count": n, "recovered": rec, "recall": round(rec / DENOM[name], 4),
                        "meets_recall": rec >= row["threshold_units"], "count_at_most_screened": n <= SCREENED[name],
                        "recovered_ids": sorted(found)}
        row["smart_only_ids"] = sorted(set(row["smart"]["recovered_ids"]) - set(row["frozen_base"]["recovered_ids"]))
        row["base_only_ids"] = sorted(set(row["frozen_base"]["recovered_ids"]) - set(row["smart"]["recovered_ids"]))
        rows.append(row)
        s, b = row["smart"], row["frozen_base"]
        print(f"{name:26s} base {b['recovered']:4d}/{DENOM[name]} @ {b['count']:>8,}   smart {s['recovered']:4d}/{DENOM[name]} @ {s['count']:>8,}"
              f"   (+{len(row['smart_only_ids'])} -{len(row['base_only_ids'])} ids)", flush=True)
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results/smart_results.json").write_text(json.dumps(rows, indent=1) + "\n")


if __name__ == "__main__":
    main()
