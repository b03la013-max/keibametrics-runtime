"""Saved FNB Role/Pair/Third failure localization and explicit PAPER comparison.

No SOURCE, Owner, selection-policy adoption, KRS run, cash purchase, or formal
NO-BET is issued here. The original frozen prediction remains immutable.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from runtime import local_fnb_semantic_closure as semantic
from runtime.jra_ticket_tree_renderer import render_ticket_tree

PROFILE = 'KM-FNB-MEC-FIRST-FAILURE-LOCALIZATION-R13'
CATEGORIES = ('MATERIAL_W_HEAD', 'PAIR_SELECTION', 'PAIR_LOCAL_THIRD',
    'GLOBAL_P3_CONSUMER', 'UNKNOWN_SELECTION', 'STRUCTURAL_EXCLUSION',
    'SOURCE_OWNER_CONSUMER_RIGHTS', 'CAPITAL', 'CANONICAL_TICKET_RENDERER')


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       indent=2, allow_nan=False)+'\n').encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def audit_prediction(prediction, original_strict, context, *, evaluated_at,
                     source_qualified=False, original_finalized=False):
    """Separate the first algorithmic failure from independent authority gates."""
    ids = semantic._validate(prediction)
    if (original_strict.get('model_prediction_sha256') != semantic._sha(prediction)
            or original_strict.get('race_id') != prediction['race_id']):
        raise ValueError('MEC_AUDIT_ORIGINAL_STRICT_PREDICTION_BINDING_MISMATCH')
    if (context.get('sha256') != semantic._sha({k:v for k,v in context.items() if k!='sha256'})
            or context.get('race_id') != prediction['race_id']
            or prediction.get('input_context_sha256') != context.get('sha256')
            or context.get('source_snapshot_sha256') != prediction['source_snapshot_sha256']):
        raise ValueError('MEC_AUDIT_CONTEXT_ORIGINAL_SHA_OR_RACE_MISMATCH')
    fresh = semantic.execute_strict_mec(prediction, evaluated_at=evaluated_at)
    inventory = semantic.assess_semantics(prediction, evaluated_at=evaluated_at)
    unknown = semantic._unknown(prediction)
    heads = set(prediction['column_rankings']['W']['front'])
    material_pairs = [r for r in prediction['pair_dispositions'] if r['status'] in ('PURCHASE','PROTECT')]
    material_thirds = [r for r in prediction['third_dispositions'] if r['status'] in ('PURCHASE','PROTECT')]
    uncovered = sorted(heads-{r['head'] for r in material_pairs}, key=int)
    off_global = [r for r in semantic.trace_pair_local_thirds(prediction) if not r['third_in_global_p3']]
    n = len(ids)
    expected_structural = n+n**3-n*(n-1)*(n-2)
    structural = sum(r['regular_terminal'] for r in inventory['pair_assessments']+inventory['third_assessments'])
    categories = [
        {'category':CATEGORIES[0], 'state':'UNRESOLVED_ALL_W_UNKNOWN' if not heads and unknown else
             'MISSING_MATERIAL_PAIR_CLOSURE' if uncovered else 'NO_MATERIAL_HEAD_FAILURE_OBSERVED',
         'known_W_front':sorted(heads,key=int), 'unknown_W_count':len(semantic._unknown(prediction,'W')),
         'uncovered_known_heads':uncovered, 'material_head_count':len({r['head'] for r in material_pairs})},
        {'category':CATEGORIES[1], 'state':'UNADOPTED_PROPOSALS' if prediction['pair_dispositions'] and not material_pairs
             else 'NO_PAIR_PROPOSALS_REACHED' if not prediction['pair_dispositions'] else 'MATERIAL_ROWS_PRESENT_NOT_ADOPTION_PROOF',
         'proposal_count':len(prediction['pair_dispositions']), 'material_count':len(material_pairs),
         'original_status_counts':dict(Counter(r['status'] for r in prediction['pair_dispositions']))},
        {'category':CATEGORIES[2], 'state':'UNRESOLVED_CONDITIONAL_SELECTION' if
             any(not r['selection_resolved'] for r in inventory['third_assessments']) else 'TERMINAL',
         'proposal_count':len(prediction['third_dispositions']), 'material_count':len(material_thirds),
         'distinct_runner_slots':n*(n-1)*(n-2),
         'unresolved_distinct_slots':sum(not r['selection_resolved'] for r in inventory['third_assessments'])},
        {'category':CATEGORIES[3], 'state':'OFF_GLOBAL_PROPOSALS_REQUIRE_PAIR_SCOPE' if off_global
             else 'NOT_TRIGGERED_BY_THIS_FROZEN_PREDICTION', 'off_global_proposals':off_global,
         'consumer_repair_does_not_create_materiality':True},
        {'category':CATEGORIES[4], 'state':'UNRESOLVED' if unknown else 'NO_UNKNOWN_RUNNERS',
         'runner_ids':sorted(unknown,key=int), 'role_slots':sum(r['unknown'] for r in inventory['role_assessments']),
         'not_low_ability_not_purchased_not_excluded':True},
        {'category':CATEGORIES[5], 'state':'ALL_DUPLICATE_POSITION_EXCLUSIONS_RECORDED' if structural==expected_structural
             else 'STRUCTURAL_TERMINAL_COUNT_MISMATCH', 'actual':structural, 'expected':expected_structural,
         'distinct_unknown_paths_are_not_structural_exclusions':True},
        {'category':CATEGORIES[6], 'state':'EXTERNALLY_VERIFIED_SOURCE' if source_qualified else 'SOURCE_ACTIVE_NOT_QUALIFIED',
         'source_qualified':bool(source_qualified), 'formal_FNB_owner_adoption_issued_here':False,
         'formal_numerical_consumer_grant_issued_here':False,
         'separate_R13_PAPER_execution_permission_does_not_adopt_selection':True},
        {'category':CATEGORIES[7], 'state':'NOT_REACHED_STRICT_MATERIAL_SELECTION_UNRESOLVED'
             if fresh['status']=='HOLD_NOT_NO_BET' else 'REQUIRES_SEPARATE_CAPITAL_EVALUATION',
         'capital_shortfall_cannot_be_inferred_from_MEC_HOLD':True},
        {'category':CATEGORIES[8], 'state':'NOT_REACHED_NO_QUALIFIED_CANONICAL_TICKETS'
             if fresh['tickets'] is None else 'CANONICAL_ARRAY_PRESENT_RENDERER_REQUIRES_CHECK',
         'original_body_presence_is_not_ticket_success':True}]
    if not heads and unknown:
        algorithmic = 'FIXED_CONTEXT_UNKNOWN_NO_MATERIAL_W_HEAD'
    elif uncovered:
        algorithmic = 'KNOWN_W_HEAD_WITHOUT_MATERIAL_PAIR_CLOSURE'
    elif any(r['status'] not in ('PURCHASE','PROTECT','EXCLUDE','SEMANTIC_ONLY') for r in prediction['pair_dispositions']):
        algorithmic = 'PAIR_SELECTION_POLICY_UNADOPTED'
    elif unknown:
        algorithmic = 'UNKNOWN_SELECTION_UNRESOLVED'
    else:
        algorithmic = fresh['first_failed_stage']
    return {'profile':PROFILE, 'classification':'PRIVATE_FROZEN_INPUT_FAILURE_AUDIT_NOT_NEW_FORECAST',
        'race_id':prediction['race_id'], 'model_id':prediction['model_id'],
        'model_code_sha256':prediction['model_code_sha256'], 'original_prediction_sha256':semantic._sha(prediction),
        'original_strict_sha256':semantic._sha(original_strict), 'fresh_strict':fresh,
        'earliest_pipeline_failure':None if source_qualified else 'SOURCE_ACTIVE_QUALIFICATION',
        'first_algorithmic_failure':algorithmic,
        'source_snapshot_sha256':prediction['source_snapshot_sha256'],
        'source_freeze_at':prediction['source_freeze_at'], 'static_freeze_at':prediction['freeze_at'],
        'original_finalized':bool(original_finalized), 'original_strict_hold_lifted':False,
        'context_unknown_runners':sum(r.get('status')=='UNKNOWN' for r in context['runners']),
        'historical_FNB_observations_consumed':sum(r.get('input_observations',0) for r in context['runners']),
        'known_column_front_counts':{c:len(prediction['column_rankings'][c]['front']) for c in ('W','P2','P3')},
        'categories':categories, 'original_hold_causes':deepcopy(original_strict['all_hold_causes']),
        'computed_no_bet':False, 'new_krs_executions':0, 'production_adopted':False,
        'formal_source_admitted':False, 'recipient_delivery_proven':False, 'registered_OOS_increment':0}


def paper_comparison(prediction, *, evaluated_at, authorization_ref):
    """Run the two already implemented unadopted policies as separate studies."""
    if not authorization_ref:
        raise ValueError('MEC_PAPER_CURRENT_REQUEST_AUTHORIZATION_REF_REQUIRED')
    before = encoded(prediction)
    studies = {}
    for function in (semantic.research_pair_local_protection, semantic.research_unknown_path_protection):
        result = function(prediction, evaluated_at=evaluated_at)
        method_witness = {}
        for name, method in result['methods'].items():
            rendered = render_ticket_tree({'final_ticket':{'tickets':method['tickets'],
                'no_bet':method['method_zero_selection']},
                'capital_policy_decision':{'decision':'AKI_REFERENCE_ONLY'},
                'final_prediction_package':{'validation_status':'UNVALIDATED'}})
            norm = lambda rows: sorted((r['bet_type'],tuple(r['selection']),r['stake']) for r in rows)
            if (not rendered['canonical_roundtrip_verified'] or norm(rendered['reflattened_tickets'])!=norm(method['tickets'])
                    or rendered['ticket_count']!=method['point_count']
                    or rendered['total_investment']!=method['paper_required_capital']
                    or rendered['text']!=method['canonical_tree']):
                raise ValueError('MEC_PAPER_CANONICAL_TREE_FULL_STAKE_IDENTITY_MISMATCH')
            method_witness[name] = {'race_id':prediction['race_id'], 'owner_model_id':prediction['model_id'],
                'source_snapshot_sha256':prediction['source_snapshot_sha256'],
                'model_prediction_sha256':semantic._sha(prediction), 'policy_id':result['profile'],
                'point_count':rendered['ticket_count'], 'stake_total':rendered['total_investment'],
                'full_canonical_array_sha256':digest(encoded(method['tickets'])),
                'tree_sha256':digest(rendered['text'].encode()), 'independent_reflatten_verified':True}
        result['method_identity_witness'] = method_witness
        studies[result['profile']] = result
    if encoded(prediction)!=before:
        raise ValueError('MEC_PAPER_MUTATED_FROZEN_PREDICTION')
    return {'profile':PROFILE+'-EXPLICIT-PAPER-COMPARISON', 'race_id':prediction['race_id'],
        'authorization_ref':authorization_ref, 'owner_count':1, 'independent_BC':False,
        'two_selection_hypotheses_are_not_two_prediction_owners':True,
        'studies':studies, 'new_krs_executions':0, 'source_or_policy_adoption_issued':False,
        'cash_purchase':False, 'prestart_delivery_success':False, 'PFS':None}
