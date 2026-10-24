"""ENV freeze boundary regressions. Synthetic clocks are NEVER actual OOS."""
from copy import deepcopy
from datetime import datetime
import importlib.util
import json
from pathlib import Path
import shutil

import pytest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('bvi_env_forward',ROOT/'scripts/jra_bvi_pipeline_forward_shadow.py')
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)


def model_fixture():
    from jra_bvi_env_shadow import train_model
    rows=[]
    for i in range(4):
        for date in ('2026-01-03','2026-03-03','2026-06-03','2026-09-03'):
            rows.append({'horse_id':'synthetic-'+str(i),'sire':'UNIT-SIRE','dam':'UNIT-DAM-'+str(i),
                'damsire':'UNIT-DAMSIRE','date':date,'venue':'京都','surface':'芝','distance_m':1600,
                'going':'良','race_name':'2勝クラス','finish':i+1,'field_size':12,
                'available_at':'2026-10-24T10:00:00Z'})
    data={'prediction_cutoff':'2026-10-24T10:00:00Z','race_date':'2026-10-25',
        'manifest_sha256':'a'*64,'rows':rows}
    return train_model(data,train_before='2026-10-25')


@pytest.fixture
def published_boundary(tmp_path,monkeypatch):
    for name in f.ENV_CODE_FILES:
        target=tmp_path/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/name,target)
    def publication_git(args,**kwargs):
        if args[1]=='rev-parse':return 'c'*40
        if args[1]=='show':return (tmp_path/args[2].split(':',1)[1]).read_bytes()
        raise AssertionError(args)
    monkeypatch.setattr(f.subprocess,'check_output',publication_git)
    publication=f.environment_model_publication(model_fixture(),root=tmp_path,
        frozen_at='2026-10-24T10:01:00Z')
    path=tmp_path/'research/model.json';path.parent.mkdir();path.write_text(json.dumps(publication))
    req={'race_date':'2026-10-25','prediction_cutoff':'2026-10-25T00:00:00Z'}
    def git(args,**kwargs):
        if args[1]=='log':return '2026-10-24T10:02:00Z'
        if args[1]=='show':
            name=args[2].split(':',1)[1]
            return (tmp_path/name).read_bytes()
        raise AssertionError(args)
    monkeypatch.setattr(f.subprocess,'check_output',git)
    return path,req,publication,tmp_path


def test_published_model_uses_actual_publication_clock_and_preserves_core(published_boundary):
    path,req,original,root=published_boundary
    publication,binding=f.load_environment_model_publication(path,req,root=root,
        now=datetime.fromisoformat('2026-10-24T10:03:00+00:00'))
    assert publication==original
    assert binding['published_at']=='2026-10-24T10:02:00Z'
    assert binding['frozen_at']!=publication['model']['training_label_max']
    assert not publication['production_authority']


@pytest.mark.parametrize('mutation',['post_acquisition','future_model_clock','future_label','code_tamper','core_tamper'])
def test_future_or_changed_model_cannot_freeze(published_boundary,mutation):
    from jra_bvi_env_shadow import sha
    path,req,publication,root=published_boundary
    if mutation=='post_acquisition':publication['frozen_at']='2026-10-24T09:59:00Z'
    elif mutation=='future_model_clock':publication['frozen_at']='2026-10-24T10:04:00Z'
    elif mutation=='future_label':
        m=publication['model'];m['training_label_max']='2026-10-25'
        m['model_sha256']=sha({k:v for k,v in m.items() if k!='model_sha256'})
    elif mutation=='code_tamper':publication['code_file_sha256']['runtime/jra_bvi_env_shadow.py']='0'*64
    else:publication['model']['residual_rms']=0
    publication['sha256']=f.sha({k:v for k,v in publication.items() if k!='sha256'})
    path.write_text(json.dumps(publication))
    with pytest.raises(ValueError):
        f.load_environment_model_publication(path,req,root=root,
            now=datetime.fromisoformat('2026-10-24T10:03:00+00:00'))


