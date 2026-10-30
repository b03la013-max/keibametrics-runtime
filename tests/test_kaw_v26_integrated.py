import copy
import json
import os
from pathlib import Path
import sys

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'runtime')]
from tools.kaw_v25_day_regression import audit,read,signed
from family_conversion_diagnostics import measure_capital_conversion
from family_pfs_promotion_gate import _num
from family_pfs_improvement import classify_dominant_pfs_loss_owner
from local_aki_columns import build,decision,build_role_rescue,freeze_role_rescue,LocalAKIError,sha


@pytest.fixture(scope='module')
def report():return audit(os.environ.get('KM_KAW_RAW_ROOT'))


def test_signed_fixed_denominators_and_money(report):
    assert len(report['rows'])==12 and report['canonical_formal_completed']==5
    assert report['fixed_four']['investment']==58800 and report['fixed_four']['return']==15030
    assert report['fixed_four']['pfs_pct']==pytest.approx(25.5612244898)
    assert report['signed_five']['investment']==66300 and report['signed_five']['return']==50640
    assert report['new_forward_oos_count']==0 and report['delivery_unknown_count']==5


@pytest.mark.parametrize('n,first,owner',[(1,'CAPITAL_EFFICIENCY','CAPITAL'),(6,'PREDICTION_ROLE_P2','PREDICTION_ROLE'),(9,'PREDICTION_ROLE_W','PREDICTION_ROLE'),(12,'PREDICTION_ROLE_W','PREDICTION_ROLE')])
def test_four_real_failure_fixtures(report,n,first,owner):
    r=report['rows'][n-1]
    assert r['first_material_failure']==first and r['dominant_pfs_loss']['owner']==owner
    assert r['signed_receipts_verified']==5 and r['numerical']['unresolved_count']==0
    assert not r['scheduler_success'] and not r['numerical_consumed_by_production_static']


def test_pair_rescue_does_not_imply_winner_rescue_or_positive_pfs(report):
    r6=report['rows'][5];r9=report['rows'][8];r12=report['rows'][11]
    assert r6['krs_incremental']['unique_pair_rescue']
    assert r9['krs_incremental']['unique_w_rescue'] and not r9['krs_incremental']['unique_pair_rescue']
    assert not r12['krs_incremental']['unique_w_rescue']
    assert {3,11}.issubset(r12['krs_incremental']['nonwinning_w_additions'])
    assert r6['arms']['OWNER_DIVERSITY_KRS_R3']['coverage']['ordered_exact_ticket_coverage']
    assert r6['arms']['OWNER_DIVERSITY_KRS_R3']['settlement']['profit_loss']<0


def test_exact_trio_and_reversed_orientation_remain_separate(report):
    assert report['rows'][0]['coverage']['ordered_exact_ticket_coverage']
    assert not report['rows'][0]['coverage']['purchased_trio_ticket_coverage']
    r12=report['rows'][11]['coverage']
    assert r12['top3_set_ticket_coverage'] and not r12['ordered_exact_ticket_coverage']
    assert not r12['purchased_trio_ticket_coverage']


def test_no_bet_budget_and_old_rejected_arms_preserved(report):
    for r in report['rows']:
        if 'arms' not in r:continue
        assert not r['arms']['FINITE_CAPITAL_10000']['tickets']
        for mode in ['PR265_R1_REJECTED','PR265_R2_REJECTED']:
            assert r['arms'][mode]['forward_admission']=='REJECTED'
        assert r['arms']['PRODUCTION']['tickets']==r['arms']['STATIC_PLUS_KRS_DIAGNOSTIC']['tickets']
    assert report['aggregates']['FINITE_CAPITAL_10000']['pfs_pct'] is None


@pytest.mark.parametrize('value',[True,float('nan'),float('inf'),float('-inf'),'inf'])
def test_nonfinite_is_missing_not_positive_pfs(value):
    assert _num(value) is None
    r={'capital':{'pfs':value},'failure_localization':{'first_material_failure':'NONE'}}
    assert classify_dominant_pfs_loss_owner(r)['owner']=='UNKNOWN'


def test_market_recoverability_requires_pre_cutoff_ticket_prices():
    req={'family_id':'LOCAL','race_id':'R','prediction_cutoff':'2026-11-09T14:58:00+09:00'}
    ft={'tickets':[{'bet_type':'EXACTA','selection':[1,2],'stake':100,'mec_tier':'CORE'}]}
    m={'race_id':'R','observed_at':'2026-11-09T14:00:00+09:00','source_ref':'official-prestart-snapshot','ticket_decimal_prices':{'EXACTA:1>2':2.0}}
    original=copy.deepcopy((req,ft,m));r=measure_capital_conversion(req,ft,{}, {},market=m)
    assert r['core_price_observations'][0]['snapshot_core_hit_recovers_portfolio']
    assert original==(req,ft,m) and r['expected_value'] is None
    m['observed_at']=req['prediction_cutoff']
    with pytest.raises(ValueError,match='TEMPORAL'):measure_capital_conversion(req,ft,{}, {},market=m)


def test_rescue_cannot_take_outcome_or_modified_owner():
    rr=os.environ.get('KM_KAW_RAW_ROOT');req=read(9,'intent',rr);src=read(9,'source_receipt_envelope',rr)['artifact']
    req['source_snapshot_sha256']=src['source_snapshot_sha256'];owner=read(9,'static_owner',rr);ku=read(9,'krs_prediction_utility',rr)
    owner['observed_facts']['5']['unknown_exact_course']=False
    with pytest.raises(LocalAKIError,match='OWNER_BINDING'):build_role_rescue(req,src,owner,ku)
    req['official_result']={}
    with pytest.raises(LocalAKIError,match='OUTCOME'):build_role_rescue(req,src,owner,ku)


def test_forward_clock_and_rejected_r3_cannot_be_bypassed(report):
    r=report['rows'][8];a=r['arms']['OWNER_DIVERSITY_KRS_R3'];rr=os.environ.get('KM_KAW_RAW_ROOT')
    req=read(9,'intent',rr);src=read(9,'source_receipt_envelope',rr)['artifact']
    from local_fullnumerical_production import materialize_production
    q=materialize_production(src,req,req['required_indices']);q['source_snapshot_sha256']=src['source_snapshot_sha256']
    with pytest.raises(LocalAKIError,match='FORWARD_AFTER_CUTOFF'):
        freeze_role_rescue(q,a['selection'],a['tickets'],evaluation_mode='FORWARD_PAPER',policy_sha256='a'*64)
    q['prediction_cutoff']='2099-11-09T14:58:00+09:00'
    s=copy.deepcopy(a['selection']);s['input_sha256']=sha(q);s.pop('sha256');s['sha256']=sha(s)
    with pytest.raises(LocalAKIError,match='REPLAY_REJECTED_ARM'):
        freeze_role_rescue(q,s,a['tickets'],evaluation_mode='FORWARD_PAPER',policy_sha256='a'*64)


def test_receipt_tampering_rejected():
    e=read(1,'final_receipt_envelope',os.environ.get('KM_KAW_RAW_ROOT'));e['artifact']['final_ticket']['tickets'][0]['stake']+=100
    with pytest.raises(ValueError,match='SIGNED_LINEAGE'):signed(e,'FINAL',e['receipt']['race_id'])
