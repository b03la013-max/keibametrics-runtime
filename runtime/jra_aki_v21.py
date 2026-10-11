"""Execute registered official JRA AKI mappings and column decision rules.

No embedded scoring weights, fallback axes, fixed formations or budget-driven
selection. Registries must come from verified Current Authority, not requests.
"""
from copy import deepcopy
from datetime import datetime
import json
import hashlib
from pathlib import Path
import math

from jra_aki_capital_preflight import AXES, AKICapitalError, sha, verify_official_v21

PROFILE = 'KM-JRA-AKI-V2.1-REGISTERED-EXECUTION-20261011'


def apply_authorized_v21(request, source, current_authority, *, root):
    """Current Authority owns registry activation; requests cannot enact rules."""
    activation = (((current_authority.get('family_scoped_authority') or {}).get('JRA') or {})
                  .get('aki_v21_activation') or {})
    if not activation:
        if request.get('aki_calculation_requirement') == 'OFFICIAL_V2_1':
            raise AKICapitalError('OFFICIAL_AKI_V21_REGISTRY_NOT_ACTIVATED')
        return deepcopy(request)
    if (activation.get('status') != 'PRODUCTION_AUTHORIZED'
            or activation.get('automatic_promotion') is not False
            or activation.get('profile') != PROFILE):
        raise AKICapitalError('OFFICIAL_AKI_V21_AUTHORIZATION_INVALID')
    root = Path(root).resolve()
    if activation.get('runtime_sha256') != hashlib.sha256((root / 'runtime/jra_aki_v21.py').read_bytes()).hexdigest():
        raise AKICapitalError('OFFICIAL_AKI_V21_RUNTIME_FINGERPRINT_MISMATCH')
    registries = {}
    for key in ('components', 'columns'):
        spec = activation.get(key) or {}
        path = (root / str(spec.get('path') or '')).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise AKICapitalError('OFFICIAL_AKI_REGISTRY_FILE_MISSING:' + key)
        registries[key] = json.loads(path.read_text())
        if sha(registries[key]) != spec.get('sha256'):
            raise AKICapitalError('OFFICIAL_AKI_REGISTRY_FINGERPRINT_MISMATCH:' + key)
    policy = registries['components'].get('feature_compiler_policy')
    if policy is not None:
        compiler = root / 'runtime/jra_aki_v21_features.py'
        if activation.get('feature_compiler_sha256') != hashlib.sha256(compiler.read_bytes()).hexdigest():
            raise AKICapitalError('OFFICIAL_AKI_COMPILER_FINGERPRINT_MISMATCH')
        from jra_aki_v21_features import compile_features
        source = compile_features(request, source, policy)
    package, calculation = materialize(source, registries['components'],
                                      registry_hash=activation['components']['sha256'])
    out = select_columns(request, source, calculation, registries['columns'],
                         registry_hash=activation['columns']['sha256'])
    out['official_aki_package'] = package
    out['official_aki_verification'] = {'status': 'PASS', 'profile': PROFILE,
                                       'calculation': calculation,
                                       'activation_sha256': sha(activation)}
    if policy is not None:
        out['aki_compiler_receipt'] = source['aki_compiler_receipt']
        out['aki_information_gate'] = source['aki_compiler_receipt']['information_gate']
    out['aki_calculation_requirement'] = 'OFFICIAL_V2_1'
    for name in ('role_registry', 'pair_dispositions', 'third_dispositions'):
        for row in out[name]:
            row.update(authority=PROFILE, production_authority=True)
    return out


