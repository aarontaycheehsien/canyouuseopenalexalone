# Smart-conversion arm: frozen protocol

Written 21 November 2026, before any smart-conversion query was built, counted or scored.

## What this arm is

A rule-based conversion of each review's **published** search strategies into OQL that restores what the mechanical translations dropped:

1. subject headings (MeSH, and Emtree and other thesauri mapped to MeSH),
2. text terms from every published database strategy, not just the one translated,
3. OpenAlex keywords reached through their own alternative labels,
4. a fallback for works without an abstract.

It is applied to the eight benchmarks whose frozen arms were mechanical translations:

- Walker 2018
- Dalgaard 2022 (special educational needs)
- Meissle 2022 (Bt maize)
- Christensen 2020 (cost of mental disorders)
- Bao 2024 (motor competence)
- Pulford 2022 (precarious employment)
- Haw 2025 (HIV in children)
- Kettle 2022 (physical activity in primary care)

It is also applied to one holdout, Noetel et al. (2024), whose citation list has never been opened.

## Blinding: what is and is not possible

**The eight existing benchmarks are not blind.** Each one's frozen arms were scored before this protocol was written, and its READMEs record which included studies were missed and why. The author of these rules has read some of those diagnoses. For these eight, the arm is therefore **post hoc**, like `adapted_proximity_wildcard_2026-11-13`.

The safeguards are procedural:

- The rules below are generic and identical for every review. No rule names a review, a study or a term chosen because of a miss.
- Each review's concept specification (`specs.py`) is a transcription of its published strategy. Every subject heading and text line it publishes is included; nothing is selected.
- The builder runs under a Python audit hook. It fails if it opens any repository file other than:
  - the published-strategy source files,
  - the frozen query files,
  - this folder.

  It cannot read `results/`, `archives/`, `validation/`, READMEs or matching files.
- Queries, vocabulary snapshots and hashes are committed and pushed before any arm is scored.
- The original frozen arms remain the primary results for all eight.

**Noetel et al. (2024) is the blind test.** Its included-citation file (`references.csv`, SHA-256 `602594f3…5e47c2`) has been downloaded and hash-checked but not opened. It will not be opened until this arm and Noetel's two originally frozen arms (A and B, never executed) are frozen and pushed. The existing Noetel files are not edited; this protocol is an amendment that adds a third arm.

## Rules

**R1. Base text.** Each concept starts from the frozen translation's text for that concept, unchanged:

| Review | Base arm |
|---|---|
| Walker | B |
| Dalgaard | C |
| Meissle | B |
| Christensen | B |
| Bao | A |
| Pulford | B |
| Haw | B |
| Kettle | B |
| Noetel | A |

Where several arms exist, the base is the least restrictive one: for example, all corpora, no language limit, or the union of database cores. Every concept is searched in `title-abstract-keywords`, OpenAlex's nearest equivalent to title, abstract and indexing fields. Date and corpus limits are the base arm's own.

**R2. Inherited text.** Any text term from another published database strategy for the same concept is added if it is not already in the base. Conversion follows the frozen builders' existing rules:

- A single word without a wildcard stays bare, so OQL stems it.
- Quoted or truncated terms become exact quoted terms.
- `adjN`, `NEAR/N` and `N5` become proximity "within N words of each other".

**R3. Subject headings.** Every published heading line contributes terms:

- **MeSH:** the descriptor's label and all its entry terms. For exploded headings (`exp`, `/exp`, `explode all trees`, PubMed `[MeSH Terms]`, which explodes by default), the narrower descriptors' labels and entry terms are added too.
- **Emtree, APA PsycINFO, ERIC, EBSCO and ProQuest subject headings:** these thesauri are not public, so each heading is mapped to MeSH:
  1. a MeSH descriptor whose label matches exactly (ignoring case),
  2. otherwise, a MeSH entry term that matches exactly, taken to its descriptor,
  3. otherwise, no mapping.

  A mapped heading is treated as MeSH, keeping its own explode flag. An unmapped heading becomes a stemmed phrase of its label, with any parenthetical qualifier removed.
