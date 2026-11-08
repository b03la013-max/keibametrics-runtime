"""JRA Production closed loop: signed FINAL -> official JRA result -> settlement -> RESULT request.

Builds ``runtime/results/<race_id>.json`` for the canonical Formal Result Runner
(which issues the signed RESULT receipt and runs review / learning / OOS).

Never mutates or backdates the immutable FINAL. Recommendation-only tickets are
settled as a frozen *recommendation* (virtual PFS); actual purchase is recorded
separately and is never inferred.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "jra_source_runtime"))

PROFILE = "KM-JRA-PRODUCTION-POSTRESULT-CLOSEDLOOP-20261010-R1"
BET_N = {"EXACTA": 2, "TRIO": 3, "TRIFECTA": 3}


class ProductionPostResultError(ValueError):
    pass


# These two historical repairs require the separately requested Owner B.
# All other races retain their existing, already authorized natural path.
OWNER_B_RECOVERY_SCOPES = {
    'KM-JRA-TKY-20261031-R06': ('FORMAL_RESULT_SETTLEMENT_REVIEW_STATE',
        'runtime/final_artifacts/KM-JRA-TKY-20261031-R06.json'),
    'KM-JRA-TKY-20261031-R05': ('NO_BET_REVIEW_STATE_ONLY',
        'runtime/jra_no_bet_learning/KM-JRA-TKY-20261031-R05-LIVE-R1.json'),
}
OWNER_B_POLICY_FILES = ('runtime/jra_production_postresult.py',
    'runtime/jra_no_bet_postresult_learning.py',
    '.github/workflows/km-jra-no-bet-postresult-learning.yml')


def require_owner_b_recovery(root, race_id, *, now=None, required_operation=None):
    """Reuse the existing committed Owner-record pattern for exact repairs only.

    Code integration is not an approval. No approval record is created here;
    it may be committed only after the Owner's separate, explicit decision.
    This is a repository governance record, not a new cryptographic signer.
    """
    scope=OWNER_B_RECOVERY_SCOPES.get(race_id) if isinstance(race_id,str) else None
    if scope is None:return None
    root=Path(root);operation,original_ref=scope
    relative=f'profiles/jra_postresult_recovery_approvals/{race_id}.json'
    path=root/relative
    try:
        if required_operation is not None and required_operation!=operation:
            raise ValueError('OPERATION_OUTSIDE_APPROVAL')
        if path.is_symlink():raise ValueError('SYMLINK')
        raw=path.read_bytes();record=json.loads(raw)
        original=root/original_ref
        if original.is_symlink():raise ValueError('ORIGINAL_SYMLINK')
        policy={}
        for name in OWNER_B_POLICY_FILES:
            policy_path=root/name
            if policy_path.is_symlink():raise ValueError('POLICY_SYMLINK')
            policy_raw=policy_path.read_bytes()
            if subprocess.check_output(['git','show','HEAD:'+name],cwd=root,timeout=10,
                    stderr=subprocess.DEVNULL)!=policy_raw:raise ValueError('POLICY_NOT_COMMITTED')
            policy[name]=hashlib.sha256(policy_raw).hexdigest()
        if policy['runtime/jra_production_postresult.py']!=hashlib.sha256(Path(__file__).read_bytes()).hexdigest():
            raise ValueError('EXECUTING_POLICY_NOT_COMMITTED')
        if (record.get('decision')!='AUTHORIZE_JRA_POSTRESULT_RECOVERY'
                or record.get('race_id')!=race_id or record.get('operation')!=operation
                or record.get('original_ref')!=original_ref
                or record.get('artifact_file_sha256')!=hashlib.sha256(original.read_bytes()).hexdigest()
                or record.get('policy_source_sha256')!=_sha(policy)
                or record.get('current_authority_manifest')!='KM-FAMILY-CURRENT-AUTHORITY-20261012-R51'
                or record.get('authorized_by')!='b03la013-max'
                or not isinstance(record.get('authorization_ref'),str)
                or not record['authorization_ref'].strip()
                or _dt(record.get('authorized_at'))>(now or datetime.now(timezone.utc))):
            raise ValueError('CONTENT_OR_PIN')
        # An uncommitted workspace file or environment variable cannot grant B.
        committed=subprocess.check_output(['git','show','HEAD:'+relative],cwd=root,timeout=10,
                                           stderr=subprocess.DEVNULL)
        if committed!=raw:raise ValueError('NOT_COMMITTED_RECORD')
    except (OSError,ValueError,TypeError,AttributeError,subprocess.SubprocessError) as exc:
        error=ProductionPostResultError('OWNER_B_APPROVAL_REQUIRED:'+str(race_id))
        error.first_failed_stage='OWNER_B_AUTHORIZATION'
        raise error from exc
    return {'operation':operation,'original_ref':original_ref,
            'authorization_record':relative,
            'authorization_record_sha256':hashlib.sha256(raw).hexdigest()}


def _sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def _dt(v):
    try:
        value=datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except (TypeError,ValueError) as exc:
        raise ProductionPostResultError("FINAL_TEMPORAL_VALUE_INVALID") from exc
    if value.tzinfo is None:
        raise ProductionPostResultError("FINAL_TEMPORAL_TIMEZONE_REQUIRED")
    return value


def legacy_final_classification(final: dict):
    """Classify missing old Formal contracts without inventing race clocks.

    A declared current Formal FINAL with a broken required time is a material
    failure, not an old-schema exclusion. A dated race ID is never a clock.
    """
    if (final.get('temporal_mode')=='FORMAL-PRE-RACE' or
            'sha256' in final or 'final_receipt' in final):
        return None
    if final.get('historical_bootstrap') is not True:
        raise ProductionPostResultError('FINAL_SCHEMA_INTEGRITY_NOT_ESTABLISHED')
    missing=[name for name in ('family_id','temporal_mode','scheduled_post_at','prediction_cutoff',
                               'final_receipt','final_receipt_sha256') if not final.get(name)]
    if not missing:
        return {'status':'NOT_ELIGIBLE_NON_FORMAL_FINAL',
                'reason':'FINAL_DOES_NOT_DECLARE_FORMAL_PRE_RACE_CONTRACT'}
    return {'status':'NOT_ELIGIBLE_LEGACY_FINAL','missing_fields':missing,
            'reason':'FORMAL_PRE_RACE_TIME_AND_SIGNATURE_CONTRACT_NOT_ESTABLISHED',
            'scheduled_post_at':final.get('scheduled_post_at'),
            'prediction_cutoff_used_as_post':False,'race_id_date_used_as_post':False,
            'persisted':False,'recommendation_pfs':None,
            'actual_purchase':'UNVERIFIED','actual_purchase_pfs':None}


def verify_final(final: dict) -> None:
    """Check the immutable body's mechanics; signature verification is separate."""
    body = {k: v for k, v in final.items() if k != "sha256"}
    if final.get("sha256") != _sha(body):
        raise ProductionPostResultError("IMMUTABLE_FINAL_HASH_INVALID")
    if final.get("family_id") != "JRA" or final.get("temporal_mode") != "FORMAL-PRE-RACE":
        raise ProductionPostResultError("NOT_JRA_FORMAL_PRE_RACE_FINAL_SCHEMA_INTEGRITY")
    if not final.get('scheduled_post_at') or not final.get('prediction_cutoff'):
        raise ProductionPostResultError('FINAL_FORMAL_TEMPORAL_FIELDS_MISSING')
    post=_dt(final['scheduled_post_at'])
    if _dt(final['prediction_cutoff'])>=post:
        raise ProductionPostResultError('FINAL_FORMAL_TEMPORAL_ORDER_INVALID')
    receipt = final.get("final_receipt") or {}
    ts = (receipt.get("receipt") or {}).get("timestamp")
    if not final.get("final_receipt_sha256") or not ts:
        raise ProductionPostResultError("SIGNED_FINAL_RECEIPT_MISSING")
    if _dt(ts) >= post:
        raise ProductionPostResultError("FINAL_RECEIPT_AFTER_POST")


