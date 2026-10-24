"""Bounded collection, immutable resume and no unverified Production admission."""
import hashlib,json,sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'runtime/jra_source_runtime')]
from scripts.jra_weekend_bvi_intake import day_plan,collect_window,producer_valid,resolve_scheduled_target
from jra_pedigree_harvest import race_reference,harvest_day,_Client


def test_actual_midnight_delayed_results_use_due_day_not_job_today():
    # Actual failed GitHub schedule40109566451: it started after JST midnight.
    result = resolve_scheduled_target('20 12 * * 6,0,1',
        run_created_at=datetime.fromisoformat('2026-10-24T16:00:39+00:00'),
        observed_at=datetime.fromisoformat('2026-10-24T16:00:59+00:00'))
    assert result['date'] == '2026-10-24' and result['mode'] == 'results'
    assert result['inferred_due_at'] == '2026-10-24T12:20:00+00:00'
    assert result['observed_at'] == '2026-10-24T16:00:59+00:00'
    assert result['run_created_at'] == '2026-10-24T16:00:39+00:00'
    assert result['reference_scope'] == 'SCHEDULING_ONLY_NOT_SOURCE_CAPTURE_OR_PREDICTION_EVIDENCE'
    assert 'harvested_at' not in result and 'prediction_cutoff' not in result


def test_retry_retains_original_run_date_and_actual_later_observation_clock():
    created = datetime.fromisoformat('2026-10-24T16:00:39+00:00')
    original = resolve_scheduled_target('20 12 * * 6,0,1',run_created_at=created,
        observed_at=datetime.fromisoformat('2026-10-24T16:00:59+00:00'))
    retry = resolve_scheduled_target('20 12 * * 6,0,1',run_created_at=created,
        observed_at=datetime.fromisoformat('2026-10-26T16:00:59+00:00'))
    assert retry['date'] == original['date'] == '2026-10-24'
    assert retry['inferred_due_at'] == original['inferred_due_at']
    assert retry['observed_at'] == '2026-10-26T16:00:59+00:00'


@pytest.mark.parametrize('schedule,created,expected_date,expected_due,mode',[
    ('20 21 * * 5,6,0','2026-10-23T21:20:01+00:00','2026-10-24','2026-10-23T21:20:00+00:00','cards'),
    ('20 21 * * 5,6,0','2026-10-24T21:20:00+00:00','2026-10-25','2026-10-24T21:20:00+00:00','cards'),
    ('20 21 * * 5,6,0','2026-10-25T21:20:00+00:00','2026-10-26','2026-10-25T21:20:00+00:00','cards'),
    ('20 12 * * 6,0,1','2026-10-26T12:20:00+00:00','2026-10-26','2026-10-26T12:20:00+00:00','results'),
    ('20 12 * * 6,0,1','2026-10-25T12:19:59+00:00','2026-10-24','2026-10-24T12:20:00+00:00','results'),
    ('20 21 * * 5,6,0','2026-10-25T08:51:00+09:00','2026-10-25','2026-10-24T21:20:00+00:00','cards'),
])
def test_existing_cron_dates_use_utc_weekdays_and_jst_target(schedule,created,expected_date,expected_due,mode):
    stamp = datetime.fromisoformat(created)
    result = resolve_scheduled_target(schedule,run_created_at=stamp,observed_at=stamp)
    assert result['date'] == expected_date and result['mode'] == mode
    assert result['inferred_due_at'] == expected_due
    assert datetime.fromisoformat(result['inferred_due_at']) <= stamp


@pytest.mark.parametrize('schedule',['','* * * * *','20 12 * * 0,6,1',None,[],{}])
def test_unregistered_schedule_cannot_infer_a_target(schedule):
    now = datetime(2026,10,24,16,tzinfo=timezone.utc)
    with pytest.raises(ValueError,match='SCHEDULE_UNSUPPORTED'):
        resolve_scheduled_target(schedule,run_created_at=now,observed_at=now)


