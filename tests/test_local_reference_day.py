"""URW dated execution/resume contracts; no network or Runtime POST."""
from copy import deepcopy
from datetime import datetime, timedelta
import gzip
import json
from pathlib import Path
import shutil
import sys

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from runtime import local_reference_day as ref
from runtime import local_race_day_dispatcher as dispatcher
from urw_reference_fixture_support import fixture_root

DAY='2026-10-20'
NOW=datetime.fromisoformat('2026-10-19T18:30:00+09:00')
SYNTHETIC_ROOT=fixture_root()
SAVED=SYNTHETIC_ROOT/'runtime/local_reference'/DAY


@pytest.fixture(autouse=True)
def synthetic_chat_store(monkeypatch):
    from runtime import formal_execution_orchestrator as orchestrator
    monkeypatch.setattr(orchestrator,'ROOT',SYNTHETIC_ROOT)


def plan():
    return json.loads(gzip.decompress((SAVED/'official_plan.json.gz').read_bytes()))


def test_official_twelve_plan_preserves_all_identities_and_cutoffs():
    p=ref.verify_plan(plan(),DAY)
    assert len({r['execution_id'] for r in p['races']})==12
    assert sum(len(r['declared_runner_universe']['runners']) for r in p['races'])==131
    for row in p['races']:
        f=row['fields']
        assert datetime.fromisoformat(f['scheduled_post_at'])-datetime.fromisoformat(f['prediction_cutoff'])==timedelta(seconds=120)
    broken=deepcopy(p);broken['races'][0]['fields']['race_date']='2026-10-19'
    broken['plan_sha256']=ref.sha({k:v for k,v in broken.items() if k!='plan_sha256'})
    with pytest.raises(ValueError,match='BINDING'):ref.verify_plan(broken,DAY)


def test_completed_all_race_readback_calls_no_capture_and_keeps_original_bytes(tmp_path):
    shutil.copytree(SAVED,tmp_path/'runtime/local_reference'/DAY)
    originals={str(p.relative_to(tmp_path)):p.read_bytes() for p in tmp_path.rglob('*')
               if p.is_file() and p.name in {'reference_prediction.json','reference_source.json','answer.txt','publication.json'}}
    def forbidden(*a,**k):pytest.fail('completed race must not regenerate')
    result=ref.run_day(tmp_path,DAY,plan=plan(),generate=forbidden)
    assert result['reference_complete_count']==12
    assert result['runtime_post_count']==result['signed_final_count']==0
    assert not result['user_delivery_verified']
    assert all((tmp_path/p).read_bytes()==raw for p,raw in originals.items())


@pytest.mark.parametrize('damage',['truncate','cross-race','changed-pointer','rehash-incomplete'])
def test_publication_rejects_actual_content_or_identity_damage(tmp_path,damage):
    folder=tmp_path/'R01';shutil.copytree(SAVED/'R01',folder)
    pub=json.loads((folder/'publication.json').read_text())
    if damage in {'truncate','rehash-incomplete'}:
        (folder/'answer.txt').write_text('REFERENCE AVAILABLE この後評価を示します')
        if damage=='rehash-incomplete':
            import hashlib
            pub['answer_sha256']=hashlib.sha256((folder/'answer.txt').read_bytes()).hexdigest()
    if damage=='cross-race':pub['race_no']=2
    if damage=='changed-pointer':pub['reference_directory']='../../R02'
    pub['sha256']=ref.sha({k:v for k,v in pub.items() if k!='sha256'})
    (folder/'publication.json').write_text(json.dumps(pub))
    with pytest.raises(ValueError):ref.verified_readback(folder,{'family_id':'LOCAL','venue_id':'URW','race_date':DAY,'race_no':1})


def test_interrupted_publication_resumes_completed_prediction_without_refitting(tmp_path):
    folder=tmp_path/'R01';shutil.copytree(SAVED/'R01',folder)
    (folder/'publication.json').unlink()
    original=(folder/'attempts/001/reference_prediction.json').read_bytes()
    def cached(intent,output,run_id):
        assert output==folder/'attempts/001'
        from runtime.local_race_entry import run_reference
        return run_reference(intent,output=output,run_id=run_id)
    pub,body=ref.one_race(folder,DAY,1,generate=cached,clock=lambda:NOW)
    assert pub['reference_runner_count']==11 and '最終結論' in body
    assert (folder/'attempts/001/reference_prediction.json').read_bytes()==original
    assert not (folder/'attempts/002').exists()


