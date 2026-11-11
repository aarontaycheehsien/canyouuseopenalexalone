import json, itertools, pathlib
out = pathlib.Path(__file__).parent
# Embase #7 eye terms adj6 screening terms -> within 5 (Ovid ADJn allows n-1 intervening words; OQL within N allows N)
eye = ["eye","retina","retinal","retinopathy","macula","macular","maculopathy","vision"]          # bare = stemmed (eye covers eyes)
scr = ["screen","diagnosis","diagnoses","detection","test","program","programme","care","exam",
       "examination","check","checkup","surveillance","monitor"]                                  # stemmed forms
l7 = " OR ".join(f"({a} and {b} within 5 words of each other)" for a, b in itertools.product(eye, scr))
l7b = ('"teleophthalmology program*" OR "tele-ophthalmology program*" OR "tele-retinal retinopathy" OR '
       '"teleretinal retinopathy" OR "tele retinal retinopathy" OR slick OR "keep sight"')
# #14 diabet* adj4 (retina... eyes) -> within 3, wildcard terms quoted
l14 = " OR ".join(f'("diabet*" and "{t}" within 3 words of each other)' for t in ["retin*","macul*","eye","eyes"])
# #17 broad screening terms
l17 = ('"screen*" OR "program*" OR "surveillance*" OR "monitor*" OR examination OR checks OR "check-up" OR "check-ups" OR checkup OR '
       'teleophthalmology OR "tele ophthalmology" OR "teleretin*" OR "tele-retin*" OR "retina-screen*" OR "keep sight" OR slick OR '
       '((testing OR detection OR diagnosis) AND ("pathway*" OR "health system*" OR "care model*" OR "service*" OR "referral*" OR uptake))')
# #21 programme names
l21 = ('"retinascreen*" OR ("DES program*" AND "diabet*") OR keepsight OR "diabetic eye screening program*" OR "Irish national diabetic retinascreen" OR '
       '"teleophthalmology screening program*" OR "national diabetes eye screening program*" OR "diabetic retinal screening" OR '
       '"Diabetes Eye Care Pathway Toolkit" OR "Manitoba Retinal Screening Vision" OR "Pan-Ontario diabetic retinopathy screening" OR '
       '"Ontario Health Teleophthalmology Screening" OR "Ontario Health\'s Teleophthalmology Screening" OR "Toronto Teleophthalmology" OR '
       '"Toronto tele-retina" OR "Toronto teleretina" OR "Toronto tele retina" OR "Screening for Limb"')
