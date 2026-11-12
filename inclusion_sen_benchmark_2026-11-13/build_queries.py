"""Build the three frozen OQL arms from Dalgaard et al. (2022) Appendices 1-2.

Standard library only; no network. Run with --check to confirm the frozen files.

The review searched nine databases. Their strategies share one free-text core
(population AND intervention AND method) and differ in field limits and in
subject-heading lines. OpenAlex has no thesaurus, so subject-heading lines are
omitted in every arm (documented narrowing). The three arms are nested:

  B  Web of Science (SCI-EXPANDED + SSCI) strategy, translated exactly: it is
     text-only, so nothing is dropped. Population terms in TITLE only.
  A  EBSCO free-text core (Academic Search Premier, ERIC, PsycINFO, SocINDEX,
     EconLit): population S1 in title or abstract; S2 as
     TI (need* OR special* OR additional*) OR
     AB ((special* OR additional* OR educational*) N5 need*).
  C  Union of every database's free-text core. The IBSS line
     ti(need* OR special* OR additional*) OR ab(need* OR special* OR additional*)
     contains every other S2 variant, so C uses it; the rest is shared.
B is a subset of A, and A of C.

Shared: intervention TI/AB (integrat* OR immers* OR inclus* OR mainstream* OR
placement*); method TI/AB (effect* OR trial* OR experiment* OR control* OR
random* OR impact* OR compar* OR difference*). Every term is a quoted exact
wildcard term (EBSCO Boolean/Phrase mode, ProQuest and WoS do not stem).
EBSCO "N5" becomes OQL "within 5 words of each other" (any order).
Dates: 2000-01-01 (every database limiter) to 2021-04-08 (the appendix's last
search date; the article text says database searches were completed on
24 April 2021). Core corpus; no language, type or other restriction.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE_FROM, DATE_TO = "2000-01-01", "2021-04-08"

POP = ["student*", "pupil*", "child*", "youth*", "young*"]
NEED = ["need*", "special*", "additional*"]
INTERVENTION = ["integrat*", "immers*", "inclus*", "mainstream*", "placement*"]
METHOD = ["effect*", "trial*", "experiment*", "control*", "random*", "impact*", "compar*", "difference*"]


def q(terms):
    return "(" + " OR ".join(f'"{t}"' for t in terms) + ")"


def check_source():
    """Assert the term lists equal the published strategy lines."""
    src = json.loads((ROOT / "source_search_strategies.json").read_text())["strategies"]
    rows = {s["database"]: {r[0].strip(): " ".join(r[1].split()) for r in s["rows"][1:]} for s in src}
    eb = rows["APA PsycINFO (EBSCO)"]
    assert eb["S1"] == "TI (student* OR pupil* OR child* OR youth* OR young*) OR AB (student* OR pupil* OR child* OR youth* OR young*)"
    assert eb["S2"] == "TI (need* OR special* OR additional*) OR AB ((special* OR additional* OR educational*) N5 (need*))"
    assert eb["S5"] == "TI (integrat* OR immers* OR inclus* OR mainstream* OR placement*)"
    assert eb["S9"] == "TI (effect* OR trial* OR experiment* OR control* OR random* OR impact* OR compar* OR difference*)"
    for db in ("Academic Search Premier (EBSCO)", "ERIC (EBSCO)", "SocINDEX (EBSCO)"):
        assert rows[db]["S1"] == eb["S1"] and rows[db]["S2"] == eb["S2"], db
    assert rows["EconLit (EBSCO)"]["S2"] == eb["S2"]
    ib = rows["International Bibliography of the Social Sciences (ProQuest)"]
    assert ib["S2"] == "ti(need* OR special* OR additional*) OR ab(need* OR special* OR additional*)"
    wos = rows["Web of Science SCI-EXPANDED and SSCI"]
    assert wos["S1"] == "TI=(student* OR pupil* OR child* OR youth* OR young*)" and wos["S2"] == "TI=(need* OR special* OR additional*)"
    assert wos["S4"].startswith("TI=(integrat* OR immers* OR inclus* OR mainstream* OR placement*) OR AB=")
    assert wos["S5"].startswith("TI=(effect* OR trial* OR experiment* OR control* OR random* OR impact* OR compar* OR difference*) OR AB=")
    assert wos["S6"] == "#5 AND #4 AND #3"


def build():
    check_source()
    date = f"date >= ({DATE_FROM}) and date <= ({DATE_TO})"
    shared = f"title-abstract has {q(INTERVENTION)} and title-abstract has {q(METHOD)}"
    prox = " OR ".join(f'("{a}" and "need*" within 5 words of each other)' for a in ("special*", "additional*", "educational*"))
    return {
        "A_ebsco_text_core": f"get works where {date} and title-abstract has {q(POP)} and (title has {q(NEED)} or abstract has ({prox})) and {shared}",
        "B_web_of_science_exact": f"get works where {date} and title has {q(POP)} and title has {q(NEED)} and {shared}",
        "C_union_of_text_cores": f"get works where {date} and title-abstract has {q(POP)} and title-abstract has {q(NEED)} and {shared}",
    }


def main():
    check = "--check" in sys.argv
    for name, oql in build().items():
        path = ROOT / "queries" / f"{name}.oql"
        if check:
            assert path.read_text() == oql + "\n", path
        else:
            path.write_text(oql + "\n")
        print(name, len(oql), hashlib.sha256((oql + "\n").encode()).hexdigest())
    if check:
        print("builder output matches frozen files")


if __name__ == "__main__":
    main()
