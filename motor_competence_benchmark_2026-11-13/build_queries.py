"""Build the frozen OQL arms from Bao et al. (2024), Table S1.

Standard library only; no network. `python3 build_queries.py [--check]`.

Table S1 gives three OR-lists of keywords (motor competence, executive functions,
population) with no field tags or platform syntax; the database-specific versions
(with MeSH "where possible") are unpublished. Mechanical rules:
  * the three blocks are ANDed;
  * field: title-abstract-keywords (the usual default for untagged database
    searches: title, abstract and subject/keyword fields);
  * a single word stays bare (OQL stems it, like most database defaults);
  * a multiword term becomes a stemmed adjacent phrase, (stemmed "..."), the
    nearest equivalent of a phrase search with plural matching;
  * a term with * becomes an exact quoted wildcard (OQL runs wildcards unstemmed);
  * dates: publication date <= 2023-06-27 (searched from inception to that day).
Arm A: no further limits (OpenAlex default core corpus).
Arm B: Arm A plus the limits the authors applied "where possible": language
English and type article (journal articles). Species is not available in OpenAlex.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE_TO = "2023-06-27"


def term(t):
    t = t.strip()
    if "*" in t:
        return f'"{t}"'
    if " " in t:
        return f'(stemmed "{t}")'
    return t


def build():
    rows = json.loads((ROOT / "source_search_strategy.json").read_text())["table_S1"]
    assert [r[0] for r in rows] == ["Keywords", "Motor competence", "Executive functions", "Population"]
    blocks = {}
    for name, terms in rows[1:]:
        parts = [term(x) for x in terms.split(" OR ")]
        blocks[name] = "(" + " OR ".join(parts) + ")"
    assert len(rows[1][1].split(" OR ")) == 24 and len(rows[2][1].split(" OR ")) == 15 and len(rows[3][1].split(" OR ")) == 8
    search = "(" + " AND ".join(blocks.values()) + ")"
    base = f"date <= ({DATE_TO}) and title-abstract-keywords has {search}"
    return {
        "A_no_limits": f"get works where {base}",
        "B_english_articles": f"get works where {base} and language is [English](en) and type is [article](article)",
    }, blocks


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
