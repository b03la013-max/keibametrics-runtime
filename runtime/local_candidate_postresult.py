from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Set

PROFILE="KM-LOCAL-NUMERICAL-CANDIDATE-POSTRESULT-v0.2-DUAL-20260923"


def _sha(x):
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def _rank(ranking,horse):
    vals=[str(x) for x in ranking]
    try:return vals.index(str(horse))+1
    except ValueError:return None


def evaluate(candidate_summary: Dict[str,Any], actual_finish_order: List[int],
             *, result_available_at: str, candidate_krs_summary: Dict[str,Any]|None=None,
             race_id: str|None=None, arm_label: str|None=None,
             frozen_pre_result: bool|None=None,
             calibration_training_race_ids: Set[str]|List[str]|None=None) -> Dict[str,Any]:
    candidate_summary=candidate_summary or {}
    pred=candidate_summary.get("candidate_static_prediction") or {}
    actual=[str(x) for x in actual_finish_order[:3]]
    if len(actual)!=3:
        raise ValueError("ACTUAL_TOP3_REQUIRED")
    ranking=[str(x) for x in pred.get("ranking") or []]
    if not ranking:
        raise ValueError("CANDIDATE_RANKING_REQUIRED")
    W=set(str(x) for x in pred.get("W") or [])
    P2=set(str(x) for x in pred.get("P2") or [])
    P3=set(str(x) for x in pred.get("P3") or [])
    ranks=[_rank(ranking,x) for x in actual]
    full=candidate_summary.get("candidate_full_numerical_summary") or {}
    krs=candidate_krs_summary or {}
    training=set(str(x) for x in (calibration_training_race_ids or []))
    if frozen_pre_result is None:
        frozen_pre_result=candidate_summary.get("status") in {
            "FROZEN_PRE_RESULT_NUMERICAL_CANDIDATE_SHADOW",
            "FROZEN_PRE_RESULT_NUMERICAL_CANDIDATE_DUAL_SHADOW",
        }
    temporal_oos=bool(
        frozen_pre_result
        and krs.get("status")=="EXECUTED"
        and krs.get("pre_post_complete") is True
        and krs.get("oos_temporal_eligible") is True
        and full.get("production_authority") is False
    )
    in_training=bool(race_id and str(race_id) in training)
    oos=bool(temporal_oos and not in_training)
    out={
      "profile":PROFILE,
      "race_id":race_id,
      "arm_label":arm_label,
      "race_source_snapshot_sha256":candidate_summary.get("source_snapshot_sha256"),
      "candidate_shadow_sha256":candidate_summary.get("sha256"),
      "candidate_prediction_sha256":pred.get("sha256"),
      "candidate_mapping_id":full.get("mapping_id"),
      "result_available_at":result_available_at,
      "actual_top3":actual,
      "winner_rank":ranks[0],
      "second_rank":ranks[1],
      "third_rank":ranks[2],
      "top3_mean_rank":None if any(x is None for x in ranks) else sum(ranks)/3,
      "winner_capture":actual[0] in W,
      "p2_capture":actual[1] in P2,
      "p3_capture":actual[2] in P3,
      "top3_set_capture":all(x in P3 for x in actual),
      "candidate_krs_status":krs.get("status") or "NOT_AVAILABLE",
      "candidate_krs_receipt_sha256":krs.get("receipt_sha256"),
      "candidate_krs_pre_post_complete":krs.get("pre_post_complete"),
      "candidate_oos_temporal_eligible":temporal_oos,
      "candidate_is_calibration_training_race":in_training,
      "candidate_oos_event_eligible":oos,
      "production_effect":"NONE",
      "automatic_promotion":False,
      "result_derived_feature_count":0,
      "note":"Measures a frozen numerical candidate only. Never rewrites Production prediction or same-race features."
    }
    out["sha256"]=_sha(out)
    return out


