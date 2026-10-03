# Cursor-order study: Stansfield case

The study now uses cursor order as its operational definition of rank, as requested. All rankings start with `cursor=*` and continue with the returned cursor. The search strings and publication-year limits remain the frozen 2003–2023 strategies. The prior single-page/cursor discrepancy remains documented. Choosing cursor order does not prove that the API applies its intended native relevance algorithm.

## Primary reference results

These figures count recovery of the 131 original eligible records. The three unmatched records remain in the denominator. Secondary results for all 133 previously identified records are in `rank_metrics.csv`. No previously unlabelled records were assessed.

| Search and cursor order | Total results | @100 | @500 | @1,000 | @2,500 | @5,000 | @12,293 | Records to 95% |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Published strategy (relevance requested) | 23,217 | 0/131 | 1/131 | 3/131 | 15/131 | 47/131 | 113/131 | 19,600 |
| Published strategy (default) | 23,217 | 1/131 | 3/131 | 7/131 | 17/131 | 31/131 | 69/131 | 21,911 |
| Restored OQL (default) | 21,679 | 1/131 | 7/131 | 29/131 | 79/131 | 112/131 | 123/131 | 17,785 |
| OQL plus keywords (default) | 26,152 | 0/131 | 3/131 | 11/131 | 50/131 | 95/131 | 124/131 | 18,335 |
| OQL without geography (default) | 46,770 | 0/131 | 1/131 | 2/131 | 11/131 | 35/131 | 94/131 | 25,348 |


The 95% target requires 125/131 records. The 99% target requires 130/131. All measured cursor searches recover fewer than 130, so 99% is unattainable within their returned sets. This describes the matched-reference evaluation, rather than proving the three unmatched records are absent from OpenAlex.

## What passed

Each reported complete cursor walk passed repeated first-400 requests, comparison of 100-record and 200-record pages, unique-ID checks, stable result counts, date checks, and repeated page requests near the start, midpoint and end. Unique result counts equalled the API counts. Those checks support reproducibility of the observed cursor sequences during this run. They do not independently establish the correctness of the hidden relevance calculation or indefinite future stability.

Complete cursor membership agrees with the earlier finite known-record membership checks: **True**. Default and relevance-requested cursor orders for the published strategy are identical across the complete sequence: **False**. The table presents one sequence when they are identical. All scores are checked separately in the walk summaries. Missing native relevance scores remain a limitation.

## Native reranking of the same candidates

The unchanged published query's reranked cursor walk failed continuation. Its starting candidate membership also differs from that of the non-reranked cursor walk. Those requests therefore cannot support a comparison of pure reranking on the same candidates.

The additional test fixes the first 100 IDs from the verified published-strategy cursor sequence. It submits the original query AND an explicit restriction to those IDs, with native `rerank=true`, requested relevance sorting, and `cursor=*`. Both requests return exactly the same 100 candidates, report `meta.reranked=true`, and give the same order. This is a **candidate-restricted native rerank**, not the unchanged-query native rerank arm. It was added after the initial pilot and must be described as such.


| Published strategy | @10 | @20 | @50 | @100 |
| --- | ---: | ---: | ---: | ---: |
| Cursor order | 0/131 | 0/131 | 0/131 | 0/131 |
| Native rerank of fixed cursor candidates | 0/131 | 0/131 | 0/131 | 0/131 |


For analysis, that reranked prefix is followed by the unmodified cursor sequence from position 101 onward. This complete order is assembled locally; it is not a successful full reranked API walk. Membership at 100 and all larger budgets is identical by construction. Comparison below 100 evaluates ordering within the same fixed candidate pool. The restricted query and pool are saved under `legacy_union_normalized/candidate_rerank/`.

## Unavailable arms

The restored OQL, keyword, no-geography and full-text arms still return HTTP 400 when relevance sorting is requested. Their default cursor orders are reported where execution and validation passed. These results must not be relabelled as validated native relevance rankings. The full-text arm also returns HTTP 504 under default cursor retrieval, so no ranked result is reported for that arm.

No citation, FWCI, date or semantic sort was added. Default order may reflect an API default sort, but that is not inferred to be native relevance. The findings support a narrower cursor-order study, with a separate fixed-candidate reranking test. They do not complete the originally intended native-relevance/reranking comparison for all OQL arms.

## Files and audit

- `rank_metrics.csv` and `metrics.json`: both cohort denominators, all budgets, complete recovery and threshold ranks.
- `reference_ranks.csv`: ranks of previously identified eligible records only.
- Per-arm `default/` and `relevance/` directories: page records, complete ordered ID lists and validation summaries.
- `probe.json`: repeat and page-size tests, rejected modes and unchanged-query reranking evidence.
- Compressed request logs: exact query, view parameters, timestamps, status and response. Credentials are excluded.
- `default_relevance_comparison.json`: full-sequence comparison for the published strategy.

This run made 773 logged HTTP requests. Successful responses reported a total cost of $0.0796. Charges without a returned cost field are not independently verified. First request: 2026-10-03T17:06:29.330846+00:00. Last request: 2026-10-03T17:34:55.446375+00:00. The scripts are `run_cursor_study.py`, `test_cursor_candidate_rerank.py` and `report_cursor_study.py`. The first supports resuming enumeration from saved pages. Keep these run artifacts intact before a future rerun.

The [OpenAlex search documentation](https://help.openalex.org/api/searching/) describes native reranking as a change to the first 100 records, with later records unchanged. The observed unchanged-query behavior and the fixed-candidate workaround are documented separately here.
