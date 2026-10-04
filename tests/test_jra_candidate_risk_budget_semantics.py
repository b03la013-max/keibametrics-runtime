from pathlib import Path
import sys
sys.path.insert(0, "runtime")

from jra_source_candidate_semantics import build_candidate_semantics


def runner(i):
    base=100-i
    return {
      "runner_id":str(i),
      "canonical_components":{
        "ZAI_WIN":{"value":base},
        "ZAI_PLACE":{"value":base-0.1},
        "T3I":{"value":base-0.2},
      }
    }


def test_r38_risk_budget_expansion_is_not_on_active_candidate_path():
    req={
      "race_id":"TEST-JRA-R38-DEPRECATED",
      "family_id":"JRA",
      "runners":[runner(i) for i in range(1,9)],
      "capital_policy":{"mode":"HARD_RACE_BUDGET","max_race_capital":10000},
    }
    sem=build_candidate_semantics(req)
    assert "candidate_risk_budget_expansion" not in sem
    assert sem["candidate_semantic_freeze"]["width_policy"]["budget_input_used"] is False
    assert sem["candidate_semantic_freeze"]["width_policy"]["target_capital_band_yen"] is None

    for p in (
      ".github/workflows/km-jra-source-candidate-forward-oos.yml",
      ".github/workflows/km-jra-source-candidate-full-lifecycle.yml",
    ):
        text=Path(p).read_text(encoding="utf-8")
        assert "expand_candidate_semantics_with_risk_budget" not in text


if __name__=="__main__":
    test_r38_risk_budget_expansion_is_not_on_active_candidate_path()
    print("JRA_R38_RISK_BUDGET_DEACTIVATION_PASS")