def evaluate_dual(dual_summary: Dict[str,Any], actual_finish_order: List[int],
                  *, result_available_at: str, race_id: str,
                  dual_krs_summary: Dict[str,Any]|None=None,
                  calibration_training_race_ids: Set[str]|List[str]|None=None) -> Dict[str,Any]:
    dual_summary=dual_summary or {}
    if dual_summary.get("status")!="FROZEN_PRE_RESULT_NUMERICAL_CANDIDATE_DUAL_SHADOW":
        raise ValueError("FROZEN_DUAL_SHADOW_REQUIRED")
    arms=dual_summary.get("arms") or {}
    if not isinstance(arms.get("v0.1"),dict):
        raise ValueError("V01_ARM_REQUIRED")
    krs=dual_krs_summary or {}
    v01=evaluate(
        arms["v0.1"],actual_finish_order,result_available_at=result_available_at,
        candidate_krs_summary=krs.get("v0.1") or krs.get("V01"),
        race_id=race_id,arm_label="v0.1-BASELINE",frozen_pre_result=True,
        calibration_training_race_ids=[]
    )
    v02=None
    if isinstance(arms.get("v0.2"),dict):
        v02=evaluate(
            arms["v0.2"],actual_finish_order,result_available_at=result_available_at,
            candidate_krs_summary=krs.get("v0.2") or krs.get("V02"),
            race_id=race_id,arm_label="v0.2-URW-DAY-CALIBRATED",frozen_pre_result=True,
            calibration_training_race_ids=calibration_training_race_ids
        )
    comparison={
      "v0.2_available":v02 is not None,
      "same_source":bool(v02 and v01.get("race_source_snapshot_sha256")==v02.get("race_source_snapshot_sha256")),
      "winner_rank_gain_v02_vs_v01":None,
      "second_rank_gain_v02_vs_v01":None,
      "third_rank_gain_v02_vs_v01":None,
      "top3_mean_rank_gain_v02_vs_v01":None,
      "winner_capture_delta_v02_vs_v01":None,
      "p2_capture_delta_v02_vs_v01":None,
      "p3_capture_delta_v02_vs_v01":None,
      "top3_set_capture_delta_v02_vs_v01":None,
      "promotion_decision":"NO_AUTOMATIC_PROMOTION",
    }
    if v02 is not None:
        def gain(k):
            a=v01.get(k); b=v02.get(k)
            return None if a is None or b is None else round(float(a)-float(b),6)
        comparison.update({
          "winner_rank_gain_v02_vs_v01":gain("winner_rank"),
          "second_rank_gain_v02_vs_v01":gain("second_rank"),
          "third_rank_gain_v02_vs_v01":gain("third_rank"),
          "top3_mean_rank_gain_v02_vs_v01":gain("top3_mean_rank"),
          "winner_capture_delta_v02_vs_v01":int(bool(v02["winner_capture"]))-int(bool(v01["winner_capture"])),
          "p2_capture_delta_v02_vs_v01":int(bool(v02["p2_capture"]))-int(bool(v01["p2_capture"])),
          "p3_capture_delta_v02_vs_v01":int(bool(v02["p3_capture"]))-int(bool(v01["p3_capture"])),
          "top3_set_capture_delta_v02_vs_v01":int(bool(v02["top3_set_capture"]))-int(bool(v01["top3_set_capture"])),
        })
    out={
      "profile":PROFILE,
      "race_id":race_id,
      "result_available_at":result_available_at,
      "actual_top3":[str(x) for x in actual_finish_order[:3]],
      "dual_shadow_sha256":dual_summary.get("sha256"),
      "arms":{"v0.1":v01,"v0.2":v02},
      "comparison":comparison,
      "oos_policy":{
        "v0.1_baseline_event_eligible":v01.get("candidate_oos_event_eligible"),
        "v0.2_event_eligible":None if v02 is None else v02.get("candidate_oos_event_eligible"),
        "v0.2_training_race":None if v02 is None else v02.get("candidate_is_calibration_training_race"),
        "automatic_promotion":False,
        "minimum_future_oos_events_before_human_review":30,
      },
      "production_effect":"NONE",
    }
    out["sha256"]=_sha(out)
    return out
