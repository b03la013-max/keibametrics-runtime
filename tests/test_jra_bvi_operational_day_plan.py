"""Scheduling compatibility tests; no SOURCE, prediction, KRS call or OOS freeze.

Archived official headers are unit fixtures. Changing their fixture date below
is not a future official discovery or a backdated preregistration.
"""
from copy import deepcopy
from datetime import datetime, timedelta
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
sys.path.insert(0,str(ROOT/'runtime/jra_source_runtime'))
import jra_bvi_operational_day_plan as plans
import jra_race_day_autopilot as autopilot
from jra_race_day_resolver import JST, parse_day_rows
from jra_race_day_registration import sha

spec=importlib.util.spec_from_file_location('fixed_bvi_priority_for_plan_test',
    ROOT/'scripts/jra_bvi_pipeline_forward_shadow.py')
fixed=importlib.util.module_from_spec(spec); spec.loader.exec_module(fixed)
DAY='2026-11-07'  # unit fixture only, never persisted in the repository


def fixture_discovery(day=DAY):
    saved=json.loads((ROOT/'runtime/jra_race_day_plan/2026-11-01.schedule.json').read_text())
    venues=[]
    for name,code,vid in [('東京','05','TKY'),('京都','08','KYO')]:
        raw=[saved[f'KM-JRA-{vid}-20261101-R{n:02d}']['official_day_row'] for n in range(1,13)]
        rows=parse_day_rows(raw)
        assert len(rows)==12
        venues.append({'venue':name,'venue_id':vid,'meeting_key':code+day[:4]+'0501','races':rows})
    return {'status':'DISCOVERED','race_date':day,'venues':venues}


def authority():
    return {'manifest_id':'UNIT_AUTHORITY_NOT_AN_ACTUAL_FUTURE_GRANT',
        'effective_at':'2026-10-12T00:00:00+09:00',
        'family_scoped_authority':{'JRA':{'production_static_owner_activation':
            {'status':'OWNER_AUTHORIZED_UNVALIDATED'}}}}


def fixture_plan():
    return plans.build_plan(fixture_discovery(),authority(),observed_at=DAY+'T08:00:00+09:00')


def save_schedule(root,plan,schedule=None):
    path=root/'runtime/jra_race_day_plan'/f'{DAY}.schedule.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(schedule or plan['official_schedule_facts']))
    return path


def req_for(plan,rid=None):
    rid=rid or f'KM-JRA-TKY-{DAY.replace("-","")}-R12'
    post=datetime.fromisoformat(plan['official_schedule_facts'][rid]['post'])
    return {'race_date':DAY,'race_id':rid,'scheduled_post_at':post.isoformat(),
        'prediction_cutoff':(post-timedelta(minutes=5)).isoformat()}


def rehash(plan):
    plan['plan_sha256']=sha({k:v for k,v in plan.items() if k!='plan_sha256'})


def test_literal_nov1_plan_reproduces_the_original_fixed_reader_blocker(tmp_path):
    path=tmp_path/'runtime/jra_race_day_plan/2026-11-01.json'
    path.parent.mkdir(parents=True)
    original=(ROOT/path.relative_to(tmp_path)).read_bytes()
    path.write_bytes(original)
    assert sum(len(e['races']) for e in json.loads(original)['entries'])==23
    with pytest.raises(ValueError,match='BVI_SHADOW_DEFER_DAY_PLAN_UNSUPPORTED'):
        fixed.production_priority_window({'race_date':'2026-11-01'},root=tmp_path,
            now=datetime.fromisoformat('2026-11-01T15:47:00.396004+09:00'))
    assert path.read_bytes()==original


def test_future_plan_is_complete_priority_census_but_only_23_flat_routes(tmp_path):
    plan=fixture_plan(); plans.persist_future_plan(tmp_path,plan)
    assert plans.validate_plan(plan)
    assert len(plan['management_race_ids'])==24
    assert len(plan['official_schedule_facts'])==24
    entries=list(autopilot.plan_entries(plan,DAY))
    assert len(entries)==23
    assert ('京都',4) not in {(v,n) for v,n,_,_ in entries}
    assert plan['scope_exclusions'][0]['race_id']==f'KM-JRA-KYO-{DAY.replace("-","")}-R04'
    assert 'cohort' not in plan and plan['forward_oos_increment']==0
    assert not (tmp_path/'runtime/jra_race_registrations').exists()
    assert all(x['oos_eligible'] is False for x in plan['forward_oos_preregistration']['targets'])
    assert all(not row.get('status') for row in plan['official_schedule_facts'].values())


