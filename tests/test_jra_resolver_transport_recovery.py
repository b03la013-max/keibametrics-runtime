"""Regression for actual job 117303437627; replay failures, never replay a bet."""
import datetime as dt
import io
import json
from pathlib import Path
import sys
import urllib.error
from unittest.mock import Mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'runtime/jra_source_runtime'),str(ROOT/'runtime')]
import jra_pedigree_harvest as h
import jra_race_day_autopilot as a
from jra_single_entry_outcome import record_formal_failure

RID='KM-JRA-TKY-20261017-R08'
RUN='39000908421'
POST='2026-10-17T13:55:00+09:00'

class Page(io.BytesIO):
    headers={'content-type':'text/html; charset=utf-8'}
    def geturl(self):return h.BASE+'/JRADB/accessD.html'

@pytest.fixture
def clock(monkeypatch):
    now=[0.0]
    monkeypatch.setattr(h.time,'monotonic',lambda:now[0])
    monkeypatch.setattr(h.time,'sleep',lambda v:now.__setitem__(0,now[0]+v))
    monkeypatch.setattr(h.random,'uniform',lambda *args:0.25)
    return now


def client(errors, deadline=180):
    c=h._Client(deadline_monotonic=deadline)
    c.opener.open=Mock(side_effect=errors)
    return c


def test_actual_tls_reset_fixture_and_same_request_resume(clock):
    trace=(ROOT/'tests/fixtures/jra_resolver_tky8_20261017_traceback.log').read_text()
    assert 'self.do_handshake()' in trace
    assert 's2 = c.post("/JRADB/accessD.html", tok)' in trace
    assert 'ConnectionResetError: [Errno 104]' in trace
    c=client([urllib.error.URLError(ConnectionResetError(104,'Connection reset by peer')),Page(b'official')])
    assert c.post('/JRADB/accessD.html','observed-token')=='official'
    assert c.opener.open.call_count==2
    calls=c.opener.open.call_args_list
    assert calls[0].args[0] is calls[1].args[0]
    assert calls[0].args[0].data==b'cname=observed-token'
    assert clock[0]==4.25

@pytest.mark.parametrize('code',[429,500,502,503,504])
def test_transient_http_recovery(clock,code):
    err=urllib.error.HTTPError(h.BASE,code,'temporary',{'Retry-After':'7'},None)
    c=client([err,Page(b'ok')])
    assert c.get('/official')=='ok'
    assert clock[0]==8

@pytest.mark.parametrize('error',[TimeoutError('connect'),urllib.error.URLError(TimeoutError('TLS')),
                                 ConnectionAbortedError('closed')])
def test_connection_timeout_classification(clock,error):
    c=client([error,Page(b'ok')]);assert c.get('/official')=='ok'


def test_read_timeout_retries_entire_response(clock):
    page=Page(b'bad');page.read1=Mock(side_effect=TimeoutError('read'))
    c=client([page,Page(b'good')]);assert c.get('/official')=='good'
    assert page.closed


def test_incomplete_body_retries(clock):
    page=Page(b'partial');page.length=42
    c=client([page,Page(b'whole')]);assert c.get('/official')=='whole'

@pytest.mark.parametrize('code',[400,401,403,404,410])
def test_permanent_http_no_retry(clock,code):
    c=client([urllib.error.HTTPError(h.BASE,code,'permanent',{},None)])
    with pytest.raises(urllib.error.HTTPError):c.get('/official')
    assert c.opener.open.call_count==1


def test_deadline_stops_retry_before_second_request(clock):
    c=client([urllib.error.URLError(ConnectionResetError(104,'reset'))],deadline=3)
    with pytest.raises(h.OfficialDeadlineExceeded):c.get('/official')
    assert c.opener.open.call_count==1
    assert clock[0]==1


def test_open_and_each_read_share_global_deadline(clock):
    p=Page(b'payload')
    def slow(n):clock[0]+=2;return b'data'
    p.read1=slow
    c=client([p],deadline=2)
    with pytest.raises(h.OfficialDeadlineExceeded):c.get('/official')
    assert c.opener.open.call_args.kwargs['timeout']==1
    assert p.closed


def test_maximum_three_attempts(clock):
    c=client([ConnectionResetError(104,'reset')]*3)
    with pytest.raises(ConnectionResetError):c.get('/official')
    assert c.opener.open.call_count==3


