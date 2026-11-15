"""Synthetic exact-URL binary capture only, no live SOURCE/CSV admission."""
from datetime import datetime, timezone, timedelta
import base64
import gzip
import hashlib

import pytest
from runtime.local_physical import source_acquisition_offered_csv as s

DAILY = 'https://www.keiba.go.jp/KeibaWeb/DataDownload/RaceDataDownload?type=daily'


def fixture(monkeypatch, *, url=DAILY, final=None, raw=b'PK_SYNTHETIC_NOT_PARSER_INPUT'):
    calls = []
    class Response:
        status = 200
        headers = {'Content-Type': 'application/zip', 'Content-Disposition': 'attachment; filename="20261104_1793718125_race.zip"'}
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def geturl(self): return final or url
        def read(self, size): return raw[:size]
    class Opener:
        def open(self, request, timeout):
            calls.append(request.full_url);return Response()
    policy = []
    monkeypatch.setattr(s,'validate_public_url',lambda value:value)
    monkeypatch.setattr(s,'_source_access_policy',lambda value,timeout:policy.append(value) or {'automatic_access_allowed':True})
    monkeypatch.setattr(s.urllib.request,'build_opener',lambda *args:Opener())
    spec={'source_id':'SYNTHETIC_CSV_CAPTURE','url':url,'source_class':'OFFICIAL_NAR_CSV_ZIP_CAPTURE',
          'authority':'NAR_OFFICIAL','official':True,'required':True}
    cutoff=(datetime.now(timezone.utc)+timedelta(minutes=5)).isoformat()
    return spec,cutoff,calls,policy,raw


@pytest.mark.parametrize('url',sorted(s.OFFERED_NAR_CSV_ZIP_URLS))
def test_only_exact_offered_zip_capture_preserves_original(monkeypatch,url):
    spec,cutoff,calls,policy,raw=fixture(monkeypatch,url=url)
    snapshot,errors=s.fetch_source(spec,cutoff)
    assert errors==[] and calls==policy==[url]
    assert snapshot['raw_sha256']==hashlib.sha256(raw).hexdigest()
    assert gzip.decompress(base64.b64decode(snapshot['raw_gzip_b64']))==raw
    assert snapshot['extracted_evidence']=={}
    assert snapshot['archive_content_disposition']=='attachment; filename="20261104_1793718125_race.zip"'
    assert 'active_runner_universe' not in snapshot
    assert 'production_numeric_consumers_authorized' not in snapshot


@pytest.mark.parametrize('mutation',[
    lambda p:p.update(url=DAILY+'&unexpected=1'),
    lambda p:p.update(source_class='OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT'),
    lambda p:p.update(authority='OTHER'),
    lambda p:p.update(official=False),
    lambda p:p.update(extract=[{'field':'fake','type':'regex','pattern':'.*'}]),
])
def test_zip_cannot_masquerade_as_other_source_or_broaden_route(monkeypatch,mutation):
    spec,cutoff,calls,policy,raw=fixture(monkeypatch);mutation(spec)
    with pytest.raises(ValueError,match='CONTENT_TYPE_NOT_ALLOWED'):
        s.fetch_source(spec,cutoff)


def test_redirected_zip_not_accepted_by_download_exception(monkeypatch):
    spec,cutoff,calls,policy,raw=fixture(monkeypatch,final='https://www.keiba.go.jp/other.zip')
    with pytest.raises(ValueError,match='CONTENT_TYPE_NOT_ALLOWED'):
        s.fetch_source(spec,cutoff)


def test_policy_refusal_never_bypassed_by_offered_zip_exception(monkeypatch):
    spec,cutoff,calls,policy,raw=fixture(monkeypatch)
    def denied(*args,**kwargs):raise ValueError('SOURCE_POLICY_ROBOTS_DISALLOWED')
    monkeypatch.setattr(s,'_source_access_policy',denied)
    with pytest.raises(ValueError,match='ROBOTS_DISALLOWED'):
        s.fetch_source(spec,cutoff)
    assert calls==[]


def test_existing_compressed_byte_limit_stays_enforced(monkeypatch):
    spec,cutoff,calls,policy,raw=fixture(monkeypatch,raw=b'PK' + b'x'*100)
    spec['max_bytes']=20
    with pytest.raises(ValueError,match='MAX_BYTES_EXCEEDED'):
        s.fetch_source(spec,cutoff)