def test_unchanged_fixed_priority_reader_accepts_fresh_complete_plan(tmp_path):
    plan=fixture_plan(); plans.persist_future_plan(tmp_path,plan); save_schedule(tmp_path,plan)
    now=datetime.fromisoformat(DAY+'T15:47:00.396004+09:00')
    # Isolating plan compatibility only: peer ids represent already verified
    # Finals at this boundary, not synthetic receipts or OOS qualification.
    stop=fixed.production_priority_window(req_for(plan),root=tmp_path,now=now,
        signed_final_ids=plan['management_race_ids'])
    assert stop==now+timedelta(seconds=600)
    assert not (tmp_path/'runtime/jra_bvi_env_forward_oos').exists()


def test_other_due_production_still_defers_and_future_opening_bounds_window(tmp_path):
    plan=fixture_plan(); plans.persist_future_plan(tmp_path,plan); save_schedule(tmp_path,plan)
    peer=f'KM-JRA-KYO-{DAY.replace("-","")}-R12'
    signed=[rid for rid in plan['management_race_ids'] if rid!=peer]
    post=datetime.fromisoformat(plan['official_schedule_facts'][peer]['post'])
    with pytest.raises(ValueError,match='BVI_SHADOW_DEFER_PRODUCTION_PENDING:'+peer):
        fixed.production_priority_window(req_for(plan),root=tmp_path,
            now=post-timedelta(minutes=45),signed_final_ids=signed)
    opening=post-timedelta(minutes=55)
    stop=fixed.production_priority_window(req_for(plan),root=tmp_path,
        now=opening-timedelta(minutes=8),signed_final_ids=signed)
    assert stop==opening-timedelta(seconds=120)


def test_held_jump_still_conservatively_blocks_the_fixed_priority_reader(tmp_path):
    plan=fixture_plan(); plans.persist_future_plan(tmp_path,plan)
    rows=deepcopy(plan['official_schedule_facts'])
    held=plan['scope_exclusions'][0]; rows[held['race_id']]['scope_decision']=held
    save_schedule(tmp_path,plan,rows)
    post=datetime.fromisoformat(rows[held['race_id']]['post'])
    signed=[rid for rid in plan['management_race_ids'] if rid!=held['race_id']]
    with pytest.raises(ValueError,match='BVI_SHADOW_DEFER_PRODUCTION_PENDING:'+held['race_id']):
        fixed.production_priority_window(req_for(plan),root=tmp_path,
            now=post-timedelta(minutes=45),signed_final_ids=signed)


def test_tick_preserves_24_official_rows_without_dispatching_held_jump(tmp_path):
    plan=fixture_plan(); plans.persist_future_plan(tmp_path,plan)
    discovery=fixture_discovery(); sent=[]
    days={v['venue']:(v['meeting_key'],v['races']) for v in discovery['venues']}
    now=datetime.fromisoformat(DAY+'T10:30:00+09:00')
    out=autopilot.tick(tmp_path,DAY,now,resolve=lambda d,v:days[v],
        meetings=lambda d:list(days),resolver_runs={},dispatch=lambda *a:sent.append(a))
    schedule=json.loads((tmp_path/f'runtime/jra_race_day_plan/{DAY}.schedule.json').read_text())
    assert len(schedule)==24
    held=plan['scope_exclusions'][0]['race_id']
    assert schedule[held]['scope_decision']['status']=='SCOPE_HOLD'
    assert not schedule[held].get('status')
    assert not any(v=='京都' and n==4 for v,n,*_ in sent)
    assert not any(row['race_id']==held for row in out)
    status=json.loads((tmp_path/f'runtime/jra_race_day_status/{DAY}.json').read_text())
    assert next(r for r in status['races'] if r['race_id']==held)['state']=='SCOPE_HOLD'
    assert not (tmp_path/'runtime/jra_race_registrations').exists()


