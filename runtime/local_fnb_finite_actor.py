"""Finite private FNB Actor, using the existing qualified day supervisor.

This is an executable runner, not a Provider, licence, model, Delivery transport
or deployment grant. Pinned private day activations and real day bindings remain
required. A restart resumes only the remaining part of an approved lease; the
day supervisor's durable Race claims prevent a second dispatch.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import date, datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import time

from runtime import local_fnb_day_supervisor as day

PROFILE = 'KM-FNB-FINITE-ACTOR-20261104-06-v1'
DATES = ('2026-11-04', '2026-11-05', '2026-11-06')
STATE_NAME = 'FNB_20261104_06_FINITE_ACTOR_CHECKPOINT.json'


class StopActor(BaseException):
    """Exit callback stacks without converting a stop into a SOURCE failure."""


class EndLease(BaseException):
    pass


def pinned(path, expected):
    path = Path(path).absolute()
    if path.is_symlink() or not day.DIGEST.fullmatch(str(expected)):
        raise ValueError('FINITE_ACTOR_PINNED_PRIVATE_INPUT_REQUIRED')
    day._private_root(path.parent)
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError('FINITE_ACTOR_PRIVATE_INPUT_SHA_MISMATCH')
    return json.loads(data)


@contextmanager
def campaign_lock(root):
    fd = os.open(root / '.fnb_finite_actor.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    finally:
        os.close(fd)


def validate(manifest, *, binding, activations):
    dates = manifest.get('race_dates')
    # Historical campaigns keep their existing checkpoint. A new campaign
    # is pinned to one explicitly approved day and cannot reuse that lease.
    if not isinstance(dates, list) or not dates or any(type(value) is not str for value in dates):
        raise ValueError('FINITE_ACTOR_EXACT_DATED_SCOPE_AND_CODE_REQUIRED')
    historical = all(value in DATES for value in dates)
    new_day = (len(dates) == 1 and dates[0] > DATES[-1]
               and date.fromisoformat(dates[0]).isoformat() == dates[0]
               and (activations.get(dates[0]) or {}).get('reference_only') is True)
    if (manifest.get('profile') != PROFILE or manifest.get('venue_id') != 'FNB'
            or manifest.get('classification') != day.CLASSIFICATION
            or not (historical or new_day)
            or dates != sorted(set(dates))
            or manifest.get('actor_code_sha256') != hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
            or not manifest.get('approval_ref')):
        raise ValueError('FINITE_ACTOR_EXACT_DATED_SCOPE_AND_CODE_REQUIRED')
    leases = manifest.get('leases')
    if not isinstance(leases, list) or not leases:
        raise ValueError('FINITE_ACTOR_APPROVED_LEASES_REQUIRED')
    previous_end = None
    days = set()
    totals = {value:0 for value in dates}
    for row in leases:
        value = row.get('race_date')
        start, stop = day.stamp(row['start_at']), day.stamp(row['stop_at'])
        seconds = (stop - start).total_seconds()
        if (value not in dates or start.astimezone(day.JST).date().isoformat() != value
                or stop.astimezone(day.JST).date().isoformat() != value
                or not seconds.is_integer() or not 1 <= seconds <= 21000
                or (previous_end is not None and start < previous_end)):
            raise ValueError('FINITE_ACTOR_LEASE_SCOPE_DURATION_OR_OVERLAP_INVALID')
        activation = activations[value]
        if (activation.get('race_date') != value or activation.get('venue_id') != 'FNB'
                or activation.get('classification') != day.CLASSIFICATION
                or activation.get('race_numbers') != list(range(1,13))
                or activation.get('max_dispatches') != 12
                or activation.get('enabled') is not True
                or activation.get('binding_sha256') != binding.get('_binding_sha256')
                or activation.get('supervisor_code_sha256') != hashlib.sha256(Path(day.__file__).read_bytes()).hexdigest()
                or not activation.get('worker_duration_approval_ref')
                or type(activation.get('approved_worker_seconds')) is not int
                or activation['approved_worker_seconds'] < seconds):
            raise ValueError('FINITE_ACTOR_EXISTING_DAY_ACTIVATION_MISMATCH')
        if new_day and (not manifest.get('actor_id')
                        or manifest['actor_id'] != activation.get('actor_id')
                        or manifest['approval_ref'] != activation.get('approval_ref')):
            raise ValueError('FINITE_ACTOR_NEW_DAY_APPROVAL_OR_ACTOR_MISMATCH')
        if activation.get('reference_only') is True:
            if not activation.get('effective_from') or not activation.get('effective_until'):
                raise ValueError('FINITE_ACTOR_REFERENCE_ACTIVATION_PERIOD_REQUIRED')
            if not (day.stamp(activation['effective_from']) <= start < stop
                    <= day.stamp(activation['effective_until'])):
                raise ValueError('FINITE_ACTOR_LEASE_OUTSIDE_REFERENCE_ACTIVATION_PERIOD')
        totals[value] += int(seconds)
        previous_end = stop
        days.add(value)
    if days != set(dates) or manifest.get('approved_day_worker_seconds') != totals:
        raise ValueError('FINITE_ACTOR_AGGREGATE_DURATION_NOT_PINNED')
    if any(totals[value] > activations[value]['approved_worker_seconds'] for value in dates):
        raise ValueError('FINITE_ACTOR_AGGREGATE_EXCEEDS_DATED_ACTIVATION')
    return leases


def nonretryable_failure(record):
    code = str(record.get('code', ''))
    return ('HTTP_403' in code or 'ROBOTS_DISALLOWED' in code
            or 'ROBOTS_DENIED' in code or record.get('retryable') is False)


def failed_routes(root, value):
    """Keep known 403/robots refusals excluded; transient misses may recover."""
    failed = set()
    for path in root.glob('FNB_' + value + '_DISCOVERY_ROUTE_*.json'):
        if path.is_symlink():
            raise ValueError('FINITE_ACTOR_DISCOVERY_RECEIPT_SYMLINK_FORBIDDEN')
        data = json.loads(path.read_bytes())
        if data.get('race_date') != value:
            raise ValueError('FINITE_ACTOR_DISCOVERY_RECEIPT_DAY_MISMATCH')
        for attempt in data.get('attempts', []):
            if (attempt.get('status') == 'HOLD' and nonretryable_failure(attempt)
                    and isinstance(attempt.get('provider'), str)):
                failed.add(attempt['provider'])
    return failed


def run(manifest, private_root, *, binding, activations, clock=lambda:datetime.now(timezone.utc),
        sleep=time.sleep, supervise=day.supervise):
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        raise ValueError('PRIVATE_DAY_EXECUTION_PUBLIC_CI_FORBIDDEN')
    root = day._private_root(private_root)
    leases = validate(manifest, binding=binding, activations=activations)
    digest = day.sha(manifest)
    first_day = manifest['race_dates'][0]
    path = root / (STATE_NAME if first_day in DATES else f'FNB_{first_day}_FINITE_ACTOR_CHECKPOINT.json')
    with campaign_lock(root):
        if path.is_symlink():
            raise ValueError('FINITE_ACTOR_CHECKPOINT_SYMLINK_FORBIDDEN')
        state = json.loads(path.read_bytes()) if path.exists() else {
            'profile':PROFILE,'manifest_sha256':digest,'leases':{},'counts_are_live_acceptance':False}
        if state.get('profile') != PROFILE or state.get('manifest_sha256') != digest:
            raise ValueError('FINITE_ACTOR_EXISTING_MANIFEST_CHANGED')
        last = day.stamp(state['observed_at']) if state.get('observed_at') else None
        def now():
            nonlocal last
            value = day.stamp(clock())
            if last is not None and value < last:
                raise ValueError('FINITE_ACTOR_CLOCK_REGRESSION')
            last = value
            return value
        def save():
            state['observed_at'] = now().isoformat()
            day.put(path, state)
        try:
            for index, row in enumerate(leases):
                key = str(index)
                start, stop = day.stamp(row['start_at']), day.stamp(row['stop_at'])
                cell = state['leases'].setdefault(key, {'race_date':row['race_date'],
                    'start_at':row['start_at'],'stop_at':row['stop_at'],'status':'NOT_STARTED'})
                if cell['status'] in ('COMPLETED','ELAPSED','FAILED'):
                    continue
                while now() < start:
                    state['status'] = 'WAIT_APPROVED_LEASE'
                    save()
                    sleep(min(30, max(0, (start-now()).total_seconds())))
                if now() >= stop:
                    cell['status'] = 'ELAPSED'
                    save(); continue
                value = row['race_date']
                cell.update(status='RUNNING', resumed=cell.get('started_at') is not None)
                cell.setdefault('started_at',now().isoformat())
                state['status'] = 'RUNNING_APPROVED_LEASE'
                save()
                def lease_clock():
                    current = now()
                    if current >= stop:
                        raise EndLease()
                    return current
                while now() < stop:
                    active_binding = dict(binding)
                    if binding.get('discovery_routes'):
                        failed = failed_routes(root, value)
                        active_binding['discovery_routes'] = [r for r in binding['discovery_routes']
                                                             if r.get('provider') not in failed]
                        if not active_binding['discovery_routes']:
                            cell.update(status='FAILED',code='NO_UNTRIED_QUALIFIED_DISCOVERY_ROUTE')
                            break
                    cell['supervisor_attempts'] = cell.get('supervisor_attempts', 0) + 1
                    save()
                    try:
                        # Existing Race claims and qualification/Delivery checks
                        # remain in force for every invocation and restart.
                        result = supervise(day=value, private_root=root, binding=active_binding,
                            activation=activations[value], worker_seconds=int((stop-now()).total_seconds()),
                            clock=lease_clock, sleep=sleep)
                        cell['last_observed_counts'] = result.get('counts', {})
                        cell['supervisor_status'] = result.get('status')
                        if result.get('status') == 'DISCOVERY_HOLD_NOT_NO_BET':
                            cell.update(status='FAILED',code=day.safe_code(result.get('code')))
                            authorize = binding.get('authorize_discovery_retry')
                            if nonretryable_failure(result) or not callable(authorize) or now() >= stop:
                                break
                            observed = now()
                            retry = authorize(day=value, result=result, activation=activations[value],
                                now=observed, attempt_count=cell['supervisor_attempts'])
                            if not isinstance(retry, dict) or retry.get('authorized') is not True:
                                break
                            retry_at = day.stamp(retry['retry_at'])
                            # A pinned binding owns retry eligibility and Provider
                            # cadence. The wrapper never tight-loops or extends time.
                            if retry_at < observed + day.timedelta(seconds=30) or retry_at >= stop:
                                raise ValueError('FINITE_ACTOR_RETRY_OUTSIDE_PERMITTED_WINDOW')
                            cell.update(status='DISCOVERY_HOLD_RETRY_PENDING',retry_at=retry_at.isoformat())
                            save()
                            while now() < retry_at:
                                sleep(min(30, max(0, (retry_at-now()).total_seconds())))
                            continue
                        # A callback returning is not proof that the lease ended.
                        # Normal supervisors can return a fractional second early.
                        while now() < stop:
                            cell['status'] = 'WAIT_LEASE_END_AFTER_SUPERVISOR_RETURN'
                            save()
                            sleep(min(30, max(0, (stop-now()).total_seconds())))
                        cell['status'] = 'COMPLETED'
                        break
                    except EndLease:
                        cell['status'] = 'COMPLETED'
                        break
                    except Exception as error:
                        cell.update(status='FAILED',code=day.safe_code(str(error)))
                        break
                save()
            state['status'] = 'FINITE_RUN_ENDED'
            save()
        except StopActor:
            state['status'] = 'STOPPED_RESUMABLE_WITH_EXISTING_RACE_CLAIMS'
            save()
        return state


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',required=True)
    parser.add_argument('--manifest-sha256',required=True)
    parser.add_argument('--private-root',required=True)
    args = parser.parse_args(argv)
    manifest = pinned(args.manifest,args.manifest_sha256)
    binding = day.load_binding(manifest['binding']['path'],manifest['binding']['sha256'])
    activations = {value:pinned(manifest['activations'][value]['path'],
                               manifest['activations'][value]['sha256']) for value in manifest['race_dates']}
    previous = {}
    def stop(signum, frame):
        raise StopActor()
    try:
        for signum in (signal.SIGTERM,signal.SIGINT):
            previous[signum] = signal.signal(signum,stop)
        result = run(manifest,args.private_root,binding=binding,activations=activations)
    finally:
        for signum, handler in previous.items():
            signal.signal(signum,handler)
    print(json.dumps({'profile':PROFILE,'status':result['status'],
        'live_prediction_success_inferred':False,'actual_purchase':False}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
