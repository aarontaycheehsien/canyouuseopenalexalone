# Motor competence and executive functions: frozen OQL POST test of a six-database review

Branch `opus5.5`, 13 November 2026 (Asia/Singapore). Committed before any candidate search was executed and before the included studies were parsed or viewed.

## Benchmark

**Bao, Wade, Leahy et al. (2024).** *Associations between motor competence and executive functions in children and adolescents: a systematic review and meta-analysis.* Sports Medicine 54:2141–2156. https://doi.org/10.1007/s40279-024-02040-1 (open access, PMC11329584).

| Feature | Detail |
|---|---|
| Unique records screened | **12,117** title and abstract records, after removing 8,381 duplicates from 20,498 identified (methods and results text) |
| Sources | Six databases: PubMed, PsycINFO, Scopus, Ovid MEDLINE, SPORTDiscus and Embase, searched from inception to 27 June 2023. Reference lists of included studies were also checked. |
| Included studies | **44** (37 in the meta-analysis) |
| Domain | Sport and exercise science, and developmental psychology |

## Information boundary

**Inspected before freezing:**
- the methods text;
- Table S1 (search terms);
- the first header row of each supplementary table.

**Not yet opened:** Table S2, which lists the included studies, the article's reference list and the risk-of-bias table. This is an AI-assisted procedural holdout, not independent blinding.

## Frozen searches

Table S1 publishes only three OR-lists of keywords (motor competence, executive functions, population). It gives no field tags and no platform syntax. The authors adapted them per database, using MeSH "where possible", and applied English-language, human and journal limits "where possible".

`build_queries.py` translates the lists mechanically:
- The three blocks are ANDed.
- All terms are searched in **title-abstract-keywords**, the usual default field for untagged searches.
- Single words stay bare (stemmed).
- Multiword terms become stemmed adjacent phrases.
- Wildcard terms stay exact wildcards.
- Publication date is limited to **2023-06-27** or earlier.

Two arms differ only in the authors' stated limits:
- **A — no limits.** Default core corpus.
- **B — English, articles.** A plus `language is English` and `type is article`. Species is not available in OpenAlex.

Free `/query` validation returned `valid: true` for both (`validation/`).

**Departures known in advance:**
1. Unpublished per-database MeSH and thesaurus terms are not reproduced.
2. Very broad single terms (stability, balance, inhibition, cognition, student\*) will match far outside the domain in a multidisciplinary index. They are kept, not repaired.
3. OpenAlex's language and type metadata are not the same as the database limits.

## Benchmark construction, outcomes and evidence

**Denominator.** The 44 included studies listed in Table S2, with full references from the article. Any discrepancy is documented. Matching follows the earlier tests:
- free routes first (NCBI, Crossref, OpenAlex single-entity lookups);
- a paid OpenAlex second pass only for unresolved studies;
- an audit of every accepted match against the full citation.

**Primary recall.** More than 95% of 44, that is **at least 42/44**.

**Workload.** The API count compared with **12,117**. Both outcomes are reported for both arms.

**Execution.**
1. A POST returning the count and first page.
2. An OQO round-trip.
3. Cursor page 2.
4. Restricted membership, in batches of at most 100.
5. A complete cursor export only if a count is **20,000 or less** and the day's remaining budget covers it. Otherwise the export is deferred to after the daily reset, using the identical query.

Post-hoc facet diagnostics are clearly labelled. No repaired query replaces a frozen arm. Request bodies, statuses, responses and UTC timestamps are archived. Headers, the key and publisher abstracts are not. An offline verifier and checksums are provided.
