"""Post-evaluation clause diagnostics, explicitly separate from frozen searches."""
import json
from run_test import ROOT, now, request, save


def main():
    summary = json.loads((ROOT / "results/summary.json").read_text())
    misses = set().union(*(set(s["missed_reference_ids"]) for s in summary))
    rows = json.loads((ROOT / "results/benchmark_matches.json").read_text())["records"]
    target = [r for r in rows if r["reference_id"] in misses]
    idfilter = {"join": "or", "filters": [{"column_id": "ids.openalex", "value": r["openalex_id"]} for r in target]}
    a = json.loads((ROOT / "validation/A_fuller_embase.json").read_text())["response"]["oqo"]
    b = json.loads((ROOT / "validation/B_compact.json").read_text())["response"]["oqo"]
    cases = dict(zip(["date", "fuller_population", "fuller_therapy", "delivery", "trial_filter"], a["filter_rows"]))
    cases.update({"compact_population": b["filter_rows"][1], "compact_therapy": b["filter_rows"][2]})
    results = []
    for name, clause in cases.items():
        query = {"get_rows": "works", "filter_rows": [idfilter, clause]}
        v = request("diagnostics/" + name, "/", {"oqo": json.dumps(query, separators=(",", ":")),
                                                    "per_page": 200, "select": "id,display_name"})
        ids = {w["id"] for w in v["results"]}
        assert v["meta"]["count"] == len(ids)
        result = {"clause": name, "matches": {r["reference_id"]: r["openalex_id"] in ids for r in target}}
        results.append(result)
        print(result, flush=True)
    save(ROOT / "results/clause_diagnostics.json", {"phase": "post-freeze, after initial evaluation; no query repair",
                                                       "completed_utc": now(), "results": results})
    terms = {
        "therapy_literal": {"column_id": "title_abstract_keywords.search.exact", "value": '"cognitive behavioral therapy"', "operator": "has"},
        "population_literal": {"column_id": "title_abstract_keywords.search.exact", "value": '"sleep disorders"', "operator": "has"},
        "online_bare": {"column_id": "title_abstract_keywords.search", "value": "online", "operator": "has"},
        "on_line_literal": {"column_id": "title_abstract_keywords.search.exact", "value": '"on-line"', "operator": "has"},
        "cbti_keyword_id": {"column_id": "keywords.id", "value": "cognitive-behavioral-therapy-for-insomnia"},
    }
    results = []
    for name, clause in terms.items():
        query = {"get_rows": "works", "filter_rows": [idfilter, clause]}
        v = request("diagnostics/" + name, "/", {"oqo": json.dumps(query, separators=(",", ":")),
                                                    "per_page": 200, "select": "id,display_name"})
        ids = {w["id"] for w in v["results"]}
        assert v["meta"]["count"] == len(ids)
        results.append({"clause": name, "matches": {r["reference_id"]: r["openalex_id"] in ids for r in target}})
    save(ROOT / "results/term_diagnostics.json", {
        "phase": "exploratory term-level checks prompted by visible keyword labels after evaluation",
        "completed_utc": now(), "results": results})


if __name__ == "__main__":
    main()
