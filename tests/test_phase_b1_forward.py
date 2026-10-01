"""Mechanical acceptance only. No generated fixture enters a real OOS ledger."""
import copy,json,sys,subprocess
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
import local_candidate_postresult as f
from krs_prediction_utility import build_krs_prediction_utility
from pfs_grand_review import actual_purchase_records

def inputs(family='LOCAL',race='FNB-20261002-R01'):
    req={'family_id':family,'race_id':race,'execution_id':race+'-EXEC','temporal_mode':'FORMAL-PRE-RACE','scheduled_post_at':'2026-10-02T02:00:00+00:00','runners':[{'runner_id':str(i),'static_roles':['W','P2','P3']} for i in [1,2,3,4]],'static_prediction':{'ranking':['1','2','3','4']}}
    utility={'summary':[{'horse_no':i,'ranks':{'SSR-W':i,'SSR-P2':i,'SSR-P3':i},'static_roles':['W','P2','P3']} for i in [1,2,3,4]],'snapshot':{'role_zones':{'W':1,'P2':2,'P3':3}}}
    fin={'signature':'mechanical-signature-placeholder','receipt':{'race_id':race,'status':'PASS'},'artifact':{'source_snapshot_sha256':'source-test','final_freeze_timestamp':'2026-10-02T00:55:00+00:00','final_prediction_package':{'krs_prediction_utility_shadow':utility},'final_ticket':{'tickets':[{'bet_type':'TRIFECTA','selection':[1,2,3],'stake':100,'mec_tier':'CORE'},{'bet_type':'TRIO','selection':[1,2,4],'stake':100,'mec_tier':'TAIL'}]}}}
    return req,fin,utility

def capture(**kw):
    req,fin,u=inputs(**kw)
    return req,fin,f.build_forward_capture(req,fin,u,generated_at='2026-10-02T01:00:00+00:00',candidate={'race_source_snapshot_sha256':'source-test'},classification='MECHANICAL_ACCEPTANCE')

def result(req,payout=True):
    return {'race_id':req['race_id'],'official_result':{'top3':[1,2,3],'payouts_per_100_yen':{'TRIFECTA':500} if payout else {}}}, {'race_id':req['race_id'],'execution_id':req['execution_id'],'result_available_at':'2026-10-02T02:10:00+00:00','official_result_verified':True,'acceptance_only':True}

def signed_result(art):
    receipt={'race_id':art['race_id'],'phase':'RESULT','status':'PASS','artifact_sha256':f._sha(art)}
    return {'artifact':copy.deepcopy(art),'receipt':receipt,'receipt_sha256':f._sha(receipt),'signature':'MECHANICAL-TEST-SIGNATURE'}

def settle(pre,fin,art,request):
    request={**request,'official_result_verification_ref':'MECHANICAL_ACCEPTANCE_ONLY'}
    return f.settle_forward_capture(pre,fin,art,result_request=request,result_envelope=signed_result(art),result_verification={'verified':True})

def test_axes_are_independent():
    x=f.failure_axes(['NUMERICAL_AUTHORITY_NOT_READY'],{'first_material_failure':'EXACT','secondary_failures':['CAPITAL']})
    assert x['performance_first_material_failure']=='EXACT' and x['secondary_failures']==['CAPITAL']

def test_forward_binding_and_late_rejected():
    req,fin,u=inputs()
    with pytest.raises(ValueError,match='NOT_PRE_RESULT'):f.build_forward_capture(req,fin,u,generated_at=req['scheduled_post_at'],candidate={})
    with pytest.raises(ValueError,match='CANDIDATE_SOURCE'):f.build_forward_capture(req,fin,u,generated_at='2026-10-02T01:00:00+00:00',candidate={'race_source_snapshot_sha256':'wrong'})

def test_capture_immutable_and_fresh_process(tmp_path):
    req,fin,pre=capture();root=str(tmp_path/'ledger');f.persist_forward_capture(pre,root)
    result_art,rreq=result(req);settled=settle(pre,fin,result_art,rreq)
    assert settled['status']=='SETTLED' and not settled['eligible'] and not settled['krs_eligible']
    f.persist_forward_settlement(pre,settled,root)
    subprocess.run([sys.executable,'-c',f"import sys;sys.path.insert(0,{str(ROOT/'runtime')!r});from local_candidate_postresult import forward_status; assert forward_status({root!r})['families']['LOCAL']['captured_races']==1"],cwd=ROOT,check=True)
    _,_,second=capture(race='FNB-20261002-R02');f.persist_forward_capture(second,root)
    assert f.forward_status(root)['families']['LOCAL']['captured_races']==2
    changed=copy.deepcopy(pre);changed['generated_at']='2026-10-02T01:01:00+00:00';changed['sha256']=f._sha({k:v for k,v in changed.items() if k!='sha256'})
    with pytest.raises(ValueError,match='NO_REGENERATION'):f.persist_forward_capture(changed,root)

