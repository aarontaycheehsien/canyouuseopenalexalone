"""Build the frozen OQL arms for the ethnicity and antidiabetic-medication adherence benchmark.

Standard library only; no network. `python3 build_queries.py [--check]`.

Source: S1 Text, the MEDLINE/Embase/CINAHL (Ovid) strategy: an adherence block AND a diabetes
block AND a glycaemic-control block, followed by "OR" and an ethnicity block. As printed, the
final OR would add every ethnicity record on its own, which cannot be what ran (it would
retrieve millions). The charitable reading used for arm M is
    adherence AND diabetes AND (glycaemic control OR ethnicity).
Searched from inception to June 2022; no language or date limits.

Arm M (mechanical), Ovid rules as on this branch:
  * only .mp. lines are translated; subject-heading lines (.../, exp ...) are omitted;
  * Ovid does not stem: every term is an exact quoted string (multiword = exact phrase);
  * field title-abstract-keywords (the nearest to .mp.); date <= 2022-06-30.

Arms S1 and S2 (designed, before the included studies were seen), the review's three
concepts: medication adherence AND diabetes AND ethnicity (the glycaemic block is dropped:
the review's question is adherence by ethnicity, and glycaemic control is not required):
  * targeted truncation (adheren*, complian*, diabet*, ethnic*, racial*, hispanic*, latin*);
    irregular and hyphenated forms spelled out (nonadheren*, multiethnic*); short ambiguous words
    exact (race, races, black, white, blacks, whites);
  * proximity for persistence, discontinuation and refill concepts, which are noisy alone;
  * each concept also ORs the OpenAlex keywords that mean it, chosen from find_keywords;
  * S1 = the three concepts in title-abstract plus keywords; S2 = S1 with the adherence concept
    restricted to medication context: adherence words within 3 words of a medication word,
    plus the adherence-specific keywords (not the broad "medication adherence" keyword).
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE_TO = "2022-06-30"


def arm_m():
    ps = json.loads((ROOT / "source_search_strategy.json").read_text())["paragraphs"]
    med = ps[ps.index("MEDLINE, Embase and CINAHL Search Strategy") + 1: ps.index("PsycINFO Search Strategy")]
    blocks, cur = [], []
    for line in med:
        if line in ("And", "AND", "OR"):
            blocks.append(cur)
            cur = []
            continue
        cur.append(line)
    blocks.append(cur)
    assert [len(b) for b in blocks] == [6, 6, 5, 15], [len(b) for b in blocks]
    out = []
    for b in blocks:
        terms = []
        for line in b:
            for part in re.split(r"\s+(?:or|OR)\s*", line):
                part = part.strip()
                m = re.fullmatch(r"(.+?)\.mp\.?", part)
                if m:
                    t = m.group(1).strip().lower()
                    if t not in terms:
                        terms.append(t)
        out.append("(" + " OR ".join(f'"{t}"' for t in terms) + ")")
    adherence, diabetes, glycaemic, ethnicity = out
    return (f"get works where date <= ({DATE_TO}) and title-abstract-keywords has {adherence} and "
            f"title-abstract-keywords has {diabetes} and (title-abstract-keywords has {glycaemic} or "
            f"title-abstract-keywords has {ethnicity})")


def kw(*pairs):
    return " or ".join(f"keyword is [{n}](keywords/{i})" for n, i in pairs)


ADH_TEXT = ('("adheren*" OR "nonadheren*" OR "non-adheren*" OR "complian*" OR "noncomplian*" OR "non-complian*" '
            'OR "concordance" OR ("medication*" and "persisten*" within 3 words of each other) '
            'OR ("treatment" and "persisten*" within 2 words of each other) OR ("therapy" and "persisten*" within 2 words of each other) '
            'OR ("discontinu*" and "medication*" within 3 words of each other) OR ("discontinu*" and "therap*" within 3 words of each other) '
            'OR "medication possession ratio" OR "proportion of days covered" OR ("refill*" and "medication*" within 3 words of each other))')
ADH_KW_BROAD = kw(("medication adherence", "treatment-adherence"), ("medication non-adherence", "medication-non-adherence"),
                  ("treatment persistence", "medication-persistence"), ("antidiabetic medication adherence", "antidiabetic-medication-adherence"),
                  ("Morisky Medication Adherence Scale", "morisky-medication-adherence-scale"))
ADH_KW_NARROW = kw(("medication non-adherence", "medication-non-adherence"), ("treatment persistence", "medication-persistence"),
                   ("antidiabetic medication adherence", "antidiabetic-medication-adherence"),
                   ("Morisky Medication Adherence Scale", "morisky-medication-adherence-scale"))
MEDWORDS = ["medication*", "medicine*", "drug*", "treatment*", "therap*", "insulin", "metformin", "prescription*", "regimen*", "pill*"]
ADH_WORDS = ["adheren*", "nonadheren*", "complian*", "noncomplian*", "persisten*", "discontinu*"]
ADH_TEXT_NARROW = ("(" + " OR ".join(f'("{a}" and "{m}" within 3 words of each other)' for a in ADH_WORDS for m in MEDWORDS)
                   + ' OR "medication possession ratio" OR "proportion of days covered")')
DM_TEXT = ('("diabet*" OR "t2dm" OR "t1dm" OR "niddm" OR "iddm" OR "antidiabet*" OR "anti-diabet*" OR "hypoglycemic agent*" '
           'OR "hypoglycaemic agent*" OR "glucose-lowering" OR "glucose lowering" OR "metformin" OR "sulfonylurea*" OR "sulphonylurea*")')
DM_KW = kw(("diabetes mellitus", "diabetes-mellitus"), ("type 2 diabetes", "type-2-diabetes"), ("type 1 diabetes", "type-1-diabetes"),
           ("antidiabetic drugs", "antidiabetic-drugs"), ("antidiabetic medication adherence", "antidiabetic-medication-adherence"))
ETH_TEXT = ('("ethnic*" OR "multiethnic*" OR "multi-ethnic*" OR "race" OR "races" OR "racial*" OR "minorit*" OR "black" OR "blacks" '
            'OR "white" OR "whites" OR "caucasian*" OR "african american*" OR "african-american*" OR "hispanic*" OR "latino*" '
            'OR "latina*" OR "latinx" OR "asian*" OR "arab*" OR "mexican american*" OR "pacific islander*" OR "native american*" '
            'OR "american indian*" OR "alaska native*" OR "indigenous" OR "aborigin*" OR "maori" OR "first nations" OR "disparit*")')
ETH_KW = kw(("ethnicity", "ethnicity"), ("race", "race"), ("racial disparities", "racial-disparities"), ("ethnic disparities", "ethnic-disparities"),
            ("ethnic differences", "ethnic-differences"), ("racial and ethnic disparities", "racial-and-ethnic-disparities"),
            ("ethnic minorities", "ethnic-minorities"), ("African Americans", "african-americans"), ("Hispanic Americans", "hispanic-americans"))


def concept(text, kws):
    return f"(title-abstract has {text} or {kws})"


def build():
    date = f"get works where date <= ({DATE_TO}) and "
    s1 = date + " and ".join([concept(ADH_TEXT, ADH_KW_BROAD), concept(DM_TEXT, DM_KW), concept(ETH_TEXT, ETH_KW)])
    s2 = date + " and ".join([concept(ADH_TEXT_NARROW, ADH_KW_NARROW), concept(DM_TEXT, DM_KW), concept(ETH_TEXT, ETH_KW)])
    return {"M_mechanical_ovid": arm_m(), "S1_designed_three_concepts": s1, "S2_designed_medication_context": s2}


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
