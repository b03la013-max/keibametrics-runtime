"""Measurement-only bloodline ablation, using the existing numerical consumers.

No arm is a FINAL or has purchase authority. Enhanced equals Current until an
eligible, separately frozen richer official input is supplied; no invented gain.
"""
import copy
from datetime import datetime, timezone
import math
import re
from jra_evidence_to_base_production import attach_production_ledger_to_request
from jra_index_provenance_builder import materialize_index_provenance, BASE, DERIVED
from jra_static_owner_executable import compile_static_owner
from jra_krs_input_builder_production import build_krs_input

PEDIGREE_FEATURES = frozenset(('pedigree_surface', 'pedigree_distance', 'pedigree_class',
    'maternal_class_signal', 'sire_track_signal', 'sire_newcomer_signal',
    'physical_pedigree_fit', 'sprint_pedigree'))

ENV_SHADOW_PROFILE = 'KM-JRA-BVI-ENV-SHADOW-COMPARISON-v1'
ENV_SHADOW_MAPPING = 'BVI-ENV-REGULARIZED-RESEARCH-SCORE-v1-NON-PRODUCTION'


def _sha(obj):
    from jra_static_owner_forward_oos import sha
    return sha(obj)


def _research_only(owner):
    """Never let the reused registry executor's transport labels enact D."""
    owner['candidate_only'] = True
    owner['production_authority'] = False
    owner['purchase_authority'] = False
    owner['static_prediction']['production_authority'] = False
    owner['static_prediction']['candidate_only'] = True
    for field in ('role_registry', 'pair_dispositions', 'third_dispositions'):
        for row in owner[field]:
            row['production_authority'] = False
            row['purchase_authority'] = False
            row['candidate_only'] = True
    owner['sha256'] = _sha({k:v for k,v in owner.items() if k!='sha256'})
    return owner


def compile_research_static(request, baseline_request, baseline_owner, *,
                            source_artifact, current_authority, root):
    """Use unchanged registered AKI selection for explicitly non-Production D.

    The R51 Production Static policy file is byte-bound by Authority. It is
    deliberately NOT edited or called with falsely relabelled candidate data.
    The existing formula registry makes ZAI_WIN/PLACE independent of BVI.
    Therefore D may reuse B's complete ranking only after exact equality is
    checked; the unchanged registered executor then recalculates role, Pair
    and Third selection from D's actual Full20. This is not a Formal proof.
    """
    if (request.get('candidate_only') is not True
            or request.get('production_authority') is not False
            or request.get('purchase_authority') is not False):
        raise ValueError('ENV_SHADOW_EXPLICIT_RESEARCH_AUTHORITY_REQUIRED')
    activation = (((current_authority or {}).get('family_scoped_authority') or {})
                  .get('JRA') or {}).get('aki_v21_activation') or {}
    if activation.get('status') != 'PRODUCTION_AUTHORIZED':
        raise ValueError('ENV_SHADOW_CURRENT_AUTHORITY_REQUIRED')
    proof = request.get('environment_shadow_proof') or {}
    if (proof.get('profile') != ENV_SHADOW_PROFILE
            or proof.get('sha256') != _sha({k:v for k,v in proof.items() if k!='sha256'})
            or proof.get('source_snapshot_sha256') != source_artifact.get('source_snapshot_sha256')
            or proof.get('baseline_owner_sha256') != baseline_owner.get('sha256')
            or baseline_owner.get('sha256') != _sha({k:v for k,v in baseline_owner.items() if k!='sha256'})
            or proof.get('numerical_runners_sha256') != _sha(request['runners'])):
        raise ValueError('ENV_SHADOW_STATIC_PROOF_BINDING_INVALID')
    if (request.get('race_id') != baseline_request.get('race_id')
            or request.get('prediction_cutoff') != baseline_request.get('prediction_cutoff')
            or request.get('source_snapshot_sha256') != baseline_request.get('source_snapshot_sha256')):
        raise ValueError('ENV_SHADOW_STATIC_SOURCE_OR_CUTOFF_CHANGED')
    baseline = {str(r['runner_id']):r for r in baseline_request['runners']}
    current = {str(r['runner_id']):r for r in request['runners']}
    if len(current) != len(request['runners']) or set(current) != set(baseline):
        raise ValueError('ENV_SHADOW_STATIC_RUNNER_UNIVERSE_CHANGED')
    for rid,row in current.items():
        cc = row.get('canonical_components') or {}
        if set(cc) != set(BASE)|set(DERIVED):
            raise ValueError('ENV_SHADOW_FULL20_REQUIRED:'+rid)
        for key,spec in cc.items():
            value = spec.get('value')
            if (isinstance(value,bool) or not isinstance(value,(int,float))
                    or not math.isfinite(value) or not 0 <= value <= 100
                    or not spec.get('mapping_version') or not spec.get('rule_id')
                    or not spec.get('source_fact') or not spec.get('evidence_refs')
                    or spec.get('candidate_only') is not True
                    or spec.get('production_authority') is not False):
                raise ValueError('ENV_SHADOW_NUMERICAL_PROVENANCE_INVALID:'+rid+':'+key)
        # No silent change to other Base inputs, DCR or the ranking metrics.
        for key in [k for k in BASE if k!='BVI']+['DCR','ZAI_WIN','ZAI_PLACE']:
            if cc[key]['value'] != baseline[rid]['canonical_components'][key]['value']:
                raise ValueError('ENV_SHADOW_CONTROLLED_INDEX_CHANGED:'+rid+':'+key)
    from jra_aki_v21 import apply_authorized_v21
    from minimum_efficient_coverage import _active_roles
    req = copy.deepcopy(request)
    req.update({k:copy.deepcopy(baseline_owner[k]) for k in
        ('static_prediction','role_registry','pair_dispositions','third_dispositions','purchased_heads')})
    req = apply_authorized_v21(req,source_artifact,current_authority,root=root)
    owner = copy.deepcopy(baseline_owner)
    owner.update({k:copy.deepcopy(req[k]) for k in
        ('static_prediction','role_registry','pair_dispositions','third_dispositions','purchased_heads')})
    roles = _active_roles(req)
    owner['active_columns'] = {col:[str(r['runner_id']) for r in req['runners']
        if col in roles[str(r['runner_id'])]] for col in ('W','P2','P3')}
    owner['profile'] = ENV_SHADOW_PROFILE
    owner['static_prediction']['authority'] = ENV_SHADOW_PROFILE
    owner['static_prediction']['status'] = 'RESEARCH_ONLY / NOT PRODUCTION STATIC'
    owner['registered_aki_shadow_replay'] = req.get('official_aki_verification')
    owner.pop('official_aki_verification',None)
    owner['environment_shadow_proof_sha256'] = proof['sha256']
    owner['ranking_reuse_basis'] = 'BVI_HAS_NO_ZAI_WIN_OR_ZAI_PLACE_COEFFICIENT; EXACT_VALUE_EQUALITY_CHECKED'
    return _research_only(owner)


