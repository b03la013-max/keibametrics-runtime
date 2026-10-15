import copy
import pytest
from runtime.jra_keibabook_evaluator_conformance import evaluate

def fixture():
    names=[{'runner_id':str(i),'name':f'馬{i}'} for i in range(1,5)]
    return {'provider':'KEIBABOOK_SMART_PREMIUM','official_universe_matched':True,'temporal_mode':'REPLAY','race_date':'2026-10-10','sources':[{'kind':k,'raw_sha256':k,'captured_at':'2026-10-10T15:00:00+09:00'} for k in ['ability','workout','stable']], 'facts':{
        'ability':[dict(r,prior_runs=[{'date':'2026-09-01','speed_index':60+int(r['runner_id'])},{'date':'2026-09-10','speed_index':65+int(r['runner_id'])}]) for r in names],
        'workout':[dict(r,assessment='好調',observed_workouts=[{'previous_workout':False,'date_course':'10/7 栗ＣＷ','final1f':11.8},{'previous_workout':True,'date_course':'10/9 栗ＣＷ','final1f':10.0}]) for r in names],
        'stable':[dict(r,trainer_comment='順調') for r in names]}}

def test_bands_preserve_origin_and_never_promote():
    result=evaluate(fixture())
    assert len(result['observations'])==4 and not result['production_authority']
    assert result['oos_increment']==0 and not result['signed_final_issued']
    for row in result['observations'].values():
        assert row['workout_speed']['facts_used']['final1f']==11.8
        assert all(x['source_authority']=='KEIBABOOK_SMART_PREMIUM' and x['production_authority'] is False for x in row.values())

def test_future_history_rejected():
    x=fixture();x['facts']['ability'][0]['prior_runs'][0]['date']='2026-10-10'
    with pytest.raises(ValueError,match='FUTURE_RESULT'):evaluate(x)

def test_no_official_universe_no_evaluation():
    x=fixture();x['official_universe_matched']=False
    with pytest.raises(ValueError,match='OFFICIAL_UNIVERSE'):evaluate(x)

def test_unsupported_course_and_target_day_workout_not_neutral():
    x=fixture()
    for row in x['facts']['workout']:
        row['observed_workouts']=[{'date_course':'10/7 芝','final1f':11.0},{'date_course':'10/10 栗ＣＷ','final1f':11.0}]
    result=evaluate(x)
    assert all('workout_speed' not in r for r in result['observations'].values())
    assert len(result['blocked'])==4

def test_every_emitted_rule_is_registered_for_its_feature():
    import json
    from pathlib import Path
    registry=json.loads((Path(__file__).resolve().parents[1]/'mapping/jra_evidence_feature_rule_registry_v1.1_20260922.json').read_text())['feature_rules']
    for row in evaluate(fixture())['observations'].values():
        for feature, observation in row.items():
            assert observation['rule_id'] in registry[feature]
