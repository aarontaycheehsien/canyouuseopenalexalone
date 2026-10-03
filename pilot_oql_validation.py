"""Small live OpenAlex OQL conformance pilot; not the review recall benchmark.

Uses the Python standard library. Requests contain no API key unless supplied
through OPENALEX_API_KEY. Credentials are never written to the audit artifacts.
"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import re
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent
from pilot_credentials import load_key
load_key()
OUT = ROOT / os.environ.get("OPENALEX_OQL_OUTPUT", "oql_validation")
API = "https://api.openalex.org"
DATES = "year >= (2003) and year <= (2023)"


class Pilot:
    def __init__(self):
        OUT.mkdir(exist_ok=True, parents=True)
        (OUT / "summary.json").write_text('{"complete": false}', encoding="utf-8")
        self.requests = []
        self.checks = []
        self.cache = {}

    def request(self, path="/", body=None, params=None):
        query = urllib.parse.urlencode(params or {})
        url = API + path + ("?" + query if query else "")
        # Canonical oxurl can retain spaces; encode them without double-encoding %xx.
        url = urllib.parse.quote(url, safe="/:?&=%,+*~()")
        headers = {"User-Agent": "OpenAlex-ES-OQL-validation/0.1", "Content-Type": "application/json"}
        if os.environ.get("OPENALEX_API_KEY"):
            headers["Authorization"] = "Bearer " + os.environ["OPENALEX_API_KEY"]
        req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None,
                                     headers=headers, method="POST" if body is not None else "GET")
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=45) as response:
                    status = response.status
                    raw = response.read().decode("utf-8", "replace")
                break
            except urllib.error.HTTPError as error:
                status = error.code
                raw = error.read().decode("utf-8", "replace")
                if status in (429, 502, 503, 504) and attempt < 2:
                    time.sleep(2 * (attempt + 1))
                    continue
                break
            except (OSError, TimeoutError) as error:
                if attempt < 2:
                    time.sleep(2)
                    continue
                status, raw = 0, json.dumps({"transport_error": type(error).__name__})
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            value = {"non_json_response": raw[:1000]}
        self.requests.append({"time_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                              "path": path, "params": params, "body": body,
                              "status": status, "response": value})
        (OUT / "requests.json").write_text(json.dumps(self.requests, ensure_ascii=False, indent=2), encoding="utf-8")
        return status, value

    def check(self, name, passed, detail=None):
        self.checks = [c for c in self.checks if c["name"] != name]
        self.checks.append({"name": name, "passed": bool(passed), "detail": detail})
        print(("PASS " if passed else "FAIL ") + name, flush=True)
        (OUT / "checks.json").write_text(json.dumps(self.checks, ensure_ascii=False, indent=2), encoding="utf-8")

    def translate(self, q):
        return self.request("/query", {"oql": q})

    def execute(self, q, **view):
        return self.request("/", {"oql": q, "per_page": 200, **view})

    def finite(self, clause):
        if clause in self.cache:
            return self.cache[clause]
        q = "works where (" + self.universe_clause + ") and (" + clause + ") and " + DATES
        status, value = self.execute(q, select="id,display_name,publication_year,relevance_score")
        if status != 200 or not isinstance(value.get("results"), list) or not value.get("meta"):
            raise RuntimeError("Execution did not return a result envelope: " + json.dumps(value)[:900])
        ids = {r["id"] for r in value["results"]}
        if value["meta"]["count"] != len(ids):
            raise RuntimeError("Finite result set truncated or count inconsistent")
        self.cache[clause] = ids
        return ids

    def run(self):
        positives = {
            "date_bounds": "works where " + DATES,
            "nested_boolean": 'works where title/abstract has ((diabetes or "diabet*") and (retinopathy or retinal) and (screening or uptake)) and ' + DATES,
            "exact_phrase": 'works where title has ("diabetic retinopathy") and ' + DATES,
            "stemmed_phrase": 'works where title has (stemmed "diabetic retinopathy") and ' + DATES,
            "bare_multiword": 'works where title/abstract has (diabetic retinopathy) and ' + DATES,
            "explicit_and": 'works where title/abstract has (diabetic and retinopathy) and ' + DATES,
            "proximity_exact": 'works where title has (within 3 ("diabetic", "retinopathy")) and ' + DATES,
            "proximity_stemmed": 'works where title has (within 3 (diabetic, retinopathy)) and ' + DATES,
            "proximity_wildcards": 'works where title has (within 3 ("diabet*", "retinopath*")) and ' + DATES,
            "wildcard_phrase": 'works where title has ("diabet* retinopath*") and ' + DATES,
            "single_character_wildcard": 'works where title has ("wom?n") and ' + DATES,
            "cross_field_or": 'works where (title has (screening) or abstract has (retinopathy)) and ' + DATES,
            "keyword_or_text": 'works where (keyword is (diabetic-retinopathy) or title/abstract has ("diabetic retinopathy")) and ' + DATES,
            "keyword_search_scope": 'works where title/abstract/keywords has ("diabetic retinopathy") and ' + DATES,
            "full_text_scope": 'works where full text has ("diabetic retinopathy") and ' + DATES,
            "geographic_codes": 'works where country is (AU or CA or IE or NZ or GB) and ' + DATES,
            "negated_group": 'works where title has (screening and not (cancer or prostate)) and ' + DATES,
        }
        for name, q in positives.items():
            status, translated = self.translate(q)
            ok = status == 200 and translated.get("validation", {}).get("valid") is True
            self.check("parse:" + name, ok, {"status": status, "validation": translated.get("validation")})
            if ok:
                s2, rt = self.request("/query", {"oqo": translated["oqo"]})
                self.check("roundtrip:" + name, s2 == 200 and rt.get("oqo") == translated["oqo"])
                se, executed = self.execute(q, per_page=3)
                envelope = se == 200 and isinstance(executed.get("results"), list) and bool(executed.get("meta"))
                self.check("execute:" + name, envelope and all(2003 <= r["publication_year"] <= 2023 for r in executed.get("results", [])),
                           {"status": se, "count": (executed.get("meta") or {}).get("count")})

        negative = {
            "unquoted_wildcard": 'works where title has (diabet*)',
            "mixed_proximity_operands": 'works where title has (within 3 (diabetic, "retinopathy"))',
            "obsolete_proximity_suffix": 'works where title has ("diabetic retinopathy" within 3 words)',
            "leading_wildcard": 'works where title has ("*retinopathy")',
            "short_wildcard": 'works where title has ("di*")',
            "unknown_field": 'works where invented_field has (screening)',
            "wrong_country_code": 'works where country is (UK)',
            "unbalanced_group": 'works where title has ((diabetes or retinal)',
            "range_literal": 'works where year is (2003-2023)',
            "fuzzy_engine_syntax": 'works where title has (diabetes~1)',
        }
        for name, q in negative.items():
            status, result = self.translate(q)
            self.check("reject:" + name, status == 400 and result.get("validation", {}).get("valid") is False,
                       {"status": status, "response": result})

        records = {}
        for term, n in [("retinopathy", 25), ("screening", 15), ("diabetes", 15)]:
            status, result = self.execute("works where title has (" + term + ") and " + DATES, per_page=n)
            if status != 200 or not result.get("meta"):
                raise RuntimeError("Cannot construct finite test corpus")
            records.update({r["id"]: r for r in result["results"]})
        self.records = records
        (OUT / "finite_corpus.json").write_text(json.dumps(list(records.values()), ensure_ascii=False, indent=2), encoding="utf-8")
        self.universe_clause = "openalex is (" + " or ".join(x.rsplit("/", 1)[-1] for x in records) + ")"
        self.check("finite_corpus_dates", all(2003 <= r["publication_year"] <= 2023 for r in records.values()), {"records": len(records)})

        a, b, c = (self.finite("title has (" + t + ")") for t in ("screening", "retinopathy", "diabetes"))
        self.check("semantics:boolean_union", self.finite("title has (screening or retinopathy)") == a | b)
        self.check("semantics:boolean_intersection", self.finite("title has (screening and retinopathy)") == a & b)
        self.check("semantics:nested_negation", self.finite("title has ((screening or retinopathy) and not diabetes)") == (a | b) - c)
        self.check("semantics:and_or_precedence", self.finite("title has (screening or retinopathy and diabetes)") == a | (b & c))
        abstract = self.finite("abstract has (retinopathy)")
        self.check("semantics:cross_field_or", self.finite("title has (screening) or abstract has (retinopathy)") == a | abstract)
        self.check("semantics:title_abstract_scope", self.finite("title/abstract has (retinopathy)") == b | abstract)
        keyword = self.finite("keyword is (diabetic-retinopathy)")
        phrase = self.finite('title/abstract has ("diabetic retinopathy")')
        self.check("semantics:keyword_or_text", self.finite('keyword is (diabetic-retinopathy) or title/abstract has ("diabetic retinopathy")') == keyword | phrase)
        self.check("semantics:exact_subset_stemmed", self.finite('title has ("diabetic")') <= self.finite("title has (diabetic)"))

        tokens = {wid: re.findall(r"\w+", r["display_name"].lower()) for wid, r in records.items()}
        expected_wildcard = {wid for wid, tok in tokens.items() if any(t.startswith("retinopath") for t in tok)}
        self.check("semantics:wildcard_title_tokens", self.finite('title has ("retinopath*")') == expected_wildcard,
                   {"expected_count": len(expected_wildcard)})
        exact_phrase = {wid for wid, tok in tokens.items() if any(tok[i:i+2] == ["diabetic", "retinopathy"] for i in range(len(tok)-1))}
        self.check("semantics:exact_phrase_title_tokens", self.finite('title has ("diabetic retinopathy")') == exact_phrase)
        previous = set()
        for distance in (0, 1, 3, 5):
            for wildcard in (False, True):
                terms = ["diabet*", "retinopath*"] if wildcard else ["diabetic", "retinopathy"]
                clause = 'title has (within ' + str(distance) + ' ("' + terms[0] + '", "' + terms[1] + '"))'
                actual = self.finite(clause)
                expected = set()
                for wid, tok in tokens.items():
                    left = [i for i, t in enumerate(tok) if (t.startswith("diabet") if wildcard else t == "diabetic")]
                    right = [i for i, t in enumerate(tok) if (t.startswith("retinopath") if wildcard else t == "retinopathy")]
                    if any(abs(i-j)-1 <= distance for i in left for j in right if i != j):
                        expected.add(wid)
                self.check("semantics:proximity_" + str(distance) + ("_wildcard" if wildcard else "_exact"), actual == expected,
                           {"expected_count": len(expected), "actual_count": len(actual), "extra": sorted(actual - expected), "missing": sorted(expected - actual)})
                if not wildcard:
                    self.check("semantics:proximity_monotone_" + str(distance), previous <= actual)
                    previous = actual

        self.execution_checks()

    def execution_checks(self):
        # Independently exercise OQL GET, OQL POST, OQO, and classic execution.
        universe = "openalex is (" + " or ".join(x.rsplit("/", 1)[-1] for x in self.records) + ")"
        q = 'works where ' + universe + ' and title has ("diabetic retinopathy") and ' + DATES
        st, tr = self.translate(q)
        s1, one = self.execute(q, per_page=25)
        s2, two = self.request("/", params={"oql": q, "per_page": 25})
        s3, three = self.request("/", {"oqo": tr["oqo"], "per_page": 25})
        s4, four = self.request(tr["oxurl"] + "&per_page=25")
        signature = lambda j: ((j.get("meta") or {}).get("count"), {x["id"] for x in j.get("results", [])})
        self.check("execution:get_post_oqo_classic_membership", all(s == 200 for s in (s1, s2, s3, s4)) and all(signature(j) == signature(one) for j in (two, three, four)))

        rank_q = 'works where title/abstract has ((retinopathy or retinal) and (screening or uptake)) and ' + DATES
        sd, default = self.execute(rank_q, per_page=150)
        sr, relevance = self.execute(rank_q, per_page=150, sort="relevance_score:desc")
        ss, reranked = self.execute(rank_q, per_page=150, sort="relevance_score:desc", rerank=True)
        ids = lambda j: [x["id"] for x in j.get("results", [])]
        default_same = ids(default) == ids(relevance)
        self.check("ranking:default_comparison_completed", sd == sr == 200,
                   {"same_order": default_same, "default_needs_separate_arm": not default_same})
        self.check("ranking:rerank_executed", ss == 200 and reranked.get("meta", {}).get("reranked") is True,
                   {"meta": reranked.get("meta")})
        self.check("ranking:rerank_preserves_top100_membership", ss == 200 and set(ids(relevance)[:100]) == set(ids(reranked)[:100]))
        self.check("ranking:rerank_preserves_101_150_order", ss == 200 and ids(relevance)[100:] == ids(reranked)[100:])
        scores = [x.get("relevance_score") for x in relevance.get("results", [])]
        self.check("ranking:relevance_scores_present", bool(scores) and all(isinstance(s, (int, float)) for s in scores),
                   {"returned": len(scores), "missing": sum(s is None for s in scores)})
        self.check("ranking:relevance_monotonic", bool(scores) and all(isinstance(s, (int, float)) for s in scores)
                   and all(x >= y for x, y in zip(scores, scores[1:])))

        # Verify cursors across an actual reranking boundary, rather than only a single page.
        for label, mode in [("native", {}), ("reranked", {"rerank": True})]:
            pages, cursor, page_responses = [], "*", []
            for _ in range(3):
                sp, page = self.execute(rank_q, per_page=50, sort="relevance_score:desc", cursor=cursor, **mode)
                if sp != 200 or not page.get("meta"):
                    break
                pages.extend(ids(page))
                page_responses.append(page)
                cursor = page["meta"].get("next_cursor")
                if not cursor:
                    break
            base = reranked if label == "reranked" else relevance
            self.check("paging:" + label + "_no_duplicates", len(pages) == len(set(pages)))
            self.check("paging:" + label + "_matches_single_page", len(pages) == 150 and pages == ids(base),
                       {"pages": len(page_responses), "records": len(pages),
                        "first_mismatch": next((i+1 for i,(a,b) in enumerate(zip(pages, ids(base))) if a != b), None),
                        "last_status": sp, "last_error": page if sp != 200 else None})

        # Positive controls show whether missing scores are query-specific.
        for label, query in [
            ("simple_term", 'works where title/abstract has (retinopathy) and ' + DATES),
            ("simple_and", 'works where title/abstract has (retinopathy and screening) and ' + DATES),
        ]:
            sc, control = self.execute(query, per_page=5, sort="relevance_score:desc")
            self.check("ranking:control_" + label, sc == 200 and len(control.get("results", [])) == 5
                       and all(isinstance(r.get("relevance_score"), (int, float)) for r in control.get("results", [])))
        sc, classic = self.request("/works", params={"search.title_and_abstract": "(retinopathy OR retinal) AND (screening OR uptake)",
                                                     "filter": "publication_year:2003-2023", "per_page": 5, "sort": "relevance_score:desc"})
        self.check("ranking:classic_nested_positive_control", sc == 200 and len(classic.get("results", [])) == 5
                   and all(isinstance(r.get("relevance_score"), (int, float)) for r in classic.get("results", [])),
                   {"oql_count": relevance.get("meta", {}).get("count"), "classic_count": (classic.get("meta") or {}).get("count")})

        summary = {"complete": True, "completed_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                   "checks": len(self.checks), "passed": sum(x["passed"] for x in self.checks),
                   "failed": [x for x in self.checks if not x["passed"]], "requests": len(self.requests),
                   "finite_corpus_size": len(self.records),
                   "cost_usd_reported": sum((r["response"].get("meta") or {}).get("cost_usd", 0) for r in self.requests)}
        (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    import sys
    pilot = Pilot()
    if "--resume-execution" in sys.argv:
        pilot.requests = json.loads((OUT / "requests.json").read_text(encoding="utf-8"))
        pilot.checks = json.loads((OUT / "checks.json").read_text(encoding="utf-8"))
        corpus = json.loads((OUT / "finite_corpus.json").read_text(encoding="utf-8"))
        pilot.records = {r["id"]: r for r in corpus}
        pilot.execution_checks()
    else:
        pilot.run()
