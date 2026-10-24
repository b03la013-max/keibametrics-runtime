"""Authored synthetic cases only; no race-day originals/results in Git."""
import copy
from itertools import combinations, permutations

import pytest

from runtime.urw_paper_selection import (POLICY, sha, select_portfolio, p1_role_hypotheses,
                                         canonical_tickets)
from runtime.jra_ticket_tree_renderer import render_ticket_tree


def seal(x):
    x.pop('sha256',None);x['sha256']=sha(x);return x


def prediction(n=6, strength=2):
    ids=list(map(str,range(1,n+1)))
    def dist(excluded=()):
        v={rid:strength**(n-int(rid)) for rid in ids if rid not in excluded}
        return {rid:w/sum(v.values()) for rid,w in v.items()}
    w=dist();p2={h:dist((h,)) for h in ids}
    p3={h+'>'+s:dist((h,s)) for h,s in permutations(ids,2)}
    pairs=[{'head':h,'second':s,'model_mass':w[h]*p2[h][s]} for h,s in permutations(ids,2)]
    triples=[{'head':h,'second':s,'third':t,'model_mass':w[h]*p2[h][s]*p3[h+'>'+s][t]}
             for h,s,t in permutations(ids,3)]
    return seal({'race_id':'SYNTHETIC-URW','ranking':ids,'feature_sha256':'feature',
                 'prediction_cutoff':'2099-10-21T12:00:00+09:00',
                 'role_columns':{rid:['W','P2','P3'] for rid in ids},
                 'role_widths':{'W':n,'P2':n,'P3':n},'winner_model_mass':w,
                 'p2_model_mass_given_head':p2,'p3_model_mass_given_pair':p3,
                 'ordered_pairs':pairs,'ordered_triples':triples})


def tickets(pred):
    ids=pred['ranking']
    return ([{'bet_type':'EXACTA','selection':list(map(int,s)),'stake':100} for s in permutations(ids,2)] +
            [{'bet_type':'TRIO','selection':list(map(int,s)),'stake':100} for s in combinations(ids,3)])


def rebuild_joint(pred):
    for row in pred['ordered_pairs']:
        h,s=row['head'],row['second']
        row['model_mass']=pred['winner_model_mass'][h]*pred['p2_model_mass_given_head'][h][s]
    for row in pred['ordered_triples']:
        h,s,t=row['head'],row['second'],row['third']
        row['model_mass']=(pred['winner_model_mass'][h]*pred['p2_model_mass_given_head'][h][s]
                           *pred['p3_model_mass_given_pair'][h+'>'+s][t])
    return seal(pred)


def run(pred=None, **kwargs):
    p=pred or prediction()
    ref={'immutable_semantic_sha256':'synthetic'}
    if kwargs.get('krs_utility'):
        u=kwargs['krs_utility'];ref.update(krs_utility_sha256=u['sha256'],
            krs_snapshot_sha256=sha(u.get('snapshot')),krs_master_seed=1,
            krs_input_sha256='input',krs_output_file_sha256='output')
    return select_portfolio(p,tickets(p),source_ref=ref,**kwargs)


def test_outcome_blind_immutable_capped_uniform_no_backfill_and_complete_ledger():
    p=prediction();ts=tickets(p);before=copy.deepcopy((p,ts,POLICY))
    out=select_portfolio(p,ts,source_ref={'sha256':'original'})
    assert (p,ts,POLICY)==before
    assert out['used_budget_yen']<=2000 and out['unused_budget_yen']>0
    assert len(out['candidate_ledger'])==len(ts)
    assert sum(x['selected'] for x in out['candidate_ledger'])==len(out['selected_tickets'])
    assert all(x['reason'] for x in out['candidate_ledger'])
    assert all(x['stake']==100 for x in out['selected_tickets'])
    assert out['coverage']['lost_ordered_scenarios']>0
    assert not out['coverage']['is_material_coverage_100_percent']
    flat=run(prediction(strength=1))
    assert flat['no_bet'] and flat['used_budget_yen']==0
    assert flat['unused_budget_yen']==2000
    assert run(day_remaining_yen=0)['no_bet']
    assert run(day_remaining_yen=300)['used_budget_yen']<=300


def test_trio_sums_exactly_six_distinct_joint_orders_not_product_of_marginals():
    p=prediction();out=run(p)
    for row in out['candidate_ledger']:
        if row['original_ticket']['bet_type']!='TRIO':continue
        ids=set(map(str,row['original_ticket']['selection']))
        expected=sum(t['model_mass'] for t in p['ordered_triples'] if {t['head'],t['second'],t['third']}==ids)
        assert row['conditional_model_mass']==pytest.approx(expected)
        assert row['ordered_scenario_count']==6


