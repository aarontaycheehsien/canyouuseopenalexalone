"""Concept specifications: a transcription of each review's published strategies (PROTOCOL.md R1-R6).

For each review:
  base       frozen query file used as R1 base text
  groups     concepts as lists of base-concept indices ANDed together (from oqlsplit.split), with a
             name and whether it is a design/method concept (R5)
  headings   per group: (vocabulary, label, explode, source line) for every published heading line
  inherited  per group: R2 text terms not already in the base (all empty: see `r2_note`)
  dropped    published lines that cannot be reproduced, with the reason

Vocabularies: "mesh" (MeSH descriptor), "mesh_pt" (MeSH publication type), and non-MeSH thesauri
mapped to MeSH under R3: "emtree", "psycinfo", "eric", "ebsco" (EBSCO DE in ASP/SocINDEX),
"proquest" (MAINSUBJECT.EXACT). PubMed [MeSH Terms] explodes by default, so explode=True.
"""

X, N = True, False   # explode / this term only

SPECS = {
    "walker_transgenerational": {
        "base": "walker_transgenerational_benchmark_2026-11-12/queries/B_title_abstract_keywords.oql",
        "groups": [{"name": "transgenerational", "concepts": [0], "design": False, "headings": []}],
        "r2_note": "one published PubMed strategy, text words only (no MeSH heading exists for the topic)",
        "dropped": [],
    },
    "inclusion_sen": {
        "base": "inclusion_sen_benchmark_2026-11-13/queries/C_union_of_text_cores.oql",
        "groups": [
            {"name": "population", "concepts": [0, 1], "design": False, "headings": [
                ("eric", "Special Needs Students", N, "ERIC S3; PsycINFO S3; ASP S3 (DE)"),
                ("ebsco", "Children with disabilities", N, "SocINDEX S3"),
                ("proquest", "Exceptional children", N, "IBSS S3"),
                ("proquest", "Learning disabilities", N, "Sociological Abstracts S2"),
                ("proquest", "Developmental disabilities", N, "Sociological Abstracts S2"),
            ]},
            {"name": "intervention", "concepts": [2], "design": False, "headings": [
                ("ebsco", "School grade placement", N, "ASP S7"),
                ("ebsco", "Inclusive education", N, "ASP S7; SocINDEX S7"),
                ("ebsco", "Mainstreaming in special education", N, "ASP S7; SocINDEX S7"),
                ("eric", "Placement", N, "ERIC S7; PsycINFO S7"),
                ("eric", "Academic Accommodations (Disabilities)", N, "ERIC S7; PsycINFO S7"),
                ("eric", "Inclusion", N, "ERIC S7; PsycINFO S7"),
                ("eric", "Mainstreaming", N, "ERIC S7; PsycINFO S7; IBSS S8; Sociological Abstracts S5"),
                ("eric", "Student Placement", N, "ERIC S7; PsycINFO S7"),
                ("ebsco", "Ability grouping (Education)", N, "SocINDEX S7"),
                ("ebsco", "Track system (Education)", N, "SocINDEX S7"),
                ("proquest", "Child placement", N, "IBSS S8"),
                ("proquest", "Special education", N, "Sociological Abstracts S5"),
            ]},
            {"name": "method", "concepts": [3], "design": True, "headings": [
                ("ebsco", "Effect sizes (Statistics)", N, "ASP S11"),
                ("eric", "Effect Size", N, "ERIC S11; PsycINFO S11"),
                ("eric", "Control Groups", N, "ASP S11; ERIC S11; PsycINFO S11"),
                ("eric", "Experimental Groups", N, "ASP S11; ERIC S11; PsycINFO S11"),
                ("eric", "Experiments", N, "ASP S11; ERIC S11; PsycINFO S11; IBSS S12; Sociological Abstracts S8"),
                ("eric", "Matched Groups", N, "ASP S11; ERIC S11; PsycINFO S11"),
                ("eric", "Quasiexperimental Design", N, "ERIC S11; PsycINFO S11"),
                ("eric", "Randomized Controlled Trials", N, "ASP S11; ERIC S11; PsycINFO S11; SocINDEX S11"),
                ("eric", "Comparative Testing", N, "ERIC S11; PsycINFO S11"),
                ("proquest", "Clinical trials", N, "IBSS S12"),
            ]},
        ],
        "r2_note": "base C is already the union of every database's free-text core",
        "dropped": [],
    },
    "bt_maize_multisource": {
        "base": "bt_maize_multisource_benchmark_2026-11-12/queries/B_all_corpora_title_abstract_keywords.oql",
        "groups": [
            {"name": "crop", "concepts": [0], "design": False, "headings": []},
            {"name": "field_setting", "concepts": [1], "design": False, "headings": []},
            {"name": "gm_trait", "concepts": [2], "design": False, "headings": []},
        ],
        "r2_note": "Web of Science and Scopus strings are identical; Ovid strategies unpublished",
        "dropped": [("Ovid .hw headings (Agricola, AGRIS, CAB Abstracts)", "strategy text not published")],
    },
    "cost_mental_disorders": {
        "base": "cost_mental_disorders_benchmark_2026-11-13/queries/B_title_abstract_keywords.oql",
        "groups": [
            {"name": "cost_of_illness", "concepts": [0], "design": False, "headings": []},
            {"name": "mental_disorders", "concepts": [1], "design": False, "headings": []},
        ],
        "r2_note": "only the PubMed [TIAB] strings are published",
        "dropped": [("PsycINFO, Web of Science, Embase, NHS York, EconLit strategies", "available on request only")],
    },
    "motor_competence": {
        "base": "motor_competence_benchmark_2026-11-13/queries/A_no_limits.oql",
        "groups": [
            {"name": "motor_competence", "concepts": [0], "design": False, "headings": []},
            {"name": "executive_functions", "concepts": [1], "design": False, "headings": []},
            {"name": "population", "concepts": [2], "design": False, "headings": []},
        ],
        "r2_note": "Table S1 publishes one keyword list per concept",
        "dropped": [("per-database MeSH and thesaurus terms", "used 'where possible' but not published")],
    },
    "precarious_employment": {
        "base": "precarious_employment_benchmark_2026-11-13/queries/B_precarious_terms_only.oql",
        "groups": [{"name": "precarious_employment", "concepts": [0], "design": False, "headings": []}],
        "r2_note": "only the Scopus strategy is published; base B is its employment block, as used in the health databases",
        "dropped": [("MEDLINE, Embase, PsycINFO and five other strategies", "not published")],
    },
    "hiv_care_continuum": {
        "base": "hiv_care_continuum_benchmark_2026-11-13/queries/B_title_abstract_keywords.oql",
        "groups": [
            {"name": "hiv", "concepts": [0], "design": False, "headings": [
                ("emtree", "human immunodeficiency virus", X, "Embase HIV"),
                ("emtree", "acquired immune deficiency syndrome", X, "Embase HIV"),
                ("mesh", "HIV", X, "PubMed HIV"),
                ("mesh", "HIV Infections", X, "PubMed HIV"),
                ("mesh", "Acquired Immunodeficiency Syndrome", X, "PubMed HIV (AIDS[MeSH Terms])"),
            ]},
            {"name": "children_adolescents", "concepts": [1], "design": False, "headings": [
                ("emtree", "child", X, "Embase"), ("emtree", "pediatrics", X, "Embase"),
                ("emtree", "adolescence", X, "Embase"), ("emtree", "young adult", X, "Embase"),
                ("mesh", "Child", X, "PubMed"), ("mesh", "Pediatrics", X, "PubMed"),
                ("mesh", "Adolescent", X, "PubMed"), ("mesh", "Young Adult", X, "PubMed"),
            ]},
            {"name": "care_continuum_outcomes", "concepts": [2], "design": False, "headings": [
                ("emtree", "patient care", X, "Embase HIV care continuum"),
                ("emtree", "health care quality", X, "Embase HIV care continuum"),
                ("emtree", "patient referral", X, "Embase HIV care continuum"),
                ("emtree", "health care access", X, "Embase HIV care continuum"),
                ("emtree", "consultation", X, "Embase HIV care continuum"),
                ("emtree", "hiv test", X, "Embase Diagnosis"),
                ("emtree", "antiretroviral therapy", X, "Embase ART"),
                ("emtree", "highly active antiretroviral therapy", X, "Embase ART"),
                ("emtree", "anti human immunodeficiency virus agent", X, "Embase ART"),
                ("emtree", "retention in care", X, "Embase Retention"),
                ("emtree", "viremia", X, "Embase Viral load"),
                ("emtree", "viral load testing", X, "Embase Viral load"),
                ("emtree", "second-line treatment", X, "Embase Viral load"),
                ("emtree", "patient compliance", X, "Embase Adherence"),
                ("mesh", "Continuity of Patient Care", X, "PubMed HIV care continuum"),
                ("mesh", "Standard of Care", X, "PubMed HIV care continuum"),
                ("mesh", "Referral and Consultation", X, "PubMed HIV care continuum"),
                ("mesh", "Health Services Accessibility", X, "PubMed HIV care continuum"),
                ("mesh", "Quality of Health Care", X, "PubMed HIV care continuum"),
                ("mesh", "HIV Testing", X, "PubMed Diagnosis"),
                ("mesh", "Anti-Retroviral Agents", X, "PubMed ART; Viral load"),
                ("mesh", "Anti-HIV Agents", X, "PubMed ART; Viral load"),
                ("mesh", "Antiretroviral Therapy, Highly Active", X, "PubMed ART; Viral load"),
                ("mesh", "Retention in Care", X, "PubMed Retention"),
                ("mesh", "Drug Resistance, Viral", X, "PubMed Viral load"),
                ("mesh", "Viremia", X, "PubMed Viral load"),
                ("mesh", "Viral Load", X, "PubMed Viral load"),
                ("mesh", "Medication Adherence", X, "PubMed Adherence"),
            ]},
            {"name": "countries", "concepts": [3], "design": False, "headings": [
                ("mesh", "Africa, Eastern", X, "PubMed Countries"),
                ("mesh", "Africa, Southern", X, "PubMed Countries"),
            ]},
        ],
        "r2_note": "every PubMed text term is contained in a translated Embase term (hiv[tw] in hiv*, 'test' in test*)",
        "dropped": [("African Index Medicus", "not reproducible")],
    },
    "pa_primary_care": {
        "base": "pa_primary_care_benchmark_2026-11-13/queries/B_title_abstract_keywords.oql",
        "groups": [
            {"name": "physical_activity", "concepts": [0], "design": False, "headings": [
                ("mesh", "Exercise", X, "MEDLINE 2"), ("mesh", "Physical Exertion", X, "MEDLINE 2"),
                ("mesh", "Physical Fitness", X, "MEDLINE 2"),
            ]},
            {"name": "primary_care", "concepts": [1], "design": False, "headings": [
                ("mesh", "Family Practice", N, "MEDLINE 24"), ("mesh", "General Practitioners", N, "MEDLINE 24"),
                ("mesh", "Community Health Nursing", X, "MEDLINE 28"), ("mesh", "Public Health Nursing", N, "MEDLINE 28"),
                ("mesh", "Community Health Services", N, "MEDLINE 31"), ("mesh", "Primary Health Care", N, "MEDLINE 34"),
                ("mesh", "Physical Therapists", N, "MEDLINE 38"),
            ]},
            {"name": "rct_filter", "concepts": [2], "design": True, "headings": [
                ("mesh_pt", "Randomized Controlled Trial", N, "MEDLINE 42 (.pt.)"),
            ]},
        ],
        "r2_note": "only the MEDLINE strategy is published",
        "dropped": [("eleven other databases and three trial registers", "adapted strategies not published")],
    },
    "noetel_exercise": {
        "base": "exercise_transfer_benchmark_2026-11-12/queries/A_fuller_source_concepts.oql",
        "groups": [
            {"name": "depression", "concepts": [0], "design": False, "headings": [
                ("mesh", "Depressive Disorder", X, "CENTRAL #13; MEDLINE 14"),
                ("mesh", "Depression", N, "CENTRAL #14; MEDLINE 13"),
                ("emtree", "depression", X, "Embase 6"),
                ("psycinfo", "major depression", X, "PsycINFO 1"),
                ("psycinfo", "atypical depression", N, "PsycINFO 2"),
                ("psycinfo", "seasonal affective disorder", N, "PsycINFO 3"),
            ]},
            {"name": "exercise", "concepts": [1], "design": False, "headings": [
                ("mesh", "Exercise", X, "CENTRAL #1; MEDLINE 1"),
                ("mesh", "Exercise Therapy", X, "CENTRAL #2; MEDLINE 2"),
                ("mesh", "Physical Education and Training", X, "CENTRAL #3; MEDLINE 3"),
                ("mesh", "Physical Fitness", N, "CENTRAL #4; MEDLINE 4"),
                ("mesh", "Physical Exertion", N, "CENTRAL #5; MEDLINE 5"),
                ("mesh", "Walking", X, "CENTRAL #6; MEDLINE 6"),
                ("mesh", "Running", X, "CENTRAL #7 (explode); MEDLINE 7"),
                ("mesh", "Jogging", N, "MEDLINE 7"),
                ("mesh", "Swimming", N, "CENTRAL #8; MEDLINE 8"),
                ("mesh", "Yoga", N, "MEDLINE 8"), ("mesh", "Qigong", N, "MEDLINE 8"),
                ("mesh", "Tai Ji", N, "MEDLINE 8"),
                ("emtree", "exercise", X, "Embase 1"), ("emtree", "physical activity", X, "Embase 2"),
                ("emtree", "sport", X, "Embase 3"),
                ("psycinfo", "physical activity", X, "PsycINFO 6"), ("psycinfo", "sports", X, "PsycINFO 7"),
                ("psycinfo", "running", N, "PsycINFO 8"), ("psycinfo", "walking", N, "PsycINFO 8"),
            ]},
            {"name": "trial", "concepts": [2], "design": True, "headings": [
                ("mesh_pt", "Randomized Controlled Trial", N, "MEDLINE 16 (.pt.)"),
                ("mesh_pt", "Controlled Clinical Trial", N, "MEDLINE 17 (.pt.)"),
                ("emtree", "crossover procedure", N, "Embase 7 (.hw.)"),
                ("emtree", "double-blind procedure", N, "Embase 7 (.hw.)"),
                ("emtree", "randomized controlled trial", N, "Embase 7 (.hw.)"),
                ("emtree", "single-blind procedure", N, "Embase 7 (.hw.)"),
                ("psycinfo", "treatment effectiveness evaluation", N, "PsycINFO 13"),
                ("psycinfo", "clinical trials", N, "PsycINFO 14"),
                ("psycinfo", "mental health program evaluation", N, "PsycINFO 15"),
                ("psycinfo", "placebo", N, "PsycINFO 16"),
            ]},
        ],
        "r2_note": "base A is the concept-level union of the five published strategies' text lines",
        "dropped": [("CENTRAL SR-DEPRESSN, HS-DEPRESSN", "Cochrane register codes"),
                    ("CENTRAL has no trial block", "trial concept is the union of the other databases' blocks, as in frozen arm A")],
    },
}
