"""Run the frozen large benchmark explicitly; no live activity on import."""
import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
HELPERS = ROOT.parent / "transfer_benchmark_2026-11-12/run_test.py"
spec = importlib.util.spec_from_file_location("insomnia_evidence_helpers", HELPERS)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)
helpers.ROOT = ROOT
save, now = helpers.save, helpers.now


def post(label, body):
    dest = ROOT / "archives" / (label + ".json")
    request = {"method": "POST", "path": "/", "body": body}
    if dest.exists():
        old = json.loads(dest.read_text())
        assert old["request"] == request
        if old["status"] == 200:
            return old["response"]
        raise RuntimeError(f"Previous failure preserved: {dest}")
    headers = {"Content-Type": "application/json", "User-Agent": "OpenAlex-independent-review-benchmark/1.0"}
    if helpers.os.environ.get("OPENALEX_API_KEY"):
        headers["Authorization"] = "Bearer " + helpers.os.environ["OPENALEX_API_KEY"]
    attempts = []
    for attempt in range(3):
        started = now()
        try:
            req = urllib.request.Request("https://api.openalex.org/", data=json.dumps(body).encode(), headers=headers)
            with urllib.request.urlopen(req, timeout=55) as r:
                status, raw = r.status, r.read().decode()
        except urllib.error.HTTPError as e:
            status, raw = e.code, e.read().decode()
        except (OSError, TimeoutError) as e:
            status, raw = 0, json.dumps({"transport_error": type(e).__name__})
        try:
            response = json.loads(raw)
        except ValueError:
            response = {"non_json_response": raw}
        attempts.append({"started_utc": started, "finished_utc": now(), "status": status, "response": response})
        if status not in (0, 429, 500, 502, 503, 504) or attempt == 2:
            break
        helpers.time.sleep(2 * (attempt + 1))
    save(dest, {"request": request, **attempts[-1], "attempts": attempts[:-1]})
    if status != 200:
        raise RuntimeError(f"HTTP {status}; response preserved at {dest}")
    return response