def test_one_failure_does_not_stop_later_races_or_shrink_denominator(tmp_path):
    shutil.copytree(SAVED,tmp_path/'runtime/local_reference'/DAY)
    (tmp_path/'runtime/local_reference'/DAY/'R01/answer.txt').write_text('truncated')
    status=ref.run_day(tmp_path,DAY,plan=plan(),generate=lambda *a,**k:pytest.fail('must not refetch'))
    assert len(status['races'])==12 and status['reference_complete_count']==11
    assert status['races'][0]['reference_status']=='HOLD'
    assert status['races'][-1]['reference_runner_count']==11
    assert status['reference_all_races_complete'] is False


@pytest.mark.parametrize('number',range(1,13))
def test_normal_chat_entry_reads_each_published_race_without_new_capture(tmp_path,monkeypatch,number):
    from runtime import local_race_entry as entry
    from runtime import formal_execution_orchestrator as orchestrator
    from runtime import local_race_key_shadow_owner as owner
    from scripts import urw_candidate_krs_replay as capture
    def forbidden(*a,**k):pytest.fail('published chat readback must not capture, predict or POST')
    monkeypatch.setattr(capture,'capture_public_urw_sources',forbidden)
    monkeypatch.setattr(owner,'compile_reference_prediction',forbidden)
    monkeypatch.setattr(orchestrator,'orchestrate',forbidden)
    intent=entry.resolve_chat_intent(f'2026年10月20日浦和{number}Rのケイバメトリクス調査願います')
    result=entry.run(intent,output=tmp_path,run_id='published-normal-chat')
    assert result['status']=='FORMAL_BLOCKED_REFERENCE_AVAILABLE'
    assert result['answer_content_check']['content_complete']
    assert result['reference']['answer_origin']=='VERIFIED_FROZEN_REFERENCE_PUBLICATION'
    assert not result['formal_final_proven']
    expected=(SAVED/f'R{number:02d}'/'answer.txt').read_text()
    assert expected in result['message']


def test_dated_reference_start_never_creates_a_formal_intent(tmp_path):
    path=tmp_path/'runtime/local_reference_start_requests'/f'{DAY}.json'
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({'family_id':'LOCAL','venue_id':'URW','race_date':DAY,
        'reference_only':True,'race_numbers':list(range(1,13)),
        'formal_runtime_post_authorized':False,'external_notifications_authorized':False,
        'new_paid_openai_api_requests':0,'request_basis':'TEST_SYNTHETIC_ONLY'}))
    assert ref.resolve_start_request(tmp_path,event='push',changed=[str(path.relative_to(tmp_path))],now=NOW)==DAY
    assert ref.resolve_start_request(tmp_path,event='schedule',now=NOW) is None
    assert ref.resolve_start_request(tmp_path,event='schedule',now=NOW+timedelta(days=1))==DAY
    assert ref.resolve_start_request(tmp_path,event='schedule',now=NOW+timedelta(days=2)) is None
    request=json.loads(path.read_text());request['formal_runtime_post_authorized']=True
    path.write_text(json.dumps(request))
    with pytest.raises(ValueError,match='SCOPE'):ref.resolve_start_request(tmp_path,event='push',changed=[str(path.relative_to(tmp_path))],now=NOW)
    assert not (tmp_path/'runtime/race_key_requests').exists()


def test_future_intake_needs_actual_urw_owner_and_never_dispatches(tmp_path,monkeypatch):
    p=plan()
    # Current production has no URW Owner. A plan is not authorization.
    with pytest.raises(ValueError):dispatcher.preregister_intakes(ROOT,p,{},now=NOW)
    from runtime.family_authority_guard import resolve_current_authority
    current=resolve_current_authority(now=NOW)[1]['manifest_id']
    # Only the future registration mechanics use a synthetic approval here.
    monkeypatch.setattr(dispatcher,'authorization',lambda *a:current)
    a={'race_numbers':[1],'preregister_authorized_races':True,'preregistration_approval_ref':'SYNTHETIC_ONLY'}
    report=dispatcher.preregister_intakes(tmp_path,p,a,now=NOW)
    assert report['registered_count']==1 and report['discovered_count']==12
    assert report['dispatch_count']==report['runtime_posts']==0
    assert not (tmp_path/'runtime/race_key_requests').exists()
    saved=list((tmp_path/'runtime/local_race_registrations'/DAY).glob('*.json'))[0]
    before=saved.read_bytes()
    dispatcher.preregister_intakes(tmp_path,p,a,now=NOW+timedelta(minutes=1))
    assert saved.read_bytes()==before
    altered=json.loads(before);altered['intake_intent']['venue_id']='JRA'
    saved.write_text(json.dumps(altered))
    with pytest.raises(ValueError,match='IMMUTABLE'):dispatcher.preregister_intakes(tmp_path,p,a,now=NOW)


