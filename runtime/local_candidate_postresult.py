from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Set

from krs_prediction_utility import build_krs_prediction_utility, evaluate_against_result

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


def evaluate_candidate_krs_envelope(candidate_summary: Dict[str,Any], envelope: Dict[str,Any],
                                    actual_finish_order: List[int], *, race_id: str,
                                    arm_label: str) -> Dict[str,Any]:
    candidate_summary=candidate_summary or {}
    pred=candidate_summary.get("candidate_static_prediction") or {}
    ranking=[str(x) for x in (pred.get("ranking") or [])]
    roles=pred.get("roles") or {}
    scores={str(x.get("runner_id")):x for x in (pred.get("runner_scores") or []) if isinstance(x,dict)}
    if not ranking:
        raise ValueError("CANDIDATE_RANKING_REQUIRED_FOR_KRS_POSTRESULT")
    art=(envelope or {}).get("artifact") or {}
    raw=art.get("raw_output")
    if not isinstance(raw,dict):
        raise ValueError("CANDIDATE_KRS_RAW_OUTPUT_MISSING")
    runners=[]
    for rid in ranking:
        row=scores.get(rid) or {}
        runners.append({
          "runner_id":rid,
          "name":row.get("name") or "",
          "static_roles":[str(x) for x in (roles.get(rid) or roles.get(str(rid)) or [])],
        })
    req={
      "race_id":race_id+"-"+arm_label+"-KRS-POSTRESULT",
      "runners":runners,
      "static_prediction":{"roles":{str(k):[str(x) for x in v] for k,v in roles.items()}},
      "role_registry":[],
      "pair_dispositions":[],
      "third_dispositions":[],
    }
    utility=build_krs_prediction_utility(req,{"status":"EXECUTED","output":raw})
    evaluation=evaluate_against_result(utility,[int(x) for x in actual_finish_order[:3]],static_ranking=ranking)
    out={
      "arm_label":arm_label,
      "candidate_krs_receipt_sha256":(envelope or {}).get("receipt_sha256"),
      "candidate_krs_output_sha256":art.get("output_sha256"),
      "candidate_krs_actual_run_count":art.get("actual_run_count"),
      "utility_sha256":utility.get("sha256"),
      "utility_class":utility.get("utility_class"),
      "post_result_evaluation":evaluation,
      "production_effect":"NONE",
      "candidate_ticket_activation":"NOT_IMPLEMENTED",
      "note":"KRS rescue/support is measured against frozen candidate static roles only; no candidate ticket PFS is inferred."
    }
    out["sha256"]=_sha(out)
    return out

def evaluate_dual(dual_summary: Dict[str,Any], actual_finish_order: List[int],
                  *, result_available_at: str, race_id: str,
                  dual_krs_summary: Dict[str,Any]|None=None,
                  calibration_training_race_ids: Set[str]|List[str]|None=None,
                  dual_krs_envelopes: Dict[str,Any]|None=None) -> Dict[str,Any]:
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
    krs_post={"v0.1":None,"v0.2":None}
    envs=dual_krs_envelopes or {}
    try:
        if isinstance(envs.get("v0.1"),dict):
            krs_post["v0.1"]=evaluate_candidate_krs_envelope(
                arms["v0.1"],envs["v0.1"],actual_finish_order,race_id=race_id,arm_label="V01"
            )
    except Exception as e:
        krs_post["v0.1"]={"status":"POSTRESULT_KRS_EVAL_FAIL","error_type":type(e).__name__,"error":str(e),"production_effect":"NONE"}
    try:
        if v02 is not None and isinstance(envs.get("v0.2"),dict):
            krs_post["v0.2"]=evaluate_candidate_krs_envelope(
                arms["v0.2"],envs["v0.2"],actual_finish_order,race_id=race_id,arm_label="V02"
            )
    except Exception as e:
        krs_post["v0.2"]={"status":"POSTRESULT_KRS_EVAL_FAIL","error_type":type(e).__name__,"error":str(e),"production_effect":"NONE"}

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
      "candidate_krs_postresult":krs_post,
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

# Existing LOCAL post-result owner also owns forward research capture/settlement.
# Shared evaluator; separate Family ledger keys prevent JRA/LOCAL/BAN pooling.
def _forward_protocol():
    from pathlib import Path
    return json.loads(Path('research/utility/forward_protocol.json').read_text())