def _validate_prediction_input(prediction, rid, source, request):
    payload = prediction.get('input')
    if (not isinstance(payload,dict) or set(payload) != {'runner','environment'}
            or not isinstance(payload['runner'],dict) or not isinstance(payload['environment'],dict)
            or _sha(payload) != prediction.get('input_sha256')
            or str(payload['runner'].get('runner_id')) != rid):
        raise ValueError('ENV_SHADOW_PREDICTION_INPUT_HASH_INVALID:'+rid)
    detail = source.get('jra_official_race_card_detail') or {}
    card = {str(r.get('runner_id') or r.get('horse_no')):r for r in detail.get('runners') or []}
    if rid not in card:
        raise ValueError('ENV_SHADOW_RUNNER_NOT_IN_SOURCE:'+rid)
    history = ((source.get('jra_official_horse_history') or {}).get('runners') or {}).get(rid) or {}
    pedigree = history.get('pedigree') or {}
    runner = payload['runner']
    name = runner.get('horse_name') or runner.get('name')
    if name and name != card[rid].get('horse_name'):
        raise ValueError('ENV_SHADOW_RUNNER_NAME_SOURCE_MISMATCH:'+rid)
    if history.get('horse_name') and history['horse_name'] != card[rid].get('horse_name'):
        raise ValueError('ENV_SHADOW_SOURCE_HISTORY_NAME_CONFLICT:'+rid)
    for key in ('sire','dam','damsire'):
        a,b = card[rid].get(key),pedigree.get(key)
        if a and b and a!=b:
            raise ValueError('ENV_SHADOW_SOURCE_PARENT_CONFLICT:'+rid+':'+key)
        observed = a or b
        supplied = runner.get(key)
        if supplied and supplied!=observed:
            raise ValueError('ENV_SHADOW_PARENT_SOURCE_MISMATCH:'+rid+':'+key)
        if prediction.get('usable_for_shadow_override') is True and key in ('sire','dam') and not supplied:
            raise ValueError('ENV_SHADOW_PARENT_INPUT_MISSING:'+rid+':'+key)
    # The model's individual-ability control reads runs. An input hash alone
    # cannot establish those labels came from this SOURCE/runner: an empty,
    # shortened or invented history would otherwise alter the fitted control.
    observed_runs = history.get('runs') or card[rid].get('recent_runs') or []
    if not isinstance(observed_runs,list):
        raise ValueError('ENV_SHADOW_SOURCE_HISTORY_INVALID:'+rid)
    if observed_runs and 'runs' not in runner:
        raise ValueError('ENV_SHADOW_SOURCE_HISTORY_INPUT_REQUIRED:'+rid)
    if 'runs' in runner and (not isinstance(runner['runs'],list) or runner['runs'] != observed_runs):
        raise ValueError('ENV_SHADOW_HISTORY_SOURCE_MISMATCH:'+rid)
    top_context = source.get('jra_race_context') or {}
    detail_context = detail.get('race_context') or {}
    for key in ('venue_name','surface','distance_m','going','race_date','weather','race_class','course_variant'):
        a,b = top_context.get(key),detail_context.get(key)
        if a not in (None,'') and b not in (None,'') and str(a)!=str(b):
            raise ValueError('ENV_SHADOW_SOURCE_ENVIRONMENT_CONFLICT:'+key)
    context = top_context or detail_context
    race = request.get('race') or {}
    observed_env = detail.get('race_environment') or {}
    for key in ('going','weather'):
        a,b = context.get(key),observed_env.get(key)
        if a not in (None,'') and b not in (None,'') and str(a)!=str(b):
            raise ValueError('ENV_SHADOW_SOURCE_ENVIRONMENT_CONFLICT:'+key)
    expected = {'venue':context.get('venue_name') or race.get('venue'),
        'surface':context.get('surface') or race.get('surface'),
        'distance_m':context.get('distance_m') or race.get('distance'),
        'going':context.get('going') or observed_env.get('going'),
        'race_date':context.get('race_date') or request.get('race_date'),
        'weather':context.get('weather') or observed_env.get('weather')}
    for key,value in payload['environment'].items():
        if key not in expected or value in (None,''):
            continue
        match = str(value) == str(expected[key])
        if key=='distance_m':
            try:match=not isinstance(value,bool) and int(value)==int(expected[key])
            except (TypeError,ValueError):match=False
        if not match:
            raise ValueError('ENV_SHADOW_ENVIRONMENT_SOURCE_MISMATCH:'+rid+':'+key)


