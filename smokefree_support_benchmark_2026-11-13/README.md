# Public support for novel smoke-free policies: designed OpenAlex searches against a six-database review

**Here the mechanical translation did best: 93 of 107 included reports (86.9%) at 7,307 records.** The designed searches found 92 at 10,282 and 89 at 4,013. None met the target of 102.

| Arm | Design | Reports / 107 | Records | vs 6,229 screened |
|---|---|---:|---:|---:|
| [M](queries/M_mechanical_ovid.oql) | Medline Ovid `.ab,ti` lines: exact terms, `ADJ3` → within 2 | **93 (86.9%)** | 7,307 | 1.17× |
| [S1](queries/S1_designed_policy_support.oql) | Designed: policy concept AND support concept (support words within 5 words of policy words), text OR keywords | 92 (86.0%) | 10,282 | 1.65× |
| [S2](queries/S2_designed_plus_places.oql) | S1 AND a "novel places" concept | 89 (83.2%) | **4,013** | **0.64×** |

Frozen and pushed ([`5cd6fce`](https://github.com/aarontaycheehsien/canyouuseopenalexalone/commit/5cd6fce)) before any search was scored and before the included reports were opened. Development used counts only. Test date: 13 November 2026.

## Benchmark

[Boderie, Sheikh, Lo et al. (2023)](https://doi.org/10.1016/j.eclinm.2023.101982), EClinicalMedicine 59:101982.

- **Sources:** six databases, covering 2004 to January 2022.
- **Screening:** 6,229 unique records screened; 107 reports included, cited as references 22–128.

**Matching.**

- 103 of the 107 reports are in OpenAlex. Abundis 2008 resolves under its Spanish title.
- Absent after two passes:
  - a German prison survey;
  - a Spanish-language article;
  - a New Zealand agency report;
  - an *Am J Health Behav* article cited as 2011.
- 21 of the 103 have no abstract in OpenAlex.

## Why the designed searches did not beat the source (post hoc)

| Concept (restricted to the 103 matched reports) | Text | OpenAlex keywords | Either |
|---|---:|---:|---:|
| Smoke-free policy | 99 | 53 | 101 |
| Support, tied to policy words within 5 (S1) | 94 | 5 | 94 |
| Novel places (S2) | 96 | 22 | 96 |
| Authors' support block (M, untied) | — | — | 97 |

**The authors' strategy was already a proximity strategy.** It ties smoking words to policy words within two words, and that is precise.

**Tying support to policy words cost recall.** I added the tie to cut the count, because support words alone left the designed search at 39,992 records. It lost 9 reports whose support wording sits further from the policy wording, and the count still ended above M's.

**The places concept cut the count to 0.64 times the screening load and lost three more reports.** These describe support for local or campus policies without naming a place term.

**OpenAlex keywords added little.** The policy keywords matched 53 reports, almost all already caught by text.

`python3 verify_designed.py smokefree_support_benchmark_2026-11-13` passes all checks.

**Limitations:**
- The designs are mine, written after the earlier tests.
- No exports were made.
- Precision is not estimated.
