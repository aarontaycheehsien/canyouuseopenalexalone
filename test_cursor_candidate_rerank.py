"""Test a disclosed native-rerank comparison with identical cursor candidates."""
from run_cursor_study import Client,ROOT,RUN,ids,read,save
from pilot_credentials import load_key
import hashlib
load_key()
name='legacy_union_normalized'
probe=read(RUN/name/'probe.json')
native=probe['modes']['relevance']['prefix_ids']
pool=native[:100]
assert len(pool)==len(set(pool))==100
q=(ROOT/'queries'/(name+'.oql')).read_text(encoding='utf-8').strip()
restricted='works where ('+q[len('works where '):]+') and openalex is ('+' or '.join(pool)+')'
folder=RUN/name/'candidate_rerank'
folder.mkdir(exist_ok=True)
(folder/'restricted_query.oql').write_text(restricted+'\n',encoding='utf-8')
save(folder/'cursor_candidate_ids.json',pool)
c=Client(name+'/candidate_rerank/requests')
s,a=c.call(restricted,per_page=100,cursor='*',sort='relevance_score:desc',rerank=True)
s2,b=c.call(restricted,per_page=100,cursor='*',sort='relevance_score:desc',rerank=True)
summary={'status':s,'repeat_status':s2,'reported_count':a.get('meta',{}).get('count'),
 'returned':len(ids(a)),'candidate_membership_preserved':set(ids(a))==set(pool),
 'repeated_order_identical':s==s2==200 and ids(a)==ids(b),
 'reranked':a.get('meta',{}).get('reranked'),'reranked_repeat':b.get('meta',{}).get('reranked'),
 'query_sha256':hashlib.sha256(restricted.encode()).hexdigest(),
 'protocol_note':'Native reranker called on the original query AND the fixed first 100 cursor IDs. This is a candidate-restricted comparison, not an unchanged-query rerank call.'}
summary['valid_candidate_rerank']=s==s2==200 and summary['reported_count']==100 and len(ids(a))==100 and summary['candidate_membership_preserved'] and summary['repeated_order_identical'] and summary['reranked'] is True and summary['reranked_repeat'] is True
if not summary['valid_candidate_rerank']:summary['error']=a.get('validation',a.get('error'))
save(folder/'ordered_ids.json',ids(a));save(folder/'summary.json',summary)
print(summary,flush=True)
