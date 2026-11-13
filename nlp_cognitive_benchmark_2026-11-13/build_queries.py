"""Frozen OQL arms for the NLP detection of cognitive impairment benchmark.

Source: the base search string in the article (Methods): NLP terms AND cognitive-impairment
terms AND detection terms AND speech/language terms, "adapted for each database"; English;
PubMed, Web of Science, Embase, CINAHL, MEDLINE, Cochrane Library, PsycINFO and Scopus from
inception to August 2024.

Arm M (mechanical): every quoted term exact (wildcards kept), on title-abstract-keywords (the
base string names no field); English; date <= 2024-08-31.

Designed arms (written before the included studies were seen), English, date <= 2024-08-31:
  S1 = NLP/computational-analysis AND cognitive-impairment AND speech/language-data concepts,
       each text in title-abstract OR the OpenAlex keywords that mean it (the authors'
       detection block is left out for recall). Development counts led to two cuts before the
       freeze: acoustic/prosodic terms left out of the method concept (the review excludes
       acoustic-only work), and generic words (word*, text, verbal, semantic, writing) left out of
       the speech/language concept (development count 39,249 before the cuts); then transcript*,
       which also matches transcriptome/transcriptional (Alzheimer genetics), replaced by
       "transcripts", "transcribed", "speech transcript*" (development count 36,126 before that);
  S2 = S1 AND a detection/classification concept.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from designed_common import concept, ex, kw, near, q, write  # noqa: E402

D = "date <= (2024-08-31) and language is [English](en)"


def arm_m():
    s = json.loads((ROOT / "source_search_strategy.json").read_text())["search_string"]
    blocks = re.findall(r"\(([^()]*)\)", s)
    assert len(blocks) == 4, blocks
    out = []
    for b in blocks:
        terms = [t.strip().strip("“”\"").replace("∗", "*").lower() for t in re.split(r"\s+OR\s+", b)]
        out.append(q(*ex(*terms)))
    assert [len(re.split(r"\s+OR\s+", b)) for b in blocks] == [7, 8, 6, 5]
    return f"get works where {D} and " + " and ".join(f"title-abstract-keywords has {b}" for b in out)


NLP_TEXT = q(*ex("natural language processing", "nlp", "computational linguistic*", "text mining", "language model*", "large language model*",
                 "bert", "word embedding*", "machine learning", "deep learning", "neural network*", "classifier*", "speech recognition",
                 "linguistic analys*", "language analys*", "speech analys*", "discourse analys*", "lexical analys*", "computational analys*",
                 "automated analys*", "automatic analys*", "speech transcript*", "transcribed speech"),
             *near(["automat*", "computational", "computer*", "computerized", "computerised"], ["speech", "language", "linguistic", "discourse", "transcripts"], 3),
             *near(["linguistic", "lexical", "semantic", "syntactic", "language", "speech"], ["feature*", "marker*", "biomarker*"], 2))
NLP_KW = kw(("natural language processing", "natural-language-processing"), ("clinical natural language processing", "clinical-natural-language-processing"),
            ("speech analysis", "speech-analysis"), ("automated speech analysis", "automatic-speech-analysis"), ("linguistic analysis", "linguistic-analysis"),
            ("linguistic features", "linguistic-features"))
COG_TEXT = q(*ex("cognitive impairment*", "cognitive decline", "cognitive disorder*", "dementia*", "alzheimer*", "mci", "neurocognitive",
                 "neurodegenerat*", "primary progressive aphasia", "frontotemporal"), *near(["cognitive", "cognitively"], ["impair*", "declin*"], 2))
COG_KW = kw(("dementia", "dementia"), ("Alzheimer's disease", "alzheimer-s-disease"), ("mild cognitive impairment", "mild-cognitive-impairment"),
            ("cognitive impairment detection", "cognitive-impairment-detection"), ("amnestic mild cognitive impairment", "amnestic-mild-cognitive-impairment"),
            ("frontotemporal dementia", "frontotemporal-dementia"))
LANG_TEXT = q(*ex("speech", "language", "spoken", "discourse", "narrative*", "transcripts", "transcribed", "conversation*", "picture description*", "cookie theft",
                  "voice", "linguistic*", "lexical", "syntactic", "utterance*"))
LANG_KW = kw(("spontaneous speech", "spontaneous-speech"), ("speech analysis", "speech-analysis"))
DET_TEXT = q(*ex("detect*", "diagnos*", "classif*", "predict*", "screen*", "identif*", "discriminat*", "distinguish*", "accuracy", "auc",
                 "sensitivity", "specificity", "recogni*"))


def build():
    s1 = f"get works where {D} and " + " and ".join([concept(NLP_TEXT, NLP_KW), concept(COG_TEXT, COG_KW), concept(LANG_TEXT, LANG_KW)])
    return {"M_mechanical_base_string": arm_m(), "S1_designed_three_concepts": s1, "S2_designed_plus_detection": s1 + " and " + concept(DET_TEXT, None)}


if __name__ == "__main__":
    write(ROOT, build(), "--check" in sys.argv)