def extract(source):
    expected = json.loads((ROOT / "source_provenance.json").read_text())["article"]["sha256"]
    assert hashlib.sha256(source.read_bytes()).hexdigest() == expected
    article = ET.parse(source).getroot()
    table = article.find(".//table-wrap[@id='Tab1']")
    refids = list(dict.fromkeys(x.get("rid") for x in table.findall(".//xref[@ref-type='bibr']")))
    assert len(refids) == 75
    rows = []
    for refid in refids:
        ref = article.find(f".//ref[@id='{refid}']")
        title = ref.find(".//article-title")
        pubids = {x.get("pub-id-type"): "".join(x.itertext()).strip() for x in ref.findall(".//pub-id")}
        citation = ref.find("mixed-citation")
        if citation is None:
            citation = ref.find("element-citation")
        rows.append({"reference_id": refid, "title": "".join(title.itertext()) if title is not None else "",
                     "year": ref.findtext(".//year"), "doi": pubids.get("doi", ""), "pmid": pubids.get("pmid", ""),
                     "source_citation": " ".join(citation.itertext()) if citation is not None else ""})
    dest = ROOT / "results/benchmark_source.json"
    if dest.exists():
        assert json.loads(dest.read_text())["records"] == rows
    else:
        save(dest, {"extracted_utc": now(), "source_table": "Tab1", "source_sha256": expected, "records": rows})
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source_xml", type=Path)
    args = parser.parse_args()
    helpers.check_freeze()
    rows = extract(args.source_xml)
    print(f"Extracted {len(rows)} originals; {sum(bool(r['doi']) for r in rows)} DOIs; {sum(bool(r['pmid']) for r in rows)} PMIDs", flush=True)
    observations = {}
    for f in sorted((ROOT / "queries").glob("*.oql")):
        body = {"oql": f.read_text().strip(), "per_page": 200, "page": 1,
                "sort": "publication_date:asc", "select": "id,doi,display_name,publication_date,ids"}
        total = post(f"{f.stem}/unrestricted_page_001", body)
        assert isinstance(total["results"], list) and "count" in total["meta"]
        observations[f.stem] = (body, total)
        print(f.stem, "unrestricted count", total["meta"]["count"], flush=True)
    matched = helpers.match_benchmark(rows)
    notes = []
    for row in matched:
        if row.get("openalex_id") and row["doi"]:
            original_doi = row["doi"].lower().removeprefix("https://doi.org/")
            returned_doi = (row.get("matched_doi") or "").lower().removeprefix("https://doi.org/")
            if original_doi != returned_doi:
                raw = json.loads((ROOT / "archives/matches" / (row["reference_id"] + ".json")).read_text())
                work = raw["response"]["results"][0]
                returned_pmid = (work["ids"].get("pmid") or "").rstrip("/").rsplit("/", 1)[-1]
                assert row["pmid"] and returned_pmid == row["pmid"], "DOI discrepancy needs manual adjudication"
                row["match_status"] = "doi_lookup_pmid_confirmed_alternate_doi"
                notes.append({"reference_id": row["reference_id"], "source_doi": row["doi"],
                              "returned_doi": row["matched_doi"], "corroborating_pmid": row["pmid"],
                              "reason": "Source DOI filter returned a different canonical DOI; source PMID agrees exactly."})
    save(ROOT / "results/benchmark_matches.json", {"records": matched})
    save(ROOT / "results/matching_notes.json", {"notes": notes})
    print("Matched", sum(bool(r["openalex_id"]) for r in matched), "of", len(rows), flush=True)
    ids = sorted({r["openalex_id"] for r in matched if r["openalex_id"]})
    restrict = {"join": "or", "filters": [{"column_id": "ids.openalex", "value": i} for i in ids]}
    summary, recovered = [], {}
    for label, (body, total) in observations.items():
        oqo = json.loads(json.dumps(total["meta"]["x_query"]["oqo"]))
        oqo["filter_rows"].append(restrict)
        member = post(f"{label}/benchmark_membership", {"oqo": oqo, "per_page": 200, "select": "id,doi,display_name,publication_date"})
        found = {r["id"] for r in member["results"]}
        assert len(found) == len(member["results"]) == member["meta"]["count"] and found <= set(ids)
        recovered[label] = found
        count = total["meta"]["count"]
        downloaded = list(total["results"])
        counts, pages = [count], 1
        complete, terminal = False, False
        if count <= 9800:
            while True:
                pages += 1
                v = post(f"{label}/unrestricted_page_{pages:03d}", {**body, "page": pages})
                counts.append(v["meta"]["count"])
                downloaded.extend(v["results"])
                if not v["results"]:
                    terminal = True
                    break
                if pages >= 50:
                    raise RuntimeError("Numbered export cap reached")
            complete = len(set(counts)) == 1 and len(downloaded) == len({r["id"] for r in downloaded}) == count
        exported = {r["id"] for r in downloaded}
        if complete:
            assert found == exported & set(ids), "Unrestricted export and membership disagree"
        found_original = sum(r["openalex_id"] in found for r in matched)
        nmatched = sum(bool(r["openalex_id"]) for r in matched)
        row = {"strategy": label, "api_count": count, "original_records": 75, "matched_records": nmatched,
               "matched_distinct_ids": len(ids), "recovered_original": found_original,
               "original_recall": found_original / 75, "matched_recall": found_original / nmatched if nmatched else None,
               "passes_recall_threshold": found_original >= 72,
               "below_reported_screening_count": count <= 67464,
               "historical_screening_count_is_unique": False,
               "downloaded_rows": len(downloaded), "distinct_downloaded_ids": len(exported),
               "export_pages": pages, "page_counts": counts, "terminal_empty_page": terminal,
               "complete_consistent_export": complete,
               "benchmark_ids_in_downloaded_pages": len(exported & set(ids)),
               "recovery_evidence": "unrestricted_export_and_restricted_membership" if complete else "restricted_membership_only; unrestricted first page and count retained",
               "missed_reference_ids": [r["reference_id"] for r in matched if r["openalex_id"] not in found]}
        summary.append(row)
        print(json.dumps(row), flush=True)
    save(ROOT / "results/summary.json", summary)
    matrix = [{**r, **{label: bool(r["openalex_id"] and r["openalex_id"] in found) for label, found in recovered.items()}} for r in matched]
    with (ROOT / "results/per_article_retrieval.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(dict.fromkeys(k for r in matrix for k in r)))
        writer.writeheader()
        writer.writerows(matrix)


if __name__ == "__main__":
    main()