def verify_archived_final_signature(final:dict,*,root:Path,race_id:str)->None:
    """Reuse the existing archived trust and signed-payload verifier offline."""
    if final.get("race_id")!=race_id:
        raise ProductionPostResultError("POSTRESULT_FINAL_RACE_ID_MISMATCH")
    from jra_presentation import archived_trust
    from jra_delivery import verify_signed_final
    try:
        health,contract=archived_trust(final,root=root)
        verify_signed_final(final,health,contract)
    except Exception as exc:
        raise ProductionPostResultError("POSTRESULT_FINAL_SIGNATURE_NOT_VERIFIED:"+
                                        type(exc).__name__+":"+str(exc)) from exc


def settle_final(final: dict, official: dict) -> dict:
    """Settle exactly the frozen FINAL tickets against verified official payouts."""
    from jra_candidate_postresult_closedloop import official_top3_orders, official_payout_entries
    ft = final.get("final_ticket") or {}
    tickets = list(ft.get("tickets") or [])
    try:
        orders=official_top3_orders(official)
        prices={kind:official_payout_entries(official,kind) for kind in BET_N}
    except ValueError as exc:
        raise ProductionPostResultError(str(exc)) from exc
    top3={number for order in orders for number in order}
    refund_ids=official.get("refund_runner_ids") or []
    if (not isinstance(refund_ids,list) or any(type(x) is not int or not 1<=x<=18 for x in refund_ids)
            or len(refund_ids)!=len(set(refund_ids))):
        raise ProductionPostResultError("OFFICIAL_REFUND_RUNNER_INVALID")
    not_refundable={int(r["horse_no"]) for r in official.get("non_finishers") or []
                    if r.get("finish_status") in {"DID_NOT_FINISH","DISQUALIFIED"}}
    if set(refund_ids)&not_refundable:
        raise ProductionPostResultError("NONCANCELLATION_REFUND_FORBIDDEN")
    if set(refund_ids)&set(top3):
        raise ProductionPostResultError("OFFICIAL_REFUND_TOP3_CONFLICT")
    seen, wins, refunded_tickets, stake_total, ret_total, refund = set(), [], [], 0, 0, 0
    for t in tickets:
        kind = str(t.get("bet_type") or "").upper()
        if kind not in BET_N:
            raise ProductionPostResultError("UNKNOWN_BET_TYPE:" + kind)
        sel = list(t.get("selection") or [])
        if any(type(x) is not int or not 1 <= x <= 18 for x in sel):
            raise ProductionPostResultError("FROZEN_SELECTION_INVALID")
        stake = t.get("stake")
        if (len(sel) != BET_N[kind] or len(set(sel)) != len(sel) or not isinstance(stake, int)
                or isinstance(stake, bool) or stake <= 0 or stake % 100):
            raise ProductionPostResultError("FROZEN_TICKET_INVALID")
        key = (kind, tuple(sorted(sel)) if kind == "TRIO" else tuple(sel))
        if key in seen:
            raise ProductionPostResultError("DUPLICATE_FROZEN_TICKET")
        seen.add(key)
        stake_total += stake
        if set(sel)&set(refund_ids):
            refund += stake
            refunded_tickets.append({"bet_type":kind,"selection":sel,"stake":stake,
                                     "refund":stake,"reason":"OFFICIAL_WITHDRAWN_RUNNER"})
            continue
        obs = sorted(sel) if kind == "TRIO" else sel
        matched=[pay for pay in prices[kind] if obs==
                 (sorted(pay["selection"]) if kind=="TRIO" else pay["selection"])]
        # A canonical combination is unique in official_payout_entries. Two
        # distinct tied-third combinations can both pay, each ticket once.
        pay=matched[0] if matched else None
        amount=(stake//100)*pay["per_100_yen"] if pay is not None else 0
        ret_total += amount
        if amount:
            wins.append({"bet_type": kind, "selection": sel, "stake": stake,
                         "payout_per_100": int(pay["per_100_yen"]), "return": amount})
    if type(ft.get("total_investment")) is not int or stake_total != ft["total_investment"]:
        raise ProductionPostResultError("FROZEN_TOTAL_INVESTMENT_MISMATCH")
    decision = (final.get("capital_policy_decision") or {}).get("decision")
    effective_investment=stake_total-refund
    exposure_class=('PAPER_REFERENCE' if decision=='PAPER' else
                    'NO_BET' if decision=='NO_BET' or bool(ft.get('no_bet')) or not stake_total else
                    'RECOMMENDATION' if decision in {
                        'EXECUTE_RECOMMENDATION_PORTFOLIO','EXECUTE_FULL_MEC'} else 'UNKNOWN')
    settled = {
        "status": "SETTLED",
        "pfs_authority": "FROZEN-RECOMMENDATION-PFS",
        "total_investment": stake_total,
        "total_payout": ret_total,
        "refund": refund,
        "effective_investment":effective_investment,
        "profit_loss": ret_total + refund - stake_total,
        "pfs": (100.0 * ret_total / effective_investment) if effective_investment else None,
        "gross_stake_pfs":(100.0 * ret_total / stake_total) if stake_total else None,
        "pfs_denominator":"EFFECTIVE_INVESTMENT_EXCLUDING_OFFICIAL_REFUNDS",
        "winning_tickets": wins,
        "refunded_tickets":refunded_tickets,
        "no_bet": bool(ft.get("no_bet")),
        "capital_policy_decision": decision,
        "capital_exposure_class":exposure_class,
        "recommendation_pfs":((100.0*ret_total/effective_investment)
                               if effective_investment and exposure_class=='RECOMMENDATION' else None),
        "actual_purchase":"UNVERIFIED",
        "actual_purchase_status":"UNVERIFIED",
        "actual_purchase_pfs":None,
        "actual_pfs_status": "NOT_VERIFIED",
        "note": "Settled frozen FINAL tickets at official JRA payouts. Recommendation PFS is virtual; actual purchase is recorded separately and never inferred.",
    }
    if len(orders)>1:
        settled.update(official_top3_orders=orders,official_finish_groups=official["finish_groups"],
                       official_winning_combinations=prices)
    return settled


def persist_dead_heat_role_rescue_result(root: Path, result: dict):
    """Settle once per race and keep rank diagnostics for every valid order."""
    import os
    from tempfile import TemporaryDirectory
    from jra_candidate_postresult_closedloop import official_top3_orders
    from jra_conditional_rank_shadow import evaluate_comparison
    from jra_role_learning_shadow import digest, persist_shadow_result, settle_shadow, write_status

    official = result['official_result']
    orders = official_top3_orders(official)
    if len(orders) < 2:
        raise ProductionPostResultError('ROLE_RESCUE_DEAD_HEAT_ORDERS_REQUIRED')
    root = Path(root)
    rid = result['race_id']
    pre = root / 'runtime/role_rescue_shadow' / f'{rid}.json'
    if not pre.is_file():
        return None
    path = root / 'runtime/role_rescue_shadow_results' / f'{rid}.json'
    if path.is_file():
        return persist_shadow_result(root, result)

    shadow = json.loads(pre.read_text(encoding='utf-8'))
    out = settle_shadow(shadow, result)
    rank = shadow.get('conditional_rank_comparison') or {}
    if rank.get('role_rankings') and rank.get('model_policy_sha256'):
        out['conditional_rank_evaluation'] = {
            'status': 'DEAD_HEAT_MULTIPLE_VALID_ORDERS', 'oos_eligible': False,
            'by_valid_order': [{'top3': order, 'evaluation': evaluate_comparison(rank, order)}
                               for order in orders],
        }
    # Settlement is a post-result diagnostic. Tie rankings have no registered
    # cohort aggregation rule, so they cannot be counted as forward OOS credit.
    out.update(official_top3_orders=orders, result_request_sha256=digest(result),
               eligibility_status='DEAD_HEAT_RESEARCH_DIAGNOSTIC_ONLY',
               oos_candidate_id=shadow.get('oos_candidate_id'), preregistration_verified=False)
    out['sha256'] = digest({k: v for k, v in out.items() if k != 'sha256'})
    path.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=path.parent) as directory:
        staged = Path(directory) / path.name
        staged.write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8')
        try:
            os.link(staged, path)
        except FileExistsError:
            return persist_shadow_result(root, result)
    write_status(root / 'runtime/role_rescue_shadow_status.json', records_dir=path.parent)
    return out


