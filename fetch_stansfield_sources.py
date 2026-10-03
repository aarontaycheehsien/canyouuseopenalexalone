"""Preserve the public study sources and extract text without modifying originals."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request
import zipfile
import xml.etree.ElementTree as ET

OUT = Path(__file__).resolve().parent / 'stansfield_pilot' / 'sources'
OUT.mkdir(parents=True, exist_ok=True)
sources = {
    'article.xml': 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12302543/fullTextXML',
    'reference.xlsx': 'https://osf.io/download/2nrzy/',
    'pubmed_original.txt': 'https://osf.io/download/3yz5d/',
    'supplements.zip': 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12302543/supplementaryFiles',
}
def fetch(item):
    name, url = item
    target = OUT / name
    try:
        if not target.exists():
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'OpenAlex-ES-pilot/1.0'}), timeout=55) as r:
                data = r.read()
            target.write_bytes(data)
        data = target.read_bytes()
        return {'file':name, 'url':url, 'bytes':len(data), 'sha256':hashlib.sha256(data).hexdigest()}
    except Exception as e:
        return {'file':name,'url':url,'error':type(e).__name__}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    manifest = list(pool.map(fetch,sources.items()))
if (OUT/'supplements.zip').exists() and zipfile.is_zipfile(OUT/'supplements.zip'):
    with zipfile.ZipFile(OUT/'supplements.zip') as z:
        for n in z.namelist():
            if n.lower().endswith(('.docx','.xlsx','.pptx')):
                (OUT / Path(n).name).write_bytes(z.read(n))
for p in OUT.glob('*.docx'):
    with zipfile.ZipFile(p) as z:
        root = ET.fromstring(z.read('word/document.xml'))
        ns = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        text = '\n'.join(''.join(e.itertext()) for e in root.findall('.//w:p',ns))
        p.with_suffix('.txt').write_text(text,encoding='utf-8')
if (OUT/'article.xml').exists():
    root = ET.fromstring((OUT/'article.xml').read_bytes())
    (OUT/'article.txt').write_text('\n'.join(''.join(p.itertext()) for p in root.iter('p')),encoding='utf-8')
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(manifest,indent=2))
