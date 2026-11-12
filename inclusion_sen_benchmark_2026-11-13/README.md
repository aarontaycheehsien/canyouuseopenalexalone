# Inclusion of students with special educational needs: OQL POST test against a nine-database review

**None of the three frozen OpenAlex searches came near the recall target of 90 of 94 studies.**

| Arm | Records returned | Studies recovered |
|---|---:|---:|
| A — the reviewers' EBSCO free-text strategy | 18,946 | 34/94 (36%) |
| B — their Web of Science strategy, translated exactly | 3,463 | 22/94 (23%) |
| C — the broadest union of their free-text strategies | 151,147 | 61/94 (65%) |

The authors screened 20,183 records.

**Recall was capped before any search ran.** 15 of the 94 studies do not exist in OpenAlex: 13 dissertations or doctoral papers, one Danish report and one book chapter. That limits any OpenAlex-only search to 79/94 (84%).

**Among the 79 studies OpenAlex holds, the main losses were:**
- The reviewers' "special/additional/educational needs" terms, which in the source databases were backed by thesaurus headings that OpenAlex has no equivalent for.
- Missing abstracts: 21 of the 79 have none in OpenAlex.

Test date: **13 November 2026**. The [protocol and queries were committed and pushed](https://github.com/aarontaycheehsien/canyouuseopenalexalone/commit/7ce6f2f) before any search ran and before the included-studies list was opened.

## Benchmark

[Dalgaard, Bondebjerg, Viinholt & Filges (2022), *The effects of inclusion on academic achievement, socioemotional development and wellbeing of children with special educational needs*](https://doi.org/10.1002/cl2.1291), Campbell Systematic Reviews 18:e1291. The review is open access.

| Reported by the authors | |
|---|---|
| Bibliographic databases | 9 on three platforms. EBSCO: Academic Search Premier, EconLit, ERIC, APA PsycINFO, SocINDEX. ProQuest: IBSS, Sociological Abstracts. Web of Science: SCI-EXPANDED, SSCI |
| Other sources | Dissertation databases, NBER, SSRN, OECD iLibrary, Nordic repositories, Google Scholar, hand searches of 14 journals, reference lists, experts |
| Records screened after deduplication | **20,183**. The database strategies returned 13,791 before deduplication. |
| Included studies | **94** (all non-randomised; 15 in the meta-analysis) |
| Date limit and search dates | From 2000. Databases searched 7–8 April 2021. |

**How it was chosen.** I screened 531 Campbell reviews (2018–2025) for screening loads of 10,000 or more. I rejected those with too few included studies for a recall estimate, evidence-and-gap maps, and one review with 607 studies, which would have taken far longer to match. ([Protocol](PROTOCOL.md))

**Reconciling the benchmark.** The supplement's study-characteristics sheet lists exactly 94 studies. Each pairs with one entry in the article's included-studies reference list. That list has 97 entries; the three extras are not studies: a handbook, the ROBINS-I guidance, and a conceptual paper.

Of the 94 studies, 42 are dissertations or reports, and 52 are journal articles or book chapters.

## Matching: 79 of 94 studies are in OpenAlex

| Type | Studies | In OpenAlex |
|---|---:|---:|
| Journal articles and book chapters | 52 | 51 |
| Dissertations, theses and reports | 42 | 28 |
| **All** | **94** | **79 (84%)** |

OpenAlex holds more dissertations than I expected. Several sit in university repositories, and many are indexed under "ProQuest LLC eBooks". Fourteen are absent even after a broader second search pass ([matches](results/benchmark_matches.json)):
- 11 US dissertations and one US doctoral executive position paper.
- One UK thesis.
- One Danish municipal report.

The 2007 Buckley book chapter is also absent; OpenAlex has only the separate 2006 article. Two match notes:
- One study's year is wrong in the review's spreadsheet (2014 for a 2004 article). It was matched by DOI.
- One dissertation is attributed to a different first name in OpenAlex. The title is identical.

**Recall cannot exceed 79/94 (84%) for any search of OpenAlex alone, before the search strategy matters at all.**

## Results of the frozen searches

Arms are nested (B ⊆ A ⊆ C), all sent as `POST https://api.openalex.org/` with `{"oql": ...}` and limited to 2000-01-01 to 2021-04-08.

| Arm | What it reproduces | Count | Recovered / 94 | Recovered / 79 in OpenAlex | Evidence |
|---|---|---:|---:|---:|---|
| [B — Web of Science, exact](queries/B_web_of_science_exact.oql) | The WoS strategy, text-only, so nothing is dropped | 3,463 | 22 (23.4%) | 22 (27.8%) | Complete export |
| [A — EBSCO free-text core](queries/A_ebsco_text_core.oql) | Five EBSCO strategies minus their subject headings | 18,946 | 34 (36.2%) | 34 (43.0%) | Complete export |
| [C — union of free-text cores](queries/C_union_of_text_cores.oql) | The broadest text variant (IBSS) | 151,147 | 61 (64.9%) | 61 (77.2%) | Restricted membership |

- **No arm meets the >95% threshold (at least 90/94).**
- **Arm A is the only arm with a lower workload.** Its 18,946 records are fewer than the 20,183 screened, but it misses most studies.
- **Arm C recovers the most,** but it returns 7.5 times the screening load.
- **For A and B, the complete cursor exports agree exactly with the restricted-membership results.**

**A direct comparison with Web of Science.** The identical WoS strategy returned 889 records in Web of Science (SCI-EXPANDED + SSCI) in April 2021. In OpenAlex it returns 3,463 over the same years. That is 3.9 times as many from the same text, which reflects OpenAlex's wider coverage (repositories, dissertations and more journals). It recovers only 22 of the 94 studies.

## Why the searches miss: a post-hoc facet diagnosis

Each facet was run alone, restricted to the 79 matched studies ([facet diagnostics](results/facet_diagnostics.json), [per-study matrix](results/per_study_retrieval.csv)).

| Facet (title or abstract unless stated) | Studies matching / 79 |
|---|---:|
| Date window | 78 |
| Has an abstract in OpenAlex | **58** |
| Population: student*, pupil*, child*, youth*, young* | 75 (title only: 62) |
| Need, arm A: title need*/special*/additional*, or abstract special/additional/educational within 5 words of need* | **37** |
| Need, arm B: title only | **31** |
| Need, arm C: title or abstract, no proximity | 68 |
| Intervention: integrat*, immers*, inclus*, mainstream*, placement* | 70 |
| Method: effect*, trial*, experiment*, control*, random*, impact*, compar*, difference* | 72 |

**The "need" facet is where arms A and B lose most studies.** Fewer than half of the included studies mention special, additional or educational needs in their title, or in a nearby abstract phrase. Many describe the population as a specific condition instead, such as cochlear implants, Down syndrome, cerebral palsy, visual impairment or learning disabilities.

In the source databases, such records could still be caught by subject headings. This analysis cannot confirm which records were actually retrieved that way. The headings are substantial:
- PsycINFO's `DE "Special Needs Students"` alone retrieves 51,020 records, against 94,319 for the text line.
- ERIC and the other EBSCO databases add similar headings.

OpenAlex has nothing equivalent, so dropping these headings is the most likely decisive loss, rather than a fault in the translation.

**Missing abstracts compound the problem.** 21 of the 79 studies in OpenAlex have no abstract there, and 11 of the 18 covered studies that even arm C misses are among them. Dissertations are the worst affected.

| Studies | Total | In OpenAlex | Recovered by A | Recovered by C | No abstract (of those in OpenAlex) |
|---|---:|---:|---:|---:|---:|
| Journal articles and chapters | 52 | 51 | 27 | 44 | 9 |
| Dissertations and reports | 42 | 28 | 7 | 17 | 12 |

Even restricted to journal articles, arm C reaches only 44/52 (85%).

One study (Rangvid 2021, *Education Economics*) falls outside the date window. It was published after the database searches and was found by other means.

## OQL POST execution checks

- Re-posting the echoed OQO gave identical counts for all three arms.
- Cursor continuation by POST works:
  - The exports for A (190 pages, 18,946 IDs) and B (35 pages, 3,463 IDs) are complete and duplicate-free, with a constant count throughout.
  - In both exports, the intersection with the benchmark equals the restricted-membership result.
- The offline verifier passes all its checks. Among them, it confirms the B ⊆ A ⊆ C nesting in both the exports and the recovered sets.

## Limitations

- **One review, chosen purposively.** It is heavy on dissertations (45% of included studies). That is typical of education reviews but unfavourable to any single bibliographic source, OpenAlex included.
- **Subject headings were dropped by design.** A redesigned OpenAlex strategy could add text synonyms for specific conditions, or OpenAlex topics, but it would need an independent test on another review; tuning it here would not count.
- **Arm C rests on restricted membership.** No complete export was made, because 151,147 records exceeds the frozen 40,000 cap.
- **No precision estimate.** No new records were screened, so precision and screening time are not estimated.
- **Search dates differ between sources.** The appendix dates the database searches 7–8 April 2021; the article text says 24 April. Only one study is affected by the date window, and it was published later anyway.

## What this adds

| Benchmark | Sources searched | Screened | Best frozen OpenAlex recall | Its count |
|---|---|---:|---|---:|
| [Insomnia](../transfer_benchmark_2026-11-12/README.md) | Multiple (clinical) | 1,974 | 27/29 (93.1%) | 718 |
| [Depression biomarkers](../large_transfer_benchmark_2026-11-12/README.md) | Multiple (clinical) | 67,464 | 66/75 (88.0%) | 357,009 |
| [Transgenerational inheritance](../walker_transgenerational_benchmark_2026-11-12/README.md) | PubMed only | 63,754 | 249/257 (96.9%) | 306,031 |
| **Inclusion and special educational needs (this test)** | **9 databases plus grey literature** | **20,183** | **61/94 (64.9%)** | **151,147** |

These two `opus5.5` tests mark the boundary.
- **Single-database search (Walker 2018):** OpenAlex reproduced PubMed's recall exactly, because the source strategy was pure text.
- **Multi-source search (this review):** OpenAlex alone falls well short, for two separable reasons:
  - **Coverage.** 16% of the included studies are not in OpenAlex, mostly US dissertations.
  - **Metadata.** It has no thesaurus to stand in for subject headings, and many abstracts are missing.

Neither problem is fixed by a better OQL query alone.

## Files and verification

- **Protocol and queries:** [Protocol](PROTOCOL.md), [freeze manifest](freeze_manifest.json), [source provenance](source_provenance.json), [nine source strategies](source_search_strategies.json), [query builder](build_queries.py), [pre-freeze validation](validation/).
- **Benchmark and per-study results:** [Benchmark](results/benchmark_source.json), [matches](results/benchmark_matches.json), [summary](results/summary.json), [per-study matrix](results/per_study_retrieval.csv), [exports for A and B](results/).
- **Raw API evidence:** [`archives/`](archives/). Request bodies, statuses, responses and UTC timestamps are kept; headers, the key and Crossref abstracts are not.
- **Live runners:** `match_benchmark.py`, `match_second_pass.py`, `run_test.py`, `check_cursor.py`, `diagnose_facets.py`. `summarise.py` is offline.

From the repository root:

```bash
python3 inclusion_sen_benchmark_2026-11-13/verify.py
```

This runs offline with the standard library only.
