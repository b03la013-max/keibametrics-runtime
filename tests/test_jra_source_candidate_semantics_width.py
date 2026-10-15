import copy
import sys
sys.path.insert(0,"runtime")

from jra_source_candidate_semantics import build_candidate_semantics, PROFILE
from minimum_efficient_coverage import build_mec_plan, validate_mec_plan
from capital_policy import resolve_capital_policy


def runner(i, win, place, third):
    return {
      "runner_id":str(i),
      "canonical_components":{
        "ZAI_WIN":{"value":float(win)},
        "ZAI_PLACE":{"value":float(place)},
        "T3I":{"value":float(third)},
      }
    }


def strong_structure():
    return [
      runner(1,100,100,100),
      runner(2,70,98,98),
      runner(3,69,70,96),
      runner(4,68,69,70),
      runner(5,67,68,69),
      runner(6,66,67,68),
      runner(7,65,66,67),
      runner(8,64,65,66),
    ]


def parity_structure():
    return [runner(i,80,80,80) for i in range(1,9)]


def test_structure_not_budget_drives_width():
    base={
      "race_id":"TEST-JRA-STRUCTURE-STRONG",
      "family_id":"JRA",
      "runners":strong_structure(),
    }
    sem=build_candidate_semantics(base)
    freeze=sem["candidate_semantic_freeze"]

    assert PROFILE=="KM-JRA-SOURCE-DERIVED-CANDIDATE-SEMANTICS-v0.3-20261004-STRUCTURE-DERIVED"
    assert freeze["width_policy"]["driver"]=="RACE_FORCE_RELATIONSHIP_NOT_BUDGET"
    assert freeze["width_policy"]["fixed_w_width"] is None
    assert freeze["width_policy"]["fixed_p2_width"] is None
    assert freeze["width_policy"]["fixed_p3_width"] is None
    assert freeze["width_policy"]["target_capital_band_yen"] is None
    assert freeze["width_policy"]["budget_input_used"] is False
    assert sem["aki_capital_bridge"]["direct_ticket_count_control"] is False

    # Strong head / strong second / strong third structure naturally compresses.
    assert len(freeze["w_active"])==1, freeze["w_active"]
    assert len(freeze["p2_active"])==2, freeze["p2_active"]
    assert len(freeze["p3_active"])==3, freeze["p3_active"]
    assert sem["future_multiplicity"]["state"]=="CONCENTRATED"

    mec=build_mec_plan(sem,None,strict_head_closure=True,min_stake=100)
    validate_mec_plan(mec)
    assert mec["minimum_required_capital"]>0


def test_parity_expands_without_budget_target():
    req={
      "race_id":"TEST-JRA-STRUCTURE-PARITY",
      "family_id":"JRA",
      "runners":parity_structure(),
    }
    sem=build_candidate_semantics(req)
    freeze=sem["candidate_semantic_freeze"]

    assert len(freeze["w_active"])==8
    assert len(freeze["p2_active"])==8
    assert len(freeze["p3_active"])==8
    assert sem["future_multiplicity"]["state"]=="DIVERSE"

    mec=build_mec_plan(sem,None,strict_head_closure=True,min_stake=100)
    validate_mec_plan(mec)

    strong=build_candidate_semantics({
      "race_id":"TEST-JRA-STRUCTURE-STRONG-COMPARE",
      "family_id":"JRA",
      "runners":strong_structure(),
    })
    strong_mec=build_mec_plan(strong,None,strict_head_closure=True,min_stake=100)
    validate_mec_plan(strong_mec)
    assert mec["ticket_count"]>strong_mec["ticket_count"]
    assert mec["minimum_required_capital"]>strong_mec["minimum_required_capital"]


def test_budget_never_changes_semantic_topology():
    r=strong_structure()
    low=build_candidate_semantics({
      "race_id":"TEST-JRA-BUDGET-INDEPENDENCE",
      "family_id":"JRA",
      "runners":copy.deepcopy(r),
      "capital_policy":{"mode":"HARD_RACE_BUDGET","max_race_capital":3000},
    })
    high=build_candidate_semantics({
      "race_id":"TEST-JRA-BUDGET-INDEPENDENCE",
      "family_id":"JRA",
      "runners":copy.deepcopy(r),
      "capital_policy":{"mode":"HARD_RACE_BUDGET","max_race_capital":10000},
    })

    for key in ("w_active","p2_active","p3_active","pair_count","third_count"):
        assert low["candidate_semantic_freeze"][key]==high["candidate_semantic_freeze"][key]
    assert low["role_registry"]==high["role_registry"]
    assert low["pair_dispositions"]==high["pair_dispositions"]
    assert low["third_dispositions"]==high["third_dispositions"]


if __name__=="__main__":
    test_structure_not_budget_drives_width()
    test_parity_expands_without_budget_target()
    test_budget_never_changes_semantic_topology()
    print("JRA_STRUCTURE_DERIVED_SEMANTICS_PASS")
