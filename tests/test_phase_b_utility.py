import copy,json,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'runtime/local_physical'),str(ROOT/'research/utility')]
from run_program import capital_arms
from nar_auxiliary_evidence import build_same_day_bias
from pfs_grand_review import actual_purchase_records,_robustness
from krs_prediction_utility import evaluate_against_result

def final():
    return {'final_freeze_timestamp':'2026-10-01T00:00:00+00:00','final_ticket':{'tickets':[{'bet_type':'TRIFECTA','selection':[1,2,3],'stake':100,'mec_tier':'CORE'}, {'bet_type':'TRIO','selection':[1,2,4],'stake':100,'mec_tier':'TAIL'}]}}
def arms(f=None,**kw):
    return capital_arms(f or final(),kw.get('budget',200),request={'race_id':'FNB-20261001-R01','scheduled_post_at':'2026-10-01T02:00:00+00:00','runners':[{'runner_id':str(i)} for i in [1,2,3,4]]},generated_at=kw.get('now','2026-10-01T01:00:00+00:00'),scheduled_post_at='2026-10-01T02:00:00+00:00')
def test_capital_equal_spend_no_new_ticket_no_mutation():
    f=final();before=copy.deepcopy(f);a=arms(f)
    assert f==before and a['production_comparable_equal_spend']
    assert a['arms']['CONSERVATIVE']['tickets'][0]['stake']==200
    assert a['arms']['WIDE']['tickets']==f['final_ticket']['tickets']
    assert all(x['investment']==200 for x in a['arms'].values())
@pytest.mark.parametrize('change,error',[(lambda f:f['final_ticket']['tickets'].append(copy.deepcopy(f['final_ticket']['tickets'][0])),'DUPLICATE'),(lambda f:f['final_ticket']['tickets'][0].update(stake=101),'STAKE'),(lambda f:f['final_ticket']['tickets'][0].update(selection=[1,1,3]),'TICKET')])
def test_capital_invalid(change,error):
    f=final();change(f)
    with pytest.raises(ValueError,match=error):arms(f)
def test_capital_late_and_budget():
    with pytest.raises(ValueError,match='NOT_PRE_RACE'):arms(now='2026-10-01T02:00:00+00:00')
    with pytest.raises(ValueError,match='BUDGET'):arms(budget=150)
    assert arms(budget=300)['production_comparable_equal_spend'] is False

def test_corner_missing_is_not_rear():
    def table(present):
        header=['着順','馬番','馬名']+(['コーナー通過順'] if present else [])
        return [header]+[[str(i),str(i),'馬']+(['1-1' if i==1 else '4-4'] if present else []) for i in [1,2,3]]
    src={'normalized_evidence':{'same_day_r01_result_tables':{'value':[table(True)]},'same_day_r02_result_tables':{'value':[table(False)]}}}
    b=build_same_day_bias(src)['summary'] if 'summary' in build_same_day_bias(src) else build_same_day_bias(src)
    assert b['corner_observations']==3 and b['corner_missing_observations']==3
    assert b['leader_at_last_corner_win_rate']==1
    assert b['front_at_last_corner_top3_rate']==round(1/3,6)

def ledger():
    return {'race_id':'FNB-20261001-R01','purchase_verified':True,'ledger_complete':True,'verification_ref':'receipt-1','scheduled_post_at':'2026-10-01T02:00:00+00:00','purchases':[{'purchase_id':'p1','timestamp':'2026-10-01T01:00:00+00:00','success':True,'proof_ref':'receipt-1','ticket':{'bet_type':'EXACTA','selection':[1,2],'stake':100}}]}
def setup(tmp,monkeypatch,obj):
    monkeypatch.chdir(tmp);Path('runtime/actual_purchases').mkdir(parents=True);Path('runtime/results').mkdir()
    Path('runtime/actual_purchases/one.json').write_text(json.dumps(obj))
def test_actual_not_inferred_and_pending(tmp_path,monkeypatch):
    obj=ledger();setup(tmp_path,monkeypatch,obj)
    rows,held=actual_purchase_records();assert not rows and 'PENDING' in held[0]['reason']
    obj['purchase_verified']=False;Path('runtime/actual_purchases/one.json').write_text(json.dumps(obj))
    rows,held=actual_purchase_records();assert not rows and 'PROOF' in held[0]['reason']
def test_duplicate_purchase_ledger_all_excluded(tmp_path,monkeypatch):
    obj=ledger();setup(tmp_path,monkeypatch,obj)
    Path('runtime/actual_purchases/two.json').write_text(json.dumps(obj))
    rows,held=actual_purchase_records();assert not rows and len(held)==2 and all('DUPLICATE' in x['reason'] for x in held)
def test_actual_success_not_frozen_and_failed_not_stake(tmp_path,monkeypatch):
    obj=ledger();obj['purchases'].append({'purchase_id':'failed','timestamp':'2026-10-01T01:00:00+00:00','success':False})
    setup(tmp_path,monkeypatch,obj)
    Path('runtime/results/FNB-20261001-R01.json').write_text(json.dumps({'race_id':obj['race_id'],'official_result':{'top3':[1,2,3],'payouts_per_100_yen':{'EXACTA':500}},'settlement':{'status':'SETTLED'},'payouts_per_100_yen':{'EXACTA':500}}))
    rows,held=actual_purchase_records();assert not held and rows[0]['investment']==100 and rows[0]['return']==500 and rows[0]['failed_purchase_count']==1
    assert rows[0]['pfs_authority']=='ACTUAL-PFS'
def test_krs_harm_rescue_both_counted_no_capital_guess():
    u={'summary':[{'horse_no':1,'ranks':{'SSR-W':2},'static_roles':['W']},{'horse_no':2,'ranks':{'SSR-P2':1},'static_roles':[]},{'horse_no':3,'ranks':{'SSR-P3':1},'static_roles':['P3']}], 'snapshot':{'role_zones':{'W':1,'P2':1,'P3':1}}}
    e=evaluate_against_result(u,[1,2,3],static_ranking=[1,2,3])
    assert e['unique_harm_role_count']==1 and e['unique_rescue_role_count']==1
    assert e['added_capital'] is None and e['rank_comparison'][0]['rank_gain']==-1

def test_outlier_stress_keeps_costs():
    rows=[{'race_id':f'{i:02d}','investment':100,'return':r,'profit_loss':r-100,'hit_but_loss':False} for i,r in enumerate([0,0,1000])]
    x=_robustness(rows)
    assert x['excluding_largest_return']['investment_weighted_pfs']==0
    assert x['largest_return_zeroed_keep_stakes_pfs']==0 and x['max_drawdown']==200

def test_separate_corner_table_ties_and_no_result_backfill():
    src={'normalized_evidence':{'same_day_r01_result_tables':{'value':[[['着順','馬番','馬名'],['1','7','A'],['2','1','B'],['3','6','C']],[['３角','7-(1,6),2'],['４角','7-6,(1,2)']]]}}}
    b=build_same_day_bias(src)
    assert b['corner_observations']==3 and b['corner_missing_observations']==0
    assert b['front_at_last_corner_top3_rate']==round(2/3,6) # pack 1/2 occupies ranks3..4, cannot claim top3
    assert b['leader_at_last_corner_win_rate']==1
    assert b['races'][0]['top3'][1]['corner_rank_intervals'][-1]['rank_max']==4