def build_result_request(final: dict, official: dict, evidence: dict) -> dict:
    verify_final(final)
    settlement = settle_final(final, official)
    finish = [int(r["horse_no"]) for r in sorted(
        (r for r in (evidence.get("parsed") or {}).get("runners") or []
         if isinstance(r.get("finish"), int)), key=lambda r: r["finish"])]
    fpp = final.get("final_prediction_package") or {}
    req = {
        "race_id": final["race_id"],
        "result_lane": "PRODUCTION",
        "official_result": {
            "status": "OFFICIAL",
            "finish_order": finish,
            "top3": [int(x) for x in official["top3"]],
            "payouts": official["payouts"],
            "refund_runner_ids":official.get("refund_runner_ids") or [],
            "non_finishers":official.get("non_finishers") or [],
            "refund_declaration":official.get("refund_declaration"),
            "source": "JRA official result (www.jra.go.jp)",
            "source_url": evidence.get("url"),
            "raw_sha256": evidence.get("sha256"),
            "captured_at": evidence.get("captured_at"),
            "result_use": "POST-RACE",
        },
        "settlement": settlement,
        "frozen_prediction_ref": {
            "prediction_id": final["race_id"] + "-PRODUCTION",
            "immutable_final_sha256": final["sha256"],
            "final_receipt_sha256": final["final_receipt_sha256"],
            "source_cutoff": final.get("prediction_cutoff"),
            "final_freeze_timestamp": final.get("final_freeze_timestamp"),
            "final_status": "FORMAL-PRE-RACE / FULL_FORMAL_E2E_PASS",
            "validation_status": fpp.get("validation_status") or "VALIDATED",
        },
        "learning_event": {
            "status": "RECORDED",
            "profile": PROFILE,
            "event_type": "JRA_PRODUCTION_POST_RACE_REVIEW",
            "result_use": "PREQUENTIAL_TO_NEXT_RACE_ONLY",
            "numeric_recalibration": False,
            "new_model_weights_applied": False,
            "promotion_authority": False,
        },
    }
    if official.get("top3_orders") is not None:
        req["official_result"].update(
            top3_orders=official["top3_orders"],finish_groups=official["finish_groups"],
            dead_heat=True,top3_is_legacy_representative=True)
    if official.get('declared_cancellation_context') is not None:
        req['official_result']['declared_cancellation_context'] = official['declared_cancellation_context']
    # Capture metadata is post-result evidence only. It cannot create an old
    # SOURCE, FINAL, receipt, clock witness, or Forward OOS admission.
    if evidence.get('raw_base64') is not None:
        from jra_candidate_postresult_closedloop import build_official_result_observation
        req['official_result']['source_observation']=build_official_result_observation(final['race_id'],evidence)
    return req


