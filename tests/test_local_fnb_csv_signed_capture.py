"""Synthetic cryptographic/adoption tests; generated fixture keys are NOT live."""
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timezone, timedelta
import base64
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import zipfile

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

from runtime import local_fnb_csv_signed_capture as bridge
from runtime import local_fnb_csv_source_admission as a
from runtime import local_fnb_csv_current_universe as u
from runtime.local_nar_csv_reference import SCHEMAS

NOW=datetime(2026,11,4,3,1,tzinfo=timezone.utc)
REPO=Path(__file__).resolve().parents[1]


def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
    path.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def archive(kind,rows):
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w') as z:
        for k,rs in rows.items():
            text=io.StringIO(newline='');w=csv.writer(text);w.writerow(SCHEMAS[k]);w.writerows([[r.get(f,'') for f in SCHEMAS[k]] for r in rs]);z.writestr('20261104_'+k+'.csv',text.getvalue().encode('utf-8-sig'))
    return out.getvalue()


def fixture(tmp_path):
    fake=tmp_path/'repo';private=tmp_path/'private';private.mkdir()
    codes={}
    for name in bridge.CODE_PATHS:
        target=fake/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((REPO/name).read_bytes());codes[name]=hashlib.sha256(target.read_bytes()).hexdigest()
    profile={'profile_id':a.PROFILE,'enabled':True,'status':'APPROVED_PRIVATE_NONPRODUCTION_CSV_PROFILE',
        'qualification_contract':bridge.CONTRACT,'signature_contract':bridge.SIGNATURE_CONTRACT,
        'current_snapshot_freshness_limits':{'max_fetch_age_seconds':600,'max_archive_age_seconds':600}}
    profile_path=private/'profile.json';profile_sha=dump(profile_path,profile)
    # Test fixture key only. Real installation additionally compares the pinned
    # public key to its repository's existing canonical trust and Gateway.
    key=Ed25519PrivateKey.generate();public=key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
    trust={'receipt_signer_key_id':bridge.SIGNER,'receipt_public_key_b64':base64.b64encode(public).decode(),
           'engine_sha256':'1'*64,'parameter_map_sha256':'2'*64}
    trust_path=private/'trust.json';trust_sha=dump(trust_path,trust)
    canonical_sha=dump(fake/'evidence/family_audit_20261016/runtime_health.json',trust)
    runtime={'source_acquisition_sha256':hashlib.sha256((REPO/'runtime/local_physical/source_acquisition_offered_csv.py').read_bytes()).hexdigest()}
    dump(fake/'profiles/current_execution_gateway.json',{'families':{'LOCAL':{**trust,'active_bundle_sha256':runtime}}})
    published=[]
    for name,url in [('manual.pdf','https://www.keiba.go.jp/pdf/manual/data_pdf_manual.pdf'),('terms.html','https://www.keiba.go.jp/terms.html')]:
        raw=b'SYNTHETIC_SCOPE_EVIDENCE_NOT_PROVIDER_PERMISSION';(private/name).write_bytes(raw);published.append({'path':name,'url':url,'sha256':hashlib.sha256(raw).hexdigest()})
    usage={'schema':'KM-NAR-OFFERED-CSV-PRIVATE-USE-EVIDENCE-v1','provider':'NAR_OFFICIAL',
        'owner_instruction_ref':'SYNTHETIC_NOT_REAL_PERMISSION','observed_endpoints':{'daily':u.DAILY_URL,'daily_odds':u.DAILY_ODDS_URL},
        'scope_assessment':{'third_party_redistribution':False,'formal_source_signing':False},'published_basis':published,
        'capability':{'method':'GET','target_venue':'FNB','target_race_dates':['2026-11-04'],
                      'valid_from':(NOW-timedelta(days=1)).isoformat(),'valid_until':(NOW+timedelta(days=1)).isoformat()}}
    usage_path=private/'usage.json';usage_sha=dump(usage_path,usage)
    owner={'decision':'APPROVE_EXACT_PRIVATE_CSV_ADOPTION','scope':bridge.SCOPE,'processing_scope':bridge.PROCESSING_SCOPE,
        'profile_sha256':profile_sha,'trust_sha256':trust_sha,'canonical_trust_sha256':canonical_sha,
        'code_sha256':codes,'actor_id':'SYNTHETIC-PRIVATE-ACTOR','receipt_signer_key_id':bridge.SIGNER,
        'expected_runtime_hashes':runtime,'approval_ref':'SYNTHETIC_NOT_ACTUAL_OWNER_APPROVAL',
        'provider_licence_granted':False,'race_dates':['2026-11-04'],'race_numbers':[1],
        'effective_from':(NOW-timedelta(days=1)).isoformat(),'effective_until':(NOW+timedelta(days=1)).isoformat()}
    owner_path=private/'owner.json';owner_sha=dump(owner_path,owner)
    binding=bridge.SignedCsvBinding(str(profile_path),profile_sha,str(owner_path),owner_sha,
        str(usage_path),usage_sha,str(trust_path),trust_sha,'SYNTHETIC-PRIVATE-ACTOR',runtime,codes)
    race=dict(競馬場='船橋',競走年月日='20261104',レース番号='1',発走時刻='1440',
        頭数='2',距離='1200',芝ダート区分='ダート',回り='左',条件='C3',天候='晴',馬場='良')
    horses=[dict(競馬場='船橋',競走年月日='20261104',レース番号='1',馬番=str(i),
        馬名='合成馬'+str(i),騎手名='合成騎手',負担重量='56',齢='4',性='牡',父馬名='合成父') for i in (1,2)]
    odds=[dict(競馬場='船橋',競走年月日='20261104',レース番号='1',賭式='単勝',番号1=str(i),オッズ='2.0') for i in (1,2)]
    raw_by_url={u.DAILY_URL:archive('race',{'racelist':[race],'horselist':horses}),u.DAILY_ODDS_URL:archive('odds',{'odds':odds})}
    request={'family_id':'LOCAL','venue_id':'FNB','race_date':'2026-11-04','race_no':1,
        'race_id':'KM-LOCAL-FNB-20261104-R01-SYNTHETIC-CSV',
        'scheduled_post_at':'2026-11-04T14:40:00+09:00','prediction_cutoff':'2026-11-04T14:35:00+09:00'}
    sources=[]
    for url,raw in raw_by_url.items():
        kind='race' if url==u.DAILY_URL else 'odds'
        snap={'source_id':'SYNTHETIC-'+kind,'source_class':'OFFICIAL_NAR_CSV_ZIP_CAPTURE','authority':'NAR_OFFICIAL','official':True,
            'required':True,'requested_url':url,'final_url':url,'http_status':200,'content_type':'application/zip',
            'raw_encoding':'gzip+base64','raw_gzip_b64':base64.b64encode(gzip.compress(raw)).decode(),
            'raw_sha256':hashlib.sha256(raw).hexdigest(),'byte_count':len(raw),
            'fetched_at':(NOW-timedelta(seconds=10)).isoformat(),
            'archive_capture_completed_at':(NOW-timedelta(seconds=6)).isoformat(),
            'archive_content_disposition':'attachment; filename="20261104_'+str(int((NOW-timedelta(seconds=60)).timestamp()))+'_'+kind+'.zip"',
            'source_access_policy':{'automatic_access_allowed':True,'data_licence_granted':False}}
        snap['snapshot_sha256']=a.sha(snap);sources.append(snap)
    source={'source_manifest_profile':bridge.CAPTURE_MANIFEST,'source_race_context':{k:request[k] for k in ('venue_id','race_date','race_no')},
        'prediction_cutoff':request['prediction_cutoff'],'source_freeze_at':(NOW-timedelta(seconds=4)).isoformat(),'sources':sources}
    receipt={'family':'LOCAL','phase':'SOURCE','race_id':request['race_id'],'status':'SOURCE_FROZEN','errors':[],
        'engine_sha256':trust['engine_sha256'],'parameter_map_sha256':trust['parameter_map_sha256'],
        'runtime_hashes':runtime,'artifact_sha256':a.sha(source),'timestamp':(NOW-timedelta(seconds=3)).isoformat()}
    envelope={'artifact':source,'receipt':receipt,'receipt_sha256':a.sha(receipt),'signer_key_id':bridge.SIGNER,
        'signature_alg':'Ed25519','signature':base64.b64encode(key.sign(json.dumps(receipt,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())).decode()}
    def resign():
        for snap in envelope['artifact']['sources']:snap['snapshot_sha256']=a.sha({k:v for k,v in snap.items() if k!='snapshot_sha256'})
        receipt['artifact_sha256']=a.sha(envelope['artifact']);envelope['receipt_sha256']=a.sha(receipt)
        envelope['signature']=base64.b64encode(key.sign(json.dumps(receipt,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())).decode()
    return fake,binding,request,envelope,trust,resign


def prepare(fixture):
    root,binding,request,envelope,trust,resign=fixture
    return bridge.prepare_qualified_csv(envelope,request,binding=binding,
        freeze_at=(NOW-timedelta(seconds=2)).isoformat(),clock=lambda:NOW,repo_root=root)


def test_existing_raw_signature_replay_creates_dormant_private_consumer_without_new_signature(tmp_path):
    f=fixture(tmp_path);out=prepare(f)
    assert out['existing_raw_signature_verified'] is True
    assert out['normalized_candidate_signature_issued'] is False
    assert out['source_receipt']==f[3]
    assert out['consumer_binding'].private_profile_path==f[1].profile_path
    source=out['assessment']['source_candidate']
    assert source['permission_evidence']['provider_licence_granted'] is False
    assert 'cloud_processing_authorized' not in source['permission_evidence']
    sig=out['consumer_binding'].source_receipt_verifier(receipt=out['source_receipt'],source_candidate=source)
    assert sig['signature_scope']=='EXISTING_GENERIC_ORIGINAL_CAPTURE_WITH_CSV_REPLAY_LINK'
    assert sig['normalized_candidate_signature_issued'] is False
    assert out['assessment']['formal_source_admitted'] is False


@pytest.mark.parametrize('field,value',[('current_load',99),('starts',[{'finish':1}]),('sire','偽の父')])
def test_rehashed_normalized_facts_cannot_reuse_original_raw_signature(tmp_path,field,value):
    out=prepare(fixture(tmp_path));candidate=deepcopy(out['assessment']['source_candidate'])
    candidate['parsed_runner_evidence']['1'][field]=value
    candidate['sha256']=a.sha({k:v for k,v in candidate.items() if k!='sha256'})
    with pytest.raises(a.CsvAdmissionHold,match='NORMALIZED_REPLAY_MISMATCH'):
        out['consumer_binding'].source_receipt_verifier(receipt=out['source_receipt'],source_candidate=candidate)


def test_returned_current_status_does_not_mutate_trusted_replay_closure(tmp_path):
    out=prepare(fixture(tmp_path));out['current_status']['rows'][0]['jockey']='偽騎手'
    sig=out['consumer_binding'].source_receipt_verifier(receipt=out['source_receipt'],source_candidate=out['assessment']['source_candidate'])
    assert sig['passed']


@pytest.mark.parametrize('fault',['profile','owner','scope','key','runtime','raw','cutoff','capture_completion'])
def test_missing_or_changed_adoption_signature_code_raw_and_time_hold(tmp_path,fault):
    f=list(fixture(tmp_path));root,binding,request,envelope,trust,resign=f
    if fault in ('profile','owner','scope'):
        path=Path(binding.profile_path if fault=='profile' else binding.owner_adoption_path);data=json.loads(path.read_bytes())
        if fault=='profile':data['enabled']=False
        elif fault=='owner':data['decision']='PENDING'
        else:data['scope']='PRODUCTION'
        pin=dump(path,data);f[1]=replace(binding,**({'profile_sha256':pin} if fault=='profile' else {'owner_adoption_sha256':pin}))
    elif fault=='key':
        other=Ed25519PrivateKey.generate().public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
        newtrust={**trust,'receipt_public_key_b64':base64.b64encode(other).decode()};pin=dump(Path(binding.trust_path),newtrust)
        owner=json.loads(Path(binding.owner_adoption_path).read_bytes());owner['trust_sha256']=pin;opin=dump(Path(binding.owner_adoption_path),owner)
        f[1]=replace(binding,trust_sha256=pin,owner_adoption_sha256=opin)
    elif fault=='runtime':envelope['receipt']['runtime_hashes']={'source_acquisition_sha256':'f'*64};resign()
    elif fault=='raw':envelope['artifact']['sources'][0]['raw_sha256']='f'*64;resign()
    elif fault=='cutoff':request['prediction_cutoff']=(NOW-timedelta(seconds=1)).isoformat()
    else:envelope['artifact']['sources'][0]['archive_capture_completed_at']=(NOW+timedelta(seconds=1)).isoformat();resign()
    with pytest.raises((a.CsvAdmissionHold,ValueError)):
        prepare(tuple(f))


def test_archive_generated_during_get_is_valid_before_completed_capture(tmp_path):
    f=fixture(tmp_path);root,binding,request,envelope,trust,resign=f
    for snap in envelope['artifact']['sources']:
        # Start NOW-10, archive generated NOW-9, completed NOW-6.
        kind='race' if snap['requested_url']==u.DAILY_URL else 'odds'
        snap['archive_content_disposition']='attachment; filename="20261104_'+str(int((NOW-timedelta(seconds=9)).timestamp()))+'_'+kind+'.zip"'
    resign();out=prepare(f)
    assert out['existing_raw_signature_verified'] is True


def test_delayed_consumer_rechecks_actual_freshness_without_moving_source_freeze(tmp_path):
    f=fixture(tmp_path);root,binding,request,envelope,trust,resign=f
    clock=[NOW]
    out=bridge.prepare_qualified_csv(envelope,request,binding=binding,
        freeze_at=(NOW-timedelta(seconds=2)).isoformat(),clock=lambda:clock[0],repo_root=root)
    frozen=out['assessment']['source_candidate']['source_freeze_at']
    clock[0]=NOW+timedelta(seconds=650)
    with pytest.raises(a.CsvAdmissionHold,match='CURRENT_UNIVERSE_EXPIRED'):
        out['consumer_binding'].source_receipt_verifier(receipt=out['source_receipt'],
            source_candidate=out['assessment']['source_candidate'])
    assert out['assessment']['source_candidate']['source_freeze_at']==frozen


def test_private_approved_profile_consumes_without_enabling_repo_default(tmp_path):
    out=prepare(fixture(tmp_path))
    assert json.loads((REPO/'profiles/local_fnb_nar_csv_source_candidate_v0.1_20261103.json').read_bytes())['enabled'] is False
    consumed=a.consume_with_approved_profile(out['assessment'],out['request'],binding=out['consumer_binding'],
        source_receipt=out['source_receipt'],repo_root=REPO,now=NOW)
    assert consumed['csv_private_profile_admission']['normalized_candidate_signature_issued'] is False
    assert consumed['numerical']['race']['distance_m']==1200
    assert consumed['numerical']['race']['surface']=='DIRT'
    assert consumed['request']['race']['distance_m']==1200


def test_rehashed_unprotected_parsed_reference_cannot_override_source_class(tmp_path):
    out=prepare(fixture(tmp_path));assessment=deepcopy(out['assessment'])
    assessment['parsed_reference']['race_reference_fields']['レース名']='G1'
    assessment['parsed_reference']['race_reference_fields']['条件']='サラブレッド系一般'
    assessment['sha256']=a.sha({k:v for k,v in assessment.items() if k!='sha256'})
    with pytest.raises(a.CsvAdmissionHold,match='PARSED_REFERENCE_RAW_REPLAY_MISMATCH'):
        a.consume_with_approved_profile(assessment,out['request'],binding=out['consumer_binding'],
            source_receipt=out['source_receipt'],repo_root=REPO,now=NOW)


def test_source_units_reject_conflicting_request_distance_alias(tmp_path):
    f=list(fixture(tmp_path));f[2]['race']={'distance':9999}
    with pytest.raises(a.CsvAdmissionHold,match='PHYSICAL_CONTEXT_CONFLICT'):
        prepare(tuple(f))


def test_generic_source_request_cannot_redefine_existing_private_cutoff(tmp_path):
    f=list(fixture(tmp_path));f[2]['prediction_cutoff']='2026-11-04T14:39:00+09:00'
    with pytest.raises(a.CsvAdmissionHold,match='CUTOFF_300_SECONDS'):
        prepare(tuple(f))


def test_now_argument_cannot_freeze_live_verifier_callback_clock(tmp_path,monkeypatch):
    f=fixture(tmp_path);root,binding,request,envelope,trust,resign=f
    actual=[NOW]
    class ActualDateTime(datetime):
        @classmethod
        def now(cls,tz=None):return actual[0]
    monkeypatch.setattr(bridge,'datetime',ActualDateTime)
    out=bridge.prepare_qualified_csv(envelope,request,binding=binding,
        freeze_at=(NOW-timedelta(seconds=2)).isoformat(),now=NOW,repo_root=root)
    actual[0]=NOW+timedelta(seconds=650)
    with pytest.raises(a.CsvAdmissionHold,match='CURRENT_UNIVERSE_EXPIRED'):
        out['consumer_binding'].source_receipt_verifier(receipt=out['source_receipt'],
            source_candidate=out['assessment']['source_candidate'])
