# OpenAlex OQL syntax and execution pilot

Validation date: 3 October 2026 (Asia/Singapore). All retrieval examples were limited to publication years 2003–2023.

## Result

The main live run completed 98 checks: **94 passed and 4 failed**. The failures concern relevance scoring and pagination. Two failed checks assess the same missing-score condition; these are not four independent bugs.

The syntax and finite-corpus retrieval checks passed. **The ranking stage is not ready for the Stansfield recovery benchmark without addressing the observed behavior.** An HTTP 200 response and valid OQL parse do not demonstrate a usable relevance ranking.

This validates representative query constructs, not a completed translation of the full Stansfield strategy. It does not measure recovery of the 131/133 eligible records and does not assign eligibility labels to new records.

## What was checked

- Seventeen valid query patterns were translated, round-tripped through the canonical query object (OQO), and executed live.
- Ten invalid patterns were rejected with HTTP 400 and an invalid validation result.
- Boolean unions, intersections, nesting, precedence, negation, field scope, and explicit keyword/text OR were checked using actual result-set membership in a fixed corpus of 54 records.
- Exact title phrases, title wildcards, and unordered proximity with and without wildcards were compared against independently tokenized titles. Proximity gaps of 0, 1, 3, and 5 were tested.
- OQL GET, OQL POST, OQO POST, and classic-filter requests recovered the same complete finite subset. Membership and ordering were kept separate.
- Default ordering, explicit relevance, reranking, and continuation across the first-100 boundary were exercised with live queries. No eligibility judgment was involved.

## Syntax that executed successfully

These examples demonstrate syntax only; they are not the final review searches.

| Capability | Tested form |
|---|---|
| Study publication window | `year >= (2003) and year <= (2023)` |
| Nested Boolean blocks | `title/abstract has ((diabetes or "diabet*") and (retinopathy or retinal) and (screening or uptake))` |
| Exact phrase | `title has ("diabetic retinopathy")` |
| Stemmed adjacent phrase | `title has (stemmed "diabetic retinopathy")` |
| Unordered exact proximity | `title has (within 3 ("diabetic", "retinopathy"))` |
| Unordered proximity with truncation | `title has (within 3 ("diabet*", "retinopath*"))` |
| Truncation inside an adjacent phrase | `title has ("diabet* retinopath*")` |
| Keyword OR text | `(keyword is (diabetic-retinopathy) or title/abstract has ("diabetic retinopathy"))` |
| Explicit keyword-inclusive scope | `title/abstract/keywords has ("diabetic retinopathy")` |
| Country-code list | `country is (AU or CA or IE or NZ or GB)` |

Wildcard operands must be quoted. A bare wildcard such as `diabet*` was rejected. Proximity lists must use consistently quoted or consistently bare operands. `UK` was rejected; the United Kingdom code is `GB`. Country filters refer to authorship metadata and must not be treated as the clinical setting of a study.

Quotes in OQL select exact, unstemmed matching. Quotes in the conventional search box/scoped stemmed API search can mean a stemmed adjacent phrase. A translation must preserve the matching mode, not just copy quotation marks.

For a simple pair of terms, Ovid `ADJn` permits up to `n-1` intervening words. The tested OQL `within N` uses a gap budget of `N`. Thus, `ADJ3` should be considered for translation to `within 2`, rather than mechanically copied as `within 3`. Multiword operands, analyzer positions, and stopwords still require case-specific checking.

## Reproducible ranking finding

The query below returned 17,819 matches at validation time:

```text
works where title/abstract has (
  (retinopathy or retinal) and (screening or uptake)
)
and year >= (2003)
and year <= (2023)
```

Observed with `POST https://api.openalex.org/`:

1. Default ordering differed from `sort=relevance_score:desc`. Keep default as a separate study arm when it differs.
2. The explicit relevance request returned 150 records, **all without `relevance_score`**. Relevance sorting was accepted, but its meaning could not be established from the output.
3. `rerank=true` reported `meta.reranked=true`. In one 150-record response, it preserved top-100 membership and the order of records 101–150.
4. Three native cursor pages of 50 records did not match the order of one 150-record response. This shows an ordering discrepancy, not proof of record loss from a complete export.
5. Reranked cursor requests returned the first two pages, then the server rejected the supplied continuation cursor with HTTP 400: `Cursor value is invalid.`

