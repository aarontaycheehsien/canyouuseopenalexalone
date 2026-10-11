# Experimental legacy union with proximity and wildcards

Source: `legacy_union_normalized.oql` on `main`, reflecting the nine published OpenAlex search branches. This is a **new, unexecuted strategy**, not a replacement for existing data or results.

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

The generated expression passed *static structural checks only*: exactly nine branches, two date bounds per branch, keyword branches unmodified. It has **not been parsed, validated, or executed by OpenAlex**. The large expression may trigger an OQL expansion/complexity limit or a server timeout.

Before measuring retrieval, POST the query to `https://api.openalex.org/query` (body `{"oql":"..."}`) and examine `validation` / OQO. Then POST the same query to `https://api.openalex.org/` with `{"oql":"...", "cursor":"*", "per_page":200}` and follow the continuation cursor until complete. Compare membership, total unique records, recovered references, and recall-at-rank with the original frozen legacy union using the same ordering policy. Preserve raw requests and errors.

Documentation: https://help.openalex.org/access/oql-spec/ and https://help.openalex.org/api/oql/.
