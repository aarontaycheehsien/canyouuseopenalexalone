"""Build the frozen OQL arms from Haw et al. (2025), Supplementary Table 1 (Embase column).

Standard library only; no network. `python3 build_queries.py [--check]`.

Table S1 gives Embase and PubMed strings for nine concepts, combined as
[HIV] AND [Children and adolescents] AND ([HIV care continuum] OR [Diagnosis] OR
[Antiretroviral therapy] OR [Linkage to care] OR [Retention in care] OR
[Viral load testing] OR [Adherence]) AND [Countries] AND [publication from 2010].

Source column. The Embase free-text lines are translated, not the PubMed ones: they
carry explicit fields (:ab,ti,kw) and valid proximity (NEAR/n), whereas the PubMed
column uses single quotes (not a PubMed phrase operator) and "n1"/"n2" (not PubMed
proximity syntax), so it cannot be run as printed. Emtree (/exp) and MeSH lines are
omitted: OpenAlex has no equivalent.

Mechanical rules:
  * an unquoted single word without * stays bare (OQL stems it);
  * a term with *, or a term in single quotes, becomes an exact quoted OQL string
    (wildcards kept; a quoted multiword term is an exact phrase);
  * NEAR/n becomes OQL proximity "within n words of each other". OQL proximity takes
    no OR groups and no mix of bare and quoted operands, so (a OR b) NEAR/n (c OR d)
    is expanded to every pair, and a pair is quoted throughout if either operand is
    quoted or truncated. A chain x NEAR/i y NEAR/j z becomes (x,y within i) AND
    (y,z within j);
  * Embase precedence (NEAR > AND > OR) is kept with explicit parentheses;
  * dates: publication date 2010-01-01 to 2023-06-01 (the review's stated window);
  * no language or type limit (the review searched "articles searchable using English
    keywords" and excluded conference abstracts at screening).
Arm A: title-abstract. Arm B: the identical string on title-abstract-keywords, the
nearest OpenAlex field to Embase's ab,ti,kw (OpenAlex keywords are assigned by
OpenAlex, not by authors).
"""
import hashlib
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE_FROM, DATE_TO = "2010-01-01", "2023-06-01"


def t(x):
    """One Embase term: 'quoted' or wildcard -> exact quoted; bare word -> bare."""
    if x.startswith("'") or "*" in x:
        return '"' + x.strip("'") + '"'
    assert " " not in x and "-" not in x, x
    return x


def near(a, b, n):
    """(a1 OR a2 ...) NEAR/n (b1 OR b2 ...) expanded to pairs."""
    out = []
    for x, y in itertools.product(a, b):
        tx, ty = t(x), t(y)
        if tx.startswith('"') or ty.startswith('"'):
            tx, ty = '"' + tx.strip('"') + '"', '"' + ty.strip('"') + '"'
        out.append(f"({tx} and {ty} within {n} words of each other)")
    return out


def chain(parts, dists):
    """x NEAR/i y NEAR/j z -> AND of adjacent pairwise proximities (each side may be an OR list)."""
    links = []
    for (a, b), n in zip(zip(parts, parts[1:]), dists):
        links.append("(" + " OR ".join(near(a, b, n)) + ")")
    return "(" + " AND ".join(links) + ")"


def OR(*xs):
    return "(" + " OR ".join(xs) + ")"


def AND(*xs):
    return "(" + " AND ".join(xs) + ")"


def terms(*xs):
    return [t(x) for x in xs]


