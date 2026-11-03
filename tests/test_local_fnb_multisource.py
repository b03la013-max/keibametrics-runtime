"""Synthetic Provider responses only; no official horse data or network."""
from datetime import datetime, timezone
import hashlib
import json
from dataclasses import replace
from unittest.mock import Mock
import pytest
from runtime import local_fnb_multisource as m

NOW='2026-11-03T03:30:00+00:00'
INTENT={'venue_id':'FNB','race_date':'2026-11-03','race_no':2}
URL='https://nar.k-ba.net/20261103/19/2/table.html'

def binding(response=None, fields=None):
    response=response or {'raw':b'synthetic provider original','retrieval_method':'HTTPS_GET_ORIGINAL_RESPONSE',
        'http_status':200,'final_url':URL,'access_policy':{'decision':'ALLOW'},
        'captured_at':NOW,'content_type':'text/plain'}
    fields=fields or [{'runner_number':1,'field':'external_speed_index','value':77,
                      'effective_at':'2026-11-03T03:28:00+00:00'}]
    return m.ProviderBinding(provider='SBO_NAR',exact_urls=(URL,),code_sha256='a'*64,
        permission_ref='SYNTHETIC_PERMISSION_NOT_REAL',permission_sha256='b'*64,
        effective_from='2026-11-03T00:00:00+00:00',effective_until='2026-11-04T00:00:00+00:00',
        actor_id='SYNTHETIC_ACTOR',automated_get_admitted=True,private_retention_admitted=True,
        cloud_processing_admitted=True,qualified_field_rules={'external_speed_index':'NOT_A_FORMAL_HPI_RULE'},
        fetch=Mock(return_value=response),parse=Mock(return_value={'identity':INTENT,'fields':fields,'encoding':'ascii'}))

def acquire(b,tmp_path):
    return m.acquire(b,url=URL,intent=INTENT,actor_id='SYNTHETIC_ACTOR',now=NOW,private_root=tmp_path,clock=lambda:NOW)

def test_actual_callback_response_bytes_are_immutable_but_vendor_index_never_formal(tmp_path):
    b=binding();p=acquire(b,tmp_path)
    assert p['raw_bytes']==len(b'synthetic provider original')
    assert (tmp_path/(p['raw_sha256']+'.raw')).read_bytes()==b'synthetic provider original'
    assert p['observations'][0]['tier']==m.TIERS[2]
    assert p['observations'][0]['rule_id'] is None
    assert p['formal_source_admitted'] is False
    assert p['active_universe_verified'] is False
    assert p['signed_source_claim'] is False

@pytest.mark.parametrize('field,value', [('automated_get_admitted',False),('permission_ref',''),
    ('code_sha256','bad'),('cloud_processing_admitted',False),('actor_id','OTHER')])
def test_unqualified_binding_never_calls_transport(tmp_path,field,value):
    b=replace(binding(),**{field:value})
    with pytest.raises(m.MultisourceHold):acquire(b,tmp_path)
    b.fetch.assert_not_called()

@pytest.mark.parametrize('field,value', [('http_status',403),('retrieval_method','SEARCH_SNIPPET'),
    ('raw',b''),('final_url','https://elsewhere.invalid/'),('access_policy',{'decision':'UNKNOWN'}),
    ('captured_at','2026-11-04T00:00:00+00:00')])
def test_response_cannot_bypass_original_policy_or_time(tmp_path,field,value):
    b=binding();r=b.fetch.return_value.copy();r[field]=value;b.fetch.return_value=r
    with pytest.raises(m.MultisourceHold):acquire(b,tmp_path)
    assert not list(tmp_path.glob('*.raw'))

def test_display_name_is_not_permanent_identity(tmp_path):
    b=binding(fields=[{'runner_number':1,'field':'horse_id','value':'NAME:TEST',
        'effective_at':'2026-11-03T03:28:00+00:00','identity_kind':'NAME_MATCH'}])
    with pytest.raises(m.MultisourceHold,match='PERMANENT_ID_NOT_OBSERVED'):acquire(b,tmp_path)

