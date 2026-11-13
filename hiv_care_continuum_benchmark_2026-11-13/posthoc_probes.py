"""Post-hoc probes explaining the two largest miss patterns. Explicit live runner; archived.

1. Children block: for matched articles failing it in title-abstract, fetch PubMed MeSH
   (NCBI efetch, free) and record whether they carry an age heading that the review's
   PubMed concept searched (Child, Adolescent, Young Adult, Pediatrics; Child also covers
   Child, Preschool when exploded). Infant and Infant, Newborn are recorded separately,
   since the review's strategy did not search them.
3. Without the age block: the frozen arm A string minus its children-and-adolescents block,
   count only (per_page 1), with recall computed offline from the facet intersections.
2. HIV block: whether articles failing it contain the single word "immunodeficiency"
   (the Embase chain assumes "immune deficiency" as two words). OQL, restricted to IDs.
4. Translation sensitivity of the age block: OQL stems bare `child` but does not reduce the
   irregular plural "children" to it. Among articles failing the block, which contain
   "children", and which contain infant or youth terms the source strategy never had.
   Recall with these is computed offline from the facet intersections.
Explanatory only; no repaired query replaces a frozen arm.
"""
import json
import re
import time
import urllib.request
from datetime import datetime, timezone

import run_test as rt

ROOT = rt.ROOT
SEARCHED = {"Child", "Child, Preschool", "Adolescent", "Young Adult", "Pediatrics"}
INFANT = {"Infant", "Infant, Newborn"}


def efetch(pmids):
    dest = ROOT / "archives/diagnostics/pubmed_mesh_efetch.json"
    if dest.exists():
        return json.loads(dest.read_text())["response_xml"]
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id=" + ",".join(pmids)
    started = datetime.now(timezone.utc).isoformat()
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": rt.UA}), timeout=120) as r:
        raw = r.read().decode()
    # keep only PMIDs and MeSH descriptors (no abstracts)
    slim = "\n".join(re.findall(r"<PMID Version=\"1\">\d+</PMID>|<DescriptorName[^>]*>[^<]+</DescriptorName>", raw))
    dest.write_text(json.dumps({"url": url, "requested_utc": started, "status": 200, "response_xml": slim}, indent=1))
    time.sleep(0.4)
    return slim


def main():
    rt.pilot_credentials.load_key()
    src = {r["ref_id"]: r for r in json.loads((ROOT / "results/benchmark_source.json").read_text())["records"]}
    m = json.loads((ROOT / "results/benchmark_matches.json").read_text())["records"]
    fac = {k: set(v["matching_ids"]) for k, v in json.loads((ROOT / "results/facet_diagnostics.json").read_text())["facets"].items()}
    child_fail = [r for r in m if r["openalex_id"] not in fac["ta_children_and_adolescents"]]
    pm = {r["ref_id"]: src[r["ref_id"]]["pmid"] for r in child_fail}
    if src["HIV-098"]["pmid"] and "HIV-098" in pm:
        pm["HIV-098"] = None   # the cited PMID is the 1980 chlamydia paper, not the included article
    xml = efetch(sorted({p for p in pm.values() if p}))
    mesh, cur = {}, None
    for line in xml.splitlines():
        if line.startswith("<PMID"):
            cur = re.sub(r"<[^>]+>", "", line)
            mesh[cur] = []
        elif cur:
            mesh[cur].append(re.sub(r"<[^>]+>", "", line))
    rows = []
    for r in child_fail:
        p = pm[r["ref_id"]]
        h = set(mesh.get(p, [])) if p else None
        rows.append({"ref_id": r["ref_id"], "study_label": r["study_label"], "pmid": p,
                     "searched_age_mesh": sorted(h & SEARCHED) if h is not None else None,
                     "infant_mesh": sorted(h & INFANT) if h is not None else None})
    hiv_fail = sorted(r["openalex_id"] for r in m if r["openalex_id"] not in fac["ta_hiv"])
    q = rt.post("diagnostics/probe_immunodeficiency", {"oql": f"get works where openalex id is ({' or '.join(hiv_fail)}) and title-abstract has \"immunodeficiency\"", "per_page": 100, "select": "id"})
    import build_queries as bq
    qa, b = bq.build()
    no_age = qa["A_title_abstract"].replace(f" and title-abstract has {b['blocks']['Children and adolescents']}", "")
    assert no_age != qa["A_title_abstract"]
    na = rt.post("diagnostics/probe_A_without_age_block_count", {"oql": no_age, "per_page": 1, "select": "id"})
    keep = fac["ta_hiv"] & fac["ta_care_continuum_outcomes"] & fac["ta_countries_in_eastern_and_southern_africa"] & fac["date_window"]
    fail_ids = sorted(r["openalex_id"] for r in child_fail)
    words = {}
    for name, cond in [("children_exact", 'title-abstract has "children"'), ("child_bare", "title-abstract has child"),
                       ("children_bare", "title-abstract has children"),
                       ("infant_youth_etc", 'title-abstract has ("infant*" OR "neonat*" OR "newborn*" OR "youth*" OR "young people" OR "baby" OR "babies" OR "exposed infant*")')]:
        r = rt.post(f"diagnostics/probe_child_failures_{name}", {"oql": f"get works where openalex id is ({' or '.join(fail_ids)}) and {cond}", "per_page": 100, "select": "id"})
        words[name] = sorted(x["id"].rsplit("/", 1)[-1] for x in r["results"])
    A = set(json.loads((ROOT / "results/run_observations.json").read_text())["arms"]["A_title_abstract"]["recovered_ids"])
    ch, inf = set(words["children_exact"]), set(words["infant_youth_etc"])
    sens = {"failing_age_block": len(fail_ids), **{k: len(v) for k, v in words.items()},
            "A_recovered_if_children_matched": len(A | (ch & keep)),
            "A_recovered_if_children_and_infant_youth_terms_matched": len(A | ((ch | inf) & keep)),
            "failing_with_neither": len([i for i in fail_ids if i not in ch | inf]), "ids": words}
    out = {"age_block_translation_sensitivity": sens, "A_without_age_block": {"count": na["meta"]["count"], "recovered_offline": len(keep)},
           "children_block_failures": rows,
           "children_summary": {"failing": len(rows), "with_pmid": sum(1 for x in rows if x["pmid"]),
                                "with_searched_age_mesh": sum(1 for x in rows if x["searched_age_mesh"]),
                                "infant_mesh_only": sum(1 for x in rows if x["infant_mesh"] and not x["searched_age_mesh"]),
                                "no_age_mesh": sum(1 for x in rows if x["pmid"] and not x["searched_age_mesh"] and not x["infant_mesh"])},
           "hiv_block_failures": hiv_fail,
           "hiv_failures_with_immunodeficiency": sorted(x["id"].rsplit("/", 1)[-1] for x in q["results"])}
    (ROOT / "results/posthoc_probes.json").write_text(json.dumps(out, indent=1) + "\n")
    print(out["A_without_age_block"], out["children_summary"], len(hiv_fail), len(out["hiv_failures_with_immunodeficiency"]))


if __name__ == "__main__":
    main()
