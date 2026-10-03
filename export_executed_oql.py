"""Display exact submitted arm queries, changing whitespace outside quotes only."""
from pathlib import Path
import hashlib
import json
import re
ROOT=Path(__file__).resolve().parent/'stansfield_pilot'
names=['oql_restored','oql_keywords','oql_fulltext','oql_no_geography']
labels=['1. Restored OQL in title/abstract','2. OQL plus keywords','3. OQL plus keywords and full text','4. OQL plus keywords, geography removed']
def tokens(q):return re.findall(r'"[^"]*"|[()]|[^\s()"]+',q)
def format_query(q):
    # Preserve complete quoted strings and every operator, operand and parenthesis.
    ts=tokens(q)
    lines=[];line='';depth=0
    for t in ts:
        if t==')':depth-=1
        indent='  '*min(depth,4)
        if line and ((len(line)+len(t)+1>100) or (t in ('and','or') and depth<=3)):
            lines.append(line);line=indent+t
        else:line+=((' ' if line else indent)+t)
        if t=='(':depth+=1
    if line:lines.append(line)
    formatted='\n'.join(lines)
    assert tokens(formatted)==ts
    return formatted
logs=[]
for folder in ['query_validation','membership_requests','order_diagnostics','final_checks']:
    path=ROOT/folder/'requests.json'
    if path.exists():logs.extend(json.loads(path.read_text(encoding='utf-8')))
alltext=['# All four executed OQL search arms\n',
 'These are the complete search strings submitted in the pilot. Display copies add whitespace outside quoted strings only. Every token and quoted string was checked against the original. Nothing is abbreviated. Original one-line `.oql` files remain unchanged.\n',
 'Sort, reranking, field selection and pagination were separate request parameters, not OQL clauses. Query 3 was submitted but its retrieval calls failed.\n']
execution=[]
for index,(name,label) in enumerate(zip(names,labels),1):
    raw=(ROOT/'queries'/(name+'.oql')).read_text(encoding='utf-8').strip()
    assert hashlib.sha256(raw.encode()).hexdigest()==json.loads((ROOT/'queries/manifest.json').read_text(encoding='utf-8'))['arms'][name]['sha256']
    body='## '+label+'\n\n```text\n'+format_query(raw)+'\n```\n'
    matching=[]
    variants={}
    for log in logs:
        q=(log.get('body') or {}).get('oql','')
        finite=q.startswith('works where ('+raw[len('works where '):]+') and openalex is (')
        if log['path']=='/' and (q==raw or finite):
            matching.append(log)
            if finite:variants[q]=True
    assert any((x.get('body') or {}).get('oql')==raw for x in matching)
    body+='\n### Known-record membership variant\n\nThe following restricted version was submitted to check membership of the matched reference IDs. Its returned order was not used as the global search ranking.\n'
    for q in variants:body+='\n```text\n'+format_query(q)+'\n```\n'
    if not variants:body+='\nNo matching restricted request found.\n'
    body+='\n### Execution requests\n\n| UTC time | Status | View parameters |\n| --- | ---: | --- |\n'
    for log in matching:
        params={k:v for k,v in log['body'].items() if k!='oql'}
        role='reference restriction' if log['body']['oql']!=raw else 'whole-case query'
        body+='| '+log['time_utc']+' | '+str(log['status'])+' | '+role+'; `'+json.dumps(params)+'` |\n'
        execution.append({'arm':index,'role':role,'time_utc':log['time_utc'],'status':log['status'],'path':log['path'],'body':log['body']})
    (ROOT/'queries'/(name+'_executed.md')).write_text('# '+label+'\n\n'+body.split('\n',1)[1],encoding='utf-8')
    alltext.append(body)
(ROOT/'ALL_FOUR_OQL_QUERIES.md').write_text('\n'.join(alltext),encoding='utf-8')
(ROOT/'queries/all_four_execution_payloads.json').write_text(json.dumps(execution,indent=2),encoding='utf-8')
print({'arms':4,'execution_requests':len(execution),'token_preservation_checks':'passed','output':'ALL_FOUR_OQL_QUERIES.md'})