def reference():
    return {'classification':m.REFERENCE_CLASS,'identity':INTENT,'observed_at_jst':'2026-11-03T12:06:39+09:00',
        'provider_observations':[{'provider':'SPAIA_KEIBA','url':'https://spaia-keiba.com/nar/race/table?date=20261103&place=19&race_number=2'}],
        'runners':[{'number':1,'name':'SYNTHETIC_RUNNER','jockey_secondary':'SYNTHETIC_JOCKEY',
                    'weight_carried_kg_secondary':55,'trainer_secondary':'SYNTHETIC_TRAINER','sbo_external_average_reference':None}]}

def test_reference_bytes_never_become_provider_raw_or_numeric_scores():
    raw=json.dumps(reference()).encode();p=m.import_user_reference(raw,expected_sha256=hashlib.sha256(raw).hexdigest())
    assert p['actual_provider_raw_count']==0 and p['formal_source_admitted'] is False
    assert all(v['provider_original_raw_sha256'] is None for v in p['observations'])
    out=m.reconcile([p],identity=INTENT)
    assert out['runner_coverage'][1]=={'reference':4,'supplemental':0,'missing':1,'conflict':0}
    assert out['numeric_consumer_changes']==0

def test_reference_sha_and_classification_are_required():
    r=reference();raw=json.dumps(r).encode()
    with pytest.raises(m.MultisourceHold):m.import_user_reference(raw,expected_sha256='0'*64)
    r['classification']='FORMAL';raw=json.dumps(r).encode()
    with pytest.raises(m.MultisourceHold):m.import_user_reference(raw,expected_sha256=hashlib.sha256(raw).hexdigest())

def test_conflict_is_not_resolved_by_vendor_majority():
    p={'identity':INTENT,'observations':[{'runner_number':1,'field':'jockey','value':'A','tier':m.TIERS[2]},
        {'runner_number':1,'field':'jockey','value':'A','tier':m.TIERS[2]},
        {'runner_number':1,'field':'jockey','value':'B','tier':m.TIERS[2]}]}
    out=m.reconcile([p],identity=INTENT)
    assert out['fields'][0]['conflict_status']=='CONFLICT_REQUIRES_AUTHORITY'
    assert out['fields'][0]['resolved_official_value'] is None
    assert out['formal_active_universe_verified'] is False

def test_r20_frontend_cannot_start_without_admitted_official_producer(tmp_path):
    src=m.r20_source_frontend(None,official_verifier=None)
    with pytest.raises(m.MultisourceHold,match='NOT_CONNECTED'):
        src(intent=INTENT,private_root=tmp_path,now=NOW)
    assert not list(tmp_path.iterdir())

def test_r20_frontend_preserves_original_source_exactly_and_keeps_supplemental_separate(tmp_path):
    original={'request':{**INTENT,'race_id':'SYNTHETIC'},'source':{'original':'SYNTHETIC_SIGNED_SOURCE_NOT_REAL'}}
    official=Mock(return_value=original)
    verifier=Mock(return_value={'passed':True,'source_artifact_sha256':m.sha(original['source'])})
    extra=Mock(return_value={'identity':INTENT,'observations':[],'formal_source_admitted':False})
    src=m.r20_source_frontend(official,official_verifier=verifier,supplemental_producers=(extra,))
    out=src(intent=INTENT,private_root=tmp_path,now=NOW)
    assert out==original and out is original
    saved=json.loads(next(tmp_path.glob('MULTISOURCE_*.json')).read_text())
    assert saved['supplemental_numeric_consumption'] is False
    assert saved['source_bytes_rewritten'] is False
    assert len(saved['supplemental_packets'])==1

