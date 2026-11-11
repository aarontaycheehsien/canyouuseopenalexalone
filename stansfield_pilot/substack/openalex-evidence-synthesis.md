# Can you use OpenAlex alone for a systematic review? What I found when I tried

*An adapted search recovered all 130 indexed benchmark records. The interesting part was working out why it missed some of them in the first place.*

What would it take for a systematic review team to start with OpenAlex? For a librarian, the attraction is easy to see. An open database could make comprehensive searching accessible to more people, and perhaps reduce the work of translating strategies across several databases and deduplicating their results. But how much relevant research would we miss, and how much would we have to screen?

In [my earlier post on scholarly discovery](https://aarontay.substack.com/p/revisiting-my-2020-predictions-about), I wondered what would happen when OpenAlex improved its search engine. Its new OpenAlex Query Language (OQL), with proximity searching and more expressive combinations of fields, gave me a reason to investigate.

Here is the headline: on **2 November 2026**, an adapted query recovered **all 130 known indexed benchmark records**, with **3,892 results reported by the API**. I had inspected the missed studies before arriving at that query. This was an exercise in developing a search against a known benchmark, and the distinction matters.

I have linked the search strategies, record-level results and archived API responses below. There is also an offline verifier, so readers can check the principal results without an OpenAlex API key.

## What would “OpenAlex alone” actually involve?

OpenAlex brings together records of scholarly works and connects them with information about authors, institutions, sources, topics and citations. That gives a searcher several possible ways to find research: words in searchable metadata, subject-related fields, and links between records. Having an OpenAlex record does not guarantee that the record contains an abstract or that the full text is openly available.

For a review team, “alone” is quite a demanding word. It would mean that the resource could supply enough of the relevant literature, let us express the review's concepts adequately, and deliver a usable result set for screening. It would also mean accepting whatever we lose by omitting other databases and supplementary methods.

Those losses may be difficult to see. A query can return thousands of plausible records while silently excluding a report whose title uses different wording, a paper with an absent abstract, or a study without usable country metadata. An ordinary search session does not tell us which relevant records never appeared.

That is why a benchmark is valuable. We can start with records already judged relevant and ask where they disappear. I found it helpful to distinguish four questions:

| Question | What would answer it? |
|---|---|
| Is the record represented in OpenAlex? | Matching it by identifiers and bibliographic details. |
| Does the search retrieve it? | Checking whether its ID belongs to the query's returned set. |
| Can I obtain the result set reliably? | Downloading pages and checking unique IDs, counts and completeness. |
| Will I encounter useful records early enough? | Evaluating a reproducible ordering against known relevant records. |

A good answer to the first question does not settle the other three. The experiments in this repository gradually made that distinction much more concrete.

## Why this was a useful test case

[Stansfield and colleagues](https://doi.org/10.1002/cesm.70038) had already investigated OpenAlex using a [systematic map of diabetic eye screening implementation](https://doi.org/10.3310/gjao0707). The original map searched 26 information resources, screened 12,293 unique records and included 131 records. The authors found 128 of those 131 in OpenAlex. Screening a subset of the OpenAlex results also identified two further eligible records.

Better still, they deposited a [reference workbook](https://osf.io/2nrzy/). That made it possible to ask which particular records a search missed, rather than simply compare result counts.

The underlying topic was the implementation of diabetic eye screening programmes in the United Kingdom, Canada, Australia, New Zealand and Ireland. This helps explain the geographical blocks that recur in the searches. A clinically relevant paper about diabetic retinopathy could still be outside the map's intended scope.

The source was a systematic map, rather than a conventional synthesis of treatment effects. As the [Stansfield paper describes][sourcearticle], it used systematic review methods but did not undertake synthesis or critical appraisal, and the original map did not conduct citation searching. Its 26 information resources included databases, academic search engines and websites. The main database searches took place in December 2023, with supplementary searching in early 2024.

So this is a useful health-information case, but not a test of every kind of systematic review. I would not assume that a search for an intervention, a qualitative experience, a diagnostic test and a rare adverse event would depend on the same metadata or behave equally well.

There are three numbers to keep in mind:

- **131** records in the original map.
- **133** in the expanded benchmark, including the two additional records.
- **130** with matched OpenAlex IDs: 128 original records plus the two additions.

The deposited IDs needed some cleaning. Three pairs were transposed, and an obsolete ID needed replacing. The [correction log][corrections] retains the source and corrected mappings; the [per-study results][matrix] retain all 133 benchmark rows. The three unmatched original records remain in the full-benchmark denominator. Failure to match them does not independently prove they are absent from OpenAlex.

The original study also gives useful historical context. Its July 2024 Boolean search retrieved 126 of the original 131 records from 21,747 results, according to the paper's Results section. In March 2025, the search returned 16,573 results and recovered 123. The authors reported that three Canadian papers had lost their abstracts from OpenAlex and no longer matched. Their PubMed search returned 2,854 records and recovered 117 of the original 131.

Those are the authors' historical results, not searches I reran alongside this experiment. My adapted searches use a 2003–2023 window; the July OpenAlex figure used a 2003-onwards limit. The terms, metadata and index dates also differ.

There is another important part of their work. The authors did not simply download the OpenAlex results and count known papers. They also explored citation and related-record searches, including starting from PubMed results. To look for additional eligible records, they ranked results with a classifier and screened 2,318 records, identifying the two additions. My query experiment does not repeat that screening exercise or evaluate all those search routes.

The changing abstract coverage is especially relevant to the later Felfeli example. The original study found that a paper could remain in the index while disappearing from a Boolean search. Its searchable description had changed. A reduction in the number of search results therefore needs investigation before we treat it as an improvement.

## Translating a search involved more than adding proximity

Proximity lets us ask for words near one another. A search for eye terms near screening terms can express something more specific than requiring both somewhere in a record.

For example, `eye AND screening` allows the two ideas to occur far apart. Requiring them near each other can help describe eye screening more specifically. Truncation asks for a prefix and its continuations: `screen*` can reach forms such as “screening” and “screened”. OR joins alternative descriptions; AND requires concepts to occur together. Field restrictions determine which parts of a record can satisfy those conditions.

In the original Stansfield translation, the available OpenAlex functionality led the authors to replace proximity with AND, spell out word variants and split the strategy into nine searches. OpenAlex's automatically generated keywords were used in place of author keywords. Their [methods][sourcearticle] explain these compromises. OQL offered a reason to revisit them, but it could not restore information missing from the records.

Controlled vocabulary is another difference. An Embase strategy can use Emtree headings and their hierarchy to retrieve records without requiring the author's exact words. An OpenAlex topic filter is a different classification feature; using it as a fallback does not reproduce the original heading or its explosion. Similarly, OpenAlex-generated keywords should not be assumed to be author-supplied keywords or equivalent to database indexing.

I used the published Ovid Embase strategy as a starting point. But two different exercises emerged: a fuller Table 8 translation, and a shorter, adapted strategy. The smaller result set discussed here comes from the adapted strategy, with shortened concept and place-name lists.

The [fuller translation report][table8] records 11,257 results and 127/130 benchmark records for its S1 search. It also describes a wonderfully instructive problem: `"DES program*"`, intended to find diabetic eye screening programmes, matched French “des programmes”. The recorded fix required it to occur with `diabet*`.

That is exactly the sort of thing I would want to investigate when moving a strategy into a large multidisciplinary index. The fuller translation still approximates controlled vocabulary and omits some Embase exclusions. Its figures are recorded in the report, but do not have the same archived-response support as the eight-strategy audit below.

So I would be careful about attributing the eventual reduction in results to proximity alone. Search development involved vocabulary, fields, geographical restrictions and metadata as well.

## The earlier experiments were less tidy

The November result did not come from a single direct translation. The repository preserves an [October pilot][pilot] in which the normalized union of the published searches returned 23,217 works and recovered 126/131 original records. A strategy restoring text operators returned 21,679 and recovered 125/131. Adding keywords increased the count to 26,152 and recovered 126/131. Removing geography increased it again, to 46,770, with 127/131 recovered.

That is a useful reminder of the usual tradeoff. Broadening a search can recover a known miss, but the additional records may be numerous. Conversely, introducing more specific operators can lose a known record as well as reduce the total. These October figures belong to their own frozen query families and run dates; they are not intermediate versions of every November query.

Before relying on those searches, the [syntax pilot][syntax] tested Boolean combinations, field scope, phrases, wildcards and proximity on a finite corpus. Of 98 checks, 94 passed and four failed. The failures concerned scoring and pagination, with two checks assessing the same missing-score condition. A full-text arm also failed execution in the research pilot, so its performance remains unavailable.

This history matters because “the query ran” is a fairly modest milestone. The work moved from checking expressions, to identifying known records, to validating exports and examining ordering. The smaller November strategy was another search-development exercise within that larger investigation.

## One word in a title changed my explanation

The initial adapted query, labelled **D** in the audit, put proximity on the condition side: “diabetic” near “retinopathy”, “eye” or “retina”, together with screening terms. It returned 3,103 results and recovered 114/130 benchmark records.

The Embase strategy allowed another route: diabetes terms combined with eye terms near screening or care terms. Restoring that route recovered more records. But one remaining miss was especially revealing.

[Felfeli and colleagues' paper](https://pubmed.ncbi.nlm.nih.gov/35577027/) is titled *Prevalence and predictors for being unscreened for diabetic retinopathy: a population-based study over a decade*. Its OpenAlex record lacked an abstract in the audit. Initially, I suspected the proximity requirement.

Testing the clauses separately changed that explanation. Restricted to this paper's OpenAlex ID, the archived requests show:

| Test on Felfeli's record | Matches |
|---|---:|
| `diabetic` and `retinopathy` within 4 words | 1 |
| The full screening-term block | 0 |
| `screen*` alone | 0 |

The title says **unscreened**. The prefix `screen*` does not start there.

An abstract might have supplied “screening” or another term in the block even when the title did not. Without it, the title and the other available searchable fields had to do more of the work. This connects the individual miss to the original study's broader finding about abstract removal.

The practical response was to test a vocabulary change: add `unscreen*`. I would not conclude from this one example that every screening search needs the same addition. Its value here was demonstrated against an identified missed record; the general value of the term would need checking on other searches.

These are actual returned counts, preserved in `responses/Felfeli_proximity.json`, `responses/Felfeli_screening_block.json` and `responses/Felfeli_screen_star.json` inside the [live-query audit ZIP][livezip]. This is why I find record-level tests useful: the broad explanation “the proximity search missed it” concealed the clause that actually failed.

## A query can validate and still mean something else

I also tried recovering such records through OpenAlex's primary topic, *Retinal Diseases and Treatments*, combined with screening or care terms. Here I made another mistake: I put the topic condition inside `about (...)`.

The validator accepted the expression. But the returned query object treated `topic is T10170` and `title-abstract-keywords has` as text to search, rather than the field conditions I intended. The isolated branch returned zero works.

OQL is the expression I submit; the OpenAlex Query Object, or OQO, records its structured interpretation. Inspecting that object lets me see which fields and operators the API actually used. It is rather like checking how a database translated a search instead of assuming the display string tells the whole story.

Here, that distinction explained why there was no obvious syntax error to fix. The system had accepted a text search that was legal but unhelpful. A familiar-looking phrase containing a field name was not necessarily being used as a field condition.

Moving the topic condition to the `where` level made it work. In the E comparison, the API-reported count rose from **3,701 to 5,574**, and benchmark recovery rose from **126 to 127**. Felfeli was recovered.

That is 1,873 additional reported results for one additional known benchmark record. I did not screen those extra results, so I cannot say how many other eligible studies they contained.

The parsed expression and isolated test are preserved in `responses/inert_topic_validator.json` and `responses/inert_topic_alone.json` in the [same archive][livezip]. Successful validation answered whether OpenAlex accepted the expression. Inspecting its interpretation answered whether I had expressed the search I meant.

## Geography created another set of misses

Three records still escaped the corrected E search: Ho (2006), Lewis (2022) and Sachdeva (2012). They lacked an author-country value in the audited OpenAlex metadata, and my shortened geographical terms did not rescue them. Ho's title, for example, names Australia's Northern Territory, which my list omitted.

The distinction between author affiliation and study setting matters here. Even complete affiliation metadata would not guarantee that an author-country filter captures where the research took place.

There are two different ways this can go wrong. A relevant study may have no resolved affiliation country, or its authors may be based somewhere other than the study setting. Conversely, an author in an eligible country can write about a programme elsewhere. Searching country names in titles and abstracts provides another route, but relies on those places being named in the available text.

The original strategy's longer place-name lists and the adapted query's shorter list therefore have real consequences. Ho's Northern Territory title is a particularly clear example of a miss introduced by my choices. It would be misleading to frame all three failures as a database-coverage problem.

A broad exception accepting unknown author country recovered all 130 benchmark records, but the result count reached **12,985**. A narrower exception accepted unknown country when the title contained “diabetic retinopathy screening” or “diabetic eye screening”. With the corrected topic clause, this produced **5,764** results and recovered all 130.

I chose those title phrases after examining the misses. They explain how the search reached this benchmark, but their performance on an unseen review remains an open question.

## What each change bought

The table below comes from the **2 November audit**, with the same 130 verified IDs used throughout. Each strategy label links to its complete executed OQL text.

D and corrected G2 were taken verbatim from the earlier draft. The other variants were reconstructed from the described changes and executed for this audit. The table therefore documents those tested expressions; it is not a complete contemporaneous log of every earlier search-development attempt.

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

The last row was the most useful result for me. Adding `unscreen*` to the screening block allowed the search to recover Felfeli without the working topic fallback. Compared with corrected G2, it returned **1,872 fewer reported results with the same benchmark recovery**.

The [CSV summary][summary] and [per-study matrix][matrix] let readers inspect the aggregate and individual outcomes. Full recovery here means **128/131 original records** or **130/133 expanded records**: approximately **97.7%** in either case. It does not mean every eligible study on this topic has been found.

Nor is result volume a direct measurement of screening time. I did not assess the previously unlabelled records, measure precision, or test a stopping rule.

## Reading the final strategy in plain language

The full query near the end of this post is long, but its structure can be read in a few parts. It limits publication years to 2003–2023 and gives the topical search two routes. One looks for “diabetic” near a retinopathy, eye or retina term and also requires a screening-related term. This is where `unscreen*` was added. The other combines `diabet*` with eye/screening or eye/care proximity combinations and named programme or teleophthalmology alternatives.

The geographical condition then supplies alternative ways to qualify: an eligible author country, one of the retained place terms in title/abstract/keywords, or the narrow unknown-country exception in the title. The final strategy omits the topic fallback. This account explains the structure; the linked OQL and archived OQO specify the executable details.

It is tempting to compare 3,892 directly with the original 12,293 records screened across 26 resources. I would use that comparison to explain scale, not to calculate a percentage of work saved. The original map's workload followed its own searches and deduplication process. My API count comes from a later index and a strategy tuned to known records, and its export has a discrepancy discussed below.

Likewise, recovering more of this benchmark than the historical PubMed search does not establish that OpenAlex is generally more sensitive. PubMed supplied abstracts for some records that had lost them in OpenAlex, and the source study explored combining the two. Different sources can contribute at different points in the search.

## Did the downloaded records support the headline?

For each strategy, the audit executed the unrestricted query to obtain its reported total, then the same query restricted to the verified benchmark IDs to measure recovery. The archived membership responses contain the returned IDs, allowing the matches to be counted rather than inferred from a search-total figure.

For the final `unscreen*` strategy, there is a second check: the unrestricted download, without a benchmark-ID filter. **All 130 verified benchmark IDs appeared in those pages.**

There was also a problem. The twenty numbered pages contained **3,892 rows but only 3,891 distinct IDs**. A non-benchmark ID appeared twice. Counting rows alone would have hidden that discrepancy.

I can therefore support the benchmark-recovery claim from both routes. I cannot describe the export as 3,892 distinct downloaded works or claim that it proves complete enumeration of a fixed result set. The [intersection output][intersection] records the counts and duplicated ID; the individual pages are inside the [full-benchmark archive][fullzip].

An [earlier October cursor study][cursor] completed five walks whose unique totals matched the reported counts and passed repeatability checks. Those were different queries. It also found problems with relevance sorting and reranked continuation, so I would not use it to promise that the relevant studies in this November search will appear near the top. Set recovery, complete export and useful ranking each need checking.

A cursor is a continuation token returned by the API to request the next batch. In those October tests, the checks included repeated starting pages, different page sizes, unique-ID totals and repeated pages near the beginning, middle and end. That gives stronger evidence about the observed sequences than seeing a successful first page.

The ordering results also show why finding records somewhere in a large set is different from finding them early. For the published-strategy cursor sequence with relevance requested, only 3/131 original records appeared in the first 1,000; 125/131 had appeared by position 19,600. The restored OQL strategy's default sequence had 29/131 in its first 1,000. These figures are from the October [cursor report][cursor], not the final November query. Requested relevance and default order were distinct modes, and the observed API problems prevent treating these as a general evaluation of OpenAlex's intended relevance algorithm.

The fixed-candidate reranking experiment has another limitation worth making explicit: its first 100 candidates contained no original benchmark records. Rearranging those same candidates could not introduce a missing benchmark record. That says something about that candidate pool; it does not establish that reranking is ineffective in general.

There is a smaller follow-up worth recording. OpenAlex's [translation guide](https://help.openalex.org/how-to/search-strategies-from-other-databases/) maps Ovid `adj4` and `adj6` to `within 3` and `within 5`. The final audited query used windows of 4 and 6. A [3 November check][followup] recorded 3,857 results and 130/130 recovery with the tighter windows, alongside 3,892 and 130/130 for the wider query. Only query text and counts were retained for that follow-up. I use 3,892 as the main result here because its raw-response evidence is available.

## Would I use OpenAlex alone?

I would now be more interested in evaluating OpenAlex as a starting point for a review like this. The useful discovery was that I could identify why a known record disappeared, repair a particular clause and measure the change in result volume.

I would still plan supplementary searching. Three original benchmark records remain unmatched. The two additional records found by Stansfield and colleagues also remind us that the original map was not an exhaustive list of everything eligible. A search developed with access to missed titles has an advantage it will not have on a new topic.

The next test I would find persuasive is to freeze the strategy before evaluating another review or a later update, and then screen results to learn what lies beyond the known benchmark. Historical comparisons with PubMed and Embase are useful for scale, but they cannot tell us whether this adapted search performs better under equivalent conditions.

What would I take into practical search development? I would retain the original query, its parsed interpretation, the date and the result count at each substantial revision. When a known record is missed, I would test its concept and geographical clauses separately before broadening the whole strategy. When a repair succeeds, I would record both the additional benchmark records and the change in the search total.

I would also keep a distinction between terms chosen from the review question and terms added after looking at missed titles. Both can be useful while developing a search, but only an evaluation on records that did not guide those choices can tell us how well the resulting strategy travels. The geographical exception is an especially important candidate for that test.

Finally, I would budget for checking the export and for supplementary discovery. The original paper's use of citation and related-record searches is relevant here. My results provide a reason to investigate an OpenAlex-centred workflow; they do not evaluate every component needed to complete one.

For now, I have a promising result and a way to examine it. The question I would carry into the next experiment is whether the same approach can recover the studies whose titles I have not already read.

## Search strategy and evidence files

The links below are pinned to repository commit `d8a0ded`, so they identify the evidence used for this post even if later experiments are added. The figures describe the archived runs; a fresh query against a changing OpenAlex index may return different results.

The complete final search is reproduced below, unchanged from [`exploratory_unscreen_no_topic.oql`][final]. Its `about` expression is represented as title/abstract/keyword searching in the archived parsed query. It retains the narrow geographical exception and the wider proximity windows used for the 3,892-result audit.

```text
get works from 2003–2023 about ((((diabetic and retinopathy within 4 words of each other) OR (diabetic and eye within 4 words of each other) OR (diabetic and retina within 4 words of each other)) AND (screen* OR unscreen* OR program* OR surveillance OR monitor* OR exam* OR check* OR teleophthalmolog* OR "tele-ophthalmology" OR teleretin* OR "tele-retinal" OR retinascreen* OR keepsight OR "keep sight" OR slick)) OR (diabet* AND ((eye and screening within 6 words of each other) OR (retinal and screening within 6 words of each other) OR (retinopathy and screening within 6 words of each other) OR (eye and care within 6 words of each other) OR (eye and examination within 6 words of each other) OR teleophthalmolog* OR "tele-ophthalmology" OR teleretin* OR retinascreen* OR keepsight OR slick))) where country is ([United Kingdom](GB) or [Canada](CA) or [Australia](AU) or [New Zealand](NZ) or [Ireland](IE)) or title-abstract-keywords has (UK OR "United Kingdom" OR Britain OR British OR England OR English OR Scotland OR Scottish OR Wales OR Welsh OR Ireland OR Irish OR Canada OR Canadian OR Australia OR Australian OR "New Zealand" OR Ontario OR Quebec OR Alberta OR Gloucestershire OR Auckland) or (country is unknown and title has ("diabetic retinopathy screening" OR "diabetic eye screening"))
```

The evidence has several levels. The eight-strategy November comparison has exact queries, returned IDs, archived responses and derived summaries that can be checked against one another. The fuller Table 8 translation and the 3 November follow-up retain useful reports and query text, but their supporting files are less complete. The October pilot and cursor study have their own logs, queries and limitations. These should be read as distinct experiments rather than pooled into one larger successful run.

For example, checking whether the final query found Felfeli means following its corrected ID into the membership response and the unrestricted pages. Checking the 3,892 total means reading the API's `meta.count`. Checking the number of distinct downloaded works requires deduplicating the page IDs. Those are different checks, even though they all concern the same search.

For readers who want to audit a result, these are the useful starting points:

| Evidence | What to inspect |
|---|---|
| [Per-study retrieval CSV][matrix] | All 133 benchmark records, source and corrected IDs, and retrieval outcomes for each strategy. |
| [Recall summary CSV][summary] and [JSON][summaryjson] | All eight totals, cohort-specific recovery and, in JSON, the missed records. |
| [Verified benchmark IDs][ids] and [correction log][corrections] | The fixed 130-ID evaluation set and the changes to deposited identifiers. |
| [Full-benchmark ZIP][fullzip] | Original workbook, requests, responses, timestamps and twenty unrestricted result pages. |
| [Live-query audit ZIP][livezip] | OQL, parsed query objects, clause-level Felfeli tests and the misplaced-topic diagnostics. |
| [Unrestricted intersection check][intersection] | 3,892 rows, 3,891 distinct IDs, the duplicate, and all 130 benchmark IDs recovered. |
| [Evidence checksums][hashes] and [offline verifier][verifier] | File-integrity checks and recalculation of the archived findings. |

Inside the full-benchmark ZIP, the final result is supported by `exploratory_unscreen_no_topic_total.json`, `verified_exploratory_unscreen_no_topic_benchmark.json` and `unrestricted_final_pages/page_01.json` through `page_20.json`. The other strategies follow the same `<strategy>_total.json` and `verified_<strategy>_benchmark.json` naming pattern. Use the `verified_` membership files: the archive also preserves earlier responses made before identifier correction.

To check the evidence locally, clone the repository, select the pinned revision and run the verifier with Python 3.11:

```bash
git clone https://github.com/aarontaycheehsien/canyouuseopenalexalone.git
cd canyouuseopenalexalone
git checkout d8a0ded5bd0487f0e98383fc1f34019672b389d8
python3 stansfield_pilot/audit_2026-11-02/verify.py
```

The verification step needs only Python's standard library and makes no API requests. It checks the listed evidence hashes, benchmark sizes, returned IDs, per-study matrix, reported totals, saved query text and executed query objects. It also checks the unrestricted export and the three Felfeli clause tests above. Hash agreement establishes consistency with the saved manifest, not independent certification of the research. The verifier is now included in CI alongside the existing offline regression tests.

For the wider investigation, the repository retains the [October pilot][pilot], [cursor-order study][cursor] and [incomplete nine-branch proximity experiment][partial]. The latter's observed recovery is a lower bound from an unfinished run and is not included as a completed strategy in the table above.

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