def test_rank_only_invariance_and_conditional_consumption_are_explained():
    p=prediction();first=run(p)
    q=copy.deepcopy(p);q['ranking'].reverse();seal(q)
    second=run(q)
    assert first['selected_tickets']==second['selected_tickets']
    assert first['input_sha256']!=second['input_sha256']
    assert second['consumed']['ranking_only_does_not_force_ticket_change']
    # A genuinely different conditional model changes the selected portfolio.
    alternate=prediction(strength=0.5)
    assert run(alternate)['selected_tickets']!=first['selected_tickets']
    broken=copy.deepcopy(p);broken['p2_model_mass_given_head']['1']['2']+=0.01;seal(broken)
    with pytest.raises(ValueError,match='ADAPTER_DISAGREES'):run(broken)


def test_explicit_exclusions_and_invalid_or_duplicate_tickets():
    p=prediction();out=run(p,excluded_runner_ids=['1'])
    assert not any(1 in t['selection'] for t in out['selected_tickets'])
    assert any(x['reason']=='EXPLICIT_SCRATCH_OR_EXCLUSION' for x in out['candidate_ledger'])
    for bad in ([{'bet_type':'EXACTA','selection':[1,1],'stake':100}],
                [tickets(p)[0],tickets(p)[0]],
                [{'bet_type':'TRIO','selection':[1,2,99],'stake':100}]):
        with pytest.raises(ValueError):select_portfolio(p,bad,source_ref={})


def test_krs_absence_is_not_incremental_value_and_toplist_missing_is_unknown():
    no=run();assert not no['consumed']['krs']
    assert no['consumed']['krs_incremental_value'].startswith('UNMEASURED')
    p=prediction(strength=1)
    ku=seal({'krs_status':'EXECUTED','race_id':p['race_id'],'snapshot':{'master_seed':1},
             'top_exacta_occurrence':[{'W':1,'P2':2,'frequency':0.3}],
             'top_trifecta_occurrence':[{'W':1,'P2':2,'P3':3,'frequency':0.2}]})
    out=run(p,krs_utility=ku)
    assert out['tier_spend_yen']['PROTECTION']<=500
    assert out['consumed']['krs']
    assert out['consumed']['krs_incremental_value'].startswith('UNMEASURED')
    assert all(x['krs_joint_support'] is None or x['krs_joint_support']['omitted_orders']=='UNKNOWN_NOT_ZERO'
               for x in out['candidate_ledger'])


def test_existing_delivery_tree_expands_to_exact_selected_tickets_and_stakes():
    p=prediction();out=run(p)
    tree=render_ticket_tree({'final_ticket':{'tickets':out['selected_tickets'],'no_bet':out['no_bet']},
                             'static_prediction':{'ranking':p['ranking']},
                             'capital_policy_decision':{'decision':'PAPER'}})
    assert canonical_tickets(tree['reflattened_tickets'])==out['selected_tickets']
    assert tree['total_investment']==out['used_budget_yen']


def test_p1_unknown_alone_neither_adds_all_roles_nor_removes_original_roles():
    p=prediction();ids=p['ranking']
    # Deliberately absent condition and path observations for every runner.
    pack=seal({'race_date':'2099-10-21','source_snapshot_sha256':'raw','source_observed_at':'2026-10-19T12:00:00+09:00',
               'runners':{x:{} for x in ids}})
    p['feature_sha256']=pack['sha256'];p['role_columns']['6']=[];seal(p)
    obs={'source':{'raw_sha256':'raw','fetched_at':pack['source_observed_at']},'race':{'distance':1400},
         'facts':[{'runner_id':x,'status':'ACTIVE_DECLARED','starts':[]} for x in ids]}
    before=copy.deepcopy(p);result=p1_role_hypotheses(p,pack,obs)
    assert p==before
    assert result['prediction']['role_columns']==p['role_columns']
    assert len(result['all_runner_review'])==len(ids)
    assert not any(x['added_roles'] for x in result['all_runner_review'])
    assert result['prediction']['frozen_at']!='2099-10-21T12:00:00+09:00'


@pytest.mark.parametrize('bad',[[1.9,2],[True,2],'12',['1.0','2']])
def test_lossy_cast_never_rewrites_original_candidate(bad):
    with pytest.raises(ValueError):canonical_tickets([{'bet_type':'EXACTA','selection':bad,'stake':100}])


