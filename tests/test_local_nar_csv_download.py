"""Synthetic offered-download transport checks; no real provider payloads."""
from datetime import datetime, timedelta, timezone
import hashlib
import io
import json
from pathlib import Path
import zipfile

import pytest

from runtime import local_nar_csv_download as d

NOW = datetime(2026, 11, 4, 3, tzinfo=timezone.utc)


def fixture(tmp_path):
    root = tmp_path / 'private'
    root.mkdir(mode=0o700)
    evidence = []
    for name, url in [('manual.pdf', 'https://www.keiba.go.jp/pdf/manual/data_pdf_manual.pdf'),
                      ('terms.html', 'https://www.keiba.go.jp/terms.html')]:
        raw = ('SYNTHETIC_' + name).encode()
        (root / name).write_bytes(raw)
        evidence.append({'path': name, 'url': url, 'sha256': hashlib.sha256(raw).hexdigest()})
    record = {'schema': 'KM-NAR-OFFERED-CSV-PRIVATE-USE-EVIDENCE-v1', 'provider': 'NAR_OFFICIAL',
              'owner_instruction_ref': 'SYNTHETIC_TEST_ONLY',
              'observed_endpoints': {'daily': d.DAILY_URL, 'monthly': d.MONTHLY_URL},
              'scope_assessment': {'third_party_redistribution': False, 'formal_source_signing': False},
              'published_basis': evidence,
              'capability': {'method': 'GET', 'valid_from': '2026-11-03T00:00:00+09:00',
                             'valid_until': '2026-11-07T00:00:00+09:00'}}
    path = root / 'usage.json'
    path.write_text(json.dumps(record))
    pin = hashlib.sha256(path.read_bytes()).hexdigest()
    data = io.BytesIO()
    with zipfile.ZipFile(data, 'w') as z:
        z.writestr('synthetic.csv', b'SYNTHETIC_ONLY')
    return root, path, pin, data.getvalue()


class Response:
    status = 200
    headers = {'content-type': 'application/zip', 'set-cookie': 'NEVER_PERSIST'}
    def __init__(self, raw, url=d.DAILY_URL):
        self.raw = raw
        self.url = url
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def geturl(self): return self.url
    def read(self, size): return self.raw[:size]


class Opener:
    def __init__(self, raw, url=d.DAILY_URL, failure=None):
        self.raw, self.url, self.failure = raw, url, failure
        self.calls = []
    def open(self, request, timeout):
        self.calls.append((request.full_url, request.method, timeout, request.headers))
        if self.failure: raise self.failure
        return Response(self.raw, self.url)


def run(tmp_path, monkeypatch, **changes):
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)
    root, path, pin, raw = fixture(tmp_path)
    opener = Opener(raw)
    kw = dict(period='daily', private_root=root, usage_path=path, usage_sha256=pin,
              clock=lambda: NOW, opener=opener)
    kw.update(changes)
    return kw, opener, raw


def test_original_exact_bytes_and_cache_keep_capture_time(tmp_path, monkeypatch):
    kw, opener, raw = run(tmp_path, monkeypatch)
    first = d.download_csv(**kw)
    second = d.download_csv(**{**kw, 'clock': lambda: NOW + timedelta(seconds=119)})
    assert first['raw'] == second['raw'] == raw
    assert first['new_http_requests'] == 1 and second['new_http_requests'] == 0
    assert second['cache_reused'] is True
    assert first['receipt'] == second['receipt']
    assert len(opener.calls) == 1
    assert opener.calls[0] == (d.DAILY_URL, 'GET', 45, {})
    assert 'set-cookie' not in json.dumps(first['receipt'])
    assert not first['receipt']['formal_source_admitted']
    assert not first['receipt']['active_universe_verified']


def test_failed_request_consumes_rate_reservation_no_retry(tmp_path, monkeypatch):
    kw, opener, raw = run(tmp_path, monkeypatch)
    opener.failure = OSError('synthetic network failure')
    with pytest.raises(d.DownloadHold, match='synthetic network failure'):
        d.download_csv(**kw)
    with pytest.raises(d.DownloadHold, match='RATE_LIMIT_AFTER_FAILED_REQUEST'):
        d.download_csv(**kw)
    assert len(opener.calls) == 1


