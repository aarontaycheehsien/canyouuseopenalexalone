import urllib.request,urllib.error,json,sys,concurrent.futures,datetime,math
from pathlib import Path
P=Path(__file__).parent; A=P.parent/'openalex_audit'; KEY=sys.stdin.readline().strip()
q=json.loads((A/'exploratory_unscreen_no_topic.json').read_text())['response']['meta']['x_query']['oqo'];expected=json.loads((P/'exploratory_unscreen_no_topic_total.json').read_text())['response']['meta']['count']
outdir=P/'unrestricted_final_pages';outdir.mkdir(exist_ok=True)
def run(page):
 payload={'oqo':q,'per_page':200,'page':page,'select':'id,display_name','rerank':False}
 req=urllib.request.Request('https://api.openalex.org/',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=55) as r:d=json.load(r)
  (outdir/f'page_{page:02d}.json').write_text(json.dumps({'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'request':payload,'response':d},indent=2));print('page',page,'records',len(d.get('results',[])),flush=True)
 except urllib.error.HTTPError as e:print('page',page,'HTTP',e.code,e.read().decode()[-300:],flush=True)
 except Exception as e:print('page',page,type(e).__name__,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:list(ex.map(run,range(1,math.ceil(expected/200)+1)))
