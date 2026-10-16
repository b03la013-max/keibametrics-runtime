import ast
import copy
from pathlib import Path
from types import SimpleNamespace
import pytest
from runtime import formal_execution_orchestrator as o


def request():
    return {'family_id':'LOCAL','race_id':'TEST','phase':'RESULT',
            'finish_order':[7,3,9],'result_available_at':'2026-09-30T12:00:00Z',
            'payouts':{'TRIFECTA':1000}}


def test_canonical_run_id_is_not_an_actions_integer():
    source=Path('runtime/local_result_from_signed_final.py').read_text()
    tree=ast.parse(source)
    node=next(n for n in tree.body if isinstance(n,ast.If)
              and 'run_id=int(run_id)' in ast.get_source_segment(source,n).replace(' ',''))
    for mode,raw,expected in [('CANONICAL_EXECUTION_STORE','123-formal','123-formal'),
                              ('EXECUTION_ID_AUTO_RESOLVE','123',123),
                              ('EXPLICIT_BACKWARD_COMPAT','123',123)]:
        ns={'resolution_mode':mode,'run_id':raw}
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual conversion>','exec'),ns)
        assert ns['run_id']==expected


def test_result_plan_never_requires_static_or_reacquires_source(monkeypatch):
    monkeypatch.setattr(o,'resolve_phase',lambda e,p: {'run_dir':Path('/unused')} if p=='FORMAL' else None)
    monkeypatch.setattr(o,'run_phase',lambda *a,**k: pytest.fail('plan executes'))
    assert o.orchestrate(request(),run_id='x',github_sha=None,plan_only=True)['phases']==['RESULT']


def test_result_dispatch_uses_existing_executor(monkeypatch,tmp_path):
    monkeypatch.setattr(o,'ROOT',tmp_path)
    monkeypatch.setattr(o,'persist_phase',lambda *a,**k: {'manifest':{'run_id':a[2]}})
    calls=[]
    def run(cmd,**kwargs):
        calls.append(cmd)
        (tmp_path/'out'/'result_receipt_envelope.json').write_text('{}')
        return SimpleNamespace(returncode=0,stdout='',stderr='')
    monkeypatch.setattr(o.subprocess,'run',run)
    r=request();r['execution_id']='E'
    out=o.run_phase(r,'RESULT',run_id='x',github_sha=None,runtime_out=tmp_path/'out',tmp_root=tmp_path/'tmp')
    assert calls[0][2]=='runtime.local_result_from_signed_final'
    assert out['run_id']=='x-result'
    assert (tmp_path/'tmp/E/result_out/result_checkpoint_basis.json').exists()


def test_result_immutable_retry(monkeypatch):
    r=request(); augmented=copy.deepcopy(r);augmented['execution_id']=o.derive_execution_id(r)
    monkeypatch.setattr(o,'resolve_phase',lambda e,p:{'run_dir':Path('/unused')})
    monkeypatch.setattr(o,'_load_checkpoint_json',lambda *a:{'request_sha256':o._sha_obj(augmented)})
    monkeypatch.setattr(o,'run_phase',lambda *a,**k:pytest.fail('retry reruns result'))
    out=o.orchestrate(r,run_id='x',github_sha=None)
    # Stored RESULT request identity alone is not complete Settlement/Learning proof.
    assert out['status']=='FORMAL_INCOMPLETE'
    assert o.completion_exit_code(out)!=0
    r['payouts']['TRIFECTA']=2000
    with pytest.raises(o.FormalOrchestrationError,match='REQUEST_MISMATCH'):
        o.orchestrate(r,run_id='x',github_sha=None)


def test_result_missing_final_cannot_recompute(monkeypatch):
    monkeypatch.setattr(o,'resolve_phase',lambda *a:None)
    with pytest.raises(o.FormalOrchestrationError,match='EXISTING_FORMAL'):
        o.orchestrate(request(),run_id='x',github_sha=None)


def test_result_override_cannot_switch_lineage(monkeypatch):
    monkeypatch.setattr(o,'resolve_phase',lambda *a:{})
    r=request();r['source_run_id']=100;r['legacy_handoff_override']=True
    with pytest.raises(ValueError,match='AMBIGUOUS_LEGACY'):
        o.orchestrate(r,run_id='x',github_sha=None)


def test_explicit_source_analysis_is_not_full_lifecycle_completion(monkeypatch):
    monkeypatch.setattr(o,'resolve_phase',lambda *a:None)
    calls=[]
    monkeypatch.setattr(o,'run_phase',lambda r,p,**k:calls.append(p) or {'phase':p,'status':'PASS'})
    r={'family_id':'LOCAL','race_id':'TEST','phase':'SOURCE','analysis_only':True,
       'scheduled_post_at':'2099-01-01T12:10:00+09:00','prediction_cutoff':'2099-01-01T12:00:00+09:00'}
    out=o.orchestrate(r,run_id='x',github_sha=None)
    assert calls==['SOURCE']
    assert out['status']=='SOURCE_PASS'
    assert o.completion_exit_code(out)!=0


def test_source_resume_compatible(monkeypatch, tmp_path):
    from tests.test_local_source_first_entry import put_source
    put_source(tmp_path, race="TEST")
    monkeypatch.setattr(o,'resolve_phase',lambda *a:{'run_dir':tmp_path})
    monkeypatch.setattr(o,'source_checkpoint_compatibility',lambda *a:{'status':'PASS'})
    monkeypatch.setattr(o,'run_phase',lambda *a,**k:pytest.fail('duplicate acquisition'))
    out=o.orchestrate({'family_id':'LOCAL','race_id':'TEST','phase':'SOURCE','analysis_only':True},run_id='x',github_sha=None)
    assert out['status']=='SOURCE_PASS'
    assert o.completion_exit_code(out)!=0


