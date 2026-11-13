"""Shared helpers for the designed-search builders (standard library only)."""
import hashlib
import itertools
import sys
from pathlib import Path


def kw(*pairs):
    return " or ".join(f"keyword is [{n}](keywords/{i})" for n, i in pairs)


def q(*terms):
    return "(" + " OR ".join(terms) + ")"


def ex(*words):
    return [f'"{w}"' for w in words]


def near(a, b, n):
    return [f'("{x}" and "{y}" within {n} words of each other)' for x, y in itertools.product(a, b)]


def concept(text, kws, field="title-abstract"):
    return f"({field} has {text} or {kws})" if kws else f"{field} has {text}"


def write(root, queries, check):
    root = Path(root)
    for name, oql in queries.items():
        path = root / "queries" / f"{name}.oql"
        if check:
            assert path.read_text() == oql + "\n", path
        else:
            path.write_text(oql + "\n")
        print(name, len(oql), hashlib.sha256((oql + "\n").encode()).hexdigest()[:16])
    if check:
        print("builder output matches frozen files")


def assert_in_source(tokens, text):
    low = text.lower()
    missing = [t for t in tokens if t.lower() not in low]
    assert not missing, missing
