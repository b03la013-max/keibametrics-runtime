from datetime import datetime, timezone
from pathlib import Path
import importlib.util,json,pytest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('bvi_forward',ROOT/'scripts/jra_bvi_pipeline_forward_shadow.py')
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)


def real_request():
    return json.loads(next((ROOT/'runtime/requests').glob('*KYO-20261011-R07*FORMAL.json')).read_text())


def test_real_historical_source_cannot_become_forward_oos():
    req=real_request()
    with pytest.raises(ValueError,match='CUTOFF_EXPIRED'):
        f.require_open_window(req,datetime(2026,10,11,13,tzinfo=timezone.utc))


def test_replay_cannot_freeze_even_with_a_pre_cutoff_clock():
    req=real_request();req['acceptance_only']=True
    with pytest.raises(ValueError,match='REPLAY_FORBIDDEN'):
        f.require_open_window(req,datetime(2026,10,11,3,tzinfo=timezone.utc))


def test_empty_forward_cohort_stays_pending_and_never_promotes(tmp_path):
    score=f.settle(tmp_path)
    assert score['eligible_settled_races']==0
    assert score['status']=='FORWARD OOS PENDING'
    assert not score['automatic_promotion']
    assert all(a['aggregate']['investment_weighted_pfs'] is None for a in score['arms'].values())


def test_current_authority_roles_match_existing_registered_policy_on_real_source():
    from copy import deepcopy
    from jra_aki_v21 import apply_authorized_v21
    from jra_bvi_shadow_comparison import compare
    from family_authority_guard import resolve_current_authority
    authority_path,authority=resolve_current_authority(ROOT)
    mapping=json.loads((ROOT/'mapping/jra_base_index_evidence_mapping_v1.0_20260921.json').read_text())
    for race in ('07','12'):
        req=json.loads(sorted((ROOT/'runtime/requests').glob(f'*KYO-20261011-R{race}*FORMAL.json'))[-1].read_text())
        saved=deepcopy(req)
        sp=next((ROOT/'runtime/executions'/req['source_execution_id']/'SOURCE').rglob('source_receipt_envelope.json'))
        envelope=json.loads(sp.read_text())
        out=compare(req,mapping,source_sha=req['source_snapshot_sha256'],receipt_sha=envelope['receipt_sha256'],
            algorithm_freeze_at=req['static_freeze_timestamp'],cutoff=req['prediction_cutoff'],
            source_artifact=envelope['artifact'],current_authority=authority,root=ROOT)
        direct=apply_authorized_v21(req,envelope['artifact'],authority,root=ROOT)
        arm=out['arms']['A_CURRENT']
        for field,keys in [('role_registry',('runner_id','column','status')),
                            ('pair_dispositions',('head','second','status')),
                            ('third_dispositions',('head','second','third','status'))]:
            project=lambda rows:sorted(tuple(str(x[k]) for k in keys) for x in rows)
            assert project(arm['owner'][field])==project(direct[field])
            assert all(x['production_authority'] is False for x in arm['owner'][field])
        assert req==saved
        ablation=out['arms']['C_BLOODLINE_ABLATION']
        assert all(r['canonical_components']['BVI']['value']==50 for r in ablation['numerical_runners'])
        assert arm['owner']['official_aki_verification']['status']=='PASS'


def test_mec_receives_each_arms_actual_materialized_numbers(monkeypatch):
    from jra_bvi_shadow_comparison import compare,execute_diagnostic_downstream
    req=real_request()
    mapping=json.loads((ROOT/'mapping/jra_base_index_evidence_mapping_v1.0_20260921.json').read_text())
    comparison=compare(req,mapping,source_sha=req['source_snapshot_sha256'],receipt_sha='0'*64,
        algorithm_freeze_at=req['static_freeze_timestamp'],cutoff=req['prediction_cutoff'])
    # Stop at the payload boundary: no synthetic KRS outcome is accepted.
    import jra_candidate_krs_plan
    checked=[]
    def check(request,**kwargs):
        checked.append(request)
        assert all(r['canonical_components']['BVI']['value']==50 for r in request['runners'])
        raise ValueError('PAYLOAD_BOUNDARY_CHECKED')
    monkeypatch.setattr(jra_candidate_krs_plan,'build_candidate_krs_payload',check)
    comparison['arms']={'C_BLOODLINE_ABLATION':comparison['arms']['C_BLOODLINE_ABLATION']}
    with pytest.raises(ValueError,match='PAYLOAD_BOUNDARY_CHECKED'):
        execute_diagnostic_downstream(comparison,req,None,lambda *args:pytest.fail('No engine call expected'))
    assert len(checked)==1


def test_result_receipt_cannot_create_a_historical_oos_cohort(tmp_path):
    f.persist_result_receipt({'race_id':'KM-JRA-OLD-RACE','result_lane':'PRODUCTION'},{},tmp_path)
    assert not (tmp_path/'runtime/jra_static_owner_forward_oos').exists()


def test_signed_result_write_is_immutable_and_request_bound(tmp_path):
    directory=tmp_path/'runtime/jra_static_owner_forward_oos/KM-JRA-FUTURE-RACE'
    directory.mkdir(parents=True)
    (directory/'pedigree_pipeline_pre_result.json').write_text('{}')
    req={'race_id':'KM-JRA-FUTURE-RACE','result_lane':'PRODUCTION','official_result':{'top3':[1,2,3]}}
    f.persist_result_receipt(req,{'receipt':'FIRST_VERIFIED_RESPONSE'},tmp_path)
    saved=(directory/'production_result_receipt.json').read_bytes()
    f.persist_result_receipt(req,{'receipt':'SECOND_VERIFIED_RESPONSE'},tmp_path)
    assert (directory/'production_result_receipt.json').read_bytes()==saved
    req['official_result']['top3']=[3,2,1]
    with pytest.raises(ValueError,match='REQUEST_CHANGED'):f.persist_result_receipt(req,{},tmp_path)


def test_jra_result_attribution_binds_static_roles_without_changing_common_definitions():
    from jra_bvi_shadow_comparison import bind_jra_static_role_trace
    from krs_prediction_utility import evaluate_against_result
    request={'family_id':'JRA','runners':[{'runner_id':'1'},{'runner_id':'2'},{'runner_id':'3'}],
        'static_prediction':{'roles':{'1':['W'],'2':['P2'],'3':['P3']}}}
    utility={'summary':[{'horse_no':i,'static_roles':[],
        'ranks':{'SSR-W':i,'SSR-P2':i,'SSR-P3':i}} for i in (1,2,3)],
        'snapshot':{'role_zones':{'W':3,'P2':3,'P3':3}},'sha256':'old'}
    fixed=bind_jra_static_role_trace(utility,request)
    result=evaluate_against_result(fixed,[1,2,3],static_ranking=[1,2,3])
    assert all(x['static_role_hit'] for x in result['rank_comparison'])
    assert result['unique_rescue_role_count']==0
    assert all(not x['static_roles'] for x in utility['summary'])
    request['family_id']='LOCAL'
    with pytest.raises(ValueError,match='FAMILY_MISMATCH'):bind_jra_static_role_trace(utility,request)
