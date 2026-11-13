"""Build the frozen OQL arms for the anxiety and eating-disorder symptoms benchmark.

Standard library only; no network. `python3 build_queries.py [--check]`.

Source: Supplementary file 3, the Scopus TITLE-ABS-KEY string (the same three blocks are
used in every database): anxiety terms AND eating-disorder terms AND youth terms. The
search ran from inception to 11 June 2024 (update), with no other limits.

Arm M (mechanical), Scopus rules as on this branch:
  * {braced} = Scopus exact phrase -> exact quoted OQL string (wildcards kept);
  * "quoted" = Scopus loose phrase (lemmatised) -> exact wildcard if it has *, else a stemmed
    phrase (single words bare, so stemmed);
  * `m#n` is not Scopus syntax (Ovid's one-character wildcard): young m#n -> "young men" OR
    "young man", young wom#n -> "young women" OR "young woman";
  * OQL needs three leading characters before a lone wildcard in a phrase: {intrusive th*}
    becomes "intrusive thought*";
  * field title-abstract-keywords (= TITLE-ABS-KEY); date <= 2024-06-11.

Arms S1 and S2 (designed, before the included studies were seen), same three concepts:
  * targeted truncation where a word has variants (worri*, internali*, dieter*), exact words
    where truncation would add noise; irregular forms spelled out;
  * proximity pairs ADDED beside the phrases they loosen, never replacing them (phrases are
    what match OpenAlex keyword labels);
  * the authors' very broad diet* and fast* replaced by dieting/dieter*/"dietary restraint"/
    fasting; internalising-symptom and puberty/school terms added;
  * each concept also ORs the OpenAlex keywords that mean it, chosen from find_keywords;
  * S1 = the three concepts; S2 = S1 AND a prospective-design concept (the review includes only
    prospective studies), in title-abstract or the keyword "prospective associations".
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE_TO = "2024-06-11"


# ---------- arm M ----------
def m_term(t):
    t = t.strip()
    if t.startswith("{"):
        inner = t.strip("{}")
    else:
        inner = t.strip('"')
    special = {"young m#n": '("young men" OR "young man")', "young wom#n": '("young women" OR "young woman")',
               "intrusive th*": '"intrusive thought*"'}
    if inner in special:
        return special[inner]
    if t.startswith("{") or "*" in inner:
        return f'"{inner.lower()}"'
    return f'(stemmed "{inner.lower()}")' if " " in inner else inner.lower()


def arm_m():
    src = json.loads((ROOT / "source_search_strategy.json").read_text())["paragraphs"]
    scopus = src[src.index("SCOPUS") + 1]
    body = scopus[len("TITLE-ABS-KEY("):-1]
    groups = re.findall(r"\(([^()]*)\)", body)
    assert len(groups) == 3, len(groups)
    blocks = []
    for g in groups:
        terms = [x.strip() for x in re.split(r"\s+OR\s+", g)]
        blocks.append("(" + " OR ".join(m_term(x) for x in terms) + ")")
    assert [len(re.split(r"\s+OR\s+", g)) for g in groups] == [13, 24, 11]
    return f"get works where date <= ({DATE_TO}) and " + " and ".join(f"title-abstract-keywords has {b}" for b in blocks)


# ---------- arms S1, S2 ----------
def kw(*pairs):
    return " or ".join(f"keyword is [{n}](keywords/{i})" for n, i in pairs)


ANX_TEXT = ('("anxi*" OR "worry" OR "worri*" OR "fear" OR "fears" OR "fearful*" OR "ruminat*" OR "panic" OR "phobi*" '
            'OR "ptsd" OR "posttraumatic" OR ("post" and "traumatic" within 1 words of each other) OR "ocd" OR "obsessi*" '
            'OR "compulsi*" OR "intrusive thought*" OR "shyness" OR "nervousness" OR "internali*")')
ANX_KW = kw(("anxiety", "anxiety"), ("anxiety symptoms", "anxiety-symptoms"), ("anxiety disorders", "anxiety-disorders"),
            ("generalized anxiety disorder", "generalized-anxiety-disorder"), ("social anxiety", "social-anxiety"),
            ("worry", "worry"), ("obsessive-compulsive disorder", "obsessive-compulsive-disorder"),
            ("obsessive-compulsive symptoms", "obsessive-compulsive-symptoms"))
ED_TEXT = ('("eating disorder*" OR ("eating" and "disorder*" within 2 words of each other) OR "disordered eating" '
           'OR "eating pathology" OR "eating psychopathology" OR ("eating" and "patholog*" within 2 words of each other) '
           'OR "eating habits" OR "eating attitude*" OR "body image" OR "body dissatisfaction" '
           'OR ("body" and "dissatisf*" within 2 words of each other) OR ("shape" and "concern*" within 2 words of each other) '
           'OR ("weight" and "concern*" within 2 words of each other) OR "drive for thinness" OR "excessive exercise" '
           'OR "compulsive exercise" OR "dieting" OR "dieter*" OR "dietary restraint" OR "restrained eating" '
           'OR ("restrict*" and "eating" within 2 words of each other) OR "fasting" OR "intention to lose weight" '
           'OR "anorexi*" OR "bulimi*" OR "binge*" OR "overeat*" OR "night eating" OR "purg*" OR "laxative*" OR "diuretic*" '
           'OR "vomit*" OR "loss of control eating" OR ("loss" and "control" and "eating" within 3 words of each other) '
           'OR "emotional eating")')
ED_KW = kw(("eating disorders", "eating-disorders"), ("disordered eating", "disordered-eating-behaviors"),
           ("eating disorder symptoms", "eating-disorder-symptoms"), ("eating disorder risk", "eating-disorder-risk"),
           ("body dissatisfaction", "body-dissatisfaction"), ("binge eating", "binge-eating"),
           ("binge eating disorder", "binge-eating-disorder"), ("anorexia nervosa", "anorexia-nervosa"),
           ("weight and shape concerns", "weight-and-shape-concerns"), ("weight dissatisfaction", "weight-dissatisfaction"))
YOUTH_TEXT = ('("child*" OR "adolesc*" OR "preadolesc*" OR "teen*" OR "youth*" OR "juvenile*" OR "pubert*" OR "pubescen*" '
              'OR "girl*" OR "boy*" OR "student*" OR "pupil*" OR "school*" OR "young adult*" OR "young people" '
              'OR "young person*" OR "young men" OR "young man" OR "young women" OR "young woman" OR "emerging adult*" '
              'OR "pediatric*" OR "paediatric*")')
YOUTH_KW = kw(("adolescents", "adolescents"), ("children", "children"))
DESIGN_TEXT = ('("longitudinal*" OR "prospective*" OR "cohort*" OR "follow-up" OR "follow up" OR "followed up" '
               'OR "predict*" OR "preced*" OR "onset" OR "subsequent*" OR "later" OR "over time" OR "baseline" '
               'OR "wave*" OR "trajector*" OR "cross-lagged" OR "temporal*" OR "risk factor*" OR "bidirectional" '
               'OR "bi-directional" OR "reciprocal")')
DESIGN_KW = kw(("prospective associations", "prospective-associations"))


def concept(text, kws, field="title-abstract"):
    return f"({field} has {text} or {kws})"


def arms_s():
    base = [concept(ANX_TEXT, ANX_KW), concept(ED_TEXT, ED_KW), concept(YOUTH_TEXT, YOUTH_KW)]
    s1 = f"get works where date <= ({DATE_TO}) and " + " and ".join(base)
    s2 = s1 + " and " + concept(DESIGN_TEXT, DESIGN_KW)
    return s1, s2


def build():
    s1, s2 = arms_s()
    return {"M_mechanical_scopus": arm_m(), "S1_designed_three_concepts": s1, "S2_designed_plus_prospective": s2}


def main():
    queries = build()
    check = "--check" in sys.argv
    for name, oql in queries.items():
        path = ROOT / "queries" / f"{name}.oql"
        if check:
            assert path.read_text() == oql + "\n", path
        else:
            path.write_text(oql + "\n")
        print(name, len(oql), hashlib.sha256((oql + "\n").encode()).hexdigest()[:16])
    if check:
        print("builder output matches frozen files")


if __name__ == "__main__":
    main()
