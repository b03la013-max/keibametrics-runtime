"""Isolation and anti-leakage checks for research-only candidate projections."""
from copy import deepcopy
from pathlib import Path
import sys
import json
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'research/jra_20261024_prediction')]
from candidates import predict,history_measure,digest,bvi_scores,ROLES,class_ordinal
from replay import failure_matrix,archived_shadow_lineage
from jra_index_provenance_builder import BASE,DCR_COMPONENT_MAX,materialize_index_provenance

def request():
    rows={}
    features={k:{'category':'STRONG','evidence_refs':['SYNTHETIC_TEST_ONLY'],'source_authority':'JRA_OFFICIAL','result_derived':False} for k in ['recent_performance','position_quality','pace_resilience','closing_quality','course_geometry_fit']}
    for n in range(1,5):
        rows[str(n)]={'base_indices':{k:{'value':50.+n*5,'rule_id':'SYNTHETIC_TEST_ONLY','mapping_version':'TEST','evidence_refs':['SYNTHETIC_TEST_ONLY'],'source_fact':'unit fixture','components':[]} for k in BASE},'dcr':{'components':{k:{'points':maximum/2,'evidence_refs':['SYNTHETIC_TEST_ONLY']} for k,maximum in DCR_COMPONENT_MAX.items()}},'weak_penalty_major_indices':['HPI','SSI','RFI'],'scenario_fit':{'value':50.,'evidence_refs':['SYNTHETIC_TEST_ONLY']},'career_starts':2}
    q=materialize_index_provenance({'runners':[{'runner_id':str(n),'name':'TEST'+str(n),'evidence_features':deepcopy(features)} for n in range(1,5)],'index_provenance_ledger':{'formula_registry':'index_formula_registry JRA v1.0','runners':rows}})
    q.update(family_id='JRA',race_id='KM-JRA-TKY-20261024-R01',source_snapshot_sha256='a'*64,prediction_cutoff='2026-10-24T09:50:00+09:00')
    q['source_snapshot']={'race_id':q['race_id'],'source_freeze_at':'2026-10-24T09:00:00+09:00','jra_race_context':{'surface':'ダ','distance_m':1400,'going':'稍重','venue_name':'東京','race_class':'1勝クラス'},'jra_official_horse_history':{'runners':{str(n):{'official':True,'runs':[{'date':'2026-10-10','surface':'ダ','distance_m':1400,'venue':'東京','going':'稍重','race_name':'1勝クラス','finish':n,'field_size':10}]} for n in range(1,5)}}}
    return q

def test_all_horses_and_distinct_ticket_universe_no_money_authority():
    q=request();r=predict(q)
    for arm in r['arms'].values():
        assert all(set(arm['ranking'][role])=={'1','2','3','4'} for role in ROLES)
        for t in arm['ticket_candidates']:
            assert len(t['selection'])==len(set(t['selection']))
            assert set(t['selection'])<={1,2,3,4}
            assert 'stake' not in t
        assert arm['metadata']['purchase_authority'] is False
        assert arm['metadata']['genuine_forward_oos_credit']==0

def test_outcome_injection_cannot_change_prediction():
    q=request();r=predict(q);q['official_result']={'top3':[1,2,3],'payout':10**9};q['finish_order']=[4,3,2,1]
    z=predict(q)
    assert {k:v['ranking'] for k,v in r['arms'].items()}=={k:v['ranking'] for k,v in z['arms'].items()}
    assert {k:v['ticket_candidates'] for k,v in r['arms'].items()}=={k:v['ticket_candidates'] for k,v in z['arms'].items()}

def test_future_or_current_day_history_is_excluded():
    q=request();horse=q['runners'][0];h=q['source_snapshot']['jra_official_horse_history']['runners']['1'];before=history_measure(q,horse)
    h['runs'] += [{'date':day,'surface':'ダ','distance_m':1400,'venue':'東京','going':'稍重','finish':1,'field_size':18} for day in ['2026-10-24','2026-10-25']]
    after=history_measure(q,horse)
    assert before['value']==after['value'] and before['observations']==after['observations']
    assert len(after['excluded'])==2

def test_missing_history_does_not_become_weak_and_input_stays_immutable():
    q=request();q['source_snapshot']['jra_official_horse_history']['runners'].pop('1');before=digest(q);r=predict(q)
    assert digest(q)==before
    assert r['all_runner_diagnostics']['1']['history']['value'] is None
    assert r['all_runner_diagnostics']['1']['history']['status']=='OFFICIAL_HISTORY_UNAVAILABLE'

