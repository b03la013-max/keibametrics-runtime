"""D uses stored real numerical inputs, but test predictions are synthetic.

These regression tests neither independently verify OIDC nor establish future
OOS or predictive improvement. The real-data acceptance owns those gates.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from family_authority_guard import resolve_current_authority
from jra_bvi_shadow_comparison import compare, ENV_SHADOW_MAPPING, compile_research_static, append_environment_arm
from jra_production_auto_handoff import require_independent_owner_activation
from jra_static_owner_executable import compile_static_owner, JRAStaticOwnerError
from jra_static_owner_forward_oos import sha


def fixture():
    path=sorted((ROOT/'runtime/requests').glob('*KYO-20261011-R12*FORMAL.json'))[-1]
    req=json.loads(path.read_text())
    source_path=next((ROOT/'runtime/executions'/req['source_execution_id']/'SOURCE').rglob('source_receipt_envelope.json'))
    envelope=json.loads(source_path.read_text())
    _,authority=resolve_current_authority(ROOT)
    mapping=json.loads((ROOT/'mapping/jra_base_index_evidence_mapping_v1.0_20260921.json').read_text())
    params={'source_sha':req['source_snapshot_sha256'],'receipt_sha':envelope['receipt_sha256'],
        'algorithm_freeze_at':req['static_freeze_timestamp'],'cutoff':req['prediction_cutoff'],
        'source_artifact':envelope['artifact'],'current_authority':authority,'root':ROOT}
    return req,mapping,params


def predictions(req, *, usable=True):
    source_path=next((ROOT/'runtime/executions'/req['source_execution_id']/'SOURCE').rglob('source_receipt_envelope.json'))
    source=json.loads(source_path.read_text())['artifact']
    card={str(r.get('runner_id') or r.get('horse_no')):r for r in source['jra_official_race_card_detail']['runners']}
    context=source['jra_race_context']
    result={str(r['runner_id']):{
        'model_sha256':'a'*64,'runner_id':str(r['runner_id']),
        'score':20.0+5*(int(r['runner_id'])%12),
        'components':[{'factor':'sire_going','contribution':1.0,
            'support':{'runs':20,'composite_offspring':5}}],
        'usable_for_shadow_override':usable,'reasons':[] if usable else ['INSUFFICIENT_COMPOSITE_OFFSPRING'],
        'production_authority':False,'purchase_authority':False}
        for r in req['runners']}
    for rid,pred in result.items():
        pred['input']={'runner':{k:card[rid].get(k) for k in ('runner_id','horse_name','sire','dam','damsire')},
            'environment':{'venue':context['venue_name'],'surface':context['surface'],
                'distance_m':context['distance_m'],'going':context['going'],'race_date':context['race_date']}}
        pred['input']['runner']['runner_id']=rid
        history=((source.get('jra_official_horse_history') or {}).get('runners') or {}).get(rid) or {}
        pred['input']['runner']['runs']=deepcopy(history.get('runs') or card[rid].get('recent_runs') or [])
        pred['input_sha256']=sha(pred['input'])
    return result


def test_original_production_static_bytes_and_authority_are_unchanged():
    _,_,params=fixture()
    approval=require_independent_owner_activation(params['current_authority'],root=ROOT)
    assert approval['policy_source_sha256']==hashlib.sha256((ROOT/'runtime/jra_static_owner_executable.py').read_bytes()).hexdigest()


def test_default_abc_are_unchanged_when_d_is_appended_and_caller_is_not_mutated():
    req,mapping,params=fixture();original=deepcopy(req)
    baseline=compare(req,mapping,**params)
    enhanced=compare(req,mapping,**params,environment_predictions=predictions(req),environment_model_sha='a'*64)
    assert req==original
    assert tuple(baseline['arms'])==('A_CURRENT','B_PEDIGREE_ENHANCED_SHADOW','C_BLOODLINE_ABLATION')
    assert tuple(enhanced['arms'])==tuple(baseline['arms'])+('D_BVI_ENV_SHADOW',)
    for name in baseline['arms']:
        for field in ('owner','bvi','numerical_runners','numerical_provenance_sha256','krs_input'):
            assert baseline['arms'][name][field]==enhanced['arms'][name][field]
    assert baseline['same_mapping_and_cutoff'] is True
    assert enhanced['same_mapping_and_cutoff'] is False


def test_d_keeps_other_base_and_zai_fixed_replays_derived_and_krs_honestly():
    req,mapping,params=fixture()
    result=compare(req,mapping,**params,environment_predictions=predictions(req),environment_model_sha='a'*64)
    b=result['arms']['B_PEDIGREE_ENHANCED_SHADOW'];d=result['arms']['D_BVI_ENV_SHADOW']
    before={str(r['runner_id']):r for r in b['numerical_runners']}
    assert d['owner']['static_prediction']['ranking']==b['owner']['static_prediction']['ranking']
    assert d['owner']['profile'].startswith('KM-JRA-BVI-ENV-SHADOW')
    assert d['owner']['static_prediction']['production_authority'] is False
    assert d['overridden_runner_ids']
    assert d['krs_input']!=b['krs_input']
    assert 'registered_aki_shadow_replay' in d['owner']
    assert 'official_aki_verification' not in d['owner']
    changed_derived=False
    for row in d['numerical_runners']:
        rid=str(row['runner_id']);cc=row['canonical_components'];old=before[rid]['canonical_components']
        for key in ('HPI','SSI','CFI','RFI','JTI','CSI','TRI','BWI','GCI','PRI','KGI','VMI','DCR','ZAI_WIN','ZAI_PLACE'):
            assert cc[key]['value']==old[key]['value']
        assert all(c['candidate_only'] and c['production_authority'] is False for c in cc.values())
        assert cc['BVI']['mapping_version']==ENV_SHADOW_MAPPING
        assert cc['BVI']['information_status']=='RESEARCH_MODEL_ESTIMATE_NOT_MEASURED_PRODUCTION_BVI'
        changed_derived|=cc['TPI']['value']!=old['TPI']['value']
    assert changed_derived
    proof=d['environment_shadow_proof']
    assert proof['sha256']==sha({k:v for k,v in proof.items() if k!='sha256'})
    assert proof['numerical_runners_sha256']==sha(d['numerical_runners'])
    assert d['krs_simulation_executed'] is False
    assert d['ticket_count'] is None and d['capital_required'] is None


def test_all_unsupported_d_predictions_retain_b_values_with_explicit_fallback():
    req,mapping,params=fixture()
    result=compare(req,mapping,**params,environment_predictions=predictions(req,usable=False),environment_model_sha='a'*64)
    b=result['arms']['B_PEDIGREE_ENHANCED_SHADOW'];d=result['arms']['D_BVI_ENV_SHADOW']
    assert d['overridden_runner_ids']==[]
    assert len(d['fallback_runner_reasons'])==len(req['runners'])
    for rid in b['bvi']:assert b['bvi'][rid]['value']==d['bvi'][rid]['value']
    assert b['krs_input']==d['krs_input']


def test_production_static_entry_still_rejects_d_candidate_numerics():
    req,mapping,params=fixture()
    d=compare(req,mapping,**params,environment_predictions=predictions(req),environment_model_sha='a'*64)['arms']['D_BVI_ENV_SHADOW']
    candidate=deepcopy(req);candidate['runners']=d['numerical_runners']
    # Even retaining the original Production mapping authority cannot admit D.
    with pytest.raises(JRAStaticOwnerError,match='CANDIDATE_NUMERICAL_FORBIDDEN'):
        compile_static_owner(candidate,source_snapshot_sha256=params['source_sha'],source_receipt_sha256=params['receipt_sha'],
            frozen_at=params['algorithm_freeze_at'],prediction_cutoff=params['cutoff'])


@pytest.mark.parametrize('fault',['model','runner','input','input_payload','parent','environment','authority','universe','score','no_authority'])
def test_candidate_binding_and_scope_fail_closed(fault):
    req,mapping,params=fixture();pred=predictions(req);rid=next(iter(pred))
    if fault=='model':pred[rid]['model_sha256']='c'*64
    if fault=='runner':pred[rid]['runner_id']='999'
    if fault=='input':pred[rid]['input_sha256']='not-a-sha'
    if fault=='input_payload':pred[rid]['input']['environment']['going']='不良'
    if fault=='parent':
        pred[rid]['input']['runner']['sire']='unrelated'
        pred[rid]['input_sha256']=sha(pred[rid]['input'])
    if fault=='environment':
        pred[rid]['input']['environment']['going']='不良'
        pred[rid]['input_sha256']=sha(pred[rid]['input'])
    if fault=='authority':pred[rid]['production_authority']=True
    if fault=='universe':pred.pop(rid)
    if fault=='score':pred[rid]['score']=float('nan')
    if fault=='no_authority':params['current_authority']=None
    with pytest.raises(ValueError,match='ENV_SHADOW_'):
        compare(req,mapping,**params,environment_predictions=pred,environment_model_sha='a'*64)


def test_append_preserves_existing_abc_execution_and_records_real_d_time():
    req,mapping,params=fixture();result=compare(req,mapping,**params)
    before=deepcopy(result['arms'])
    append_environment_arm(result,req,mapping,predictions=predictions(req),model_sha='a'*64,
        source_artifact=params['source_artifact'],current_authority=params['current_authority'],root=ROOT)
    for name in before:assert result['arms'][name]==before[name]
    d=result['arms']['D_BVI_ENV_SHADOW']
    assert d['owner']['frozen_at']==d['numerical_calculated_at']
    assert d['owner']['frozen_at']!=params['algorithm_freeze_at']
    assert d['environment_shadow_proof']['execution_class']=='POST_CAPTURE_DIAGNOSTIC'
    assert d['owner']['original_prediction_cutoff']==req['prediction_cutoff']
    with pytest.raises(ValueError,match='ENV_SHADOW_D_ALREADY_PRESENT'):
        append_environment_arm(result,req,mapping,predictions=predictions(req),model_sha='a'*64,
            source_artifact=params['source_artifact'],current_authority=params['current_authority'],root=ROOT)


def test_candidate_static_proof_detects_numerical_mutation():
    req,mapping,params=fixture()
    all_arms=compare(req,mapping,**params,environment_predictions=predictions(req),environment_model_sha='a'*64)['arms']
    b=all_arms['B_PEDIGREE_ENHANCED_SHADOW'];d=all_arms['D_BVI_ENV_SHADOW']
    base=deepcopy(req);base['runners']=deepcopy(b['numerical_runners'])
    candidate=deepcopy(req);candidate['runners']=deepcopy(d['numerical_runners'])
    candidate.update(candidate_only=True,production_authority=False,purchase_authority=False)
    candidate['environment_shadow_proof']=deepcopy(d['environment_shadow_proof'])
    candidate['runners'][0]['canonical_components']['TPI']['value']+=1
    with pytest.raises(ValueError,match='ENV_SHADOW_STATIC_PROOF_BINDING_INVALID'):
        compile_research_static(candidate,base,b['owner'],source_artifact=params['source_artifact'],
            current_authority=params['current_authority'],root=ROOT)


@pytest.mark.parametrize('fault',['omit','empty','finish','future','current','wrong_type'])
def test_source_bound_ability_history_cannot_be_replaced_or_omitted(fault):
    from jra_bvi_shadow_comparison import _validate_prediction_input
    req,_,params=fixture();preds=predictions(req)
    rid=next(k for k,p in preds.items() if p['input']['runner']['runs'])
    pred=preds[rid];runner=pred['input']['runner']
    if fault=='omit':runner.pop('runs')
    if fault=='empty':runner['runs']=[]
    if fault=='finish':runner['runs'][0]['finish']=1 if runner['runs'][0]['finish']!=1 else 2
    if fault in ('future','current'):
        row=deepcopy(runner['runs'][0]);row['date']='2099-01-01' if fault=='future' else req['race_date']
        runner['runs'].append(row)
    if fault=='wrong_type':runner['runs']={}
    # Rehashing self-declared input does not make it SOURCE-authenticated.
    pred['input_sha256']=sha(pred['input'])
    with pytest.raises(ValueError,match='ENV_SHADOW_.*HISTORY_'):
        _validate_prediction_input(pred,rid,params['source_artifact'],req)


def test_conflicting_signed_history_name_or_source_environment_is_not_silently_used():
    from jra_bvi_shadow_comparison import _validate_prediction_input
    req,_,params=fixture();preds=predictions(req);rid=next(iter(preds))
    source=deepcopy(params['source_artifact'])
    source['jra_official_horse_history']['runners'][rid]['horse_name']='unrelated'
    with pytest.raises(ValueError,match='ENV_SHADOW_SOURCE_HISTORY_NAME_CONFLICT'):
        _validate_prediction_input(preds[rid],rid,source,req)
    source=deepcopy(params['source_artifact'])
    source['jra_official_race_card_detail']['race_context']['going']='不良'
    with pytest.raises(ValueError,match='ENV_SHADOW_SOURCE_ENVIRONMENT_CONFLICT'):
        _validate_prediction_input(preds[rid],rid,source,req)
