"""Offline: split every benchmark's misses into 'not indexed in OpenAlex' and 'indexed but missed by
the search', from the archived matches and run observations. Writes RECALL_SPLIT.md and
recall_split.csv. Standard library only.

    python3 recall_split.py

Unit: each benchmark's own (reference, study, report or trial). A unit is indexed if any OpenAlex
ID was matched to it, and found if any of its IDs is in the arm's recovered set. The best arm is
the frozen arm with the highest recall (ties: fewer records), chosen after the fact.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
B = [("walker_transgenerational_benchmark_2026-11-12", "Transgenerational inheritance (Walker 2018)", "PubMed only", 63754),
     ("inclusion_sen_benchmark_2026-11-13", "Special educational needs (Dalgaard 2022)", "9 databases + grey literature", 20183),
     ("bt_maize_multisource_benchmark_2026-11-12", "Bt maize (Meissle 2022)", "12 databases + specialist sites", 12967),
     ("cost_mental_disorders_benchmark_2026-11-13", "Cost of mental disorders (Christensen 2020)", "6 databases + bibliographies", 13579),
     ("motor_competence_benchmark_2026-11-13", "Motor competence (Bao 2024)", "6 databases + reference lists", 12117),
     ("precarious_employment_benchmark_2026-11-13", "Precarious employment (Pulford 2022)", "9 databases + grey literature", 12940),
     ("hiv_care_continuum_benchmark_2026-11-13", "HIV care in children (Haw 2025)", "3 databases + hand-search", 10281),
     ("pa_primary_care_benchmark_2026-11-13", "Physical activity in primary care (Kettle 2022)", "12 databases + 3 trial registers", 14566),
     ("anxiety_eating_benchmark_2026-11-13", "Anxiety and eating disorders (Trompeter 2025)", "6 databases + PsyArXiv", 19591),
     ("ethnicity_adherence_benchmark_2026-11-13", "Ethnicity and diabetes adherence (Asiri 2023)", "4 databases + grey literature", 17410),
     ("smokefree_support_benchmark_2026-11-13", "Smoke-free policy support (Boderie 2023)", "6 databases", 6229),
     ("vr_stroke_benchmark_2026-11-13", "VR for stroke rehabilitation (Soleimani 2024)", "5 databases", 7381),
     ("nlp_cognitive_benchmark_2026-11-13", "NLP for cognitive impairment (Shankar 2025)", "8 databases", 5033),
     ("hcw_mental_emro_benchmark_2026-11-13", "Health workers' mental health, EMRO (Salahi Ardekani 2025)", "3 databases", 11572),
     ("call_handlers_benchmark_2026-11-13", "Call-handlers' mental health (Osório 2024)", "10 databases + hand-search + citations", 11571)]
DESIGNED = ("anxiety", "ethnicity", "smokefree", "vr_", "nlp", "hcw", "call")
STATED = {"walker": 257, "inclusion": 94, "bt": 166, "cost": 143, "motor": 44, "precarious": 50, "hiv": 190, "pa": 51,
          "anxiety": 54, "ethnicity": 41, "smokefree": 107, "vr": 55, "nlp": 51, "hcw": 89, "call": 37}
REASON = {"walker": "OpenAlex spans all disciplines, so the PubMed text strategy returns 4.8x the records",
          "inclusion": "Dissertations and reports absent; weak special-needs wording",
          "bt": "Regional journals, reports and website items absent",
          "pa": "Meeting abstracts and a thesis absent; scattered misses across 15 sources",
          "precarious": "Health block too narrow; missing abstracts",
          "smokefree": "Support wording too varied; 4 reports absent",
          "hcw": "4 regional-journal studies absent; 3 vocabulary misses (anesthetists, pre-hospital staff, no country named)",
          "call": "10 absent, six from a practitioner journal the authors hand-searched",
          "hiv": "Age concept relied on subject headings",
          "vr": "Robotic and brain-computer-interface trials counted as VR never say so",
          "ethnicity": "Ethnicity reported only as a covariate; abstracts missing",
          "cost": "Inconsistent cost wording; missing abstracts; bibliography-found studies",
          "anxiety": "Undergraduate samples without youth wording; one misdated record",
          "nlp": "Two misdated records; three avoid NLP terms",
          "motor": "Recent journal literature with consistent vocabulary"}
SUBTYPE = {"hiv": "indexing-dependent concept", "vr": "review scope wider than its vocabulary", "ethnicity": "concept only in full text",
           "cost": "vocabulary, and load failed", "anxiety": "vocabulary, near miss", "nlp": "vocabulary and metadata, near miss"}


def units(d):
    m = json.loads((d / "results/benchmark_matches.json").read_text())
    recs = m["records"] if isinstance(m, dict) else m
    sp = d / "results/benchmark_source.json"
    src = json.loads(sp.read_text()) if sp.exists() else {}
    if src.get("studies") and "ref_ids" in src["studies"][0]:
        by = {r["ref_id"]: r.get("openalex_id") for r in recs}
        return {s["study_id"]: {by.get(r) for r in s["ref_ids"]} - {None} for s in src["studies"]}
    out = {}
    for i, r in enumerate(recs):
        ids = {r.get("openalex_id")} | set(r.get("alternate_openalex_ids") or [])
        ids.discard(None)
        out[str(i)] = ids
    return out


def main():
    rows = []
    for b, label, sources, screened in B:
        d = ROOT / b
        u = units(d)
        n = STATED[b.split("_")[0]]
        assert len(u) == n or (len(u) == n + 1 and b.startswith("bt_")), (b, len(u))   # Bt maize source file carries one legend row with no ID
        indexed = sum(1 for v in u.values() if v)
        obs = json.loads((d / "results/run_observations.json").read_text())["arms"]
        scored = {arm: (sum(1 for v in u.values() if v & set(o["recovered_ids"])), o["count"]) for arm, o in obs.items()}
        arm = max(scored, key=lambda a: (scored[a][0], -scored[a][1]))
        k, count = scored[arm]
        mech = next(((a, *v) for a, v in scored.items() if a.startswith("M_")), None) if b.startswith(DESIGNED) else None
        thr = int(0.95 * n) + 1
        within = [v for v in scored.values() if v[1] <= screened]
        best_within = max(within, key=lambda v: (v[0], -v[1])) if within else None
        key = b.split("_")[0]
        if best_within and best_within[0] >= thr:
            cls = "Pass"
        elif k >= thr:
            cls = "Recall met, load failed"
        elif indexed < thr:
            cls = "Coverage makes target impossible"
        elif indexed - thr <= 1 and n - indexed >= 2:   # real coverage loss leaving no room for any search miss
            cls = "Coverage leaves no margin, plus search misses"
        else:
            cls = "Search failure: " + SUBTYPE.get(key, "search")
        des = None
        if b.startswith(DESIGNED):
            sa = max((a for a in scored if a.startswith("S")), key=lambda a: (scored[a][0], -scored[a][1]))
            des = (sa, *scored[sa])
        rows.append({"benchmark": label, "folder": b, "sources": sources, "included": n, "in_openalex": indexed,
                     "not_indexed": n - indexed, "indexed_but_missed": indexed - k, "found": k,
                     "recall_all": k / n, "recall_indexed": k / indexed, "best_arm": arm, "records": count,
                     "authors_screened": screened, "designed": b.startswith(DESIGNED), "best_is_designed": arm.startswith("S"),
                     "designed_arm": des[0] if des else None, "designed_found": des[1] if des else None, "designed_records": des[2] if des else None,
                     "mechanical_found": mech[1] if mech else None, "mechanical_records": mech[2] if mech else None,
                     "threshold": thr, "best_within_load_found": best_within[0] if best_within else None,
                     "best_within_load_records": best_within[1] if best_within else None, "classification": cls, "main_reason": REASON[key]})
    rows.sort(key=lambda r: -r["recall_indexed"])
    with open(ROOT / "recall_split.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader()
        w.writerows([{k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()} for r in rows])
    N = sum(r["included"] for r in rows); I = sum(r["in_openalex"] for r in rows); K = sum(r["found"] for r in rows)
    miss_n, miss_s = N - I, I - K
    pct = lambda x: f"{100 * x:.1f}%"  # noqa: E731
    lines = ["# Not indexed versus missed by the search", "",
             f"**Across the 15 benchmarks on branch `opus5.5`, {miss_n + miss_s} included studies were not retrieved by the best frozen OpenAlex search. "
             f"{miss_n} ({100 * miss_n / (miss_n + miss_s):.0f}%) are not indexed in OpenAlex; {miss_s} ({100 * miss_s / (miss_n + miss_s):.0f}%) are indexed but the search missed them.**", "",
             "- **Recall, all included** = found ÷ all included studies: what OpenAlex alone delivers.",
             "- **Recall, indexed only** = found ÷ included studies that are in OpenAlex: how well the search strategy performs on what OpenAlex holds.", "",
             "| Review | Included | In OpenAlex | Not indexed | Indexed but missed | Recall, all included | Recall, indexed only | Records (authors screened) |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in rows:
        mark = "†" if r["best_is_designed"] else ""
        mark += "‡" if r["folder"].startswith("vr_") else ""
        lines.append(f"| [{r['benchmark']}]({r['folder']}/README.md){mark} | {r['included']} | {r['in_openalex']} ({r['in_openalex'] / r['included']:.0%}) | {r['not_indexed']} | "
                     f"{r['indexed_but_missed']} | {pct(r['recall_all'])} | {pct(r['recall_indexed'])} | {r['records']:,} ({r['authors_screened']:,}) |")
    lines += [f"| **All 15** | **{N:,}** | **{I:,} ({I / N:.1%})** | **{miss_n}** | **{miss_s}** | **{pct(K / N)}** | **{pct(K / I)}** | |", "",
              "† Best arm is a designed search (text OR OpenAlex keywords, targeted truncation and proximity). For smoke-free policy support the mechanical translation was best; all five designed-search reviews are compared below.",
              "‡ The one 'not indexed' trial is unidentifiable: its title is truncated in the review's own supplement.", "",
              "**Metadata, not strategy.** Some 'indexed but missed' items are misdated in OpenAlex and fall outside the date limit: one in the anxiety review and two in the NLP review. "
              "Leaving them out, indexed-only recall is 90.6% and 93.9%.", "",
              "**Best arm chosen after the fact.** For each review the frozen arm with the highest recall is shown, which flatters OpenAlex slightly.", "",
              "## Mechanical translation versus designed search (indexed only)", "",
              "| Review | Mechanical: found @ records | Designed: found @ records |", "|---|---:|---:|"]
    for r in rows:
        if r["designed"]:
            lines.append(f"| {r['benchmark']} | {r['mechanical_found']}/{r['in_openalex']} ({pct(r['mechanical_found'] / r['in_openalex'])}) @ {r['mechanical_records']:,} | "
                         f"{r['designed_found']}/{r['in_openalex']} ({pct(r['designed_found'] / r['in_openalex'])}) @ {r['designed_records']:,} |")
    lines += ["", "## Classification against both success criteria", "",
              "Success = recall strictly above 95% of all included studies **and** records no more than the authors' unique records screened, in the same frozen arm.", "",
              "| Review | Target | In OpenAlex | Best within authors' load | Best at any load | Failure type | Main reason |", "|---|---:|---:|---:|---:|---|---|"]
    order = ["Pass", "Recall met, load failed", "Coverage makes target impossible", "Coverage leaves no margin, plus search misses"]
    for r in sorted(rows, key=lambda r: (order.index(r["classification"]) if r["classification"] in order else 4, -r["recall_indexed"])):
        bw = f"{r['best_within_load_found']}/{r['included']} @ {r['best_within_load_records']:,}" if r["best_within_load_found"] is not None else "none"
        lines.append(f"| {r['benchmark']} | {r['threshold']} | {r['in_openalex']} ({r['in_openalex'] / r['included']:.0%}) | {bw} | "
                     f"{r['found']}/{r['included']} @ {r['records']:,} | **{r['classification']}** | {r['main_reason']} |")
    import collections
    cnt = collections.Counter(r["classification"].split(":")[0] for r in rows)
    lines += ["", "| Failure type | Reviews |", "|---|---:|"] + [f"| {k} | {v} |" for k, v in sorted(cnt.items(), key=lambda kv: (order.index(kv[0]) if kv[0] in order else 4))]
    lines += ["", "Generated by `python3 recall_split.py` from each benchmark's archived matches and run observations; data in [`recall_split.csv`](recall_split.csv).", ""]
    (ROOT / "RECALL_SPLIT.md").write_text("\n".join(lines))
    print("\n".join(lines[:4]))


if __name__ == "__main__":
    main()
