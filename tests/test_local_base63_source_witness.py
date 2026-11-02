"""Synthetic-only independent source witness tests; never a live prediction."""
import base64
from copy import deepcopy
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path

import pytest

from runtime import local_base63_source_witness as witness

ROOT=Path(__file__).resolve().parents[1]

def registry():
    return json.loads((ROOT/"mapping/local_evidence_feature_rule_registry_v1.1_production_numerical_20261008.json").read_text())

def fixture():
    header='<h4>2026年10月2日 船橋 第4競走 16:15発走</h4><h3>Ｃ３一</h3><li>ダート 1500ｍ（左） 天候：曇 馬場：重</li>'
    rows=[['枠番','馬番','競走馬','騎手']]
    for no in (1,2):
        descriptors=[f'{no} 26.09.{d:02d} 良 5頭 船橋 左1500 {no}番' for d in (25,18,11,4)]+[f'{no} 26.08.28 良 5頭 船橋 左1500 {no}番']
        primary=[str(no),str(no),f'テスト馬{no}',f'テスト騎手{no}','0.0(0人気)']+descriptors
        meta=['牡3','鹿毛','船橋','56.0']+['Ｃ３一']*5
        blood=['テスト父','テスト厩舎','450(+2)']+[f'2人 450 テスト騎手{no} 56.0']*5
        content=['テスト母']+['1:38.0 3-2-2-1 39.0']*5
        margins=['(テスト母父)']+['1.0 テスト勝馬']*5
        rows.extend((primary,meta,blood,content,margins))
    raw=(header+'<table>'+''.join('<tr>'+''.join('<td>'+v+'</td>' for v in r)+'</tr>' for r in rows)+'</table>').encode()
    url='https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/DebaTable?k_raceDate=2026%2F10%2F02&k_raceNo=4&k_babaCode=19'
    card={'source_id':'NAR-FNB-SYNTHETIC','official':True,'source_class':'OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT',
        'requested_url':url,'final_url':url,'raw_gzip_b64':base64.b64encode(gzip.compress(raw)).decode(),
        'raw_sha256':hashlib.sha256(raw).hexdigest(),'fetched_at':'2026-10-02T06:57:00Z'}
    card['snapshot_sha256']=witness.canon_hash(card)
    source={'source_freeze_at':'2026-10-02T06:58:00Z','prediction_cutoff':'2026-10-02T07:05:00Z',
        'source_snapshot_sha256':'f'*64,'sources':[card],
        'normalized_evidence':{'track_condition':{'value':'重','source_id':card['source_id'],'snapshot_sha256':card['snapshot_sha256']}}}
    request={'family_id':'LOCAL','venue_id':'FNB','race_id':'KM-LOCAL-FNB-20261002-R04-SYNTHETIC',
        'race_date':'2026-10-02','race_no':4,'prediction_cutoff':'2026-10-02T07:05:00Z',
        'race':{'venue':'船橋','distance_m':1500,'direction':'LEFT','surface':'DIRT','class':'C3'},
        'runners':[{'runner_id':str(n),'name':f'テスト馬{n}'} for n in (1,2)]}
    return source,request

def test_independent_raw_parser_and_all_63_rules_with_standard_distance_m():
    source,request=fixture()
    source['normalized_evidence']['race_card_tables']={'value':'DELIBERATELY_NOT_USED'}
    result=witness.verify(source,request,registry())
    assert result['runner_count']==2
    assert result['component_records']==126
    assert len(result['base_index_ledger'])==18
    assert result['all_63_rules_visited']
    assert result['independent_official_race_context']['distance']==1500
    assert result['independent_official_race_context']['direction']=='LEFT'
    same=[r for r in result['component_ledger'] if r['component']=='same_distance']
    assert all(not r['missing'] for r in same)
    assert result['production_compiler_called'] is False
    assert result['all_63_rules_empirical_measurement_complete'] is False
    assert result['source_to_score_all_records_arithmetic_match'] is False
    pedigree=[r for r in result['component_ledger'] if r['index']=='BVIg-L']
    assert len(pedigree)==14 and all(r['missing'] and r['witness_score']==52 for r in pedigree)

