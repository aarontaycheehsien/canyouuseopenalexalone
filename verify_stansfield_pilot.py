"""Focused consistency checks for the pilot's denominators, identity and query semantics."""
import os
os.environ['OPENALEX_OQL_OUTPUT']='stansfield_pilot/final_checks'
from pilot_oql_validation import Pilot,OUT
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent/'stansfield_pilot'
p=Pilot()
for name in ['oql_restored','oql_keywords','oql_fulltext','oql_no_geography','legacy_union']:
    q=(ROOT/'queries'/(name+'.oql')).read_text(encoding='utf-8').strip()
    st,tr=p.translate(q)
    sr,rt=p.request('/query',{'oqo':tr['oqo']})
    p.check('final_roundtrip:'+name,st==sr==200 and tr['oqo']==rt.get('oqo'))
q=(ROOT/'queries/legacy_union.oql').read_text(encoding='utf-8').strip()
st,a=p.execute(q,per_page=200,sort='relevance_score:desc',select='id,relevance_score')
sc,b=p.execute(q,per_page=200,cursor='*',sort='relevance_score:desc',select='id,relevance_score')
ids=lambda r:[x['id'] for x in r.get('results',[])]
p.check('legacy_native_cursor_same_first200',st==sc==200 and ids(a)==ids(b),
        {'status':sc,'overlap':len(set(ids(a))&set(ids(b)))})
(OUT/'summary.json').write_text(json.dumps({'checks':p.checks},indent=2),encoding='utf-8')
