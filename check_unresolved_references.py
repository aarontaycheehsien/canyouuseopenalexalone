import os
os.environ['OPENALEX_OQL_OUTPUT']='stansfield_pilot/unresolved_checks'
from pilot_oql_validation import Pilot,OUT
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent/'stansfield_pilot'
p=Pilot()
checks=[('94497704','barriers enablers eye care','2012'),('94499085','Non-attendance Diabetes Eye Services South Auckland','2022'),('93704206','Improving retinopathy screening NSF target','2004')]
for eppi,terms,year in checks:
    s,r=p.request('/works',params={'search.title':terms,'filter':'publication_year:'+year,'per_page':10})
    print(eppi,s,[(x['id'],x['display_name'],x['publication_year']) for x in r.get('results',[])],flush=True)
refs=json.loads((ROOT/'reference_records.json').read_text(encoding='utf-8'))
metadata=json.loads((ROOT/'current_reference_metadata.json').read_text(encoding='utf-8'))
lookup={x['id'].rsplit('/',1)[-1]:x for x in metadata}
mismatches=[]
for ref in refs:
    record=lookup.get(ref['current_openalex_id'])
    if ref.get('pmid') and record:
        pmid=record.get('ids',{}).get('pmid')
        if pmid and pmid.rsplit('/',1)[-1]!=ref['pmid']:
            mismatches.append({'eppi':ref['eppi_id'],'source_pmid':ref['pmid'],'current_pmid':pmid})
(OUT/'identifier_check.json').write_text(json.dumps({'pmid_mismatches':mismatches},indent=2),encoding='utf-8')
print('PMID mismatches',mismatches,flush=True)
