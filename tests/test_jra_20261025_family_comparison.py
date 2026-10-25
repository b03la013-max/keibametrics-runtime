"""Boundary regressions for the existing fixed-arm cross-Venue evaluation."""
import inspect
import json
from pathlib import Path
import sys

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts import jra_20261025_family_compare as m


def fixture(tmp_path,*,stored=False,paper=False):
    rid='KM-JRA-TKY-20261025-R02'
    q={'race_id':rid,'source_snapshot_sha256':'a'*64,'prediction_cutoff':'2026-10-25T10:15:00+09:00',
       'runners':[{'runner_id':str(i)} for i in range(1,5)]}
    f={**{k:q[k] for k in ('race_id','source_snapshot_sha256','prediction_cutoff')},
       'family_id':'JRA','temporal_mode':'FORMAL-PRE-RACE','scheduled_post_at':'2026-10-25T10:20:00+09:00',
       'final_receipt_sha256':'b'*64,'final_receipt':{'receipt':{'timestamp':'2026-10-25T10:00:00+09:00'}},
       'static_prediction':{'ranking':['1','2','3','4'],'roles':{'1':['W'],'2':['P2'],'3':['P3'],'4':[]}},
       'final_ticket':{'tickets':[] if paper else [{'bet_type':'EXACTA','selection':[1,2],'stake':100}],
                       'total_investment':0 if paper else 100},
       'capital_policy_decision':{'paper_only':paper},'krs_prediction_utility':{}}
    f['sha256']=m.digest(f)
    official={'top3':[1,2,3],'payouts':{'EXACTA':{'selection':[1,2],'per_100_yen':600}}}
    for folder,obj,name in [('requests',q,rid+'-LIVE-R1-FORMAL.json'),('final_artifacts',f,rid+'.json')]:
        p=tmp_path/'runtime'/folder/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj))
    if stored:
        result={'frozen_prediction_ref':{'immutable_final_sha256':f['sha256']},
                'official_result':official,'settlement':settle(f,official)}
        p=tmp_path/'runtime/results'/(rid+'.json');p.parent.mkdir(parents=True);p.write_text(json.dumps(result))
    return rid,q,f,official


def settle(final,official):
    tickets=final['final_ticket']['tickets'];inv=sum(t['stake'] for t in tickets)
    wins=[{**t,'return':t['stake']*6} for t in tickets if t['selection']==[1,2]]
    payout=sum(t['return'] for t in wins)
    return {'total_investment':inv,'total_payout':payout,'profit_loss':payout-inv,
            'pfs':100*payout/inv if inv else None,'winning_tickets':wins}


def mock_pools(monkeypatch,ranking=('1','2','3','4')):
    def pool(request,final,shadow=None):
        rr={r:list(ranking) for r in m.ROLES}
        head={h:[s for s in ranking if s!=h] for h in ranking}
        third={h+'>'+s:[t for t in ranking if t not in (h,s)] for h in ranking for s in ranking if h!=s}
        arm={'ranking':rr,'head_local_p2':head,'pair_conditioned_third':third}
        return {'arms':{'STATIC_INDEX':arm}},{'STATIC_INDEX':(m.ranked_tickets(rr),None,{})}
    monkeypatch.setattr(m,'portfolio_pools',pool)


def test_tied_p3_accepts_either_valid_order_without_double_race_count():
    rank=['1','2','4','3'];rr={'W':rank,'P2':['2','1','4','3'],'P3':['4','3','1','2']}
    arm={'ranking':rr,'head_local_p2':{h:[s for s in rank if s!=h] for h in rank},
         'pair_conditioned_third':{h+'>'+s:[t for t in rank if t not in (h,s)] for h in rank for s in rank if h!=s}}
    f={'static_prediction':{'roles':{'1':['W'],'2':['P2'],'3':['P3'],'4':[]}}}
    o={'top3':[1,2,3],'top3_orders':[[1,2,3],[1,2,4]]}
    out=m.role_score(arm,f,o)
    assert out['matched_width_role_capture']['P3']
    assert out['top1_ordered_exact']
    assert out['actual_role_rank']['P3']==1.5
    assert len(out['official_valid_orders'])==2