def test_wrong_race_seed_and_impossible_krs_joint_total_hold():
    p=prediction(strength=1)
    base={'krs_status':'EXECUTED','race_id':p['race_id'],'snapshot':{'master_seed':1},
          'top_exacta_occurrence':[],'top_trifecta_occurrence':[]}
    for change in ({'race_id':'OTHER'},{'snapshot':{'master_seed':999}},
                   {'top_trifecta_occurrence':[{'W':h,'P2':s,'P3':t,'frequency':0.9}
                                               for h,s,t in permutations((1,2,3))]}):
        with pytest.raises(ValueError):run(p,krs_utility=seal({**base,**change}))


def test_posthoc_time_is_explicit_and_cluster_instability_is_detectable():
    from runtime.local_krs_bridge_candidate import _structure_upper_cluster
    p=prediction();p['prediction_cutoff']='2020-01-01T00:00:00+09:00';seal(p)
    out=run(p)
    assert out['classification']=='POSTHOC_DEVELOPMENT_NOT_PRESTART'
    assert out['created_at'] and out['forward_oos_credit']==0
    rows=[{'runner_id':str(i),'score':50.0} for i in range(1,7)]
    same,_=_structure_upper_cluster(rows,'score',min_active=1)
    rows[0]['score']+=1e-6
    changed,_=_structure_upper_cluster(rows,'score',min_active=1)
    assert len(same)==6 and len(changed)==1  # Detect, do not silently claim stability.


def test_p1_requires_both_evidence_families_and_rejects_history_after_capture():
    p=prediction();ids=p['ranking'];p['role_columns']['2']=['W']
    values={x:{'STAGE:progression':None,'STAGE:final_reserve':None} for x in ids}
    pack=seal({'race_date':'2099-10-21','source_snapshot_sha256':'raw','source_observed_at':'2026-10-21T09:00:00+09:00',
               'runners':values})
    p['feature_sha256']=pack['sha256'];seal(p)
    fact={'date':'26.10.20','surface':'DIRT','distance':1400,'finish':2,'field_size':10,'provider_race_id':'synthetic_past'}
    obs={'source':{'raw_sha256':'raw','fetched_at':pack['source_observed_at']},'race':{'distance':1400},
         'facts':[{'runner_id':x,'status':'ACTIVE_DECLARED','starts':[fact] if x=='2' else []} for x in ids]}
    first=p1_role_hypotheses(p,pack,obs)
    assert not next(x for x in first['all_runner_review'] if x['runner_id']=='2')['added_roles']
    pack['runners']['2']['STAGE:progression']=0.2;seal(pack);p['feature_sha256']=pack['sha256'];seal(p)
    second=p1_role_hypotheses(p,pack,obs)
    row=next(x for x in second['all_runner_review'] if x['runner_id']=='2')
    assert set(row['added_roles'])=={'P2','P3'} and len(row['evidence_families'])==2
    bad=copy.deepcopy(obs);bad['source']['fetched_at']='2026-10-19T09:00:00+09:00'
    pack['source_observed_at']=bad['source']['fetched_at'];seal(pack);p['feature_sha256']=pack['sha256'];seal(p)
    with pytest.raises(ValueError,match='HISTORY_AFTER_ACTUAL_CAPTURE'):p1_role_hypotheses(p,pack,bad)


@pytest.mark.parametrize('bad',['offsetting_p3_rows','offsetting_p2_rows','negative_factors','unused_runner'])
def test_normalized_joint_total_cannot_hide_invalid_conditioning_distributions(bad):
    p=prediction(n=3,strength=1)
    if bad=='offsetting_p3_rows':
        p['p3_model_mass_given_pair']['1>2']['3']=2.0
        p['p3_model_mass_given_pair']['2>1']['3']=0.0
    elif bad=='offsetting_p2_rows':
        for h,scale in [('1',1.5),('2',0.5)]:
            p['p2_model_mass_given_head'][h]={s:value*scale for s,value in p['p2_model_mass_given_head'][h].items()}
    elif bad=='negative_factors':
        p['winner_model_mass']={h:-value for h,value in p['winner_model_mass'].items()}
        p['p2_model_mass_given_head']={h:{s:-value for s,value in values.items()}
                                      for h,values in p['p2_model_mass_given_head'].items()}
    else:
        p['p3_model_mass_given_pair']['1>2']['99']=0.0
    rebuild_joint(p)
    # Each supplied ordered row agrees with its factors and global mass is one;
    # the invalid per-context distribution must still be rejected.
    assert sum(x['model_mass'] for x in p['ordered_pairs'])==pytest.approx(1)
    assert sum(x['model_mass'] for x in p['ordered_triples'])==pytest.approx(1)
    with pytest.raises(ValueError,match='CONDITIONAL_DISTRIBUTION'):
        select_portfolio(p,tickets(p),source_ref={})


