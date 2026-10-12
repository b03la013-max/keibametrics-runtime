"""AKI-to-actual-ticket binding, independent of probability or ticket caps.

Central v2.3 articles 34-36 and 423/440: v2.1 has separate P2/P3 axes.
The existing Full20 v2 width proxy is explicitly not the official v2.1.
"""
from __future__ import annotations
import hashlib
import json
import math

PROFILE = 'KM-JRA-AKI-CAPITAL-PREFLIGHT-v1.0-20261011'
AXES = ('W-AKI', 'P2-AKI', 'P3-AKI', 'ASI', 'RSI',
        'external_change', 'solid_finish_correction')


class AKICapitalError(ValueError):
    pass


def sha(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                   separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def verify_official_v21(package, *, race_id, source_hash, rule_registry):
    """Verify supplied official components; never infer missing mapping/axes.

    Caller must obtain rule_registry from verified Current Authority. Hashes
    bind the package; they do not replace source/authority signature checks.
    """
    if package.get('version') != 'AKI-JRA v2.1':
        raise AKICapitalError('OFFICIAL_AKI_VERSION_MISMATCH')
    if package.get('race_id') != race_id or package.get('source_snapshot_sha256') != source_hash:
        raise AKICapitalError('OFFICIAL_AKI_SOURCE_MISMATCH')
    if not source_hash or not rule_registry:
        raise AKICapitalError('OFFICIAL_AKI_AUTHORITY_MISSING')
    if package.get('sha256') != sha({k: v for k, v in package.items() if k != 'sha256'}):
        raise AKICapitalError('OFFICIAL_AKI_DIGEST_MISMATCH')
    values = {}
    components = package.get('components') or {}
    if set(components) != set(AXES):
        raise AKICapitalError('OFFICIAL_AKI_COMPONENTS_INCOMPLETE')
    for axis in AXES:
        row = components[axis]
        value = row.get('value')
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 100:
            raise AKICapitalError('OFFICIAL_AKI_VALUE_INVALID:' + axis)
        rule = rule_registry.get(axis) or {}
        if (not rule.get('rule_id') or not rule.get('mapping_version')
                or row.get('rule_id') != rule['rule_id']
                or row.get('mapping_version') != rule['mapping_version']
                or row.get('status') != 'CALCULATED' or not row.get('evidence_refs')
                or not row.get('source_fact')):
            raise AKICapitalError('OFFICIAL_AKI_PROVENANCE_INVALID:' + axis)
        values[axis] = value
    # Central v2.3 article 36: ASI stays outside the total; no invented clamp.
    total = (.30 * values['W-AKI'] + .20 * values['P2-AKI']
             + .20 * values['P3-AKI'] + .20 * values['RSI']
             + .10 * values['external_change'] - values['solid_finish_correction'])
    return {'version': 'AKI-JRA v2.1', 'axes': values, 'total': total,
            'axis_failure_risk': 100 - values['ASI'],
            'P-AKI_compatibility_only': .45 * values['P2-AKI'] + .55 * values['P3-AKI'],
            'axis_candidate_rule': ('SINGLE_AXIS_CANDIDATE' if values['ASI'] >= 80 else
                                    'SINGLE_AXIS_WITH_FAILURE_REVIEW' if values['ASI'] >= 65 else
                                    'TWO_PILLARS_OR_ROLE_DIVERSITY' if values['ASI'] >= 50 else
                                    'SINGLE_AXIS_FORBIDDEN'),
            'direct_ticket_count_control': False, 'package_sha256': package['sha256']}


def _key(ticket):
    bt = ticket.get('bet_type')
    if bt not in {'EXACTA', 'TRIFECTA', 'TRIO'}:
        raise AKICapitalError('UNSUPPORTED_TICKET_TYPE')
    selection = tuple(str(x) for x in ticket.get('selection', []))
    if len(selection) != (2 if bt == 'EXACTA' else 3) or len(set(selection)) != len(selection):
        raise AKICapitalError('INVALID_TICKET_SELECTION')
    return bt, tuple(sorted(selection)) if bt == 'TRIO' else selection


def verify_aki_ticket_binding(request, mec, *, source=None, current_authority=None, root=None):
    """Stop a material PURCHASE Cartesian universe from bypassing width policy.

    Applies to the authorized Static Owner, whose policy selects the actual
    PURCHASE rows. General PROTECT/tail coverage remains owned by Common MEC.
    """
    static = request.get('static_prediction') or {}
    if static.get('aki_jra_v21') is not None:
        return _verify_v21_ticket_binding(request, mec, source=source,
                                          current_authority=current_authority, root=root)
    aki = static.get('aki_jra_v2')
    if not isinstance(aki, dict) or not aki.get('formation'):
        raise AKICapitalError('AKI_WIDTH_DECISION_MISSING')
    if request.get('aki_calculation_requirement') == 'OFFICIAL_V2_1':
        # Full20-derived W/P/ASI/RSI is not formal P2/P3 evidence.
        raise AKICapitalError('OFFICIAL_V2_1_NOT_SATISFIED_BY_FULL20_PROXY')
    roles = static.get('roles') or {}
    active = {c: {str(r) for r, cols in roles.items() if c in cols}
              for c in ('W', 'P2', 'P3')}
    f = aki['formation']
    for c, field in [('W', 'heads'), ('P2', 'seconds'), ('P3', 'thirds')]:
        width = f.get(field)
        if isinstance(width, bool) or not isinstance(width, int) or width < 1:
            raise AKICapitalError('AKI_FORMATION_INVALID:' + c)
        available = len(roles) - (1 if len(active['W']) == 1 and c != 'W' else 0)
        if not active[c] or len(active[c]) != min(width, available):
            raise AKICapitalError('AKI_ROLE_WIDTH_MISMATCH:' + c)
    pairs = {(str(h), str(s)) for h in active['W'] for s in active['P2'] if h != s}
    thirds = {(h, s, str(t)) for h, s in pairs for t in active['P3'] if t not in {h, s}}
    actual_pairs = [(str(x['head']), str(x['second']))
                    for x in request.get('pair_dispositions', []) if x.get('status') == 'PURCHASE']
    actual_thirds = [(str(x['head']), str(x['second']), str(x['third']))
                     for x in request.get('third_dispositions', []) if x.get('status') == 'PURCHASE']
    if len(actual_pairs) != len(set(actual_pairs)) or set(actual_pairs) != pairs:
        raise AKICapitalError('AKI_PAIR_PURCHASE_SET_MISMATCH')
    if len(actual_thirds) != len(set(actual_thirds)) or set(actual_thirds) != thirds:
        raise AKICapitalError('AKI_THIRD_PURCHASE_SET_MISMATCH')
    expected = {('EXACTA', p) for p in pairs} | {('TRIFECTA', t) for t in thirds}
    tickets = mec.get('tickets') or []
    actual = [_key(t) for t in tickets]
    if len(actual) != len(set(actual)) or set(actual) != expected:
        raise AKICapitalError('AKI_ACTUAL_TICKET_SET_MISMATCH')
    total = 0
    for t in tickets:
        stake = t.get('stake')
        if isinstance(stake, bool) or not isinstance(stake, int) or stake <= 0 or stake % 100:
            raise AKICapitalError('AKI_TICKET_STAKE_INVALID')
        total += stake
    if mec.get('ticket_count') != len(tickets) or mec.get('minimum_required_capital') != total:
        raise AKICapitalError('AKI_ACTUAL_COUNT_CAPITAL_MISMATCH')
    return {'profile': PROFILE, 'status': 'PASS',
            'calculation_class': 'OWNER_AUTHORIZED_FULL20_PROXY_NOT_OFFICIAL_V2_1',
            'official_v21_verified': False,
            'aki_decision_sha256': sha(aki), 'ticket_set_sha256': sha(tickets),
            'column_widths': {c: len(v) for c, v in active.items()},
            'exacta_count': len(pairs), 'trifecta_count': len(thirds),
            'ticket_count': len(tickets), 'required_capital': total,
            'probability_or_ev_claim': False, 'budget_fill': False}


def _verify_v21_ticket_binding(request, mec, *, source, current_authority, root):
    if source is None or current_authority is None or root is None:
        raise AKICapitalError('OFFICIAL_AKI_TRUST_CONTEXT_REQUIRED')
    if request.get('aki_calculation_requirement') != 'OFFICIAL_V2_1':
        raise AKICapitalError('OFFICIAL_AKI_REQUIREMENT_MISSING')
    from jra_aki_dispatch import apply_authorized_v21
    independently_rebuilt = apply_authorized_v21(request, source, current_authority, root=root)
    for field in ('official_aki_package', 'official_aki_verification', 'aki_compiler_receipt', 'aki_information_gate', 'aki_column_selection',
                  'role_registry', 'pair_dispositions', 'third_dispositions', 'purchased_heads'):
        if independently_rebuilt.get(field) != request.get(field):
            raise AKICapitalError('OFFICIAL_AKI_RECOMPUTATION_MISMATCH:' + field)
    package = request.get('official_aki_package') or {}
    verified = request.get('official_aki_verification') or {}
    calculated = verified.get('calculation') or {}
    if (verified.get('status') != 'PASS' or not verified.get('activation_sha256')
            or package.get('race_id') != request.get('race_id')
            or package.get('source_snapshot_sha256') != request.get('source_snapshot_sha256')
            or package.get('sha256') != sha({k: v for k, v in package.items() if k != 'sha256'})
            or calculated.get('package_sha256') != package.get('sha256')
            or calculated != request['static_prediction']['aki_jra_v21']):
        raise AKICapitalError('OFFICIAL_AKI_V21_BINDING_INVALID')
    selected = request.get('aki_column_selection') or {}
    if selected.get('sha256') != sha({k: v for k, v in selected.items() if k != 'sha256'}):
        raise AKICapitalError('OFFICIAL_AKI_COLUMN_SELECTION_DIGEST_INVALID')
    # Validate Common MEC independently using its complete semantic coverage
    # rather than applying the old fixed-formation Cartesian assertion.
    from minimum_efficient_coverage import build_mec_plan, validate_mec_plan
    expected = build_mec_plan(request)
    validate_mec_plan(mec)
    if mec.get('tickets') != expected['tickets'] or mec.get('coverage_units') != expected['coverage_units']:
        raise AKICapitalError('OFFICIAL_AKI_ACTUAL_TICKET_SET_MISMATCH')
    return {'profile': PROFILE, 'status': 'PASS', 'official_v21_verified': True,
            'calculation_class': 'REGISTERED_OFFICIAL_AKI_V2_1',
            'package_sha256': package['sha256'], 'selection_sha256': selected['sha256'],
            'ticket_set_sha256': sha(mec['tickets']), 'ticket_count': mec['ticket_count'],
            'required_capital': mec['minimum_required_capital'],
            'probability_or_ev_claim': False, 'budget_fill': False}
