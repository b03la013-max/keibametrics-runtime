"""Synthetic official-layout witnesses and strict refund settlement."""
import copy
import hashlib

import pytest

from runtime import urw_nankan_reference_source as n
from scripts.urw_paper_selection_replay import settle_observed_ticket_list as settle_ticket_list
from scripts.urw_paper_selection_replay import _portfolio_effect, _summary


def case(status='競走除外',note='返還:4号馬'):
    race={'provider':'NANKAN_OFFICIAL','venue_id':'URW','race_no':1,'race_date':'2026-10-19',
          'provider_race_id':'2026101918070101','distance':1400,'program_runner_count':4,
          'scheduled_post_at':'2026-10-19T12:20:00+09:00'}
    facts=[{'runner_id':str(i),'name':f'自作{i}'} for i in range(1,5)]
    rows=''.join(f'<tr><td>{i}</td><td>{i}</td><td>{i}</td><td>自作{i}</td></tr>' for i in range(1,4))
    rows+=f'<tr><td>-</td><td>4</td><td>4</td><td>自作4</td><td>{status}</td></tr>'
    payout=''.join(f'<tr><th>{bt}</th><td>{sel}</td><td>{pay}</td><td>1</td></tr>'
                   for bt,sel,pay in [('馬単','1-2','500'),('三連複','1-2-3','900'),('三連単','1-2-3','2,200')])
    raw=(f'<meta charset="utf-8"><p class="nk23_c-tab1__subtitle">1R 2026年10月19日 浦和競馬 ダ1,400m (3頭) 発走時刻12:20</p>'
         '<table><tr><th>着</th><th>枠</th><th>馬番</th><th>馬名</th></tr>'+rows+'</table>'
         '<table><tr><th></th><th>組番</th><th>金額</th><th>人気</th></tr>'+payout+
         f'<tr><th>備考</th><td colspan="3">{note}</td></tr></table>').encode()
    return race,facts,raw


def parse(race,facts,raw):
    receipt={'url':n.ORIGIN+'/result/'+race['provider_race_id']+'.do','http_status':200,
             'fetched_at':'2026-10-19T04:00:00+00:00','raw_sha256':hashlib.sha256(raw).hexdigest()}
    return n.parse_result(raw,race,facts,receipt,race_id='KM-LOCAL-URW-20261019-R01-TEST')


def test_complete_witness_preserves_explicit_refund_and_private_boundary():
    result=parse(*case())
    assert result['official_result']['refunded_runner_ids']==['4']
    assert result['private_storage_required']
    assert result['public_redistribution_authorized'] is False
    assert result['active_verified'] is False
    assert result['official_result']['payouts']['TRIFECTA']==2200


@pytest.mark.parametrize('change',['count','venue','provider','name','refund_note','missing_payout','numeric_cancel'])
def test_incomplete_or_contradictory_witness_holds(change):
    race,facts,raw=case()
    if change=='count':race['program_runner_count']=5
    if change=='venue':race['venue_id']='KAW'
    if change=='provider':race['provider']='NAR_OFFICIAL'
    if change=='name':facts[0]['name']='別馬'
    if change=='refund_note':raw=raw.replace('返還:4号馬'.encode(),'未知の返還'.encode())
    if change=='missing_payout':raw=raw.replace(b'<td>500</td>',b'<td>-</td>')
    if change=='numeric_cancel':raw=raw.replace('<td>自作1</td>'.encode(),'<td>自作1</td><td>出走取消</td>'.encode())
    with pytest.raises(n.NankanError):parse(race,facts,raw)


def test_dnf_does_not_infer_a_refund_and_nonfinish_unknown_holds():
    result=parse(*case(status='競走中止',note=''))
    assert result['official_result']['refunded_runner_ids']==[]
    with pytest.raises(n.NankanError):parse(*case(status='UNKNOWN',note=''))


def test_refund_is_separate_from_hit_and_missing_payout_is_never_zero():
    result=parse(*case())
    tickets=[{'bet_type':'EXACTA','selection':[1,2],'stake':100},
             {'bet_type':'EXACTA','selection':[1,4],'stake':100}]
    settled=settle_ticket_list(tickets,result,require_resolved_refunds=True)
    assert settled['return']==600 and settled['winnings']==500 and settled['refund']==100
    assert settled['by_bet_type']['EXACTA']['refunded_ticket_count']==1
    for payout in (None,0,-100,float('nan')):
        missing=copy.deepcopy(result);missing['official_result']['payouts']['EXACTA']=payout
        assert settle_ticket_list(tickets,missing,require_resolved_refunds=True)['return'] is None


