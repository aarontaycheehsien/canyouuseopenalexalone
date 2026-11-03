import urllib.request,urllib.parse,urllib.error,json,sys,datetime,concurrent.futures,copy
from pathlib import Path
P=Path(__file__).parent
KEY=sys.stdin.readline().strip()
ids=json.loads((P/'named_ids.json').read_text())
queries=json.loads((P/'queries_executed.json').read_text())
fallback='screen* OR program* OR care OR utilization OR teleophthalmolog* OR exam* OR check* OR slick OR keepsight OR retinascreen*'
g2=queries['G2_exact']; e=queries['E_corrected_reconstructed']
main=g2.split('and (title-abstract-keywords has (',1)[1].split(' or (topic is ',1)[0][:-1]
geo=e.split(' and (country is ',1)[1][:-1]
geo='country is '+geo
geog2='country is '+g2.split(' and (country is ',1)[1][:-1]
inert='(topic is T10170 AND title-abstract-keywords has ('+fallback+'))'
newqs={
 'E_inert_reconstructed':'get works from 2003–2023 about ('+main+' OR '+inert+') where '+geo,
 'G2_inert_reconstructed':'get works from 2003–2023 about ('+main+' OR '+inert+') where '+geog2,
 'two_branches_no_topic':'get works from 2003–2023 about ('+main+') where '+geo,
 'inert_topic_alone':'get works about '+inert,
 'topic_filter_alone':'get works where topic is T10170 and title-abstract-keywords has ('+fallback+')'
}
(P/'extra_queries.json').write_text(json.dumps(newqs,indent=2))
idfilter={'join':'or','filters':[{'column_id':'id','value':i} for i in ids]}
jobs=[]
for label in ['D_exact','E_corrected_reconstructed','G1_reconstructed','G2_exact','G2_strict_reconstructed']:
 obj=json.loads((P/(label+'.json')).read_text())['response']['meta']['x_query']['oqo']
 obj=copy.deepcopy(obj); obj.setdefault('filter_rows',[]).append(idfilter)
 jobs.append((label+'_named',{'oqo':obj,'per_page':200,'select':'id,display_name'}))
jobs.extend((k,{'oql':q,'per_page':1,'select':'id,display_name'}) for k,q in newqs.items())
jobs.append(('named_metadata',{'oqo':{'get_rows':'works','filter_rows':[idfilter]},'per_page':200,'select':'id,display_name,publication_year,authorships,primary_topic,topics,keywords,abstract_inverted_index,ids'}))
def call(item):
 label,payload=item
 req=urllib.request.Request('https://api.openalex.org/',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'})
 out={'label':label,'request':payload,'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(req,timeout=55) as r: out.update(status=r.status,response=json.load(r))
 except urllib.error.HTTPError as ex: out.update(status=ex.code,error=ex.read().decode().replace(KEY,'[REDACTED]'))
 except Exception as ex: out.update(status='error',error=type(ex).__name__)
 (P/(label+'.json')).write_text(json.dumps(out,indent=2))
 resp=out.get('response',{}); rows=resp.get('results',[])
 print(json.dumps({'label':label,'status':out['status'],'count':resp.get('meta',{}).get('count'),'ids':[x.get('id') for x in rows],'error':out.get('error','')[:1000]}),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: list(pool.map(call,jobs))