def _definition_hashes():
    from pathlib import Path
    import hashlib
    files=_forward_protocol().get('definition_files') or []
    return {p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in files}

def _safe_forward_key(family,race):
    import re
    if family not in _forward_protocol()['family_cohorts'] or not re.fullmatch(r'[A-Za-z0-9_-]+',race):
        raise ValueError('UNSAFE_FAMILY_OR_RACE_KEY')

def _forward_dt(x):
    from datetime import datetime
    return datetime.fromisoformat(str(x).replace('Z','+00:00'))

def build_forward_capture(request, final, utility, *, generated_at, candidate=None, classification='FORWARD', artifact_inventory=None):
    from pfs_grand_review import capital_arms
    protocol=_forward_protocol();art=final.get('artifact') or {};receipt=final.get('receipt') or {}
    from pathlib import Path
    from local_numerical_authority_gate import assess
    authority=assess()
    family=request.get('family_id','LOCAL');rid=request['race_id'];post=request['scheduled_post_at']
    _safe_forward_key(family,rid)
    if classification not in {'FORWARD','MECHANICAL_ACCEPTANCE'}:raise ValueError('CLASSIFICATION_REQUIRED')
    if _definition_hashes()!=protocol.get('definition_sha256'):raise ValueError('DEFINITION_NOT_PREREGISTERED')
    if Path('runtime/results',rid+'.json').exists() or Path('runtime/executions',request['execution_id'],'RESULT','LATEST.json').exists():raise ValueError('RESULT_ALREADY_STORED')
    if family not in protocol['family_cohorts']:raise ValueError('FAMILY_NOT_REGISTERED')
    if receipt.get('race_id')!=rid or receipt.get('status')!='PASS' or not final.get('signature'):raise ValueError('SIGNED_FINAL_REQUIRED')
    if _forward_dt(generated_at)>=_forward_dt(post):raise ValueError('NOT_PRE_RESULT')
    if classification=='FORWARD' and _forward_dt(generated_at)<_forward_dt(protocol['activation_at']):raise ValueError('PRE_ACTIVATION_NOT_OOS')
    if request.get('temporal_mode')!='FORMAL-PRE-RACE':raise ValueError('POST_START_NOT_OOS')
    if not utility or not utility.get('summary'):raise ValueError('FROZEN_KRS_UTILITY_REQUIRED')
    if request.get('family_id','LOCAL')=='LOCAL' and not candidate:raise ValueError('FROZEN_CANDIDATE_REQUIRED')
    source=art.get('source_snapshot_sha256')
    if not source:raise ValueError('SOURCE_HASH_REQUIRED')
    if candidate and candidate.get('race_source_snapshot_sha256') not in {None,source}:raise ValueError('CANDIDATE_SOURCE_MISMATCH')
    frozen_utility=(art.get('final_prediction_package') or {}).get('krs_prediction_utility_shadow')
    if frozen_utility is not None and frozen_utility!=utility:raise ValueError('KRS_FINAL_BINDING_MISMATCH')
    if _forward_dt(art['final_freeze_timestamp'])>_forward_dt(generated_at):raise ValueError('FINAL_NOT_YET_FROZEN')
    # Preserve the same baseline, never recompute predictions after RESULT.
    budget=sum(t['stake'] for t in (art.get('final_ticket') or {}).get('tickets') or [])
    try:
        capital=capital_arms(final,budget,request=request,generated_at=generated_at,scheduled_post_at=post)
    except ValueError as error:
        capital={'status':'HOLD_CAPITAL_ONLY','arms':{},'production_comparable_equal_spend':False,'reason':str(error)}
    obj={'profile':protocol['version'],'family_id':family,'race_id':rid,'execution_id':request['execution_id'],
         'classification':classification,'generated_at':generated_at,'scheduled_post_at':post,
         'source_sha256':source,'final_basis_sha256':_sha(final),'final_receipt_sha256':final.get('receipt_sha256'),'runner_universe_sha256':_sha(request.get('runners')),
         'protocol_sha256':_sha(protocol),'definition_sha256':_definition_hashes(),'static_prediction':request.get('static_prediction') or {},
         'krs_utility':utility,'candidate':candidate,'capital':capital,'artifact_inventory':artifact_inventory or {},
         'authority_status':['NUMERICAL_AUTHORITY_NOT_READY'] if authority['status']!='READY' else ['FULL_NUMERICAL_AUTHORITY_READY'],'production_effect':'NONE','automatic_promotion':False}
    obj['sha256']=_sha(obj);return obj

