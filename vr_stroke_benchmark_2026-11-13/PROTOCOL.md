# Vr stroke: frozen test of designed OpenAlex searches

Branch `opus5.5`, 13 November 2026 (Asia/Singapore). Committed before any candidate search was scored and before the included studies were opened or matched.

## Benchmark

**Soleimani, Ghazisaeedi and Heydari (2024).** *The efficacy of virtual reality for upper limb rehabilitation in stroke patients: a systematic review and meta-analysis.* BMC Med Inform Decis Mak 24:135. https://doi.org/10.1186/s12911-024-02534-y (open access, PMC11127427).

| Feature | Detail |
|---|---|
| Unique records screened | **7,381** (11,834 identified, 4,459 duplicates; PRISMA figure) |
| Sources | PubMed, Scopus, IEEE, Web of Science and PsycNet; English-language RCTs from inception to March 2023 |
| Full texts | 69 |
| Included | **55 RCTs** |

## Information boundary

Inspected before freezing: The methods paragraphs, the PRISMA figure, and Additional File 1 (search strategies). Opening the supplements printed the first line of Additional File 3 ('Characteristics of included studies [ordered by study ID]') and nothing more. No included study, and no OpenAlex record of any, was viewed.

Development used API counts only, never result lists. The records in `development/` hold the final counts. Earlier rounds' counts are stated below and in `build_queries.py`; for this benchmark, the first round's files were overwritten when the counts were rerun.

## Frozen searches

| Arm | Design |
|---|---|
| **M — mechanical** | The Web of Science TS= string (all four blocks are text): bare words stemmed, quoted phrases exact, wildcards exact; `title-abstract-keywords` |
| **S1 — designed** | Stroke AND virtual-reality/gaming AND randomised-trial concepts, each text OR OpenAlex keywords; the authors' near-universal rehabilitation block dropped |
| **S2 — designed, upper limb** | S1 AND an upper-limb concept |

All arms: English (the authors' limit); publication date ≤ 2023-03-31. The design choices and their reasons are in `build_queries.py`; shared helpers are in `../designed_common.py`.

Development counts: M 18,063; S1 1,536; S2 976. Free `/query` validation returned `valid: true` for all three arms (`validation/`).

## Outcomes and evidence

**Denominator.** The 55 included trials, with references from the article and its supplements.

**Matching** follows the earlier tests:
1. Free routes first.
2. A paid OpenAlex second pass for unresolved items.
3. An audit of every match against its citation.

**Primary recall threshold:** strictly more than 95% of 55, that is **at least 53/55**. Each arm's count is compared with **7,381**.

**Execution:**
1. POST the count and the first page.
2. Round-trip the echoed OQO.
3. Fetch cursor page 2.
4. Check restricted membership, in batches of at most 100.

Because the daily budget is limited, no complete exports are made; restricted membership is the evidence. Post-hoc diagnostics are labelled as such.
