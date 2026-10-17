import copy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from jra_presentation import build_presentation, save_presentation, read_presentation


def fixture():
    final = json.loads((ROOT / 'runtime/final_artifacts/KM-JRA-KYO-20261017-R07.json').read_text())
    health = json.loads((ROOT / 'evidence/jra_bvi_phase3_20261017/runtime_health.json').read_text())['krs']['body']
    contract = json.loads((ROOT / 'profiles/family_runtime_contracts_20261008_R28.json').read_text())['families']['JRA']
    return final, health, contract


def build(**kw):
    f, h, c = fixture()
    return build_presentation(f, health=h, contract=c, generated_at='2026-10-17T04:40:00+00:00', **kw)


def test_real_kyo7_exact_tickets_and_all_runners():
    bundle = build()
    f, _, _ = fixture()
    assert bundle['detail']['tickets'] == f['final_ticket']['tickets']
    assert bundle['manifest']['final_receipt_sha256'] == '325f88a709dbd6509d8f62498fba17d4d29880d15e828bae226ddf7baa4ec84c'
    assert bundle['detail']['ticket_count'] == 6
    assert bundle['detail']['total_investment'] == 600
    assert len(bundle['detail']['ranking']) == 10
    assert all(len(r['indices']) == 20 for r in bundle['detail']['ranking'])
    assert 'ココロヅヨサ' in bundle['text'] and '600円' in bundle['text']
    assert bundle['detail']['receipts']['KRS']['actual_run_count'] == 5000
    assert bundle['detail']['delivery']['user_delivery_verified'] is False
    assert bundle['detail']['presentation_before_post'] is False


def test_wrong_identity_authority_sha_rejected():
    f, _, _ = fixture()
    for kw in ({'expected_race_id': 'KM-JRA-KYO-20261017-R05'},
               {'expected_final_sha256': '0' * 64},
               {'expected_authority': 'LOCAL'}):
        with pytest.raises(ValueError):
            build(**kw)
    bad = copy.deepcopy(f)
    bad['final_ticket']['tickets'][0]['stake'] += 100
    _, h, c = fixture()
    with pytest.raises(ValueError):
        build_presentation(bad, health=h, contract=c, generated_at='2026-10-17T04:40:00Z')


