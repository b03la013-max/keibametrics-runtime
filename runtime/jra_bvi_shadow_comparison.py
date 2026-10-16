"""Measurement-only bloodline ablation, using the existing numerical consumers.

No arm is a FINAL or has purchase authority. Enhanced equals Current until an
eligible, separately frozen richer official input is supplied; no invented gain.
"""
import copy
from datetime import datetime, timezone
from jra_evidence_to_base_production import attach_production_ledger_to_request
from jra_index_provenance_builder import materialize_index_provenance
from jra_static_owner_executable import compile_static_owner
from jra_krs_input_builder_production import build_krs_input

PEDIGREE_FEATURES = frozenset(('pedigree_surface', 'pedigree_distance', 'pedigree_class',
    'maternal_class_signal', 'sire_track_signal', 'sire_newcomer_signal',
    'physical_pedigree_fit', 'sprint_pedigree'))


def compare(prepared, mapping, *, source_sha, receipt_sha, algorithm_freeze_at, cutoff,
            enhanced_features=None, source_artifact=None, current_authority=None, root=None):
    """Recompute A/B/C; caller owns temporal authentication and freeze publication.

    Removing a pedigree-derived distance_fit also ablates its CFI contribution.
    C retains the authorized missing-information DCR policy, never a new weight.
    KRS inputs are evaluated, not a claim that simulation/MEC/Capital executed.
    """
    arms = {}
    for name in ('A_CURRENT', 'B_PEDIGREE_ENHANCED_SHADOW', 'C_BLOODLINE_ABLATION'):
        req = copy.deepcopy(prepared)
        for runner in req['runners']:
            features = runner['evidence_features']
            if name.startswith('B_') and enhanced_features is not None:
                # Non-pedigree information remains identical in every arm.
                for key, spec in enhanced_features.get(str(runner['runner_id']), {}).items():
                    if key in PEDIGREE_FEATURES:
                        features[key] = copy.deepcopy(spec)
            if name.startswith('C_'):
                runner['evidence_features'] = {k:v for k,v in features.items()
                    if k not in PEDIGREE_FEATURES
                    and v.get('source_authority') != 'JRA_OFFICIAL_POINT_IN_TIME_CORPUS'}
        req = materialize_index_provenance(attach_production_ledger_to_request(req, mapping))
        calculated_at = datetime.now(timezone.utc).isoformat()
        owner = compile_static_owner(req, source_snapshot_sha256=source_sha,
            source_receipt_sha256=receipt_sha, frozen_at=algorithm_freeze_at,
            prediction_cutoff=cutoff)
        if current_authority is not None:
            from jra_aki_v21 import apply_authorized_v21
            from minimum_efficient_coverage import _active_roles
            req.update({k:copy.deepcopy(owner[k]) for k in ('static_prediction','role_registry',
                'pair_dispositions','third_dispositions','purchased_heads')})
            req=apply_authorized_v21(req,source_artifact,current_authority,root=root)
            for key in ('static_prediction','role_registry','pair_dispositions','third_dispositions','purchased_heads'):
                owner[key]=copy.deepcopy(req[key])
            roles=_active_roles(req)
            owner['active_columns']={col:[str(r['runner_id']) for r in req['runners']
                if col in roles[str(r['runner_id'])]] for col in ('W','P2','P3')}
            owner['official_aki_verification']=req.get('official_aki_verification')
            owner['production_authority']=False;owner['purchase_authority']=False
            for field in ('role_registry','pair_dispositions','third_dispositions'):
                for row in owner[field]:
                    row['production_authority']=False;row['purchase_authority']=False
            from jra_static_owner_forward_oos import sha
            owner['sha256']=sha({k:v for k,v in owner.items() if k!='sha256'})
        krs = build_krs_input(req)['krs_input_data']
        arms[name] = {'owner': owner, 'krs_input': krs,
            'numerical_calculated_at':calculated_at,
            'bvi': {str(r['runner_id']):r['canonical_components']['BVI'] for r in req['runners']},
            'numerical_provenance_sha256':req['index_provenance_hash'],
            'numerical_runners':copy.deepcopy(req['runners']),
            'candidate_only': True, 'production_authority': False, 'purchase_authority': False,
            'krs_simulation_executed': False, 'mec_executed': False,
            'ticket_count': None, 'capital_required': None}
    from jra_static_owner_forward_oos import sha
    a,b=arms['A_CURRENT'],arms['B_PEDIGREE_ENHANCED_SHADOW']
    return {'arms': arms, 'enhanced_input_supplied': enhanced_features is not None,
        'enhanced_input_distinct':sha([r['evidence_features'] for r in a['numerical_runners']])!=sha([r['evidence_features'] for r in b['numerical_runners']]),
        'enhanced_bvi_artifact_distinct':sha(a['bvi'])!=sha(b['bvi']),
        'enhanced_bvi_distinct':any(a['bvi'][rid]['value']!=b['bvi'][rid]['value'] for rid in a['bvi']),
        'enhanced_ranking_distinct':a['owner']['static_prediction']['ranking']!=b['owner']['static_prediction']['ranking'],
        'same_runner_universe': True, 'same_mapping_and_cutoff': True,
        'production_effect': 'NONE', 'predictive_improvement_demonstrated': False,
        'policy_scope': ('CURRENT_AUTHORITY_REGISTERED_COLUMNS / CURRENT_PRODUCTION_POLICY_SHADOW' if current_authority is not None else 'CURRENT_NUMERICAL_MAPPING / EXISTING_STATIC_OWNER_EXECUTABLE_SHADOW; NOT A NEW PRODUCTION FINAL')}


