"""Private FNB multi-Race supervision, with no authority or scheduler grant.

The formal LOCAL dispatcher and R20/R19 keep their own admission, adoption,
numerical, KRS and publication gates. This module adds durable private day
coordination: claim before calling an already authorized executor, re-read
originals after ACK, continue independent later races after HOLD, and never
turn reference material or an ACK into a completed prestart prediction.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import date, datetime, timezone, timedelta
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import time

from runtime.local_fnb_research_runtime import _private_root
from runtime.local_fnb_r14_private_dual_krs import ENGINE_SHA, MAP_SHA

PROFILE = 'KM-FNB-PRIVATE-DAY-SUPERVISOR-v1-20261103'
PLAN_PROFILE = 'KM-FNB-PRIVATE-DAY-DISCOVERY-v1'
CLASSIFICATION = 'SINGLE_RACE_PRESTART_NONPRODUCTION_NOT_REGISTERED_OOS'
JST = timezone(timedelta(hours=9))
STAGES = ('SOURCE', 'NUMERICAL', 'STATIC', 'KRS', 'MEC', 'TICKET', 'CAPITAL',
          'SAVE', 'DELIVERY', 'RESULT', 'LEARNING')
DIGEST = re.compile('[a-f0-9]{64}')


def stamp(value):
    result = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('AWARE_CLOCK_REQUIRED')
    return result.astimezone(timezone.utc)


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                       allow_nan=False) + '\n').encode()


def sha(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def safe_code(value):
    return value if isinstance(value, str) and re.fullmatch('[A-Z][A-Z0-9_]{0,119}', value) else 'PRIVATE_BINDING_FAILURE_UNVERIFIED'


def put(path, value):
    """Atomic/fsynced latest checkpoint; immutable execution originals stay owned by their executor."""
    path = Path(path)
    _private_root(path.parent)
    if path.is_symlink():
        raise ValueError('PRIVATE_CHECKPOINT_SYMLINK_FORBIDDEN')
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as f:
        temporary = Path(f.name)
        f.write(encoded(value)); f.flush(); os.fsync(f.fileno())
    try:
        temporary.chmod(0o600)
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_DIRECTORY)
        try: os.fsync(directory)
        finally: os.close(directory)
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def lease(root):
    """One private filesystem only; not a cross-host distributed lock."""
    fd = os.open(root / '.day_supervisor.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    finally:
        os.close(fd)


def validate_plan(plan, now):
    if plan.get('profile') != PLAN_PROFILE or plan.get('venue_id') != 'FNB':
        raise ValueError('FNB_DISCOVERY_PROFILE_REQUIRED')
    day = date.fromisoformat(plan['race_date'])
    observed = stamp(plan['observed_at'])
    if observed > now:
        raise ValueError('DISCOVERY_OBSERVATION_IN_FUTURE')
    rows = plan.get('races')
    if not isinstance(rows, list) or not rows:
        raise ValueError('OFFICIAL_RACES_NOT_DISCOVERED')
    numbers = [r.get('race_no') for r in rows]
    if any(type(n) is not int or not 1 <= n <= 12 for n in numbers) or len(set(numbers)) != len(numbers):
        raise ValueError('DISCOVERY_DUPLICATE_OR_INVALID_RACE')
    for row in rows:
        prefix = f'KM-LOCAL-FNB-{day:%Y%m%d}-R{row["race_no"]:02d}'
        if not re.fullmatch(re.escape(prefix) + r'(?:-[A-Za-z0-9_]+)*', str(row.get('race_id'))):
            raise ValueError('DISCOVERY_RACE_IDENTITY_MISMATCH')
        post = stamp(row['scheduled_post_at'])
        if post.astimezone(JST).date() != day:
            raise ValueError('DISCOVERY_POST_DATE_MISMATCH')
        cutoff = row.get('prediction_cutoff')
        if cutoff is not None and stamp(cutoff) >= post:
            raise ValueError('CUTOFF_MUST_PRECEDE_OFFICIAL_POST')
        if row.get('start_at') is not None and cutoff is not None and stamp(row['start_at']) >= stamp(cutoff):
            raise ValueError('APPROVED_START_WINDOW_INVALID')
    return sorted(rows, key=lambda r: (stamp(r['scheduled_post_at']), r['race_no']))


def original(root, descriptor):
    if not isinstance(descriptor, dict) or not DIGEST.fullmatch(str(descriptor.get('sha256'))):
        raise ValueError('PINNED_PRIVATE_ORIGINAL_REQUIRED')
    relative = Path(descriptor['path'])
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('ORIGINAL_OUTSIDE_PRIVATE_STORE')
    path = root / relative
    for part in (path, *path.parents):
        if part == root.parent: break
        if part.is_symlink(): raise ValueError('ORIGINAL_SYMLINK_FORBIDDEN')
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != descriptor['sha256']:
        raise ValueError('PRIVATE_ORIGINAL_BYTES_CHANGED')
    return data


def verify_prediction(root, race, result, now):
    """Require a qualified reader's same-Race evidence and independently read its actual originals."""
    if result.get('status') != 'VERIFIED_COMPLETE_ORIGINAL':
        return False
    if (result.get('race_id') != race['race_id'] or result.get('classification') != CLASSIFICATION
            or result.get('prediction_cutoff') != race.get('prediction_cutoff')
            or result.get('verifier_readback_pass') is not True
            or not DIGEST.fullmatch(str(result.get('verifier_code_sha256')))
            or not DIGEST.fullmatch(str(result.get('source_snapshot_sha256')))
            or not DIGEST.fullmatch(str(result.get('model_code_sha256')))):
        raise ValueError('COMPLETE_ORIGINAL_IDENTITY_OR_QUALIFICATION_MISMATCH')
    cutoff = stamp(race['prediction_cutoff'])
    if not stamp(result['source_freeze_at']) <= stamp(result['prediction_freeze_at']) < cutoff:
        raise ValueError('PRESTART_FREEZE_NOT_PROVEN')
    if stamp(result['prediction_freeze_at']) > now:
        raise ValueError('PREDICTION_FREEZE_IN_FUTURE')
    if result.get('source_snapshot_sha256') != result.get('stages', {}).get('SOURCE', {}).get('source_snapshot_sha256'):
        raise ValueError('SOURCE_SNAPSHOT_DIFFERENT_FROM_COMPLETION')
    n = result.get('horse_count')
    krs = result.get('stages', {}).get('KRS', {})
    if (type(n) is not int or n < 2 or result.get('index_cells') != n * 29
            or krs.get('engine_sha256') != ENGINE_SHA or krs.get('map_sha256') != MAP_SHA
            or krs.get('run_count') != 5000 or krs.get('seed') != 1):
        raise ValueError('FULL29_OR_CANONICAL_KRS_PROOF_MISMATCH')
    for stage in STAGES[:8]:
        evidence = result.get('stages', {}).get(stage, {})
        allowed = {'VERIFIED', 'COMPUTED_NO_BET'} if stage in {'MEC','TICKET','CAPITAL'} else {'VERIFIED'}
        if evidence.get('status') not in allowed:
            raise ValueError('FULL_PIPELINE_STAGE_NOT_VERIFIED_' + stage)
    no_bet = result.get('computed_no_bet')
    ticket = result['stages']['TICKET']
    no_bet_stages = any(result['stages'][stage].get('status') == 'COMPUTED_NO_BET'
                        for stage in ('MEC','TICKET','CAPITAL'))
    if (type(no_bet) is not bool or (no_bet_stages and not no_bet)
            or (no_bet and (ticket.get('status') != 'COMPUTED_NO_BET'
                or type(ticket.get('ticket_count')) is not int or ticket['ticket_count'] != 0
                or type(ticket.get('total_investment')) is not int or ticket['total_investment'] != 0
                or not isinstance(ticket.get('reason'), str) or not ticket['reason'].strip()))):
        raise ValueError('COMPUTED_NO_BET_REQUIRES_VERIFIED_ZERO_TICKET_REASON')
    original(root, result['body_original'])
    original(root, result['checkpoint_original'])
    original(root, result['source_original'])
    original(root, result['request_original'])
    return True


