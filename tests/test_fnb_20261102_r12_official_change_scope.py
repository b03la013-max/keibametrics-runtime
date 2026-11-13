"""R12: official changes to another Race must not stop this Race.

All fixtures are synthetic. They never claim to be a fetched Signed SOURCE
or provide license, approval or a verified Active universe for 2026-11-02.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
import pytest

from runtime.local_fnb_r12_official_change_scope import reconcile
from runtime import formal_execution_orchestrator as o


def fixture(race_no=4):
    request={"venue_id":"FNB","race_no":race_no,"race_date":"2026-11-02",
             "scheduled_post_at":"2026-11-02T16:20:00+09:00"}
    source={"source_race_context":{"venue_id":"FNB",
        "race_date":"2026/11/02","race_no":race_no},
        "declared_runner_universe":{"runners":[{"horse_no":1,"name":"テスト甲"},
                                                {"horse_no":2,"name":"テスト乙"}]},
        "official_runner_universe":{"runners":[
            {"horse_no":1,"name":"テスト甲","jockey":"本田正重"},
            {"horse_no":2,"name":"テスト乙","jockey":"張田昂"}]}}
    day={"venue_id":"FNB","race_date":"2026-11-02",
         "source_authority":"NAR_OFFICIAL",
         "official_day_list_fetched":True,
         "all_notice_rows_parsed":True,"notices":[]}
    return source,request,day


def test_r12_unobserved_change_list_is_unknown_not_zero_change_guarantee():
    src,req,day=fixture()
    result=reconcile(src,req)
    assert result["status"]=="OFFICIAL_CHANGE_LIST_NOT_OBSERVED_UNKNOWN"
    assert result["no_change_guarantee"] is False
    assert result["license_verified_here"] is False


def test_r12_day_list_other_race_only_is_not_target_source_failure():
    src,req,day=fixture()
    day["notices"]=[{"race_no":6,"event_type":"JOCKEY_CHANGE",
        "horse_no":7,"new_jockey":"本田正重"}]
    result=reconcile(src,req,day)
    assert result["status"]=="OTHER_RACE_ONLY_NO_KNOWN_TARGET_NOTICE"
    assert result["other_race_notice_count"]==1
    assert not result["target_notices"]
    assert result["no_change_guarantee"] is False


def test_r12_target_known_jockey_change_validates_final_frozen_rider():
    src,req,day=fixture()
    day["notices"]=[{"race_no":4,"event_type":"JOCKEY_CHANGE",
                     "horse_no":1,"new_jockey":"本田正重"}]
    # Synthetic parsed-card fixture: the official active runner list may lack
    # a jockey column; the actual default resolver is separately tested
    # against an archived real signed source.
    def parsed_rider(source, horse):
        assert horse==1
        return {"current_jockey":source["official_runner_universe"]["runners"][0]["jockey"]}
    result=reconcile(src,req,day,rider_resolver=parsed_rider)
    assert result["status"]=="TARGET_KNOWN_CHANGES_RECONCILED"
    bad=copy.deepcopy(src)
    bad["official_runner_universe"]["runners"][0]["jockey"]="別騎手"
    with pytest.raises(ValueError,match="FNB_CHANGE_JOCKEY_NOT_APPLIED"):
        reconcile(bad,req,day,rider_resolver=parsed_rider)


def test_r12_cancelled_horse_must_not_remain_in_active_universe():
    src,req,day=fixture()
    day["notices"]=[{"race_no":4,"event_type":"CANCELLED","horse_no":1}]
    with pytest.raises(ValueError,match="FNB_CHANGE_CANCELLED_HORSE_STILL_ACTIVE"):
        reconcile(src,req,day)
    src["official_runner_universe"]["runners"].pop(0)
    result=reconcile(src,req,day)
    assert result["status"]=="TARGET_KNOWN_CHANGES_RECONCILED"


def test_r12_current_rider_whitespace_is_not_a_change_contradiction():
    src,req,day=fixture()
    day["notices"]=[{"race_no":4,"event_type":"JOCKEY_CHANGE",
                     "horse_no":1,"new_jockey":"所　蛍"}]
    result=reconcile(src,req,day,rider_resolver=lambda *_:{"current_jockey":"所蛍"})
    assert result["status"]=="TARGET_KNOWN_CHANGES_RECONCILED"
    assert result["no_change_guarantee"] is False
    with pytest.raises(ValueError,match="FNB_CHANGE_JOCKEY_NOT_APPLIED"):
        reconcile(src,req,day,rider_resolver=lambda *_:{"current_jockey":"別騎手"})


def test_r12_changed_post_time_must_be_reflected_not_retroactive():
    src,req,day=fixture()
    day["notices"]=[{"race_no":4,"event_type":"POST_TIME_CHANGE",
                     "new_post_at":"2026-11-02T16:30:00+09:00"}]
    with pytest.raises(ValueError,match="FNB_CHANGE_POST_TIME_NOT_REFLECTED"):
        reconcile(src,req,day)
    req["scheduled_post_at"]="2026-11-02T16:30:00+09:00"
    assert reconcile(src,req,day)["status"]=="TARGET_KNOWN_CHANGES_RECONCILED"


@pytest.mark.parametrize("fault",["missing_coverage","cross_date","duplicate","bad_type"])
def test_r12_failed_day_list_and_notice_revision_never_falsely_passes(fault):
    src,req,day=fixture()
    if fault=="missing_coverage":
        day["all_notice_rows_parsed"]=False
    elif fault=="cross_date":
        day["race_date"]="2026-11-03"
    elif fault=="duplicate":
        row={"race_no":4,"event_type":"CANCELLED","horse_no":1}
        day["notices"]=[row,copy.deepcopy(row)]
    else:
        day["notices"]=[{"race_no":4,"event_type":"UNRECOGNIZED","horse_no":1}]
    with pytest.raises(ValueError):
        reconcile(src,req,day)


def test_r12_historical_real_materializer_retains_unknown_changes_and_29_cells():
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/"runtime"))
    from local_fullnumerical_production import materialize_production
    eid="LOCAL-KM-LOCAL-FNB-20261002-R04-LIVE-R1-EXEC"
    phase=o.resolve_phase(eid,"SOURCE")
    saved=o._load_checkpoint_json(phase,"source_receipt_envelope.json")
    intent=json.loads((root/"runtime/formal_intents/KM-LOCAL-FNB-20261002-R04-LIVE-R1.json").read_text())
    out=materialize_production(saved["artifact"],intent,intent["required_indices"])
    assert out["numeric_coverage"]["required_count"]==348
    assert out["numeric_coverage"]["calculated_count"]==312
    assert out["numeric_coverage"]["ruled_neutral_count"]==36
    assert out["fnb_official_change_preflight"]["status"]=="OFFICIAL_CHANGE_LIST_NOT_OBSERVED_UNKNOWN"
