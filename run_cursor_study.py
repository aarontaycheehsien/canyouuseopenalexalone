"""Evaluate explicitly chosen cursor order; never substitute a new search strategy.

Each worker has independent compressed request logs. Run --probe first, then
--enumerate. Resume enumeration from saved pages with the same opaque cursor.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request
from pilot_credentials import load_key

ROOT=Path(__file__).resolve().parent/'stansfield_pilot'
RUN=ROOT/'cursor_study_2026-10-04'
RUN.mkdir(exist_ok=True)
NAMES=['legacy_union_normalized','oql_restored','oql_keywords','oql_fulltext','oql_no_geography']
SELECT='id,publication_year,relevance_score'
def save(path,value):
    path.write_text(json.dumps(value,indent=2),encoding='utf-8')
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def ids(result):return [r['id'].rsplit('/',1)[-1] for r in result.get('results',[])]
class Client:
    def __init__(self,name):
        self.path=RUN/name
        self.path.mkdir(parents=True,exist_ok=True)
        self.seq=max([int(p.name.split('_')[0]) for p in self.path.glob('*_request.json.gz')]+[0])
    def call(self,q,**view):
        body={'oql':q,'per_page':200,'select':SELECT,**view}
        req=urllib.request.Request('https://api.openalex.org/',data=json.dumps(body).encode(),
          headers={'Content-Type':'application/json','User-Agent':'OpenAlex-ES-cursor-study/1.0',
                   'Authorization':'Bearer '+os.environ['OPENALEX_API_KEY']},method='POST')
        for attempt in range(2):
            started=datetime.now(timezone.utc).isoformat()
            try:
                with urllib.request.urlopen(req,timeout=45) as response:
                    status=response.status;raw=response.read().decode('utf-8','replace')
            except urllib.error.HTTPError as e:
                status=e.code;raw=e.read().decode('utf-8','replace')
            except (OSError,TimeoutError) as e:
                status=0;raw=json.dumps({'transport_error':type(e).__name__})
            try:value=json.loads(raw)
            except json.JSONDecodeError:value={'non_json_response':raw[:500]}
            self.seq+=1
            log={'started_utc':started,'completed_utc':datetime.now(timezone.utc).isoformat(),
                 'path':'/','body':body,'status':status,'response':value}
            with gzip.open(self.path/f'{self.seq:05d}_request.json.gz','wt',encoding='utf-8') as f:
                json.dump(log,f,ensure_ascii=False)
            if status not in (0,429,502,503) or attempt==1:break
            time.sleep(2)
        return status,value

def walk_prefix(client,q,size,records=400,**mode):
    cursor='*';allids=[];responses=[];status=200
    while len(allids)<records:
        status,r=client.call(q,per_page=size,cursor=cursor,**mode)
        responses.append({'status':status,'count':r.get('meta',{}).get('count'),
           'reranked':r.get('meta',{}).get('reranked'),'numeric_scores':sum(isinstance(x.get('relevance_score'),(int,float)) for x in r.get('results',[]))})
        if status!=200:break
        allids.extend(ids(r));cursor=r.get('meta',{}).get('next_cursor')
        if not cursor:break
    return {'status':status,'ids':allids,'responses':responses}

def probe(name):
    c=Client(name+'/probe')
    q=(ROOT/'queries'/(name+'.oql')).read_text(encoding='utf-8').strip()
    item={'arm':name,'query_sha256':hashlib.sha256(q.encode()).hexdigest(),'modes':{}}
    for label,mode in [('relevance',{'sort':'relevance_score:desc'}),('default',{})]:
        a=walk_prefix(c,q,200,**mode)
        test={'status':a['status'],'prefix_ids':a['ids'],'responses':a['responses']}
        if a['status']==200 and len(a['ids'])==400:
            b=walk_prefix(c,q,200,**mode)
            small=walk_prefix(c,q,100,**mode)
            test.update(repeated_prefix_identical=b['status']==200 and a['ids']==b['ids'],
              page_size_invariant=small['status']==200 and a['ids']==small['ids'],
              prefix_unique=len(set(a['ids']))==400,
              count_stable=len({x['count'] for p in [a,b,small] for x in p['responses']})==1,
              eligible_for_enumeration=b['status']==small['status']==200 and a['ids']==b['ids']==small['ids'] and len(set(a['ids']))==400 and len({x['count'] for p in [a,b,small] for x in p['responses']})==1)
        else:test['eligible_for_enumeration']=False
        item['modes'][label]=test
        save(RUN/name/'probe.json',item)
        print(name,label,{k:v for k,v in test.items() if k not in ['prefix_ids','responses']},flush=True)
    native=item['modes']['relevance'];default=item['modes']['default']
    item['default_same_as_relevance_prefix']=native['status']==default['status']==200 and native['prefix_ids']==default['prefix_ids']
    # Test only accepted native relevance arms. The entire run uses cursor=*.
    if native['status']==200:
        reranked=walk_prefix(c,q,200,**{'sort':'relevance_score:desc','rerank':True})
        nr=native['prefix_ids'];rr=reranked['ids']
        item['rerank']={'status':reranked['status'],'responses':reranked['responses'],'prefix_ids':rr,
           'top100_membership_preserved':len(rr)>=100 and set(nr[:100])==set(rr[:100]),
           'positions101_400_unchanged':len(rr)==400 and nr[100:400]==rr[100:400],
           'no_duplicates':len(rr)==len(set(rr)),
           'first_page_reranked':bool(reranked['responses']) and reranked['responses'][0]['reranked'] is True}
        if reranked['status']==200 and len(rr)==400:
            again=walk_prefix(c,q,200,**{'sort':'relevance_score:desc','rerank':True})
            item['rerank']['repeated_prefix_identical']=again['status']==200 and rr==again['ids']
        save(RUN/name/'probe.json',item)
        print(name,'rerank',{k:v for k,v in item['rerank'].items() if k not in ['prefix_ids','responses']},flush=True)
    save(RUN/name/'probe.json',item)
    return item

def enumerate_mode(name,label):
    pth=RUN/name/'probe.json'
    probe_data=read(pth)
    p=probe_data['modes'][label]
    if not p.get('eligible_for_enumeration'):return {'arm':name,'mode':label,'status':'probe_failed'}
    folder=RUN/name/label
    folder.mkdir(exist_ok=True)
    c=Client(name+'/'+label+'/requests')
    q=(ROOT/'queries'/(name+'.oql')).read_text(encoding='utf-8').strip()
    mode={'sort':'relevance_score:desc'} if label=='relevance' else {}
    rows=[];cursor='*';count=None;meta=[]
    for pagefile in sorted(folder.glob('page_*.json')):
        page=read(pagefile)
        rows.extend(page['results']);cursor=page['next_cursor'];count=page['count'];meta.append(page['page_meta'])
    if not rows or cursor:
        while cursor:
            status,r=c.call(q,cursor=cursor,**mode)
            if status!=200:
                failure={'arm':name,'mode':label,'status':'execution_failed','http_status':status,'records':len(rows),'expected':count}
                save(folder/'summary.json',failure)
                print(name,label,failure,flush=True);return failure
            page_count=r['meta']['count']
            if count is None:count=page_count
            chunk=r['results'];next_cursor=r['meta'].get('next_cursor')
            page_meta={'count':page_count,'returned':len(chunk),'numeric_scores':sum(isinstance(x.get('relevance_score'),(int,float)) for x in chunk),'dates_in_window':all(2003<=x.get('publication_year',0)<=2023 for x in chunk)}
            meta.append(page_meta)
            page={'count':page_count,'next_cursor':next_cursor,'results':chunk,'page_meta':page_meta}
            save(folder/f'page_{len(meta):05d}.json',page)
            rows.extend(chunk)
            if next_cursor==cursor or (not chunk and next_cursor):
                save(folder/'summary.json',{'status':'cursor_did_not_advance','records':len(rows)})
                return {'status':'cursor_did_not_advance'}
            cursor=next_cursor
            if len(meta)%10==0:print(name,label,len(rows),'/',count,flush=True)
    ordered=[x['id'].rsplit('/',1)[-1] for x in rows]
    # Recheck page boundaries near the start, midpoint and end of the completed walk.
    repeat_checks=[]
    pages=sorted(folder.glob('page_*.json'))
    for index in sorted(set([0,len(pages)//2,max(0,len(pages)-2)])):
        incoming='*' if index==0 else read(pages[index-1])['next_cursor']
        expected=read(pages[index])['results']
        s,r=c.call(q,cursor=incoming,**mode)
        repeat_checks.append({'page':index+1,'status':s,'same_order':s==200 and [x['id'] for x in r['results']]==[x['id'] for x in expected]})
    summary={'arm':name,'mode':label,'status':'complete','reported_count':count,'records':len(rows),
      'unique_records':len(set(ordered)),'duplicates':len(ordered)-len(set(ordered)),
      'count_stable':all(x['count']==count for x in meta),'count_matches_unique':len(set(ordered))==count,
      'all_dates_in_window':all(x['dates_in_window'] for x in meta),
      'numeric_scores':sum(x['numeric_scores'] for x in meta),'pages':len(meta),
      'matches_probe_prefix':ordered[:400]==p['prefix_ids'],
      'boundary_repeat_checks':repeat_checks,'query_sha256':hashlib.sha256(q.encode()).hexdigest(),
      'completed_utc':datetime.now(timezone.utc).isoformat()}
    summary['valid_cursor_walk']=summary['duplicates']==0 and summary['count_stable'] and summary['count_matches_unique'] and summary['all_dates_in_window'] and summary['matches_probe_prefix'] and all(x['same_order'] for x in repeat_checks)
    save(folder/'ordered_ids.json',ordered)
    save(folder/'summary.json',summary)
    print(name,label,{k:v for k,v in summary.items() if k!='boundary_repeat_checks'},flush=True)
    return summary

if __name__=='__main__':
    load_key()
    parser=argparse.ArgumentParser();parser.add_argument('--probe',action='store_true');parser.add_argument('--enumerate',action='store_true')
    parser.add_argument('--arm',choices=NAMES);parser.add_argument('--mode',choices=['relevance','default']);args=parser.parse_args()
    if args.probe:
        with ThreadPoolExecutor(max_workers=4) as pool:
            summaries=list(pool.map(probe,NAMES))
        save(RUN/'probe_summary.json',summaries)
    if args.enumerate:
        jobs=[]
        for name in NAMES:
            if args.arm and name!=args.arm:continue
            for label in ['relevance','default']:
                if args.mode and label!=args.mode:continue
                if read(RUN/name/'probe.json')['modes'][label].get('eligible_for_enumeration'):jobs.append((name,label))
        with ThreadPoolExecutor(max_workers=4) as pool:
            summaries=list(pool.map(lambda x:enumerate_mode(*x),jobs))
        save(RUN/('enumeration_summary.json' if not args.arm else args.arm+'_resume_summary.json'),summaries)
