"""Recalculate the transfer test offline; standard library only, no network."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(name):
    return json.loads((ROOT / name).read_text())


def doi(value):
    return value.lower().removeprefix("https://doi.org/").removeprefix("http://doi.org/")


def main():
    for line in (ROOT / "SHA256SUMS").read_text().splitlines():
        expected, name = line.split("  ", 1)
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
    freeze = read("freeze_manifest.json")
    for name, expected in freeze["sha256"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
    assert not freeze["benchmark_titles_inspected"] and not freeze["candidate_queries_executed"]
    source = read("results/benchmark_source.json")
    rows = source["records"]
    original_ids = {r["reference_id"] for r in rows}
    assert len(rows) == len(original_ids) == 29
    assert source["source_sha256"] == read("source_provenance.json")["article"]["sha256"]
    assert source["extracted_utc"] > freeze["frozen_at_utc"]
    matches = read("results/benchmark_matches.json")["records"]
    assert len(matches) == 29 and {r["reference_id"] for r in matches} == original_ids
    source_by_ref = {r["reference_id"]: r for r in rows}
    for row in matches:
        ref = row["reference_id"]
        assert all(row[k] == v for k, v in source_by_ref[ref].items())
        record = read(f"archives/matches/{ref}.json")
        assert record["status"] == 200
        assert record["request"]["params"]["filter"] == "doi:" + row["doi"]
        raw = record["response"]
        assert len(raw["results"]) == raw["meta"]["count"] == 1
        work = raw["results"][0]
        assert doi(work["doi"]) == doi(row["doi"]) == doi(row["matched_doi"])
        assert work["id"] == row["openalex_id"] and work["display_name"] == row["matched_title"]
        assert row["match_status"] == "exact_doi"
    assert len({r["openalex_id"] for r in matches}) == 29
    matrix = list(csv.DictReader((ROOT / "results/per_article_retrieval.csv").open()))
    assert len(matrix) == 29 and {r["reference_id"] for r in matrix} == original_ids
    assert {r["reference_id"]: r["openalex_id"] for r in matrix} == {r["reference_id"]: r["openalex_id"] for r in matches}
    summaries = read("results/summary.json")
    assert len(summaries) == 3
    all_export_times = []
    for summary in summaries:
        label = summary["strategy"]
        q = (ROOT / "queries" / (label + ".oql")).read_text().strip()
        parsed = read(f"validation/{label}.json")["response"]["oqo"]
        files = sorted((ROOT / "archives" / (label + "_numbered")).glob("page_*.json"))
        ids, counts, batches = [], [], []
        for page, file in enumerate(files, 1):
            envelope = json.loads(file.read_text())
            assert envelope["status"] == 200
            assert envelope["started_utc"] > freeze["frozen_at_utc"]
            all_export_times.append(envelope["finished_utc"])
            params = envelope["request"]["params"]
            assert params == {"oql": q, "per_page": 200, "page": page,
                              "sort": "publication_date:asc", "select": "id,doi,display_name,publication_date,ids"}
            v = envelope["response"]
            executed = v["meta"]["x_query"]["oqo"]
            assert executed["filter_rows"] == parsed["filter_rows"]
            assert executed["get_rows"] == "works"
            assert executed["sort_by"] == [{"column_id": "publication_date", "direction": "asc"}]
            batch = [w["id"] for w in v["results"]]
            batches.append(batch)
            ids.extend(batch)
            counts.append(v["meta"]["count"])
        assert batches[-1] == [] and all(batches[:-1])
        assert all(len(batch) == 200 for batch in batches[:-2])
        assert len(counts) == summary["pages"] == summary["terminal_empty_page"]
        assert counts == summary["page_counts"]
        assert len(set(counts)) == 1
        assert len(ids) == len(set(ids)) == counts[0] == summary["api_count"]
        assert summary["downloaded_rows"] == summary["distinct_ids"] == len(ids)
        assert summary["duplicate_ids"] == [] and summary["complete_consistent_export"]
        actual = set(ids)
        found = sum(r["openalex_id"] in actual for r in matches)
        missed = [r["reference_id"] for r in matches if r["openalex_id"] not in actual]
        assert found == summary["recovered_original"]
        assert summary["original_records"] == summary["matched_records"] == summary["matched_distinct_ids"] == 29
        assert found / 29 == summary["original_recall"] == summary["matched_recall"]
        assert missed == summary["missed_reference_ids"]
        assert summary["meets_numerical_threshold"] == (found / 29 > .95 and counts[0] <= 1974)
        for row in matrix:
            assert row[label] == str(row["openalex_id"] in actual)
        print(f"{label}: {len(ids):,} unique IDs; {found}/29 ({found / 29:.1%}); threshold={summary['meets_numerical_threshold']}")
    # All matching occurred after the unrestricted exports were finished.
    match_files = list((ROOT / "archives/matches").glob("*.json"))
    assert min(json.loads(f.read_text())["started_utc"] for f in match_files) > max(all_export_times)
    id_by_ref = {r["reference_id"]: r["openalex_id"] for r in matches}
    for name in ["clause_diagnostics", "term_diagnostics"]:
        for case in read(f"results/{name}.json")["results"]:
            envelope = read(f"archives/diagnostics/{case['clause']}.json")
            assert envelope["status"] == 200
            v = envelope["response"]
            ids = {w["id"] for w in v["results"]}
            assert len(ids) == v["meta"]["count"]
            assert case["matches"] == {ref: id_by_ref[ref] in ids for ref in case["matches"]}
    print("Freeze hashes, 29 DOI mappings, exports, matrix, thresholds and diagnostics verified offline.")


if __name__ == "__main__":
    main()
