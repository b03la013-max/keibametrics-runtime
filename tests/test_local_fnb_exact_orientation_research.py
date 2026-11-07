"""Exact transport and decision counterexamples; synthetic, never OOS credit."""
from copy import deepcopy
from pathlib import Path

import pytest

from runtime import local_fnb_exact_orientation_research as m
from runtime import local_fnb_semantic_closure as semantic
from test_local_fnb_semantic_closure import fixture, seal

NOW='2026-11-04T02:00:00+00:00'


def inputs():
    p=fixture()
    p['race_id']='KM-LOCAL-FNB-20261104-R01-SYNTHETIC'
    p['PRE_KRS_input']={'race':{'prediction_id':'synthetic-fixed-1'}}
    ctx={'race_id':p['race_id'],'source_snapshot_sha256':p['source_snapshot_sha256'],
        'runners':[{'runner_id':r,'paths':[{'world_hypothesis':'TRACK_OR_HOLD',
            'source_event_date':'2026-10-01','source_raw_sha256':'b'*64,
            'stage_cost_hypotheses':{'launch':1}}], 'stage_cost_topology':{'launch':1},
            'reachable_position_range':[1,4]} for r in p['active_runners']]}
    ctx['sha256']=semantic._sha(ctx);p['input_context_sha256']=ctx['sha256']
    p['runner_world_stage_basis']={r:{'synthetic':True} for r in p['active_runners']};seal(p)
    ssr={r:{'SSR-W':w,'SSR-P2':s,'SSR-P3':t,'Z4R-W':0.5,'Z4R-P2':0.5,'Z4R-P3':0.5,'LSR':0.1}
        for r,w,s,t in [('1',0.5,0.1,0.1),('2',0.2,0.5,0.2),('3',0.1,0.2,0.5),('4',0.8,0.8,0.8)]}
    k={'snapshot':{'run_count':5000,'master_seed':1,'prediction_id':'synthetic-fixed-1'},
       'scenario_analysis':{n:{'run_count':1000,'ssr':deepcopy(ssr),'positions':{}}
                            for n in m.SCENARIOS},'top_trifecta_occurrence':[]}
    s2=semantic.research_unknown_path_protection(p,evaluated_at=NOW)
    freeze={'profile':m.PROFILE,'module_sha256':m.MODULE_SHA,
        'profile_sha256':m.sha(m.PROFILE_PATH.read_bytes()),'frozen_at':NOW}
    return p,ctx,k,s2,freeze


def evaluate(x):
    p,c,k,s,f=x
    return m.evaluate(p,c,k,s,freeze=f,evaluated_at=NOW)


def construct(x,r=None):
    p,c,k,s,f=x
    return m.construct(p,c,k,r or evaluate(x),s,freeze=f,evaluated_at=NOW)


def reseal_context(x):
    p,c,k,s,f=x;c.pop('sha256',None);c['sha256']=semantic._sha(c)
    p['input_context_sha256']=c['sha256'];seal(p)
    return p,c,k,semantic.research_unknown_path_protection(p,evaluated_at=NOW),f


def test_nonzero_exact_off_global_third_and_original_sets_retained():
    x=inputs();before=deepcopy(x);r=evaluate(x);out=construct(x,r)
    assert r['exact_selected']==[['1','2','3']]
    assert x[0]['column_rankings']['P3']['front']==['1']
    assert out['methods']['TRIFECTA']['tickets'][0]['selection']==[1,2,3]
    assert out['methods']['TRIFECTA']['required_MEC']==100
    assert all(out['methods'][k]['point_count']==x[3]['methods'][k]['point_count'] for k in ('EXACTA','TRIO'))
    assert out['all_original_S2_ordered_pairs_and_sets_preserved']
    assert out['methods']['TRIFECTA']['canonical_roundtrip_verified']
    assert not out['recipient_ACK'] and not out['formal_final'] and out['new_KRS']==0
    assert x==before


def test_protect_original_stays_zero_and_exact_is_separate_policy():
    x=inputs();assert not x[3]['methods']['TRIFECTA']['tickets']
    r=evaluate(x)
    assert all(z['formal_terminal']=='POLICY_NOT_ADOPTED' for z in r['ledger'])
    assert all(z['status']==semantic.PROPOSAL_STATUS for z in x[0]['third_dispositions'])
    assert not r['formal_selection_adopted'] and r['registered_OOS_increment']==0


def test_unknown_high_krs_never_becomes_purchase_or_rank_zero():
    x=inputs();r=evaluate(x)
    rows=[z for z in r['ledger'] if len({z['head'],z['second'],z['third']})==3 and z['unknown_participants']]
    assert rows and all(z['terminal']=='UNKNOWN_UNRESOLVED' for z in rows)
    assert all(z['rank'] is None for col in ('W','P2','P3') for z in x[0]['column_rankings'][col]['rows'] if z['runner_id']=='4')


