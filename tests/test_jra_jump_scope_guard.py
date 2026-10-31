"""Offline Scope checks; discovery fixture is not SOURCE or Live credit."""
import copy
import datetime as dt
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'runtime/jra_source_runtime')]
import jra_race_day_resolver as resolver
import jra_race_day_autopilot as autopilot

# Exact published official day-row metadata from main49f; no runner/paid Raw.
OFFICIAL_ROWS = {'京都': ['9時45分 2歳未勝利牝［指定］ ダート1,400m11頭 出馬表 オッズ 未確定', '10時15分 2歳未勝利[指定] ダート1,800m13頭 出馬表 オッズ 未確定', '10時45分 2歳未勝利[指定] 芝2,000m12頭 出馬表 オッズ 未確定', '11時15分 障害3歳以上未勝利 芝→ダート2,910m13頭 出馬表 オッズ 未確定', '12時05分 メイクデビュー京都 2歳新馬（混合）［指定］ 芝1,600m17頭 出馬表 オッズ 未確定', '12時35分 メイクデビュー京都 2歳新馬[指定] ダート1,800m16頭 出馬表 オッズ 未確定', '13時05分 3歳以上1勝クラス（混合）［指定］ ダート1,400m16頭 出馬表 オッズ 未確定', '13時35分 3歳以上1勝クラス（混合）［指定］ 芝2,200m14頭 出馬表 オッズ 未確定', '14時10分 愛宕特別 3歳以上2勝クラス（混合）［指定］ ダート1,800m10頭 出馬表 オッズ 未確定', '14時45分 古都ステークス 3歳以上3勝クラス（混合）［指定］ 芝3,000m9頭 出馬表 オッズ 未確定', '15時20分 まほろばステークス 3歳以上オープン（国際）（特指） 芝1,600m13頭 出馬表 オッズ 未確定', '16時05分 3歳以上2勝クラス（混合）（特指） 芝1,400m13頭 出馬表 オッズ 未確定'], '東京': ['10時00分 2歳未勝利牝［指定］ 芝1,400m15頭 出馬表 オッズ 未確定', '10時30分 2歳未勝利[指定] ダート1,400m16頭 出馬表 オッズ 未確定', '11時00分 2歳未勝利[指定] 芝1,800m9頭 出馬表 オッズ 未確定', '11時30分 メイクデビュー東京 2歳新馬（混合）［指定］ 芝1,600m14頭 出馬表 オッズ 未確定', '12時20分 メイクデビュー東京 2歳新馬（混合）［指定］ 芝2,000m8頭 出馬表 オッズ 未確定', '12時50分 3歳以上1勝クラス[指定] ダート1,400m15頭 出馬表 オッズ 未確定', '13時20分 3歳以上1勝クラス[指定] ダート1,600m15頭 出馬表 オッズ 未確定', '13時50分 本栖湖特別 3歳以上2勝クラス（混合）（特指） 芝2,400m8頭 出馬表 オッズ 未確定', '14時25分 紅葉ステークス 3歳以上3勝クラス（混合）（特指） 芝1,600m14頭 出馬表 オッズ 未確定', '15時00分 秋嶺ステークス 3歳以上3勝クラス（混合）（特指） ダート1,300m16頭 出馬表 オッズ 未確定', '15時40分 天皇賞(秋) 3歳以上オープン（国際）（指定） 芝2,000m17頭 出馬表 オッズ 未確定', '16時25分 清里特別 3歳以上2勝クラス（混合）［指定］ ダート1,600m14頭 出馬表 オッズ 未確定']}
DAY='2026-11-01'

def days(venue):
    code=resolver.venue_code(venue)
    return code+'20260411',resolver.parse_day_rows(OFFICIAL_ROWS[venue])

