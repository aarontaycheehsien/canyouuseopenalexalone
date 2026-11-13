"""Post-hoc: would the omitted MEDLINE lines have caught arm A's misses? Explicit live runner.

For each matched reference missed by arm A, fetch PubMed MeSH descriptors and publication
types (NCBI efetch, free; only PMIDs, descriptors and types are archived, no abstracts) and
test, for each block it fails in title-abstract, the omitted lines for that block:
  physical activity: exp exercise/ or exp physical exertion/ or exp physical fitness/ (line 2;
    tested here on the descriptor and its MeSH tree numbers, so the explosion is honoured);
  primary care: Family Practice/, General Practitioners/, exp community health nursing/,
    public health nursing/, Community Health Services/, Primary Health Care/, Physical
    Therapists/ (lines 24, 28, 31, 34, 38);
  RCT filter: randomized controlled trial.pt. (line 42).
Explanatory only; no repaired query replaces a frozen arm.
"""
import json
import re
import time
import urllib.request
from datetime import datetime, timezone

import run_test as rt

ROOT = rt.ROOT
PC_EXACT = {"Family Practice", "General Practitioners", "Public Health Nursing", "Community Health Services", "Primary Health Care", "Physical Therapists"}
PC_TREE = ("N02.421.143.143",)                     # Community Health Nursing (exploded)
PA_TREE = ("G11.427.410.698", "G11.427.410.701", "G11.427.410.702")  # Exercise, Physical Exertion, Physical Fitness (exploded)


def fetch(label, url):
    dest = ROOT / f"archives/diagnostics/{label}.json"
    if dest.exists():
        return json.loads(dest.read_text())["response_slim"]
    started = datetime.now(timezone.utc).isoformat()
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": rt.UA}), timeout=120) as r:
        raw = r.read().decode()
    time.sleep(0.4)
    return raw, dest, started, url


def main():
    m = json.loads((ROOT / "results/benchmark_matches.json").read_text())["records"]
    src = {r["ref_id"]: r for r in json.loads((ROOT / "results/benchmark_source.json").read_text())["records"]}
    fac = {k: set(v["matching_ids"]) for k, v in json.loads((ROOT / "results/facet_diagnostics.json").read_text())["facets"].items()}
    A = set(json.loads((ROOT / "results/run_observations.json").read_text())["arms"]["A_title_abstract"]["recovered_ids"])
    missed = [r for r in m if r["openalex_id"] and r["openalex_id"] not in A]
    pm = {}
    for r in missed:
        p = src[r["ref_id"]]["pmid"]
        if not p:
            arch = ROOT / f"archives/matching/oa_doi_{r['ref_id']}.json"
            ids = json.loads(arch.read_text())["response"].get("ids", {}) if arch.exists() else {}
            p = (ids.get("pmid") or "").rsplit("/", 1)[-1] or None
        pm[r["ref_id"]] = p
    pmids = sorted({p for p in pm.values() if p})
    got = fetch("pubmed_mesh_pt_efetch", "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id=" + ",".join(pmids))
    if isinstance(got, tuple):
        raw, dest, started, url = got
        recs = {}
        for art in re.findall(r"<PubmedArticle>.*?</PubmedArticle>", raw, re.S):
            p = re.search(r'<PMID Version="1">(\d+)</PMID>', art).group(1)
            recs[p] = {"mesh_ui": re.findall(r'<DescriptorName UI="(D\d+)"[^>]*>([^<]+)</DescriptorName>', art),
                       "publication_types": re.findall(r"<PublicationType[^>]*>([^<]+)</PublicationType>", art)}
        uis = sorted({u for v in recs.values() for u, _ in v["mesh_ui"]})
        trees = {}
        for u in uis:
            with urllib.request.urlopen(urllib.request.Request(f"https://id.nlm.nih.gov/mesh/{u}.json", headers={"User-Agent": rt.UA}), timeout=60) as r:
                d = json.loads(r.read())
            tn = d.get("treeNumber") or []
            tn = tn if isinstance(tn, list) else [tn]
            trees[u] = [t.rsplit("/", 1)[-1] for t in tn]
            time.sleep(0.2)
        got = {"records": recs, "tree_numbers": trees}
        dest.write_text(json.dumps({"url": url, "requested_utc": started, "status": 200, "tree_source": "https://id.nlm.nih.gov/mesh/{UI}.json", "response_slim": got}, indent=1))
    recs, trees = got["records"], got["tree_numbers"]
    rows = []
    for r in missed:
        i, p = r["openalex_id"], pm[r["ref_id"]]
        fails = [b for b in ("physical_activity", "primary_care", "rct_filter") if i not in fac[f"ta_{b}"]]
        info = recs.get(p) if p else None
        rescued = {}
        if info:
            names = {n for _, n in info["mesh_ui"]}
            tns = [t for u, _ in info["mesh_ui"] for t in trees.get(u, [])]
            rescued = {"physical_activity": any(t.startswith(PA_TREE) for t in tns),
                       "primary_care": bool(names & PC_EXACT) or any(t.startswith(PC_TREE) for t in tns),
                       "rct_filter": "Randomized Controlled Trial" in info["publication_types"]}
        rows.append({"ref_id": r["ref_id"], "study_label": r["study_label"], "pmid": p, "fails": fails,
                     "omitted_lines_would_pass": {b: rescued.get(b) for b in fails} if info else None,
                     "mesh": sorted({n for _, n in info["mesh_ui"]}) if info else None,
                     "publication_types": info["publication_types"] if info else None})
    out = {"arm_A_missed": rows,
           "rescued_by_omitted_lines": sum(1 for x in rows if x["omitted_lines_would_pass"] and all(x["omitted_lines_would_pass"].values())),
           "not_in_pubmed": [x["ref_id"] for x in rows if not x["pmid"]]}
    (ROOT / "results/posthoc_probes.json").write_text(json.dumps(out, indent=1) + "\n")
    for x in rows:
        print(x["ref_id"], x["study_label"], x["pmid"], x["omitted_lines_would_pass"])
    print("rescued", out["rescued_by_omitted_lines"], "of", len(rows), "not in PubMed", out["not_in_pubmed"])


if __name__ == "__main__":
    main()
