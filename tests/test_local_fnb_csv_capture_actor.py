"""Synthetic transport correctness only: no Provider bytes, admission or LIVE."""
import csv
from datetime import datetime, timedelta, timezone
import hashlib
import io
import json
from pathlib import Path
import zipfile
import urllib.error

import pytest

from runtime import local_fnb_csv_capture_actor as actor
from runtime.local_nar_csv_reference import SCHEMAS

NOW = datetime(2026, 11, 3, 4, 0, tzinfo=timezone.utc)
INTENT = {'venue_id': 'FNB', 'race_date': '2026-11-03', 'race_no': 2,
          'prediction_cutoff': '2026-11-03T10:00:00+00:00'}


def zip_fixture(bad_columns=False):
    race = dict.fromkeys(SCHEMAS['racelist'], '')
    race.update(競馬場='船橋', 競走年月日='20261103', レース番号='2', 発走時刻='1245',
                頭数='1', 距離='1200', 芝ダート区分='ダート', 回り='左')
    horse = dict.fromkeys(SCHEMAS['horselist'], '')
    horse.update(競馬場='船橋', 競走年月日='20261103', レース番号='2', 馬番='1', 馬名='合成試験馬', 着順='1')
    result = io.BytesIO()
    with zipfile.ZipFile(result, 'w') as z:
        for kind, row in [('racelist', race), ('horselist', horse)]:
            s = io.StringIO(newline=''); w = csv.writer(s)
            w.writerow(SCHEMAS[kind])
            values = [row[k] for k in SCHEMAS[kind]]
            w.writerow(values[:-1] if bad_columns else values)
            z.writestr('20261103_' + kind + '.csv', s.getvalue().encode())
    return result.getvalue()


def make_binding(folder, *, grant=True, rights=True):
    code = hashlib.sha256(Path(actor.__file__).read_bytes()).hexdigest()
    text = f'''from runtime.local_fnb_multisource import ProviderBinding
def verify(**kw):
    return {{**{{k:v for k,v in kw.items() if k != 'now'}}, 'passed': {rights!r},
        'automated_get_admitted': True, 'private_retention_admitted': True,
        'cloud_processing_admitted': True}}
def get_capture_binding():
    return {{'provider': ProviderBinding('NAR_OFFICIAL', ({actor.DAILY_URL!r},),
        {code!r}, 'SYNTHETIC_CORRECTNESS_ONLY', {'a'*64!r},
        '2026-11-03T00:00:00+00:00', '2026-11-04T00:00:00+00:00',
        'TEST-ACTOR', {grant!r}, True, True, {{'csv.馬名': 'MUST_NOT_BECOME_TIER2'}}, None, None),
        'verify_rights': verify, 'encoding': 'utf-8', 'header_mode': 'present'}}
'''
    path = folder/'BINDING.py'; path.write_text(text); path.chmod(0o600)
    return path, hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def setup(tmp_path, monkeypatch):
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)
    binding, pin = make_binding(tmp_path)
    root = tmp_path/'private'
    calls = []
    raw = zip_fixture()
    class Response:
        status = 200
        headers = {'content-type': 'application/zip'}
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def geturl(self): return actor.DAILY_URL
        def read(self, size): return raw[:size]
    class Opener:
        def open(self, req, timeout):
            calls.append((req.full_url, req.method, timeout)); return Response()
    monkeypatch.setattr(actor, 'validate_public_url', lambda url: url)
    monkeypatch.setattr(actor, '_source_access_policy', lambda url, timeout:
        {'automatic_access_allowed': True, 'robots_status': 'POLICY_READ', 'robots_sha256': 'b'*64})
    monkeypatch.setattr(actor.urllib.request, 'build_opener', lambda *args: Opener())
    def run(execution_id='TEST-1', **changes):
        kw = dict(binding_path=binding, binding_sha256=pin, actor_id='TEST-ACTOR', intent=INTENT,
                  private_root=root, execution_id=execution_id, clock=lambda: NOW)
        kw.update(changes)
        return actor.capture(**kw)
    return run, calls, root, raw, binding, pin, Response


def test_qualified_single_get_uses_existing_parser_and_remains_reference(setup):
    run, calls, root, raw, *_ = setup
    result = run()
    assert calls == [(actor.DAILY_URL, 'GET', 30)]
    assert result['raw_sha256'] == hashlib.sha256(raw).hexdigest()
    assert result['archive_crc_verified'] and result['local_raw_readback_sha_verified']
    assert result['external_store_get_verified'] is False
    assert result['horse_count'] == 1 and result['formal_source_admitted'] is False
    assert result['active_universe_verified'] is False and result['registered_oos_increment'] == 0
    assert (root/(result['raw_sha256']+'.raw')).read_bytes() == raw
    packet = json.loads(next(root.glob('*.receipt.json')).read_text())
    assert packet['observations'] and all(x['tier'] == 'PRIVATE_REFERENCE_SHADOW' for x in packet['observations'])
    assert all(x['field'] != 'csv.着順' for x in packet['observations'])
    assert all(x['rule_id'] is None for x in packet['observations'])
    assert next(root.glob('*.raw')).stat().st_mode & 0o077 == 0


@pytest.mark.parametrize('grant,rights', [(False,True), (True,False)])
def test_no_network_without_provider_rights(setup, grant, rights):
    run, calls, root, raw, binding, *_ = setup
    path, pin = make_binding(binding.parent, grant=grant, rights=rights)
    with pytest.raises(ValueError): run(binding_path=path, binding_sha256=pin)
    assert calls == [] and not list(root.glob('*.raw'))


