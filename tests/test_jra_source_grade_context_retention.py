"""Observed SOURCE grade/context repair; no legacy original or Physics mutation."""
import base64
from copy import deepcopy
import gzip
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
DATA=Path(os.environ.get('KM_LINEAGE_DATA_ROOT',str(ROOT)))
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'runtime/jra_source_runtime')]

from jra_source_runtime.source_acquisition import _OfficialGradeTableExtractor, _html_tables
from jra_source_runtime.jra_race_card_detail import parse_race_card_detail
from jra_horse_history import parse_horse_history
from jra_krs_input_builder_production import build_krs_input
from jra_official_fact_evaluator_production import official_production_observations
from jra_source_runtime.source_acquisition import sha_obj
from jra_registered_common import parse_workout
from jra_source_to_evidence_features import _registered_common_workout_features


def fixture_request(venue='TKY',number=11):
    return json.loads((DATA/'runtime/requests'/f'KM-JRA-{venue}-20261024-R{number:02d}-LIVE-R1-FORMAL.json').read_text())


def raw_detail(source):
    sha=source['jra_official_race_card_detail']['source_snapshot_sha256']
    snap=next(x for x in source['sources'] if x['snapshot_sha256']==sha)
    raw=gzip.decompress(base64.b64decode(snap['raw_gzip_b64']))
    assert hashlib.sha256(raw).hexdigest()==snap['raw_sha256']
    return raw,snap['content_type']


def test_grade_retention_is_opt_in_and_exact():
    markup='<table><tr><td>七夕賞<img alt="G&#8546;"></td><td>白富士S<img alt="リステッド"></td><td><img alt="勝馬GⅠ"></td></tr></table>'
    assert _html_tables(markup)==[[['七夕賞','白富士S','']]]
    parser=_OfficialGradeTableExtractor();parser.feed(markup)
    assert parser.tables==[[['七夕賞 GⅢ','白富士S リステッド','']]]


def test_actual_kyoto11_printed_grades_retained_without_changing_context():
    source=fixture_request('KYO',11)['source_snapshot'];before=deepcopy(source)
    raw,ctype=raw_detail(source);reparsed=parse_race_card_detail(raw,ctype)
    row=reparsed['runners'][0]
    assert [x['race_class_text'] for x in row['recent_runs'][:4]]==[
        '七夕賞 GⅢ','都大路S リステッド','白富士S リステッド','エリザベス杯 GⅠ']
    assert reparsed['race_context']==source['jra_official_race_card_detail']['race_context']
    assert source==before
    history=source['jra_official_horse_history']['runners']['1']
    snap=next(x for x in source['sources'] if x.get('snapshot_sha256')==history['source_snapshot_sha256'])
    parsed=parse_horse_history(gzip.decompress(base64.b64decode(snap['raw_gzip_b64'])),snap['content_type'])
    assert [x['race_name'] for x in parsed['runs'][:4]]==[
        '七夕賞 GⅢ','都大路S リステッド','白富士S リステッド','エリザベス杯 GⅠ']


def test_actual_source_weather_going_and_class_reach_krs_without_hsv_changes():
    request=fixture_request();before=deepcopy(request)
    assert request['krs_input_data']['environment']['weather']=='unknown'
    assert request['krs_input_data']['race']['going'] is None
    result=build_krs_input(request)
    assert result['krs_input_data']['environment']['weather']=='雨'
    assert result['krs_input_data']['race']['going']=='稍重'
    assert result['krs_input_data']['race']['class']=='オープン'
    assert result['krs_input_data']['horses']==request['krs_input_data']['horses']
    assert result['krs_input_data']['simulation']==request['krs_input_data']['simulation']
    assert request==before


def test_explicit_environment_is_preserved():
    request=fixture_request();request['environment']={'weather':'cloudy','scenario':'explicit-control'}
    request['race']['going']='explicit-control'
    result=build_krs_input(request)
    assert result['krs_input_data']['environment']==request['environment']
    assert result['krs_input_data']['race']['going']=='explicit-control'


