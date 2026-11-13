"""Frozen OQL arms for the virtual-reality upper-limb stroke rehabilitation benchmark.

Source: Additional File 1. PubMed, Scopus, IEEE, Web of Science and PsycNet, English-language
RCTs from inception to March 2023. Four blocks: stroke AND technology AND rehabilitation AND
trial design; the PubMed trial block uses publication types and filters, so arm M translates
the Web of Science TS= string, whose four blocks are all text.

Arm M (mechanical), Web of Science rules: unquoted words are lemmatised, so they stay bare
(stemmed); quoted phrases are exact; truncated terms are exact wildcards; ? -> * ; the source's
misspelling asisst* is kept as written; OQL allows at most two wildcards in a phrase, so
"Random* Control* Trial*" becomes "random* controlled trial*" OR "random* control trial*"; unbalanced quotes in the source are read as phrases;
field title-abstract-keywords (TS = topic); English (the authors' limit); date <= 2023-03-31.

Designed arms (written before the included studies were seen), English, date <= 2023-03-31:
  S1 = stroke AND virtual-reality/gaming AND randomised-trial concepts, each text in
       title-abstract OR the OpenAlex keywords that mean it; the authors' near-universal
       rehabilitation block (therapy, treat*, care, system, support ...) is dropped;
  S2 = S1 AND an upper-limb concept (the review's population is upper-limb rehabilitation).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from designed_common import assert_in_source, concept, ex, kw, near, q, write  # noqa: E402

D = "date <= (2023-03-31) and language is [English](en)"


def arm_m():
    src = [p for p in json.loads((ROOT / "source_search_strategy.json").read_text())["paragraphs"] if p.startswith("TS=")][0]
    stroke = q("stroke*".join(['"', '"']), "cva", '"cerebrovas*"', '"poststroke*"', '"post-stroke*"', '"hemipleg*"', "paretic", "apoplexy", "paresis",
               '"hemipare*"', '"neuroplast*"',
               "(" + q('"cerebral*"', '"brain*"', "cerebellar") + " AND " + q('"infarct*"', '"isch*mi*"', '"thrombo*"', '"emboli*"', '"apoplex*"',
                                                                               '"attack*"', '"vascular*"', '"injur*"') + ")",
               "(" + q("cerebral", "brain", "cerebella") + " AND " + q("haemorrhage", "hemorrhage", "haematoma", "hematoma", '"bleed*"') + ")",
               '"transient ischemic attack"', "tia", '"subarachnoid hemorrhage"', '"gait disorders"')
    tech = q('"comput*"', '"asisst*"', '"comput* assist*"', '"simulat*"', '"comput* base*"', '"genera*"', '"cyber*"', '"virtual*"', '"immers*"',
             '"semi* immers*"', '"metaverse*"', "3d", '"augment*"', '"digit*"', '"visual*"', '"virtual reality"', "(stemmed \"virtual reality\")", "vr",
             '"augmented reality"', "(stemmed \"augmented reality\")", "ar", '"mixed reality"', "(stemmed \"mixed reality\")", '"game*"',
             '"video* game*"', "(stemmed \"video game\")", '"interact* game*"', '"serious* game*"', '"gamificat*"')
    rehab = q('"rehab*"', "recovery", '"restore*"', '"habilitat*"', "therapy", '"treat*"', "care", '"plan*"', '"intervent*"', '"approach*"',
              '"interact*"', '"counsel*"', '"heal*"', '"aid*"', '"help*"', '"relief*"', '"well*"', "support", "program", "software", "system", "device",
              '"technique*"')
    rct = q('"clinical trial*"', '"random* controlled trial*"', '"random* control trial*"', '"rct"')
    assert_in_source(["Stroke*", "Cerebrovas*", "isch?mi*", "asisst*", "comput* base*", "semi* immers*", "metaverse*", "Gamificat*", "Habilitat*",
                      "Random* Control* Trial*", "Subarachnoid hemorrhage", "Gait Disorders", "cerebella"], src)
    return f"get works where {D} and " + " and ".join(f"title-abstract-keywords has {b}" for b in (stroke, tech, rehab, rct))


STROKE_TEXT = q(*ex("stroke*", "poststroke", "post-stroke", "hemipar*", "hemipleg*", "cerebrovascular", "paretic", "cerebrovascular accident*",
                    "intracerebral hemorrhage", "intracerebral haemorrhage"), *near(["cerebral", "brain"], ["infarct*"], 2))
STROKE_KW = kw(("stroke", "stroke"), ("ischemic stroke", "ischemic-stroke"), ("stroke rehabilitation", "stroke-rehabilitation"),
               ("hemiparesis", "hemiparesis"), ("post-stroke hemiparesis", "post-stroke-hemiparesis"), ("upper limb hemiparesis", "upper-limb-hemiparesis"))
VR_TEXT = q(*ex("virtual reality", "virtual-reality", "virtual environment*", "virtual rehabilitation", "virtual training", "immersive",
                "semi-immersive", "non-immersive", "exergam*", "video gam*", "videogam*", "serious game*", "computer game*", "interactive game*",
                "gaming", "game-based", "kinect", "nintendo", "wii", "xbox", "playstation", "eyetoy", "leap motion", "head-mounted display*",
                "augmented reality", "mixed reality", "gamif*", "rehabilitation gaming system", "telerehabilitation"),
            *near(["virtual"], ["reality", "realities"], 2), *near(["video"], ["game*"], 2))
VR_KW = kw(("virtual reality", "virtual-reality"), ("immersive virtual reality", "immersive-virtual-reality"),
           ("virtual reality simulation", "virtual-reality-simulation"), ("exergames", "exergames"), ("virtual reality exergames", "virtual-reality-exergames"),
           ("video games", "video-games"))
RCT_TEXT = q(*ex("random*", "rct", "rcts", "controlled trial*", "controlled clinical trial*", "control group*", "controlled study", "clinical trial*",
                 "pilot trial*", "feasibility trial*", "single-blind*", "double-blind*", "assessor-blind*", "sham"))
RCT_KW = kw(("randomized controlled trials", "randomized-controlled-trials"), ("pragmatic randomized controlled trial", "pragmatic-randomized-controlled-trial"))
UL_TEXT = q(*ex("upper limb*", "upper-limb*", "upper extremit*", "upper-extremit*", "arm", "arms", "hand", "hands", "wrist*", "finger*", "shoulder*",
                "elbow*", "reach*", "grasp*", "dexterity", "fugl-meyer", "box and block", "wolf motor", "action research arm", "motor function*",
                "motor recovery", "motor performance"))
UL_KW = kw(("upper limb", "upper-limb"), ("upper limb function", "upper-limb-function"), ("upper limb rehabilitation", "upper-limb-rehabilitation"),
           ("upper limb hemiparesis", "upper-limb-hemiparesis"), ("motor recovery", "motor-recovery"))


def build():
    s1 = f"get works where {D} and " + " and ".join([concept(STROKE_TEXT, STROKE_KW), concept(VR_TEXT, VR_KW), concept(RCT_TEXT, RCT_KW)])
    return {"M_mechanical_wos": arm_m(), "S1_designed_stroke_vr_rct": s1, "S2_designed_plus_upper_limb": s1 + " and " + concept(UL_TEXT, UL_KW)}


if __name__ == "__main__":
    write(ROOT, build(), "--check" in sys.argv)
