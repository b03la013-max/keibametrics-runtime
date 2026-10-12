"""Actual seven-venue diagnostics are not pre-start performance evidence."""
import base64,datetime as dt,hashlib,json,tarfile
from pathlib import Path
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from runtime.local_aki_columns import sha
ROOT=Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('venue,count',[('URW',22),('SON',16),('HIM',19),('KSM',11),('KCH',46),('SAG',98),('MIZ',104)])
def test_real_after_event_source_and_full_krs_final_chain(venue,count):
    e=ROOT/'evidence/local_aki_columns_20261012';m=json.loads((e/'post_event_seven_venue_manifest.json').read_text())
    a=e/'post_event_seven_venue_receipts.tar.gz';assert hashlib.sha256(a.read_bytes()).hexdigest()==m['archive_sha256']
    att=json.loads((e/'destination_verification.json').read_text());key=Ed25519PublicKey.from_public_bytes(base64.b64decode(att['health']['receipt_public_key_b64']))
    c=next(c for c in m['cases'] if c['venue_id']==venue);d=c['acceptance']['path']
    with tarfile.open(a,'r:gz') as archive:
        def load(path):
            raw=archive.extractfile(path).read();assert hashlib.sha256(raw).hexdigest()==m['files'][path];return json.loads(raw)
        source=load(c['source_path']);intent=load(c['intent_path'])
        pre=load(d+'/pre_krs_receipt.json');krs=load(d+'/krs_receipt.json');final=load(d+'/final_receipt.json')
        for obj,phase,status in [(source,'SOURCE','SOURCE_FROZEN'),(pre,'PRE_KRS','PASS'),(krs,'KRS_RUN','EXECUTED'),(final,'FINAL','PASS')]:
            raw=json.dumps(obj['receipt'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
            key.verify(base64.b64decode(obj['signature']),raw)
            assert sha(obj['artifact'])==obj['receipt']['artifact_sha256']
            assert hashlib.sha256(raw).hexdigest()==obj['receipt_sha256']
            assert obj['receipt']['phase']==phase and obj['receipt']['status']==status
            assert obj['receipt']['race_id']==intent['race_id']
        assert dt.datetime.fromisoformat(source['artifact']['source_freeze_at'])>dt.datetime.fromisoformat(intent['scheduled_post_at'])
        assert intent['performance_evaluation_eligible'] is False
        assert krs['artifact']['actual_run_count']==20000
        assert krs['artifact']['input_sha256']==pre['artifact']['input_sha256']==sha(load(d+'/krs_input.json'))
        assert final['artifact']['krs_receipt_sha256']==krs['receipt_sha256']
        assert final['artifact']['source_receipt_sha256']==source['receipt_sha256']
        fpp=final['artifact']['final_prediction_package'];assert fpp['temporal_mode']=='REPLAY'
        assert fpp['aki_selection']==load(d+'/selection.json')
        assert len(fpp['paper_tickets'])==count
        assert final['artifact']['final_ticket']['tickets']==[]
        assert m['unknown_future_oos_count']==0


def test_urw_sigkill_receipt_preserved_not_counted_as_twenty_thousand():
    e=ROOT/'evidence/local_aki_columns_20261012';m=json.loads((e/'post_event_seven_venue_manifest.json').read_text())
    with tarfile.open(e/'post_event_seven_venue_receipts.tar.gz','r:gz') as archive:
        p='evidence/local_aki_columns_20261012/external/KM-LOCAL-AKI-POST-EVENT-URW-20260923-R01/87835f734f66ce66/krs_receipt.json'
        obj=json.load(archive.extractfile(p));assert obj['receipt']['status']=='FAIL'
        assert obj['artifact']['returncode']==-9
        assert 'actual_run_count' not in obj['artifact']
    assert m['successful_actual_krs_runs']==140000
    assert m['failed_attempt_actual_run_count'].startswith('UNKNOWN')
