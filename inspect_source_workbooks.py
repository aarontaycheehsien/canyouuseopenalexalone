import json
from pathlib import Path
import xml.etree.ElementTree as E
import zipfile
ROOT=Path(__file__).resolve().parent/'stansfield_pilot'/'sources'
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def read_xlsx(path):
    with zipfile.ZipFile(path) as z:
        ss=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            ss=[''.join(e.itertext()) for e in E.fromstring(z.read('xl/sharedStrings.xml'))]
        wb=E.fromstring(z.read('xl/workbook.xml'))
        rels={e.attrib['Id']:e.attrib['Target'] for e in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        out={}
        for sheet in wb.find('s:sheets',NS):
            rid=sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
            target=rels[rid].lstrip('/')
            if not target.startswith('xl/'): target='xl/'+target
            rows=[]
            for row in E.fromstring(z.read(target)).findall('.//s:sheetData/s:row',NS):
                values={}
                for c in row:
                    v=c.find('s:v',NS)
                    val=v.text if v is not None else ''
                    if c.attrib.get('t')=='s':val=ss[int(val)]
                    elif c.attrib.get('t')=='inlineStr':val=''.join(c.find('s:is',NS).itertext())
                    values[c.attrib['r']]=val
                rows.append(values)
            out[sheet.attrib['name']]=rows
        return out
if __name__=='__main__':
    for name in ['CESM-3-e70038-s003.xlsx','reference.xlsx']:
        d=read_xlsx(ROOT/name)
        (ROOT/Path(name).with_suffix('.json')).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
        print(name)
        if name=='reference.xlsx':
            for sheet,rows in d.items():print(sheet,len(rows),rows[:4])
        else: print(json.dumps(d,indent=2,ensure_ascii=False))
