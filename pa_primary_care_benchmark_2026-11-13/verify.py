"""Offline verifier: standard library only, no network requests.

    python3 pa_primary_care_benchmark_2026-11-13/verify.py
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
    ok(man["candidate_queries_executed"] is False and man["benchmark_list_opened"] is False, "manifest: nothing executed or inspected before freeze")
    r = subprocess.run([sys.executable, str(ROOT / "build_queries.py"), "--check"], capture_output=True, text=True)
    ok(r.returncode == 0, "builder reproduces frozen queries and source assertions pass")

    src = J("results/benchmark_source.json")
    ok(len(src["studies"]) == 51 == src["stated_included_studies"] and [r["article_ref_number"] for r in src["records"]] == list(range(20, 71)), "51 studies citing 51 distinct references (article refs 20-70)")
    ok(sorted(r for st in src["studies"] for r in st["ref_ids"]) == sorted(r["ref_id"] for r in src["records"] for _ in r["study_ids"]), "study-to-reference mapping consistent both ways")
    m = J("results/benchmark_matches.json")
    r = subprocess.run([sys.executable, str(ROOT / "adjudicate.py")], capture_output=True, text=True)
    ok(r.returncode == 0 and J("results/benchmark_matches.json") == m, "adjudication reproduces benchmark_matches.json")
    looked = set()
    for p in list((ROOT / "archives/matching").glob("oa_*.json")) + list((ROOT / "archives/matching").glob("correction_*.json")):
        d = json.loads(p.read_text())
        resp = d["response"] if d["status"] == 200 else {}
        if resp.get("id"):
            looked.add(wid(resp))
        for x in resp.get("results", []):
            looked.add(wid(x))
    ids = sorted({x["openalex_id"] for x in m["records"] if x["openalex_id"]})
    ok(all(i in looked for i in ids) and len(ids) == 48, "48 distinct matches, each backed by an archived OpenAlex response")
    ok(all(x["citation_title_agreement"] >= 0.9 for x in m["records"] if x["decision"] == "accepted_auto"), "every automatic match agrees with its full citation")
    ok(sorted((x["ref_id"], x["decision"]) for x in m["records"] if x["decision"] != "accepted_auto") == [("PA-026", "not_in_openalex"), ("PA-044", "accepted_manual"), ("PA-051", "not_in_openalex"), ("PA-058", "not_in_openalex"), ("PA-060", "accepted_manual")], "two manual acceptances and three documented absences")

    obs = J("results/run_observations.json")
    for q in sorted((ROOT / "queries").glob("*.oql")):
        arm = q.stem
        first = J(f"archives/{arm}/unrestricted_cursor_001.json")
        ok(first["request"]["method"] == "POST" and first["request"]["body"]["oql"] == q.read_text().strip(), f"{arm}: frozen OQL sent by POST")
        oqo, count = first["response"]["meta"]["x_query"]["oqo"], first["response"]["meta"]["count"]
        ok(oqo["filter_rows"] == J(f"validation/{arm}.query.json")["oqo"]["filter_rows"], f"{arm}: executed filters equal pre-freeze validation")
        rt = J(f"archives/{arm}/oqo_roundtrip.json")
        ok(rt["request"]["body"]["oqo"] == oqo and rt["response"]["meta"]["count"] == count == obs["arms"][arm]["count"], f"{arm}: OQO round-trip count equal")
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
        ok(sorted(seen) == ids and sorted(found) == obs["arms"][arm]["recovered_ids"], f"{arm}: all IDs tested once; recovered IDs reproduced")
        e = obs["arms"][arm]["export"]
        if e["attempted"]:
            pages = sorted((ROOT / f"archives/{arm}").glob("unrestricted_cursor_*.json"))
            rows, counts = [], set()
            for p in pages:
                d = json.loads(p.read_text())
                ok(d["request"]["body"]["oql"] == q.read_text().strip(), f"{arm}/{p.stem}: same OQL")
                rows += [wid(x) for x in d["response"]["results"]]
                counts.add(d["response"]["meta"]["count"])
            ok(len(rows) == len(set(rows)) == count and counts == {count}, f"{arm}: complete export of {count} distinct IDs")
            ok(sorted(set(rows) & set(ids)) == sorted(found), f"{arm}: export intersection equals restricted membership")
            exp = J(f"results/{arm}_export_ids.json")
            ok(exp == sorted(set(rows)), f"{arm}: export ID file reproduced")
        else:
            ok(count > 20000, f"{arm}: no export because count exceeds the 20,000 cap")
            p1 = {wid(x) for x in first["response"]["results"]}
            p2 = J(f"archives/{arm}/unrestricted_cursor_002.json")["response"]
            ok(p2["meta"]["count"] == count and not ({wid(x) for x in p2["results"]} & p1), f"{arm}: cursor page 2 consistent and disjoint")

    ok(set(obs["arms"]["A_title_abstract"]["recovered_ids"]) <= set(obs["arms"]["B_title_abstract_keywords"]["recovered_ids"]), "A recovered set within B")
    ok(set(J("results/A_title_abstract_export_ids.json")) <= set(J("results/B_title_abstract_keywords_export_ids.json")), "A export within B export")

    s = J("results/summary.json")
    with open(ROOT / "results/per_study_retrieval.csv") as f:
        rows = list(csv.DictReader(f))
    ok(len(rows) == 51, "matrix: 51 study rows")
    for arm, v in s["arms"].items():
        k = sum(int(r[arm]) for r in rows)
        found = set(obs["arms"][arm]["recovered_ids"])
        k2 = sum(1 for st in src["studies"] if any(next(x["openalex_id"] for x in m["records"] if x["ref_id"] == r) in found for r in st["ref_ids"]))
        ok(k == k2 == v["studies_recovered"] and v["references_recovered"] == len(found) and v["meets_recall_threshold"] == (k >= 49) and v["count_at_most_screened"] == (v["api_count"] <= 14566), f"{arm}: {k}/51 studies and threshold flags")
    fac = J("results/facet_diagnostics.json")
    ok(fac["ids"] == ids, "facet diagnostics cover the 48 matched IDs")
    import build_queries as bq  # noqa: E402
    qa, b = bq.build()
    for p in (ROOT / "archives/diagnostics").glob("*.json"):
        d = json.loads(p.read_text())
        if p.stem == "pubmed_mesh_pt_efetch":
            ok("Abstract" not in json.dumps(d["response_slim"]) and d["url"].startswith("https://eutils.ncbi.nlm.nih.gov/"), "PubMed probe archived without abstracts")
            continue
        body = d["request"]["body"]["oql"]
        listed = body.split("openalex id is (", 1)[1].split(")", 1)[0].split(" or ")
        ok(set(listed) <= set(ids), f"diagnostic {p.stem} restricted to matched IDs")

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