def test_r20_frontend_rejects_failed_official_signature_admission_before_supplemental(tmp_path):
    extra=Mock();src=m.r20_source_frontend(lambda **kw:{'request':INTENT,'source':{}},
        official_verifier=lambda **kw:{'passed':False},supplemental_producers=(extra,))
    with pytest.raises(m.MultisourceHold,match='ADMISSION_UNVERIFIED'):
        src(intent=INTENT,private_root=tmp_path,now=NOW)
    extra.assert_not_called()


def test_provider_licence_and_rule_name_do_not_grant_numeric_consumer(tmp_path):
    b=binding(fields=[{'runner_number':1,'field':'weight_kg','value':480,
                     'effective_at':'2026-11-03T03:28:00+00:00'}])
    b=replace(b,qualified_field_rules={'weight_kg':'SYNTHETIC_BWI_RULE'})
    out=acquire(b,tmp_path)
    assert out['observations'][0]['tier']==m.TIERS[2]
    assert out['observations'][0]['rule_id'] is None


def test_supplemental_tier_requires_separate_exact_registry_consumer_verification(tmp_path):
    b=binding(fields=[{'runner_number':1,'field':'weight_kg','value':480,
                     'effective_at':'2026-11-03T03:28:00+00:00'}])
    b=replace(b,qualified_field_rules={'weight_kg':'SYNTHETIC_BWI_RULE'})
    out=m.acquire(b,url=URL,intent=INTENT,actor_id='SYNTHETIC_ACTOR',now=NOW,private_root=tmp_path,clock=lambda:NOW,
        consumer_verifier=lambda **kw:{'passed':True,'rule_id':kw['rule_id'],'raw_sha256':kw['raw_sha256']})
    assert out['observations'][0]['tier']==m.TIERS[1]
    assert out['formal_source_admitted'] is False


def test_capture_timestamp_may_follow_request_start_after_real_transport_delay(tmp_path):
    b=binding();r=b.fetch.return_value.copy();r['captured_at']='2026-11-03T03:30:03+00:00';b.fetch.return_value=r
    out=m.acquire(b,url=URL,intent=INTENT,actor_id='SYNTHETIC_ACTOR',now=NOW,private_root=tmp_path,
                  clock=lambda:'2026-11-03T03:30:05+00:00')
    assert out['acquisition_verified_at']=='2026-11-03T03:30:05+00:00'


def test_an_unconnected_provider_does_not_block_an_independent_qualified_one_or_repeat_target(tmp_path):
    b=binding();targets=[{'provider':'NANKAN_OFFICIAL','url':'https://www.nankankeiba.com/program/20261103190802.do'},
        {'provider':'SBO_NAR','url':URL},{'provider':'SBO_NAR','url':URL}]
    out=m.acquire_available(targets,{'SBO_NAR':b},intent=INTENT,actor_id='SYNTHETIC_ACTOR',now=NOW,
                            private_root=tmp_path,clock=lambda:NOW)
    assert len(out['packets'])==1 and len(out['provider_receipts'])==2
    b.fetch.assert_called_once()
    assert out['provider_receipts'][0]['reason']=='MULTISOURCE_PROVIDER_BINDING_NOT_CONNECTED'


@pytest.mark.parametrize('key,left,right', [('distance_m',1200,1500),('surface','DIRT','TURF'),
    ('scheduled_post_at','2026-11-03T12:45:00+09:00','2026-11-03T13:20:00+09:00')])
def test_condition_conflicts_block_acquisition_and_reconciliation(tmp_path,key,left,right):
    intent={**INTENT,key:left};b=binding();b.parse.return_value['identity']={**INTENT,key:right}
    with pytest.raises(m.MultisourceHold,match='RACE_CONDITION_CONFLICT'):
        m.acquire(b,url=URL,intent=intent,actor_id='SYNTHETIC_ACTOR',now=NOW,private_root=tmp_path,clock=lambda:NOW)
    with pytest.raises(m.MultisourceHold,match='RACE_CONDITION_CONFLICT'):
        m.reconcile([{'identity':{**INTENT,key:right},'observations':[]}],identity=intent)
    with pytest.raises(m.MultisourceHold,match='RACE_CONDITION_CONFLICT'):
        m.reconcile([{'identity':intent,'observations':[]},
                     {'identity':{**INTENT,key:right},'observations':[]}],identity=INTENT)