@pytest.mark.parametrize('created,observed',[
    (datetime(2026,10,24,16),datetime(2026,10,24,16,tzinfo=timezone.utc)),
    (datetime(2026,10,24,16,tzinfo=timezone.utc),datetime(2026,10,24,16)),
    ('2026-10-24T16:00:00+00:00',datetime(2026,10,24,16,tzinfo=timezone.utc)),
    (datetime(2026,10,24,16,tzinfo=timezone.utc),'2026-10-24T16:00:00+00:00'),
])
def test_schedule_requires_explicit_aware_datetime_clocks(created,observed):
    with pytest.raises(ValueError,match='SCHEDULE_AWARE_CLOCK_REQUIRED'):
        resolve_scheduled_target('20 12 * * 6,0,1',run_created_at=created,observed_at=observed)


def test_future_original_run_clock_is_rejected():
    observed = datetime(2026,10,24,16,tzinfo=timezone.utc)
    with pytest.raises(ValueError,match='RUN_CREATED_IN_FUTURE'):
        resolve_scheduled_target('20 12 * * 6,0,1',run_created_at=observed+timedelta(seconds=1),observed_at=observed)


@pytest.mark.parametrize('schedule,created',[
    ('20 12 * * 6,0,1','2026-10-27T12:20:00+00:00'),
    ('20 21 * * 5,6,0','2026-10-27T21:20:00+00:00'),
    ('20 12 * * 6,0,1','2026-10-24T12:19:59+00:00'),
])
def test_stale_or_ambiguous_schedule_reference_fails_without_guessing(schedule,created):
    stamp = datetime.fromisoformat(created)
    with pytest.raises(ValueError,match='SCHEDULE_STALE_OR_AMBIGUOUS_REFERENCE'):
        resolve_scheduled_target(schedule,run_created_at=stamp,observed_at=stamp)


class OfficialDay:
    def __init__(self,codes=('04','05','08')):
        self.calls=[];self.codes=codes
        self.days=[f'pw01srl00{c}2026040320261024/AB' for c in codes]
    def get(self,path):
        self.calls.append(path);return "doAction('/JRADB/accessS.html','ROOT')"
    def post(self,path,token):
        self.calls.append(token)
        if token=='ROOT':return ' '.join(self.days)
        for code,day in zip(self.codes,self.days):
            if token==day:return ' '.join(f'pw01sde01{code}20260403{n:02d}20261024/AB' for n in range(1,13))
        raise AssertionError('Planner must not request a race or horse page')


def window():return {'date':'2026-10-24','mode':'results','start':0,'race_ids':['A','B','C']}
def data(count=10,tokens=10):
    x={'profile':'KM-JRA-OFFICIAL-PEDIGREE-HARVEST-v1.0-20261010','official':True,'source':'www.jra.go.jp',
       'horse_count':count,'horse_token_count':tokens,'horses':[{'profile_token_sha256':str(i),'sire':'S','dam':'D'} for i in range(count)],
       'race_observations':[{'race_id':r,'universe_status':'OBSERVED_OFFICIAL'} for r in ['A','B','C']]}
    x['sha256']=hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest();return x


def test_36_races_are_12_sequential_windows_without_horse_requests():
    c=OfficialDay();w=day_plan('2026-10-24','results',client=c)
    assert len(w)==12 and {x['start'] for x in w}==set(range(0,36,3))
    ids=[r for b in w for r in b['race_ids']];assert len(ids)==len(set(ids))==36
    assert len(c.calls)==8


@pytest.mark.parametrize('code',['01','02','03','04','05','06','07','08','09','10'])
def test_all_ten_venues_use_observed_navigation_not_permanent_ids(code):
    ref=race_reference(f'pw01sde01{code}202604030120261024/AB','2026-10-24')
    assert ref['race_no']==1 and ref['identity_kind'].endswith('NOT_PERMANENT_REGISTRY_ID')