def test_corrupted_cached_bytes_rejected(tmp_path, monkeypatch):
    kw, opener, raw = run(tmp_path, monkeypatch)
    first = d.download_csv(**kw)
    (Path(kw['private_root']) / first['receipt']['raw_file']).write_bytes(b'changed')
    with pytest.raises(d.DownloadHold, match='CACHED_RAW_SHA_MISMATCH'):
        d.download_csv(**kw)
    assert len(opener.calls) == 1


def test_corrupted_receipt_and_path_are_not_trusted(tmp_path, monkeypatch):
    kw, opener, raw = run(tmp_path, monkeypatch)
    d.download_csv(**kw)
    root = Path(kw['private_root'])
    state = json.loads((root / 'offered_csv_ledger.json').read_text())
    receipt = root / state['daily']['receipt_file']
    receipt.write_bytes(receipt.read_bytes() + b' ')
    with pytest.raises(d.DownloadHold, match='CACHED_RECEIPT_SHA_MISMATCH'):
        d.download_csv(**kw)
    state['daily']['receipt_file'] = '../outside.receipt.json'
    (root / 'offered_csv_ledger.json').write_text(json.dumps(state))
    with pytest.raises(d.DownloadHold, match='RATE_LIMIT_AFTER_INCOMPLETE_REQUEST'):
        d.download_csv(**kw)
    assert len(opener.calls) == 1


def test_monthly_cadence_24h(tmp_path, monkeypatch):
    kw, opener, raw = run(tmp_path, monkeypatch, period='monthly')
    opener.url = d.MONTHLY_URL
    d.download_csv(**kw)
    cached = d.download_csv(**{**kw, 'clock': lambda: NOW + timedelta(seconds=86399)})
    assert cached['cache_reused'] and len(opener.calls) == 1
    new = d.download_csv(**{**kw, 'clock': lambda: NOW + timedelta(days=1)})
    assert not new['cache_reused'] and len(opener.calls) == 2


def test_no_fresh_claim_on_clock_regression(tmp_path, monkeypatch):
    kw, opener, raw = run(tmp_path, monkeypatch)
    d.download_csv(**kw)
    with pytest.raises(d.DownloadHold, match='CLOCK_REGRESSION'):
        d.download_csv(**{**kw, 'clock': lambda: NOW - timedelta(seconds=1)})
    assert len(opener.calls) == 1


def test_usage_evidence_mutation_blocks_before_network(tmp_path, monkeypatch):
    kw, opener, raw = run(tmp_path, monkeypatch)
    (Path(kw['usage_path']).parent / 'manual.pdf').write_bytes(b'changed')
    with pytest.raises(d.DownloadHold, match='EVIDENCE_SHA_MISMATCH'):
        d.download_csv(**kw)
    assert not opener.calls


def test_scope_expired_blocks_before_network(tmp_path, monkeypatch):
    kw, opener, raw = run(tmp_path, monkeypatch, clock=lambda: NOW + timedelta(days=3))
    with pytest.raises(d.DownloadHold, match='DATED_PRIVATE_SCOPE_REQUIRED'):
        d.download_csv(**kw)
    assert not opener.calls


def test_redirect_rejected_and_original_bad_zip_preserved(tmp_path, monkeypatch):
    kw, opener, raw = run(tmp_path, monkeypatch)
    opener.url = 'https://other.invalid/file'
    with pytest.raises(d.DownloadHold, match='EXACT_HTTP200_REQUIRED'):
        d.download_csv(**kw)
    assert len(opener.calls) == 1
    opener.url = d.DAILY_URL
    opener.raw = b'NOT_ZIP_ORIGINAL'
    with pytest.raises(d.DownloadHold, match='BadZipFile'):
        d.download_csv(**{**kw, 'clock': lambda: NOW + timedelta(seconds=120)})
    assert (Path(kw['private_root']) / (hashlib.sha256(opener.raw).hexdigest() + '.zip')).read_bytes() == opener.raw


def test_redirect_handler_never_follows():
    with pytest.raises(d.DownloadHold, match='REDIRECT_NOT_ALLOWED'):
        d._NoRedirect().redirect_request(None, None, 302, '', {}, d.MONTHLY_URL)


def test_public_ci_prohibited_before_network(tmp_path, monkeypatch):
    kw, opener, raw = run(tmp_path, monkeypatch)
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    with pytest.raises(d.DownloadHold, match='PUBLIC_CI_DISABLED'):
        d.download_csv(**kw)
    assert not opener.calls