def _check_forward(obj):
    body={k:v for k,v in obj.items() if k!='sha256'}
    if _sha(body)!=obj.get('sha256'):raise ValueError('FORWARD_HASH_MISMATCH')
    protocol=_forward_protocol()
    # Exact preregistered historical pairs remain valid across C1 settlement
    # repairs. This is not a wildcard for changing arm selectors or weights.
    version={'protocol_sha256':obj.get('protocol_sha256'),'definition_sha256':obj.get('definition_sha256')}
    if version in protocol.get('correctness_compatible_frozen_versions',[]):return
    if obj.get('protocol_sha256')!=_sha(protocol):raise ValueError('PROTOCOL_VERSION_MISMATCH')
    if obj.get('definition_sha256')!=_definition_hashes():raise ValueError('DEFINITION_VERSION_MISMATCH')

def persist_forward_capture(obj, root='runtime/local_candidate_forward_measurements'):
    from pathlib import Path
    _check_forward(obj);_safe_forward_key(obj['family_id'],obj['race_id']);folder=Path(root)/obj['family_id']/obj['race_id'];folder.mkdir(parents=True,exist_ok=True)
    target=folder/'pre_result.json'
    if (folder/'settlement.json').exists():
        if target.exists() and json.loads(target.read_text())==obj:return str(target)
        raise ValueError('RESULT_EXISTS_NO_REGENERATION')
    if target.exists():
        old=json.loads(target.read_text())
        if old!=obj:raise ValueError('PRE_RESULT_IMMUTABLE')
        return str(target)
    # Exclusive creation; a fresh process cannot overwrite a frozen arm.
    with target.open('x') as f:json.dump(obj,f,ensure_ascii=False,sort_keys=True,indent=2)
    return str(target)

def failure_axes(authority_status, diagnosis=None):
    diagnosis=diagnosis or {}
    first=diagnosis.get('performance_first_material_failure') or diagnosis.get('first_failure') or diagnosis.get('first_material_failure') or 'UNDIAGNOSED'
    return {'authority_formality_status':authority_status,'performance_first_material_failure':first,
            'secondary_failures':diagnosis.get('secondary_failures') or diagnosis.get('secondary_failure') or [],
            'performance_diagnosis_source':'EXISTING_DIAGNOSIS' if first!='UNDIAGNOSED' else 'NOT_INFERRED_FROM_AUTHORITY'}

def result_authority(obj, result, request, envelope, verification):
    """Caller verifies the signed envelope through existing /verify before invoking us."""
    failures=[];receipt=(envelope or {}).get('receipt') or {};artifact=(envelope or {}).get('artifact') or {}
    if request.get('official_result_verified') is not True:failures.append('OFFICIAL_CONFIRMATION_MISSING')
    if not str(request.get('official_result_verification_ref') or '').strip():failures.append('VERIFICATION_REFERENCE_MISSING')
    if request.get('execution_id')!=obj['execution_id']:failures.append('EXECUTION_ID_MISSING_OR_MISMATCH')
    if request.get('race_id')!=obj['race_id'] or result.get('race_id')!=obj['race_id'] or receipt.get('race_id')!=obj['race_id']:failures.append('RACE_IDENTITY_MISMATCH')
    if (verification or {}).get('verified') is not True or not (envelope or {}).get('signature'):failures.append('SIGNED_RESULT_NOT_VERIFIED')
    if receipt.get('status')!='PASS' or receipt.get('phase')!='RESULT':failures.append('RESULT_RECEIPT_NOT_PASS')
    if receipt.get('artifact_sha256')!=_sha(artifact) or (envelope or {}).get('receipt_sha256')!=_sha(receipt):failures.append('RESULT_DIGEST_MISMATCH')
    expected_final=obj.get('final_receipt_sha256')
    if not expected_final or (artifact.get('frozen_references') or {}).get('final_receipt_sha256')!=expected_final:failures.append('SIGNED_FINAL_EXECUTION_BINDING_MISMATCH')
    # Normalized top3 is allowed, but outcome/payout/source/time must originate in signed RESULT.
    official=artifact.get('official_result') or {};normalized=result.get('official_result') or {}
    signed_top=official.get('top3') or official.get('finish_order',[])[:3]
    actual_top=normalized.get('top3') or normalized.get('finish_order',[])[:3]
    if list(signed_top)!=list(actual_top):failures.append('SIGNED_OUTCOME_MISMATCH')
    if any(normalized.get(k)!=v for k,v in official.items() if k not in {'top3','finish_order'}):failures.append('SIGNED_RESULT_CONTENT_MISMATCH')
    return {'status':'PASS' if not failures else 'HOLD_RESULT_AUTHORITY','failures':failures,
        'verification_ref':request.get('official_result_verification_ref'),
        'result_receipt_sha256':(envelope or {}).get('receipt_sha256'),
        'result_artifact_sha256':receipt.get('artifact_sha256'),
        'verified_signed_result':(verification or {}).get('verified') is True}

