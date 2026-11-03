# Follow-up checks, 3 November 2026

Two live checks made while fact-checking the [revised Substack draft](../substack/openalex-evidence-synthesis.md). Both were run through the OpenAlex MCP `search_works` tool (OQL, preview mode, retracted works included). Recall was measured by restricting each query to the [130 verified benchmark IDs](../audit_2026-11-02/benchmark/benchmark_130_verified_ids.txt), which are the same IDs as in `../reference_retrieval.csv`. Only counts were recorded; raw responses were not archived.

| Query | Proximity distances | Results | Benchmark records found |
|---|---|---:|---:|
| [`final_exact.oql`](queries/final_exact.oql) (copy of the audit's `exploratory_unscreen_no_topic.oql`) | within 4 / within 6 | 3,892 | 130/130 |
| [`final_strict_adj.oql`](queries/final_strict_adj.oql) | within 3 / within 5 | 3,857 | 130/130 |

- **Re-run:** the first row reproduces the 2 November audit result.
- **Stricter distances:** the second row follows OpenAlex's own rule for translating Ovid searches, which maps `adjN` to `within N−1` ([search strategies from other databases](https://help.openalex.org/how-to/search-strategies-from-other-databases/)). The only difference from the first query is the eight proximity distances.

## Context

- **Screening load depends on the shortened term lists.** A fuller translation of the same Embase strategy (Table 8) retrieved 11,257 works and 127/130 benchmark records ([Table 8 translation](../queries/embase_table8_oql_2026/README.md)).
- **The numbered pages contained a duplicate.** The API reported 3,892 matches. The export contained 3,892 rows but only 3,891 distinct IDs. The duplicate was outside the benchmark, and all 130 benchmark IDs appeared in the export. The counts alone do not identify an omitted work or establish that the result set stayed fixed between page requests. [Intersection check](../audit_2026-11-02/results/unrestricted_intersection_check.json). In the [earlier cursor study](../cursor_study_2026-10-04/CURSOR_ORDER_REPORT.md), cursor walks returned as many unique IDs as the API reported for the queries tested.
