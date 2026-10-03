# Study plan: From indexed to findable

## Cursor-order amendment, 4 October 2026

The user chose cursor order as the study's operational definition of rank after reviewing the single-page/cursor discrepancy. All measured sequences therefore start with `cursor=*` and follow the returned cursors. Repeated prefixes, different page sizes, duplicate IDs, full unique counts, date bounds and repeated boundary pages must pass. The original discrepancy remains in the report. This choice does not independently certify the hidden relevance algorithm.

Measure the published-search union with requested relevance sorting and default sorting separately. Measure default cursor ordering for restored OQL arms where explicit relevance sorting is rejected. Retain rejected modes and execution failures as unavailable. Do not relabel default cursor order as native relevance. The publication-year window and reference cohorts remain unchanged.

The unchanged-query reranked cursor call uses a different candidate set and fails continuation. An added exploratory test restricts the original published query to the first 100 IDs in its verified cursor sequence and applies the native reranker to exactly those candidates. Report that restriction explicitly. A locally assembled reranked prefix plus the original continuation is a derived sequence, not a successful full reranked API walk. This test was added after the initial findings and is separate from the originally proposed unchanged-query reranking arm.

Cursor-study evidence and rank results are saved under `cursor_study_2026-10-04/`. The original plan below records the initial design and its unresolved API limitations.

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
