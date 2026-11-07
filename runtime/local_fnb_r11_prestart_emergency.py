"""FNB R11: emergency READ-ONLY prestart readiness using the official public program.

This is a published schedule/count observation, not fresh licensed NAR raw,
a Signed SOURCE, Active runner validation, KRS, FINAL, NO-BET, or Delivery.
FNB venue authority cannot grant numerical consumer / common Capital scope.
No network, cron, worker, write-to-main, signature, or purchase operation.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path

PROFILE="KM-FNB-R11-20261102-EMERGENCY-PRESTART-READINESS-v1"
JST=timezone(timedelta(hours=9))
DAY="2026-11-02"
OFFICIAL_MENU_URL=("https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/"
                   "RaceList?k_babaCode=19&k_raceDate=2026%2F11%2F02")
# Source: NAR 2026-11-02 FNB daily RaceList and operator 2026-10-29
# published schedule. The counts are LISTED, never guaranteed Active.
_ROWS=[
 (1,"14:45",1200,12,"２歳三"),
 (2,"15:15",1200,12,"２歳二"),
 (3,"15:45",1500,7,"船橋デビュー馬限定未勝利選抜馬２歳"),
 (4,"16:20",1200,9,"Ｃ２二 三 四ウ"),
 (5,"16:50",1200,9,"Ｃ２二 三 四イ"),
 (6,"17:20",1500,11,"谷津干潟特別３歳選抜馬"),
 (7,"17:55",1200,11,"勝ち枡杯Ｃ１六 七"),
 (8,"18:30",1500,12,"馬い！卵はサンサンエッグ津田Ｃ２二 三 四"),
 (9,"19:05",1200,11,"ユーチャリススプリントＢ３選抜馬イ"),
 (10,"19:40",1200,12,"カサブランカスプリントＢ３選抜馬ア"),
 (11,"20:15",1600,13,"霜月特別Ｂ３二"),
 (12,"20:50",1500,11,"ＪＢＣ２０２６金沢・門別まであＣ１六 七"),
]


def _hash(data):
    return hashlib.sha256(json.dumps(data,ensure_ascii=False,sort_keys=True,
        separators=(",",":"),allow_nan=False).encode("utf-8")).hexdigest()


def program():
    rows=[{"venue":"FNB","race_date":DAY,"race_no":n,
           "scheduled_post_at":DAY+"T"+clock+":00+09:00",
           "declared_runner_count":count,"required_index_cells_theoretical":count*29,
           "distance_m":distance,"surface":"dirt","direction":"left",
           "race_title":title,"source_menu_url":OFFICIAL_MENU_URL}
          for n,clock,distance,count,title in _ROWS]
    if len(rows)!=12 or [x["race_no"] for x in rows]!=list(range(1,13)):
        raise ValueError("OFFICIAL_DAY_12_RACE_LIST_REQUIRED")
    if sum(r["declared_runner_count"] for r in rows)!=130:
        raise ValueError("OFFICIAL_DAY_130_LISTED_UNIVERSE_INVALID")
    if sum(r["required_index_cells_theoretical"] for r in rows)!=3770:
        raise ValueError("FNB_29_CELL_THEORETICAL_COUNT_MISMATCH")
    if any(a["scheduled_post_at"]>=b["scheduled_post_at"] for a,b in zip(rows,rows[1:])):
        raise ValueError("FNB_OFFICIAL_POSTS_NOT_STRICTLY_ORDERED")
    return rows


def evaluate(*, now, observed_day=None):
    """Return 12 distinct terminal diagnoses without simulating prediction."""
    if now.tzinfo is None:
        raise ValueError("FNB_OBSERVATION_TIMEZONE_REQUIRED")
    now_jst=now.astimezone(JST)
    from runtime.local_fnb_r6_readonly_acceptance import inspect
    day=observed_day if observed_day is not None else {}
    blockers=list(day.get("blockers") or [])
    rows=[]
    for item in program():
        post=datetime.fromisoformat(item["scheduled_post_at"])
        remaining=(post-now_jst).total_seconds()
        before_post=remaining>0
        # Existing formal cutoff must be from a trusted dated plan+approval.
        # Never equate pre-start with being earlier than a made-up -5min.
        official_cutoff=None
        status=("PRESTART_WINDOW_NOT_FORMALLY_AUTHORIZED" if before_post
                else "POSTSTART_DIAGNOSTIC_ONLY_NOT_RETROACTIVE_PRESTART")
        rows.append({
            **item,
            "prestart_countdown_seconds":int(remaining),
            "scheduled_post_in_future":before_post,
            "official_prediction_cutoff":official_cutoff,
            "actual_active_runners":None,
            "actual_full29_calculated_count":None,
            "actual_ruled_neutral_count":None,
            "actual_ruled_hold_count":None,
            "actual_unknown_feature_count":None,
            "eligible_frozen_baseline_and_candidate":False,
            "baseline_krs_5000_seed1_receipt":None,
            "candidate_krs_5000_seed1_receipt":None,
            "baseline_three_method_trees":None,
            "candidate_three_method_trees":None,
            "signed_final_receipt":None,
            "recipient_delivery_ack":None,
            "verified_formal_no_bet":False,
            "recommendation_pfs":None,
            "actual_purchase_pfs":None,
            "first_material_failure":"OWNER_SCOPE_OR_SOURCE_ADMISSION_UNPROVEN"
               if before_post else "PRESTART_FINAL_NOT_PROVEN_BEFORE_POST",
            "status":status,
            "fnb_current_track_bias":"UNVERIFIED_CURRENT" if item["race_no"]==1
               else "UNKNOWN_UNTIL_EARLIER_OFFICIAL_RESULT_OBSERVATION",
            "next_result_may_update_only_later_races":True,
        })
    report={
        "profile":PROFILE,
        "classification":"PRIVATE_READ_ONLY_PROGRAM_PREFLIGHT_NOT_REGISTERED_OOS",
        "venue":"FNB","date":DAY,"observed_at":now_jst.isoformat(),
        "official_program_url":OFFICIAL_MENU_URL,
        "official_program_sources":[OFFICIAL_MENU_URL,
            "https://blog.f-keiba.com/info/2026/10/88-8fa8.html"],
        "race_count":12,
        "listed_runner_count":130,
        "theoretical_29_index_cells":3770,
        "actual_runner_count":None,
        "actual_calculated_cells":None,
        "current_authority_observed":day.get("authority_manifest_observed"),
        "owner_scope_authorized":day.get("fnb_static_owner_authorized") is True,
        "dated_plan_valid":day.get("dated_plan_exists_and_valid") is True,
        "dated_approval_present":day.get("dated_approval_present") is True,
        "numerical_consumption":day.get("numeric_consumption"),
        "repository_blockers":blockers,
        "source_license_and_signed_official_raw_verified":False,
        "production_race_dispatches":0,
        "registered_oos_increment":0,
        "horse_29_predictions":None,
        "krs_runs":0,
        "signed_final_count":0,
        "user_visible_full_ticket_delivery_pass":False,
        "pfs":None,
        "races":rows
    }
    report["receipt_sha256"]=_hash(report)
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",default=".")
    p.add_argument("--output",required=True)
    args=p.parse_args()
    from runtime.local_fnb_r6_readonly_acceptance import inspect
    root=Path(args.root)
    now=datetime.now(timezone.utc)
    live=inspect(root,DAY,now=now)
    result=evaluate(now=now,observed_day=live)
    out=Path(args.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":"FNB_READONLY_PREFLIGHT_12R",
                     "count":result["race_count"],"listed":result["listed_runner_count"],
                     "cells":result["theoretical_29_index_cells"],
                     "owner_scope":result["owner_scope_authorized"],
                     "signed_final_count":result["signed_final_count"],
                     "receipt_sha256":result["receipt_sha256"]},ensure_ascii=False))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