def test_reference_backup_never_wakes_formal_day_worker():
    workflow=(ROOT/'.github/workflows/km-local-race-key-entry.yml').read_text()
    formal=workflow.split('  local-day:',1)[1]
    assert "github.event.schedule == '0,5,10 5 16 10 *'" in formal
    reference=workflow.split('  reference-day:',1)[1].split('  resolve:',1)[0]
    assert 'runtime.local_reference_day' in reference
    assert 'formal_execution_orchestrator' not in reference
    assert 'runtime.local_race_entry' not in reference


def test_new_horse_readback_binds_course_without_rewriting_frozen_answer():
    from runtime import local_race_entry as entry
    folder=SAVED/'R03';attempt=folder/'attempts/001'
    original=(folder/'answer.txt').read_bytes()
    prediction=json.loads((attempt/'reference_prediction.json').read_text())
    source=json.loads((attempt/'reference_source.json').read_text())
    parts=json.loads((folder/'answer_parts.json').read_text())
    body,required=entry.reference_readback_presentation(prediction,source,original.decode(),parts)
    assert 'コース：浦和ダート1400m（左）' in body
    assert body.endswith(original.decode()) and (folder/'answer.txt').read_bytes()==original
    assert entry.reference_answer_content_check(required,body)['content_complete']
    # Actual UI regression: all five UNKNOWN horses and conclusion were present,
    # but the client filled today's 800m into the next day's 1400m race.
    mixed=body.replace('コース：浦和ダート1400m（左）','コース：浦和ダート800m（左）')
    assert not entry.reference_answer_content_check(required,mixed)['content_complete']
    with pytest.raises(ValueError,match='COMPLETE_BODY'):
        entry.reference_readback_presentation(prediction,source,original.decode().split('最終結論')[0],parts)


def test_readback_course_cannot_come_from_a_different_frozen_card():
    from runtime import local_race_entry as entry
    folder=SAVED/'R03';attempt=folder/'attempts/001'
    prediction=json.loads((attempt/'reference_prediction.json').read_text())
    source=json.loads((attempt/'reference_source.json').read_text())
    other=json.loads((SAVED/'R07/attempts/001/reference_source.json').read_text())
    source['sources']=other['sources']
    with pytest.raises(ValueError,match='SOURCE_BINDING'):
        entry.reference_readback_presentation(prediction,source,(folder/'answer.txt').read_text(),json.loads((folder/'answer_parts.json').read_text()))


def test_new_chat_request_publishes_for_other_output_and_day_worker(tmp_path,monkeypatch):
    from runtime import local_race_entry as entry
    from runtime import formal_execution_orchestrator as orchestrator
    monkeypatch.setattr(orchestrator,'ROOT',tmp_path)
    monkeypatch.setattr(entry,'_chat_final',lambda *a:(None,[]))
    monkeypatch.setattr(entry,'chat_formal_status',lambda *a:{'status':'BLOCKED',
        'first_failed_stage':'AUTHORIZATION','code':'VENUE_OWNER_NOT_AUTHORIZED'})
    original=entry.run_reference;calls=[]
    def capture_once(intent,*,output,run_id):
        if not (output/'reference_prediction.json').exists():
            calls.append(output)
            # Authored TEST_SYNTHETIC_ONLY fixture stands in for one capture.
            shutil.copytree(SAVED/'R05/attempts/001',output)
            return json.loads((output/'entry_report.json').read_text())
        return original(intent,output=output,run_id=run_id)
    monkeypatch.setattr(entry,'run_reference',capture_once)
    intent=entry.resolve_chat_intent('2026年10月20日浦和5Rのケイバメトリクス調査願います')
    first=entry.run_chat(intent,output=tmp_path/'chat1',run_id='new')
    published=tmp_path/'runtime/local_reference'/DAY/'R05'
    before={p.name:p.read_bytes() for p in published.iterdir() if p.suffix in {'.txt','.json'}}
    assert first['reference_generation_executed'] and first['answer_content_check']['content_complete']
    second=entry.run_chat(intent,output=tmp_path/'chat2',run_id='readback')
    assert not second['reference_generation_executed'] and len(calls)==1
    assert (published/'readback.txt').read_text() in second['message']
    assert second['reference']['answer_origin']=='VERIFIED_FROZEN_REFERENCE_PUBLICATION'
    ref.one_race(published,DAY,5,generate=lambda *a,**k:pytest.fail('day worker cannot generate again'))
    assert {p.name:p.read_bytes() for p in published.iterdir() if p.suffix in {'.txt','.json'}}==before
    assert not (tmp_path/'research').exists()


