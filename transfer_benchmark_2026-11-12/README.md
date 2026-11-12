# Can OpenAlex do it again? An independent-review transfer test

**The frozen searches recovered 27/29 included articles (93.1%). None met the prespecified greater-than-95% recovery threshold, although all returned fewer records than the review originally screened.** All 29 articles matched OpenAlex by DOI, so the observed shortfall was in retrieval, not benchmark matching.

Test date: **12 November 2026**. The protocol and exact queries were [committed and pushed before inspecting the included-study titles](https://github.com/aarontaycheehsien/canyouuseopenalexalone/commit/f58477e7f845283257bf75c7781b719b332d3074). This report preserves the frozen result. The later clause tests explain aspects of the misses; no repaired query replaces the primary searches.

## Why this benchmark?

The selected review is [Hwang et al. (2025), *Systematic review and meta-analysis on fully automated digital cognitive behavioral therapy for insomnia*](https://doi.org/10.1038/s41746-025-01514-4). Its [public article](https://pmc.ncbi.nlm.nih.gov/articles/PMC11903857/) and supplement provide a practical benchmark:

- A different condition and intervention from diabetic eye screening, without a geographical eligibility restriction.
- Database-specific strategies, including Embase, in Supplementary Table 2 (PDF page 18).
- An identifiable set of 29 included **articles**, linked from Table 1 to bibliography entries.
- A reported search through 31 March 2024 across PubMed, CENTRAL, Embase and PsycINFO: 3,101 records identified and **1,974 screened after deduplication**.

The benchmark was selected for those features before checking OpenAlex coverage or retrieval. Other insomnia reviews and SYNERGY were considered; the [protocol](PROTOCOL.md) records the selection rationale and alternatives. This was a purposive feasibility choice, not an exhaustive or representative selection of reviews. The packaged SYNERGY records already have OpenAlex matches, so using that subset alone would not answer the full-denominator question.

The unit here is the included article/report. Table 1 reconciled to 29 distinct references and then to 29 distinct OpenAlex IDs. This does not establish that the 29 articles represent 29 independent trials.

## What was fixed before looking at the answers?

The AI assistant read the methods, aggregate selection counts and search-strategy page before query construction. The full XML and supplement were downloaded locally, but scripts exposed only those sections until the freeze. Included-study titles, bibliography entries, OpenAlex matches and candidate result counts were not inspected during query design.

This is a procedural holdout within an AI-assisted session. It is not independent human blinding or formal registry preregistration, and it cannot rule out exposure in model training. The public freeze commit makes the order of the recorded work inspectable.

The two main searches were:

**A: Fuller Embase text adaptation.** Keep the source's population, therapy, digital-delivery and `random*` trial-design blocks. Preserve every delivery term. Represent subject headings through their text labels, add British/American spelling variants and truncate therapy/disorder endings. This cannot reproduce exploded Emtree headings and must not be described as an exact Embase translation.

**B: Compact text candidate.** Narrow the population to insomnia, consolidate therapy variants with `behavio*`, and remove the trial-design requirement. Keep the delivery list. The rationale was to avoid dependence on trial-design wording in searchable metadata. It was a hypothesis to test, not a demonstrated improvement.

**C: Fuller adaptation without the trial filter** was frozen as a sensitivity comparison. It differs from A only by removing `random*`, allowing that change to be assessed separately from the compact candidate's other changes.

All three search title/abstract/OpenAlex keywords with a publication-date ceiling of **2024-03-31**. They use the default core corpus and API defaults, with no explicit retraction override. All matched benchmark records have `is_retracted: false`. No country restriction, topic fallback, product name, benchmark ID or title-informed exception was added. The API's translation endpoint validated every query and exposed the intended field filters. Its warnings concerned inability to express the mixed exact/stemmed search as a classic URL, not invalid OQL.

The success criterion was fixed as **at least 28/29 articles recovered** and **no more than 1,974 reported results**. Recovery is calculated against every original included article, not merely a conveniently matched subset.

## The frozen results

| Strategy and exact query | API results | Downloaded rows | Distinct IDs | Original articles recovered | Meets both thresholds? |
|---|---:|---:|---:|---:|---|
| [A — Fuller Embase text adaptation](queries/A_fuller_embase.oql) | 718 | 718 | 718 | 27/29 — 93.1% | No |
| [B — Compact text candidate](queries/B_compact.oql) | 1,553 | 1,553 | 1,553 | 27/29 — 93.1% | No |
| [C — Fuller adaptation without trial filter](queries/C_fuller_without_trial_filter.oql) | 1,591 | 1,591 | 1,591 | 27/29 — 93.1% | No |

All strategies missed the same two articles. Removing `random*` from A added **873 results**, with no gain among known inclusions. The compact candidate returned **835 more results than A**, also without a gain. Its shorter expression did not produce a smaller result set than the fuller baseline.

All 29 benchmark identifiers were exact DOI matches. Title comparisons found three OpenAlex titles that omit the source citation's “a randomized clinical trial” subtitle; their DOIs and remaining titles agree. There were no ambiguous matches or many-to-one mappings. Coverage was **29/29**, while conditional retrieval and full-benchmark retrieval were both **27/29**.

Recovery was calculated by intersecting those IDs with **unrestricted downloaded results**. Benchmark IDs were not part of the primary searches. Raw outputs, individual membership and computed totals are in the [per-article matrix](results/per_article_retrieval.csv) and [summary JSON](results/summary.json).

## What failed for the two missed articles?

These tests were performed **after** saving the frozen results. They restrict diagnostic queries to the two missed IDs; their purpose is to identify failing clauses, not to substitute ID lookups for retrieval.

| Frozen clause | Lancee et al. (2013), CR66 | Theadom et al. (2018), CR63 |
|---|---|---|
| Publication-date limit | Pass | Pass |
| Fuller population block | Pass | Fail |
| Compact population block | Pass | Fail |
| Fuller therapy block | Fail | Pass |
| Compact therapy block | Fail | Pass |
| Delivery block | Pass | Fail |
| `random*` trial filter | Pass | Pass |

**[Lancee et al.](https://doi.org/10.1016/j.brat.2013.09.004)** concerns motivational email support for internet-delivered self-help treatment for insomnia. Its OpenAlex title lacks the therapy phrases, and its saved record has no abstract. The returned keywords nevertheless include a CBT-I label. An explicit `keywords.id` filter for `cognitive-behavioral-therapy-for-insomnia` retrieves it, while the tested therapy text does not—including a diagnostic literal `"cognitive behavioral therapy"` search. The evidence supports a difference between the tested keyword-ID and text-search behavior; it does not establish the underlying indexing cause.

**[Theadom et al.](https://doi.org/10.1177/0269215517736671)** describes on-line interventions for sleep quality after traumatic brain injury. Its abstract discusses sleep difficulties and disturbance, rather than insomnia, and uses “on-line”. Diagnostic searches recover it with literal `"sleep disorders"` but not the frozen fuller population branch containing `"sleep disorder*"`; literal `"on-line"` matches where bare `online` does not. The returned keyword metadata include related sleep and online-intervention labels, but those labels alone do not establish how each text expression will match.

These are observed differences for two records, not a general claim that truncation, keywords or hyphens are always handled this way. The [clause diagnostics](results/clause_diagnostics.json), [term checks](results/term_diagnostics.json) and [raw diagnostic responses](archives/diagnostics/) retain the evidence. They also show why dropping the trial filter could not rescue these misses: both already passed it.

## Export checks and limitations

OpenAlex accepted the first cursor request, then returned HTTP 401 because continuing cursor pagination requires a free API key. No key was configured. The protocol allowed a documented fallback to ordinary pages, which succeeded. The [deviation record](execution_deviations.json) and [failed response](archives/A_fuller_embase/page_002.json) preserve that limitation.

All three exports used numbered pages sorted by publication date, with an additional empty terminal page. Every page reported a consistent total; each export had exactly that many rows and distinct IDs, with no duplicate IDs. This supports completeness of the observed export, but is not a historical index snapshot or proof that a changing API could never omit and substitute records between requests.

The smaller counts are **potential screening volumes**, not measured screening-time savings. Today's OpenAlex metadata and coverage differ from what was available at the review's search date, even with the publication cutoff. No new results were screened for eligibility, so this test does not estimate precision or establish that the original benchmark contains every eligible article. The offline checks establish consistency of saved evidence, not independent validation of the review's inclusion decisions.

## What this adds to the first experiment

The stronger claim from the diabetic-eye-screening exercise did not transfer to these frozen searches: **the greater-than-95% target was missed by one article**. OpenAlex contained all 29 benchmark articles, but the translated text conditions recovered only 27.

The result is still useful. A source-derived adaptation returned 718 records and recovered 93.1% of the benchmark without repairs informed by missed titles. The predefined attempt to reduce reliance on the trial filter more than doubled result volume without increasing known recovery. Subsequent diagnostics identified concrete search behavior worth investigating in another development phase.

The next search could test explicit keyword filters, literal variants and hyphenated forms. That would be retrospective repair on this benchmark and would need a new independent test before claiming those changes generalise. The present outcome gives the follow-up post its central distinction: coverage, frozen-query retrieval and performance after inspecting misses are separate findings.

## Reproduce and inspect

- [Frozen protocol](PROTOCOL.md), [freeze manifest](freeze_manifest.json) and [syntax/OQO validations](validation/).
- [Source provenance and hashes](source_provenance.json); [29 extracted references](results/benchmark_source.json); [DOI mappings](results/benchmark_matches.json).
- Unrestricted pages: [A](archives/A_fuller_embase_numbered/), [B](archives/B_compact_numbered/), [C](archives/C_fuller_without_trial_filter_numbered/).
- [Per-article retrieval matrix](results/per_article_retrieval.csv), [aggregate results](results/summary.json) and [evidence checksums](SHA256SUMS).

Run the offline verifier from the repository root:

```bash
python3 transfer_benchmark_2026-11-12/verify.py
```

It requires only Python's standard library and makes no requests. It checks hashes, frozen queries against executed OQO filters, 29 DOI mappings, page counts, distinct IDs, the full-denominator matrix, thresholds and diagnostic results.

`run_test.py SOURCE_XML` is an explicitly live runner. It expects the source XML identified in `source_provenance.json`, verifies its hash, and resumes from archived responses instead of overwriting evidence. A fresh index replication belongs in a new output copy with a separate date and provenance. `diagnose_misses.py` runs the labelled post-evaluation diagnostics. Do not use broad test discovery to replay the repository.

The full source article and supplement are not redistributed here; provenance points to the publisher/Europe PMC copies. The archived OpenAlex responses and bibliographic facts support inspection of this test.
