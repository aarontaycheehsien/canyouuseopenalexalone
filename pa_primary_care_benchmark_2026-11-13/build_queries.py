"""Build the frozen OQL arms from Kettle et al. (2022), web appendix, MEDLINE (Ovid) lines 1-46.

Standard library only; no network. `python3 build_queries.py [--check]`.

Structure: (#1-21 physical activity, OR) AND (#23-38 primary care, OR) AND (#41-44 RCT filter, OR).
Mechanical rules (the same Ovid rules as earlier tests on this branch):
  * only free-text lines (.ti,ab.) are translated; subject-heading lines (.../) and the
    publication-type line (#42, .pt.) are omitted, since OpenAlex has no equivalent;
  * Ovid does not stem, so every term becomes an exact quoted OQL string; multiword terms
    are exact phrases; truncation * is kept; Ovid's optional wildcard ? (randomi?ed) becomes
    a mid-word * (randomi*ed);
  * Ovid adjN allows N-1 intervening words, so adjN becomes "within N-1 words of each
    other" (OpenAlex's published rule for Ovid). OQL proximity takes no OR groups, so
    (a OR b) adjN (c OR d) is expanded to every pair;
  * OQL refuses a proximity with two wildcards unless each has at least four leading
    characters. One pair breaks this: physical* adj3 fit* (line 4). There, and only there,
    physical* is expanded to "physical" and "physically", keeping fit* truncated;
  * field: title-abstract (= .ti,ab.);
  * dates: none at the start (no date limits); publication date <= 2021-04-01, the end of
    the authors' final PubMed update (searches 9-21 September 2020, update to 1 April 2021);
  * no language or type limit.
Arm A: title-abstract. Arm B: the identical string on title-abstract-keywords.
"""
import hashlib
import itertools
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE_TO = "2021-04-01"
BLOCKS = {"physical_activity": range(1, 22), "primary_care": range(23, 39), "rct_filter": range(41, 45)}


def term(t):
    t = t.strip().lower().replace("?", "*")
    assert t and not re.search(r"[()\"/]", t), t
    return f'"{t}"'


def tokens(s):
    return re.findall(r"\(|\)|\badj\d+\b|\bor\b|[^\s()]+(?:\s+(?!or\b|adj\d+\b)[^\s()]+)*", s, flags=re.I)


def parse(toks):
    """expr := unit (('or'|'adjN') unit)*, left to right; returns a list of OQL alternatives."""
    def unit(i):
        if toks[i] == "(":
            alts, i = expr(i + 1)
            assert toks[i] == ")"
            return alts, i + 1
        return [term(toks[i])], i + 1

    def expr(i):
        alts, i = unit(i)
        while i < len(toks) and toks[i] != ")":
            op = toks[i].lower()
            right, i = unit(i + 1)
            if op == "or":
                alts = alts + right
            else:
                n = int(op[3:]) - 1
                pairs = []
                for a, b in itertools.product(alts, right):
                    if (a, b) == ('"physical*"', '"fit*"'):
                        pairs += [f'("{x}" and {b} within {n} words of each other)' for x in ("physical", "physically")]
                    else:
                        pairs.append(f"({a} and {b} within {n} words of each other)")
                alts = pairs
        return alts, i

    alts, i = expr(0)
    assert i == len(toks), toks
    return alts


def line_alternatives(text):
    m = re.fullmatch(r"(.*)\.ti,ab\.", text.strip())
    if not m:
        return None   # subject heading or publication type: omitted
    return parse(tokens(m.group(1)))


def build():
    src = json.loads((ROOT / "source_search_strategy.json").read_text())
    lines = dict((n, t) for n, t in src["medline_lines"])
    assert lines[22] == "or/1-21" and lines[39] == "or/23-38" and lines[40] == "39 and 22" and lines[45] == "41 or 42 or 43 or 44" and lines[46] == "40 and 45"
    blocks, omitted = {}, []
    for name, rng in BLOCKS.items():
        alts = []
        for n in rng:
            a = line_alternatives(lines[n])
            if a is None:
                omitted.append([n, lines[n]])
            else:
                alts += a
        blocks[name] = "(" + " OR ".join(alts) + ")"
    assert all(not (re.search(r'"(\w{1,3})\*', x) and x.count("*") > 1) for b in blocks.values() for x in re.findall(r"\([^()]*within[^()]*\)", b))
    assert [n for n, _ in omitted] == [2, 24, 28, 31, 34, 38, 42], omitted
    date = f"date <= ({DATE_TO})"
    q = {}
    for arm, field in [("A_title_abstract", "title-abstract"), ("B_title_abstract_keywords", "title-abstract-keywords")]:
        q[arm] = f"get works where {date} and " + " and ".join(f"{field} has {b}" for b in blocks.values())
    return q, {"blocks": blocks, "omitted_lines": omitted}


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
