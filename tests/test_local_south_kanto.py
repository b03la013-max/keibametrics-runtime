"""Read-only official discovery and LOCAL evidence boundaries; no Runtime POST."""
import base64
from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

from runtime import local_race_day_dispatcher as d
from runtime.jra_next_race_learning_binding_audit import audit_learning_consumption
from tests.test_local_race_day_dispatcher import plan, snapshot, NOW


def menu_fetch(venue='URW', siblings=('10','22','24'), day='2026/10/15'):
    def fetch(spec, cutoff):
        code = d.LOCAL_BABA_CODES[venue]
        html = f'2026年10月15日（木）{d.VENUE_NAMES[venue]}競馬当日メニュー'
        html += ''.join(f'<a href="RaceList?k_babaCode={c}&amp;k_raceDate={day}">場</a>' for c in (*siblings,code))
        html += f'<a href="DebaTable?k_babaCode={code}&amp;k_raceDate={day}&amp;k_raceNo=1">1R</a>'
        return snapshot(spec, html)
    return fetch


def test_four_only_official_resolver_current_registry():
    r=d.discover_meetings('2026-10-15', now=NOW, fetch=menu_fetch(siblings=('19','20','21','03','10')))
    assert r['venues']==['FNB','OHI','URW','KAW']
    assert not r['new_live_send'] and not r['formal_registration_proven']


def test_original_official_index_bytes_urw12_next_day_not_a_prediction():
    # Original GET snapshot from CI39120192594, not reconstructed web text.
    original=json.loads((Path(__file__).parent/'fixtures/local_official_south_kanto_top_20261018.json').read_text())
    fetch=lambda spec,cutoff:(original,[])
    r=d.discover_meetings('2026-10-19',now=NOW,fetch=fetch)
    assert r['venues']==['URW'] and not r['formal_registration_proven']
    today=d.discover_meetings('2026-10-18',now=NOW,fetch=fetch)
    assert today['status']=='NO_SOUTH_KANTO_MEETING'


def test_official_other_venue_is_positive_nonholding_evidence():
    r=d.discover_meetings('2026-10-15',now=NOW,fetch=menu_fetch('KCH',siblings=('10','22')))
    assert r['status']=='NO_SOUTH_KANTO_MEETING' and r['venues']==[]


@pytest.mark.parametrize('kind',['empty','wrong_date','foreign','broken_sha','network'])
def test_failure_is_never_no_meeting(kind,tmp_path):
    def fetch(spec,cutoff):
        if kind=='network': raise TimeoutError('original timeout')
        s,e=menu_fetch()(spec,cutoff)
        html=d.raw_html(s)
        if kind=='empty': html='取得できません'
        if kind=='wrong_date': html=html.replace('2026/10/15','2026/10/16')
        if kind=='foreign': html=html.replace('RaceList?','https://example.org/KeibaWeb/TodayRaceInfo/RaceList?')
        s,e=snapshot(spec,html)
        if kind=='broken_sha': s['raw_sha256']='0'*64
        return s,e
    r=d.south_kanto_day(tmp_path,'2026-10-15',120,now=NOW,fetch=fetch)
    assert r['status']=='HOLD_OFFICIAL_DISCOVERY' and not r['target_races_complete']
    assert not list((tmp_path/'runtime/race_key_requests').glob('*'))


def test_corrupt_identifiable_sibling_isolated_unknown_alias_holds(tmp_path):
    p=plan(); folder=tmp_path/'runtime/race_key_requests';folder.mkdir(parents=True)
    (folder/(p['races'][0]['race_key']+'.json')).write_text('{broken')
    assert d.existing_race_refs(tmp_path,p['races'][1])==[]
    with pytest.raises(ValueError): d.existing_race_refs(tmp_path,p['races'][0])
    (folder/'unknown-alias.json').write_text('null')
    with pytest.raises(ValueError): d.existing_race_refs(tmp_path,p['races'][1])


