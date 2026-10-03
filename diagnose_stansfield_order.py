import os
os.environ['OPENALEX_OQL_OUTPUT']='stansfield_pilot/order_diagnostics'
from pilot_oql_validation import Pilot,OUT
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent/'stansfield_pilot'
p=Pilot()
summary={}
ids=lambda r:[x['id'].rsplit('/',1)[-1] for x in r.get('results',[])]
for name in ['oql_restored','oql_keywords','oql_no_geography','legacy_union']:
    q=(ROOT/'queries'/(name+'.oql')).read_text(encoding='utf-8').strip()
    s,a=p.execute(q,per_page=200,select='id,relevance_score,publication_year')
    sr,b=p.execute(q,per_page=200,sort='relevance_score:desc',select='id,relevance_score,publication_year')
    ss,c=p.execute(q,per_page=200,sort='relevance_score:desc',rerank=True,select='id,relevance_score,publication_year')
    sd,d=p.execute(q,per_page=200,select='id,relevance_score,publication_year')
    sc,e=p.execute(q,per_page=200,cursor='*',select='id,relevance_score,publication_year')
    item={'default_status':s,'relevance_status':sr,'reranked_status':ss,
      'default_repeat_identical':s==sd==200 and ids(a)==ids(d),
      'default_cursor_status':sc,'default_cursor_first200_identical':s==sc==200 and ids(a)==ids(e),
      'numeric_relevance':bool(b.get('results')) and all(isinstance(x.get('relevance_score'),(int,float)) for x in b.get('results',[])),
      'native_rerank_executed':c.get('meta',{}).get('reranked'),
      'default_first200':ids(a),'native_first200':ids(b),'reranked_first200':ids(c),
      'default_vs_relevance_identical':s==sr==200 and ids(a)==ids(b)}
    if sr!=200:item['relevance_error']=b.get('validation',{}).get('errors',b.get('error'))
    summary[name]=item
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(name,{k:v for k,v in item.items() if not k.endswith('first200')},flush=True)
# Minimal exact/stemmed positive controls and alternate execution doors.
controls={}
for name,q in [('exact','works where title/abstract has ("retinopathy") and year >= (2003) and year <= (2023)'),
               ('stemmed','works where title/abstract has (retinopathy) and year >= (2003) and year <= (2023)')]:
    st,tr=p.translate(q)
    post,r=p.execute(q,per_page=3,sort='relevance_score:desc')
    get,rg=p.request('/',params={'oql':q,'per_page':3,'sort':'relevance_score:desc'})
    oq,ro=p.request('/',{'oqo':tr['oqo'],'per_page':3,'sort':'relevance_score:desc'})
    controls[name]={'POST':post,'GET':get,'OQO':oq,'scores':[x.get('relevance_score') for x in r.get('results',[])]}
(OUT/'minimal_controls.json').write_text(json.dumps(controls,indent=2),encoding='utf-8')
print('Controls',controls,flush=True)
