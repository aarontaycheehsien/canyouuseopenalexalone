"""Development helper: free validation then count only (per_page 1); archives under <bench>/development/.
Results are never printed; only counts and validation errors."""
import json, os, sys, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent)); import pilot_credentials
pilot_credentials.load_key()
H = {"Content-Type": "application/json", "Authorization": "Bearer " + os.environ["OPENALEX_API_KEY"]}

def post(url, body):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=json.dumps(body).encode(), headers=H), timeout=180) as r:
            return r.status, json.loads(r.read()), r.headers.get("x-ratelimit-remaining-usd")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}"), None

def run(bench, label, oql):
    d = Path(bench) / "development"; d.mkdir(exist_ok=True)
    st, v, _ = post("https://api.openalex.org/query", {"oql": oql})
    ok = st == 200 and v.get("validation", {}).get("valid")
    rec = {"label": label, "oql": oql, "validated_utc": datetime.now(timezone.utc).isoformat(), "valid": bool(ok)}
    if not ok:
        rec["errors"] = v.get("validation", {}).get("errors") or v
        print(label, "INVALID", json.dumps(rec["errors"])[:400])
    else:
        st, c, rem = post("https://api.openalex.org/", {"oql": oql, "per_page": 1, "select": "id"})
        rec["count"] = c["meta"]["count"]
        print(f"{label:40s} {rec['count']:>9,}  budget {rem}")
    (d / f"{label}.json").write_text(json.dumps(rec, indent=1))
    return rec

if __name__ == "__main__":
    bench = sys.argv[1]
    for f in sorted((Path(bench) / "queries").glob("*.oql")):
        run(bench, "dev1_" + f.stem, f.read_text().strip())
