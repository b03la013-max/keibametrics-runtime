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


def test_real_compact_result_receipt_binds_request_without_embedded_artifact(monkeypatch,tmp_path):
    from copy import deepcopy
    directory=ROOT/'runtime/jra_static_owner_forward_oos/KM-JRA-KYO-20261012-R07'
    pre=json.loads((directory/'pedigree_pipeline_pre_result.json').read_text())
    result=json.loads((ROOT/'runtime/results'/f"{pre['race_id']}.json").read_text())
    bound=json.loads((directory/'production_result_receipt.json').read_text())
    assert 'artifact' not in bound['signed_result_envelope']
    assert bound['signed_result_envelope']['receipt']['artifact_sha256']==f.sha(result)
    # Boundary test only. Live acceptance independently calls the real verifier.
    target=tmp_path/directory.relative_to(ROOT);target.mkdir(parents=True)
    rp=tmp_path/'runtime/results';rp.mkdir()
    for name,value in [('pedigree_pipeline_pre_result.json',pre),('production_result_receipt.json',bound)]:
        (target/name).write_text(json.dumps(value))
    result_path=rp/f"{pre['race_id']}.json";result_path.write_text(json.dumps(result))
    monkeypatch.setattr(f.subprocess,'check_output',lambda *a,**k:pre['frozen_at'])
    monkeypatch.setattr(f,'call',lambda *a,**k:{'valid':True})
    out=f._settle_record(target/'pedigree_pipeline_pre_result.json',tmp_path)
    assert out['signed_result_verified'] and out['oos_eligible']
    result['official_result']['top3']=list(reversed(result['official_result']['top3']))
    result_path.write_text(json.dumps(result))
    with pytest.raises(ValueError,match='SIGNED_RESULT_BINDING_INVALID'):
        f._settle_record(target/'pedigree_pipeline_pre_result.json',tmp_path)


def test_corrupt_race_is_held_without_blocking_other_races(tmp_path):
    p=tmp_path/'runtime/jra_static_owner_forward_oos/broken/pedigree_pipeline_pre_result.json'
    p.parent.mkdir(parents=True);p.write_text('{}')
    out=f.settle(tmp_path)
    assert out['eligible_settled_races']==0
    assert out['race_failures']==[{'race_id':'broken','status':'HOLD','reason':'BVI_FORWARD_FROZEN_HASH_INVALID'}]


def test_canonical_production_baseline_binds_actual_tickets_and_rejects_changed_direction():
    from copy import deepcopy
    req=real_request()
    final=json.loads((ROOT/'runtime/final_artifacts'/f"{req['race_id']}.json").read_text())
    comparison={'arms':{'A_CURRENT':{'owner':{k:deepcopy(final[k]) for k in
        ('static_prediction','role_registry','pair_dispositions','third_dispositions')},
        'diagnostic_tickets':deepcopy(final['final_ticket']['tickets'])}}}
    proof=f.bind_production_reference(comparison,req,final)
    assert proof['final_sha256']==final['sha256']
    assert proof['pfs_basis'].endswith('ACTUAL_PURCHASE_UNVERIFIED')
    comparison['arms']['A_CURRENT']['diagnostic_tickets'][0]['selection'].reverse()
    with pytest.raises(ValueError,match='CANONICAL_TICKET_REPLAY_MISMATCH'):
        f.bind_production_reference(comparison,req,final)


def test_real_comparison_consumption_preserves_verified_source_annotations():
    from copy import deepcopy
    from jra_bvi_shadow_comparison import compare
    from family_authority_guard import resolve_current_authority
    req=real_request();saved=deepcopy(req)
    mapping=json.loads((ROOT/'mapping/jra_base_index_evidence_mapping_v1.0_20260921.json').read_text())
    env=json.loads(next((ROOT/'runtime/executions'/req['source_execution_id']/'SOURCE').rglob('source_receipt_envelope.json')).read_text())
    _,authority=resolve_current_authority(ROOT)
    compared=compare(req,mapping,source_sha=req['source_snapshot_sha256'],receipt_sha=env['receipt_sha256'],
        algorithm_freeze_at=req['static_freeze_timestamp'],cutoff=req['prediction_cutoff'],
        source_artifact=env['artifact'],current_authority=authority,root=ROOT)
    proof=f.arm_consumption(compared,req,env['artifact'],mapping,authority,execution_class='POSTCAPTURE_DIAGNOSTIC_ONLY')
    assert len(proof)==3 and req==saved
    assert all(p['static_execution_proof_status']=='BOUND_ACTUAL_EXECUTION' for p in proof.values())
    req['source_checkpoint_manifest']['receipt_sha256']='0'*64
    with pytest.raises(ValueError,match='SOURCE_ANNOTATION_INVALID'):
        f.arm_consumption(compared,req,env['artifact'],mapping,authority)