def test_refresh_tracks_changed_held_post_but_never_promotes_dispatch(tmp_path):
    plan=fixture_plan(); plans.persist_future_plan(tmp_path,plan)
    discovery=fixture_discovery(); venue=discovery['venues'][1]
    row=venue['races'][3]; row['raw']=row['raw'].replace('11時15分','15時55分')
    row['post_time']='15:55'
    days={v['venue']:(v['meeting_key'],v['races']) for v in discovery['venues']}
    schedule={}; plans.refresh_census_schedule(plan,schedule,days,resolve=lambda *a:pytest.fail('cached'))
    held=plan['scope_exclusions'][0]['race_id']
    assert schedule[held]['post']==DAY+'T15:55:00+09:00'
    assert schedule[held]['scope_decision']['status']=='SCOPE_HOLD'
    save_schedule(tmp_path,plan,schedule)
    with pytest.raises(ValueError,match='BVI_SHADOW_DEFER_PRODUCTION_PENDING:'+held):
        fixed.production_priority_window(req_for(plan),root=tmp_path,
            now=datetime.fromisoformat(DAY+'T15:10:00+09:00'),
            signed_final_ids=[rid for rid in plan['management_race_ids'] if rid!=held])


@pytest.mark.parametrize('mutation',[
    'bad_marker','bad_hash','duplicate_entry','jump_promoted','missing_fact',
    'duplicate_target','drop_held_target','extra_schedule_status','bad_window',
    'missing_discovery_row','duplicate_venue','false_flat_surface','wrong_meeting_year',
])
def test_self_rehashed_tampering_is_rejected_before_routing(mutation):
    plan=fixture_plan()
    if mutation=='bad_marker':plan['dispatch_scope']='ALL'
    elif mutation=='bad_hash':plan['plan_sha256']='0'*64
    elif mutation=='duplicate_entry':plan['entries'][0]['races'].append(12)
    elif mutation=='jump_promoted':plan['entries'][1]['races'].insert(3,4)
    elif mutation=='missing_fact':plan['official_schedule_facts'].pop(plan['management_race_ids'][0])
    elif mutation=='duplicate_target':plan['forward_oos_preregistration']['targets'].append(plan['forward_oos_preregistration']['targets'][0])
    elif mutation=='drop_held_target':plan['forward_oos_preregistration']['targets'].pop(3)
    elif mutation=='extra_schedule_status':plan['official_schedule_facts'][plan['management_race_ids'][0]]['status']='HOLD'
    elif mutation=='bad_window':plan['dispatch_window_minutes_before_post']=[60,20]
    elif mutation=='missing_discovery_row':plan['official_discovery']['venues'][0]['races'].pop()
    elif mutation=='duplicate_venue':plan['official_discovery']['venues'][1]=deepcopy(plan['official_discovery']['venues'][0])
    elif mutation=='false_flat_surface':plan['official_discovery']['venues'][1]['races'][3]['surface']='芝'
    else:plan['official_discovery']['venues'][0]['meeting_key']='0520250501'
    if mutation!='bad_hash':
        plan['official_discovery_sha256']=sha(plan['official_discovery']); rehash(plan)
    with pytest.raises(ValueError):list(autopilot.plan_entries(plan,DAY))


def test_missing_plan_is_exclusively_created_and_existing_bytes_are_never_normalized(tmp_path,monkeypatch):
    discovery=fixture_discovery(); venues={v['venue']:v for v in discovery['venues']}
    import family_authority_guard
    monkeypatch.setattr(family_authority_guard,'resolve_current_authority',lambda *a,**k:(None,authority()))
    calls=[]
    def resolve(day,venue):
        calls.append((day,venue)); v=venues[venue]; return v['meeting_key'],v['races']
    kwargs={'default_all':True,'cache':{},'meetings':lambda d:list(venues),'resolve':resolve,
        'observed_clock':lambda:datetime.fromisoformat(DAY+'T08:00:00+09:00')}
    assert plans.ensure_future_plan(tmp_path,DAY,**kwargs)
    path=tmp_path/f'runtime/jra_race_day_plan/{DAY}.json'; original=path.read_bytes()
    assert len(calls)==2
    assert plans.ensure_future_plan(tmp_path,DAY,**kwargs)
    assert path.read_bytes()==original and len(calls)==2
    with pytest.raises(FileExistsError):plans.persist_future_plan(tmp_path,json.loads(original))


def test_denied_acquisition_is_not_retried_by_the_builder(tmp_path):
    from urllib.error import HTTPError
    calls=[]
    def denied(day):
        calls.append(day); raise HTTPError('https://www.jra.go.jp/',403,'Forbidden',{},None)
    cache={}
    for _ in range(2):
        assert not plans.ensure_future_plan(tmp_path,DAY,default_all=True,cache=cache,
            meetings=denied,resolve=lambda *a:pytest.fail('No fallback permitted'),
            observed_clock=lambda:datetime.fromisoformat(DAY+'T08:00:00+09:00'))
    assert calls==[DAY]
    failure=json.loads((tmp_path/'runtime_out/jra_bvi_day_plan_failure.json').read_text())
    assert failure['status']=='BLOCKED' and failure['forward_oos_increment']==0
    assert not (tmp_path/f'runtime/jra_race_day_plan/{DAY}.json').exists()


