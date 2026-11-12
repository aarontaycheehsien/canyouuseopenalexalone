"""Offline verifier: standard library only, no network requests.

    python3 walker_transgenerational_benchmark_2026-11-12/verify.py
"""
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
J = lambda p: json.loads((ROOT / p).read_text())  # noqa: E731
checks = []


def ok(cond, msg):
    checks.append((bool(cond), msg))
    if not cond:
        print("FAIL:", msg)


def wid(x):
    return x["id"].rsplit("/", 1)[-1]


def main():
    # 1. Freeze integrity: frozen files unchanged since the pushed freeze commit.
    man = J("freeze_manifest.json")
    for f, h in man["sha256"].items():
        ok(hashlib.sha256((ROOT / f).read_bytes()).hexdigest() == h, f"frozen file unchanged: {f}")
    ok(man["candidate_queries_executed"] is False, "manifest records no execution before freeze")
    r = subprocess.run([sys.executable, str(ROOT / "build_queries.py"), "--check"], capture_output=True, text=True)
    ok(r.returncode == 0, "query builder reproduces frozen queries")

    # 2. Benchmark reconstruction.
    src = J("results/benchmark_source.json")
    recs = src["records"]
    ok(len(recs) == 257, "257 references")
    ok(sum(r["stream"] == "human" for r in recs) == 46 and sum(r["stream"] == "animal" for r in recs) == 211, "46 human + 211 animal")
    ok(len(src["cross_listed_human_entries_in_animal_section"]) == 46 and src["entries_in_supplement"] == 303, "303 entries = 257 + 46 cross-listed")

    # 3. Matching evidence: every accepted ID appears in an archived OpenAlex lookup.
    m = J("results/benchmark_matches.json")
    looked_up = set()
    for p in (ROOT / "archives/matching").glob("oa_*.json"):
        d = json.loads(p.read_text())
        if d["status"] == 200 and d["response"].get("id"):
            looked_up.add(wid(d["response"]))
    ok(all(x["openalex_id"] in looked_up for x in m["records"]), "every match backed by an archived lookup")
    ids = sorted({x["openalex_id"] for x in m["records"]})
    ok(len(ids) == m["distinct_openalex_ids"] == 253, "253 distinct works")
    ok(sum(x["decision"] == "accepted_manual" for x in m["records"]) == 10, "10 manual adjudications recorded")

    # 4. Arms: OQL POST, identical OQO restriction, membership.
    obs = J("results/run_observations.json")
    for q in sorted((ROOT / "queries").glob("*.oql")):
        arm = q.stem
        first = J(f"archives/{arm}/unrestricted_cursor_001.json")
        ok(first["request"]["method"] == "POST" and first["request"]["path"] == "/", f"{arm}: executed by POST /")
        ok(first["request"]["body"]["oql"] == q.read_text().strip(), f"{arm}: posted OQL equals frozen file")
        oqo = first["response"]["meta"]["x_query"]["oqo"]
        val = J(f"validation/{arm}.query.json")["oqo"]
        ok(oqo["filter_rows"] == val["filter_rows"], f"{arm}: executed filters equal pre-freeze validation")
        count = first["response"]["meta"]["count"]
        ok(count == obs["arms"][arm]["count"], f"{arm}: count archived")
        rt = J(f"archives/{arm}/oqo_roundtrip.json")
        ok(rt["request"]["body"]["oqo"] == oqo and rt["response"]["meta"]["count"] == count, f"{arm}: OQO round-trip count equal")
        found, seen = set(), []
        for p in sorted((ROOT / f"archives/{arm}").glob("benchmark_membership_*.json")):
            d = json.loads(p.read_text())
            body = d["request"]["body"]["oqo"]
            extra = body["filter_rows"][-1]
            batch = [f["value"] for f in extra["filters"]]
            ok(body["filter_rows"][:-1] == oqo["filter_rows"] and {k: v for k, v in body.items() if k != "filter_rows"} == {k: v for k, v in oqo.items() if k != "filter_rows"},
               f"{arm}/{p.stem}: only an ID restriction was added")
            ok(extra["join"] == "or" and all(f["column_id"] == "ids.openalex" for f in extra["filters"]) and len(batch) <= 100, f"{arm}/{p.stem}: restriction is <=100 OpenAlex IDs")
            got = {wid(x) for x in d["response"]["results"]}
            ok(d["response"]["meta"]["count"] == len(got) and got <= set(batch), f"{arm}/{p.stem}: complete batch response")
            seen += batch
            found |= got
        ok(sorted(seen) == ids, f"{arm}: all 253 IDs tested exactly once")
        ok(sorted(found) == obs["arms"][arm]["recovered_ids"], f"{arm}: recovered IDs reproduced")
        c2 = J(f"archives/{arm}/unrestricted_cursor_002.json")
        ok(c2["response"]["meta"]["count"] == count and not ({wid(x) for x in c2["response"]["results"]} & {wid(x) for x in first["response"]["results"]}),
           f"{arm}: POST cursor page 2 consistent and disjoint")

    # 5. Summary and matrix recomputed.
    s = J("results/summary.json")
    with open(ROOT / "results/per_reference_retrieval.csv") as f:
        rows = list(csv.DictReader(f))
    ok(len(rows) == 257, "matrix has 257 rows")
    for arm, a in s["arms"].items():
        refs = sum(int(r[arm]) for r in rows)
        ok(refs == a["recovered_references"] == 249, f"{arm}: 249/257 references")
        ok(a["meets_recall_threshold"] == (refs >= 245) and a["count_below_original_screened"] == (a["api_count"] <= 63754), f"{arm}: thresholds")
        ok(a["complete_unrestricted_export"] is False, f"{arm}: partial-export label present")
    ok(sum(int(r["pubmed_strategy_rerun_2026_11_12"]) for r in rows) == s["published_pubmed_strategy_rerun_today_references"], "PubMed rerun tally")

    # 6. Diagnostics and secondary analyses only add restrictions.
    d = J("results/clause_diagnostics.json")
    missed = sorted(set(ids) - set(obs["arms"]["A_faithful_title_abstract"]["recovered_ids"]))
    ok(d["missed_ids"] == missed, "diagnostics cover exactly the missed works")
    for p in (ROOT / "archives/diagnostics").glob("*.json"):
        body = json.loads(p.read_text())["request"]["body"]["oql"]
        ok(body.startswith("get works where openalex id is (" + " or ".join(missed) + ")"), f"diagnostic {p.stem} restricted to missed IDs")
    for p in (ROOT / "archives/synergy").glob("*_overlap_count.json"):
        dd = json.loads(p.read_text())
        arm = p.stem.replace("_overlap_count", "")
        base = J(f"archives/{arm}/unrestricted_cursor_001.json")["response"]["meta"]["x_query"]["oqo"]["filter_rows"]
        fr = dd["request"]["body"]["oqo"]["filter_rows"]
        ok(fr[:-1] == base and fr[-1]["column_id"] == "collection", f"{p.stem}: only a collection filter added")

    # 7. No credential in archived requests.
    key_file = ROOT.parent / ".env.txt"
    if key_file.exists():
        key = key_file.read_text().strip()
        leaked = [p for p in ROOT.rglob("*") if p.is_file() and key and key in p.read_text(errors="ignore")]
        ok(not leaked, "API key absent from every archived file")

    # 8. Checksums for every archived file (SHA256SUMS lists all files except itself and this script).
    sums = (ROOT / "SHA256SUMS").read_text().splitlines()
    bad = [ln for ln in sums if not ln.endswith("./verify.py") and hashlib.sha256((ROOT / ln.split("  ", 1)[1]).read_bytes()).hexdigest() != ln.split("  ", 1)[0]]
    ok(not bad and len(sums) > 400, f"SHA256SUMS matches {len(sums)} files")

    failed = [m for c, m in checks if not c]
    print(f"{len(checks) - len(failed)}/{len(checks)} checks passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
