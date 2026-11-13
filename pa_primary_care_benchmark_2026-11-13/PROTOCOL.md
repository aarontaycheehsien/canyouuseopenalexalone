# Physical activity interventions in primary care: frozen OQL POST test of a multi-database review

Branch `opus5.5`, 13 November 2026 (Asia/Singapore). Committed before any candidate search was executed and before the included-studies tables or reference list were parsed or matched.

## Benchmark

**Kettle, Madigan, Coombe, Graham, Thomas et al. (2022).** *Effectiveness of physical activity interventions delivered or prompted by health professionals in primary care settings: systematic review and meta-analysis of randomised controlled trials.* BMJ 376:e068465. https://doi.org/10.1136/bmj-2021-068465 (open access, PMC8864760).

| Feature | Detail |
|---|---|
| Unique records screened | **14,566** titles and abstracts after deduplication (25,170 identified) |
| Sources | MEDLINE, Embase, PsycINFO, CINAHL, SPORTDiscus, Sports Medicine and Education Index, ASSIA, PEDro, Bibliomap, SCI-E, CPCI-S and OpenGrey, plus CENTRAL, ClinicalTrials.gov and TRoPHI. Searches 9–21 September 2020, with a PubMed update to 1 April 2021. |
| Full texts | 405 |
| Included | **61 reports of 51 studies** (46 meta-analysed) |
| Domain | Primary care and behavioural medicine |

Selected from the follow-up candidate list on this branch (10,000 or more unique records, more than one source).

## Information boundary

**Inspected before freezing:**
- the methods text and the first results paragraph (PRISMA counts);
- the MEDLINE strategy in the web appendix (lines 1–46).

**Incidental exposure, recorded honestly.** Table 1 is embedded in the "Study selection" section, so the extraction of that section printed its first six rows: Aittasalo (2006), Alonso-Dominguez (2019), Apinaniz (2019), Arija (2018), Carroll (2010) and Cheng (2018). No other included study, and no OpenAlex record of any, was viewed. Supplementary Table 1 (intervention details) was not opened.

The frozen queries are a mechanical translation of the MEDLINE strategy. This is an AI-assisted procedural holdout, not independent blinding.

## Frozen searches

The MEDLINE strategy is (physical-activity lines 1–21) AND (primary-care lines 23–38) AND (RCT filter lines 41–44). `build_queries.py` translates it with the Ovid rules used earlier on this branch:

- **Fields:** only `.ti,ab.` lines are translated. Subject-heading lines (2, 24, 28, 31, 34, 38) and the publication-type line (42) are omitted because OpenAlex has no equivalent.
- **Terms:** Ovid does not stem, so every term is an exact quoted string, and multiword terms are exact phrases. `*` is kept, and Ovid's optional `?` (`randomi?ed`) becomes a mid-word `*`.
- **Proximity:** `adjN` becomes `within N−1 words of each other` (OpenAlex's published rule for Ovid). OR groups are expanded into pairs.
- **One substitution:** OQL refuses a proximity with two wildcards unless each has at least four leading characters. In `physical* adj3 fit*` only, `physical*` becomes "physical" and "physically".
- **Field:** `title-abstract`.
- **Date:** no lower limit; publication date on or before **2021-04-01**, the end of the final PubMed update.
- **Scope:** default core corpus, with no language or type limit.

| Arm | Field |
|---|---|
| **A** | `title-abstract` (= `.ti,ab.`) |
| **B** | `title-abstract-keywords` |

The free `/query` validation returned `valid: true` for both (`validation/`).

**Departures known in advance:**
1. MeSH and the RCT publication type are not reproduced.
2. The other eleven databases, three trial registers and their adapted strategies are not reproduced, nor is SCI-E's date limit.
3. Grey literature and registry records need not be in OpenAlex.

## Benchmark construction, outcomes and evidence

**Denominator.** The 51 included studies in Tables 1 and 2, with every report cited for each study.

**Unit:** the study. A study counts as recovered if any of its cited reports is retrieved. Report-level recall over the cited reports is reported as a secondary outcome.

**Matching** follows the earlier tests:
1. Free routes first: NCBI citation matching, Crossref, and OpenAlex single-entity lookups.
2. A paid OpenAlex second pass, only for unresolved reports.
3. An audit of every accepted match against its full citation.

**Primary recall threshold:** strictly more than 95% of 51 studies, that is **at least 49/51**.

**Workload:** each arm's API count is compared with **14,566**. Both outcomes are reported for both arms.

**Execution** follows the earlier tests:
1. POST the count and the first page.
2. Round-trip the echoed OQO.
3. Fetch cursor page 2.
4. Check restricted membership, in batches of at most 100.
5. Make a complete cursor export only for counts of **20,000 or fewer**, and only if the daily budget allows; otherwise membership is the evidence.

Post-hoc facet diagnostics are labelled as such. Request bodies, statuses, responses and UTC timestamps are archived, but headers, the key and publisher abstracts are not. An offline verifier and checksums are provided.
