# Bt maize and non-target animals: frozen multi-source OQL POST transfer test

Branch `opus5.5`, 12 November 2026 (Asia/Singapore). Committed and pushed before any candidate search was executed and before the included-reference list was opened.

## Why this benchmark

The request: a review that screened more than 10,000 records **and searched multiple sources**. Selected: **Meissle, Naranjo & Romeis (2022), *Does the growing of Bt maize change abundance or ecological function of non-target animals compared to the growing of non-GM maize? A systematic review*, Environmental Evidence 11:21, https://doi.org/10.1186/s13750-022-00272-0.**

- **12 bibliographic databases**: Web of Science Core Collection, BIOSIS, Zoological Record, SciELO, CAB Abstracts, Agricola, AGRIS, Scopus, BASE, ProQuest Dissertations & Theses, JSTOR and Google Scholar.
- **Other sources**: specialist searches of regulatory, project, industry and civil-society websites, plus references from reviews and colleagues.
- **12,967 database references after deduplication** were screened, with 110 more from specialist websites and 19 from other sources.
- **166 included articles**, listed with identifier numbers in Additional file 2. Screening 86 reviews contributed 7 additional references.
- The searches ran in December 2014 (all years), with updates in January and August 2019 (last update 23 August 2019).
- **Domain**: agricultural entomology and ecology, outside clinical medicine. The included set has regulatory reports, theses and non-English articles, so it tests whether OpenAlex alone can stand in for a deliberately multi-source search.

### How it was found

A scan of 106 open-access systematic reviews and maps in *Environmental Evidence* (Europe PMC, 2015–2025) extracted reported screening counts. The scan read the methods text only. Candidates were then compared on four things: screening count, number of sources, whether a WoS/Scopus string was published, and whether an included list was available.

Runners-up:

- Tuttle & Donahue (2022) on sediment and corals. It screened 10,221 records, but none of its additional files is a list of included articles.
- The perch seed-dispersal review. Its deduplicated count is uncertain.

Noetel et al. (2024) was left alone, because it is frozen but not executed on `main`.

## Information boundary

Before freezing, I read:

- the article's methods and results counts, including the composition 71/46/49 of the 166;
- Additional file 1 (search strings and specialist-site table);
- the additional-file descriptions.

Additional file 2, which lists the full-text screening decisions and the included references, was downloaded but not opened or parsed. No included title, identifier or OpenAlex result was seen. This is an AI-assisted procedural holdout, not independent blinding, and cannot exclude exposure through model training.

## Frozen searches

`build_queries.py` generates both arms from the Web of Science `TS=` and Scopus `TITLE-ABS-KEY` strings, which are identical in content. Each arm is sent as `POST https://api.openalex.org/` with `{"oql": ...}`.

Shared translation rules:

- **Field.** Title, abstract and keywords map to `title-abstract-keywords`.
- **Bare words** stay bare. OQL stems them, the nearest match to WoS lemmatisation and Scopus plurals.
- **Quoted phrases and `farm-scale`** become `stemmed` adjacent phrases.
- **`Cry*` and `Vip*`** stay wildcards.
- **Structure.** Three OR blocks joined by AND.
- **Date.** Publication date ≤ 2019-08-23.

The arms:

- **A — core corpus.** OpenAlex's default.
- **B — `(all corpora)`.** Identical to A except that it adds the expansion corpus. The only change between A and B is the corpus, so B shows whether OpenAlex's non-core records (more repository, thesis and grey material) help replace the multi-source search.

Departures decided in advance:

1. **Some sources and features are not replicated.** Ovid `.hw` subject headings, BASE/ProQuest/JSTOR/Google Scholar full-text behaviour, the non-target block used only in full-text engines, specialist websites, review screening and contacts are not reproduced.
2. **Keywords are not the same.** OpenAlex keywords are not WoS or Scopus author/indexer keywords.
3. **The date limit is approximate.** A publication-date ceiling only approximates three search dates. Initial searches covered all years, and updates ran from 2014.
4. **Language** is not restricted. The source searched in English and included non-English articles found along the way.

Free `/query` validation (no execution) returned `valid: true` for both arms. Responses are in `validation/`.

## Benchmark construction (after the freeze)

**Denominator.** The denominator is every reference that Additional file 2 marks as included, with an identifier number. It is reconciled against the stated **166**. Any discrepancy is documented entry by entry, and nothing is silently dropped.

**Matching order**:

1. DOI, if the list gives one.
2. NCBI citation matcher or PubMed title search, to obtain a PMID.
3. Crossref bibliographic query.
4. OpenAlex single-entity lookup (free).

**Adjudication.** Fuzzy matches need explicit adjudication with candidates kept. Grey or regulatory documents with no OpenAlex record stay in the denominator as not covered.

**Reporting.** Three figures are reported separately:

- coverage;
- recall among covered references;
- recall against all 166.

**Other breakdowns.** Recall is also broken down by document type and by language, where the list allows it.

## Outcomes

- **Primary recall threshold**: strictly more than 95% of the full denominator. For N = 166 that is **at least 158/166**.
- **Workload comparison**: the API count against **12,967** database references after deduplication. The ratio to 13,096, which adds the specialist and other-source references, is also given. A lower count is a potential screening volume, not a measured saving. No new screening is done.
- Both are reported for both arms, and neither arm is chosen after the fact.

## Execution and evidence

This follows the Walker test on the same branch:

1. **First page**, per arm: one POST giving the count, the executed OQO and the first page (`per_page=100`, `sort=publication_date:asc`, `cursor=*`).
2. **Round trip**: the echoed OQO is posted again, and the count must match.
3. **Cursor continuation**: page 2 by POST.
4. **Membership**: the identical executed OQO, AND restricted to the matched benchmark IDs, in batches of at most 100. The OQO's corpus setting is preserved.
5. **Complete export**: attempted by cursor POST only if the count is ≤ 40,000, a limit set by budget. Otherwise the evidence is labelled restricted membership only.
6. **Post-hoc clause diagnostics** on misses, run only after primary results are saved. No repaired query replaces a frozen arm.

Request bodies, statuses, responses and UTC timestamps are archived. Headers and the API key are not, and abstracts are not redistributed. An offline, standard-library verifier is provided.