def build_settlement_correction(final:dict, original_result:dict, official:dict, evidence:dict,
                                *, audited_at:str)->dict:
    """Record a post-result correction separately; never rewrite signed inputs.

    This is an unsigned audit revision, not a newly signed RESULT receipt or
    an authorization to replace an old canonical result or Learning State.
    """
    verify_final(final)
    if original_result.get("race_id")!=final["race_id"]:
        raise ProductionPostResultError("CORRECTION_RACE_MISMATCH")
    if (original_result.get("frozen_prediction_ref") or {}).get("immutable_final_sha256")!=final["sha256"]:
        raise ProductionPostResultError("CORRECTION_FINAL_BINDING_MISMATCH")
    if (not isinstance(evidence.get("sha256"),str) or len(evidence["sha256"])!=64
            or any(c not in '0123456789abcdef' for c in evidence['sha256'])):
        raise ProductionPostResultError("CORRECTION_OFFICIAL_RAW_HASH_REQUIRED")
    when=_dt(audited_at)
    captured=_dt(evidence["captured_at"])
    if not when.tzinfo or not captured.tzinfo or not _dt(final["scheduled_post_at"])<captured<=when:
        raise ProductionPostResultError("CORRECTION_CHRONOLOGY_INVALID")
    corrected=settle_final(final,official)
    before=original_result["settlement"]
    fields=("total_investment","refund","effective_investment","total_payout","profit_loss","pfs")
    out={"race_id":final["race_id"],"profile":"JRA-EXISTING-SETTLEMENT-CORRECTION-AUDIT",
         "classification":"POSTRESULT_CORRECTION_AUDIT_NOT_SIGNED_RESULT_NOT_FORWARD_OOS",
         "audited_at":when.isoformat(),"original_result_sha256":_sha(original_result),
         "immutable_final_sha256":final["sha256"],"final_receipt_sha256":final["final_receipt_sha256"],
         "official_evidence":{"raw_sha256":evidence["sha256"],"captured_at":evidence["captured_at"],"url":evidence.get("url")},
         "official_refund_runner_ids":official.get("refund_runner_ids") or [],
         "original_settlement":before,"corrected_settlement":corrected,
         "changes":{k:{"before":before.get(k),"after":corrected.get(k)} for k in fields if before.get(k)!=corrected.get(k)},
         "signed_result_correction":"NOT_ISSUED","old_learning_unchanged":True,
         "original_frozen_prediction_unchanged":True,"actual_purchase_status":"UNVERIFIED"}
    out["sha256"]=_sha(out)
    return out


def _intent_for(root: Path, race_id: str) -> dict:
    from jra_candidate_postresult_closedloop import validate_result_target
    hits = []
    for p in sorted((root / "runtime" / "jra_formal_intents").glob(race_id + "-*.json")):
        x = json.loads(p.read_text(encoding="utf-8"))
        if x.get("race_id") == race_id and (x.get("jra_source") or {}).get("jra_meeting_key"):
            # The unsigned routing intent cannot rename a different date,
            # venue or race while retaining the immutable FINAL's race_id.
            try:
                identity=validate_result_target(race_id,x.get('race_date'),
                    x['jra_source']['jra_meeting_key'],x.get('race_no'))
            except (TypeError,ValueError) as exc:
                raise ProductionPostResultError('JRA_FORMAL_INTENT_IDENTITY_MISMATCH') from exc
            if x.get('venue_id',identity['venue_id'])!=identity['venue_id']:
                raise ProductionPostResultError('JRA_FORMAL_INTENT_IDENTITY_MISMATCH')
            hits.append(x)
    if not hits:
        raise ProductionPostResultError("JRA_FORMAL_INTENT_MISSING")
    keys = {(h["race_date"], h["jra_source"]["jra_meeting_key"], int(h["race_no"])) for h in hits}
    if len(keys) != 1:
        raise ProductionPostResultError("JRA_FORMAL_INTENT_AMBIGUOUS")
    return hits[-1]


def _result_execution_id(final, race_id):
    execution_id = ((final.get('execution_stage_manifest') or {}).get('SIGNED_SOURCE_RECEIPT_VERIFIED') or {}).get('execution_id')
    if not isinstance(execution_id,str) or not re.fullmatch(re.escape(race_id)+r'-LIVE-R[1-9]\d*',execution_id):
        raise ProductionPostResultError('RESULT_REUSE_SOURCE_EXECUTION_IDENTITY_MISMATCH')
    return execution_id


def _bind_result_response(request,response,final):
    receipt=response.get('receipt') or {}
    if (receipt.get('phase')!='RESULT' or receipt.get('status')!='PASS' or receipt.get('errors')
            or receipt.get('race_id')!=request['race_id'] or receipt.get('artifact_sha256')!=_sha(request)
            or response.get('receipt_sha256')!=_sha(receipt)
            or response.get('signature_alg')!='Ed25519' or not response.get('signature')
            or not response.get('signer_key_id')):
        raise ProductionPostResultError('RESULT_REUSE_RECEIPT_BINDING_MISMATCH')
    if _dt(receipt.get('timestamp'))<=_dt(final['scheduled_post_at']):
        raise ProductionPostResultError('RESULT_REUSE_TEMPORAL_BEFORE_POST')


