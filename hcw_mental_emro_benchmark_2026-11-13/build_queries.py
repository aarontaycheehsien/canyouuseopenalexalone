"""Frozen OQL arms for the healthcare-worker mental health (EMRO, COVID-19) benchmark.

Source: the free-text keyword string in the Methods (PubMed, Scopus, Embase; 1 January 2020 to
4 August 2024): COVID terms AND healthcare-worker terms AND mental-health terms. The search had
no geographic limit; the review's scope (WHO Eastern Mediterranean Region, EMRO) was applied at
screening, where 11,220 of 11,572 records were excluded as outside EMRO.

Arm M (mechanical): every quoted term exact (wildcards kept), on title-abstract-keywords (the
string names no field); 2020-01-01 to 2024-08-04.

Designed arms (written before the included studies were seen), same dates:
  each concept = title-abstract text OR the OpenAlex keywords that mean it (find_keywords):
  COVID AND healthcare workers AND mental health AND an EMRO concept. The EMRO concept adds the
  review's geographic scope, which the authors applied only at screening:
  S1 = EMRO as country/region/city names in title-abstract OR an author institution in any of the
       22 EMRO countries (OpenAlex affiliation metadata);
  S2 = EMRO as names in title-abstract only (no affiliation clause).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from designed_common import concept, ex, kw, q, write  # noqa: E402

D = "date >= (2020-01-01) and date <= (2024-08-04)"


def arm_m():
    b1 = q(*ex("covid-19", "covid19", "coronavirus", "sars-cov-2", "coronavirus disease-19"))
    b2 = q(*ex("health care worker*", "healthcare personnel*", "medical staff*", "nurse*", "doctor*", "physician*"))
    b3 = q(*ex("mental health", "psychological impact", "anxiety", "depress*", "stress", "ptsd"))
    return f"get works where {D} and " + " and ".join(f"title-abstract-keywords has {b}" for b in (b1, b2, b3))


COVID = q(*ex("covid*", "coronavirus*", "sars-cov-2", "sars cov 2", "2019-ncov", "ncov", "pandemic*"))
COVID_KW = kw(("COVID-19 pandemic", "covid-19"), ("COVID-19 pandemic impact", "covid-19-pandemic-impact"))
HCW = q(*ex("health care worker*", "healthcare worker*", "health-care worker*", "health worker*", "health professional*",
            "healthcare professional*", "health care professional*", "health personnel", "healthcare personnel", "medical staff",
            "hospital staff", "health staff", "medical worker*", "frontline", "front-line", "nurse*", "nursing", "doctor*", "physician*",
            "resident*", "midwi*", "pharmacist*", "dentist*", "paramedic*", "clinician*", "surgeon*", "anesthesiologist*",
            "anaesthetist*", "intern*", "medical students"))
HCW_KW = kw(("healthcare workers", "healthcare-workers"), ("nurses", "nurses"), ("registered nurses", "registered-nurses"),
            ("physician burnout", "physician-burnout"))
MENTAL = q(*ex("mental health", "psycholog*", "psychiatric", "anxi*", "depress*", "stress*", "ptsd", "posttraumatic", "post-traumatic",
               "burnout", "burn-out", "distress*", "insomnia", "sleep quality", "sleep disturbance*", "fear*", "emotional exhaustion",
               "resilien*", "wellbeing", "well-being", "suicid*", "obsessive"))
MENTAL_KW = kw(("mental health", "mental-health"), ("anxiety", "anxiety"), ("depression", "depression"), ("stress", "stress"),
               ("burnout", "burnout"), ("psychological distress", "psychological-distress"))
EMRO_NAMES = ["afghan*", "bahrain*", "djibouti*", "egypt*", "iran", "iranian*", "iraq*", "jordan*", "kuwait*", "lebanon", "lebanese",
              "libya*", "morocc*", "oman", "omani*", "pakistan*", "palestin*", "gaza", "west bank", "qatar*", "saudi*", "somali*",
              "sudan*", "syria*", "tunisia*", "united arab emirates", "uae", "emirati*", "yemen*", "eastern mediterranean", "middle east*",
              "arab*", "gulf cooperation", "gcc", "mena", "emro", "tehran", "shiraz", "mashhad", "isfahan", "tabriz", "riyadh", "jeddah",
              "dammam", "mecca", "makkah", "medina", "madinah", "cairo", "alexandria", "karachi", "lahore", "islamabad", "peshawar",
              "rawalpindi", "amman", "beirut", "doha", "muscat", "dubai", "abu dhabi", "baghdad", "kabul", "khartoum", "tunis", "rabat",
              "casablanca", "sanaa", "mogadishu", "damascus", "benghazi", "tripoli", "kuwait city", "manama"]
EMRO_TEXT = q(*ex(*EMRO_NAMES))
EMRO_CODES = [("Afghanistan", "AF"), ("Bahrain", "BH"), ("Djibouti", "DJ"), ("Egypt", "EG"), ("Iran", "IR"), ("Iraq", "IQ"), ("Jordan", "JO"),
              ("Kuwait", "KW"), ("Lebanon", "LB"), ("Libya", "LY"), ("Morocco", "MA"), ("Oman", "OM"), ("Pakistan", "PK"), ("Palestine", "PS"),
              ("Qatar", "QA"), ("Saudi Arabia", "SA"), ("Somalia", "SO"), ("Sudan", "SD"), ("Syria", "SY"), ("Tunisia", "TN"),
              ("United Arab Emirates", "AE"), ("Yemen", "YE")]
EMRO_INST = "institution country is (" + " or ".join(f"[{n}](countries/{c})" for n, c in EMRO_CODES) + ")"


def build():
    base = f"get works where {D} and " + " and ".join([concept(COVID, COVID_KW), concept(HCW, HCW_KW), concept(MENTAL, MENTAL_KW)])
    return {"M_mechanical_free_text": arm_m(),
            "S1_designed_emro_text_or_affiliation": base + f" and (title-abstract has {EMRO_TEXT} or {EMRO_INST})",
            "S2_designed_emro_text_only": base + f" and title-abstract has {EMRO_TEXT}"}


if __name__ == "__main__":
    write(ROOT, build(), "--check" in sys.argv)
