# NLP detection of cognitive impairment: designed OpenAlex searches against an eight-database review

**The designed search found 46 of 51 included studies (90.2%) at 4,725 records, below the authors' 5,033 screened. The mechanical translation of the published base string found 25 (49.0%) at 1,027.** Neither met the target of 49.

| Arm | Design | Studies / 51 | Records | vs 5,033 screened |
|---|---|---:|---:|---:|
| [M](queries/M_mechanical_base_string.oql) | The base search string, exact phrases | 25 (49.0%) | 1,027 | 0.20× |
| [S1](queries/S1_designed_three_concepts.oql) | Designed: NLP/computational analysis AND cognitive impairment AND speech/language, text OR keywords | **46 (90.2%)** | **4,725** | **0.94×** |
| [S2](queries/S2_designed_plus_detection.oql) | S1 AND a detection/classification concept | 45 (88.2%) | 4,033 | 0.80× |

All arms are limited to English and dated on or before 2024-08-31. Frozen and pushed ([`5cd6fce`](https://github.com/aarontaycheehsien/canyouuseopenalexalone/commit/5cd6fce)) before any search was scored and before the included studies were opened. Test date: 13 November 2026.

## Benchmark

[Shankar, Bundele and Mukhopadhyay (2025)](https://doi.org/10.1016/j.mcpdig.2025.100205), Mayo Clin Proc Digit Health 3:100205.

- **Sources:** eight databases, from inception to August 2024.
- **Screening:** 5,033 unique records screened; 51 studies included.
- **Matching:** all 51 are in OpenAlex, matched by DOI.
- **Dates:** two are dated by OpenAlex after the search end (September and November 2024), so every date-limited arm excludes them.

## What made the difference (post hoc)

| Concept (restricted to 51 studies) | Text | OpenAlex keywords | Either |
|---|---:|---:|---:|
| NLP / computational analysis | 48 | 22 | 49 |
| Cognitive impairment | 50 | 37 | 50 |
| Speech / language | 51 | 15 | 51 |
| M's NLP block (exact phrases) | — | — | 38 |
| M's detection block (exact words) | — | — | 39 |

**The published base string is too literal for a search engine without subject indexing.** Its exact phrases ("natural language processing", "speech analysis") and exact detection words ("detection", "classification") miss "automated analysis", "machine learning", "linguistic markers" and "classifier".

**The designed concepts fixed this**, using truncation, proximity pairs (automat\* near speech, linguistic near feature\*) and the NLP and speech keywords.

**The designed arm's five misses:**
- 2 date artefacts;
- 1 study of bipolar disorder (no cognitive-impairment terms);
- 2 studies described as a "speech-based AI system" or as analysing "pauses", which avoid NLP vocabulary.

**One development trap is worth recording.** The wildcard `transcript*` also matches "transcriptome". It pulled in Alzheimer genetics and inflated the development count from about 4,700 to 36,000, until it was replaced by specific forms before the freeze.

`python3 verify_designed.py nlp_cognitive_benchmark_2026-11-13` passes all checks.
