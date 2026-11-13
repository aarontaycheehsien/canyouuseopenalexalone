# Anxiety and eating-disorder symptoms in adolescents: frozen test of designed OpenAlex searches

Branch `opus5.5`, 13 November 2026 (Asia/Singapore). Committed before any candidate search was scored and before the included studies were opened or matched.

## Benchmark

**Trompeter, Dârvariu, Brieva-Toloza et al. (2025).** *The prospective relationship between anxiety symptoms and eating disorder symptoms among adolescents: a systematic review and meta-analysis of a bi-directional relationship.* Eur Child Adolesc Psychiatry 34:1691–1718. https://doi.org/10.1007/s00787-024-02601-9 (open access, PMC12198302).

| Feature | Detail |
|---|---|
| Unique records screened | **19,591** after de-duplication (35,568 identified) |
| Sources | MEDLINE, PsycINFO, Scopus, Web of Science, Embase and ProQuest, from inception to 12 May 2023, updated 11 June 2024; manual PsyArXiv search; references of included studies |
| Full texts | 714 |
| Included | **54 studies** |

## Information boundary

Inspected before freezing: the methods and results paragraphs about searching and screening, and Supplementary file 3 (search terms). Tables were stripped before any text was printed. No included study, and no OpenAlex record of any, was viewed. Development used API counts only; no result list was printed.

## Frozen searches

| Arm | Design |
|---|---|
| **M — mechanical** | The Scopus TITLE-ABS-KEY string translated by this branch's rules, on `title-abstract-keywords` |
| **S1 — designed** | Anxiety AND eating-disorder AND youth concepts. Each concept is a `title-abstract` text block OR the OpenAlex keywords that mean it |
| **S2 — designed, prospective** | S1 AND a prospective-design concept, as text or the keyword "prospective associations" |

All arms: publication date ≤ 2024-06-11; no language or type limit. The design choices are documented in `build_queries.py`:

- targeted truncation;
- proximity pairs added beside phrases rather than replacing them;
- the authors' broad `diet*` and `fast*` replaced with dieting terms;
- OpenAlex keywords chosen with `find_keywords`.

Development counts are archived in `development/`: M 21,566, S1 20,271 and S2 9,424 records. Free `/query` validation returned `valid: true` for all three arms (`validation/`).

## Outcomes and evidence

**Denominator.** The 54 included studies, with references from the article.

**Matching** follows the earlier tests:
1. Free routes first.
2. A paid OpenAlex second pass for unresolved studies.
3. An audit of every match against its citation.

**Primary recall threshold:** strictly more than 95% of 54, that is **at least 52/54**. Each arm's count is compared with **19,591**.

**Execution:**
1. POST the count and the first page.
2. Round-trip the echoed OQO.
3. Fetch cursor page 2.
4. Check restricted membership, in batches of at most 100.

Because the daily budget is limited, no complete exports are planned; restricted membership is the evidence. Post-hoc diagnostics are labelled as such.