def ranking_metrics(pred,actual,universe_size):
    rank=[str(x) for x in pred.get('ranking') or []];roles=pred.get('roles') or {}
    def role(r):return set(str(x) for x in pred.get(r) or []) or {str(k) for k,v in roles.items() if any(str(x).startswith(r) for x in v)}
    ranks=[rank.index(str(x))+1 if str(x) in rank else universe_size+1 for x in actual]
    w,p2,p3=role('W'),role('P2'),role('P3')
    return {'winner_rank':ranks[0],'winner_reciprocal_rank':1/ranks[0] if str(actual[0]) in rank else 0,
        'mean_actual_top3_rank':sum(ranks)/3,'top3_contained_count':sum(str(x) in rank[:3] for x in actual),
        'W_hit':str(actual[0]) in w,'P2_hit':str(actual[1]) in p2,'P3_hit':str(actual[2]) in p3,
        'W_universe':sorted(w),'missing_actual_count':sum(str(x) not in rank for x in actual)}

def evaluate_frozen_candidate(obj,actual):
    candidate=obj.get('candidate') or {};arm=(candidate.get('arms') or {}).get('v0.1') or candidate
    pred=arm.get('candidate_static_prediction') or {}
    if not pred.get('ranking'):return {'status':'HOLD_CANDIDATE_UNAVAILABLE','future_eligible':False}
    universe=len(obj['static_prediction'].get('ranking') or [])
    base=ranking_metrics(obj['static_prediction'],actual,universe);cand=ranking_metrics(pred,actual,universe)
    bw,cw=set(base['W_universe']),set(cand['W_universe']);winner=str(actual[0])
    missing=arm.get('missingness_saturation') or {};coverage=arm.get('runner_component_coverage') or {}
    ratios=[float(v['missingness_ratio']) for indices in missing.values() if isinstance(indices,dict) for v in indices.values() if isinstance(v,dict) and isinstance(v.get('missingness_ratio'),(int,float))]
    return {'status':'EVALUATED_FROZEN_V01','candidate_sha256':candidate.get('sha256') or _sha(candidate),
        'baseline':base,'candidate':cand,'paired_winner_rank_difference':cand['winner_rank']-base['winner_rank'],
        'paired_top3_rank_difference':cand['mean_actual_top3_rank']-base['mean_actual_top3_rank'],
        'role_capture_delta':sum(int(cand[k])-int(base[k]) for k in ['W_hit','P2_hit','P3_hit']),
        'false_W_promotion':len((cw-bw)-{winner}),'false_W_demotion':int(winner in bw-cw),
        'missingness':{'mean_index_missingness_ratio':sum(ratios)/len(ratios) if ratios else None,'runner_component_coverage':coverage,'index_saturation':missing},
        'neutral_component_causal_rank_effect':'UNIDENTIFIED_WITHOUT_PRE_REGISTERED_ABLATION',
        'KRS_downstream_effect':'See frozen candidate KRS postresult artifact; no ticket effect inferred'}

