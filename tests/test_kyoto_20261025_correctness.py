"""Operational/financial regressions, not outcome-fitted prediction rules."""
import copy
import datetime as dt
import json
from pathlib import Path
import sys

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'runtime/jra_source_runtime')]
from formal_request_validator import ticket_capital_metrics,FormalValidationError
from formal_temporal_audit import build_temporal_audit
from jra_race_day_autopilot import write_status,reconcile_source_run_status
from post_result_learning import build_post_result_review,build_learning_state


def test_kyoto6_final_exposure_is_600_and_100_percent_on_11_to_1():
    tickets=[{'bet_type':'EXACTA','selection':[11,1],'stake':100}]+[
        {'bet_type':'TRIFECTA','selection':[11,1,t],'stake':100} for t in (12,5,6,4,9)]
    metrics=ticket_capital_metrics(tickets)
    assert metrics['total_investment']==600
    assert metrics['head_stake']=={'11':600} and metrics['pair_stake']=={'11>1':600}
    assert metrics['head_capital_concentration']==metrics['pair_capital_concentration']==1
    assert metrics['bet_type_stake']=={'EXACTA':100,'TRIFECTA':500}
    # Replacing preflight metrics must not mutate the selected tickets.
    before=copy.deepcopy(tickets);ticket_capital_metrics(tickets);assert tickets==before


def test_trio_exposure_is_not_invented_as_an_ordered_head():
    metrics=ticket_capital_metrics([
        {'bet_type':'EXACTA','selection':[3,2],'stake':100},
        {'bet_type':'TRIO','selection':[2,3,5],'stake':100}])
    assert metrics['head_capital_concentration']==.5 and metrics['total_investment']==200
    assert ticket_capital_metrics([])['total_investment']==0
    for stake in (True,0,-100,50):
        with pytest.raises(FormalValidationError):
            ticket_capital_metrics([{'bet_type':'EXACTA','selection':[1,2],'stake':stake}])


def source_case(tmp_path):
    rid='KM-JRA-KYO-20261025-R03';execution=rid+'-LIVE-R1'
    for directory,body in [('jra_formal_intents',{}),('jra_source_requests',{
            'family_id':'JRA','race_id':rid,'execution_id':execution,
            'prediction_cutoff':'2026-10-25T10:55:00+09:00'})]:
        path=tmp_path/'runtime'/directory/(execution+'.json')
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(body))
    run={'databaseId':40149439237,'attempt':1,'status':'completed','conclusion':'failure',
         'displayTitle':'JRA SOURCE runtime/jra_source_requests/'+execution+'.json',
         'headSha':'5d43535f22151ed9c5dad76da90ca74855ee998a'}
    return rid,execution,run


def test_real_source_failure_cannot_stay_running_or_become_zero_percent_pfs(tmp_path):
    rid,_,run=source_case(tmp_path)
    for hour,minute,eligible in [(10,11,True),(11,11,False)]:
        value=write_status(tmp_path,'2026-10-25',dt.datetime.fromisoformat(
            f'2026-10-25T{hour:02}:{minute:02}:00+09:00'),
            {rid:{'post':'2026-10-25T11:00:00+09:00'}},{},
            formal_runs=[],resolver_runs=[],source_runs=[run])['races'][0]
        assert value['state']=='SOURCE_FAILED'
        assert value['source_run_id']=='40149439237'
        assert value['temporal_eligibility'] is eligible
        assert value['recommendation_pfs'] is None
        assert value['detailed_failure_stage_verified'] is False
    assert not (tmp_path/'runtime/final_artifacts').exists()


def test_source_reconciliation_never_overrides_newer_attempt_or_final(tmp_path):
    rid,execution,run=source_case(tmp_path);now=dt.datetime.fromisoformat('2026-10-25T10:11:00+09:00')
    for changes in ({'attempt':2,'status':'in_progress','conclusion':None},
                    {'databaseId':40149439238,'status':'queued','conclusion':None}):
        row={'race_id':rid,'state':'DISPATCHED_RUNNING'}
        reconcile_source_run_status(tmp_path,row,[run,{**run,**changes}],now)
        assert row['state']=='DISPATCHED_RUNNING'
    for state in ('FINAL','AKI_NO_BET','SETTLED_SIGNED_RESULT_LEARNED'):
        row={'race_id':rid,'state':state};reconcile_source_run_status(tmp_path,row,[run],now)
        assert row['state']==state
    path=tmp_path/'runtime/jra_formal_intents'/(execution.replace('R1','R2')+'.json')
    path.write_text('{}')
    row={'race_id':rid,'state':'DISPATCHED_RUNNING'}
    reconcile_source_run_status(tmp_path,row,[run],now)
    assert row['state']=='DISPATCHED_RUNNING'


@pytest.mark.parametrize('title',[
    'JRA SOURCE runtime/jra_source_requests/KM-JRA-TKY-20261025-R03-LIVE-R1.json',
    'JRA SOURCE runtime/jra_source_requests/../jra_formal_intents/KM-JRA-KYO-20261025-R03-LIVE-R1.json',
    'JRA SOURCE arbitrary.json'])
def test_unrelated_or_unresolved_run_identity_is_not_a_failure(tmp_path,title):
    rid,_,run=source_case(tmp_path);row={'race_id':rid,'state':'DISPATCHED_RUNNING'}
    reconcile_source_run_status(tmp_path,row,[{**run,'displayTitle':title}],
        dt.datetime.fromisoformat('2026-10-25T10:11:00+09:00'))
    assert row['state']=='DISPATCHED_RUNNING'