def concepts():
    c = {}
    c["HIV"] = OR(t("hiv*"),
                  chain([["'human immun*'"], ["'deficien*'"], ["'virus'"]], [1, 1]),
                  chain([["'acquired'"], ["'immun*'"], ["'deficien*'"], ["'syndrome'"]], [1, 1, 1]))
    c["Children and adolescents"] = OR(*terms("child", "pediatric*", "paediatric*", "adolesc*", "teen*"),
                                       AND(t("'young*'"), t("'adult*'")))
    c["HIV care continuum"] = OR(*near(["continuum", "continuity", "cascade", "standard"], ["care", "'health service*'"], 2),
                                 *near(["'health'"], ["'quality'"], 2), *near(["'standard'"], ["'care'"], 2),
                                 t("'refer*'"), *near(["'health*'"], ["'access*'"], 2), t("'consult*'"))
    c["Diagnosis"] = OR(*near(["'hiv'"], ["'point of care'", "'test*'", "'diag*'"], 1))
    c["Antiretroviral therapy"] = OR(*near(["antiretrovir*", "'anti retrovir*'", "'anti-retrovir*'"], ["therap*", "treat*", "agent*"], 1))
    c["Linkage to care"] = OR(
        AND(t("care"), OR(*terms("link*", "enrol*", "consult*", "access*", "engag*", "connect*", "enter*", "entry",
                                 "entrance", "initiat*", "integra*", "attend*"))),
        AND(OR(t("treatment"), t("therapy")),
            OR(*terms("rapid", "'same day'", "'fast track'", "universal", "'test and treat'", "'treat all'", "early",
                      "accelerat*", "instant", "prompt", "fast", "quick", "expedit*", "immediate"))))
    c["Retention in care"] = AND(t("care"), OR(t("'retain'"), t("'retention'")))
    c["Viral load testing"] = chain([["viral", "virus", "virologic*"], ["load"],
                                     ["undetect*", "monitor*", "test*", "fail*", "resist*", "suppress*", "success",
                                      "response", "level", "concentration", "sustain"]], [1, 2])
    c["Adherence"] = OR(*terms("adheren*", "complian*"))
    c["Countries in Eastern and Southern Africa"] = OR(
        *terms("angola", "botswana", "comoros", "eritrea", "eswatini", "swaziland", "ethiopia", "kenya", "lesotho",
               "madagascar", "malawi", "mauritius", "mozambique", "namibia", "rwanda", "seychelles", "'south africa'",
               "'south sudan'", "uganda", "tanzania", "zambia", "zimbabwe"),
        AND(OR(t("east*"), t("south*")), t("africa")))
    return c


SOURCE_TOKENS = ["hiv*", "'human immun*'", "'deficien*'", "'syndrome'", "pediatric*", "paediatric*", "adolesc*", "teen*",
                 "'young*'", "'adult*'", "continuum", "cascade", "'health service*'", "'refer*'", "'access*'",
                 "'consult*'", "'point of care'", "'test*'", "'diag*'", "'anti retrovir*'", "'anti-retrovir*'",
                 "agent*", "entrance", "'same day'", "'fast track'", "'test and treat'", "'treat all'", "expedit*",
                 "'retain'", "'retention'", "virologic*", "undetect*", "concentration", "sustain", "adheren*",
                 "complian*", "eswatini", "seychelles", "'south africa'", "'south sudan'", "east*", "south*"]


def build():
    src = json.loads((ROOT / "source_search_strategy.json").read_text())
    rows = {r[0]: r[1] for r in src["table_S1"][1:]}
    emb = " ".join(rows.values())
    missing = [x for x in SOURCE_TOKENS if x not in emb]
    assert not missing, missing   # every hand-transcribed token is in the Embase column
    c = concepts()
    assert set(c) <= set(rows), set(c) - set(rows)
    outcome = OR(*(c[k] for k in ["HIV care continuum", "Diagnosis", "Antiretroviral therapy", "Linkage to care",
                                  "Retention in care", "Viral load testing", "Adherence"]))
    blocks = {"HIV": c["HIV"], "Children and adolescents": c["Children and adolescents"], "Care continuum outcomes": outcome,
              "Countries in Eastern and Southern Africa": c["Countries in Eastern and Southern Africa"]}
    date = f"date >= ({DATE_FROM}) and date <= ({DATE_TO})"
    queries = {}
    for arm, field in [("A_title_abstract", "title-abstract"), ("B_title_abstract_keywords", "title-abstract-keywords")]:
        queries[arm] = f"get works where {date} and " + " and ".join(f"{field} has {b}" for b in blocks.values())
    return queries, {"blocks": blocks, "outcome_concepts": {k: c[k] for k in c if k not in blocks}}


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
