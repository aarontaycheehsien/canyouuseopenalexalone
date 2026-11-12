# Larger-workload independent-review test: frozen protocol

## Benchmark selection and scope

The user requested an additional test using a review with more records screened in the original study. Select Kennis et al., *Prospective biomarkers of major depressive disorder: a systematic review and meta-analysis*, published online in 2019 and in the 2020 volume of Molecular Psychiatry. DOI: https://doi.org/10.1038/s41380-019-0585-z. Public article: https://pmc.ncbi.nlm.nih.gov/articles/PMC6974432/.

The review reports **67,464 articles screened** and **75 unique prospective articles/studies included**. A structural count confirms that Table 1 cites 75 distinct bibliography reference IDs. All 75 will constitute the benchmark, regardless of OpenAlex coverage. Search topics span seven biological systems; PubMed, PsycINFO and Embase were searched, followed by citation/reference checks and an update in June 2019.

The screening count is not a verified unique-record total. The authors explicitly say it may include duplicate screening across biomarker classes. The supplement's per-search flow table also has internally inconsistent counts; simply adding its reported screening cells gives 51,843, not 67,464. Retain the main article's number as a reported workload context, not a corrected deduplicated denominator or a basis for claiming screening-time savings.

The public supplement supplies **PubMed** strings. It says the translated Embase and PsycINFO strategies are available on request; those were not obtained. This tests source-derived concepts in OpenAlex, not an exact Embase replication. No authors are contacted as part of this task.

Brouwer et al. (2019), depressive relapse/recurrence, was considered first: the paper reports 66 articles, while its accessible raw screening dataset has 63 inclusion labels and the packaged SYNERGY data have 62. Access to the detailed appendix was also problematic. It was not selected because reconciling those sources would require additional work before a defensible full-benchmark test. No OpenAlex performance was evaluated for it. The larger Walker evidence map was considered at metadata level; Kennis was selected once its methods, source strings and complete benchmark structure were accessible.

## Information boundary

Before freezing, the operator read Kennis's methods, aggregate results, source search Appendix A and flow-count Appendix B. Scripts counted Table 1 reference IDs without printing the table's article identities. Two author labels in a forest-plot caption (Charles and Cosgriff) appeared while locating supplementary material; no included-study titles, DOIs, OpenAlex IDs, matched coverage or candidate search results were inspected. These incidental labels were not used to build queries.

The prior insomnia test is complete, and its general lessons can inform this second design. Independence here means that the new benchmark's retrieval failures have not guided the frozen queries. It does not imply independent human blinding, an absence of prior model-training exposure, or formal registry preregistration. Commit and push this protocol and query hashes before opening the 75 references.

## Frozen query designs

Common settings: title/abstract/OpenAlex keywords; default core corpus; no lower date bound; upper publication date **2019-06-30**, because the review reports an update in June without a day. No benchmark IDs, country filters, selected topic IDs, language filters, document-type exclusions or human/animal classification filters appear in the unrestricted queries. API defaults apply to retractions.

### A — Fuller source-derived union

Reconstruct the conceptual Boolean structure of the seven initial source searches and carry it through the June 2019 cutoff:

```text
Depression population
AND (
  Longer prediction/prognosis block AND
    (neuroimaging OR neurotrophic OR other hormones OR oxidative stress)
  OR Shorter prediction/prognosis block AND
    (gastrointestinal OR immunology)
  OR neurotransmitters
  OR gonadal hormones
)
```

The source neurotransmitter and gonadal-hormone searches do not have a prediction block; retain that distinction. `vocabulary.json` records the extracted lists; `extract_search_terms.py` and `build_queries.py` make extraction and construction reviewable.

This is an adaptation of source concepts, not verbatim execution of a valid PubMed expression. The supplement contains inconsistent quotes, parentheses, field syntax and delimiters. Before looking at benchmark titles, normalize curly quotes, remove PubMed/Embase field tags, remove duplicate alternatives, split the fused `nitric oxideOR` delimiter, and use the Dinoprost descriptor without its subheading. Preserve the source's unusual chemical strings containing `7OR8` and spelling `insuline-like`; do not invent corrections using included articles. Interpret the missing conjunction between prediction and neurotrophic terms as AND, following the methods' three-concept description.

MeSH headings become text labels; their hierarchy is not reproduced. Multiword terms become quoted phrases; bare terms use OpenAlex's text behavior. Omit the PubMed-specific human, English and review exclusions rather than assert equivalent classification. The neurotransmitter branch's recent-only text restriction was a workaround for newly unindexed PubMed articles, explicitly not used in the other source databases; use its text throughout the full date range in OpenAlex. The source's exact combined June 2019 update string is not supplied, so this is not a replay of that update.

### B — Compact three-concept candidate

Require depression/affective wording, a shorter prospective/prediction/onset/relapse vocabulary, and a compact biomarker block. Consolidate source families with single-word prefixes and add the conceptual labels `biomarker*`, `inflamm*`, `immune` and `hormon*`. Use source imaging abbreviations and representative neurotransmitter/hormone/oxidative terms, but omit many long chemical variants. All three concepts are required even for neurotransmitters and gonadal hormones.

The exact vocabulary and OQL are fixed in `build_queries.py` and `queries/`. This is an intentional sensitivity/volume tradeoff based on the review question. No result-volume or recall feedback is used to select terms. A and B differ in several ways; their comparison cannot isolate shortening alone.

## Evaluation and access limits

Primary recovery threshold: **strictly greater than 95% of all 75 original included articles**, requiring **72/75**. Retain unmatched/ambiguous articles as unrecovered in that denominator, with coverage and conditional recall reported separately. Deduplicate source citations while retaining every original article; distinguish article-level results from independent cohorts.

For each frozen query obtain an unrestricted count and then run the identical executed OQO with only an additional AND restriction to verified benchmark IDs. Archive all returned IDs, requests, parsed objects, status codes and UTC times. Record-level matching uses DOI first, then PMID, then explicit title/author/year evidence if necessary. No fuzzy candidate is automatically accepted.

Compare reported result volume with the historical **67,464 screening count only descriptively**. Whether OpenAlex uses fewer unique records than the original review cannot be established from that figure. Do not label meeting both a recall threshold and this nonunique count as demonstrated workload savings.

No OpenAlex API key is configured. The insomnia test established that continuing cursor pagination requires a key. For each unrestricted result set with at most 9,800 records, attempt complete numbered-page export with page size 200, publication-date sorting and an empty terminal page. For a larger set, retain a 200-record first page and the unrestricted count; report that no complete export was verified. Benchmark-restricted membership remains a separate retrieval measurement and must not be described as unrestricted-export confirmation. Do not select a different benchmark or revise queries because exports are large.

Only after initial results are saved, inspect misses and run labelled clause diagnostics if useful. Any repaired search is exploratory, must receive a new name, and cannot overwrite the frozen results. No additional relevance screening or precision estimate is planned. An unfavourable result is a complete test outcome.

## Preservation and checks

Preserve source URLs and SHA-256 hashes, source-derived vocabulary, protocol/query hashes, metadata matching evidence, totals, per-article matrix, raw responses and an offline verifier. Full source documents remain in the local working area rather than being redistributed. Use explicit offline verification; do not run broad test discovery over historical live-request scripts.
