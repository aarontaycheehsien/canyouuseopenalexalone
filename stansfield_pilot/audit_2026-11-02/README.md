# Stansfield benchmark audit, 2 November 2026

All eight strategies were tested against the 130 known OpenAlex-indexed records in the authors’ diabetic eye screening benchmark. Adding `unscreen*` to the screening terms and removing G2’s topic fallback retrieved all 130 in 3,892 results. Corrected G2 retrieved the same 130 in 5,764 results. The 1,872-record difference measures result volume. The alternative was developed after inspecting a known miss and has only been evaluated on this benchmark.

| Strategy | Total results | Original indexed records | Expanded indexed records |
|---|---:|---:|---:|
| D, one-sided proximity | 3,103 | 112/128 | 114/130 |
| E, misplaced topic clause | 3,701 | 124/128 | 126/130 |
| E, corrected topic clause | 5,574 | 125/128 | 127/130 |
| G1, broad unknown-country exception | 12,985 | 128/128 | 130/130 |
| G2, misplaced topic clause | 3,891 | 127/128 | 129/130 |
| G2, corrected | 5,764 | 128/128 | 130/130 |
| G2, tighter distances | 5,734 | 128/128 | 130/130 |
| Add `unscreen*`, omit topic fallback | 3,892 | 128/128 | 130/130 |

## How to inspect the evidence

1. Compare the [eight complete OQL queries](queries/) with the [recall summary](results/recall_summary.csv) and [per-study matrix](results/per_study_retrieval.csv). The matrix includes the three original records outside the fixed 130-ID set. D and corrected G2 come verbatim from the draft. Other variants use the modifications described in it. The complete A–C queries were unavailable.
2. Inspect the [verified IDs](benchmark/benchmark_130_verified_ids.txt) and [identifier corrections](benchmark/id_corrections.json). The verified set equals the 130 current IDs in the branch’s [earlier benchmark](../reference_retrieval.csv). The deposited spreadsheet uses an obsolete ID for Lindenmeyer (2014) and has three pairs of transposed IDs. The audit retains both the deposited and verified mappings.
3. Run `python3 verify.py` from this directory. It needs only Python’s standard library. It checks the evidence hashes, reconstructs recall from API-returned IDs, compares the results with the matrix, and intersects unrestricted result pages with the benchmark.
4. For the exact requests and responses, open the [two original archives](archives/). The full-benchmark archive contains the authors’ workbook, UTC timestamps, unrestricted totals, benchmark-restricted responses, and twenty pages from the exploratory query. The first audit contains the clause-level Felfeli tests, validator response and publisher checks. The [original scripts](original_scripts/) preserve the run procedures. For a live replay, submit the OQL files to the OpenAlex API. Live index counts may change.

## What the comparison establishes

Felfeli (2023) was the one study missed by the 3,891-result variant. Its title contains “unscreened”. The archived record-level tests show it passed the diabetic/retinopathy proximity condition and failed the screening-term block, including `screen*`. The 3,892-result variant recovered it using `unscreen*`. The misplaced topic clause validated as text and returned zero works alone.

The unrestricted download returned 3,892 rows across twenty numbered pages and 3,891 distinct IDs. One non-benchmark ID appeared twice. All 130 benchmark IDs were present in the downloaded rows, confirming the membership result for this variant independently of the benchmark-restricted query. The export should not be described as 3,892 distinct downloaded IDs. [Intersection check](results/unrestricted_intersection_check.json)

The authors’ spreadsheet contains 131 original records and two additional eligible studies. Of those 133, 130 have OpenAlex IDs. Recovery of every indexed benchmark record represents 128/131 of the original set and 130/133 of the expanded set, both 97.7%. Further eligible studies may exist among unscreened results. The public interactive map contains one additional reference, Larizza (2013), compared with the deposited sheet. The audit used the deposited sheet to reproduce the published benchmark. [Authors’ workbook](https://osf.io/2nrzy/) · [Stansfield et al.](https://doi.org/10.1002/cesm.70038) · [Interactive map](https://eppi.ioe.ac.uk/cms/Portals/35/Maps/TaSP.html)
