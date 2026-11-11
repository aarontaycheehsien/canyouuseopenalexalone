# Embase Table 8 translated to OQL (November 2026)

A fresh translation of the Ovid Embase strategy in O'Mara-Eves et al. (2026), Appendix 4, Table 8, into OpenAlex OQL. It applies the lessons from the fact-check of the Substack draft. Run live on 1 November 2026 through the OpenAlex MCP `search_works` tool (OQL, retracted works included, publication years 2003–2023). Counts can drift because OpenAlex is a live index.

Files:

- `build_table8_oql.py` regenerates the queries. `S*.oql` are the searches.
- `S*_ids.oql` are the same searches restricted to the 130 known OpenAlex IDs in `../../reference_retrieval.csv`, used to measure recall.

## Mapping from Table 8

| Embase line | OQL translation |
| --- | --- |
| #4 `diabet*` and #7 (eye terms adj6 screening terms), #8/#9/#11 | `"diabet*" AND` 112 pairs of `(eye-term and screening-term within 5 words of each other)`. Ovid adjN allows N−1 intervening words, so adj6 = within 5. Bare terms are stemmed. |
| #14 `diabet* adj4 (retina … eyes)` AND #17 | `("diabet*" and "retin*"/"macul*"/"eye"/"eyes" within 3 words of each other)` AND the #17 terms |
| #2, #13 (Emtree diabetic retinopathy) with #6/#16 (screening) | `topic is T10170` (primary topic) AND `diabet*` AND the #17 terms, at the `where` level |
| #21 programme names | Kept, except `"DES program*"`, which must now co-occur with `diabet*` (see below) |
| #22–#24 countries (Emtree, text, affiliation) | `country is (GB, CA, AU, NZ, IE)` OR the #23 place/people list in title-abstract-keywords OR the same list in `raw affiliation` |
| #25 journal country, #31 animal exclusion, #33 Asia/Africa/US exclusion | Not translated |
| #29 years | 2003–2023 |

Lessons applied:

- Proximity distances use the ADJ gap rule.
- The topic fallback is a `where`-level filter, not text inside `about (...)`.
- Wildcards inside proximity are quoted.
- Affiliation text is searched as well as resolved country codes.

### Two silent-noise problems found during execution

1. **`"DES program*"` matches the French phrase "des programmes".** On its own it retrieved 18,443 works for 2003–2023, and with it the faithful translation returned 29,431 works. The whole programme-name line retrieved 526 records in Embase. Requiring `diabet*` with that phrase brought the result to 11,257.
2. **The validator rejected two wildcard forms.** `"eye*"` is too short a prefix when a proximity has two wildcards, and `"check-up*"` is split at the hyphen. Both were replaced by explicit forms.

## Arms and results

- **S1:** a faithful translation (with the two fixes above).
- **S2:** S1 plus a country-unknown route. It accepts records with no resolved country when the title contains the #14 core (diabet* within 3 of retin*/macul*/eye) and a screening word.
- **S3:** S2 plus a fallback for records without abstracts: `it doesn't have an abstract and title-abstract-keywords has ("diabet*" AND ("diabetes screening" OR "vision screening" OR "retinal screening" OR "eye care" OR "diabetic eye disease" OR "eye examination"))`. The quoted phrases match OpenAlex keywords. This stands in for the Emtree headings that Embase used to reach abstract-less records.

Recall uses 130 known eligible records in OpenAlex: 128 of the original 131, plus Briand-Racine (2013) and Hirji (2014). Precision is a lower bound: retrieved known includes divided by records retrieved. Unscreened records may hold further eligible studies.

| Search | Records | Known includes found (n = 130) | Original set (n = 128) | Of 131 | Precision (lower bound) | Records per include | Missed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **S1** faithful | 11,257 | 127 (97.7%) | 125 (97.7%) | 125 (95.4%) | 1.13% | 89 | Felfeli 2023, Hwang 2015, Sachdeva 2012 |
| **S2** + country-unknown route | not run separately | 128 (98.5%), deduced | 126 | 126 (96.2%) | — | — | Felfeli 2023, Hwang 2015 |
| **S3** + abstract-less keyword fallback | 12,364 | 130 (100%) | 128 (100%) | 128 (97.7%) | 1.05% | 95 | none |

S2's recall is deduced, not measured:

- S3 contains S2, and S2 contains S1.
- S1 missed exactly three records. Two of them (Felfeli and Hwang) have a resolved country (CA), so the country-unknown route cannot reach them; they enter S3 only through the fallback.
- Sachdeva enters S3 only through the country-unknown route, which S2 already has.

### Comparators (from the source papers, not re-run)

| Search | Records | Includes | Precision |
| --- | ---: | ---: | ---: |
| Original map, 26 resources (O'Mara-Eves et al., 2026) | 12,293 screened | 131 | 1.07% |
| Ovid Embase, Table 8 (20 December 2023) | 5,069 | not reported in the sources read | — |
| PubMed (Stansfield et al., 2025) | 2,854 | 117 / 131 | 4.1% |
| OpenAlex July 2024, 9 strings (Stansfield et al., 2025) | 21,747 | 126 / 131 (+2 new) | 0.59% |
| OpenAlex March 2025 (Stansfield et al., 2025) | 16,573 | 123 / 131 (+2 new) | 0.75% |
| Restored OQL, October 2026 pilot (`../../PILOT_REPORT.md`) | 21,679 | 125 / 131 | — |

## Interpretation limits

- **S1 is the fair estimate.** S2 and S3 each add a clause designed after seeing which known records S1 missed, so their gains are in-sample and optimistic.
- **The S3 keyword fallback is broad:** 4,496 abstract-less works worldwide before the country filter. Together, the S2 and S3 additions add 1,107 records to S1.
- **Volume is higher than Embase's:** these searches return 2.2–2.4 times Embase's 5,069. The untranslated exclusions (#25, #31, #33) explain part of the gap. The rest comes from OpenAlex's much larger, multidisciplinary corpus.
- **Precision is a lower bound.** Only known includes count as relevant. The map excluded a further 328 records that met the general criteria for pragmatic reasons. Stansfield et al. found 2 new eligible studies among 2,318 screened OpenAlex records.
- **Ranking was not evaluated.** These are set-based screening loads.
