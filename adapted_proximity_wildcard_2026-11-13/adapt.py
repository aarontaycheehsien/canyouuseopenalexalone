"""Rule-based truncation and proximity applied to every frozen arm of the eight benchmarks.

POST HOC: written on 13 November 2026 after every benchmark's misses had been seen. The rules
are generic and identical for every benchmark; nothing is tuned to a study.

Rules, applied only inside search blocks (`<field> has ( ... )`):
  T  truncation: a single word with no wildcard (bare, or exactly quoted) is cut to the common
     prefix of the word and its Porter stem and given a wildcard, if that prefix has at least
     five letters (child -> "child*", temporary -> "temporar*", employment -> "employ*").
     Shorter words, and words with digits, hyphens or apostrophes, are left as they were.
  P  proximity: a two-word phrase without a wildcard, stemmed or exact, becomes a proximity
     pair of its words, each truncated by rule T, "within 2 words of each other" (so word order
     and one intervening word are allowed). Phrases of three or more words are left as they were.
  Existing proximity groups keep their distance; their single-word operands are truncated by T,
  and all operands are quoted (OQL requires all quoted or all bare).
  OQL refuses a proximity with two wildcards unless each has at least four leading characters;
  where a group would break that, the operands rule T truncated revert to their exact words.
Existing wildcards, operators, dates and filters are unchanged.

    python3 adapt.py            # writes queries/<benchmark>__<arm>.oql
"""
import json
import re
from pathlib import Path

from nltk.stem import PorterStemmer

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
BENCHMARKS = ["walker_transgenerational_benchmark_2026-11-12", "inclusion_sen_benchmark_2026-11-13",
              "bt_maize_multisource_benchmark_2026-11-12", "cost_mental_disorders_benchmark_2026-11-13",
              "motor_competence_benchmark_2026-11-13", "precarious_employment_benchmark_2026-11-13",
              "hiv_care_continuum_benchmark_2026-11-13", "pa_primary_care_benchmark_2026-11-13"]
OPS = {"or", "and", "not"}
P = PorterStemmer()


def trunc(word):
    """Rule T for one word; returns an OQL term (quoted wildcard, or None to keep as is)."""
    w = word.lower()
    if "*" in w or not re.fullmatch(r"[a-z]+", w):
        return None
    s = P.stem(w)
    k = 0
    while k < min(len(w), len(s)) and w[k] == s[k]:
        k += 1
    return f'"{w[:k]}*"' if k >= 5 else None


def op_term(word):
    """A single word as a quoted proximity operand."""
    return trunc(word) or f'"{word.strip(chr(34)).lower()}"'


def legal(orig, new):
    """Revert T-truncations in a proximity group if OQL's two-wildcard rule would be broken."""
    wild = [o for o in new if "*" in o]
    if len(wild) >= 2 and any(len(o.strip('"').split("*")[0].split()[-1]) < 4 for o in wild):
        return [f'"{w.strip(chr(34)).lower()}"' if n != f'"{w.strip(chr(34)).lower()}"' and "*" not in w else n for w, n in zip(orig, new)]
    return new


def phrase(words):
    if len(words) != 2 or any("*" in w for w in words):
        return None
    a, b = legal(words, [op_term(words[0]), op_term(words[1])])
    return f"({a} and {b} within 2 words of each other)"


TOKEN = re.compile(r'(?P<prox>\((?P<pin>[^()]*?) within (?P<n>\d+) words of each other\))'
                   r'|(?P<stem>\(stemmed "(?P<sp>[^"]+)"\))'
                   r'|(?P<quote>"(?P<q>[^"]*)")'
                   r'|(?P<word>\b[A-Za-z][A-Za-z0-9\'-]*\b)')


def sub(m):
    if m.group("prox"):
        ops = [o.strip() for o in re.split(r"\s+and\s+", m.group("pin"))]
        new = []
        for o in ops:
            inner = o.strip('"')
            new.append(op_term(inner) if " " not in inner else f'"{inner}"')
        new = legal([o.strip('"') for o in ops], new)
        return "(" + " and ".join(new) + f" within {m.group('n')} words of each other)"
    if m.group("stem"):
        return phrase(m.group("sp").split()) or m.group(0)
    if m.group("quote") is not None:
        q = m.group("q")
        words = q.split()
        if len(words) == 1:
            return trunc(q) or m.group(0)
        return phrase(words) or m.group(0)
    w = m.group("word")
    if w.lower() in OPS:
        return w
    return trunc(w) or w


def balanced(s, i):
    depth = 0
    for j in range(i, len(s)):
        depth += {"(": 1, ")": -1}.get(s[j], 0)
        if depth == 0:
            return j + 1
    raise ValueError("unbalanced")


def adapt(oql):
    out, i = [], 0
    for m in re.finditer(r" has \(", oql):
        start = m.end() - 1
        if start < i:
            continue
        end = balanced(oql, start)
        out.append(oql[i:start])
        out.append(TOKEN.sub(sub, oql[start:end]))
        i = end
    out.append(oql[i:])
    return "".join(out)


def main():
    plan = []
    for b in BENCHMARKS:
        for q in sorted((REPO / b / "queries").glob("*.oql")):
            src = q.read_text().strip()
            new = adapt(src)
            name = f"{b.split('_benchmark')[0]}__{q.stem}"
            (ROOT / "queries" / f"{name}.oql").write_text(new + "\n")
            plan.append({"benchmark": b, "arm": q.stem, "name": name, "frozen_chars": len(src), "adapted_chars": len(new)})
            print(name, len(src), "->", len(new))
    (ROOT / "queries" / "plan.json").write_text(json.dumps(plan, indent=1) + "\n")


if __name__ == "__main__":
    main()