def test_binding_pin_and_actor_mismatch_stop_before_get(setup):
    run, calls, *_ = setup
    with pytest.raises(ValueError, match='BINDING_SHA'): run(binding_sha256='0'*64)
    with pytest.raises(ValueError, match='QUALIFICATION'): run(actor_id='OTHER')
    assert calls == []


def test_robots_hold_and_cutoff_do_not_issue_target_get(setup, monkeypatch):
    run, calls, *_ = setup
    with pytest.raises(ValueError, match='CUTOFF_EXPIRED'):
        run(intent={**INTENT, 'prediction_cutoff': NOW.isoformat()})
    monkeypatch.setattr(actor, '_source_access_policy', lambda url, timeout: {'automatic_access_allowed': False})
    with pytest.raises(ValueError, match='ROBOTS_ALLOW'): run()
    assert calls == []


def test_duplicate_execution_and_cross_execution_rate_limit(setup):
    run, calls, *_ = setup
    run()
    with pytest.raises(ValueError, match='ALREADY_CLAIMED'): run()
    with pytest.raises(ValueError, match='RATE_LIMIT'): run('TEST-2')
    assert len(calls) == 1
    run('TEST-3', clock=lambda: NOW + timedelta(seconds=120))
    assert len(calls) == 2


def test_schema_hold_retains_original_bytes_and_receipt(setup, monkeypatch):
    run, calls, root, raw, binding, pin, Response = setup
    bad = zip_fixture(bad_columns=True)
    monkeypatch.setattr(Response, 'read', lambda self, size: bad[:size])
    with pytest.raises(ValueError, match='COLUMN_COUNT'): run()
    digest = hashlib.sha256(bad).hexdigest()
    assert (root/(digest+'.raw')).read_bytes() == bad
    hold = json.loads((root/'TEST-1.hold.json').read_text())
    assert hold['raw_sha256'] == digest and hold['first_failed_stage'] == 'CSV_PARSE'
    assert hold['formal_source_admitted'] is False
    assert not list(root.glob('*.parsed.json'))


def test_redirect_rejected_and_public_ci_disabled(setup, monkeypatch):
    run, calls, *_ = setup
    with pytest.raises(ValueError, match='REDIRECT_NOT_ALLOWED'):
        actor._NoRedirect().redirect_request(None,None,302,'',{},actor.DAILY_URL)
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    with pytest.raises(ValueError, match='PUBLIC_CI_DISABLED'): run()
    assert calls == []


@pytest.mark.parametrize('boundary', ['cutoff', 'permission'])
def test_policy_wait_crossing_boundary_prevents_target_get(setup, monkeypatch, boundary):
    run, calls, root, *_ = setup
    current = [NOW]
    def policy(url, timeout):
        current[0] = (datetime(2026,11,4,tzinfo=timezone.utc) if boundary == 'permission'
                      else datetime(2026,11,3,10,tzinfo=timezone.utc))
        return {'automatic_access_allowed': True}
    monkeypatch.setattr(actor, '_source_access_policy', policy)
    with pytest.raises(ValueError, match='QUALIFICATION|CUTOFF_EXPIRED'):
        run(clock=lambda: current[0])
    assert calls == []
    hold = json.loads((root/'TEST-1.hold.json').read_text())
    assert hold['first_failed_stage'] == 'PRE_GET_QUALIFICATION'


@pytest.mark.parametrize('header', ['Retry-After', 'retry-after', 'RETRY-AFTER'])
def test_http429_backoff_persists_across_new_execution_ids(setup, monkeypatch, header):
    run, calls, root, *_ = setup
    class Denied:
        def open(self, req, timeout):
            calls.append(req.full_url)
            raise urllib.error.HTTPError(req.full_url,429,'Rate limited',{header:'600'},None)
    monkeypatch.setattr(actor.urllib.request, 'build_opener', lambda *args: Denied())
    with pytest.raises(urllib.error.HTTPError): run()
    assert json.loads((root/'TEST-1.hold.json').read_text())['http_status'] == 429
    with pytest.raises(ValueError, match='RATE_LIMIT'):
        run('TEST-2', clock=lambda: NOW + timedelta(seconds=120))
    assert len(calls) == 1
    state = json.loads((root/'NAR_CSV_LAST_TARGET.json').read_text())
    assert datetime.fromisoformat(state['next_eligible_at']) == NOW + timedelta(seconds=600)


@pytest.mark.parametrize('mode', ['oversized', 'empty', 'read_error'])
def test_http_body_failures_preserve_status_without_full_raw_sha(setup, monkeypatch, mode):
    run, calls, root, raw, binding, pin, Response = setup
    def read(self, size):
        if mode == 'read_error': raise OSError('synthetic failed stream')
        return b'x' * (actor.MAX_BYTES + 1) if mode == 'oversized' else b''
    monkeypatch.setattr(Response, 'read', read)
    with pytest.raises((ValueError, OSError)): run()
    hold = json.loads((root/'TEST-1.hold.json').read_text())
    assert hold['http_status'] == 200 and hold['raw_sha256'] is None
    assert hold['original_raw_bytes_saved'] == 0 and not list(root.glob('*.raw'))
    assert hold['received_bytes'] == (actor.MAX_BYTES + 1 if mode == 'oversized' else 0 if mode == 'empty' else None)
    assert hold['raw_truncated'] is (True if mode == 'oversized' else False if mode == 'empty' else None)
    assert hold['first_failed_stage'] == 'TARGET_BODY_READ'