def _hold(cell, stage, code, now):
    cell.update(status='HOLD', first_failed_stage=stage, code=safe_code(code), observed_at=now.isoformat())
    cell.setdefault('first_failure', {'stage':stage, 'code':safe_code(code), 'observed_at':now.isoformat()})


def load_binding(path, expected):
    path = Path(path).absolute()
    if path.is_symlink() or not DIGEST.fullmatch(str(expected)):
        raise ValueError('PINNED_PRIVATE_BINDING_REQUIRED')
    _private_root(path.parent)
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError('PRIVATE_BINDING_SHA_MISMATCH')
    namespace = {'__name__':'_km_fnb_day_' + expected, '__file__':str(path)}
    exec(compile(data, str(path), 'exec'), namespace)
    result = namespace['get_day_binding']()
    for key in ('discover_day', 'verify_discovery', 'authorize_race', 'execute_race', 'inspect_race'):
        if not callable(result.get(key)):
            raise ValueError('QUALIFIED_DAY_BINDING_FUNCTION_MISSING_' + key.upper())
    result['_binding_sha256'] = expected
    return result


def activated(plan, race, binding, activation):
    if not binding or not activation or activation.get('enabled') is not True:
        raise ValueError('EXACT_EXISTING_ACTOR_ACTIVATION_REQUIRED')
    if (activation.get('race_date') != plan['race_date'] or activation.get('venue_id') != 'FNB'
            or race['race_no'] not in activation.get('race_numbers', [])
            or activation.get('classification') != CLASSIFICATION
            or not activation.get('approval_ref') or not activation.get('actor_id')
            or activation.get('binding_sha256') != binding.get('_binding_sha256')
            or activation.get('supervisor_code_sha256') != hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
            or type(activation.get('max_dispatches')) is not int or activation['max_dispatches'] < 1):
        raise ValueError('DATED_ACTOR_CODE_BINDING_AND_RACE_SCOPE_NOT_APPROVED')
    return True


