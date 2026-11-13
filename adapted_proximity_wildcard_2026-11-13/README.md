# Truncation and proximity applied to all eight benchmarks (post hoc)

**Blanket truncation and proximity raised recall in three of the six reviews that fell short, but by much in only one, and usually at a large cost in records.**

The one clear win was the HIV review: 135 → 154 of 190 studies, at 10,122 records against the authors' 10,281. Elsewhere the same rules added 0–3 studies while doubling or tripling the count, and lost a study in two arms.

**This is post hoc.** The rules were written on 13 November 2026, after every benchmark's misses had been seen. They are generic and identical for every benchmark; nothing is tuned to a study. The frozen arms remain the primary results.

## The rules (`adapt.py`)

Applied only inside search blocks:

- **Truncation (T):** a single word without a wildcard is cut to the common prefix of the word and its Porter stem, plus `*`, if that prefix has at least five letters. For example, `child` → `"child*"`, `temporary` → `"temporar*"`, `employment` → `"employ*"`.
- **Proximity (P):** a two-word phrase without a wildcard becomes a proximity pair of its truncated words, `within 2 words of each other`, so word order and one intervening word are allowed.
- **Existing proximity groups:** their single words are truncated, and all operands are quoted. Where OQL's two-wildcard limit would be broken (each `*` needs four leading characters), the truncated operands revert to exact words.

Nothing else changes: existing wildcards, operators, dates and filters stay as frozen.

## Results (`results/adapted_results.json`)

Recall is in each benchmark's own unit. The frozen figures were re-scored from archived IDs and match the published summaries.

| Benchmark (target) | Arm | Frozen: recovered @ records | Adapted: recovered @ records |
|---|---|---:|---:|
| HIV in children (181/190) | A title-abstract | 134 @ 7,750 | **154 @ 10,122** |
| | B + keywords | 135 @ 7,897 | **154 @ 10,122** |
| Precarious employment (48/50) | A with health block | 38 @ 8,140 | 41 @ 22,468 |
| | B employment only | 44 @ 42,085 | 47 @ 128,285 |
| Cost of mental disorders (136/143) | A title-abstract | 104 @ 33,520 | 107 @ 58,129 |
| | B + keywords | 116 @ 40,605 | 115 @ 62,928 |
| Transgenerational (245/257) | A | 249 @ 306,031 | 250 @ 688,639 |
| | B | 249 @ 309,758 | 250 @ 691,184 |
| Motor competence (42/44) | A no limits | 43 @ 12,012 | 42 @ 35,650 |
| | B English articles | 43 @ 7,807 | 42 @ 22,562 |
| Bt maize (158/166) | A core | 121 @ 6,775 | 121 @ 7,281 |
| | B all corpora | 121 @ 7,053 | 121 @ 7,582 |
| Physical activity (49/51 studies) | A | 39 @ 4,414 | 39 @ 5,252 |
| | B | 40 @ 4,543 | 40 @ 5,343 |
| Special educational needs (90/94) | A, B, C | 34, 22, 61 | unchanged: already truncated with proximity |

## What it shows

- **Truncation helps where a bare word hides plurals.** The HIV gain is almost entirely `child` → `child*` (it matches the earlier single-change test, 154). Across the other reviews, blanket truncation mostly adds noise: Walker's count more than doubles for one extra reference.
- **The special-needs strategy was already truncated throughout, with proximity, and still reached only 61/94.** Truncation cannot fix studies that are absent from OpenAlex or lack the concept words.
- **Proximity appears not to reach OpenAlex keywords.** Both lost studies (W2910009840 in the motor-competence review, W2170631082 in the cost-of-illness review) matched the frozen arm only through the keywords field, where a stemmed phrase matched a keyword. Their proximity versions did not. Keep phrases as phrases when searching `title-abstract-keywords`, or add the proximity pair alongside the phrase rather than in place of it.
- **No adapted arm meets both criteria that its frozen arm missed.** Precarious employment B comes closest on recall, 47/50, but at 9.9 times the authors' screening load.

**Takeaway:** truncation and proximity should be applied selectively, to the words that need them. Blanket application raises the count far faster than recall.

## Files

- `adapt.py`: rules and query generation; `queries/` holds the adapted OQL and `plan.json`.
- `run_adapted.py`: free validation, count and restricted membership; `archives/` holds request bodies, statuses, responses and UTC times (no headers or key).
- `archives/diagnose/`: the two loss diagnostics.
