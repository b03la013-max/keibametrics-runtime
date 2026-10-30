"""Mechanical trust-boundary regressions; never Live/OOS evidence.

Test-only Ed25519 keys are generated in memory. Real signed artifacts are
read-only controls in test_post_result_family_isolation, not re-signed here.
"""
import ast
import base64
import copy
import importlib.util
import json
from pathlib import Path
import sys

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from local_result_settlement import settle_frozen_tickets,LocalSettlementError
from family_runtime_contract import require_receipt_binding,FamilyRuntimeError


@pytest.fixture
def app(monkeypatch):
    key=Ed25519PrivateKey.generate().private_bytes(
        serialization.Encoding.Raw,serialization.PrivateFormat.Raw,serialization.NoEncryption())
    for name,value in {
        'KM_LOCAL_ENGINE_SHA256':'a'*64,'KM_LOCAL_PARAMETER_MAP_SHA256':'b'*64,
        'KM_LOCAL_RECEIPT_SIGNER_KEY_ID':'TEST-ONLY-NOT-PRODUCTION',
        'KM_LOCAL_RECEIPT_PRIVATE_KEY_B64':base64.b64encode(key).decode(),
    }.items():
        monkeypatch.setenv(name,value)
    spec=importlib.util.spec_from_file_location('test_only_local_app',ROOT/'runtime/local_physical/app.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ticket():
    return {'total_investment':300,'tickets':[
        {'bet_type':'EXACTA','selection':[1,2],'stake':100},
        {'bet_type':'TRIO','selection':[3,1,2],'stake':100},
        {'bet_type':'TRIFECTA','selection':[3,2,1],'stake':100}]}


def official():
    return {'finish_order':[1,2,3,4],'payouts':{'EXACTA':500,'TRIO':300,'TRIFECTA':1000},
            'result_available_at':'2026-10-25T12:00:00+09:00','source':'TEST-NOT-OFFICIAL'}


def payload(app):
    final=app.signed_receipt('FINAL','TEST-RACE','PASS',{
        'final_ticket':ticket(),'final_prediction_package':{'ranking':[1,2,3,4]},
        'final_freeze_timestamp':'2026-10-25T11:00:00+09:00'})
    amounts=settle_frozen_tickets(ticket(),official())
    return {'family_id':'LOCAL','race_id':'TEST-RACE','final_receipt':final,
            'official_result':official(),'result_available_at':official()['result_available_at'],
            'pfs_authority':'TEST-PAPER','settlement':{
                'status':'COMPLETE','investment':300,'settled_investment':300,
                'return':800,'winning_tickets':amounts['winning_tickets']}}


def test_signature_binds_artifact_family_key_schema_and_original_is_immutable(app):
    p=payload(app); original=copy.deepcopy(p['final_receipt'])
    assert app.verify_envelope(original)
    for mutate in (
        lambda e:e['artifact']['final_ticket'].update(total_investment=900),
        lambda e:e['receipt'].update(family='BAN'),
        lambda e:e.update(signer_key_id='OTHER'),
        lambda e:e.update(signature_alg='OTHER'),
    ):
        altered=copy.deepcopy(original);mutate(altered)
        assert app.verify_envelope(altered) is False
    assert p['final_receipt']==original


@pytest.mark.parametrize('field,value,code',[
    ('phase','PRE_KRS','PHASE_MISMATCH'),('race_id','OTHER','RACE_ID_MISMATCH'),
    ('family','BAN','RECEIPT_INVALID')])
def test_result_requires_actual_local_final(app,field,value,code):
    p=payload(app)
    receipt=copy.deepcopy(p['final_receipt']['receipt']);receipt[field]=value
    p['final_receipt']=app.signed_receipt(receipt['phase'],receipt['race_id'],'PASS',p['final_receipt']['artifact'])
    if field=='family':
        # Even a valid signature from the test key cannot change family.
        p['final_receipt']['receipt']['family']=value
        rb=app.jdump(p['final_receipt']['receipt'])
        p['final_receipt']['receipt_sha256']=app.sha_obj(p['final_receipt']['receipt'])
        p['final_receipt']['signature']=base64.b64encode(app.private_key().sign(rb)).decode()
    result=app.result(p)
    assert result['receipt']['status']=='FAIL'
    assert any(code in e for e in result['receipt']['errors'])
    assert result['artifact']['automatic_next_race_learning_state'] is None


def test_official_frozen_accounting_correct_return_and_idempotent_reuse(app,monkeypatch):
    p=payload(app);before=copy.deepcopy(p)
    a=app.result(p)
    assert a['receipt']['status']=='PASS',a['receipt']['errors']
    assert a['artifact']['settlement']['return']==800
    assert a['artifact']['settlement']['pfs']==pytest.approx(266.666667)
    monkeypatch.setattr(app,'_build_result',lambda p:pytest.fail('duplicate settlement'))
    b=app.result(copy.deepcopy(p))
    assert a==b and p==before
    b['artifact']['settlement']['return']=0
    assert app.result(p)==a  # caller cannot mutate cached original


def test_fabricated_finance_fails_and_conflicting_duplicate_is_rejected(app):
    p=payload(app);p['settlement']['return']=999999
    failed=app.result(p)
    assert failed['receipt']['status']=='FAIL'
    assert 'SETTLEMENT_FINANCE_MISMATCH_OFFICIAL_FROZEN_TICKETS' in failed['receipt']['errors']
    p=payload(app);assert app.result(p)['receipt']['status']=='PASS'
    p['settlement']['return']=999999
    with pytest.raises(app.HTTPException,match='RESULT_REUSE_REQUEST_MISMATCH'):
        app.result(p)


@pytest.mark.parametrize('extra',[{'dead_heat':True},{'refund_runner_ids':[1]},
                                {'finish_groups':[[1],[2,3]]}])
def test_unsupported_tie_or_refund_is_not_zero_loss_or_learning(app,extra):
    p=payload(app);p['official_result'].update(extra)
    res=app.result(p)
    assert res['receipt']['status']=='FAIL'
    assert 'LOCAL_NONFLAT_RESULT_NOT_SETTLED' in res['receipt']['errors']
    assert res['artifact']['automatic_next_race_learning_state'] is None


def test_no_bet_is_zero_exposure_with_null_pfs(app):
    p=payload(app)
    p['final_receipt']=app.signed_receipt('FINAL','TEST-RACE','PASS',{
        'final_ticket':{'tickets':[],'total_investment':0}})
    p['settlement'].update({'investment':0,'settled_investment':0,'return':0,'winning_tickets':[]})
    res=app.result(p)
    assert res['receipt']['status']=='PASS',res['receipt']['errors']
    assert res['artifact']['settlement']['pfs'] is None


def test_missing_payout_duplicate_invalid_ticket_and_investment_total_are_refused():
    o=official();o['payouts'].pop('EXACTA')
    with pytest.raises(LocalSettlementError,match='PAYOUT_NOT_READY'):
        settle_frozen_tickets(ticket(),o)
    for change,code in (
        (lambda t:t['tickets'].append(copy.deepcopy(t['tickets'][1])),'DUPLICATE'),
        (lambda t:t['tickets'][0].update(selection=[1,1]),'SELECTION_INVALID'),
        (lambda t:t['tickets'][0].update(stake=101),'STAKE_UNIT'),
        (lambda t:t.update(total_investment=900),'TOTAL_MISMATCH'),
    ):
        t=ticket();change(t)
        with pytest.raises(LocalSettlementError,match=code):
            settle_frozen_tickets(t,official())


def test_receipt_binding_rejects_cross_family_race_phase_and_payload(app):
    e=payload(app)['final_receipt']
    kwargs={'family':'LOCAL','race_id':'TEST-RACE','phase':'FINAL','signer':app.SIGNER}
    require_receipt_binding(e,**kwargs)
    for override in ({'family':'BAN'},{'race_id':'OTHER'},{'phase':'RESULT'},{'signer':'OTHER'}):
        with pytest.raises(FamilyRuntimeError):
            require_receipt_binding(e,**{**kwargs,**override})
    e['artifact']['final_ticket']['tickets'][0]['stake']=900
    with pytest.raises(FamilyRuntimeError,match='CONTENT_DIGEST'):
        require_receipt_binding(e,**kwargs)


@pytest.mark.parametrize('path,function',[('runtime/local_result_from_signed_final.py','post'),
                                         ('runtime/non_jra_formal_runner.py','call')])
def test_actual_result_transport_has_no_blind_side_effect_retry(path,function):
    tree=ast.parse((ROOT/path).read_text())
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==function)
    attempts=[]
    def request_json(*a,**kw):
        attempts.append(kw['attempts']);return 200,{}
    scope={'request_json':request_json,'endpoint':'https://example.invalid','json':json}
    exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual caller>','exec'),scope)
    scope[function]('/result',{})
    scope[function]('/verify',{})
    assert attempts==[1,4]