def test_missing_signed_result_remains_unknown_even_when_offline_label_settles(tmp_path,monkeypatch):
    rid,_,_,official=fixture(tmp_path);mock_pools(monkeypatch)
    before={str(p.relative_to(tmp_path)):p.read_bytes() for p in tmp_path.rglob('*.json')}
    out=m.compare(tmp_path,venues=('TKY',),official_labels={rid:official},settlement_fn=settle)
    assert out['formal_series']['status']=='INCOMPLETE_MISSING_CANONICAL_RESULT_REQUEST'
    assert out['formal_series']['full_population_pfs'] is None
    assert out['baseline_offline_research']['all']['pfs']==600
    assert out['new_signatures']==out['runtime_posts']==out['forward_oos_increment']==0
    assert out['coverage'][1]['label_status']=='UNSIGNED_OFFICIAL_LABEL_RESEARCH_ONLY'
    assert {str(p.relative_to(tmp_path)):p.read_bytes() for p in tmp_path.rglob('*.json')}==before


def test_missing_labels_do_not_become_zero_percent_results(tmp_path,monkeypatch):
    fixture(tmp_path);mock_pools(monkeypatch)
    out=m.compare(tmp_path,venues=('TKY',),settlement_fn=settle)
    assert out['evaluated_finals']==out['matched_comparison_count']==0
    assert out['coverage'][1]['state']=='FROZEN_FINAL_RESULT_PENDING'
    assert out['coverage'][1]['pfs'] is None


def test_result_override_and_source_crossover_are_refused(tmp_path,monkeypatch):
    rid,q,_,official=fixture(tmp_path,stored=True);mock_pools(monkeypatch)
    with pytest.raises(ValueError,match='CANONICAL_RESULT_OVERRIDE'):
        m.compare(tmp_path,venues=('TKY',),official_labels={rid:{**official,'top3':[2,1,3]}},settlement_fn=settle)
    qp=tmp_path/'runtime/requests'/(rid+'-LIVE-R1-FORMAL.json');q['source_snapshot_sha256']='c'*64;qp.write_text(json.dumps(q))
    with pytest.raises(ValueError,match='ORIGINAL_BINDING'):
        m.compare(tmp_path,venues=('TKY',),settlement_fn=settle)


def test_lost_positive_control_and_same_exposure_are_reported(tmp_path,monkeypatch):
    rid,_,_,_=fixture(tmp_path,stored=True);mock_pools(monkeypatch,('3','4','2','1'))
    out=m.compare(tmp_path,venues=('TKY',),settlement_fn=settle)
    arm=out['candidate_metrics']['STATIC_INDEX']
    assert arm['unique_ticket_harm']==1
    assert arm['positive_controls'][rid]['lost_hit']
    assert arm['cash']['investment']==out['baseline_offline_research']['all']['investment']==100
    assert arm['cash']['total_points']==1


def test_paper_does_not_gain_a_budget_and_construction_cannot_read_labels(tmp_path,monkeypatch):
    fixture(tmp_path,stored=True,paper=True);mock_pools(monkeypatch)
    out=m.compare(tmp_path,venues=('TKY',),settlement_fn=settle)
    arm=out['candidate_metrics']['STATIC_INDEX']['cash']
    assert arm['investment']==arm['total_points']==0 and arm['pfs'] is None
    assert not {'result','official','labels','payouts'} & set(inspect.signature(m.matched_exposure).parameters)


def test_duplicate_outcomes_and_duplicate_venues_cannot_double_count(tmp_path):
    with pytest.raises(ValueError,match='VALID_ORDERS'):
        m.orders({'top3':[1,2,3],'top3_orders':[[1,2,3],[1,2,3]]})
    with pytest.raises(ValueError,match='DUPLICATE_VENUE'):
        m.compare(tmp_path,venues=('TKY','TKY'))
