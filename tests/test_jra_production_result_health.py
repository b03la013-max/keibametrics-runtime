"""Offline Production acceptance: legacy exclusion and race-isolated failures."""
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'runtime/jra_source_runtime'),str(ROOT/'tests')]
import jra_production_postresult as p
from jra_candidate_postresult_closedloop import PendingOfficialResult
from test_jra_production_postresult import final,OFFICIAL,EVIDENCE


def save(root,rid,obj):
    path=root/'runtime/final_artifacts'/(rid+'.json')
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj));return path


def test_t11_real_hsn_legacy_is_explicit_and_never_fetches_or_invents_a_clock(monkeypatch,tmp_path):
    rid='KM-JRA-HSN-20260921-R12'
    raw=(ROOT/'runtime/final_artifacts'/(rid+'.json')).read_bytes();obj=json.loads(raw)
    assert obj.get('scheduled_post_at') is None and obj.get('temporal_mode') is None
    path=save(tmp_path,rid,obj);before=path.read_bytes()
    def no_call(*args,**kwargs):pytest.fail('LEGACY_MUST_NOT_REACH_FORMAL_RESULT_OR_NETWORK')
    monkeypatch.setattr(p,'process',no_call)
    health=tmp_path/'health.json'
    assert p.main(['--repo-root',str(tmp_path),'--race-id',rid,'--health-out',str(health)])==0
    report=json.loads(health.read_text());row=report['processed'][0]
    assert row['status']=='NOT_ELIGIBLE_LEGACY_FINAL'
    assert {'temporal_mode','scheduled_post_at','final_receipt'}<=set(row['missing_fields'])
    assert row['prediction_cutoff_used_as_post'] is row['race_id_date_used_as_post'] is False
    assert row['recommendation_pfs'] is None and not row['persisted']
    assert path.read_bytes()==before and (ROOT/'runtime/final_artifacts'/(rid+'.json')).read_bytes()==raw
    assert not (tmp_path/'runtime/results').exists()


@pytest.mark.parametrize('missing',['scheduled_post_at','prediction_cutoff'])
def test_a_declared_modern_formal_cannot_hide_missing_required_time_as_legacy(missing):
    obj=final();obj.pop(missing);obj['sha256']=p._sha({k:v for k,v in obj.items() if k!='sha256'})
    assert p.legacy_final_classification(obj) is None
    with pytest.raises(p.ProductionPostResultError,match='TEMPORAL_FIELDS_MISSING'):
        p.verify_final(obj)


@pytest.mark.parametrize('mutation',['missing_mode','altered_mode','missing_mode_resealed','stripped_seals'])
def test_current_broken_schema_never_hides_as_legacy_success(tmp_path,monkeypatch,mutation):
    rid='KM-JRA-TKY-20261028-R01';obj=final()
    if mutation=='altered_mode':obj['temporal_mode']='POST-RACE'
    else:obj.pop('temporal_mode')
    if mutation=='missing_mode_resealed':obj['sha256']=p._sha({k:v for k,v in obj.items() if k!='sha256'})
    elif mutation=='stripped_seals':
        obj.pop('sha256');obj.pop('final_receipt')
    path=save(tmp_path,rid,obj);before=path.read_bytes();health=tmp_path/'health.json'
    monkeypatch.setattr('jra_candidate_postresult_closedloop.fetch_jra_result',lambda *a:pytest.fail('BROKEN_SCHEMA_FETCH'))
    assert p.main(['--repo-root',str(tmp_path),'--race-id',rid,'--health-out',str(health)])==2
    row=json.loads(health.read_text())['processed'][0]
    assert row['status']=='BLOCKED_RESULT_INTEGRITY'
    assert row['recommendation_pfs'] is None and not row['persisted']
    assert path.read_bytes()==before and not (tmp_path/'runtime/results').exists()