@pytest.mark.parametrize('case',['crossing','tie','zero_role'])
def test_scenario_order_is_selective_and_ties_are_not_arbitrarily_broken(case):
    x=inputs();k=x[2]
    if case=='crossing':k['scenario_analysis']['leader_failure']['ssr']['3']['SSR-P2']=0.9
    elif case=='tie':
        for s in k['scenario_analysis'].values():s['ssr']['3']['SSR-P2']=s['ssr']['2']['SSR-P2']
    else:k['scenario_analysis']['natural']['ssr']['3']['SSR-P3']=0
    r=evaluate(x);out=construct(x,r)
    assert not r['exact_selected'] and not out['methods']['TRIFECTA']['tickets']
    assert not out['methods']['TRIFECTA']['computed_whole_race_NO_BET']


def test_exclusive_lead_conflict_is_protect_not_structural():
    x=inputs()
    for row in x[1]['runners']:
        row['paths'][0]['world_hypothesis']='LEAD_HOLD'
    x=reseal_context(x);r=evaluate(x)
    row=next(z for z in r['ledger'] if z['path_id']=='1>2>3')
    assert row['terminal']=='EXACT_PROTECT_ONLY' and 'SCENARIO_CONFLICT' in row['reason']
    assert not r['exact_selected']


def test_every_orientation_compared_duplicates_only_structural():
    r=evaluate(inputs())
    assert len(r['ledger'])==64 and len(r['same_set_six_orientation_comparisons'])==4
    for row in r['same_set_six_orientation_comparisons']:
        assert len(row['all_six_orientations'])==6
        assert sum(z['terminal']=='EXACT_PURCHASE' for z in row['all_six_orientations'])<=1
    assert all(len({z['head'],z['second'],z['third']})<3 for z in r['ledger'] if z['terminal']=='STRUCTURAL_INELIGIBLE')
    assert all(z['joint_support_status']=='CENSORED_NOT_ZERO_NOT_PROVEN_UNOBSERVED' for z in r['ledger'])


def test_capital_overrun_keeps_full_paper_and_no_purchase(monkeypatch):
    x=inputs()
    monkeypatch.setattr('runtime.capital_policy.load_family_default_capital_policy',
        lambda:{'mode':'HARD_RACE_BUDGET','max_race_capital':0,'insufficient_action':'PAPER'})
    out=construct(x);t=out['methods']['TRIFECTA']
    assert t['point_count']==1 and t['required_MEC']==t['budget_shortfall']==100
    assert t['within_existing_cap_eligible_paper_amount']==0
    assert t['capital_policy']['decision']=='PAPER' and t['actual_purchase']==0
    assert t['capital_nonselected_full_paper_amount']==100


@pytest.mark.parametrize('case,code',[
    ('original_purchase','ORIGINAL_PROPOSAL_MUTATED'),('source','CONTEXT_SOURCE_STATIC_BINDING'),
    ('old_krs','KRS_EXECUTION_OR_REVISION'),('no_scenario','SCENARIO_NOT_EXECUTED'),
    ('seed','KRS_EXECUTION_OR_REVISION'),('freeze','EXACT_PROFILE_CODE_FREEZE')])
def test_invalid_inputs_fail_closed(case,code):
    x=inputs();p,c,k,s,f=x
    if case=='original_purchase':
        p['third_dispositions'][0]['status']='PURCHASE';seal(p);s['model_prediction_sha256']=semantic._sha(p)
    elif case=='source':p['source_snapshot_sha256']='0'*64;seal(p)
    elif case=='old_krs':k['snapshot']['prediction_id']='other-revision'
    elif case=='no_scenario':k['scenario_analysis'].pop('natural')
    elif case=='seed':k['snapshot']['master_seed']=2
    else:f['module_sha256']='0'*64
    with pytest.raises(ValueError,match=code):evaluate(x)


def test_forged_purchase_in_both_ledger_and_summary_is_not_transport_authority():
    x=inputs();r=evaluate(x)
    row=next(z for z in r['ledger'] if z['path_id']=='1>3>2');row['terminal']='EXACT_PURCHASE'
    r['exact_selected'].append(['1','3','2']);r['material_exact_count']+=1
    with pytest.raises(ValueError,match='REVIEW_NOT_REPRODUCIBLE'):construct(x,r)


def test_aware_clock_and_future_freeze_enforced():
    x=inputs();x[4]['frozen_at']='2026-11-04T03:00:00+00:00'
    with pytest.raises(ValueError,match='FREEZE_IN_FUTURE'):evaluate(x)
    x[4]['frozen_at']='2026-11-04T02:00:00'
    with pytest.raises(ValueError,match='AWARE_CLOCK_REQUIRED'):evaluate(x)
