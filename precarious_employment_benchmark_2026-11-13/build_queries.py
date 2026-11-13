"""Build the frozen OQL arms from Pulford et al. (2022), Figure S2.1 (Scopus strategy).

Standard library only; no network. `python3 build_queries.py [--check]`.

Figure S2.1 is the Scopus string: precarious-employment terms AND health terms, all
TITLE-ABS. The methods say the health terms "were included in searches of non-health
databases", so the health databases (MEDLINE, Embase, PsycINFO) ran the
precarious-employment block alone. Mechanical rules (Scopus lemmatises unquoted words
and "loose phrases"):
  * an unquoted single word stays bare (OQL stems it);
  * a quoted phrase becomes a stemmed adjacent phrase, (stemmed "...");
  * a term with * becomes an exact quoted wildcard (OQL runs wildcards unstemmed;
    mid-word wildcards such as labo*r are supported);
  * field: title-abstract (= TITLE-ABS);
  * dates: publication date <= 2019-03-31 ("up to March 2019"); no lower limit stated.
Arm A: the Scopus string exactly (precarious AND health), as for non-health databases.
Arm B: the precarious-employment block alone, as for health databases.
Default core corpus; no language, type or other limit.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE_TO = "2019-03-31"


def term(t):
    t = t.strip()
    quoted = t.startswith('"')
    t = t.strip('"')
    if "*" in t:
        return f'"{t}"'
    if quoted and " " in t:
        return f'(stemmed "{t}")'
    assert " " not in t, t
    return t


def block(text):
    terms = re.findall(r'TITLE-ABS\(([^)]*)\)', text)
    return "(" + " OR ".join(term(x) for x in terms) + ")", len(terms)


def build():
    txt = json.loads((ROOT / "source_search_strategy.json").read_text())["figure_S2_1_text"]
    pre, health = txt.split(") AND (")
    pre_b, n1 = block(pre)
    health_b, n2 = block(health)
    assert (n1, n2) == (38, 15), (n1, n2)
    date = f"date <= ({DATE_TO})"
    return {
        "A_scopus_with_health_terms": f"get works where {date} and title-abstract has {pre_b} and title-abstract has {health_b}",
        "B_precarious_terms_only": f"get works where {date} and title-abstract has {pre_b}",
    }, {"precarious_employment": pre_b, "health": health_b}


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
        bpath.write_text(json.dumps(blocks, indent=1) + "\n")


if __name__ == "__main__":
    main()
