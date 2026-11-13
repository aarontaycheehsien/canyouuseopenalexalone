# Nlp cognitive: frozen test of designed OpenAlex searches

Branch `opus5.5`, 13 November 2026 (Asia/Singapore). Committed before any candidate search was scored and before the included studies were opened or matched.

## Benchmark

**Shankar, Bundele and Mukhopadhyay (2025).** *A systematic review of natural language processing techniques for early detection of cognitive impairment.* Mayo Clin Proc Digit Health 3(2):100205. https://doi.org/10.1016/j.mcpdig.2025.100205 (open access, PMC12190899).

| Feature | Detail |
|---|---|
| Unique records screened | **5,033** (23,562 from databases plus 811 from other sources; 19,340 duplicates) |
| Sources | PubMed, Web of Science, Embase, CINAHL, MEDLINE, Cochrane Library, PsycINFO and Scopus, inception to August 2024; English; reference lists and citation searching |
| Full texts | 104 |
| Included | **51 studies** |

## Information boundary

Inspected before freezing: The methods text, including the base search string and the eligibility criteria, and the PRISMA counts. No included study, and no OpenAlex record of any, was viewed.

Development used API counts only, never result lists. The records in `development/` hold the final counts. Earlier rounds' counts are stated below and in `build_queries.py`; for this benchmark, the first round's files were overwritten when the counts were rerun.

## Frozen searches

| Arm | Design |
|---|---|
| **M — mechanical** | The base search string, every quoted term exact, on `title-abstract-keywords` |
| **S1 — designed** | NLP/computational-analysis AND cognitive-impairment AND speech/language concepts, each text OR OpenAlex keywords |
| **S2 — designed, detection** | S1 AND a detection/classification concept |

All arms: English; publication date ≤ 2024-08-31. The design choices and their reasons are in `build_queries.py`; shared helpers are in `../designed_common.py`.

Development counts: M 1,027; S1 4,725 (39,249 and then 36,126 before two rounds of cuts: generic language words, then transcript*, which matched transcriptomics); S2 4,033. Free `/query` validation returned `valid: true` for all three arms (`validation/`).

## Outcomes and evidence

**Denominator.** The 51 included studys, with references from the article and its supplements.

**Matching** follows the earlier tests:
1. Free routes first.
2. A paid OpenAlex second pass for unresolved items.
3. An audit of every match against its citation.

**Primary recall threshold:** strictly more than 95% of 51, that is **at least 49/51**. Each arm's count is compared with **5,033**.

**Execution:**
1. POST the count and the first page.
2. Round-trip the echoed OQO.
3. Fetch cursor page 2.
4. Check restricted membership, in batches of at most 100.

Because the daily budget is limited, no complete exports are made; restricted membership is the evidence. Post-hoc diagnostics are labelled as such.
