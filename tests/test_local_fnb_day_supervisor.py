"""Synthetic correctness only. Fixture clocks/Cutoffs grant no LIVE authority."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import pytest
from runtime import local_fnb_day_supervisor as s

NOW = datetime(2026, 11, 3, 7, 10, tzinfo=timezone.utc)


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
