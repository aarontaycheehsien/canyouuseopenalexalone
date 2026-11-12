"""Build the frozen OQL arms from Walker et al. (2018) Supplemental Table S1.

Standard library only. Makes no network requests. Run from any directory:
    python3 walker_transgenerational_benchmark_2026-11-12/build_queries.py [--check]

Translation rules (all fixed before any candidate search was executed):
  * Every PubMed term becomes an exact (quoted) OQL string. PubMed does not
    stem [tiab] text words, and OQL quotes mean exact, unstemmed matching.
  * PubMed truncation (*) is kept as an OQL wildcard inside the quotes.
  * The "[tiab]" tag and any space before it are removed; the field is set
    once for the whole search string.
  * Search #3's F-generation terms are untagged in PubMed (All Fields with
    automatic term mapping). OpenAlex has no All Fields equivalent, so they
    are searched in the same field as everything else. This narrows #3.
  * Boolean structure is preserved: (#1) OR (#2) OR (#3) OR (#4) OR (#5),
    with #3 = (F-terms) AND (generation* OR offspring OR progeny).
  * PubMed was searched "up to November 2016"; the publication-date ceiling
    is 2016-11-30. No language, type, species or corpus restriction.
Arm A searches title-abstract (closest to PubMed [tiab]).
Arm B is the identical Boolean string on title-abstract-keywords, so the
only difference between A and B is the added OpenAlex keyword field.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE_CEILING = "2016-11-30"
ARMS = {
    "A_faithful_title_abstract": "title-abstract",
    "B_title_abstract_keywords": "title-abstract-keywords",
}


def pubmed_terms(text):
    """Split a PubMed OR-list into terms, dropping field tags."""
    text = re.sub(r"\s*\[tiab\]", "", text)
    terms = [t.strip() for t in text.split(" OR ")]
    assert all(terms) and not any(" AND " in t for t in terms), terms
    return terms


def quote(term):
    term = term.strip().strip('"')
    assert '"' not in term and term, term
    return f'"{term}"'


def or_group(terms):
    return "(" + " OR ".join(quote(t) for t in terms) + ")"


def build_search_string():
    rows = json.loads((ROOT / "source_search_strategy_S1.json").read_text())
    lines = {r[0].strip(): " ".join(r[1].split()) for r in rows[1:]}
    assert set(lines) == {"#1", "#2", "#3", "#4", "#5", "Full search"}, lines.keys()
    assert "(#1 OR #2 OR #3 OR #4 OR #5)" in lines["Full search"]
    blocks = {}
    for key in ("#1", "#2", "#4", "#5"):
        blocks[key] = or_group(pubmed_terms(lines[key]))
    m = re.fullmatch(r"\((.*)\) AND \((.*)\)", lines["#3"])
    assert m, lines["#3"]
    f_terms, gen_terms = pubmed_terms(m.group(1)), pubmed_terms(m.group(2))
    assert len(f_terms) == 27 and gen_terms == ["generation*", "offspring", "progeny"]
    blocks["#3"] = f"({or_group(f_terms)} AND {or_group(gen_terms)})"
    counts = {k: len(pubmed_terms(lines[k])) for k in ("#1", "#2", "#4", "#5")}
    assert counts == {"#1": 2, "#2": 4, "#4": 12, "#5": 48}, counts
    search = "(" + " OR ".join(blocks[k] for k in ("#1", "#2", "#3", "#4", "#5")) + ")"
    return search, blocks


def build():
    search, blocks = build_search_string()
    queries = {}
    for name, field in ARMS.items():
        queries[name] = f"get works where date <= ({DATE_CEILING}) and {field} has {search}"
    return queries, blocks


def main():
    queries, blocks = build()
    check = "--check" in sys.argv
    for name, oql in queries.items():
        path = ROOT / "queries" / f"{name}.oql"
        if check:
            assert path.read_text() == oql + "\n", f"{path} differs from builder output"
        else:
            path.write_text(oql + "\n")
        print(name, len(oql), "chars", hashlib.sha256((oql + "\n").encode()).hexdigest())
    (ROOT / "queries" / "blocks.json").write_text(json.dumps(blocks, indent=1) + "\n") if not check else None
    if check:
        assert json.loads((ROOT / "queries" / "blocks.json").read_text()) == blocks
        print("builder output matches frozen files")


if __name__ == "__main__":
    main()
