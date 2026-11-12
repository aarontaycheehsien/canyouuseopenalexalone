"""Post-hoc, descriptive: how much of each arm's volume is PubMed-indexed, and by domain.

The first group-by attempt kept the echoed publication-date sort and was refused
(HTTP 400, archived as *_by_domain.json); the retry drops sort_by only."""
import json
import run_test as rt

def main():
    rt.pilot_credentials.load_key()
    out = {"note": "Post-hoc descriptive decomposition of result volume; not part of the frozen outcomes."}
    for arm in ("A_faithful_title_abstract", "B_title_abstract_keywords"):
        oqo = json.loads((rt.ROOT / f"archives/{arm}/unrestricted_cursor_001.json").read_text())["response"]["meta"]["x_query"]["oqo"]
        o1 = json.loads(json.dumps(oqo)); o1["filter_rows"].append({"column_id": "has_pmid", "value": True})
        r = rt.post(f"decomposition/{arm}_pubmed_indexed", {"oqo": o1, "per_page": 1, "select": "id"})
        o2 = json.loads(json.dumps(oqo)); o2.pop("sort_by", None); o2["group_by"] = [{"column_id": "primary_topic.domain.id"}]
        g = rt.post(f"decomposition/{arm}_by_domain_unsorted", {"oqo": o2})
        out[arm] = {"pubmed_indexed": r["meta"]["count"],
                    "by_domain": {x.get("key_display_name") or x.get("key"): x["count"] for x in g.get("group_by") or g.get("results") or []}}
        print(arm, out[arm])
    (rt.ROOT / "results/volume_decomposition.json").write_text(json.dumps(out, indent=1) + "\n")

if __name__ == "__main__":
    main()
