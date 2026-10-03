"""Targeted controls for the issues found by pilot_oql_validation.py."""
import os
os.environ["OPENALEX_OQL_OUTPUT"] = "oql_validation/ranking_diagnostics"
from pilot_oql_validation import Pilot, OUT, DATES
import json
from datetime import datetime, timezone

p = Pilot()
q = "works where title/abstract has (retinopathy screening) and " + DATES
ids = lambda j: [r["id"] for r in j.get("results", [])]
controls = {}
for label, extras in [("native", {}), ("reranked", {"rerank": True})]:
    status, single = p.execute(q, per_page=150, sort="relevance_score:desc", **extras)
    concatenated, cursor = [], "*"
    for index in range(3):
        status, page = p.execute(q, per_page=50, sort="relevance_score:desc", cursor=cursor, **extras)
        if status != 200:
            break
        concatenated.extend(ids(page))
        cursor = (page.get("meta") or {}).get("next_cursor")
        if not cursor:
            break
    p.check("simple_query:" + label + "_paging", status == 200 and concatenated == ids(single),
            {"last_status": status, "returned": len(concatenated), "last_response_if_error": page if status != 200 else None})
    controls[label] = {"single_page_count": len(ids(single)), "paged_count": len(concatenated),
                       "single_page_scores_present": all(isinstance(r.get("relevance_score"), (int,float)) for r in single.get("results", []))}
    if label == "reranked" and status != 200:
        status_off, off = p.execute(q, per_page=50, sort="relevance_score:desc", cursor=cursor)
        p.check("simple_query:continuation_without_rerank", status_off == 200 and ids(off) == ids(single)[100:150],
                {"status": status_off, "response_if_error": off if status_off != 200 else None})

# Mixed keyword/text branches are relevant to the planned enhanced strategy.
mixed = 'works where (keyword is (diabetic-retinopathy) or title/abstract has ("diabetic retinopathy")) and ' + DATES
status, value = p.execute(mixed, per_page=5, sort="relevance_score:desc")
p.check("keyword_or_text:relevance_available", status == 200 and len(value.get("results", [])) == 5
        and all(isinstance(r.get("relevance_score"), (int,float)) for r in value.get("results", [])),
        {"status": status, "count": (value.get("meta") or {}).get("count"), "response_if_error": value if status != 200 else None})

summary = {"complete": True, "completed_utc": datetime.now(timezone.utc).isoformat(), "controls": controls,
           "checks": p.checks, "requests": len(p.requests)}
(OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
