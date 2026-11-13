# Mental health of emergency call-handlers and dispatchers: frozen test of designed OpenAlex searches

Branch `opus5.5`, 13 November 2026 (Asia/Singapore). Committed before any candidate search was scored and before the included studies were opened or matched.

## Benchmark

**Osório, Talwar, Stevelink, Sihre et al. (2024).** *Systematic review and meta-analysis on the mental health of emergency and urgent call-handlers and dispatchers.* Occup Med (Lond) 75(6):282–291. https://doi.org/10.1093/occmed/kqae104 (open access, PMC12449257).

| Feature | Detail |
|---|---|
| Unique records screened | **11,571** (16,857 identified, 5,290 duplicates) |
| Sources | Ten databases from inception to 7 January 2024, plus Google Scholar, hand-searching of Annals of Emergency Dispatch and Response, other reviews' reference lists, and forward and backward citation searching; five languages |
| Full texts | 183 |
| Included | **37 articles** |

## Information boundary

Inspected before freezing: The methods text and Supplementary Table 1 (search strategy), read only as far as the heading of Supplementary Table 2. Supplementary Table 4 (included studies) and the reference list were not opened. No included study, and no OpenAlex record of any, was viewed. Development used API counts only, archived in `development/`.

## Frozen searches

| Arm | Design |
|---|---|
| **M — mechanical** | The Supplementary Table 1 string, Ovid rules, on `title-abstract-keywords` |
| **S1 — designed** | Call-handler concept (dispatch terms tied to an emergency context; call-centre and helpline terms) AND mental-health concept, each text OR OpenAlex keywords |
| **S2 — designed, narrower** | S1 without the generic call-centre and helpline terms |

All arms: English, French, Spanish, Italian or Portuguese; publication date ≤ 2024-01-07. Design choices and reasons are in `build_queries.py`; shared helpers are in `../designed_common.py`.

Development counts: M 4,677; S1 9,179; S2 3,805. Free `/query` validation returned `valid: true` for all three arms (`validation/`).

## Outcomes and evidence

**Denominator.** The 37 included articles, with references from the article and its supplement.

**Matching:**
1. DOI and PMID routes first (free).
2. A paid title search only for unresolved items.
3. An audit of every match against its citation.

**Primary recall threshold:** strictly more than 95% of 37, that is **at least 36/37**. Each arm's count is compared with **11,571**.

**Execution:**
1. POST the count and the first page.
2. Round-trip the echoed OQO.
3. Fetch cursor page 2.
4. Check restricted membership, in batches of at most 100.

No exports are made, because of the daily budget; restricted membership is the evidence. Post-hoc diagnostics are labelled as such.
