"""Bounded collection, immutable resume and no unverified Production admission."""
import hashlib,json,sys
from pathlib import Path
from unittest.mock import patch
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'runtime/jra_source_runtime')]
from scripts.jra_weekend_bvi_intake import day_plan,collect_window,producer_valid
from jra_pedigree_harvest import race_reference,harvest_day,_Client


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
       'race_observations':[{'race_id':r} for r in ['A','B','C']]}
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
