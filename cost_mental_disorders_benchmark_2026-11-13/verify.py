"""Offline verifier: standard library only, no network requests.

    python3 cost_mental_disorders_benchmark_2026-11-13/verify.py
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
    man = J("freeze_manifest.json")
    for f, h in man["sha256"].items():
        ok(hashlib.sha256((ROOT / f).read_bytes()).hexdigest() == h, f"frozen file unchanged: {f}")
    ok(man["candidate_queries_executed"] is False and man["included_references_parsed_or_matched"] is False, "manifest: nothing executed or matched before freeze")
    r = subprocess.run([sys.executable, str(ROOT / "build_queries.py"), "--check"], capture_output=True, text=True)
    ok(r.returncode == 0, "builder reproduces frozen queries")

    src = J("results/benchmark_source.json")
    ok(len(src["records"]) == 143 == src["stated_included"], "143 included references parsed")
    m = J("results/benchmark_matches.json")
    r = subprocess.run([sys.executable, str(ROOT / "adjudicate.py")], capture_output=True, text=True)
    ok(r.returncode == 0 and J("results/benchmark_matches.json") == m, "adjudication reproduces benchmark_matches.json")
    looked = set()
    for p in (ROOT / "archives/matching").glob("oa_*.json"):
        d = json.loads(p.read_text())
        resp = d["response"] if d["status"] == 200 else {}
        if resp.get("id"):
            looked.add(wid(resp))
        for x in resp.get("results", []):
            looked.add(wid(x))
    allids = sorted({i for x in m["records"] if x["openalex_id"] for i in [x["openalex_id"], *x.get("alternate_openalex_ids", [])]})
    ok(all(i in looked for i in allids), "every matched or alternate ID backed by an archived OpenAlex response")
    ok(m["in_openalex"] == 141 and m["distinct_openalex_ids"] == 141 and len(allids) == 142, "141 references in OpenAlex, one alternate record")

    obs = J("results/run_observations.json")
    for q in sorted((ROOT / "queries").glob("*.oql")):
        arm = q.stem
        first = J(f"archives/{arm}/unrestricted_cursor_001.json")
        ok(first["request"]["method"] == "POST" and first["request"]["body"]["oql"] == q.read_text().strip(), f"{arm}: frozen OQL sent by POST")
        oqo, count = first["response"]["meta"]["x_query"]["oqo"], first["response"]["meta"]["count"]
        ok(oqo["filter_rows"] == J(f"validation/{arm}.query.json")["oqo"]["filter_rows"], f"{arm}: executed filters equal pre-freeze validation")
        rt = J(f"archives/{arm}/oqo_roundtrip.json")
        ok(rt["request"]["body"]["oqo"] == oqo and rt["response"]["meta"]["count"] == count == obs["arms"][arm]["count"], f"{arm}: OQO round-trip count equal")
        p2 = J(f"archives/{arm}/unrestricted_cursor_002.json")
        ok(p2["response"]["meta"]["count"] == count and not ({wid(x) for x in p2["response"]["results"]} & {wid(x) for x in first["response"]["results"]}), f"{arm}: cursor page 2 consistent and disjoint")
        found, seen = set(), []
        for p in sorted((ROOT / f"archives/{arm}").glob("benchmark_membership_*.json")):
            d = json.loads(p.read_text())
            body = d["request"]["body"]["oqo"]
            extra = body["filter_rows"][-1]
            batch = [f["value"] for f in extra["filters"]]
            ok(body["filter_rows"][:-1] == oqo["filter_rows"] and {k: v for k, v in body.items() if k != "filter_rows"} == {k: v for k, v in oqo.items() if k != "filter_rows"}, f"{arm}/{p.stem}: only an ID restriction added")
            ok(all(f["column_id"] == "ids.openalex" for f in extra["filters"]) and len(batch) <= 100, f"{arm}/{p.stem}: <=100 OpenAlex IDs")
            got = {wid(x) for x in d["response"]["results"]}
            ok(d["response"]["meta"]["count"] == len(got) and got <= set(batch), f"{arm}/{p.stem}: complete batch")
            seen += batch
            found |= got
        ok(sorted(seen) == allids and sorted(found) == obs["arms"][arm]["recovered_ids"], f"{arm}: all IDs tested once; recovered IDs reproduced")
        ok(obs["arms"][arm]["export"]["eligible"] is False, f"{arm}: count above the 20,000 export cap, so no export")
    ok(set(obs["arms"]["A_title_abstract"]["recovered_ids"]) <= set(obs["arms"]["B_title_abstract_keywords"]["recovered_ids"]), "A recovered set within B")

    s = J("results/summary.json")
    with open(ROOT / "results/per_reference_retrieval.csv") as f:
        rows = list(csv.DictReader(f))
    ok(len(rows) == 143 and sum(int(r["in_openalex"]) for r in rows) == 141, "matrix: 143 rows, 141 in OpenAlex")
    for arm, v in s["arms"].items():
        k = sum(int(r[arm]) for r in rows)
        ok(k == v["recovered"] and v["meets_recall_threshold"] == (k >= 136) and v["count_at_most_screened"] == (v["api_count"] <= 13579), f"{arm}: {k}/143 and threshold flags")
    fac = J("results/facet_diagnostics.json")
    ok(fac["ids"] == allids, "facet diagnostics cover all matched and alternate IDs")
    for p in (ROOT / "archives/diagnostics").glob("*.json"):
        body = json.loads(p.read_text())["request"]["body"]["oql"]
        listed = body.split("openalex id is (", 1)[1].split(")", 1)[0].split(" or ")
        ok(set(listed) <= set(allids), f"diagnostic {p.stem} restricted to matched IDs")
    pr = J("results/pubmed_strategy_rerun.json")
    hits = set()
    for p in sorted((ROOT / "archives/pubmed").glob("esearch_batch_*.json")):
        hits |= set(json.loads(p.read_text())["response"]["esearchresult"]["idlist"])
    ok(sum(1 for r in pr["rows"] if r["pmid"] in hits) == pr["retrieved_by_pubmed_strategy_today"], "PubMed re-run tally reproduced from archives")

    key_file = ROOT.parent / ".env.txt"
    if key_file.exists():
        key = key_file.read_text().strip()
        ok(not [p for p in ROOT.rglob("*") if p.is_file() and key in p.read_text(errors="ignore")], "API key absent from every file")
    sums = (ROOT / "SHA256SUMS").read_text().splitlines()
    bad = [ln for ln in sums if hashlib.sha256((ROOT / ln.split("  ", 1)[1]).read_bytes()).hexdigest() != ln.split("  ", 1)[0]]
    ok(not bad, f"SHA256SUMS matches {len(sums)} files")
    failed = [m for c, m in checks if not c]
    print(f"{len(checks) - len(failed)}/{len(checks)} checks passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
