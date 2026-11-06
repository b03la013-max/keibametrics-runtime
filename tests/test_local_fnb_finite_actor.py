"""Synthetic scheduling/lifecycle tests only; no SOURCE or Delivery is granted."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path

import pytest
from runtime import local_fnb_finite_actor as actor
from runtime import local_fnb_day_supervisor as day


def fixture():
    binding = {'_binding_sha256':'b'*64}
    leases = []
    activations = {}
    for value in actor.DATES:
        leases.append({'race_date':value,'start_at':value+'T14:00:00+09:00',
                       'stop_at':value+'T14:00:02+09:00'})
        activations[value] = {'enabled':True,'race_date':value,'venue_id':'FNB',
            'classification':day.CLASSIFICATION,'race_numbers':list(range(1,13)),
            'max_dispatches':12,'binding_sha256':'b'*64,'approval_ref':'SYNTHETIC_ONLY',
            'actor_id':'SYNTHETIC_NOT_LIVE','worker_duration_approval_ref':'SYNTHETIC_ONLY',
            'approved_worker_seconds':2,
            'supervisor_code_sha256':hashlib.sha256(Path(day.__file__).read_bytes()).hexdigest()}
    manifest = {'profile':actor.PROFILE,'venue_id':'FNB','classification':day.CLASSIFICATION,
        'race_dates':list(actor.DATES),'approval_ref':'SYNTHETIC_NOT_OWNER_APPROVAL',
        'actor_code_sha256':hashlib.sha256(Path(actor.__file__).read_bytes()).hexdigest(),
        'leases':leases,'approved_day_worker_seconds':dict.fromkeys(actor.DATES,2)}
    return manifest,binding,activations


class Clock:
    def __init__(self, manifest):
        self.manifest = manifest
        self.current = day.stamp(manifest['leases'][0]['start_at'])
    def __call__(self):
        return self.current
    def sleep(self, seconds):
        # Simulate container suspension/resumption at the next scheduled lease.
        future = [day.stamp(row['start_at']) for row in self.manifest['leases']
                  if day.stamp(row['start_at']) > self.current]
        self.current = min(future) if future else self.current + timedelta(seconds=seconds)


@pytest.fixture(autouse=True)
def private_actor_environment(monkeypatch):
    monkeypatch.delenv('GITHUB_ACTIONS',raising=False)


def test_real_wrapper_invokes_each_dated_existing_supervisor_and_stops(tmp_path):
    manifest,binding,activations = fixture(); clock = Clock(manifest); calls = []
    def supervise(**kwargs):
        calls.append((kwargs['day'],kwargs['worker_seconds']))
        clock.current += timedelta(seconds=kwargs['worker_seconds'])
        return {'counts':{'verified_prestart_originals':0}}
    result = actor.run(manifest,tmp_path,binding=binding,activations=activations,
                       clock=clock,sleep=clock.sleep,supervise=supervise)
    assert calls == [(value,2) for value in actor.DATES]
    assert result['status'] == 'FINITE_RUN_ENDED'
    assert result['counts_are_live_acceptance'] is False
    assert all(cell['last_observed_counts']['verified_prestart_originals'] == 0
               for cell in result['leases'].values())


def test_restart_preserves_completed_leases_and_does_not_redispatch(tmp_path):
    manifest,binding,activations = fixture(); clock = Clock(manifest); calls = []
    def supervise(**kwargs):
        calls.append(kwargs['day']);clock.current += timedelta(seconds=2)
        return {'counts':{}}
    for _ in range(2):
        actor.run(manifest,tmp_path,binding=binding,activations=activations,
                  clock=clock,sleep=clock.sleep,supervise=supervise)
    assert calls == list(actor.DATES)


def test_sigterm_style_stop_is_resumable_only_for_remaining_lease(tmp_path):
    manifest,binding,activations = fixture(); clock = Clock(manifest)
    def interrupted(**kwargs):
        clock.current += timedelta(seconds=1)
        raise actor.StopActor()
    result = actor.run(manifest,tmp_path,binding=binding,activations=activations,
                       clock=clock,sleep=clock.sleep,supervise=interrupted)
    assert result['status'] == 'STOPPED_RESUMABLE_WITH_EXISTING_RACE_CLAIMS'
    assert result['leases']['0']['status'] == 'RUNNING'
    seconds = []
    def resume(**kwargs):
        seconds.append(kwargs['worker_seconds']);clock.current += timedelta(seconds=kwargs['worker_seconds'])
        return {'counts':{}}
    result = actor.run(manifest,tmp_path,binding=binding,activations=activations,
                       clock=clock,sleep=clock.sleep,supervise=resume)
    assert seconds == [1,2,2]
    assert result['leases']['0']['resumed'] is True


def test_failed_lease_does_not_prevent_independent_later_days(tmp_path):
    manifest,binding,activations = fixture();clock = Clock(manifest);calls=[]
    def supervise(**kwargs):
        calls.append(kwargs['day']);clock.current += timedelta(seconds=2)
        if len(calls) == 1: raise ValueError('SOURCE_UNAVAILABLE')
        return {'counts':{}}
    result=actor.run(manifest,tmp_path,binding=binding,activations=activations,
                     clock=clock,sleep=clock.sleep,supervise=supervise)
    assert calls == list(actor.DATES)
    assert result['leases']['0']['code'] == 'SOURCE_UNAVAILABLE'
    assert result['leases']['1']['status'] == 'COMPLETED'


def test_no_execution_after_finite_end(tmp_path):
    manifest,binding,activations = fixture();clock=Clock(manifest)
    clock.current=day.stamp(manifest['leases'][-1]['stop_at'])+timedelta(days=1)
    def forbidden(**kwargs): raise AssertionError('late supervisor call')
    result=actor.run(manifest,tmp_path,binding=binding,activations=activations,
                     clock=clock,sleep=clock.sleep,supervise=forbidden)
    assert all(cell['status']=='ELAPSED' for cell in result['leases'].values())


def test_existing_lease_duration_limit_and_aggregate_budget_stay_enforced():
    manifest,binding,activations=fixture()
    manifest['leases'][0]['stop_at']='2026-11-04T20:00:01+09:00'
    with pytest.raises(ValueError,match='DURATION'):
        actor.validate(manifest,binding=binding,activations=activations)
    manifest,binding,activations=fixture()
    manifest['approved_day_worker_seconds']['2026-11-04']=3
    with pytest.raises(ValueError,match='AGGREGATE'):
        actor.validate(manifest,binding=binding,activations=activations)


def test_changed_scope_code_or_activation_rejected():
    for change in ('scope','code','activation'):
        manifest,binding,activations=fixture()
        if change=='scope':manifest['race_dates'].append('2026-11-07')
        elif change=='code':manifest['actor_code_sha256']='a'*64
        else:activations[actor.DATES[0]]['race_numbers']=[1]
        with pytest.raises(ValueError):actor.validate(manifest,binding=binding,activations=activations)


def test_only_remaining_approved_days_run_without_a_backdated_lease(tmp_path):
    manifest,binding,activations=fixture()
    remaining=list(actor.DATES[1:])
    manifest['race_dates']=remaining
    manifest['leases']=[r for r in manifest['leases'] if r['race_date'] in remaining]
    manifest['approved_day_worker_seconds']={value:2 for value in remaining}
    activations={value:activations[value] for value in remaining}
    clock=Clock(manifest);calls=[]
    def supervise(**kwargs):
        calls.append(kwargs['day']);clock.current+=timedelta(seconds=kwargs['worker_seconds'])
        return {'counts':{}}
    result=actor.run(manifest,tmp_path,binding=binding,activations=activations,
                     clock=clock,sleep=clock.sleep,supervise=supervise)
    assert calls==remaining and result['status']=='FINITE_RUN_ENDED'


@pytest.mark.parametrize('dates',[[],['2026-11-05','2026-11-05'],
    ['2026-11-06','2026-11-05'],['2026-11-07']])
def test_remaining_day_scope_cannot_duplicate_reorder_or_extend_dates(dates):
    manifest,binding,activations=fixture();manifest['race_dates']=dates
    with pytest.raises(ValueError,match='EXACT_DATED_SCOPE'):
        actor.validate(manifest,binding=binding,activations=activations)


def test_known_failed_provider_not_retried_on_next_lease(tmp_path):
    manifest,binding,activations=fixture();clock=Clock(manifest);calls=[]
    binding['discovery_routes']=[{'provider':'NANKAN_OFFICIAL'},{'provider':'FKEIBA_OFFICIAL'}]
    (tmp_path/'FNB_2026-11-04_DISCOVERY_ROUTE_prior.json').write_text(json.dumps({
        'race_date':'2026-11-04','attempts':[{'provider':'NANKAN_OFFICIAL','status':'HOLD',
                                           'code':'SOURCE_POLICY_ROBOTS_UNKNOWN_HTTP_403'}]}))
    def supervise(**kwargs):
        calls.append([row['provider'] for row in kwargs['binding']['discovery_routes']])
        clock.current+=timedelta(seconds=2)
        return {'counts':{}}
    actor.run(manifest,tmp_path,binding=binding,activations=activations,
              clock=clock,sleep=clock.sleep,supervise=supervise)
    assert calls[0]==['FKEIBA_OFFICIAL']
    assert calls[1]==['NANKAN_OFFICIAL','FKEIBA_OFFICIAL']


def test_no_parallel_campaign_and_no_mutated_manifest_restart(tmp_path):
    manifest,binding,activations=fixture();clock=Clock(manifest)
    with actor.campaign_lock(tmp_path),pytest.raises(BlockingIOError):
        actor.run(manifest,tmp_path,binding=binding,activations=activations,clock=clock)
    (tmp_path/actor.STATE_NAME).write_text(json.dumps({'profile':actor.PROFILE,'manifest_sha256':'a'*64}))
    with pytest.raises(ValueError,match='MANIFEST_CHANGED'):
        actor.run(manifest,tmp_path,binding=binding,activations=activations,clock=clock)


def test_public_ci_cannot_start_private_runner(tmp_path,monkeypatch):
    manifest,binding,activations=fixture();monkeypatch.setenv('GITHUB_ACTIONS','true')
    with pytest.raises(ValueError,match='PUBLIC_CI_FORBIDDEN'):
        actor.run(manifest,tmp_path,binding=binding,activations=activations)


def test_multiple_leases_cannot_exceed_same_day_activation_total():
    manifest,binding,activations=fixture()
    manifest['leases'].insert(1,{'race_date':'2026-11-04',
        'start_at':'2026-11-04T14:00:02+09:00','stop_at':'2026-11-04T14:00:04+09:00'})
    manifest['approved_day_worker_seconds']['2026-11-04']=4
    with pytest.raises(ValueError,match='AGGREGATE_EXCEEDS_DATED_ACTIVATION'):
        actor.validate(manifest,binding=binding,activations=activations)


def test_reference_lease_must_fit_approved_effective_period():
    manifest, binding, activations = fixture()
    first = manifest['leases'][0]
    activation = activations[first['race_date']]
    activation['reference_only'] = True
    with pytest.raises(ValueError, match='REFERENCE_ACTIVATION_PERIOD_REQUIRED'):
        actor.validate(manifest, binding=binding, activations=activations)

    activation.update(effective_from=first['start_at'], effective_until=first['stop_at'])
    assert actor.validate(manifest, binding=binding, activations=activations) == manifest['leases']

    activation['effective_from'] = first['race_date'] + 'T14:00:01+09:00'
    with pytest.raises(ValueError, match='LEASE_OUTSIDE_REFERENCE_ACTIVATION_PERIOD'):
        actor.validate(manifest, binding=binding, activations=activations)


def test_transient_failed_route_is_available_in_later_lease(tmp_path):
    (tmp_path/'FNB_2026-11-04_DISCOVERY_ROUTE_prior.json').write_text(json.dumps({
        'race_date':'2026-11-04','attempts':[{'provider':'FKEIBA_OFFICIAL',
            'status':'HOLD','code':'TEMPORARY_DNS_UNAVAILABLE'}]}))
    assert actor.failed_routes(tmp_path,'2026-11-04') == set()


def test_early_discovery_hold_is_failed_not_completed_and_next_day_runs(tmp_path):
    manifest,binding,activations=fixture();clock=Clock(manifest);calls=[]
    def supervise(**kwargs):
        calls.append(kwargs['day'])
        if len(calls)==1:
            return {'status':'DISCOVERY_HOLD_NOT_NO_BET','code':'TEMPORARY_DNS_UNAVAILABLE',
                    'counts':{'verified_prestart_originals':0}}
        clock.current+=timedelta(seconds=kwargs['worker_seconds'])
        return {'counts':{}}
    result=actor.run(manifest,tmp_path,binding=binding,activations=activations,
                    clock=clock,sleep=clock.sleep,supervise=supervise)
    assert calls==list(actor.DATES)
    assert result['leases']['0']['status']=='FAILED'
    assert result['leases']['0']['supervisor_status']=='DISCOVERY_HOLD_NOT_NO_BET'


def test_pinned_binding_can_authorize_bounded_transient_recovery(tmp_path):
    manifest,binding,activations=fixture();clock=Clock(manifest);calls=[]
    manifest['leases'][0]['stop_at']='2026-11-04T14:02:00+09:00'
    manifest['approved_day_worker_seconds']['2026-11-04']=120
    activations['2026-11-04']['approved_worker_seconds']=120
    stop=day.stamp(manifest['leases'][0]['stop_at'])
    original_sleep=clock.sleep
    def sleep(seconds):
        if clock.current < stop:clock.current+=timedelta(seconds=seconds)
        else:original_sleep(seconds)
    def supervise(**kwargs):
        calls.append((kwargs['day'],kwargs['worker_seconds']))
        if len(calls)==1:
            return {'status':'DISCOVERY_HOLD_NOT_NO_BET','code':'TEMPORARY_DNS_UNAVAILABLE','counts':{}}
        clock.current+=timedelta(seconds=kwargs['worker_seconds'])
        return {'counts':{}}
    binding['authorize_discovery_retry']=lambda **kwargs:{'authorized':True,
        'retry_at':(kwargs['now']+timedelta(seconds=30)).isoformat()}
    result=actor.run(manifest,tmp_path,binding=binding,activations=activations,
                    clock=clock,sleep=sleep,supervise=supervise)
    assert calls[:2]==[('2026-11-04',120),('2026-11-04',90)]
    assert result['leases']['0']['supervisor_attempts']==2
    assert result['leases']['0']['status']=='COMPLETED'


def test_retry_authorizer_cannot_create_tight_loop(tmp_path):
    manifest,binding,activations=fixture();clock=Clock(manifest)
    binding['authorize_discovery_retry']=lambda **kwargs:{'authorized':True,'retry_at':kwargs['now'].isoformat()}
    def supervise(**kwargs):
        return {'status':'DISCOVERY_HOLD_NOT_NO_BET','code':'TEMPORARY_DNS_UNAVAILABLE','counts':{}}
    result=actor.run(manifest,tmp_path,binding=binding,activations=activations,
                    clock=clock,sleep=clock.sleep,supervise=supervise)
    assert result['leases']['0']['status']=='FAILED'
    assert result['leases']['0']['code']=='FINITE_ACTOR_RETRY_OUTSIDE_PERMITTED_WINDOW'


def test_legacy_discovery_403_cannot_be_retried_even_by_retry_callback(tmp_path):
    manifest,binding,activations=fixture();clock=Clock(manifest);authorized=[]
    binding['authorize_discovery_retry']=lambda **kwargs:authorized.append(kwargs)
    def supervise(**kwargs):
        return {'status':'DISCOVERY_HOLD_NOT_NO_BET','code':'SOURCE_POLICY_ROBOTS_UNKNOWN_HTTP_403','counts':{}}
    result=actor.run(manifest,tmp_path,binding=binding,activations=activations,
                    clock=clock,sleep=clock.sleep,supervise=supervise)
    assert authorized==[]
    assert result['leases']['0']['status']=='FAILED'
