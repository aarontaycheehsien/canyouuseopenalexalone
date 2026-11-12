"""Protocol execution check 4: cursor continuation by POST beyond page 1 (one page per arm)."""
import json
import run_test as rt

def main():
    rt.pilot_credentials.load_key()
    out = {}
    for f in sorted((rt.ROOT / "queries").glob("*.oql")):
        arm = f.stem
        first = json.loads((rt.ROOT / f"archives/{arm}/unrestricted_cursor_001.json").read_text())
        body = dict(first["request"]["body"], cursor=first["response"]["meta"]["next_cursor"])
        v = rt.post(f"{arm}/unrestricted_cursor_002", body)
        p1 = {x["id"] for x in first["response"]["results"]}; p2 = {x["id"] for x in v["results"]}
        out[arm] = {"page2_rows": len(p2), "count_unchanged": v["meta"]["count"] == first["response"]["meta"]["count"],
                    "pages_disjoint": not (p1 & p2), "next_cursor_present": bool(v["meta"].get("next_cursor"))}
        print(arm, out[arm])
    (rt.ROOT / "results/cursor_check.json").write_text(json.dumps(out, indent=1) + "\n")

if __name__ == "__main__":
    main()
