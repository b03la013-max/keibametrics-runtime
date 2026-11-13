"""FNB R9 60R repository-only status matrix never invents signed results."""
from copy import deepcopy

from runtime.local_fnb_r9_60r_observation import summarize


def _day(date):
    return {"race_date":date, "races":[{
        "race_no":n,"scheduled_post_at":None,
        "cutoff_disposition":"OFFICIAL_CUTOFF_NOT_PROVEN",
        "source_checkpoint":"NOT_OBSERVED_IN_REPO",
        "formal_checkpoint":"NOT_OBSERVED_IN_REPO",
        "result_checkpoint":"NOT_OBSERVED_IN_REPO",
        "actual_29_index_calculation":"NOT_VERIFIED",
        "krs_5000":"NOT_VERIFIED",
        "signed_final_prestart":"NOT_VERIFIED",
        "delivery_recipient_ack":"NOT_VERIFIED",
        "no_bet_proven":False
    } for n in range(1,13)]}


def test_r9_60r_horizon_complete_but_never_qualified_as_live_or_no_bet():
    days=[_day(f"2026-11-{n:02}") for n in range(2,7)]
    result=summarize(days)
    assert result["race_count"]==60
    assert result["status"]=="REPOSITORY_60R_OBSERVATION_COMPLETE_NOT_LIVE"
    assert all(x["recommendation_pfs"] is None for x in result["races"])
    assert all(not x["no_bet_proven"] for x in result["races"])
    assert result["new_dispatches"]==0
    assert result["registered_oos_increment"]==0
    assert result["full_29_current_day_calculation_verified"] is False


def test_r9_five_day_scope_fails_on_duplicate_or_missing_race():
    original=[_day(f"2026-11-{n:02}") for n in range(2,7)]
    duplicate=deepcopy(original)
    duplicate[4]["race_date"]="2026-11-05"
    assert "DAY_IDENTITY_DUPLICATE_OR_MISSING" in summarize(duplicate)["errors"]
    short=deepcopy(original)
    short[0]["races"].pop()
    assert summarize(short)["status"]=="REPOSITORY_60R_OBSERVATION_INCOMPLETE"