def tick(plan, private_root, *, binding=None, activation=None, execute=False, clock=lambda:datetime.now(timezone.utc)):
    root = _private_root(private_root)
    now = clock(); stamp(now.isoformat())
    rows = validate_plan(plan, now)
    path = root / ('FNB_' + plan['race_date'] + '_DAY_CHECKPOINT.json')
    with lease(root):
        state = json.loads(path.read_bytes()) if path.exists() else {'profile':PROFILE, 'race_date':plan['race_date'], 'venue_id':'FNB', 'races':{}}
        if (state.get('profile'), state.get('race_date'), state.get('venue_id')) != (PROFILE, plan['race_date'], 'FNB'):
            raise ValueError('EXISTING_DAY_CHECKPOINT_IDENTITY_MISMATCH')
        state.update(observed_at=now.isoformat(), latest_discovery_sha256=sha(plan), execute_requested=execute,
                     production_authority_granted=False, actual_purchase=False, forward_oos_increment=0)
        save = lambda: put(path, state)
        for race in rows:
            key = str(race['race_no'])
            cell = state['races'].setdefault(key, {'race_no':race['race_no'], 'race_id':race['race_id'],
                'status':'DISCOVERED', 'stages':{s:{'status':'NOT_EXECUTED'} for s in STAGES}, 'dispatch_count':0})
            if cell.get('race_id') != race['race_id']:
                _hold(cell, 'REVISION', 'CLAIMED_RACE_REVISION_CHANGED_NO_AUTOMATIC_REDISPATCH', now); save(); continue
            cell['official_post_at'] = race['scheduled_post_at']
            cell['prediction_cutoff'] = race.get('prediction_cutoff')
            if cell.get('claim'):
                # Never resend an ambiguous dispatch, even after a process restart.
                cell.pop('completion', None)
                cell.pop('delivery', None)
                cell.pop('result_learning', None)
                if cell['claim']['race_sha256'] != sha(race):
                    _hold(cell, 'REVISION', 'CLAIMED_DISCOVERY_CHANGED_NO_AUTOMATIC_REDISPATCH', now); save(); continue
                try:
                    result = binding['inspect_race'](race=race, private_root=root, now=clock()) if binding else {}
                    if verify_prediction(root, race, result, clock()):
                        cell.update(status='VERIFIED_PRESTART_ORIGINAL', completion=result, stages=result['stages'])
                        permitted = False
                        if execute:
                            try:
                                activated(plan, race, binding, activation)
                                authorizer = binding.get('authorize_resume_mutations', binding['authorize_race'])
                                permitted = authorizer(race=race, activation=activation, plan=plan, now=clock()) is True
                                if not permitted:
                                    cell['activation_hold'] = 'CURRENT_RESUME_SOURCE_OWNER_AUTHORITY_NOT_VERIFIED'
                            except ValueError as error: cell['activation_hold'] = safe_code(str(error))
                        _deliver(binding, root, race, cell, clock, save, allow_mutation=permitted)
                        _post_result(binding, activation, root, race, cell, clock, save, allow_mutation=permitted)
                    elif cell.get('status') not in {'HOLD', 'MISSED_WINDOW'}:
                        cell['status'] = 'ACK_OR_AMBIGUOUS_DISPATCH_MONITOR_ORIGINALS'
                        if race.get('prediction_cutoff') and clock() >= stamp(race['prediction_cutoff']):
                            _hold(cell, 'TIME', 'NO_VERIFIED_ORIGINAL_AT_CUTOFF_NO_REDISPATCH', clock())
                except Exception as error:
                    _hold(cell, 'ORIGINAL_READBACK', safe_code(str(error)), clock())
                save(); continue
            # A missing Cutoff is never inferred from the official post. The
            # observed post nevertheless proves that a new prestart execution
            # is no longer possible. Classify time expiry before other missing
            # authorities so late races cannot remain misleadingly actionable.
            if clock() >= stamp(race['scheduled_post_at']):
                cell.update(status='MISSED_WINDOW', first_failed_stage='TIME',
                            code='OFFICIAL_POST_PASSED_NO_RETROACTIVE_PRESTART_EXECUTION')
                save(); continue
            if race.get('prediction_cutoff') is not None and clock() >= stamp(race['prediction_cutoff']):
                cell.update(status='MISSED_WINDOW', first_failed_stage='TIME',
                            code='NO_RETROACTIVE_PRESTART_EXECUTION')
                save(); continue
            if not execute:
                cell['status'] = 'OBSERVE_ONLY_NO_DISPATCH'
                if race.get('prediction_cutoff') is None:
                    cell['unresolved'] = ['PREDICTION_CUTOFF_NOT_RESOLVED']
                save(); continue
            try:
                if os.environ.get('GITHUB_ACTIONS') == 'true':
                    raise ValueError('PRIVATE_DAY_EXECUTION_PUBLIC_CI_FORBIDDEN')
                activated(plan, race, binding, activation)
                if now.astimezone(JST).date().isoformat() != plan['race_date']:
                    raise ValueError('EXECUTION_REQUIRES_CURRENT_JST_DAY')
                if binding['verify_discovery'](plan=plan, now=clock()) is not True:
                    raise ValueError('QUALIFIED_OFFICIAL_DISCOVERY_NOT_VERIFIED')
                if race.get('prediction_cutoff') is None:
                    raise ValueError('PREDICTION_CUTOFF_NOT_RESOLVED')
                cutoff = stamp(race['prediction_cutoff'])
                if clock() >= cutoff:
                    cell.update(status='MISSED_WINDOW', first_failed_stage='TIME', code='NO_RETROACTIVE_PRESTART_EXECUTION'); save(); continue
                if race.get('start_at') is None:
                    raise ValueError('APPROVED_START_TIME_NOT_RESOLVED')
                if clock() < stamp(race['start_at']):
                    cell['status'] = 'WAIT_APPROVED_START_WINDOW'; save(); continue
                if binding['authorize_race'](race=race, activation=activation, plan=plan, now=clock()) is not True:
                    raise ValueError('RACE_SOURCE_OWNER_CONSUMER_AUTHORITY_NOT_VERIFIED')
                if sum(c['dispatch_count'] for c in state['races'].values()) >= activation['max_dispatches']:
                    raise ValueError('APPROVED_DISPATCH_BUDGET_EXHAUSTED')
                # No wall-clock supplied by a caller can replace a fresh clock after checks.
                if clock() >= cutoff:
                    raise ValueError('CUTOFF_EXPIRED_DURING_PREFLIGHT')
                cell['claim'] = {'claimed_at':clock().isoformat(), 'race_sha256':sha(race),
                    'actor_id':activation['actor_id'], 'approval_ref':activation['approval_ref']}
                cell['status'] = 'CLAIM_DURABLE_BEFORE_EXECUTION'
                save()
                if clock() >= cutoff:
                    raise ValueError('CUTOFF_EXPIRED_AFTER_DURABLE_CLAIM')
                # Reserve the attempt durably before entering an external
                # Actor. A process death after send must consume its approved
                # budget even if acknowledgement/checkpoint completion is lost.
                # This conservative count is not an Actor-receipt assertion.
                cell['dispatch_count'] += 1
                save()
                if clock() >= cutoff:
                    raise ValueError('CUTOFF_EXPIRED_AFTER_DURABLE_ATTEMPT_RESERVATION')
                acknowledgement = binding['execute_race'](race=race, private_root=root, now=clock())
                # Retain only safe control fields. Raw bodies and callback tracebacks are not logs.
                cell['acknowledgement'] = {k:acknowledgement[k] for k in ('status','run_id') if k in acknowledgement}
                cell['status'] = 'ACK_OR_AMBIGUOUS_DISPATCH_MONITOR_ORIGINALS'; save()
                if acknowledgement.get('status') in {'EXECUTION_HOLD_NOT_NO_BET','HOLD','RESEARCH_EXECUTION_HOLD_NOT_NO_BET'}:
                    _hold(cell, safe_code(acknowledgement.get('first_failed_stage','EXECUTION')),
                          safe_code(acknowledgement.get('reason')), clock()); save()
                result = binding['inspect_race'](race=race, private_root=root, now=clock())
                if verify_prediction(root, race, result, clock()):
                    cell.update(status='VERIFIED_PRESTART_ORIGINAL', completion=result, stages=result['stages'])
                    _deliver(binding, root, race, cell, clock, save, allow_mutation=True)
                    _post_result(binding, activation, root, race, cell, clock, save, allow_mutation=True)
            except Exception as error:
                _hold(cell, 'EXECUTION' if cell.get('claim') else 'PREFLIGHT', safe_code(str(error)), clock())
            save()
        verified = [c for c in state['races'].values() if c.get('completion')
                    and c.get('status') in {'VERIFIED_PRESTART_ORIGINAL', 'DELIVERED_PRESTART'}]
        state['counts'] = {'discovered':len(rows), 'dispatched':sum(c['dispatch_count'] for c in state['races'].values()),
            'verified_prestart_originals':len(verified),
            'verified_prestart_recipient_deliveries':sum(c.get('status') == 'DELIVERED_PRESTART' for c in state['races'].values()),
            'no_bet_races':sum(c['completion'].get('computed_no_bet') is True for c in verified),
            'verified_result_learning_races':sum(bool(c.get('result_learning')) for c in verified)}
        save(); return state


