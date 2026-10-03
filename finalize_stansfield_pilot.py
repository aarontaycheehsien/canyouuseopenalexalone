"""Create the pilot results and protocol from saved evidence, with focused checks."""
import csv
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'stansfield_pilot'
read=lambda p:json.loads((OUT/p).read_text(encoding='utf-8'))
refs=read('reference_records.json')
members=read('membership_summary.json')
baseline=read('legacy_country_normalization/summary.json')
orders=read('order_diagnostics/summary.json')
validation=json.loads((ROOT/'oql_validation/authenticated_2026-10-04/summary.json').read_text(encoding='utf-8'))
primary=[r for r in refs if r['primary']]
secondary=refs
matched=[r for r in refs if r['current_openalex_id']]
assert len(refs)==133 and len(primary)==131
assert len(matched)==130 and len({r['current_openalex_id'] for r in matched})==130
assert all(r['within_date_window'] for r in matched)
assert baseline['known_union_matches_nine_classic_searches']
assert sum(r['pubmed_retrieved'] for r in primary)==117
metadata={r['id'].rsplit('/',1)[-1]:r for r in read('current_reference_metadata.json')}
for ref in matched:
    observed=(metadata[ref['current_openalex_id']].get('ids',{}).get('pmid') or '').rsplit('/',1)[-1]
    if ref.get('pmid') and observed:assert observed==ref['pmid']
year_differences=sum(r['source_year']!=r['current_year'] for r in matched)
for a,b in [('oql_restored','oql_keywords'),('oql_keywords','oql_no_geography')]:
    assert set(members[a]['returned_known_ids'])<=set(members[b]['returned_known_ids'])