def test_metadata_only_enrichment_is_not_a_changed_bvi_value():
    from copy import deepcopy
    from jra_bvi_shadow_comparison import compare,PEDIGREE_FEATURES
    req=real_request();enriched={}
    for runner in req['runners']:
        enriched[str(runner['runner_id'])]={key:{**deepcopy(value),'observed_at':'2026-10-11T03:30:00+00:00'}
            for key,value in runner['evidence_features'].items() if key in PEDIGREE_FEATURES}
    mapping=json.loads((ROOT/'mapping/jra_base_index_evidence_mapping_v1.0_20260921.json').read_text())
    out=compare(req,mapping,source_sha=req['source_snapshot_sha256'],receipt_sha='0'*64,
        algorithm_freeze_at=req['static_freeze_timestamp'],cutoff=req['prediction_cutoff'],enhanced_features=enriched)
    assert out['enhanced_bvi_distinct'] is False
    assert out['enhanced_ranking_distinct'] is False


def _actual_oct18_priority_fixture(tmp_path):
    import shutil
    plan_path=Path('runtime/jra_race_day_plan/2026-10-18.json')
    (tmp_path/plan_path.parent).mkdir(parents=True)
    shutil.copyfile(ROOT/plan_path,tmp_path/plan_path)
    shutil.copytree(ROOT/'runtime/jra_race_registrations/2026-10-18',tmp_path/'runtime/jra_race_registrations/2026-10-18')
    schedule=Path('runtime/jra_race_day_plan/2026-10-18.schedule.json')
    shutil.copyfile(ROOT/schedule,tmp_path/schedule)
    plan=json.loads((tmp_path/plan_path).read_text())
    req=json.loads((tmp_path/'runtime/jra_race_registrations/2026-10-18/KM-JRA-NGT-20261018-R01.json').read_text())['intake_intent']
    return req,plan['cohort']['race_ids']


def test_oct18_shadow_defers_to_other_due_production_from_real_cohort(tmp_path):
    req,ids=_actual_oct18_priority_fixture(tmp_path)
    with pytest.raises(ValueError,match='DEFER_PRODUCTION_PENDING:.*TKY'):
        f.production_priority_window(req,root=tmp_path,now=datetime.fromisoformat('2026-10-18T09:00:00+09:00'))


def test_oct25_and_future_shadow_fail_closed_without_official_plan(tmp_path):
    for day in ('2026-10-25','2026-11-01'):
        with pytest.raises(ValueError,match='DEFER_OFFICIAL_DAY_PLAN_MISSING'):
            f.production_priority_window({'race_date':day},root=tmp_path)


def test_freeze_uses_dynamic_production_priority_and_explicit_code_lineage():
    text=(ROOT/'scripts/jra_bvi_pipeline_forward_shadow.py').read_text()
    assert "day>='2026-10-25'" in text
    assert "{day.replace" in text and "'code_git_sha':" in text
    assert "'model_sha256':" in text


def test_oct18_shadow_stops_before_next_dispatch_and_requires_useful_slack(tmp_path):
    req,ids=_actual_oct18_priority_fixture(tmp_path)
    stop=f.production_priority_window(req,root=tmp_path,now=datetime.fromisoformat('2026-10-18T08:40:00+09:00'))
    assert stop==datetime.fromisoformat('2026-10-18T08:48:00+09:00')
    with pytest.raises(ValueError,match='DEFER_INSUFFICIENT_SAFE_WINDOW'):
        f.production_priority_window(req,root=tmp_path,now=datetime.fromisoformat('2026-10-18T08:46:00+09:00'))


def test_oct18_verified_completed_peers_allow_bounded_shadow_not_late_freeze(tmp_path):
    req,ids=_actual_oct18_priority_fixture(tmp_path)
    now=datetime.fromisoformat('2026-10-18T09:10:00+09:00')
    assert f.production_priority_window(req,root=tmp_path,now=now,signed_final_ids=ids)==datetime.fromisoformat('2026-10-18T09:20:00+09:00')
    with pytest.raises(ValueError,match='DEFER_INSUFFICIENT_SAFE_WINDOW'):
        f.production_priority_window(req,root=tmp_path,now=datetime.fromisoformat('2026-10-18T09:32:00+09:00'),signed_final_ids=ids)


def test_oct18_corrupt_registration_cannot_admit_shadow(tmp_path):
    req,ids=_actual_oct18_priority_fixture(tmp_path)
    other=next(rid for rid in ids if rid!=req['race_id'])
    path=tmp_path/'runtime/jra_race_registrations/2026-10-18'/f'{other}.json'
    doc=json.loads(path.read_text());doc['planned_required_cells']=1;path.write_text(json.dumps(doc))
    with pytest.raises(ValueError,match='JRA_REGISTRATION_HASH_MISMATCH'):
        f.production_priority_window(req,root=tmp_path,now=datetime.fromisoformat('2026-10-18T08:00:00+09:00'))
    assert f.production_priority_window({'race_date':'2026-10-17'},root=tmp_path) is None
