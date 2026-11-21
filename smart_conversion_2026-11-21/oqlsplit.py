"""Split a frozen OQL works query into filters, concepts and exclusions (standard library only).

A frozen query has the form
    get works [(all corpora)] where <filter> and ... and <field> has (<search>) and ...
Each <search> is split at its top level: `A AND B AND C` gives three concepts, `A NOT B`
gives concept A and exclusion B. A search with a top-level OR is one concept.
"""
import re


def _top(s, sep):
    """Split s at occurrences of sep that sit outside parentheses and quotes."""
    out, depth, q, i, start = [], 0, False, 0, 0
    while i < len(s):
        c = s[i]
        if c == '"':
            q = not q
        elif not q and c == "(":
            depth += 1
        elif not q and c == ")":
            depth -= 1
        elif not q and depth == 0 and s.startswith(sep, i):
            out.append(s[start:i])
            i += len(sep)
            start = i
            continue
        i += 1
    out.append(s[start:])
    return [x.strip() for x in out]


def strip_outer(s):
    s = s.strip()
    while s.startswith("(") and s.endswith(")") and len(_top(s[1:-1], "\x00")) == 1:
        depth, ok = 0, True
        for i, c in enumerate(s):
            depth += {"(": 1, ")": -1}.get(c, 0)
            if depth == 0 and i < len(s) - 1:
                ok = False
                break
        if not ok:
            break
        s = s[1:-1].strip()
    return s


HAS = re.compile(r"^(title-abstract-keywords|title-abstract|title|abstract) has (.*)$", re.S)


def split(oql):
    m = re.match(r"^get works( \(all corpora\))? where (.*)$", oql.strip(), re.S)
    corpus, body = m.group(1) or "", m.group(2)
    filters, concepts, fields, exclusions = [], [], [], []
    for cond in _top(body, " and "):
        h = HAS.match(cond)
        if not h:
            filters.append(cond)
            continue
        field, search = h.group(1), strip_outer(h.group(2))
        parts = _top(search, " NOT ")
        main, excl = parts[0], parts[1:]
        exclusions += [(field, strip_outer(x)) for x in excl]
        main = strip_outer(main)
        new = [main] if len(_top(main, " OR ")) > 1 else [strip_outer(x) for x in _top(main, " AND ")]
        concepts += new
        fields += [field] * len(new)
    return {"corpus": corpus.strip(), "filters": filters, "concepts": concepts, "fields": fields, "exclusions": exclusions}
