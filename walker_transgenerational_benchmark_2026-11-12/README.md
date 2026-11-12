# Transgenerational inheritance: an OQL POST test against a 63,754-record review

**Both frozen OpenAlex searches recovered 249 of 257 included references (96.9%), meeting the prespecified recall threshold of 245. Neither met the workload comparison: they returned 306,031 and 309,758 records, about 4.8 times the 63,754 the authors screened.**

The published PubMed strategy, re-run today against the same benchmark, also retrieves exactly 249 of 257. It misses the same eight references. The OpenAlex translation therefore matched PubMed's recall reference for reference. The cost is volume: the extra results come mainly from non-biomedical literature that PubMed never indexed.

Test date: **12 November 2026**. The [protocol and queries were committed and pushed](https://github.com/aarontaycheehsien/canyouuseopenalexalone/commit/06917fc) before any search ran and before the included list was parsed.

## Benchmark

[Walker et al. (2018), *Human and animal evidence of potential transgenerational inheritance of health effects: An evidence map and state-of-the-science evaluation*](https://doi.org/10.1016/j.envint.2017.12.032), Environment International 115:48–69. An [author version](https://ntp.niehs.nih.gov/ntp/ohat/transgenerational/ohat_review_article_508.pdf) is on the NTP site.

| Reported by the authors | |
|---|---|
| Databases | PubMed only, searched up to November 2016 |
| Records title/abstract screened after deduplication | **63,754** |
| Included references | **257** (46 human, 211 animal) |
| Search strategy | Supplemental Table S1: text words only, no MeSH heading exists for the topic |

This is a good translation target because a single, text-word-only PubMed strategy leaves little room for translation choices. It also moves the repository's tests out of depression and clinical trials into environmental health and toxicology, covering animal and human evidence.

**Reconciling the benchmark.** The supplement's included list has 303 entries, because its animal section repeats all 46 human references. Removing those repeats leaves 46 + 211 = 257, which matches the stated totals exactly. Four pairs within the 257 are the same publication in OpenAlex (three *a*/*b* ahead-of-print and print pairs, plus a 2015/2016 pair). Results are reported both per reference (257) and per distinct work (253).

**Matching: 257/257 references matched OpenAlex.**
- Routes: 228 by NCBI citation matching to a PMID, 20 by PubMed title search, and 9 by Crossref DOI.
- Ten matches needed manual adjudication. Nine were caused by the parser cutting a title at its first full stop or question mark. One was an online-versus-print year difference.
- The notes are in [`benchmark_matches.json`](results/benchmark_matches.json).
- Two OpenAlex records carry wrong publication dates (2009 for papers from 1977 and 1981). Neither affected the date limit.

## The frozen searches

Both arms were sent as `POST https://api.openalex.org/` with `{"oql": ...}`, using publication date ≤ 2016-11-30 and the default core corpus, with no other restrictions.

| Arm | Construction | API count | References recovered | Distinct works | ≥ 245? | ≤ 63,754? |
|---|---|---:|---:|---:|---|---|
| [A — faithful, title-abstract](queries/A_faithful_title_abstract.oql) | Every PubMed `[tiab]` term as an exact OQL string, truncation kept, Boolean structure unchanged | 306,031 | **249/257 (96.9%)** | 245/253 | Yes | No (4.80×) |
| [B — same string, title-abstract-keywords](queries/B_title_abstract_keywords.oql) | Identical Boolean, OpenAlex keywords added | 309,758 | **249/257 (96.9%)** | 245/253 | Yes | No (4.86×) |

**The two arms differ only in the keyword field.** Adding keywords brought in 3,727 more records and recovered no additional benchmark reference. Membership was identical.

## Why the misses are not an OpenAlex failure

The eight missed references are all animal studies: three ENU mutagenesis papers, two radiation papers, and one paper each on TCDD fertility, induced diabetes and *Drosophila* eye reduction.

- **Clause diagnostics.** Run after the primary results were saved, these show that every missed record passes the date limit and the generation/offspring/progeny words, but fails every distinctive block (#1–#5) in both fields. Three of them have no abstract in OpenAlex. ([Clause diagnostics](results/clause_diagnostics.json))
- **The published strategy doesn't find them either.** Re-running S1 in PubMed today, restricted to the benchmark PMIDs, retrieves exactly 249 of 257, and its eight misses are the same eight. The PubMed records of the missed papers contain none of the strategy's distinctive terms in their title, abstract, MeSH, substance or keyword fields. ([PubMed check](results/missed_pubmed_check.json))
- **They were screened by another route.** Seven of the eight appear among the PMIDs in SYNERGY's copy of the screening set. The review team therefore screened them, but by a route the reported strategy does not describe. The authors mention only 3–4 references from other sources, so this gap is not fully explained by the paper.

This is a post-hoc reference ceiling, not part of the frozen outcomes. PubMed's records and indexing have changed since 2016, so it is today's PubMed rather than the authors' original result set. It still shows that on this benchmark, the OQL translation lost nothing that the stated strategy could retrieve.

One missed paper (Aigner et al., 2009) does match the F-generation terms in OpenAlex full text. PubMed's All Fields search does not cover full text, so this is a diagnostic observation, not a fair comparison.

## Where the extra volume comes from

These counts are a post-hoc, descriptive breakdown of arm A ([volume decomposition](results/volume_decomposition.json)).

- **PubMed-indexed records:** 76,061 of the 306,031 carry a PMID, the same order of magnitude as the 63,789 PubMed returned in 2016. The other roughly 230,000 records are not PubMed-indexed.
- **By domain:**
  - Social sciences: 117,479
  - Physical sciences: 69,169
  - Health sciences: 63,435
  - Life sciences: 54,641

  Records were not read individually. Plausible sources of the non-biomedical volume are generic phrases such as "second generation" (immigrants, technologies), "intergenerational" and the grandparent terms in social science, and "F2 progeny" in plant and animal breeding.

The strategy was designed for a biomedical database. Run across all disciplines, it retrieves large non-biomedical literatures, and that, rather than poorer matching, is where most of the excess sits. A screening team could cut this with domain or PubMed-indexing filters, but that would be a new strategy needing its own independent test. It is not a repair of this one.

**Fidelity to the original retrieval** ([SYNERGY overlap](results/secondary_synergy_overlap.json)). SYNERGY holds 48,375 OpenAlex IDs from an earlier export of this review's PubMed screening (Howard et al., 2016). Of these, 47,686 still resolve today, and arm A retrieves **42,236 of them (88.6%)**. The remaining 11.4% are records the original PubMed retrieval contained but the OpenAlex translation does not; their causes were not investigated. The narrower field for the F-terms is one candidate. Apart from seven of the eight missed references, none of these records is an included reference. The screening labels were not used.

## OQL POST execution checks

- Re-posting the echoed OQO returned identical counts for both arms.
- Cursor continuation by POST works with an API key. Page 2 kept the same count and contained no IDs from page 1, for both arms.
- All 85 offline checks pass. Among them, the verifier confirms that each benchmark-membership request is the identical executed OQO with only an ID restriction added, and that each diagnostic and overlap query adds only its own restriction.

## Limitations

- **No complete unrestricted export.** Both counts exceeded the frozen 40,000-record export cap; exporting 306,000 records would cost about $1.50–$3 of search credits (collection import or cursor paging) against a $1 daily free budget. Recovery therefore rests on benchmark-restricted membership of the identical executed query, plus the archived first two cursor pages. This is the same evidence standard as the depression-biomarker test, and it is weaker than the insomnia test's full export.
- **Translation departures.**
  - The F-generation terms searched PubMed All Fields but only title and abstract in OpenAlex.
  - A publication-date ceiling is not the same as a PubMed entry-date snapshot.
  - Only the core corpus was searched.
- **No precision estimate.** No new records were screened, so precision and screening time are not measured. A lower count would only have shown potential screening volume.
- **One review.** This is a purposive, single-review test. It cannot estimate average performance across reviews.
- **Incidental exposure before the freeze.** One included title was seen while checking the HAWC data structure (Aigner et al., 2007). That paper is one of the eight misses, and the frozen queries contain no term derived from it.

## What this adds

| Benchmark | Original screening | Best frozen OpenAlex recall | OpenAlex count |
|---|---:|---|---:|
| [Insomnia](../transfer_benchmark_2026-11-12/README.md) | 1,974 | 27/29 (93.1%) | 718 |
| [Depression biomarkers](../large_transfer_benchmark_2026-11-12/README.md) | 67,464 reported | 66/75 (88.0%) | 357,009 |
| **Transgenerational inheritance (this test)** | **63,754** | **249/257 (96.9%)** | **306,031** |

This is the first frozen test in the repository to clear the >95% recall threshold. It is also the first where the source search was a single, faithfully translatable text-word strategy. Taken together, the results suggest that OpenAlex's coverage and OQL's exact, truncated and Boolean search can reproduce a well-specified PubMed strategy's recall. Searching every discipline, however, multiplies the screening volume unless the strategy is redesigned for a multidisciplinary index.

## Files and verification

- **Protocol and queries:** [Protocol](PROTOCOL.md), [freeze manifest](freeze_manifest.json), [source provenance](source_provenance.json), [S1 source table](source_search_strategy_S1.json), [query builder](build_queries.py), [pre-freeze validation](validation/).
- **Benchmark and per-reference results:** [Benchmark source](results/benchmark_source.json), [matches](results/benchmark_matches.json), [per-reference matrix](results/per_reference_retrieval.csv), [summary](results/summary.json).
- **Raw API evidence:** [`archives/`](archives/). Request bodies, statuses, responses and UTC timestamps are kept. Headers and the API key are not. Crossref abstracts were redacted.
- **Live runners:** `match_benchmark.py`, `run_test.py`, `check_cursor.py`, `secondary_overlap.py`, `diagnose_misses.py`, `decompose_volume.py`. `summarise.py` is offline.

From the repository root:

```bash
python3 walker_transgenerational_benchmark_2026-11-12/verify.py
```

This runs offline with the standard library only. A new live replication should use a fresh output directory.

The secondary analysis created a private collection, `col_C484yaPTuH`, in the key owner's OpenAlex account. It can be deleted without affecting any result here.