def _environment_arm(base_request, base_arm, predictions, model_sha, *,
                     source_artifact, current_authority, root,
                     calculated_at=None, diagnostic_cutoff=None):
    if not re.fullmatch(r'[0-9a-f]{64}',str(model_sha or '')):
        raise ValueError('ENV_SHADOW_MODEL_SHA_REQUIRED')
    if not isinstance(predictions,dict):
        raise ValueError('ENV_SHADOW_PREDICTIONS_REQUIRED')
    req = copy.deepcopy(base_request)
    ids = {str(r['runner_id']) for r in req['runners']}
    if set(predictions) != ids:
        raise ValueError('ENV_SHADOW_PREDICTION_RUNNER_UNIVERSE_MISMATCH')
    overrides, fallbacks = [], {}
    for rid in sorted(ids):
        pred = predictions[rid]
        if (not isinstance(pred,dict) or pred.get('model_sha256') != model_sha
                or str(pred.get('runner_id')) != rid
                or not re.fullmatch(r'[0-9a-f]{64}',str(pred.get('input_sha256') or ''))
                or pred.get('production_authority') is not False
                or pred.get('purchase_authority') is not False):
            raise ValueError('ENV_SHADOW_PREDICTION_BINDING_INVALID:'+rid)
        _validate_prediction_input(pred,rid,source_artifact,req)
        if pred.get('usable_for_shadow_override') is not True:
            fallbacks[rid] = copy.deepcopy(pred.get('reasons') or ['INSUFFICIENT_DATA'])
            continue
        score = pred.get('score')
        if isinstance(score,bool) or not isinstance(score,(float,int)) or not math.isfinite(score) or not 0 <= score <= 100:
            raise ValueError('ENV_SHADOW_SCORE_INVALID:'+rid)
        previous = req['index_provenance_ledger']['runners'][rid]['base_indices']['BVI']
        req['index_provenance_ledger']['runners'][rid]['base_indices']['BVI'] = {
            'value':score,'rule_id':'BVI-ENV-REGULARIZED-SHADOW-v1',
            'mapping_version':ENV_SHADOW_MAPPING,
            'evidence_refs':['BVI_ENV_MODEL:'+model_sha,'BVI_ENV_INPUT:'+pred['input_sha256'],
                             'BVI_ENV_PREDICTION:'+_sha(pred)],
            'source_fact':'Fitted normalized-finish research score; NOT authorized Production BVI/category; '+
                          'baseline_BVI='+str(previous['value']),
            'components':copy.deepcopy(pred.get('components') or []),
            'profile':ENV_SHADOW_PROFILE,'information_status':'RESEARCH_MODEL_ESTIMATE_NOT_MEASURED_PRODUCTION_BVI',
            'dcr':copy.deepcopy(previous.get('dcr')),'baseline_production_bvi':copy.deepcopy(previous),
            'candidate_only':True,'production_authority':False,'purchase_authority':False,
        }
        overrides.append(rid)
    req = materialize_index_provenance(req)
    req['candidate_only']=True;req['production_authority']=False;req['purchase_authority']=False
    req['base_index_mapping_authority'] = {
        'mapping_id':ENV_SHADOW_MAPPING,'baseline_mapping_id':base_request['base_index_mapping_authority']['mapping_id'],
        'production_authority':False,'candidate_only':True,'model_sha256':model_sha}
    for row in req['runners']:
        for cell in row['canonical_components'].values():
            cell.update(candidate_only=True,production_authority=False,purchase_authority=False)
    actual_now = datetime.now(timezone.utc)
    calculation = datetime.fromisoformat(str(calculated_at or actual_now.isoformat()).replace('Z','+00:00'))
    if calculation.tzinfo is None or abs((actual_now-calculation).total_seconds()) > 30:
        raise ValueError('ENV_SHADOW_ACTUAL_CALCULATION_TIME_REQUIRED')
    original_cutoff = datetime.fromisoformat(str(req['prediction_cutoff']).replace('Z','+00:00'))
    if original_cutoff.tzinfo is None:
        raise ValueError('ENV_SHADOW_CUTOFF_TIMEZONE_REQUIRED')
    if diagnostic_cutoff is not None:
        diag = datetime.fromisoformat(str(diagnostic_cutoff).replace('Z','+00:00'))
        if diag.tzinfo is None or diag < calculation:
            raise ValueError('ENV_SHADOW_DIAGNOSTIC_CUTOFF_INVALID')
    proof = {'profile':ENV_SHADOW_PROFILE,'source_snapshot_sha256':req['source_snapshot_sha256'],
        'prediction_cutoff':req['prediction_cutoff'],'model_sha256':model_sha,
        'calculated_at':calculation.isoformat(),'diagnostic_cutoff':diagnostic_cutoff,
        'execution_class':('POST_CAPTURE_DIAGNOSTIC' if calculation>original_cutoff
                           else 'PRE_CUTOFF_RESEARCH_SHADOW_NOT_OOS_YET'),
        'predictions_sha256':_sha(predictions),'baseline_owner_sha256':base_arm['owner']['sha256'],
        'numerical_runners_sha256':_sha(req['runners']),'formula_replay_sha256':req['index_provenance_hash'],
        'overridden_runner_ids':overrides,'fallback_runner_reasons':fallbacks,
        'production_effect':'NONE','production_authority':False,'purchase_authority':False,
        'classification':'RESEARCH_ONLY / NO FORMAL STATIC OR BVI CONSUMPTION CLAIM'}
    proof['sha256']=_sha(proof);req['environment_shadow_proof']=proof
    owner = compile_research_static(req,base_request,base_arm['owner'],source_artifact=source_artifact,
                                    current_authority=current_authority,root=root)
    owner['original_baseline_frozen_at']=owner['frozen_at']
    owner['frozen_at']=calculation.isoformat()
    owner['original_prediction_cutoff']=req['prediction_cutoff']
    owner['diagnostic_cutoff']=diagnostic_cutoff
    owner=_research_only(owner)
    krs = build_krs_input(req)['krs_input_data']
    return {'owner':owner,'krs_input':krs,'numerical_calculated_at':calculation.isoformat(),
        'bvi':{str(r['runner_id']):r['canonical_components']['BVI'] for r in req['runners']},
        'numerical_provenance_sha256':req['index_provenance_hash'],'numerical_runners':req['runners'],
        'base_index_mapping_authority':req['base_index_mapping_authority'],
        'environment_shadow_proof':proof,'environment_predictions':copy.deepcopy(predictions),
        'overridden_runner_ids':overrides,'fallback_runner_reasons':fallbacks,
        'candidate_only':True,'production_authority':False,'purchase_authority':False,
        'krs_simulation_executed':False,'mec_executed':False,'ticket_count':None,'capital_required':None}