fields=list(dict.fromkeys(k for r in refs for k in r))
with (OUT/'reference_retrieval.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(refs)
summary=[]
for name,item in [('legacy_union_normalized',baseline)]+[(k,members[k]) for k in ['oql_restored','oql_keywords','oql_fulltext','oql_no_geography']]:
    complete=item.get('finite_complete',False)
    summary.append({'arm':name,'api_reported_query_count':item.get('total_query_count'),
      'reference_membership_complete':complete,
      'primary_retrieved':item.get('primary_retrieved') if complete else None,
      'primary_recall':item.get('primary_retrieved',0)/131 if complete else None,
      'secondary_retrieved':item.get('secondary_retrieved') if complete else None,
      'secondary_recall':item.get('secondary_retrieved',0)/133 if complete else None,
      'native_ranking_status':'unvalidated','rank_metrics':None})
with (OUT/'results_summary.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
(OUT/'results_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
corrections=[{k:r.get(k) for k in ['eppi_id','title','pmid','original_openalex_id','current_openalex_id','match_method']} for r in refs if r['current_openalex_id'] and r['current_openalex_id']!=r['original_openalex_id']]
(OUT/'identity_corrections.json').write_text(json.dumps(corrections,indent=2,ensure_ascii=False),encoding='utf-8')
unresolved=[r for r in refs if not r['current_openalex_id']]
table='\n'.join('| '+label+' | '+(f"{x['api_reported_query_count']:,}" if x['api_reported_query_count'] is not None else 'Unavailable')+' | '+(f"{x['primary_retrieved']}/131 ({x['primary_recall']:.1%})" if x['primary_recall'] is not None else 'Unavailable')+' | '+(f"{x['secondary_retrieved']}/133 ({x['secondary_recall']:.1%})" if x['secondary_recall'] is not None else 'Unavailable')+' |' for label,x in zip(['Published searches, normalized union','OQL: restored text operators','OQL plus keywords','OQL plus keywords and full text','OQL plus keywords, no geography'],summary))
report=f'''# OpenAlex evidence-synthesis pilot: Stansfield case

Pilot run: 4 October 2026, Singapore time. Status: source retrieval, query construction, syntax validation and known-reference membership completed. Ranking validation failed. The full-text arm also failed execution. This is a feasibility pilot, not a completed ranking benchmark or evidence that OpenAlex can replace a multi-database search.

## Results

| Search arm | API-reported matching works | Original eligible records | Expanded eligible records |
| --- | ---: | ---: | ---: |
{table}

Verified current coverage is **128/131 (97.7%)** for the primary reference set and **130/133 (97.7%)** for the expanded set. Three original records remain unmatched after full-title and shorter title/year searches. “Unmatched” is not proof of absence from the index. Retrieval recall counts unmatched records as not identified and keeps them in the denominator.

These are known-positive membership results, not screening precision. Membership was measured by adding an OpenAlex-ID restriction to each frozen query. Returned unique IDs equalled the finite-query count, so those results were not truncated. The total query sizes are API counts, not independently downloaded and deduplicated full corpora. Full-text failures are unavailable, not zero.

The published strategy's normalized union retrieved 126/131 original records. Restored OQL retrieved 125/131, with 1,538 fewer matching works (6.6% fewer). Keyword expansion added one known original record and 4,473 matching works relative to restored OQL. Removing geography added another known original record and 20,618 matching works relative to the keyword arm. These are changes in result volume, not measured changes in completed screening effort. New metadata, keyword assignment and the translation choices prevent attributing all changes to OQL itself.

## What the syntax pilot established

The authenticated conformance suite completed **{validation['checks']} checks: {validation['passed']} passed and {validation['checks']-validation['passed']} failed**. A 54-record finite corpus supported direct set comparisons for Boolean union/intersection, precedence, negation, field unions, phrases, truncation and unordered proximity. GET, POST, OQO and classic execution agreed on the tested finite phrase query. Negative controls rejected invalid syntax. These checks cover the tested cases rather than every possible query.

All four final OQL arms parsed. Each final query also passed OQL → OQO → OQL → OQO identity checking. The restored, keyword and no-geography arms executed successfully. The large full-text union parsed but returned HTTP 504 or 500 even with retries and an ID restriction. Its count and recall are therefore unreported.

Ovid ADJ6 and ADJ4 were translated to OQL `within 5` and `within 3`, respectively, using Cartesian disjunctions of the source alternatives. Proximity operands and literal terms were quoted. Wildcards were retained. This restores explicit text operators but does not establish tokenizer identity with Ovid. The translation cannot restore Emtree headings and explosions, journal-country fields, or controlled-vocabulary animal/geographical exclusions. Original Embase text fields are approximated by OpenAlex title/abstract. Source document cells and translation choices are retained in `queries/manifest.json`.

## Why rank outcomes are withheld

1. All restored OQL arms reject an explicit native relevance sort with HTTP 400, `relevance_sort_requires_search`. A minimal exact-term query produces the same rejection via GET, POST and OQO, while its bare stemmed counterpart returns numeric relevance scores. Restoring wildcards and literal matching therefore has a material interaction with relevance sorting in the observed API.
2. The published-search union accepts relevance sorting and reranking, but returns no numeric native relevance scores. Its first 200 relevance-sorted results differ between a single-page call and a cursor call, including after country normalization.
3. The separate nested Boolean control had 150 missing relevance scores and incompatible cursor results. A reranked cursor sequence returned its first 100 records, then HTTP 400 `Cursor value is invalid` on page three. A single response claimed reranking and preserved the tested top-100 membership, but that does not validate the continuation.

These observations do not establish an internal cause. They are enough to fail the predeclared ordering gate. No alternative sort, semantic retrieval, extra scoring term, external reranker, or classic-API substitution was introduced to manufacture a native relevance ranking.

The default first 200 results repeated identically and matched the first default cursor page for the three executing restored OQL arms. Within that bounded observation, default order retrieved 1/131 original records at rank 100 for restored OQL, and 0/131 for the keyword and no-geography arms. These are exploratory default-order observations from a single 200-record window. They are not verified native relevance results, an all-budget evaluation, or a stopping rule. The default cannot be compared to a successfully executed native relevance arm for those queries.

Recall@500/1,000/2,500/5,000/12,293, records-to-95%, and reranking comparisons remain unavailable. The 95% target requires 125 of 131 original records. The 99% target requires 130 and is not attainable in any of the currently measured matched-reference query sets, which recover at most 127. Ranking cannot repair query exclusions. Unresolved matching remains a separate limitation.

## Source and identity audit

The published workbook has three pairs of OpenAlex IDs swapped relative to their titles and PMIDs: two Prothero records, two Riordan records, and two Ting records. The audit corrected six current mappings only where the source PMID and normalized title agreed with the counterpart OpenAlex record. One Lindenmeyer record's old OpenAlex ID failed lookup and was rematched by exact normalized title and source year. The source workbook remains unchanged. Original IDs, current IDs, correction method and source flags remain in the record-level CSV. Corrections do not change aggregate retrieval counts because all counterpart records belong to the same primary set.

The URL translator also carried the legacy `countries/gb` namespace into OQO/OQL as `COUNTRIES/GB`. That translated branch recovered fewer known records than the original classic request. Changing that leaf to the documented bare code `GB` resolved the union discrepancy: all 126 primary and 128 expanded matches agree with the deduplicated reference membership of the nine classic searches. Eight individual translated branches already agreed; the affiliation-country branch caused the difference. The uncorrected translation and its diagnostics are preserved. Agreement here is established for the matched-reference corpus, not independently for every record in the full result set.

{year_differences} matched records have different publication years in OpenAlex and the source workbook. Online/issue dates may explain some differences, but their causes were not individually adjudicated. All remain within 2003–2023. Both years are preserved. Historical retrieval flags are retained as supplied rather than reinterpreted using today's metadata.

Unresolved records:

{chr(10).join('- '+r['short_title']+': '+r['title'] for r in unresolved)}

## Scope and interpretation for a paper

The original map searched **26 information resources** and screened **12,293 records**. This is not a direct experiment against a fixed five-database combination. Original PubMed retrieval recovered 117/131 records from a 2,854-record search. Those figures are contextual historical comparators, not freshly executed PubMed results.

A defensible paper asks whether contemporary OpenAlex supports *operationally reproducible, high-recall searching at realistic screening budgets*. Coverage, query capture, ranking validity and usable screening effort should be separate endpoints. This pilot already shows why successful parsing and high index coverage alone cannot establish that claim. A broader replacement claim needs additional reviews, validated ranking, prespecified acceptable loss, and eventually screening/precision evidence. No previously unlabelled records were assessed in this pilot.

## Evidence and reproducibility

- [Stansfield et al. article](https://onlinelibrary.wiley.com/doi/full/10.1002/cesm.70038)
- [Public reference deposit](https://osf.io/sndr3/)
- [Europe PMC full XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12302543/fullTextXML) and [supplementary files](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12302543/supplementaryFiles)
- [OQL specification](https://help.openalex.org/access/oql-spec/) and [OQL API](https://help.openalex.org/api/oql/), checked against the current documentation dated 3 October 2026.

Downloaded originals and SHA-256 hashes are in `sources/`. Frozen query text and OQO are in `queries/`. The conformance run is in `../oql_validation/authenticated_2026-10-04/`. Request logs retain query parameters, payloads, responses and UTC timestamps. Credentials are loaded from the local `.env.txt` through `pilot_credentials.py` and never included in request logs.

Execution scripts, in order: `fetch_stansfield_sources.py`, `inspect_source_workbooks.py`, `build_stansfield_queries.py`, `run_stansfield_gate.py`, `measure_stansfield_membership.py`, `check_unresolved_references.py`, `diagnose_stansfield_order.py`, `verify_stansfield_pilot.py`, `diagnose_legacy_translation.py`, `normalize_legacy_country.py`, and `finalize_stansfield_pilot.py`. The authenticated conformance suite is `pilot_oql_validation.py` with `OPENALEX_OQL_OUTPUT=oql_validation/authenticated_2026-10-04`. Live reruns overwrite each script's designated result folder, so archive it or use a separate checkout for a new run. They may produce changed counts because OpenAlex is a live index.
'''
(OUT/'PILOT_REPORT.md').write_text(report,encoding='utf-8')
plan='''# Study plan: From indexed to findable

Research question: Can contemporary OpenAlex retrieve known eligible evidence at realistic screening budgets using reproducible native ordering, rather than merely contain it?

## First case and restrictions

- Reuse the Stansfield diabetic eye screening case, with original eligibility and publication years 2003–2023 inclusive. Keep the search-run date distinct from the publication restriction. Current metadata does not recreate historical OpenAlex snapshots.
- Primary denominator: 131 original eligible records. Secondary denominator: 133 previously identified eligible records, including the two added by Stansfield's OpenAlex work. Keep these cohorts separate.
- Preserve source IDs and correct mappings only with independent identity evidence. Retain unmatched records in recall denominators. Record current and source publication years.
- Ignore all previously unlabelled records. Do not infer negatives, precision, specificity, screening stopping rules or newly discovered eligibility.
- Compare against the actual historical map (26 information sources, 12,293 records screened), with PubMed as a contextual comparator. Do not describe it as a randomized five-database replacement study.

## Search arms

1. Replay the published nine OpenAlex searches with the 2003–2023 limit. Verify a normalized single union against the nine original requests before using its membership or ordering.
2. OQL restoring available Embase Boolean, proximity and wildcard operators in title/abstract. Explicitly document unavailable controlled-vocabulary and field equivalents.
3. Same source-derived concepts expanded into title/abstract/keywords, plus the published keyword branches.
4. Explicit union of the keyword arm with the same text strategy searched in full text.
5. Keyword arm with the geographical search restriction removed. The review's country eligibility remains intact.

Freeze strategies from source methods before measuring eligible-record retrieval. Repairs to syntax, namespace or identity require an explicit audit trail. Distinguish those repairs from post hoc changes intended to improve recall.

## Mandatory OQL validation before the ranking benchmark

Check current official syntax, live parsing, OQO structure, round-trip identity and actual execution. Test Boolean set identities, quoted/stemmed phrases, wildcard forms, proximal gaps, field unions, keywords, date limits and invalid controls on a finite corpus. Do not equate HTTP 200 or a valid parser response with correct semantics.

For each final arm, inspect intended clauses and compare equivalent execution surfaces where representable. Validate source namespace handling. Compare repeated requests, basic and cursor pages, score availability/order, duplicate IDs and the reranking boundary. A source-equivalent query must recover the same known-positive set by independent membership checks. A full-corpus equivalence claim requires a separate full-corpus comparison.

The pilot has passed syntax/finite semantics but failed the ordering gate. Resolve exact-search relevance rejection, Boolean relevance score/pagination discrepancies, and reranked cursor continuation before reporting native recall-at-rank. Resolve full-text execution errors before reporting its count or recall. Re-test minimal examples and final queries after an API change. Preserve current evidence. Do not silently introduce another API, ranking method or retrieval strategy.

## Ranking and outcomes after validation

- Native relevance.
- Native relevance with OpenAlex's native reranking.
- Default order as a separate arm when a valid comparison shows it differs from relevance. Record the effective API behavior. Add no citation, FWCI, date or semantic ranking arms.
- Coverage and complete-query matched-reference recall, always reported separately from rank-limited recall.
- Recall@100, 500, 1,000, 2,500, 5,000 and 12,293. Also @10, 20 and 50 for the top-100 reranking comparison.
- Native reranking affects only the first 100 according to current documentation. Verify identical membership at 100 and continuation from 101 rather than assuming it. Under validated preservation, recall at 100 and above must agree between native and reranked arms.
- Records to reach 95% and 99% of each reference cohort. For the primary cohort those require 125 and 130 records, respectively. Mark targets beyond complete-query recovery unattainable instead of reporting a finite rank.
- Query size, number of API calls, reported cost, execution failures, reproducibility and changes between repeated runs. Distinguish API query counts from fully enumerated unique result counts.

Known-positive rank evaluation can measure how quickly a strategy recovers the reference set. It cannot estimate precision or justify stopping on new reviews while unlabelled records remain unassessed. Do not tune queries or rerankers on held-out eligible records. Expand to multiple reviews before making a general database-replacement claim. Study-design/PubMed-derived filters should only be evaluated in reviews whose eligibility genuinely uses those designs; they are not appropriate restrictions for this all-design map.

## Pilot deliverables and remaining work

Completed: preserved original sources, frozen query manifests, authenticated conformance tests, record identity audit, verified reference membership for four executing arms, documented country-namespace repair, and a report with raw evidence.

Remaining dependent work: validate native relevance and reranking for the final queries, make the full-text arm execute, enumerate valid complete rankings, calculate all prespecified rank outcomes, and broaden to further reviews. The current pilot is suitable for a methods/feasibility discussion. Its ranking benchmark is incomplete.
'''
(OUT/'STUDY_PLAN.md').write_text(plan,encoding='utf-8')
# Check that the credential has not leaked into any authored or response artifact.
from pilot_credentials import load_key
import os
load_key()
secret=os.environ['OPENALEX_API_KEY'].encode()
leaks=[]
for folder in [OUT,ROOT/'oql_validation/authenticated_2026-10-04']:
    for path in folder.rglob('*'):
        if path.is_file() and path.suffix.lower() in ['.json','.csv','.md','.oql','.txt'] and secret in path.read_bytes():
            leaks.append(str(path))
assert not leaks, 'Credential leakage detected'
checks={'cohort_counts':True,'unique_current_ids':True,'all_matched_dates_in_window':True,
 'legacy_known_membership_matches_classic_union':True,'keyword_and_no_geo_known_sets_monotone':True,
 'credential_scan_passed':True,'matched_pmid_consistency':True,'year_disagreements':year_differences,'completed_utc':dt.datetime.now(dt.timezone.utc).isoformat()}
(OUT/'consistency_checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
print('Consistency checks passed; report and plan saved.')
