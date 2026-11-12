# Status: frozen, matching started, searches not executed

As of 13 November 2026, this benchmark is **incomplete**.

- **Done:**
  - The protocol and both OQL arms were frozen and pushed in commit `1c95f20`.
  - The included-article list was parsed into `results/benchmark_source.json`.
- **Partly done:** automatic matching to OpenAlex. Of the 167 entries in `results/matching_raw.json`, 134 were auto-accepted and 33 still need manual adjudication.
- **Not done:**
  - The frozen arms have not been run.
  - No recall, count or workload result exists.

Matching evidence (OpenAlex and Crossref lookups, with Crossref abstracts removed) is in `archives/`. The live runners are `match_benchmark.py` and `run_test.py`.

The multi-source test that was completed on this branch is [`inclusion_sen_benchmark_2026-11-13`](../inclusion_sen_benchmark_2026-11-13/README.md).

To finish this test:
1. Adjudicate the 33 remaining matches.
2. Run the frozen arms unchanged.
3. Report against the protocol's prespecified outcomes.
