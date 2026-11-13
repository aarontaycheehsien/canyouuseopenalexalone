# Anxiety and eating-disorder symptoms: designed OpenAlex searches against a six-database review

**The designed searches recovered 48 of 54 included studies (88.9%), against 42 (77.8%) for the mechanical translation. The best of them returned less than half the authors' screening load.** None met the prespecified recall target of 52.

| Arm | Design | Studies / 54 | Records | vs 19,591 screened |
|---|---|---:|---:|---:|
| [M](queries/M_mechanical_scopus.oql) | Scopus string, translated mechanically | 42 (77.8%) | 21,566 | 1.10× |
| [S1](queries/S1_designed_three_concepts.oql) | Designed: text OR OpenAlex keywords, per concept | 48 (88.9%) | 20,271 | 1.03× |
| [S2](queries/S2_designed_plus_prospective.oql) | S1 AND a prospective-design concept | **48 (88.9%)** | **9,424** | **0.48×** |

The protocol and queries were committed and pushed ([`f7720d0`](https://github.com/aarontaycheehsien/canyouuseopenalexalone/commit/f7720d0)) before any search was scored and before the included studies were opened. Development used API counts only ([`development/`](development/)). Test date: 13 November 2026.

## Benchmark

[Trompeter, Dârvariu, Brieva-Toloza et al. (2025)](https://doi.org/10.1007/s00787-024-02601-9), Eur Child Adolesc Psychiatry 34:1691–1718.

- **Sources:** six databases (MEDLINE, PsycINFO, Scopus, Web of Science, Embase, ProQuest), a manual PsyArXiv search and reference lists.
- **Screening:** 19,591 unique records screened; 54 studies included.

**Matching.** All 54 studies are in OpenAlex, citing 53 references (Fitzsimmons-Craft 2012 reports two studies).

- Fairweather-Schmidt and Wade (2019) was accepted manually: its DOI resolves to a record with the same authors under a different title.
- Hanback's 2010 dissertation is in OpenAlex but dated 2025-05-30, so every date-limited arm excludes it.

## What the design changed (post-hoc diagnostics)

Each concept was run alone, restricted to the 53 matched references ([facets](results/facet_diagnostics.json), [matrix](results/per_study_retrieval.csv)).

| Concept | Text only | OpenAlex keywords only | Either |
|---|---:|---:|---:|
| Anxiety | 51 | 30 | 51 |
| Eating-disorder symptoms | 52 | 46 | **53** |
| Youth | 50 | 12 | 50 |
| Prospective design (S2 only) | 52 | 1 | 52 |

**The youth concept accounts for most of the gain over M.**
- The mechanical youth block lost 8 references in Scopus terms.
- The designed block recovered five of them with `student*`, `school*`, `pubert*` and the "adolescents"/"children" keywords.
- 20 of the 53 references have no abstract in OpenAlex.

**OpenAlex keywords made the eating-disorder concept complete.** Neither text nor keywords alone reached all 53; together they did.

**The design block was free.** The review includes only prospective studies, and 52 of 53 abstracts or keywords say so. S2 lost nothing against S1 and halved the count.

**The six studies S2 misses** (five references):
- 3 fail the youth concept: undergraduate samples, two without abstracts;
- 1 has no anxiety term (Le Grange 2014, on "abnormal eating attitudes");
- 1 is the misdated dissertation.

## Checks

For every arm:
- re-posting the echoed OQO gave the same count;
- cursor page 2 was consistent;
- membership was tested in batches of 100 or fewer.

`python3 verify_designed.py anxiety_eating_benchmark_2026-11-13` passes all checks.

**Limitations:**
- The design was mine, written with the lessons of the eight earlier benchmarks in mind, though without seeing this review's studies.
- There are no complete exports.
- Precision is not estimated.