def test_uncommitted_model_publication_is_not_forward_evidence(published_boundary,monkeypatch):
    path,req,publication,root=published_boundary
    actual=f.subprocess.check_output
    def git(args,**kwargs):
        if args[1]=='show' and args[2]=='HEAD:research/model.json':return b'{}'
        return actual(args,**kwargs)
    monkeypatch.setattr(f.subprocess,'check_output',git)
    with pytest.raises(ValueError,match='PUBLICATION_NOT_COMMITTED'):
        f.load_environment_model_publication(path,req,root=root,
            now=datetime.fromisoformat('2026-10-24T10:03:00+00:00'))


def test_weather_does_not_fill_going_in_target_environment():
    model=model_fixture()
    source={'prediction_cutoff':'2026-10-25T00:00:00Z',
        'jra_race_context':{'official':True,'production_fact_authority':True,'race_date':'2026-10-25',
            'venue_name':'京都','surface':'芝','distance_m':1600,'weather':'雨'},
        'jra_official_race_card_detail':{'runners':[{'runner_id':'1','sire':'UNIT-SIRE',
            'dam':'UNIT-NEW-DAM','damsire':'UNIT-DAMSIRE'}]}}
    predictions,environment=f.environment_predictions_for_source(model,source)
    assert environment['going'] is None and environment['weather']=='雨'
    assert 'going' in predictions['1']['missing_environment']
    assert predictions['1']['input']['environment']['race_date']=='2026-10-25'


def test_target_source_history_and_field_size_reach_model_without_future_results():
    from jra_bvi_env_shadow import predict
    model=model_fixture()
    context={'official':True,'production_fact_authority':True,'race_date':'2026-10-25',
        'venue_name':'京都','surface':'芝','distance_m':1600,'going':'良','race_class':'2勝クラス'}
    recent=[{'date':'2026-10-01','finish':2,'field_size':12},
        {'date':'2026-10-25','finish':1,'field_size':12},
        {'date':'2026-10-26','finish':1,'field_size':12}]
    runner={'runner_id':'1','horse_name':'UNIT-HORSE','sire':'UNIT-SIRE',
        'dam':'UNIT-NEW-DAM','damsire':'UNIT-DAMSIRE','recent_runs':recent}
    source={'race_id':'KM-JRA-KYO-20261025-R01','prediction_cutoff':'2026-10-25T00:00:00Z',
        'jra_official_race_card_detail':{'race_context':context,'runners':[runner]}}
    predictions,environment=f.environment_predictions_for_source(model,source)
    expected=deepcopy(runner);expected['runs']=deepcopy(recent)
    direct=predict(model,expected,environment)
    assert predictions['1']['control_score']==direct['control_score']
    assert predictions['1']['input']['runner']['runs']==recent
    assert environment['field_size']==1
    changed=deepcopy(source)
    changed['jra_official_race_card_detail']['runners'][0]['recent_runs']=recent[:1]
    without_future,_=f.environment_predictions_for_source(model,changed)
    assert predictions['1']['control_score']==without_future['1']['control_score']
    assert predictions['1']['score']==without_future['1']['score']


def test_verified_profile_history_supersedes_card_recent_runs_and_checks_identity():
    model=model_fixture()
    context={'official':True,'production_fact_authority':True,'race_date':'2026-10-25',
        'venue_name':'京都','surface':'芝','distance_m':1600,'going':'良'}
    runner={'runner_id':'1','horse_name':'UNIT-HORSE','sire':'UNIT-SIRE','dam':'UNIT-NEW-DAM',
        'recent_runs':[{'date':'2026-10-01','finish':12,'field_size':12}]}
    source={'prediction_cutoff':'2026-10-25T00:00:00Z','jra_race_context':context,
        'jra_official_race_card_detail':{'runners':[runner]},
        'jra_official_horse_history':{'runners':{'1':{'horse_name':'UNIT-HORSE',
            'pedigree':{'sire':'UNIT-SIRE','dam':'UNIT-NEW-DAM','damsire':'UNIT-DAMSIRE'},
            'runs':[{'date':'2026-10-01','finish':1,'field_size':12}]}}}}
    predictions,_=f.environment_predictions_for_source(model,source)
    assert predictions['1']['input']['runner']['runs'][0]['finish']==1
    assert predictions['1']['input']['runner']['damsire']=='UNIT-DAMSIRE'
    source['jra_official_horse_history']['runners']['1']['pedigree']['sire']='WRONG-SIRE'
    with pytest.raises(ValueError,match='HISTORY_PARENT_CONFLICT'):
        f.environment_predictions_for_source(model,source)
    source['jra_official_horse_history']['runners']['1']['horse_name']='DIFFERENT-HORSE'
    with pytest.raises(ValueError,match='HISTORY_NAME_CONFLICT'):
        f.environment_predictions_for_source(model,source)


