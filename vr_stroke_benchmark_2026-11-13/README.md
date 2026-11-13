# Virtual reality for upper-limb stroke rehabilitation: designed OpenAlex searches against a five-database review

**The designed search found 35 of 55 included trials (63.6%) at 1,536 records; the mechanical translation found 22 (40.0%) at 18,063.** Both fall far short of the target of 53.

Most designed-search misses come from the review's scope, not the search. 18 of the 20 trials it missed are robotic-assisted or brain–computer-interface trials. The review counts these as virtual reality, but their abstracts never mention it.

| Arm | Design | Trials / 55 | Records | vs 7,381 screened |
|---|---|---:|---:|---:|
| [M](queries/M_mechanical_wos.oql) | Web of Science TS= string (all text), WoS rules | 22 (40.0%) | 18,063 | 2.45× |
| [S1](queries/S1_designed_stroke_vr_rct.oql) | Designed: stroke AND VR/gaming AND randomised trial, text OR keywords | **35 (63.6%)** | **1,536** | **0.21×** |
| [S2](queries/S2_designed_plus_upper_limb.oql) | S1 AND upper-limb concept | 34 (61.8%) | 976 | 0.13× |

All arms are limited to English, as the authors' were. Frozen and pushed ([`5cd6fce`](https://github.com/aarontaycheehsien/canyouuseopenalexalone/commit/5cd6fce)) before any search was scored and before the included trials were opened. Test date: 13 November 2026.

## Benchmark

[Soleimani, Ghazisaeedi and Heydari (2024)](https://doi.org/10.1186/s12911-024-02534-y), BMC Med Inform Decis Mak 24:135.

- **Sources:** PubMed, Scopus, IEEE, Web of Science and PsycNet.
- **Screening:** 7,381 unique records screened; 55 RCTs included.

**The included trials are not in the reference list.** Additional File 3 gives only each trial's title and author-year, so all 55 were matched by OpenAlex title search.

- 54 of the 55 are in OpenAlex. Brunner 2017 was accepted as the VIRTUES trial, not its 2014 protocol; Reinkensmeyer 2012 was found in a second pass.
- Li 2021 cannot be identified: its title is truncated in the supplement.

## Why trials are missed (post hoc)

| Concept (restricted to 54 matched trials) | Text | OpenAlex keywords | Either |
|---|---:|---:|---:|
| Stroke | 54 | 46 | 54 |
| **Virtual reality / gaming** | **36** | 10 | **36** |
| Randomised trial | 53 | 0 | 53 |
| Upper limb (S2) | 53 | 33 | 53 |

**The designed arm's 19 misses.**
- 18 fail the VR concept. They are trials of robot-assisted training (ArmAssist, Pneu-WREX, end-effector robots) or brain–computer interfaces that the review classes as "VR".
- 1 fails the trial concept.

**Why the authors found them.** Their deliberately broad technology block (comput\*, assist\*, simulat\*, visual\*, digit\*, genera\*) admits robotics. A search written for the review's stated topic does not.

**The mechanical arm's problem is different.** Its trial block (exact "clinical trial\*", "random\* controlled trial\*", "rct") passes only 31 of 54. Many abstracts say "randomized clinical trial" or "randomly assigned", and the source databases supplied the RCT publication type instead.

`python3 verify_designed.py vr_stroke_benchmark_2026-11-13` passes all checks.