def settle_forward_capture(obj, final, result, *, result_request, diagnosis=None, result_envelope=None, result_verification=None):
    from mec_r4_shadow import settle_ticket_list
    _check_forward(obj)
    if obj['final_basis_sha256']!=_sha(final):raise ValueError('FINAL_BINDING_MISMATCH')
    if result.get('race_id')!=obj['race_id'] or result_request.get('race_id')!=obj['race_id']:raise ValueError('RESULT_RACE_MISMATCH')
    # Missing/mismatched RESULT authority is a research HOLD, never Production veto.
    when=result_request['result_available_at']
    if _forward_dt(when)<=_forward_dt(obj['scheduled_post_at']):raise ValueError('RESULT_NOT_POST_RACE')
    top3=(result.get('official_result') or {}).get('top3') or (result.get('official_result') or {}).get('finish_order',[])[:3]
    top3=[int(x.get('horse_no') or x.get('runner_id')) if isinstance(x,dict) else int(x) for x in top3]
    krs=evaluate_against_result(obj['krs_utility'],top3,static_ranking=obj['static_prediction'].get('ranking'))
    arms={}
    for name,arm in obj['capital']['arms'].items():
        if arm.get('status')=='HOLD_SHADOW':arms[name]=arm;continue
        settlement=settle_ticket_list(arm['tickets'],result)
        inv=settlement.get('investment');ret=settlement.get('return')
        arms[name]={**settlement,'hit':ret>0 if ret is not None else None,'hit_but_loss':0<ret<inv if ret is not None else None}
    complete=bool(arms) and all(a.get('status')=='SETTLED' for a in arms.values())
    baseline=arms.get('PRODUCTION') or {}
    if complete:
        for arm in arms.values():
            arm['net_delta_vs_production']=arm['profit_loss']-baseline['profit_loss']
            arm['marginal_return_vs_production']=arm['return']-baseline['return']
            arm['drawdown_equity_increment']=arm['profit_loss']
    authority=result_authority(obj,result,result_request,result_envelope,result_verification)
    krs_eligible=(obj['classification']=='FORWARD' and authority['status']=='PASS' and not result_request.get('acceptance_only'))
    eligible=krs_eligible and complete and obj['capital']['production_comparable_equal_spend']
    out={'family_id':obj['family_id'],'race_id':obj['race_id'],'execution_id':obj['execution_id'],
         'profile':obj['profile'],'pre_result_sha256':obj['sha256'],'result_sha256':_sha(result),
         'scheduled_post_at':obj['scheduled_post_at'],'official_result_verified':result_request.get('official_result_verified') is True,
         'classification':obj['classification'],'eligible':eligible,'krs_eligible':krs_eligible,
         'status':authority['status'] if authority['status']!='PASS' else 'SETTLED' if complete else 'HOLD_MISSING_PAYOUT_OR_ARM',
         'settlement_completeness':'SETTLED' if complete else 'HOLD_MISSING_PAYOUT_OR_ARM','result_authority':authority,
         'candidate_evaluation':evaluate_frozen_candidate(obj,top3),
         'krs_incremental_utility':krs,'arms':arms,'failure_axes':failure_axes(obj['authority_status'],diagnosis),
         'production_effect':'NONE','automatic_promotion':False}
    out['sha256']=_sha(out);return out

def persist_forward_settlement(pre, measurement,root='runtime/local_candidate_forward_measurements'):
    from pathlib import Path
    _check_forward(pre);_safe_forward_key(pre['family_id'],pre['race_id'])
    if _sha({k:v for k,v in measurement.items() if k!='sha256'})!=measurement.get('sha256'):raise ValueError('SETTLEMENT_HASH_MISMATCH')
    if measurement.get('pre_result_sha256')!=pre['sha256'] or measurement.get('race_id')!=pre['race_id'] or measurement.get('family_id')!=pre['family_id']:raise ValueError('SETTLEMENT_BINDING_MISMATCH')
    folder=Path(root)/pre['family_id']/pre['race_id'];path=folder/'settlement.json'
    if not (folder/'pre_result.json').exists() or json.loads((folder/'pre_result.json').read_text())!=pre:raise ValueError('PRE_RESULT_PERSISTENCE_REQUIRED')
    if path.exists():
        old=json.loads(path.read_text())
        if old==measurement:return str(path)
        if old.get('status')=='SETTLED':raise ValueError('SETTLEMENT_IMMUTABLE')
        # Held diagnostic is retained; later official payout completion may close it.
        history=folder/('held-'+old['sha256']+'.json')
        if not history.exists():history.write_text(json.dumps(old,sort_keys=True))
    path.write_text(json.dumps(measurement,ensure_ascii=False,sort_keys=True,indent=2));return str(path)

