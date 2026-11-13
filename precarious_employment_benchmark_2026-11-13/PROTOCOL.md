# Precarious employment and health: frozen OQL POST test of a nine-database review

Branch `opus5.5`, 13 November 2026 (Asia/Singapore). Committed before any candidate search was executed and before the included studies were parsed or matched.

## Benchmark

**Pulford, Thapa, Thomson et al. (2022).** *Does persistent precarious employment affect health outcomes among working age adults? A systematic review and meta-analysis.* J Epidemiol Community Health 76:909–917. https://doi.org/10.1136/jech-2022-219292 (open access, PMC9554022).

| Feature | Detail |
|---|---|
| Unique records screened | **12,940**, title and abstract, after deduplication (article text) |
| Sources | Nine databases searched up to March 2019: MEDLINE, Embase, ASSIA, Scopus, IBSS, PsycINFO, EconLit, SocINDEX and Sociological Abstracts. Grey literature from a wider scoping review was also considered. |
| Included studies | **50**, reflecting 46 datasets; 29 meta-analysed |
| Domain | Social epidemiology and labour economics, with health and social-science databases |

Selected from a full-text check of 300 open-access reviews whose abstracts report 10,000 or more records.

## Information boundary

**Inspected before freezing:**
- the methods and results text;
- Figure S2.1, the Scopus strategy, on pages 1–2 of Additional file 1.

**Incidental exposure, recorded honestly.** The included-studies table (Table S2.1) begins on the page after the strategy. The text extraction printed its first two rows: Kivimäki (2003, 10-Town Study) and Emerson (2018, 1970 British Cohort Study). No other included study, and no OpenAlex record of any, was viewed.

The frozen queries are a mechanical translation of Figure S2.1. This is an AI-assisted procedural holdout, not independent blinding.

## Frozen searches

Only the Scopus string is published. It combines a block of 38 precarious-employment terms with a block of 15 health terms, all in `TITLE-ABS`. The methods say the health terms "were included in searches of non-health databases". That implies the health databases (MEDLINE, Embase, PsycINFO) ran the employment block alone.

`build_queries.py` translates the string mechanically. Scopus lemmatises unquoted words and loose phrases, so:
- **Words:** an unquoted word stays bare, which OQL stems.
- **Phrases:** a quoted phrase becomes a stemmed adjacent phrase.
- **Wildcards:** a truncated term becomes an exact wildcard. Mid-word wildcards such as `labo*r` and `hospitali*ation` are supported.
- **Field:** `title-abstract`.
- **Date:** publication date on or before **2019-03-31**. No start year was stated.
- **Scope:** the default core corpus, with no language or type limit.

The two arms differ only in the health block:

| Arm | Search | Mirrors the authors' search in |
|---|---|---|
| **A — Scopus string exactly** | Employment block AND health block | The non-health databases |
| **B — employment block only** | Employment block alone | The health databases |

**B is a superset of A.** The free `/query` validation returned `valid: true` for both (`validation/`).

**Departures known in advance:**
1. The other eight databases' strategies are unpublished, so any subject headings they used are not reproduced.
2. Grey literature from the scoping review is not searched.
3. The date ceiling approximates the March 2019 search date.

## Benchmark construction, outcomes and evidence

**Denominator.** The 50 included studies in Table S2.1, with full references from the article and supplement. Any discrepancy, such as several studies sharing a dataset, is documented, and the study remains the unit.

**Matching** follows the earlier tests:
1. Free routes first: NCBI citation matching, Crossref, and OpenAlex single-entity lookups.
2. A paid OpenAlex second pass, only for unresolved studies.
3. An audit of every accepted match against its full citation.

**Primary recall threshold:** strictly more than 95% of 50, that is **at least 48/50**.

**Workload:** each arm's API count is compared with **12,940**. Both outcomes are reported for both arms.

**Execution** follows the earlier tests:
1. POST the count and the first page.
2. Round-trip the echoed OQO.
3. Fetch cursor page 2.
4. Check restricted membership, in batches of at most 100.
5. Make a complete cursor export only for counts of **20,000 or fewer**.

Post-hoc facet diagnostics are labelled as such. Request bodies, statuses, responses and UTC timestamps are archived, but headers, the key and publisher abstracts are not. An offline verifier and checksums are provided.
