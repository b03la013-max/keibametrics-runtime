"""TEST_SYNTHETIC_ONLY public-presentation contracts, never live acceptance."""
from copy import deepcopy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil

import pytest

from runtime import local_reference_delivery as delivery
from urw_reference_fixture_support import fixture_root

DAY='2026-10-20'
INTENT={'family_id':'LOCAL','venue_id':'URW','race_date':DAY,'race_no':5}


def exported(tmp_path):
    original=fixture_root()/'runtime/local_reference'/DAY/'R05'
    before=(original/'readback.txt').read_bytes()
    manifest=delivery.export_publication(original,tmp_path)
    folder=tmp_path/'runtime/local_reference_delivery'/DAY/'R05'
    assert (folder/'readback.txt').read_bytes()==before
    assert manifest['TEST_SYNTHETIC_ONLY'] is True
    assert 'TEST_SYNTHETIC_ONLY' in before.decode()
    return folder,manifest,before


def test_export_and_read_are_identical_body_with_limited_scope_no_source_or_prediction(tmp_path,monkeypatch):
    folder,manifest,original=exported(tmp_path)
    from runtime import local_race_entry as entry
    from scripts import urw_candidate_krs_replay as capture
    from runtime import local_race_key_shadow_owner as owner
    def forbidden(*a,**k):pytest.fail('published presentation cannot capture, predict or reverify raw source')
    monkeypatch.setattr(capture,'capture_public_urw_sources',forbidden)
    monkeypatch.setattr(owner,'compile_reference_prediction',forbidden)
    monkeypatch.setattr(entry,'run_reference',forbidden)
    report,body=delivery.read_publication(tmp_path,INTENT)
    assert body.encode()==original
    assert report['reference_readback_only'] and not report['prediction_reexecution']
    assert report['verification_scope']==delivery.SCOPE
    assert not report['source_freshness_claim'] and not report['source_raw_reverified']
    assert not report['signature_verified'] and not report['formal_final_proven']
    assert not report['delivery']['chat_render_verified']
    assert len(manifest['runners'])==12 and '最終結論' in body


@pytest.mark.parametrize('damage',['truncated-body','missing-horse-rehashed','cross-race-rehashed',
    'model-components-rehashed','invent-model-sha-rehashed','cutoff-rehashed','formal-rehashed'])
def test_corrupt_public_presentation_holds_even_with_rehashed_manifest(tmp_path,damage):
    folder,m,original=exported(tmp_path)
    body=original.decode()
    if damage=='truncated-body':
        body=body.split('最終結論')[0]
    if damage=='missing-horse-rehashed':
        paragraph=m['runners'][0]['required_part']
        body=body.replace(paragraph,'')
        m['required_parts'].remove(paragraph)
        m['required_parts_sha256']=delivery.sha(m['required_parts'])
        m['body_sha256']=hashlib.sha256(body.encode()).hexdigest()
    if damage=='cross-race-rehashed':m['race_no']=6
    if damage=='model-components-rehashed':
        key=next(iter(m['method_components_sha256']))
        m['method_components_sha256'][key]='a'*64
        m['method_binding_sha256']=delivery.sha({'method':m['method'],'components':m['method_components_sha256']})
    if damage=='invent-model-sha-rehashed':m['model_sha256']='a'*64
    if damage=='cutoff-rehashed':m['prediction_cutoff']='2026-10-20T14:17:00+09:00'
    if damage=='formal-rehashed':m['formal_final_proven']=True
    m['sha256']=delivery.sha({k:v for k,v in m.items() if k!='sha256'})
    (folder/'manifest.json').write_text(json.dumps(m))
    (folder/'readback.txt').write_text(body)
    with pytest.raises(ValueError,match='PUBLIC_REFERENCE_PRESENTATION_HOLD'):
        delivery.read_publication(tmp_path,INTENT)


def test_chat_prefers_existing_canonical_and_only_reads_public_when_raw_cache_absent(tmp_path,monkeypatch):
    from runtime import local_race_entry as entry
    from runtime import formal_execution_orchestrator as orchestrator
    folder,_,original=exported(tmp_path)
    monkeypatch.setattr(orchestrator,'ROOT',tmp_path)
    monkeypatch.setattr(entry,'run_reference',lambda *a,**k:pytest.fail('public readback cannot generate'))
    report,body=entry._chat_reference(INTENT,output=tmp_path/'out',run_id='synthetic-public')
    assert original.decode() in body and delivery.NOTICE in body
    assert report['answer_origin']=='PUBLISHED_REFERENCE_PRESENTATION'
    assert report['reference_generated_in_this_request'] is False
    canonical=tmp_path/'runtime/local_reference'/DAY/'R05'
    canonical.mkdir(parents=True)
    (canonical/'publication.json').write_text('{}')
    monkeypatch.setattr(delivery,'read_publication',lambda *a:pytest.fail('damaged canonical cannot fall back'))
    with pytest.raises(ValueError,match='REFERENCE_PUBLICATION_HASH'):
        entry._chat_reference(INTENT,output=tmp_path/'out',run_id='canonical-damaged')


