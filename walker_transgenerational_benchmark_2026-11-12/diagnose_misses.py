"""Post-hoc clause diagnostics for benchmark records missed by the frozen arms.

Run only after results/run_observations.json exists. Every query is restricted
to the missed IDs, so it explains failures; it is not a retrieval result and
no repaired query replaces a frozen arm. Abstracts are read through free
single-entity lookups and stored only as term flags, not as text.
"""
import json
import re

import run_test as rt

ROOT = rt.ROOT


def main():
    rt.pilot_credentials.load_key()
    obs = json.loads((ROOT / "results" / "run_observations.json").read_text())
    matches = json.loads((ROOT / "results" / "benchmark_matches.json").read_text())["records"]
    blocks = json.loads((ROOT / "queries" / "blocks.json").read_text())
    found = set(obs["arms"]["A_faithful_title_abstract"]["recovered_ids"]) | set(obs["arms"]["B_title_abstract_keywords"]["recovered_ids"])
    missed = sorted({m["openalex_id"] for m in matches if m["openalex_id"] not in found})
    idlist = "(" + " or ".join(missed) + ")"
    f_terms, gen_terms = re.fullmatch(r"\((\(.*?\)) AND (\(.*\))\)", blocks["#3"]).groups()
    clauses = {"date_ceiling": "date <= (2016-11-30)"}
    for field in ("title-abstract", "title-abstract-keywords", "fulltext"):
        fld = "full text" if field == "fulltext" else field
        for k in ("#1", "#2", "#3", "#4", "#5"):
            clauses[f"{field}:{k}"] = f"{fld} has {blocks[k]}"
        clauses[f"{field}:#3_F_terms_only"] = f"{fld} has {f_terms}"
        clauses[f"{field}:#3_generation_terms_only"] = f"{fld} has {gen_terms}"
    out = {"missed_ids": missed, "clauses": {}, "records": {}}
    for name, cond in clauses.items():
        label = "diagnostics/" + re.sub(r"[^A-Za-z0-9]+", "_", name)
        r = rt.post(label, {"oql": f"get works where openalex id is {idlist} and {cond}", "per_page": 100, "select": "id"})
        hits = sorted(x["id"].rsplit("/", 1)[-1] for x in r["results"])
        assert r["meta"]["count"] == len(hits)
        out["clauses"][name] = {"condition": cond, "matching_missed_ids": hits}
        print(name, len(hits), flush=True)
    import urllib.request
    probe = re.compile(r"transgeneration|trans-generation|multigeneration|multi-generation|intergeneration|"
                       r"inter-generation|\bf ?\(?[2-9]\)?\b|\bf ?\(?10\)?\b|generation|offspring|progeny|grand", re.I)
    for w in missed:
        with urllib.request.urlopen(urllib.request.Request(
                f"https://api.openalex.org/works/{w}?select=id,display_name,abstract_inverted_index,keywords,publication_date,has_fulltext",
                headers={"User-Agent": rt.UA}), timeout=60) as resp:
            rec = json.loads(resp.read().decode())
        inv = rec.get("abstract_inverted_index") or {}
        words = sorted(((p, t) for t, ps in inv.items() for p in ps))
        abstract = " ".join(t for _, t in words)
        out["records"][w] = {
            "title": rec.get("display_name"), "publication_date": rec.get("publication_date"),
            "has_abstract": bool(inv), "abstract_word_count": len(words), "has_fulltext": rec.get("has_fulltext"),
            "keywords": [k.get("display_name") for k in rec.get("keywords") or []],
            "title_term_hits": sorted({m.group(0).lower() for m in probe.finditer(rec.get("display_name") or "")}),
            "abstract_term_hits": sorted({m.group(0).lower() for m in probe.finditer(abstract)}),
        }
    (ROOT / "results" / "clause_diagnostics.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