def test_complete_window_is_not_reacquired_or_overwritten(tmp_path):
    p=tmp_path/'runtime/pedigree_corpus/20261024-results-race0-r3.json';p.parent.mkdir(parents=True)
    x=data();p.write_text(json.dumps(x));before=p.read_bytes()
    result=collect_window(window(),tmp_path,run_id='1',verifier=lambda p:x,
                          collector=lambda *a,**k:pytest.fail('duplicate request'))
    assert result['status']=='ALREADY_VERIFIED_COMPLETE' and p.read_bytes()==before


def test_partial_window_reuses_verified_profiles_and_preserves_original(tmp_path):
    p=tmp_path/'runtime/pedigree_corpus/20261024-results-race0-r3.json';p.parent.mkdir(parents=True)
    old=data(9);p.write_text(json.dumps(old));before=p.read_bytes();received=[]
    def acquire(*a,**kw):received.append(kw['existing_horses']);return data()
    result=collect_window(window(),tmp_path,run_id='2',verifier=lambda p:old,collector=acquire)
    assert result['new'] and len(received[0])==9 and 'retry-2' in result['file']
    assert p.read_bytes()==before


def test_unattested_cache_is_never_reused(tmp_path):
    p=tmp_path/'runtime/pedigree_corpus/20261024-results-race0-r3.json';p.parent.mkdir(parents=True);p.write_text(json.dumps(data()))
    def acquire(*a,**kw):assert not kw['existing_horses'];return data()
    assert collect_window(window(),tmp_path,run_id='3',verifier=lambda p:None,collector=acquire)['new']


def test_access_denial_stops_remaining_windows_without_requests(tmp_path):
    from urllib.error import HTTPError
    calls=[]
    def acquire(*a,**kw):calls.append(1);raise HTTPError('https://www.jra.go.jp/',429,'refused',{},None)
    first=collect_window(window(),tmp_path,run_id='4',verifier=lambda p:None,collector=acquire)
    later={**window(),'start':3}
    second=collect_window(later,tmp_path,run_id='4',verifier=lambda p:None,collector=acquire)
    assert first['access_refused'] and second['status']=='DEFERRED_ACCESS_REFUSED' and len(calls)==1
    assert not list((tmp_path/'runtime/pedigree_corpus').glob('*'))


@pytest.mark.parametrize('code',[403,429])
def test_access_denial_is_not_erased_by_later_universe_error(tmp_path,code):
    calls=[]
    def acquire(*a,**kw):
        calls.append(1);obj=data();obj['access_refused']=True
        obj['errors']=[f'HTTPError:{code}'];obj['race_observations'][0]['race_id']='CHANGED'
        obj['sha256']=hashlib.sha256(json.dumps({k:v for k,v in obj.items() if k!='sha256'},ensure_ascii=False,sort_keys=True).encode()).hexdigest()
        return obj
    first=collect_window(window(),tmp_path,run_id='refusal-'+str(code),verifier=lambda p:None,collector=acquire)
    second=collect_window({**window(),'start':3},tmp_path,run_id='refusal-'+str(code),verifier=lambda p:None,collector=acquire)
    assert first['access_refused'] and 'UNIVERSE_CHANGED' in first['error']
    assert second['status']=='DEFERRED_ACCESS_REFUSED' and len(calls)==1


def test_low_coverage_is_isolated_outside_corpus(tmp_path):
    r=collect_window(window(),tmp_path,run_id='5',verifier=lambda p:None,collector=lambda *a,**k:data(8))
    assert r['status']=='QUARANTINED_ACQUISITION' and not r['new']
    assert (tmp_path/r['quarantine']).exists()
    assert not list((tmp_path/'runtime/pedigree_corpus').glob('*'))


def test_changed_race_universe_is_not_admitted(tmp_path):
    r=collect_window({**window(),'race_ids':['X','B','C']},tmp_path,run_id='6',verifier=lambda p:None,collector=lambda *a,**k:data())
    assert not r['new'] and 'UNIVERSE_CHANGED' in r['error']


