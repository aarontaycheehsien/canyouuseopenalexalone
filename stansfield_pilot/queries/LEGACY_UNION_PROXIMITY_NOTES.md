# Experimental legacy union with proximity and wildcards

Source: `legacy_union_normalized.oql`, reflecting the nine published OpenAlex search branches. This is an **experimental strategy with an incomplete archived run**. Existing baseline data and conclusions remain in place; this archive does not establish a validated replacement strategy.

## Archived execution and interpretation

The saved run on **11 October 2026 (UTC)** executed the nine branches separately. Branches 4, 5, 7 and 8 completed. The original runner stopped branches 1, 2, 3 and 6 on duplicate IDs during pagination; branch 9 stopped when API credits were exhausted. The complete union was therefore withheld.

The offline partial union contains **10,079 unique works**: 4,900 overlap the original 23,217-work legacy set and 5,179 are additional IDs. It recovered **102/131 primary references (77.9%)** and **104/133 expanded references (78.2%)**, all already recovered by the legacy strategy. These are lower bounds from incomplete retrieval. The legacy strategy recovered 126/131 and 128/133, respectively. These observations do not establish final recall, improved precision, or reduced screening effort.

See [branch outcomes](../legacy_union_proximity_run/branches_summary.json), [final run status](../legacy_union_proximity_run/final_summary.json), and [partial union summary](../legacy_union_proximity_run/partial_merge_summary.json). Historical artifacts are preserved as recorded, including the original anonymous-run manifest. The later authenticated workflow attempt failed because the repository API-key secret was missing; it made no requests. The revised runner has offline regression coverage, but no completed authenticated live run is archived here.

## Structural changes

- **Nine OR branches retained**, all with publication years 2003–2023.
- **Branches 1–6:** retain their original geographical/full-text/title-and-abstract/author-country restrictions. Replace the shared, broad `diabetic AND eye AND screening` topic blocks with a proximity-and-wildcard topic:
  - `"diabet*"` AND `within 5 (eye term, screening term)`; OR
  - `"diabet*"` AND `within 3 ("diabet*", eye term)` AND at least one screening/intervention term somewhere in the same searched title-and-abstract field.
- **Branches 7 and 8:** unchanged, since OpenAlex keyword identifiers cannot be given proximity operators. Their contribution to the union is retained.
- **Branch 9:** retains all original programme-name alternatives and additionally ORs variants using `"retinascreen*"`, `"DES program*"`, `"Diabetic eye screening program*"`, and `"teleophthalmology screening program*"`.

The shared eye-term set has 7 entries: `eye`, `eyes`, `retina*`, `retinopath*`, `macula*`, `maculopath*`, `vision`.

The main screening-term set has 8 entries: `screen*`, `diagnos*`, `detect*`, `test*`, `program*`, `exam*`, `monitor*`, `care`.

Each of the 6 revised topic branches contains 56 `within 5` pairs and 7 `within 3` pairs, for **378 proximity expressions** in the union. All wildcard operands are quoted.

## Caveats

This alters both wildcard handling and proximity, so it does **not isolate** the effect of proximity alone. It does not promise a subset of the legacy set, because wildcards can broaden vocabulary. The first branch retains an original full-text **geography** restriction, not full-text topic searching.

Static structural checks found exactly nine branches, two date bounds per branch, and unchanged keyword branches. The archived execution subsequently returned results for each separate branch. This does not validate complete enumeration, the combined nine-branch expression as a single API request, or ranking. The full expression may still trigger an OQL expansion/complexity limit or a server timeout.

Before promoting this strategy, complete an authenticated enumeration and compare membership, unique totals and recovered references with the original frozen legacy union. Examine validation / OQO when validating the full expression. The saved unions are sorted by work ID; they are not ranked retrieval sequences and cannot support recall-at-rank comparisons. Such comparisons require separately preserved and validated ordering. Current request logs retain status, timing and cost metadata, not full response bodies.

## Running the tools

- Run `python -m unittest -v test_legacy_proximity` for offline regression and archive consistency checks. Tests use temporary copies and make no API requests.
- Live retrieval requires `OPENALEX_API_KEY` in the environment. Run `python run_legacy_proximity_union.py` in a separate checkout when preserving an earlier run: it replaces the designated output folder's branch and derived results. Incomplete runs save their audit and observed IDs, including empty partial lists, and exit with status 1. Completed runs exit with status 0. Duplicate positions are audited and deduplicated; each completed branch must still enumerate the API-reported unique count.
- Run `python merge_partial_legacy_proximity.py` to rebuild an observed union without API requests. It checks all nine distinct branches, query hashes, ID validity, duplicates and saved counts before writing results. Failed validation removes earlier partial union products. Its historical `partial_*` filenames remain; the summary status and failure count distinguish incomplete from complete inputs.
- GitHub retrieval and offline merge workflows run only by manual dispatch on a non-default branch and commit results to that selected branch. The live workflow requires the repository `OPENALEX_API_KEY` secret; a missing secret does not upload an old archive as a new result. Only offline tests run automatically on pull requests and the main/experiment branches. No live search is needed to merge this archive.

Documentation: https://help.openalex.org/access/oql-spec/ and https://help.openalex.org/api/oql/.
