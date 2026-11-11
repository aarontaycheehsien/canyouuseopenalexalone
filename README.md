# OpenAlex evidence synthesis experiments

The reports on this branch use the Stansfield diabetic eye screening benchmark. The [revised Substack draft](stansfield_pilot/substack/openalex-evidence-synthesis.md) explains how the searches changed and what the benchmark establishes.

| Report | Evidence |
|---|---|
| [2 November 2026 benchmark audit](stansfield_pilot/audit_2026-11-02/README.md) | Eight strategies, complete OQL, corrected study IDs, per-study retrieval, archived API responses and an offline verifier. The exploratory `unscreen*` variant recovered 130/130 indexed studies in 3,892 results. |
| [3 November follow-up checks](stansfield_pilot/followup_2026-11-03/README.md) | Live re-run of the final query (3,892 results, 130/130) and a version using OpenAlex's adjN → within N−1 rule (3,857 results, 130/130). |
| [1 November G2 fact-check](stansfield_pilot/queries/G2_CORRECTED.md) | Correct placement of the topic filter and the effects of using tighter proximity distances. |
| [1 November Embase Table 8 translation](stansfield_pilot/queries/embase_table8_oql_2026/README.md) | A separate translation of the published Embase strategy and its benchmark results. |
| [October pilot](stansfield_pilot/PILOT_REPORT.md) | Original search arms, source retrieval and known-study membership. |
| [Cursor-order study](stansfield_pilot/cursor_study_2026-10-04/CURSOR_ORDER_REPORT.md) | Ranking and pagination evidence. |