def forward_status(root='runtime/local_candidate_forward_measurements'):
    from pathlib import Path
    from pfs_grand_review import _aggregate,_robustness
    out={'profile':_forward_protocol()['version'],'families':{},'automatic_promotion':False,'production_effect':'NONE','capture_failures':[]}
    # Reuse immutable execution records as the failed-capture denominator; do not hide failures.
    for path in Path('runtime/executions').glob('*/FORMAL/runs/*/local_forward_measurement_failure.json'):
        failure=json.loads(path.read_text());request_path=path.parent/'formal_request.json'
        # Unavailable timing stays diagnostic, never eligible OOS.
        out['capture_failures'].append({'race_id':failure.get('race_id'),'execution_id':failure.get('execution_id'),'reason':failure.get('error'),'source_path':str(path)})
    for family in _forward_protocol()['family_cohorts']:
        rows=[];held=[];krs_rows=[];physical_seen=set();captured=len(list((Path(root)/family).glob('*/pre_result.json')))
        for path in sorted((Path(root)/family).glob('*/settlement.json')):
            x=json.loads(path.read_text())
            if x.get('family_id')!=family:continue
            pre=json.loads((path.parent/'pre_result.json').read_text());_check_forward(pre)
            if _sha({k:v for k,v in x.items() if k!='sha256'})!=x.get('sha256') or x.get('pre_result_sha256')!=pre['sha256']:raise ValueError('LEDGER_INTEGRITY_FAIL')
            import re
            physical=re.sub(r'-LIVE-R\d+$','',x['race_id'])
            if physical in physical_seen:
                held.append({'race_id':x['race_id'],'status':'DUPLICATE_PHYSICAL_RACE'});continue
            physical_seen.add(physical)
            if x.get('krs_eligible'):krs_rows.append(x)
            if not x.get('eligible'):held.append({'race_id':x['race_id'],'status':x['status'],'classification':x['classification']});continue
            rows.append(x)
        rows.sort(key=lambda x:x['scheduled_post_at'])
        arm_report={}
        for arm in ['PRODUCTION','CONSERVATIVE','BALANCED','WIDE']:
            economics=[{'race_id':f'{i:08d}','investment':x['arms'][arm]['investment'],'return':x['arms'][arm]['return'],
                        'profit_loss':x['arms'][arm]['profit_loss'],'hit_but_loss':x['arms'][arm]['hit_but_loss']} for i,x in enumerate(rows)]
            arm_report[arm]={'aggregate':_aggregate(economics),'robustness':_robustness(economics)}
        out['families'][family]={'captured_races':captured,'krs_eligible_races':len(krs_rows),'candidate_evaluations':[{'race_id':x['race_id'],'scheduled_post_at':x['scheduled_post_at'],**x['candidate_evaluation']} for x in krs_rows if x.get('candidate_evaluation',{}).get('status')=='EVALUATED_FROZEN_V01'],'krs_measurements':[{'race_id':x['race_id'],**x['krs_incremental_utility']} for x in krs_rows],'eligible_races':len(rows),'held':held,'arms':arm_report,'pilot_minimum':30,
                                 'verdict':'EMPIRICAL_VERDICT_PENDING','race_ids':[x['race_id'] for x in rows]}
    for family,data in out['families'].items():
        data['candidate_futility_review']=candidate_futility_review(data['candidate_evaluations'])
    return out

def candidate_futility_review(rows):
    """Preregistered descriptive review trigger, not a statistical proof or automatic deletion."""
    from collections import defaultdict
    from pfs_grand_review import _venue
    groups=defaultdict(list)
    usable=[r for r in rows if r.get('status')=='EVALUATED_FROZEN_V01']
    for row in usable:groups[(str(row['scheduled_post_at'])[:10],_venue(row['race_id']))].append(row)
    contexts=[{'day':d,'venue':v,'races':len(xs),
        'winner_difference':sum(x['paired_winner_rank_difference'] for x in xs)/len(xs),
        'top3_difference':sum(x['paired_top3_rank_difference'] for x in xs)/len(xs),
        'role_delta':sum(x['role_capture_delta'] for x in xs)} for (d,v),xs in sorted(groups.items())]
    enough=len({x['day'] for x in contexts})>=2 and len({x['venue'] for x in contexts})>=2
    adverse=sum(x['paired_winner_rank_difference']>0 and x['paired_top3_rank_difference']>0 for x in usable)
    favorable=sum(x['paired_winner_rank_difference']<0 or x['paired_top3_rank_difference']<0 for x in usable)
    strata=defaultdict(list)
    for row in usable:
        missing=(row.get('missingness') or {}).get('index_saturation') or {}
        if not missing:continue
        neutral=any(v.get('fully_neutral_sub_index') for indices in missing.values() if isinstance(indices,dict) for v in indices.values() if isinstance(v,dict))
        strata[neutral].append(row)
    missing_known=all(bool((r.get('missingness') or {}).get('index_saturation')) for r in usable)
    reversals=any(sum(r['paired_winner_rank_difference'] for r in xs)<0 or sum(r['paired_top3_rank_difference'] for r in xs)<0 for xs in strata.values())
    trigger=bool(enough and missing_known and adverse>favorable and not reversals and all(x['winner_difference']>0 and x['top3_difference']>0 and x['role_delta']<=0 for x in contexts))
    return {'decision':'EARLY_FUTILITY_REJECT_OR_SIMPLIFY_HUMAN_REVIEW' if trigger else 'HOLD_INSUFFICIENT_CONTEXT' if not enough or not missing_known else 'CONTINUE',
        'contexts':contexts,'adverse_races':adverse,'favorable_races':favorable,'missingness_observed':missing_known,
        'missingness_stratum_reversal':reversals,'automatic_promotion':False,'automatic_deletion':False,
        'allowed_decisions':_forward_protocol()['candidate_decisions']}


