from copy import deepcopy
import hashlib
import itertools
import json
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from jra_aki_v21 import PROFILE, materialize, select_columns, apply_authorized_v21
from jra_aki_capital_preflight import AXES, AKICapitalError, sha, verify_aki_ticket_binding
from minimum_efficient_coverage import build_mec_plan
from capital_policy import resolve_capital_policy


def fixture(tmp_path):
    """Synthetic enacted registries ONLY; not Production scoring assumptions."""
    values = dict(zip(AXES, [20, 20, 20, 90, 10, 0, 0]))
    source = {'family_id': 'JRA', 'race_id': 'TEST', 'source_snapshot_sha256': 'a'*64,
              'source_freeze_at': '2026-10-11T10:00:00+09:00',
              'prediction_cutoff': '2026-10-11T10:05:00+09:00'}
    def fact(category):
        return {'category': category, 'status': 'OBSERVED', 'source_snapshot_sha256': 'a'*64,
                'observed_at': source['source_freeze_at'], 'evidence_refs': ['TEST-SOURCE'],
                'source_fact': 'Synthetic mechanical acceptance, not live source'}
    component_registry = {'kind': 'AKI_COMPONENT_MAPPING', 'family_id': 'JRA',
                          'production_authority': True, 'mapping_version': 'TEST-NOT-PRODUCTION',
                          'axes': {a: {'rule_id': 'TEST-' + a, 'formula': 'SUM',
                             'terms': [{'feature': a, 'category_map': {'LOW': v, 'HIGH': 70}}]}
                                   for a, v in values.items()}}
    component_registry['axes']['ASI']['formula'] = '100_MINUS_SUM'
    component_registry['axes']['ASI']['terms'][0]['category_map']['LOW'] = 10
    source['aki_evidence_features'] = {a: fact('LOW') for a in AXES}
    def rule(name, feature, category):
        return {'rule_id': name, 'all_of': [{'feature': feature, 'category': category}]}
    column_registry = {'kind': 'AKI_COLUMN_SELECTION', 'family_id': 'JRA',
                       'production_authority': True, 'mapping_version': 'TEST-NOT-PRODUCTION',
                       'columns': {c: {'BASE': [rule('TEST-BASE-' + c, c, 'MAIN')],
                                       'REVIEW': [rule('TEST-REVIEW-' + c, c, 'ALTERNATIVE')]}
                                   for c in ('W', 'P2', 'P3')},
                       'pairs': [rule('TEST-PAIR', 'compatible', 'YES')],
                       'thirds': [rule('TEST-THIRD', 'compatible', 'YES')]}
    source['aki_selection_features'] = {
        'runners': {str(i): {c: fact('MAIN' if i in main else 'ALTERNATIVE' if i in alt else 'OTHER')
                  for c, main, alt in [('W', {1}, {2}), ('P2', {2,3}, {4}), ('P3', {3,4}, {5})]}
                    for i in range(1,6)},
        'pairs': {f'{h}>{s}': {'compatible': fact('YES')} for h,s in itertools.permutations(range(1,6),2)},
        'thirds': {f'{h}>{s}>{t}': {'compatible': fact('YES')} for h,s,t in itertools.permutations(range(1,6),3)}}
    request = {'family_id': 'JRA', 'race_id': 'TEST', 'source_snapshot_sha256': 'a'*64,
               'prediction_cutoff': source['prediction_cutoff'],
               'runners': [{'runner_id': str(i)} for i in range(1,6)],
               'static_prediction': {'ranking': ['1','2','3','4','5'], 'roles': {},
                                     'aki_jra_v2': {'old_proxy': True}}}
    (tmp_path/'runtime').mkdir()
    code = (ROOT/'runtime/jra_aki_v21.py').read_bytes()
    (tmp_path/'runtime/jra_aki_v21.py').write_bytes(code)
    activation = {'status': 'PRODUCTION_AUTHORIZED', 'profile': PROFILE, 'automatic_promotion': False,
                  'runtime_sha256': hashlib.sha256(code).hexdigest()}
    for key, reg in [('components', component_registry), ('columns', column_registry)]:
        path = key + '.json'
        (tmp_path/path).write_text(json.dumps(reg))
        activation[key] = {'path': path, 'sha256': sha(reg)}
    authority = {'family_scoped_authority': {'JRA': {'aki_v21_activation': activation}}}
    return request, source, component_registry, column_registry, authority


