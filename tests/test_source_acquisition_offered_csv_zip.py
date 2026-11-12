"""Standalone generic ZIP-capture integration; no parser/Owner/CSV admission."""
from copy import deepcopy
import base64
import gzip
import io
import zipfile

import pytest
from runtime.local_physical import source_acquisition_offered_csv as s

RACE='https://www.keiba.go.jp/KeibaWeb/DataDownload/RaceDataDownload?type=daily'
ODDS='https://www.keiba.go.jp/KeibaWeb/DataDownload/OddsDataDownload?type=daily'


def transport(monkeypatch):
    originals={}
    for url,kind in ((RACE,'race'),(ODDS,'odds')):
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w') as z:z.writestr('20261104_'+kind+'.csv','SYNTHETIC_CAPTURE_ONLY')
        originals[url]=b.getvalue()
    calls=[]
    class Response:
        status=200
        def __init__(self,url):
            self.url=url
            kind='race' if url==RACE else 'odds'
            self.headers={'Content-Type':'application/zip','Content-Disposition':
                'attachment; filename="20261104_1793761200_'+kind+'.zip"'}
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def geturl(self):return self.url
        def read(self,size):return originals[self.url][:size]
    class Opener:
        def open(self,request,timeout):calls.append(request.full_url);return Response(request.full_url)
    monkeypatch.setattr(s,'validate_public_url',lambda value:value)
    monkeypatch.setattr(s,'_source_access_policy',lambda *args,**kwargs:{
        'automatic_access_allowed':True,'data_licence_granted':False})
    monkeypatch.setattr(s.urllib.request,'build_opener',lambda *args:Opener())
    monkeypatch.setattr(s,'utcnow',lambda:'2026-11-04T03:00:10+00:00')
    return originals,calls


def manifest():
    return {'race_id':'SYNTHETIC_GENERIC_CAPTURE_ONLY','prediction_cutoff':'2026-11-04T04:00:00+00:00',
        'sources':[{'source_id':'SYNTHETIC-'+kind,'url':url,'required':True,'official':True,
            'source_class':'OFFICIAL_NAR_CSV_ZIP_CAPTURE','authority':'NAR_OFFICIAL','extract':[]}
            for url,kind in ((RACE,'race'),(ODDS,'odds'))]}


def test_generic_binary_originals_roundtrip_without_runner_or_consumer_promotion(monkeypatch):
    originals,calls=transport(monkeypatch)
    artifact,errors=s.acquire_sources(manifest())
    assert errors==[] and sorted(calls)==sorted(originals)
    assert s.verify_source_artifact(artifact)==(True,[])
    assert artifact['normalized_evidence']=={}
    assert 'official_runner_universe' not in artifact
    assert 'production_numeric_consumers_authorized' not in artifact
    assert artifact['source_fetch_execution']['prediction_authority'] is False
    for snapshot in artifact['sources']:
        assert gzip.decompress(base64.b64decode(snapshot['raw_gzip_b64']))==originals[snapshot['requested_url']]
        assert snapshot['source_access_policy']['data_licence_granted'] is False
        assert snapshot['archive_capture_completed_at']=='2026-11-04T03:00:10+00:00'
        assert snapshot['archive_content_disposition'].startswith('attachment; filename="20261104_')


@pytest.mark.parametrize('field,value',[
    ('archive_content_disposition','attachment; filename="forged.zip"'),
    ('archive_capture_completed_at','2099-01-01T00:00:00+00:00'),
    ('raw_sha256','f'*64),
])
def test_capture_metadata_and_original_digest_are_part_of_snapshot_hash(monkeypatch,field,value):
    transport(monkeypatch);artifact,_=s.acquire_sources(manifest());changed=deepcopy(artifact)
    changed['sources'][0][field]=value
    valid,errors=s.verify_source_artifact(changed)
    assert valid is False
    assert any('SNAPSHOT_HASH_MISMATCH' in e for e in errors)


def test_required_policy_refusal_stops_before_any_offered_zip_get(monkeypatch):
    originals,calls=transport(monkeypatch)
    def denied(*args,**kwargs):raise ValueError('SOURCE_POLICY_ROBOTS_DISALLOWED')
    monkeypatch.setattr(s,'_source_access_policy',denied)
    artifact,errors=s.acquire_sources(manifest())
    assert calls==[]
    assert artifact['formal_ready'] is False
    assert len(artifact['missing_required_sources'])==2
    assert any('ROBOTS_DISALLOWED' in error for error in errors)


def test_capture_completion_is_body_completion_not_request_start(monkeypatch):
    originals,calls=transport(monkeypatch)
    ticks=iter(['2026-11-04T03:00:00+00:00','2026-11-04T03:00:05+00:00'])
    monkeypatch.setattr(s,'utcnow',lambda:next(ticks))
    snapshot,errors=s.fetch_source(manifest()['sources'][0],'2026-11-04T04:00:00+00:00')
    assert errors==[]
    assert snapshot['fetched_at']=='2026-11-04T03:00:00+00:00'
    assert snapshot['archive_capture_completed_at']=='2026-11-04T03:00:05+00:00'
