# Inclusion of students with special educational needs: frozen OQL POST test of a multi-source review

Branch `opus5.5`, 13 November 2026 (Asia/Singapore). Written and committed before any candidate search ran and before the included-study references were parsed or viewed.

## Why this benchmark

The request was a review that screened more than 10,000 records **and searched multiple sources**. Selected: **Dalgaard, Bondebjerg, Viinholt & Filges (2022), *The effects of inclusion on academic achievement, socioemotional development and wellbeing of children with special educational needs*, Campbell Systematic Reviews 18:e1291, https://doi.org/10.1002/cl2.1291** (open access, PMC9727566).

- **20,183 records screened** on title and abstract after duplicate removal, from nine bibliographic databases plus grey literature, hand searching, citation tracking and other resources.
- **94 included studies.** Most are non-randomised; 15 entered the meta-analysis.
- **Nine databases on three platforms**, each with a reported strategy (Supporting Information Appendices 1–2):
  - EBSCO: Academic Search Premier, EconLit, ERIC, APA PsycINFO, SocINDEX.
  - ProQuest: International Bibliography of the Social Sciences (IBSS), Sociological Abstracts.
  - Web of Science: Science Citation Index Expanded and Social Sciences Citation Index.
- **Grey literature, hand searching and citation tracking** were also used: ProQuest and EBSCO dissertations, NBER, SSRN, OECD iLibrary, Nordic repositories, Google Scholar, hand searches of 14 journals, and others (Appendix 4).
- **A different domain** from the repository's earlier benchmarks: education and social science.

Candidate search: the 531 Campbell Systematic Reviews records from 2018–2025 in Europe PMC were screened for abstracts reporting 10,000 or more records. Shortlisted reviews were rejected for these reasons:
- Too few included studies for a meaningful recall estimate: residential energy efficiency (16), basic income (27), small class size in special education (7), financial capability (24 studies).
- Evidence-and-gap maps rather than reviews.
- Much larger matching burden: targeted reading and mathematics interventions (607 studies).

No OpenAlex retrieval result informed the choice.

## Information boundary

**Inspected before freezing:**
- Abstract, methods, search, selection and results-of-search sections of the article.
- Appendices 1–2 (database strategies), and the titles of Appendices 3–4.
- The first header row of each supplementary spreadsheet.

**Not inspected:** the "Included studies" reference list, the study characteristics or risk-of-bias rows, and any OpenAlex record of an included study. This is an AI-assisted procedural holdout, not independent blinding, and it cannot exclude exposure through model training.

## Translation and frozen arms

All nine strategies share a free-text core: **population AND intervention AND method**. They differ in two ways: field limits, and subject-heading lines (EBSCO `DE`, ProQuest `MAINSUBJECT.EXACT`).

**OpenAlex has no equivalent for subject headings, so every arm omits the heading lines.** This is a known narrowing. In PsycINFO, for example, `DE "Special Needs Students"` alone is an OR branch of the population facet.

`build_queries.py` generates three nested arms. It asserts the term lists against the published lines (`source_search_strategies.json`). Every term is a quoted, exact wildcard term, because none of the source interfaces stem in the modes used.

| Arm | What it reproduces | Population facet |
|---|---|---|
| **B — Web of Science, exact** | The WoS SCI-EXPANDED + SSCI strategy, which is text-only, so nothing is dropped | Population and need terms in the **title** only |
| **A — EBSCO free-text core** | The five EBSCO strategies minus their subject-heading lines | S1 in title or abstract; S2 = `TI (need* OR special* OR additional*) OR AB ((special* OR additional* OR educational*) N5 need*)`, with N5 translated as OQL "within 5 words of each other" |
| **C — union of all free-text cores** | The broadest text variant (IBSS), which contains every other S2 variant | Need terms in title or abstract, no proximity |

Shared across all three arms:
- Intervention: `integrat* OR immers* OR inclus* OR mainstream* OR placement*` in title or abstract.
- Method: `effect* OR trial* OR experiment* OR control* OR random* OR impact* OR compar* OR difference*` in title or abstract.
- Publication date from **2000-01-01** (every database limiter) to **2021-04-08**. The appendix dates every database search 7–8 April 2021; the article text says 24 April. Date-only failures are reported separately.
- Default core corpus, with no language, type or benchmark-ID restriction.

**Nesting: B ⊆ A ⊆ C.** B is the cleanest test, because the same text-only strategy ran in Web of Science and returned 889 records.

All arms are submitted as `POST https://api.openalex.org/` with `{"oql": ...}`. Free `/query` validation returned `valid: true` for all three arms (`validation/`).

## Benchmark construction (after the freeze)

**Denominator.** Every entry in the article's "Included studies" reference list. The article reports 94 studies. If the list has a different number of entries, or several entries per study, the discrepancy is documented and both levels are reported:
- **Reference level:** each listed reference.
- **Study level:** recovered if any of its listed references is retrieved.
- **Primary unit:** the study level, if the mapping is unambiguous from the review; otherwise the reference level.

**Matching.** By DOI where present. Otherwise:
- Crossref and OpenAlex bibliographic lookup, with explicit adjudication.
- Dissertations, reports and working papers are matched only to the same document type and version; a journal version of a thesis is not accepted silently.
- Unmatched or ambiguous entries stay in the denominator as unrecovered.

**Reported separately:** OpenAlex coverage (how many entries exist in OpenAlex), recall among covered entries, and recall against the full denominator.

## Outcomes

- **Primary recall:** strictly greater than 95% of the full denominator. For 94 studies that means **at least 90/94**.
- **Workload comparison:** API count against **20,183** records screened from all sources. The review's database results sum to 13,791 before deduplication, which is reported as context. A lower count is potential screening volume only.
- Both outcomes are reported for all three arms. No arm is chosen after the fact.

**Expectation, stated in advance.** Benchmark studies found only through grey literature or hand searching may be absent from OpenAlex or may lack the terms the strategies need. Recall below the threshold would be an informative result, not a failure of procedure.

## Execution and evidence

1. **Per arm:** one POST giving `meta.count`, the executed OQO and the first page (`per_page=100`, `sort=publication_date:asc`, `cursor=*`). Then:
   - A round-trip POST of the echoed OQO, which must give an identical count.
   - One cursor continuation page.
2. **Membership:** the identical executed OQO plus only an AND restriction to the matched benchmark IDs, at most 100 per batch.
3. **Complete cursor export** only for arms with a count of **at most 40,000**. Otherwise recovery is labelled restricted-membership evidence.
4. **Post-hoc, labelled, after the primary results are saved:**
   - Clause diagnostics on missed records.
   - A check of which missed records OpenAlex holds at all.
   - A breakdown of the result set by domain.
   - No repaired query replaces a frozen arm.

**Archiving.** Every request body, status, response and UTC timestamp is kept. Request headers and the key are not. Publisher abstracts are not archived. An offline, standard-library verifier and SHA-256 checksums are provided.