# Mechanical safety fixtures, not historical Signed RESULT or Forward OOS.
def _refund_snapshot(status='取消', *, payouts=True, notice=''):
    import base64, gzip, hashlib
    html = '<h2>2026年7月20日（月）盛岡第9競走競走成績</h2>' + notice
    html += '<table><tr><th>着順</th><th>馬番</th><th>馬名</th></tr>'
    for position, horse in [(1, 10), (2, 3), (3, 11)]:
        html += f'<tr><td>{position}</td><td>{horse}</td><td>Fixture</td></tr>'
    if status is not None:
        html += f'<tr><td>{status}</td><td>1</td><td>Fixture</td></tr>'
    html += '</table>'
    if payouts:
        html += '<table>'
        for name, selection, amount in [('馬連単','10-3',770), ('三連複','3-10-11',640), ('三連単','10-3-11',2250)]:
            html += f'<tr><td>{name}</td><td>{selection}</td><td>{amount}円</td><td>1人気</td></tr>'
        html += '</table>'
    raw = html.encode()
    return {'http_status':200, 'official':True, 'content_type':'text/html; charset=utf-8',
            'raw_gzip_b64':base64.b64encode(gzip.compress(raw)).decode(),
            'raw_sha256':hashlib.sha256(raw).hexdigest()}


def _parse_refund_fixture(snapshot, runners=(1,3,10,11)):
    return o.parse_official_result_snapshot(snapshot, {'venue_id':'MOR','race_date':'2026-07-20','race_no':9}, runners)


@pytest.mark.parametrize('status', ['取消', '除外', '出走取消', '競走除外'])
def test_result_refundable_frozen_runner_cannot_silently_become_loss(status):
    with pytest.raises(o.FormalOrchestrationError, match='OFFICIAL_RESULT_REFUND_REQUIRED'):
        _parse_refund_fixture(_refund_snapshot(status))


@pytest.mark.parametrize('status', ['取消', '除外', None, '中止', '失格'])
def test_result_preexcluded_or_nonrefundable_runner_preserves_normal_payout(status):
    runners = (3,10,11) if status in {'取消','除外'} else (1,3,10,11)
    order, payouts = _parse_refund_fixture(_refund_snapshot(status), runners)
    assert order == [10,3,11]
    assert payouts == {'EXACTA':770,'TRIO':640,'TRIFECTA':2250}


def test_result_missing_payout_and_full_cancel_remain_held():
    with pytest.raises(o.FormalOrchestrationError, match='PAYOUT_NOT_READY'):
        _parse_refund_fixture(_refund_snapshot(None, payouts=False))
    with pytest.raises(o.FormalOrchestrationError, match='CANCELLATION_HOLD'):
        _parse_refund_fixture(_refund_snapshot(None, notice='競走取り止め'))


def test_refund_hold_stops_before_settlement_learning_and_completion(monkeypatch, tmp_path):
    def acquire(*args, **kwargs):
        _parse_refund_fixture(_refund_snapshot('取消'))
        pytest.fail('refund must not construct a settlement request')
    monkeypatch.setattr(o, 'acquire_official_result_request', acquire)
    monkeypatch.setattr(o, 'orchestrate', lambda *a, **k: pytest.fail('must not settle/sign/learn'))
    out = o.resume_official_result(request(), run_id='refund-test', github_sha=None,
                                  runtime_out=tmp_path/'out', tmp_root=tmp_path/'tmp')
    assert out['status'] == 'BLOCKED'
    assert out['first_failed_code'] == 'OFFICIAL_RESULT_REFUND_REQUIRED'
    assert out['completion']['complete'] is False
    assert o.completion_exit_code(out) != 0
    assert not (tmp_path/'out').exists()


@pytest.mark.parametrize('replacement,code', [
    ('<td>取消</td><td>unknown</td>', 'REFUND_REQUIRED'),
    ('<td>取消</td>', 'REFUND_REQUIRED'),
])
def test_refund_status_with_unreadable_runner_is_not_discarded(replacement, code):
    import base64, gzip, hashlib
    snapshot = _refund_snapshot()
    raw = gzip.decompress(base64.b64decode(snapshot['raw_gzip_b64']))
    raw = raw.replace('<td>取消</td><td>1</td>'.encode(), replacement.encode())
    snapshot.update(raw_gzip_b64=base64.b64encode(gzip.compress(raw)).decode(), raw_sha256=hashlib.sha256(raw).hexdigest())
    with pytest.raises(o.FormalOrchestrationError, match=code):
        _parse_refund_fixture(snapshot)


def test_refund_guard_does_not_turn_absent_result_into_success():
    import base64, gzip, hashlib
    raw = '<h2>2026年7月20日（月）盛岡第9競走競走成績</h2>'.encode()
    snapshot = {'http_status':200, 'official':True, 'content_type':'text/html; charset=utf-8',
                'raw_gzip_b64':base64.b64encode(gzip.compress(raw)).decode(),
                'raw_sha256':hashlib.sha256(raw).hexdigest()}
    with pytest.raises(o.FormalOrchestrationError, match='FINISH_TABLE_HOLD'):
        _parse_refund_fixture(snapshot)
