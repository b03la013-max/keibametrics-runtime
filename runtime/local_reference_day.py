"""Prepare every official URW reference independently of Formal activation.

Uses the existing official day discovery, reference compiler and immutable
readback. No Runtime POST, Production consumer, signed FINAL or betting action.
Completed forecasts are read back; failed captures have separate attempts.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
import fcntl
import gzip
import hashlib
import json
import re
from pathlib import Path

from runtime.local_race_day_dispatcher import discover, sha, write
from runtime.local_race_key_intake import JST
from runtime.local_race_entry import (run_reference, reference_answer,
    reference_answer_content_check, reference_readback_presentation, chat_formal_status)
from runtime.urw_reference_source_policy import source_policy_failure


ROOT = Path(__file__).resolve().parents[1]


def resolve_start_request(root, *, event, changed=(), now=None):
    """Existing push-start pattern, strictly URW reference-only and dated."""
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None:raise ValueError('REFERENCE_START_TIMEZONE_REQUIRED')
    today=now.astimezone(JST).date().isoformat();root=Path(root)
    prefix='runtime/local_reference_start_requests/'
    if event=='push':
        paths=[p for p in changed if re.fullmatch(re.escape(prefix)+r'\d{4}-\d{2}-\d{2}\.json',p)]
        if not paths:return None
        if len(paths)!=1:raise ValueError('REFERENCE_START_EXACTLY_ONE_DATED_REQUEST')
        path=root/paths[0]
    elif event=='schedule':
        path=root/prefix/(today+'.json')
        if not path.exists():return None
    else:
        raise ValueError('REFERENCE_START_UNSUPPORTED_EVENT')
    request=json.loads(path.read_text());day=request.get('race_date','')
    if (request.get('family_id')!='LOCAL' or request.get('venue_id')!='URW'
            or request.get('reference_only') is not True or request.get('race_numbers')!=list(range(1,13))
            or any(type(n) is not int for n in request.get('race_numbers',[]))
            or request.get('formal_runtime_post_authorized') is not False
            or request.get('external_notifications_authorized') is not False
            or type(request.get('new_paid_openai_api_requests')) is not int
            or request.get('new_paid_openai_api_requests')!=0 or not request.get('request_basis')
            or date.fromisoformat(day).isoformat()!=day or day<today
            or path.name!=day+'.json'):
        raise ValueError('REFERENCE_START_SCOPE_OR_DATE_INVALID')
    return day


def immutable(path, value):
    """Never overwrite a different completed publication or plan."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != value:
            raise ValueError('REFERENCE_IMMUTABLE_CONFLICT:'+str(path))
        return
    with path.open('xb') as output:
        output.write(value)


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)+'\n').encode()


def verify_plan(plan, day):
    if (plan.get('family_id')!='LOCAL' or plan.get('venue_id')!='URW'
            or plan.get('race_date')!=day
            or plan.get('plan_sha256')!=sha({k:v for k,v in plan.items() if k!='plan_sha256'})
            or [r['fields']['race_no'] for r in plan['races']]!=list(range(1,13))):
        raise ValueError('REFERENCE_OFFICIAL_TWELVE_RACE_PLAN_REQUIRED')
    for row in plan['races']:
        fields=row['fields']
        if (fields['venue_id']!='URW' or fields['race_date']!=day
                or datetime.fromisoformat(fields['scheduled_post_at']).astimezone(JST).date().isoformat()!=day
                or datetime.fromisoformat(fields['prediction_cutoff'])>=datetime.fromisoformat(fields['scheduled_post_at'])):
            raise ValueError('REFERENCE_PLAN_RACE_BINDING_MISMATCH')
    return plan


def load_plan(folder, day):
    return verify_plan(json.loads(gzip.decompress((folder/'official_plan.json.gz').read_bytes())),day)


