# OpenAlex evidence-synthesis pilot: Stansfield case

Follow-up: the user subsequently chose cursor order as the operational definition of rank. A separate cursor study checks and enumerates those sequences. Its results are in `cursor_study_2026-10-04/CURSOR_ORDER_REPORT.md`. The initial findings below remain unchanged as the record of the first pilot.

Pilot run: 4 October 2026, Singapore time. Status: source retrieval, query construction, syntax validation and known-reference membership completed. Ranking validation failed. The full-text arm also failed execution. This is a feasibility pilot, not a completed ranking benchmark or evidence that OpenAlex can replace a multi-database search.

## Results

| Search arm | API-reported matching works | Original eligible records | Expanded eligible records |
| --- | ---: | ---: | ---: |
| Published searches, normalized union | 23,217 | 126/131 (96.2%) | 128/133 (96.2%) |
| OQL: restored text operators | 21,679 | 125/131 (95.4%) | 127/133 (95.5%) |
| OQL plus keywords | 26,152 | 126/131 (96.2%) | 128/133 (96.2%) |
| OQL plus keywords and full text | Unavailable | Unavailable | Unavailable |
| OQL plus keywords, no geography | 46,770 | 127/131 (96.9%) | 129/133 (97.0%) |

Verified current coverage is **128/131 (97.7%)** for the primary reference set and **130/133 (97.7%)** for the expanded set. Three original records remain unmatched after full-title and shorter title/year searches. “Unmatched” is not proof of absence from the index. Retrieval recall counts unmatched records as not identified and keeps them in the denominator.

These are known-positive membership results, not screening precision. Membership was measured by adding an OpenAlex-ID restriction to each frozen query. Returned unique IDs equalled the finite-query count, so those results were not truncated. The total query sizes are API counts, not independently downloaded and deduplicated full corpora. Full-text failures are unavailable, not zero.

The published strategy's normalized union retrieved 126/131 original records. Restored OQL retrieved 125/131, with 1,538 fewer matching works (6.6% fewer). Keyword expansion added one known original record and 4,473 matching works relative to restored OQL. Removing geography added another known original record and 20,618 matching works relative to the keyword arm. These are changes in result volume, not measured changes in completed screening effort. New metadata, keyword assignment and the translation choices prevent attributing all changes to OQL itself.

## What the syntax pilot established

The authenticated conformance suite completed **98 checks: 94 passed and 4 failed**. A 54-record finite corpus supported direct set comparisons for Boolean union/intersection, precedence, negation, field unions, phrases, truncation and unordered proximity. GET, POST, OQO and classic execution agreed on the tested finite phrase query. Negative controls rejected invalid syntax. These checks cover the tested cases rather than every possible query.

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

25 matched records have different publication years in OpenAlex and the source workbook. Online/issue dates may explain some differences, but their causes were not individually adjudicated. All remain within 2003–2023. Both years are preserved. Historical retrieval flags are retained as supplied rather than reinterpreted using today's metadata.

Unresolved records:

- Hayden (2012): The barriers and enablers that affect access to primary and secondary eye care services across England, Wales, Scotland and Northern Ireland
- Kumar (2022): Non-attendance at Diabetes Eye Services in South Auckland and the impact of Covid19
- Turner (2004): Improving retinopathy screening -- are we meeting the NSF target?

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