@pytest.fixture(autouse=True)
def offline(monkeypatch):
    import socket,urllib.request
    def deny(*a,**k):raise AssertionError('OFFLINE_SCOPE_TEST_NO_NETWORK')
    monkeypatch.setattr(socket.socket,'connect',deny)
    monkeypatch.setattr(urllib.request,'urlopen',deny)
    monkeypatch.setattr(urllib.request.OpenerDirector,'open',deny)
    for name in ('observed_formal_runs','observed_resolver_runs','observed_source_runs'):
        monkeypatch.setattr(autopilot,name,lambda *a,**k:[])

def test_official_nov1_rows_keep_all12_ordinals_and_hold_the_jump():
    key,rows=days('京都')
    assert len(rows)==12 and [r['race_no'] for r in rows]==list(range(1,13))
    jump=rows[3]
    assert jump['surface']=='芝→ダート' and jump['title']=='障害3歳以上未勝利'
    with pytest.raises(ValueError,match='JRA_JUMP_DEDICATED_OWNER_UNCONFIRMED'):
        resolver.build_intent(race_date=DAY,venue='京都',race_no=4,meeting_key=key,race=jump)
    # A parser that reports only turf must not erase the explicit discipline.
    turf_only={**jump,'surface':'芝'}
    with pytest.raises(ValueError,match='JRA_JUMP_DEDICATED_OWNER_UNCONFIRMED'):
        resolver.build_intent(race_date=DAY,venue='京都',race_no=4,meeting_key=key,race=turf_only)
    assert len(rows)==12 and rows[4]['race_no']==5

@pytest.mark.parametrize('field,value',[
    ('surface','障'),('surface','障害'),('surface','芝→ダート'),('surface','ダート→芝'),
    ('title','障害3歳以上未勝利'),('title','京都ジャンプステークス'),
    ('title','競走 J・GⅠ'),('title','競走 J･GⅡ'),('title','競走 J.GIII'),
    ('raw','11時15分 障害3歳以上未勝利 芝2,910m13頭'),
])
def test_explicit_official_jump_markers_hold_at_arbitrary_race_numbers(field,value):
    race={'race_no':7,'post_time':'13:00','surface':'芝','title':'3歳以上オープン',field:value,
          'dedicated_jump_owner_confirmed':True}
    before=copy.deepcopy(race)
    with pytest.raises(ValueError,match='JRA_JUMP_DEDICATED_OWNER_UNCONFIRMED'):
        resolver.build_intent(race_date=DAY,venue='東京',race_no=7,meeting_key='0520260411',race=race)
    assert race==before

@pytest.mark.parametrize('code,venue',[(k,v[1]) for k,v in resolver.VENUES.items()])
def test_all10_regular_venues_keep_flat_intents_without_distance_or_runner_name_inference(code,venue):
    race={'race_no':4,'post_time':'13:00','surface':'芝','distance_m':3600,
          'title':'3歳以上オープン GⅠ','field_size':12,
          'horse_name':'障害ヒーロー','runners':[{'name':'ジャンプホース'}]}
    intent=resolver.build_intent(race_date=DAY,venue=venue,race_no=4,meeting_key=code+'20260411',race=race)
    assert intent['race']['surface']=='芝'
    assert intent['prediction_cutoff']=='2026-11-01T12:55:00+09:00'
    assert intent['external_dispatch_deadline_at']=='2026-11-01T12:58:00+09:00'
    assert intent['run_count']==5000 and 'scope_hold' not in intent

def test_canonical_execute_stops_before_intent_write_or_authority_source_handoff(tmp_path,monkeypatch):
    monkeypatch.setattr(resolver,'resolve_day',lambda *a,**k:days('京都'))
    args=SimpleNamespace(date=DAY,venue='京都',race=4,run_count=5000,revision=1,
                         orchestration_session_id=None,out_dir=str(tmp_path),min_lead_minutes=15)
    with pytest.raises(ValueError,match='JRA_JUMP_DEDICATED_OWNER_UNCONFIRMED'):
        resolver.execute(args,999999999)
    assert list(tmp_path.iterdir())==[]

