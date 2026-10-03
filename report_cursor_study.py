"""Summarize complete cursor walks and the disclosed fixed-candidate rerank."""
from __future__ import annotations
import csv
from datetime import datetime,timezone
import gzip
import json
import math
import os
from pathlib import Path
from run_cursor_study import ROOT,RUN,NAMES,read,save

BUDGETS=[10,20,50,100,500,1000,2500,5000,12293]
LABELS={'legacy_union_normalized':'Published strategy','oql_restored':'Restored OQL','oql_keywords':'OQL plus keywords','oql_fulltext':'OQL plus full text','oql_no_geography':'OQL without geography'}
refs=read(ROOT/'reference_records.json')
assert len(refs)==133 and sum(r['primary'] for r in refs)==131
cohorts={'primary':[r for r in refs if r['primary']],'secondary':refs}
walks=[]
for arm in NAMES:
    for mode in ['relevance','default']:
        folder=RUN/arm/mode
        if (folder/'summary.json').exists():
            s=read(folder/'summary.json')
            if s.get('valid_cursor_walk'):
                ordered=read(folder/'ordered_ids.json')
                assert len(ordered)==len(set(ordered))==s['reported_count']
                walks.append({'arm':arm,'mode':mode,'ordered':ordered,'summary':s,'derived':False})
assert walks, 'No validated complete cursor walk exists'
initial_index=RUN/'enumeration_summary.json'
if initial_index.exists() and not (RUN/'initial_enumeration_summary.json').exists():
    save(RUN/'initial_enumeration_summary.json',read(initial_index))
save(initial_index,[w['summary'] for w in walks])
same=None
base={x['mode']:x for x in walks if x['arm']=='legacy_union_normalized'}
if 'relevance' in base and 'default' in base:
    same=base['relevance']['ordered']==base['default']['ordered']
    save(RUN/'default_relevance_comparison.json',{'full_order_identical':same,'records':len(base['relevance']['ordered']),
      'same_rank_positions':sum(a==b for a,b in zip(base['relevance']['ordered'],base['default']['ordered']))})
rerank_path=RUN/'legacy_union_normalized/candidate_rerank'
rerank=read(rerank_path/'summary.json') if (rerank_path/'summary.json').exists() else {}
if rerank.get('valid_candidate_rerank') and 'relevance' in base:
    rr=read(rerank_path/'ordered_ids.json');native=base['relevance']['ordered']
    assert set(rr)==set(native[:100]) and len(rr)==len(set(rr))==100
    combined=rr+native[100:]
    assert len(set(combined))==len(native)
    walks.append({'arm':'legacy_union_normalized','mode':'fixed_candidate_native_rerank',
      'ordered':combined,'summary':base['relevance']['summary'],'derived':True})
    save(rerank_path/'derived_full_order.json',combined)

members=read(ROOT/'membership_summary.json')
normalized=read(ROOT/'legacy_country_normalization/summary.json')
metrics=[];record_rows=[];membership_checks=[];curves={}
for w in walks:
    ranks={wid:i for i,wid in enumerate(w['ordered'],1)}
    expected=set((normalized if w['arm']=='legacy_union_normalized' else members[w['arm']])['returned_known_ids'])
    observed={r['current_openalex_id'] for r in refs if r['current_openalex_id'] in ranks}
    check={'arm':w['arm'],'mode':w['mode'],'finite_membership_matches_full_cursor':observed==expected,
      'finite_only':sorted(expected-observed),'cursor_only':sorted(observed-expected)}
    membership_checks.append(check)
    for cohort,records in cohorts.items():
        positions=sorted(ranks[r['current_openalex_id']] for r in records if r['current_openalex_id'] in ranks)
        n=len(records)
        item={'arm':w['arm'],'mode':w['mode'],'cohort':cohort,'denominator':n,
          'result_count':len(w['ordered']),'known_recovered':len(positions),'complete_query_recall':len(positions)/n,
          'derived_order':w['derived'],'finite_membership_matches_full_cursor':observed==expected}
        for budget in BUDGETS:
            hits=sum(p<=budget for p in positions)
            item['found_at_'+str(budget)]=hits
            item['recall_at_'+str(budget)]=hits/n
        for pct in [95,99]:
            target=math.ceil(pct*n/100)
            item['target_'+str(pct)]=target
            item['records_to_'+str(pct)]=positions[target-1] if len(positions)>=target else None
            item['target_'+str(pct)+'_status']='attainable' if len(positions)>=target else 'unattainable_in_cursor_results'
        metrics.append(item)
        curves[(w['arm'],w['mode'],cohort)]=positions
    for ref in refs:
        record_rows.append({'arm':w['arm'],'mode':w['mode'],'eppi_id':ref['eppi_id'],'primary':ref['primary'],
          'current_openalex_id':ref['current_openalex_id'],'rank':ranks.get(ref['current_openalex_id']),
          'title':ref['title'],'unmatched_reference':not bool(ref['current_openalex_id'])})