def _deliver(binding, root, race, cell, clock, save, *, allow_mutation=False):
    if not binding or not callable(binding.get('inspect_delivery')):
        return
    completion = cell['completion']
    receipt = binding['inspect_delivery'](race=race, completion=completion, private_root=root, now=clock())
    if receipt.get('recipient_ack_verified') is True:
        data = json.loads(original(root, receipt['original']))
        if (data.get('race_id') != race['race_id'] or data.get('body_sha256') != completion['body_original']['sha256']
                or data.get('recipient_ack_verified') is not True
                or stamp(data['received_at']) < stamp(completion['prediction_freeze_at'])
                or not stamp(data['received_at']) < stamp(race['prediction_cutoff'])
                or stamp(data['received_at']) > clock()):
            raise ValueError('RECIPIENT_ACK_RECEIPT_IDENTITY_OR_CLOCK_MISMATCH')
        cell.update(status='DELIVERED_PRESTART', delivery=receipt); return
    if (not allow_mutation or cell.get('delivery_claim') or not callable(binding.get('deliver'))
            or clock() >= stamp(race['prediction_cutoff'])):
        return
    key = race['race_id'] + ':' + completion['body_original']['sha256']
    cell['delivery_claim'] = {'idempotency_key':key, 'claimed_at':clock().isoformat()}; save()
    # Ambiguous delivery is reconciled with inspect_delivery, never blindly re-sent.
    binding['deliver'](race=race, completion=completion, idempotency_key=key, private_root=root, now=clock())