def setup_day(monkeypatch):
    base=plan()
    def discover(venue,day,*args,**kwargs):
        p=deepcopy(base);p['venue_id']=venue
        for r in p['races']:
            r['fields']['venue_id']=venue
            r['execution_id']=r['execution_id'].replace('-KAW-',f'-{venue}-')
        p['plan_sha256']=d.sha({k:v for k,v in p.items() if k!='plan_sha256'})
        return p
    monkeypatch.setattr(d,'discover_meetings',lambda *a,**k:{'venues':['OHI','KAW']})
    monkeypatch.setattr(d,'discover',discover)
    return discover


def test_all_discovered_targets_retained_without_approval_or_execution(tmp_path,monkeypatch):
    setup_day(monkeypatch)
    monkeypatch.setattr(d,'prepare_worker',lambda *a:pytest.fail('NO EXECUTION FROM DISCOVERY'))
    r=d.south_kanto_day(tmp_path,'2026-10-15',120,now=NOW)
    assert r['target_races']==4 and r['target_races_complete']
    assert len(r['venues']['KAW']['races'])==2
    saved=json.loads((tmp_path/'runtime/local_race_day_plan/2026-10-15-KAW.json').read_text())
    assert saved['races'][0]['required_numerical_manifest']=='LOCAL-FULL-NUMERICAL-MAPPING-v1.0-PRODUCTION-20261008'
    monkeypatch.setenv('KM_LOCAL_AUTONOMOUS_ENABLED','true')
    r=d.south_kanto_day(tmp_path,'2026-10-15',120,now=NOW,execute=True)
    assert r['target_races']==4 and all(v['status']=='HOLD' for v in r['venues'].values())
    assert r['live_execution_requested'] and r['new_live_send'] is None
    assert all(v['first_stop_stage']=='DATED_OWNER_AUTHORIZATION' for v in r['venues'].values())


@pytest.mark.parametrize('failure',['scope','worker','drift'])
def test_sibling_scope_worker_and_plan_failures_never_stop_other_venue(tmp_path,monkeypatch,failure):
    discover=setup_day(monkeypatch);monkeypatch.setenv('KM_LOCAL_AUTONOMOUS_ENABLED','true')
    for v in ['OHI','KAW']:
        d.write(tmp_path/'profiles/local_autonomous_approvals'/f'2026-10-15-{v}.json',{'worker_seconds':0})
    if failure=='drift':
        old=discover('OHI','2026-10-15');old['races'][0]['fields']['scheduled_post_at']='2026-10-15T19:00:00+09:00'
        old['plan_sha256']=d.sha({k:v for k,v in old.items() if k!='plan_sha256'})
        d.write(tmp_path/'runtime/local_race_day_plan/2026-10-15-OHI.json',old)
    def authorize(a,p,*args):
        if failure=='scope' and p['venue_id']=='OHI':raise ValueError('OWNER_SCOPE_HOLD')
    monkeypatch.setattr(d,'authorization',authorize)
    executed=[]
    def prepare(root,p,*args):
        def step():
            if failure=='worker' and p['venue_id']=='OHI':raise ValueError('ORIGINAL_WORKER_ERROR')
            executed.append(p['venue_id'])
            d.write(root/'runtime/execution_reports/LOCAL-2026-10-15'/(p['venue_id']+'.json'),
                    d.canonical_day_index(root,p,now=NOW))
            return {'races':{}}
        return {'worker_seconds':0},step
    monkeypatch.setattr(d,'prepare_worker',prepare)
    r=d.south_kanto_day(tmp_path,'2026-10-15',120,now=NOW,execute=True)
    assert executed==['KAW'] and r['venues']['OHI']['status'].startswith('HOLD')
    assert len(r['venues']['KAW']['races'])==2


def test_cli_reports_hold_as_nonzero_after_evidence_write(monkeypatch,tmp_path):
    import sys
    monkeypatch.setattr(sys,'argv',['dispatcher','--south-kanto','--date','2026-10-19',
                                  '--cutoff-seconds','120','--repo-root',str(tmp_path)])
    monkeypatch.setattr(d,'south_kanto_day',lambda *a,**k:{
        'target_races_complete':True,'venues':{'URW':{'status':'HOLD','first_stop_stage':'DATED_OWNER_AUTHORIZATION'}}})
    assert d.main()==1