def test_unbound_or_post_cutoff_context_cannot_fill_krs():
    for kind in ['sha','race','time','timezone']:
        request=fixture_request();source=request['source_snapshot']
        if kind=='sha':source['source_snapshot_sha256']='0'*64
        if kind=='race':source['race_id']='ANOTHER_RACE'
        if kind=='time':source['source_freeze_at']='2026-10-24T16:00:00+09:00'
        if kind=='timezone':source['source_freeze_at']='2026-10-24T14:00:00'
        if kind!='sha':
            request['source_snapshot_sha256']=sha_obj({k:v for k,v in source.items() if k!='source_snapshot_sha256'})
        result=build_krs_input(request)
        assert result['krs_input_data']['environment']['weather']=='unknown'
        assert result['krs_input_data']['race']['going'] is None
        assert result['krs_input_data']['horses']==request['krs_input_data']['horses']
        expected={'sha':'NO_BOUND_SOURCE_CONTEXT','race':'NO_BOUND_SOURCE_CONTEXT',
                  'time':'SOURCE_CONTEXT_TIME_INELIGIBLE','timezone':'SOURCE_CONTEXT_TIME_INELIGIBLE'}[kind]
        assert result['explicit_engine_hsv_provenance']['source_context_status']==expected


def test_absent_source_does_not_add_a_new_gate():
    request=fixture_request();request.pop('source_snapshot')
    result=build_krs_input(request)
    assert result['krs_input_data']==request['krs_input_data']


def test_retained_grade_reaches_existing_class_feature_without_new_rule():
    request=fixture_request('KYO',11);original=deepcopy(request['source_snapshot'])
    # Isolated retrospective parser view. No SOURCE/Freeze is minted or saved.
    view=deepcopy(original);view['source_snapshot_sha256']=request['source_snapshot_sha256']
    registry=json.loads((ROOT/'mapping/jra_evidence_feature_rule_registry_v1.3_20261010.json').read_text())
    before=official_production_observations(view,registry)
    history=view['jra_official_horse_history']['runners']['1']
    snap=next(x for x in view['sources'] if x['snapshot_sha256']==history['source_snapshot_sha256'])
    history['runs']=parse_horse_history(gzip.decompress(base64.b64decode(snap['raw_gzip_b64'])),snap['content_type'])['runs']
    after=official_production_observations(view,registry)
    assert 'class_performance' not in before['1']
    assert after['1']['class_performance']['category']=='POSITIVE'
    assert after['1']['class_performance']['rule_id']=='KM-JRA-CLASS-PERFORMANCE-v1'
    assert after['1']['class_performance']['observation_count']==4
    assert {k:v for k,v in after['1'].items() if k!='class_performance'}==before['1']
    assert request['source_snapshot']==original


def test_compact_workout_does_not_promote_horse_name_to_gait():
    request=fixture_request('TKY',4);source=request['source_snapshot'];original=deepcopy(source)
    workout=source['jra_registered_common']['workout']
    snap=next(s for s in source['sources'] if s['snapshot_sha256']==workout['source_snapshot_sha256'])
    parsed=parse_workout(gzip.decompress(base64.b64decode(snap['raw_gzip_b64'])),snap['content_type'],source['jra_official_runner_universe'])
    assert parsed['schema']=='COMPACT_ASSESSMENT' and len(parsed['runners'])==16
    old={x['runner_id']:x for x in workout['runners']}
    view=deepcopy(source);view['jra_registered_common']['workout']['runners']=parsed['runners']
    for row in parsed['runners']:
        assert row['gait']==''
        assert {k:v for k,v in row.items() if k!='gait'}=={k:v for k,v in old[row['runner_id']].items() if k!='gait'}
        before=_registered_common_workout_features(row['runner_id'],source)
        after=_registered_common_workout_features(row['runner_id'],view)
        assert set(after)=={'workout_capability'}
        assert {k:v for k,v in before['workout_capability'].items() if k!='source_fact'}=={k:v for k,v in after['workout_capability'].items() if k!='source_fact'}
        assert row['horse_name'] not in after['workout_capability']['source_fact']
    assert source==original


def test_detailed_workout_reads_printed_gait_column():
    raw='<table><tr><th>馬番</th><th>馬名</th><th>コース</th><th>調教タイム</th><th>脚色</th><th>評価</th></tr><tr><td>1</td><td>テスト</td><td>坂路</td><td>54.0 12.5</td><td>馬なり</td><td>動き良い</td><td>A</td></tr></table>'.encode()
    row=parse_workout(raw,'text/html; charset=utf-8')['runners'][0]
    assert row['gait']=='馬なり' and row['assessment']=='動き良い' and row['rating']=='A'
    assert row['final1f']==12.5