# #23 place / people terms (text) ; Embase NOT qualifiers kept as AND NOT
places = ['"United Kingdom"','UK','Britain','British','(england AND NOT "new england")','"Isle of Man"','"Channel Islands"','Guernsey','London',
 'Ireland','"irish*"','Scotland','"scottish*"','Hebrides','Wales','Welsh','bath','("birmingham*" AND NOT "alabama*")','"bradford*"','"brighton*"',
 '"bristol*"','"carlisle*"','("cambridge*" AND NOT ("massachusetts*" OR "boston*" OR "harvard*"))','"canterbury*"','"chelmsford*"','"chester*"',
 '"chichester*"','"coventry*"','"derby*"','("durham*" AND NOT ("carolina*" OR nc))','ely','"exeter*"','"gloucester*"','"hereford*"','hull',
 '"lancaster*"','"leeds*"','"leicester*"','("lincoln*" AND NOT "nebraska*")','"liverpool*"','"manchester*"','"newcastle*"','"norwich*"',
 '"nottingham*"','"oxford*"','"peterborough*"','"plymouth*"','"portsmouth*"','"preston*"','"ripon*"','"salford*"','"salisbury*"','"sheffield*"',
 '"southampton*"','"st albans"','"stoke*"','"sunderland*"','"truro*"','"wakefield*"','wells','"westminster*"','"winchester*"','"wolverhampton*"',
 '("worcester*" AND NOT ("massachusetts*" OR "boston*" OR "harvard*"))','("york*" AND NOT ("new york*" OR ny))','"bangor*"','"cardiff*"','newport',
 '"st asaph*"','"st davids"','"swansea*"','"aberdeen*"','"dundee*"','"edinburgh*"','"glasgow*"','"inverness*"','"stirling*"','"armagh*"','"belfast*"',
 '"lisburn*"','"londonderry*"','"derry*"','"newry*"','"ulster*"','Canada','"canadian*"','"canadien*"','alberta','Manitoba','"New Brunswick"',
 '"Newfoundland and Labrador"','"Northwest Territories"','"Nova Scotia"','Nunavut','Ontario','"Prince Edward Island"','Quebec','Saskatchewan',
 '"Yukon Territory"','Vancouver','Victoria','Calgary','Edmonton','Regina','Saskatoon','Winnipeg','Ottawa','McMaster','"thunder bay"','Montreal',
 'McGill','Moncton','Fredericton','"charlottetown*"','"halifax*"','Dalhousie','"labrador*"','"newfoundland*"','"iqaluit*"','"northwest territor*"',
 '"yellowknife*"','"whitehorse*"','"first nation*"','metis','inuk','innu','innuit','autochtone','Hamilton','Kingston','Sudbury','Laval','Sherbrooke',
 'Nunavik','Kuujjuaq','Inukjuak','Puvirnituq','"australia*"','"Australian Capital Territory"','"New South Wales"','"Northern Territory"',
 'Queensland','"South Australia"','Tasmania','"Western Australia"','"New Zealand"','NZ','Otago','Canterbury','Nelson','Wellington','Taranaki',
 'Auckland','"Hawke\'s bay"','"Hawkes bay"','Aotearoa','Eire','"New Zealander*"','"maori*"','"polynesian*"','northland','waitemata','Manukau',
 'waikato','"lakes district"','tairawhiti','"aborigin*"','"torres strait islander*"','Sydney','melbourne','Cork','Dublin','Galway','Waterford',
 'Maynooth','Limerick','Cashel','Kilkenny','Drogheda','Aston','Sussex','Kent','Keele','"East Anglia"','Warwick','"St Andrews"','Strathclyde',
 'Cranfield','Essex','"Anglia Ruskin"','Waterloo','"Western University"','Guelph','"Simon Fraser"']
geo_text = " OR ".join(places)
codes = "([United Kingdom](GB) or [Canada](CA) or [Australia](AU) or [New Zealand](NZ) or [Ireland](IE))"
# Concept block (#20 OR #21): A1 = diabet* AND (#7); A2 = #14 AND #17; CV stand-in = DR topic (T10170) AND diabet* AND #17
concept = (f'(title-abstract-keywords has (("diabet*" AND ({l7} OR {l7b})) OR (({l14}) AND ({l17})))'
           f' or (topic is [Retinal Diseases and Treatments](T10170) and title-abstract-keywords has ("diabet*" AND ({l17}))))')
names = f'title-abstract-keywords has ({l21})'
geo = f'(country is {codes} or title-abstract-keywords has ({geo_text}) or raw affiliation has ({geo_text}))'
# country-unknown route: no resolved country, but the core concept (#14 within 3 + screening word) is in the TITLE
unk = f'(country is unknown and title has (({l14}) AND ("screen*" OR "program*" OR "examination*" OR teleophthalmology OR "tele-ophthalmology")))'
yr = "year >= (2003) and year <= (2023)"
fb = ('(it doesn\'t have an abstract and title-abstract-keywords has ("diabet*" AND ("diabetes screening" OR "vision screening" OR '
      '"retinal screening" OR "eye care" OR "diabetic eye disease" OR "eye examination")))')
concept3 = concept[:-1] + f" or {fb})"
S3 = f"get works where {yr} and ({names} or ({concept3} and ({geo} or {unk})))"
S1 = f"get works where {yr} and ({names} or ({concept} and {geo}))"
S2 = f"get works where {yr} and ({names} or ({concept} and ({geo} or {unk})))"
import csv
refs = out.parents[1] / 'reference_retrieval.csv'
ids = ' or '.join(sorted({r['current_openalex_id'] for r in csv.DictReader(open(refs, encoding='utf-8-sig')) if r['current_openalex_id']}))
for k, q in {"S1": S1, "S2": S2, "S3": S3}.items():
    (out/f"{k}.oql").write_text(q)
    (out/f"{k}_ids.oql").write_text(q.replace(f"where {yr} and", f"where {yr} and openalex is ({ids}) and", 1))
    print(k, len(q), len((out/f'{k}_ids.oql').read_text()))
