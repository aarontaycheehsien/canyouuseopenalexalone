# Ethnicity and antidiabetic medication adherence: frozen test of designed OpenAlex searches

Branch `opus5.5`, 13 November 2026 (Asia/Singapore). Committed before any candidate search was scored and before the included studies were opened or matched.

## Benchmark

**Asiri, Todd, Robinson and Husband (2023).** *Ethnic disparities in medication adherence? A systematic review examining the association between ethnicity and antidiabetic medication adherence.* PLoS One 18(2):e0271650. https://doi.org/10.1371/journal.pone.0271650 (open access, PMC9946219).

| Feature | Detail |
|---|---|
| Unique records screened | **17,410** after removing duplicates (18,107 from databases plus 22 from other sources) |
| Sources | MEDLINE, Embase, CINAHL and PsycINFO from inception to June 2022; grey literature; reference lists and citation search |
| Full texts | 164 |
| Included | **41 studies** |

## Information boundary

Inspected before freezing: the methods and results paragraphs about searching and screening, and S1 Text (search terms). Tables were stripped before any text was printed. One quality-assessment paragraph printed with citation numbers only.

A metadata extraction printed the first four surnames in the article XML: Guariguata, Whiting, Hambleton and Beagley. Those names belong to a background diabetes-prevalence reference; whether any included study shares an author is unknown. No included study, and no OpenAlex record of any, was knowingly viewed. Development used API counts only.

## Frozen searches

The source strategy ends "adherence AND diabetes AND glycaemic control OR ethnicity". Read literally, the final OR would admit every ethnicity record on its own, so **arm M** uses the charitable reading: adherence AND diabetes AND (glycaemic control OR ethnicity).

| Arm | Design |
|---|---|
| **M — mechanical** | The Ovid `.mp.` lines, exact terms, on `title-abstract-keywords`; subject headings omitted |
| **S1 — designed** | Medication adherence AND diabetes AND ethnicity. Each concept is `title-abstract` text OR the OpenAlex keywords that mean it |
| **S2 — designed, medication context** | S1 with the adherence concept restricted to adherence words within 3 words of a medication word, plus adherence-specific keywords |

All arms: publication date ≤ 2022-06-30; no language or type limit. Design choices are documented in `build_queries.py`.

Development counts are archived in `development/`: M 9,320, S1 6,908 and S2 3,418 records. Free `/query` validation returned `valid: true` for all three arms.

## Outcomes and evidence

**Denominator.** The 41 included studies, with references from the article.

**Matching** follows the earlier tests: free routes first, a paid second pass, and an audit against each citation.

**Primary recall threshold:** strictly more than 95% of 41, that is **at least 39/41**. Each arm's count is compared with **17,410**.

**Execution:** as for the anxiety benchmark. No complete exports are planned; restricted membership is the evidence. Post-hoc diagnostics are labelled as such.