def reuse_or_submit_production_result(root,request,*,call,checkpoint,run_id,github_sha=None,publish=None):
    """Reuse verified JRA RESULT checkpoints before requesting another signature.

    The hosted publisher persists a claim before submission and a response
    before external verification or downstream work. An unknown outcome
    requires reconciliation and never opens another submission attempt.
    """
    from execution_store import resolve_phase,persist_phase,phase_root,require_public_storage
    from jra_result_submission import ResultSubmission
    root=Path(root);checkpoint=Path(checkpoint);race_id=request.get('race_id')
    if (not isinstance(race_id,str) or not re.fullmatch(r'KM-JRA-[A-Z]{3}-\d{8}-R\d{2}',race_id)
            or request.get('family_id','JRA')!='JRA'
            or str(request.get('result_lane') or 'PRODUCTION').upper()!='PRODUCTION'):
        raise ProductionPostResultError('RESULT_REUSE_PRODUCTION_JRA_REQUIRED')
    require_owner_b_recovery(root,race_id,required_operation='FORMAL_RESULT_SETTLEMENT_REVIEW_STATE')
    final=json.loads((root/'runtime/final_artifacts'/(race_id+'.json')).read_text())
    verify_final(final)
    verify_archived_final_signature(final,root=root,race_id=race_id)
    refs=request.get('frozen_prediction_ref') or {}
    if (refs.get('immutable_final_sha256')!=final.get('sha256') or
            refs.get('final_receipt_sha256')!=final.get('final_receipt_sha256')):
        raise ProductionPostResultError('RESULT_REUSE_FINAL_BINDING_MISMATCH')
    require_public_storage(request)
    execution_id=_result_execution_id(final,race_id)
    executions=root/'runtime/executions'
    phase=resolve_phase(execution_id,'RESULT',root=executions)
    saved_dir=phase['run_dir'] if phase else None
    if phase and not {'result_request.json','result_receipt_envelope.json'}<=set(phase['manifest']['files']):
        raise ProductionPostResultError('RESULT_REUSE_CHECKPOINT_INCOMPLETE')
    if phase is None:
        # Local post-signature recovery may precede immutable publication.
        local_files=[(checkpoint/name).exists() for name in ('result_request.json','result_receipt_envelope.json')]
        if any(local_files):
            if not all(local_files):
                raise ProductionPostResultError('RESULT_REUSE_LOCAL_CHECKPOINT_INCOMPLETE')
            saved_dir=checkpoint
        elif any((phase_root(execution_id,'RESULT',executions)/'runs').glob('*')):
            raise ProductionPostResultError('RESULT_REUSE_PARTIAL_CHECKPOINT_UNRESOLVED')
    submission=ResultSubmission(root,execution_id,request) if publish is not None else None
    if saved_dir is not None:
        saved_request=json.loads((saved_dir/'result_request.json').read_text())
        if saved_request!=request:
            raise ProductionPostResultError('RESULT_REUSE_REQUEST_SHA_MISMATCH')
        response=json.loads((saved_dir/'result_receipt_envelope.json').read_text())
        reused=True
    else:
        status,response = submission.state() if submission is not None else ('READY',None)
        reused=status=='RESPONSE_RECORDED'
        if not reused:
            if status!='READY':
                raise ProductionPostResultError('RESULT_SUBMISSION_'+status)
            if submission is not None:
                submission.claim(str(run_id),publish)
                path=root/'runtime/results'/(race_id+'.json')
                current=json.loads(path.read_text(encoding='utf-8'))
                current_final=json.loads((root/'runtime/final_artifacts'/(race_id+'.json')).read_text(encoding='utf-8'))
                if current!=request or current_final!=final:
                    raise ProductionPostResultError('RESULT_SUBMISSION_CANONICAL_INPUT_CHANGED')
            code,response=call('/result',request)
            if not 200<=code<300:raise ProductionPostResultError('RESULT_SUBMISSION_HTTP_FAILURE:'+str(code))
    # Keep the received original bytes locally even when verification is
    # refused or disconnected. These files are not verified phase admission.
    require_public_storage(response)
    checkpoint.mkdir(parents=True,exist_ok=True)
    for name,value in (('result_request.json',request),('result_receipt_envelope.json',response)):
        target=checkpoint/name
        if target.exists():
            if json.loads(target.read_text())!=value:
                raise ProductionPostResultError('RESULT_REUSE_LOCAL_CHECKPOINT_CONFLICT')
        elif saved_dir is not None:
            target.write_bytes((saved_dir/name).read_bytes())
        else:
            with target.open('x',encoding='utf-8') as fh:
                json.dump(value,fh,ensure_ascii=False,sort_keys=True,indent=2)
    _bind_result_response(request,response,final)
    if submission is not None and not reused:
        submission.save_response(response,publish)
    code,verification=call('/verify',response)
    if not 200<=code<300 or verification.get('valid') is not True:
        raise ProductionPostResultError('RESULT_REUSE_SIGNATURE_NOT_VERIFIED')
    if phase is None:
        persist_phase(execution_id,'RESULT',str(run_id),checkpoint,root=executions,github_sha=github_sha)
    return response,{'status':'VERIFIED_REUSE' if reused else 'NEW_VERIFIED_RESULT_RECEIPT',
                     'result_resigning':False if reused else None,'new_result_submission':not reused,
                     'execution_id':execution_id,
                     'request_sha256':_sha(request),'receipt_sha256':response['receipt_sha256']}


