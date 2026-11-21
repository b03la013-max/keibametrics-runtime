"""Research mechanics; synthetic examples are never genuine OOS samples."""
from pathlib import Path
import copy
import importlib.util
import json
import sys

import pytest

PATH=Path(__file__).resolve().parents[1]/'research/jra_bvi_next/candidate.py'
spec=importlib.util.spec_from_file_location('bvi_next',PATH)
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
sys.path.insert(0,str(PATH.parent))
import connection_audit as connection


@pytest.mark.parametrize('name,surface,expected',[
 ('障害未勝利','芝',True),('中山グランドJ','芝',True),('東京HJ','芝',True),
 ('阪神スプリングJ','芝',True),('東京優駿','芝',False),('菊花賞','芝',False),
 ('一般競走','芝ダ',True),('ペガサスJS','芝',True),('1勝クラス','ダ',False)])
def test_explicit_domain_classifier_uses_race_name_not_distance(name,surface,expected):
    assert c.is_explicit_jump({'race_name':name,'surface':surface,'distance_m':3000})==expected


def test_independent_offspring_not_run_count_controls_role_rescue():
    roles={'W':['1'],'P2':['1','2'],'P3':['2','3']};before=copy.deepcopy(roles)
    cases=[{'runner_id':'4','minimum_general_offspring':3,'minimum_environment_offspring':300,
            'environment_lower_proxy':0.05,'environment_effect':0.1}]
    proposal=c.role_audit_proposal(roles,cases)
    assert proposal['p3_rescue']==[] and roles==before
    cases[0]['minimum_general_offspring']=4
    assert c.role_audit_proposal(roles,cases)['p3_rescue']==['4']


def test_proposal_is_bounded_deterministic_and_has_no_exclusion_or_ticket_authority():
    roles={'W':['1'],'P2':['2'],'P3':['3']}
    candidates=[{'runner_id':str(i),'minimum_general_offspring':4,'minimum_environment_offspring':4,
                 'environment_effect':0.05,'environment_lower_proxy':0.01} for i in (5,4)]
    before=copy.deepcopy((roles,candidates))
    proposal=c.role_audit_proposal(roles,candidates)
    assert proposal['p3_rescue']==['4']
    assert proposal['roles']=={'W':['1'],'P2':['2'],'P3':['3','4']}
    assert proposal['candidate_width_increment']==1
    assert not proposal['production_authority'] and not proposal['purchase_authority']
    assert proposal['exclusions']==[]
    assert (roles,candidates)==before


def test_unsupported_or_zero_lower_proxy_never_upgrades_a_horse():
    base={'runner_id':'9','minimum_general_offspring':99,'minimum_environment_offspring':99,
          'environment_effect':0.1,'environment_lower_proxy':0.0}
    assert c.role_audit_proposal({'W':['1']},[base])['p3_rescue']==[]


@pytest.mark.parametrize('unknown',[None,float('nan'),float('inf'),float('-inf'),True,'0.1'])
def test_unknown_or_nonfinite_proxy_cannot_become_a_rescue(unknown):
    base={'runner_id':'9','minimum_general_offspring':99,'minimum_environment_offspring':99,
          'environment_effect':0.1,'environment_lower_proxy':unknown}
    assert c.role_audit_proposal({'W':['1']},[base])['p3_rescue']==[]


def test_cluster_interval_not_run_independence_or_calibrated_ci():
    rows=[{'horse_id':h,'sire':'S','target':0.3} for h in ['A','A','B','B']]
    out=c.cluster_interval(rows,[0.4]*4,[0.5]*4,'horse_id')
    assert out['n_clusters']==2 and out['resamples']==300
    assert not out['calibrated'] and out['upper_97_5pct']<0


def test_permutation_is_protocol_fixed_and_no_promotion():
    assert c.PROTOCOL['negative_control'].endswith('20261025')
    assert not c.PROTOCOL['hyperparameter_search']
    assert not c.PROTOCOL['automatic_promotion']
    assert c.sha(c.PROTOCOL)==c.sha(json.loads(json.dumps(c.PROTOCOL)))


def test_term_separates_sire_and_damsire_and_does_not_infer_weather():
    row={'sire':'S','damsire':'D','surface':'芝','venue':'東京','distance_m':1800,'going':None,'date':'2026-08-01'}
    assert c.term(row,'sire_damsire_pair')==('S','D')
    assert c.term(row,'sire_distance')==('S','芝',1600)
    assert c.term(row,'damsire_distance')==('D','芝',1600)
    assert c.term(row,'sire_going') is None
    assert c.term(row,'season')==(3,'芝')


def test_partial_pooling_weights_repeat_runs_as_two_horses_not_101_offspring():
    class Fixed:
        def _fit_stage(self,rows,weights,targets,stage):
            return {'terms':[],'converged':True},[0.5]*len(rows)
    rows=[{'horse_id':'A','sire':'S','damsire':'D','target':1.,'surface':'芝','venue':'東京','distance_m':1600,'going':'良'} for _ in range(100)]
    rows.append({**rows[0],'horse_id':'B','target':0.})
    model=c.fit(rows,Fixed(),include_environment=False)
    assert model['training_runs']==101 and model['training_composite_horses']==2
    assert model['training_horse_weight']==pytest.approx(2.)
    sire=model['stages'][0]['terms'][('S',)]
    assert sire['composite_offspring']==2 and sire['runs']==101
    assert sire['effect']==pytest.approx(0.,abs=1e-12)
    assert sire['shrinkage']==pytest.approx(2/14)
    assert sire['permanent_independent_offspring'] is None


def test_unconverged_control_cannot_publish_a_candidate():
    class Fixed:
        def _fit_stage(self,*args):
            return {'terms':[],'converged':False},[0.5]
    with pytest.raises(ValueError,match='CONTROL_NOT_CONVERGED'):
        c.fit([{'horse_id':'A','target':1.}],Fixed())


@pytest.mark.parametrize('se',[None,float('nan'),float('inf'),-0.1])
def test_missing_term_uncertainty_stays_unknown(se):
    effect,upper,lower=connection.environment_band([{'effect':0.05,'standard_error_proxy':se}])
    assert effect==0.05 and upper is None and lower is None


def test_missing_outcome_is_null_not_zero_rescue():
    summary=connection.summarize_outcomes([{'status':'ARCHIVED_RESULT_MISSING','unevaluated_rescues':1}])
    assert summary['qualified_archived_result_races']==0
    assert summary['unknown_archived_result_races']==1
    assert summary['unevaluated_rescues']==1
    assert summary['correct_P3_rescues'] is None and summary['false_P3_rescues'] is None


def test_mixed_outcomes_report_observed_counts_and_unknown_denominator():
    rows=[{'status':'ARCHIVED_RESULT_MISSING','unevaluated_rescues':1},
          {'status':'ARCHIVED_OFFICIAL_LABEL_READ; NOT_INDEPENDENTLY_REVERIFIED_HERE',
           'P3_correct_rescue':0,'false_P3_rescue':1,'false_top3_candidate_additions':1}]
    summary=connection.summarize_outcomes(rows)
    assert summary['qualified_archived_result_races']==1 and summary['unknown_archived_result_races']==1
    assert summary['false_P3_rescues']==1 and summary['unevaluated_rescues']==1