def test_failed_bootstrap_keeps_independent_flat_production_and_blocks_only_research(tmp_path,monkeypatch,capsys):
    monkeypatch.setattr(plans,'ensure_future_plan',lambda *a,**k:False)
    calls=[]
    def tick(*a,**kwargs):
        calls.append(kwargs)
        return [{'race_id':'UNIT_ONLY','status':'DISPATCH'}]
    monkeypatch.setattr(autopilot,'tick',tick)
    monkeypatch.setattr(autopilot,'_pending_work',lambda *a,**k:False)
    assert autopilot.main(['--repo-root',str(tmp_path),'--date',DAY,'--all-races-default'])==0
    output=capsys.readouterr().out
    assert 'BLOCKED_OFFICIAL_PRIORITY_PLAN_BOOTSTRAP' in output
    assert 'FIXED_D_RESEARCH_ONLY' in output
    assert len(calls)==1 and calls[0]['flat_scope_only'] is True
    assert not (tmp_path/f'runtime/jra_race_day_plan/{DAY}.json').exists()


@pytest.mark.parametrize('saved_plan',[True,False])
def test_incomplete_research_census_cannot_stop_an_independently_valid_flat_race(tmp_path,saved_plan):
    plan=fixture_plan()
    if saved_plan:plans.persist_future_plan(tmp_path,plan)
    discovery=fixture_discovery(); discovery['venues'][0]['races'].pop()
    days={v['venue']:(v['meeting_key'],v['races']) for v in discovery['venues']}
    target=discovery['venues'][0]['races'][3]
    post=datetime.fromisoformat(DAY+'T'+target['post_time']+':00+09:00')
    sent=[]
    out=autopilot.tick(tmp_path,DAY,post-timedelta(minutes=40),
        default_all=True,flat_scope_only=not saved_plan,
        resolve=lambda d,v:days[v],meetings=lambda d:list(days),resolver_runs={},
        dispatch=lambda *a:sent.append(a))
    assert any(v=='東京' and n==4 for v,n,*_ in sent)
    assert not any(v=='京都' and n==4 for v,n,*_ in sent)
    if saved_plan:
        schedule=json.loads((tmp_path/f'runtime/jra_race_day_plan/{DAY}.schedule.json').read_text())
        assert schedule[f'{DAY}:BVI_PRIORITY_CENSUS']['status']=='RESEARCH_PRIORITY_CENSUS_UNVERIFIED'
        with pytest.raises(ValueError,match='BVI_SHADOW_DEFER_ALL_RACES_SCOPE_UNVERIFIED'):
            fixed.production_priority_window(req_for(plan),root=tmp_path,now=post-timedelta(minutes=40),
                signed_final_ids=plan['management_race_ids'])
    else:
        assert not (tmp_path/f'runtime/jra_race_day_plan/{DAY}.json').exists()
        with pytest.raises(ValueError,match='BVI_SHADOW_DEFER_OFFICIAL_DAY_PLAN_MISSING'):
            fixed.production_priority_window(req_for(plan),root=tmp_path,now=post-timedelta(minutes=40))


def test_dispatch_date_mismatch_is_rejected():
    with pytest.raises(ValueError,match='BVI_PRIORITY_DISPATCH_DATE_MISMATCH'):
        list(autopilot.plan_entries(fixture_plan(),'2026-11-08'))


def test_durable_claim_publishes_new_validated_plan_in_same_transaction(tmp_path,monkeypatch):
    plan=fixture_plan(); path=plans.persist_future_plan(tmp_path,plan); calls=[]
    def run(argv,**kwargs):
        calls.append(argv)
        return SimpleNamespace(returncode=0,stdout='')
    monkeypatch.setattr(autopilot.subprocess,'run',run)
    autopilot._commit(tmp_path,DAY)
    add=next(c for c in calls if c[:2]==['git','add'])
    assert path.relative_to(tmp_path).as_posix() in add


def test_legacy_explicit_plan_route_is_unchanged():
    plan={'entries':[{'venue':'東京','races':[11,12]}]}
    assert list(autopilot.plan_entries(plan,DAY))==[('東京',11,5000,None),('東京',12,5000,None)]