def test_t10_one_blocked_race_does_not_prevent_normal_result_request_and_health_failure(tmp_path,monkeypatch):
    good='KM-JRA-TKY-20261028-R02';bad='KM-JRA-NGT-20261028-R01'
    for rid in [bad,good]:save(tmp_path,rid,final())
    calls=[]
    def run(root,rid,*,now):
        calls.append(rid)
        if rid==bad:
            exc=ValueError('OFFICIAL_RESULT_RUNNER_UNIVERSE_MISMATCH')
            exc.first_failed_stage='VERIFY_OFFICIAL_RESULT'
            raise exc
        path=root/'runtime/results'/(rid+'.json');path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text('{"classification":"UNIT_TEST_RESULT_REQUEST_NOT_SIGNED"}')
        return 'RESULT_REQUEST_WRITTEN'
    monkeypatch.setattr(p,'process',run)
    health=tmp_path/'health.json'
    assert p.main(['--repo-root',str(tmp_path),'--days','100000','--health-out',str(health)])==2
    report=json.loads(health.read_text())
    assert set(calls)=={bad,good} and report['execution_health']=='PARTIAL_BLOCKED'
    assert report['counts']['BLOCKED_RESULT_INTEGRITY']==1
    assert report['counts']['RESULT_REQUEST_WRITTEN']==1
    badrow=next(row for row in report['processed'] if row['race_id']==bad)
    assert badrow['first_failed_stage']=='VERIFY_OFFICIAL_RESULT'
    assert badrow['recommendation_pfs'] is None and not badrow['persisted']
    assert report['signed_result_receipt_verified_by_health'] is False
    assert (tmp_path/'runtime/results'/(good+'.json')).exists()


def test_t8_unpublished_is_pending_and_not_a_verified_success(tmp_path,monkeypatch):
    rid='KM-JRA-TKY-20261028-R02';save(tmp_path,rid,final())
    def run(*args,**kwargs):raise PendingOfficialResult('JRA_RESULT_NOT_PUBLISHED')
    monkeypatch.setattr(p,'process',run)
    health=tmp_path/'health.json'
    assert p.main(['--repo-root',str(tmp_path),'--race-id',rid,'--health-out',str(health)])==0
    report=json.loads(health.read_text())
    assert report['execution_health']=='PENDING_OFFICIAL_RESULT'
    assert report['processed'][0]['recommendation_pfs'] is None
    assert not (tmp_path/'runtime/results').exists()


def test_failure_retains_exact_raw_separately_from_health(tmp_path, monkeypatch):
    import base64
    import hashlib

    rid = 'KM-JRA-TKY-20261028-R02'
    save(tmp_path, rid, final())
    response = b'<html>failed result observation</html>'
    error = PendingOfficialResult('JRA_OFFICIAL_RESULT_RACE_NOT_PUBLISHED')
    error.first_failed_stage = 'RESULT_RACE_SELECTION'
    error.result_failure_capture = {
        'capture_stage': 'RESULT_DAY',
        'url': 'https://www.jra.go.jp/JRADB/accessS.html',
        'captured_at': '2026-10-28T07:00:00Z',
        'sha256': hashlib.sha256(response).hexdigest(),
        'raw_base64': base64.b64encode(response).decode('ascii'),
    }

    def run(*args, **kwargs):
        raise error

    monkeypatch.setattr(p, 'process', run)
    health = tmp_path / 'health.json'
    raw_dir = tmp_path / 'raw-failures'
    assert p.main(['--repo-root', str(tmp_path), '--race-id', rid, '--health-out',
                   str(health), '--failure-raw-dir', str(raw_dir)]) == 0
    row = json.loads(health.read_text())['processed'][0]
    assert row['first_failed_stage'] == 'RESULT_RACE_SELECTION'
    assert row['status'] == 'PENDING_OFFICIAL_RESULT'
    assert 'raw_base64' not in health.read_text()
    capture = json.loads((raw_dir / row['failure_raw_artifact']).read_text())
    assert capture['capture_stage'] == 'RESULT_DAY'
    assert capture['target_race_id'] == rid
    assert base64.b64decode(capture['raw_base64']) == response
    assert capture['scope'] == 'DIAGNOSTIC_ONLY_NOT_RESULT_ADMISSION'
    assert not (tmp_path / 'runtime/results').exists()


