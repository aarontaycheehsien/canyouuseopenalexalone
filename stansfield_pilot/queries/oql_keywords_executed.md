# 2. OQL plus keywords


```text
works where ( ( title/abstract/keywords has ( ( "retinascreen*" or "DES program*" or "Keepsight" or
        "Diabetic eye screening program*" or "Irish national diabetic retinascreen" or
        "teleophthalmology screening program*" or "National diabetes eye screening program" or
        "National diabetes eye screening programs" or "National diabetes eye screening programme" or
        "National diabetes eye screening programmes" or "Diabetic Retinal Screening" or
        "Diabetes Eye Care Pathway Toolkit" or "Manitoba Retinal Screening Vision" or
        "Pan-Ontario diabetic retinopathy screening" or "Ontario Health Teleophthalmology Screening"
        or "Ontario Health's Teleophthalmology Screening" or "Toronto Teleophthalmology" or
        "Toronto tele-retina" or "Toronto teleretina" or "Toronto tele retina" or
        "Screening for Limb" ) )
    or ( title/abstract/keywords has ( ( ( "diabet*" and ( ( within 5 ( "eye" , "screen" ) or within
        5 ( "eye" , "screening" ) or within 5 ( "eye" , "diagnosis" ) or within 5 ( "eye" ,
        "diagnoses" ) or within 5 ( "eye" , "detection" ) or within 5 ( "eye" , "test" ) or within 5
        ( "eye" , "tests" ) or within 5 ( "eye" , "testing" ) or within 5 ( "eye" , "program" ) or
        within 5 ( "eye" , "programs" ) or within 5 ( "eye" , "programme" ) or within 5 ( "eye" ,
        "programmes" ) or within 5 ( "eye" , "care" ) or within 5 ( "eye" , "exam" ) or within 5 (
        "eye" , "exams" ) or within 5 ( "eye" , "examination" ) or within 5 ( "eye" , "examinations"
        ) or within 5 ( "eye" , "checks" ) or within 5 ( "eye" , "check-up" ) or within 5 ( "eye" ,
        "check-ups" ) or within 5 ( "eye" , "checkup" ) or within 5 ( "eye" , "checkups" ) or within
        5 ( "eye" , "surveillance" ) or within 5 ( "eye" , "monitor" ) or within 5 ( "eye" ,
        "monitoring" ) or within 5 ( "eyes" , "screen" ) or within 5 ( "eyes" , "screening" ) or
        within 5 ( "eyes" , "diagnosis" ) or within 5 ( "eyes" , "diagnoses" ) or within 5 ( "eyes"
        , "detection" ) or within 5 ( "eyes" , "test" ) or within 5 ( "eyes" , "tests" ) or within 5
        ( "eyes" , "testing" ) or within 5 ( "eyes" , "program" ) or within 5 ( "eyes" , "programs"
        ) or within 5 ( "eyes" , "programme" ) or within 5 ( "eyes" , "programmes" ) or within 5 (
        "eyes" , "care" ) or within 5 ( "eyes" , "exam" ) or within 5 ( "eyes" , "exams" ) or within
        5 ( "eyes" , "examination" ) or within 5 ( "eyes" , "examinations" ) or within 5 ( "eyes" ,
        "checks" ) or within 5 ( "eyes" , "check-up" ) or within 5 ( "eyes" , "check-ups" ) or
        within 5 ( "eyes" , "checkup" ) or within 5 ( "eyes" , "checkups" ) or within 5 ( "eyes" ,
        "surveillance" ) or within 5 ( "eyes" , "monitor" ) or within 5 ( "eyes" , "monitoring" ) or
        within 5 ( "retina" , "screen" ) or within 5 ( "retina" , "screening" ) or within 5 (
        "retina" , "diagnosis" ) or within 5 ( "retina" , "diagnoses" ) or within 5 ( "retina" ,
        "detection" ) or within 5 ( "retina" , "test" ) or within 5 ( "retina" , "tests" ) or within
        5 ( "retina" , "testing" ) or within 5 ( "retina" , "program" ) or within 5 ( "retina" ,
        "programs" ) or within 5 ( "retina" , "programme" ) or within 5 ( "retina" , "programmes" )
        or within 5 ( "retina" , "care" ) or within 5 ( "retina" , "exam" ) or within 5 ( "retina" ,
        "exams" ) or within 5 ( "retina" , "examination" ) or within 5 ( "retina" , "examinations" )
        or within 5 ( "retina" , "checks" ) or within 5 ( "retina" , "check-up" ) or within 5 (
        "retina" , "check-ups" ) or within 5 ( "retina" , "checkup" ) or within 5 ( "retina" ,
        "checkups" ) or within 5 ( "retina" , "surveillance" ) or within 5 ( "retina" , "monitor" )
        or within 5 ( "retina" , "monitoring" ) or within 5 ( "retinal" , "screen" ) or within 5 (
        "retinal" , "screening" ) or within 5 ( "retinal" , "diagnosis" ) or within 5 ( "retinal" ,
        "diagnoses" ) or within 5 ( "retinal" , "detection" ) or within 5 ( "retinal" , "test" ) or
        within 5 ( "retinal" , "tests" ) or within 5 ( "retinal" , "testing" ) or within 5 (
        "retinal" , "program" ) or within 5 ( "retinal" , "programs" ) or within 5 ( "retinal" ,
        "programme" ) or within 5 ( "retinal" , "programmes" ) or within 5 ( "retinal" , "care" ) or
        within 5 ( "retinal" , "exam" ) or within 5 ( "retinal" , "exams" ) or within 5 ( "retinal"
        , "examination" ) or within 5 ( "retinal" , "examinations" ) or within 5 ( "retinal" ,
        "checks" ) or within 5 ( "retinal" , "check-up" ) or within 5 ( "retinal" , "check-ups" ) or
        within 5 ( "retinal" , "checkup" ) or within 5 ( "retinal" , "checkups" ) or within 5 (
        "retinal" , "surveillance" ) or within 5 ( "retinal" , "monitor" ) or within 5 ( "retinal" ,
        "monitoring" ) or within 5 ( "retinopathy" , "screen" ) or within 5 ( "retinopathy" ,
        "screening" ) or within 5 ( "retinopathy" , "diagnosis" ) or within 5 ( "retinopathy" ,
        "diagnoses" ) or within 5 ( "retinopathy" , "detection" ) or within 5 ( "retinopathy" ,
        "test" ) or within 5 ( "retinopathy" , "tests" ) or within 5 ( "retinopathy" , "testing" )
        or within 5 ( "retinopathy" , "program" ) or within 5 ( "retinopathy" , "programs" ) or
        within 5 ( "retinopathy" , "programme" ) or within 5 ( "retinopathy" , "programmes" ) or
        within 5 ( "retinopathy" , "care" ) or within 5 ( "retinopathy" , "exam" ) or within 5 (
        "retinopathy" , "exams" ) or within 5 ( "retinopathy" , "examination" ) or within 5 (
        "retinopathy" , "examinations" ) or within 5 ( "retinopathy" , "checks" ) or within 5 (
        "retinopathy" , "check-up" ) or within 5 ( "retinopathy" , "check-ups" ) or within 5 (
        "retinopathy" , "checkup" ) or within 5 ( "retinopathy" , "checkups" ) or within 5 (
        "retinopathy" , "surveillance" ) or within 5 ( "retinopathy" , "monitor" ) or within 5 (
        "retinopathy" , "monitoring" ) or within 5 ( "macula" , "screen" ) or within 5 ( "macula" ,
        "screening" ) or within 5 ( "macula" , "diagnosis" ) or within 5 ( "macula" , "diagnoses" )
        or within 5 ( "macula" , "detection" ) or within 5 ( "macula" , "test" ) or within 5 (
        "macula" , "tests" ) or within 5 ( "macula" , "testing" ) or within 5 ( "macula" , "program"
        ) or within 5 ( "macula" , "programs" ) or within 5 ( "macula" , "programme" ) or within 5 (
        "macula" , "programmes" ) or within 5 ( "macula" , "care" ) or within 5 ( "macula" , "exam"
        ) or within 5 ( "macula" , "exams" ) or within 5 ( "macula" , "examination" ) or within 5 (
        "macula" , "examinations" ) or within 5 ( "macula" , "checks" ) or within 5 ( "macula" ,
        "check-up" ) or within 5 ( "macula" , "check-ups" ) or within 5 ( "macula" , "checkup" ) or
        within 5 ( "macula" , "checkups" ) or within 5 ( "macula" , "surveillance" ) or within 5 (
        "macula" , "monitor" ) or within 5 ( "macula" , "monitoring" ) or within 5 ( "macular" ,
        "screen" ) or within 5 ( "macular" , "screening" ) or within 5 ( "macular" , "diagnosis" )
        or within 5 ( "macular" , "diagnoses" ) or within 5 ( "macular" , "detection" ) or within 5
        ( "macular" , "test" ) or within 5 ( "macular" , "tests" ) or within 5 ( "macular" ,
        "testing" ) or within 5 ( "macular" , "program" ) or within 5 ( "macular" , "programs" ) or
        within 5 ( "macular" , "programme" ) or within 5 ( "macular" , "programmes" ) or within 5 (
        "macular" , "care" ) or within 5 ( "macular" , "exam" ) or within 5 ( "macular" , "exams" )
        or within 5 ( "macular" , "examination" ) or within 5 ( "macular" , "examinations" ) or
        within 5 ( "macular" , "checks" ) or within 5 ( "macular" , "check-up" ) or within 5 (
        "macular" , "check-ups" ) or within 5 ( "macular" , "checkup" ) or within 5 ( "macular" ,
        "checkups" ) or within 5 ( "macular" , "surveillance" ) or within 5 ( "macular" , "monitor"
        ) or within 5 ( "macular" , "monitoring" ) or within 5 ( "maculopathy" , "screen" ) or
        within 5 ( "maculopathy" , "screening" ) or within 5 ( "maculopathy" , "diagnosis" ) or
        within 5 ( "maculopathy" , "diagnoses" ) or within 5 ( "maculopathy" , "detection" ) or
        within 5 ( "maculopathy" , "test" ) or within 5 ( "maculopathy" , "tests" ) or within 5 (
        "maculopathy" , "testing" ) or within 5 ( "maculopathy" , "program" ) or within 5 (
        "maculopathy" , "programs" ) or within 5 ( "maculopathy" , "programme" ) or within 5 (
        "maculopathy" , "programmes" ) or within 5 ( "maculopathy" , "care" ) or within 5 (
        "maculopathy" , "exam" ) or within 5 ( "maculopathy" , "exams" ) or within 5 ( "maculopathy"
        , "examination" ) or within 5 ( "maculopathy" , "examinations" ) or within 5 ( "maculopathy"
        , "checks" ) or within 5 ( "maculopathy" , "check-up" ) or within 5 ( "maculopathy" ,
        "check-ups" ) or within 5 ( "maculopathy" , "checkup" ) or within 5 ( "maculopathy" ,
        "checkups" ) or within 5 ( "maculopathy" , "surveillance" ) or within 5 ( "maculopathy" ,
        "monitor" ) or within 5 ( "maculopathy" , "monitoring" ) or within 5 ( "vision" , "screen" )
        or within 5 ( "vision" , "screening" ) or within 5 ( "vision" , "diagnosis" ) or within 5 (
        "vision" , "diagnoses" ) or within 5 ( "vision" , "detection" ) or within 5 ( "vision" ,
        "test" ) or within 5 ( "vision" , "tests" ) or within 5 ( "vision" , "testing" ) or within 5
        ( "vision" , "program" ) or within 5 ( "vision" , "programs" ) or within 5 ( "vision" ,
        "programme" ) or within 5 ( "vision" , "programmes" ) or within 5 ( "vision" , "care" ) or
        within 5 ( "vision" , "exam" ) or within 5 ( "vision" , "exams" ) or within 5 ( "vision" ,
        "examination" ) or within 5 ( "vision" , "examinations" ) or within 5 ( "vision" , "checks"
        ) or within 5 ( "vision" , "check-up" ) or within 5 ( "vision" , "check-ups" ) or within 5 (
        "vision" , "checkup" ) or within 5 ( "vision" , "checkups" ) or within 5 ( "vision" ,
        "surveillance" ) or within 5 ( "vision" , "monitor" ) or within 5 ( "vision" , "monitoring"
        ) ) or "teleophthalmology program*" or "tele-ophthalmology program*" or
        "Tele-retinal retinopathy" or "teleretinal retinopathy" or "tele retinal retinopathy" or
        "SLICK" or "keep sight" ) ) or ( ( within 3 ( "diabet*" , "eye" ) or within 3 ( "diabet*" ,
        "eyes" ) or within 3 ( "diabet*" , "retina" ) or within 3 ( "diabet*" , "retinal" ) or
        within 3 ( "diabet*" , "retinopathy" ) or within 3 ( "diabet*" , "macula" ) or within 3 (
        "diabet*" , "macular" ) or within 3 ( "diabet*" , "maculopathy" ) ) and ( "Screen*" or
        "program*" or "surveillance*" or "monitor*" or "examination" or "examinations" or "checks"
        or "check-up" or "Check-ups" or "Teleophthalmology" or "tele-ophthalmology" or "teleretin*"
        or "tele-retin*" or "Retina-Screen*" or "Keep sight" or "SLICK" or ( ( "testing" or
        "detection" or "diagnosis" ) and ( "pathway*" or "health system*" or "care model*" or
        "service*" or "referral*" or "uptake" ) ) ) ) ) )
      and ( title/abstract/keywords has ( ( "United Kingdom" or "UK" or "u. k." or "Britain" or
        "British" or ( "england" and not "new england" ) or "Isle of Man" or "Channel Islands" or
        "Guernsey" or "London" or "Ireland" or "irish*" or "Scotland" or "scottish*" or "Hebrides"
        or "Wales" or "Welsh" or "bath" or ( "birmingham*" and not "alabama*" ) or "bradford*" or
        "brighton*" or "bristol*" or "carlisle*" or ( "cambridge*" and not ( "massachusetts*" or
        "boston*" or "harvard*" ) ) or "canterbury*" or "chelmsford*" or "chester*" or "chichester*"
        or "coventry*" or "derby*" or ( "durham*" and not ( "carolina*" or "nc" ) ) or "ely" or
        "exeter*" or "gloucester*" or "hereford*" or "hull" or "lancaster*" or "leeds*" or
        "leicester*" or ( "lincoln*" and not "nebraska*" ) or "liverpool*" or "manchester*" or
        "newcastle*" or "norwich*" or "nottingham*" or "oxford*" or "peterborough*" or "plymouth*"
        or "portsmouth*" or "preston*" or "ripon*" or "salford*" or "salisbury*" or "sheffield*" or
        "southampton*" or "st albans" or "stoke*" or "sunderland*" or "truro*" or "wakefield*" or
        "wells" or "westminster*" or "winchester*" or "wolverhampton*" or ( "worcester*" and not (
        "massachusetts*" or "boston*" or "harvard*" ) ) or ( "york*" and not ( "new york*" or "ny" )
        ) or "bangor*" or "cardiff*" or "newport" or "st asaph*" or "st davids" or "swansea*" or
        "aberdeen*" or "dundee*" or "edinburgh*" or "glasgow*" or "inverness*" or "stirling*" or
        "armagh*" or "belfast*" or "lisburn*" or "londonderry*" or "derry*" or "newry*" or "ulster*"
        or "Canada" or "canadian*" or "canadien*" or "alberta" or "Manitoba" or "New Brunswick" or
        "Newfoundland and Labrador" or "Northwest Territories" or "Nova Scotia" or "Nunavut" or
        "Ontario" or "Prince Edward Island" or "Quebec" or "Saskatchewan" or "Yukon Territory" or
        "Vancouver" or "Victoria" or "Calgary" or "Edmonton" or "Regina" or "Saskatoon" or
        "Winnipeg" or "Ottawa" or "McMaster" or "thunder bay" or "Montreal" or "McGill" or "Moncton"
        or "Fredericton" or "prince edward island*" or "charlottetown*" or "nova scotia*" or
        "halifax*" or "Dalhousie" or "labrador*" or "newfoundland*" or "nunavut*" or "iqaluit*" or
        "northwest territor*" or "yellowknife*" or "whitehorse*" or "first nation*" or "metis" or
        "inuk" or "innu" or "innuit" or "autochtone" or "Hamilton" or "Kingston" or "Sudbury" or
        "Laval" or "Sherbrooke" or "Nunavik" or "Kuujjuaq" or "Inukjuak" or "Puvirnituq" or
        "australia*" or "Australian Capital Territory" or "New South Wales" or "Northern Territory"
        or "Queensland" or "South Australia" or "Tasmania" or "Victoria" or "Western Australia" or
        "New Zealand" or "NZ" or "Otago" or "Canterbury" or "Nelson" or "Wellington" or "Taranaki"
        or "Auckland" or "Hawke's bay" or "Hawkes bay" or "Aotearoa" or "Eire" or "New Zealander" or
        "New Zealanders" or "maori*" or "polynesian*" or "northland" or "waitemata" or "Manukau" or
        "waikato" or "lakes district" or "tairawhiti" or "aborigin*" or "torres strait islander*" or
        "Sydney" or "melbourne" or "Cork" or "Dublin" or "Galway" or "Waterford" or "Maynooth" or
        "Limerick" or "Cashel" or "Kilkenny" or "Drogheda" or "Aston" or "Sussex" or "Kent" or
        "Ulster" or "Keele" or "East Anglia" or "Warwick" or "St Andrews" or "Strathclyde" or
        "Cranfield" or "Essex" or "Anglia Ruskin" or "Waterloo" or "Western University" or "Guelph"
        or "Simon Fraser" ) ) or country is ( AU or CA or IE or NZ or GB ) ) ) )
  or ( ( keyword is ( diabetic-retinopathy )
      and keyword is ( screening or screening-uptake ) )
    or ( keyword is ( diabetes or diabetes-mellitus or type-1-diabetes or type-2-diabetes or
        diabetic-complications or diabetes-complications )
      and keyword is ( retinopathy or maculopathy ) ) ) )
and year >= ( 2003 )
and year <= ( 2023 )
```

