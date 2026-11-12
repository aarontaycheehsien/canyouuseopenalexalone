"""Build the two prespecified queries from reviewed Appendix A vocabulary."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent


def group(terms):
    return "(" + " OR ".join(t if re.fullmatch(r"[A-Za-z0-9*]+", t) else json.dumps(t) for t in terms) + ")"


def build():
    v = json.loads((ROOT / "vocabulary.json").read_text())
    g = v["biomarker_groups"]
    long_groups = ["neuroimaging", "neurotrophic", "other_hormones", "oxidative_stress"]
    short_groups = ["gastrointestinal", "immunology"]
    no_prediction = ["neurotransmitters", "gonadal_hormones"]
    full = group(v["population"]) + " AND (" + " OR ".join([
        "(" + group(v["prediction_long"]) + " AND " + group([t for key in long_groups for t in g[key]]) + ")",
        "(" + group(v["prediction_short"]) + " AND " + group([t for key in short_groups for t in g[key]]) + ")",
        group([t for key in no_prediction for t in g[key]]),
    ]) + ")"
    compact = " AND ".join([
        group(["depress*", "affective"]),
        group(["prospective", "longitud*", "predict*", "onset", "relaps*", "recurr*", "remiss*", "risk", "vulnerab*"]),
        group(["neuroimag*", "MRI", "fMRI", "EEG", "DTI", "MEG", "PET", "SPECT", "brain imaging",
               "microbi*", "gut", "fecal", "prebiotic", "probiotic", "CRP", "C-reactive protein",
               "cytokine*", "interleukin*", "inflamm*", "immune", "BDNF", "neurotroph*", "growth factor",
               "growth protein", "serotonin", "dopamine", "norepinephrine", "noradrenalin",
               "gamma-aminobutyric acid", "glutamat*", "acetylcholin*", "choliner*", "hormon*", "steroid*",
               "cortisol", "corticotropin", "estrad*", "estron*", "estrogen", "oestrogen", "oestrad*",
               "progest*", "prolact*", "androgen*", "testost*", "dehydroepiandrosterone", "DHEA",
               "gonadotrop*", "FSH", "LH", "ACTH", "thyroid", "thyroxine", "TRH", "TSH", "insulin",
               "leptin", "melatonin", "cholesterol", "oxidative stress", "reactive oxygen species",
               "free radicals", "nitric oxide", "lipid peroxidation", "malondialdehyde", "glutathione",
               "deoxyguanosine", "isoprostane*", "prostaglandin*", "biomarker*"]),
    ])
    return {"A_fuller_source_union": full, "B_compact_three_concepts": compact}


if __name__ == "__main__":
    for name, expr in build().items():
        query = f"get works where date <= (2019-06-30) and title-abstract-keywords has ({expr})\n"
        (ROOT / "queries" / (name + ".oql")).write_text(query)
        print(name, len(query), "characters")
