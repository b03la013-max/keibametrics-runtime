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


def entry_intent():
    return {'family_id':'JRA','race_id':'KM-JRA-KYO-20261101-R04',
            'venue_id':'KYO','race_date':DAY,'race_no':4,
            'prediction_cutoff':DAY+'T11:10:00+09:00',
            'scheduled_post_at':DAY+'T11:15:00+09:00',
            'external_dispatch_deadline_at':DAY+'T11:13:00+09:00',
            'jra_source':{'jra_meeting_key':'0820260411'}}


def current_header_payload(location):
    header={'surface':'芝','raw_race_context':'障害3歳以上未勝利 芝2,910m'}
    if location=='ROOT':return header
    if location=='RACE':return {'race':header}
    if location=='SOURCE_CONTEXT':return {'jra_race_context':header}
    if location=='DETAIL':return {'jra_official_race_card_detail':{'race_context':header}}
    if location=='SNAPSHOT_CONTEXT':return {'source_snapshot':{'jra_race_context':header}}
    if location=='SNAPSHOT_DETAIL':return {'source_snapshot':{'jra_official_race_card_detail':{'race_context':header}}}
    raise AssertionError(location)


@pytest.mark.parametrize('location',['ROOT','RACE','SOURCE_CONTEXT','DETAIL','SNAPSHOT_CONTEXT','SNAPSHOT_DETAIL'])
def test_explicit_current_headers_close_bridge_and_formal_authority_gap(location):
    from jra_execution_maturity_bridge import _require_jra,build_source_request
    from formal_request_validator import validate_production_authority
    payload={**entry_intent(),**current_header_payload(location),
             'base_index_mapping_authority':{'production_authority':True,'status':'PRODUCTION'}}
    before=copy.deepcopy(payload)
    assert resolver.explicit_current_jump_context(payload)
    _require_jra(payload) # Pure shape validation also serves historical readback.
    for call in (build_source_request,validate_production_authority):
        with pytest.raises(ValueError,match='JRA_JUMP_DEDICATED_OWNER_UNCONFIRMED'):
            call(payload)
    assert payload==before


@pytest.mark.parametrize('payload',[None,{},[],{'race':None},{'race':{'surface':'UNKNOWN'}}])
def test_no_new_positive_scope_witness_for_unlabelled_or_legacy_inputs(payload):
    assert resolver.explicit_current_jump_context(payload) is False


def test_current_context_adapter_ignores_names_other_race_history_and_raw_bundles():
    from jra_execution_maturity_bridge import _require_jra,build_source_request
    from formal_request_validator import validate_production_authority
    for code,(_,venue) in resolver.VENUES.items():
        for surface in ('芝','ダ'):
            payload={**entry_intent(),'venue_id':venue,
                'race':{'surface':surface,'distance':3200,'title':'3歳以上オープン'},
                'name':'ジャンプホース','horse_name':'障害ヒーロー',
                'runners':[{'name':'障害ヒーロー','recent_runs':[{'race_name':'東京ハイジャンプ'}]}],
                'jra_official_horse_history':{'runners':{'1':{'race_name':'障害3歳以上未勝利'}}},
                'sources':[{'raw':'障害3歳以上未勝利'}],
                'raw':'Unstructured history mentions 障害; not a current race header.',
                'base_index_mapping_authority':{'production_authority':True,'status':'PRODUCTION'}}
            before=copy.deepcopy(payload)
            assert not resolver.explicit_current_jump_context(payload)
            _require_jra(payload)
            assert build_source_request(payload)['venue_id']==venue
            assert validate_production_authority(payload)['production_authority_verified']
            assert payload==before


def test_generic_raw_or_nested_history_cannot_be_stringified_into_a_current_header():
    historical={'runners':[{'race_name':'東京ハイジャンプ'}]}
    payload={'race':{'surface':'芝','raw':'Recent history: 障害3歳以上未勝利'},
             'jra_race_context':{'surface':'ダ','raw':historical,'raw_race_context':historical},
             'jra_official_race_card_detail':{'race_context':{'surface':'芝','raw':historical}}}
    assert not resolver.explicit_current_jump_context(payload)
    # The original Discovery-row interface still reads its known official row.
    assert resolver.official_jump_race({'raw':'11時15分 障害3歳以上未勝利'})


def test_intent_resolver_current_official_row_is_scoped_but_not_arbitrary_metadata():
    from jra_execution_maturity_bridge import build_source_request
    req={**entry_intent(),'intent_resolver':{'official_day_row':'11時15分 障害3歳以上未勝利 芝2910m 12頭'}}
    assert resolver.explicit_current_jump_context(req)
    with pytest.raises(ValueError,match=resolver.JUMP_SCOPE_REASON):build_source_request(req)
    req['intent_resolver']={'official_day_row':{'history':'障害未勝利'},'history':'東京ハイジャンプ'}
    assert not resolver.explicit_current_jump_context(req)
    assert build_source_request(req)['race_id']==req['race_id']


