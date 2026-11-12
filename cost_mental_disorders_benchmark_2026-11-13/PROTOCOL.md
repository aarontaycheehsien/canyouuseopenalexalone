# Cost of mental disorders: frozen OQL POST test of a six-database review

Branch `opus5.5`, 13 November 2026 (Asia/Singapore). Committed before any candidate search was executed and before the included references were parsed or matched.

## Why this benchmark

The request was for a review that screened more than 10,000 unique records and searched multiple sources.

**Selected:** Christensen, Lim, Saha et al. (2020), *The cost of mental disorders: a systematic review*, Epidemiology and Psychiatric Sciences 29:e142, https://doi.org/10.1017/S204579602000075X. It is open access (PMC7443800).

- **Records screened:** 13,579 titles and abstracts, after 5,241 duplicates were removed from 18,820 database records. These figures are from the PRISMA flow chart.
- **Sources:** six databases. Records found in each:

  | Database | Records |
  |---|---:|
  | PubMed | 11,201 |
  | PsycINFO | 2,807 |
  | Web of Science | 2,610 |
  | Embase | 2,196 |
  | NHS York | 6 |
  | EconLit | 0 |

  Bibliography searching added 31 articles.
- **Included:** 143 articles. Of these, 112 came from the database searches and 31 from bibliography searching.
- **Domain:** health economics (cost-of-illness studies), across nine mental disorder groups.

**How it was chosen.** A Europe PMC scan of 6,456 open-access systematic reviews (2017–2025) whose abstracts report screening counts produced a shortlist. Each shortlisted review was then checked against its PRISMA flow chart. Two shortlisted reviews failed, because their abstracts report records before deduplication:

- Kilich et al. (2020) screened 7,925 unique records.
- Hindi et al. (2024) screened 5,812.

The motor-competence review (12,117 screened) is queued next.

## Information boundary, recorded honestly

Online Resource 1 holds the search strings and, immediately after them, the **author–year citations of all 143 included studies** (for example "Amaddeo et al., 1997"). Both were displayed together before this freeze.

Not yet done:
- Full titles and identifiers have not been parsed or matched.
- No OpenAlex result for any included study has been seen.

**Why the exposure has limited effect.** The frozen queries are a mechanical translation of the published PubMed strings; no term was added, removed or chosen with reference to the included studies. The few judgement calls listed below concern syntax only:
- the date ceiling;
- the field;
- the handling of a nested NOT;
- one missing operator.

This remains an AI-assisted procedural holdout, not independent blinding.

## Frozen searches

Only the PubMed strings are published. The authors say the strings for the other five databases "were modified to fit the other databases and can be provided by request". This test therefore translates the PubMed strategy alone and asks whether OpenAlex can stand in for all six sources.

The authors ran a separate search for each of the nine disorder groups:

> #1 cost-of-illness terms AND #2 (1980–2019, NOT animal\*, NOT trial\*) AND one #3 disorder group

Their union is #1 AND (group 1 OR … OR group 9), NOT animal\*, NOT trial\*.

`build_queries.py` makes the translation mechanically:

- **Terms.** Every `[TIAB]` term or phrase becomes an exact, quoted OQL string, because PubMed does not stem. Truncation is kept as an OQL wildcard inside the quotes.
- **Nested NOT.** The substance group's `(abuse [TIAB] NOT (child OR children OR sexual abuse))` keeps its NOT inside the search string. The untagged inner terms are searched in the same field.
- **Missing operator.** The schizophrenia group has no operator between `schizotypal* [TIAB]` and `psychotic* [TIAB]`. PubMed's default operator is AND, so the two are ANDed.
- **Stray space.** `alcohol- related disorder` becomes the phrase "alcohol related disorder".
- **Exclusions.** `NOT animal*` and `NOT trial*` stay as NOT clauses in the same field.
- **Dates.** From 1980-01-01 to **2019-06-30**. The string allows dates up to 2019-12-31, but the searches ran in May and June 2019.
- **Corpus.** The default core corpus, with no language, type or other restriction.

There are two arms, differing only in field:

- **A — title-abstract.** The closest equivalent of `[TIAB]`.
- **B — title-abstract-keywords.** The same string, with OpenAlex keywords added. The only difference from A is the keyword field.

The free `/query` validation returned `valid: true` for both arms (`validation/`).

Some departures from the original search are known in advance:

1. **Unpublished strategies.** The PsycINFO, Web of Science, Embase, NHS York and EconLit strategies are unpublished. Any subject headings they used cannot be reproduced.
2. **Short acronyms.** Terms such as "ADD", "BP", "ODD", "GAD" and "ASD" match ordinary words and other meanings in both PubMed and OpenAlex. They are kept, not repaired.
3. **No exact equivalents.** A publication-date ceiling is not the same as a PubMed snapshot, and `title-abstract` is not exactly `[TIAB]`.

## Benchmark construction (after the freeze)

**Denominator.** Every one of the 143 included articles listed in Online Resource 1, with full references taken from the article and Online Resources 1–2.

- If the 112 database-found and 31 bibliography-found articles can be told apart from the published material, recall is reported for each subset. Otherwise only the total is reported.
- Any discrepancy against 143 is documented entry by entry.

**Matching**, in this order:

1. Crossref bibliographic query to find a DOI.
2. PubMed title search to find a PMID.
3. OpenAlex single-entity lookup, which is free.
4. OpenAlex title search, as a fallback.

Every accepted match is audited against the full citation. Unmatched references stay in the denominator as not covered.

## Outcomes

- **Primary recall:** strictly more than 95% of the 143 included articles, that is **at least 136/143**.
- **Workload:** the API count compared with **13,579**.
- Both outcomes are reported for both arms. No arm is chosen after the fact.

## Execution and evidence

The procedure is the same as in the other tests on this branch:

1. A POST returning the count and the first page (with `cursor=*`).
2. A round-trip of the echoed OQO.
3. Cursor page 2.
4. Benchmark-restricted membership, in batches of at most 100.

**Export.** A complete cursor export is made for each arm with a count of **20,000 or fewer**. This cap is lower than the earlier tests' 40,000 because only $0.31 of today's free budget remained at freeze time. If the remaining budget cannot cover an export on 13 November, it runs after the daily reset, using the identical frozen query.

**Diagnostics.** Post-hoc facet diagnostics are run, clearly labelled. No repaired query replaces a frozen arm.

Request bodies, statuses, responses and UTC timestamps are archived. Headers, the key and publisher abstracts are not. An offline verifier and SHA-256 checksums are provided.