def initial_forward_acceptance(pre,measurement,counts_before,counts_after):
    required=['source_receipt_envelope.json','final_receipt_envelope.json','candidate_numerical_shadow_summary.json','krs_prediction_utility.json','mec_r4_shadow_pre_result.json','local_mec_r5_shadow_pre_result.json','common_exact_continuity_shadow_pre_result.json']
    inventory=pre.get('artifact_inventory') or {};missing=[name for name in required if not inventory.get(name,{}).get('sha256')]
    pre_pass=not missing and pre['classification']=='FORWARD' and pre.get('capital',{}).get('production_comparable_equal_spend') is True
    post_pass=measurement.get('eligible') is True and measurement.get('result_authority',{}).get('status')=='PASS'
    return {'profile':'PHASE-B2-INITIAL-FORWARD-ACCEPTANCE','race_id':pre['race_id'],'execution_id':pre['execution_id'],
        'status':'LIVE_FORWARD_MEASUREMENT_OPERATIONAL' if pre_pass and post_pass else 'PENDING_OR_HELD',
        'pre_race_capture':'PASS' if pre_pass else 'HOLD','post_result_settlement':'PASS' if post_pass else 'HOLD',
        'freeze_timestamps':{'forward':pre['generated_at'],'scheduled_post':pre['scheduled_post_at']},
        'source_sha256':pre['source_sha256'],'final_sha256':pre['final_basis_sha256'],'artifact_inventory':inventory,
        'baseline':pre['static_prediction'],'candidate':measurement.get('candidate_evaluation'),
        'KRS':measurement.get('krs_incremental_utility'),'capital_arms':measurement.get('arms'),
        'official_result_authority':measurement.get('result_authority'),'first_material_failure':measurement.get('failure_axes'),
        'counts_before':counts_before,'counts_after':counts_after,'capture_failures':missing,
        'common_exact_MEC_settlements':'immutable RESULT execution artifacts, inspect independent eligibility counts',
        'production_effect':'NONE','prediction_improvement_claim':False,'actual_PFS':'UNKNOWN unless explicit purchase ledger verified'}

def forward_tracker_result_authority(race_id, lineage_root, *, local_only=False):
    """Additional authority requirement for prospective LOCAL rows; preserve historical cohorts."""
    import re
    from pathlib import Path
    dates=re.findall(r'20\d{6}',str(race_id))
    if not dates or dates[0]<'20261001':return None
    if local_only and not any(v in str(race_id).split('-') for v in ['LOCAL','FNB','URW','OHI','KAW','SON','NGY','KOC','SAG','MON','MOR','KSM']):return None
    path=Path(lineage_root)/(str(race_id)+'.json')
    auth=(json.loads(path.read_text()).get('result_authority') or {}) if path.exists() else {}
    ok=auth.get('status')=='PASS' and auth.get('verified_signed_result') is True and all(auth.get(k) for k in ['verification_ref','result_receipt_sha256','result_artifact_sha256'])
    return {'verified':bool(ok),'oos_admissible':bool(ok),'refs':[auth] if ok else [],'status':'PASS' if ok else 'HOLD_RESULT_AUTHORITY'}
