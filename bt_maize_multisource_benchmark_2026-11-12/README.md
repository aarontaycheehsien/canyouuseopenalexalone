# Bt maize and non-target animals: OQL POST test against a 12-database review

**Both frozen OpenAlex searches recovered 121 of 166 included references (72.9%), well short of the prespecified target of 158.** They returned 6,775 records (core corpus) and 7,053 (all corpora). That is about half the 12,967 records the authors screened.

**Recall was capped before any search ran.** Only 138 of the 166 references (83.1%) exist in OpenAlex. Among those 138, the searches recovered 121 (87.7%). The losses were:

- **Abstracts:** 38 of the 138 have no abstract in OpenAlex, and 9 of the 17 covered misses are among them.
- **Wording:** the field-sampling block (`field OR plot OR … monitoring`) is the block most often absent from the text OpenAlex holds.

Adding the expansion corpus brought in 278 more records and no extra reference.

Test date: **13 November 2026**. The protocol and queries were committed and pushed on 12 November ([`1c95f20`](https://github.com/aarontaycheehsien/canyouuseopenalexalone/commit/1c95f20)), before the included list was opened. Matching started that evening, and the searches were run when the work resumed on 13 November. Nothing in the frozen files changed in between; the verifier checks their hashes.

## Benchmark

[Meissle, Naranjo & Romeis (2022), *Does the growing of Bt maize change abundance or ecological function of non-target animals compared to the growing of non-GM maize? A systematic review*](https://doi.org/10.1186/s13750-022-00272-0), Environmental Evidence 11:21. Open access.

| Reported by the authors | |
|---|---|
| Bibliographic sources | 12: Web of Science Core Collection, BIOSIS, Zoological Record, SciELO, CAB Abstracts, Agricola, AGRIS, Scopus, BASE, ProQuest Dissertations & Theses, JSTOR, Google Scholar |
| Other sources | Specialist regulatory, project, industry and civil-society websites; references from reviews and colleagues |
| Records screened | **12,967** database references after deduplication, plus 110 from specialist websites and 19 from other sources |
| Included references | **166**: 71 found only by database search, 49 by database and other routes, 46 only by other routes |
| Searches | December 2014 (all years), updated January and August 2019 (last 23 August 2019) |

Searching a dozen sources is typical of environmental-evidence reviews.

**Reconciling the benchmark.** Additional file 2 parses to 167 labelled entries. One is the file's legend text ("References excluded at the full text stage are labelled with EX…"). Removing it gives 71 / 49 / 46 = 166, exactly as the article reports ([matches](results/benchmark_matches.json)).

## Matching: 138 of 166 references are in OpenAlex

**How the matching was done:**

1. Crossref, PubMed and OpenAlex title search for every reference.
2. A broader second OpenAlex pass for anything not matched automatically.
3. An audit of every accepted match against the full citation text.

**Audit corrections.** The audit caught two wrong automatic matches:

- A "Part 2" paper matched to its "Part 3" companion.
- A 2011 maize study matched to a 2023 soybean study through a truncated title.

Both were rejected, and further searches did not find the right records.

**Manual adjudications (six), each with a recorded reason:**

- Two German dissertations. The review appends an English translation to their titles.
- A Spanish article that the review cites under an English title.
- Three online-versus-issue year differences.

**The 28 references not in OpenAlex** are mostly grey or regional literature:

- IOBC/WPRS bulletin papers.
- German project reports and theses.
- Syngenta study reports.
- GMO-safety web pages.
- A Cornell PhD thesis.
- Chinese plant-protection journals.
- Philippine and Turkish papers.
- A French trade magazine article.

| Found by (review's labels) | References | In OpenAlex | Recovered (either arm) |
|---|---:|---:|---:|
| Database search only | 71 | 57 | 50 |
| Database search and other routes | 49 | 43 | 39 |
| Other routes only | 46 | 38 | 32 |
| **All** | **166** | **138** | **121** |

Of the 120 references the review's own database searches found, 100 are in OpenAlex and 89 are recovered.

## The frozen searches

Both arms translate the review's Web of Science and Scopus string, which is identical on both platforms, onto `title-abstract-keywords`. Each is submitted as `POST https://api.openalex.org/` with `{"oql": ...}` and a publication date of 23 August 2019 or earlier ([protocol](PROTOCOL.md)).

| Arm | API count | Recovered / 166 | Recovered / 138 in OpenAlex | ≥ 158? | ≤ 12,967? | Evidence |
|---|---:|---:|---:|---|---|---|
| [A — core corpus](queries/A_core_title_abstract_keywords.oql) | 6,775 | 121 (72.9%) | 121 (87.7%) | No | Yes (0.52×) | Complete export |
| [B — all corpora](queries/B_all_corpora_title_abstract_keywords.oql) | 7,053 | 121 (72.9%) | 121 (87.7%) | No | Yes (0.54×) | Complete export |

**Recall by type and language.** Among the 138 references OpenAlex holds:

- Journal articles: 112/128.
- Dissertations: 7/8.
- English-language records: 118/131.
- Non-English records: 3/8.

## Why covered references are missed (post-hoc)

Each block was run alone, restricted to the 138 matched references ([facet diagnostics](results/facet_diagnostics.json), [per-reference matrix](results/per_reference_retrieval.csv)).

| Facet | Matching / 138 |
|---|---:|
| Date ≤ 2019-08-23 | 138 |
| Has an abstract in OpenAlex | **100** |
| Maize block (maize, corn, Zea mays) | 133 |
| Field-sampling block (field, plot, location, trial, farm scale, scouting, trap, trapping, sampling, monitoring) | **124** |
| GM block (transgenic, Bt, Bacillus thuringiensis, GM, genetically modified/engineered, Cry\*, Vip\*) | 134 |

**Results by block.**

- Results are identical whether keywords are included or not. Over these 138 records, OpenAlex keywords contributed nothing.
- Of the 17 covered misses, 14 fail the field-sampling block; some fail other blocks too.

**The role of abstracts.**

- References with an abstract are recovered 92/100 times.
- References without one are recovered 29/38 times, from the title alone.

Where OpenAlex holds only the title, a reference can be retrieved only if all three blocks appear in it. Whether the source databases held fuller abstracts or indexer keywords for these papers was not checked.

## OQL POST execution checks

For both arms:

- Re-posting the echoed OQO returned an identical count.
- Cursor page 2 was consistent with page 1 and disjoint from it.
- The complete cursor exports are duplicate-free, with a constant count throughout: 68 pages for A and 71 for B.
- Each export's intersection with the benchmark equals the restricted-membership result.
- The core export is a subset of the all-corpora export.

The offline verifier passes 204 of 204 checks.

## Limitations

- **One review.** It is a single, purposive benchmark.
- **The source used more than its text string.** The review's Ovid subject headings, full-text engines (BASE, JSTOR, Google Scholar) and specialist websites are not reproduced. This is by design, since the question is whether OpenAlex alone can stand in for them.
- **No precision estimate.** No new records were screened, so precision and screening time are not estimated.
- **The date ceiling is approximate.** It approximates three search dates, but no benchmark reference fails it.

## What this adds

| Benchmark | Sources searched | Screened | In OpenAlex | Best frozen OpenAlex recall | Its count |
|---|---|---:|---:|---|---:|
| [Transgenerational inheritance](../walker_transgenerational_benchmark_2026-11-12/README.md) | PubMed only | 63,754 | 257/257 | 249/257 (96.9%) | 306,031 |
| [Inclusion and special educational needs](../inclusion_sen_benchmark_2026-11-13/README.md) | 9 databases plus grey | 20,183 | 79/94 | 61/94 (64.9%) | 151,147 |
| **Bt maize and non-target animals (this test)** | **12 databases plus specialist sites** | **12,967** | **138/166** | **121/166 (72.9%)** | **6,775** |

Both multi-source reviews show the same two limits:

- **Coverage.** About one in six included references is not in OpenAlex at all (16% and 17%).
- **Metadata.** Among the covered references, missing abstracts and the absence of thesauri cost a further 12–23% of recall.

The Bt maize search translates more cleanly than the inclusion search because its source string used no subject headings. That is why its covered-reference recall is higher (87.7% against 77.2%) at a far smaller count.

## Files and verification

- **Protocol and source:** [Protocol](PROTOCOL.md), [freeze manifest](freeze_manifest.json), [provenance](source_provenance.json), [source strategy](source_search_strategy.json), [builder](build_queries.py), [validation](validation/).
- **Benchmark:** [Benchmark](results/benchmark_source.json) and [matches](results/benchmark_matches.json). The documented adjudications are in `adjudicate.py`, which runs offline.
- **Results:** [summary](results/summary.json), [matrix](results/per_reference_retrieval.csv) and the exports.
- **Raw evidence:** [`archives/`](archives/). Request bodies, statuses, responses and UTC timestamps are kept. Headers, the API key and Crossref abstracts are not.
- **Live runners:** `match_benchmark.py`, `match_second_pass.py`, `run_test.py`, `diagnose_facets.py`. `summarise.py` runs offline.

From the repository root:

```bash
python3 bt_maize_multisource_benchmark_2026-11-12/verify.py
```

It runs offline using only the standard library.