save(RUN/'metrics.json',metrics);save(RUN/'membership_checks.json',membership_checks)
for name,rows in [('rank_metrics.csv',metrics),('reference_ranks.csv',record_rows)]:
    with (RUN/name).open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def count_cell(item,budget):return f"{item['found_at_'+str(budget)]}/{item['denominator']}"
selected=[x for x in metrics if x['cohort']=='primary' and x['mode']!='fixed_candidate_native_rerank' and not (same and x['arm']=='legacy_union_normalized' and x['mode']=='default')]
table='| Search and cursor order | Total results | @100 | @500 | @1,000 | @2,500 | @5,000 | @12,293 | Records to 95% |\n| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n'
for item in selected:
    label=LABELS[item['arm']]+(' (relevance requested)' if item['mode']=='relevance' else ' (default)')
    target=f"{item['records_to_95']:,}" if item['records_to_95'] is not None else 'Unattainable'
    table+='| '+label+' | '+f"{item['result_count']:,}"+' | '+' | '.join(count_cell(item,b) for b in [100,500,1000,2500,5000,12293])+' | '+target+' |\n'
rt=''
rerank_metrics=[x for x in metrics if x['cohort']=='primary' and x['arm']=='legacy_union_normalized' and x['mode'] in ['relevance','fixed_candidate_native_rerank']]
if len(rerank_metrics)==2:
    rt='\n| Published strategy | @10 | @20 | @50 | @100 |\n| --- | ---: | ---: | ---: | ---: |\n'
    for item in rerank_metrics:
        label='Cursor order' if item['mode']=='relevance' else 'Native rerank of fixed cursor candidates'
        rt+='| '+label+' | '+' | '.join(count_cell(item,b) for b in [10,20,50,100])+' |\n'

failed=[]
for arm in NAMES:
    p=read(RUN/arm/'probe.json')
    for mode,test in p['modes'].items():
        if not test.get('eligible_for_enumeration'):failed.append({'arm':arm,'mode':mode,'status':test['status']})
validates=all(x['finite_membership_matches_full_cursor'] for x in membership_checks)
cost=0;calls=0;statuses={};times=[]
from pilot_credentials import load_key
load_key();secret=os.environ['OPENALEX_API_KEY']
for path in RUN.rglob('*_request.json.gz'):
    with gzip.open(path,'rt',encoding='utf-8') as f:raw=f.read()
    assert secret not in raw
    log=json.loads(raw);calls+=1;statuses[str(log['status'])]=statuses.get(str(log['status']),0)+1
    cost+=log['response'].get('meta',{}).get('cost_usd',0) or 0
    times.append(log['started_utc'])
audit={'requests':calls,'cost_usd_reported':cost,'statuses':statuses,'first_request_utc':min(times),
 'last_request_utc':max(times),'credential_scan_passed':True,'membership_agreement_all':validates,
 'completed_utc':datetime.now(timezone.utc).isoformat(),'validated_complete_walks':len(walks)-sum(w['derived'] for w in walks),
 'derived_fixed_candidate_rerank':bool(rerank.get('valid_candidate_rerank')),'failed_modes':failed}
save(RUN/'audit.json',audit)