def test_official_authority_not_relaxed(clock):
    c=client([Page(b'ok')])
    with pytest.raises(ValueError,match='JRA_OFFICIAL_ONLY'):c._open('https://example.com/fake')
    assert c.opener.open.call_count==0


def run(status='completed',conclusion='failure',number=RUN):
    return {'databaseId':int(number),'displayTitle':'JRA intent 東京 2026-10-17 R8',
            'status':status,'conclusion':conclusion,'attempt':1,
            'createdAt':'2026-10-17T04:00:12Z'}


def make_failure(root):
    failure={'run_id':RUN,'workflow_run_id':RUN,'run_attempt':1,
             'first_failed_stage':'RESOLVE_OFFICIAL_RACE_AND_BUILD_INTENT',
             'failure_owner':'JRA_OFFICIAL_RACE_RESOLVER','exception_class':'URLError',
             'retryable':True,'retry_deadline':'2026-10-17T13:40:00+09:00',
             'last_attempt_at':'2026-10-17T13:01:40+09:00',
             'status_updated_at':'2026-10-17T13:01:40+09:00',
             'terminal_state':'RESOLVER_FAILED','conclusion':'failure','error':'reset'}
    return record_formal_failure(root,{'family_id':'JRA','race_id':RID,'execution_id':RID+'-LIVE-R1'},failure)


def test_failure_checkpoint_without_intent_and_expiry(tmp_path):
    make_failure(tmp_path)
    for hh,mm,expected in [(13,2,'RESOLVER_FAILED'),(13,40,'RESOLVER_DEADLINE_EXCEEDED')]:
        row=a.race_status(tmp_path,RID,{'post':POST},{RID:{'dispatched_at':POST}},dt.datetime(2026,10,17,hh,mm,tzinfo=a.JST))
        assert row['state']==expected
        for k in ('race_id','workflow_run_id','execution_id','first_failed_stage','failure_owner',
                  'exception_class','retryable','retry_deadline','temporal_eligibility','last_attempt_at',
                  'terminal_state','status_updated_at'):
            assert k in row,k


def test_status_writer_loss_recovered_from_workflow_observation(tmp_path):
    # No failure checkpoint at all: only the real Workflow outcome is known.
    row={'race_id':RID,'state':'DISPATCHED_RUNNING','post':POST}
    a.reconcile_resolver_run_status(tmp_path,row,[run()],dt.datetime(2026,10,17,14,tzinfo=a.JST))
    assert row['state']=='RESOLVER_DEADLINE_EXCEEDED'
    assert row['workflow_run_id']==RUN
    assert row['exception_class'] is None and row['retryable'] is False


def test_no_cross_race_match_or_source_success_reclassification(tmp_path):
    row={'race_id':RID.replace('R08','R03'),'state':'DISPATCHED_RUNNING','post':POST}
    a.reconcile_resolver_run_status(tmp_path,row,[run()],dt.datetime(2026,10,17,13,tzinfo=a.JST))
    assert 'workflow_run_id' not in row
    folder=tmp_path/'runtime/jra_formal_intents';folder.mkdir(parents=True)
    (folder/(RID+'-LIVE-R1.json')).write_text('{}')
    row={'race_id':RID,'state':'DISPATCHED_RUNNING','post':POST}
    a.reconcile_resolver_run_status(tmp_path,row,[run()],dt.datetime(2026,10,17,13,tzinfo=a.JST))
    assert row['state']=='DISPATCHED_RUNNING'


def test_safe_recovery_beyond_dispatch_window_and_other_race_continuation(tmp_path):
    make_failure(tmp_path)
    folder=tmp_path/'runtime/jra_race_day_plan';folder.mkdir(parents=True)
    (folder/'2026-10-17.json').write_text(json.dumps({'entries':[{'venue':'東京','races':[8,9]}]}))
    (folder/'2026-10-17.state.json').write_text(json.dumps({RID:{'dispatched_at':'2026-10-17T13:00:01+09:00'}}))
    races=[{'race_no':8,'post_time':'13:55'},{'race_no':9,'post_time':'14:10'}]
    sent=[];retried=[]
    kw=dict(resolve=lambda *args:('0520260404',races),resolver_runs=[run()],publish=lambda:None,
            dispatch=lambda *args:sent.append(args),retry_resolver=lambda *args:retried.append(args))
    now=dt.datetime(2026,10,17,13,20,tzinfo=a.JST)
    a.tick(tmp_path,'2026-10-17',now,**kw)
    a.tick(tmp_path,'2026-10-17',now,**kw)
    assert len(retried)==1 and len(sent)==1
    assert sent[0][1]==9


