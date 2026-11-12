"""Verify saved evidence for the large transfer test; no API requests."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(name):
    return json.loads((ROOT / name).read_text())


def doi(value):
    return (value or "").lower().removeprefix("https://doi.org/").removeprefix("http://doi.org/")


def main():
    for line in (ROOT / "SHA256SUMS").read_text().splitlines():
        expected, name = line.split("  ", 1)
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
    frozen = read("freeze_manifest.json")
    for name, expected in frozen["sha256"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
    assert not frozen["benchmark_titles_inspected"] and not frozen["candidate_queries_executed"]
    dependency = read("implementation_dependencies.json")
    for name, expected in dependency["sha256"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
    source = read("results/benchmark_source.json")
    assert source["extracted_utc"] > frozen["frozen_at_utc"]
    assert source["source_sha256"] == read("source_provenance.json")["article"]["sha256"]
    originals = source["records"]
    assert len(originals) == len({r["reference_id"] for r in originals}) == 75
    original_by_ref = {r["reference_id"]: r for r in originals}
    matches = read("results/benchmark_matches.json")["records"]
    assert len(matches) == 75 and {r["reference_id"] for r in matches} == set(original_by_ref)
    for row in matches:
        ref = row["reference_id"]
        assert all(row[k] == value for k, value in original_by_ref[ref].items())
        raw = read(f"archives/matches/{ref}.json")
        assert raw["status"] == 200
        assert len(raw["response"]["results"]) == raw["response"]["meta"]["count"] == 1
        work = raw["response"]["results"][0]
        if row["doi"]:
            assert raw["request"]["params"]["filter"] == "doi:" + row["doi"]
            assert doi(work["doi"]) == doi(row["matched_doi"])
            if doi(row["doi"]) == doi(work["doi"]):
                assert row["match_status"] == "exact_doi"
            else:
                assert row["match_status"] == "doi_lookup_pmid_confirmed_alternate_doi"
                notes = read("results/matching_notes.json")["notes"]
                assert any(n["reference_id"] == ref and n["source_doi"] == row["doi"]
                           and n["returned_doi"] == work["doi"] and n["corroborating_pmid"] == row["pmid"] for n in notes)
        else:
            assert raw["request"]["params"]["filter"] == "pmid:" + row["pmid"]
            assert row["match_status"] == "exact_pmid"
        assert (work["ids"]["pmid"] or "").rstrip("/").rsplit("/", 1)[-1] == row["pmid"]
        assert row["openalex_id"] == work["id"]
        assert row["matched_title"] == work["display_name"]
    assert sum(r["match_status"] == "exact_doi" for r in matches) == 72
    assert sum(r["match_status"] == "doi_lookup_pmid_confirmed_alternate_doi" for r in matches) == 1
    ids = sorted({r["openalex_id"] for r in matches})
    assert len(ids) == 75
    restriction = {"join": "or", "filters": [{"column_id": "ids.openalex", "value": i} for i in ids]}
    matrix = list(csv.DictReader((ROOT / "results/per_article_retrieval.csv").open()))
    assert len(matrix) == 75 and {r["reference_id"] for r in matrix} == set(original_by_ref)
    assert {r["reference_id"]: r["openalex_id"] for r in matrix} == {r["reference_id"]: r["openalex_id"] for r in matches}
    summaries = read("results/summary.json")
    assert len(summaries) == 2
    retrieval = {}
    for s in summaries:
        label = s["strategy"]
        query = (ROOT / "queries" / (label + ".oql")).read_text().strip()
        envelope = read(f"archives/{label}/unrestricted_page_001.json")
        assert envelope["status"] == 200 and envelope["started_utc"] > frozen["frozen_at_utc"]
        assert envelope["request"] == {"method": "POST", "path": "/", "body": {
            "oql": query, "per_page": 200, "page": 1, "sort": "publication_date:asc",
            "select": "id,doi,display_name,publication_date,ids"}}
        total = envelope["response"]
        count = total["meta"]["count"]
        oqo = total["meta"]["x_query"]["oqo"]
        assert oqo["filter_rows"] == read(f"validation/{label}.json")["response"]["oqo"]["filter_rows"]
        member_env = read(f"archives/{label}/benchmark_membership.json")
        assert member_env["status"] == 200
        wanted = json.loads(json.dumps(oqo))
        wanted["filter_rows"].append(restriction)
        assert member_env["request"]["body"] == {"oqo": wanted, "per_page": 200, "select": "id,doi,display_name,publication_date"}
        member = member_env["response"]
        assert member["meta"]["x_query"]["oqo"]["filter_rows"] == wanted["filter_rows"]
        found = {r["id"] for r in member["results"]}
        assert len(found) == len(member["results"]) == member["meta"]["count"]
        assert found <= set(ids)
        retrieval[label] = found
        assert s["api_count"] == count
        assert s["original_records"] == s["matched_records"] == s["matched_distinct_ids"] == 75
        assert s["recovered_original"] == len(found)
        assert s["original_recall"] == s["matched_recall"] == len(found) / 75
        assert s["passes_recall_threshold"] == (len(found) >= 72)
        assert s["below_reported_screening_count"] == (count <= 67464)
        assert not s["historical_screening_count_is_unique"]
        assert s["missed_reference_ids"] == [r["reference_id"] for r in matches if r["openalex_id"] not in found]
        # These observations exceed the prespecified key-free full-export cap.
        assert count > 9800
        assert len(list((ROOT / "archives" / label).glob("unrestricted_page_*.json"))) == 1
        downloaded = {r["id"] for r in total["results"]}
        assert len(downloaded) == len(total["results"]) == s["downloaded_rows"] == s["distinct_downloaded_ids"] == 200
        assert s["export_pages"] == 1 and s["page_counts"] == [count]
        assert not s["terminal_empty_page"] and not s["complete_consistent_export"]
        assert s["benchmark_ids_in_downloaded_pages"] == len(downloaded & set(ids))
        assert s["recovery_evidence"].startswith("restricted_membership_only")
        for row in matrix:
            assert row[label] == str(row["openalex_id"] in found)
        print(f"{label}: {count:,} reported results; {len(found)}/75 ({len(found)/75:.1%}); full export NOT verified")
    by_ref = {r["reference_id"]: r["openalex_id"] for r in matches}
    diagnostics = read("results/clause_diagnostics.json")
    for case in diagnostics["results"]:
        raw = read(f"archives/diagnostics/{case['clause']}.json")
        assert raw["status"] == 200
        found = {r["id"] for r in raw["response"]["results"]}
        assert len(found) == raw["response"]["meta"]["count"]
        assert case["matches"] == {ref: by_ref[ref] in found for ref in case["matches"]}
    flow = read("results/source_flow_counts.json")
    assert sum(int(row[4]) for row in flow["table_cells"][1:]) == flow["sum_screening_cells"] == 51843
    assert flow["reported_main_text_screened"] == 67464 and flow["authors_warn_cross_category_duplicates"]
    a, b = (retrieval[s["strategy"]] for s in summaries)
    assert len(a - b) == 5 and len(b - a) == 2
    print("Verified freeze, 75 identifier mappings, unchanged query restrictions, membership, partial-export labels and diagnostics.")


if __name__ == "__main__":
    main()
