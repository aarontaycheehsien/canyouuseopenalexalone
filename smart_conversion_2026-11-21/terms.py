"""Term forms (PROTOCOL.md R3 'Term form') and term extraction from OQL search text."""
import re

from nltk.stem import PorterStemmer

_P = PorterStemmer()


def normal_form(label):
    """'A, B' -> 'B A'; parenthetical qualifiers removed; punctuation except - and ' -> space."""
    s = re.sub(r"\([^)]*\)", " ", label)
    if s.count(",") == 1:
        a, b = s.split(",")
        s = f"{b} {a}"
    s = re.sub(r"[^\w\s'\-]", " ", s)
    return " ".join(s.split())


def oql_term(form):
    """OQL search fragment for one normalised term."""
    words = form.split()
    if len(words) == 1:
        w = words[0]
        if (w.isupper() and len(w) > 1) or any(ch.isdigit() for ch in w) or "'" in w:
            return f'"{w}"'
        return w.lower()
    return f'(stemmed "{form.lower()}")'


def mesh_term_forms(labels):
    """Distinct OQL fragments for a list of MeSH labels (dedup on the fragment)."""
    seen = {}
    for lab in labels:
        f = normal_form(lab)
        if f:
            seen.setdefault(oql_term(f).lower(), oql_term(f))
    return list(seen.values())


def stem_key(text):
    return " ".join(_P.stem(w) for w in re.sub(r"[^\w\s]", " ", text.lower().replace("-", " ")).split())


def plain_terms(search):
    """Non-wildcard terms of an OQL search string, excluding proximity groups (R4 inputs)."""
    s = re.sub(r'\([^()]*within \d+ words of each other\)', " ", search)
    out = []
    for m in re.finditer(r'\(stemmed "([^"]+)"\)|"([^"]+)"|\b([A-Za-z][\w\'-]*)\b', s):
        t = m.group(1) or m.group(2) or m.group(3)
        if not t or "*" in t or t.upper() in ("AND", "OR", "NOT", "STEMMED"):
            continue
        out.append(t)
    return sorted(set(out))
