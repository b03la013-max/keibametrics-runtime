"""Verified existing execution checkpoints are reused before any /result call."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import sys
import textwrap

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tests')]
import jra_production_postresult as production
from execution_store import persist_phase,resolve_phase

RID='KM-JRA-KYO-20261025-R07'


def fixture(tmp_path):
    raw=(ROOT/'runtime/final_artifacts'/(RID+'.json')).read_bytes();final=json.loads(raw)
    for relative in ['runtime/final_artifacts/'+RID+'.json',
                     'profiles/KM_FAMILY_CURRENT_AUTHORITY_20261012_R51.json',
                     'profiles/family_runtime_contracts_20261008_R28.json',
                     'evidence/jra_bvi_phase3_20261017/runtime_health.json']:
        target=tmp_path/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/relative,target)
    request={'race_id':RID,'result_lane':'PRODUCTION','official_result':{'fixture':'OFFLINE_NOT_LIVE'},
             'settlement':{'status':'SETTLED','total_investment':100,'total_payout':0},
             'frozen_prediction_ref':{'immutable_final_sha256':final['sha256'],
                                      'final_receipt_sha256':final['final_receipt_sha256']}}
    receipt={'race_id':RID,'phase':'RESULT','status':'PASS','errors':[],
             'artifact_sha256':production._sha(request),'timestamp':'2026-10-25T05:00:00Z'}
    envelope={'receipt':receipt,'receipt_sha256':production._sha(receipt),
              'signature_alg':'Ed25519','signature':'UNIT_TEST_NOT_REAL_SIGNATURE',
              'signer_key_id':'UNIT_TEST_NOT_REAL_SIGNER'}
    execution_id=final['execution_stage_manifest']['SIGNED_SOURCE_RECEIPT_VERIFIED']['execution_id']
    return request,envelope,execution_id


def stored(root,request,envelope,eid):
    source=root/'temporary-checkpoint';source.mkdir()
    for name,value in [('result_request.json',request),('result_receipt_envelope.json',envelope)]:
        (source/name).write_text(json.dumps(value))
    persist_phase(eid,'RESULT','earlier-result',source,root=root/'runtime/executions',github_sha='a'*40)
    phase=resolve_phase(eid,'RESULT',root=root/'runtime/executions')
    return {p:p.read_bytes() for p in phase['run_dir'].iterdir() if p.is_file()}


def execute(root,request,call,attempt='second-run'):
    return production.reuse_or_submit_production_result(root,request,call=call,
        checkpoint=root/'runtime_out/result_checkpoint',run_id=attempt,github_sha='b'*40)


def test_existing_verified_checkpoint_reuse_makes_zero_signing_calls_and_preserves_bytes(tmp_path):
    request,envelope,eid=fixture(tmp_path);before=stored(tmp_path,request,envelope,eid);calls=[]
    def call(path,payload):
        calls.append(path);assert path=='/verify';assert payload==envelope
        return 200,{'valid':True}
    result,diagnostic=execute(tmp_path,request,call)
    assert calls==['/verify'] and result==envelope
    assert diagnostic['status']=='VERIFIED_REUSE' and diagnostic['result_resigning'] is False
    assert {p:p.read_bytes() for p in before}==before
    assert len(list((tmp_path/'runtime/executions'/eid/'RESULT/runs').iterdir()))==1


@pytest.mark.parametrize('mutation',['request','race','phase','artifact','receipt_digest','signature','pre_post_time'])
def test_saved_mismatch_or_failed_signature_never_falls_back_to_resigning(tmp_path,mutation):
    request,envelope,eid=fixture(tmp_path);saved=deepcopy(request)
    if mutation=='request':saved['settlement']['total_payout']=999
    elif mutation=='race':envelope['receipt']['race_id']='KM-JRA-KYO-20261025-R08'
    elif mutation=='phase':envelope['receipt']['phase']='FINAL'
    elif mutation=='artifact':envelope['receipt']['artifact_sha256']='c'*64
    elif mutation=='receipt_digest':envelope['receipt_sha256']='c'*64
    elif mutation=='pre_post_time':envelope['receipt']['timestamp']='2026-10-25T00:00:00Z'
    if mutation in {'race','phase','artifact','pre_post_time'}:envelope['receipt_sha256']=production._sha(envelope['receipt'])
    before=stored(tmp_path,saved,envelope,eid);calls=[]
    def call(path,payload):
        calls.append(path);assert path=='/verify'
        return 200,{'valid':mutation!='signature'}
    with pytest.raises(production.ProductionPostResultError,match='RESULT_REUSE_'):
        execute(tmp_path,request,call)
    assert '/result' not in calls and {p:p.read_bytes() for p in before}==before


def test_new_verified_receipt_is_saved_to_existing_store_then_reused(tmp_path):
    request,envelope,eid=fixture(tmp_path);calls=[]
    def call(path,payload):
        calls.append(path)
        return (200,envelope) if path=='/result' else (200,{'valid':True})
    response,first=execute(tmp_path,request,call,'first-run')
    assert calls==['/result','/verify'] and first['status']=='NEW_VERIFIED_RESULT_RECEIPT'
    phase=resolve_phase(eid,'RESULT',root=tmp_path/'runtime/executions');before={p:p.read_bytes() for p in phase['run_dir'].iterdir() if p.is_file()}
    calls.clear();again,second=execute(tmp_path,request,call)
    assert again==response and calls==['/verify'] and second['result_resigning'] is False
    assert {p:p.read_bytes() for p in before}==before


def test_actual_workflow_uses_reuse_before_signing_and_isolates_optional_bvi_typeerror(tmp_path,monkeypatch):
    workflow=(ROOT/'.github/workflows/km-formal-result-runner.yml').read_text()
    assert workflow.index('res,result_receipt_reuse=reuse_or_submit_production_result')<workflow.index('code,res=call("/result",p)')
    assert 'git add "$result_phase"' in workflow
    start=workflow.index('          from scripts.jra_bvi_pipeline_forward_shadow import persist_result_receipt')
    end=workflow.index('          print("KM_RESULT_RESULT="',start)
    import scripts.jra_bvi_pipeline_forward_shadow as shadow
    def fail(*args):raise TypeError('offline unsupported future result shape')
    monkeypatch.setattr(shadow,'persist_result_receipt',fail)
    final=tmp_path/'final.json';final.write_bytes(b'preserved immutable final')
    learning=tmp_path/'learning_state.json';learning.write_bytes(b'preserved learning state')
    before={final:final.read_bytes(),learning:learning.read_bytes()}
    env={'p':{'race_id':RID},'res':{'fixture':'already verified'},'summary':{}}
    exec(compile(textwrap.dedent(workflow[start:end]),'<actual-optional-BVI-block>','exec'),env)
    assert env['summary']['bvi_forward_result_receipt']['status']=='HOLD'
    assert 'TypeError' in env['summary']['bvi_forward_result_receipt']['reason']
    assert {p:p.read_bytes() for p in before}==before
