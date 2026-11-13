# Ethnicity and antidiabetic medication adherence: designed OpenAlex searches against a four-database review

**The designed searches recovered 36 of 41 included studies (87.8%), against 34 (82.9%) for the mechanical translation. The tighter design did so at 3,418 records, a fifth of the authors' 17,410.** None met the prespecified recall target of 39.

| Arm | Design | Studies / 41 | Records | vs 17,410 screened |
|---|---|---:|---:|---:|
| [M](queries/M_mechanical_ovid.oql) | Ovid `.mp.` lines, translated mechanically | 34 (82.9%) | 9,320 | 0.54× |
| [S1](queries/S1_designed_three_concepts.oql) | Designed: text OR OpenAlex keywords, per concept | 36 (87.8%) | 6,908 | 0.40× |
| [S2](queries/S2_designed_medication_context.oql) | S1, adherence words within 3 words of a medication word | **36 (87.8%)** | **3,418** | **0.20×** |

The protocol and queries were committed and pushed ([`f7720d0`](https://github.com/aarontaycheehsien/canyouuseopenalexalone/commit/f7720d0)) before any search was scored and before the included studies were opened. Development used API counts only. Test date: 13 November 2026.

## Benchmark

[Asiri, Todd, Robinson and Husband (2023)](https://doi.org/10.1371/journal.pone.0271650), PLoS One 18:e0271650.

- **Sources:** MEDLINE, Embase, CINAHL and PsycINFO, grey literature and reference lists.
- **Screening:** 17,410 unique records screened; 41 studies included.
- **Matching:** all 41 are in OpenAlex, matched by DOI, PMID or title.

**The source strategy is ambiguous.** It ends "… AND glycaemic control OR ethnicity". Arm M reads this as adherence AND diabetes AND (glycaemic OR ethnicity). The designed arms drop the glycaemic concept, because the review's question is adherence by ethnicity.

## What the design changed (post-hoc diagnostics)

Restricted to the 41 matched studies:

| Concept | Text only | OpenAlex keywords only | Either |
|---|---:|---:|---:|
| Medication adherence (S1) | 40 | 38 | 40 |
| Medication adherence, medication context (S2) | 40 | 10 | 40 |
| Diabetes | 41 | 34 | 41 |
| Ethnicity | 36 | 29 | **37** |

**Ethnicity is the weak concept, and no wording fixes it.** These studies report ethnicity as one covariate among many.
- 13 of the 41 have no abstract in OpenAlex.
- Of the 4 ethnicity misses, two have no abstract. A third, from Klang in Malaysia, presumably names local groups (Malay, Chinese, Indian) rather than "ethnicity" or "race". The designed block, written without seeing the studies, lacked those names.

**Proximity cut the count in half and lost nothing net.** Requiring adherence words within three words of a medication word took S1's 6,908 records to 3,418. S2 lost one study S1 found and gained one S1 missed.

**The mechanical arm's losses.** It lost 7 studies, mostly through the strategy's glycaemic-control and ethnicity blocks, which both fail for studies that mention neither in their title or abstract.

## Checks

For every arm:
- re-posting the echoed OQO gave the same count;
- cursor page 2 was consistent;
- membership was tested in batches of 100 or fewer.

`python3 verify_designed.py ethnicity_adherence_benchmark_2026-11-13` passes all checks.

**Limitations:** as for the anxiety benchmark.
