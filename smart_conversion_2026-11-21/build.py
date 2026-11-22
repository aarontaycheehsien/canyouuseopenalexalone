"""Build the smart-conversion arm for every review (offline; PROTOCOL.md R1-R6).

    python3 build.py [--check] [--cap N] [--no-keywords]

Reads only: specs.py, vocab/*.json, the frozen base query files. An audit hook enforces this.
Writes queries/<review>__S_smart.oql, queries/<review>__base_equivalence.oql and
queries/build_report.json. --check compares against the written files instead.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent


def _guard(event, args):
    if event != "open" or not args or not isinstance(args[0], (str, bytes)):
        return
    p = Path(args[0] if isinstance(args[0], str) else args[0].decode()).resolve()
    try:
        rel = p.relative_to(REPO)
    except ValueError:
        return                                     # outside the repository (stdlib, nltk)
    s = rel.as_posix()
    allowed = s.startswith(ROOT.name + "/") or (
        "/queries/" in s and s.endswith(".oql") and not s.startswith(ROOT.name)) or s.startswith(".git/")
    if not allowed:
        raise PermissionError(f"blinding guard: builder may not open {s}")


sys.addaudithook(_guard)

import oqlsplit  # noqa: E402
from specs import SPECS  # noqa: E402
from terms import mesh_term_forms, normal_form, oql_term, plain_terms  # noqa: E402

FIELD = "title-abstract-keywords"


def heading_terms(rec, cap):
    if rec["mapping"] == "unmapped":
        return [oql_term(normal_form(rec["label"]))], {"level": None}
    levels, used = rec["levels"], 0
    labels = list(levels[0][0]["terms"])
    if rec["explode"]:
        for i in range(1, len(levels)):
            cand = labels + [t for x in levels[i] for t in x["terms"]]
            if len(mesh_term_forms(cand)) > cap:
                break
            labels, used = cand, i
    return mesh_term_forms(labels), {"level": used, "levels_available": len(levels) - 1}


def groups_for(name, cap):
    spec = SPECS[name]
    base = oqlsplit.split((REPO / spec["base"]).read_text())
    mesh = json.loads((ROOT / "vocab/mesh_resolved.json").read_text())
    out = []
    for g in spec["groups"]:
        parts = [base["concepts"][i] for i in g["concepts"]]
        text = parts[0] if len(parts) == 1 else " AND ".join(f"({p})" for p in parts)
        extra, info = [], []
        for vocab, label, explode, src in g["headings"]:
            ts, meta = heading_terms(mesh[f"{vocab}|{label}|{explode}"], cap)
            info.append({"heading": f"{vocab}|{label}|{explode}", "source": src, "terms": len(ts), **meta})
            extra += ts
        low = text.lower()
        extra = [t for t in dict.fromkeys(extra) if t.lower() not in low]
        out.append({**g, "text": text, "fields": [base["fields"][i] for i in g["concepts"]], "parts": parts,
                    "extra": extra, "heading_info": info})
    return base, out


def r4_terms(group):
    """Inputs to the R4 keyword lookup: plain terms of a topic concept, base and heading-derived."""
    if group["design"]:
        return []
    terms = set(plain_terms(group["text"]) + plain_terms(" OR ".join(group["extra"])))
    return sorted(t for t in terms if not is_abbreviation(t))


def is_abbreviation(t):
    """Amendment 1 (22 Nov 2026): R4 skips abbreviations, whose keyword alternative labels conflate
    unrelated expansions (BP -> blood pressure). All-capital terms and single words of <= 5 characters."""
    return (t.isupper() and len(t) > 1) or (" " not in t and len(t) <= 5)


def keyword_clauses(group, kwmap):
    if group["design"] or kwmap is None:
        return []
    have = {t.lower() for t in r4_terms(group)}
    out = {}
    for t in r4_terms(group):
        for k in kwmap.get(t, []):
            if k["display_name"].lower() not in have:
                out[k["id"]] = k["display_name"]
    return [f"keyword is [{n}](keywords/{i})" for i, n in sorted(out.items())]


def render(name, cap=200, keywords=True):
    base, groups = groups_for(name, cap)
    kwmap = json.loads((ROOT / "vocab/keyword_matches.json").read_text()) if keywords else None
    head = f"get works{(' ' + base['corpus']) if base['corpus'] else ''} where "
    conds = []
    for g in groups:
        search = " OR ".join([f"({g['text']})"] + g["extra"]) if g["extra"] else g["text"]
        c = f"{FIELD} has ({search})"
        kws = keyword_clauses(g, kwmap) if keywords else []
        conds.append((g["design"], f"({' or '.join([c] + kws)})" if kws else c))
    excl = [f"not {FIELD} has ({x})" for _, x in base["exclusions"]]
    topic = [c for d, c in conds if not d]
    if any(d for d, _ in conds):
        allc = [c for _, c in conds]
        core = (f"((it has an abstract and {' and '.join(allc)}) or "
                f"(it doesn't have an abstract and {' and '.join(topic)}))")
        body = base["filters"] + [core] + excl
    else:
        body = base["filters"] + [c for _, c in conds] + excl
    smart = head + " and ".join(body)
    eq = head + " and ".join(base["filters"] + [f"{f} has ({p})" for g in groups for f, p in zip(g["fields"], g["parts"])]
                             + [f"not {f} has ({x})" for f, x in base["exclusions"]])
    report = {"review": name, "cap": cap, "keywords": keywords, "chars": len(smart),
              "groups": [{"name": g["name"], "design": g["design"], "extra_terms": len(g["extra"]),
                          "keyword_clauses": len(keyword_clauses(g, kwmap)) if keywords else 0,
                          "headings": g["heading_info"]} for g in groups],
              "r2_note": SPECS[name]["r2_note"], "dropped": SPECS[name]["dropped"]}
    return smart, eq, report


def main():
    check = "--check" in sys.argv
    caps = json.loads((ROOT / "queries/caps.json").read_text()) if (ROOT / "queries/caps.json").exists() else {}
    reports = []
    for name in SPECS:
        cfg = caps.get(name, {"cap": 200, "keywords": True})
        smart, eq, rep = render(name, cfg["cap"], cfg["keywords"])
        reports.append(rep)
        for suffix, text in (("S_smart", smart), ("base_equivalence", eq)):
            p = ROOT / "queries" / f"{name}__{suffix}.oql"
            if check:
                assert p.read_text() == text + "\n", p
            else:
                p.parent.mkdir(exist_ok=True)
                p.write_text(text + "\n")
        print(f"{name:28s} {len(smart):6d} chars  " + "  ".join(f"{g['name']}+{g['extra_terms']}t/{g['keyword_clauses']}k" for g in rep["groups"]))
    rp = ROOT / "queries/build_report.json"
    if check:
        assert json.loads(rp.read_text()) == reports, rp
        print("builder output matches frozen files")
    else:
        rp.write_text(json.dumps(reports, indent=1) + "\n")


if __name__ == "__main__":
    main()
