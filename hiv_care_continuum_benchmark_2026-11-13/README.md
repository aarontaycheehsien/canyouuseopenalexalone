# HIV care continuum in children and adolescents: OQL POST test against a three-database review

**Neither frozen OpenAlex search met the recall target of 181 of the 190 included articles.**

| Arm | What it searches | Articles recovered | Records returned |
|---|---|---:|---:|
| A | The Embase free-text strategy on title and abstract | 134/190 (70.5%) | 7,750 |
| B | The same strategy on title, abstract and OpenAlex keywords | 135/190 (71.1%) | 7,897 |

The authors screened 10,281 records.

**Coverage is complete.** All 190 articles are in OpenAlex.

**The age block causes most misses.** It loses 49 of the 190 articles, and is the only failing block for 47 of arm A's 56 misses. These are studies of infants, of all-age or adult cohorts that report children or adolescents as a subgroup, and abstracts that say "children" rather than "child".

The review could rely on subject headings to catch these; a free-text search cannot. 33 of the 49 carry a PubMed age heading that the review's PubMed strategy searched.

Test date: **13 November 2026**. The protocol and queries were committed and pushed ([`ce2c1bf`](https://github.com/aarontaycheehsien/canyouuseopenalexalone/commit/ce2c1bf)) before any search was executed and before the included-studies table or reference list was opened.

## Benchmark

[Haw, Banegas, Lujintanon et al. (2025), *Characterizing the HIV care continuum among children and adolescents with HIV in eastern and southern Africa in the era of "Universal Test and Treat": a systematic review and meta-analysis*](https://doi.org/10.1002/jia2.26526), J Int AIDS Soc 28(6):e26526. Open access.

| Reported by the authors | |
|---|---|
| Databases | PubMed, Embase and African Index Medicus, 1 January 2010 to 1 June 2023, plus hand-searched bibliographies and studies drawn from other systematic reviews |
| Screened (unique records) | **10,281** |
| Full texts | 1,510 |
| Included | **190 articles** |
| Published strategy | Supplementary Table 1: Embase and PubMed strings for nine concepts |

**The benchmark list.** Supplementary Table 3 lists the 190 articles by author and year. These were paired with the article's references: entries 26–214, cited together in the results, plus entry 10 (Gelaw 2021, first cited in the introduction). Typos in the table, such as "Iyun 2929" and "Tapera 209", were resolved by surname to the only unpaired reference.

**Matching:**

- 189 articles matched by DOI or title, each agreeing with its full citation.
- One was accepted manually: Zijenah 2022, where the agreement score is lowered only by spacing around "+" in the title.
- **One reference-list error was corrected.** Table S3 lists "Dunlop 2022" (South Africa, urban, 2004–2018). Its paired reference, number 98, is a 1980 paper on chlamydia serotypes. The table attributes identify the intended article: [Dunlop et al. 2022, S Afr Med J](https://doi.org/10.7196/samj.2022.v112i5.16277), on the Johannesburg paediatric HIV programme 2004–2018. Scored literally, reference 98 would lower each arm by one.

## Results

Both arms translate the **Embase** free-text lines of Table S1. The PubMed column cannot be run as printed: it uses single quotes and `n1`/`n2`, neither of which is PubMed syntax. Emtree and MeSH lines are omitted because OpenAlex has no equivalent.

The translation rules:

- unquoted words stay bare, so they are stemmed;
- quoted or truncated terms become exact strings;
- `NEAR/n` becomes `within n words of each other`. OQL proximity accepts neither OR groups nor a mix of bare and quoted operands, so OR groups are expanded into every pair.

Both arms were sent as `POST https://api.openalex.org/` with `{"oql": ...}`, limited to 2010-01-01 to 2023-06-01.

| Arm | API count | Recovered / 190 | ≥ 181? | ≤ 10,281? | Evidence |
|---|---:|---:|---|---|---|
| [A — title-abstract](queries/A_title_abstract.oql) | 7,750 | 134 (70.5%) | No | Yes (0.75×) | Complete export, 78 pages |
| [B — title-abstract-keywords](queries/B_title_abstract_keywords.oql) | 7,897 | 135 (71.1%) | No | Yes (0.77×) | Complete export, 79 pages |

**B is a superset of A.** OpenAlex keywords add 147 records and one article (Berihun 2023).

## Why articles are missed (post-hoc)

Each block was run alone, restricted to the 190 matched articles ([facet diagnostics](results/facet_diagnostics.json), [probes](results/posthoc_probes.json), [per-study matrix](results/per_study_retrieval.csv)).

| Facet (title-abstract) | Articles passing |
|---|---:|
| Date window | 190 |
| Has an abstract in OpenAlex | 180 |
| HIV | 185 |
| **Children and adolescents** | **141** |
| Any care-continuum outcome | 187 |
| Eastern and southern African countries | 189 |

Arm A's 56 misses by failing block:

| Failing block | Articles |
|---|---:|
| Age block only | 47 |
| HIV block only | 4 |
| Outcome block only | 2 |
| Countries block only | 1 |
| Two blocks | 2 |

Missing abstracts are not the problem here: all 10 articles without an abstract were retrieved.

### The age block

The Embase free-text block is: `child`, `pediatric*`, `paediatric*`, `adolesc*`, `teen*`, and `young*` AND `adult*`. Of the 49 articles that fail it:

- **21 say "children".** OQL stems bare `child`, but its stemmer does not reduce the irregular plural "children" to it. I could not confirm from Elsevier's documentation whether Embase matches the plural, so this may be partly a translation artefact. Matching "children" would lift arm A to 154/190 (81%).
- **18 use infant, neonate, newborn, youth or "young people"**, terms that the strategy never had. Adding them as well reaches 169/190 (89%), still short of 181.
- **13 contain none of these.** By Table S3's age column, 11 of them are cohorts of people aged 15 and older or of all ages.

**Subject headings explain how the review found them.** 33 of the 49 carry PubMed's Child, Adolescent or Young Adult heading, which the review's PubMed strategy searched. Six more carry only Infant headings.

Dropping the age block entirely (a post-hoc count, not a tested arm) reaches 181/190, exactly the threshold, at 30,963 records. That is three times the authors' screening load.

### The HIV block

Five articles fail it.

- **Two write "human immunodeficiency virus".** The Embase chain `'human immun*' NEAR/1 'deficien*' NEAR/1 'virus'` expects "immune deficiency" as two words. In Embase, Emtree would catch these.
- **Three never mention HIV** in title or abstract; they speak only of antiretroviral therapy.

## OQL POST execution checks

For both arms:

- re-posting the echoed OQO gave identical counts;
- cursor page 2 was consistent with page 1 and disjoint from it;
- the complete exports have no duplicates and a constant count, and the benchmark IDs in each equal the restricted-membership result.

A's export is a subset of B's. The offline verifier passes all its checks.

## Limitations

- **Subject indexing.** Emtree and MeSH are not reproduced, and this review's age concept depends on them.
- **One plural is unresolved.** Whether Embase matches "children" for `child` is unconfirmed. If it does, the frozen translation understates a faithful one by up to 20 articles.
- **Other sources.** African Index Medicus, the hand-search and studies drawn from other reviews are not reproduced.
- **Chained proximity.** Expanding chained proximity into pairs is slightly looser than Embase's chained `NEAR`.
- **Precision.** No new screening was done, so precision is not estimated.

## Where this fits

| Benchmark | Sources searched | Unique records screened | In OpenAlex | Best frozen OpenAlex recall | Its count |
|---|---|---:|---:|---:|---:|
| [Transgenerational inheritance](../walker_transgenerational_benchmark_2026-11-12/README.md) | PubMed only | 63,754 | 100% | 96.9% | 306,031 |
| [Inclusion and special educational needs](../inclusion_sen_benchmark_2026-11-13/README.md) | 9 databases plus grey literature | 20,183 | 84% | 64.9% | 151,147 |
| [Bt maize and non-target animals](../bt_maize_multisource_benchmark_2026-11-12/README.md) | 12 databases plus specialist sites | 12,967 | 83% | 72.9% | 6,775 |
| [Cost of mental disorders](../cost_mental_disorders_benchmark_2026-11-13/README.md) | 6 databases plus bibliography search | 13,579 | 99% | 81.1% | 40,605 |
| [Motor competence and executive functions](../motor_competence_benchmark_2026-11-13/README.md) | 6 databases plus reference lists | 12,117 | 100% | 97.7% | 12,012 |
| [Precarious employment and health](../precarious_employment_benchmark_2026-11-13/README.md) | 9 databases plus grey literature | 12,940 | 96% | 88.0% | 42,085 |
| **HIV care continuum in children (this test)** | **3 databases plus hand-search** | **10,281** | **100%** | **71.1%** | **7,897** |

**Why this review falls short despite full coverage.** Every article is in OpenAlex, and the search is precise. The shortfall is a population concept, children within mixed-age cohorts, that the authors' databases resolved through age indexing rather than text.

## Files and verification

- **Protocol and source:** [protocol](PROTOCOL.md), [freeze manifest](freeze_manifest.json), [provenance](source_provenance.json), [Table S1](source_search_strategy.json), [builder](build_queries.py), [validation](validation/).
- **Benchmark:** [benchmark](results/benchmark_source.json), [matches](results/benchmark_matches.json).
- **Results:** [summary](results/summary.json), [matrix](results/per_study_retrieval.csv), exports in [`results/`](results/).
- **Raw evidence:** [`archives/`](archives/). Headers, the API key and abstracts are not archived.
- **Live runners:** `match_benchmark.py`, `match_correction.py`, `run_test.py`, `diagnose_facets.py`, `posthoc_probes.py`.
- **Offline scripts:** `adjudicate.py`, `summarise.py`.

```bash
python3 hiv_care_continuum_benchmark_2026-11-13/verify.py
```
