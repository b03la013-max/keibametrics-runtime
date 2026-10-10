"""JRA verified zero-bet result settlement and post-result learning.

A blocked Production Full20 can legitimately terminate NO_BET, not a
fabricated Final. This module closes the zero-exposure result branch
without counting it as a prediction or capital/PFS sample.
"""
from __future__ import annotations
from datetime import datetime
from hashlib import sha256
import json
from jra_production_no_bet_terminal import verify_no_bet_terminal

PROFILE = "KM-JRA-NO-BET-POSTRESULT-LEARNING-v1-20261010"

class JRANoBetLearningError(ValueError):
    pass

def _hash(obj):
    return sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()

def _time(value):
    try:
        d=datetime.fromisoformat(str(value).replace("Z","+00:00"))
        return d if d.tzinfo is not None else None
    except (TypeError,ValueError):
        return None

def build_no_bet_learning(terminal,official_result,*,race_no,acquired_at,
                          result_source_snapshot_sha256,official_capture_verified=False):
    """Zero investment and payout are recorded; PFS is undefined, not 100%.
    
    The external caller must independently verify the official JRA raw source
    and its GitHub OIDC artifact attestation before setting the verified flag.
    """
    if official_capture_verified is not True:
        raise JRANoBetLearningError("OFFICIAL_POSTRESULT_CAPTURE_NOT_VERIFIED")
    try:
        decision=verify_no_bet_terminal(terminal,require_live=True)
    except ValueError as exc:
        raise JRANoBetLearningError("NO_BET_TERMINAL_INVALID:"+str(exc)) from exc
    if not (isinstance(official_result,dict)
            and official_result.get("official") is True
            and official_result.get("result_derived") is True
            and official_result.get("race_no") == race_no):
        raise JRANoBetLearningError("OFFICIAL_RESULT_IDENTITY_INVALID")
    if not (isinstance(result_source_snapshot_sha256,str)
            and len(result_source_snapshot_sha256)==64
            and all(c in "0123456789abcdef" for c in result_source_snapshot_sha256)
            and official_result.get("source_snapshot_sha256")==result_source_snapshot_sha256):
        raise JRANoBetLearningError("OFFICIAL_RESULT_SNAPSHOT_UNBOUND")
    announced=official_result.get("sha256")
    raw_parsed={k:v for k,v in official_result.items()
                if k not in ("sha256","race_no","source_snapshot_sha256")}
    if not announced or announced!=_hash(raw_parsed):
        raise JRANoBetLearningError("OFFICIAL_RESULT_CONTENT_HASH_INVALID")
    taken=_time(acquired_at)
    decided=_time(terminal.get("created_at"))
    if not taken or not decided or taken<=decided:
        raise JRANoBetLearningError("POSTRESULT_CHRONOLOGY_INVALID")
    results=official_result.get("runners")
    if not isinstance(results,list) or len(results)<3:
        raise JRANoBetLearningError("OFFICIAL_RESULT_UNIVERSE_INVALID")
    seen=set()
    finish={}
    for row in results:
        if not isinstance(row,dict):
            raise JRANoBetLearningError("OFFICIAL_RESULT_ROW_BAD")
        rid=str(row.get("runner_id") or "")
        pos=row.get("finish")
        if not rid or rid in seen or rid not in terminal["index_universe"]:
            raise JRANoBetLearningError("OFFICIAL_RESULT_RUNNER_MISMATCH")
        if type(pos) is not int or pos<1 or pos in finish:
            raise JRANoBetLearningError("OFFICIAL_RESULT_FINISH_INVALID")
        seen.add(rid); finish[pos]=rid
    if any(pos not in finish for pos in (1,2,3)):
        raise JRANoBetLearningError("OFFICIAL_TOP3_INCOMPLETE")
    top3=[finish[pos] for pos in (1,2,3)]
    obj={
        "profile":PROFILE,
        "race_id":terminal["race_id"],
        "family_id":"JRA",
        "decision_lineage_sha256":terminal["sha256"],
        "signed_pre_race_source_receipt_sha256":terminal["signed_source_receipt_sha256"],
        "post_race_official_snapshot_sha256":result_source_snapshot_sha256,
        "post_race_official_detail_sha256":announced,
        "post_race_official_acquired_at":taken.isoformat(),
        "official_top3":top3,
        "official_finish_count":len(results),
        "decision":"NO_BET",
        "reason":terminal["decision_reason"],
        "status":"ZERO_EXPOSURE_RESULT_RECORDED",
        "final_prediction_existed":False,
        "pre_krs_executed":False,
        "krs_executed":False,
        "signed_final_verified":False,
        "ticket_count":0,
        "investment":0,
        "payout":0,
        "profit_loss":0,
        "pfs":None,
        "eligible_for_production_prediction_kpi":False,
        "eligible_for_market_superiority_promotion":False,
        "learning_class":"EVIDENCE_AVAILABILITY_AND_OPPORTUNITY_COST_ONLY",
        "first_blocked_stage":terminal.get("first_blocked_stage"),
        "terminal_index_count":decision["terminal_index_count"],
        "base_calculated_count":decision["calculated_base_count"],
        "base_held_count":decision["held_base_count"],
        "derived_held_count":decision["held_derived_count"],
        "production_effect":"NONE",
    }
    obj["sha256"]=_hash(obj)
    return obj