def prepare_plan(root, day, *, now=None, fetch=None):
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None or date.fromisoformat(day)<now.astimezone(JST).date():
        raise ValueError('REFERENCE_PLAN_CURRENT_OR_FUTURE_DAY_REQUIRED')
    folder=Path(root)/'runtime/local_reference'/day
    if (folder/'official_plan.json.gz').exists():
        return load_plan(folder,day)
    if fetch is None:
        from scripts.urw_candidate_krs_replay import fetch_public_urw_reference
        fetch=fetch_public_urw_reference
    plan=verify_plan(discover('URW',day,120,now=now,fetch=fetch),day)
    immutable(folder/'official_plan.json.gz',gzip.compress(encoded(plan),mtime=0))
    return plan


def verified_readback(folder, expected):
    """Validate original bytes and actual body; no model/capture is invoked."""
    publication=json.loads((folder/'publication.json').read_text())
    if publication.get('sha256')!=sha({k:v for k,v in publication.items() if k!='sha256'}):
        raise ValueError('REFERENCE_PUBLICATION_HASH_MISMATCH')
    if any(publication.get(k)!=v for k,v in expected.items()):
        raise ValueError('REFERENCE_PUBLICATION_RACE_MISMATCH')
    reference=folder/publication['reference_directory']
    # The only accepted pointer is a local immutable attempt of this same race.
    if (publication['reference_directory']!='reference'
            and not re.fullmatch(r'attempts/[0-9]{3}',publication['reference_directory'])):
        raise ValueError('REFERENCE_PUBLICATION_PATH_INVALID')
    request=json.loads((reference/'reference_intent.json').read_text())
    if any(str(request.get(k))!=str(expected[k]) for k in ('venue_id','race_date','race_no')):
        raise ValueError('REFERENCE_PUBLICATION_RACE_MISMATCH')
    report=run_reference(request,output=reference,run_id='reference-day-readback')
    prediction=json.loads((reference/'reference_prediction.json').read_text())
    source=json.loads((reference/'reference_source.json').read_text())
    body=(folder/'answer.txt').read_text()
    # Validate the frozen body against its original requirements; formatting
    # code may evolve without re-rendering or re-timestamping the forecast.
    parts=json.loads((folder/'answer_parts.json').read_text())
    _,source_parts=reference_answer(prediction,source)
    if (not reference_answer_content_check(parts,body)['content_complete']
            or not reference_answer_content_check(source_parts,body)['content_complete']
            or hashlib.sha256(body.encode()).hexdigest()!=publication['answer_sha256']
            or prediction['sha256']!=publication['forecast_sha256']
            or source['source_snapshot_sha256']!=publication['evidence_sha256']
            or prediction['method_components_sha256']!=publication['method_components_sha256']
            or not report.get('reference_readback_only')):
        raise ValueError('REFERENCE_PUBLICATION_CONTENT_MISMATCH')
    if 'readback_sha256' in publication:
        display,_=reference_readback_presentation(prediction,source,body,parts)
        if ((folder/'readback.txt').read_text()!=display
                or hashlib.sha256(display.encode()).hexdigest()!=publication['readback_sha256']):
            raise ValueError('REFERENCE_PUBLICATION_READBACK_MISMATCH')
    return publication,body


