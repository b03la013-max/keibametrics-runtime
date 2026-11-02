"""R12 race-specific current changes. Fetched absence is NOT a no-change guarantee.

Optional saved official day-wide notices are scoped by race. Other-race notices
never block this race. Only typed target notices require actual runner and
jockey/revised-post consistency. This does not authorize unsigned SOURCE.
"""
from __future__ import annotations

import re

PROFILE="KM-FNB-R12-OFFICIAL-DAY-CHANGES-SCOPE-v1"

def reconcile(source, request, day_list=None):
    context=source.get("source_race_context") or {}
    race=request.get("race") or {}
    day=str(request.get("race_date") or race.get("race_date") or "").replace("/","-")
    no=request.get("race_no") or race.get("race_no")
    if request.get("venue_id")!="FNB":
        return {"status":"NOT_APPLICABLE_NON_FNB"}
    if (context.get("venue_id")!="FNB" or
            str(context.get("race_date") or "").replace("/","-")!=day or
            context.get("race_no")!=no or type(no) is not int or not 1<=no<=12):
        raise ValueError("FNB_CHANGE_RACE_CONTEXT_MISMATCH")
    base={"profile":PROFILE, "source_signature_verified_here":False,
          "license_verified_here":False, "no_change_guarantee":False,
          "prestart_delivery_pass":False}
    if day_list is None:
        return {**base,"status":"OFFICIAL_CHANGE_LIST_NOT_OBSERVED_UNKNOWN",
                "target_notices":[],"other_race_notice_count":None}
    if (not isinstance(day_list,dict)
            or day_list.get("venue_id")!="FNB"
            or day_list.get("race_date")!=day
            or day_list.get("source_authority")!="NAR_OFFICIAL"
            or day_list.get("official_day_list_fetched") is not True
            or day_list.get("all_notice_rows_parsed") is not True
            or not isinstance(day_list.get("notices"),list)):
        raise ValueError("FNB_CHANGE_LIST_COVERAGE_OR_IDENTITY_INVALID")
    own,other=[],[]
    seen=set()
    for item in day_list["notices"]:
        if not isinstance(item,dict):
            raise ValueError("FNB_CHANGE_NOTICE_OBJECT_REQUIRED")
        rn=item.get("race_no")
        kind=item.get("event_type")
        if (type(rn) is not int or not 1<=rn<=12 or
                kind not in {"JOCKEY_CHANGE","CANCELLED","EXCLUDED","POST_TIME_CHANGE"}):
            raise ValueError("FNB_CHANGE_NOTICE_TYPE_OR_RACE_INVALID")
        horse=item.get("horse_no")
        if kind!="POST_TIME_CHANGE" and (type(horse) is not int or not 1<=horse<=20):
            raise ValueError("FNB_CHANGE_HORSE_NUMBER_INVALID")
        ident=(rn,kind,horse)
        if ident in seen:
            raise ValueError("FNB_CHANGE_DUPLICATE_REQUIRES_REVISION")
        seen.add(ident)
        (own if rn==no else other).append(item)
    declared=(source.get("declared_runner_universe") or {}).get("runners") or []
    active=(source.get("official_runner_universe") or
            source.get("active_runner_universe") or {}).get("runners") or []
    declared_by={h.get("horse_no"):h for h in declared if isinstance(h,dict)}
    active_by={h.get("horse_no"):h for h in active if isinstance(h,dict)}
    for item in own:
        kind=item["event_type"]
        horse=item.get("horse_no")
        if kind=="POST_TIME_CHANGE":
            if (not isinstance(item.get("new_post_at"),str)
                    or request.get("scheduled_post_at")!=item["new_post_at"]):
                raise ValueError("FNB_CHANGE_POST_TIME_NOT_REFLECTED")
        elif horse not in declared_by:
            raise ValueError("FNB_CHANGE_HORSE_NOT_DECLARED")
        elif kind in {"CANCELLED","EXCLUDED"}:
            if horse in active_by:
                raise ValueError("FNB_CHANGE_CANCELLED_HORSE_STILL_ACTIVE")
        else:
            if horse not in active_by:
                raise ValueError("FNB_CHANGE_JOCKEY_ON_INACTIVE_HORSE")
            expected=item.get("new_jockey")
            actual=active_by[horse].get("jockey")
            if (not isinstance(expected,str) or not expected.strip() or
                    not isinstance(actual,str) or not actual.strip() or
                    re.sub(r"\s+","",expected)!=re.sub(r"\s+","",actual)):
                raise ValueError("FNB_CHANGE_JOCKEY_NOT_APPLIED")
    status=("TARGET_KNOWN_CHANGES_RECONCILED" if own else
            "OTHER_RACE_ONLY_NO_KNOWN_TARGET_NOTICE" if other else
            "TARGET_NO_KNOWN_NOTICE_IN_FETCHED_LIST")
    return {**base,"status":status,"target_notices":own,
            "other_race_notice_count":len(other),
            "official_list_complete_as_observed":True}
