"""R4: look up OpenAlex keywords for every topic-concept term (network; archived; no work titles).

    python3 fetch_keywords.py      # writes vocab/keyword_matches.json

A keyword matches a term when one of its alternative labels equals the term (lower-cased,
Porter-stemmed words) and its display name does not. Uses the uncapped (200) term lists, so the
lookups cover every cap level a size reduction might use.
"""
import json
from pathlib import Path

import netlib
from build import groups_for, r4_terms
from specs import SPECS
from terms import stem_key

ROOT = Path(__file__).resolve().parent


def main():
    terms = sorted({t for n in SPECS for g in groups_for(n, 200)[1] for t in r4_terms(g)})
    print(len(terms), "terms", flush=True)
    out = {}
    for i, t in enumerate(terms):
        st, r = netlib.get("keywords", "https://api.openalex.org/keywords",
                           {"search": t, "per_page": 25, "select": "id,display_name,display_name_alternatives"})
        assert st == 200, (st, t)
        k = stem_key(t)
        hits = [{"id": x["id"].rsplit("/", 1)[-1], "display_name": x["display_name"]}
                for x in r["results"]
                if stem_key(x["display_name"]) != k and any(stem_key(a) == k for a in (x.get("display_name_alternatives") or []))]
        if hits:
            out[t] = hits
        if i % 200 == 0:
            print(i, flush=True)
    (ROOT / "vocab/keyword_matches.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(len(out), "terms with keyword matches")


if __name__ == "__main__":
    main()