def test_missing_payout_holds_only_shadow(tmp_path):
    req,fin,pre=capture();before=copy.deepcopy(fin);art,rreq=result(req,False)
    x=settle(pre,fin,art,rreq)
    assert x['status'].startswith('HOLD') and fin==before and x['production_effect']=='NONE'

def test_family_cohorts_never_pool(tmp_path):
    root=str(tmp_path/'ledger')
    for family in ['JRA','LOCAL','BAN']:
        _,_,pre=capture(family=family,race=family+'-20990101-R01');f.persist_forward_capture(pre,root)
    status=f.forward_status(root)
    assert all(x['captured_races']==1 and x['krs_eligible_races']==0 for x in status['families'].values())

def test_actual_real_result_fixture_mechanical(tmp_path,monkeypatch):
    # Real archived race/result; fixture purchase is schema acceptance, NEVER proof of purchase.
    official=json.loads((ROOT/'runtime/results/20260922-NKY-R11.json').read_text())
    rid=official['race_id'];monkeypatch.chdir(tmp_path)
    Path('runtime/results').mkdir(parents=True);Path('runtime/actual_purchases').mkdir()
    Path('runtime/results/'+rid+'.json').write_text(json.dumps(official))
    ledger={'race_id':rid,'purchase_verified':True,'ledger_complete':True,'verification_ref':'MECHANICAL_ACCEPTANCE_NOT_REAL_PURCHASE','scheduled_post_at':'2026-09-22T15:30:00+09:00','purchases':[{'purchase_id':'test-only','timestamp':'2026-09-22T15:00:00+09:00','success':True,'proof_ref':'MECHANICAL_ACCEPTANCE_NOT_REAL_PURCHASE','ticket':{'bet_type':'EXACTA','selection':[14,3],'stake':100},'refund':0}]}
    Path('runtime/actual_purchases/fixture.json').write_text(json.dumps(ledger))
    rows,held=actual_purchase_records();assert not held and rows[0]['return']==12080
    Path('runtime/actual_purchases/fixture.json').unlink()
    assert actual_purchase_records()==([],[])

def test_lifecycle_hooks_after_verify_and_existing_storage():
    runner=(ROOT/'runtime/non_jra_formal_runner.py').read_text();res=(ROOT/'runtime/local_result_from_signed_final.py').read_text()
    assert runner.index('final_sha=verify_envelope(fin,"FINAL")')<runner.index('forward=build_forward_capture')
    assert 'local_forward_measurement_pre_result.json' in res and 'runtime_result_in' in res
    assert 'persist_forward_settlement' in res

def test_forward_eligibility_and_family_counts_in_isolated_test_ledger(tmp_path):
    # Deliberately exercise FORWARD eligibility mechanically in pytest temp storage only.
    root=str(tmp_path/'ledger')
    for family in ['JRA','LOCAL']:
        req,fin,u=inputs(family=family,race=family+'-20990101-R01')
        pre=f.build_forward_capture(req,fin,u,generated_at='2026-10-02T01:00:00+00:00',candidate={'race_source_snapshot_sha256':'source-test'})
        art,rreq=result(req);rreq['acceptance_only']=False
        measurement=settle(pre,fin,art,rreq)
        assert measurement['eligible'] and measurement['krs_eligible']
        assert measurement['krs_incremental_utility']['production_harm'] is False
        f.persist_forward_capture(pre,root);f.persist_forward_settlement(pre,measurement,root)
    status=f.forward_status(root)
    assert status['families']['LOCAL']['eligible_races']==1 and status['families']['JRA']['eligible_races']==1
    assert status['families']['BAN']['eligible_races']==0

def test_actual_optional_reader_consumes_current_verified_result(tmp_path,monkeypatch):
    official=json.loads((ROOT/'runtime/results/20260922-NKY-R11.json').read_text());rid=official['race_id']
    monkeypatch.chdir(tmp_path);Path('runtime/actual_purchases').mkdir(parents=True)
    ledger={'race_id':rid,'purchase_verified':True,'ledger_complete':True,'verification_ref':'MECHANICAL-NOT-REAL-PURCHASE','scheduled_post_at':'2026-09-22T15:30:00+09:00','purchases':[{'purchase_id':'test-only','timestamp':'2026-09-22T15:00:00+09:00','success':True,'proof_ref':'TEST','ticket':{'bet_type':'EXACTA','selection':[14,3],'stake':100}}]}
    Path('runtime/actual_purchases/test.json').write_text(json.dumps(ledger))
    rows,held=actual_purchase_records(result_overrides={rid:official})
    assert len(rows)==1 and not held and rows[0]['return']==12080
