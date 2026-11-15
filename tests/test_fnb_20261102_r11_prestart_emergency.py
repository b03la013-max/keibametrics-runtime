"""R11 live-day emergency readiness: official clock is not invented cutoff."""
from datetime import datetime,timezone,timedelta
from runtime.local_fnb_r11_prestart_emergency import program,evaluate,DAY

JST=timezone(timedelta(hours=9))


def test_fnb_20261102_12race_130_listed_3770_theoretical_cells():
    rows=program()
    assert len(rows)==12
    assert sum(x["declared_runner_count"] for x in rows)==130
    assert sum(x["required_index_cells_theoretical"] for x in rows)==3770
    assert rows[0]["scheduled_post_at"]=="2026-11-02T14:45:00+09:00"
    assert rows[-1]["scheduled_post_at"]=="2026-11-02T20:50:00+09:00"
    assert rows[2]["declared_runner_count"]==7
    assert rows[10]["declared_runner_count"]==13


def test_r11_two_hour_prestart_is_not_formal_approval_or_numeric_completion():
    t=datetime(2026,11,2,12,47,tzinfo=JST)
    existing={"authority_manifest_observed":"KM-FAMILY-CURRENT-AUTHORITY-20261012-R51",
        "fnb_static_owner_authorized":False,"dated_plan_exists_and_valid":False,
        "dated_approval_present":False,"numeric_consumption":{
            k:False for k in ("prediction_consumption_authorized",
                "krs_consumption_authorized","ticket_consumption_authorized",
                "capital_consumption_authorized")},
        "blockers":["FNB_PRODUCTION_STATIC_OWNER_NOT_AUTHORIZED"]}
    grade=evaluate(now=t,observed_day=existing)
    assert grade["race_count"]==12
    assert grade["listed_runner_count"]==130
    assert grade["theoretical_29_index_cells"]==3770
    assert grade["production_race_dispatches"]==0
    assert grade["registered_oos_increment"]==0
    assert grade["source_license_and_signed_official_raw_verified"] is False
    assert grade["signed_final_count"]==0
    assert grade["owner_scope_authorized"] is False
    assert grade["dated_approval_present"] is False
    assert grade["races"][0]["prestart_countdown_seconds"]==118*60
    assert grade["races"][0]["official_prediction_cutoff"] is None
    assert grade["races"][0]["fnb_current_track_bias"]=="UNVERIFIED_CURRENT"
    assert all(x["actual_active_runners"] is None for x in grade["races"])
    assert all(x["actual_full29_calculated_count"] is None for x in grade["races"])
    assert all(x["recommendation_pfs"] is None for x in grade["races"])
    assert all(x["verified_formal_no_bet"] is False for x in grade["races"])
    assert grade["receipt_sha256"]==evaluate(now=t,observed_day=existing)["receipt_sha256"]


def test_r11_late_observation_is_diagnostic_not_backdated_prestart_success():
    after=datetime(2026,11,2,15,0,tzinfo=JST)
    grade=evaluate(now=after)
    assert grade["races"][0]["status"]=="POSTSTART_DIAGNOSTIC_ONLY_NOT_RETROACTIVE_PRESTART"
    assert grade["races"][1]["status"]=="PRESTART_WINDOW_NOT_FORMALLY_AUTHORIZED"
    assert grade["races"][0]["recipient_delivery_ack"] is None
    assert grade["races"][0]["recommendation_pfs"] is None


def test_r11_timezone_must_be_aware():
    import pytest
    with pytest.raises(ValueError,match="FNB_OBSERVATION_TIMEZONE_REQUIRED"):
        evaluate(now=datetime(2026,11,2,12,50))