def bind_jra_static_role_trace(utility, request):
    """JRA measurement consumer repair; Common/LOCAL definitions stay frozen."""
    if request.get('family_id')!='JRA':raise ValueError('JRA_STATIC_TRACE_FAMILY_MISMATCH')
    from krs_prediction_utility import _request_static_roles
    from jra_static_owner_forward_oos import sha
    bound=copy.deepcopy(utility);roles=_request_static_roles(request)
    for row in bound['summary']:
        row['static_roles']=sorted(roles.get(int(row['horse_no']),set()))
    bound['static_role_binding']='JRA_COMPARISON_FORMAL_ROLE_REGISTRY / NO PRODUCTION CHANGE'
    bound['sha256']=sha({k:v for k,v in bound.items() if k!='sha256'})
    return bound


def execute_diagnostic_downstream(comparison, prepared, official, call):
    """Real external candidate KRS plus existing MEC/Capital, never a FINAL.

    `call` must execute /krs/execute and independently verify /verify. Historical
    payout use is explicitly virtual diagnosis, never a forward-OOS result.
    """
    from jra_candidate_krs_plan import (build_candidate_krs_payload,
        verify_candidate_krs_execution, ACCEPTANCE_INPUT_CLASS, INPUT_CLASS)
    from krs_prediction_utility import build_krs_prediction_utility, evaluate_against_result
    from minimum_efficient_coverage import build_mec_plan, validate_mec_plan
    from capital_policy import resolve_capital_policy
    from mec_r4_shadow import settle_ticket_list
    for name, arm in comparison['arms'].items():
        req=copy.deepcopy(prepared)
        req['runners']=copy.deepcopy(arm['numerical_runners'])
        req.update({k:copy.deepcopy(arm['owner'][k]) for k in
            ('static_prediction','role_registry','pair_dispositions','third_dispositions','purchased_heads')})
        # A distinct diagnostic identity cannot overwrite the real race's runs.
        req['race_id']=prepared['race_id']+('-BVI-FORWARD-SHADOW' if official is None else '-BVI-POSTCAPTURE-DIAGNOSTIC')
        req['candidate_only']=True;req['production_authority']=False
        req['krs_input_data']=copy.deepcopy(arm['krs_input'])
        req['krs_input_data']['race']['race_id']=req['race_id']
        for r in req['runners']:
            r['static_roles']=req['static_prediction']['roles'][str(r['runner_id'])]
        payload=build_candidate_krs_payload(req,input_class=INPUT_CLASS if official is None else ACCEPTANCE_INPUT_CLASS)
        response=call('/krs/execute',payload,420)
        receipt=verify_candidate_krs_execution(payload,response)
        verified=call('/verify',response['run_receipt'],30)
        if verified.get('valid') is not True:raise ValueError('BVI_SHADOW_KRS_SIGNATURE_INVALID')
        utility=bind_jra_static_role_trace(build_krs_prediction_utility(req,response),req)
        mec=build_mec_plan(req,utility,strict_head_closure=True,min_stake=100)
        validate_mec_plan(mec)
        capital=resolve_capital_policy(req,mec)
        tickets=mec['tickets'] if not capital['no_bet'] else []
        arm.update(krs_simulation_executed=True,mec_executed=True,
            krs_signed_run_receipt=response['run_receipt'],krs_output=response['output'],
            krs_receipt_verified=True,krs_utility=utility,
            krs_result_utility=None,
            mec=mec,capital_policy_decision=capital,ticket_count=len(tickets),
            capital_required=capital['required_capital'],diagnostic_tickets=tickets,
            diagnostic_virtual_settlement=None,
            settlement_classification='POSTCAPTURE VIRTUAL DIAGNOSTIC / NOT FROZEN FORWARD OOS / NO PURCHASE',
            purchase_authority=False,production_authority=False)
        if official is not None:
            payout_result={'official_result':{'top3':official['top3'],
                'payouts':{k:v['per_100_yen'] for k,v in official['payouts'].items()}}}
            arm['diagnostic_virtual_settlement']=settle_ticket_list(tickets,payout_result)
            arm['krs_result_utility']=evaluate_against_result(utility,official['top3'],
                static_ranking=arm['owner']['static_prediction']['ranking'])
        else:
            arm['settlement_classification']='FROZEN_FORWARD_SHADOW / NO RESULT AVAILABLE / NO PURCHASE'
    return comparison
