"""FNB R11 first-day and prequential venue-context temporal guard.

The FNB Venue Canon v2.1 requires current-day track bias UNKNOWN before the
first race and only verified, already-observed results from earlier races may
enter later-race venue context. No coefficients, threshold, role, KRS, ticket
or Capital rules are created here. This validates optional observations only.
"""
from __future__ import annotations

from datetime import date, datetime, timezone

PROFILE="KM-FNB-R11-FIRST-DAY-TEMPORAL-PURITY-v1"


def aware(value):
    t=datetime.fromisoformat(str(value).replace("Z","+00:00"))
    if t.tzinfo is None:
        raise ValueError("FNB_TRACK_OBSERVATION_TIMEZONE_REQUIRED")
    return t.astimezone(timezone.utc)


def verify(*, source_artifact:dict, request:dict):
    race=request.get("race") or {}
    venue=str(race.get("venue_id") or request.get("venue_id") or "").upper()
    if venue!="FNB":
        return {"status":"NOT_APPLICABLE_NON_FNB"}
    context=source_artifact.get("source_race_context") or {}
    day=str(race.get("race_date") or request.get("race_date") or "").replace("/","-")
    num=race.get("race_no") or request.get("race_no")
    if (not day or not isinstance(num,int) or isinstance(num,bool)
            or not 1<=num<=12 or
            context.get("venue_id")!="FNB" or
            str(context.get("race_date") or "").replace("/","-")!=day or
            context.get("race_no")!=num):
        raise ValueError("FNB_DAY_TRACK_RACE_IDENTITY_INVALID")
    date.fromisoformat(day)
    cutoff=aware(request.get("prediction_cutoff"))
    frozen=aware(source_artifact.get("source_freeze_at"))
    if not frozen<cutoff:
        raise ValueError("FNB_TRACK_SOURCE_NOT_PRE_CUTOFF")
    rows=source_artifact.get("fnb_same_day_result_observations")
    if rows is None:
        rows=[]
    if not isinstance(rows,list):
        raise ValueError("FNB_TRACK_OBSERVATIONS_NOT_ARRAY")
    accepted=[]
    for row in rows:
        if not isinstance(row,dict):
            raise ValueError("FNB_TRACK_OBSERVATION_NOT_OBJECT")
        origin=row.get("race_no")
        if type(origin) is not int or origin<1 or origin>=num:
            raise ValueError("FNB_SAME_DAY_RESULT_NOT_PRIOR_RACE")
        if (row.get("race_date")!=day or
                row.get("venue_id")!="FNB" or
                row.get("official_result_verified") is not True or
                row.get("signed_result_receipt_verified") is not True):
            raise ValueError("FNB_TRACK_RESULT_OFFICIAL_LINEAGE_REQUIRED")
        available=aware(row.get("first_observed_at"))
        if available>frozen or available>=cutoff:
            raise ValueError("FNB_TRACK_RESULT_OBSERVED_AFTER_FROZEN")
        if origin in accepted:
            raise ValueError("FNB_TRACK_PRIOR_RESULT_DUPLICATE")
        accepted.append(origin)
    if num==1 and accepted:
        raise ValueError("FNB_R01_CANNOT_HAVE_SAME_DAY_PRIOR_RESULT")
    # First-day or no verified earlier result cannot truthfully claim a
    # measured same-day bias. Official "going" is a different observed fact;
    # do not confuse it with a learned current GCI/TVGCI adjustment.
    venue_context=request.get("venue_prediction_context")
    if venue_context is not None and not isinstance(venue_context,dict):
        raise ValueError("FNB_VENUE_PREDICTION_CONTEXT_INVALID")
    venue_context=venue_context or {}
    if not accepted:
        allowed=("UNVERIFIED_CURRENT","SIGNED_SOURCE_RECHECK_REQUIRED",
                 "UNKNOWN","CURRENT_UNKNOWN","NOT_VERIFIED")
        status=venue_context.get("current_track_state")
        if status is not None and status not in allowed:
            raise ValueError("FNB_FIRST_DAY_BIAS_CLAIM_WITHOUT_PRIOR_OBSERVATION")
        for name in ("current_gci_value","same_day_track_bias_score",
                     "same_day_gci","current_tvgci_value"):
            if venue_context.get(name) is not None:
                raise ValueError("FNB_FIRST_DAY_UNSUPPORTED_CURRENT_BIAS_NUMERIC")
    return {
        "profile":PROFILE,
        "status":("FIRST_RACE_CURRENT_TRACK_BIAS_UNVERIFIED" if num==1 else
                  "TRACK_BIAS_PRIOR_RESULT_OBSERVATIONS_VERIFIED" if accepted
                  else "TRACK_BIAS_CURRENT_UNVERIFIED_NO_SIGNED_PRIOR_RESULTS"),
        "current_track_bias_status":"UNVERIFIED_CURRENT" if not accepted
            else "OBSERVED_PRIOR_RACE_ONLY_NOT_CALIBRATED",
        "race_date":day,"race_no":num,
        "prior_race_results_accepted":sorted(accepted),
        "historical_venue_prior_is_not_same_day_current":True,
        "no_future_or_same_race_results_used":True,
        "automatic_venue_bias_coefficients":False,
        "numerical_mapping_changed":False,
        "prediction_krs_ticket_capital_consumption_authorized":False,
        "source_signature_created":False
    }