def run_tick(root,now,**kwargs):
    return autopilot.tick(root,DAY,now,meetings=lambda d:['京都','東京'],
        resolve=lambda d,v:days(v),default_all=True,resolver_runs=[],**kwargs)

def test_autopilot_manages24_with_jump_hold_before_windows_and_no_claim(tmp_path):
    sent=[]
    rows=run_tick(tmp_path,dt.datetime(2026,11,1,0,45,tzinfo=resolver.JST),dispatch=lambda *a:sent.append(a))
    assert len(rows)==24 and sum(x['status']=='WAIT' for x in rows)==23
    assert sum(x['status']=='SCOPE_HOLD' for x in rows)==1 and sent==[]
    schedule=json.loads((tmp_path/f'runtime/jra_race_day_plan/{DAY}.schedule.json').read_text())
    state=json.loads((tmp_path/f'runtime/jra_race_day_plan/{DAY}.state.json').read_text())
    assert len(schedule)==24 and state=={}
    assert schedule['KM-JRA-KYO-20261101-R04']['status']=='SCOPE_HOLD'
    assert not (tmp_path/f'runtime/jra_race_day_plan/{DAY}.json').exists()
    assert not (tmp_path/'runtime/jra_formal_intents').exists()

def test_due_flat_sibling_runs_while_jump_is_held_before_claim_and_dispatch(tmp_path):
    sent=[];jump='KM-JRA-KYO-20261101-R04'
    def publish():
        state=json.loads((tmp_path/f'runtime/jra_race_day_plan/{DAY}.state.json').read_text())
        assert jump not in state
    rows=run_tick(tmp_path,dt.datetime(2026,11,1,10,25,tzinfo=resolver.JST),
                  dispatch=lambda *a:sent.append(a),publish=publish)
    assert sent==[('東京',3,DAY,5000)]
    assert next(r for r in rows if r['race_id']==jump)['status']=='SCOPE_HOLD'
    state=json.loads((tmp_path/f'runtime/jra_race_day_plan/{DAY}.state.json').read_text())
    assert jump not in state and state['KM-JRA-TKY-20261101-R03']['dispatch_state']=='DISPATCH_ACKNOWLEDGED'

def test_existing_explicit_scope_hold_and_claim_metadata_are_not_rewritten(tmp_path):
    directory=tmp_path/'runtime/jra_race_day_plan';directory.mkdir(parents=True)
    jump='KM-JRA-KYO-20261101-R04'
    plan={'entries':[{'venue':'東京','races':[1]}]}
    plan_path=directory/(DAY+'.json');plan_path.write_text(json.dumps(plan));original=plan_path.read_bytes()
    hold={'status':'SCOPE_HOLD','scope_hold_reason':'EXISTING_OWNER_HOLD','original_metadata':'keep'}
    (directory/(DAY+'.schedule.json')).write_text(json.dumps({jump:hold}))
    prior={jump:{'dispatch_state':'HOLD_AMBIGUOUS_DISPATCH_NO_AUTOMATIC_RETRY','claimed_at':'original'}}
    (directory/(DAY+'.state.json')).write_text(json.dumps(prior))
    autopilot.tick(tmp_path,DAY,dt.datetime(2026,11,1,0,45,tzinfo=resolver.JST),
        resolve=lambda d,v:days(v),dispatch=lambda *a:pytest.fail('no dispatch'),resolver_runs=[])
    schedule=json.loads((directory/(DAY+'.schedule.json')).read_text());state=json.loads((directory/(DAY+'.state.json')).read_text())
    assert plan_path.read_bytes()==original and schedule[jump]==hold and state==prior


def registration_inputs(flat_only=False):
    discovery={'status':'DISCOVERED','race_date':DAY,'venues':[]}
    for venue in ('京都','東京'):
        key,rows=days(venue)
        if flat_only:
            rows=[{**r,'surface':'芝','title':'3歳以上1勝クラス','raw':'flat official row'} for r in rows]
        discovery['venues'].append({'venue':venue,'meeting_key':key,'races':rows})
    authority={'manifest_id':'KM-FAMILY-CURRENT-AUTHORITY-20261012-R51',
        'family_scoped_authority':{'JRA':{'production_static_owner_activation':{'status':'PRODUCTION_AUTHORIZED'}}}}
    return discovery,authority


