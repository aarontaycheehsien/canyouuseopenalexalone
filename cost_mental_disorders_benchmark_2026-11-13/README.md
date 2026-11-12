# Cost of mental disorders: OQL POST test against a six-database review

**Neither frozen OpenAlex search met the recall target of 136 out of 143 included articles.**

| Arm | Searches | Articles recovered | Records returned |
|---|---|---:|---:|
| A | title and abstract | 104/143 (72.7%) | 33,520 |
| B | title, abstract and OpenAlex keywords | 116/143 (81.1%) | 40,605 |

Both arms returned 2.5–3 times the 13,579 records the authors screened.

**Coverage was not the problem.** 141 of the 143 articles are in OpenAlex; only a Portuguese working paper and a Danish ministry report are missing.

**The published PubMed strategy does worse than either arm.** Re-run in PubMed today, it retrieves only 86 of the 143. Both OpenAlex translations of that same strategy beat it.

**The losses come from the cost-of-illness vocabulary.** Many included studies never use the strategy's cost phrases in their title or abstract, and 45 of the 141 have no abstract in OpenAlex.

Test date: **13 November 2026**. The protocol and queries were [committed and pushed](https://github.com/aarontaycheehsien/canyouuseopenalexalone/commit/d00273f) before any search was executed and before the included references were parsed or matched. One exposure happened before the freeze: the supplement prints the included studies' author–year citations directly after the search strings, and both were displayed together. The queries are a mechanical translation of the published strings; see the [protocol](PROTOCOL.md).

## Benchmark

[Christensen, Lim, Saha et al. (2020), *The cost of mental disorders: a systematic review*](https://doi.org/10.1017/S204579602000075X), Epidemiology and Psychiatric Sciences 29:e142. Open access.

| From the PRISMA flow chart | |
|---|---|
| Database records | 18,820 in total: PubMed 11,201, PsycINFO 2,807, Web of Science 2,610, Embase 2,196, NHS York 6, EconLit 0 |
| Duplicates removed | 5,241 |
| Title and abstract screened | **13,579** |
| Included | **143** articles: 112 from the databases plus 31 from bibliography searching |
| Search period | May–June 2019, publications from 1980 onward |

**Why this review.** I shortlisted it from a Europe PMC scan of 6,456 open-access systematic reviews.

**Two other candidates failed the 10,000-record test** once their PRISMA flow charts were checked. Their abstracts give counts before deduplication:

- Kilich et al. (2020) screened 7,925 unique records.
- Hindi et al. (2024) screened 5,812.

**Limits of the source material.**

- Only the PubMed strings are published. The authors say the other five databases' strings are available on request.
- The supplement does not say which of the 143 articles came from bibliography searching, so recall is reported against all 143.

## Matching: 141 of 143 articles are in OpenAlex

**How articles were matched.**

1. NCBI citation matching, PubMed title search and Crossref, each resolved by free OpenAlex lookups.
2. A broader OpenAlex second pass for seven articles.
3. An audit of every accepted match against the full citation.

**Manual adjudications.** Twelve are documented in `adjudicate.py`. Four are articles that OpenAlex indexes under their original-language titles (German, Spanish), where the review cites an English translation.

**Duplicate and misattributed records.** One article has two OpenAlex records, and either counts as found. One record has a wrong first author in OpenAlex.

**Not in OpenAlex:** a Portuguese university working paper (2003) and a Danish Ministry of Health report (1999).

## Results of the frozen searches

Both arms translate the nine published PubMed searches (cost terms AND a disorder group, NOT animal\*, NOT trial\*) into one OQL string with exact quoted terms. Both were sent as `POST https://api.openalex.org/` with `{"oql": ...}`, dated 1980-01-01 to 2019-06-30.

| Arm | API count | Recovered / 143 | Recovered / 141 in OpenAlex | ≥ 136? | ≤ 13,579? |
|---|---:|---:|---:|---|---|
| [A — title-abstract](queries/A_title_abstract.oql) | 33,520 | 104 (72.7%) | 104 (73.8%) | No | No (2.47×) |
| [B — title-abstract-keywords](queries/B_title_abstract_keywords.oql) | 40,605 | 116 (81.1%) | 116 (82.3%) | No | No (2.99×) |

**OpenAlex keywords help here.** B is A plus the keyword field. It adds 7,085 records and recovers 12 more articles. This is the first test on this branch where keywords made a difference; in the Walker and Bt maize tests they changed nothing.

**Evidence.** Both counts exceeded the frozen 20,000-record export cap, so recovery rests on benchmark-restricted membership of the identical executed query. The archived first two cursor pages back it up.

## Comparison with PubMed (post-hoc)

The published PubMed string, re-run in PubMed on 13 November 2026 and restricted to the 132 benchmark PMIDs, retrieves **86 of 143** ([PubMed re-run](results/pubmed_strategy_rerun.json)).

| Today's PubMed strategy | OpenAlex A | OpenAlex B | Articles |
|---|---|---|---:|
| found | found | found | 77 |
| not found | found | found | 27 |
| not found | not found | found | 9 |
| found | not found | found | 3 |
| found | not found | not found | 6 |
| not found | not found | not found | 21 |

**The OpenAlex translations find articles PubMed's own string misses.** Of the 57 articles today's PubMed string misses, the OpenAlex translations recover 36 (27 by both arms, 9 by B alone). They miss only 6 that PubMed finds.

**This review relied on more than PubMed.** Its 143 articles came from four large databases plus bibliography searching. Several were indexed under non-English titles, or are journal articles without PMIDs (11 have no PMID).

## Why articles are missed (post-hoc)

Each component of the search was run alone, restricted to the 141 articles OpenAlex holds plus the one alternate record ([facet diagnostics](results/facet_diagnostics.json), [per-reference matrix](results/per_reference_retrieval.csv)).

| Facet | Title-abstract | With keywords |
|---|---:|---:|
| Date window | 142 | 142 |
| Has an abstract in OpenAlex | 96 | 96 |
| Cost-of-illness terms (16 phrases) | **108** | **122** |
| Disorder terms (nine groups) | 137 | 137 |
| Excluded by NOT animal\* or NOT trial\* | 2 | 2 |

**The cost-terms facet loses most.** Arm A misses 37 of the articles OpenAlex holds:

- 33 lack the cost-of-illness phrases.
- 2 match the NOT animal\* or NOT trial\* exclusions.
- 2 fail only the disorder terms.

Many cost studies are titled simply "The costs of …" or "Economic consequences of …". These use none of the 16 phrases in the strategy, such as "cost of illness", "economic burden" and "health care cost\*". OpenAlex keywords recover some of them.

**Missing abstracts hurt recall.** Among articles with no abstract in OpenAlex, arm B recovers 39 of 45. Among those with one, it recovers 77 of 96.

## OQL POST execution checks

- Re-posting the echoed OQO gave identical counts for both arms.
- Cursor page 2 kept the same count and contained no IDs from page 1.
- Arm A's recovered set is a subset of B's.

The offline verifier passes all its checks.

## Limitations

- **Only one strategy translated.** The five unpublished database strategies are unavailable, so only the PubMed strategy was translated. Any subject headings or extra terms used elsewhere are missing by necessity.
- **The PubMed re-run is not the original search.** It uses today's PubMed, not the authors' 2019 result set.
- **No precision estimate.** No new screening was done, so precision is not estimated.
- **Membership evidence only.** No complete export was made, because both counts exceeded 20,000.

## Where this fits

| Benchmark | Sources searched | Unique records screened | In OpenAlex | Best frozen OpenAlex recall | Its count |
|---|---|---:|---:|---:|---:|
| [Transgenerational inheritance](../walker_transgenerational_benchmark_2026-11-12/README.md) | PubMed only | 63,754 | 100% | 96.9% | 306,031 |
| [Inclusion and special educational needs](../inclusion_sen_benchmark_2026-11-13/README.md) | 9 databases plus grey literature | 20,183 | 84% | 64.9% | 151,147 |
| [Bt maize and non-target animals](../bt_maize_multisource_benchmark_2026-11-12/README.md) | 12 databases plus specialist sites | 12,967 | 83% | 72.9% | 6,775 |
| **Cost of mental disorders (this test)** | **6 databases plus bibliography search** | **13,579** | **99%** | **81.1%** | **40,605** |

**This is the first multi-source test where coverage is nearly complete.** The shortfall here is search vocabulary, not missing literature.

**The comparison with PubMed is the clearest yet.** The same strategy run in OpenAlex finds more of the review's articles than it does in PubMed. Even so, it doesn't match the union of six databases and snowballing.

## Files and verification

- **Protocol and source:** [Protocol](PROTOCOL.md), [freeze manifest](freeze_manifest.json), [provenance](source_provenance.json), [source strings](source_search_strategy.json), [builder](build_queries.py), [validation](validation/).
- **Benchmark:** [benchmark](results/benchmark_source.json), [matches](results/benchmark_matches.json) (documented adjudications in `adjudicate.py`, which runs offline).
- **Results:** [summary](results/summary.json), [matrix](results/per_reference_retrieval.csv), [PubMed re-run](results/pubmed_strategy_rerun.json), [facet diagnostics](results/facet_diagnostics.json).
- **Raw evidence:** [`archives/`](archives/). Headers, the key and Crossref abstracts are not archived.
- **Live runners:** `match_benchmark.py`, `match_second_pass.py`, `run_test.py`, `diagnose_facets.py`, `pubmed_rerun.py`. `summarise.py` runs offline.

From the repository root:

```bash
python3 cost_mental_disorders_benchmark_2026-11-13/verify.py
```