@pytest.mark.parametrize('family',['LOCAL','BAN'])
def test_formal_non_jra_authority_check_remains_unchanged(family):
    from formal_request_validator import validate_production_authority
    req={'family_id':family,**current_header_payload('SOURCE_CONTEXT'),
         'base_index_mapping_authority':{'production_authority':True,'status':'PRODUCTION'}}
    assert validate_production_authority(req)['production_authority_verified']


@pytest.mark.parametrize('method',['prepare_production_numerical','build_formal_request'])
def test_signed_source_current_header_holds_before_numerics_or_new_binding(method):
    import jra_execution_maturity_bridge as bridge
    intent=entry_intent()
    artifact={'race_id':intent['race_id'],'prediction_cutoff':intent['prediction_cutoff'],
              'source_freeze_at':DAY+'T10:20:00+09:00','source_snapshot_sha256':'a'*64,
              **current_header_payload('DETAIL')}
    env={'artifact':artifact,'receipt':{'runtime_revision':'existing-runtime'},'receipt_sha256':'b'*64}
    before=copy.deepcopy((intent,env))
    # This is a pure synthetic envelope boundary test, not signature acceptance.
    with pytest.raises(ValueError,match='JRA_JUMP_DEDICATED_OWNER_UNCONFIRMED'):
        getattr(bridge,method)(intent,env)
    assert (intent,env)==before


def test_legacy_no_bridge_metadata_still_does_not_require_new_context():
    from jra_execution_maturity_bridge import verify_formal_request_binding
    assert verify_formal_request_binding(entry_intent(),{'artifact':{}})['status']=='NOT_APPLICABLE'


def test_historical_pure_shape_and_binding_checks_are_not_new_scope_submissions():
    from jra_execution_maturity_bridge import _require_jra,verify_formal_request_binding
    old={**entry_intent(),**current_header_payload('RACE')}
    _require_jra(old)
    assert verify_formal_request_binding(old,{'artifact':current_header_payload('SOURCE_CONTEXT')})['status']=='NOT_APPLICABLE'


def test_existing_formal_default_family_also_holds_known_jump():
    from formal_request_validator import validate_production_authority
    req={**current_header_payload('SOURCE_CONTEXT'),
         'base_index_mapping_authority':{'production_authority':True,'status':'PRODUCTION'}}
    with pytest.raises(ValueError,match='JRA_JUMP_DEDICATED_OWNER_UNCONFIRMED'):
        validate_production_authority(req)


def app_scope_guards_only():
    # Execute only the two pure guard definitions. Sourceapp itself, acquisition,
    # private keys and receipt signing are never imported or called by this test.
    import ast
    from typing import Any,Dict
    code=ast.parse((ROOT/'runtime/jra_source_runtime/app.py').read_text())
    nodes=[n for n in code.body if isinstance(n,ast.FunctionDef)
           and n.name in ('_validate_family','_reject_explicit_jump_context')]
    assert len(nodes)==2
    class GuardHTTPError(Exception):
        def __init__(self,status_code,detail):self.status_code=status_code;self.detail=detail
    namespace={'Any':Any,'Dict':Dict,'HTTPException':GuardHTTPError,
               'explicit_current_jump_context':resolver.explicit_current_jump_context,
               'JUMP_SCOPE_REASON':resolver.JUMP_SCOPE_REASON}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'sourceapp-pure-scope-guards','exec'),namespace)
    return namespace,GuardHTTPError


@pytest.mark.parametrize('location',['ROOT','RACE','SOURCE_CONTEXT','DETAIL','SNAPSHOT_CONTEXT','SNAPSHOT_DETAIL'])
def test_source_api_incoming_pure_guard_rejects_explicit_jump_without_source_or_key(location):
    guards,error=app_scope_guards_only()
    with pytest.raises(error) as caught:
        guards['_validate_family']({'family_id':'JRA',**current_header_payload(location)})
    assert caught.value.status_code==422 and caught.value.detail==resolver.JUMP_SCOPE_REASON
    guards['_validate_family']({'family_id':'JRA'}) # unknown context is not new required evidence


def test_source_acquire_scope_guards_are_outside_optional_catches_and_before_signing():
    import ast
    code=ast.parse((ROOT/'runtime/jra_source_runtime/app.py').read_text())
    acquire=next(n for n in code.body if isinstance(n,ast.FunctionDef) and n.name=='source_acquire')
    def calls(node,name):
        return any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id==name for n in ast.walk(node))
    direct=[(i,n) for i,n in enumerate(acquire.body) if isinstance(n,ast.Expr)
            and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name)
            and n.value.func.id=='_reject_explicit_jump_context']
    assert len(direct)==3
    assert isinstance(acquire.body[direct[0][0]-1],ast.Try) and calls(acquire.body[direct[0][0]-1],'enrich_with_race_context')
    assert isinstance(acquire.body[direct[1][0]-1],ast.Try) and calls(acquire.body[direct[1][0]-1],'fetch_and_enrich_race_card_detail')
    assert isinstance(acquire.body[direct[2][0]-1],ast.If) and calls(acquire.body[direct[2][0]-1],'bind_latest_environment')
    assert direct[-1][1].lineno < next(n.lineno for n in ast.walk(acquire) if isinstance(n,ast.Return) and calls(n,'signed_receipt'))
    assert sum(calls(n,'_reject_explicit_jump_context') for n in ast.walk(acquire) if isinstance(n,ast.Try))==0