### Known-record membership variant

The following restricted version was submitted to check membership of the matched reference IDs. Its returned order was not used as the global search ranking.

```text
works where ( ( ( title/abstract/keywords has ( ( "retinascreen*" or "DES program*" or "Keepsight"
        or "Diabetic eye screening program*" or "Irish national diabetic retinascreen" or
        "teleophthalmology screening program*" or "National diabetes eye screening program" or
        "National diabetes eye screening programs" or "National diabetes eye screening programme" or
        "National diabetes eye screening programmes" or "Diabetic Retinal Screening" or
        "Diabetes Eye Care Pathway Toolkit" or "Manitoba Retinal Screening Vision" or
        "Pan-Ontario diabetic retinopathy screening" or "Ontario Health Teleophthalmology Screening"
        or "Ontario Health's Teleophthalmology Screening" or "Toronto Teleophthalmology" or
        "Toronto tele-retina" or "Toronto teleretina" or "Toronto tele retina" or
        "Screening for Limb" ) )
      or ( title/abstract/keywords has ( ( ( "diabet*" and ( ( within 5 ( "eye" , "screen" ) or
        within 5 ( "eye" , "screening" ) or within 5 ( "eye" , "diagnosis" ) or within 5 ( "eye" ,
        "diagnoses" ) or within 5 ( "eye" , "detection" ) or within 5 ( "eye" , "test" ) or within 5
        ( "eye" , "tests" ) or within 5 ( "eye" , "testing" ) or within 5 ( "eye" , "program" ) or
        within 5 ( "eye" , "programs" ) or within 5 ( "eye" , "programme" ) or within 5 ( "eye" ,
        "programmes" ) or within 5 ( "eye" , "care" ) or within 5 ( "eye" , "exam" ) or within 5 (
        "eye" , "exams" ) or within 5 ( "eye" , "examination" ) or within 5 ( "eye" , "examinations"
        ) or within 5 ( "eye" , "checks" ) or within 5 ( "eye" , "check-up" ) or within 5 ( "eye" ,
        "check-ups" ) or within 5 ( "eye" , "checkup" ) or within 5 ( "eye" , "checkups" ) or within
        5 ( "eye" , "surveillance" ) or within 5 ( "eye" , "monitor" ) or within 5 ( "eye" ,
        "monitoring" ) or within 5 ( "eyes" , "screen" ) or within 5 ( "eyes" , "screening" ) or
        within 5 ( "eyes" , "diagnosis" ) or within 5 ( "eyes" , "diagnoses" ) or within 5 ( "eyes"
        , "detection" ) or within 5 ( "eyes" , "test" ) or within 5 ( "eyes" , "tests" ) or within 5
        ( "eyes" , "testing" ) or within 5 ( "eyes" , "program" ) or within 5 ( "eyes" , "programs"
        ) or within 5 ( "eyes" , "programme" ) or within 5 ( "eyes" , "programmes" ) or within 5 (
        "eyes" , "care" ) or within 5 ( "eyes" , "exam" ) or within 5 ( "eyes" , "exams" ) or within
        5 ( "eyes" , "examination" ) or within 5 ( "eyes" , "examinations" ) or within 5 ( "eyes" ,
        "checks" ) or within 5 ( "eyes" , "check-up" ) or within 5 ( "eyes" , "check-ups" ) or
        within 5 ( "eyes" , "checkup" ) or within 5 ( "eyes" , "checkups" ) or within 5 ( "eyes" ,
        "surveillance" ) or within 5 ( "eyes" , "monitor" ) or within 5 ( "eyes" , "monitoring" ) or
        within 5 ( "retina" , "screen" ) or within 5 ( "retina" , "screening" ) or within 5 (
        "retina" , "diagnosis" ) or within 5 ( "retina" , "diagnoses" ) or within 5 ( "retina" ,
        "detection" ) or within 5 ( "retina" , "test" ) or within 5 ( "retina" , "tests" ) or within
        5 ( "retina" , "testing" ) or within 5 ( "retina" , "program" ) or within 5 ( "retina" ,
        "programs" ) or within 5 ( "retina" , "programme" ) or within 5 ( "retina" , "programmes" )
        or within 5 ( "retina" , "care" ) or within 5 ( "retina" , "exam" ) or within 5 ( "retina" ,
        "exams" ) or within 5 ( "retina" , "examination" ) or within 5 ( "retina" , "examinations" )
        or within 5 ( "retina" , "checks" ) or within 5 ( "retina" , "check-up" ) or within 5 (
        "retina" , "check-ups" ) or within 5 ( "retina" , "checkup" ) or within 5 ( "retina" ,
        "checkups" ) or within 5 ( "retina" , "surveillance" ) or within 5 ( "retina" , "monitor" )
        or within 5 ( "retina" , "monitoring" ) or within 5 ( "retinal" , "screen" ) or within 5 (
        "retinal" , "screening" ) or within 5 ( "retinal" , "diagnosis" ) or within 5 ( "retinal" ,
        "diagnoses" ) or within 5 ( "retinal" , "detection" ) or within 5 ( "retinal" , "test" ) or
        within 5 ( "retinal" , "tests" ) or within 5 ( "retinal" , "testing" ) or within 5 (
        "retinal" , "program" ) or within 5 ( "retinal" , "programs" ) or within 5 ( "retinal" ,
        "programme" ) or within 5 ( "retinal" , "programmes" ) or within 5 ( "retinal" , "care" ) or
        within 5 ( "retinal" , "exam" ) or within 5 ( "retinal" , "exams" ) or within 5 ( "retinal"
        , "examination" ) or within 5 ( "retinal" , "examinations" ) or within 5 ( "retinal" ,
        "checks" ) or within 5 ( "retinal" , "check-up" ) or within 5 ( "retinal" , "check-ups" ) or
        within 5 ( "retinal" , "checkup" ) or within 5 ( "retinal" , "checkups" ) or within 5 (
        "retinal" , "surveillance" ) or within 5 ( "retinal" , "monitor" ) or within 5 ( "retinal" ,
        "monitoring" ) or within 5 ( "retinopathy" , "screen" ) or within 5 ( "retinopathy" ,
        "screening" ) or within 5 ( "retinopathy" , "diagnosis" ) or within 5 ( "retinopathy" ,
        "diagnoses" ) or within 5 ( "retinopathy" , "detection" ) or within 5 ( "retinopathy" ,
        "test" ) or within 5 ( "retinopathy" , "tests" ) or within 5 ( "retinopathy" , "testing" )
        or within 5 ( "retinopathy" , "program" ) or within 5 ( "retinopathy" , "programs" ) or
        within 5 ( "retinopathy" , "programme" ) or within 5 ( "retinopathy" , "programmes" ) or
        within 5 ( "retinopathy" , "care" ) or within 5 ( "retinopathy" , "exam" ) or within 5 (
        "retinopathy" , "exams" ) or within 5 ( "retinopathy" , "examination" ) or within 5 (
        "retinopathy" , "examinations" ) or within 5 ( "retinopathy" , "checks" ) or within 5 (
        "retinopathy" , "check-up" ) or within 5 ( "retinopathy" , "check-ups" ) or within 5 (
        "retinopathy" , "checkup" ) or within 5 ( "retinopathy" , "checkups" ) or within 5 (
        "retinopathy" , "surveillance" ) or within 5 ( "retinopathy" , "monitor" ) or within 5 (
        "retinopathy" , "monitoring" ) or within 5 ( "macula" , "screen" ) or within 5 ( "macula" ,
        "screening" ) or within 5 ( "macula" , "diagnosis" ) or within 5 ( "macula" , "diagnoses" )
        or within 5 ( "macula" , "detection" ) or within 5 ( "macula" , "test" ) or within 5 (
        "macula" , "tests" ) or within 5 ( "macula" , "testing" ) or within 5 ( "macula" , "program"
        ) or within 5 ( "macula" , "programs" ) or within 5 ( "macula" , "programme" ) or within 5 (
        "macula" , "programmes" ) or within 5 ( "macula" , "care" ) or within 5 ( "macula" , "exam"
        ) or within 5 ( "macula" , "exams" ) or within 5 ( "macula" , "examination" ) or within 5 (
        "macula" , "examinations" ) or within 5 ( "macula" , "checks" ) or within 5 ( "macula" ,
        "check-up" ) or within 5 ( "macula" , "check-ups" ) or within 5 ( "macula" , "checkup" ) or
        within 5 ( "macula" , "checkups" ) or within 5 ( "macula" , "surveillance" ) or within 5 (
        "macula" , "monitor" ) or within 5 ( "macula" , "monitoring" ) or within 5 ( "macular" ,
        "screen" ) or within 5 ( "macular" , "screening" ) or within 5 ( "macular" , "diagnosis" )
        or within 5 ( "macular" , "diagnoses" ) or within 5 ( "macular" , "detection" ) or within 5
        ( "macular" , "test" ) or within 5 ( "macular" , "tests" ) or within 5 ( "macular" ,
        "testing" ) or within 5 ( "macular" , "program" ) or within 5 ( "macular" , "programs" ) or
        within 5 ( "macular" , "programme" ) or within 5 ( "macular" , "programmes" ) or within 5 (
        "macular" , "care" ) or within 5 ( "macular" , "exam" ) or within 5 ( "macular" , "exams" )
        or within 5 ( "macular" , "examination" ) or within 5 ( "macular" , "examinations" ) or
        within 5 ( "macular" , "checks" ) or within 5 ( "macular" , "check-up" ) or within 5 (
        "macular" , "check-ups" ) or within 5 ( "macular" , "checkup" ) or within 5 ( "macular" ,
        "checkups" ) or within 5 ( "macular" , "surveillance" ) or within 5 ( "macular" , "monitor"
        ) or within 5 ( "macular" , "monitoring" ) or within 5 ( "maculopathy" , "screen" ) or
        within 5 ( "maculopathy" , "screening" ) or within 5 ( "maculopathy" , "diagnosis" ) or
        within 5 ( "maculopathy" , "diagnoses" ) or within 5 ( "maculopathy" , "detection" ) or
        within 5 ( "maculopathy" , "test" ) or within 5 ( "maculopathy" , "tests" ) or within 5 (
        "maculopathy" , "testing" ) or within 5 ( "maculopathy" , "program" ) or within 5 (
        "maculopathy" , "programs" ) or within 5 ( "maculopathy" , "programme" ) or within 5 (
        "maculopathy" , "programmes" ) or within 5 ( "maculopathy" , "care" ) or within 5 (
        "maculopathy" , "exam" ) or within 5 ( "maculopathy" , "exams" ) or within 5 ( "maculopathy"
        , "examination" ) or within 5 ( "maculopathy" , "examinations" ) or within 5 ( "maculopathy"
        , "checks" ) or within 5 ( "maculopathy" , "check-up" ) or within 5 ( "maculopathy" ,
        "check-ups" ) or within 5 ( "maculopathy" , "checkup" ) or within 5 ( "maculopathy" ,
        "checkups" ) or within 5 ( "maculopathy" , "surveillance" ) or within 5 ( "maculopathy" ,
        "monitor" ) or within 5 ( "maculopathy" , "monitoring" ) or within 5 ( "vision" , "screen" )
        or within 5 ( "vision" , "screening" ) or within 5 ( "vision" , "diagnosis" ) or within 5 (
        "vision" , "diagnoses" ) or within 5 ( "vision" , "detection" ) or within 5 ( "vision" ,
        "test" ) or within 5 ( "vision" , "tests" ) or within 5 ( "vision" , "testing" ) or within 5
        ( "vision" , "program" ) or within 5 ( "vision" , "programs" ) or within 5 ( "vision" ,
        "programme" ) or within 5 ( "vision" , "programmes" ) or within 5 ( "vision" , "care" ) or
        within 5 ( "vision" , "exam" ) or within 5 ( "vision" , "exams" ) or within 5 ( "vision" ,
        "examination" ) or within 5 ( "vision" , "examinations" ) or within 5 ( "vision" , "checks"
        ) or within 5 ( "vision" , "check-up" ) or within 5 ( "vision" , "check-ups" ) or within 5 (
        "vision" , "checkup" ) or within 5 ( "vision" , "checkups" ) or within 5 ( "vision" ,
        "surveillance" ) or within 5 ( "vision" , "monitor" ) or within 5 ( "vision" , "monitoring"
        ) ) or "teleophthalmology program*" or "tele-ophthalmology program*" or
        "Tele-retinal retinopathy" or "teleretinal retinopathy" or "tele retinal retinopathy" or
        "SLICK" or "keep sight" ) ) or ( ( within 3 ( "diabet*" , "eye" ) or within 3 ( "diabet*" ,
        "eyes" ) or within 3 ( "diabet*" , "retina" ) or within 3 ( "diabet*" , "retinal" ) or
        within 3 ( "diabet*" , "retinopathy" ) or within 3 ( "diabet*" , "macula" ) or within 3 (
        "diabet*" , "macular" ) or within 3 ( "diabet*" , "maculopathy" ) ) and ( "Screen*" or
        "program*" or "surveillance*" or "monitor*" or "examination" or "examinations" or "checks"
        or "check-up" or "Check-ups" or "Teleophthalmology" or "tele-ophthalmology" or "teleretin*"
        or "tele-retin*" or "Retina-Screen*" or "Keep sight" or "SLICK" or ( ( "testing" or
        "detection" or "diagnosis" ) and ( "pathway*" or "health system*" or "care model*" or
        "service*" or "referral*" or "uptake" ) ) ) ) ) ) and ( title/abstract/keywords has ( (
        "United Kingdom" or "UK" or "u. k." or "Britain" or "British" or ( "england" and not
        "new england" ) or "Isle of Man" or "Channel Islands" or "Guernsey" or "London" or "Ireland"
        or "irish*" or "Scotland" or "scottish*" or "Hebrides" or "Wales" or "Welsh" or "bath" or (
        "birmingham*" and not "alabama*" ) or "bradford*" or "brighton*" or "bristol*" or
        "carlisle*" or ( "cambridge*" and not ( "massachusetts*" or "boston*" or "harvard*" ) ) or
        "canterbury*" or "chelmsford*" or "chester*" or "chichester*" or "coventry*" or "derby*" or
        ( "durham*" and not ( "carolina*" or "nc" ) ) or "ely" or "exeter*" or "gloucester*" or
        "hereford*" or "hull" or "lancaster*" or "leeds*" or "leicester*" or ( "lincoln*" and not
        "nebraska*" ) or "liverpool*" or "manchester*" or "newcastle*" or "norwich*" or
        "nottingham*" or "oxford*" or "peterborough*" or "plymouth*" or "portsmouth*" or "preston*"
        or "ripon*" or "salford*" or "salisbury*" or "sheffield*" or "southampton*" or "st albans"
        or "stoke*" or "sunderland*" or "truro*" or "wakefield*" or "wells" or "westminster*" or
        "winchester*" or "wolverhampton*" or ( "worcester*" and not ( "massachusetts*" or "boston*"
        or "harvard*" ) ) or ( "york*" and not ( "new york*" or "ny" ) ) or "bangor*" or "cardiff*"
        or "newport" or "st asaph*" or "st davids" or "swansea*" or "aberdeen*" or "dundee*" or
        "edinburgh*" or "glasgow*" or "inverness*" or "stirling*" or "armagh*" or "belfast*" or
        "lisburn*" or "londonderry*" or "derry*" or "newry*" or "ulster*" or "Canada" or "canadian*"
        or "canadien*" or "alberta" or "Manitoba" or "New Brunswick" or "Newfoundland and Labrador"
        or "Northwest Territories" or "Nova Scotia" or "Nunavut" or "Ontario" or
        "Prince Edward Island" or "Quebec" or "Saskatchewan" or "Yukon Territory" or "Vancouver" or
        "Victoria" or "Calgary" or "Edmonton" or "Regina" or "Saskatoon" or "Winnipeg" or "Ottawa"
        or "McMaster" or "thunder bay" or "Montreal" or "McGill" or "Moncton" or "Fredericton" or
        "prince edward island*" or "charlottetown*" or "nova scotia*" or "halifax*" or "Dalhousie"
        or "labrador*" or "newfoundland*" or "nunavut*" or "iqaluit*" or "northwest territor*" or
        "yellowknife*" or "whitehorse*" or "first nation*" or "metis" or "inuk" or "innu" or
        "innuit" or "autochtone" or "Hamilton" or "Kingston" or "Sudbury" or "Laval" or "Sherbrooke"
        or "Nunavik" or "Kuujjuaq" or "Inukjuak" or "Puvirnituq" or "australia*" or
        "Australian Capital Territory" or "New South Wales" or "Northern Territory" or "Queensland"
        or "South Australia" or "Tasmania" or "Victoria" or "Western Australia" or "New Zealand" or
        "NZ" or "Otago" or "Canterbury" or "Nelson" or "Wellington" or "Taranaki" or "Auckland" or
        "Hawke's bay" or "Hawkes bay" or "Aotearoa" or "Eire" or "New Zealander" or "New Zealanders"
        or "maori*" or "polynesian*" or "northland" or "waitemata" or "Manukau" or "waikato" or
        "lakes district" or "tairawhiti" or "aborigin*" or "torres strait islander*" or "Sydney" or
        "melbourne" or "Cork" or "Dublin" or "Galway" or "Waterford" or "Maynooth" or "Limerick" or
        "Cashel" or "Kilkenny" or "Drogheda" or "Aston" or "Sussex" or "Kent" or "Ulster" or "Keele"
        or "East Anglia" or "Warwick" or "St Andrews" or "Strathclyde" or "Cranfield" or "Essex" or
        "Anglia Ruskin" or "Waterloo" or "Western University" or "Guelph" or "Simon Fraser" ) ) or
        country is ( AU or CA or IE or NZ or GB ) ) ) )
    or ( ( keyword is ( diabetic-retinopathy ) and keyword is ( screening or screening-uptake ) )
      or ( keyword is ( diabetes or diabetes-mellitus or type-1-diabetes or type-2-diabetes or
        diabetic-complications or diabetes-complications ) and keyword is ( retinopathy or
        maculopathy ) ) ) )
  and year >= ( 2003 )
  and year <= ( 2023 ) )
and openalex is ( W102211962
  or W133138556
  or W147193200
  or W1531291820
  or W1555314626
  or W1582532655
  or W159079241
  or W1605365105
  or W1965763915
  or W1974257011
  or W1979762576
  or W1979832181
  or W1980532269
  or W1983180255
  or W1983455295
  or W1998470199
  or W2012244609
  or W2019738782
  or W2035904548
  or W2045867306
  or W2051157055
  or W2056754897
  or W2059053512
  or W2059323660
  or W2067435056
  or W2068330450
  or W2068942383
  or W2069087339
  or W2070584107
  or W2081374068
  or W2103291025
  or W2119369454
  or W2126830768
  or W2127888591
  or W2128326945
  or W2129671420
  or W2129706953
  or W2131424154
  or W2137297224
  or W2140408413
  or W2142679415
  or W2147736741
  or W2150736691
  or W2150995354
  or W2151384865
  or W2156841030
  or W2164665650
  or W2165952134
  or W2167035512
  or W2168941618
  or W2169948307
  or W2172295224
  or W2193176257
  or W2211342319
  or W2262340642
  or W2328489735
  or W2339973334
  or W2342926115
  or W2346489057
  or W2404159748
  or W2405119914
  or W2575340954
  or W2590463259
  or W2591232282
  or W2592655617
  or W2600233120
  or W2612667187
  or W2766812641
  or W2768572445
  or W2803635223
  or W2803922294
  or W2805909107
  or W2888738728
  or W2898951878
  or W2903475542
  or W2913437479
  or W2919310303
  or W2943146351
  or W2944051522
  or W2953951961
  or W2963078422
  or W2965420043
  or W3000719683
  or W3011977104
  or W3016782994
  or W3017192035
  or W3022420917
  or W3027210051
  or W3092728347
  or W3093233282
  or W3108802630
  or W3109008062
  or W3115467577
  or W3122025734
  or W3126510186
  or W3129169745
  or W3134382414
  or W3159281016
  or W3160924776
  or W3181852238
  or W3194571354
  or W3197871327
  or W3200756352
  or W3200770789
  or W3201055785
  or W3207506343
  or W3209441643
  or W3211243369
  or W3213923128
  or W3215625743
  or W3216712031
  or W4200158933
  or W4210842964
  or W4220940019
  or W4223469416
  or W4242938226
  or W4280598166
  or W4281401710
  or W4283260062
  or W4288763631
  or W4297977795
  or W4307582454
  or W4309822054
  or W4310692022
  or W4311283030
  or W4312315505
  or W4319009170
  or W4361297832
  or W4377047469
  or W4386756937 )
```

