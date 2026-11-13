"""Five-day FNB 60R read-only evidence matrix, not an execution scheduler.

The externally published meeting dates may be 2026-11-02..06, but this code
does NOT establish current official races, Source licenses, live Runtime health
or confirmed recipient delivery. It only inspects existing repo checkpoints.
No worker, Cron, signed artifact or OOS registry is created.
"""
from __future__ import annotations

import argparse
from datetime import date, timedelta, datetime, timezone
import json
from pathlib import Path

from runtime.local_fnb_r6_readonly_acceptance import inspect

PROFILE="KM-FNB-R9-60R-REPOSITORY-ONLY-EVIDENCE-v1"


def summarize(days: list[dict]) -> dict:
    errors=[]
    dates=[]
    races=[]
    for day in days:
        date_key=day.get("race_date")
        if not isinstance(date_key,str) or date_key in dates:
            errors.append("DAY_IDENTITY_DUPLICATE_OR_MISSING")
        dates.append(date_key)
        rows=day.get("races")
        if not isinstance(rows,list) or len(rows)!=12 or sorted(
                row.get("race_no") for row in rows if isinstance(row,dict)
                )!=list(range(1,13)):
            errors.append("DAY_12R_COVERAGE_INVALID:"+str(date_key))
            continue
        for row in rows:
            races.append({
                "race_date":date_key,"race_no":row["race_no"],
                "start_time":row.get("scheduled_post_at"),
                "cutoff_status":row.get("cutoff_disposition"),
                "SOURCE":row.get("source_checkpoint"),
                "FORMAL":row.get("formal_checkpoint"),
                "RESULT":row.get("result_checkpoint"),
                "actual_29_indices":row.get("actual_29_index_calculation"),
                "KRS_5000":row.get("krs_5000"),
                "prestart_final":row.get("signed_final_prestart"),
                "recipient_ack":row.get("delivery_recipient_ack"),
                "no_bet_proven":row.get("no_bet_proven") is True,
                "recommendation_pfs":None})
    if len(days)!=5 or len(races)!=60:
        errors.append("FIVE_DAYS_60R_COHORT_NOT_COMPLETE")
    return {
        "profile":PROFILE,
        "classification":"PRIVATE_RESEARCH_READ_ONLY / NOT_REGISTERED_OOS",
        "status":"REPOSITORY_60R_OBSERVATION_COMPLETE_NOT_LIVE" if not errors
                 else "REPOSITORY_60R_OBSERVATION_INCOMPLETE",
        "dates":dates,"race_count":len(races),"races":races,
        "all_60_verified_prestart_delivery":False,
        "all_60_owner_approval":False,
        "full_29_current_day_calculation_verified":False,
        "signed_source_license_and_signature_verified":False,
        "no_bet_is_not_equivalent_to_unexecuted":True,
        "unsettled_pfs_is_null":True,
        "new_dispatches":0,"new_runtime_posts":0,
        "registered_oos_increment":0,"production_modified":False,
        "errors":errors, "source_scope":
          "EXISTING_GITHUB_REPOSITORY_SNAPSHOT_ONLY_NOT_RUNTIME_OR_PERSONAL_DELIVERY"}


def observe(root: Path, *, start_date: str, now: datetime|None=None) -> dict:
    start=date.fromisoformat(start_date)
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("R9_OBSERVATION_TIMEZONE_REQUIRED")
    days=[inspect(root,(start+timedelta(days=i)).isoformat(),now=now)
          for i in range(5)]
    response=summarize(days)
    response["observed_at"]=now.isoformat()
    response["days"]=[{
        "race_date":x["race_date"],
        "observed_authority":x["authority_manifest_observed"],
        "owner_venues":x["owner_venues"],
        "fnb_static_owner_authorized":x["fnb_static_owner_authorized"],
        "dated_plan_exists_and_valid":x["dated_plan_exists_and_valid"],
        "dated_approval_present":x["dated_approval_present"],
        "numeric_consumption":x["numeric_consumption"],
        "blockers":x["blockers"]} for x in days]
    return response


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",default=".")
    parser.add_argument("--start-date",required=True)
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    report=observe(Path(args.root),start_date=args.start_date)
    target=Path(args.output)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
                      encoding="utf-8")
    print(json.dumps({"status":report["status"],"races":report["race_count"],
                      "output":str(target)},ensure_ascii=False))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
