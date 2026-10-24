from copy import deepcopy
import inspect
from pathlib import Path
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from research.jra_20261024_capital.comparison import (
    digest, ranked_tickets, matched_exposure, concentration, cash_metrics,
    evaluate_portfolio)


def inputs():
    q={'race_id':'KM-JRA-TKY-20261024-R01','source_snapshot_sha256':'a'*64,
       'prediction_cutoff':'2026-10-24T10:00:00+09:00',
       'runners':[{'runner_id':str(h)} for h in range(1,5)]}
    f={**{k:q[k] for k in ('race_id','source_snapshot_sha256','prediction_cutoff')},
       'static_prediction':{'ranking':['1','2','3','4']},
       'final_ticket':{'tickets':[
           {'bet_type':'EXACTA','selection':[1,2],'stake':200},
           {'bet_type':'EXACTA','selection':[1,3],'stake':100},
           {'bet_type':'TRIO','selection':[1,2,3],'stake':100},
           {'bet_type':'TRIFECTA','selection':[1,2,3],'stake':100}],
           'total_investment':500}}
    f['sha256']=digest(f)
    return q,f


def test_result_blind_matched_budget_types_stakes_and_input_immutable():
    q,f=inputs();old=deepcopy((q,f));rr={r:['4','3','2','1'] for r in ('W','P2','P3')}
    candidates=ranked_tickets(rr)
    out=matched_exposure(f,q,candidates,candidate_id='SYNTHETIC_TEST_ONLY')
    assert out['investment']==500 and out['ticket_count']==4
    assert out['same_bet_type_counts'] and out['same_bet_type_stake_multisets']
    assert (q,f)==old
    assert not {'result','official','finish','payouts'} & set(inspect.signature(matched_exposure).parameters)
    with pytest.raises(TypeError):matched_exposure(f,q,candidates,candidate_id='SYNTHETIC_TEST_ONLY',official={'top3':[4,3,2]})


def test_partial_candidate_pool_falls_back_to_frozen_tickets():
    q,f=inputs()
    out=matched_exposure(f,q,[{'bet_type':'EXACTA','selection':[4,3],'priority_score':1}],candidate_id='TEST')
    assert out['investment']==500 and out['ticket_count']==4
    assert {'bet_type':'EXACTA','selection':[4,3],'stake':200} in out['tickets']
    assert out['same_bet_type_stake_multisets']


@pytest.mark.parametrize('ticket',[
    {'bet_type':'EXACTA','selection':[1,5]},
    {'bet_type':'EXACTA','selection':[1,1]},
    {'bet_type':'WIN','selection':[1]},
    {'bet_type':'TRIFECTA','selection':[1,2]},
    {'bet_type':'EXACTA','selection':[1,2],'priority_score':float('nan')},
])
def test_invalid_candidate_fails_closed(ticket):
    q,f=inputs()
    with pytest.raises(ValueError):matched_exposure(f,q,[ticket],candidate_id='TEST')


def test_source_crossover_and_final_tampering_rejected():
    q,f=inputs()
    with pytest.raises(ValueError):matched_exposure(f,q,[],candidate_id='TEST',metadata={'source_sha256':'b'*64})
    f['final_ticket']['total_investment']=100
    with pytest.raises(ValueError):matched_exposure(f,q,[],candidate_id='TEST')


@pytest.mark.parametrize('metadata',[
    {'prediction_cutoff':'2026-10-24T11:00:00+09:00'},
    {'feature_input_sha256':'f'*64},
    {'runner_universe_sha256':'e'*64},
])
def test_candidate_cutoff_feature_and_universe_bindings_fail_closed(metadata):
    q,f=inputs()
    with pytest.raises(ValueError):matched_exposure(f,q,[],candidate_id='TEST',metadata=metadata)


