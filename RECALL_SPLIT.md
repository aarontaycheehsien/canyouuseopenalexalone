# Not indexed versus missed by the search

**Across the 15 benchmarks on branch `opus5.5`, 256 included studies were not retrieved by the best frozen OpenAlex search. 69 (27%) are not indexed in OpenAlex; 187 (73%) are indexed but the search missed them.**

- **Recall, all included** = found ÷ all included studies: what OpenAlex alone delivers.
- **Recall, indexed only** = found ÷ included studies that are in OpenAlex: how well the search strategy performs on what OpenAlex holds.

| Review | Included | In OpenAlex | Not indexed | Indexed but missed | Recall, all included | Recall, indexed only | Records (authors screened) |
|---|---:|---:|---:|---:|---:|---:|---:|
| [Motor competence (Bao 2024)](motor_competence_benchmark_2026-11-13/README.md) | 44 | 44 (100%) | 0 | 1 | 97.7% | 97.7% | 7,807 (12,117) |
| [Transgenerational inheritance (Walker 2018)](walker_transgenerational_benchmark_2026-11-12/README.md) | 257 | 257 (100%) | 0 | 8 | 96.9% | 96.9% | 306,031 (63,754) |
| [Health workers' mental health, EMRO (Salahi Ardekani 2025)](hcw_mental_emro_benchmark_2026-11-13/README.md)† | 89 | 85 (96%) | 4 | 3 | 92.1% | 96.5% | 7,176 (11,572) |
| [Precarious employment (Pulford 2022)](precarious_employment_benchmark_2026-11-13/README.md) | 50 | 48 (96%) | 2 | 4 | 88.0% | 91.7% | 42,085 (12,940) |
| [Smoke-free policy support (Boderie 2023)](smokefree_support_benchmark_2026-11-13/README.md) | 107 | 103 (96%) | 4 | 10 | 86.9% | 90.3% | 7,307 (6,229) |
| [NLP for cognitive impairment (Shankar 2025)](nlp_cognitive_benchmark_2026-11-13/README.md)† | 51 | 51 (100%) | 0 | 5 | 90.2% | 90.2% | 4,725 (5,033) |
| [Anxiety and eating disorders (Trompeter 2025)](anxiety_eating_benchmark_2026-11-13/README.md)† | 54 | 54 (100%) | 0 | 6 | 88.9% | 88.9% | 9,424 (19,591) |
| [Call-handlers' mental health (Osório 2024)](call_handlers_benchmark_2026-11-13/README.md)† | 37 | 27 (73%) | 10 | 3 | 64.9% | 88.9% | 9,179 (11,571) |
| [Ethnicity and diabetes adherence (Asiri 2023)](ethnicity_adherence_benchmark_2026-11-13/README.md)† | 41 | 41 (100%) | 0 | 5 | 87.8% | 87.8% | 3,418 (17,410) |
| [Bt maize (Meissle 2022)](bt_maize_multisource_benchmark_2026-11-12/README.md) | 166 | 138 (83%) | 28 | 17 | 72.9% | 87.7% | 6,775 (12,967) |
| [Physical activity in primary care (Kettle 2022)](pa_primary_care_benchmark_2026-11-13/README.md) | 51 | 48 (94%) | 3 | 8 | 78.4% | 83.3% | 4,543 (14,566) |
| [Cost of mental disorders (Christensen 2020)](cost_mental_disorders_benchmark_2026-11-13/README.md) | 143 | 141 (99%) | 2 | 25 | 81.1% | 82.3% | 40,605 (13,579) |
| [Special educational needs (Dalgaard 2022)](inclusion_sen_benchmark_2026-11-13/README.md) | 94 | 79 (84%) | 15 | 18 | 64.9% | 77.2% | 151,147 (20,183) |
| [HIV care in children (Haw 2025)](hiv_care_continuum_benchmark_2026-11-13/README.md) | 190 | 190 (100%) | 0 | 55 | 71.1% | 71.1% | 7,897 (10,281) |
| [VR for stroke rehabilitation (Soleimani 2024)](vr_stroke_benchmark_2026-11-13/README.md)†‡ | 55 | 54 (98%) | 1 | 19 | 63.6% | 64.8% | 1,536 (7,381) |
| **All 15** | **1,429** | **1,360 (95.2%)** | **69** | **187** | **82.1%** | **86.2%** | |

† Best arm is a designed search (text OR OpenAlex keywords, targeted truncation and proximity). For smoke-free policy support the mechanical translation was best; all five designed-search reviews are compared below.
‡ The one 'not indexed' trial is unidentifiable: its title is truncated in the review's own supplement.

**Metadata, not strategy.** Some 'indexed but missed' items are misdated in OpenAlex and fall outside the date limit: one in the anxiety review and two in the NLP review. Leaving them out, indexed-only recall is 90.6% and 93.9%.

**Best arm chosen after the fact.** For each review the frozen arm with the highest recall is shown, which flatters OpenAlex slightly.

## Mechanical translation versus designed search (indexed only)

| Review | Mechanical: found @ records | Designed: found @ records |
|---|---:|---:|
| Health workers' mental health, EMRO (Salahi Ardekani 2025) | 77/85 (90.6%) @ 15,916 | 82/85 (96.5%) @ 7,176 |
| Smoke-free policy support (Boderie 2023) | 93/103 (90.3%) @ 7,307 | 92/103 (89.3%) @ 10,282 |
| NLP for cognitive impairment (Shankar 2025) | 25/51 (49.0%) @ 1,027 | 46/51 (90.2%) @ 4,725 |
| Anxiety and eating disorders (Trompeter 2025) | 42/54 (77.8%) @ 21,566 | 48/54 (88.9%) @ 9,424 |
| Call-handlers' mental health (Osório 2024) | 17/27 (63.0%) @ 4,677 | 24/27 (88.9%) @ 9,179 |
| Ethnicity and diabetes adherence (Asiri 2023) | 34/41 (82.9%) @ 9,320 | 36/41 (87.8%) @ 3,418 |
| VR for stroke rehabilitation (Soleimani 2024) | 22/54 (40.7%) @ 18,063 | 35/54 (64.8%) @ 1,536 |

## Classification against both success criteria

Success = recall strictly above 95% of all included studies **and** records no more than the authors' unique records screened, in the same frozen arm.

| Review | Target | In OpenAlex | Best within authors' load | Best at any load | Failure type | Main reason |
|---|---:|---:|---:|---:|---|---|
| Motor competence (Bao 2024) | 42 | 44 (100%) | 43/44 @ 7,807 | 43/44 @ 7,807 | **Pass** | Recent journal literature with consistent vocabulary |
| Transgenerational inheritance (Walker 2018) | 245 | 257 (100%) | none | 249/257 @ 306,031 | **Recall met, load failed** | OpenAlex spans all disciplines, so the PubMed text strategy returns 4.8x the records |
| Call-handlers' mental health (Osório 2024) | 36 | 27 (73%) | 24/37 @ 9,179 | 24/37 @ 9,179 | **Coverage makes target impossible** | 10 absent, six from a practitioner journal the authors hand-searched |
| Bt maize (Meissle 2022) | 158 | 138 (83%) | 121/166 @ 6,775 | 121/166 @ 6,775 | **Coverage makes target impossible** | Regional journals, reports and website items absent |
| Physical activity in primary care (Kettle 2022) | 49 | 48 (94%) | 40/51 @ 4,543 | 40/51 @ 4,543 | **Coverage makes target impossible** | Meeting abstracts and a thesis absent; scattered misses across 15 sources |
| Special educational needs (Dalgaard 2022) | 90 | 79 (84%) | 34/94 @ 18,946 | 61/94 @ 151,147 | **Coverage makes target impossible** | Dissertations and reports absent; weak special-needs wording |
| Health workers' mental health, EMRO (Salahi Ardekani 2025) | 85 | 85 (96%) | 82/89 @ 7,176 | 82/89 @ 7,176 | **Coverage leaves no margin, plus search misses** | 4 regional-journal studies absent; 3 vocabulary misses (anesthetists, pre-hospital staff, no country named) |
| Precarious employment (Pulford 2022) | 48 | 48 (96%) | 38/50 @ 8,140 | 44/50 @ 42,085 | **Coverage leaves no margin, plus search misses** | Health block too narrow; missing abstracts |
| Smoke-free policy support (Boderie 2023) | 102 | 103 (96%) | 89/107 @ 4,013 | 93/107 @ 7,307 | **Coverage leaves no margin, plus search misses** | Support wording too varied; 4 reports absent |
| NLP for cognitive impairment (Shankar 2025) | 49 | 51 (100%) | 46/51 @ 4,725 | 46/51 @ 4,725 | **Search failure: vocabulary and metadata, near miss** | Two misdated records; three avoid NLP terms |
| Anxiety and eating disorders (Trompeter 2025) | 52 | 54 (100%) | 48/54 @ 9,424 | 48/54 @ 9,424 | **Search failure: vocabulary, near miss** | Undergraduate samples without youth wording; one misdated record |
| Ethnicity and diabetes adherence (Asiri 2023) | 39 | 41 (100%) | 36/41 @ 3,418 | 36/41 @ 3,418 | **Search failure: concept only in full text** | Ethnicity reported only as a covariate; abstracts missing |
| Cost of mental disorders (Christensen 2020) | 136 | 141 (99%) | none | 116/143 @ 40,605 | **Search failure: vocabulary, and load failed** | Inconsistent cost wording; missing abstracts; bibliography-found studies |
| HIV care in children (Haw 2025) | 181 | 190 (100%) | 135/190 @ 7,897 | 135/190 @ 7,897 | **Search failure: indexing-dependent concept** | Age concept relied on subject headings |
| VR for stroke rehabilitation (Soleimani 2024) | 53 | 54 (98%) | 35/55 @ 1,536 | 35/55 @ 1,536 | **Search failure: review scope wider than its vocabulary** | Robotic and brain-computer-interface trials counted as VR never say so |

| Failure type | Reviews |
|---|---:|
| Pass | 1 |
| Recall met, load failed | 1 |
| Coverage makes target impossible | 4 |
| Coverage leaves no margin, plus search misses | 3 |
| Search failure | 6 |

Generated by `python3 recall_split.py` from each benchmark's archived matches and run observations; data in [`recall_split.csv`](recall_split.csv).
