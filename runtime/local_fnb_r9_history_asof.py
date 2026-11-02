"""Prevent FNB horse-history information from crossing prediction as-of.

This is a source-order and anti-hindsight correctness preflight ONLY.
It makes no numerical-policy change and grants no SOURCE licence or FNB Owner.
Undated history remains explicitly counted UNKNOWN, never fabricated as a
dated start. A post-race or same-race historical performance is a hard HOLD.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
import re

PROFILE="KM-FNB-R9-HISTORICAL-START-ASOF-v1"


def _when(value):
    if not isinstance(value,str):
        return None
    match=re.fullmatch(r"(\d{2})[./](\d{1,2})[./](\d{1,2})",value.strip())
    if match:
        y,m,d=map(int,match.groups())
        try:
            return date(2000+y,m,d)
        except ValueError:
            return None
    try:
        return date.fromisoformat(value.strip().replace("/","-"))
    except ValueError:
        return None


def _instant(value):
    t=datetime.fromisoformat(str(value).replace("Z","+00:00"))
    if t.tzinfo is None:
        raise ValueError("FNB_SOURCE_ASOF_NAIVE_TIMESTAMP")
    return t.astimezone(timezone.utc)


def assert_result_blind(compiled, source_artifact, request):
    if request.get("venue_id")!="FNB":
        return {"status":"NOT_APPLICABLE_NON_FNB","rejected":False}
    day=date.fromisoformat(str(request["race_date"]))
    freeze=_instant(source_artifact["source_freeze_at"])
    cutoff=_instant(request["prediction_cutoff"])
    if not freeze<cutoff:
        raise ValueError("FNB_SOURCE_FREEZE_NOT_PRE_CUTOFF")
    runners=compiled.get("runners")
    expected=request.get("runners")
    if not isinstance(runners,list) or not isinstance(expected,list):
        raise ValueError("FNB_HISTORICAL_RUNNER_LIST_REQUIRED")
    expected_ids={str(r.get("runner_id")) for r in expected}
    actual_ids={str(r.get("runner_id")) for r in runners}
    if not expected_ids or expected_ids!=actual_ids or len(runners)!=len(expected):
        raise ValueError("FNB_HISTORICAL_UNIVERSE_MISMATCH")
    observed=0
    undated=0
    for runner in runners:
        raw=runner.get("raw_candidate_evidence")
        if not isinstance(raw,dict):
            raise ValueError("FNB_HISTORICAL_RAW_PER_RUNNER_MISSING")
        fetched=_instant(raw.get("race_card_fetched_at"))
        if fetched>freeze or fetched>=cutoff:
            raise ValueError("FNB_HISTORICAL_RAW_OBSERVED_AFTER_FREEZE")
        dates=[]
        for run in raw.get("starts") or []:
            when=_when(run.get("date")) if isinstance(run,dict) else None
            if when is None:
                undated+=1
                continue
            observed+=1
            if when>=day:
                raise ValueError("FNB_FUTURE_OR_SAME_RACE_HISTORICAL_START")
            if when>fetched.date():
                raise ValueError("FNB_HISTORICAL_START_AFTER_SOURCE_OBSERVATION")
            dates.append(when)
        if any(a<b for a,b in zip(dates,dates[1:])):
            raise ValueError("FNB_HISTORY_NOT_NEWEST_FIRST")
    return {"profile":PROFILE, "status":"PRE_RACE_DATED_HISTORY_CHECKED",
            "runners":len(runners),"dated_starts":observed,
            "undated_starts_unknown":undated,
            "post_result_start_used":False,
            "history_score_formula_changed":False,
            "independent_source_license":False,
            "production_numeric_consumer_granted":False}