### Execution requests

| UTC time | Status | View parameters |
| --- | ---: | --- |
| 2026-10-03T16:18:21.859055+00:00 | 200 | whole-case query; `{"per_page": 3}` |
| 2026-10-03T16:18:23.014647+00:00 | 400 | whole-case query; `{"per_page": 3, "sort": "relevance_score:desc"}` |
| 2026-10-03T16:25:32.839671+00:00 | 200 | whole-case query; `{"per_page": 1, "select": "id,publication_year"}` |
| 2026-10-03T16:25:39.150712+00:00 | 200 | reference restriction; `{"per_page": 200, "select": "id,publication_year"}` |
| 2026-10-03T16:22:55.900502+00:00 | 200 | whole-case query; `{"per_page": 200, "select": "id,relevance_score,publication_year"}` |
| 2026-10-03T16:22:57.106336+00:00 | 400 | whole-case query; `{"per_page": 200, "sort": "relevance_score:desc", "select": "id,relevance_score,publication_year"}` |
| 2026-10-03T16:22:58.317029+00:00 | 400 | whole-case query; `{"per_page": 200, "sort": "relevance_score:desc", "rerank": true, "select": "id,relevance_score,publication_year"}` |
| 2026-10-03T16:23:06.326337+00:00 | 200 | whole-case query; `{"per_page": 200, "select": "id,relevance_score,publication_year"}` |
| 2026-10-03T16:23:13.925212+00:00 | 200 | whole-case query; `{"per_page": 200, "cursor": "*", "select": "id,relevance_score,publication_year"}` |
