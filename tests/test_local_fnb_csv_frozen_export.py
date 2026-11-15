"""Synthetic runtime-output integration, not admitted SOURCE or actual KRS."""
from copy import deepcopy
from datetime import datetime,timezone
import importlib.util
import json
from pathlib import Path

import pytest
from runtime import local_fnb_csv_postresult as post
from runtime import local_fnb_csv_research_runtime as runtime
from runtime import local_fnb_semantic_closure as semantic
from runtime.minimum_efficient_coverage import build_mec_plan

FREEZE=datetime(2026,11,3,5,31,tzinfo=timezone.utc)


def inputs():
    request={'race_id':'KM-LOCAL-FNB-20261103-R01-SYNTHETIC','family_id':'LOCAL','venue_id':'FNB',
        'race_date':'2026-11-03','race_no':1,'prediction_cutoff':'2026-11-03T14:40:00+09:00',
        'scheduled_post_at':'2026-11-03T14:45:00+09:00'}
    req={**request,'available_bet_types':['EXACTA','TRIO','TRIFECTA'],'role_registry':[],
        'purchased_heads':['1'],'pair_dispositions':[{'head':'1','second':'2','status':'PURCHASE'}],
        'third_dispositions':[{'head':'1','second':'2','third':'3','status':'PURCHASE'}],
        'capital_policy':{'mode':'HARD_RACE_BUDGET','max_race_capital':10000,'insufficient_action':'NO_BET'}}
    for no,col in [('1','W'),('2','P2'),('3','P3')]:
        for column in ('W','P2','P3'):
            req['role_registry'].append({'runner_id':no,'column':column,
                'status':'CORE' if column==col else 'EXCLUDED','reason':'SYNTHETIC_FIXED_SELECTION'})
    plan=build_mec_plan(req,strict_head_closure=True,min_stake=100)
    strict={'race_id':request['race_id'],'status':'CANONICAL_MEC_EXECUTED_NOT_FORMAL_QUALIFICATION',
        'all_hold_causes':[],'strict_mec_executed':True,'canonical_mec_plan':plan,
        'canonical_mec_request':req,'tickets':deepcopy(plan['tickets'])}
    pred={'race_id':request['race_id'],'model_id':'SYNTHETIC_FIXED_OWNER_NOT_LIVE',
        'model_code_sha256':runtime.common.MODEL_SHA,'source_snapshot_sha256':'a'*64,
        'freeze_at':'2026-11-03T14:30:00+09:00','roles':{'1':['W'],'2':['P2'],'3':['P3']}}
    krs={'run_count':5000,'seed':1,'engine_sha256':runtime.common.ENGINE_SHA,
        'parameter_map_sha256':runtime.common.MAP_SHA,'new_engine_execution':False}
    return request,strict,pred,krs


def originals(folder):
    for name in ('original.zip','csv_source_assessment.json','csv_source_receipt_envelope.json',
        'owner_decision_original.json','race_request.json','research_prediction.json','original_strict_mec.json',
        'numerical/numerical_materialization.json','krs/research_krs_receipt.json','krs/execution_output.json'):
        path=folder/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b'{"synthetic":true}\n')


def test_strict_hold_exports_nothing_and_does_not_become_no_bet(tmp_path):
    req,strict,pred,krs=inputs();strict['status']='HOLD_NOT_NO_BET'
    out=post.export_strict_methods(folder=tmp_path,request=req,prediction=pred,strict=strict,krs=krs,
        clock=lambda:FREEZE,execution_recipe_sha256='b'*64)
    assert out['methods']=={} and out['computed_no_bet'] is False
    assert not list(tmp_path.iterdir())


def test_exporter_resolves_real_existing_capital_and_keeps_three_alternatives(tmp_path):
    req,strict,pred,krs=inputs();originals(tmp_path)
    out=post.export_strict_methods(folder=tmp_path,request=req,prediction=pred,strict=strict,krs=krs,
        clock=lambda:FREEZE,execution_recipe_sha256='b'*64)
    assert set(out['methods'])==set(post.METHODS)
    for method,detail in out['methods'].items():
        frozen=json.loads(Path(detail['frozen_original']['path']).read_bytes())
        assert frozen['method']==method and frozen['selection_complete'] is True
        assert all(t['bet_type']==method for t in frozen['final_ticket']['tickets'])
        assert frozen['capital_policy_decision']['decision']=='EXECUTE_FULL_MEC'
        assert frozen['formal_final'] is False


def test_paper_capital_is_not_exported_as_selected_or_computed_no_bet(tmp_path):
    req,strict,pred,krs=inputs();originals(tmp_path)
    strict['canonical_mec_request']['aki_information_gate']={'action':'PAPER','reason':'SYNTHETIC_ONLY'}
    out=post.export_strict_methods(folder=tmp_path,request=req,prediction=pred,strict=strict,krs=krs,
        clock=lambda:FREEZE,execution_recipe_sha256='b'*64)
    assert all(v['status']=='PAPER_NOT_PRESTART_SELECTED' for v in out['methods'].values())
    assert not (tmp_path/'postresult').exists()