def test_actual_clock_order_does_not_misread_declared_cutoff_as_computation():
    q={'static_computed_at':'2026-10-25T13:40:14.449934+09:00',
       'prediction_cutoff':'2026-10-25T14:20:00+09:00',
       'static_freeze_timestamp':'2026-10-25T14:20:00+09:00',
       'scheduled_post_at':'2026-10-25T14:25:00+09:00'}
    audit=build_temporal_audit(q,{'source_freeze_at':'2026-10-25T13:37:42+09:00'},
                               '2026-10-25T13:44:22.309108+09:00')
    assert audit['clock_consistency']=='PASS'
    assert audit['legacy_static_freeze_timestamp_semantics']=='DECLARED_CUTOFF_BOUNDARY_NOT_COMPUTATION_TIME'
    assert not audit['forward_oos_eligibility_granted'] and not audit['independent_persistence_verified']
    q['static_computed_at']='2026-10-25T14:30:00+09:00'
    assert build_temporal_audit(q,None,'2026-10-25T13:44:22+09:00')['clock_consistency']=='FAIL'


def review_case(paper=False,exact_required=False):
    tickets=[] if paper else [{'bet_type':'EXACTA','selection':[3,2],'stake':100},
                             {'bet_type':'TRIO','selection':[2,3,5],'stake':100}]
    f={'race_id':'FIXTURE','final_receipt_sha256':'receipt',
       'capital_policy_decision':{'decision':'PAPER' if paper else 'EXECUTE_FULL_MEC'},
       'final_ticket':{'tickets':tickets,'no_bet':paper,'total_investment':0 if paper else 200},
       'final_prediction_package':{'roles':{'3':['W'],'2':['P2'],'5':['P3']}},
       'minimum_efficient_coverage':{'coverage_units':[
           {'id':'ORDERED_PAIR:3>2'},{'id':'TAIL_SET:2>3>5'}]+(
           [{'id':'EXACT_THIRD:3>2>5'}] if exact_required else [])}}
    r={'race_id':'FIXTURE','official_result':{'top3':[3,2,5]},
       'settlement':{'total_investment':0 if paper else 200,'total_payout':0 if paper else 1510}}
    return r,f


def test_paper_keeps_prediction_quality_separate_from_ticket_conversion():
    r,f=review_case(paper=True);before=copy.deepcopy((r,f))
    legacy=build_post_result_review(r,f)
    assert legacy['failure_localization']['first_material_failure']=='ORDERED_PAIR_CONVERSION'
    v2=build_post_result_review(r,f,review_semantics='DECISION_AWARE_V2')
    assert v2['failure_localization']['first_material_failure']=='NONE'
    assert v2['capital']['pfs'] is None and v2['capital']['status']=='NOT_APPLICABLE_PAPER'
    assert v2['conversion']['status']=='NOT_APPLICABLE_PAPER'
    assert v2['pfs_improvement']['dominant_pfs_loss_owner']['applicability']=='NOT_APPLICABLE_ZERO_EXPOSURE'
    assert 'ORDERED_PAIR_CONVERSION' not in build_learning_state(v2)['shadow_candidates']
    f['final_prediction_package']['roles']['3']=[]
    failed=build_post_result_review(r,f,review_semantics='DECISION_AWARE_V2')
    assert failed['failure_localization']['first_material_failure']=='PREDICTION_ROLE_W'
    assert failed['pfs_improvement']['dominant_pfs_loss_owner']['applicability']=='NOT_APPLICABLE_ZERO_EXPOSURE'
    f['final_prediction_package']['roles']['3']=['W'];assert (r,f)==before
    assert build_post_result_review(r,f)==legacy


def test_kyoto7_profitable_protection_keeps_unrequired_exact_as_residual():
    r,f=review_case()
    v2=build_post_result_review(r,f,review_semantics='DECISION_AWARE_V2')
    assert v2['failure_localization']['first_material_failure']=='NONE'
    assert v2['failure_localization']['residual_diagnostics']==['EXACT_ORIENTATION_NOT_CAPTURED']
    assert v2['capital']['pfs']==755
    r,f=review_case(exact_required=True)
    assert build_post_result_review(r,f,review_semantics='DECISION_AWARE_V2')[
        'failure_localization']['first_material_failure']=='EXACT_ORIENTATION'


def test_all_nine_actual_kyoto_finals_keep_bytes_roles_and_finance():
    sys.path.insert(0,str(ROOT/'scripts'))
    from audit_kyoto_20261025_correctness import audit
    report=audit(ROOT)
    assert report['race_count']==9 and report['runner_count']==117
    assert report['role_cells_replayed']==351 and report['actual_investment']==8100
    assert all(r['temporal_audit']['clock_consistency']=='PASS' for r in report['races'])
    indexed={int(r['race_id'][-2:]):r for r in report['races']}
    assert indexed[4]['candidate_first_material_failure']=='PREDICTION_ROLE_W'
    assert indexed[5]['candidate_first_material_failure']=='NONE' and indexed[5]['pfs'] is None
    assert indexed[6]['actual_capital']['head_stake']=={'11':600}
    assert indexed[7]['candidate_first_material_failure']=='NONE'
    assert indexed[8]['candidate_first_material_failure']=='NONE'
    assert report['historical_signed_records_rewritten']==report['forward_oos_increment']==0