@pytest.mark.parametrize('corruption',['missing','changed'])
def test_new_publication_binds_the_full_chat_readback(tmp_path,corruption):
    folder=tmp_path/'R05'
    def generate(intent,*,output,run_id):
        shutil.copytree(SAVED/'R05/attempts/001',output)
        return json.loads((output/'entry_report.json').read_text())
    pub,_=ref.one_race(folder,DAY,5,generate=generate)
    assert pub['readback_sha256']==__import__('hashlib').sha256((folder/'readback.txt').read_bytes()).hexdigest()
    if corruption=='missing':(folder/'readback.txt').unlink()
    else:(folder/'readback.txt').write_text('search results only')
    with pytest.raises((ValueError,OSError)):
        ref.one_race(folder,DAY,5,generate=lambda *a,**k:pytest.fail('corruption cannot trigger regeneration'))


def test_simultaneous_chat_and_day_publication_captures_once(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    folder=tmp_path/'R05';start=Barrier(2);calls=[]
    def generate(intent,*,output,run_id):
        calls.append(output)
        shutil.copytree(SAVED/'R05/attempts/001',output)
        return json.loads((output/'entry_report.json').read_text())
    def request():
        start.wait(timeout=5)
        return ref.one_race(folder,DAY,5,generate=generate)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(request) for _ in range(2)]
        results=[f.result(timeout=20) for f in futures]
    assert len(calls)==1 and results[0]==results[1]
    assert len(list((folder/'attempts').iterdir()))==1


@pytest.mark.parametrize('missing_prose',[False,True])
def test_completed_forecast_without_receipt_resumes_without_capture_or_fit(tmp_path,monkeypatch,missing_prose):
    from runtime import local_race_entry as entry
    from runtime import local_race_key_shadow_owner as owner
    from scripts import urw_candidate_krs_replay as capture
    folder=tmp_path/'R05';attempt=folder/'attempts/001'
    shutil.copytree(SAVED/'R05/attempts/001',attempt)
    (attempt/'entry_report.json').unlink()
    if missing_prose:(attempt/'reference_prediction.md').unlink()
    originals={name:(attempt/name).read_bytes() for name in ('reference_prediction.json','reference_source.json','reference_intent.json')}
    def forbidden(*a,**k):pytest.fail('frozen forecast must not capture or refit')
    monkeypatch.setattr(capture,'capture_public_urw_sources',forbidden)
    monkeypatch.setattr(owner,'compile_reference_prediction',forbidden)
    pub,body=ref.one_race(folder,DAY,5)
    assert pub['reference_runner_count']==12 and '最終結論' in body
    assert (attempt/'entry_report.json').is_file() and (attempt/'reference_prediction.md').is_file()
    assert {name:(attempt/name).read_bytes() for name in originals}==originals
    assert not (folder/'attempts/002').exists()


def test_late_uncaptured_race_does_not_fetch_or_stop_saved_later_races(tmp_path):
    shutil.copytree(SAVED,tmp_path/'runtime/local_reference'/DAY)
    shutil.rmtree(tmp_path/'runtime/local_reference'/DAY/'R01')
    def forbidden(*a,**k):pytest.fail('late unseen race must not capture')
    late=datetime.fromisoformat('2026-10-20T12:19:00+09:00')
    result=ref.run_day(tmp_path,DAY,plan=plan(),generate=forbidden,clock=lambda:late)
    assert result['races'][0]['error']=='ValueError:REFERENCE_DEADLINE_NO_NEW_FORECAST'
    assert result['reference_complete_count']==11 and len(result['races'])==12
    assert not (tmp_path/'runtime/local_reference'/DAY/'R01/attempts').exists()


def test_automatic_discovery_does_not_require_per_day_manual_requests(tmp_path,monkeypatch):
    shutil.copytree(SAVED,tmp_path/'runtime/local_reference'/DAY)
    seen=[]
    def discover(root,day,**kwargs):
        seen.append(day)
        if day=='2026-10-19':raise ValueError('OFFICIAL_SOURCE_UNAVAILABLE')
        return plan()
    monkeypatch.setattr(ref,'prepare_plan',discover)
    result=ref.run_discovery_window(tmp_path,now=NOW,
        generate=lambda *a,**k:pytest.fail('completed next-day references must not generate'))
    assert seen==['2026-10-19',DAY]
    assert result['days'][0]['status']=='HOLD_REFERENCE_PREPARATION'
    assert result['days'][1]['reference_complete_count']==12
    assert result['runtime_post_count']==0 and not result['formal_final_proven']
    assert not (tmp_path/'runtime/local_reference_start_requests').exists()
    with pytest.raises(ValueError,match='WINDOW_DATE'):
        ref.run_discovery_window(tmp_path,now=NOW,start_day='2026-10-21')
