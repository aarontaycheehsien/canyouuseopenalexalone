"""Known-positive membership only. No ranking or labels for other records."""
import os
os.environ['OPENALEX_OQL_OUTPUT']='stansfield_pilot/membership_requests'
from pilot_oql_validation import Pilot, OUT
from inspect_source_workbooks import read_xlsx
import csv
import json
from pathlib import Path
import re
import unicodedata
ROOT=Path(__file__).resolve().parent/'stansfield_pilot'
p=Pilot()
source=read_xlsx(ROOT/'sources/reference.xlsx')['Includes in DES map = 133']
refs=[]
for row in source:
    c={re.sub(r'\d','',k):v for k,v in row.items()}
    if not c.get('A','').isdigit():continue
    refs.append({'eppi_id':c['A'],'primary':c.get('B')=='y','historical_present':c.get('C')=='y',
      'original_openalex_id':'W'+c['D'] if c.get('D','').isdigit() else None,
      'historical_july_retrieved':c.get('E')=='y','historical_march_retrieved':c.get('F')=='y',
      'pubmed_retrieved':c.get('G')=='y','pmid':c.get('H'), 'short_title':c.get('I'),
      'title':c['J'],'source_year':int(c['K'])})
assert len(refs)==133 and sum(x['primary'] for x in refs)==131
assert sum(x['pubmed_retrieved'] and x['primary'] for x in refs)==117
def norm(s):return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s).lower())
known=[x['original_openalex_id'] for x in refs if x['original_openalex_id']]
current={}
for start in range(0,len(known),80):
    s,r=p.request('/works',params={'filter':'openalex_id:'+'|'.join(known[start:start+80]),'per_page':200})
    if s!=200:raise RuntimeError('ID lookup failed')
    current.update({x['id'].rsplit('/',1)[-1]:x for x in r['results']})
for ref in refs:
    wid=ref['original_openalex_id']
    record=current.get(wid)
    if wid and not record:
        s,r=p.request('/works/'+wid)
        if s==200 and r.get('id'):
            record=r
            current[r['id'].rsplit('/',1)[-1]]=r
    if record:
        # The published workbook has three pairs of OpenAlex IDs swapped.
        # Correct only where the source PMID AND normalized title independently agree.
        observed_pmid=record.get('ids',{}).get('pmid','') or ''
        if ref.get('pmid') and observed_pmid and observed_pmid.rsplit('/',1)[-1]!=ref['pmid']:
            verified=[x for x in current.values() if (x.get('ids',{}).get('pmid','') or '').rsplit('/',1)[-1]==ref['pmid']
                      and norm(x['display_name'])==norm(ref['title'])]
            if len(verified)!=1:raise RuntimeError('Conflicting source identity needs manual resolution')
            record=verified[0]
            method='source_id_corrected_by_pmid_and_exact_title'
        else:method='published_id'
        ref.update(current_openalex_id=record['id'].rsplit('/',1)[-1],match_method='published_id',
                   current_year=record['publication_year'],current_title=record['display_name'],
                   current_doi=record.get('doi'))
        ref['match_method']=method
    else:
        s,r=p.request('/works',params={'search.title':ref['title'],'per_page':5})
        candidates=r.get('results',[])
        (OUT/(ref['eppi_id']+'_candidates.json')).write_text(json.dumps(candidates,indent=2),encoding='utf-8')
        exact=[x for x in candidates if norm(x['display_name'])==norm(ref['title']) and x['publication_year']==ref['source_year']]
        if len(exact)==1:
            record=exact[0]
            ref.update(current_openalex_id=record['id'].rsplit('/',1)[-1],match_method='exact_title_and_year',
                       current_year=record['publication_year'],current_title=record['display_name'],current_doi=record.get('doi'))
            current[ref['current_openalex_id']]=record
        else:ref.update(current_openalex_id=None,match_method='unresolved',current_year=None)
    ref['within_date_window']=bool(ref['current_year'] and 2003<=ref['current_year']<=2023)
(ROOT/'reference_records.json').write_text(json.dumps(refs,indent=2,ensure_ascii=False),encoding='utf-8')
(ROOT/'current_reference_metadata.json').write_text(json.dumps(list(current.values()),indent=2,ensure_ascii=False),encoding='utf-8')
print('Coverage',sum(bool(x['current_openalex_id']) for x in refs),'of',len(refs),flush=True)
universe='openalex is ('+' or '.join(sorted({x['current_openalex_id'] for x in refs if x['current_openalex_id']}))+')'
result={}
names=['oql_restored','oql_keywords','oql_fulltext','oql_no_geography','legacy_union']
for name in names:
    path=ROOT/'queries'/(name+'.oql')
    if not path.exists():
        result[name]={'status':'missing_query'}
        continue
    q=path.read_text(encoding='utf-8').strip()
    s,r=p.execute(q,per_page=1,select='id,publication_year')
    sf,rf=p.execute('works where ('+q[len('works where '):]+') and '+universe,per_page=200,select='id,publication_year')
    hits={x['id'].rsplit('/',1)[-1] for x in rf.get('results',[])}
    complete=sf==200 and rf.get('meta',{}).get('count')==len(hits)
    item={'count_status':s,'total_query_count':r.get('meta',{}).get('count'),
          'finite_status':sf,'finite_complete':complete,'returned_known_ids':sorted(hits)}
    if complete:
        assert all(2003<=x['publication_year']<=2023 for x in rf['results'])
        for ref in refs:ref[name+'_retrieved']=ref['current_openalex_id'] in hits
        item['primary_retrieved']=sum(ref[name+'_retrieved'] for ref in refs if ref['primary'])
        item['secondary_retrieved']=sum(ref[name+'_retrieved'] for ref in refs)
    else:item['error']=rf
    result[name]=item
    (ROOT/'membership_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(name,{k:v for k,v in item.items() if k not in ('returned_known_ids','error')},flush=True)
# Independent replay of the nine source branches, union only after membership lookup.
manifest=json.loads((ROOT/'queries/manifest.json').read_text(encoding='utf-8'))
legacy_hits=set()
branch=[]
for arm in manifest['legacy_searches']:
    allids=sorted({x['current_openalex_id'] for x in refs if x['current_openalex_id']})
    ids=set()
    complete=True
    for start in range(0,len(allids),80):
        s,r=p.request(arm['oxurl']+',openalex_id:'+'|'.join(allids[start:start+80])+'&per_page=200')
        subset={x['id'].rsplit('/',1)[-1] for x in r.get('results',[])}
        complete=complete and s==200 and r.get('meta',{}).get('count')==len(subset)
        ids.update(subset)
    branch.append({'line':arm['line'],'status':s,'complete':complete,'hits':sorted(ids)})
    if complete:legacy_hits.update(ids)
    print('source branch',arm['line'],s,len(ids),flush=True)
(ROOT/'legacy_branch_membership.json').write_text(json.dumps(branch,indent=2),encoding='utf-8')
if all(x['complete'] for x in branch):
    result['legacy_independent']={'primary_retrieved':sum(x['current_openalex_id'] in legacy_hits for x in refs if x['primary']),
      'secondary_retrieved':sum(x['current_openalex_id'] in legacy_hits for x in refs),
      'union_equals_oql_union':legacy_hits==set(result.get('legacy_union',{}).get('returned_known_ids',[]))}
(ROOT/'membership_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
(ROOT/'reference_records.json').write_text(json.dumps(refs,indent=2,ensure_ascii=False),encoding='utf-8')
fields=list(dict.fromkeys(k for r in refs for k in r))
with (ROOT/'reference_retrieval.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(refs)
print('Finished known-record membership',flush=True)
