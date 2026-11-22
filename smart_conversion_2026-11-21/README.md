# Smart conversion of published search strategies (21–22 November 2026)

**Restoring dropped subject headings and adding OpenAlex keywords raised recall in four of the eight mechanically translated reviews. It never cost a study. It reached both success criteria nowhere new.**

The largest gain was in the HIV review: 135 to 163 of 190 studies, at 11,302 records against the authors' 10,281. In the blind holdout, the new arm found 5 more citations than the best frozen arm, at 2.1 times as many records.

## What was tested

The full rules are in [`PROTOCOL.md`](PROTOCOL.md). The protocol was committed and pushed before any query was built (`496be19`), and the queries were frozen before any scoring (`e0a2a03`). Each review's published strategy is converted by the same rules:

- **R1. Base text:** the text of the frozen mechanical translation. All concepts are searched in `title-abstract-keywords`.
- **R2. Inherited text terms:** text terms from every other published database strategy. **This added nothing in any review.** Where several strategies are published, their text was already in the frozen base.
- **R3. Subject headings:**
  - Every published MeSH heading contributes its label and entry terms. An exploded heading also contributes its narrower descriptors, capped at 200 terms per heading.
  - Emtree, APA PsycINFO, ERIC, EBSCO and ProQuest headings are mapped to MeSH by exact label or entry term.
  - Headings with no MeSH equivalent become phrases of their own label: 39 of the 114 headings ([`vocab/mesh_resolved.json`](vocab/mesh_resolved.json)).
- **R4. OpenAlex keywords:** a keyword is added when one of its alternative labels equals a topic term. Searching `title-abstract-keywords` already reaches keywords by their main labels, so only alternative labels can add anything. Amendment 1, made before validation, skips abbreviations: OpenAlex lists unrelated acronyms among alternative labels, so "BP" was matching "blood pressure".
- **R5. Missing-abstract fallback:** works with no abstract need match only the topic concepts. This applies only to Dalgaard, Kettle and Noetel, the only strategies with a design concept.

The builder runs under an audit hook that refuses to open any benchmark results, archives, READMEs or matching files. Each review's restructured base (`queries/*__base_equivalence.oql`) returns exactly its frozen arm's count, which confirms that splitting the query into one condition per concept preserves its meaning.

## Results

Both arms were run on 22 November 2026. Counts differ slightly from the original runs because the OpenAlex index has changed since.

| Review | Frozen base: found @ records | Smart: found @ records | Authors screened |
|---|---:|---:|---:|
| HIV in children (Haw 2025) | 135/190 @ 7,848 | **163/190 @ 11,302** | 10,281 |
| Special educational needs (Dalgaard 2022) | 60/94 @ 149,653 | **67/94 @ 194,952** | 20,183 |
| Precarious employment (Pulford 2022) | 44/50 @ 40,793 | **47/50 @ 84,097** | 12,940 |
| Physical activity in primary care (Kettle 2022) | 40/51 @ 4,539 | 41/51 @ 30,007 | 14,566 |
| Transgenerational inheritance (Walker 2018) | 249/257 @ 304,802 | 249/257 @ 307,461 | 63,754 |
| Motor competence (Bao 2024) | 43/44 @ 11,892 | 43/44 @ 11,911 | 12,117 |
| Bt maize (Meissle 2022) | 121/166 @ 7,131 | 121/166 @ 7,131 | 12,967 |
| Cost of mental disorders (Christensen 2020) | 116/143 @ 40,339 | 116/143 @ 40,339 | 13,579 |

- **Gains come from published headings.** The four reviews that gained are the ones with published subject headings (Haw, Dalgaard, Kettle) or with keyword synonyms for the main concept (Pulford). The other four published no usable headings, and their results barely moved.
- **The record cost varies widely.** Haw's gain of 28 studies took 44% more records. Kettle's single extra study took 6.6 times as many. The split between the missing-abstract branch, which drops the RCT filter, and the added terms was not measured.
- **No study was lost.** In no review did the new arm miss a study that the base found (`results/smart_results.json`, `base_only_ids`).
- **No new pass.** Bao meets both criteria with either arm. Walker meets the recall target but returns 4.8 times the authors' screening load.

### Blind holdout: exercise for depression (Noetel et al. 2024)

The rules and all three queries were frozen and pushed before the 218-citation list was opened (`80d5ec2` holds the counts recorded before it was opened).

- **Coverage:** 192 citations match OpenAlex works: 186 automatically and 6 after adjudication ([`results/noetel_adjudication.json`](results/noetel_adjudication.json)). That is 88.1% coverage, so the protocol's target of 208/218 is impossible for any search.

| Arm | Found @ records | Authors screened |
|---|---:|---:|
| A, fuller source concepts (frozen 12 Nov) | 181/218 @ 75,760 | 13,115 |
| B, compact three concepts (frozen 12 Nov) | 174/218 @ 40,144 | 13,115 |
| Smart conversion | 186/218 @ 158,416 | 13,115 |

On the review nobody had inspected, the new arm recovers 186 of the 192 citations that OpenAlex holds (96.9%). Arm A recovers 181 (94.3%). The new arm costs twice A's records, and every arm returns 3 to 12 times the authors' screening load.

## Limits

- **Post hoc for the eight.** Their misses were known when the rules were written, and the rules' author had read some of the diagnoses. The safeguards are procedural: generic rules, a transcription of every published heading, the audit hook, and freezing before scoring. Only Noetel is blind.
- **MeSH stands in for other thesauri.** Emtree and the other thesauri are not public, so mapping their headings to MeSH approximates them. About a third of headings had no MeSH equivalent and are searched only as their label phrase.
- **Text search is not indexing.** Subject headings become text: a work is found only if its title, abstract or keywords use the heading's words. Human indexing is not reproduced.
- **A single run.** Each figure comes from one OpenAlex snapshot, and counts drift as the index changes.

## Files

- `PROTOCOL.md`: rules and Amendment 1.
- `specs.py`: each review's transcribed concepts and headings.
- `build.py`, `oqlsplit.py`, `terms.py`: the offline builder.
- `fetch_mesh.py`, `fetch_keywords.py`, `validate.py`: network steps (`netlib.py` archives every response).
- `queries/`: frozen queries, `caps.json`, `build_report.json`, `validation_report.json`.
- `vocab/`: MeSH resolution and keyword matches.
- `run.py`: the eight benchmarks.
- `noetel_run.py`, `noetel_match.py`: the holdout.
- `freeze_manifest.json`: hashes at the freeze.
- `verify.py`: offline verifier. `python3 smart_conversion_2026-11-21/verify.py` passes 309/309 checks.
