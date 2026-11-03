from pathlib import Path
import json,zipfile,datetime
P=Path(__file__).parent
labels=[('D_exact','D: original one-sided proximity',3103),('E_inert_reconstructed','E: misplaced topic clause',3701),('E_corrected_reconstructed','E: corrected topic clause',5574),('G1_reconstructed','G1: broad unknown-country exception',12985),('G2_inert_reconstructed','G2: misplaced topic clause',3891),('G2_exact','G2: final query as printed',5764),('G2_strict_reconstructed','G2: tighter distances',5734),('exploratory_unscreen_no_topic','Exploratory: no topic fallback; add unscreen*',None)]
lines=['# OpenAlex live query audit','', 'Run on 2 November 2026, Singapore time. API timestamps are recorded in UTC in the response files.','', 'The supplied draft was read without modifying it. D and G2 were executed verbatim from its complete query strings. Other variants were reconstructed from G2 or the described changes; their exact query strings and API query objects are included. A–C were not reconstructed because the draft does not provide their complete original queries.','', '## Result counts','', '| Query | Draft count | Live count | Named records retrieved / 13 |','|---|---:|---:|---:|']
for k,title,expected in labels:
 d=json.loads((P/(k+'.json')).read_text()); count=d['response']['meta']['count']
 n=json.loads((P/(k+'_named.json')).read_text())['response']['meta']['count']
 lines.append(f'| {title} | {expected if expected is not None else "Not in draft"} | {count} | {n} |')
lines += ['', '## Named-record recovery','', 'This is a diagnostic set of 13 named works extracted from the draft, deliberately enriched for failures. It is not the complete 130-study benchmark and is not a representative recall estimate.','', '| Work | D | E corrected | G2 | G2 tighter | Exploratory unscreen* |','|---|---|---|---|---|---|']
meta=json.loads((P/'named_metadata_classic.json').read_text())['results']
keys=['D_exact','E_corrected_reconstructed','G2_exact','G2_strict_reconstructed','exploratory_unscreen_no_topic']
found={k:{r['id'] for r in json.loads((P/(k+'_named.json')).read_text())['response']['results']} for k in keys}
for r in sorted(meta,key=lambda x:x['id']):
 lines.append('| '+r['display_name']+' ('+r['id'].rsplit('/',1)[-1]+') | '+' | '.join('Yes' if r['id'] in found[k] else 'No' for k in keys)+' |')
lines += ['', '## Verified mechanism and correction','', '- The misplaced topic clause validates (validation.valid=true), but its compiled query treats field-like tokens as text. Executed alone it returns zero works.', '- Removing the inert branch gives the same E count, 3,701. Correcting the topic branch raises E to 5,574 and recovers Felfeli among the diagnostic studies.', '- Felfeli (W4280598166) DOES match diabetic/retinopathy within four words. It does NOT match screen* or the complete screening block of D. Its title contains unscreened. Its absence from D therefore cannot be attributed to failure of that proximity condition.', '- Adding unscreen* to the original screening block, keeping both proximity branches and G2 geography, and omitting the topic fallback returns 3,892 works. All 13 named studies match. This is exploratory, tuned against an observed miss, and is not an independent validation.', '- G2 recovers Lewis, Sachdeva and Ho, which corrected E misses. The tighter-distance G2 also retrieves all 13 named works.', '', '## Additional counts','', '| Test | Live result |','|---|---:|']
for k,desc in [('Elsevier_no_abstract','Elsevier 2024–2025 articles without OpenAlex abstracts'),('Elsevier_no_abstract_PMID','Same set with a PMID'),('AMR_title_abstract','AMR phrase in title/abstract, abstract-less Elsevier subset'),('AMR_about','AMR phrase using about, same subset')]:
 d=json.loads((P/(k+'.json')).read_text()); lines.append(f'| {desc} | {d["response"]["meta"]["count"]} |')
lines += ['', 'Publisher and open-access grouped counts are retained in articles_by_publisher.json and articles_by_OA.json. These reproduce the displayed rounded abstract-availability percentages. A PMID does not establish that a PubMed abstract exists.','', '## Limits','', '- The complete 130 OpenAlex benchmark IDs were not supplied. Neither 128/128 nor 130/130 has been independently verified.', '- Historical 2024/2025 results were not rerun and cannot be reconstructed from current index data alone.', '- Named-study checks append an AND restriction for the 13 IDs to the API-returned canonical OQO. They are not intersections with downloaded full result sets.', '- No complete result-set exports were downloaded; total counts come from API metadata.', '- Fulltext holdings counts, historic A–C queries, and PubMed abstract availability were not tested.', '- JSON files include exploratory validation errors as well as successful responses, to preserve an audit trail. Failed ID-filter trials are superseded by successful ids.openalex tests.', '- No API key is included in this archive.','']
(P/'README.md').write_text('\n'.join(lines))
out=P.parent/'OpenAlex_live_query_audit_2026-11-02.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 z.write(P/'README.md','README.md')
 for f in sorted(P.glob('*.json')): z.write(f,'responses/'+f.name)
print(out)
print('Archived JSON files:',len(list(P.glob('*.json'))))
print('Archive bytes:',out.stat().st_size)
