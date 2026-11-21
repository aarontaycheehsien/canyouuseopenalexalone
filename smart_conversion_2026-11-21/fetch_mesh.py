"""R3: resolve every published heading to MeSH and collect its terms (network; archived).

    python3 fetch_mesh.py          # writes vocab/mesh_resolved.json

For each heading: mapping (R3 order: descriptor label, then entry term, else unmapped), the
descriptor's terms, and for exploded headings the narrower descriptors by tree level (breadth
first, stopping once the 200-term cap is passed, since deeper levels cannot be used).
"""
import json
from pathlib import Path

import netlib
from specs import SPECS
from terms import mesh_term_forms

ROOT = Path(__file__).resolve().parent
API = "https://id.nlm.nih.gov/mesh"
CAP = 200
PFX = "PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#> PREFIX mesh: <http://id.nlm.nih.gov/mesh/> "


def sparql(q):
    st, r = netlib.get("mesh", API + "/sparql", {"query": PFX + q, "format": "JSON", "year": "current", "limit": 1000})
    assert st == 200, (st, q)
    return r["results"]["bindings"]


def uid(uri):
    return uri.rsplit("/", 1)[-1]


def lookup(kind, label):
    """Exact, case-insensitive label match among MeSH descriptors or terms. The API's exact match is
    case-sensitive, so the label is tried as given, in title case, sentence case and lower case;
    then a 'contains' search (whose first 50 hits may miss a common term) is filtered."""
    variants = [label, label.title(), label[:1].upper() + label[1:].lower(), label.lower()]
    for v in dict.fromkeys(variants):
        st, r = netlib.get("mesh", f"{API}/lookup/{kind}", {"label": v, "match": "exact", "limit": 50})
        assert st == 200, (st, v)
        hits = [x for x in r if x["label"].lower() == label.lower()]
        if hits:
            return hits
    st, r = netlib.get("mesh", f"{API}/lookup/{kind}", {"label": label, "match": "contains", "limit": 50})
    assert st == 200, (st, label)
    return [x for x in r if x["label"].lower() == label.lower()]


def descriptor_terms(d):
    st, r = netlib.get("mesh", f"{API}/lookup/details", {"descriptor": d})
    assert st == 200, d
    return [t["label"] for t in r["terms"]]


def descriptor_label(d):
    b = sparql(f"SELECT ?l WHERE {{ mesh:{d} rdfs:label ?l }}".replace("SELECT", "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> SELECT"))
    return b[0]["l"]["value"]


def children(d):
    q = f"PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> SELECT DISTINCT ?c WHERE {{ ?c meshv:broaderDescriptor mesh:{d} }}"
    return sorted(uid(b["c"]["value"]) for b in sparql(q))


def resolve(vocab, label):
    if vocab in ("mesh", "mesh_pt"):
        hits = lookup("descriptor", label)
        assert hits, f"MeSH descriptor not found: {label}"
        return {"mapping": "mesh_descriptor", "descriptor": uid(hits[0]["resource"])}
    hits = lookup("descriptor", label)
    if hits:
        return {"mapping": "mesh_descriptor_label", "descriptor": uid(hits[0]["resource"])}
    for t in lookup("term", label):
        q = (f"SELECT DISTINCT ?d WHERE {{ ?d meshv:preferredConcept|meshv:concept ?c . "
             f"?c meshv:preferredTerm|meshv:term mesh:{uid(t['resource'])} . ?d a meshv:TopicalDescriptor }}")
        ds = sorted(uid(b["d"]["value"]) for b in sparql(q))
        if ds:
            return {"mapping": "mesh_entry_term", "descriptor": ds[0], "via_term": t["label"]}
    return {"mapping": "unmapped", "descriptor": None}


def main():
    out = {}
    for bench, spec in SPECS.items():
        for g in spec["groups"]:
            for vocab, label, explode, src in g["headings"]:
                key = f"{vocab}|{label}|{explode}"
                if key in out:
                    continue
                rec = {"vocab": vocab, "label": label, "explode": explode, **resolve(vocab, label)}
                if rec["descriptor"]:
                    d = rec["descriptor"]
                    rec["descriptor_label"] = descriptor_label(d)
                    levels = [[{"descriptor": d, "terms": descriptor_terms(d)}]]
                    if explode:
                        seen, frontier, n = {d}, [d], len(mesh_term_forms(levels[0][0]["terms"]))
                        while frontier and n <= CAP:
                            nxt = sorted({c for f in frontier for c in children(f)} - seen)
                            if not nxt:
                                break
                            seen |= set(nxt)
                            lvl = [{"descriptor": c, "terms": descriptor_terms(c)} for c in nxt]
                            levels.append(lvl)
                            n = len(mesh_term_forms([t for L in levels for x in L for t in x["terms"]]))
                            frontier = nxt
                    rec["levels"] = levels
                out[key] = rec
                print(f"{key:70s} {rec['mapping']:22s} {rec.get('descriptor_label','')[:40]:40s} levels={len(rec.get('levels', []))}", flush=True)
    (ROOT / "vocab").mkdir(exist_ok=True)
    (ROOT / "vocab/mesh_resolved.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