def _number(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        raise AKICapitalError('AKI_NONFINITE_VALUE')
    return v


def _time(value):
    try:
        t = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if t.tzinfo is None:
            raise ValueError()
        return t
    except (AttributeError, TypeError, ValueError) as exc:
        raise AKICapitalError('AKI_TIME_INVALID') from exc


def _registry(registry, expected_hash, kind):
    if not expected_hash or sha(registry) != expected_hash:
        raise AKICapitalError('AKI_REGISTRY_FINGERPRINT_MISMATCH')
    if (registry.get('family_id') != 'JRA' or registry.get('kind') != kind
            or registry.get('production_authority') is not True
            or not registry.get('mapping_version')):
        raise AKICapitalError('AKI_REGISTERED_AUTHORITY_REQUIRED')


def _fact(facts, name, *, cutoff, source_hash):
    fact = facts.get(name)
    if (not isinstance(fact, dict) or fact.get('status') != 'OBSERVED'
            or fact.get('source_snapshot_sha256') != source_hash
            or not fact.get('evidence_refs') or not fact.get('source_fact')
            or 'category' not in fact):
        raise AKICapitalError('AKI_REQUIRED_FACT_MISSING:' + name)
    if _time(fact.get('observed_at')) > cutoff:
        raise AKICapitalError('AKI_POST_CUTOFF_FACT:' + name)
    return fact


def materialize(source, registry, *, registry_hash):
    """Compiler categories -> registered contributions -> official axes.

    Source authenticity is verified by the parent signed-SOURCE route. Here
    source identity, timestamps, every observed fact and authority hashes bind
    deterministic computation. No synthetic neutral observation is allowed.
    """
    _registry(registry, registry_hash, 'AKI_COMPONENT_MAPPING')
    if source.get('family_id') != 'JRA' or not source.get('race_id'):
        raise AKICapitalError('AKI_JRA_RACE_REQUIRED')
    source_hash = source.get('source_snapshot_sha256')
    cutoff = _time(source.get('prediction_cutoff'))
    if not source_hash or _time(source.get('source_freeze_at')) > cutoff:
        raise AKICapitalError('AKI_SOURCE_FREEZE_INVALID')
    specs = registry.get('axes') or {}
    if set(specs) != set(AXES):
        raise AKICapitalError('AKI_MAPPING_AXES_INCOMPLETE')
    facts = source.get('aki_evidence_features') or {}
    components = {}
    for axis in AXES:
        spec = specs[axis]
        if not spec.get('rule_id') or spec.get('formula') not in {'SUM', '100_MINUS_SUM'}:
            raise AKICapitalError('AKI_MAPPING_FORMULA_INVALID:' + axis)
        terms = spec.get('terms') or []
        names = [x.get('feature') for x in terms]
        if not terms or not all(names) or len(names) != len(set(names)):
            raise AKICapitalError('AKI_MAPPING_TERMS_INVALID:' + axis)
        contributions, refs, raw = [], [], []
        for term in terms:
            f = _fact(facts, term['feature'], cutoff=cutoff, source_hash=source_hash)
            categories = term.get('category_map') or {}
            category = f['category']
            if not isinstance(category, str) or category not in categories:
                raise AKICapitalError('AKI_UNREGISTERED_CATEGORY:' + term['feature'])
            contribution = _number(categories[category])
            contributions.append({'feature': term['feature'], 'category': category,
                                  'contribution': contribution, 'evidence_refs': f['evidence_refs']})
            refs.extend(f['evidence_refs'])
            raw.append(f['source_fact'])
        value = sum(t['contribution'] for t in contributions)
        if spec['formula'] == '100_MINUS_SUM':
            value = 100 - value
        # Clamping is applied only when explicitly enacted in the registry.
        if 'bounds' in spec:
            bounds = spec['bounds']
            if bounds != [0, 100]:
                raise AKICapitalError('AKI_MAPPING_BOUNDS_INVALID')
            value = max(0, min(100, value))
        if not 0 <= value <= 100:
            raise AKICapitalError('AKI_MAPPING_RESULT_OUT_OF_RANGE:' + axis)
        components[axis] = {'value': value, 'rule_id': spec['rule_id'],
                            'mapping_version': registry['mapping_version'], 'status': 'CALCULATED',
                            'evidence_refs': sorted(set(refs)), 'source_fact': raw,
                            'contributions': contributions}
    package = {'version': 'AKI-JRA v2.1', 'profile': PROFILE, 'race_id': source['race_id'],
               'source_snapshot_sha256': source_hash, 'prediction_cutoff': source['prediction_cutoff'],
               'mapping_registry_sha256': registry_hash, 'components': components}
    package['sha256'] = sha(package)
    rules = {axis: {'rule_id': spec['rule_id'], 'mapping_version': registry['mapping_version']}
             for axis, spec in specs.items()}
    calculation = verify_official_v21(package, race_id=source['race_id'], source_hash=source_hash,
                                      rule_registry=rules)
    return package, calculation


def _select(facts, rules, *, cutoff, source_hash):
    matches = []
    for rule in rules:
        tests = rule.get('all_of') or []
        if not rule.get('rule_id') or not tests:
            raise AKICapitalError('AKI_SELECTION_RULE_INVALID')
        observed = []
        for test in tests:
            f = _fact(facts, test['feature'], cutoff=cutoff, source_hash=source_hash)
            observed.append((f, test['category']))
        if all(f['category'] == cat for f, cat in observed):
            matches.append({'rule_id': rule['rule_id'], 'evidence_refs': sorted(set(
                r for f, _ in observed for r in f['evidence_refs']))})
    return matches


def select_columns(request, source, calculation, registry, *, registry_hash):
    """Rule-bound candidate selection under each column-specific AKI review.

    Every runner is evaluated for each role; selected pairs are head-local,
    thirds pair-local. Full prediction ranking/Full20 stay unchanged. The
    entire decision universe is preserved, independently of purchased tickets.
    """
    _registry(registry, registry_hash, 'AKI_COLUMN_SELECTION')
    if (request.get('race_id') != source.get('race_id')
            or request.get('source_snapshot_sha256') != source.get('source_snapshot_sha256')
            or request.get('prediction_cutoff') != source.get('prediction_cutoff')):
        raise AKICapitalError('AKI_SELECTION_SOURCE_MISMATCH')
    axes = calculation['axes']
    cutoff = _time(source.get('prediction_cutoff'))
    source_hash = source['source_snapshot_sha256']
    rank = [str(x) for x in request['static_prediction']['ranking']]
    ids = {str(r['runner_id']) for r in request['runners']}
    if set(rank) != ids or len(rank) != len(ids):
        raise AKICapitalError('AKI_FULL_RUNNER_UNIVERSE_INVALID')
    triggers = {
        'W': 'REVIEW' if axes['W-AKI'] >= 50 or axes['ASI'] < 65 else 'BASE',
        'P2': 'REVIEW' if axes['P2-AKI'] >= 50 or axes['RSI'] >= 60 else 'BASE',
        'P3': 'REVIEW' if axes['P3-AKI'] >= 50 or axes['RSI'] >= 60 else 'BASE',
    }
    compiled = source.get('aki_selection_features') or {}
    if set(compiled.get('runners') or {}) != ids:
        raise AKICapitalError('AKI_SELECTION_RUNNER_FEATURES_INCOMPLETE')
    columns = {c: [] for c in triggers}
    ledger = []
    main = {c: set() for c in triggers}
    tiered = registry.get('disposition_policy') == 'MAIN_ORDERED_ALTERNATIVE_SET_PROTECTION'
    for c, mode in triggers.items():
        spec = (registry.get('columns') or {}).get(c) or {}
        rules = spec.get('BASE')
        if not isinstance(rules, list) or not rules:
            raise AKICapitalError('AKI_BASE_SELECTION_RULE_MISSING:' + c)
        chosen_rules = list(rules)
        if mode == 'REVIEW':
            extension = spec.get('REVIEW')
            if not isinstance(extension, list) or not extension:
                raise AKICapitalError('AKI_COLUMN_REVIEW_RULE_MISSING:' + c)
            chosen_rules.extend(extension)
        for rid in rank:
            matches = _select(compiled['runners'][rid], chosen_rules, cutoff=cutoff, source_hash=source_hash)
            base_matches = _select(compiled['runners'][rid], rules, cutoff=cutoff, source_hash=source_hash)
            if base_matches:
                main[c].add(rid)
            if matches:
                columns[c].append(rid)
            ledger.append({'runner_id': rid, 'column': c, 'status': ('CORE' if not tiered or base_matches else 'PROTECTED') if matches else 'EXCLUDED',
                           'reason': 'REGISTERED_POSITIVE_EVIDENCE' if matches else 'REGISTERED_RULES_NOT_SATISFIED',
                           'rule_matches': matches, 'review_mode': mode})
    if any(not v for v in columns.values()):
        raise AKICapitalError('AKI_EVIDENCE_SELECTED_COLUMN_EMPTY')
    if len(columns['W']) == 1 and (axes['W-AKI'] >= 60 or axes['ASI'] < 65):
        raise AKICapitalError('AKI_SINGLE_HEAD_FORBIDDEN')
    pairs, thirds = [], []
    for h in columns['W']:
        for s in columns['P2']:
            if h == s:
                continue
            key = h + '>' + s
            facts = (compiled.get('pairs') or {}).get(key)
            if not isinstance(facts, dict):
                raise AKICapitalError('AKI_HEAD_LOCAL_PAIR_FACT_MISSING:' + key)
            matches = _select(facts, registry.get('pairs') or [], cutoff=cutoff, source_hash=source_hash)
            if not registry.get('pairs'):
                raise AKICapitalError('AKI_PAIR_RULES_MISSING')
            ordered_pair = not tiered or (h in main['W'] and s in main['P2'])
            pairs.append({'head': h, 'second': s, 'status': ('PURCHASE' if ordered_pair else 'PROTECT') if matches else 'SEMANTIC_ONLY',
                          'reason': 'REGISTERED_PAIR_EVIDENCE' if matches else 'NO_MATERIAL_PAIR_EVIDENCE',
                          'rule_matches': matches})
            if not matches:
                continue
            for t in columns['P3']:
                if t in {h, s}:
                    continue
                tkey = key + '>' + t
                tfacts = (compiled.get('thirds') or {}).get(tkey)
                if not isinstance(tfacts, dict):
                    raise AKICapitalError('AKI_PAIR_LOCAL_THIRD_FACT_MISSING:' + tkey)
                tmatches = _select(tfacts, registry.get('thirds') or [], cutoff=cutoff, source_hash=source_hash)
                if not registry.get('thirds'):
                    raise AKICapitalError('AKI_THIRD_RULES_MISSING')
                thirds.append({'head': h, 'second': s, 'third': t,
                               'status': ('PURCHASE' if not tiered or (ordered_pair and t in main['P3']) else 'PROTECT') if tmatches else 'SEMANTIC_ONLY',
                               'reason': 'REGISTERED_THIRD_EVIDENCE' if tmatches else 'GLOBAL_P3_SEMANTIC_ONLY',
                               'rule_matches': tmatches})
    if set(columns['W']) != {x['head'] for x in pairs if x['status'] in {'PURCHASE','PROTECT'}}:
        raise AKICapitalError('AKI_SELECTED_HEAD_WITHOUT_MATERIAL_PAIR')
    result = deepcopy(request)
    result['role_registry'] = ledger
    result['pair_dispositions'] = pairs
    result['third_dispositions'] = thirds
    result['purchased_heads'] = columns['W']
    result['static_prediction']['roles'] = {rid: [c for c in columns if rid in columns[c]] for rid in rank}
    result['static_prediction']['aki_jra_v21'] = deepcopy(calculation)
    result['static_prediction'].pop('aki_jra_v2', None)
    result['aki_column_selection'] = {'profile': PROFILE, 'registry_sha256': registry_hash,
                                      'triggers': triggers, 'columns': columns,
                                      'direct_ticket_count_control': False,
                                      'budget_input_used': False}
    result['aki_column_selection']['sha256'] = sha(result['aki_column_selection'])
    return result
