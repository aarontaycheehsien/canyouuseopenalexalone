# Can OpenAlex recover the studies in a systematic review? Testing its new search language

*One paper's title contained “diabetic retinopathy”, yet my search missed it. Investigating why led to a query that recovered all 130 indexed benchmark records—and some useful lessons about what that result establishes.*

One paper in my benchmark had “diabetic retinopathy” in its title, yet my search missed it. I initially suspected the proximity operator. Testing the clauses separately showed that the problem was another word: **unscreened**. My screening block contained `screen*`, which did not match it.

That small discovery became part of a larger exercise. On **2 November 2026**, an adapted OpenAlex query recovered **all 130 known indexed benchmark records**, with **3,892 results reported by the API**. All 130 IDs also appeared in the ordinary downloaded results, without restricting the search to those IDs. The download contained a duplicate, which I will return to.

I developed the final query after inspecting the records earlier versions missed. So the result shows what I could achieve while developing a search against a known benchmark. Whether that strategy works as well before I have read the missed titles is the next question.

For me, the attraction is practical. Could an open resource make comprehensive searching available to more review teams, while reducing the work of translating searches across databases and combining their results? In [my earlier post on scholarly discovery](https://aarontay.substack.com/p/revisiting-my-2020-predictions-about), I wondered what would happen when OpenAlex improved its search engine. Its new OpenAlex Query Language, or OQL, gave me a reason to investigate.

This post follows three discoveries: a vocabulary gap, a query that meant something different from what I intended, and a geographical restriction that excluded relevant records. The complete strategies, individual outcomes and archived responses are linked below.

## A benchmark that made the misses visible

[Stansfield and colleagues](https://doi.org/10.1002/cesm.70038) had already investigated OpenAlex using a [systematic map of diabetic eye screening implementation](https://doi.org/10.3310/gjao0707). The map concerned programmes in the United Kingdom, Canada, Australia, New Zealand and Ireland. Its searches covered 26 information resources, produced 12,293 unique records to screen and led to 131 included records.

Those resources included databases, academic search engines and websites. The main database searches took place in December 2023, with supplementary searches in early 2024. This was a systematic map: the [source paper][sourcearticle] describes systematic review methods, but without synthesis or critical appraisal, and without citation searching in the original map. It supplies a useful health-information benchmark, rather than a test of every type of systematic review.

The authors matched 128 of the original 131 records to OpenAlex. They also explored citation and related-record searches, including starting from PubMed results. To investigate additional eligible research, they ranked OpenAlex results with a classifier and screened 2,318 records, finding two additions. My query experiment does not repeat that screening exercise.

Their [deposited reference workbook](https://osf.io/2nrzy/) made the case particularly valuable. I could check individual records and investigate why they disappeared. The denominators are:

| Reference set | Records |
|---|---:|
| Original map | 131 |
| Expanded benchmark, including two additions | 133 |
| Matched OpenAlex records: 128 original plus two additions | 130 |

The [per-study results][matrix] retain all 133 rows. Three pairs of deposited OpenAlex IDs were transposed, and an obsolete ID needed replacing; the [correction log][corrections] records those changes. The three unmatched original records stay in the full-benchmark denominator. Failure to match them is not independent proof that they are absent from OpenAlex.

The historical searches provide context. The paper's Results section reports 21,747 OpenAlex results in July 2024, recovering 126 of the original 131 records. In March 2025, the search returned 16,573 and recovered 123. Three Canadian papers had lost their OpenAlex abstracts and no longer matched. The team's PubMed search returned 2,854 records and recovered 117 of the original 131.

A paper could therefore remain in the index while disappearing from a search. This is one reason I wanted to distinguish coverage from retrieval. The historical counts also have different dates and search conditions: my adapted queries use 2003–2023, while the July OpenAlex figure used a 2003-onwards limit.

## What OQL made possible

OpenAlex connects records of scholarly works with information about authors, institutions, sources, topics and citations. A record can be represented in that network without an abstract, and inclusion does not imply that the full text is openly available.

For searching, the available fields and operators determine how much of a review strategy can be expressed. Proximity asks for words near one another. `eye AND screening` allows the terms to occur far apart; a proximity condition can describe eye screening more specifically. Truncation such as `screen*` reaches words beginning with that prefix, including “screening” and “screened”. OR supplies alternatives, while AND requires concepts together.

The original Stansfield translation replaced proximity with AND, spelled out word variants and split the strategy into nine searches because of the available OpenAlex functionality. Automatically generated keywords were used in place of author keywords. The authors explain those compromises in their [methods][sourcearticle]. OQL offered a way to revisit them.

Some translation gaps remain. Emtree headings and their hierarchy in Embase can retrieve records without relying on the author's wording. An OpenAlex topic filter is a different classification feature; it does not reproduce an Emtree heading or its explosion. OpenAlex-generated keywords are also different from author keywords. Changing the search language cannot supply metadata that a record lacks.

There are several experiments in the repository. This is how they fit together:

| Investigation | Question | Evidence retained |
|---|---|---|
| [October syntax and retrieval pilot][pilot] | Do the translated expressions behave as intended and retrieve known records? | Queries, checks, request logs and membership results. |
| [October cursor study][cursor] | Can result sequences be exported consistently, and where do known records appear? | Complete walks for five modes, ordered IDs, checks and failed-mode records. |
| [1 November fuller Table 8 translation][table8] | How does a fuller adaptation of the published Embase strategy behave? | Query files, generator and reported results; less complete response evidence. |
| [2 November eight-strategy audit][summaryjson] | What do the adapted queries recover, and what changes their result volume? | Exact queries, raw responses, benchmark matches and an unrestricted export. This is the main comparison below. |
| [3 November follow-up][followup] | Does tightening proximity distances preserve benchmark recovery? | Query text and recorded counts; raw responses were not archived. |

The October findings are useful background, but those queries should not be treated as successive versions of every November search. I discuss them separately after the main result.

## First discovery: “unscreened” was outside the screening block

The initial adapted query, labelled **D** in the audit, required “diabetic” near “retinopathy”, “eye” or “retina”, together with screening terms. It returned 3,103 results and recovered 114/130 benchmark records.

The source Embase strategy supplied another route: diabetes terms combined with eye terms near screening or care terms. Restoring that route recovered more records. One remaining miss was [Felfeli and colleagues' paper](https://pubmed.ncbi.nlm.nih.gov/35577027/), *Prevalence and predictors for being unscreened for diabetic retinopathy: a population-based study over a decade*.

Its OpenAlex record lacked an abstract in the audit. To find the failing clause, I restricted each diagnostic query to its verified ID, `W4280598166`:

| Test on Felfeli's record | Matches |
|---|---:|
| `diabetic` and `retinopathy` within 4 words | 1 |
| The full screening-term block | 0 |
| `screen*` alone | 0 |

The proximity condition worked. The title's “unscreened” fell outside the prefix `screen*`.

An abstract might have supplied “screening” or another term in the block. Without it, the title and other available searchable fields had to do more of the work. That connects this individual miss to the original study's finding about abstract removal.

Adding `unscreen*` was a vocabulary repair worth testing. The evidence for that diagnosis is unusually concrete: the requests and returned counts are in `responses/Felfeli_proximity.json`, `responses/Felfeli_screening_block.json` and `responses/Felfeli_screen_star.json` inside the [live-query audit ZIP][livezip]. There is a worked example for following this record through the outputs at the end.

## Second discovery: the accepted query was not the query I meant

I also tried a fallback using OpenAlex's primary topic, *Retinal Diseases and Treatments*, combined with screening or care terms. I put the topic condition inside `about (...)`.

The expression validated. But the returned query object treated `topic is T10170` and `title-abstract-keywords has` as search text, rather than the field conditions I intended. The isolated branch returned zero works.

OQL is the expression submitted to the API. The OpenAlex Query Object, or OQO, records its structured interpretation. Looking at that object showed which fields and operators the API had actually used. Here, the parser had accepted a legal text search with a meaning I did not intend.

Moving the topic condition to the `where` level repaired that mistake. In the E comparison, the reported count rose from **3,701 to 5,574**, and benchmark recovery rose from **126 to 127**. Felfeli was recovered.

That is 1,873 additional reported results for one additional known benchmark record. I did not screen the extra results, so I cannot say how many other eligible studies they contained. The interpretation and isolated test are preserved in `responses/inert_topic_validator.json` and `responses/inert_topic_alone.json` in the [same archive][livezip].

The lesson I would take into another search is to inspect how an unfamiliar expression was interpreted. A successful validation response alone would not have exposed this mistake.

## Third discovery: my geographical shortcut excluded relevant records

Three records still escaped corrected E: Ho (2006), Lewis (2022) and Sachdeva (2012). They lacked an author-country value in the audited metadata, and my shortened list of geographical terms did not rescue them. Ho's title names Australia's Northern Territory, which my list omitted.

Author affiliation is an imperfect way to search for study setting. A relevant study may lack a resolved country, or its authors may be based outside the country studied. Conversely, an author in an eligible country can research a programme elsewhere. Place names in titles and abstracts offer another route, provided those names appear in the available text and are included in the search.

A broad exception accepting unknown author country recovered all 130 benchmark records, but returned **12,985** results. A narrower exception accepted unknown country when the title contained “diabetic retinopathy screening” or “diabetic eye screening”. With the corrected topic clause, this returned **5,764** results and recovered all 130.

I chose those phrases after examining the missed titles. Ho's example also makes my own role in the misses clear: shortening the place-name list changed retrieval. These were not simply records missing from the database.

## What the repairs changed

The eight-strategy audit used the same 130 verified benchmark IDs throughout. D and corrected G2 came verbatim from the earlier draft. Other variants were reconstructed from the changes described there and executed for the audit; they are not a complete contemporaneous record of every earlier attempt.

Each label links to the exact OQL used:

| Search strategy | API-reported results | Indexed benchmark recovered |
|---|---:|---:|
| [D: condition-side proximity][D] | 3,103 | 114/130 |
| [E: second route, misplaced topic clause][Ei] | 3,701 | 126/130 |
| [E: corrected topic clause][Ec] | 5,574 | 127/130 |
| [G1: broad unknown-country exception][G1] | 12,985 | 130/130 |
| [G2: narrow exception, misplaced topic clause][G2i] | 3,891 | 129/130 |
| [G2: narrow exception, corrected topic clause][G2] | 5,764 | 130/130 |
| [G2: corrected clause, tighter proximity distances][G2s] | 5,734 | 130/130 |
| [Narrow exception, omit topic fallback, add `unscreen*`][final] | **3,892** | **130/130** |

The final row combines the narrow geographical exception with `unscreen*` and removes the topic fallback. It recovered all 130 benchmark records with **1,872 fewer reported results than corrected G2**. Felfeli no longer needed the working topic branch to be retrieved.

These changes answer different questions. It helps to make them explicit:

| Change | What kind of change was it? | What the evidence supports |
|---|---|---|
| Move the topic condition out of `about (...)` | Repair an expression that did not implement the intended field filter. | E increased from 126/130 to 127/130, with 1,873 more reported results. |
| Add the narrow unknown-country exception | Change the strategy after inspecting missed titles. | Corrected E to corrected G2 recovered three more benchmark records, with 190 more reported results. |
| Add `unscreen*` and omit the topic fallback | Change vocabulary after diagnosing a miss, and change the strategy's retrieval routes. | The final query recovered 130/130 with 3,892 reported results. |
| Shorten the concept and place-name lists | Adapt the source strategy. | There is no complete comparison isolating every shortening decision from the other changes. |

That last point is especially important when comparing the final query with the [fuller Table 8 translation][table8]. Its S1 search reportedly returned 11,257 results and recovered 127/130. Why did the shorter strategy recover more in fewer results? The later targeted repairs are part of the explanation, but this is not a controlled test of shortening alone. The strategies differ in several ways, and their response evidence is not equally complete.

The fuller translation report also records a useful warning: `"DES program*"`, intended to find diabetic eye screening programmes, matched French “des programmes”. The reported fix required `diabet*` with the phrase. This illustrates why transferring vocabulary into a large multidisciplinary index needs checking as well as translating operators.

The final query's structure is straightforward even though its text is long. One topical route combines condition-side proximity with screening terms, including `unscreen*`. Another combines `diabet*` with eye/screening or eye/care combinations and programme or teleophthalmology alternatives. The geographical block accepts an eligible author country, retained place-name text, or the narrow title-based unknown-country exception. Publication years are limited to 2003–2023.

The [CSV summary][summary] and [per-study matrix][matrix] show the aggregate and individual outcomes. Recovering all indexed benchmark records means **128/131 original records** or **130/133 expanded records**, approximately **97.7%** in either case. It says nothing directly about the eligibility of the other returned records. Their number is a potential screening burden, not a measurement of screening time or precision.

## Checking the download as well as the search count

For each strategy, the audit obtained an unrestricted total, then tested the same query restricted to the verified benchmark IDs. The membership responses preserve the actual returned IDs.

For the final strategy, the unrestricted download provides another check. All 130 IDs appeared in its twenty numbered pages, without a benchmark restriction. That strengthens the recovery claim beyond relying on the restricted queries alone.

However, the pages contained **3,892 rows and 3,891 distinct IDs**. A non-benchmark ID appeared twice. I can support recovery of all 130 benchmark records, but cannot describe this as a verified complete download of 3,892 distinct works. The saved counts do not establish whether the underlying result set stayed fixed between requests.

The [intersection output][intersection] identifies the duplicate and records that no benchmark IDs were missing. The [full-benchmark ZIP][fullzip] contains the individual pages, so readers can check the intersection themselves.

There is also a follow-up on the proximity distances. OpenAlex's [translation guide](https://help.openalex.org/how-to/search-strategies-from-other-databases/) maps Ovid `adj4` and `adj6` to `within 3` and `within 5`. The final audited query used windows of 4 and 6. On 3 November, the [tighter version][followup] was recorded as returning 3,857 results and 130/130 benchmark records. That follow-up retained query text and counts, but no raw responses. The 3,892 figure remains the main result here because its archived responses can be examined.

## What I would take into the next search

This makes me more interested in OpenAlex as a starting point for a review like this. The practical gain was being able to diagnose a missed record, change a specific clause and inspect the consequence for the result set.

I would still plan supplementary searching. Three original benchmark records remain unmatched. The original authors' two additional discoveries also show why even a carefully assembled benchmark should not be treated as an exhaustive list of eligible research. Their citation, related-record and PubMed combination searches offer relevant possibilities beyond the Boolean strategies tested here.

I would keep a record of which terms came from the review question and source strategy, and which were added after examining misses. Knowing that a geographical exception reaches three titles I have already read is useful for search development. To evaluate its wider value, I would freeze the strategy and test it on another review or update whose records had not guided those choices.

Historical figures give a sense of scale: 3,892 reported matches is a manageable number to contemplate beside the original map's 12,293 screened records. They do not establish work saved or superiority to PubMed or Embase. Search terms, dates, index contents and the processes producing those numbers differ. Screening previously unlabelled results would also be necessary to assess relevance beyond the benchmark.

For another experiment, I would preserve the query and its parsed interpretation, investigate individual misses before broadening whole blocks, and check the exported IDs as well as the reported count. The result here is encouraging precisely because it can be examined at that level. The next challenge is recovering the studies whose titles I have not already read.

## Supporting context: what happened in October?

Readers interested in the earlier experiments can follow the [retrieval pilot][pilot] and [cursor report][cursor]. They answer related questions using different frozen queries.

The October normalized union of the published searches returned 23,217 works and recovered 126/131 original records. Restoring text operators returned 21,679 and recovered 125/131. Adding keywords increased the count to 26,152 and recovered 126/131; removing geography increased it to 46,770 with 127/131 recovered. Broadening could recover known misses, but with substantial increases in volume.

The [syntax pilot][syntax] completed 98 checks, with 94 passing and four failing. The failures concerned scoring and pagination; two assessed the same missing-score condition. The full-text arm also failed execution in the research pilot, leaving its performance unavailable.

The subsequent cursor study validated five complete walks, checking repeated pages, page sizes, unique IDs and counts. A cursor is a token supplied by the API to request the next batch. Those walks support the consistency of the observed exports, but do not validate the final November query's export or establish that the intended relevance algorithm was applied correctly.

Ordering was a separate concern. In October's published-strategy cursor sequence with relevance requested, only 3/131 original records appeared in the first 1,000, and 125/131 had appeared by position 19,600. The restored OQL default sequence had 29/131 in its first 1,000. These were different ordering modes with documented API limitations. The fixed-candidate reranking test started with no original benchmark records among its 100 candidates, so rearranging them could not recover a benchmark record. It is not a general test of reranking's usefulness.

An [additional nine-branch proximity experiment][partial] was incomplete. Its observed recovery is a lower bound and is not included as a completed strategy in the November table. Keeping these outcomes separate prevents a successful membership result from becoming a claim that every retrieval and ranking component worked.

## Search strategy and evidence files

The evidence links are pinned to repository commit `d8a0ded`. They identify the files used for this post even if later experiments are added. The offline verifier recalculates findings from saved responses; a new live search against a changing index may produce different results.

### The complete final query

This is a line-wrapped display copy of [`exploratory_unscreen_no_topic.oql`][final]. Only whitespace outside quoted phrases and entity labels has changed for readability. The linked file remains the canonical executed text. In the archived OQO, its `about` expression searches title/abstract/keywords.

```text
get works from 2003–2023 about ((((diabetic and retinopathy within 4 words of each other) OR
(diabetic and eye within 4 words of each other) OR (diabetic and retina within 4 words of each
other)) AND (screen* OR unscreen* OR program* OR surveillance OR monitor* OR exam* OR check* OR
teleophthalmolog* OR "tele-ophthalmology" OR teleretin* OR "tele-retinal" OR retinascreen* OR
keepsight OR "keep sight" OR slick)) OR (diabet* AND ((eye and screening within 6 words of each
other) OR (retinal and screening within 6 words of each other) OR (retinopathy and screening within
6 words of each other) OR (eye and care within 6 words of each other) OR (eye and examination within
6 words of each other) OR teleophthalmolog* OR "tele-ophthalmology" OR teleretin* OR retinascreen*
OR keepsight OR slick))) where country is ([United Kingdom](GB) or [Canada](CA) or [Australia](AU)
or [New Zealand](NZ) or [Ireland](IE)) or title-abstract-keywords has (UK OR "United Kingdom" OR
Britain OR British OR England OR English OR Scotland OR Scottish OR Wales OR Welsh OR Ireland OR
Irish OR Canada OR Canadian OR Australia OR Australian OR "New Zealand" OR Ontario OR Quebec OR
Alberta OR Gloucestershire OR Auckland) or (country is unknown and title has
("diabetic retinopathy screening" OR "diabetic eye screening"))
```

### Follow one record from a miss to the downloaded result

Felfeli's verified OpenAlex ID is **`W4280598166`**. Its source and verified IDs are identical; it was not one of the identifier corrections.

1. In the [per-study CSV][matrix], find EPPI ID `93511073` or the OpenAlex ID. D and E with the misplaced topic clause show “Not retrieved”; the final `exploratory_unscreen_no_topic` column shows “Retrieved”.
2. In the [live-query ZIP][livezip], inspect `responses/Felfeli_proximity.json`, `responses/Felfeli_screening_block.json` and `responses/Felfeli_screen_star.json`. They record the single-record tests and counts of 1, 0 and 0.
3. In the [full-benchmark ZIP][fullzip], open `verified_exploratory_unscreen_no_topic_benchmark.json`. The record is the 119th item in `response.results`, with the matching ID and title.
4. Open `unrestricted_final_pages/page_07.json` in that same ZIP. It appears as the 118th item in `response.results`, confirming its presence in the download without a benchmark-ID restriction. These positions locate entries in archived files; they are not a claim about a validated relevance rank.
5. To check the entire benchmark, inspect the [intersection output][intersection] and run the verifier below. It checks that all 130 verified IDs are present across the downloaded pages.

The 3,892 total is a different observation: it is the API's `meta.count` in `exploratory_unscreen_no_topic_total.json`. Deduplicating the downloaded page IDs produces 3,891. Both numbers need to remain visible.

### Files for checking the other results

| Evidence | What to inspect |
|---|---|
| [Per-study retrieval CSV][matrix] | All 133 benchmark records, source and corrected IDs, and retrieval outcomes for each strategy. |
| [Recall summary CSV][summary] and [JSON][summaryjson] | All eight totals, cohort-specific recovery and, in JSON, the missed records. |
| [Verified benchmark IDs][ids] and [correction log][corrections] | The fixed 130-ID evaluation set and the changes to deposited identifiers. |
| [Full-benchmark ZIP][fullzip] | Original workbook, requests, responses, timestamps and twenty unrestricted result pages. |
| [Live-query audit ZIP][livezip] | OQL, parsed query objects, clause-level Felfeli tests and the misplaced-topic diagnostics. |
| [Unrestricted intersection check][intersection] | 3,892 rows, 3,891 distinct IDs, the duplicate, and all 130 benchmark IDs recovered. |
| [Evidence checksums][hashes] and [offline verifier][verifier] | File-integrity checks and recalculation of the archived findings. |

Inside the full-benchmark ZIP, each strategy has a `<strategy>_total.json` and a `verified_<strategy>_benchmark.json`. Use the `verified_` membership files; the archive also preserves earlier responses made before identifier correction. The twenty unrestricted pages are named `unrestricted_final_pages/page_01.json` through `page_20.json`.

The November audit has the strongest support for the principal comparison because readers can inspect the queries, returned IDs and raw responses together. The fuller Table 8 translation and 3 November follow-up retain reports and query text with less complete response evidence. The October experiments have their own logs and limitations.

### Recalculate the archived findings

Clone the repository, select the pinned evidence revision and run the verifier with Python 3.11:

```bash
git clone https://github.com/aarontaycheehsien/canyouuseopenalexalone.git
cd canyouuseopenalexalone
git checkout d8a0ded5bd0487f0e98383fc1f34019672b389d8
python3 stansfield_pilot/audit_2026-11-02/verify.py
```

The verification step uses Python's standard library, needs no API key and makes no API requests. It checks evidence hashes, benchmark sizes, returned IDs, the per-study matrix, reported totals, saved query text and executed query objects. It also checks the unrestricted benchmark intersection and the three Felfeli clause tests. It now runs in CI alongside the existing offline regression tests.

Passing those checks establishes consistency of the archived evidence and calculations. It does not independently validate the original eligibility decisions, certify every search operation, or show how the strategy will perform on another review.

[corrections]: https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/d8a0ded5bd0487f0e98383fc1f34019672b389d8/stansfield_pilot/audit_2026-11-02/benchmark/id_corrections.json
[matrix]: https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/d8a0ded5bd0487f0e98383fc1f34019672b389d8/stansfield_pilot/audit_2026-11-02/results/per_study_retrieval.csv
[table8]: https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/d8a0ded5bd0487f0e98383fc1f34019672b389d8/stansfield_pilot/queries/embase_table8_oql_2026/README.md
[livezip]: https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/d8a0ded5bd0487f0e98383fc1f34019672b389d8/stansfield_pilot/audit_2026-11-02/archives/OpenAlex_live_query_audit_2026-11-02.zip
[fullzip]: https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/d8a0ded5bd0487f0e98383fc1f34019672b389d8/stansfield_pilot/audit_2026-11-02/archives/OpenAlex_full_130_benchmark_audit_2026-11-02.zip
[summary]: https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/d8a0ded5bd0487f0e98383fc1f34019672b389d8/stansfield_pilot/audit_2026-11-02/results/recall_summary.csv
[summaryjson]: https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/d8a0ded5bd0487f0e98383fc1f34019672b389d8/stansfield_pilot/audit_2026-11-02/results/recall_summary.json
[intersection]: https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/d8a0ded5bd0487f0e98383fc1f34019672b389d8/stansfield_pilot/audit_2026-11-02/results/unrestricted_intersection_check.json
[cursor]: https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/d8a0ded5bd0487f0e98383fc1f34019672b389d8/stansfield_pilot/cursor_study_2026-10-04/CURSOR_ORDER_REPORT.md
[followup]: https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/d8a0ded5bd0487f0e98383fc1f34019672b389d8/stansfield_pilot/followup_2026-11-03/README.md
[ids]: https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/d8a0ded5bd0487f0e98383fc1f34019672b389d8/stansfield_pilot/audit_2026-11-02/benchmark/benchmark_130_verified_ids.txt
[hashes]: https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/d8a0ded5bd0487f0e98383fc1f34019672b389d8/stansfield_pilot/audit_2026-11-02/SHA256SUMS
[verifier]: https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/d8a0ded5bd0487f0e98383fc1f34019672b389d8/stansfield_pilot/audit_2026-11-02/verify.py
[pilot]: https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/d8a0ded5bd0487f0e98383fc1f34019672b389d8/stansfield_pilot/PILOT_REPORT.md
[partial]: https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/d8a0ded5bd0487f0e98383fc1f34019672b389d8/stansfield_pilot/queries/LEGACY_UNION_PROXIMITY_NOTES.md
[D]: https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/d8a0ded5bd0487f0e98383fc1f34019672b389d8/stansfield_pilot/audit_2026-11-02/queries/D_exact.oql
[Ei]: https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/d8a0ded5bd0487f0e98383fc1f34019672b389d8/stansfield_pilot/audit_2026-11-02/queries/E_inert_reconstructed.oql
[Ec]: https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/d8a0ded5bd0487f0e98383fc1f34019672b389d8/stansfield_pilot/audit_2026-11-02/queries/E_corrected_reconstructed.oql
[G1]: https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/d8a0ded5bd0487f0e98383fc1f34019672b389d8/stansfield_pilot/audit_2026-11-02/queries/G1_reconstructed.oql
[G2i]: https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/d8a0ded5bd0487f0e98383fc1f34019672b389d8/stansfield_pilot/audit_2026-11-02/queries/G2_inert_reconstructed.oql
[G2]: https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/d8a0ded5bd0487f0e98383fc1f34019672b389d8/stansfield_pilot/audit_2026-11-02/queries/G2_exact.oql
[G2s]: https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/d8a0ded5bd0487f0e98383fc1f34019672b389d8/stansfield_pilot/audit_2026-11-02/queries/G2_strict_reconstructed.oql
[final]: https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/d8a0ded5bd0487f0e98383fc1f34019672b389d8/stansfield_pilot/audit_2026-11-02/queries/exploratory_unscreen_no_topic.oql
[sourcearticle]: https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/d8a0ded5bd0487f0e98383fc1f34019672b389d8/stansfield_pilot/sources/article.txt
[syntax]: https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/d8a0ded5bd0487f0e98383fc1f34019672b389d8/OQL_VALIDATION_REPORT.md
