# Corrected Variant G2 (Substack draft fact-check)

Run live on 1 November 2026 through the OpenAlex MCP `search_works` tool (OQL, retracted works included). Counts can drift because OpenAlex is a live index.

## What was wrong with the draft's G2

The draft put its topic fallback inside the search phrase:

```text
about ( ... OR (topic is T10170 AND title-abstract-keywords has (...)) )
```

Inside `about (...)` OpenAlex reads `topic`, `is`, `T10170`, `title-abstract-keywords` and `has` as search words, not as a field filter. Run alone, that clause returns 0 works, and `check_oql` still reports the query as valid. The draft's G2 therefore equals its text branches alone: rewriting it without the topic clause gives the same 3,891 results.

## Correction

The topic clause now sits at the `where` level, ORed with the text search. Nothing else is changed. `topic is` means primary topic.

### G2-corrected (draft's proximity distances: within 4 / within 6)

```text
get works where year >= (2003) and year <= (2023) and (title-abstract-keywords has ((((diabetic and retinopathy within 4 words of each other) OR (diabetic and eye within 4 words of each other) OR (diabetic and retina within 4 words of each other)) AND (screen* OR program* OR surveillance OR monitor* OR exam* OR check* OR teleophthalmolog* OR "tele-ophthalmology" OR teleretin* OR "tele-retinal" OR retinascreen* OR keepsight OR "keep sight" OR slick)) OR (diabet* AND ((eye and screening within 6 words of each other) OR (retinal and screening within 6 words of each other) OR (retinopathy and screening within 6 words of each other) OR (eye and care within 6 words of each other) OR (eye and examination within 6 words of each other) OR teleophthalmolog* OR "tele-ophthalmology" OR teleretin* OR retinascreen* OR keepsight OR slick))) or (topic is [Retinal Diseases and Treatments](T10170) and title-abstract-keywords has (screen* OR program* OR care OR utilization OR teleophthalmolog* OR exam* OR check* OR slick OR keepsight OR retinascreen*))) and (country is ([United Kingdom](GB) or [Canada](CA) or [Australia](AU) or [New Zealand](NZ) or [Ireland](IE)) or title-abstract-keywords has (UK OR "United Kingdom" OR Britain OR British OR England OR English OR Scotland OR Scottish OR Wales OR Welsh OR Ireland OR Irish OR Canada OR Canadian OR Australia OR Australian OR "New Zealand" OR Ontario OR Quebec OR Alberta OR Gloucestershire OR Auckland) or (country is unknown and title has ("diabetic retinopathy screening" OR "diabetic eye screening")))
```

### G2-corrected-ADJ (Ovid ADJ semantics: adj4 = within 3, adj6 = within 5)

The same query, with `within 4` changed to `within 3` and `within 6` changed to `within 5`. This follows the gap-budget finding in `OQL_VALIDATION_REPORT.md`.

## Results

Recall is measured against the 130 current OpenAlex IDs in `reference_retrieval.csv` (`current_openalex_id`): 128 primary records plus Briand-Racine (2013) and Hirji (2014). Membership was tested by ANDing each query with `openalex is (...)` over those IDs.

| Query | Works (2003–2023) | Known records retrieved | Missed |
| --- | ---: | ---: | --- |
| Draft G2 (topic clause inside `about`) | 3,891 | 129/130 (127/128 primary) | Felfeli (2023), W4280598166 |
| Draft G2 with topic clause removed | 3,891 | — | identical count: the clause was inert |
| Topic branch alone (`topic is T10170 and ...`) | 23,038 | — | — |
| **G2-corrected (within 4 / 6)** | **5,764** | **130/130 (128/128)** | none |
| **G2-corrected-ADJ (within 3 / 5)** | **5,734** | **130/130 (128/128)** | none |

## Interpretation limits

- The working topic branch adds 1,873 works (+48%) to the draft's 3,891. The draft's claim that the fallback costs only a few hundred records does not hold.
- Felfeli (2023) is recovered only because its primary topic is currently T10170. Topic assignments change between releases.
- Recall is measured on the same known records that were used to design the country terms and the scoped `country is unknown` clause. It is an optimistic, in-sample estimate, not evidence of recall on unseen records.
- The search is still a narrowed translation of the Embase strategy (Table 8 in O'Mara-Eves et al., 2026), not a direct one. For comparison, the fuller restoration in `PILOT_REPORT.md` retrieved 21,679 works with 125/131 recall.
- Precision is unmeasured; no unlabelled records were screened.