def test_source_after_cutoff_is_rejected():
    q=request();q['source_snapshot']['source_freeze_at']='2026-10-24T09:51:00+09:00'
    with pytest.raises(ValueError,match='RESEARCH_SOURCE_TIME_OR_ID'):predict(q)

def test_bvi_ablation_keeps_original_ledger_dcr_and_other_base_values():
    q=request();before=deepcopy(q);bvi_scores(q)
    assert q==before
    assert all(q['runners'][i]['canonical_components']['DCR']['value']==before['runners'][i]['canonical_components']['DCR']['value'] for i in range(4))

def test_duplicate_runner_fails_before_candidate_generation():
    q=request();q['runners'].append(deepcopy(q['runners'][0]))
    with pytest.raises(ValueError,match='RANK_DUPLICATE_RUNNER'):predict(q)

def test_final_source_mismatch_is_rejected():
    q=request();f={'race_id':q['race_id'],'prediction_cutoff':q['prediction_cutoff'],'source_snapshot_sha256':'b'*64}
    with pytest.raises(ValueError,match='RESEARCH_FINAL_INPUT_BINDING'):predict(q,f)


def test_source_universe_mismatch_is_rejected():
    q=request();q['source_snapshot']['official_runner_universe']={
        'runners':[{'runner_id':'1'},{'runner_id':'2'},{'runner_id':'3'}]}
    with pytest.raises(ValueError,match='RESEARCH_SOURCE_RUNNER_UNIVERSE'):predict(q)


@pytest.mark.parametrize(('name','expected'),[
    ('GⅠ',6),('ＧⅡ',5),('G III',4),('G3',4),('オープン',3.5),
    ('2勝クラス',2),('未勝利',0),('クラス情報なし',None)])
def test_history_class_symbols_are_distinct(name,expected):
    assert class_ordinal(name)==expected


def test_protected_pair_and_third_are_accepted_but_unconverted_exact_is_distinct():
    q=request();roles={'1':['W'],'2':['P2'],'3':['P3'],'4':[]}
    final={'static_prediction':{'ranking':['1','2','3','4']},
           'pair_dispositions':[{'head':'1','second':'2','status':'PROTECT'}],
           'third_dispositions':[{'head':'1','second':'2','third':'3','status':'PROTECT'}],
           'final_ticket':{'tickets':[{'bet_type':'EXACTA','selection':[1,2],'stake':100},
                                      {'bet_type':'TRIO','selection':[1,2,3],'stake':100}]}}
    row={'race_id':q['race_id'],'venue':'TKY','kind':'FORMAL_FINAL',
         'q':q,'f':final,'baseline_roles':roles,'top3':['1','2','3'],
         'provenance':{'fixture':True}}
    result=failure_matrix(row,{str(n):{} for n in range(1,5)})
    assert result['first_prediction_failure']=='PROTECTED_EXACT_NOT_CONVERTED'
    assert result['correct_ticket_present']=={'EXACTA':True,'TRIFECTA':False,'TRIO':True}
    final['final_ticket']['tickets'].append({'bet_type':'TRIFECTA','selection':[1,2,3],'stake':100})
    assert failure_matrix(row,{str(n):{} for n in range(1,5)})['first_prediction_failure']=='ORDERED_EXACT_CAPTURED'


def test_archived_input_binding_does_not_qualify_new_candidates_or_read_new_states(tmp_path):
    rid='KM-JRA-TKY-20261024-R01';f={'sha256':'f'*64,'source_snapshot_sha256':'s'*64}
    old={'race_id':rid,'baseline_final_sha256':f['sha256'],'source_sha256':f['source_snapshot_sha256'],
         'prediction_input_sha256':'p'*64,'checkpoint_learning_input_sha256':'l'*64,
         'learning_state_bindings':[{'state_id':'ORIGINAL','state_sha256':'o'*64}]}
    old['sha256']=digest(old)
    directory=tmp_path/'runtime/role_rescue_shadow';directory.mkdir(parents=True)
    path=directory/(rid+'.json');path.write_text(json.dumps(old))
    fresh=tmp_path/'runtime/learning_states';fresh.mkdir();(fresh/'new.json').write_text('INVALID STATE MUST NOT BE READ')
    lineage=archived_shadow_lineage(tmp_path,rid,f)
    assert lineage['original_prediction_input_sha256']=='p'*64
    assert lineage['original_learning_state_bindings']==old['learning_state_bindings']
    assert lineage['does_not_witness_new_research_candidate_freeze'] is True
    assert lineage['fresh_states_read']==0
    old['prediction_input_sha256']='tampered';path.write_text(json.dumps(old))
    with pytest.raises(ValueError,match='REPLAY_ORIGINAL_SHADOW_HASH'):
        archived_shadow_lineage(tmp_path,rid,f)
