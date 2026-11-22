"""Validate, size-reduce and count the smart arms (network; archived). No benchmark membership.

    python3 validate.py

For each review: free OQL validation of the smart query, applying PROTOCOL.md size reductions in
order (explosion cap 100, 50, 0; then no keyword clauses) until valid; then unrestricted counts of
the smart query, its base_equivalence rendering and the frozen base arm. Writes queries/caps.json
and queries/validation_report.json; rebuild with build.py afterwards.
"""
import json
from pathlib import Path

import netlib
from build import render
from specs import SPECS

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
STEPS = [(200, True), (100, True), (50, True), (0, True), (0, False)]


def validate(oql):
    st, r = netlib.post("validate", "https://api.openalex.org/query", {"oql": oql})
    v = (r or {}).get("validation") or {}
    return st == 200 and bool(v.get("valid")), {"status": st, "errors": v.get("errors") or (r if st != 200 else []),
                                                  "warnings": v.get("warnings", [])}


def count(oql):
    """A persistent timeout (504) counts as 'too slow' under PROTOCOL.md and moves to the next reduction."""
    try:
        st, r = netlib.post("count", "https://api.openalex.org/", {"oql": oql, "per_page": 1, "select": "id"})
    except SystemExit as e:
        return None, {"error": str(e)}
    if st != 200:
        return None, r
    return r["meta"]["count"], None


def main():
    caps, report = {}, {}
    for name, spec in SPECS.items():
        tried = []
        for cap, kw in STEPS:
            smart, eq, _ = render(name, cap, kw)
            ok, info = validate(smart)
            n, err = count(smart) if ok else (None, None)
            tried.append({"cap": cap, "keywords": kw, "valid": ok, "count_ok": n is not None, **info,
                          **({"count_error": err} if err else {})})
            if ok and n is not None:
                break
        caps[name] = {"cap": cap, "keywords": kw}
        eq_ok, eq_info = validate(eq)
        eq_n, _ = count(eq)
        base_n, _ = count((REPO / spec["base"]).read_text().strip())
        report[name] = {"steps": tried, "smart_count": n, "base_equivalence_count": eq_n,
                        "frozen_base_count": base_n, "equivalence_holds": eq_n == base_n and eq_n is not None,
                        "base_equivalence_valid": eq_ok}
        print(f"{name:26s} cap={cap:3d} kw={kw!s:5s} smart={n}  eq={eq_n} base={base_n} {'OK' if eq_n == base_n else 'MISMATCH'}", flush=True)
    (ROOT / "queries/caps.json").write_text(json.dumps(caps, indent=1) + "\n")
    (ROOT / "queries/validation_report.json").write_text(json.dumps(report, indent=1) + "\n")


if __name__ == "__main__":
    main()