def test_public_absence_is_distinct_from_partial_corrupt_publication(tmp_path):
    assert delivery.read_publication(tmp_path,INTENT) is None
    (tmp_path/'runtime/local_reference_delivery'/DAY/'R05').mkdir(parents=True)
    with pytest.raises(ValueError,match='PUBLIC_REFERENCE_PRESENTATION_HOLD'):
        delivery.read_publication(tmp_path,INTENT)


def test_saved_day_reads_fixed_cohort_without_discovery_and_one_hold_does_not_stop_later(tmp_path,monkeypatch):
    index=delivery.export_day(fixture_root(),tmp_path,DAY)
    assert index['TEST_SYNTHETIC_ONLY'] is True
    from scripts import urw_candidate_krs_replay as capture
    from runtime import local_race_key_shadow_owner as owner
    from runtime import local_race_entry as entry
    def forbidden(*a,**k):pytest.fail('saved day cannot fetch, generate or raw-reverify')
    monkeypatch.setattr(capture,'capture_public_urw_sources',forbidden)
    monkeypatch.setattr(owner,'compile_reference_prediction',forbidden)
    monkeypatch.setattr(entry,'run_reference',forbidden)
    status=delivery.read_delivery_day(tmp_path,DAY)
    assert status['reference_complete_count']==status['cohort_count']==12
    assert status['current_discovery_count']==status['new_forecast_count']==0
    assert status['verification_scope']==delivery.SCOPE
    assert all(r['reference_readback_only'] for r in status['races'])
    assert not status['source_freshness_claim'] and not status['permanent_autonomy_proven']
    assert not status['user_delivery_verified']
    target=tmp_path/'runtime/local_reference_delivery'/DAY/'R01/readback.txt'
    target.write_text('search results only')
    status=delivery.read_delivery_day(tmp_path,DAY)
    assert status['reference_complete_count']==11 and status['cohort_count']==12
    assert status['races'][0]['reference_status']=='HOLD'
    assert status['races'][-1]['reference_status']=='AVAILABLE_VERIFIED_PUBLISHED_PRESENTATION'
    assert not status['reference_all_races_complete']


def test_discovery_window_reuses_published_day_when_another_day_source_fails(tmp_path,monkeypatch):
    from runtime import local_reference_day as ref
    delivery.export_day(fixture_root(),tmp_path,DAY)
    calls=[]
    def unavailable(root,day,**kwargs):
        calls.append(day)
        raise ValueError('OFFICIAL_SOURCE_UNAVAILABLE')
    monkeypatch.setattr(ref,'prepare_plan',unavailable)
    result=ref.run_discovery_window(tmp_path,now=datetime.fromisoformat('2026-10-19T22:00:00+09:00'))
    assert calls==['2026-10-19']
    saved=result['days'][1]
    assert saved['reference_complete_count']==saved['cohort_count']==12
    assert saved['discovered_count']==saved['current_discovery_count']==0
    assert saved['source_freshness_claim'] is False
    assert saved['permanent_autonomy_proven'] is False
    assert result['days'][0]['status']=='HOLD_REFERENCE_PREPARATION'


def test_day_index_cannot_change_runner_count_or_deadline_while_rehashing(tmp_path):
    delivery.export_day(fixture_root(),tmp_path,DAY)
    path=tmp_path/'runtime/local_reference_delivery'/DAY/'index.json'
    index=json.loads(path.read_text())
    index['races'][0]['runner_count']+=1
    index['races'][1]['prediction_cutoff']='2026-10-20T12:47:00+09:00'
    index['sha256']=delivery.sha({k:v for k,v in index.items() if k!='sha256'})
    path.write_text(json.dumps(index))
    status=delivery.read_delivery_day(tmp_path,DAY)
    assert status['reference_complete_count']==10 and status['cohort_count']==12
    assert [r['reference_status'] for r in status['races'][:2]]==['HOLD','HOLD']
    assert status['races'][-1]['reference_status']=='AVAILABLE_VERIFIED_PUBLISHED_PRESENTATION'
