# Exercise for depression: frozen transfer-test protocol

The user requested another benchmark with at least 10,000 screening records. Select Noetel et al. (2024), *Effect of exercise for depression: systematic review and network meta-analysis of randomised controlled trials*, DOI https://doi.org/10.1136/bmj-2023-075847, article https://pmc.ncbi.nlm.nih.gov/articles/PMC10870815/ and public data https://osf.io/nzw6u/.

The review explicitly reports **13,115 titles and abstracts screened after 5,505 duplicates were removed**, and **218 included studies**. The authors' `referencing_information_included_studies.csv` has exactly **218 citation rows**; the characteristics table has 218 study-heading rows. Use every citation row as the primary denominator, regardless of OpenAlex coverage. This is recovery of the representative citations supplied by the authors, not an assertion that every companion publication from each trial is enumerated. Preserve and investigate any duplicate citations without silently changing the denominator.

Walker et al.'s transgenerational evidence map was also considered (63,758 unique records), but accessing its source data was less straightforward. No candidate OpenAlex retrieval performance was inspected for either review during selection.

## Information boundary

Before freezing, only the review methods, aggregate screening/inclusion counts, search-strategy document, file listings, citation-file column names/nonempty counts, and structural table counts were inspected. No included citation titles, identifiers, abstracts or OpenAlex coverage/results were read. The source citation file and characteristics table were downloaded but not displayed. This is a procedural holdout, not independent human blinding or formal registry preregistration. Previous benchmark experience informed the design. Commit and push this protocol and exact query hashes before opening citation identities or running searches.

## Frozen searches

Both queries search title/abstract/OpenAlex keywords in the default core corpus, with no lower date bound and publication date through **2023-06-03**, the review's final database-search date. No language, country, human/animal or document-type filters, topic IDs or benchmark IDs are in the unrestricted searches.

**A, fuller source concepts:** depression/dysthymia/seasonal-affective vocabulary AND a broad exercise block primarily from SPORTDiscus plus controlled-heading labels elsewhere in the source AND the union of trial-design terminology across the source databases. This is a concept-level adaptation, not the Boolean union of five faithfully translated database searches. CENTRAL's absence of an RCT block is not reproduced. Controlled-vocabulary labels become text; hierarchy and indexing are not reproduced. Source proximity becomes document-level AND, intentionally broadening it. Prefixes consolidate word forms. `depress*` broadens the source's narrower depression expressions. The exact construction is in `build_queries.py`.

**B, compact three concepts:** depression/dysthymia AND common exercise modalities and activity phrases AND random/trial/placebo/control prefixes. It omits some broad activity combinations and less specific trial terms. It has no terms selected using benchmark titles. A and B differ in multiple vocabulary choices, so their comparison does not isolate query length.

Source strategies were retrieved from OSF's S1 document. They cover CENTRAL, MEDLINE, Embase, PsycINFO and SPORTDiscus. The article describes SPORTDiscus via Embase, while S1 says EBSCO; retain S1 as the query source and do not claim exact platform replication. Source reference-list searching is not reproduced.

## Measurement

Primary threshold: **strictly greater than 95% of all 218 supplied citations**, requiring **208/218**. Keep unmatched and ambiguous records in the denominator as unrecovered; report coverage and recall among matched citations separately. Use DOI first, PMID when available, then title/author/year evidence. Exact DOI agreement must be checked against the returned canonical DOI. Fuzzy matches require explicit adjudication; preserve candidates and decisions. Multiple citation rows mapping to one work remain visible.

Obtain unrestricted counts and retain the first 200 results. Evaluate membership using the identical parsed executed OQO with only an AND restriction to verified benchmark IDs, in batches of at most 100. Archive requests, raw responses, status codes and UTC timestamps. The historical 13,115 is a deduplicated screening workload, but differences in sources, time, record types and matching mean lower current OpenAlex volume is not proof of screening-time savings or equivalent eligibility precision.

No API key is configured. Prior work established that continuing cursor pagination requires a key. For result counts at most 9,800 attempt complete numbered exports, including an empty terminal page and count/ID consistency checks. For larger results keep the first page and count; clearly label recovery as restricted membership, without complete unrestricted-export validation. Do not revise queries or switch benchmarks after seeing results.

After primary results are preserved, missed-record metadata or separately labelled clause diagnostics may be examined. No post-hoc query repairs are part of the primary test. No new relevance screening or precision estimate is planned. Preserve source hashes, query hashes, mapping evidence, per-citation results and an offline verifier. Source documents and abstracts stay in scratch storage; archive only the bibliographic and API evidence necessary for audit. Run explicit offline checks, not broad discovery over historical scripts that make live requests.
