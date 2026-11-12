# Motor competence and executive functions: OQL POST test against a six-database review

**Both frozen OpenAlex searches recovered 43 of the 44 included studies (97.7%), which meets the prespecified recall threshold of 42.** Both also returned fewer records than the authors screened:

- **Arm A (no limits):** 12,012 records, against the authors' 12,117 screened.
- **Arm B (the authors' English-language and journal-article limits):** 7,807 records.

This is the only multi-source benchmark on this branch where OpenAlex alone meets both the recall and the workload criteria. Complete cursor exports confirm both arms.

The one miss is Meijer et al. (2022). Its title speaks of "neurocognitive functioning", and it fails only the executive-function block. "Neurocognitive" is a single token, so the phrase "cognitive function" does not match it, and the record's title, abstract and keywords contain none of the block's other terms.

Test date: **13 November 2026**. The protocol and queries were committed and pushed ([`c6bff3d`](https://github.com/aarontaycheehsien/canyouuseopenalexalone/commit/c6bff3d)) before any search ran and before the list of included studies was opened.

## Benchmark

[Bao, Wade, Leahy et al. (2024), *Associations between motor competence and executive functions in children and adolescents: a systematic review and meta-analysis*](https://doi.org/10.1007/s40279-024-02040-1), Sports Medicine 54:2141–2156. Open access.

| Reported by the authors | |
|---|---|
| Databases | 6: PubMed, PsycINFO, Scopus, Ovid MEDLINE, SPORTDiscus, Embase, searched from inception to 27 June 2023, plus reference lists of included studies |
| Records | 20,498 identified, 8,381 duplicates removed, **12,117 screened** |
| Included | **44 studies** (37 meta-analysed) |
| Published strategy | Table S1: three OR-lists of keywords; the per-database versions (with MeSH "where possible") were not published |

**Matching.** All 44 studies are in OpenAlex. Forty-three were matched by DOI from the article's reference list, and one by an OpenAlex title search. Every match agrees with its full citation (similarity ≥ 0.9).

**Pairing studies to references.** The study list (Table S2) gives author and year, and these were paired with the reference list. For each of the two *a*/*b* pairs (Mazzoccante 2020, Rigoli 2012), the suffix was assigned by reference-list order. Both members of each pair are included, so this does not affect recall.

## Results

Both arms translate Table S1 onto `title-abstract-keywords`. Single words are stemmed, multiword terms become stemmed phrases, and wildcards are exact. Both were sent as `POST https://api.openalex.org/` with `{"oql": ...}`, limited to publications dated on or before 2023-06-27.

| Arm | API count | Recovered / 44 | ≥ 42? | ≤ 12,117? | Evidence |
|---|---:|---:|---|---|---|
| [A — no limits](queries/A_no_limits.oql) | 12,012 | 43 (97.7%) | **Yes** | **Yes** (0.99×) | Complete export, 121 pages |
| [B — English, articles](queries/B_english_articles.oql) | 7,807 | 43 (97.7%) | **Yes** | **Yes** (0.64×) | Complete export, 79 pages |

**What the authors' limits change.** The English-language and journal-article limits remove 4,205 records and lose nothing. All 44 included studies are English-language articles in OpenAlex.

**How it compares with the screening load.** Arm A's count is almost identical to the authors' screening load. That similarity is coincidence, not a sign that the two record sets overlap; their overlap was not measured.

**Facet diagnostics (post-hoc, [file](results/facet_diagnostics.json)).** These checked which part of the search each included study passes.
- All 44 studies pass the date limit, the motor-competence block, the population block, and the English-language and article filters.
- 43 of 44 pass the executive-function block.
- 5 of 44 have no abstract in OpenAlex. All five were still retrieved, from their titles and keywords.

## OQL POST execution checks

For both arms:
- Re-posting the echoed OQO gave identical counts.
- Cursor page 2 was consistent with page 1 and disjoint from it.
- The complete cursor exports have no duplicates and a constant count throughout.
- The benchmark IDs found in each export equal the restricted-membership result.

Across arms, B's export is a subset of A's. The offline verifier passes all its checks.

## Limitations

- **Unpublished database strategies.** Only Table S1's keywords could be translated, not the per-database strategies. Choices about field (title, abstract and keywords) and phrase handling are documented in the [protocol](PROTOCOL.md).
- **One review with 44 studies.** At this size, one study is 2.3 percentage points of recall. The pass at 43/44 rests on a margin of one study.
- **No precision estimate.** No new screening was done, so a count near the authors' screening load says nothing about how many relevant records it contains.

## Where this fits

| Benchmark | Sources searched | Unique records screened | In OpenAlex | Best frozen OpenAlex recall | Its count |
|---|---|---:|---:|---:|---:|
| [Transgenerational inheritance](../walker_transgenerational_benchmark_2026-11-12/README.md) | PubMed only | 63,754 | 100% | 96.9% | 306,031 |
| [Inclusion and special educational needs](../inclusion_sen_benchmark_2026-11-13/README.md) | 9 databases plus grey literature | 20,183 | 84% | 64.9% | 151,147 |
| [Bt maize and non-target animals](../bt_maize_multisource_benchmark_2026-11-12/README.md) | 12 databases plus specialist sites | 12,967 | 83% | 72.9% | 6,775 |
| [Cost of mental disorders](../cost_mental_disorders_benchmark_2026-11-13/README.md) | 6 databases plus bibliography search | 13,579 | 99% | 81.1% | 40,605 |
| **Motor competence and executive functions (this test)** | **6 databases plus reference lists** | **12,117** | **100%** | **97.7%** | **12,012** |

**What drives the difference.** OpenAlex alone succeeds when two conditions hold:
1. The included literature is recent, English-language, journal-published and fully covered.
2. The topic's vocabulary is consistent enough for a keyword strategy.

This review meets both. The education, ecology and health-economics reviews do not: they include grey literature and non-English work, or use inconsistent vocabulary.

## Files and verification

- **Protocol and source:** [Protocol](PROTOCOL.md), [freeze manifest](freeze_manifest.json), [provenance](source_provenance.json), [Table S1](source_search_strategy.json), [builder](build_queries.py), [validation](validation/).
- **Benchmark:** [Benchmark](results/benchmark_source.json), [matches](results/benchmark_matches.json).
- **Results:** [summary](results/summary.json), [per-study matrix](results/per_study_retrieval.csv), exports in [`results/`](results/).
- **Raw evidence:** [`archives/`](archives/). Request headers and the API key are not archived.
- **Runners:** `match_benchmark.py`, `run_test.py`, `diagnose_facets.py`. `adjudicate.py` and `summarise.py` run offline.

```bash
python3 motor_competence_benchmark_2026-11-13/verify.py
```