def append_environment_arm(comparison, prepared, mapping, *, predictions, model_sha,
                           source_artifact, current_authority, root,
                           calculated_at=None, diagnostic_cutoff=None):
    """Append D without replacing frozen A/B/C or re-stamping their execution.

    The existing B features are replayed solely to reconstruct its numerical
    ledger; every Full20 value must match B before model estimates are applied.
    Historical D computations record their real calculation time separately
    from the original SOURCE cutoff and can never create Forward OOS evidence.
    """
    if current_authority is None or source_artifact is None:
        raise ValueError('ENV_SHADOW_CURRENT_AUTHORITY_REQUIRED')
    if 'D_BVI_ENV_SHADOW' in comparison['arms']:
        raise ValueError('ENV_SHADOW_D_ALREADY_PRESENT')
    b = comparison['arms']['B_PEDIGREE_ENHANCED_SHADOW']
    req = copy.deepcopy(prepared)
    req['runners']=copy.deepcopy(b['numerical_runners'])
    req = materialize_index_provenance(attach_production_ledger_to_request(req,mapping))
    old = {str(r['runner_id']):r['canonical_components'] for r in b['numerical_runners']}
    for row in req['runners']:
        rid=str(row['runner_id'])
        if {k:v['value'] for k,v in row['canonical_components'].items()} != {k:v['value'] for k,v in old[rid].items()}:
            raise ValueError('ENV_SHADOW_B_BASELINE_REPLAY_MISMATCH:'+rid)
    comparison['arms']['D_BVI_ENV_SHADOW']=_environment_arm(req,b,predictions,model_sha,
        source_artifact=source_artifact,current_authority=current_authority,root=root,
        calculated_at=calculated_at,diagnostic_cutoff=diagnostic_cutoff)
    comparison['same_mapping_and_cutoff']=False
    comparison['environment_mapping_scope']='A/B/C AUTHORIZED MAPPING UNCHANGED; D DISTINCT RESEARCH MODEL; SAME SOURCE CUTOFF'
    comparison['environment_model_sha256']=model_sha
    return comparison


