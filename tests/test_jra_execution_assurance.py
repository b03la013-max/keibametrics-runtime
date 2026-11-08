import copy
import hashlib
import json
from pathlib import Path
import sys
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from jra_production_krs_contract import (production_krs_payload,assert_production_krs_receipt,
    checkpoint_krs_request,JRAProductionKRSContractError)
from race_day_fast_reflection import build_fast_reflection
from jra_learning_intake import build_shadow_learning_intake,digest


def frozen():
    rid='KM-JRA-KYO-20261017-R11'
    req=json.loads((ROOT/'runtime/requests'/f'{rid}-LIVE-R1-FORMAL.json').read_text())
    raw=json.loads((ROOT/'evidence/jra_day_review_20261017/krs_checkpoints/39007251004'/rid/'krs_response.json').read_text())
    return production_krs_payload(req),raw


def check(payload,response):
    return assert_production_krs_receipt(payload,response,
        expected_engine_sha256='9929df994aa7964173edef9af7e9a705628ce377babf22df3af4e280fc275421')


def test_actual_kyo11_receipt_cannot_authenticate_a_changed_output():
    p,r=frozen();before=copy.deepcopy(r)
    check(p,r)
    r['output']['unexpected_result_after_signing']=True
    with pytest.raises(JRAProductionKRSContractError,match='STRUCTURED_OUTPUT_MISMATCH'):check(p,r)
    r=copy.deepcopy(before);r['output_canonical_json']+=' '
    with pytest.raises(JRAProductionKRSContractError,match='OUTPUT_HASH_MISMATCH'):check(p,r)


def test_declared_input_contract_checks_content_and_rejects_unknown_version():
    p,r=frozen();receipt=r['run_receipt']['receipt']
    receipt['input_hash_contract']='KM-KRS-INPUT-DATA-SORTED-UTF8-v1'
    receipt['input_sha256']=digest(p['input_data']);check(p,r)
    changed=copy.deepcopy(p);changed['input_data']['horses'][0]['name']='DIFFERENT'
    with pytest.raises(JRAProductionKRSContractError,match='INPUT_HASH_MISMATCH'):check(changed,r)
    receipt['input_hash_contract']='UNREGISTERED'
    with pytest.raises(JRAProductionKRSContractError,match='CONTRACT_UNSUPPORTED'):check(p,r)


def test_exact_wire_checkpoint_is_immutable_and_can_reproduce_request(tmp_path):
    p,_=frozen();body,record=checkpoint_krs_request(p,tmp_path)
    assert json.loads(body)==p
    assert record['wire_sha256']==hashlib.sha256((tmp_path/'krs_request_wire.json').read_bytes()).hexdigest()
    assert checkpoint_krs_request(p,tmp_path)==(body,record)
    p['seed']+=1
    with pytest.raises(JRAProductionKRSContractError,match='CHECKPOINT_CONFLICT'):checkpoint_krs_request(p,tmp_path)


def test_paper_zero_investment_is_not_missing_learning_data():
    assert build_fast_reflection({'race_id':'P','settlement':{'investment':0}})['settlement']['investment']==0
    assert build_fast_reflection({'race_id':'U'})['settlement']['investment'] is None


def test_shadow_learning_blocks_future_target_unverified_and_tampered_states():
    state={'state_id':'S','race_id':'KM-JRA-KYO-20261017-R11','effective_time':'2026-10-17T17:20:00+09:00',
        'learning_validity':'FAMILY-CANDIDATE'};state['sha256']=digest(state)
    args=dict(race_id='KM-JRA-TKY-20261018-R01',source_freeze='2026-10-18T09:00:00+09:00',
              cutoff='2026-10-18T09:10:00+09:00',observed_at='2026-10-18T09:00:00+09:00')
    before=copy.deepcopy(state);r=build_shadow_learning_intake([state],**args)
    assert state==before and len(r['accepted'])==1
    duplicate=build_shadow_learning_intake([state,copy.deepcopy(state)],**args)
    assert not duplicate['accepted'] and len(duplicate['excluded'])==2
    assert r['prediction_application']=='NOT APPLIED'
    target=copy.deepcopy(state);target['race_id']=args['race_id'];target['sha256']=digest({k:v for k,v in target.items() if k!='sha256'})
    assert build_shadow_learning_intake([target],**args)['excluded'][0]['reason']=='TARGET_RACE_LEARNING_FORBIDDEN'
    with pytest.raises(ValueError,match='AFTER_CUTOFF'):
        build_shadow_learning_intake([state],**{**args,'observed_at':'2026-10-18T09:11:00+09:00'})
    changed={**state,'effective_time':'2026-10-19T00:00:00+09:00'}
    assert build_shadow_learning_intake([changed],**args)['excluded'][0]['reason']=='STATE_HASH_MISMATCH'

def test_role_rescue_shadow_uses_frozen_unique_proposals_and_never_changes_final():
    from jra_role_rescue_shadow import build_role_rescue_shadow
    final=json.loads((ROOT/'runtime/final_artifacts/KM-JRA-KYO-20261017-R11.json').read_text())
    before=copy.deepcopy(final);out=build_role_rescue_shadow(final)
    assert final==before
    assert out['actual_added_capital']==0
    assert [(p['horse_no'],p['proposal']) for p in out['selected_proposals']]==[(11,'ADD_P2_SHADOW')]
    final.pop('krs_run_receipt')
    with pytest.raises(ValueError,match='ACTUAL_KRS_EVIDENCE'):build_role_rescue_shadow(final)