def test_equivalent_post_timezones_and_surface_labels_are_equal():
    assert not m.race_condition_conflicts({**INTENT,'surface':'ダート',
            'scheduled_post_at':'2026-11-03T12:45:00+09:00'},
           {**INTENT,'surface':'DIRT','scheduled_post_at':'2026-11-03T03:45:00+00:00'})


def test_old_raw_capture_cannot_be_claimed_as_this_get(tmp_path):
    b=binding();b.fetch.return_value['captured_at']='2026-11-03T03:29:59+00:00'
    with pytest.raises(m.MultisourceHold,match='CAPTURE_BEFORE_ACQUISITION_START'):acquire(b,tmp_path)


def test_cutoff_is_rechecked_after_transport(tmp_path):
    b=binding();b.fetch.return_value['captured_at']='2026-11-03T03:30:03+00:00'
    with pytest.raises(m.MultisourceHold,match='CUTOFF_EXPIRED'):
        m.acquire(b,url=URL,intent={**INTENT,'prediction_cutoff':'2026-11-03T03:30:02+00:00'},
            actor_id='SYNTHETIC_ACTOR',now=NOW,private_root=tmp_path,clock=lambda:'2026-11-03T03:30:05+00:00')


def test_transport_os_failure_is_private_hold_and_does_not_skip_another_binding(tmp_path):
    from urllib.error import URLError
    a=binding();a=replace(a,provider='NANKAN_OFFICIAL',exact_urls=('https://www.nankankeiba.com/program/20261103190802.do',))
    a.fetch.side_effect=URLError('https://private-secret.invalid/key?token=secret')
    b=binding();targets=[{'provider':'NANKAN_OFFICIAL','url':a.exact_urls[0]},{'provider':'SBO_NAR','url':URL}]
    out=m.acquire_available(targets,{'NANKAN_OFFICIAL':a,'SBO_NAR':b},intent=INTENT,actor_id='SYNTHETIC_ACTOR',
            now=NOW,private_root=tmp_path,clock=lambda:NOW)
    assert len(out['packets'])==1
    assert out['provider_receipts'][0]['reason']=='MULTISOURCE_TRANSPORT_OS_ERROR'
    assert 'secret' not in json.dumps(out)


def test_supplemental_producer_cannot_rewrite_the_frozen_official_request(tmp_path):
    original={'request':{**INTENT,'scheduled_post_at':'2026-11-03T12:45:00+09:00'},'source':{'original':'SYNTHETIC'}}
    def extra(**kw):
        original['request']['scheduled_post_at']='2026-11-03T14:45:00+09:00'
        return {'identity':INTENT,'observations':[]}
    src=m.r20_source_frontend(lambda **kw:original,official_verifier=lambda **kw:{'passed':True,
        'source_artifact_sha256':m.sha(original['source'])},supplemental_producers=(extra,))
    with pytest.raises(m.MultisourceHold,match='OFFICIAL_SOURCE_MUTATED'):
        src(intent=INTENT,private_root=tmp_path,now=NOW)


def test_unchanged_provider_body_can_have_two_immutable_fresh_capture_receipts(tmp_path):
    b=binding();first=acquire(b,tmp_path)
    b.fetch.return_value['captured_at']='2026-11-03T03:31:00+00:00'
    second=m.acquire(b,url=URL,intent=INTENT,actor_id='SYNTHETIC_ACTOR',
        now='2026-11-03T03:31:00+00:00',private_root=tmp_path,clock=lambda:'2026-11-03T03:31:00+00:00')
    assert first['raw_sha256']==second['raw_sha256']
    assert first['sha256']!=second['sha256']
    assert len(list(tmp_path.glob('*.raw')))==1
    assert len(list(tmp_path.glob('*.receipt.json')))==2