def test_target_context_conflicts_are_not_selected_away():
    model=model_fixture()
    context={'official':True,'production_fact_authority':True,'race_date':'2026-10-25',
        'venue_name':'京都','surface':'芝','distance_m':1600,'going':'良'}
    source={'prediction_cutoff':'2026-10-25T00:00:00Z','jra_race_context':context,
        'jra_official_race_card_detail':{'race_context':dict(context,going='重'),
            'runners':[{'runner_id':'1','sire':'UNIT-SIRE','dam':'UNIT-NEW-DAM'}]}}
    with pytest.raises(ValueError,match='ENVIRONMENT_CONFLICT:going'):
        f.environment_predictions_for_source(model,source)


def test_environment_cohort_does_not_change_with_ticket_count_or_result():
    binding={'model_sha256':'m'*64,'code_file_sha256':{'x':'c'*64}}
    protocol={'profile':'ENV','equal_budget':'COMMON_BUDGET','equal_ticket_rule':'FROZEN_PREFIX',
        'equal_ticket_count':5,'equal_ticket_subset_hashes':{'D':'t'*64}}
    before=f.environment_cohort_fingerprint('p'*64,binding,protocol)
    protocol['equal_ticket_count']=30;protocol['equal_ticket_subset_hashes']={'D':'x'*64}
    assert f.environment_cohort_fingerprint('p'*64,binding,protocol)==before
    binding['model_sha256']='n'*64
    assert f.environment_cohort_fingerprint('p'*64,binding,protocol)!=before


def test_three_arm_default_protocol_is_unchanged_and_d_is_explicit():
    from jra_bvi_oos_metrics import ARMS,ENV_ARM,preregister,comparison_arms,aggregate
    tickets=[{'bet_type':'WIN','selection':[1],'stake':100}]
    abc={'arms':{name:{'diagnostic_tickets':deepcopy(tickets)} for name in ARMS}}
    old=preregister(abc)
    assert old['profile']=='KM-JRA-BVI-CONTROLLED-COMPARISON-v1'
    assert 'arm_names' not in old and set(old['equal_ticket_subset_hashes'])==set(ARMS)
    assert set(aggregate([])['arms'])==set(ARMS)
    four=deepcopy(abc);four['arms'][ENV_ARM]={'diagnostic_tickets':deepcopy(tickets),
        'environment_shadow_proof':{'model_sha256':'d'*64}}
    new=preregister(four)
    assert new['profile']=='KM-JRA-BVI-ENV-CONTROLLED-COMPARISON-v1'
    assert new['arm_names']==list(ARMS)+(list((ENV_ARM,)))
    assert new['environment_model_sha256']=='d'*64
    assert len(aggregate([],include_environment=True)['arms'])==4
    four['arms']['UNKNOWN']={}
    with pytest.raises(ValueError,match='ARM_SET_INVALID'):comparison_arms(four)


def test_environment_requires_distinct_output_before_any_network(monkeypatch,tmp_path):
    req={'race_date':'2026-10-25','race_id':'KM-JRA-UNIT-R01','family_id':'JRA',
        'temporal_mode':'FORMAL-PRE-RACE','prediction_cutoff':'2099-10-25T00:00:00Z',
        'scheduled_post_at':'2099-10-25T00:05:00Z'}
    path=tmp_path/'req.json';path.write_text(json.dumps(req))
    monkeypatch.setattr(f.urllib.request,'urlopen',lambda *a,**kw:pytest.fail('No network on output rejection'))
    with pytest.raises(ValueError,match='SEPARATE_IMMUTABLE_OUTPUT_REQUIRED'):
        f.freeze(path,tmp_path/'source.json',tmp_path/'pedigree_pipeline_pre_result.json',
            environment_model_path=tmp_path/'model.json')