def test_decimal_finish_and_recency_missing_positions_keep_original_weights():
    assert witness.finish(2,5)==Decimal(75)
    assert witness.decay_mean([Decimal(100),None,Decimal(50)])==Decimal(80)
    assert witness.avg([None,None]) is None
    assert witness.spread([Decimal(5)]) is None
    assert witness.spread([Decimal(2),Decimal(4)])==Decimal(1)

def test_grade_whole_roman_tokens_and_no_jockey_causal_strength_claim():
    assert witness.grade('GIII')[0]==92
    assert witness.grade('GII')[0]==96
    assert witness.grade('SI')[1]=='CLASS_UNRESOLVED_CANONICAL_NEUTRAL'
    source,request=fixture();result=witness.verify(source,request,registry())
    skills=[r for r in result['component_ledger'] if r['component']=='position_acquisition_skill']
    assert all(r['evidence_quality']=='PROXY' for r in skills)
    assert all('SELECTED_SAME_HORSE_HISTORY_NOT_COMPLETE_PERSON_POPULATION' in r['qualification_issues'] for r in skills)

def test_tampered_raw_or_declared_hash_never_replays():
    source,request=fixture();source['sources'][0]['raw_sha256']='0'*64
    with pytest.raises(ValueError,match='RAW_SHA_MISMATCH'):witness.verify(source,request,registry())

@pytest.mark.parametrize('field,value',[('distance_m',1200),('direction','RIGHT'),('class','C1')])
def test_original_context_conflicts_are_not_hidden_by_request_aliases(field,value):
    source,request=fixture();request['race'][field]=value
    with pytest.raises(ValueError,match='OFFICIAL_REQUEST_.*_CONFLICT'):witness.verify(source,request,registry())

def test_declared_url_cannot_override_foreign_raw_race_header():
    source,request=fixture();card=source['sources'][0]
    raw=gzip.decompress(base64.b64decode(card['raw_gzip_b64'])).replace('第4競走'.encode(),'第5競走'.encode())
    card['raw_gzip_b64']=base64.b64encode(gzip.compress(raw)).decode();card['raw_sha256']=hashlib.sha256(raw).hexdigest()
    card['snapshot_sha256']=witness.canon_hash({k:v for k,v in card.items() if k!='snapshot_sha256'})
    source['normalized_evidence']['track_condition']['snapshot_sha256']=card['snapshot_sha256']
    with pytest.raises(ValueError,match='OFFICIAL_RAW_RACE_DATE_OR_NUMBER_CONFLICT'):
        witness.verify(source,request,registry())

def test_same_day_history_cannot_become_prestart_evidence():
    source,request=fixture()
    card,raw,parser=witness.original_card(source,request)
    parsed=witness.parse_original_runners(parser,source,request)
    from datetime import date
    parsed['1']['history'][0]['date']=date(2026,10,2)
    with pytest.raises(ValueError,match='FUTURE_OR_SAME_DAY_HISTORY_FORBIDDEN'):
        witness.independently_score(parsed,source,request,registry())

def test_auxiliary_after_freeze_is_flagged_and_never_retimestamped():
    source,request=fixture();aux=deepcopy(source['sources'][0]);aux['source_id']='AUX-SYNTHETIC'
    aux['source_class']='OFFICIAL_RIDER_PROFILE';aux['fetched_at']='2026-10-02T06:58:01Z'
    aux['snapshot_sha256']=witness.canon_hash({k:v for k,v in aux.items() if k!='snapshot_sha256'})
    source['sources'].append(aux)
    result=witness.verify(source,request,registry())
    assert result['source_snapshots_after_freeze']==1
    assert result['source_snapshots_at_or_after_cutoff']==0
    assert source['source_freeze_at']=='2026-10-02T06:58:00Z'
    assert result['source_snapshot_byte_audit'][1]['time_grade']=='AFTER_FREEZE_BEFORE_CUTOFF'

def test_core_card_after_freeze_is_not_admitted_like_unused_auxiliary():
    source,request=fixture();source['source_freeze_at']='2026-10-02T06:56:00Z'
    with pytest.raises(ValueError,match='CARD_FREEZE_OR_CUTOFF_INELIGIBLE'):
        witness.verify(source,request,registry())