def test_modified_producer_bytes_are_rejected():
    x=data();assert producer_valid(x);x['horse_count']=999;assert not producer_valid(x)


def test_unresolved_runner_universe_is_not_admitted(tmp_path):
    x=data();x['race_observations'][0]['universe_status']='UNRESOLVED'
    x['sha256']=hashlib.sha256(json.dumps({k:v for k,v in x.items() if k!='sha256'},ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    r=collect_window(window(),tmp_path,run_id='7',verifier=lambda p:None,collector=lambda *a,**k:x)
    assert not r['new'] and 'UNIVERSE_UNRESOLVED' in r['error']


def test_weekday_meeting_is_not_skipped_by_new_cursor_mode():
    from scripts.jra_pedigree_backfill_cursor import advance
    state={'status':'ACTIVE','date':'2026-09-26','start_race':33,'race_batch_size':3,'earliest_date':'2023-01-01'}
    assert advance(state,previous_official_date='2026-09-21',require_official_calendar=True)['date']=='2026-09-21'
    held=advance(state,require_official_calendar=True)
    assert held['date']==state['date'] and held['start_race']==33
    assert 'NO_WEEKDAY_GUESS' in held['calendar_resolution_status']


def test_client_formal_retry_default_is_unchanged():
    assert _Client().stop_on_access_denied is False
    assert _Client(stop_on_access_denied=True).stop_on_access_denied is True


def test_previous_official_day_uses_observed_monday_not_weekend_guess():
    from jra_pedigree_harvest import previous_official_race_date
    class Calendar:
        def get(self,path):return "doAction('/JRADB/accessS.html','pw01sklROOT')"
        def post(self,path,token):
            if token=='pw01sklROOT':return ('var yearMonth = "202610"; objParam["2609"]="AB"; '
                'pw01skl00 pw01skl10 Number(arg) >= yearMonth objParam[String(arg).substring(2,6)] '
                '<select name="kaisaiY_list"><option value="2026"></option></select>'
                '<select name="kaisaiM_list"><option value="09"></option></select>')
            assert token=='pw01skl10202609/AB'
            return 'pw01srl00042026040320260921/AB pw01srl00042026040320260926/AB'
    assert previous_official_race_date(Calendar(),'2026-09-26')=='2026-09-21'


def test_workflow_is_serial_and_never_connects_to_formal_or_krs():
    text=(ROOT/'.github/workflows/km-jra-pedigree-corpus-harvest.yml').read_text()
    assert 'max-parallel: 1' in text and 'cancel-in-progress: false' in text
    assert 'ADMISSION_OUTCOME' in text and 'test "$ADMISSION_OUTCOME" = success' in text
    assert '/krs/' not in text and 'km-jra-formal' not in text
    assert 'HEAD:$TARGET_BRANCH' in text


def test_real_aki_no_bet_full20_bvi_is_not_misclassified_as_uncomputed():
    from jra_aki_no_bet_terminal import verify_aki_no_bet_terminal
    from jra_bvi_consumption import build_bvi_consumption
    mapping=json.loads((ROOT/'mapping/jra_base_index_evidence_mapping_v1.0_20260921.json').read_text())
    total=0
    for race in ('NGT-20261024-R01','KYO-20261024-R04','TKY-20261024-R05'):
        terminal=json.loads((ROOT/'runtime/jra_no_bet_terminals'/f'KM-JRA-{race}-LIVE-R1.json').read_text())
        verified=verify_aki_no_bet_terminal(terminal,require_live=True,root=ROOT)
        proof=build_bvi_consumption(terminal['failure_report']['prepared_numerical_request'],mapping)
        assert verified['actual_full20'] and not verified['signed_final_verified']
        assert len(proof['runners'])*20==verified['terminal_index_count']
        assert verified['total_investment']==0
        total+=len(proof['runners'])
    assert total==40