In this nested-query test, the native cursor export's first 150 IDs and the one-page response's 150 IDs were entirely disjoint. This is stronger than a change in tie order, but it still does not establish whether any records would be lost from a complete export.

Positive controls returned numeric relevance scores for a simple OQL term and a simple OQL conjunction. The equivalent classic scoped Boolean request also returned scores and the same overall count:

```text
GET /works
  ?search.title_and_abstract=(retinopathy OR retinal) AND (screening OR uptake)
  &filter=publication_year:2003-2023
  &sort=relevance_score:desc
```

Equal global counts do not prove full-set equality. The classic request is a diagnostic control; it has not been substituted for the planned OQL arm.

## Additional ranking controls

The targeted follow-up completed ten additional requests, archived separately.

- A simple stemmed OQL query (`title/abstract has (retinopathy screening)`) returned numeric scores. Its native cursor and one-page exports contained the same first 150 IDs, but six positions differed; small score changes were visible between requests. These observations should be described as live ordering variability, rather than equated with the nested-query failure.
- The same simple query also failed when continuing a reranked cursor beyond the first 100 results. Removing the rerank flag from that continuation did not repair the invalid cursor.
- The explicit keyword/text union (`keyword is (diabetic-retinopathy) or title/abstract has ("diabetic retinopathy")`) executed without an explicit relevance sort in the main syntax tests. Adding `sort=relevance_score:desc` returned HTTP 400 with `relevance_sort_requires_search`. Thus, syntax acceptance and ordinary retrieval of this planned arm do not establish that it supports the requested ranking.

The root cause is not established. These findings identify combinations that need resolution or a separately validated export/ranking method before the main research comparison.

## Gate before the main research pilot

- Freeze and validate every final OQL strategy and archive its OQO interpretation.
- Check term-level truncation limits and proximity boundaries before running the translated full search.
- Require an established relevance ordering and reproducible pagination for each query arm before interpreting recall at rank.
- Record native default ordering separately where it differs.
- Confirm that reranking preserves result membership and continues beyond rank 100 correctly using the chosen export method.
- Retrieve the complete query result sets; missing or failed pages must not become apparent retrieval failures of the search strategy.
- Preserve the 2003–2023 publication window, use only the existing eligible reference sets, and defer screening of unlabelled records.

## Files and reproduction

Run from this workspace with Python 3 and internet access:

```powershell
$env:OPENALEX_OQL_OUTPUT = 'oql_validation/verified_run'
python -u pilot_oql_validation.py
python -u diagnose_oql_ranking.py
```

`pilot_oql_validation.py` uses only the Python standard library. It saves request bodies, response bodies, statuses, validation checks, the finite corpus, and a completion summary. It does not save request headers or credentials. Future runs reflect the live API and may differ from this archived run.

- `oql_validation/verified_run/summary.json`: completed main-run totals and failed checks.
- `oql_validation/verified_run/checks.json`: individual checks.
- `oql_validation/verified_run/requests.json`: main-run response audit trail.
- `oql_validation/verified_run/finite_corpus.json`: fixed records used for semantic checks.
- `oql_validation/ranking_diagnostics/`: additional simple-query and keyword/text controls.

The full Stansfield supplementary strategy files could not be downloaded from the publisher during this pass. Therefore, no claim is made that the final full strategy has passed validation. The live syntax checks and ranking findings are independently reproducible from the saved scripts.

## Primary documentation

- [OpenAlex OQL specification](https://help.openalex.org/access/oql-spec/)
- [OpenAlex OQL execution and translation API](https://help.openalex.org/api/oql/)
- [OpenAlex search and reranking](https://help.openalex.org/api/searching/)
- [Ovid operator definitions](https://ospguides.ovid.com/OSPguides/bookdb.htm)
- [Stansfield et al. (2025)](https://onlinelibrary.wiley.com/doi/full/10.1002/cesm.70038)
