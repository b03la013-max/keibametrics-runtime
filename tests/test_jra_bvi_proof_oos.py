from pathlib import Path
import sys,json,copy,importlib.util
import pytest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'runtime'));sys.path.insert(0,str(ROOT/'tests'))
from jra_bvi_failure_attribution import acquisition_failure,summarize,classify_block
from jra_evidence_to_base_production import build_production_ledger,evaluate_partial_production_base_indices
from jra_bvi_static_proof import build_static_proof,verify_static_proof
from jra_bvi_oos_metrics import evaluate,preregister,aggregate
from test_jra_production_auto_handoff import fixture
MAPPING=json.loads((ROOT/'mapping/jra_base_index_evidence_mapping_v1.0_20260921.json').read_text())


def test_known_failed_parent_acquisition_cannot_become_dcr_neutral():
    runner={'runner_id':'7','career_starts':0,'newcomer':True,'evidence_features':{}}
    source={'jra_official_race_card_detail':{'runners':[{'horse_no':7}]},
        'jra_official_horse_history':{'status':'UNAVAILABLE','errors':['JRA_HORSE_HISTORY_FAILED:7:HTTPError:403']}}
    cause=acquisition_failure('7',source,runner,{},MAPPING)
    assert cause=='SOURCE_ACQUISITION_FAILED'
    runners=[{**runner,'runner_id':str(i),'bvi_acquisition_failure':cause} for i in (7,8)]
    with pytest.raises(ValueError,match='BVI_DCR_INELIGIBLE'):build_production_ledger('test',runners,MAPPING)
    out=summarize(evaluate_partial_production_base_indices('test',runners,MAPPING))
    assert out['counts']['BLOCKED_SOURCE_ACQUISITION']==2
    assert out['counts']['DCR_ONLY_CAUSE_UNDETERMINED']==0


def test_newcomer_no_prior_runs_and_unknown_missingness_are_not_fetch_failures():
    runner={'runner_id':'7','career_starts':0,'newcomer':True,'evidence_features':{}}
    source={'jra_official_horse_history':{'status':'NO_PRIOR_RUNS','runners':{'7':{'status':'NO_PRIOR_RUNS'}}}}
    assert acquisition_failure('7',source,runner,{},MAPPING) is None
    source['jra_official_horse_history']={'status':'UNAVAILABLE','errors':['JRA_HORSE_HISTORY_PROFILE_TOKENS_MISSING']}
    assert acquisition_failure('7',source,runner,{},MAPPING) is None
    source['jra_official_horse_history']={'status':'UNAVAILABLE','errors':['JRA_HORSE_HISTORY_FAILED:8:HTTPError:403']}
    assert acquisition_failure('7',source,runner,{},MAPPING) is None
    rows=[{**runner,'runner_id':str(i)} for i in (7,8)]
    out=summarize(evaluate_partial_production_base_indices('test',rows,MAPPING))
    assert out['counts']['DCR_ONLY_CAUSE_UNDETERMINED']==2
    assert classify_block('JRA_PEDIGREE_TARGET_IDENTITY_CONFLICT')=='BLOCKED_IDENTITY'
    assert classify_block('FEATURE_NOT_PRODUCTION')=='BLOCKED_RULE_OR_EVALUATOR'


def test_actual_static_replay_binds_input_owner_and_formal_output_and_rejects_tamper():
    intent,env,report,authority=fixture()
    prepared=report['prepared_numerical_request'];owner=report['static_owner_executable_diagnostic']
    formal={**copy.deepcopy(prepared),'prediction_cutoff':intent['prediction_cutoff'],
        'source_snapshot_sha256':env['artifact']['source_snapshot_sha256'],
        **{k:copy.deepcopy(owner[k]) for k in ('static_prediction','role_registry','pair_dispositions','third_dispositions','purchased_heads')}}
    p=build_static_proof(prepared,owner,formal,authority)
    assert verify_static_proof(p,formal)
    changed=copy.deepcopy(formal);changed['runners'][0]['canonical_components']['BVI']['value']-=1
    with pytest.raises(ValueError,match='BINDING_INVALID'):verify_static_proof(p,changed)
    changed=copy.deepcopy(formal);changed['static_prediction']['ranking'].reverse()
    with pytest.raises(ValueError,match='BINDING_INVALID'):verify_static_proof(p,changed)
    bad=copy.deepcopy(owner);bad['frozen_at']='2026-10-10T13:00:00+09:00'
    with pytest.raises(ValueError):build_static_proof(prepared,bad,formal,authority)