@pytest.mark.parametrize('record',json.loads((ROOT/'tests/fixtures/family_post_result_isolation.json').read_text())['local_records'],ids=lambda x:x['race_id'])
def test_actual_kaw_ohi_signed_artifacts_preserve_crypto_bytes_and_accounting(record):
    import hashlib
    # Public verification key of the existing LOCAL signer, never a test key
    # or a signing secret. Signatures are verified offline without /verify.
    key=Ed25519PublicKey.from_public_bytes(base64.b64decode('jqWqOYlmhXXmpv/nR7lx3c2n/S5shDYava/WJVxn4kE='))
    envelopes={}
    for phase,name in [('FINAL','final_envelope'),('RESULT','result_envelope')]:
        metadata=record['sources'][name];path=ROOT/metadata['path'];before=path.read_bytes()
        assert hashlib.sha256(before).hexdigest()==metadata['raw_sha256']
        envelope=json.loads(before)
        require_receipt_binding(envelope,family='LOCAL',race_id=record['race_id'],
                                phase=phase,signer='KM-LOCAL-RUNTIME-ED25519-20260922')
        key.verify(base64.b64decode(envelope['signature']),json.dumps(
            envelope['receipt'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
        envelopes[phase]=envelope
        assert path.read_bytes()==before
    actual=settle_frozen_tickets(envelopes['FINAL']['artifact']['final_ticket'],
                                 envelopes['RESULT']['artifact']['official_result'])
    frozen=envelopes['RESULT']['artifact']['settlement']
    assert (actual['investment'],actual['return'])==(frozen['investment'],frozen['return'])


def test_local_and_jra_imports_do_not_select_the_other_source_module(tmp_path):
    import subprocess
    code='''
import sys
from pathlib import Path
root=Path(sys.argv[1]);sys.path[:0]=[str(root/'runtime/local_physical'),str(root/'runtime')]
import source_acquisition as local
sys.path.insert(0,str(root/'runtime/jra_source_runtime'))
import jra_same_day_results as jra
assert jra._decode.__module__=='jra_source_runtime.source_acquisition'
assert local.SOURCE_PROFILE != jra.snapshot_from_bytes.__globals__['SOURCE_PROFILE']
assert local.__file__.endswith('/local_physical/source_acquisition.py')
'''
    proc=subprocess.run([sys.executable,'-I','-c',code,str(ROOT)],capture_output=True,text=True,cwd=tmp_path,timeout=10)
    assert proc.returncode==0,proc.stderr
