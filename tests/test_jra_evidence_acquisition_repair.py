"""Regression checks for real observed SOURCE acquisition defects."""
import copy
import json
import gzip
import base64
from pathlib import Path
import sys
from datetime import date
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'runtime/jra_source_runtime')]
from jra_official_fact_evaluator_production import _observed_runs
from jra_registered_common import parse_speed,enrich_with_registered_common


def test_detail_join_requires_full_run_identity_and_does_not_mutate():
    row={'date':'2026-09-01','venue':'京都','surface':'ダ','distance_m':1400,'finish':2,'field_size':16,'going':'良','rating':90}
    history={'runs':[row]}; detail={'recent_runs':[{**row,'final3f':36.5,'margin':0.2}]}
    original=copy.deepcopy(history)
    actual=_observed_runs(history,detail,date(2026,10,10))
    assert actual[0]['final3f']==36.5 and actual[0]['rating']==90
    assert history==original
    detail['recent_runs'][0]['distance_m']=1800
    assert 'final3f' not in _observed_runs(history,detail,date(2026,10,10))[0]
    detail['recent_runs'][0]['distance_m']=1400
    detail['recent_runs'].append(copy.deepcopy(detail['recent_runs'][0]))
    assert 'final3f' not in _observed_runs(history,detail,date(2026,10,10))[0]


def test_real_signed_speed_snapshot_has_three_runners_not_fake_four_and_real_average():
    path=next((ROOT/'runtime/executions/KM-JRA-KYO-20261010-R09-LIVE-R1/SOURCE/runs').glob('*/source_receipt_envelope.json'))
    source=json.loads(path.read_text())['artifact']
    snap=next(x for x in source['sources'] if x.get('source_id')=='NETKEIBA-SPEED-PAST')
    parsed=parse_speed(gzip.decompress(base64.b64decode(snap['raw_gzip_b64'])),snap['content_type'])
    assert parsed['runner_count']==3
    assert [x['five_run_average_raw'] for x in parsed['runners']]==['74','81','81']
    assert all(x['horse_name']!='2走前' for x in parsed['runners'])
    # Partial public data remains partial and is never a full official universe.
    assert parsed['runner_count']<source['jra_official_runner_universe']['runner_count']


def test_speed_is_fetched_even_when_workout_fails_and_requirement_is_retained():
    artifact={'source_race_context':{'venue_id':'KYO','race_date':'2026-10-10','race_no':9},'jra_official_runner_universe':{'runners':[]}}
    calls=[]
    def fetch(url,*args):
        calls.append(url)
        if 'speed.html' not in url: raise ValueError('WORKOUT_UNAVAILABLE')
        return b'x',{'content-type':'text/html'},{'snapshot_sha256':'s'}
    with patch('jra_registered_common._discover_race_id',return_value=('202608040309',None)),patch('jra_registered_common._fetch',side_effect=fetch),patch('jra_registered_common.parse_speed',return_value={'runners':[]}),patch('jra_registered_common._reconcile',return_value={'verified':True}):
        actual,errors=enrich_with_registered_common(artifact,'2026-10-10T14:00:00+09:00',require_workout=True)
    assert any('speed.html' in x for x in calls)
    assert actual['jra_registered_common']['speed']['runner_universe_match']['verified']
    assert actual['jra_registered_common']['status']=='PARTIAL'
    assert errors and 'WORKOUT' in errors[0]


def test_closing_percentile_requires_observed_comparable_peers():
    from test_jra_official_fact_evaluator_production import source
    from jra_official_fact_evaluator_production import official_production_observations
    registry=json.loads((ROOT/'mapping/jra_evidence_feature_rule_registry_v1.1_20260922.json').read_text())
    s=source(); s['jra_official_runner_universe']['runners']=[];s['jra_official_horse_history']['runners']={};s['jra_official_race_card_detail']['runners']=[]
    for i in range(1,5):
        rid=str(i);s['jra_official_runner_universe']['runners'].append({'runner_id':rid})
        rows=[{'date':day,'venue':'東京','surface':'芝','distance_m':1800,'going':'良','finish':i,'field_size':10}
              for day in ('2026-09-01','2026-09-10')]
        s['jra_official_horse_history']['runners'][rid]={'runs':rows}
        s['jra_official_race_card_detail']['runners'].append({'runner_id':rid,'recent_runs':[{**r,'final3f':34.0+i} for r in rows]})
    observations=official_production_observations(s,registry)
    assert observations['1']['closing_quality']['category']=='EXCEPTIONAL'
    assert observations['4']['closing_quality']['category']=='VERY_WEAK'
    assert observations['1']['closing_quality']['observation_count']==2
    s['jra_official_race_card_detail']['runners'][-1]['recent_runs'][0]['going']='重'
    assert all('closing_quality' not in r for r in official_production_observations(s,registry).values())
