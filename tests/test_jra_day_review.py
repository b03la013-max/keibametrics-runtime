import copy
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'runtime')]
from jra_full_day_postrace_review import parse_official, settle_tickets, robust, metric, prediction
from jra_krs_utility_measurement import build_krs_prediction_utility, evaluate_against_result
from krs_prediction_utility import evaluate_against_result as evaluate_common_utility
import pytest

EVIDENCE=ROOT/'evidence/jra_day_review_20261017'
if not (EVIDENCE/'official/042026040101.html').exists():
    from unpack_jra_day_review import unpack
    unpack()

def official(key,venue,race):
    return parse_official((EVIDENCE/'official'/f'{key}.html').read_text(),'2026-10-17',venue,race)

def test_all_36_official_identities_and_seven_payout_types():
    inventory=json.loads((EVIDENCE/'official/collection.json').read_text())
    assert len(inventory['races'])==36
    for rec in inventory['races']:
        key=rec['race_key'];venue={'04':'NGT','05':'TKY','08':'KYO'}[key[:2]]
        obj=official(key,venue,int(key[-2:]))
        assert len(obj['top3'])==3
        assert len(obj['payouts'])>=7

def test_wrong_race_is_rejected():
    with pytest.raises(ValueError,match='RACE_NUMBER'):official('082026040611','KYO',12)

def test_actual_frozen_kyo11_ticket_recalculation():
    final=json.loads((ROOT/'runtime/final_artifacts/KM-JRA-KYO-20261017-R11.json').read_text())
    result=settle_tickets(final['final_ticket']['tickets'],official('082026040611','KYO',11))
    assert (result['investment'],result['return'],result['profit_loss'])==(2900,9100,6200)
    assert [t['bet_type'] for t in result['tickets'] if t['hit']]==['TRIO']

def test_dnf_is_not_a_scratch_refund():
    obj=official('042026040108','NGT',8)
    assert any(r['finish_status']=='中止' for r in obj['exceptional_runners'])
    result=settle_tickets([{'bet_type':'WIN','selection':[16],'stake':100}],obj)
    assert result['return']==0

def test_duplicate_and_invalid_stake_fail_closed():
    obj=official('082026040611','KYO',11)
    ticket={'bet_type':'TRIO','selection':[10,5,9],'stake':100}
    with pytest.raises(ValueError,match='DUPLICATE_CANONICAL'):settle_tickets([ticket,{**ticket,'selection':[5,9,10]}],obj)
    with pytest.raises(ValueError,match='INVALID_STAKE'):settle_tickets([{**ticket,'stake':150}],obj)

def test_paper_is_null_and_missing_predictions_do_not_enter_accuracy():
    assert settle_tickets([],official('082026040611','KYO',11))['pfs'] is None
    assert metric([True,None,False,'NOT EXECUTED'])=={'numerator':1,'denominator':2,'rate':.5}

def test_whole_race_exclusion_keeps_denominator_consistent():
    rows=[{'race_id':'a','post':'1','investment':100,'return':1000},
          {'race_id':'b','post':'2','investment':300,'return':0}]
    result=robust(rows)
    assert result['weighted_pfs']==250
    assert result['largest_returns_excluded']['1']['investment']==300
    assert result['largest_returns_excluded']['1']['weighted_pfs']==0

def test_multiple_official_dead_heat_payouts_match_exact_ticket():
    obj={'exceptional_runners':[],'special_refund_detected':False,
         'payouts':{'EXACTA':[{'selection':[1,2],'per_100_yen':900},{'selection':[2,1],'per_100_yen':700}]}}
    assert settle_tickets([{'bet_type':'EXACTA','selection':[2,1],'stake':200}],obj)['return']==1400

def test_actual_krs_summary_static_binding_and_legacy_measurement():
    rid='KM-JRA-KYO-20261017-R11'
    final=json.loads((ROOT/'runtime/final_artifacts'/f'{rid}.json').read_text())
    req=json.loads((ROOT/'runtime/requests'/f'{rid}-LIVE-R1-FORMAL.json').read_text())
    raw=json.loads((EVIDENCE/'krs_checkpoints/39007251004'/rid/'krs_response.json').read_text())
    rebuilt=build_krs_prediction_utility(req,raw)
    assert next(r for r in rebuilt['summary'] if r['horse_no']==5)['static_roles']==['P2','P3','W']
    # Both 5 in P2 and 9 in P3 already existed. Empty legacy summary roles
    # must not convert those two confirmations into unique rescues.
    ev=evaluate_against_result(final['krs_prediction_utility'],[10,5,9],
        static_ranking=final['static_prediction']['ranking'],static_roles=final['static_prediction']['roles'])
    assert ev['unique_rescue_role_count']==0
    assert ev['rank_comparison'][1]['static_role_hit'] is True

def test_p3_uses_same_metric_as_frozen_proposal_selection():
    utility={'summary':[{'horse_no':1,'ranks':{'SSR-W':1}},
        {'horse_no':2,'ranks':{'SSR-P2':1}},
        {'horse_no':3,'ranks':{'SSR-P3':1,'SSR-T3':3}}],
        'snapshot':{'role_zones':{'W':1,'P2':1,'P3':1}}}
    result=evaluate_against_result(utility,[1,2,3],static_roles={'3':['P3']},p3_rank_metric='SSR-T3')
    assert result['rank_comparison'][2]['krs_rank']==3
    assert result['rank_comparison'][2]['krs_role_zone_hit'] is False
    legacy=evaluate_common_utility(utility,[1,2,3])
    assert legacy['rank_comparison'][2]['krs_rank']==1

def test_actual_kyo12_dead_heat_never_invents_unique_second_third():
    obj=official('082026040612','KYO',12)
    assert obj['top3_display_order_is_not_unique'] is True
    assert len(obj['payouts']['EXACTA'])==2
    final=json.loads((ROOT/'runtime/final_artifacts/KM-JRA-KYO-20261017-R12.json').read_text())
    pred=prediction(final,obj)
    assert pred['P2'] is None and pred['P3'] is None and pred['ordered_exact'] is None
    assert settle_tickets(final['final_ticket']['tickets'],obj)['investment']==1600

def test_preregistered_common_definition_bytes_are_preserved():
    import hashlib
    protocol=json.loads((ROOT/'research/utility/forward_protocol.json').read_text())
    assert {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in protocol['definition_files']}==protocol['definition_sha256']
