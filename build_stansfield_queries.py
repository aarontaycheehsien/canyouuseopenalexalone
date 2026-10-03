"""Freeze source-derived queries before examining reference-record retrieval."""
import hashlib
import json
from pathlib import Path
import re
from inspect_source_workbooks import read_xlsx

ROOT=Path(__file__).resolve().parent/'stansfield_pilot'
SRC=ROOT/'sources'
QDIR=ROOT/'queries'
QDIR.mkdir(parents=True,exist_ok=True)
rows=read_xlsx(SRC/'CESM-3-e70038-s003.xlsx')['Sheet1']
cells={k:v for row in rows for k,v in row.items()}
def line(cell):
    return re.sub(r'^\d+\s+', '',cells[cell]).split('.ab,bk,bt,kf,ot,ti.')[0].strip()
def quote(s):return '"'+s.strip().strip('"')+'"'
def normalize(expr):
    # Ovid infix NOT requires explicit AND NOT in OQL. Quotes freeze literal terms.
    tokens=re.findall(r'"[^"]*"|[()]|\b(?:or|and|not)\b|[^\s()]+',expr,flags=re.I)
    out=[]
    for t in tokens:
        if t.lower() in ('or','and'):out.append(t.lower())
        elif t.lower()=='not':out.extend(['and','not'])
        elif t in ('(',')'):out.append(t)
        else:out.append(quote(t))
    return ' '.join(out)
eye=['eye','eyes','retina','retinal','retinopathy','macula','macular','maculopathy','vision']
screen=['screen','screening','diagnosis','diagnoses','detection','test','tests','testing','program','programs','programme','programmes','care','exam','exams','examination','examinations','checks','check-up','check-ups','checkup','checkups','surveillance','monitor','monitoring']
def prox(left,right,gap):
    return '('+' or '.join('within '+str(gap)+' ('+quote(a)+', '+quote(b)+')' for a in left for b in right)+')'
special=['teleophthalmology program*','tele-ophthalmology program*','Tele-retinal retinopathy','teleretinal retinopathy','tele retinal retinopathy','SLICK','keep sight']
p7='('+prox(eye,screen,5)+' or '+' or '.join(map(quote,special))+')'
p14=prox(['diabet*'],eye[:-1],3)
p17=normalize(line('A34'))
topic='(("diabet*" and '+p7+') or ('+p14+' and '+p17+'))'
program=normalize(line('A43'))
geo_text=normalize(line('A47'))
countries='country is (AU or CA or IE or NZ or GB)'
def text(scope,expr):return scope+' has ('+expr+')'
def restored(scope,geo=True):
    core=text(scope,topic)
    if geo:core='('+core+' and ('+text(scope,geo_text)+' or '+countries+'))'
    return '('+text(scope,program)+' or '+core+')'
kw='((keyword is (diabetic-retinopathy) and keyword is (screening or screening-uptake)) or (keyword is (diabetes or diabetes-mellitus or type-1-diabetes or type-2-diabetes or diabetic-complications or diabetes-complications) and keyword is (retinopathy or maculopathy)))'
dates='year >= (2003) and year <= (2023)'
arms={
 'oql_restored':'works where '+restored('title/abstract')+' and '+dates,
 'oql_keywords':'works where ('+restored('title/abstract/keywords')+' or '+kw+') and '+dates,
 'oql_fulltext':'works where ('+restored('title/abstract/keywords')+' or '+restored('full text')+' or '+kw+') and '+dates,
 'oql_no_geography':'works where ('+restored('title/abstract/keywords',False)+' or '+kw+') and '+dates,
}
legacy=re.findall(r'https://openalex.org/works\?filter=[^\n\r]+',(SRC/'CESM-3-e70038-s004.txt').read_text(encoding='utf-8'))
assert len(legacy)==9
manifest={'frozen_before_retrieval':True,'publication_years':[2003,2023],
 'sources':['CESM-3-e70038-s003.xlsx','CESM-3-e70038-s004.docx'],
 'translation_notes':[
  'Controlled Emtree headings, journal-country fields, and Emtree human/animal/geographic exclusions lack equivalent fields and are not claimed restored.',
  'Original text fields approximated by title/abstract; affiliation geography approximated by author-country codes as in the published OpenAlex translation.',
  'Ovid ADJ6 and ADJ4 translated to unordered within 5 and within 3. Cartesian disjunctions preserve synonym alternatives.',
  'Ovid literals quoted to avoid adding stemming; wildcard tokens retained. Source phrase teleophthalmology program* treated as adjacent phrase.',
  'Keyword arms expand the same source-derived terms into title/abstract/keywords and retain the two original keyword-filter branches without geography.',
  'Full-text arm is an explicit union with the keyword arm, so it cannot intentionally reduce membership.',
  'No design filters: original map eligibility includes all designs. No tuning against eligible titles.',
 ],'arms':{}}
for name,q in arms.items():
    (QDIR/(name+'.oql')).write_text(q+'\n',encoding='utf-8')
    manifest['arms'][name]={'oql_file':name+'.oql','sha256':hashlib.sha256(q.encode()).hexdigest(),'characters':len(q)}
manifest['legacy_searches']=[{'line':i,'oxurl':url.replace('https://openalex.org','')+',publication_year:2003-2023'} for i,url in enumerate(legacy,1)]
(QDIR/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print({k:len(v) for k,v in arms.items()})
