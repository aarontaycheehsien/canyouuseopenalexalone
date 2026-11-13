"""Frozen OQL arms for the public-support-for-novel-smoke-free-policies benchmark.

Source: Appendix I. Every database used: smoke-free policy terms AND support/attitude terms in
title and abstract (plus subject headings and publication-type exclusions). Reports published
1 January 2004 to 19 January 2022.

Arm M (mechanical): the Medline Ovid .ab,ti lines. Ovid does not stem, so terms are exact;
ADJ3 -> within 2 words (OpenAlex's rule for Ovid); OR groups expanded to pairs; subject headings
and the .pt. exclusions omitted; title-abstract; 2004-01-01 to 2022-01-19.

Designed arms (written before the included studies were seen):
  S1 = smoke-free policy concept AND support concept, each text in title-abstract OR the
       OpenAlex keywords that mean it (from find_keywords). Policy words near smoking words with
       proximity; OQL's two-wildcard limit means short words (ban, law) are spelled out. Because
       "support" is near-universal in tobacco-policy abstracts (development count 39,992), the
       support text is tied to policy words: a support word within 5 words of a smoking or policy
       word (development count 10,282). Support keywords: public support, public opinion survey.
  S2 = S1 AND a "novel places" concept (outdoor areas, vehicles, homes, multi-unit housing,
       campuses, parks, beaches, stadiums, dining terraces, (semi-)private places): the review's
       scope is support for smoke-free places beyond indoor public places and workplaces.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from designed_common import assert_in_source, concept, ex, kw, near, q, write  # noqa: E402

D = "date >= (2004-01-01) and date <= (2022-01-19)"
SMOKE = ["smoking", "smoke", "tobacco"]
POLICY = ["regulation*", "government*", "law", "laws", "policy", "policies", "ban", "bans", "banned", "free", "restrict*", "act", "acts"]
SUPPORT = ["opinion*", "support*", "views", "attitude*", "feeling*", "acceptance*", "accepts", "perception*", "misperception*"]


def arm_m():
    import json
    src = json.loads((ROOT / "source_search_strategy.json").read_text())["text"]
    assert_in_source(["smokefree"] + SMOKE + POLICY + SUPPORT + ["public ADJ3 view"], src)
    b1 = q('"smokefree"', *near(SMOKE, POLICY, 2))
    b2 = q(*ex(*SUPPORT), *near(["public"], ["view"], 2))
    return f"get works where {D} and title-abstract has {b1} and title-abstract has {b2}"


S_POLICY_TEXT = q(*ex("smoke-free", "smokefree", "smoke free", "tobacco-free", "tobacco free", "smoking ban*", "no smoking", "no-smoking"),
                  *near(["smok*", "tobacco", "cigarette*"], ["polic*", "regulat*", "restrict*", "prohibit*", "legislat*", "rule*"], 3),
                  *near(["smoking", "smoke", "tobacco", "cigarette"], ["ban", "bans", "banned", "banning", "law", "laws", "free"], 3))
S_POLICY_KW = kw(("smoke-free policies", "smoke-free-policies"), ("smoking bans", "smoking-bans"), ("public smoking bans", "smoking-bans-in-public-places"),
                 ("home smoking bans", "home-smoking-bans"), ("smoke-free homes", "smoke-free-homes"), ("outdoor smoking", "outdoor-smoking"),
                 ("smoke-free campus policy", "smoke-free-campus-policy"), ("smoke-free workplace policies", "smoke-free-workplace-policies"),
                 ("tobacco policy", "tobacco-policy"))
SUPW = ["support*", "opinion*", "attitud*", "acceptab*", "acceptance", "approv*", "endors*", "perception*", "favo*r", "oppos*"]
POLW = ["smok*", "tobacco", "smoke-free", "smokefree", "ban", "bans", "banning", "polic*", "law", "laws", "legislat*", "restrict*", "regulat*", "prohibit*"]
S_SUPPORT_TEXT = q(*near(SUPW, POLW, 5))
S_SUPPORT_KW = kw(("public support", "public-support"), ("public opinion survey", "public-opinion-survey"))
S_PLACE_TEXT = q(*ex("outdoor*", "park", "parks", "playground*", "beach*", "car", "cars", "vehicle*", "home", "homes", "household*",
                     "housing", "apartment*", "multi-unit", "multiunit", "condominium*", "stadium*", "sport*", "campus*", "universit*",
                     "school ground*", "hospital ground*", "terrace*", "patio*", "outdoor dining", "bus stop*", "street*", "entrance*",
                     "private", "semi-private", "public places", "public spaces", "event*", "festival*", "zoo*", "prison*", "balcon*"))
S_PLACE_KW = kw(("outdoor smoking", "outdoor-smoking"), ("smoke-free homes", "smoke-free-homes"), ("home smoking bans", "home-smoking-bans"),
                ("household smoking", "home-smoking"), ("smoke-free campus policy", "smoke-free-campus-policy"))


def build():
    s1 = f"get works where {D} and " + " and ".join([concept(S_POLICY_TEXT, S_POLICY_KW), concept(S_SUPPORT_TEXT, S_SUPPORT_KW)])
    return {"M_mechanical_ovid": arm_m(), "S1_designed_policy_support": s1,
            "S2_designed_plus_places": s1 + " and " + concept(S_PLACE_TEXT, S_PLACE_KW)}


if __name__ == "__main__":
    write(ROOT, build(), "--check" in sys.argv)