def test_existing_incomplete_request_is_retried_without_rewriting_it(tmp_path):
    from jra_result_submission import ResultSubmission
    requests = tmp_path / 'runtime/results'
    requests.mkdir(parents=True)
    frozen=final()
    race=frozen['race_id']
    execution_id=race+'-LIVE-R1'
    frozen['execution_stage_manifest']={'SIGNED_SOURCE_RECEIPT_VERIFIED':{'execution_id':execution_id}}
    frozen['sha256']=p._sha({k:v for k,v in frozen.items() if k!='sha256'})
    save(tmp_path,race,frozen)
    request=p.build_result_request(frozen,OFFICIAL,EVIDENCE)
    path=requests/(race+'.json')
    raw=json.dumps(request).encode()
    path.write_bytes(raw)
    rows=[{'race_id':race,'status':'PENDING_RESULT_RUNNER'}]
    assert p.process(tmp_path,race,enroll_signer=True)=='BLOCKED_RESULT_LEGACY_UNRESOLVED'
    assert p.pending_result_dispatches(tmp_path,rows)==[]
    journal=ResultSubmission(tmp_path,execution_id,request)
    journal.enroll()
    assert p.pending_result_dispatches(tmp_path,rows)==[path.relative_to(tmp_path).as_posix()]
    assert p.process(tmp_path,race,enroll_signer=True)=='PENDING_RESULT_RUNNER'
    journal.claim('100-1',lambda path:None)
    assert p.process(tmp_path,race,enroll_signer=True)=='BLOCKED_RESULT_SIGNER_OUTCOME_UNKNOWN'
    assert p.pending_result_dispatches(tmp_path, rows) == []
    assert path.read_bytes()==raw


def test_enrolled_request_is_scanned_after_discovery_window_without_refetch(tmp_path,monkeypatch):
    from jra_result_submission import ResultSubmission
    frozen=final()
    race=frozen['race_id'];execution_id=race+'-LIVE-R1'
    frozen['execution_stage_manifest']={'SIGNED_SOURCE_RECEIPT_VERIFIED':{'execution_id':execution_id}}
    frozen['sha256']=p._sha({k:v for k,v in frozen.items() if k!='sha256'})
    save(tmp_path,race,frozen)
    request=p.build_result_request(frozen,OFFICIAL,EVIDENCE)
    path=tmp_path/'runtime/results'/(race+'.json');path.parent.mkdir(parents=True)
    path.write_text(json.dumps(request))
    journal=ResultSubmission(tmp_path,execution_id,request);journal.enroll()
    monkeypatch.setattr('jra_candidate_postresult_closedloop.fetch_jra_result',lambda *a:pytest.fail('MUST_NOT_REFETCH'))
    health=tmp_path/'health.json'
    assert p.main(['--repo-root',str(tmp_path),'--days','0','--enroll-signer','--health-out',str(health)])==0
    assert json.loads(health.read_text())['execution_health']=='PENDING_RESULT_RUNNER'
    assert list(p.new_result_commit_paths(tmp_path,[{'race_id':race,'status':'RESULT_REQUEST_WRITTEN'}]))==[
        path.relative_to(tmp_path).as_posix(),(journal.path/'ENROLLED.json').relative_to(tmp_path).as_posix()]


def test_old_signed_phase_can_finish_review_without_new_signer_enrollment(tmp_path,monkeypatch):
    from execution_store import persist_phase
    frozen=final();race=frozen['race_id'];execution_id=race+'-LIVE-R1'
    frozen['execution_stage_manifest']={'SIGNED_SOURCE_RECEIPT_VERIFIED':{'execution_id':execution_id}}
    frozen['sha256']=p._sha({k:v for k,v in frozen.items() if k!='sha256'})
    save(tmp_path,race,frozen)
    request=p.build_result_request(frozen,OFFICIAL,EVIDENCE)
    path=tmp_path/'runtime/results'/(race+'.json');path.parent.mkdir(parents=True)
    path.write_text(json.dumps(request))
    receipt={'phase':'RESULT','status':'PASS','race_id':race,'artifact_sha256':p._sha(request),
             'timestamp':'2026-10-11T07:30:00Z'}
    envelope={'receipt':receipt,'receipt_sha256':p._sha(receipt),'signature':'offline-test',
              'signer_key_id':'offline-test','signature_alg':'Ed25519'}
    staging=tmp_path/'checkpoint';staging.mkdir()
    (staging/'result_request.json').write_text(json.dumps(request))
    (staging/'result_receipt_envelope.json').write_text(json.dumps(envelope))
    persist_phase(execution_id,'RESULT','old-result',staging,root=tmp_path/'runtime/executions')
    monkeypatch.setattr('jra_candidate_postresult_closedloop.fetch_jra_result',lambda *a:pytest.fail('MUST_NOT_REFETCH'))
    health=tmp_path/'health.json'
    assert p.main(['--repo-root',str(tmp_path),'--days','0','--enroll-signer','--health-out',str(health)])==0
    rows=json.loads(health.read_text())['processed']
    assert p.pending_result_dispatches(tmp_path,rows)==[path.relative_to(tmp_path).as_posix()]


