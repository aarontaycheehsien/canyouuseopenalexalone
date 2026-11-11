import urllib.request,urllib.parse,urllib.error,json,sys,copy,datetime,concurrent.futures
from pathlib import Path
P=Path(__file__).parent; A=P.parent/'openalex_audit'; KEY=sys.stdin.readline().strip()
records=json.loads((P/'benchmark_source_records.json').read_text()); ids=[r['openalex_id'] for r in records if r['openalex_id']]
assert len(ids)==len(set(ids))==130
(P/'benchmark_130_ids.txt').write_text('\n'.join(ids)+'\n')
idfilter={'join':'or','filters':[{'column_id':'ids.openalex','value':i} for i in ids]}
labels=['D_exact','E_inert_reconstructed','E_corrected_reconstructed','G1_reconstructed','G2_inert_reconstructed','G2_exact','G2_strict_reconstructed','exploratory_unscreen_no_topic']
jobs=[]
for label in labels:
 old=json.loads((A/(label+'.json')).read_text())
 obj=copy.deepcopy(old['response']['meta']['x_query']['oqo'])
 jobs.append((label+'_total',{'oqo':obj,'per_page':1,'select':'id,display_name'}))
 filtered=copy.deepcopy(obj); filtered.setdefault('filter_rows',[]).append(idfilter)
 jobs.append((label+'_benchmark',{'oqo':filtered,'per_page':200,'select':'id,display_name,publication_year,doi'}))
jobs.append(('benchmark_metadata',{'oqo':{'get_rows':'works','filter_rows':[idfilter]},'per_page':200,'select':'id,display_name,publication_year,doi,ids'}))
def call(item):
 label,payload=item
 out={'label':label,'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'request':payload}
 req=urllib.request.Request('https://api.openalex.org/',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=55) as r: out.update(status=r.status,response=json.load(r))
 except urllib.error.HTTPError as ex: out.update(status=ex.code,error=ex.read().decode().replace(KEY,'[REDACTED]'))
 except Exception as ex: out.update(status='error',error=type(ex).__name__)
 (P/(label+'.json')).write_text(json.dumps(out,indent=2))
 resp=out.get('response',{}); found={r['id'].rsplit('/',1)[-1] for r in resp.get('results',[])}
 summary={'label':label,'status':out['status'],'count':resp.get('meta',{}).get('count')}
 if label.endswith('_benchmark'): summary['misses']=[{'id':r['openalex_id'],'short':r['short_title'],'title':r['title']} for r in records if r['openalex_id'] and r['openalex_id'] not in found]
 if out.get('error'): summary['error']=out['error'][-2000:]
 print(json.dumps(summary),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex: list(ex.map(call,jobs))