def test_candidate_lineage_is_preserved_without_modifying_original_freeze():
    q,f=inputs();meta={'prediction_cutoff':q['prediction_cutoff'],
        'feature_input_sha256':digest(q['runners']),'model_sha256':'m'*64,
        'code_sha256':'c'*64,'policy_sha256':'p'*64}
    out=matched_exposure(f,q,[],candidate_id='TEST',metadata=meta)
    assert out['candidate_metadata']==meta
    assert out['feature_input_sha256']==meta['feature_input_sha256']
    meta['model_sha256']='different'
    assert out['candidate_metadata']['model_sha256']=='m'*64


def test_paper_cannot_gain_research_capital_from_candidates():
    q,f=inputs();f['final_ticket']={'tickets':[],'total_investment':0};f.pop('sha256');f['sha256']=digest(f)
    out=matched_exposure(f,q,[{'bet_type':'EXACTA','selection':[4,3],'stake':100}],candidate_id='TEST')
    assert out['tickets']==[] and out['investment']==0


def test_type_mix_is_explicit_but_budget_and_total_count_stay_exact():
    q,f=inputs();rr={r:['4','3','2','1'] for r in ('W','P2','P3')}
    out=matched_exposure(f,q,ranked_tickets(rr),candidate_id='TEST',bet_type_mix=True)
    assert out['same_budget'] and out['same_total_point_count']
    assert sorted(t['stake'] for t in out['tickets'])==[100,100,100,200]
    assert out['permitted_bet_types_unchanged']


def test_cash_metrics_refund_zero_exposure_and_robust_tail():
    rows=[{'race_id':'A','post_at':'2026-10-24T10:00:00+09:00','investment':1500,'refund':1200,'effective_investment':300,'return':2000},
          {'race_id':'B','post_at':'2026-10-24T11:00:00+09:00','investment':400,'refund':0,'effective_investment':400,'return':0},
          {'race_id':'C','post_at':'2026-10-24T12:00:00+09:00','investment':0,'refund':0,'effective_investment':0,'return':0}]
    m=cash_metrics(rows)
    assert m['pfs']==pytest.approx(2000/700*100)
    assert m['profit_loss']==1300 and m['maximum_drawdown']==400
    assert m['zero_exposure_races']==1
    assert m['largest_returns_excluded']['1']['pfs']==0
    assert cash_metrics(rows[2:])['pfs'] is None


def test_concentration_trio_does_not_invent_an_ordered_head():
    q,f=inputs();c=concentration(f['final_ticket']['tickets'])
    assert c['investment']==500 and c['ordered_investment']==400
    assert c['max_head_share_of_ordered']==1


def test_replacement_harm_and_false_positive_cost_are_measured():
    q,f=inputs();rr={r:['4','3','2','1'] for r in ('W','P2','P3')}
    p=matched_exposure(f,q,ranked_tickets(rr),candidate_id='TEST')
    def synthetic_settle(final,official):
        ts=final['final_ticket']['tickets'];winning=[t for t in ts if t['bet_type']=='EXACTA' and t['selection']==[1,2]]
        pay=sum(t['stake']*3 for t in winning);inv=sum(t['stake'] for t in ts)
        return {'total_investment':inv,'total_payout':pay,'profit_loss':pay-inv,'pfs':100*pay/inv if inv else None,'winning_tickets':winning}
    e=evaluate_portfolio(f,p,{},settlement_fn=synthetic_settle)
    assert e['unique_ticket_harm'] and not e['unique_ticket_rescue']
    assert e['removed_return']==600 and e['false_positive_redeployed_stake']>0


def test_refunded_added_tickets_are_not_false_positive_losing_cost():
    q,f=inputs();p={'tickets':[{'bet_type':'EXACTA','selection':[4,3],'stake':500}]}
    def synthetic_settle(final,official):
        ts=final['final_ticket']['tickets'];inv=sum(t['stake'] for t in ts)
        refund=sum(t['stake'] for t in ts if 4 in t['selection'])
        return {'total_investment':inv,'total_payout':0,'refund':refund,
            'profit_loss':refund-inv,'winning_tickets':[]}
    e=evaluate_portfolio(f,p,{},settlement_fn=synthetic_settle)
    assert e['false_positive_redeployed_stake']==0