def compare(prepared, mapping, *, source_sha, receipt_sha, algorithm_freeze_at, cutoff,
            enhanced_features=None, source_artifact=None, current_authority=None, root=None,
            environment_predictions=None, environment_model_sha=None):
    """Recompute A/B/C; caller owns temporal authentication and freeze publication.

    Removing a pedigree-derived distance_fit also ablates its CFI contribution.
    C retains the authorized missing-information DCR policy, never a new weight.
    KRS inputs are evaluated, not a claim that simulation/MEC/Capital executed.
    """
    arms = {}
    environment_base_request = None
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
        if name=='B_PEDIGREE_ENHANCED_SHADOW' and environment_predictions is not None:
            environment_base_request = copy.deepcopy(req)
    if environment_predictions is not None:
        if current_authority is None or source_artifact is None:
            raise ValueError('ENV_SHADOW_CURRENT_AUTHORITY_REQUIRED')
        arms['D_BVI_ENV_SHADOW'] = _environment_arm(environment_base_request,
            arms['B_PEDIGREE_ENHANCED_SHADOW'],environment_predictions,environment_model_sha,
            source_artifact=source_artifact,current_authority=current_authority,root=root)
    from jra_static_owner_forward_oos import sha
    a,b=arms['A_CURRENT'],arms['B_PEDIGREE_ENHANCED_SHADOW']
    return {'arms': arms, 'enhanced_input_supplied': enhanced_features is not None,
        'enhanced_input_distinct':sha([r['evidence_features'] for r in a['numerical_runners']])!=sha([r['evidence_features'] for r in b['numerical_runners']]),
        'enhanced_bvi_artifact_distinct':sha(a['bvi'])!=sha(b['bvi']),
        'enhanced_bvi_distinct':any(a['bvi'][rid]['value']!=b['bvi'][rid]['value'] for rid in a['bvi']),
        'enhanced_ranking_distinct':a['owner']['static_prediction']['ranking']!=b['owner']['static_prediction']['ranking'],
        'same_runner_universe': True, 'same_mapping_and_cutoff': environment_predictions is None,
        **({'environment_mapping_scope':'A/B/C AUTHORIZED MAPPING UNCHANGED; D DISTINCT RESEARCH MODEL; SAME CUTOFF',
            'environment_model_sha256':environment_model_sha} if environment_predictions is not None else {}),
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
        if name=='D_BVI_ENV_SHADOW':
            req['purchase_authority']=False
            req['base_index_mapping_authority']=copy.deepcopy(arm['base_index_mapping_authority'])
            req['environment_shadow_proof']=copy.deepcopy(arm['environment_shadow_proof'])
            req['index_provenance_hash']=arm['numerical_provenance_sha256']
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