def _source_bound_result_universe(root: Path, final: dict):
    """Reuse the immutable SOURCE store and existing crypto/OIDC verifiers.

    A cancelled declared runner belongs to RESULT, but never becomes an active
    prediction runner. An arbitrary in-file PASS or public key is insufficient.
    """
    from execution_store import resolve_phase
    from jra_pedigree_corpus import _verified_source, _attested
    stage = ((final.get('final_prediction_package') or {}).get('execution_stage_manifest')
             or {}).get('SIGNED_SOURCE_RECEIPT_VERIFIED') or {}
    race = final.get('race_id')
    execution_id = stage.get('execution_id')
    if (not isinstance(race, str) or not isinstance(execution_id, str)
            or not re.fullmatch(re.escape(race) + r'-LIVE-R[1-9]\d*', execution_id)):
        raise ProductionPostResultError('RESULT_SOURCE_EXECUTION_BINDING_INVALID')
    saved = resolve_phase(execution_id, 'SOURCE', root=root / 'runtime/executions')
    if saved is None or 'source_receipt_envelope.json' not in saved['manifest']['files']:
        raise ProductionPostResultError('RESULT_ORIGINAL_SOURCE_CHECKPOINT_MISSING')
    path = saved['run_dir'] / 'source_receipt_envelope.json'
    checked = _verified_source(path)
    if checked is None:
        raise ProductionPostResultError('RESULT_SOURCE_SIGNATURE_OR_SNAPSHOT_INVALID')
    envelope = json.loads(path.read_text())
    source = envelope['artifact']
    if (checked.get('race_id') != race or source.get('race_id') != race
            or envelope.get('receipt_sha256') != stage.get('receipt_sha256')
            or checked.get('source_snapshot_sha256') != final.get('source_snapshot_sha256')
            or checked.get('source_snapshot_sha256') != stage.get('source_snapshot_sha256')):
        raise ProductionPostResultError('RESULT_ORIGINAL_SOURCE_FINAL_BINDING_MISMATCH')
    if not _attested(path, signer='km-jra-source-first-runner.yml',
                     not_after=_dt(final['prediction_cutoff'])):
        raise ProductionPostResultError('RESULT_SOURCE_OIDC_NOT_VERIFIED')
    declared = (source.get('jra_declared_runner_universe') or {}).get('runners')
    active = (source.get('official_runner_universe') or {}).get('runners')
    def ids(rows):
        if not isinstance(rows, list) or not rows:
            raise ProductionPostResultError('RESULT_SOURCE_UNIVERSE_MISSING')
        out = []
        for row in rows:
            if (not isinstance(row, dict) or type(row.get('horse_no')) is not int
                    or not 1 <= row['horse_no'] <= 18
                    or str(row.get('runner_id')) != str(row['horse_no'])):
                raise ProductionPostResultError('RESULT_SOURCE_RUNNER_IDENTITY_INVALID')
            out.append(str(row['runner_id']))
        if len(out) != len(set(out)):
            raise ProductionPostResultError('RESULT_SOURCE_UNIVERSE_DUPLICATE')
        return out
    declared_ids, active_ids = ids(declared), ids(active)
    cancelled = {str(row['runner_id']) for row in declared
                 if row.get('status') in {'CANCELLED', 'EXCLUDED'}}
    ranking = (final.get('static_prediction') or {}).get('ranking')
    if (any(row.get('status') not in {'ACTIVE', 'CANCELLED', 'EXCLUDED'} for row in declared)
            or any(row.get('status') != 'ACTIVE' for row in active)
            or not isinstance(ranking, list) or len(ranking) != len(set(map(str, ranking)))
            or set(map(str, ranking)) != set(active_ids)
            or set(active_ids) != set(declared_ids) - cancelled):
        raise ProductionPostResultError('RESULT_DECLARED_ACTIVE_FINAL_BINDING_MISMATCH')
    # The exception below concerns runners already excluded by the original
    # pre-prediction SOURCE, never a newly withdrawn active runner. Certify no
    # signed ticket can create a refund liability outside that active set.
    for ticket in (final.get('final_ticket') or {}).get('tickets') or []:
        selection = ticket.get('selection')
        if (not isinstance(selection, list) or not selection
                or any(type(number) is not int or str(number) not in set(active_ids)
                       for number in selection)):
            raise ProductionPostResultError('RESULT_FROZEN_TICKET_OUTSIDE_ACTIVE_SOURCE')
    return declared_ids, cancelled


