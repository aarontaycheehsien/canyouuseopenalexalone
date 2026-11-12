"""Extract Appendix A vocabulary, without opening any included-study records.

Usage: python extract_search_terms.py SOURCE_SUPPLEMENT.docx
Writes vocabulary.json for review BEFORE a protocol freeze; do not rerun to
change a frozen experiment. Standard library only.
"""
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parent


def terms(text):
    text = text.replace("“", '"').replace("”", '"').replace("’", "'")
    text = text.replace("nitric oxideOR", "nitric oxide OR")
    text = re.sub(r'\("2014"\[Date - Publication\]\s*:\s*"2016/08/02"\[Date - Publication\]\)', "", text)
    text = re.sub(r"\[[^\]]*\]", " ", text)
    text = re.sub(r":ab\.ti", " ", text, flags=re.I)
    text = text.replace('"', " ")
    parts = re.split(r"\bOR\b", text, flags=re.I)
    out = []
    for part in parts:
        term = " ".join(part.replace("(", " ").replace(")", " ").split()).strip()
        if term == "Dinoprost/analogs and derivatives":
            term = "Dinoprost"
        if term and term.lower() not in {x.lower() for x in out}:
            out.append(term)
    return out


def main():
    with zipfile.ZipFile(sys.argv[1]) as doc:
        root = ET.fromstring(doc.read("word/document.xml"))
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    text = "\n".join("".join(t.text or "" for t in p.findall(".//w:t", ns)) for p in root.findall(".//w:p", ns))
    text = text[:text.index("Supplementary material B:")]
    sections = re.split(r"\n(?=A[1-7][ .])", text)[1:]
    assert len(sections) == 7
    a1, a2, a3, a4, a5, a6, a7 = sections
    a1groups = a1.split(" AND ")
    population = terms(a1groups[0][a1groups[0].index('("depressive'):])
    long_prediction = terms(a1groups[1])
    short_prediction = terms(a2.split(" AND ")[2])
    groups = {
        "neuroimaging": terms(a1groups[2]),
        "gastrointestinal": terms(a2[a2.index("(microbiota"):].split(" AND ")[0]),
        "immunology": terms(a3[a3.index("(CRP"):].split(" AND ")[0]),
        "neurotrophic": terms(a4[a4.index("(BDNF"):]),
        "neurotransmitters": terms(a5.split(" AND ")[1]),
        "gonadal_hormones": terms(a6[a6.index('"sex hormones"'):a6.index("Pubmed additional search")]),
        "other_hormones": terms(a6[a6.index("Cortisol["):].split(" AND ")[0]),
        "oxidative_stress": terms(a7[a7.index("(oxidative stress"):]),
    }
    value = {"population": population, "prediction_long": long_prediction,
             "prediction_short": short_prediction, "biomarker_groups": groups}
    (ROOT / "vocabulary.json").write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    for name, values in [("population", population), ("prediction_long", long_prediction),
                         ("prediction_short", short_prediction), *groups.items()]:
        print(name, len(values), values)


if __name__ == "__main__":
    main()