def execute(request, source, authority, root):
    out = apply_authorized_v21(request, source, authority, root=root)
    mec = build_mec_plan(out)
    report = verify_aki_ticket_binding(out, mec, source=source, current_authority=authority, root=root)
    return out, mec, report


def test_registered_calculation_selection_mec_capital_end_to_end(tmp_path):
    req, src, _, _, auth = fixture(tmp_path)
    before = deepcopy((req, src, auth))
    out, mec, report = execute(req, src, auth, tmp_path)
    assert (req, src, auth) == before
    assert out['static_prediction']['ranking'] == req['static_prediction']['ranking']
    assert 'aki_jra_v2' not in out['static_prediction']
    assert report['official_v21_verified'] is True
    assert report['ticket_count'] == 5
    assert len(out['role_registry']) == 15
    assert out['static_prediction']['aki_jra_v21']['total'] == 16
    decision = resolve_capital_policy({'capital_policy': {'mode': 'HARD_RACE_BUDGET', 'max_race_capital': 10000}}, mec)
    assert decision['required_capital'] == 500
    assert decision['unused_budget'] == 9500
    assert not decision['budget_fill_required']


@pytest.mark.parametrize('axis,column', [('P2-AKI','P2'), ('P3-AKI','P3'), ('W-AKI','W')])
def test_each_axis_reviews_only_its_corresponding_column(tmp_path, axis, column):
    req, src, _, _, auth = fixture(tmp_path)
    base, base_mec, _ = execute(req, src, auth, tmp_path)
    src['aki_evidence_features'][axis]['category'] = 'HIGH'
    wide, wide_mec, _ = execute(req, src, auth, tmp_path)
    for c in ('W','P2','P3'):
        old = base['aki_column_selection']['columns'][c]
        new = wide['aki_column_selection']['columns'][c]
        assert len(new) > len(old) if c == column else new == old
    assert wide_mec['ticket_count'] > base_mec['ticket_count']


def test_budget_does_not_select_roles_or_erase_semantics(tmp_path):
    req, src, _, _, auth = fixture(tmp_path)
    out, mec, _ = execute(req, src, auth, tmp_path)
    small = deepcopy(req)
    small['capital_policy'] = {'mode': 'HARD_RACE_BUDGET', 'max_race_capital': 100, 'insufficient_action': 'PAPER'}
    out2, mec2, _ = execute(small, src, auth, tmp_path)
    assert out2['aki_column_selection'] == out['aki_column_selection']
    assert mec2['tickets'] == mec['tickets']
    assert resolve_capital_policy(small, mec2)['decision'] == 'PAPER'


@pytest.mark.parametrize('case', ['missing_fact','late_fact','wrong_source','rule_change','runtime_change','no_activation'])
def test_unknown_or_unauthorized_inputs_block_without_proxy_fallback(tmp_path, case):
    req, src, _, _, auth = fixture(tmp_path)
    if case == 'missing_fact': del src['aki_evidence_features']['P2-AKI']
    elif case == 'late_fact': src['aki_evidence_features']['P2-AKI']['observed_at'] = '2026-10-11T11:00:00+09:00'
    elif case == 'wrong_source': src['aki_evidence_features']['P2-AKI']['source_snapshot_sha256'] = 'other'
    elif case == 'rule_change': (tmp_path/'components.json').write_text('{}')
    elif case == 'runtime_change': (tmp_path/'runtime/jra_aki_v21.py').write_text('# tampered')
    else:
        auth = {}
        req['aki_calculation_requirement'] = 'OFFICIAL_V2_1'
    with pytest.raises(AKICapitalError): execute(req, src, auth, tmp_path)


def test_signed_source_recomputation_rejects_forged_decision(tmp_path):
    req, src, _, _, auth = fixture(tmp_path)
    out, mec, _ = execute(req, src, auth, tmp_path)
    out['official_aki_verification']['activation_sha256'] = 'forged'
    with pytest.raises(AKICapitalError, match='RECOMPUTATION_MISMATCH'):
        verify_aki_ticket_binding(out, mec, source=src, current_authority=auth, root=tmp_path)
    with pytest.raises(AKICapitalError, match='TRUST_CONTEXT_REQUIRED'):
        verify_aki_ticket_binding(out, mec)
