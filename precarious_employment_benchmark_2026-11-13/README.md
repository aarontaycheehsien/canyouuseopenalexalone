# Precarious employment and health: OQL POST test against a nine-database review

**Neither frozen OpenAlex search met the recall target of 48 of the 50 included studies.**

| Arm | What it searches | Studies recovered | Records returned |
|---|---|---:|---:|
| A | The published Scopus string: employment terms AND health terms | 38/50 (76.0%) | 8,140 |
| B | The employment terms alone, as the authors ran them in the health databases | 44/50 (88.0%) | 42,085 |

The authors screened 12,940 records.

**Coverage is near-complete.** 48 of the 50 studies are in OpenAlex. The two absent are an American Sociological Association conference paper and a 2009 US dissertation.

**Arm A loses studies to its health block.** That block has no mental-health, substance-use or disease-specific terms. Studies of depressive symptoms, psychological distress, antidepressant use, alcohol misuse, cortisol and lung cancer all fail it.

**Arm B's four misses fail the employment block** in title and abstract. Three of the four have no abstract in OpenAlex.

Test date: **13 November 2026**. The protocol and queries were committed and pushed ([`0675e05`](https://github.com/aarontaycheehsien/canyouuseopenalexalone/commit/0675e05)) before any search was executed and before the included studies were parsed. Before the freeze, the first two rows of the included-studies table printed incidentally (Kivimäki 2003, Emerson 2018). The protocol records this.

## Benchmark

[Pulford, Thapa, Thomson et al. (2022), *Does persistent precarious employment affect health outcomes among working age adults? A systematic review and meta-analysis*](https://doi.org/10.1136/jech-2022-219292), J Epidemiol Community Health 76:909–917. Open access.

| Reported by the authors | |
|---|---|
| Databases | 9, up to March 2019: MEDLINE, Embase, ASSIA, Scopus, IBSS, PsycINFO, EconLit, SocINDEX, Sociological Abstracts. Grey literature from a wider scoping review was also considered. |
| Screened after deduplication | **12,940** |
| Included | **50 studies** (46 datasets; 29 meta-analysed) |
| Published strategy | The Scopus string only. Its health terms "were included in searches of non-health databases". |

**How the review was selected.** It was found by a full-text check of 300 open-access reviews whose abstracts report 10,000 or more records.

**The benchmark list.** The included studies are references 45–94 of the article, exactly 50 entries. Their first authors match the supplement's Table S2.1.

**Matching:**

- 48 studies matched by DOI or title, each agreeing with its full citation.
- Two are not in OpenAlex after a broader second pass: Jin-man 2015 (ASA conference paper) and Cross 2009 (dissertation).

## Results

Both arms translate the Scopus `TITLE-ABS` string onto `title-abstract`:

- unquoted words stay bare, so they are stemmed;
- quoted phrases become stemmed phrases;
- truncated terms, including mid-word ones such as `labo*r`, become exact wildcards.

Both were sent as `POST https://api.openalex.org/` with `{"oql": ...}`, limited to publications on or before 2019-03-31.

| Arm | API count | Recovered / 50 | Recovered / 48 in OpenAlex | ≥ 48? | ≤ 12,940? | Evidence |
|---|---:|---:|---:|---|---|---|
| [A — Scopus string](queries/A_scopus_with_health_terms.oql) | 8,140 | 38 (76.0%) | 38 (79.2%) | No | Yes (0.63×) | Complete export, 82 pages |
| [B — employment terms only](queries/B_precarious_terms_only.oql) | 42,085 | 44 (88.0%) | 44 (91.7%) | No | No (3.25×) | Restricted membership |

**B is a superset of A.** Dropping the health block recovers six more studies at 5.2 times the count.

## Why studies are missed (post-hoc)

Each block was run alone, restricted to the 48 matched studies ([facet diagnostics](results/facet_diagnostics.json), [per-study matrix](results/per_study_retrieval.csv)).

| Facet | Title-abstract | With OpenAlex keywords |
|---|---:|---:|
| Date ≤ 2019-03-31 | 48 | 48 |
| Has an abstract in OpenAlex | 34 | 34 |
| Employment block (38 terms) | 44 | **47** |
| Health block (15 terms) | **42** | 42 |

**The health block** has 15 terms: health, wellbeing, death, hospitali\*ation, prescri\*, injur\*, absen\*, mortality, illness, disease, ill health, sick\*, morbidity, disabilit\*, disabled. It misses titles and abstracts that name a specific outcome, such as "depressive symptoms", "psychological distress", "antidepressant medication", "alcohol misuse", "cortisol" or "lung cancer".

These six studies would fail the same block in Scopus. The review evidently found them through MEDLINE, Embase or PsycINFO, which searched the employment terms alone. Arm B reproduces that approach and recovers all six.

**The employment block** fails four studies in title and abstract. OpenAlex keywords would rescue three of them. The fourth, a Finnish study titled "Life-course experiences and mortality by adult social class among young men", matches none of the terms in any field.

This is a post-hoc observation, not a tested arm: an employment-only search on `title-abstract-keywords` would reach at most 47/50. That is still one short of the target.

**Missing abstracts matter.** 14 of the 48 matched studies have no abstract in OpenAlex.

- Among studies with an abstract, arm B recovers 33/34.
- Among studies without one, it recovers 11/14.

## OQL POST execution checks

For both arms:

- re-posting the echoed OQO gave identical counts;
- cursor page 2 was consistent with page 1 and disjoint from it.

Arm A's complete export (8,140 records, duplicate-free, with a constant count) agrees exactly with its restricted-membership result. A's recovered set is a subset of B's. The offline verifier passes all its checks.

## Limitations

- **One strategy published.** Only the Scopus string is available. The other eight databases' strategies, including any subject headings, are not reproduced.
- **Grey literature.** The grey literature drawn from the wider scoping review is not searched.
- **Arm B's evidence.** Arm B rests on restricted membership. Its count of 42,085 exceeds the 20,000 export cap.
- **Precision.** No new screening was done, so precision is not estimated.

## Where this fits

| Benchmark | Sources searched | Unique records screened | In OpenAlex | Best frozen OpenAlex recall | Its count |
|---|---|---:|---:|---:|---:|
| [Transgenerational inheritance](../walker_transgenerational_benchmark_2026-11-12/README.md) | PubMed only | 63,754 | 100% | 96.9% | 306,031 |
| [Inclusion and special educational needs](../inclusion_sen_benchmark_2026-11-13/README.md) | 9 databases plus grey literature | 20,183 | 84% | 64.9% | 151,147 |
| [Bt maize and non-target animals](../bt_maize_multisource_benchmark_2026-11-12/README.md) | 12 databases plus specialist sites | 12,967 | 83% | 72.9% | 6,775 |
| [Cost of mental disorders](../cost_mental_disorders_benchmark_2026-11-13/README.md) | 6 databases plus bibliography search | 13,579 | 99% | 81.1% | 40,605 |
| [Motor competence and executive functions](../motor_competence_benchmark_2026-11-13/README.md) | 6 databases plus reference lists | 12,117 | 100% | 97.7% | 12,012 |
| **Precarious employment and health (this test)** | **9 databases plus grey literature** | **12,940** | **96%** | **88.0%** | **42,085** |

**The trade-off in this review.** The one string the authors published is tuned for multidisciplinary databases. Run in OpenAlex it is precise (8,140 records) but misses a quarter of the studies.

Their health-database approach, the employment terms alone, recovers 88%, but at 3.3 times their screening load. Neither version on its own reproduces what nine databases achieved together.

## Files and verification

- **Protocol and source:** [protocol](PROTOCOL.md), [freeze manifest](freeze_manifest.json), [provenance](source_provenance.json), [Scopus string](source_search_strategy.json), [builder](build_queries.py), [validation](validation/).
- **Benchmark:** [benchmark](results/benchmark_source.json), [matches](results/benchmark_matches.json).
- **Results:** [summary](results/summary.json), [matrix](results/per_study_retrieval.csv), [arm A export](results/A_scopus_with_health_terms_export_ids.json).
- **Raw evidence:** [`archives/`](archives/). Headers and the API key are not archived.
- **Live runners:** `match_benchmark.py`, `match_second_pass.py`, `run_test.py`, `diagnose_facets.py`.
- **Offline scripts:** `adjudicate.py`, `summarise.py`.

```bash
python3 precarious_employment_benchmark_2026-11-13/verify.py
```