def signed_envelope(artifact,eid,key,health):
    receipt={'family':'LOCAL','phase':'FINAL','status':'PASS','errors':[], 'race_id':eid,
             'engine_sha256':health['engine_sha256'],'parameter_map_sha256':health['parameter_map_sha256'],
             'timestamp':'2026-10-15T17:44:00+09:00','artifact_sha256':d.sha(artifact)}
    rb=json.dumps(receipt,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    return dict(receipt=receipt,artifact=artifact,receipt_sha256=d.sha(receipt),signature_alg='Ed25519',
                signer_key_id=health['receipt_signer_key_id'],signature=base64.b64encode(key.sign(rb)).decode())


@pytest.mark.parametrize('bad',['none','signature','identity','after_cutoff','no_health','tree'])
def test_index_trust_deadline_full_denominator_no_delivery_claim(tmp_path,monkeypatch,bad):
    p=plan(); key=Ed25519PrivateKey.generate()
    health=dict(receipt_signer_key_id='TEST_ONLY',engine_sha256='engine',parameter_map_sha256='parameter',
        receipt_public_key_b64=base64.b64encode(key.public_key().public_bytes(
            serialization.Encoding.Raw,serialization.PublicFormat.Raw)).decode())
    # Fingerprint assessor is separately covered by Gateway regression; no network.
    monkeypatch.setattr('runtime.execution_gateway.assess_runtime_health',lambda h,f:{'status':'PASS'})
    artifact={'final_freeze_timestamp':'2026-10-15T17:43:00+09:00'}
    eid=p['races'][0]['execution_id']; env=signed_envelope(artifact,eid,key,health)
    if bad=='signature': env['signature']=base64.b64encode(b'X'*64).decode()
    if bad=='identity': env=signed_envelope(artifact,p['races'][1]['execution_id'],key,health)
    if bad=='after_cutoff':
        p['races'][0]['fields']['prediction_cutoff']='2026-10-15T17:43:30+09:00'
        p['plan_sha256']=d.sha({k:v for k,v in p.items() if k!='plan_sha256'})
    path=tmp_path/'final.json';path.write_text(json.dumps(env))
    monkeypatch.setattr(d,'checkpoint_status',lambda root,e:{'stages':{'FINAL':{'artifact_ref':'final.json'}}} if e==eid else {'stages':{'FINAL':{}}})
    def render(a):
        if bad=='tree':raise ValueError('CANONICAL_TICKET_MISMATCH')
        return {'text':'full vertical tree','ticket_count':2,'total_investment':200}
    monkeypatch.setattr('runtime.jra_ticket_tree_renderer.render_ticket_tree',render)
    report=d.canonical_day_index(tmp_path,p,now=NOW,health=None if bad=='no_health' else health)
    assert report['target_races']==2 and len(report['races'])==2
    assert report['signed_final_before_cutoff_count']==(1 if bad=='none' else 0)
    assert report['delivery_verified_count']==0 and not report['new_live_send']
    assert all(r['delivery_sent_at'] is None and r['actual_purchase_pfs']=='UNKNOWN' for r in report['races'])
    if bad=='none': assert report['races'][0]['canonical_tree']=='full vertical tree'
    else: assert 'canonical_tree' not in report['races'][0]


def test_local_learning_reuses_readonly_common_audit_without_injection():
    states=[{'state_id':'old','race_id':'KM-LOCAL-KAW-20261015-R01','sha256':'a'*64,
             'effective_time':'2026-10-15T17:00:00+09:00'},
            {'state_id':'future','race_id':'KM-LOCAL-KAW-20261015-R02','sha256':'b'*64,
             'effective_time':'2026-10-15T18:00:00+09:00'},
            {'state_id':'foreign','race_id':'KM-JRA-TKY-20261015-R01','sha256':'c'*64,
             'effective_time':'2026-10-15T17:00:00+09:00'}]
    original=deepcopy(states)
    r=audit_learning_consumption(race_id='KM-LOCAL-KAW-20261015-R03',family_id='LOCAL',
       source_freeze=NOW.isoformat(),prediction_cutoff='2026-10-15T18:00:00+09:00',learning_states=states)
    assert r['eligible_state_ids']==['old'] and not r['input_bound_state_ids']
    assert r['status']=='NEXT_RACE_CONSUMPTION_UNVERIFIED' and not r['production_policy_changed']
    assert states==original
