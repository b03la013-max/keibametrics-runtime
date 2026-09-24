from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List

from local_candidate_postresult import evaluate, evaluate_candidate_krs_envelope

PROFILE="KM-LOCAL-NUMERICAL-CANDIDATE-POSTRESULT-v0.3-EVIDENCE-ROUTING-20260925"
DESIGN_FREEZE_DATE="2026-09-25"


def _sha(x: Any) -> str:
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def evaluate_v03(
    summary: Dict[str,Any],
    actual_finish_order: List[int],
    *,
    result_available_at: str,
    race_id: str,
    krs_summary: Dict[str,Any]|None=None,
    krs_envelope: Dict[str,Any]|None=None,
    signed_final_binding_valid: bool=False,
) -> Dict[str,Any]:
    s=summary or {}
    if s.get("status")!="FROZEN_PRE_RESULT_NUMERICAL_CANDIDATE_V03_SHADOW":
        raise ValueError("FROZEN_V03_SHADOW_REQUIRED")
    if str(s.get("design_freeze_date") or "")!=DESIGN_FREEZE_DATE:
        raise ValueError("V03_DESIGN_FREEZE_DATE_MISMATCH")
    race_date=str(s.get("race_date") or "")
    future_eligible=bool(race_date>=DESIGN_FREEZE_DATE and s.get("retrospective_replay") is not True)
    arm=s.get("arm") or {}
    base=evaluate(
        arm,actual_finish_order,
        result_available_at=result_available_at,
        candidate_krs_summary=krs_summary or {},
        race_id=race_id,
        arm_label="v0.3-EVIDENCE-ROUTING",
        frozen_pre_result=True,
        calibration_training_race_ids=[],
    )
    # The generic evaluator knows temporal/KRS eligibility. v0.3 additionally
    # rejects pre-design historical replays from Forward OOS admission.
    base["candidate_oos_event_eligible"]=bool(
        base.get("candidate_oos_event_eligible")
        and future_eligible
        and signed_final_binding_valid is True
    )
    base["candidate_is_pre_design_replay"]=not future_eligible
    base["signed_final_binding_valid"]=bool(signed_final_binding_valid)
    coverage_rows=(s.get("arm") or {}).get("runner_component_coverage") or {}
    coverage_values=[
        float((row or {}).get("real_component_coverage_ratio"))
        for row in coverage_rows.values()
        if isinstance((row or {}).get("real_component_coverage_ratio"),(int,float))
    ]
    missing_counts=[
        int((row or {}).get("missing_component_count"))
        for row in coverage_rows.values()
        if isinstance((row or {}).get("missing_component_count"),int)
    ]
    base["mean_component_coverage_ratio"]=(None if not coverage_values else sum(coverage_values)/len(coverage_values))
    base["mean_missing_component_count"]=(None if not missing_counts else sum(missing_counts)/len(missing_counts))
    base["component_coverage_runner_count"]=len(coverage_values)

    krs_post=None
    if isinstance(krs_envelope,dict):
        try:
            krs_post=evaluate_candidate_krs_envelope(
                arm,krs_envelope,actual_finish_order,race_id=race_id,arm_label="V03"
            )
        except Exception as e:
            krs_post={"status":"POSTRESULT_KRS_EVAL_FAIL","error_type":type(e).__name__,"error":str(e),"production_effect":"NONE"}
    if isinstance(krs_post,dict):
        ev=krs_post.get("post_result_evaluation") or {}
        base["candidate_krs_utility_class"]=ev.get("classification") or krs_post.get("utility_class")
        base["candidate_krs_rescue_count"]=ev.get("rescue_count")
        base["candidate_krs_support_count"]=ev.get("support_count")
        base["candidate_krs_miss_count"]=len(ev.get("misses") or []) if isinstance(ev.get("misses"),list) else None

    out={
        "profile":PROFILE,
        "race_id":race_id,
        "race_date":race_date,
        "result_available_at":result_available_at,
        "actual_top3":[str(x) for x in actual_finish_order[:3]],
        "v03_shadow_sha256":s.get("sha256"),
        "arm":base,
        "candidate_krs_postresult":krs_post,
        "design_freeze_date":DESIGN_FREEZE_DATE,
        "future_oos_candidate":future_eligible,
        "signed_final_binding_valid":bool(signed_final_binding_valid),
        "production_effect":"NONE",
        "automatic_promotion":False,
        "note":"v0.3 was designed after 2026-09-24 outcomes. Any replay dated before 2026-09-25 is diagnostic only and can never enter its Forward OOS tracker."
    }
    out["sha256"]=_sha(out)
    return out
