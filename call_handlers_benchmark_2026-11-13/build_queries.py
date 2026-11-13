"""Frozen OQL arms for the mental health of emergency call-handlers and dispatchers benchmark.

Source: Supplementary Table 1. Ten databases (Medline, PubMed, PsycARTICLES, PsycEXTRA,
PsycINFO, Embase, Web of Science, CINAHL Plus, Cochrane Library) from inception to 7 January 2024,
plus Google Scholar, hand-searching of Annals of Emergency Dispatch and Response, other reviews'
reference lists, and forward and backward citation searching. Languages: English, French,
Spanish, Italian and Portuguese. Two blocks: call-handler/dispatcher terms AND mental-health
terms (MeSH exploded).

Arm M (mechanical), Ovid rules: terms exact, truncation kept; cris?s -> cris*s; adj3 -> within 2
words; OQL allows at most two wildcards per phrase, each with four leading characters when there
are two, so the middle wildcard of three-wildcard phrases is dropped ("emergenc* call* cent*" ->
"emergenc* call cent*") and "emergenc* call* tak*" -> "emergenc* call taker*", and "emergenc* med*
communicat*" -> "emergenc* medical communicat*"; field title-abstract-keywords; the five languages;
date <= 2024-01-07.

Designed arms (written before the included studies were seen), same languages and date:
  S1 = call-handler concept AND mental-health concept, each title-abstract text OR the OpenAlex
       keywords that mean it. Bare dispatch* (power systems, logistics) is replaced by dispatch
       terms in an emergency context (proximity); call-centre, crisis-line and helpline terms kept;
       mental health adds occupational stress, burnout and alcohol/hazardous drinking.
  S2 = S1 without the generic call-centre/helpline terms (commercial call centres, helpline users).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from designed_common import concept, ex, kw, near, q, write  # noqa: E402

D = "date <= (2024-01-07) and language is ([English](en) or [French](fr) or [Spanish](es) or [Italian](it) or [Portuguese](pt))"


def arm_m():
    b1 = q(*ex("call handl*", "dispatch*", "emergenc* call handl*", "emergenc* dispatch*", "emergenc* call cent*", "emergenc* dispatch cent*",
               "emergenc* call*", "emergenc* communicat*", "emergenc* medical communicat*", "call* operator*", "emergenc* call taker*", "cris*s call*"))
    b2 = q(*ex("stress*", "trauma*", "mental health", "well being", "wellbeing", "ptsd", "post traumatic stress disorder", "anxiet*", "depressi*",
               "resilien*"), *near(["post trauma*"], ["growth"], 2))
    return f"get works where {D} and " + " and ".join(f"title-abstract-keywords has {b}" for b in (b1, b2))


CORE = ["call handl*", "call-handl*", "call taker*", "call-taker*", "dispatcher*", "telecommunicator*", "emergency call*", "emergency communication*",
        "public safety telecommunicat*", "public safety answering", "emergency operator*", "control room*", "999 call*", "112 call*", "911 call*"]
GENERIC = ["call cent*", "call-cent*", "crisis line*", "crisis call*", "helpline*", "hotline*"]
DISPATCH = near(["dispatch*"], ["emergenc*", "ambulance*", "police", "fire", "911", "medical", "rescue"], 3)
CHD_KW = kw(("emergency medical dispatch", "emergency-medical-dispatch"), ("call centers", "call-centers"), ("dispatchers", "dispatchers"))
CHD_KW_NARROW = kw(("emergency medical dispatch", "emergency-medical-dispatch"), ("dispatchers", "dispatchers"))
MENTAL = q(*ex("mental health", "psycholog*", "psychiatric", "anxi*", "depress*", "stress*", "ptsd", "posttraumatic", "post-traumatic",
               "trauma*", "burnout", "burn-out", "distress*", "wellbeing", "well-being", "resilien*", "emotional exhaustion", "compassion fatigue",
               "secondary traumatic", "vicarious", "alcohol*", "hazardous drinking", "substance use", "sleep*", "suicid*"),
           *near(["post trauma*", "posttraumatic"], ["growth"], 2))
MENTAL_KW = kw(("mental health", "mental-health"), ("anxiety", "anxiety"), ("depression", "depression"), ("stress", "stress"),
               ("burnout", "burnout"), ("psychological distress", "psychological-distress"))


def build():
    s1 = f"get works where {D} and " + " and ".join([concept(q(*ex(*CORE, *GENERIC), *DISPATCH), CHD_KW), concept(MENTAL, MENTAL_KW)])
    s2 = f"get works where {D} and " + " and ".join([concept(q(*ex(*CORE), *DISPATCH), CHD_KW_NARROW), concept(MENTAL, MENTAL_KW)])
    return {"M_mechanical_ovid": arm_m(), "S1_designed_two_concepts": s1, "S2_designed_without_generic_call_centres": s2}


if __name__ == "__main__":
    write(ROOT, build(), "--check" in sys.argv)
