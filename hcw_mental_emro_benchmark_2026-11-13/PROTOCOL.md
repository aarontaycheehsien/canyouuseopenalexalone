# Mental health of healthcare workers in the Eastern Mediterranean during COVID-19: frozen test of designed OpenAlex searches

Branch `opus5.5`, 13 November 2026 (Asia/Singapore). Committed before any candidate search was scored and before the included studies were opened or matched.

## Benchmark

**Salahi Ardekani, Sajedifar, Letafati, Jafarabadi Ashtiani et al. (2025).** *Risk factors associated with mental health symptoms among health care workers during the COVID-19 pandemic in EMRO countries: a systematic review.* BMC Health Serv Res 25:1501. https://doi.org/10.1186/s12913-025-13285-5 (open access, PMC12636158).

| Feature | Detail |
|---|---|
| Unique records screened | **11,572** (21,126 identified, 9,554 duplicates) |
| Sources | PubMed, Scopus and Embase, 1 January 2020 to 4 August 2024; no geographic limit in the search (11,220 records excluded at screening as outside EMRO) |
| Full texts | 322 |
| Included | **89 studies** |

## Information boundary

Inspected before freezing: The methods text (search keywords, databases, dates, PRISMA counts) and Table 1 (key search terms). The included-studies table and reference list were not opened. No included study, and no OpenAlex record of any, was viewed. Development used API counts only, archived in `development/`.

## Frozen searches

| Arm | Design |
|---|---|
| **M — mechanical** | The published free-text string, exact terms, on `title-abstract-keywords` |
| **S1 — designed, EMRO by text or affiliation** | COVID AND healthcare workers AND mental health (each text OR OpenAlex keywords) AND EMRO country/region/city names OR an author institution in an EMRO country |
| **S2 — designed, EMRO by text only** | As S1 without the institution-country clause |

All arms: Publication date 2020-01-01 to 2024-08-04; no language or type limit. Design choices and reasons are in `build_queries.py`; shared helpers are in `../designed_common.py`.

Development counts: M 15,916; S1 10,174; S2 7,176. Free `/query` validation returned `valid: true` for all three arms (`validation/`).

## Outcomes and evidence

**Denominator.** The 89 included studys, with references from the article and its supplement.

**Matching:**
1. DOI and PMID routes first (free).
2. A paid title search only for unresolved items.
3. An audit of every match against its citation.

**Primary recall threshold:** strictly more than 95% of 89, that is **at least 85/89**. Each arm's count is compared with **11,572**.

**Execution:**
1. POST the count and the first page.
2. Round-trip the echoed OQO.
3. Fetch cursor page 2.
4. Check restricted membership, in batches of at most 100.

No exports are made, because of the daily budget; restricted membership is the evidence. Post-hoc diagnostics are labelled as such.
