"""Build the frozen OQL arms from the Web of Science / Scopus string of Meissle et al. (2022).

Standard library only, no network. `python3 build_queries.py [--check]`.

Rules (fixed before any candidate search was executed):
  * The WoS TS= and Scopus TITLE-ABS-KEY strings are identical in content; they
    search title, abstract and keywords, so the OQL field is title-abstract-keywords.
  * Bare words stay bare (OQL stems them), the nearest equivalent of WoS
    lemmatisation and Scopus plural matching.
  * Quoted phrases and the hyphenated farm-scale become stemmed adjacent
    phrases (stemmed "..."), the nearest equivalent of Scopus loose phrases.
  * Cry* and Vip* stay wildcards (OQL runs wildcards on exact text).
  * Boolean structure: three OR blocks joined by AND.
  * Last database update 23.8.2019: publication date <= 2019-08-23.
Arm A runs on OpenAlex's default core corpus. Arm B is identical except
(all corpora), adding the expansion corpus; it isolates that one change.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CEILING = "2019-08-23"


def term(t):
    t = t.strip()
    if t.startswith('"'):
        return f'(stemmed {t})'
    if "-" in t:
        return f'(stemmed "{t.replace("-", " ")}")'
    if t.endswith("*"):
        return f'"{t}"'
    return t


def build():
    src = json.loads((ROOT / "source_search_strategy.json").read_text())
    wos = src["web_of_science"]["string"]
    sco = src["scopus"]["string"]
    inner_w = re.fullmatch(r"TS = \((.*)\)", wos).group(1)
    inner_s = re.fullmatch(r"TITLE-ABS-KEY\((.*)\)", sco).group(1)
    assert inner_w == inner_s, "WoS and Scopus strings differ"
    blocks = re.findall(r"\(([^()]*)\)", inner_s)
    assert len(blocks) == 3 and re.sub(r"\([^()]*\)", "X", inner_s) == "X AND X AND X"
    parts = []
    for b in blocks:
        terms = [term(t) for t in b.split(" OR ")]
        parts.append("(" + " OR ".join(terms) + ")")
    search = "(" + " AND ".join(parts) + ")"
    return {
        "A_core_title_abstract_keywords": f"get works where date <= ({CEILING}) and title-abstract-keywords has {search}",
        "B_all_corpora_title_abstract_keywords": f"get works (all corpora) where date <= ({CEILING}) and title-abstract-keywords has {search}",
    }


def main():
    check = "--check" in sys.argv
    for name, oql in build().items():
        p = ROOT / "queries" / f"{name}.oql"
        if check:
            assert p.read_text() == oql + "\n", p
        else:
            p.write_text(oql + "\n")
        print(name, hashlib.sha256((oql + "\n").encode()).hexdigest())
    if check:
        print("builder output matches frozen files")


if __name__ == "__main__":
    main()
