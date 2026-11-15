"""Dormant one-Race future PAPER study of the two existing selection hypotheses.

An exact separate Owner decision is required. This does not adopt a Production
selection policy, change the original strict MEC, admit SOURCE, start KRS, or
grant purchase/Delivery authority. No default decision or enabled Profile is
created by this module.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
import fcntl
import json
import re
from pathlib import Path

from runtime import local_fnb_research_runtime as private
from runtime import local_fnb_mec_failure_localization as comparison
from runtime import local_fnb_semantic_closure as semantic

PROFILE = 'KM-FNB-ONE-FUTURE-RACE-SELECTION-PAPER-STUDY-v1'
DECISION_PROFILE = 'KM-FNB-BOUNDED-FUTURE-SELECTION-PAPER-DECISION-v1'
SCOPE = 'LOCAL_FNB_ONE_FUTURE_RACE_PAPER_ONLY_NOT_PRODUCTION_NOT_OOS'
PIN_PATHS = ('runtime/local_fnb_selection_study.py',
    'runtime/local_fnb_research_runtime.py',
    'runtime/local_fnb_mec_failure_localization.py', 'runtime/local_fnb_semantic_closure.py',
    'runtime/minimum_efficient_coverage.py', 'runtime/local_fnb_context_static_candidate.py',
    'runtime/capital_policy.py', 'runtime/jra_ticket_tree_renderer.py',
    'profiles/family_user_capital_default_20261003_R1.json',
    'profiles/local_fnb_context_static_candidate_v0.1_20261103.json',
    'profiles/local_fnb_pair_local_semantic_protection_research_v0.1_20261103.json',
    'profiles/local_fnb_unknown_paths_protection_research_v0.1_20261103.json')


def _now():
    return datetime.now(timezone.utc)


def required_pins():
    return {name:private.digest((private.REPO/name).read_bytes()) for name in PIN_PATHS}


def verify_decision(decision, *, request, prediction):
    """Verify the supplied pinned instruction record; never issue approval."""
    if decision.get('decision') != 'APPROVED_BOUNDED_PRIVATE_FUTURE_PAPER_STUDY':
        raise private.ResearchHold('SELECTION_STUDY_OWNER_DECISION_PENDING')
    authority = decision.get('authority_evidence') or {}
    race_match = re.fullmatch(r'KM-LOCAL-FNB-(\d{8})-R(0[1-9]|1[0-2])(?:-[A-Za-z0-9_]+)*',
        str(request.get('race_id') or ''))
    if (decision.get('profile') != DECISION_PROFILE or decision.get('scope') != SCOPE
            or decision.get('race_id') != request.get('race_id')
            or prediction.get('race_id') != request.get('race_id')
            or request.get('family_id') != 'LOCAL' or request.get('venue_id') != 'FNB' or not race_match
            or decision.get('max_races') != 1 or type(decision.get('max_races')) is not int
            or decision.get('max_new_krs_starts') != 0
            or type(decision.get('max_new_krs_starts')) is not int
            or decision.get('code_and_profile_pins') != required_pins()
            or authority.get('type') != 'DIRECT_USER_INSTRUCTION_IN_CURRENT_CHAT'
            or not authority.get('request_id') or not authority.get('approval_ref')
            or authority.get('owner_identity_confirmed_by_direct_instruction') is not True
            or authority.get('record_is_crypto_signature') is not False
            or any(decision.get(key) is not False for key in
                ('production_adoption','original_strict_mec_changed','source_scope_changed',
                 'registered_oos_authorized','actual_purchase_authorized','paid_resources_authorized'))):
        raise private.ResearchHold('SELECTION_STUDY_EXACT_DECISION_SCOPE_OR_PINS_MISMATCH')
    semantic._validate(prediction)
    if prediction['model_code_sha256'] != private.MODEL_SHA:
        raise private.ResearchHold('SELECTION_STUDY_FIXED_MODEL_MISMATCH')
    effective = private._stamp(decision['effective_from'])
    until = private._stamp(decision['effective_until'])
    approved_at = private._stamp(decision['authorization_observed_at'])
    cutoff = private._stamp(request['prediction_cutoff'])
    post = private._stamp(request['scheduled_post_at'])
    frozen = private._stamp(prediction['freeze_at'])
    observed = private._stamp(_now())
    if post.astimezone(timezone(timedelta(hours=9))).strftime('%Y%m%d') != race_match.group(1):
        raise private.ResearchHold('SELECTION_STUDY_POST_DATE_RACE_ID_MISMATCH')
    if not approved_at <= effective <= frozen <= observed < until <= cutoff < post:
        raise private.ResearchHold('SELECTION_STUDY_NOT_FUTURE_EFFECTIVE_NO_RETROACTIVE_PROMOTION')
    return {'scope':SCOPE,'race_id':request['race_id'],'effective_from':effective.isoformat(),
        'effective_until':until.isoformat(),'verified_at':observed.isoformat(),
        'approval_ref':authority['approval_ref'],'max_races':1,'max_new_krs_starts':0,
        'source_or_production_authority_granted':False}


def run_study(*, decision_path, decision_sha256, prediction_path, prediction_sha256,
              request, private_root):
    """Run only the explicitly authorized future PAPER study; no network/KRS."""
    decision_bytes = private._pinned(decision_path,decision_sha256)
    prediction_bytes = private._pinned(prediction_path,prediction_sha256)
    decision,prediction = json.loads(decision_bytes),json.loads(prediction_bytes)
    verified = verify_decision(decision,request=request,prediction=prediction)
    recipe = {'decision_sha256':decision_sha256,'prediction_sha256':prediction_sha256,
        'request_sha256':private.digest(private.encoded(request)),
        'code_and_profile_pins':required_pins()}
    # One direct approval owns one slot. Re-encoding its JSON or changing an
    # input revision cannot buy a second dispatch under the same instruction.
    authority = decision['authority_evidence']
    slot = semantic._sha({'profile':PROFILE,'scope':SCOPE,
        'owner_request_id':authority['request_id'],'approval_ref':authority['approval_ref']})
    root = private._private_root(Path(private_root)/slot)
    lock = root/'.selection_study.lock'
    if lock.is_symlink():
        raise private.ResearchHold('PRIVATE_STORE_SYMLINK_FORBIDDEN')
    with lock.open('a') as handle:
        fcntl.flock(handle,fcntl.LOCK_EX | fcntl.LOCK_NB)
        final = root/'selection_study_manifest.json'
        if (root/'finalization_failure.json').exists():
            raise private.ResearchHold('SELECTION_STUDY_FINAL_SAVE_FAILED_NOT_COMPLETE')
        if final.exists():
            saved = private._verify_saved_manifest(final)
            if saved.get('profile') != PROFILE or saved.get('input_recipe') != recipe:
                raise private.ResearchHold('SELECTION_STUDY_ONE_RACE_SLOT_ALREADY_USED')
            return {**saved,'completion_reused':True,'new_krs_executions':0}
        if (root/'execution_claim.json').exists():
            raise private.ResearchHold('SELECTION_STUDY_PARTIAL_CLAIM_NO_AUTOMATIC_REDISPATCH')
        private._immutable(root/'execution_claim.json',private.encoded({
            'profile':PROFILE,'race_id':request['race_id'],'input_recipe':recipe,
            'claimed_at':_now().isoformat(),'max_races':1,'max_new_krs_starts':0}))
        private._immutable(root/'owner_decision_original.json',decision_bytes)
        private._immutable(root/'prediction_original.json',prediction_bytes)
        private._immutable(root/'race_request.json',private.encoded(request))
        result = comparison.paper_comparison(prediction,evaluated_at=_now().isoformat(),
            authorization_ref=verified['approval_ref'])
        private._immutable(root/'separate_unadopted_selection_paper_comparison.json',private.encoded(result))
        verify_decision(decision,request=request,prediction=prediction)
        inventory = [{'path':str(p.relative_to(root)),'sha256':private.digest(p.read_bytes())}
            for p in sorted(root.rglob('*')) if p.is_file() and p.name!='.selection_study.lock']
        manifest = {'profile':PROFILE,'classification':SCOPE,'race_id':request['race_id'],
            'input_recipe':recipe,'separate_owner_study_permission':verified,
            'private_artifacts':inventory,'completed_at':_now().isoformat(),
            'new_krs_executions':0,'formal_final':False,'source_admitted':False,
            'original_strict_mec_hold_lifted':False,'production_policy_adopted':False,
            'actual_purchase':False,'recipient_delivery_proven':False,'registered_OOS_increment':0}
        private._immutable(final,private.encoded(manifest))
        try:
            verify_decision(decision,request=request,prediction=prediction)
        except private.ResearchHold:
            private._immutable(root/'finalization_failure.json',private.encoded({
                'status':'SELECTION_STUDY_FINAL_SAVE_OUTSIDE_APPROVED_WINDOW',
                'observed_at':_now().isoformat(),'race_id':request['race_id']}))
            raise
        return {**manifest,'completion_reused':False}