def test_retry_reuses_bytes_and_detects_corruption(tmp_path):
    a = build()
    save_presentation(tmp_path, a)
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    f, h, c = fixture()
    later = build_presentation(f, health=h, contract=c, generated_at='2026-10-17T05:00:00Z')
    save_presentation(tmp_path, later)
    assert before == {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    out = read_presentation(tmp_path, expected_race_id=f['race_id'], expected_final_sha256=f['sha256'])
    assert out['text'] == a['text']
    (tmp_path / 'presentation.md').write_text('truncated')
    with pytest.raises(ValueError):
        read_presentation(tmp_path)


def test_renderer_failure_uses_exact_signed_ticket_ledger(monkeypatch):
    import jra_presentation
    def fail(_):
        raise RuntimeError('renderer fixture fault')
    monkeypatch.setattr(jra_presentation, 'render_ticket_tree', fail)
    out = build()
    assert out['detail']['render_mode'] == 'EXACT_TICKET_LEDGER_FALLBACK'
    assert out['detail']['ticket_count'] == 6
    assert out['detail']['total_investment'] == 600
    assert all(str(t['stake']) + '円' in out['text'] for t in out['detail']['tickets'])


def test_replay_and_unsigned_policy_block_are_not_formal():
    f, h, c = fixture()
    f['temporal_mode'] = 'POST-START-REPLAY'
    from jra_production_postresult import _sha
    f['sha256'] = _sha({k:v for k,v in f.items() if k != 'sha256'})
    with pytest.raises(ValueError):
        build_presentation(f, health=h, contract=c, generated_at='2026-10-17T04:40:00Z')
    with pytest.raises((ValueError, KeyError)):
        build_presentation({'race_id': 'KM-JRA-KYO-20261017-R03'}, health=h, contract=c, generated_at='2026-10-17T04:40:00Z')


def test_real_kyo5_paper_reference_is_not_purchase():
    _, h, c = fixture()
    f = json.loads((ROOT / 'runtime/final_artifacts/KM-JRA-KYO-20261017-R05.json').read_text())
    out = build_presentation(f, health=h, contract=c, generated_at='2026-10-17T04:40:00Z')
    assert out['detail']['status'] == 'PAPER'
    assert out['detail']['ticket_count'] == 0 and out['detail']['total_investment'] == 0
    assert out['detail']['mec_reference'] == {'ticket_count': 8, 'required_capital': 800}
    assert '正式券面 0点・0円' in out['text'] and 'MEC参考 8点・800円' in out['text']


def test_partial_publication_after_timeout_recovers_original_time(tmp_path):
    a = build()
    (tmp_path / 'presentation_detail.json').write_text(json.dumps(a['detail'], ensure_ascii=False, sort_keys=True, indent=2)+'\n')
    f, h, c = fixture()
    b = build_presentation(f, health=h, contract=c, generated_at='2026-10-17T06:00:00Z')
    save_presentation(tmp_path, b)
    assert read_presentation(tmp_path)['manifest'] == a['manifest']


def test_actual_replay_intent_and_kyo3_failure_cannot_be_formal():
    _, h, c = fixture()
    replay = json.loads((ROOT / 'runtime/jra_formal_intents/KM-JRA-KYO-20261012-R11-REPLAY-R1.json').read_text())
    assert replay['temporal_mode'] == 'POST-START-REPLAY'
    rows = json.loads((ROOT / 'evidence/jra_delivery_presentation_20261017/fixture_provenance.json').read_text())
    blocked = rows['kyo3_status']
    assert blocked['execution_error'] == 'AKI_SELECTED_HEAD_WITHOUT_MATERIAL_PAIR'
    for row in (replay, blocked):
        with pytest.raises((ValueError, KeyError)):
            build_presentation(row, health=h, contract=c, generated_at='2026-10-17T04:40:00Z')


def test_delivery_cli_timeout_preserves_final_and_compact_readback(tmp_path, monkeypatch, capsys):
    import io
    import runpy
    import urllib.request
    import family_authority_guard
    f, h, _ = fixture()
    final_path = ROOT / 'runtime/final_artifacts/KM-JRA-KYO-20261017-R07.json'
    original = final_path.read_bytes()
    monkeypatch.setattr(family_authority_guard, 'resolve_current_authority',
        lambda **kw: (None, {'common_family_components': {
            'family_runtime_contracts_profile': 'profiles/family_runtime_contracts_20261008_R28.json'}}))
    monkeypatch.setattr(urllib.request, 'urlopen', lambda *a, **kw: io.BytesIO(json.dumps(h).encode()))
    monkeypatch.setattr(sys, 'argv', ['jra_delivery.py', '--final', str(final_path), '--output-dir', str(tmp_path),
                                   '--run-url', 'https://github.com/b03la013-max/keibametrics-runtime/actions/runs/38998786014',
                                   '--expected-race-id', f['race_id']])
    runpy.run_path(str(ROOT / 'runtime/jra_delivery.py'), run_name='__main__')
    first = capsys.readouterr().out
    runpy.run_path(str(ROOT / 'runtime/jra_delivery.py'), run_name='__main__')
    assert capsys.readouterr().out == first
    def timeout(*a, **kw):
        raise TimeoutError('health timeout fixture')
    monkeypatch.setattr(urllib.request, 'urlopen', timeout)
    with pytest.raises(TimeoutError):
        runpy.run_path(str(ROOT / 'runtime/jra_delivery.py'), run_name='__main__')
    assert read_presentation(tmp_path, expected_race_id=f['race_id'], expected_final_sha256=f['sha256'])['text'] == first
    monkeypatch.setattr(sys, 'argv', ['jra_presentation.py', '--directory', str(tmp_path),
                                    '--expected-race-id', f['race_id'], '--expected-final-sha256', f['sha256']])
    runpy.run_path(str(ROOT / 'runtime/jra_presentation.py'), run_name='__main__')
    assert capsys.readouterr().out == first
    assert final_path.read_bytes() == original


def test_workflows_publish_presentation_and_reuse_before_source():
    formal = (ROOT / '.github/workflows/km-formal-request-runner.yml').read_text()
    single = (ROOT / '.github/workflows/km-jra-formal-single-entry.yml').read_text()
    assert 'cp "runtime/jra_delivery/$RID"/presentation* krs-artifacts/' in formal
    assert 'presentation_availability.json' in formal
    assert single.index('presentation_detail.json') < single.index('- name: Build canonical JRA SOURCE request')
    assert '--expected-race-id "$RID"' in single
    assert single.index('runtime/jra_presentation.py') < single.index('python runtime/jra_delivery.py')
    assert 'verify_final(f);print(f["sha256"])' in single
