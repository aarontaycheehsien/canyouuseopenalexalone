# HIV care continuum in children and adolescents: frozen OQL POST test of a three-database review

Branch `opus5.5`, 13 November 2026 (Asia/Singapore). Committed before any candidate search was executed and before the included studies were opened or matched.

## Benchmark

**Haw, Banegas, Lujintanon, Fairlie, Bwakura-Dangarembizi, Agwu, Ng and Lesko (2025).** *Characterizing the HIV care continuum among children and adolescents with HIV in eastern and southern Africa in the era of "Universal Test and Treat": a systematic review and meta-analysis.* J Int AIDS Soc 28(6):e26526. https://doi.org/10.1002/jia2.26526 (open access, PMC12166130).

| Feature | Detail |
|---|---|
| Unique records screened | **10,281** (article results text) |
| Sources | PubMed, Embase and African Index Medicus, for peer-reviewed articles "searchable using English keywords" published 1 January 2010 to 1 June 2023. Bibliographies of selected articles were hand-searched, and individual studies from systematic reviews were added. |
| Full texts | 1,510 |
| Included | **190 articles** |
| Domain | Paediatric HIV epidemiology and health services, eastern and southern Africa |

Selected from the follow-up candidate list on this branch (10,000 or more unique records, more than one source).

## Information boundary

**Inspected before freezing:**
- the article's methods and results text, including the PRISMA counts;
- Supplementary Table 1 (search strategy) in the Supporting Information file.

**Not inspected:** Supplementary Table 3 (the included-studies list) and the article's reference list. No included study, and no OpenAlex record of any, was viewed. A text search of the article body printed a run of citation numbers (162–211) with no bibliographic content.

The frozen queries are a mechanical translation of Table S1. This is an AI-assisted procedural holdout, not independent blinding.

## Frozen searches

Table S1 gives an Embase and a PubMed version of nine concepts, combined as HIV AND children/adolescents AND (care continuum OR diagnosis OR ART OR linkage OR retention OR viral load OR adherence) AND eastern/southern African countries AND publication from 2010.

**The Embase free-text lines are translated.** They carry explicit fields (`:ab,ti,kw`) and valid `NEAR/n` proximity. The PubMed column uses single quotes and `n1`/`n2`, neither of which is PubMed syntax, so it cannot be run as printed. Emtree and MeSH lines are omitted because OpenAlex has no equivalent.

`build_queries.py` applies these rules:
- **Words:** an unquoted word without `*` stays bare, which OQL stems.
- **Quoted or truncated terms:** become exact quoted strings, wildcards kept.
- **Proximity:** `NEAR/n` becomes `within n words of each other`. OQL proximity accepts neither OR groups nor a mix of bare and quoted operands, so OR groups are expanded to every pair, and a pair is quoted throughout if either side is quoted or truncated. A chain `x NEAR/i y NEAR/j z` becomes (x, y within i) AND (y, z within j).
- **Date:** publication date 2010-01-01 to 2023-06-01.
- **Scope:** default core corpus, no language or type limit.

| Arm | Field |
|---|---|
| **A** | `title-abstract` |
| **B** | `title-abstract-keywords`, the nearest field to Embase `ab,ti,kw` (OpenAlex keywords are machine-assigned, not author keywords) |

The free `/query` validation returned `valid: true` for both (`validation/`).

**Departures known in advance:**
1. Emtree and MeSH indexing are not reproduced; the review's subject-heading routes are lost.
2. African Index Medicus is not reproduced.
3. Studies found only by hand-searching or from other reviews' included lists need not match the strategy at all.
4. Pairwise expansion of chained proximity is slightly looser than Embase's chained NEAR.

## Benchmark construction, outcomes and evidence

**Denominator.** The 190 included articles in Supplementary Table 3, with full references from the article. Duplicates or discrepancies between table and reference list are documented; the article remains the unit.

**Matching** follows the earlier tests:
1. Free routes first: NCBI citation matching, Crossref, and OpenAlex single-entity lookups.
2. A paid OpenAlex second pass, only for unresolved articles.
3. An audit of every accepted match against its full citation.

**Primary recall threshold:** strictly more than 95% of 190, that is **at least 181/190**.

**Workload:** each arm's API count is compared with **10,281**. Both outcomes are reported for both arms.

**Execution** follows the earlier tests:
1. POST the count and the first page.
2. Round-trip the echoed OQO.
3. Fetch cursor page 2.
4. Check restricted membership, in batches of at most 100.
5. Make a complete cursor export only for counts of **20,000 or fewer**, and only if the daily budget allows; otherwise membership is the evidence.

Post-hoc facet diagnostics are labelled as such. Request bodies, statuses, responses and UTC timestamps are archived, but headers, the key and publisher abstracts are not. An offline verifier and checksums are provided.