def _post_result(binding, activation, root, race, cell, clock, save, *, allow_mutation=False):
    """Only a separately approved result Actor may continue a real frozen prediction."""
    if not binding or clock() < stamp(race['scheduled_post_at']) or not callable(binding.get('inspect_result_learning')):
        return
    cell.pop('result_learning', None)
    result = binding['inspect_result_learning'](race=race, completion=cell['completion'], private_root=root, now=clock())
    if result.get('status') == 'VERIFIED_RESULT_SETTLEMENT_LEARNING':
        if (result.get('race_id') != race['race_id']
                or result.get('prediction_source_sha256') != cell['completion']['source_snapshot_sha256']
                or result.get('prediction_body_sha256') != cell['completion']['body_original']['sha256']
                or result.get('official_result_admission_verified') is not True):
            raise ValueError('RESULT_FROZEN_PREDICTION_JOIN_UNVERIFIED')
        original(root, result['result_original']); original(root, result['learning_original'])
        cell['result_learning'] = result
        cell['stages'].update(RESULT={'status':'VERIFIED'}, LEARNING={'status':'VERIFIED'})
        return
    if (not allow_mutation or cell.get('post_result_claim') or not activation or activation.get('result_learning_enabled') is not True
            or not activation.get('post_result_approval_ref')
            or not callable(binding.get('authorize_post_result')) or not callable(binding.get('execute_result_learning'))):
        return
    if binding['authorize_post_result'](race=race, activation=activation, completion=cell['completion'], now=clock()) is not True:
        raise ValueError('POST_RESULT_ACTOR_NOT_AUTHORIZED')
    key = race['race_id'] + ':' + cell['completion']['source_snapshot_sha256']
    cell['post_result_claim'] = {'idempotency_key':key,'claimed_at':clock().isoformat()}; save()
    binding['execute_result_learning'](race=race, completion=cell['completion'], idempotency_key=key, private_root=root, now=clock())


