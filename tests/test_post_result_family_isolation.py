"""Existing LOCAL schema and BAN contract controls do not inherit JRA rules.

The LOCAL views copy fields from pinned signed artifacts; they are not new
FINALs, RESULTs or Learning States. BAN has no stored signed race in this
repository, so its controls prove schema isolation only, never Live readiness.
"""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from post_result_learning import build_post_result_review,build_learning_state,LearningError

FIXTURE=json.loads((ROOT/'tests/fixtures/family_post_result_isolation.json').read_text())
LOCAL=FIXTURE['local_records']
BAN=FIXTURE['ban_schema_only']


@pytest.mark.parametrize('record',LOCAL,ids=lambda r:r['race_id'])
@pytest.mark.parametrize('semantics',['LEGACY','DECISION_AWARE_V2'])
def test_existing_local_result_schema_preserves_current_main_review_and_learning(record,semantics):
    result,final=deepcopy((record['result'],record['final']))
    before=deepcopy((result,final))
    # This is the existing LOCAL adapter's view, not a new JRA payout schema.
    assert result['official_result']['top3']==result['official_result']['finish_order'][:3]
    assert all(type(v) is int for v in result['official_result']['payouts'].values())
    review=build_post_result_review(result,final,review_semantics=semantics)
    learning=build_learning_state(review)
    expected=record['expected_current_main'][semantics]
    assert review['sha256']==expected['review_sha256']
    assert learning['sha256']==expected['learning_sha256']
    assert review['capital']==expected['capital']
    assert review['prediction']['role_capture']==expected['role_capture']
    assert review['failure_localization']['first_material_failure']==expected['first_material_failure']
    assert review['krs']['post_result_evaluation']['classification']==expected['krs_classification']
    assert 'official_top3_orders' not in review
    assert review['production_change_authorized'] is learning['production_change_authorized'] is False
    assert (result,final)==before


@pytest.mark.parametrize('record',LOCAL,ids=lambda r:r['race_id'])
def test_local_opaque_result_metadata_does_not_create_jra_schema_requirements(record):
    # A scoping control, not a claim that LOCAL dead heats are adjudicated.
    result,final=deepcopy((record['result'],record['final']))
    result['official_result'].update(dead_heat=True,finish_groups={'family_specific_metadata':True})
    before=deepcopy(result)
    review=build_post_result_review(result,final)
    assert review['sha256']==record['expected_current_main']['LEGACY']['review_sha256']
    assert 'official_top3_orders' not in review
    assert result==before


@pytest.mark.parametrize('semantics',['LEGACY','DECISION_AWARE_V2'])
def test_ban_schema_only_control_preserves_unknown_and_does_not_establish_live_runtime(semantics):
    assert BAN['actual_signed_result_found'] is False
    result,final=deepcopy((BAN['result'],BAN['final']))
    before=deepcopy((result,final))
    review=build_post_result_review(result,final,review_semantics=semantics)
    learning=build_learning_state(review)
    assert review['sha256']==BAN['expected_current_main'][semantics]['review_sha256']
    assert learning['sha256']==BAN['expected_current_main'][semantics]['learning_sha256']
    assert review['capital']['pfs'] is None and review['capital']['settlement_status']=='UNKNOWN'
    assert learning['production_change_authorized'] is False
    assert (result,final)==before
    from family_runtime_contract import FamilyRuntimeError,resolve_family_runtime,load_contracts
    with pytest.raises(FamilyRuntimeError,match='ATTESTATION_MISSING'):
        resolve_family_runtime({'family_id':'BAN'},load_contracts())


@pytest.mark.parametrize('record',LOCAL+[BAN],ids=lambda r:r.get('race_id','BAN-SCHEMA-ONLY'))
def test_non_jra_review_works_in_fresh_process_without_jra_candidate_module(tmp_path,record):
    code='''
import json,sys
sys.path.insert(0,sys.argv[1])
from post_result_learning import build_post_result_review,build_learning_state
# Model a family bundle without the JRA-only Candidate collector. A combined
# pytest collection cannot hide this boundary by preloading that module.
sys.modules['jra_candidate_postresult_closedloop']=None
result,final=json.load(sys.stdin)
review=build_post_result_review(result,final)
learning=build_learning_state(review)
assert sys.modules['jra_candidate_postresult_closedloop'] is None
assert 'jra_source_runtime.jra_same_day_results' not in sys.modules
print(json.dumps([review['sha256'],learning['sha256']]))
'''
    proc=subprocess.run([sys.executable,'-I','-c',code,str(ROOT/'runtime')],
        input=json.dumps([record['result'],record['final']]),capture_output=True,
        text=True,cwd=tmp_path,timeout=15)
    assert proc.returncode==0,proc.stderr
    expected=record['expected_current_main']['LEGACY']
    assert json.loads(proc.stdout)==[expected['review_sha256'],expected['learning_sha256']]


def test_jra_canonical_identity_cannot_bypass_tie_checks_with_optional_local_family_label():
    from jra_candidate_postresult_closedloop import verify_official_result
    from jra_production_postresult import build_result_request
    facts=json.loads((ROOT/'tests/fixtures/jra_20261025_ngt_dead_heat.json').read_text())['records'][0]
    path=ROOT/'runtime/final_artifacts'/(facts['race_id']+'.json')
    raw=path.read_bytes();final=json.loads(raw)
    official=verify_official_result(facts['parsed'],facts['official_payout_text_derived'],
                                    list(map(str,final['static_prediction']['ranking'])))
    result=build_result_request(final,official,{'parsed':facts['parsed']})
    result['family_id']=final['family_id']='LOCAL'  # untrusted optional labels
    result['official_result']['top3_orders'].pop()
    with pytest.raises(LearningError,match='GROUP_BINDING_MISMATCH'):
        build_post_result_review(result,final)
    assert path.read_bytes()==raw
