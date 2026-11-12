# Larger-workload test: prospective biomarkers of depression

**The fuller query recovered 66/75 included articles (88.0%) in 357,009 reported results. The compact query recovered 63/75 (84.0%) in 175,049 results. Neither met the frozen greater-than-95% recovery target, and both result counts exceeded the review's reported screening count.** All 75 original articles matched OpenAlex.

This second test responds to the request for a review with a much larger original screening workload than the [insomnia benchmark](../transfer_benchmark_2026-11-12/README.md). The [protocol and queries were committed and pushed](https://github.com/aarontaycheehsien/canyouuseopenalexalone/commit/39728476e3c0bfcd702c3e45b9893edaf32bea65) before inspecting the included-study titles or running the candidate searches. Test date: **12 November 2026**.

## Benchmark and original workload

Selected review: [Kennis et al., *Prospective biomarkers of major depressive disorder: a systematic review and meta-analysis*](https://doi.org/10.1038/s41380-019-0585-z), published online in 2019 and in the 2020 volume of Molecular Psychiatry. The [public article](https://pmc.ncbi.nlm.nih.gov/articles/PMC6974432/) reports searches in PubMed, PsycINFO and Embase, citation/reference checking, a June 2019 update, and **75 unique prospective articles**. Table 1's 75 distinct reference IDs define the benchmark.

The reported **67,464 articles screened** provides the larger-workload setting, but requires two qualifications:

1. The authors explicitly warn that this count may include articles screened more than once across biomarker classes.
2. The supplement's per-search flow table is internally inconsistent. Its title/abstract-screening cells sum to **51,843**, not 67,464; some other cells are also inconsistent. The [saved table values](results/source_flow_counts.json) make that calculation inspectable. Neither number is established here as the number of unique records screened across the whole review.

The result volumes exceed both figures. Nevertheless, the historical figure cannot support a precise unique-record workload comparison or a percentage of screening time saved.

The source covers neuroimaging, gastrointestinal factors, immunology, neurotrophic factors, neurotransmitters, hormones and oxidative stress. It was chosen for its larger workload, larger benchmark and accessible methods—not favourable OpenAlex matching or retrieval. [The protocol](PROTOCOL.md) records alternatives and the information inspected before freezing. Two author labels from a figure caption appeared incidentally during source retrieval; included-study titles, identifiers and search results were held back. This remains an AI-assisted procedural holdout, not independent human blinding or a guarantee against prior model-training exposure.

## What was actually translated?

The public supplement provides **PubMed** searches. Embase and PsycINFO translations are available only on request and were not obtained. This tests source-derived text concepts in OpenAlex, not a faithful Embase replication.

**[A — Fuller source-derived union](queries/A_fuller_source_union.oql)** preserves the source depression vocabulary and biomarker term lists. It reconstructs the intended OR union of the source branches. Most branches require prediction/prognosis vocabulary, while the neurotransmitter and gonadal-hormone branches retain the source's absence of that requirement.

**[B — Compact three-concept candidate](queries/B_compact_three_concepts.oql)** requires depression/affective wording, a shorter prospective/prediction/onset/relapse block, and a compact biomarker block. It adds general category words and consolidates families with prefixes, while omitting many chemical variants. All three concepts are required for every biomarker category. This was a predefined tradeoff, not a query selected after seeing its count or misses.

Both search title/abstract/OpenAlex keywords with a publication-date ceiling of **2019-06-30**, using the default core corpus and API defaults. All benchmark metadata indicate `is_retracted: false`. No country, benchmark-ID or topic filters occur in the unrestricted queries.

Translation limitations matter when interpreting the high volumes. MeSH headings become text labels; their hierarchies are absent. PubMed-specific human, language and review exclusions were omitted. The neurotransmitter branch's recent-only text-search workaround was not carried into OpenAlex. The exact combined June 2019 update string was unavailable. The source also contains malformed quotes, parentheses and delimiters requiring reconstruction; all normalization choices were documented before evaluation. The [extracted vocabulary](vocabulary.json) and [query builder](build_queries.py) make these decisions inspectable.

The failure is a finding about **these adaptations**, not proof that every possible OpenAlex translation would perform the same way.

## Frozen outcomes

The primary recall threshold was **at least 72/75**, the smallest whole number exceeding 95%. Every original article remains in the denominator.

| Query | API-reported results | Original articles recovered | Above 95% recall? | Below reported 67,464 screening count? |
|---|---:|---:|---|---|
| Fuller source-derived union | 357,009 | 66/75 — 88.0% | No | No |
| Compact three-concept candidate | 175,049 | 63/75 — 84.0% | No | No |

The compact candidate returns fewer records, but loses five articles found by the fuller query and gains two others. It is not simply a subset. Shorter query text does not establish a better balance of recall and screening burden.

Matching identified **75 distinct OpenAlex IDs**: 72 direct DOI agreements, one source-DOI lookup returning a different canonical DOI corroborated by the same PMID, and two PMID-only lookups. Every one of the 75 OpenAlex PMIDs agrees with the source citation. The alternate-DOI case is [recorded explicitly](results/matching_notes.json); it does not change membership or recovery. Some source references are unstructured and some returned titles omit subtitles; complete source citation text and returned titles are retained alongside identifiers.

Coverage is 75/75. Conditional retrieval among matched records and full-benchmark recovery are therefore the same percentages. [The per-article matrix](results/per_article_retrieval.csv) shows every inclusion and miss; [the summary JSON](results/summary.json) records the calculations.

## Evidence strength: membership is not a complete export

For each strategy, unrestricted OQL execution supplied a total and first page. Its returned OQO was then reused with **only an additional AND restriction to the 75 matched IDs**. Those responses contain the 66 and 63 recovered IDs. The offline verifier checks that the restriction was added to the identical executed filters.

Both sets exceeded the protocol's 9,800-record cap for attempted key-free numbered-page export. Continuing cursor pagination requires an API key, which was not configured. As prespecified, only the **first 200 unrestricted records per strategy** were retained; neither set was downloaded in full. These pages were sorted by publication date ascending and contain no benchmark IDs. They are not relevance-ranking tests.

The large test's recovery measurement rests on archived **benchmark-restricted membership**, with unrestricted counts and first pages retained. It does **not** have the unrestricted-export confirmation available for the insomnia test. This limitation is encoded in the summary, not just noted in prose.

## What the miss diagnostics establish

The [post-evaluation clause tests](results/clause_diagnostics.json) cover the 14 articles missed by at least one strategy. No frozen query was repaired.

- Every diagnostic record passes the date limit and both population blocks.
- Every compact-query miss passes its prediction/prospective block and fails its biomarker block.
- All fuller-query misses fail the biomarker alternatives that could admit them. The tested prediction blocks pass for these records, while the neurotransmitter/gonadal-hormone alternatives also fail to rescue them.

Examples include papers about neural reward responses, frontal asymmetry and prefrontal brain function. Their coverage in OpenAlex does not guarantee retrieval by the selected biomarker vocabulary. A missed DEX–CRH article has no abstract in the saved metadata; other missed articles have abstracts, so absent abstracts are not a complete explanation.

The five articles lost by the compact candidate are among the review's neuroimaging entries. Two inflammatory-risk articles missed by the fuller query are recovered by the compact version. The diagnostics identify failing blocks; they do not by themselves identify a particular matching word or establish an internal indexing cause. [Raw responses](archives/diagnostics/) are retained for further investigation.

## What this means for the follow-up post

| Independent case | Original screening context | Fuller candidate | Compact candidate |
|---|---|---|---|
| Insomnia | 1,974 records after deduplication | 27/29, 718 results | 27/29, 1,553 results |
| Depression biomarkers | 67,464 reported; cross-category duplicates and flow-count inconsistencies | 66/75, 357,009 results | 63/75, 175,049 results |

None of these frozen main candidates exceeded 95% recovery. OpenAlex matching coverage was complete in both cases. That separates coverage from the harder problem of expressing a search that recovers records efficiently.

These are two purposively selected reviews with different subject matter, source searches and adaptations. They do not estimate average performance across systematic reviews. New results were not screened for eligibility, so precision and actual screening time were not measured. The original depression review also used citation searching, which these Boolean queries do not reproduce.

A useful development phase would investigate biomarker synonyms, field behavior, controlled-vocabulary alternatives and supported exclusions. Gains obtained after examining these misses would be retrospective results requiring another independent test. This report preserves the failed thresholds rather than selecting a repaired query as though it had been the original candidate.

## Files and offline verification

- [Protocol](PROTOCOL.md), [freeze manifest](freeze_manifest.json), [source provenance](source_provenance.json), [validated interpretations](validation/).
- [Original references](results/benchmark_source.json), [identifier matches](results/benchmark_matches.json), [matching note](results/matching_notes.json), [per-article outcomes](results/per_article_retrieval.csv).
- Raw totals/pages and membership: [fuller query](archives/A_fuller_source_union/), [compact query](archives/B_compact_three_concepts/).
- [Summary](results/summary.json), [clause diagnostics](results/clause_diagnostics.json), [checksums](SHA256SUMS).

From the repository root, run:

```bash
python3 large_transfer_benchmark_2026-11-12/verify.py
```

This uses only the standard library and makes no requests. It checks hashes, all 75 identifier mappings and PMIDs, original versus restricted query filters, totals, membership, the matrix, thresholds, diagnostics and explicit partial-export labels.

`run_test.py SOURCE_XML` and `diagnose_misses.py` are explicit live runners; existing successful responses are reused rather than overwritten. The runner uses the small test's standard-library matching helper, whose hash is recorded in `implementation_dependencies.json`. A new live replication should use a separate dated output location. The full source article and supplement are not redistributed; original URLs and hashes are retained.