def test_environment_empty_cohort_is_pending_without_inflating_abc(tmp_path):
    score=f.settle(tmp_path,include_environment=True)
    assert score['eligible_settled_races']==0 and len(score['arms'])==3
    env=score['environment_candidate']
    assert env['eligible_settled_races']==0 and env['required_forward_races']==30
    assert env['status']=='FORWARD OOS PENDING' and len(env['arms'])==4
    assert not env['automatic_promotion']
    assert json.loads((tmp_path/'runtime/jra_static_owner_forward_oos/pedigree_env_current.json').read_text())==env


def test_distinct_model_cohorts_cannot_satisfy_thirty_by_pooling(monkeypatch):
    from jra_bvi_oos_metrics import ARMS,ENV_ARM
    monkeypatch.setattr(f,'policy_fingerprint',lambda:'CURRENT')
    records=[]
    for cohort in ('model-one','model-two'):
        for i in range(20):
            records.append({'race_id':cohort+'-'+str(i),'policy_fingerprint':cohort,
                'base_policy_fingerprint':'CURRENT','result_captured_at':'2026-10-25T08:00:00Z',
                'environment_candidate':{'model_sha256':cohort,
                    'target_environment':{'venue':'京都','surface':'芝','distance_m':1600,'going':'良'}},
                'arms':{name:{'settlement':{'investment':100,'return':0,'profit_loss':-100}}
                    for name in ARMS+(ENV_ARM,)}})
    score=f.environment_scorecard(records,[])
    assert score['unpooled_race_count']==40
    assert score['eligible_settled_races']==20 and score['status']=='FORWARD OOS PENDING'
    assert all(g['eligible_settled_races']==20 for g in score['cohorts'].values())
    assert not score['automatic_promotion']


def test_equal_budget_robustness_keeps_same_four_arm_races_and_excludes_no_bet():
    from jra_bvi_oos_metrics import ARMS,ENV_ARM
    names=ARMS+(ENV_ARM,)
    records=[{'race_id':str(i),'result_captured_at':f'2026-10-25T0{i}:00:00Z'} for i in (1,2,3)]
    evaluations=[]
    for i,ratio in ((1,4.0),(2,0.0),(3,2.0)):
        evaluations.append({'race_id':str(i),'arms':{name:{'equal_budget_return_per_yen':ratio} for name in names},
            'equal_ticket':{'status':'FROZEN_PREFIX_DIAGNOSTIC','arms':{name:{'investment':100,
                'return':100*ratio,'profit_loss':100*ratio-100} for name in names}}})
    evaluations[2]['arms'][ENV_ARM]['equal_budget_return_per_yen']=None
    measured=f.environment_controlled_pfs(records,evaluations)
    assert measured['fractional_diagnostic_only']
    for name in names:
        arm=measured['equal_budget'][name]
        assert arm['aggregate']['race_count']==2
        assert arm['aggregate']['investment_weighted_pfs']==200.0
        assert arm['robustness']['excluding_largest_return']['investment_weighted_pfs']==0.0
        assert measured['equal_ticket_count'][name]['aggregate']['race_count']==3


def test_result_receipt_can_bind_only_explicit_environment_preregistration(tmp_path):
    directory=tmp_path/'runtime/jra_static_owner_forward_oos/KM-JRA-FUTURE-RACE'
    directory.mkdir(parents=True)
    (directory/'pedigree_env_pre_result.json').write_text('{}')
    request={'race_id':'KM-JRA-FUTURE-RACE','result_lane':'PRODUCTION','official_result':{'top3':[1,2,3]}}
    f.persist_result_receipt(request,{'receipt':'UNIT_BOUNDARY_NOT_REAL_SIGNATURE'},tmp_path)
    assert (directory/'production_result_receipt.json').exists()
    assert not (directory/'pedigree_pipeline_pre_result.json').exists()
