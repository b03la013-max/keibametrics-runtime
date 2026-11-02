"""R11: verify 2026-11-02 first-day FNB track bootstrap and no result leakage."""
import pytest
from runtime.local_fnb_r11_venue_temporal import verify


def fixture(race_no=1):
    request={"venue_id":"FNB","race_date":"2026-11-02","race_no":race_no,
             "race":{"race_no":race_no,"race_date":"2026-11-02"},
             "prediction_cutoff":"2026-11-02T14:40:00+09:00"}
    source={"source_race_context":{"venue_id":"FNB",
              "race_date":"2026/11/02","race_no":race_no},
            "source_freeze_at":"2026-11-02T14:33:00+09:00"}
    return source,request


def prior(n=1,at="2026-11-02T14:30:00+09:00"):
    return {"race_date":"2026-11-02","venue_id":"FNB","race_no":n,
            "official_result_verified":True,
            "signed_result_receipt_verified":True,"first_observed_at":at}


def test_r11_fnb_1r_unknown_current_not_yesterday_bias():
    source,request=fixture()
    state=verify(source_artifact=source,request=request)
    assert state["status"]=="FIRST_RACE_CURRENT_TRACK_BIAS_UNVERIFIED"
    assert state["prior_race_results_accepted"]==[]
    assert state["current_track_bias_status"]=="UNVERIFIED_CURRENT"
    assert state["numerical_mapping_changed"] is False
    assert state["prediction_krs_ticket_capital_consumption_authorized"] is False


def test_r11_later_race_without_verified_result_stays_current_unknown():
    source,request=fixture(3)
    state=verify(source_artifact=source,request=request)
    assert state["status"]=="TRACK_BIAS_CURRENT_UNVERIFIED_NO_SIGNED_PRIOR_RESULTS"


def test_r11_prior_signed_result_may_only_inform_later_race():
    source,request=fixture(3)
    source["fnb_same_day_result_observations"]=[prior(1)]
    state=verify(source_artifact=source,request=request)
    assert state["prior_race_results_accepted"]==[1]
    assert state["current_track_bias_status"]=="OBSERVED_PRIOR_RACE_ONLY_NOT_CALIBRATED"


@pytest.mark.parametrize("num", [3,4,12])
def test_r11_same_or_future_race_result_forbidden(num):
    source,request=fixture(3)
    source["fnb_same_day_result_observations"]=[prior(num)]
    with pytest.raises(ValueError,match="FNB_SAME_DAY_RESULT_NOT_PRIOR_RACE"):
        verify(source_artifact=source,request=request)


def test_r11_prior_result_future_observation_must_not_leak():
    source,request=fixture(3)
    source["fnb_same_day_result_observations"]=[prior(1,at="2026-11-02T14:34:00+09:00")]
    with pytest.raises(ValueError,match="FNB_TRACK_RESULT_OBSERVED_AFTER_FROZEN"):
        verify(source_artifact=source,request=request)


def test_r11_older_real_materializer_stays_behaviorally_compatible():
    import sys,json
    from pathlib import Path
    from runtime import formal_execution_orchestrator as o
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/"runtime"))
    from local_fullnumerical_production import materialize_production
    eid="LOCAL-KM-LOCAL-FNB-20261002-R04-LIVE-R1-EXEC"
    src=o.resolve_phase(eid,"SOURCE")
    assert src
    art=o._load_checkpoint_json(src,"source_receipt_envelope.json")["artifact"]
    intent=json.loads((root/"runtime/formal_intents/KM-LOCAL-FNB-20261002-R04-LIVE-R1.json").read_text())
    result=materialize_production(art,intent,intent["required_indices"])
    assert result["numeric_coverage"]["required_count"]==348
    assert result["numeric_coverage"]["calculated_count"]==312
    assert result["numeric_coverage"]["ruled_neutral_count"]==36
    temporal=result["fnb_venue_temporal_preflight"]
    assert temporal["current_track_bias_status"]=="UNVERIFIED_CURRENT"
    assert temporal["race_no"]==4
    assert temporal["no_future_or_same_race_results_used"] is True
