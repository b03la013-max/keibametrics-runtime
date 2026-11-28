"""KAG-JRA Shadow: temporal guard, result isolation, five-layer & bet-type gates."""
import json
import sys
from datetime import datetime
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime/analysis'))
import jra_kag_prerace_shadow as G

RID = 'KM-JRA-TKY-20261129-R01'


def a_final(*, ordered=True, trio=False):
    return {'race_id': RID,
            'scheduled_post_at': '2026-11-29T10:00:00+09:00',
            'final_freeze_timestamp': '2026-11-29T09:27:00+09:00',
            'sha256': 'signed-final-digest-reference',
            'final_prediction_package': {'ranking': ['1', '2', '3', '4'],
                                         'roles': {'1': ['W'], '2': ['P2'], '3': ['P3'], '4': []}},
            'final_ticket': {'no_bet': False,
                             'tickets': ([{'bet_type': 'EXACTA', 'selection': [1, 2], 'stake': 100}] if ordered else [])
                             + ([{'bet_type': 'TRIO', 'selection': [1, 2, 3], 'stake': 100}] if trio else [])}}


def at(iso):
    return datetime.fromisoformat(iso)


def test_prestart_without_results_and_multicombination_counterchallenge(tmp_path):
    fp = tmp_path / 'runtime/final_artifacts' / (RID+'.json')
    fp.parent.mkdir(parents=True)
    fp.write_text(json.dumps(a_final()))
    result = tmp_path / 'runtime/results' / (RID+'.json')
    result.parent.mkdir(parents=True)
    result.write_text(json.dumps({'official_result': {'top3': [1, 2, 3]}}))
    done = G.freeze_day(tmp_path, '2026-11-29', now=at('2026-11-29T09:40:00+09:00'))
    assert done['created_count'] == 1
    c = G._read(tmp_path / 'runtime/jra_governance/prerace' / (RID+'.json'))
    assert {x['code'] for x in c['checks'] if x['status'] == 'CHALLENGE'} >= {
        'MULTI_PRIMARY_ABSENT', 'STATIC_TOP3_NOT_W', 'ORDERED_STAKE_EXCEEDS_MULTI'}
    assert c['true_forward_oos'].startswith('PENDING')
    assert c['git_first_commit_prestart_verified'] is False
    assert all(c['summary']['layer_coverage'][x] >= 1 for x in G.LAYERS)
    assert 'official_result' not in json.dumps(c) and 'finish_order' not in json.dumps(c)
    result.write_text(json.dumps({'official_result': {'top3': [4, 3, 2]}}))
    assert G.freeze_day(tmp_path, '2026-11-29', now=at('2026-11-29T09:45:00+09:00'))['created_count'] == 0
    assert c == G._read(tmp_path / 'runtime/jra_governance/prerace' / (RID+'.json'))


def test_rejects_poststart_and_bad_timezone(tmp_path):
    fp = tmp_path / 'runtime/final_artifacts' / (RID+'.json')
    fp.parent.mkdir(parents=True)
    fp.write_text(json.dumps(a_final()))
    done = G.freeze_day(tmp_path, '2026-11-29', now=at('2026-11-29T10:00:00+09:00'))
    assert done['created_count'] == 0
    assert 'NOT_PRESTART_ELIGIBLE' in done['skipped'][0]['reason']
    with pytest.raises(ValueError, match='AWARE_CLOCK_REQUIRED'):
        G.analyze_final(a_final(), race_id=RID, now=at('2026-11-29T09:40:00'), artifact_sha256='f')


def test_trio_and_no_bet_not_flagged_as_multi_gap():
    d = G.analyze_final(a_final(trio=True), race_id=RID,
                        now=at('2026-11-29T09:45:00+09:00'), artifact_sha256='s')
    assert not any(x['code'] == 'MULTI_PRIMARY_ABSENT'
                   for x in d['checks'] if x['status'] == 'CHALLENGE')
    no = a_final()
    no['final_ticket'] = {'no_bet': True, 'tickets': []}
    d = G.analyze_final(no, race_id=RID,
                        now=at('2026-11-29T09:45:00+09:00'), artifact_sha256='s')
    assert not any(x['code'] == 'MULTI_PRIMARY_ABSENT'
                   for x in d['checks'] if x['status'] == 'CHALLENGE')


def test_unknown_source_not_claimed_verified_and_bad_ticket_red1():
    f = a_final()
    f['final_ticket']['tickets'][0]['selection'] = [1, 99]
    d = G.analyze_final(f, race_id=RID, now=at('2026-11-29T09:45:00+09:00'),
                        artifact_sha256='s')
    assert any(x['code'] == 'TICKET_RUNNER_UNIVERSE_MISMATCH' and x['severity'] == 'P0'
               for x in d['checks'])
    assert any(x['layer'] == 'RED-5' and x['status'] == 'UNKNOWN'
               for x in d['checks'])
    assert d['blue']['source_signature_reverified'] is False


def test_post_audit_never_upgrades_oos_status(tmp_path):
    fp = tmp_path / 'runtime/final_artifacts' / (RID+'.json')
    fp.parent.mkdir(parents=True)
    fp.write_text(json.dumps(a_final()))
    G.freeze_day(tmp_path, '2026-11-29', now=at('2026-11-29T09:45:00+09:00'))
    path = tmp_path / 'runtime/jra_governance/2026-11-29.json'
    path.write_text(json.dumps({'races': [{'race_id': RID, 'challenges': [{'code': 'C'}]}]}))
    audit = G.audit_day(tmp_path, '2026-11-29')
    assert audit['post_result_join_count'] == 1
    assert audit['missing_independent_commit_proof'] is True
    assert audit['forward_oos_performance_claim'] is False