- **Publication types** (for example `randomized controlled trial.pt.`) are looked up as MeSH publication-type descriptors and converted the same way.
- **Unreproducible lines** are dropped and listed in `specs.py`: register codes such as CENTRAL's `SR-DEPRESSN`, and unpublished strategies.

**Term form.** An inverted term "A, B" becomes "B A". Multi-word terms become stemmed phrases. All-capital abbreviations and terms with digits become exact quoted words, so that "AIDS" is not stemmed to "aid". Other single words stay bare. Punctuation other than hyphens and apostrophes becomes a space. Duplicates are removed.

**Cap.** If one exploded heading yields more than 200 distinct terms, narrower descriptors are added one tree level at a time, stopping at the deepest level that stays within 200. The level used is recorded.

**R4. OpenAlex keywords.** A text search with `title-abstract-keywords` already finds every work carrying a keyword whose label is one of the search terms. A test on 21 November 2026 showed this: the "physical activity" keyword (`keywords/exercise`) adds 0 works to `title-abstract-keywords has (stemmed "physical activity")`. Keyword IDs therefore add works only through a keyword's alternative labels.

The rule:

- For every non-wildcard term of a **topic** concept, search the OpenAlex keyword list (`/keywords?search=`, 25 results). Keyword records carry no work titles.
- Add a keyword when one of its alternative labels equals the term, comparing lower-cased, Porter-stemmed words, but its display name does not.
- Design and method concepts get no keywords.
- Every lookup response is archived.

**R5. Missing-abstract fallback.** Where a strategy has a design or method concept (an RCT filter, or trial or effect terms):

- Works with an abstract must match every concept.
- Works without an abstract must match every topic concept, and the design concept is waived.

This applies to Dalgaard, Kettle and Noetel. Elsewhere there is no design concept, so R5 changes nothing.

**R6. Exclusions** (`NOT`, as in Christensen) are kept unchanged and apply to both branches of R5.

## Size and validity

Each query is checked with OpenAlex's free OQL validation. If one is refused for size or estimated time, the following reductions are applied in order until it is accepted, and each step is recorded:

1. Lower the explosion cap uniformly across all headings in that query: first 100 terms, then 50, then descriptor and entry terms only.
2. Drop R4's keyword clauses.

Count requests are allowed during building. Benchmark membership is not.

**Equivalence check.** The builder also renders each review's base without R2–R5. Its count must equal the live count of the frozen base arm, which confirms that R1's restructuring into one condition per concept preserves meaning.

## Measurement

The existing benchmarks are scored exactly as their frozen arms were: an unrestricted count, then membership restricted to the verified benchmark IDs in batches of at most 100. Each is scored in its own unit (studies or references).

Noetel's arms A, B and the new arm are scored as its 12 November protocol specifies:

- the primary threshold is more than 95% of the 218 supplied citations (208 of 218),
- matching is done by DOI, then PMID, then title, author and year, with adjudication.

The success criteria are the repository's existing ones: recall above 95%, and a count no larger than the authors' screening load.

No query is revised after scoring. Diagnostics of misses may follow, labelled as such.

## Amendments made before the freeze

### Amendment 1 (22 November 2026, 00:20 UTC): no keyword lookups for abbreviations

**When and on what evidence.** This was decided after the R4 keyword lookups were archived and before any query was validated, counted or scored. It rests only on the keyword records, which contain no work titles and no benchmark information.

**The problem.** OpenAlex lists acronyms among keywords' alternative labels. Applied to abbreviations, R4 therefore added unrelated keywords:

- "BP" matched blood pressure, black phosphorus and backpropagation (Christensen),
- "GAD" matched glutamic acid decarboxylase (Christensen),
- "gp" matched globus pallidus (Kettle),
- "ccg" matched chemically converted graphene (Kettle).

These came to 88 keyword matches in Christensen's mental-disorders concept and 59 in Kettle's primary-care concept.

**The change.** R4 skips all-capital terms and single words of five characters or fewer. This is consistent with R3, which already treats abbreviations as exact words. The abbreviations themselves remain text search terms.

**Effect.** The matches fall to 3 and 13 in those two concepts. Matches elsewhere are mostly unchanged, for example "marijuana" to "cannabis" and "insecure employment" to "precarious employment".