def test_cross_bet_scenario_suppression_is_explained_without_claiming_payout_redundancy():
    p=prediction(n=4,strength=4)
    source=[{'bet_type':'EXACTA','selection':[1,2],'stake':500},
            {'bet_type':'TRIO','selection':[1,2,3],'stake':300}]
    before=copy.deepcopy((p,source))
    result=select_portfolio(p,source,source_ref={})
    exacta,trio=result['candidate_ledger']
    assert result['selected_tickets']==[{'bet_type':'TRIO','selection':[1,2,3],'stake':100}]
    assert exacta['joint_lift_over_uniform_not_ev']>=POLICY['minimum_joint_lift_over_uniform']
    diagnostic=exacta['final_tier_diagnostics']['CORE']
    assert 'BELOW_RELATIVE_MARGINAL_GAIN' in diagnostic['blocking_conditions']
    assert diagnostic['within_bet_type_marginal_model_coverage']==pytest.approx(exacta['conditional_model_mass'])
    assert diagnostic['cross_bet_suppressed_marginal_mass']>0
    assert diagnostic['shared_marginal_model_coverage']<diagnostic['relative_marginal_gain_floor']
    assert not diagnostic['economic_redundancy_inferred_from_coverage']
    assert result['coverage']['objective']=='SHARED_ORDERED_SCENARIO_UNION_NOT_ADDITIVE_PAYOUT'
    assert not result['coverage']['cross_bet_overlap_proves_economic_redundancy']
    # Outcome 1,2,3 belongs to both payout events, although S1 retains only TRIO.
    assert source[0]['selection']==[1,2] and set(source[1]['selection'])=={1,2,3}
    assert trio['decision_trace'][0]['decision']=='SELECTED'
    assert trio['decision_trace'][0]['eligible_for_this_step']
    assert (p,source)==before


def test_diagnostics_separate_protection_only_no_bet_and_exhausted_budget():
    p=prediction(strength=1)
    utility=seal({'krs_status':'EXECUTED','race_id':p['race_id'],'snapshot':{'master_seed':1},
                  'top_exacta_occurrence':[{'W':1,'P2':2,'frequency':0.3}],
                  'top_trifecta_occurrence':[{'W':1,'P2':2,'P3':3,'frequency':0.2}]})
    protected=run(p,krs_utility=utility)
    assert protected['participation_state']=='PROTECTION_ONLY'
    assert protected['tier_spend_yen']['CORE']==0
    assert 0<protected['tier_spend_yen']['PROTECTION']<=500
    assert not protected['no_bet']
    unknown=next(row for row in protected['candidate_ledger'] if row['krs_joint_support'] is None)
    assert unknown['final_tier_diagnostics']['PROTECTION']['krs_support_state']=='UNKNOWN_NOT_ZERO'
    assert 'KRS_TOPLIST_SUPPORT_UNKNOWN' in unknown['final_tier_diagnostics']['PROTECTION']['blocking_conditions']
    assert run(p)['participation_state']=='COMPLETE_NO_BET'
    exhausted=run(day_remaining_yen=0)
    assert exhausted['used_budget_yen']==0 and exhausted['unused_budget_yen']==0
    assert all('FIXED_TIER_BUDGET_EXHAUSTED' in row['final_tier_diagnostics'][tier]['blocking_conditions']
               for row in exhausted['candidate_ledger'] for tier in ('CORE','PROTECTION'))


def test_equal_gain_tie_is_canonical_and_trace_conserves_selected_ticket_units():
    p=prediction(n=4,strength=1)
    p['winner_model_mass']={'1':0.7,'2':0.1,'3':0.1,'4':0.1};rebuild_joint(p)
    source=[{'bet_type':'EXACTA','selection':[1,3],'stake':700},
            {'bet_type':'EXACTA','selection':[1,2],'stake':100}]
    first=select_portfolio(p,source,source_ref={})
    second=select_portfolio(p,list(reversed(source)),source_ref={})
    assert first['selected_tickets']==second['selected_tickets']
    assert first['candidate_ledger']==second['candidate_ledger']
    selected=sorted(first['candidate_ledger'],key=lambda row:row['decision_trace'][0]['selection_order'])
    assert [row['original_ticket']['selection'] for row in selected]==[[1,2],[1,3]]
    assert first['used_budget_yen']==200 and first['participation_state']=='CORE_ONLY'
    assert sum(row['selection_detail']['stake'] for row in selected)==first['used_budget_yen']
    assert sha(POLICY)=='663c63f6931d49d5cbc994ee17cef8a3075d957216db18bf02590d82d5e3c34d'
