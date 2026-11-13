# Smokefree support: frozen test of designed OpenAlex searches

Branch `opus5.5`, 13 November 2026 (Asia/Singapore). Committed before any candidate search was scored and before the included studies were opened or matched.

## Benchmark

**Boderie, Sheikh, Lo, Sheikh, Burdorf et al. (2023).** *Public support for smoke-free policies in outdoor areas and (semi-)private places: a systematic review and meta-analysis.* EClinicalMedicine 59:101982. https://doi.org/10.1016/j.eclinm.2023.101982 (open access, PMC10225670).

| Feature | Detail |
|---|---|
| Unique records screened | **6,229** (14,749 identified; duplicates and reports published before 2004 removed) |
| Sources | Embase.com, Medline Ovid, Web of Science, Cochrane CENTRAL, CINAHL and PsycINFO, reports published 1 January 2004 to 19 January 2022; reference and citation screening of included papers |
| Full texts | 348 |
| Included | **107 reports** |

## Information boundary

Inspected before freezing: The methods and results paragraphs about searching and screening (tables stripped), and Appendix I of the supplementary PDF, printed only up to the heading 'Appendix II' (which holds the included-studies table). A results sentence printed a run of citation numbers (22–128) with no bibliographic content. No included study, and no OpenAlex record of any, was viewed.

Development used API counts only, never result lists. The records in `development/` hold the final counts. Earlier rounds' counts are stated below and in `build_queries.py`; for this benchmark, the first round's files were overwritten when the counts were rerun.

## Frozen searches

| Arm | Design |
|---|---|
| **M — mechanical** | The Medline Ovid `.ab,ti` lines: exact terms, `ADJ3` → within 2 words; subject headings and `.pt.` exclusions omitted; `title-abstract` |
| **S1 — designed** | Smoke-free policy concept AND support concept, each text OR OpenAlex keywords; support words tied to policy words within 5 words |
| **S2 — designed, novel places** | S1 AND a concept for the review's novel places (outdoor areas, vehicles, homes, multi-unit housing, campuses …) |

All arms: Publication date 2004-01-01 to 2022-01-19; no language or type limit. The design choices and their reasons are in `build_queries.py`; shared helpers are in `../designed_common.py`.

Development counts: M 7,307; S1 10,282 (39,992 before the support concept was tied to policy words); S2 4,013. Free `/query` validation returned `valid: true` for all three arms (`validation/`).

## Outcomes and evidence

**Denominator.** The 107 included reports, with references from the article and its supplements.

**Matching** follows the earlier tests:
1. Free routes first.
2. A paid OpenAlex second pass for unresolved items.
3. An audit of every match against its citation.

**Primary recall threshold:** strictly more than 95% of 107, that is **at least 102/107**. Each arm's count is compared with **6,229**.

**Execution:**
1. POST the count and the first page.
2. Round-trip the echoed OQO.
3. Fetch cursor page 2.
4. Check restricted membership, in batches of at most 100.

Because the daily budget is limited, no complete exports are made; restricted membership is the evidence. Post-hoc diagnostics are labelled as such.