def supervise(*, day, private_root, binding, activation, worker_seconds=0,
              clock=lambda:datetime.now(timezone.utc), sleep=time.sleep):
    if type(worker_seconds) is not int or not 0 <= worker_seconds <= 21000:
        raise ValueError('BOUNDED_WORKER_LEASE_REQUIRED')
    if worker_seconds and (not activation.get('worker_duration_approval_ref') or worker_seconds > activation.get('approved_worker_seconds',0)):
        raise ValueError('EXACT_WORKER_DURATION_APPROVAL_REQUIRED')
    end = clock() + timedelta(seconds=worker_seconds)
    while True:
        plan = binding['discover_day'](day=day, venue_id='FNB', now=clock())
        state = tick(plan, private_root, binding=binding, activation=activation, execute=True, clock=clock)
        if clock() >= end:
            return state
        sleep(min(30, max(0, (end-clock()).total_seconds())))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--discovery-json', required=True)
    p.add_argument('--private-root', required=True)
    p.add_argument('--execute', action='store_true')
    p.add_argument('--binding'); p.add_argument('--binding-sha256')
    p.add_argument('--activation'); p.add_argument('--activation-sha256')
    p.add_argument('--worker-seconds', type=int, default=0,
                   help='Bounded existing-Actor lease; requires exact activation duration approval')
    args = p.parse_args(argv)
    if args.worker_seconds and not args.execute:
        p.error('--worker-seconds requires --execute and an approved existing Actor binding')
    if args.execute and not all((args.binding, args.binding_sha256, args.activation, args.activation_sha256)):
        p.error('--execute requires --binding, --binding-sha256, --activation and --activation-sha256')
    plan = json.loads(Path(args.discovery_json).read_bytes())
    binding = activation = None
    if args.execute:
        binding = load_binding(args.binding, args.binding_sha256)
        data = Path(args.activation).read_bytes()
        if hashlib.sha256(data).hexdigest() != args.activation_sha256:
            raise ValueError('EXACT_ACTIVATION_BYTES_NOT_PINNED')
        activation = json.loads(data)
    if args.worker_seconds:
        state = supervise(day=plan['race_date'], private_root=args.private_root,
                          binding=binding, activation=activation, worker_seconds=args.worker_seconds)
    else:
        state = tick(plan, args.private_root, binding=binding, activation=activation, execute=args.execute)
    print(json.dumps({'profile':PROFILE,'race_date':state['race_date'],'counts':state['counts'],
        'prediction_authority_granted':False,'actual_purchase':False},ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
