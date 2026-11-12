"""Offline verifier: standard library only, no network requests.

    python3 inclusion_sen_benchmark_2026-11-13/verify.py
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
    ok(man["candidate_queries_executed"] is False and man["benchmark_references_inspected"] is False, "manifest: nothing executed or inspected before freeze")
    r = subprocess.run([sys.executable, str(ROOT / "build_queries.py"), "--check"], capture_output=True, text=True)
    ok(r.returncode == 0, "builder reproduces frozen queries and source assertions pass")

    src = J("results/benchmark_source.json")
    ok(len(src["records"]) == 94 and len({s["reference_list_entry"] for s in src["records"]}) == 94, "94 studies, each paired to a distinct reference entry")
    ok(len(src["reference_entries_not_in_study_sheet"]) == 3, "3 non-study reference entries documented")

    m = J("results/benchmark_matches.json")
    looked = set()
    for p in (ROOT / "archives/matching").glob("oa_*.json"):
        d = json.loads(p.read_text())
        resp = d["response"] if d["status"] == 200 else {}
        if resp.get("id"):
            looked.add(wid(resp))
        for x in resp.get("results", []):
            looked.add(wid(x))
    ids = sorted({x["openalex_id"] for x in m["records"] if x["openalex_id"]})
    ok(all(x["openalex_id"] in looked for x in m["records"] if x["openalex_id"]), "every match backed by an archived OpenAlex response")
    ok(len(ids) == m["in_openalex"] == 79, "79 studies in OpenAlex")

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

    a = set(obs["arms"]["A_ebsco_text_core"]["recovered_ids"]); b = set(obs["arms"]["B_web_of_science_exact"]["recovered_ids"]); c = set(obs["arms"]["C_union_of_text_cores"]["recovered_ids"])
    ok(b <= a <= c, "nesting B within A within C holds for recovered studies")
    ok(set(J("results/B_web_of_science_exact_export_ids.json")) <= set(J("results/A_ebsco_text_core_export_ids.json")), "B export is a subset of A export")

    s = J("results/summary.json")
    with open(ROOT / "results/per_study_retrieval.csv") as f:
        rows = list(csv.DictReader(f))
    ok(len(rows) == 94 and sum(int(r["in_openalex"]) for r in rows) == 79, "matrix: 94 rows, 79 in OpenAlex")
    for arm, v in s["arms"].items():
        k = sum(int(r[arm]) for r in rows)
        ok(k == v["recovered_studies"] and v["meets_recall_threshold"] == (k >= 90), f"{arm}: {k}/94 and threshold flag")
    fac = J("results/facet_diagnostics.json")
    ok(fac["ids"] == ids, "facet diagnostics cover the 79 matched IDs")
    for p in (ROOT / "archives/diagnostics").glob("*.json"):
        ok(json.loads(p.read_text())["request"]["body"]["oql"].startswith("get works where openalex id is (" + " or ".join(ids) + ")"), f"diagnostic {p.stem} restricted to matched IDs")

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
