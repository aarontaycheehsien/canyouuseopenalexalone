# OpenAlex evidence synthesis experiments

The reports on this branch use the Stansfield diabetic eye screening benchmark. The [revised Substack draft](stansfield_pilot/substack/openalex-evidence-synthesis.md) explains how the searches changed and what the benchmark establishes.

| Report | Evidence |
|---|---|
| [2 November 2026 benchmark audit](stansfield_pilot/audit_2026-11-02/README.md) | Eight strategies, complete OQL, corrected study IDs, per-study retrieval, archived API responses and an offline verifier. The exploratory `unscreen*` variant recovered 130/130 indexed studies in 3,892 results. |
| [12 November 2026 independent-review transfer test](transfer_benchmark_2026-11-12/README.md) | Queries frozen before inspecting the insomnia review's included titles. All three retrieved 27/29 original articles (93.1%), below the prespecified >95% target; complete exports, diagnostics and an offline verifier are retained. |
| [12 November 2026 larger-workload transfer test](large_transfer_benchmark_2026-11-12/README.md) | Depression-biomarker review reporting 67,464 screening records (not a verified unique count). Frozen queries recovered 66/75 and 63/75; unrestricted counts, benchmark membership, partial-export limitations and diagnostics are retained. |
| [12 November 2026 transgenerational-inheritance test (branch `opus5.5`)](walker_transgenerational_benchmark_2026-11-12/README.md) | Walker et al. (2018): 63,754 records screened, single text-word PubMed strategy. Frozen OQL POST queries recovered 249/257 references (96.9%), meeting the >95% target and matching the published PubMed strategy re-run today, but returned 306,031 results (4.8× the screening load). Restricted-membership evidence, diagnostics and an offline verifier are retained. |
| [3 November follow-up checks](stansfield_pilot/followup_2026-11-03/README.md) | Live re-run of the final query (3,892 results, 130/130) and a version using OpenAlex's adjN → within N−1 rule (3,857 results, 130/130). |
| [1 November G2 fact-check](stansfield_pilot/queries/G2_CORRECTED.md) | Correct placement of the topic filter and the effects of using tighter proximity distances. |
| [1 November Embase Table 8 translation](stansfield_pilot/queries/embase_table8_oql_2026/README.md) | A separate translation of the published Embase strategy and its benchmark results. |
| [October pilot](stansfield_pilot/PILOT_REPORT.md) | Original search arms, source retrieval and known-study membership. |
| [Cursor-order study](stansfield_pilot/cursor_study_2026-10-04/CURSOR_ORDER_REPORT.md) | Ranking and pagination evidence. |