def test_expired_failure_never_retries(tmp_path):
    make_failure(tmp_path)
    folder=tmp_path/'runtime/jra_race_day_plan';folder.mkdir(parents=True)
    (folder/'2026-10-17.json').write_text(json.dumps({'entries':[{'venue':'東京','races':[8]}]}))
    (folder/'2026-10-17.state.json').write_text(json.dumps({RID:{'dispatched_at':POST}}))
    retry=Mock()
    a.tick(tmp_path,'2026-10-17',dt.datetime(2026,10,17,13,40,tzinfo=a.JST),
        resolve=lambda *args:('0520260404',[{'race_no':8,'post_time':'13:55'}]),
        resolver_runs=[run()],retry_resolver=retry,publish=lambda:None,dispatch=Mock())
    retry.assert_not_called()


def test_successful_retry_intent_supersedes_old_resolver_failure(tmp_path):
    make_failure(tmp_path)
    folder=tmp_path/'runtime/jra_formal_intents';folder.mkdir(parents=True)
    (folder/(RID+'-LIVE-R1.json')).write_text(json.dumps({'race_id':RID}))
    row=a.race_status(tmp_path,RID,{'post':POST},{RID:{}},dt.datetime(2026,10,17,13,20,tzinfo=a.JST))
    assert row['state']=='DISPATCHED_RUNNING'


def test_corrupt_other_failure_does_not_abort_day(tmp_path):
    p=make_failure(tmp_path)
    value=json.loads(p.read_text());value['formal_execution_failure']['workflow_run_id']='invalid'
    p.write_text(json.dumps(value))
    assert a.resolver_failure(tmp_path,RID) is None


def test_actual_signed_source_checkpoint_reuse_preserves_bytes(tmp_path):
    from execution_store import materialize_phase
    from verify_source_envelope import verify
    eid='KM-JRA-TKY-20261017-R04-LIVE-R1'
    original=ROOT/'runtime/executions'/eid/'SOURCE'
    before={p.relative_to(original).as_posix():p.read_bytes() for p in original.rglob('*.json')}
    assert materialize_phase(eid,'SOURCE',tmp_path) is not None
    proof=verify(tmp_path/'source_receipt_envelope.json')
    assert proof['valid'] and proof['race_id']=='KM-JRA-TKY-20261017-R04'
    assert proof['receipt_sha256']=='922a7baa9815b38ec7636967e35307d19a1dd1bee95525da45cbdf04d8a706a8'
    assert before=={p.relative_to(original).as_posix():p.read_bytes() for p in original.rglob('*.json')}
    # Offline Ed25519/hash validation is not fresh GitHub OIDC attestation.


def test_deadline_expiring_during_claim_publish_prevents_send(tmp_path,clock):
    make_failure(tmp_path)
    folder=tmp_path/'runtime/jra_race_day_plan';folder.mkdir(parents=True)
    (folder/'2026-10-17.json').write_text(json.dumps({'entries':[{'venue':'東京','races':[8]}]}))
    (folder/'2026-10-17.state.json').write_text(json.dumps({RID:{'dispatched_at':POST}}))
    retry=Mock()
    def slow_publish():clock[0]+=61
    a.tick(tmp_path,'2026-10-17',dt.datetime(2026,10,17,13,39,tzinfo=a.JST),
        resolve=lambda *args:('0520260404',[{'race_no':8,'post_time':'13:55'}]),
        resolver_runs=[run()],retry_resolver=retry,publish=slow_publish,dispatch=Mock())
    retry.assert_not_called()


def test_failed_claim_publication_does_not_send(tmp_path):
    make_failure(tmp_path)
    folder=tmp_path/'runtime/jra_race_day_plan';folder.mkdir(parents=True)
    (folder/'2026-10-17.json').write_text(json.dumps({'entries':[{'venue':'東京','races':[8]}]}))
    (folder/'2026-10-17.state.json').write_text(json.dumps({RID:{'dispatched_at':POST}}))
    retry=Mock()
    a.tick(tmp_path,'2026-10-17',dt.datetime(2026,10,17,13,20,tzinfo=a.JST),
        resolve=lambda *args:('0520260404',[{'race_no':8,'post_time':'13:55'}]),
        resolver_runs=[run()],retry_resolver=retry,publish=Mock(side_effect=OSError('push failed')),dispatch=Mock())
    retry.assert_not_called()
