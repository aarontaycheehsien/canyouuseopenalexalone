"""Repair a documented namespace difference, without changing search terms."""
import os
os.environ['OPENALEX_OQL_OUTPUT']='stansfield_pilot/legacy_country_normalization'
from pilot_oql_validation import Pilot,OUT
from pathlib import Path
import copy
import hashlib
import json
ROOT=Path(__file__).resolve().parent/'stansfield_pilot'
p=Pilot()
translated=json.loads((ROOT/'queries/legacy_translated.json').read_text(encoding='utf-8'))
repairs=[]
def walk(node):
    if isinstance(node,list):
        for x in node:walk(x)
    elif isinstance(node,dict):
        if node.get('column_id')=='authorships.countries' and str(node.get('value','')).lower().startswith('countries/'):
            before=node['value'];node['value']=before.split('/',1)[1].upper()
            repairs.append({'column':node['column_id'],'before':before,'after':node['value']})
        for x in list(node.values()):
            if isinstance(x,(list,dict)):walk(x)
corrected=copy.deepcopy(translated)
for x in corrected:walk(x['oqo'])
oqo={'get_rows':'works','filter_rows':[{'join':'or','filters':[{'join':'and','filters':x['oqo']['filter_rows']} for x in corrected]}]}
s,tr=p.request('/query',{'oqo':oqo})
assert s==200
q=tr['oql']
(ROOT/'queries/legacy_union_normalized.oql').write_text(q+'\n',encoding='utf-8')
(ROOT/'queries/legacy_union_normalized.oqo.json').write_text(json.dumps(oqo,indent=2),encoding='utf-8')
refs=json.loads((ROOT/'reference_records.json').read_text(encoding='utf-8'))
universe='openalex is ('+' or '.join(sorted({r['current_openalex_id'] for r in refs if r['current_openalex_id']}))+')'
st,r=p.execute(q,per_page=1,select='id')
sf,rf=p.execute('works where ('+q[len('works where '):]+') and '+universe,per_page=200,select='id')
hits={x['id'].rsplit('/',1)[-1] for x in rf.get('results',[])}
classic=set().union(*(set(x['hits']) for x in json.loads((ROOT/'legacy_branch_membership.json').read_text(encoding='utf-8'))))
summary={'repairs':repairs,'count_status':st,'total_query_count':r.get('meta',{}).get('count'),
 'finite_status':sf,'finite_complete':sf==200 and rf['meta']['count']==len(hits),
 'known_union_matches_nine_classic_searches':hits==classic,'primary_retrieved':sum(x['current_openalex_id'] in hits for x in refs if x['primary']),
 'secondary_retrieved':sum(x['current_openalex_id'] in hits for x in refs),'returned_known_ids':sorted(hits),'query_sha256':hashlib.sha256(q.encode()).hexdigest()}
assert summary['finite_complete'] and hits==classic
for ref in refs:ref['legacy_union_normalized_retrieved']=ref['current_openalex_id'] in hits
(ROOT/'reference_records.json').write_text(json.dumps(refs,indent=2,ensure_ascii=False),encoding='utf-8')
sr,rr=p.execute(q,per_page=200,sort='relevance_score:desc',select='id,relevance_score')
sc,rc=p.execute(q,per_page=200,sort='relevance_score:desc',cursor='*',select='id,relevance_score')
summary.update(relevance_status=sr,numeric_relevance=bool(rr.get('results')) and all(isinstance(x.get('relevance_score'),(int,float)) for x in rr.get('results',[])),
 relevance_cursor_status=sc,relevance_cursor_same_first200=[x['id'] for x in rr.get('results',[])]==[x['id'] for x in rc.get('results',[])])
(OUT/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print({k:v for k,v in summary.items() if k!='returned_known_ids'},flush=True)