def test_production_missing_named_final_is_no_final_not_internal_success(tmp_path):
    out=tmp_path/'health.json'
    assert p.main(['--repo-root',str(tmp_path),'--race-id','KM-JRA-TKY-20261028-R01','--health-out',str(out)])==0
    report=json.loads(out.read_text())
    assert report['processed'][0]['status']=='NO_PRODUCTION_FINAL'
    assert report['execution_health']=='SUCCESS_NO_DUE_RACES'


@pytest.mark.parametrize('decision',['EXECUTE_RECOMMENDATION_PORTFOLIO','EXECUTE_FULL_MEC'])
def test_recommendation_paper_and_zero_exposure_denominators_are_separate(decision):
    recommendation=p.settle_final(final(decision=decision),OFFICIAL)
    assert recommendation['recommendation_pfs']==recommendation['pfs']
    assert recommendation['actual_purchase']=='UNVERIFIED' and recommendation['actual_purchase_pfs'] is None
    paper=p.settle_final(final(decision='PAPER'),OFFICIAL)
    assert paper['capital_exposure_class']=='PAPER_REFERENCE' and paper['recommendation_pfs'] is None
    assert paper['pfs'] is not None  # explicit hypothetical reference only
    paper_final=final(decision='PAPER');paper_final['final_ticket']['no_bet']=True
    assert p.settle_final(paper_final,OFFICIAL)['capital_exposure_class']=='PAPER_REFERENCE'
    zero=final();zero['final_ticket'].update(tickets=[],total_investment=0,no_bet=True)
    no_bet=p.settle_final(zero,OFFICIAL)
    assert no_bet['capital_exposure_class']=='NO_BET'
    assert no_bet['recommendation_pfs'] is no_bet['pfs'] is None


def test_t15_existing_result_request_is_not_reissued_or_overwritten(tmp_path,monkeypatch):
    rid='KM-JRA-TKY-20261028-R01';out=tmp_path/'runtime/results'/(rid+'.json')
    out.parent.mkdir(parents=True);raw=b'{"existing_signed_result":"opaque immutable bytes"}\n';out.write_bytes(raw)
    monkeypatch.setattr('jra_candidate_postresult_closedloop.fetch_jra_result',lambda *a:pytest.fail('ALREADY_RESULTED_FETCH'))
    assert p.process(tmp_path,rid)=='ALREADY_RESULTED'
    assert p.process(tmp_path,rid)=='ALREADY_RESULTED' and out.read_bytes()==raw
    assert not (tmp_path/'runtime/learning_states').exists()


@pytest.mark.parametrize('changed',[
    {'race_date':'2026-10-24'}, {'race_no':2}, {'venue_id':'KYO'},
    {'jra_source':{'jra_meeting_key':'0820260404'}},
    {'jra_source':{'jra_meeting_key':'0420250404'}},
])
def test_unsigned_routing_intent_cannot_cross_bind_another_date_venue_or_race(tmp_path,changed):
    rid='KM-JRA-NGT-20261025-R11'
    intent={'race_id':rid,'race_date':'2026-10-25','race_no':11,'venue_id':'NGT',
            'jra_source':{'jra_meeting_key':'0420260404'}}
    intent.update(changed)
    path=tmp_path/'runtime/jra_formal_intents'/(rid+'-LIVE-R1.json')
    path.parent.mkdir(parents=True);path.write_text(json.dumps(intent));before=path.read_bytes()
    with pytest.raises(p.ProductionPostResultError,match='INTENT_IDENTITY_MISMATCH'):
        p._intent_for(tmp_path,rid)
    assert path.read_bytes()==before and not (tmp_path/'runtime/results').exists()
