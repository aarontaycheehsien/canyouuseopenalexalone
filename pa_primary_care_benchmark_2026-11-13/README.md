# Physical activity in primary care: OQL POST test against a fifteen-source review

**Neither frozen OpenAlex search met the recall target of 49 of the 51 included studies.** The target was out of reach before any search ran: only 48 of the 51 studies are in OpenAlex.

| Arm | What it searches | Studies recovered | Records returned |
|---|---|---:|---:|
| A | The MEDLINE free-text strategy on title and abstract | 39/51 (76.5%) | 4,414 |
| B | The same strategy on title, abstract and OpenAlex keywords | 40/51 (78.4%) | 4,543 |

The authors screened 14,566 records.

**Both searches are very precise:** each returns under a third of the authors' screening load.

**The misses are scattered.** Arm A misses 9 of the 48 findable studies, and they fail different blocks: primary care (5), the RCT filter (4) and physical activity (2), with some failing more than one. Four of the ten missed references have no abstract in OpenAlex.

**MEDLINE's indexing explains only three misses.** The subject headings and publication type that the translation had to drop would rescue 3 of the 10 missed references. The rest were presumably found through the other databases and trial registers.

Test date: **13 November 2026**. The protocol and queries were committed and pushed ([`0840572`](https://github.com/aarontaycheehsien/canyouuseopenalexalone/commit/0840572)) before any search was executed and before the included-studies tables were parsed. Before the freeze, the first six rows of Table 1 printed incidentally; the protocol records this.

## Benchmark

[Kettle, Madigan, Coombe et al. (2022), *Effectiveness of physical activity interventions delivered or prompted by health professionals in primary care settings: systematic review and meta-analysis of randomised controlled trials*](https://doi.org/10.1136/bmj-2021-068465), BMJ 376:e068465. Open access.

| Reported by the authors | |
|---|---|
| Sources | 12 databases (MEDLINE, Embase, PsycINFO, CINAHL, SPORTDiscus, SMEI, ASSIA, PEDro, Bibliomap, SCI-E, CPCI-S, OpenGrey) and 3 trial registers (CENTRAL, ClinicalTrials.gov, TRoPHI), September 2020, plus a PubMed update to April 2021 |
| Identified / screened | 25,170 / **14,566** |
| Included | **61 reports of 51 studies** (46 meta-analysed) |
| Published strategy | Web appendix: full strategies for each source; the MEDLINE one is translated here |

**How the review was selected.** It came from the follow-up candidate list on this branch. The candidate before it was dropped: [Mann et al. (2022)](https://doi.org/10.3389/fpubh.2022.877058), on outdoor learning, screened 13,148 unique records from nine databases. However, it publishes no list of its 147 included records, neither in the article (60 references, aggregate tables only) nor in its supplementary files.

**The benchmark list.** Tables 1 and 2 list the 51 studies with the references cited for each. That is 51 distinct references:

- Hall 2011 and Morey 2009 report one study;
- one paper (Harris 2018) reports two trials, PACE-Lift and PACE-UP.

The other ten included reports are not cited anywhere in the article or appendix, so they cannot be scored.

**Matching:**

- 46 references matched by DOI, PMID or title, each agreeing with its full citation.
- **Steptoe 1999** was accepted manually: its own DOI resolves to a record that OpenAlex has merged with an attached commentary and typed "editorial".
- **Hesselink 2013** was accepted via its identifiers. The citation text names a Diabetologia conference abstract that is not in OpenAlex, but the printed DOI and PMID resolve to the same trial's full report in BMC Family Practice. Scored as the abstract, each arm loses one study.
- **Not in OpenAlex** after a second pass:
  - Clapperton 2020, a West Indian Medical Journal supplement abstract;
  - Mitchell 2013, an AJRCCM meeting abstract (other abstracts of the same trial are not cited and are not credited);
  - Richardson 2007, a US thesis.

## Results

Both arms translate the **MEDLINE (Ovid)** free-text lines with the Ovid rules used earlier on this branch:

- terms are exact, since Ovid does not stem, with `*` kept and `?` made a mid-word `*`;
- `adjN` becomes `within N−1 words of each other`, with OR groups expanded into pairs;
- the six subject-heading lines and the publication-type line are omitted.

One substitution was needed. OQL refuses a proximity with two wildcards unless each has four leading characters, so in `physical* adj3 fit*` alone, `physical*` became "physical" and "physically".

Both arms were sent as `POST https://api.openalex.org/` with `{"oql": ...}`, limited to publications on or before 2021-04-01.

| Arm | API count | Studies / 51 | References / 51 | ≥ 49 studies? | ≤ 14,566? | Evidence |
|---|---:|---:|---:|---|---|---|
| [A — title-abstract](queries/A_title_abstract.oql) | 4,414 | 39 (76.5%) | 38 | No | Yes (0.30×) | Complete export, 45 pages |
| [B — title-abstract-keywords](queries/B_title_abstract_keywords.oql) | 4,543 | 40 (78.4%) | 39 | No | Yes (0.31×) | Complete export, 46 pages |

**B is a superset of A.** OpenAlex keywords add one study, Duijzer 2017, whose title says "primary healthcare" as one word; the strategy has only "primary health care".

## Why studies are missed (post-hoc)

Each block was run alone, restricted to the 48 matched references ([facet diagnostics](results/facet_diagnostics.json), [PubMed probe](results/posthoc_probes.json), [per-study matrix](results/per_study_retrieval.csv)).

| Facet | Title-abstract | With OpenAlex keywords |
|---|---:|---:|
| Date ≤ 2021-04-01 | 48 | 48 |
| Has an abstract in OpenAlex | 38 | 38 |
| Physical activity (21 lines) | 46 | 46 |
| Primary care (16 lines) | **42** | 43 |
| RCT filter (3 free-text lines) | **43** | 43 |

**Missing abstracts.** Ten matched references have no abstract in OpenAlex, and four of arm A's ten missed references are among them.

**The omitted MEDLINE lines rescue three.** For each reference arm A missed, PubMed's descriptors and publication types were checked against the omitted lines for the blocks it fails:

- **Rescued (3):** Driehuis 2012 and Reed 2008 are typed Randomized Controlled Trial, and Duijzer 2017 is indexed under Primary Health Care.
- **Not rescued (6):** Apinaniz 2019, Pinto 2002, Taheri 2020, Hall 2011, Moreno 2019 and Schillinger 2009. Hall 2011's study is still recovered through its companion report, Morey 2009.
- **Not in PubMed (1):** the Dutton 2006 dissertation.

These references were presumably found through the other eleven databases or the trial registers, whose adapted strategies differ from MEDLINE's.

## OQL POST execution checks

For both arms:

- re-posting the echoed OQO gave identical counts;
- cursor page 2 was consistent with page 1 and disjoint from it;
- the complete exports have no duplicates and a constant count, and the benchmark IDs in each equal the restricted-membership result.

A's export is a subset of B's. The offline verifier passes all its checks.

## Limitations

- **One strategy of fifteen.** Only the MEDLINE strategy is translated. The review's recall rests on fifteen sources, including three trial registers, and this test reproduces one.
- **Subject indexing.** MeSH and the RCT publication type are not reproduced.
- **Uncited reports.** Ten of the 61 included reports cannot be identified, so report-level recall covers only the 51 cited references.
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
| [HIV care continuum in children](../hiv_care_continuum_benchmark_2026-11-13/README.md) | 3 databases plus hand-search | 10,281 | 100% | 71.1% | 7,897 |
| **Physical activity in primary care (this test)** | **12 databases plus 3 trial registers** | **14,566** | **94%** | **78.4%** | **4,543** |

**What this review adds to the picture.** The strategy is precise in OpenAlex, but one database's free-text search cannot stand in for fifteen sources. Coverage is not the main problem: three of the 51 studies are absent and nine more are present but missed. The misses are scattered across blocks rather than concentrated in one, so no single fix would recover them.

## Files and verification

- **Protocol and source:** [protocol](PROTOCOL.md), [freeze manifest](freeze_manifest.json), [provenance](source_provenance.json), [MEDLINE strategy](source_search_strategy.json), [builder](build_queries.py), [validation](validation/).
- **Benchmark:** [benchmark](results/benchmark_source.json), [matches](results/benchmark_matches.json).
- **Results:** [summary](results/summary.json), [matrix](results/per_study_retrieval.csv), exports in [`results/`](results/).
- **Raw evidence:** [`archives/`](archives/). Headers, the API key and abstracts are not archived.
- **Live runners:** `match_benchmark.py`, `match_second_pass.py`, `run_test.py`, `diagnose_facets.py`, `posthoc_probes.py`.
- **Offline scripts:** `adjudicate.py`, `summarise.py`.

```bash
python3 pa_primary_care_benchmark_2026-11-13/verify.py
```