def process(root: Path, race_id: str, *, now=None, enroll_signer=False) -> str:
    require_owner_b_recovery(root,race_id,now=now,required_operation='FORMAL_RESULT_SETTLEMENT_REVIEW_STATE')
    out = root / "runtime" / "results" / (race_id + ".json")
    if out.exists():
        return _saved_request_status(root,race_id) if enroll_signer else "ALREADY_RESULTED"
    fpath = root / "runtime" / "final_artifacts" / (race_id + ".json")
    if not fpath.exists():
        return "NO_PRODUCTION_FINAL"
    final = json.loads(fpath.read_text(encoding="utf-8"))
    classification=legacy_final_classification(final)
    if classification:
        return classification['status']
    stage="VERIFY_FROZEN_FINAL"
    evidence = None
    try:
        verify_final(final)
        verify_archived_final_signature(final,root=root,race_id=race_id)
        post = _dt(final["scheduled_post_at"])
        now = now or datetime.now(timezone.utc)
        if now <= post + timedelta(minutes=1):
            return "RESULT_NOT_YET_DUE"
        stage="VERIFY_PRE_START_GIT_WITNESS"
        rel = fpath.relative_to(root).as_posix()
        committed = subprocess.check_output(["git", "log", "--diff-filter=A", "-1", "--format=%cI", "--", rel],
                                            cwd=root, text=True).strip()
        if not committed or _dt(committed) >= post:
            raise ProductionPostResultError("NO_PRE_START_GIT_COMMIT_WITNESS")
        from jra_candidate_postresult_closedloop import fetch_jra_result, verify_official_result
        stage="RESOLVE_FORMAL_INTENT"
        intent = _intent_for(root, race_id)
        stage="FETCH_OFFICIAL_RESULT"
        evidence = fetch_jra_result(intent["race_date"], intent["jra_source"]["jra_meeting_key"],
                                    int(intent["race_no"]))
        stage="VERIFY_OFFICIAL_RESULT"
        ranking = [str(x) for x in (final.get("static_prediction") or {}).get("ranking") or []]
        parsed = evidence['parsed']
        result_ids = [str(row.get('runner_id')) for row in
                      list(parsed.get('runners') or []) + list(parsed.get('non_finishers') or [])]
        # Normal existing RESULT retains the exact PR348 path and its existing
        # gates. Restore SOURCE only for unique extra result rows that could be
        # legitimate declared cancellations outside the frozen active set.
        if len(result_ids) == len(set(result_ids)) and set(result_ids) - set(ranking):
            stage="VERIFY_SIGNED_SOURCE_UNIVERSE"
            declared_ids, source_cancelled = _source_bound_result_universe(root, final)
            stage="VERIFY_OFFICIAL_RESULT"
            official = verify_official_result(parsed, evidence['text'], declared_ids,
                                             source_cancelled_runner_ids=source_cancelled)
        else:
            official = verify_official_result(parsed, evidence['text'], ranking)
        stage="SETTLE_IMMUTABLE_FINAL"
        req = build_result_request(final, official, evidence)
        cpre = root / "runtime" / "source_candidate_oos" / race_id / "pre_result.json"
        if cpre.exists():
            c = json.loads(cpre.read_text(encoding="utf-8"))
            req["candidate_shadow_ref"] = {"final_receipt_sha256": c.get("candidate_final_receipt_sha256"),
                                           "pre_result_sha256": c.get("sha256"),
                                           "production_effect": "NONE"}
        stage="PERSIST_RESULT_REQUEST"
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            with out.open('x',encoding='utf-8') as handle:
                handle.write(json.dumps(req,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
        except FileExistsError as exc:
            saved=json.loads(out.read_text(encoding='utf-8'))
            if saved!=req:
                raise ProductionPostResultError('RESULT_REQUEST_IMMUTABILITY_CONFLICT') from exc
            return 'ALREADY_RESULTED'
        if enroll_signer:
            from jra_result_submission import ResultSubmission
            ResultSubmission(root,_result_execution_id(final,race_id),req).enroll()
        return "RESULT_REQUEST_WRITTEN"
    except Exception as exc:
        if not getattr(exc,"first_failed_stage",None):exc.first_failed_stage=stage
        if evidence and evidence.get('raw_base64'):
            exc.result_failure_capture = {'capture_stage': 'RESULT_DETAIL', **{
                key: evidence.get(key)
                for key in ('url', 'captured_at', 'content_type', 'sha256', 'raw_base64', 'identity')
            }}
        raise


def write_result_failure_capture(directory, race_id, exc):
    """Keep original public response bytes only in the run's diagnostic artifact."""
    import base64
    from urllib.parse import urlsplit

    capture = getattr(exc, 'result_failure_capture', None)
    if not capture or not re.fullmatch(r'KM-JRA-[A-Z]{3}-\d{8}-R\d{2}', race_id):
        return None
    url = urlsplit(capture.get('url') or '')
    if url.scheme != 'https' or url.hostname != 'www.jra.go.jp' or url.username or url.password:
        return None
    raw = base64.b64decode(capture['raw_base64'], validate=True)
    if hashlib.sha256(raw).hexdigest() != capture.get('sha256'):
        raise ValueError('RESULT_FAILURE_CAPTURE_SHA_MISMATCH')
    record = {'scope': 'DIAGNOSTIC_ONLY_NOT_RESULT_ADMISSION', 'target_race_id': race_id,
              'first_failed_stage': getattr(exc, 'first_failed_stage', None),
              'error_code': str(exc).split(':', 1)[0], **capture}
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    filename = race_id + '-' + _sha(record) + '.json'
    (directory / filename).write_text(json.dumps(record, ensure_ascii=False, sort_keys=True),
                                      encoding='utf-8')
    return filename


def _saved_request(root, race_id):
    from jra_result_submission import ResultSubmission
    final=json.loads((root/'runtime/final_artifacts'/(race_id+'.json')).read_text(encoding='utf-8'))
    path=root/'runtime/results'/(race_id+'.json')
    request=json.loads(path.read_text(encoding='utf-8'))
    refs=request.get('frozen_prediction_ref') or {}
    if (final.get('race_id')!=race_id or request.get('race_id')!=race_id or request.get('result_lane')!='PRODUCTION'
            or refs.get('immutable_final_sha256')!=final.get('sha256')
            or refs.get('final_receipt_sha256')!=final.get('final_receipt_sha256')
            or (request.get('official_result') or {}).get('status')!='OFFICIAL'
            or (request.get('settlement') or {}).get('status')!='SETTLED'):
        raise ProductionPostResultError('RESULT_SAVED_REQUEST_FINAL_BINDING_MISMATCH')
    execution_id=_result_execution_id(final,race_id)
    return path,request,final,execution_id,ResultSubmission(root,execution_id,request)


def _saved_request_status(root,race_id):
    from execution_store import resolve_phase
    _,request,final,execution_id,submission=_saved_request(root,race_id)
    phase=resolve_phase(execution_id,'RESULT',root=root/'runtime/executions')
    if phase:
        files=phase['manifest']['files']
        if not {'result_request.json','result_receipt_envelope.json'}<=set(files):
            raise ProductionPostResultError('RESULT_SAVED_PHASE_INCOMPLETE')
        saved=json.loads((phase['run_dir']/'result_request.json').read_text(encoding='utf-8'))
        if saved!=request:
            raise ProductionPostResultError('RESULT_SAVED_PHASE_REQUEST_BINDING_MISMATCH')
        response=json.loads((phase['run_dir']/'result_receipt_envelope.json').read_text(encoding='utf-8'))
        _bind_result_response(request,response,final)
        review_path=root/'runtime/reviews_auto'/(race_id+'-AUTO.json')
        state_path=root/'runtime/learning_states'/(race_id+'.json')
        if review_path.is_file() and state_path.is_file():
            review=json.loads(review_path.read_text(encoding='utf-8'))
            state=json.loads(state_path.read_text(encoding='utf-8'))
            official=request['official_result']
            refs=request['frozen_prediction_ref']
            settlement=request['settlement']
            capital=review.get('capital') or {}
            review_sha=review.get('sha256')
            if (review.get('race_id')!=race_id or state.get('race_id')!=race_id
                    or review.get('immutable_final_artifact_sha256')!=refs['immutable_final_sha256']
                    or review.get('final_receipt_sha256')!=refs['final_receipt_sha256']
                    or review.get('official_top3')!=official['top3']
                    or review.get('official_top3_orders')!=official.get('top3_orders')
                    or review.get('official_finish_groups')!=official.get('finish_groups')
                    or capital.get('investment')!=settlement['total_investment']
                    or capital.get('settled_investment')!=settlement['effective_investment']
                    or capital.get('return')!=settlement['total_payout']
                    or review_sha!=_sha({k:v for k,v in review.items() if k!='sha256'})
                    or state.get('sha256')!=_sha({k:v for k,v in state.items() if k!='sha256'})
                    or state.get('source_review_sha256')!=review_sha):
                raise ProductionPostResultError('RESULT_SAVED_LEARNING_BINDING_MISMATCH')
            return 'ALREADY_RESULTED'
        return 'PENDING_RESULT_RUNNER'
    status,_=submission.state()
    if status in {'READY','RESPONSE_RECORDED'}:
        return 'PENDING_RESULT_RUNNER'
    return 'BLOCKED_RESULT_'+status


def pending_result_dispatches(root, rows):
    """Retry only unclaimed enrolled requests or exact returned envelopes."""
    paths = set()
    for row in rows:
        if row.get('status') not in {'PENDING_RESULT_RUNNER','RESULT_REQUEST_WRITTEN'}:
            continue
        race_id=row['race_id']
        if re.fullmatch(r'KM-JRA-[A-Z]{3}-\d{8}-R\d{2}',race_id) and _saved_request_status(root,race_id)=='PENDING_RESULT_RUNNER':
            paths.add('runtime/results/'+race_id+'.json')
    return sorted(paths)


def new_result_commit_paths(root, rows):
    """Stage enrollment with each completed request in one existing Git commit."""
    for row in rows:
        if row.get('status')!='RESULT_REQUEST_WRITTEN':
            continue
        path,_,_,_,submission=_saved_request(root,row['race_id'])
        if submission.state()[0]!='READY':
            raise ProductionPostResultError('RESULT_NEW_REQUEST_NOT_ENROLLED')
        yield path.relative_to(root).as_posix()
        yield (submission.path/'ENROLLED.json').relative_to(root).as_posix()


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", default=".")
    p.add_argument("--race-id")
    p.add_argument("--days", type=int, default=3)
    p.add_argument('--health-out')
    p.add_argument('--failure-raw-dir')
    p.add_argument('--dispatch-from-health')
    p.add_argument('--commit-from-health')
    p.add_argument('--enroll-signer',action='store_true')
    a = p.parse_args(argv)
    from jra_postresult_health import (build_execution_health,failure_row,
                                      write_execution_health,health_exit_code)
    root = Path(a.repo_root).resolve()
    if a.dispatch_from_health or a.commit_from_health:
        report = json.loads(Path(a.dispatch_from_health or a.commit_from_health).read_text(encoding='utf-8'))
        paths=pending_result_dispatches if a.dispatch_from_health else new_result_commit_paths
        for path in paths(root, report['processed']):
            print(path)
        return 0
    from jra_candidate_postresult_closedloop import PendingOfficialResult
    paths = ([root / "runtime" / "final_artifacts" / (a.race_id + ".json")] if a.race_id
             else sorted((root / "runtime" / "final_artifacts").glob("KM-JRA-*.json")))
    now = datetime.now(timezone.utc)
    results = []
    for f in paths:
        rid = f.stem
        row={'race_id':rid,'final_ref':f.relative_to(root).as_posix(),'persisted':False,
             'recommendation_pfs':None,'actual_purchase':'UNVERIFIED','actual_purchase_pfs':None}
        failure = None
        try:
            if not f.exists():
                results.append({**row,'status':'NO_PRODUCTION_FINAL'})
                continue
            fin=json.loads(f.read_text(encoding='utf-8'))
            row['frozen_final_sha256']=fin.get('sha256')
            row['source_ref']={'source_snapshot_sha256':fin.get('source_snapshot_sha256')}
            classification=legacy_final_classification(fin)
            if classification:
                results.append({**row,**classification})
                continue
            if not a.race_id:
                age = (now - _dt(fin.get("scheduled_post_at"))).total_seconds()
                if age < 0:
                    continue
                if age > a.days*86400:
                    # The discovery window governs new fetches only. A known
                    # enrolled request can finish after restart or day rollover.
                    if not a.enroll_signer or not (root/'runtime/results'/(rid+'.json')).is_file():
                        continue
                    stage=((fin.get('execution_stage_manifest') or {}).get('SIGNED_SOURCE_RECEIPT_VERIFIED') or {})
                    eid=stage.get('execution_id')
                    if not isinstance(eid,str) or not re.fullmatch(re.escape(rid)+r'-LIVE-R[1-9]\d*',eid):
                        continue
                    execution=root/'runtime/executions'/eid
                    enrolled=(execution/'RESULT_SUBMISSION'/'ENROLLED.json').is_file()
                    prior_response=(execution/'RESULT'/'LATEST.json').is_file() and not (
                        (root/'runtime/reviews_auto'/(rid+'-AUTO.json')).is_file()
                        and (root/'runtime/learning_states'/(rid+'.json')).is_file())
                    if not enrolled and not prior_response:
                        continue
                    if _saved_request_status(root,rid)=='ALREADY_RESULTED':
                        continue
            status = process(root,rid,now=now,**({'enroll_signer':True} if a.enroll_signer else {}))
            row.update(status=status,persisted=status=='RESULT_REQUEST_WRITTEN')
        except PendingOfficialResult as e:
            failure = e
            row.update(status='PENDING_OFFICIAL_RESULT',
                       first_failed_stage=getattr(e, 'first_failed_stage', None) or 'FETCH_OFFICIAL_RESULT',
                       exception_class=type(e).__name__,error_code=str(e).split(':',1)[0],error=str(e))
        except Exception as e:  # report, never fabricate
            failure = e
            row=failure_row(rid,e,'PRODUCTION_RESULT',**{k:v for k,v in row.items() if k!='race_id'})
        if failure is not None and a.failure_raw_dir:
            try:
                capture = write_result_failure_capture(a.failure_raw_dir, rid, failure)
                if capture:
                    row['failure_raw_artifact'] = capture
            except (OSError, ValueError) as capture_error:
                row['failure_raw_artifact_error'] = type(capture_error).__name__
        results.append(row)
    report=build_execution_health('PRODUCTION',results)
    report['profile']=PROFILE
    if a.health_out:write_execution_health(a.health_out,report)
    print(json.dumps(report,ensure_ascii=False))
    return health_exit_code(report)


if __name__ == "__main__":
    raise SystemExit(main())