def test_expired_exporter_does_not_create_ticket_originals(tmp_path):
    req,strict,pred,krs=inputs();originals(tmp_path)
    with pytest.raises(ValueError,match='AFTER_CUTOFF'):
        post.export_strict_methods(folder=tmp_path,request=req,prediction=pred,strict=strict,krs=krs,
            clock=lambda:datetime(2026,11,3,5,40,tzinfo=timezone.utc),execution_recipe_sha256='b'*64)
    assert not (tmp_path/'postresult').exists()


@pytest.mark.parametrize('strict_ready',[True,False])
def test_qualified_completed_runtime_actually_saves_postresult_consumable_originals(tmp_path,monkeypatch,strict_ready):
    req,strict,pred,krs=inputs()
    if not strict_ready:
        strict.update(status='HOLD_NOT_NO_BET',tickets=None,
            all_hold_causes=[{'reason':'SYNTHETIC_UNKNOWN_SELECTION_NOT_ADOPTED'}])
    pred.update(active_runners=['1','2','3'],PRE_KRS_input={})
    numerical={**{key:req[key] for key in ('race_id','race_date','race_no')},'race':{},
        'candidate_current_state':{'source_snapshot_sha256':'a'*64},'candidate_environment':{},
        'candidate_full_numerical_summary':{'required_indices':[]},
        'runners':[{'runner_id':str(n)} for n in (1,2,3)]}
    parsed={'capture':{'captured_at':'2026-11-03T14:00:00+09:00'},
        'runners':[{'runner_number':n} for n in (1,2,3)]}
    monkeypatch.setattr(runtime.common,'_pinned',lambda *args:None)
    monkeypatch.setattr(runtime.common,'_prestart_clock',lambda *args,**kwargs:FREEZE)
    monkeypatch.setattr(runtime,'observation_packet',lambda *args,**kwargs:{
        'runners':[{'runner_id':str(n)} for n in (1,2,3)],'counts':{}})
    monkeypatch.setattr(runtime,'build_context',lambda *args,**kwargs:{})
    monkeypatch.setattr(runtime.common,'build_upstream',lambda *args,**kwargs:({},{}))
    monkeypatch.setattr(runtime,'predict',lambda *args,**kwargs:deepcopy(pred))
    monkeypatch.setattr(semantic,'assess_semantics',lambda *args,**kwargs:{})
    monkeypatch.setattr(semantic,'execute_strict_mec',lambda *args,**kwargs:deepcopy(strict))
    import runtime.local_fnb_r13_private_numeric_document as document
    monkeypatch.setattr(document,'render_full_numeric',lambda *args,**kwargs:{'body':'SYNTHETIC_ONLY'})
    monkeypatch.setattr(runtime.common,'_render_private_body',lambda *args,**kwargs:b'SYNTHETIC_ONLY\n')
    def execute(*args,**kwargs):
        target=kwargs['destination'];target.mkdir(parents=True,exist_ok=True)
        (target/'execution_output.json').write_bytes(b'{"synthetic":true}\n')
        return deepcopy(krs)
    monkeypatch.setattr(runtime.common,'execute_krs',execute)
    source_originals={name:runtime._source_original({'SYNTHETIC_NOT_REAL_SOURCE':True},None,'SYNTHETIC')
        for name in ('csv_source_assessment.json','csv_source_receipt_envelope.json')}
    out=runtime._execute(numerical,parsed,b'SYNTHETIC_ZIP_NOT_REAL_SOURCE',req,
        private_root=tmp_path,engine='SYNTHETIC',params='SYNTHETIC',admission={'synthetic':True},
        owner_decision={'decision_sha256':'c'*64},owner_decision_bytes=b'{"synthetic":true}\n',
        source_freeze_at='2026-11-03T14:00:00+09:00',qualified_source_originals=source_originals)
    if not strict_ready:
        assert out['selection_complete'] is False and out['computed_no_bet'] is False
        assert out['complete_tickets'] is None and out['postresult_method_exports']['methods']=={}
        assert not (Path(out['output_directory'])/'postresult').exists()
        return
    assert out['selection_complete'] is True and out['computed_no_bet'] is False
    assert set(out['complete_tickets'])==set(post.METHODS)
    assert '独立代替案' in Path(out['complete_private_body']['path']).read_text()
    for method,detail in out['postresult_method_exports']['methods'].items():
        descriptor=detail['frozen_original'];raw=Path(descriptor['path']).read_bytes()
        assert post.verify_exported_frozen(original_bytes=raw,sha256=descriptor['sha256'],
            candidate={},now=FREEZE) is True
    # Corrupting an original invalidates the actual completed-runtime linkage.
    (Path(out['output_directory'])/'csv_source_receipt_envelope.json').write_bytes(b'CHANGED')
    with pytest.raises(ValueError,match='ORIGINAL_BYTES_CHANGED'):
        post.verify_exported_frozen(original_bytes=raw,sha256=descriptor['sha256'],candidate={},now=FREEZE)
