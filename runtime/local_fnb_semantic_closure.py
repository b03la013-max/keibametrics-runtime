"""Full Active semantic inventory and isolated pair-local paper consumer.

Recording every unresolved branch is not a completed prediction.  Neither this
module nor a graph-coverage ratio grants SOURCE, Owner, selection or FINAL scope.
The optional PROTECT mapping is a NEW, unadopted research policy.  Common MEC,
the Static model, KRS, numerical indices and global P3 roles remain unchanged.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from datetime import datetime
import hashlib
import json
from pathlib import Path

from runtime.minimum_efficient_coverage import build_mec_plan, validate_mec_plan, MECError
from runtime.capital_policy import resolve_capital_policy
from runtime.jra_ticket_tree_renderer import render_ticket_tree

PROFILE = 'KM-FNB-FULL-ACTIVE-SEMANTIC-INVENTORY-v0.1-20261103'
RESEARCH_POLICY = 'KM-FNB-PAIR-LOCAL-SEMANTIC-PROTECTION-RESEARCH-v0.1-20261103'
UNKNOWN_RESEARCH_POLICY = 'KM-FNB-UNKNOWN-PATHS-AS-PROTECTION-RESEARCH-v0.1-20261103'
MODEL_ID = 'KM-FNB-CONTEXT-PARETO-STATIC-RESEARCH-v0.1-20261103'
MODEL_CODE_SHA256 = '8fbee4eafada822ddb28185eb7233a96626e9ce93c8ff9a705fc3516faf9eed4'
VERSION = '0.1'
METHODS = ('EXACTA', 'TRIO', 'TRIFECTA')
PROPOSAL_STATUS = 'UNADOPTED_RESEARCH_SEMANTIC_ONLY'


def _sha(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
        separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def _time(value):
    dt = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('FNB_SEMANTIC_TIMEZONE_REQUIRED')
    return str(value)


def _code_sha():
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def _validate(pred):
    if not isinstance(pred, dict) or pred.get('model_id') != MODEL_ID:
        raise ValueError('FNB_SEMANTIC_FIXED_MODEL_MISMATCH')
    for key in ('model_code_sha256', 'source_snapshot_sha256'):
        value = pred.get(key)
        if not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
            raise ValueError('FNB_SEMANTIC_SHA_MISSING:' + key)
    for key in ('freeze_at', 'source_freeze_at'):
        _time(pred.get(key))
    if pred['model_code_sha256'] != MODEL_CODE_SHA256 or pred.get('model_version') != '0.1':
        raise ValueError('FNB_SEMANTIC_FIXED_MODEL_CODE_OR_VERSION_MISMATCH')
    if datetime.fromisoformat(pred['freeze_at']) < datetime.fromisoformat(pred['source_freeze_at']):
        raise ValueError('FNB_SEMANTIC_MODEL_BEFORE_SOURCE_FREEZE')
    active = pred.get('active_runners')
    if (not isinstance(active, list) or len(active) < 2 or len(set(active)) != len(active)
            or any(not isinstance(r, str) or not r.isdigit() or int(r) <= 0 for r in active)):
        raise ValueError('FNB_SEMANTIC_ACTIVE_INVALID')
    ids = set(active)
    if set(pred.get('roles') or {}) != ids:
        raise ValueError('FNB_SEMANTIC_FULL_ACTIVE_ROLES_MISSING')
    columns = pred.get('column_rankings') or {}
    for column in ('W', 'P2', 'P3'):
        rows = (columns.get(column) or {}).get('rows') or []
        if len(rows) != len(active) or {str(r.get('runner_id')) for r in rows} != ids:
            raise ValueError('FNB_SEMANTIC_FULL_ACTIVE_COLUMN_MISSING:' + column)
        if any(type(r.get('unknown')) is not bool for r in rows):
            raise ValueError('FNB_SEMANTIC_UNKNOWN_STATE_MISSING:' + column)
        front = (columns.get(column) or {}).get('front') or []
        if len(set(front)) != len(front) or not set(front) <= ids:
            raise ValueError('FNB_SEMANTIC_FRONT_IDENTITY_INVALID:' + column)
        unknown = {r['runner_id'] for r in rows if r['unknown']}
        if any(r['unknown'] and (r.get('rank') is not None or
                r.get('rank_interval') != {'min': 1, 'max': len(active)}) for r in rows):
            raise ValueError('FNB_SEMANTIC_UNKNOWN_RANK_MUST_REMAIN_NULL_FULL_INTERVAL:' + column)
        if unknown & set(front):
            raise ValueError('FNB_SEMANTIC_UNKNOWN_FRONT_PROMOTION_FORBIDDEN:' + column)
        if any((column in pred['roles'][r]) != (r in front) for r in active):
            raise ValueError('FNB_SEMANTIC_ROLE_FRONT_CONFLICT:' + column)
    for key, fields in (('pair_dispositions', ('head', 'second')),
                        ('third_dispositions', ('head', 'second', 'third'))):
        if not isinstance(pred.get(key), list):
            raise ValueError('FNB_SEMANTIC_PROPOSAL_LIST_MISSING:' + key)
        seen = set()
        for row in pred[key]:
            identity = tuple(str(row.get(k)) for k in fields)
            if not set(identity) <= ids or len(set(identity)) != len(identity):
                raise ValueError('FNB_SEMANTIC_PROPOSAL_IDENTITY_INVALID:' + key)
            if identity in seen:
                raise ValueError('FNB_SEMANTIC_DUPLICATE_PROPOSAL:' + key)
            seen.add(identity)
            if not isinstance(row.get('status'), str) or not row['status']:
                raise ValueError('FNB_SEMANTIC_PROPOSAL_STATUS_MISSING:' + key)
    if pred.get('sha256') != _sha({k: v for k, v in pred.items() if k != 'sha256'}):
        raise ValueError('FNB_SEMANTIC_ORIGINAL_PREDICTION_SHA_MISMATCH')
    return list(active)


def _unknown(pred, column=None):
    columns = (column,) if column else ('W', 'P2', 'P3')
    return {row['runner_id'] for col in columns for row in pred['column_rankings'][col]['rows'] if row['unknown']}


def _proposal_qualification(prediction):
    """A local proposal needs its actual head/Pair-conditioned front evidence."""
    head_rows = {r['head']: r for r in prediction.get('head_local_P2') or []}
    third_rows = {(r['head'], r['second']): r for r in prediction.get('pair_conditioned_Third') or []}
    unknown = _unknown(prediction)
    pairs = {}
    for r in prediction['pair_dispositions']:
        h, s = r['head'], r['second']
        front = ((head_rows.get(h) or {}).get('ranking') or {}).get('front') or []
        pairs[(h, s)] = h in prediction['column_rankings']['W']['front'] and s in front and not {h, s} & unknown
    thirds = {}
    for r in prediction['third_dispositions']:
        h, s, t = r['head'], r['second'], r['third']
        front = ((third_rows.get((h, s)) or {}).get('ranking') or {}).get('front') or []
        thirds[(h, s, t)] = bool(pairs.get((h, s))) and t in front and not {h, s, t} & unknown
    return pairs, thirds


def original_request(prediction):
    """Transport original proposals unchanged; no materiality is invented."""
    active = _validate(prediction)
    registry = []
    for runner in active:
        roles = prediction['roles'][runner]
        for column in ('W', 'P2', 'P3'):
            unknown = runner in _unknown(prediction, column)
            registry.append({'runner_id': runner, 'column': column,
                'status': 'CORE' if column in roles else 'UNRESOLVED' if unknown else 'NOT_FRONT',
                'source_model_roles': deepcopy(roles),
                'unknown_is_not_low_ability_or_excluded': unknown})
    return {'race_id': prediction['race_id'], 'family_id': 'LOCAL', 'venue_id': 'FNB',
        'classification': 'HISTORICAL_UNADOPTED_RESEARCH_NOT_FORMAL_NOT_OOS',
        'runners': [{'runner_id': r} for r in active], 'role_registry': registry,
        'pair_dispositions': deepcopy(prediction['pair_dispositions']),
        'third_dispositions': deepcopy(prediction['third_dispositions']),
        'original_unknown_semantic_paths': deepcopy(prediction.get('unresolved_semantic_paths') or []),
        'source_model_prediction_sha256': _sha(prediction),
        'source_model_code_sha256': prediction['model_code_sha256'],
        'source_snapshot_sha256': prediction['source_snapshot_sha256'],
        'source_freeze_at': prediction['source_freeze_at'], 'model_freeze_at': prediction['freeze_at'],
        'available_bet_types': list(METHODS)}


def _bindings(prediction, evaluated_at):
    _time(evaluated_at)
    if datetime.fromisoformat(evaluated_at) < datetime.fromisoformat(prediction['freeze_at']):
        raise ValueError('FNB_SEMANTIC_EVALUATION_BEFORE_MODEL_FREEZE')
    return {'evaluated_at': _time(evaluated_at), 'model_id': prediction['model_id'],
        'model_version': prediction.get('model_version'),
        'model_code_sha256': prediction['model_code_sha256'],
        'model_prediction_sha256': _sha(prediction),
        'source_snapshot_sha256': prediction['source_snapshot_sha256'],
        'source_freeze_at': prediction['source_freeze_at'], 'model_freeze_at': prediction['freeze_at'],
        'assessment_code_sha256': _code_sha()}


def trace_pair_local_thirds(prediction):
    """Trace each original proposal, including the prior 38 off-global proposals.

    All original proposals lack selection authority.  The additional global-P3
    incompatibility describes the OLD isolated paper bridge, not a proven
    structural exclusion or a successful original strict-MEC consumption.
    """
    _validate(prediction)
    global_p3 = set(prediction['column_rankings']['P3']['front'])
    pair_keys = {(r['head'], r['second']) for r in prediction['pair_dispositions']}
    pair_qualification, third_qualification = _proposal_qualification(prediction)
    unknown = _unknown(prediction)
    traces = []
    for row in prediction['third_dispositions']:
        h, s, t = row['head'], row['second'], row['third']
        reasons = ['ORIGINAL_PROPOSAL_HAS_NO_ADOPTED_MATERIAL_SELECTION_AUTHORITY']
        if t not in global_p3:
            reasons.append('PREVIOUS_PARTIAL_PAPER_COMMON_MEC_GLOBAL_P3_GATE')
        if (h, s) not in pair_keys:
            reasons.append('HEAD_LOCAL_PAIR_NOT_FORMED')
        elif not pair_qualification.get((h, s)):
            reasons.append('HEAD_LOCAL_PAIR_PROPOSAL_SCHEMA_OR_ELIGIBILITY_CONFLICT')
        if not third_qualification.get((h, s, t)):
            reasons.append('PAIR_CONDITIONED_THIRD_PROPOSAL_SCHEMA_OR_ELIGIBILITY_CONFLICT')
        if {h, s, t} & unknown:
            reasons.append('UNKNOWN_PARTICIPANT_REMAINS_UNRESOLVED')
        traces.append({'pair_id': h + '>' + s, 'third_id': t,
            'path_id': h + '>' + s + '>' + t,
            'head': h, 'second': s, 'third': t,
            'head_roles': deepcopy(prediction['roles'][h]),
            'second_roles': deepcopy(prediction['roles'][s]),
            'third_roles': deepcopy(prediction['roles'][t]),
            'original_status': row['status'], 'original_reason': row.get('reason'),
            'head_local_pair_formed': bool(pair_qualification.get((h, s))),
            'pair_conditioned_third_front_qualified': bool(third_qualification.get((h, s, t))),
            'third_in_global_p3': t in global_p3,
            'previous_partial_paper_global_gate_would_omit': t not in global_p3,
            'formal_structural_ineligibility_proven': False,
            'original_strict_mec_material_consumption': False,
            'new_selection_policy_required': True,
            'source_snapshot_sha256': prediction['source_snapshot_sha256'],
            'source_freeze_at': prediction['source_freeze_at'],
            'model_freeze_at': prediction['freeze_at'],
            'model_code_sha256': prediction['model_code_sha256'],
            'model_prediction_sha256': _sha(prediction), 'reasons': reasons})
    return traces


def assess_semantics(prediction, *, evaluated_at):
    """Record N×3 roles, N² pair slots and N³ Third slots without a lost node.

    Duplicate positions alone are structural terminals.  Non-front, UNKNOWN,
    missing conditional assessment and unadopted proposals remain unresolved;
    an exhaustive inventory is deliberately NOT full semantic completion.
    """
    active = _validate(prediction)
    pair_map = {(r['head'], r['second']): r for r in prediction['pair_dispositions']}
    third_map = {(r['head'], r['second'], r['third']): r for r in prediction['third_dispositions']}
    head_map = {r['head']: r for r in prediction.get('head_local_P2') or []}
    conditional_map = {(r['head'], r['second']): r for r in prediction.get('pair_conditioned_Third') or []}
    unknown = _unknown(prediction)
    role_rows, pairs, thirds = [], [], []
    for r in active:
        for col in ('W', 'P2', 'P3'):
            is_unknown = r in _unknown(prediction, col)
            in_front = r in prediction['column_rankings'][col]['front']
            role_rows.append({'runner_id': r, 'column': col,
                'status': 'UNRESOLVED_UNKNOWN_POSSIBLE' if is_unknown else
                    'UNADOPTED_SEMANTIC_ONLY' if in_front else 'UNRESOLVED_NONFRONT_NOT_AN_EXCLUSION',
                'source_roles': deepcopy(prediction['roles'][r]),
                'selection_resolved': False, 'regular_terminal': False,
                'unknown': is_unknown, 'semantic_front': in_front,
                'source_column_rank': deepcopy(next(x for x in prediction['column_rankings'][col]['rows'] if x['runner_id'] == r))})
    for h in active:
        for s in active:
            key = (h, s)
            structural = h == s
            if structural:
                state, reason = 'STRUCTURAL_INELIGIBLE', 'SAME_RUNNER_CANNOT_FINISH_FIRST_AND_SECOND'
            elif {h, s} & unknown:
                state, reason = 'UNRESOLVED_UNKNOWN_POSSIBLE', 'UNKNOWN_PARTICIPANT_NOT_REJECTED_NOT_PURCHASED'
            elif key in pair_map:
                state, reason = 'UNADOPTED_SEMANTIC_ONLY', pair_map[key].get('reason')
            elif h not in head_map:
                state, reason = 'UNRESOLVED_HEAD_LOCAL_ASSESSMENT_MISSING', 'NO_HEAD_CONDITIONED_P2_ASSESSMENT_NOT_AN_EXCLUSION'
            else:
                state, reason = 'UNRESOLVED_NONFRONT_PAIR_NOT_AN_EXCLUSION', 'PAIR_NOT_PROPOSED_BY_FIXED_MODEL_NO_HARD_EXCLUSION_ASSERTED'
            pairs.append({'pair_id': h + '>' + s, 'head': h, 'second': s,
                'status': state, 'reason': reason, 'regular_terminal': structural,
                'selection_resolved': structural, 'unknown_participants': sorted({h, s} & unknown, key=int),
                'source_proposal': deepcopy(pair_map.get(key)),
                'head_local_p2_assessment_present': h in head_map})
            for t in active:
                k3 = (h, s, t)
                structural3 = len({h, s, t}) < 3
                if structural3:
                    state3, reason3 = 'STRUCTURAL_INELIGIBLE', 'SAME_RUNNER_CANNOT_OCCUPY_MULTIPLE_FINISH_POSITIONS'
                elif {h, s, t} & unknown:
                    state3, reason3 = 'UNRESOLVED_UNKNOWN_POSSIBLE', 'UNKNOWN_PARTICIPANT_NOT_REJECTED_NOT_PURCHASED'
                elif k3 in third_map:
                    state3, reason3 = 'UNADOPTED_SEMANTIC_ONLY', third_map[k3].get('reason')
                elif key not in pair_map:
                    state3, reason3 = 'UNRESOLVED_HEAD_LOCAL_PAIR_NOT_FORMED', 'PAIR_NOT_MATERIAL_OR_NOT_PROPOSED_NO_THIRD_EXCLUSION_ASSERTED'
                elif key not in conditional_map:
                    state3, reason3 = 'UNRESOLVED_PAIR_THIRD_ASSESSMENT_MISSING', 'NO_PAIR_CONDITIONED_THIRD_ASSESSMENT'
                else:
                    state3, reason3 = 'UNRESOLVED_NONFRONT_THIRD_NOT_AN_EXCLUSION', 'THIRD_NOT_PROPOSED_BY_FIXED_MODEL_NO_HARD_EXCLUSION_ASSERTED'
                thirds.append({'path_id': h + '>' + s + '>' + t,
                    'pair_id': h + '>' + s, 'head': h, 'second': s, 'third': t,
                    'status': state3, 'reason': reason3, 'regular_terminal': structural3,
                    'selection_resolved': structural3,
                    'unknown_participants': sorted({h, s, t} & unknown, key=int),
                    'source_proposal': deepcopy(third_map.get(k3)),
                    'pair_conditioned_third_assessment_present': key in conditional_map,
                    'third_in_global_p3': t in prediction['column_rankings']['P3']['front']})
    n = len(active)
    all_rows = role_rows + pairs + thirds
    result = {'profile': PROFILE, 'version': VERSION, 'race_id': prediction['race_id'],
        **_bindings(prediction, evaluated_at), 'active_runners': active,
        'unknown_runners': sorted(unknown, key=int),
        'role_assessments': role_rows, 'pair_assessments': pairs, 'third_assessments': thirds,
        'expected_slots': {'role': n * 3, 'pair': n * n, 'third': n * n * n},
        'recorded_slots': {'role': len(role_rows), 'pair': len(pairs), 'third': len(thirds)},
        'all_active_and_branch_slots_recorded': True,
        'regular_terminal_count': sum(r['regular_terminal'] for r in all_rows),
        'unresolved_or_unadopted_count': sum(not r['selection_resolved'] for r in all_rows),
        'state_counts': dict(Counter(r['status'] for r in all_rows)),
        'full_semantic_complete': False, 'strict_mec_ready': False,
        'inventory_completion_is_not_selection_completion': True,
        'original_unresolved_semantic_paths': deepcopy(prediction.get('unresolved_semantic_paths') or []),
        'conditional_third_trace': trace_pair_local_thirds(prediction),
        'production_adopted': False, 'formal_final': False, 'independent_BC': False,
        'registered_forward_oos_increment': 0}
    result['sha256'] = _sha(result)
    return result


def execute_strict_mec(prediction, *, evaluated_at):
    """Actually run unchanged strict MEC and retain all original HOLD causes."""
    request = original_request(prediction)
    material_pairs = [r for r in request['pair_dispositions'] if r['status'] in ('PURCHASE', 'PROTECT')]
    heads = set(prediction['column_rankings']['W']['front'])
    covered_heads = {r['head'] for r in material_pairs}
    holds = [{'stage': 'MEC_MATERIAL_HEAD_CLOSURE', 'head': h,
        'reason': 'ACTIVE_W_WITHOUT_MATERIAL_PAIR_CLOSURE',
        'original_pair_proposal_count': sum(r['head'] == h for r in request['pair_dispositions'])}
        for h in sorted(heads - covered_heads, key=int)]
    if not heads and not _unknown(prediction):
        holds.append({'stage': 'KNOWN_W_HEAD_ASSESSMENT_UNFORMED',
            'reason': 'NO_KNOWN_W_FRONT_OR_EXPLICIT_SELECTION_TERMINAL'})
    for kind, rows in (('PAIR', request['pair_dispositions']), ('THIRD', request['third_dispositions'])):
        for row in rows:
            if row['status'] not in ('PURCHASE', 'PROTECT', 'EXCLUDE', 'SEMANTIC_ONLY'):
                holds.append({'stage': kind + '_MATERIAL_SELECTION_UNFORMED',
                    'path_id': '>'.join(row[k] for k in ('head', 'second', 'third') if k in row),
                    'reason': 'UNADOPTED_MODEL_SEMANTIC_PROPOSAL_IS_NOT_MATERIAL_SELECTION',
                    'original_status': row['status']})
    for r in sorted(_unknown(prediction), key=int):
        holds.append({'stage': 'UNKNOWN_ROLE_SELECTION_UNRESOLVED', 'runner_id': r,
            'possible_columns': ['W', 'P2', 'P3'], 'reason': 'NO_HARD_EXCLUSION_OR_SELECTION_AUTHORITY'})
    try:
        plan = build_mec_plan(request, strict_head_closure=True, min_stake=100)
        validate_mec_plan(plan)
        state, error = 'CANONICAL_MEC_EXECUTED_NOT_FORMAL_QUALIFICATION', None
    except MECError as exc:
        plan = None
        state, error = 'HOLD_NOT_NO_BET', str(exc)
    if holds:
        state = 'HOLD_NOT_NO_BET'
    return {'profile': PROFILE, 'race_id': prediction['race_id'],
        **_bindings(prediction, evaluated_at), 'status': state,
        'first_failed_stage': 'MEC_MATERIAL_HEAD_CLOSURE' if error and error.startswith('ACTIVE_W_WITHOUT_MATERIAL_PAIR_CLOSURE') else
            'CANONICAL_MEC' if error else holds[0]['stage'] if holds else None,
        'canonical_mec_error': error, 'all_hold_causes': holds,
        'canonical_mec_request': request, 'canonical_mec_plan': plan,
        'tickets': None if error or holds else plan['tickets'], 'no_bet': None,
        'strict_mec_executed': True, 'canonical_mec_code_sha256': hashlib.sha256(
            Path(__file__).with_name('minimum_efficient_coverage.py').read_bytes()).hexdigest(),
        'full_semantic_complete': False, 'formal_final': False}


def research_pair_local_protection(prediction, *, evaluated_at, capital_policy=None,
                                   include_unknown_paths=False):
    """Optional NEW research selection policy; never lift the original HOLD.

    Known original front proposals are PROTECT hypotheses.  A pair's effective
    P3 is global-P3 union that pair's explicit conditional proposals.  Canonical
    MEC is called separately with only that head/pair materialized.  The scoped
    request is not a changed global Static role assignment.  Union/dedup of
    canonical per-pair tickets preserves each declared coverage unit.
    """
    active = _validate(prediction)
    unknown = _unknown(prediction)
    policy_id = UNKNOWN_RESEARCH_POLICY if include_unknown_paths else RESEARCH_POLICY
    if any(r['status'] != PROPOSAL_STATUS for r in prediction['pair_dispositions'] + prediction['third_dispositions']):
        raise ValueError('FNB_RESEARCH_POLICY_REQUIRES_UNCHANGED_ORIGINAL_SEMANTIC_PROPOSALS')
    if any({r['head'], r['second']} & unknown for r in prediction['pair_dispositions']):
        raise ValueError('FNB_RESEARCH_UNKNOWN_PAIR_MATERIALIZATION_FORBIDDEN')
    if any({r['head'], r['second'], r['third']} & unknown for r in prediction['third_dispositions']):
        raise ValueError('FNB_RESEARCH_UNKNOWN_THIRD_MATERIALIZATION_FORBIDDEN')
    pair_keys = {(r['head'], r['second']) for r in prediction['pair_dispositions']}
    if any((r['head'], r['second']) not in pair_keys for r in prediction['third_dispositions']):
        raise ValueError('FNB_RESEARCH_THIRD_WITHOUT_PAIR_FORBIDDEN')
    global_p3 = set(prediction['column_rankings']['P3']['front'])
    qualified_pairs, qualified_thirds = _proposal_qualification(prediction)
    if not all(qualified_pairs.values()) or not all(qualified_thirds.values()):
        raise ValueError('FNB_RESEARCH_LOCAL_PROPOSAL_SCHEMA_OR_FRONT_ELIGIBILITY_CONFLICT')
    material_pairs = deepcopy(prediction['pair_dispositions'])
    local_proposals = deepcopy(prediction['third_dispositions'])
    if include_unknown_paths:
        # These are explicitly NEW selection decisions over original possible
        # paths, not inferred ability or changed source/model roles.
        selected = {(r['head'], r['second']) for r in material_pairs}
        known_heads = set(prediction['column_rankings']['W']['front'])
        for h in active:
            for s in active:
                if h == s:
                    continue
                if h in unknown or (h in known_heads and s in unknown):
                    if (h, s) not in selected:
                        material_pairs.append({'head': h, 'second': s,
                            'status': 'NEW_RESEARCH_UNKNOWN_POSSIBILITY_PROPOSAL',
                            'reason': 'UNKNOWN_HEAD_OR_SECOND_ALL_POSSIBLE_PATHS_PROTECTED_BY_NEW_POLICY'})
                        selected.add((h, s))
        proposed = {(r['head'], r['second'], r['third']) for r in local_proposals}
        for h, s in sorted(selected, key=lambda k: tuple(int(x) for x in k)):
            for t in active:
                if t in {h, s}:
                    continue
                if h in unknown or s in unknown or t in unknown:
                    if (h, s, t) not in proposed:
                        local_proposals.append({'head': h, 'second': s, 'third': t,
                            'status': 'NEW_RESEARCH_UNKNOWN_POSSIBILITY_PROPOSAL',
                            'reason': 'UNKNOWN_PARTICIPANT_ALL_POSSIBLE_CONDITIONAL_THIRDS_PROTECTED_BY_NEW_POLICY'})
                        proposed.add((h, s, t))
    subplans, ticket_map, consumed = [], {}, set()
    material_triples = set()
    for original_pair in material_pairs:
        h, s = original_pair['head'], original_pair['second']
        local = [r for r in local_proposals if (r['head'], r['second']) == (h, s)]
        effective_p3 = (global_p3 | {r['third'] for r in local}) - {h, s}
        scoped = original_request(prediction)
        scoped['role_registry'] = []
        for r in active:
            for col, present in (('W', r == h), ('P2', r == s), ('P3', r in effective_p3)):
                scoped['role_registry'].append({'runner_id': r, 'column': col,
                    'status': 'PROTECTED' if present else 'UNRESOLVED' if r in unknown else 'NOT_IN_THIS_PAIR_SCOPE',
                    'pair_scoped_consumer_view_not_global_static_role': True})
        scoped['pair_dispositions'] = [{**deepcopy(original_pair), 'status': 'PROTECT',
            'reason': 'UNADOPTED_RESEARCH_FRONT_AS_PAIR_LOCAL_PROTECTION'}]
        scoped['third_dispositions'] = [{**deepcopy(r), 'status': 'PROTECT',
            'reason': 'UNADOPTED_RESEARCH_PAIR_CONDITIONED_THIRD_PROTECTION'} for r in local]
        scoped['research_policy_id'] = policy_id
        plan = build_mec_plan(scoped, strict_head_closure=True, min_stake=100)
        validate_mec_plan(plan)
        for row in local:
            consumed.add((h, s, row['third']))
        material_triples.update((h, s, t) for t in effective_p3)
        for ticket in plan['tickets']:
            key = (ticket['bet_type'], tuple(ticket['selection']))
            if key not in ticket_map:
                ticket_map[key] = deepcopy(ticket)
                ticket_map[key]['pair_scope_support'] = []
            ticket_map[key]['pair_scope_support'].append(h + '>' + s)
            ticket_map[key]['coverage_ids'] = sorted(set(ticket_map[key]['coverage_ids']) | set(ticket['coverage_ids']))
        subplans.append({'pair_id': h + '>' + s, 'global_p3_unchanged': sorted(global_p3, key=int),
            'pair_local_third_proposals': deepcopy(local),
            'effective_pair_scoped_p3': sorted(effective_p3, key=int),
            'request': scoped, 'canonical_plan': plan})
    tickets = sorted(ticket_map.values(), key=lambda r: (METHODS.index(r['bet_type']), r['selection']))
    methods = {}
    for method in METHODS:
        selected = [deepcopy(t) for t in tickets if t['bet_type'] == method]
        required = sum(t['stake'] for t in selected)
        request = original_request(prediction)
        if capital_policy is not None:
            request['capital_policy'] = deepcopy(capital_policy)
        policy = resolve_capital_policy(request, {'minimum_required_capital': required,
            'profile': policy_id, 'sha256': _sha(selected), 'material_coverage_ratio': 1.0})
        zero = not selected
        tree = render_ticket_tree({'final_ticket': {'tickets': selected, 'no_bet': zero},
            'capital_policy_decision': {'decision': 'AKI_REFERENCE_ONLY'},
            'final_prediction_package': {'validation_status': 'UNVALIDATED'}})
        methods[method] = {'tickets': selected, 'point_count': len(selected),
            'paper_required_capital': required, 'capital_limit': policy['capital_limit'],
            'recommended_cash_investment': 0, 'actual_cash_investment': 0,
            'paper_proposals_not_purchase_authority': True,
            'unused_capital': None if policy['capital_limit'] is None else max(0, policy['capital_limit'] - required),
            'capital_shortfall': None if policy['capital_limit'] is None else max(0, required - policy['capital_limit']),
            'capital_policy': policy, 'canonical_tree': tree['text'],
            'canonical_roundtrip_verified': tree['canonical_roundtrip_verified'],
            'status': 'COMPUTED_ZERO_ORIENTATION' if zero and method == 'TRIFECTA' else
                'COMPUTED_NO_KNOWN_MATERIAL_PROPOSALS' if zero else
                'UNADOPTED_RESEARCH_PAPER_PROPOSALS_WITH_EXPLICIT_UNKNOWN_PROTECTION' if include_unknown_paths else
                'PARTIAL_UNADOPTED_RESEARCH_PAPER_PROPOSALS',
            'method_zero_selection': zero, 'whole_race_no_bet': None,
            'zero_reason': 'STRUCTURAL_NO_THREE_DISTINCT_ACTIVE_RUNNERS' if zero and len(active) < 3 and method in ('TRIO', 'TRIFECTA') else
                'NO_EXACT_PURCHASE_ORIENTATION_ASSERTED' if zero and method == 'TRIFECTA' else
                'NO_KNOWN_FRONT_PROPOSALS' if zero else None,
            'alternative_not_combined_purchase': True}
    all_proposals = {(r['head'], r['second'], r['third']) for r in prediction['third_dispositions']}
    off_global = [r for r in trace_pair_local_thirds(prediction) if not r['third_in_global_p3']]
    candidate_inventory = None
    if include_unknown_paths:
        candidate_inventory = assess_semantics(prediction, evaluated_at=evaluated_at)
        selected_pairs = {(r['head'], r['second']) for r in material_pairs}
        for row in candidate_inventory['role_assessments']:
            row['candidate_policy_status'] = ('PROTECTED_UNKNOWN_POSSIBILITY' if row['unknown'] else
                'PROTECTED_KNOWN_FRONT' if row['semantic_front'] else 'NOT_SELECTED_AS_GLOBAL_ROLE_BY_NEW_RESEARCH_FRONT_POLICY')
            row['candidate_regular_terminal'] = True
        for row in candidate_inventory['pair_assessments']:
            key = (row['head'], row['second'])
            row['candidate_policy_status'] = ('STRUCTURAL_INELIGIBLE' if row['regular_terminal'] else
                'PROTECT' if key in selected_pairs else 'NOT_SELECTED_BY_NEW_RESEARCH_FRONT_POLICY_NOT_ABILITY_EXCLUSION')
            row['candidate_regular_terminal'] = True
        for row in candidate_inventory['third_assessments']:
            key = (row['head'], row['second'], row['third'])
            row['candidate_policy_status'] = ('STRUCTURAL_INELIGIBLE' if row['regular_terminal'] else
                'PROTECT' if key in material_triples else 'NOT_SELECTED_BY_NEW_RESEARCH_FRONT_POLICY_NOT_ABILITY_EXCLUSION')
            row['candidate_regular_terminal'] = True
        # The original assessment states/sha are retained in a separate object;
        # this child inventory describes candidate decisions, not original ones.
        candidate_inventory['profile'] = UNKNOWN_RESEARCH_POLICY + '-DECISION-INVENTORY'
        candidate_inventory.pop('sha256', None)
        candidate_inventory['candidate_all_selection_slots_terminal'] = True
        candidate_inventory['candidate_regular_terminal_count'] = sum(candidate_inventory['recorded_slots'].values())
        candidate_inventory['original_full_semantic_complete'] = False
        candidate_inventory['full_semantic_complete'] = False
        candidate_inventory['candidate_inventory_sha256'] = _sha(candidate_inventory)
    original_consumed = consumed & all_proposals
    expected_unknown_paths = {(h, s, t) for h in active for s in active for t in active
        if len({h, s, t}) == 3 and (h in unknown or
            (h in prediction['column_rankings']['W']['front'] and s in unknown) or
            ((h, s) in {(r['head'], r['second']) for r in material_pairs} and t in unknown))}
    return {'profile': policy_id, 'version': VERSION, 'race_id': prediction['race_id'],
        **_bindings(prediction, evaluated_at),
        'classification': 'NEW_UNADOPTED_RESEARCH_UNKNOWN_PROTECTION_POLICY_NOT_FORMAL_FINAL' if include_unknown_paths else
            'NEW_UNADOPTED_RESEARCH_SELECTION_POLICY_PARTIAL_PAPER_NOT_FINAL',
        'material_mapping_is_new_research_hypothesis': True,
        'active_runners': active, 'unknown_runners': sorted(unknown, key=int),
        'original_unknown_semantic_paths': deepcopy(prediction.get('unresolved_semantic_paths') or []),
        'known_pair_scoped_subplans': subplans, 'methods': methods,
        'conditional_third_proposals': len(all_proposals),
        'conditional_third_proposals_consumed_in_candidate': len(original_consumed),
        'off_global_third_proposals_preserved': off_global,
        'all_original_conditional_third_proposals_consumed': original_consumed == all_proposals,
        'candidate_material_pair_count': len(material_pairs),
        'candidate_material_conditional_third_count': len(material_triples),
        'unknown_possible_conditional_path_count': len(expected_unknown_paths),
        'unknown_possible_paths_protected': len(expected_unknown_paths & material_triples),
        'all_declared_unknown_possible_paths_protected': include_unknown_paths and expected_unknown_paths <= material_triples,
        'candidate_decision_inventory': candidate_inventory,
        'candidate_all_selection_slots_terminal': bool(candidate_inventory),
        'global_static_p3_changed': False, 'original_strict_hold_lifted': False,
        'unknown_selection_resolved_under_unadopted_policy': include_unknown_paths,
        'unknown_evidence_uncertainty_resolved': False, 'full_semantic_complete': False,
        'full_active_final_forecast': False, 'production_adopted': False,
        'formal_owner_scope': False, 'independent_BC': False,
        'new_krs_runs': 0, 'krs_physics_changed': False, 'actual_purchase': False,
        'registered_forward_oos_increment': 0}


def research_unknown_path_protection(prediction, *, evaluated_at, capital_policy=None):
    """Explicit opt-in all-possible UNKNOWN path protection research candidate."""
    return research_pair_local_protection(prediction, evaluated_at=evaluated_at,
        capital_policy=capital_policy, include_unknown_paths=True)