report=f'''# Cursor-order study: Stansfield case

The study now uses cursor order as its operational definition of rank, as requested. All rankings start with `cursor=*` and continue with the returned cursor. The search strings and publication-year limits remain the frozen 2003–2023 strategies. The prior single-page/cursor discrepancy remains documented. Choosing cursor order does not prove that the API applies its intended native relevance algorithm.

## Primary reference results

These figures count recovery of the 131 original eligible records. The three unmatched records remain in the denominator. Secondary results for all 133 previously identified records are in `rank_metrics.csv`. No previously unlabelled records were assessed.

{table}

The 95% target requires 125/131 records. The 99% target requires 130/131. All measured cursor searches recover fewer than 130, so 99% is unattainable within their returned sets. This describes the matched-reference evaluation, rather than proving the three unmatched records are absent from OpenAlex.

## What passed

Each reported complete cursor walk passed repeated first-400 requests, comparison of 100-record and 200-record pages, unique-ID checks, stable result counts, date checks, and repeated page requests near the start, midpoint and end. Unique result counts equalled the API counts. Those checks support reproducibility of the observed cursor sequences during this run. They do not independently establish the correctness of the hidden relevance calculation or indefinite future stability.

Complete cursor membership agrees with the earlier finite known-record membership checks: **{validates}**. Default and relevance-requested cursor orders for the published strategy are identical across the complete sequence: **{same}**. The table presents one sequence when they are identical. All scores are checked separately in the walk summaries. Missing native relevance scores remain a limitation.

## Native reranking of the same candidates

The unchanged published query's reranked cursor walk failed continuation. Its starting candidate membership also differs from that of the non-reranked cursor walk. Those requests therefore cannot support a comparison of pure reranking on the same candidates.

The additional test fixes the first 100 IDs from the verified published-strategy cursor sequence. It submits the original query AND an explicit restriction to those IDs, with native `rerank=true`, requested relevance sorting, and `cursor=*`. Both requests return exactly the same 100 candidates, report `meta.reranked=true`, and give the same order. This is a **candidate-restricted native rerank**, not the unchanged-query native rerank arm. It was added after the initial pilot and must be described as such.

{rt}

For analysis, that reranked prefix is followed by the unmodified cursor sequence from position 101 onward. This complete order is assembled locally; it is not a successful full reranked API walk. Membership at 100 and all larger budgets is identical by construction. Comparison below 100 evaluates ordering within the same fixed candidate pool. The restricted query and pool are saved under `legacy_union_normalized/candidate_rerank/`.

## Unavailable arms

The restored OQL, keyword, no-geography and full-text arms still return HTTP 400 when relevance sorting is requested. Their default cursor orders are reported where execution and validation passed. These results must not be relabelled as validated native relevance rankings. The full-text arm also returns HTTP 504 under default cursor retrieval, so no ranked result is reported for that arm.

No citation, FWCI, date or semantic sort was added. Default order may reflect an API default sort, but that is not inferred to be native relevance. The findings support a narrower cursor-order study, with a separate fixed-candidate reranking test. They do not complete the originally intended native-relevance/reranking comparison for all OQL arms.

## Files and audit

- `rank_metrics.csv` and `metrics.json`: both cohort denominators, all budgets, complete recovery and threshold ranks.
- `reference_ranks.csv`: ranks of previously identified eligible records only.
- Per-arm `default/` and `relevance/` directories: page records, complete ordered ID lists and validation summaries.
- `probe.json`: repeat and page-size tests, rejected modes and unchanged-query reranking evidence.
- Compressed request logs: exact query, view parameters, timestamps, status and response. Credentials are excluded.
- `default_relevance_comparison.json`: full-sequence comparison for the published strategy.

This run made {calls} logged HTTP requests. Successful responses reported a total cost of ${cost:.4f}. Charges without a returned cost field are not independently verified. First request: {min(times)}. Last request: {max(times)}. The scripts are `run_cursor_study.py`, `test_cursor_candidate_rerank.py` and `report_cursor_study.py`. The first supports resuming enumeration from saved pages. Keep these run artifacts intact before a future rerun.

The [OpenAlex search documentation](https://help.openalex.org/api/searching/) describes native reranking as a change to the first 100 records, with later records unchanged. The observed unchanged-query behavior and the fixed-candidate workaround are documented separately here.
'''
(RUN/'CURSOR_ORDER_REPORT.md').write_text(report,encoding='utf-8')
# Scientific output from a standard plotting library. Rendering is inspected separately.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(9,5.3),layout='constrained')
colors=['#235789','#d16f21','#287a50','#8b5c9d','#6c757d']
for color,item in zip(colors,selected):
    points=curves[(item['arm'],item['mode'],'primary')]
    xx=[0]+points+[item['result_count']]
    yy=[0]+[i/131*100 for i in range(1,len(points)+1)]+[len(points)/131*100]
    label=LABELS[item['arm']]
    if item['arm']=='legacy_union_normalized' and not same:
        label+=': '+('relevance requested' if item['mode']=='relevance' else 'default')
    elif item['mode']=='default':
        label+=' (default)'
    ax.step(xx,yy,where='post',label=label,color=color,linewidth=2)
ax.axvline(12293,color='#666666',linestyle='--',linewidth=1,label='Original map: 12,293 screened')
ax.axhline(95,color='#999999',linestyle=':',linewidth=1)
ax.set(xlabel='Records retrieved in cursor order',ylabel='Known original records recovered (%)',
       title='OpenAlex cursor-order recall: Stansfield case',ylim=(0,100),xlim=(0,max(x['result_count'] for x in selected)))
ax.grid(axis='y',alpha=.2);ax.legend(loc='lower right',fontsize=8)
fig.savefig(RUN/'cursor_recall.png',dpi=180);fig.savefig(RUN/'cursor_recall.svg')
plt.close(fig)
print(table)
print(rt)
print(json.dumps(audit,indent=2))