def test_mixed_registration_keeps_management24_and_registers_flat23_only(tmp_path):
    from jra_race_day_registration import build_registrations,persist_registrations,verify_registration
    discovery,authority=registration_inputs();before=copy.deepcopy((discovery,authority))
    plan,records=build_registrations(discovery,authority,observed_at='2026-11-01T00:45:00+09:00')
    jump='KM-JRA-KYO-20261101-R04'
    assert (discovery,authority)==before
    assert len(plan['management_race_ids'])==24 and len(records)==plan['cohort']['race_count']==23
    assert jump not in records and jump not in plan['cohort']['race_ids']
    assert len(plan['scope_exclusions'])==1 and plan['scope_exclusions'][0]['race_id']==jump
    assert plan['scope_exclusions'][0]['action']=='EXCLUDE_FROM_FLAT_DISPATCH_ONLY'
    assert sum(len(e['races']) for e in plan['entries'])==23
    assert persist_registrations(tmp_path,plan,records)==23
    assert not (tmp_path/'runtime/jra_formal_intents').exists()
    for rid,record in records.items():
        assert record['executed_cells']==0 and record['source_executed'] is False
        verify_registration(record,plan,race_id=rid,official_post=dt.datetime.fromisoformat(record['intake_intent']['scheduled_post_at']))
    # The approved exclusions remain visible even though dispatch entries omit jump.
    rows=run_tick(tmp_path,dt.datetime(2026,11,1,0,50,tzinfo=resolver.JST),dispatch=lambda *a:pytest.fail('early send'))
    assert len(rows)==23 # dispatch entries contain only the regular cohort
    index=json.loads((tmp_path/f'runtime/jra_race_day_status/{DAY}.json').read_text())
    assert len(index['races'])==24
    assert next(r for r in index['races'] if r['race_id']==jump)['state']=='SCOPE_HOLD'
    saved={p:p.read_bytes() for p in (tmp_path/'runtime').rglob('*.json')}
    with pytest.raises(ValueError,match='ALREADY_EXISTS_DIFFERENT'):
        persist_registrations(tmp_path,{**plan,'unapproved_change':True},records)
    changed=copy.deepcopy(records);changed[next(iter(changed))]['executed_cells']=20
    with pytest.raises(ValueError,match='ALREADY_EXISTS_DIFFERENT'):
        persist_registrations(tmp_path,plan,changed)
    assert saved=={p:p.read_bytes() for p in saved}


def test_flat_only_registration_keeps_legacy_plan_schema_and_byte_semantics():
    import importlib.util,hashlib
    from jra_race_day_registration import build_registrations
    discovery,authority=registration_inputs(flat_only=True)
    kwargs={'observed_at':'2026-11-01T00:45:00+09:00'}
    plan,records=build_registrations(discovery,authority,**kwargs)
    assert len(records)==24 and 'scope_exclusions' not in plan and 'management_race_ids' not in plan
    # Frozen pre-change output for this deterministic all-flat fixture.
    assert hashlib.sha256(json.dumps((plan,records),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()=='dba364a38205432ab2f3064281c0e2a158e96326421459250505993006bee8e5'
    # Exact checked-in pre-change bytes are supplied only to the offline harness.
    import os
    baseline=os.environ.get('KM_SCOPE_REGISTRATION_BASELINE')
    if baseline:
        spec=importlib.util.spec_from_file_location('scope_registration_baseline',baseline)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        old=module.build_registrations(discovery,authority,**kwargs)
        assert (plan,records)==old
        assert json.dumps((plan,records),ensure_ascii=False,sort_keys=True)==json.dumps(old,ensure_ascii=False,sort_keys=True)
