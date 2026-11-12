"""Explicit live runner for the frozen transfer test; never runs on import.

Standard library only. OPENALEX_API_KEY is optional and never archived.
Usage: python run_test.py /path/to/PMC11903857.xml
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def request(label, path, params):
    dest = ROOT / "archives" / (label + ".json")
    # Resume from saved evidence, rather than overwrite an earlier observation.
    if dest.exists():
        previous = json.loads(dest.read_text())
        assert previous["request"] == {"path": path, "params": params}
        if previous["status"] == 200:
            return previous["response"]
        raise RuntimeError(f"Earlier failed request retained: {dest}")
    headers = {"User-Agent": "OpenAlex-independent-review-benchmark/1.0"}
    if os.environ.get("OPENALEX_API_KEY"):
        headers["Authorization"] = "Bearer " + os.environ["OPENALEX_API_KEY"]
    url = "https://api.openalex.org" + path + "?" + urllib.parse.urlencode(params)
    attempts = []
    for attempt in range(3):
        started = now()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=45) as r:
                status, raw = r.status, r.read().decode()
        except urllib.error.HTTPError as e:
            status, raw = e.code, e.read().decode()
        except (OSError, TimeoutError) as e:
            status, raw = 0, json.dumps({"transport_error": type(e).__name__})
        try:
            value = json.loads(raw)
        except ValueError:
            value = {"non_json_response": raw}
        attempts.append({"started_utc": started, "finished_utc": now(), "status": status, "response": value})
        if status not in (0, 429, 500, 502, 503, 504) or attempt == 2:
            break
        time.sleep(2 * (attempt + 1))
    save(dest, {"request": {"path": path, "params": params}, **attempts[-1], "attempts": attempts[:-1]})
    if status != 200:
        raise RuntimeError(f"HTTP {status}; evidence saved at {dest}")
    return value


def check_freeze():
    manifest = json.loads((ROOT / "freeze_manifest.json").read_text())
    for name, expected in manifest["sha256"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name


def extract_benchmark(source):
    expected = json.loads((ROOT / "source_provenance.json").read_text())["article"]["sha256"]
    assert hashlib.sha256(source.read_bytes()).hexdigest() == expected
    article = ET.parse(source).getroot()
    table = article.find(".//table-wrap[@id='Tab1']")
    rows = []
    for tr in table.findall(".//tbody/tr"):
        cell = tr.find("td")
        refs = cell.findall(".//xref[@ref-type='bibr']")
        assert len(refs) == 1
        rid = refs[0].get("rid")
        ref = article.find(f".//ref[@id='{rid}']")
        title = ref.find(".//article-title")
        year = ref.findtext(".//year")
        title_text = "".join(title.itertext()) if title is not None else ""
        if not title_text:
            mixed = ref.find("mixed-citation")
            # Four Sleep citations are unstructured in the publisher XML.
            # Their author/title text precedes the italic journal name.
            title_text = mixed.text.split("et al. ", 1)[1].strip().rstrip(".")
            year = re.search(r"\((\d{4})\)", " ".join(mixed.itertext()))[1]
        ids = {x.get("pub-id-type"): "".join(x.itertext()).strip() for x in ref.findall(".//pub-id")}
        rows.append({"reference_id": rid, "table_label": " ".join(cell.itertext()),
                     "title": title_text,
                     "year": year, "doi": ids.get("doi", ""), "pmid": ids.get("pmid", "")})
    assert len(rows) == len({r["reference_id"] for r in rows}) == 29
    dest = ROOT / "results" / "benchmark_source.json"
    if dest.exists():
        assert json.loads(dest.read_text())["records"] == rows
    else:
        save(dest, {"extracted_utc": now(), "source_table": "Tab1", "source_sha256": expected, "records": rows})
    return rows


def export_query(query_file):
    label = query_file.stem
    q = query_file.read_text().strip()
    rows, counts, pages = [], [], 0
    while True:
        pages += 1
        if pages > 50:
            raise RuntimeError("Numbered export exceeds 10,000 rows; a key is required for cursor export")
        params = {"oql": q, "per_page": 200, "page": pages,
                  "sort": "publication_date:asc", "select": "id,doi,display_name,publication_date,ids"}
        v = request(f"{label}_numbered/page_{pages:03d}", "/", params)
        assert isinstance(v.get("results"), list) and "count" in v["meta"]
        counts.append(v["meta"]["count"])
        rows.extend(v["results"])
        print(f"{label}: page {pages}, {len(rows)} rows, total {counts[-1]}", flush=True)
        if not v["results"]:
            break
    ids = [r["id"] for r in rows]
    info = {"strategy": label, "api_count": counts[0], "page_counts": counts,
            "pages": pages, "downloaded_rows": len(ids), "distinct_ids": len(set(ids)),
            "duplicate_ids": sorted({i for i in ids if ids.count(i) > 1}),
            "pagination_mode": "numbered_fallback", "terminal_empty_page": pages,
            "complete_consistent_export": len(set(counts)) == 1 and counts[0] == len(ids) == len(set(ids))}
    save(ROOT / "results" / (label + "_export.json"), info)
    return info, {r["id"]: r for r in rows}


def match_benchmark(rows):
    matched = []
    fields = "id,doi,display_name,publication_year,publication_date,ids,abstract_inverted_index,keywords,primary_topic,is_retracted"
    for row in rows:
        if row["doi"]:
            identifier = "doi:" + row["doi"]
        elif row["pmid"]:
            identifier = "pmid:" + row["pmid"]
        else:
            matched.append({**row, "openalex_id": "", "match_status": "needs_manual_matching"})
            continue
        v = request("matches/" + row["reference_id"], "/works", {"filter": identifier, "per_page": 200, "select": fields})
        hits = v.get("results", [])
        if len(hits) == 1 and v["meta"]["count"] == 1:
            work = hits[0]
            matched.append({**row, "openalex_id": work["id"], "matched_title": work["display_name"],
                            "matched_doi": work["doi"], "matched_year": work["publication_year"],
                            "match_status": "exact_doi" if row["doi"] else "exact_pmid"})
        else:
            matched.append({**row, "openalex_id": "", "match_status": "unmatched" if not hits else "ambiguous"})
    save(ROOT / "results" / "benchmark_matches.json", {"records": matched})
    return matched


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source_xml", type=Path)
    args = parser.parse_args()
    check_freeze()
    rows = extract_benchmark(args.source_xml)
    # Finish unrestricted searches before matching and inspecting any misses.
    exports = {f.stem: export_query(f) for f in sorted((ROOT / "queries").glob("*.oql"))}
    matched = match_benchmark(rows)
    matrix = []
    for row in matched:
        matrix.append({**row, **{label: bool(row["openalex_id"] and row["openalex_id"] in works)
                               for label, (_, works) in exports.items()}})
    dest = ROOT / "results" / "per_article_retrieval.csv"
    with dest.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(dict.fromkeys(k for r in matrix for k in r)))
        writer.writeheader()
        writer.writerows(matrix)
    summary = []
    for label, (info, works) in exports.items():
        found = sum(r[label] for r in matrix)
        nmatched = sum(bool(r["openalex_id"]) for r in matrix)
        summary.append({**info, "original_records": len(matrix), "matched_records": nmatched,
                        "matched_distinct_ids": len({r["openalex_id"] for r in matrix if r["openalex_id"]}),
                        "recovered_original": found, "original_recall": found / len(matrix),
                        "matched_recall": found / nmatched if nmatched else None,
                        "meets_numerical_threshold": found / len(matrix) > .95 and info["api_count"] <= 1974,
                        "missed_reference_ids": [r["reference_id"] for r in matrix if not r[label]]})
    save(ROOT / "results" / "summary.json", summary)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
