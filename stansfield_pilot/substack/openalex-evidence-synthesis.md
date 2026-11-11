# Can OpenAlex find the studies a systematic review found?

*I tested the new OpenAlex Query Language against a published diabetic eye screening review. One word in one title changed what I thought the search needed.*

What would it take for a systematic review team to start with OpenAlex? The attraction for a librarian is obvious. Translating a strategy across databases takes time, as does deduplicating the results. But a large index is only useful if you can retrieve the relevant studies without sending an unmanageable number of records to screening.

In [my recent post on scholarly discovery](https://aarontay.substack.com/p/revisiting-my-2020-predictions-about), I wondered what would happen when OpenAlex improved its own search engine. Here was a chance to test it. A published systematic map of diabetic eye screening programmes came with something unusually useful: the authors had shared the OpenAlex IDs of the studies they found. I could try a search, see precisely which studies it missed and ask why.

My final search retrieved **all 130 known indexed records in 3,892 results** on 2 November 2026. It took several attempts to get there, and I had seen the missed studies before writing the final query. The most instructive part of the exercise was what happened to a paper with the word “unscreened” in its title.

## Why this review made a useful test

The [original map by O’Mara-Eves and colleagues](https://doi.org/10.3310/gjao0707) examined how diabetic eye screening programmes were implemented in five countries. Searches across 26 resources produced 12,293 unique records to screen and 131 included records. [Stansfield and colleagues](https://doi.org/10.1002/cesm.70038) found that OpenAlex held 128 of those 131. They also found two further eligible records when they screened a subset of the OpenAlex results. That gives us two useful denominators: **133 records in the expanded map, 130 with OpenAlex IDs**. The deposited IDs needed a little cleaning before use: three pairs were transposed and one was obsolete. The [audit](https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/267ea4ea3893a773d0acf557ae77db9a589a1768/stansfield_pilot/audit_2026-11-02/benchmark/id_corrections.json) keeps both the deposited and corrected mappings.

In July 2024, the authors’ nine OpenAlex Boolean searches returned [21,747 records in the paper’s Results section](https://pmc.ncbi.nlm.nih.gov/articles/PMC12302543/) after deduplication and a 2003-onwards limit, and retrieved 126 of the original 131. In March 2025, repeating those searches returned 16,573 records and retrieved 123. Three Canadian papers that had matched in July dropped out after their abstracts were removed. For comparison, the team’s PubMed search returned 2,854 records and retrieved 117 of the original 131. PubMed supported proximity searching at the time. OpenAlex did not.

The [OpenAlex Query Language (OQL)](https://help.openalex.org/access/oql/) now lets a searcher combine word proximity, truncation and conditions across fields in one query. I adapted the published Ovid Embase strategy, shortened its concept and place-name lists, and tested it on the November 2026 index. The shortening matters. A [fuller translation of the same Embase strategy](https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/a637343/stansfield_pilot/queries/embase_table8_oql_2026/README.md), which I ran separately, returned 11,257 results and retrieved 127 of the 130 benchmark records. My adapted query covered publications from 2003 to 2023. Stansfield’s July figure used a 2003-onwards limit. The search terms, date window and version of the index all differed, so the comparison cannot isolate the effect of proximity searching. OpenAlex also [documents what changes when a strategy is translated](https://help.openalex.org/how-to/search-strategies-from-other-databases/), including the loss of subject-heading explosion.

## The paper that changed the search

My first proximity version required “diabetic” near “retinopathy”, “eye” or “retina”, together with a screening term. It returned 3,103 records and retrieved 114 of the 130. Consider a title about *retinopathy screening for people with diabetes*. The screening words sit together, but the condition may be expressed further away and in a different form. The Embase strategy allowed for both arrangements. Restoring a second route that looked for eye terms near screening or care terms helped recover such records.

One paper still puzzled me. [Felfeli and colleagues](https://pubmed.ncbi.nlm.nih.gov/35577027/) examined which adults with diabetes in Ontario went unscreened for diabetic retinopathy. Their [OpenAlex record](https://openalex.org/works/W4280598166) had no abstract. At first I attributed the miss to the proximity requirement. Testing the clauses separately showed exactly where that explanation went wrong. “Diabetic retinopathy” passed the proximity test. The entire screening block failed. The title says **unscreened**, and the truncation `screen*` looks for words that *start* with “screen”.

I could also recover Felfeli by using its OpenAlex primary topic, *Retinal Diseases and Treatments*, alongside a search for screening or care terms. Here I made a different mistake. I put the topic condition inside `about (...)`. The validator accepted it, but the parsed query treated the field names as search text. Tested on its own, that branch returned zero records. Moving the condition to `where` made it work. Across the full strategy, the change added **1,873 results to recover one more known study**. Some of those additional results might also be eligible. I did not screen them.

## The geography problem

Three papers still escaped the corrected search: Lewis (2022), Sachdeva (2012) and Ho (2006). All three lacked an author-country value in OpenAlex, and my list of geographical search terms did not rescue them. Ho’s title, for example, names Australia’s Northern Territory, a place my shortened list omitted. This is a broader limitation of using affiliation to search for study setting. An author based overseas can study an Australian programme, even when every affiliation is recorded correctly.

Allowing every record with an unknown author country through the geographical filter recovered all 130 studies, but returned 12,985 results. I tried a narrower exception: accept an unknown country if the title contains “diabetic retinopathy screening” or “diabetic eye screening”. That added 190 records to the corrected search, bringing the total to 5,764 and recovering the three misses. I chose those phrases **after reading their titles**. A different study could describe the same programme in entirely different words.

## What each change bought

These are live result counts from 2 November 2026. The recall column uses the same 130 indexed benchmark records throughout. The audit reran the first query and corrected G2 verbatim from the earlier draft, and reconstructed the other variants from the changes described there. The [full audit](https://github.com/aarontaycheehsien/canyouuseopenalexalone/tree/267ea4ea3893a773d0acf557ae77db9a589a1768/stansfield_pilot/audit_2026-11-02) gives the eight queries and the outcome for every study.

| Query version | Records returned | Benchmark records found |
|---|---:|---:|
| Require proximity on the condition side only | 3,103 | 114/130 |
| Restore the second search route, with the misplaced topic clause | 3,701 | 126/130 |
| Correct the topic clause | 5,574 | 127/130 |
| Add the narrow unknown-country exception to the corrected query (G2) | 5,764 | 130/130 |
| Use the narrow exception with the misplaced topic clause | 3,891 | 129/130 |
| Keep the narrow exception, omit the topic clause and add `unscreen*` | **3,892** | **130/130** |

The last two rows are the comparison I would have missed if I had only looked at the headline recall figure. Adding `unscreen*` in place of the ineffective topic branch brought the count up by one and recovered Felfeli. Compared with the working topic version, it returned **1,872 fewer records** with the same benchmark recall. I also checked the unrestricted download. Its 20 numbered pages contained 3,892 rows but only 3,891 distinct IDs, one fewer than the API-reported total. Checking the row count alone would have missed the duplicate. All 130 benchmark IDs appeared in those pages. In my [earlier paging tests](https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/23a85c8bbf70139e9a9383cd23b69ca08e9a32c2/stansfield_pilot/cursor_study_2026-10-04/CURSOR_ORDER_REPORT.md), cursor-based paging returned as many unique IDs as the API reported.

OpenAlex’s [translation guide](https://help.openalex.org/how-to/search-strategies-from-other-databases/) maps Ovid’s `adj4` and `adj6` to `within 3` and `within 5`. My [original query used windows of 4 and 6](https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/23a85c8bbf70139e9a9383cd23b69ca08e9a32c2/stansfield_pilot/followup_2026-11-03/queries/final_exact.oql). On 3 November, the [query with windows of 3 and 5](https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/23a85c8bbf70139e9a9383cd23b69ca08e9a32c2/stansfield_pilot/followup_2026-11-03/queries/final_strict_adj.oql) returned 3,857 results and still found all 130 benchmark records. The wider query returned 3,892 in the [same follow-up](https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/89a588d27e760537d44ff50711d757ba8c095f6d/stansfield_pilot/followup_2026-11-03/README.md). This follow-up retained the query text and counts, but did not archive the raw API responses.

## Would I start a review with OpenAlex?

For a topic like this, I would consider it as a starting point. What changed my view was being able to diagnose *why* a known paper disappeared, adjust one clause, and measure what that adjustment cost. That is something a librarian can use when developing a search.

I would still plan supplementary searches. Finding 130/130 indexed records represents **130/133 (97.7%) of the expanded map**. And the result I most want to know for the next review is how many eligible studies a search like this would find *before* I knew their titles. The two studies OpenAlex added to the original map are a reminder that even a carefully assembled benchmark can be incomplete.

The next test I would find persuasive is a search whose terms are fixed in advance and evaluated on another review or a later update. For now, this case gives me a specific answer: an adapted OpenAlex query recovered every indexed benchmark record with a result set small enough to merit comparison with conventional searches. For scale: 3,892 results, against 2,854 for the team’s PubMed search, 5,069 for their [Embase search](https://doi.org/10.3310/gjao0707) and 12,293 records screened across all 26 resources. How well that strategy travels is still an open question.

*Note on missing abstracts.* The [November publisher check (archived ZIP)](https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/267ea4ea3893a773d0acf557ae77db9a589a1768/stansfield_pilot/audit_2026-11-02/archives/OpenAlex_live_query_audit_2026-11-02.zip) found 308,942 Elsevier article records from 2024–2025 that lacked an OpenAlex abstract but had a PMID. Those identifiers offer a way to check whether PubMed supplies additional searchable text. A PMID alone does not establish that an abstract is available there.

[Original benchmark spreadsheet](https://osf.io/2nrzy/) · [Per-study retrieval results](https://github.com/aarontaycheehsien/canyouuseopenalexalone/blob/267ea4ea3893a773d0acf557ae77db9a589a1768/stansfield_pilot/audit_2026-11-02/results/per_study_retrieval.csv) · [Archived search evidence](https://github.com/aarontaycheehsien/canyouuseopenalexalone/tree/267ea4ea3893a773d0acf557ae77db9a589a1768/stansfield_pilot/audit_2026-11-02/archives)