def test_partial_refund_metadata_or_strict_missing_refund_is_hold():
    ts=[{'bet_type':'EXACTA','selection':[1,4],'stake':100}]
    for official in ({'top3':[1,2,3]}, {'top3':[1,2,3],'refunded_runner_ids':[4]},
                     {'top3':[1,2,3],'refund_status':'UNRESOLVED'}):
        out=settle_ticket_list(ts,{'official_result':official},require_resolved_refunds=True)
        assert out['status']=='HOLD_REFUND_UNRESOLVED' and out['return'] is None
    partial={'official_result':{'top3':[1,2,3],'refunded_runner_ids':[4]}}
    assert settle_ticket_list(ts,partial)['return'] is None


def test_multiple_refunded_runners_refund_each_ticket_once_with_original_stakes():
    result=parse(*case())
    result['official_result']['refunded_runner_ids']=['4','5']  # Authored multi-refund settlement case.
    tickets=[{'bet_type':'EXACTA','selection':[1,4],'stake':300},
             {'bet_type':'TRIO','selection':[5,1,4],'stake':200},
             {'bet_type':'EXACTA','selection':[1,2],'stake':200},
             {'bet_type':'TRIO','selection':[3,1,2],'stake':300},
             {'bet_type':'TRIFECTA','selection':[1,2,3],'stake':100}]
    before=copy.deepcopy(tickets)
    value=settle_ticket_list(tickets,result)
    assert tickets==before
    assert value['investment']==1100 and value['refund']==500
    assert value['winnings']==5900 and value['return']==6400
    assert value['profit_loss']==5300
    assert value['by_bet_type']['TRIO']['refunded_ticket_count']==1
    assert value['by_bet_type']['TRIO']['winnings']==2700
    with pytest.raises(ValueError,match='DUPLICATE_TICKET'):
        settle_ticket_list([{'bet_type':'TRIO','selection':[1,2,3],'stake':100},
                            {'bet_type':'TRIO','selection':[3,2,1],'stake':200}],result)


def test_same_result_can_pay_exacta_and_trio_despite_shared_scenario_coverage():
    value=settle_ticket_list([{'bet_type':'EXACTA','selection':[1,2],'stake':100},
                              {'bet_type':'TRIO','selection':[3,1,2],'stake':100}],parse(*case()))
    assert value['winnings']==500+900
    assert set(value['hit_types'])=={'EXACTA','TRIO'}


def test_selection_effect_separates_no_bet_release_refund_and_hit():
    result=parse(*case())
    value=_portfolio_effect([], [{'bet_type':'EXACTA','selection':[1,4],'stake':300}],result)
    assert value['no_bet_released'] and value['reference_no_bet']
    assert value['delta']=={'investment':300,'winnings':0,'refund':300,'return':300,'profit_loss':0}
    assert not value['candidate']['hit_types']
    assert value['added_finance']['by_bet_type']['EXACTA']['refunded_ticket_count']==1
    assert not value['causal_or_future_performance_claim']
    no_bet=settle_ticket_list([],result)
    assert no_bet['investment']==0 and no_bet['pfs'] is None


def test_missing_result_never_changes_known_selection_participation():
    one={'status':'SETTLED','investment':100,'return':500,'refund':0,'profit_loss':400}
    value=_summary([one],3,planned_race_investments=[100,0,300])
    assert value['investment']==400
    assert value['participating_races']==2 and value['participation_rate']==pytest.approx(2/3)
    assert value['return'] is None and value['final_research_balance'] is None
    assert value['maximum_drawdown_yen'] is None and value['balance_after_each_race_yen'] is None
    assert _summary([one],3)['participating_races'] is None
    with pytest.raises(ValueError,match='INVESTMENT_UNIVERSE'):
        _summary([one],3,planned_race_investments=[100])
    with pytest.raises(ValueError,match='INVESTMENT_TOTAL'):
        _summary([one],1,planned_race_investments=[100],planned_investment=200)


@pytest.mark.parametrize('side',['reference','candidate'])
def test_portfolio_comparison_cannot_drop_duplicate_stakes(side):
    duplicate=[{'bet_type':'EXACTA','selection':[1,2],'stake':100},
               {'bet_type':'EXACTA','selection':[1,2],'stake':200}]
    args={'reference':[],'candidate':[],'result':parse(*case())};args[side]=duplicate
    with pytest.raises(ValueError,match='DUPLICATE_TICKET'):_portfolio_effect(**args)


def test_complete_settlement_requires_same_planned_race_stakes():
    one={'status':'SETTLED','investment':100,'return':500,'refund':0,'profit_loss':400}
    with pytest.raises(ValueError,match='SETTLEMENT_PLANNED_STAKE_MISMATCH'):
        _summary([one],1,planned_race_investments=[200])
    other={**one,'investment':200,'profit_loss':300}
    with pytest.raises(ValueError,match='SETTLEMENT_PLANNED_STAKE_MISMATCH'):
        _summary([one,other],2,planned_race_investments=[200,100])
    value=_summary([one,other],2,planned_race_investments=[100,200])
    assert value['final_research_balance']==150000+value['profit_loss']
