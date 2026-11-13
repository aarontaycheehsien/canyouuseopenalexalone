# Mental health of healthcare workers in the Eastern Mediterranean during COVID-19: designed OpenAlex searches against a three-database review

**The designed searches found 82 of 89 included studies (92.1%), against 77 (86.5%) for the mechanical translation. They returned 7,176 records, 0.62 times the authors' 11,572.** No arm met the target of 85. Only 85 of the 89 studies are in OpenAlex, so the target required a perfect search.

| Arm | Design | Studies / 89 | Records | vs 11,572 screened |
|---|---|---:|---:|---:|
| [M](queries/M_mechanical_free_text.oql) | Published free-text string, exact terms | 77 (86.5%) | 15,916 | 1.38× |
| [S1](queries/S1_designed_emro_text_or_affiliation.oql) | Designed concepts (text OR keywords) AND EMRO by names OR author-institution country | 82 (92.1%) | 10,174 | 0.88× |
| [S2](queries/S2_designed_emro_text_only.oql) | As S1, EMRO by names in title or abstract only | **82 (92.1%)** | **7,176** | **0.62×** |

Frozen and pushed ([`3c7639d`](https://github.com/aarontaycheehsien/canyouuseopenalexalone/commit/3c7639d)) before any search was scored and before the included studies were opened. Test date: 13 November 2026.

## Benchmark

[Salahi Ardekani, Sajedifar, Letafati, Jafarabadi Ashtiani et al. (2025)](https://doi.org/10.1186/s12913-025-13285-5), BMC Health Serv Res 25:1501.

- **Sources:** PubMed, Scopus and Embase, 2020 to August 2024.
- **Screening:** 11,572 unique records screened; 89 studies included.

The authors' search had no geographic limit. They excluded 11,220 records at screening as outside the Eastern Mediterranean Region.

**Matching.** 85 of the 89 are in OpenAlex, found by DOI, PMID or title. The four absent are from Iranian and Egyptian regional journals.

## What it shows

**Adding the review's geographic scope to the search is the main efficiency gain.** The authors left the region to screening. The designed arms put it into the search and cut the count from 15,916 to 7,176, while recovering five more studies than the mechanical arm.

**Author-affiliation country added nothing.** S1 and S2 found the same 82 studies; the affiliation clause only added records.

**The three studies S2 misses (indexed, not retrieved):**
- a study of anesthetists in Saudi Arabia ("anesthetist" was not in the worker concept);
- a study of pre-hospital emergency medicine personnel;
- a study whose title and abstract name no country.

Block-by-block diagnostics were not run, to conserve the daily API budget. These reasons come from the record titles. `python3 verify_designed.py hcw_mental_emro_benchmark_2026-11-13` passes all checks.
