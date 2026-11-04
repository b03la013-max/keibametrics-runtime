"""Synthetic correctness only. Fixture clocks/Cutoffs grant no LIVE authority."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import pytest
from runtime import local_fnb_day_supervisor as s

NOW = datetime(2026, 11, 3, 7, 10, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def synthetic_private_actor_environment(monkeypatch):
    # Only local synthetic callbacks run in these fixtures; no Provider I/O.
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)


def plan():
    return {'profile':s.PLAN_PROFILE,'race_date':'2026-11-03','venue_id':'FNB','observed_at':'2026-11-03T07:00:00Z',
        'races':[{'race_no':n,'race_id':f'KM-LOCAL-FNB-20261103-R{n:02d}',
                  'scheduled_post_at':post,'prediction_cutoff':cut,'start_at':'2026-11-03T07:00:00Z'}
                 for n,post,cut in [(5,'2026-11-03T07:50:00Z','2026-11-03T07:40:00Z'),
                                   (6,'2026-11-03T08:25:00Z','2026-11-03T08:15:00Z')]]}


def activation():
    return {'enabled':True,'race_date':'2026-11-03','venue_id':'FNB','race_numbers':[5,6],
            'actor_id':'SYNTHETIC_FIXTURE_ONLY','approval_ref':'SYNTHETIC_NOT_OWNER_APPROVAL',
            'classification':s.CLASSIFICATION,'binding_sha256':'b'*64,'max_dispatches':2,
            'delivery_enabled':True,'delivery_approval_ref':'SYNTHETIC_SELF_ONLY',
            'delivery_recipient_id':'SYNTHETIC_OWNER_SELF','delivery_route_id':'SYNTHETIC_PRIVATE_ROUTE',
            'supervisor_code_sha256':hashlib.sha256(Path(s.__file__).read_bytes()).hexdigest()}


def binding(root, *, complete=False, hold_first=False):
    sent=[]; delivered=[]; available={}
    def execute_race(*,race,private_root,now):
        saved=json.loads((root/'FNB_2026-11-03_DAY_CHECKPOINT.json').read_bytes())
        assert saved['races'][str(race['race_no'])]['claim']
        sent.append(race['race_no'])
        if hold_first and race['race_no']==5:
            return {'status':'EXECUTION_HOLD_NOT_NO_BET','first_failed_stage':'SOURCE_PRODUCER','reason':'SOURCE_PRODUCER_NOT_CONNECTED'}
        if complete:available[race['race_no']]=completion(root,race)
        return {'status':'ACK','run_id':'SYNTHETIC_CORRECTNESS_ONLY'}
    return {'_binding_sha256':'b'*64,'discover_day':lambda **k:plan(),'verify_discovery':lambda **k:True,
            'authorize_race':lambda **k:True,'execute_race':execute_race,
            'inspect_race':lambda **k:available.get(k['race']['race_no'],{}),
            'inspect_delivery':lambda **k:{'recipient_ack_verified':False},
            'authorize_delivery':lambda **k:True,
            'deliver':lambda **k:delivered.append(k['race']['race_no']),
            'sent':sent,'delivered':delivered,'available':available}


def completion(root,race):
    def write(name,data):
        p=root/name;p.write_bytes(data)
        return {'path':name,'sha256':hashlib.sha256(data).hexdigest()}
    prefix=str(race['race_no'])
    stages={k:{'status':'VERIFIED'} for k in s.STAGES[:8]}
    stages['SOURCE']['source_snapshot_sha256']='a'*64
    stages['KRS'].update(engine_sha256=s.ENGINE_SHA,map_sha256=s.MAP_SHA,run_count=5000,seed=1)
    return {'status':'VERIFIED_COMPLETE_ORIGINAL','classification':s.CLASSIFICATION,
            'race_id':race['race_id'],'prediction_cutoff':race['prediction_cutoff'],
            'verifier_readback_pass':True,'verifier_code_sha256':'c'*64,
            'source_snapshot_sha256':'a'*64,'model_code_sha256':'d'*64,
            'source_freeze_at':'2026-11-03T07:01:00Z','prediction_freeze_at':'2026-11-03T07:02:00Z',
            'horse_count':2,'index_cells':58,'stages':stages,'computed_no_bet':False,
            'body_original':write(prefix+'_body.md',b'SYNTHETIC CORRECTNESS NOT LIVE\n'),
            'checkpoint_original':write(prefix+'_checkpoint.json',b'{}\n'),
            'request_original':write(prefix+'_request.json',b'{}\n'),
            'source_original':write(prefix+'_source.json',b'{}\n')}


def tick(root,p=None,b=None,a=None,execute=True):
    return s.tick(p or plan(),root,binding=b,activation=a or activation(),execute=execute,clock=lambda:NOW)


def test_ack_is_not_completion_and_no_restart_redispatch(tmp_path):
    b=binding(tmp_path)
    first=tick(tmp_path,b=b)
    assert first['counts']['dispatched']==2 and first['counts']['verified_prestart_originals']==0
    second=tick(tmp_path,b=b)
    assert second['counts']['dispatched']==2 and b['sent']==[5,6]


def test_source_hold_does_not_stop_next_race(tmp_path):
    b=binding(tmp_path,hold_first=True)
    state=tick(tmp_path,b=b)
    assert b['sent']==[5,6]
    assert state['races']['5']['status']=='HOLD'
    assert state['races']['5']['code']=='SOURCE_PRODUCER_NOT_CONNECTED'
    assert state['counts']['no_bet_races']==0


def test_complete_original_is_independently_read_and_tamper_revokes_count(tmp_path):
    b=binding(tmp_path,complete=True)
    state=tick(tmp_path,b=b)
    assert state['counts']['verified_prestart_originals']==2
    (tmp_path/'5_body.md').write_text('changed')
    state=tick(tmp_path,b=b)
    assert state['counts']['verified_prestart_originals']==1
    assert state['races']['5']['status']=='HOLD'
    assert state['races']['5']['code']=='PRIVATE_ORIGINAL_BYTES_CHANGED'
    assert b['sent']==[5,6]


def test_missing_old_original_cannot_stay_successful(tmp_path):
    b=binding(tmp_path,complete=True);tick(tmp_path,b=b)
    b['available'].clear()
    state=tick(tmp_path,b=b)
    assert state['counts']['verified_prestart_originals']==0


def test_wrong_race_original_rejected(tmp_path):
    b=binding(tmp_path);tick(tmp_path,b=b)
    b['available'][5]=completion(tmp_path,plan()['races'][1])
    state=tick(tmp_path,b=b)
    assert state['races']['5']['status']=='HOLD'
    assert state['counts']['verified_prestart_originals']==0


def test_changed_claimed_cutoff_never_redispatches(tmp_path):
    b=binding(tmp_path);tick(tmp_path,b=b)
    p=plan();p['races'][0]['prediction_cutoff']='2026-11-03T07:39:00Z'
    state=tick(tmp_path,p,b)
    assert state['races']['5']['code']=='CLAIMED_DISCOVERY_CHANGED_NO_AUTOMATIC_REDISPATCH'
    assert b['sent']==[5,6]


def test_no_default_cutoff_is_invented(tmp_path):
    p=plan()
    for r in p['races']:r['prediction_cutoff']=None
    b=binding(tmp_path);state=tick(tmp_path,p,b)
    assert not b['sent']
    assert all(c['prediction_cutoff'] is None and c['code']=='PREDICTION_CUTOFF_NOT_RESOLVED' for c in state['races'].values())


def test_observe_mode_does_not_send_delivery_from_old_complete_claim(tmp_path):
    b=binding(tmp_path,complete=True);tick(tmp_path,b=b)
    b['delivered'].clear()
    state=tick(tmp_path,b=b,execute=False)
    assert b['delivered']==[]
    assert state['counts']['verified_prestart_recipient_deliveries']==0


def test_approved_max_dispatches_is_enforced(tmp_path):
    b=binding(tmp_path);a=activation();a['max_dispatches']=1
    state=tick(tmp_path,b=b,a=a)
    assert b['sent']==[5]
    assert state['races']['6']['code']=='APPROVED_DISPATCH_BUDGET_EXHAUSTED'


def test_changed_supervisor_code_pin_stops_mutation(tmp_path):
    b=binding(tmp_path);a=activation();a['supervisor_code_sha256']='0'*64
    state=tick(tmp_path,b=b,a=a)
    assert b['sent']==[]
    assert state['counts']['dispatched']==0


def test_disabled_activation_stays_disabled(tmp_path):
    b=binding(tmp_path);a=activation();a['enabled']=False
    state=tick(tmp_path,b=b,a=a)
    assert b['sent']==[] and all(c['status']=='HOLD' for c in state['races'].values())


def test_postcutoff_new_start_never_happens(tmp_path):
    b=binding(tmp_path)
    later=datetime(2026,11,3,9,tzinfo=timezone.utc)
    state=s.tick(plan(),tmp_path,binding=b,activation=activation(),execute=True,clock=lambda:later)
    assert not b['sent'] and all(c['status']=='MISSED_WINDOW' for c in state['races'].values())


def test_duplicate_discovery_is_not_accepted(tmp_path):
    p=plan();p['races'].append(deepcopy(p['races'][0]))
    with pytest.raises(ValueError,match='DUPLICATE'):
        tick(tmp_path,p,binding(tmp_path))


def test_future_day_observation_allowed_but_not_execution(tmp_path):
    p=plan();p['race_date']='2026-11-04'
    for r in p['races']:
        r['race_id']=r['race_id'].replace('20261103','20261104')
        for k in ['scheduled_post_at','prediction_cutoff','start_at']:r[k]=r[k].replace('2026-11-03','2026-11-04')
    state=tick(tmp_path,p,binding(tmp_path),execute=False)
    assert state['counts']['dispatched']==0


def test_private_store_in_git_checkout_is_forbidden():
    with pytest.raises(ValueError,match='PRIVATE_SOURCE_IN_GIT_WORKTREE_FORBIDDEN'):
        s.tick(plan(),Path(s.__file__).parents[1]/'unsafe_private_store',execute=False,clock=lambda:NOW)


def saved_reference_binding(root, monkeypatch):
    """Adapter-only fixtures; existing reader owns frozen-body qualification."""
    from runtime import local_fnb_rakuten_reference as reference
    b = binding(root)
    reads = []
    def read(folder, intent, *, now):
        reads.append((str(folder), intent, now))
        race = next(r for r in plan()['races'] if r['race_no'] == intent['race_no'])
        body = 'SYNTHETIC INDEPENDENT REFERENCE FULL BODY\n'
        return {'status':'VERIFIED_REFERENCE_BODY_READY_TO_RENDER', 'classification':'REFERENCE',
            'body':body, 'body_sha256':hashlib.sha256(body.encode()).hexdigest(),
            'publication_folder':str(folder), 'private_readback_verified':True,
            'prestart_at_readback':True, 'source_age_seconds_at_readback':900,
            'observation_age_seconds_at_readback':900, 'source_within_existing_600s':False,
            'observation_within_existing_600s':False,
            'manifest':{'scheduled_post_at':race['scheduled_post_at'],
                'prediction_cutoff':race['prediction_cutoff'], 'revision':'REFERENCE-SYNTHETIC',
                'sha256':'a'*64, 'source_sha256':'b'*64,
                'source_fetched_at':'2026-11-03T06:55:00Z',
                'forecast_frozen_at':'2026-11-03T06:56:00Z',
                'prepared_at':'2026-11-03T06:57:00Z', 'observation_raw_sha256':'c'*64}}
    monkeypatch.setattr(reference, 'read_saved_reference', read)
    b['inspect_reference'] = lambda **kw: {'status':'VERIFIED_REFERENCE_BODY_READY_TO_RENDER',
        'publication_folder':str(root / ('reference_'+str(kw['race']['race_no']))),
        'body':'CALLBACK BODY IS NOT THE INDEPENDENTLY READ ORIGINAL'}
    b['verify_saved_discovery'] = lambda **kw: True
    b['verify_discovery'] = lambda **kw: False
    b['inspect_race'] = lambda **kw: {'status':'NO_FORMAL_ORIGINAL'}
    return b, reads


def test_independent_reference_readback_survives_formal_authority_hold(tmp_path, monkeypatch):
    b, reads = saved_reference_binding(tmp_path, monkeypatch)
    state = s.tick(plan(),tmp_path,binding=b,activation=None,execute=True,clock=lambda:NOW)
    assert len(reads) == 2 and b['sent'] == []
    assert state['counts']['reference_saved_readbacks'] == 2
    assert state['counts']['reference_ready_to_render'] == 2
    assert state['counts']['verified_prestart_originals'] == state['counts']['dispatched'] == 0
    assert state['counts']['reference_ack_verified'] == state['counts']['reference_autonomous_completed'] == 0
    assert state['reference_discovery']['formal_qualification_granted'] is False
    for cell in state['races'].values():
        ref = cell['reference']
        assert ref['body'] == 'SYNTHETIC INDEPENDENT REFERENCE FULL BODY\n'
        assert ref['body_original']['sha256'] == ref['body_sha256']
        assert ref['recipient_ack'] == 'UNKNOWN' and ref['displayed'] is False
        assert ref['formal_final_proven'] is False and ref['natural_delivery_verified'] is False
        assert ref['source_within_existing_600s'] is False
        assert 'completion' not in cell and 'claim' not in cell


def test_saved_discovery_check_never_becomes_formal_qualification(tmp_path, monkeypatch):
    b, reads = saved_reference_binding(tmp_path, monkeypatch)
    state = tick(tmp_path,b=b)
    assert len(reads) == 2 and b['sent'] == []
    assert all(c['code']=='QUALIFIED_OFFICIAL_DISCOVERY_NOT_VERIFIED' for c in state['races'].values())
    assert all('claim' not in c for c in state['races'].values())


def test_reference_day_raw_failure_stops_only_reference_readback(tmp_path, monkeypatch):
    b, reads = saved_reference_binding(tmp_path, monkeypatch)
    b['verify_saved_discovery'] = lambda **kw: False
    state = tick(tmp_path,b=b,execute=False)
    assert reads == [] and state['counts']['reference_saved_readbacks'] == 0
    assert all(c['reference']['code']=='REFERENCE_SAVED_DISCOVERY_READBACK_NOT_VERIFIED'
               for c in state['races'].values())


def test_current_reference_byte_loss_revokes_reference_count(tmp_path, monkeypatch):
    from runtime import local_fnb_rakuten_reference as reference
    b, _ = saved_reference_binding(tmp_path, monkeypatch)
    assert tick(tmp_path,b=b,execute=False)['counts']['reference_saved_readbacks'] == 2
    def corrupt(*args, **kwargs):
        raise ValueError('REFERENCE_FROZEN_PUBLICATION_INTEGRITY_HOLD')
    monkeypatch.setattr(reference, 'read_saved_reference', corrupt)
    state = tick(tmp_path,b=b,execute=False)
    assert state['counts']['reference_saved_readbacks'] == 0
    assert all(c['reference']['code']=='REFERENCE_FROZEN_PUBLICATION_INTEGRITY_HOLD'
               and 'body' not in c['reference'] for c in state['races'].values())


def test_reference_cutoff_must_match_saved_day_identity(tmp_path, monkeypatch):
    from runtime import local_fnb_rakuten_reference as reference
    b, _ = saved_reference_binding(tmp_path, monkeypatch)
    read = reference.read_saved_reference
    def wrong(*args, **kwargs):
        result = read(*args, **kwargs)
        result['manifest']['prediction_cutoff'] = '2026-11-03T07:39:00Z'
        return result
    monkeypatch.setattr(reference, 'read_saved_reference', wrong)
    state = tick(tmp_path,b=b,execute=False)
    assert state['counts']['reference_saved_readbacks'] == 0
    assert all(c['reference']['code']=='REFERENCE_SAVED_DISCOVERY_POST_OR_CUTOFF_MISMATCH'
               for c in state['races'].values())


@pytest.mark.parametrize('suffix',['','-OLDER_SOURCE_REVISION'])
def test_no_formal_original_does_not_hide_an_ambiguous_single_race_claim(tmp_path, suffix):
    b = binding(tmp_path)
    b['inspect_race'] = lambda **kw: {'status':'NO_FORMAL_ORIGINAL'}
    claim = tmp_path/'single_owner_claims'/(plan()['races'][0]['race_id']+suffix)/'claim.json'
    claim.parent.mkdir(parents=True)
    claim.write_bytes(b'{"status":"SYNTHETIC_PARTIAL_EXECUTION"}\n')
    state = tick(tmp_path,b=b)
    assert b['sent'] == [6]
    assert state['races']['5']['code'] == 'EXISTING_EXECUTION_OR_PARTIAL_ORIGINAL_REQUIRES_READBACK'
    assert state['races']['5']['dispatch_count'] == 0
    assert state['counts']['dispatched'] == 1


def test_changed_race_identity_cannot_retain_prior_reference_readback(tmp_path, monkeypatch):
    b, _ = saved_reference_binding(tmp_path, monkeypatch)
    assert tick(tmp_path,b=b,execute=False)['counts']['reference_saved_readbacks'] == 2
    p = plan()
    p['races'][0]['race_id'] += '-NEW_REVISION'
    b['verify_saved_discovery'] = lambda **kw: False
    state = tick(tmp_path,p,b,execute=False)
    assert state['counts']['reference_saved_readbacks'] == 0
    assert 'reference' not in state['races']['5']


def test_saved_discovery_reader_cannot_mutate_formal_plan(tmp_path, monkeypatch):
    b, reads = saved_reference_binding(tmp_path, monkeypatch)
    p = plan(); original = deepcopy(p)
    def mutate(**kw):
        kw['plan']['races'][0]['prediction_cutoff'] = '2026-11-03T07:39:00Z'
        return True
    b['verify_saved_discovery'] = mutate
    state = tick(tmp_path,p,b,execute=False)
    assert p == original and reads == []
    assert state['reference_discovery']['code'] == 'REFERENCE_SAVED_DISCOVERY_MUTATED_BY_READER'
    assert state['counts']['reference_saved_readbacks'] == 0
