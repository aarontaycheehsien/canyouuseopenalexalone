import os
os.environ['OPENALEX_OQL_OUTPUT']='stansfield_pilot/query_validation'
from pilot_oql_validation import Pilot, OUT
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent/'stansfield_pilot'
p=Pilot()
manifest=json.loads((ROOT/'queries/manifest.json').read_text(encoding='utf-8'))
summary={}
for name,arm in manifest['arms'].items():
    q=(ROOT/'queries'/arm['oql_file']).read_text(encoding='utf-8').strip()
    s,tr=p.translate(q)
    item={'parse_status':s,'validation':tr.get('validation')}
    if s==200:
        (ROOT/'queries'/(name+'.oqo.json')).write_text(json.dumps(tr['oqo'],indent=2),encoding='utf-8')
        se,r=p.execute(q,per_page=3)
        sr,rr=p.execute(q,per_page=3,sort='relevance_score:desc')
        item.update(execute_status=se,count=r.get('meta',{}).get('count'),relevance_status=sr,
                    numeric_relevance=all(isinstance(x.get('relevance_score'),(int,float)) for x in rr.get('results',[])) and bool(rr.get('results')),
                    relevance_error=rr if sr!=200 else None)
    summary[name]=item
    print(name,json.dumps({k:v for k,v in item.items() if k not in ('relevance_error','validation')}),flush=True)
    (OUT/'arm_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
legacy=[]
for arm in manifest['legacy_searches']:
    s,tr=p.request('/query',{'oxurl':arm['oxurl']})
    item={'line':arm['line'],'status':s,'validation':tr.get('validation')}
    if s==200:
        item['oqo']=tr['oqo']
        item['oql']=tr['oql']
    legacy.append(item)
    print('legacy',arm['line'],s,flush=True)
    (ROOT/'queries/legacy_translated.json').write_text(json.dumps(legacy,indent=2),encoding='utf-8')
if all(x['status']==200 for x in legacy):
    # Union published branches without inventing an arbitrary cross-query rank merge.
    filters=[{'join':'and','filters':x['oqo']['filter_rows']} for x in legacy]
    union={'get_rows':'works','filter_rows':[{'join':'or','filters':filters}]}
    s,tr=p.request('/query',{'oqo':union})
    if s==200:
        (ROOT/'queries/legacy_union.oql').write_text(tr['oql']+'\n',encoding='utf-8')
        (ROOT/'queries/legacy_union.oqo.json').write_text(json.dumps(union,indent=2),encoding='utf-8')
    summary['legacy_union']={'translation_status':s,'validation':tr.get('validation')}
(OUT/'arm_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