@pytest.mark.parametrize('family',['LOCAL','BAN'])
def test_non_jra_authority_fresh_import_does_not_import_the_jra_adapter(family,tmp_path):
    import os,subprocess
    code='''
import pathlib,socket,sys,urllib.request
root=pathlib.Path(sys.argv[1])
def deny(*a,**k):raise AssertionError('SCOPE_PURE_FRESH_IMPORT_NETWORK_FORBIDDEN')
socket.socket.connect=deny;socket.create_connection=deny;urllib.request.urlopen=deny
sys.path.insert(0,str(root/'runtime'))
from formal_request_validator import validate_production_authority
req={'family_id':sys.argv[2],'race':{'surface':'障','title':'障害未勝利'},
     'base_index_mapping_authority':{'production_authority':True,'status':'PRODUCTION'}}
assert validate_production_authority(req)['production_authority_verified']
assert 'jra_source_runtime.jra_race_day_resolver' not in sys.modules
print('SCOPE_PURE_FRESH_IMPORT_PASS')
'''
    env={k:v for k,v in os.environ.items() if k not in ('PYTHONPATH','GH_TOKEN','GITHUB_TOKEN')}
    result=subprocess.run([sys.executable,'-I','-c',code,str(ROOT),family],cwd=tmp_path,
                          env=env,capture_output=True,text=True,timeout=15)
    assert result.returncode==0,result.stdout+result.stderr
    assert result.stdout.strip()=='SCOPE_PURE_FRESH_IMPORT_PASS'


def formal_inline_scope_order():
    import ast,yaml
    document=yaml.safe_load((ROOT/'.github/workflows/km-formal-request-runner.yml').read_text())
    steps=document['jobs']['formal-run']['steps']
    step=next(s for s in steps if s.get('id')=='formal_execution')
    assert "steps.production_readback.outputs.reused == 'false'" in step['if']
    script=step['run'].split("python - <<'PY'\n",1)[1].rsplit('\nPY',1)[0]
    return ast,ast.parse(script)


def assert_formal_scope_before_calculation(tree):
    import ast
    guards=[n for n in ast.walk(tree) if isinstance(n,ast.If)
            and any(isinstance(c,ast.Call) and isinstance(c.func,ast.Name)
                    and c.func.id=='explicit_current_jump_context' for c in ast.walk(n.test))]
    assert len(guards)==2
    by_arg={next(c.args[0].id for c in ast.walk(n.test) if isinstance(c,ast.Call)
                 and isinstance(c.func,ast.Name) and c.func.id=='explicit_current_jump_context'):n for n in guards}
    assert set(by_arg)=={'req','source_artifact'}
    numerical_names={'load_production_mapping','build_zero_touch_source_index_report','attach_source_features_to_request',
                     'compile_evidence_feature_ledger','attach_production_ledger_to_request','materialize_index_provenance'}
    first_numeric=min(n.lineno for n in ast.walk(tree) if isinstance(n,ast.Call)
                      and isinstance(n.func,ast.Name) and n.func.id in numerical_names)
    assert by_arg['req'].lineno < by_arg['source_artifact'].lineno < first_numeric
    for guard in guards:
        assert any(isinstance(n,ast.Raise) for n in guard.body)
        assert any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='mark'
                   and n.args and isinstance(n.args[0],ast.Constant) and n.args[0].value=='JRA_PRODUCTION_SCOPE'
                   for n in ast.walk(guard))
    parents={child:node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    node=by_arg['source_artifact']
    while node in parents:
        node=parents[node]
        if isinstance(node,ast.If):
            assert not any(isinstance(c,ast.Constant) and c.value=='jra_maturity_bridge' for c in ast.walk(node.test))


def test_manual_formal_without_bridge_is_scoped_before_full20_and_source_feature_compile():
    _,tree=formal_inline_scope_order()
    assert_formal_scope_before_calculation(tree)


@pytest.mark.parametrize('damage',['REMOVE_SOURCE_GUARD','MOVE_GUARD_AFTER_FULL20'])
def test_early_scope_order_regression_rejects_guard_removal_or_late_validation(damage):
    import ast
    _,tree=formal_inline_scope_order()
    guard=next(n for n in ast.walk(tree) if isinstance(n,ast.If)
        and any(isinstance(c,ast.Call) and isinstance(c.func,ast.Name) and c.func.id=='explicit_current_jump_context'
                and c.args[0].id=='source_artifact' for c in ast.walk(n.test)))
    if damage=='MOVE_GUARD_AFTER_FULL20':guard.lineno=10**6
    else:
        holder=next(n for n in ast.walk(tree) if hasattr(n,'body') and guard in n.body)
        holder.body.remove(guard)
    with pytest.raises(AssertionError):assert_formal_scope_before_calculation(tree)
