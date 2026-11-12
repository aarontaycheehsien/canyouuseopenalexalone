"""Build the frozen OQL arms from Christensen et al. (2020), Online Resource 1.

Standard library only; no network. `python3 build_queries.py [--check]`.

The authors publish only their PubMed strings; the strings for PsycINFO, Web of
Science, Embase, NHS York (EED/HTA) and EconLit were "modified to fit" and are
available only on request. Separate searches were run per disorder group:
#1 (cost terms) AND #2 (dates, NOT animal*, NOT trial*) AND one #3 group.
Their union is #1 AND #2 AND (#3 group 1 OR ... OR group 9).

Mechanical rules, the same as the Walker test on this branch:
  * every [TIAB] term or phrase becomes an exact quoted OQL string; truncation
    (*) is kept as an OQL wildcard inside the quotes (PubMed does not stem);
  * untagged terms inside a tagged group (child, children, sexual abuse in the
    substance group) are searched in the same field;
  * the substance group's `(abuse [TIAB] NOT (child OR children OR sexual abuse))`
    keeps its NOT inside the search string;
  * the schizophrenia group has no operator between `schizotypal* [TIAB]` and
    `psychotic* [TIAB]`; PubMed's default operator is AND, so they are ANDed;
  * `alcohol- related disorder` (a stray space in the source) is the phrase
    "alcohol related disorder";
  * #2's NOT animal* and NOT trial* are NOT clauses on the same field;
  * dates: 1980-01-01 to 2019-06-30 (searches were run May-June 2019; the string
    allows to 2019-12-31 but nothing later could have been retrieved).
Arm A: title-abstract (closest to [TIAB]). Arm B: identical string on
title-abstract-keywords; the only difference is OpenAlex's keyword field.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE_FROM, DATE_TO = "1980-01-01", "2019-06-30"
GROUPS = ["Mood disorder", "Organic disorders", "Mental and behavioural disorders due to psychoactive substance use",
          "Schizophrenia spectrum disorders", "Neurotic/Anxiety disorders", "Eating disorder", "Personality Disorders",
          "Mental Retardation", "Behavioral Disorders"]


def clean(term):
    term = term.replace("“", "").replace("”", "").replace('"', "")
    term = re.sub(r"\s*\[TIAB\]\s*", "", term).strip()
    term = re.sub(r"-\s+", " ", term)  # "alcohol- related" -> "alcohol related"
    term = re.sub(r"\s+", " ", term)
    assert term and "[" not in term, term
    return f'"{term}"'


def or_list(text):
    inner = text.strip()
    assert inner.startswith("(") and inner.endswith(")"), inner[:40]
    inner = inner[1:-1]
    nested = "(abuse [TIAB] NOT (child OR children OR sexual abuse))"
    inner = inner.replace(nested, "@ABUSE@")
    out = []
    for t in re.split(r"\s+OR\s+", inner):
        t = t.strip()
        if t == "@ABUSE@":
            out.append('("abuse" NOT ("child" OR "children" OR "sexual abuse"))')
        elif re.fullmatch(r"schizotypal\* \[TIAB\] psychotic\* \[TIAB\]", t):
            out.append('("schizotypal*" AND "psychotic*")')
        else:
            out.append(clean(t))
    return "(" + " OR ".join(out) + ")"


def build():
    p = json.loads((ROOT / "source_search_strategy.json").read_text())["paragraphs"]
    text = {p[i]: p[i + 1] for i in range(len(p) - 1)}
    cost = or_list(text["Cost-of-illness terms: #1"])
    assert text["Restriction of time, to human studies and avoiding RCT/trials: #2"] == \
        "((“1980/01/01” [PDAT] : “2019/12/31” [PDAT]) NOT (animal* [TIAB]) NOT (trial* [TIAB]))"
    groups = []
    for g in GROUPS:
        key = [k for k in text if k.startswith("# " + g)]
        assert len(key) == 1, g
        groups.append(or_list(text[key[0]]))
    assert cost.count('" OR "') == 15, cost
    disorders = "(" + " OR ".join(groups) + ")"
    core = f"({cost} AND {disorders}) NOT (\"animal*\" OR \"trial*\")"
    date = f"date >= ({DATE_FROM}) and date <= ({DATE_TO})"
    return {
        "A_title_abstract": f"get works where {date} and title-abstract has ({core})",
        "B_title_abstract_keywords": f"get works where {date} and title-abstract-keywords has ({core})",
    }, {"cost_#1": cost, **{f"group_{i + 1}": g for i, g in enumerate(groups)}}


def main():
    queries, blocks = build()
    check = "--check" in sys.argv
    for name, oql in queries.items():
        path = ROOT / "queries" / f"{name}.oql"
        if check:
            assert path.read_text() == oql + "\n", path
        else:
            path.write_text(oql + "\n")
        print(name, len(oql), hashlib.sha256((oql + "\n").encode()).hexdigest())
    bpath = ROOT / "queries" / "blocks.json"
    if check:
        assert json.loads(bpath.read_text()) == blocks
        print("builder output matches frozen files")
    else:
        bpath.write_text(json.dumps(blocks, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