def historical():
    root=ROOT/'runtime/jra_static_owner_forward_oos/KM-JRA-KYO-20261012-R07'
    return (json.loads((root/'pedigree_pipeline_pre_result.json').read_text()),
        json.loads((ROOT/'runtime/results/KM-JRA-KYO-20261012-R07.json').read_text())['official_result'],
        json.loads((root/'pedigree_pipeline_result.json').read_text()))


def test_old_cohort_profiles_are_evaluated_without_posthoc_ticket_selection():
    pre,official,settled=historical();before=copy.deepcopy(pre)
    result=evaluate(pre,official,settled)
    assert pre==before and result['equal_ticket']['status']=='NOT_PREREGISTERED'
    assert sum(result['profiles'].values())==len(pre['comparison']['arms']['A_CURRENT']['numerical_runners'])
    summary=aggregate([result]);assert summary['race_count']==1
    for name in result['arms']:
        assert sum(v['n'] for p in summary['arms'][name].values() for k,v in p['target_roles'].items() if k=='W')==1


def test_frozen_prefix_protocol_is_result_independent_and_tamper_rejected():
    pre,official,settled=historical();pre['comparison_protocol']=preregister(pre['comparison'])
    out=evaluate(pre,official,settled)
    assert out['equal_ticket']['status']=='FROZEN_PREFIX_DIAGNOSTIC'
    assert len({v['investment'] for v in out['equal_ticket']['arms'].values()})==1
    pre['comparison_protocol']['equal_ticket_count']+=1
    with pytest.raises(ValueError,match='PROTOCOL_MISMATCH'):evaluate(pre,official,settled)


def test_enhanced_arm_cannot_change_non_pedigree_evidence():
    pre,official,settled=historical()
    pre['comparison']['arms']['B_PEDIGREE_ENHANCED_SHADOW']['numerical_runners'][0]['evidence_features']['arbitrary_nonpedigree']={'category':'STRONG'}
    with pytest.raises(ValueError,match='NON_PEDIGREE_INPUT_CHANGED'):evaluate(pre,official,settled)


def test_handoff_proof_survives_existing_transport_validation_and_canonical_replay():
    from jra_production_auto_handoff import compile_production_auto_handoff
    from jra_bvi_static_proof import static_input
    from jra_index_provenance_builder import materialize_index_provenance
    intent,env,report,authority=fixture()
    req=compile_production_auto_handoff(intent,env,report,current_authority=authority,
        frozen_at=report['static_owner_executable_diagnostic']['frozen_at'],root=ROOT)
    assert verify_static_proof(req['bvi_static_consumption_proof'],req)
    real=json.loads(next((ROOT/'runtime/requests').glob('*KYO-20261011-R07*FORMAL.json')).read_text())
    assert static_input(real)==static_input(materialize_index_provenance(copy.deepcopy(real)))


def test_real_corpus_ablation_is_not_misreported_as_bvi_scalar_only():
    pre,official,settled=historical()
    out=evaluate(pre,official,settled)
    arm=out['arms']['C_BLOODLINE_ABLATION']
    assert arm['other_base_index_changes_vs_a']['GCI']
    assert arm['other_base_index_changes_vs_a']['KGI']
    assert arm['bvi_only_causal_comparison'] is False
    assert out['arms']['A_CURRENT']['bvi_only_causal_comparison'] is False
