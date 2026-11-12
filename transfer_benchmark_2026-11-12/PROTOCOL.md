# Independent-review transfer test: protocol frozen before benchmark inspection

## Selection

Selected review: Hwang et al. (2025), *Systematic review and meta-analysis on fully automated digital cognitive behavioral therapy for insomnia*. DOI: https://doi.org/10.1038/s41746-025-01514-4. Public text: https://pmc.ncbi.nlm.nih.gov/articles/PMC11903857/.

The review reports 29 included articles, 3,101 records identified and 1,974 records screened after deduplication. It searched PubMed, CENTRAL, Embase and PsycINFO through 31 March 2024. Its supplement supplies each database's strategy in Supplementary Table 2 (PDF page 18). Its article contains an included-study table and references. This is a different condition and intervention from the diabetic-eye-screening map and has no geographical eligibility restriction.

Selection was based on public methods, recoverable search syntax, a reported full-benchmark denominator and screening volume, and topic independence. No OpenAlex coverage or recovery result was used to select it. The sample is small: one article represents 3.45 percentage points of recall. This is one external case study, not a representative sample of reviews.

Candidates considered during discovery:

| Candidate | Selection consideration |
|---|---|
| Hwang et al. 2025, fully automated digital CBT for insomnia | Selected: accessible article and supplement; Embase strategy; 29 included articles; explicit deduplicated screening count. |
| eHealth versus in-person CBT for insomnia, 2024, PMC11384180 | Public methods and search supplement reported; narrower head-to-head question. Not taken forward once the selected review met the criteria. No retrieval performance assessed. |
| Behavioural components of CBT for insomnia in older adults, PMC10909422 | Public methods describe a MEDLINE strategy; 15 studies gives a smaller benchmark. No retrieval performance assessed. |
| Packaged SYNERGY dataset | Useful for later screening research, but the packaged data are OpenAlex work objects. Their matched subset must not substitute for every original included record. Original review denominators would need reconciliation. No labelled rows inspected. |

This was a purposive feasibility search, not an exhaustive search for benchmarks. Candidate sources: https://pmc.ncbi.nlm.nih.gov/articles/PMC11384180/, https://pmc.ncbi.nlm.nih.gov/articles/PMC10909422/, https://github.com/asreview/synergy-dataset/blob/master/README.md.

## Information boundary

Before freezing, the operator read the selected review's methods, aggregate selection counts, and search-strategy page, but did not inspect included-study titles, the characteristics table, bibliography entries, OpenAlex matches, or benchmark recall. The complete source XML and supplement were downloaded locally; scripts exposed only the allowed sections. Search snippets included general background and numbered citations, not an extracted list of included titles.

This is a procedural holdout within an AI-assisted session. It is not independent human blinding, a formal registry preregistration, or a guarantee that the model has never encountered these publications in training. The protocol and query files are committed before opening the benchmark. Once frozen, any change to the search concepts or limits must be a separately labelled exploratory analysis.

## Fixed search designs

All queries use title/abstract/OpenAlex keywords, the default core corpus, and a publication-date upper bound of 2024-03-31 with no lower bound. No country, author, institution, language, document-type, abstract-availability, or benchmark-ID filters are added. No topic IDs are selected. Default API corpus/retraction behavior will be reported from execution; this is not a claim to search all possible records in OpenAlex.

The supplement lists concept blocks, rather than a complete line-numbered Embase command. The adaptation assumes OR within blocks and AND between population, intervention, delivery and study-design blocks.

- **A — Fuller Embase text adaptation (primary baseline):** retain all four source concepts and the complete delivery-mode list. Represent the sleep-disorder and behavior-therapy headings by text labels; include British and American behavior spellings and truncate therapy/disorder endings. Retain the source `random*` design filter. Exploded Emtree headings cannot be reproduced by this text adaptation: no claim of exact Embase equivalence is made.
- **B — Compact text candidate (primary transfer candidate):** narrow the population to insomnia, collapse British/American spelling variants using `behavio*`, and omit the `random*` filter to avoid depending on whether trial design appears in searchable metadata. Retain the complete delivery-mode list. These choices come from the review question and source strategy, before seeing included titles. No product names or missed-record vocabulary are added.
- **C — Fuller adaptation without trial filter (prespecified sensitivity):** identical to A except for removal of `random*`. This isolates the effect of the trial filter and helps interpret A versus B; it is not a third independently developed success demonstration.

The exact OQL files in `queries/` are authoritative. The API's free translation endpoint is used to validate them and inspect their OQO interpretation before execution. Any syntax-only corrections before freezing are retained in validation records. No candidate result counts or titles are inspected during query design. A generic kelp query was used solely to confirm API execution was available.

## Benchmark and matching

After freezing, extract every included article reference from the review's characteristics table, reconciling its 29 reported inclusions against unique reference entries. Use article/report-level recovery as the primary unit, not an assumed count of independent trials. If the table and reported denominator disagree, report the discrepancy before drawing a threshold conclusion; do not silently discard records.

Resolve identifiers using exact DOI or PMID matches where available. For unresolved records, use title, author and year and record the evidence and uncertainty. Keep unmatched or ambiguous originals in the full denominator and report them separately. Deduplicate OpenAlex IDs for coverage calculations while retaining every original benchmark row. Report any many-to-one mappings.

## Execution and outcomes

Execute unrestricted queries and archive requests, UTC timestamps, HTTP status, parsed interpretations and raw responses. Export all result pages with cursor pagination where supported. Fall back to ordinary pages only with an explicit deviation record. Check row count, distinct IDs, repeated pages, count drift, terminal pagination and actual benchmark intersections. A count alone does not establish a complete export.

Primary outcomes for A and B:

1. Fraction of **all 29 original included articles** recovered in unrestricted results, including unmatched records in the denominator.
2. API result volume, downloaded rows and distinct downloaded IDs.
3. Whether recovery is **strictly greater than 95%** (at least 28/29) and reported result volume is **at most 1,974**, the review's original deduplicated screening count. An export inconsistency makes completeness uncertain and must accompany any threshold statement.

Secondary: matched-record coverage, recall conditional on matched records, C's sensitivity results, and record-level reasons for misses. Historical screening counts and today's publication-date-limited OpenAlex results are not directly measured time savings. Records and metadata may have been added or changed after the original search.

No relevance screening of new results is prespecified in this first test. Known-inclusion yield is not precision: unlabelled results may contain eligible studies. No claim that OpenAlex can replace all systematic-review sources follows from passing the threshold.

## Analysis boundary and preservation

Inspect misses only after the frozen searches and initial intersections have been saved. Diagnostic metadata checks may explain misses without altering primary queries. Any repaired query must be separately labelled exploratory and cannot overwrite A, B or C. A repair is optional; the requested test is complete when the frozen results and limitations are documented, even if performance is poor.

Save a report, per-article matrix, raw API evidence, source provenance, query hashes and an offline verifier. Do not run repository-wide test discovery because archived scripts may execute live searches. Retain source publication URLs and hashes; do not redistribute the full review or supplement as original project content.
