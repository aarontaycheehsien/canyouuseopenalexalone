import os
os.environ['OPENALEX_OQL_OUTPUT']='stansfield_pilot/legacy_translation_checks'
from pilot_oql_validation import Pilot,OUT
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent/'stansfield_pilot'
p=Pilot()
ref=json.loads((ROOT/'reference_records.json').read_text(encoding='utf-8'))
branches=json.loads((ROOT/'legacy_branch_membership.json').read_text(encoding='utf-8'))
union=json.loads((ROOT/'membership_summary.json').read_text(encoding='utf-8'))['legacy_union']['returned_known_ids']
classic=set().union(*(set(x['hits']) for x in branches))
different=classic^set(union)
print('Different',[(r['title'],r['current_openalex_id']) for r in ref if r['current_openalex_id'] in different],flush=True)
translated=json.loads((ROOT/'queries/legacy_translated.json').read_text(encoding='utf-8'))
universe='openalex is ('+' or '.join(sorted({r['current_openalex_id'] for r in ref if r['current_openalex_id']}))+')'
results=[]
for tr,branch in zip(translated,branches):
    q='works where ('+tr['oql'][len('works where '):]+') and '+universe
    s,r=p.execute(q,per_page=200,select='id')
    hits={x['id'].rsplit('/',1)[-1] for x in r.get('results',[])}
    complete=s==200 and r.get('meta',{}).get('count')==len(hits)
    item={'line':branch['line'],'status':s,'complete':complete,'classic_hits':branch['hits'],
      'oql_hits':sorted(hits),'same_membership':complete and hits==set(branch['hits']),
      'classic_only':sorted(set(branch['hits'])-hits),'oql_only':sorted(hits-set(branch['hits']))}
    results.append(item)
    print('branch',branch['line'],{k:v for k,v in item.items() if not k.endswith('hits')},flush=True)
(OUT/'summary.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
