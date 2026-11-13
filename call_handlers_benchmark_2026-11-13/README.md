# Mental health of emergency call-handlers and dispatchers: designed OpenAlex searches against a ten-database review

**Coverage decides this one: only 27 of the 37 included articles are in OpenAlex, so even a perfect search could reach only 73%.** The designed search found 24 (64.9%) at 9,179 records; the mechanical translation found 17 (45.9%) at 4,677. The target was 36.

| Arm | Design | Articles / 37 | Records | vs 11,571 screened |
|---|---|---:|---:|---:|
| [M](queries/M_mechanical_ovid.oql) | Supplementary Table 1 string, Ovid rules | 17 (45.9%) | 4,677 | 0.40× |
| [S1](queries/S1_designed_two_concepts.oql) | Call-handler concept (dispatch tied to emergency context; call-centre and helpline terms) AND mental health, text OR keywords | **24 (64.9%)** | 9,179 | 0.79× |
| [S2](queries/S2_designed_without_generic_call_centres.oql) | S1 without generic call-centre and helpline terms | 22 (59.5%) | 3,805 | 0.33× |

All arms are limited to the review's five languages and to dates up to 7 January 2024. Frozen and pushed ([`3c7639d`](https://github.com/aarontaycheehsien/canyouuseopenalexalone/commit/3c7639d)) before any search was scored and before the included articles were opened. Test date: 13 November 2026.

## Benchmark

[Osório, Talwar, Stevelink, Sihre et al. (2024)](https://doi.org/10.1093/occmed/kqae104), Occup Med (Lond) 75:282–291.

- **Sources:** ten databases, Google Scholar, hand-searching of *Annals of Emergency Dispatch and Response* (AEDR), and citation searching.
- **Screening:** 11,571 unique records screened; 37 articles included.

**The benchmark list.** Supplementary Table 4 gives author and year for each article. These were paired with the article's references by first author and year.

**Matching:**
- Miller 2017's printed PMID belongs to a different paper; the correct record was found by title.
- **Ten are absent from OpenAlex.** Six are AEDR articles, the journal the authors hand-searched because PubMed does not index it. The other four are a 1997 psychology journal article, a Spanish-language report, a French-language journal article, and a state public-health review.

## What it shows

**This is a coverage failure first.** The literature lives partly in a specialist practitioner journal that neither PubMed nor OpenAlex indexes.

**Among the 27 indexed articles, the designed search found 24 (88.9%); the mechanical arm found 17.** Without block diagnostics, the cause of the mechanical arm's seven extra misses is not established.

**The three indexed misses use wording outside the call-handler concept:** "police communicators" and "emergency telecommunications personnel".

**S2's narrower concept cost recall.** It dropped two telephone-helpline nurse studies that the review counts as call handling.

Block-by-block diagnostics were not run, to conserve the daily API budget. `python3 verify_designed.py call_handlers_benchmark_2026-11-13` passes all checks.
