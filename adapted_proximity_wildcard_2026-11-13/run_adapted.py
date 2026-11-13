"""Live runner: validate (free /query), count and restricted membership for each adapted arm.
Archives request bodies, statuses, responses and UTC times (no headers, no key).
Recall is scored in each benchmark's own unit; the frozen arms are re-scored offline from their
archived recovered IDs in the same unit as a check against their published summaries."""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
sys.path.insert(0, str(REPO))
import pilot_credentials  # noqa: E402

DENOM = {"walker_transgenerational": 257, "inclusion_sen": 94, "bt_maize_multisource": 166, "cost_mental_disorders": 143,
         "motor_competence": 44, "precarious_employment": 50, "hiv_care_continuum": 190, "pa_primary_care": 51}
SCREENED = {"walker_transgenerational": 63754, "inclusion_sen": 20183, "bt_maize_multisource": 12967, "cost_mental_disorders": 13579,
            "motor_competence": 12117, "precarious_employment": 12940, "hiv_care_continuum": 10281, "pa_primary_care": 14566}


def call(label, url, body):
    dest = ROOT / "archives" / f"{label}.json"
    if dest.exists():
        d = json.loads(dest.read_text())
        if d["request"]["body"] == body:
            return d["status"], d["response"]
    started = datetime.now(timezone.utc).isoformat()
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "Authorization": "Bearer " + os.environ["OPENALEX_API_KEY"]})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            status, resp = r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        status, resp = e.code, json.loads(e.read() or b"{}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({"request": {"method": "POST", "url": url, "body": body}, "status": status, "requested_utc": started, "response": resp}, indent=1))
    time.sleep(0.15)
    return status, resp


def units(bench_dir):
    """unit id -> set of OpenAlex IDs that count for it."""
    m = json.loads((bench_dir / "results/benchmark_matches.json").read_text())
    recs = m["records"] if isinstance(m, dict) else m
    if bench_dir.name.startswith("pa_primary_care"):
        src = json.loads((bench_dir / "results/benchmark_source.json").read_text())
        by = {r["ref_id"]: r["openalex_id"] for r in recs}
        return {s["study_id"]: {by[r] for r in s["ref_ids"] if by[r]} for s in src["studies"]}
    out = {}
    for i, r in enumerate(recs):
        ids = {r.get("openalex_id")} | set(r.get("alternate_openalex_ids") or [])
        ids.discard(None)
        if ids:
            out[str(i)] = ids   # each record is one unit (study or reference)
    return out


def score(u, found):
    return sum(1 for ids in u.values() if ids & found)


def main():
    pilot_credentials.load_key()
    plan = json.loads((ROOT / "queries/plan.json").read_text())
    rows = []
    for p in plan:
        bdir = REPO / p["benchmark"]
        key = p["name"].split("__")[0]
        u = units(bdir)
        ids = sorted(set().union(*u.values()))
        frozen_obs = json.loads((bdir / "results/run_observations.json").read_text())["arms"][p["arm"]]
        frozen_rec = score(u, set(frozen_obs["recovered_ids"]))
        oql = (ROOT / "queries" / f"{p['name']}.oql").read_text().strip()
        st, v = call(f"{p['name']}/validate", "https://api.openalex.org/query", {"oql": oql})
        valid = st == 200 and v.get("validation", {}).get("valid")
        row = {**p, "unit_denominator": DENOM[key], "units_in_openalex": len(u), "screened": SCREENED[key],
               "frozen_count": frozen_obs["count"], "frozen_recovered": frozen_rec, "valid": bool(valid)}
        if not valid:
            row["validation_errors"] = v.get("validation", {}).get("errors") or v
            rows.append(row); print(p["name"], "INVALID", str(row["validation_errors"])[:300]); continue
        st, c = call(f"{p['name']}/count", "https://api.openalex.org/", {"oql": oql, "per_page": 1, "select": "id"})
        found = set()
        for k in range(0, len(ids), 100):
            batch = ids[k:k + 100]
            st2, r2 = call(f"{p['name']}/membership_{k // 100 + 1:02d}", "https://api.openalex.org/",
                           {"oql": oql + " and openalex id is (" + " or ".join(batch) + ")", "per_page": 100, "select": "id"})
            got = {x["id"].rsplit("/", 1)[-1] for x in r2["results"]}
            assert r2["meta"]["count"] == len(got) and got <= set(batch)
            found |= got
        row.update({"adapted_count": c["meta"]["count"], "adapted_recovered": score(u, found), "adapted_recovered_ids": sorted(found),
                    "lost_vs_frozen": sorted(set(frozen_obs["recovered_ids"]) - found)})
        rows.append(row)
        print(f"{p['name']:60s} frozen {frozen_rec:4d} @ {frozen_obs['count']:>8,}  adapted {row['adapted_recovered']:4d} @ {row['adapted_count']:>8,}  / {DENOM[key]}", flush=True)
    (ROOT / "results/adapted_results.json").write_text(json.dumps(rows, indent=1) + "\n")


if __name__ == "__main__":
    main()
