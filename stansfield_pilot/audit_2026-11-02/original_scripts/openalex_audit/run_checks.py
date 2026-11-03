import urllib.request,urllib.parse,urllib.error,json,sys,datetime,concurrent.futures
from pathlib import Path
ROOT=Path(__file__).parent
KEY=sys.stdin.readline().strip()
D=json.loads((ROOT/'draft_queries.json').read_text())
ids=json.loads((ROOT/'named_ids.json').read_text())
g2=D['71']; vd=D['44']
scoped=' or (country is unknown and title has ("diabetic retinopathy screening" OR "diabetic eye screening"))'
e=g2.replace(scoped,'')
g1=g2.replace(scoped,' or country is unknown')
strict=g2.replace('within 4 words','within 3 words').replace('within 6 words','within 5 words')
qset={'D_exact':vd,'E_corrected_reconstructed':e,'G1_reconstructed':g1,'G2_exact':g2,'G2_strict_reconstructed':strict,
'Elsevier_no_abstract':'get articles from 2024–2025 published by [Elsevier BV](P4310320990) where it doesn\'t have an abstract',
'Elsevier_no_abstract_PMID':'get articles from 2024–2025 published by [Elsevier BV](P4310320990) where it doesn\'t have an abstract and PMID is not unknown',
'AMR_title_abstract':'get articles from 2024–2025 with "antimicrobial resistance" in the title or abstract published by [Elsevier BV](P4310320990) where it doesn\'t have an abstract',
'AMR_about':'get articles from 2024–2025 about "antimicrobial resistance" published by [Elsevier BV](P4310320990) where it doesn\'t have an abstract',
'articles_by_OA':'get the count and percent with an abstract of articles from 2024–2025 by open access',
'articles_by_publisher':'get the count and percent with an abstract of articles from 2024–2025 by publisher',
'named_records_test':'get works where work is ('+' or '.join(ids)+')'}
(ROOT/'queries_executed.json').write_text(json.dumps(qset,indent=2))
def call(label,q):
 params={'oql':q,'per_page':'1','select':'id,display_name'}
 if label.startswith('articles_by_'): params={'oql':q}
 u='https://api.openalex.org/?'+urllib.parse.urlencode(params)
 result={'label':label,'query':q,'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 req=urllib.request.Request(u,headers={'Authorization':'Bearer '+KEY})
 try:
  with urllib.request.urlopen(req,timeout=55) as r: result.update(status=r.status,response=json.load(r))
 except urllib.error.HTTPError as ex:
  body=ex.read().decode(); result.update(status=ex.code,error=body.replace(KEY,'[REDACTED]'))
 except Exception as ex: result.update(status='error',error=type(ex).__name__)
 (ROOT/(label+'.json')).write_text(json.dumps(result,indent=2))
 resp=result.get('response',{})
 print(json.dumps({'label':label,'status':result['status'],'count':resp.get('meta',{}).get('count'),'summary':resp.get('summary'),'groups':resp.get('group_by',[])[:18],'sample':resp.get('results',[])[:1],'error':result.get('error')}),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 list(pool.map(lambda x:call(*x),qset.items()))