def test_nonmissing_management_values_are_not_ability_measurements():
    source,request=fixture();result=witness.verify(source,request,registry())
    management=[r for r in result['component_ledger'] if r['index']=='DCR']
    assert len(management)==12 and all(r['evidence_quality']=='MANAGEMENT' for r in management)
    assert all(r['empirical_ability_measurement_proven'] is False for r in management)
    assert all(not r['missing'] for r in management)

@pytest.mark.parametrize('key',['same_day_r99_result_tables','same_day_r01_result_tables','odds_tables'])
def test_self_hashed_normalized_key_cannot_invent_raw_result_or_odds(key):
    source,request=fixture();card=source['sources'][0]
    source['normalized_evidence'][key]={'value':[['SYNTHETIC_FORGED_METADATA']],
        'source_id':card['source_id'],'snapshot_sha256':card['snapshot_sha256']}
    source['source_snapshot_sha256']=witness.canon_hash({k:v for k,v in source.items() if k!='source_snapshot_sha256'})
    with pytest.raises(ValueError,match='DCR_NORMALIZED_.*DIFFERS_FROM_RAW'):
        witness.verify(source,request,registry())

def _add_synthetic_page(source,kind,race_no,body):
    raw=body.encode();endpoint='RaceMarkTable' if kind=='OFFICIAL_SAME_DAY_RACE_RESULT_PASSING_ORDER' else 'OddsTanFuku'
    url=f'https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/{endpoint}?k_raceDate=2026%2F10%2F02&k_raceNo={race_no}&k_babaCode=19'
    s={'source_id':f'SYNTHETIC-{endpoint}-{race_no}','source_class':kind,'official':True,
        'requested_url':url,'final_url':url,'raw_gzip_b64':base64.b64encode(gzip.compress(raw)).decode(),
        'raw_sha256':hashlib.sha256(raw).hexdigest(),'fetched_at':'2026-10-02T06:57:00Z'}
    s['snapshot_sha256']=witness.canon_hash(s);source['sources'].append(s)
    return {'value':[], 'source_id':s['source_id'],'snapshot_sha256':s['snapshot_sha256']}

def test_dcr_counts_independently_parsed_prior_result_and_official_odds_tables():
    source,request=fixture()
    source['normalized_evidence']['same_day_r01_result_tables']=_add_synthetic_page(source,
        'OFFICIAL_SAME_DAY_RACE_RESULT_PASSING_ORDER',1,
        '<h4>2026年10月2日 船橋 第1競走 競走成績</h4><table><tr><th>着順</th><th>馬番</th><th>馬名</th></tr><tr><td>1</td><td>1</td><td>テスト馬</td></tr></table>')
    source['normalized_evidence']['odds_tables']=_add_synthetic_page(source,
        'OFFICIAL_ACTIVE_BETTING_UNIVERSE',4,
        '<h4>2026年10月2日 船橋 第4競走 16:15発走</h4><table><tr><th>馬番</th><th>単勝オッズ</th><th>複勝オッズ</th></tr><tr><td>1</td><td>0.0</td><td>0.0-0.0</td></tr><tr><td>2</td><td>0.0</td><td>0.0-0.0</td></tr></table>')
    result=witness.verify(source,request,registry())
    raw=result['independent_management_source_inputs']
    assert raw['prior_race_numbers']==[1] and raw['prior_result_count']==1
    assert raw['odds_source_present'] is True
    values={r['component']:r['witness_score'] for r in result['component_ledger'] if r['runner_id']=='1'}
    assert values['same_day_gci_coverage']==33.333333
    assert values['late_odds_changes_coverage']==100
    # Presence is a management fact, never a claim that unpublished 0.0 is a price.
    assert result['model_consumers_authorized'] is False

def test_current_race_result_cannot_be_counted_as_prior_gci_source():
    source,request=fixture()
    source['normalized_evidence']['same_day_r04_result_tables']=_add_synthetic_page(source,
        'OFFICIAL_SAME_DAY_RACE_RESULT_PASSING_ORDER',4,
        '<h4>2026年10月2日 船橋 第4競走 競走成績</h4><table><tr><th>着順</th><th>馬番</th><th>馬名</th></tr><tr><td>1</td><td>1</td><td>テスト馬</td></tr></table>')
    with pytest.raises(ValueError,match='DCR_CURRENT_OR_FUTURE_RESULT_FORBIDDEN'):
        witness.verify(source,request,registry())