def one_race(folder, day, number, *, generate=run_reference, clock=lambda:datetime.now(timezone.utc)):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    with (folder/'worker.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        return _one_race_locked(folder, day, number, generate=generate, clock=clock)


def _one_race_locked(folder, day, number, *, generate, clock):
    expected={'family_id':'LOCAL','venue_id':'URW','race_date':day,'race_no':number}
    if (folder/'publication.json').exists():
        return verified_readback(folder,expected)
    attempts=folder/'attempts';attempts.mkdir(exist_ok=True)
    existing=sorted(attempts.glob('[0-9][0-9][0-9]'))
    # A completed forecast is resumed, never regenerated after an interrupted
    # publication. Failed acquisition attempts retain their original files.
    completed=[p for p in existing if (p/'reference_prediction.json').exists()]
    if len(completed)>1:
        raise ValueError('REFERENCE_COMPETING_COMPLETED_ATTEMPTS')
    selected=completed[0] if completed else attempts/f'{len(existing)+1:03d}'
    if not completed and len(existing)>=3:
        raise ValueError('REFERENCE_CAPTURE_ATTEMPT_LIMIT_REACHED')
    intent={**expected,'prediction_mode':'REFERENCE'}
    report=generate(intent,output=selected,run_id='urw-reference-day')
    prediction=json.loads((selected/'reference_prediction.json').read_text())
    source=json.loads((selected/'reference_source.json').read_text())
    body,parts=reference_answer(prediction,source)
    if not reference_answer_content_check(parts,body)['content_complete']:
        raise ValueError('REFERENCE_COMPLETE_BODY_REQUIRED')
    display,_=reference_readback_presentation(prediction,source,body,parts)
    publication={**expected,'profile':'KM-URW-FROZEN-REFERENCE-PUBLICATION-v1',
        'race_id':prediction['race_id'],'reference_directory':str(selected.relative_to(folder)),
        'evidence_sha256':prediction['source_snapshot_sha256'],'forecast_sha256':prediction['sha256'],
        'method_components_sha256':prediction['method_components_sha256'],
        'declared_runner_universe_sha256':sha(source['declared_runner_universe']),
        'reference_runner_count':len(prediction['runners']),
        'scheduled_post_at':prediction['scheduled_post_at'],'prediction_cutoff':prediction['prediction_cutoff'],
        'source_frozen_at':prediction['source_freeze_at'],'forecast_frozen_at':prediction['frozen_at'],
        'answer_sha256':hashlib.sha256(body.encode()).hexdigest(),
        'readback_sha256':hashlib.sha256(display.encode()).hexdigest(),
        'prepared_at':clock().isoformat(),'formal_final_proven':False,
        'notification_sent_at':None,'user_received_at':None,'chat_render_verified':False,
        'source_freshness_claim':False,'recommended_pfs':'N/A','actual_purchase_pfs':'UNKNOWN'}
    publication['sha256']=sha(publication)
    immutable(folder/'answer.txt',body.encode())
    immutable(folder/'answer_parts.json',encoded(parts))
    immutable(folder/'readback.txt',display.encode())
    # Publication is last, after all required content is durably present.
    immutable(folder/'publication.json',encoded(publication))
    return verified_readback(folder,expected)


def run_day(root, day, *, plan=None, generate=run_reference, clock=lambda:datetime.now(timezone.utc)):
    root=Path(root);folder=root/'runtime/local_reference'/day
    folder.mkdir(parents=True,exist_ok=True)
    with (folder/'worker.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        plan=verify_plan(plan,day) if plan is not None else prepare_plan(root,day)
        status={'family_id':'LOCAL','venue_id':'URW','race_date':day,'plan_sha256':plan['plan_sha256'],
            'cohort_race_numbers':list(range(1,13)),'discovered_count':12,'races':[],
            'formal_registered_count':0,'formal_activation_approved_count':0,
            'runtime_post_count':0,'paid_openai_api_requests':0,'signed_final_count':0,
            'user_delivery_verified':False,'observed_at':clock().isoformat()}
        bodies=[];readbacks=[]
        for race in plan['races']:
            fields=race['fields'];number=fields['race_no']
            row={'race_no':number,'formal_execution_id':race['execution_id'],
                'scheduled_post_at':fields['scheduled_post_at'],'prediction_cutoff':fields['prediction_cutoff'],
                'declared_runner_count':len(race['declared_runner_universe']['runners']),
                'formal_status':'NOT_EXECUTED_REQUIRES_SEPARATE_DATED_AUTHORIZATION',
                'reference_status':'HOLD','chat_render_verified':False}
            try:
                race_folder=folder/f'R{number:02d}'
                frozen=(race_folder/'publication.json').exists() or any(
                    race_folder.glob('attempts/*/reference_prediction.json'))
                if not frozen and clock()>=datetime.fromisoformat(fields['prediction_cutoff']):
                    raise ValueError('REFERENCE_DEADLINE_NO_NEW_FORECAST')
                pub,body=one_race(race_folder,day,number,generate=generate,clock=clock)
                if any(pub[k]!=fields[k] for k in ('scheduled_post_at','prediction_cutoff')):
                    raise ValueError('REFERENCE_PLAN_CLOCK_CHANGED_RECONCILIATION_REQUIRED')
                saved_source=json.loads((folder/f'R{number:02d}'/pub['reference_directory']/'reference_source.json').read_text())
                saved_prediction=json.loads((folder/f'R{number:02d}'/pub['reference_directory']/'reference_prediction.json').read_text())
                saved_parts=json.loads((folder/f'R{number:02d}'/'answer_parts.json').read_text())
                display,_=reference_readback_presentation(saved_prediction,saved_source,body,saved_parts)
                # Retain the original answer; the display derivative adds the
                # current race course from exactly the same frozen SOURCE.
                immutable(folder/f'R{number:02d}'/'readback.txt',display.encode())
                row.update(reference_status='AVAILABLE_VERIFIED_FROZEN_BODY',reference=pub,
                    reference_runner_count=pub['reference_runner_count'],
                    declared_universe_changed=saved_source['declared_runner_universe']['runner_universe_sha256']!=race['declared_runner_universe']['runner_universe_sha256'],
                    answer_path=f'runtime/local_reference/{day}/R{number:02d}/answer.txt',
                    readback_path=f'runtime/local_reference/{day}/R{number:02d}/readback.txt',
                    readback_sha256=hashlib.sha256(display.encode()).hexdigest())
                bodies.append(body)
                readbacks.append(display)
            except (OSError,ValueError,KeyError,TypeError,RuntimeError) as exc:
                row.update(source_policy_failure(exc) or {
                    'first_failed_stage':'REFERENCE_CAPTURE_OR_READBACK','error':f'{type(exc).__name__}:{exc}'})
            status['races'].append(row)
            row['lifecycle']={
                'Discovery':'OFFICIAL_PLAN_VERIFIED',
                'Registration':'NOT_PERFORMED_BY_REFERENCE_WORKER',
                'SOURCE':'UNSIGNED_REFERENCE_ONLY' if row['reference_status']=='AVAILABLE_VERIFIED_FROZEN_BODY' else 'REFERENCE_UNAVAILABLE',
                'Active_Runner':'DECLARED_ONLY_REQUIRES_FRESH_RACE_DAY_VERIFICATION',
                'Numerical':'NOT_EXECUTED', 'Static':'NOT_EXECUTED',
                'KRS':'NOT_EXECUTED', 'FINAL':'NOT_EXECUTED',
                'REFERENCE':row['reference_status'],
                'Delivery':'SAVED_NOT_CHAT_RENDER_VERIFIED',
                'Settlement':'N/A_REFERENCE_ONLY', 'Learning':'N/A_REFERENCE_ONLY'}
            # A HOLD in one race never removes it or stops later races.
            write(folder/'status.json',status)
        status['reference_complete_count']=sum(r['reference_status']=='AVAILABLE_VERIFIED_FROZEN_BODY' for r in status['races'])
        first_hold=next((row for row in status['races'] if row['reference_status']=='HOLD'),None)
        if first_hold and first_hold.get('first_failed_stage')=='DATA_SOURCE_POLICY':
            status.update({key:first_hold[key] for key in ('first_failed_stage','code','source_policy')})
            status['first_failed_race_no']=first_hold['race_no']
        status['completed_at']=clock().isoformat()
        status['reference_all_races_complete']=status['reference_complete_count']==12
        status['completion_scope']='SAVED_REFERENCE_CONTENT_ONLY_NOT_CHAT_RENDER_OR_FORMAL'
        status['formal_count_scope']='THIS_REFERENCE_WORKER_ONLY; CONSULT_VERIFIED_RUNTIME_RECEIPTS_FOR_FORMAL'
        status['sha256']=sha(status)
        write(folder/'status.json',status)
        if status['reference_all_races_complete']:
            combined=(f'{date.fromisoformat(day).year}年の浦和開催・保存済みREFERENCE全12R。正式予測ではありません。\n'
                'Raceの日付と番号を照合し、該当Raceの本文だけを原本忠実に読み戻してください。\n\n'
                +'\n\n'.join(bodies))
            immutable(folder/'all_races_reference.txt',combined.encode())
            immutable(folder/'all_races_readback.txt','\n\n'.join(readbacks).encode())
        return status


def run_discovery_window(root, *, now=None, start_day=None, generate=run_reference, fetch=None):
    """Reuse the day worker for today's and tomorrow's official URW cards.

    This is unsigned reference discovery only, with no dated Formal authority.
    An unavailable day never prevents the other day's independent execution.
    """
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None:raise ValueError('REFERENCE_START_TIMEZONE_REQUIRED')
    today=now.astimezone(JST).date()
    anchor=date.fromisoformat(start_day) if start_day else today
    if anchor not in (today-timedelta(days=1),today):
        raise ValueError('REFERENCE_DISCOVERY_WINDOW_DATE_MISMATCH')
    result={'family_id':'LOCAL','venue_id':'URW','reference_only':True,
        'observed_at':now.isoformat(),'runtime_post_count':0,'formal_final_proven':False,
        'chat_render_verified':False,'days':[]}
    for offset in (0,1):
        day=(anchor+timedelta(days=offset)).isoformat()
        folder=Path(root)/'runtime/local_reference'/day
        try:
            # A published display can be read without re-acquiring its private
            # SOURCE. This is a fixed-cohort readback, never fresh Discovery.
            if not (folder/'official_plan.json.gz').exists():
                from runtime.local_reference_delivery import read_delivery_day
                saved=read_delivery_day(root,day)
                if saved is not None:
                    write(folder/'status.json',saved)
                    result['days'].append({**saved,'discovered_count':0,
                        'status_path':str(folder/'status.json')})
                    continue
            plan=prepare_plan(root,day,now=now,fetch=fetch)
            report=run_day(root,day,plan=plan,generate=generate)
            summary={'race_date':day,'discovered_count':report['discovered_count'],
                'reference_complete_count':report['reference_complete_count'],
                'reference_all_races_complete':report['reference_all_races_complete'],
                'status_path':str(folder/'status.json')}
            if report.get('first_failed_stage')=='DATA_SOURCE_POLICY':
                summary.update({key:report[key] for key in ('first_failed_stage','code','source_policy','first_failed_race_no')})
            result['days'].append(summary)
        except (OSError,ValueError,KeyError,TypeError,RuntimeError) as error:
            failure={'family_id':'LOCAL','venue_id':'URW','race_date':day,
                'status':'HOLD_REFERENCE_PREPARATION','first_failed_stage':'OFFICIAL_DISCOVERY_OR_REFERENCE',
                'error':f'{type(error).__name__}:{error}','observed_at':datetime.now(timezone.utc).isoformat(),
                'formal_final_proven':False,'runtime_post_count':0,'chat_render_verified':False}
            failure.update(source_policy_failure(error) or {})
            write(folder/'preparation_failure.json',failure)
            result['days'].append(failure)
    return result


def readiness(root, plan):
    """Concrete approval packet; diagnosis grants no execution authority."""
    from runtime.execution_gateway import family_config
    root=Path(root);day=plan['race_date']
    rows=[]
    for race in plan['races']:
        f=race['fields'];post=datetime.fromisoformat(f['scheduled_post_at'])
        rows.append({'race_no':f['race_no'],'execution_id':race['execution_id'],
            'intent_draft':race['request_intent_draft'],
            'scheduled_post_at':f['scheduled_post_at'],'prediction_cutoff':f['prediction_cutoff'],
            'proposed_source_window':[(post-timedelta(minutes=60)).isoformat(),(post-timedelta(minutes=12)).isoformat()],
            'minimum_remaining_seconds_proposed':600,
            'processing_time_status':'600_SECOND_RESERVE_PROPOSAL_NOT_MEASURED_URW_FORMAL_LATENCY',
            'checkpoint_root':f"runtime/executions/{race['execution_id']}",
            'formal_readback':f"python -m runtime.local_race_key_gate --readback-only --execution-id {race['execution_id']}",
            'reference_readback':f'runtime/local_reference/{day}/R{f["race_no"]:02d}/readback.txt',
            'reference_original_answer':f'runtime/local_reference/{day}/R{f["race_no"]:02d}/answer.txt',
            'formal_gates':chat_formal_status({'family_id':'LOCAL','venue_id':'URW','race_date':day,'race_no':f['race_no']})})
    return {'family_id':'LOCAL','venue_id':'URW','race_date':day,'plan_sha256':plan['plan_sha256'],
        'discovered_race_numbers':list(range(1,13)),'formal_approved_race_numbers':[],
        'formal_registration_count':0,'destination':family_config('LOCAL')['external_endpoint'],
        'payload_scope':'INTENT_SOURCE_STATIC_PRE_KRS_KRS_FINAL_RESULT_SETTLEMENT',
        'initial_formal_phase':'B_SINGLE_RACE_ONLY_UNTIL_ACCEPTED',
        'formal_post_authorized':False,'worker_activation_authorized':False,
        'proposed_worker_leases':[['11:15','16:45'],['16:15','18:10']],
        'worker_timezone':'Asia/Tokyo','retry_policy':'EXISTING_PRE_SEND_TRANSPORT_ONLY; AMBIGUOUS_DISPATCH_NO_RETRY',
        'preflight_max_attempts':3,'ambiguous_dispatch_retries':0,
        'initial_formal_max_dispatches':1,'initial_formal_concurrency':1,
        'reference_max_capture_attempts_per_race':3,
        'railway_soft_usd':5,'railway_hard_usd':10,'new_paid_openai_api_requests':0,
        'result_continuation':'EXISTING_LOCAL_ENTRY_RESULT_JOB_ONLY_AFTER_VERIFIED_SIGNED_FINAL',
        'races':rows}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    selection=parser.add_mutually_exclusive_group(required=True)
    selection.add_argument('--date')
    selection.add_argument('--discover-current-and-next',action='store_true')
    parser.add_argument('--repo-root',default=str(ROOT))
    parser.add_argument('--plan-only',action='store_true')
    args=parser.parse_args();root=Path(args.repo_root)
    if args.discover_current_and_next:
        if args.plan_only:raise ValueError('REFERENCE_DISCOVERY_REQUIRES_DAY_WORKER')
        result=run_discovery_window(root)
        print(json.dumps(result,ensure_ascii=False))
        return 0 if any(r.get('reference_all_races_complete') for r in result['days']) else 2
    if date.fromisoformat(args.date).isoformat()!=args.date:
        raise ValueError('REFERENCE_EXACT_ISO_DATE_REQUIRED')
    folder=root/'runtime/local_reference'/args.date
    try:
        if not (folder/'official_plan.json.gz').exists() and not args.plan_only:
            from runtime.local_reference_delivery import read_delivery_day
            saved=read_delivery_day(root,args.date)
            if saved is not None:
                write(folder/'status.json',saved)
                print(json.dumps(saved,ensure_ascii=False))
                return 0 if saved['reference_all_races_complete'] else 2
        plan=prepare_plan(root,args.date)
        write(folder/'formal_readiness.json',readiness(root,plan))
        result={'discovered_count':12,'plan_sha256':plan['plan_sha256']} if args.plan_only else run_day(root,args.date,plan=plan)
    except (OSError,ValueError,KeyError,TypeError,RuntimeError) as error:
        # Acquisition errors must survive a failed worker, just like successful
        # frozen bodies. This diagnostic grants no Formal or delivery credit.
        failure={'family_id':'LOCAL','venue_id':'URW','race_date':args.date,
            'status':'HOLD_REFERENCE_PREPARATION','error':f'{type(error).__name__}:{error}',
            'first_failed_stage':'REFERENCE_READBACK_OR_GENERATION' if (folder/'official_plan.json.gz').exists() else 'OFFICIAL_DISCOVERY',
            'observed_at':datetime.now(timezone.utc).isoformat(),'runtime_posts':0,
            'formal_final_proven':False,'chat_render_verified':False}
        failure.update(source_policy_failure(error) or {})
        write(folder/'preparation_failure.json',failure)
        print(json.dumps(failure,ensure_ascii=False))
        return 2
    print(json.dumps({k:v for k,v in result.items() if k!='races'},ensure_ascii=False))
    return 0 if args.plan_only or result['reference_all_races_complete'] else 2


if __name__=='__main__':
    raise SystemExit(main())
