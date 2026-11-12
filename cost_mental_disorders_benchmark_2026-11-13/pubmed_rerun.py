"""Post-hoc reference ceiling: the published PubMed strings re-run in PubMed today,
restricted to the benchmark PMIDs (free NCBI E-utilities). Archived under archives/pubmed/.

PubMed's indexing has changed since 2019, so this is today's PubMed, not the authors'
result set. It shows how many benchmark articles the published PubMed strategy itself
can find, against which the OpenAlex translation can be read.
"""
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    p = json.loads((ROOT / "source_search_strategy.json").read_text())["paragraphs"]
    text = {p[i]: p[i + 1] for i in range(len(p) - 1)}
    cost = text["Cost-of-illness terms: #1"]
    restr = text["Restriction of time, to human studies and avoiding RCT/trials: #2"].replace("“", '"').replace("”", '"')
    groups = [v for k, v in text.items() if k.startswith("# ")]
    assert len(groups) == 9
    full = f"({cost}) AND {restr} AND (" + " OR ".join(groups) + ")"
    raw = json.loads((ROOT / "results/matching_raw.json").read_text())
    m = {r["ref_id"]: r for r in json.loads((ROOT / "results/benchmark_matches.json").read_text())["records"]}
    pmid = {}
    for r in raw:
        oid = m[r["ref_id"]]["openalex_id"]
        for c in r["candidates"] + r.get("second_pass_candidates", []):
            if c["openalex_id"] == oid and c.get("pmid"):
                pmid[r["ref_id"]] = str(c["pmid"]).rsplit("/", 1)[-1]
    pm = sorted(set(pmid.values()))
    hits, calls = set(), []
    (ROOT / "archives/pubmed").mkdir(parents=True, exist_ok=True)
    for i in range(0, len(pm), 100):
        q = f"({full}) AND (" + " OR ".join(x + "[uid]" for x in pm[i:i + 100]) + ")"
        body = urllib.parse.urlencode({"db": "pubmed", "retmode": "json", "retmax": 200, "term": q}).encode()
        started = datetime.now(timezone.utc).isoformat()
        res = json.load(urllib.request.urlopen(urllib.request.Request("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", data=body), timeout=120))
        (ROOT / f"archives/pubmed/esearch_batch_{i // 100 + 1}.json").write_text(json.dumps({"requested_utc": started, "term": q, "response": res}, indent=1))
        r = res["esearchresult"]
        hits |= set(r.get("idlist", []))
        calls.append({"batch": i // 100 + 1, "count": r.get("count"), "errors": r.get("errorlist"), "warnings": r.get("warninglist")})
        time.sleep(0.5)
    rows = [{"ref_id": k, "pmid": pmid.get(k), "pubmed_strategy_today": pmid.get(k) in hits} for k in m]
    out = {"note": __doc__.strip(), "references_with_pmid": len(pmid), "calls": calls,
           "retrieved_by_pubmed_strategy_today": sum(r["pubmed_strategy_today"] for r in rows), "rows": rows}
    (ROOT / "results/pubmed_strategy_rerun.json").write_text(json.dumps(out, indent=1) + "\n")
    print({k: v for k, v in out.items() if k not in ("rows", "note")})


if __name__ == "__main__":
    main()
