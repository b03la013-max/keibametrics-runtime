"""LOCAL day planning and bounded handoff to the EXISTING Race-Key workflow.

Planning is read-only and never freezes a prediction. Execution is opt-in through
an owner-approved dated plan AND the repository activation variable. Claims are
published before dispatch: an ambiguous acknowledgement is held, never retried.
"""
from __future__ import annotations

import argparse
import base64
from datetime import date, datetime, timedelta, timezone
import gzip
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import parse_qs, urljoin, urlparse

from runtime.local_race_key_intake import FIELDS, JST, build
from runtime.local_physical.nar_source_manifest import LOCAL_BABA_CODES, VENUE_NAMES, _url, _race_card_source
from runtime.local_physical.source_acquisition import fetch_source, _decode, _html_text
from runtime.local_physical.nar_runner_universe import enrich_source_artifact

WORKFLOW = 'km-local-race-key-entry.yml'
ROOT = Path(__file__).resolve().parents[1]


def sha(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
    temporary.replace(path)


def raw_html(snapshot):
    raw = gzip.decompress(base64.b64decode(snapshot['raw_gzip_b64'], validate=True))
    if hashlib.sha256(raw).hexdigest() != snapshot['raw_sha256']:
        raise ValueError('OFFICIAL_RAW_SHA_MISMATCH')
    if snapshot['http_status'] != 200 or snapshot['authority'] != 'NAR_OFFICIAL':
        raise ValueError('OFFICIAL_MENU_OR_CARD_UNAVAILABLE')
    return _decode(raw, snapshot.get('content_type', ''))


class CardLinks(HTMLParser):
    def __init__(self, venue, day):
        super().__init__()
        self.venue, self.day, self.races = venue, day, set()

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return
        href = dict(attrs).get('href', '')
        parsed = urlparse(urljoin('https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/', href))
        if (parsed.scheme, parsed.netloc, parsed.path) != (
                'https', 'www.keiba.go.jp', '/KeibaWeb/TodayRaceInfo/DebaTable'):
            return
        q = parse_qs(parsed.query)
        if q.get('k_babaCode') != [LOCAL_BABA_CODES[self.venue]] or q.get('k_raceDate') != [self.day.replace('-', '/')]:
            return
        values = q.get('k_raceNo', [])
        if len(values) != 1 or not re.fullmatch(r'(?:[1-9]|1[0-2])', values[0]):
            raise ValueError('OFFICIAL_MENU_RACE_NUMBER_INVALID')
        self.races.add(int(values[0]))


def discover(venue, day, cutoff_seconds, *, now, fetch=fetch_source, authority_resolver=None):
    """Use official menu links, then each individual official card; never guess N."""
    if venue not in LOCAL_BABA_CODES or date.fromisoformat(day).isoformat() != day:
        raise ValueError('LOCAL_DAY_IDENTITY_INVALID')
    if type(cutoff_seconds) is not int or not 120 <= cutoff_seconds <= 3600:
        raise ValueError('EXPLICIT_CUTOFF_SECONDS_REQUIRED')
    from runtime.family_authority_guard import resolve_current_authority
    authority = (authority_resolver or resolve_current_authority)(now=now)
    menu_url = _url('RaceList', LOCAL_BABA_CODES[venue], day.replace('-', '/'), 1)
    spec = {'source_id': f'NAR-{venue}-{day}-DAY-MENU', 'source_class': 'OFFICIAL_DAY_MENU',
            'authority': 'NAR_OFFICIAL', 'official': True, 'required': True,
            'url': menu_url, 'max_bytes': 900000}
    menu, errors = fetch(spec, '')
    if errors:
        raise ValueError('OFFICIAL_MENU_HOLD:' + ';'.join(errors))
    links = CardLinks(venue, day)
    links.feed(raw_html(menu))
    numbers = sorted(links.races)
    if not numbers or numbers != list(range(1, max(numbers) + 1)):
        raise ValueError('OFFICIAL_ALL_RACES_NOT_PROVEN')
    records, snapshots = [], [menu]
    for number in numbers:
        spec = _race_card_source(venue, LOCAL_BABA_CODES[venue], day.replace('-', '/'), number)
        card, errors = fetch(spec, '')
        if errors:
            raise ValueError(f'OFFICIAL_CARD_R{number:02d}_HOLD:' + ';'.join(errors))
        html = raw_html(card)
        navigation = CardLinks(venue, day)
        navigation.feed(html)
        if navigation.races | {number} != set(numbers):
            raise ValueError('OFFICIAL_ALL_RACES_MENU_CARD_DISAGREEMENT')
        text = re.sub(r'\s+', '', _html_text(html)).split('競走馬')[0]
        d = date.fromisoformat(day)
        heading = re.search(rf'{d.year}年{d.month}月{d.day}日.*?{VENUE_NAMES[venue]}第{number}競走(\d{{1,2}}:\d{{2}})発走', text)
        if not heading:
            raise ValueError(f'OFFICIAL_CARD_R{number:02d}_IDENTITY_OR_CLOCK_MISSING')
        post = datetime.fromisoformat(day + 'T' + heading[1] + ':00+09:00')
        fields = dict(venue_id=venue, race_date=day, race_no=number,
                      scheduled_post_at=post.isoformat(), prediction_cutoff=(post-timedelta(seconds=cutoff_seconds)).isoformat())
        # Shape/authority only: past races may be observed in a day plan, never dispatched.
        request = build(fields, now=min(now, post-timedelta(days=1)), authority_resolver=lambda **kw: authority)
        tables = card.get('extracted_evidence', {}).get('race_card_tables')
        universe = enrich_source_artifact({'normalized_evidence': {'race_card_tables': {
            'value': tables, 'source_id': card['source_id'], 'snapshot_sha256': card['snapshot_sha256']}}})
        if not universe['declared_runner_universe']['runners']:
            raise ValueError('OFFICIAL_RUNNER_UNIVERSE_EMPTY')
        records.append({'race_key': f'{venue}-{d:%Y%m%d}-R{number:02d}-LIVE-R1',
                        'execution_id': request['execution_id'], 'fields': fields,
                        'current_authority_at_observation': request['current_authority_manifest'],
                        'declared_runner_universe': universe['declared_runner_universe'],
                        'observed_active_runner_universe': universe['active_runner_universe'],
                        'runner_status_registry': universe['runner_status_registry'],
                        'source_basis_sha256': card['snapshot_sha256'],
                        'freeze': False, 'dispatch_requires_fresh_signed_source': True})
        snapshots.append(card)
    plan = {'family_id': 'LOCAL', 'venue_id': venue, 'race_date': day,
            'observed_at': now.isoformat(), 'races': records, 'official_snapshots': snapshots,
            'status': 'PREREGISTRATION_ONLY_NOT_SIGNED_SOURCE', 'prediction_freeze': False}
    plan['plan_sha256'] = sha(plan)
    return plan


def authorization(approval, plan, root, now):
    """Approval is an owner-maintained repository record, not inferred from a race request."""
    from runtime.family_authority_guard import resolve_current_authority
    from runtime.execution_gateway import family_config
    _, current = resolve_current_authority(root=root, now=now)
    owner = json.loads((root/'profiles/local_production_static_owner_20261014_v1.json').read_text())
    expected = {'family_id': 'LOCAL', 'venue_id': plan['venue_id'], 'race_date': plan['race_date'],
                'current_authority_manifest': current['manifest_id'],
                'destination': family_config('LOCAL')['external_endpoint'].rstrip('/'),
                'plan_sha256': plan['plan_sha256']}
    if any(approval.get(k) != v for k, v in expected.items()):
        raise ValueError('DATED_OWNER_APPROVAL_BINDING_REQUIRED')
    if (approval.get('enabled') is not True or not approval.get('owner_approval_ref')
            or approval.get('scheduled_execution_authorized') is not True
            or approval.get('existing_runtime_usage_cost_authorized') is not True
            or approval.get('data_scope') != 'INTENT_SOURCE_STATIC_PRE_KRS_KRS_FINAL_RESULT_SETTLEMENT'
            or sorted(approval.get('race_numbers', [])) != [r['fields']['race_no'] for r in plan['races']]
            or not owner.get('enabled') or plan['venue_id'] not in owner.get('venues', [])
            or owner.get('family_authority_basis') != current['manifest_id']):
        raise ValueError('OWNER_SCOPE_SCHEDULE_OR_COST_APPROVAL_REQUIRED')
    lead, margin = approval.get('start_lead_seconds'), approval.get('minimum_remaining_seconds')
    if type(lead) is not int or type(margin) is not int or not 1800 <= lead <= 7200 or not 300 <= margin < lead:
        raise ValueError('OWNER_DISPATCH_WINDOW_REQUIRED')
    return current['manifest_id']


def checkpoint_status(root, eid):
    """Observe existing stage storage without rerunning prediction or settlement."""
    execution = root/'runtime/executions'/eid
    latest = {}
    for phase in ('SOURCE', 'FORMAL', 'RESULT'):
        pointer = execution/phase/'LATEST.json'
        if pointer.exists():
            latest[phase] = json.loads(pointer.read_text())
    delivery = root/'runtime/execution_reports'/eid/'delivery/canonical_tree.txt'
    reports=[]
    from runtime.formal_failure_diagnostics import failure_class_for, resume_hint_for
    for path in sorted((root/'runtime/execution_reports'/eid).glob('*.json')):
        report=json.loads(path.read_text())
        code=report.get('code') or report.get('reason')
        reports.append({'path':str(path.relative_to(root)), 'status':report.get('status'),
                        'error':code, 'failure_class':failure_class_for(code) if code else None,
                        'recovery':resume_hint_for(code) if code else None})
    stages = {}
    filenames = {'SOURCE':'source_receipt_envelope.json', 'PRE_KRS':'pre_krs_receipt_envelope.json',
                 'KRS':'krs_receipt_envelope.json', 'FINAL':'final_receipt_envelope.json',
                 'RESULT':'result_receipt_envelope.json'}
    for stage, filename in filenames.items():
        phase = 'FORMAL' if stage in {'PRE_KRS','KRS','FINAL'} else stage
        pointer = latest.get(phase)
        if not pointer:
            stages[stage] = {'status':'NOT_OBSERVED'}
            continue
        path = root/'runtime/executions'/pointer['run_path']/filename
        if not path.exists():
            stages[stage] = {'status':'NOT_OBSERVED'}
            continue
        envelope = json.loads(path.read_text())
        stages[stage] = {'status':'PERSISTED_REQUIRES_FRESH_VERIFICATION',
                         'receipt_sha256':envelope.get('receipt_sha256'),
                         'timestamp':envelope.get('receipt',{}).get('timestamp'), 'artifact_ref':str(path.relative_to(root))}
    return {'checkpoints': latest, 'stages':stages, 'existing_diagnostics':reports,
            'canonical_tree_ref': str(delivery.relative_to(root)) if delivery.exists() else None,
            'chat_delivery_verified': False, 'actual_purchase_pfs': 'UNKNOWN'}


def reconcile_run(fields, claimed_at):
    """Match the existing workflow's explicit race title; ambiguous matches HOLD."""
    title = f"LOCAL {fields['venue_id']} {fields['race_date']} R{fields['race_no']}"
    result = subprocess.run(['gh','run','list','--workflow',WORKFLOW,'--branch','main',
                             '--event','workflow_dispatch','--limit','100',
                             '--json','databaseId,displayTitle,createdAt,status,conclusion,url'],
                            capture_output=True,text=True,check=True,timeout=30)
    matches = [r for r in json.loads(result.stdout) if r['displayTitle']==title
               and datetime.fromisoformat(r['createdAt'].replace('Z','+00:00')) >= datetime.fromisoformat(claimed_at)]
    if len(matches)>1:
        raise ValueError('MULTIPLE_ACTIONS_RUNS_FOR_CLAIM')
    return matches[0] if matches else None


def runtime_ready():
    from runtime.execution_gateway import family_config, fetch_health, assess_runtime_health
    health = fetch_health(family_config('LOCAL')['external_endpoint'])
    result = assess_runtime_health(health, 'LOCAL')
    if result['status'] != 'PASS':
        raise ValueError('RUNTIME_FINGERPRINT_HOLD:' + ','.join(result.get('errors', [])))
    return result


def dispatch(fields):
    command = ['gh', 'workflow', 'run', WORKFLOW, '--ref', 'main']
    for field in FIELDS:
        command += ['-f', f'{field}={fields[field]}']
    result = subprocess.run(command, text=True, capture_output=True, timeout=30)
    if result.returncode:
        raise RuntimeError('ACTIONS_DISPATCH_UNACKNOWLEDGED:' + result.stderr.strip())
    return {'transport': 'GITHUB_ACTIONS_WORKFLOW_DISPATCH', 'acknowledged': True,
            'run_id': None, 'signed_final_proven': False}


def tick(root, plan, approval, state, *, now, execute=False, authorize=authorization,
         health=runtime_ready, send=dispatch, publish=None, reconcile=reconcile_run, clock=None):
    if sha({k:v for k,v in plan.items() if k != 'plan_sha256'}) != plan.get('plan_sha256'):
        raise ValueError('DAY_PLAN_SHA_MISMATCH')
    if now.tzinfo is None or now.astimezone(JST).date().isoformat() != plan['race_date']:
        raise ValueError('DISPATCH_REQUIRES_CURRENT_LOCAL_DAY')
    current = authorize(approval, plan, root, now)
    if execute and publish is None:
        raise ValueError('DURABLE_CLAIM_PUBLISH_REQUIRED')
    state.setdefault('races', {})
    for race in plan['races']:
        eid, fields = race['execution_id'], race['fields']
        cell = state['races'].setdefault(eid, {})
        cell.update(checkpoint_status(root, eid))
        post, cutoff = (datetime.fromisoformat(fields[k]) for k in ('scheduled_post_at','prediction_cutoff'))
        cell['remaining_seconds'] = (cutoff-now).total_seconds()
        if cell.get('claimed_at'):
            cell['status'] = 'DISPATCH_ACKNOWLEDGED_MONITOR_CHECKPOINTS' if cell.get('acknowledgement') else 'HOLD_AMBIGUOUS_DISPATCH_NO_AUTOMATIC_RETRY'
            if execute:
                try:
                    cell['actions_run'] = reconcile(fields, cell['claimed_at'])
                    if (cell.get('actions_run') or {}).get('conclusion') in {'failure','cancelled','timed_out'}:
                        cell['status']='ACTIONS_FAILURE_CHECKPOINT_RECOVERY_HOLD'
                    if cell['stages']['FINAL']['status']=='NOT_OBSERVED' and now >= cutoff-timedelta(seconds=approval['minimum_remaining_seconds']):
                        cell['deadline_alert']='FINAL_NOT_OBSERVED_DEADLINE_APPROACHING_OR_EXPIRED'
                    if cell['stages']['FINAL']['status']!='NOT_OBSERVED':
                        from runtime.local_race_key_gate import terminal_state
                        cell['final_readback']=terminal_state(eid, (cell.get('actions_run') or {}).get('status','unknown'))
                except Exception as exc:
                    cell['monitor_error']=str(exc)
            continue
        # Check ALL same-race execution revisions, not only the expected R1.
        prefix = eid.rsplit('-R1', 1)[0]
        existing = list((root/'runtime/executions').glob(prefix+'-R*')) + list((root/'runtime/formal_intents').glob(prefix+'-R*.json'))
        key = root/'runtime/race_key_requests'/f"{race['race_key']}.json"
        for other in (root/'runtime/race_key_requests').glob('*.json'):
            candidate=json.loads(other.read_text())
            if all(str(candidate.get(k))==str(fields[k]) for k in ('venue_id','race_date','race_no')):
                existing.append(other)
        if existing or key.exists():
            cell['status'] = 'EXISTING_RACE_READ_BACK_OR_APPROVED_CHECKPOINT_RESUME_ONLY'
            if execute and cell['stages']['FINAL']['status']!='NOT_OBSERVED':
                try:
                    from runtime.local_race_key_gate import terminal_state
                    cell['final_readback']=terminal_state(eid,'existing')
                except Exception as exc:
                    cell['monitor_error']=str(exc)
            continue
        if now >= min(cutoff, post-timedelta(seconds=120))-timedelta(seconds=approval['minimum_remaining_seconds']):
            cell['status'] = 'DEADLINE_HOLD_NO_RETROACTIVE_START'
            continue
        if now < post-timedelta(seconds=approval['start_lead_seconds']):
            cell['status'] = 'WAIT_DISPATCH_WINDOW'
            continue
        if cell.get('preflight_attempts',0) >= 3:
            cell['status']='HOLD_PREFLIGHT_RETRY_LIMIT_OWNER_RECOVERY_REQUIRED'
            continue
        try:
            request = build(fields, now=now)
            if request['execution_id'] != eid or request['current_authority_manifest'] != current:
                raise ValueError('RACE_OR_AUTHORITY_BINDING_MISMATCH')
            if execute:
                cell['preflight_attempts']=cell.get('preflight_attempts',0)+1
            cell['runtime_health'] = health() if execute else {'status': 'NOT_CALLED_DRY_RUN'}
            if not execute:
                cell['status'] = 'DRY_RUN_ELIGIBLE_NO_LIVE_SEND'
                continue
            send_at = clock() if clock else now
            if send_at >= min(cutoff,post-timedelta(seconds=120))-timedelta(seconds=approval['minimum_remaining_seconds']):
                raise ValueError('DEADLINE_EXPIRED_DURING_PREFLIGHT')
            build(fields,now=send_at)  # Re-resolve authority and deadline after health latency.
            cell.update(status='CLAIMED_BEFORE_DISPATCH', claimed_at=now.isoformat(),
                        fields_sha256=sha(fields), current_authority_manifest=current,
                        recovery='RECONCILE_ACTIONS_RUN_OR_EXISTING_CHECKPOINT; NEVER BLIND_REDISPATCH')
            write(key, fields)
            publish()  # Must succeed BEFORE any external runtime-capable dispatch.
            send_at = clock() if clock else now
            if send_at >= min(cutoff,post-timedelta(seconds=120))-timedelta(seconds=approval['minimum_remaining_seconds']):
                raise ValueError('DEADLINE_EXPIRED_DURING_DURABLE_CLAIM')
            latest_request=build(fields,now=send_at)
            if latest_request['current_authority_manifest'] != current:
                raise ValueError('CURRENT_AUTHORITY_CHANGED_DURING_CLAIM')
            cell['acknowledgement'] = send(fields)
            cell['status'] = 'DISPATCH_ACKNOWLEDGED_MONITOR_CHECKPOINTS'
            publish()
        except Exception as exc:
            cell.update(status='HOLD_AMBIGUOUS_DISPATCH_NO_AUTOMATIC_RETRY' if cell.get('claimed_at') else 'HOLD_PRE_DISPATCH',
                        error=str(exc), first_failure='ACTIONS_HANDOFF' if cell.get('claimed_at') else 'PRE_DISPATCH_GUARD')
            # Other races remain independent; no RESULT waiting in this driver.
    state.update(observed_at=now.isoformat(), plan_sha256=plan['plan_sha256'],
                 production_prediction_changed=False, chat_delivery_verified=False)
    return state


def publish_state(root, paths):
    """Reuse strict existing persistence; never auto-resolve authority/receipt conflicts."""
    from tools.persist_local_checkpoints import persist
    def git(*args):
        subprocess.run(['git',*args], cwd=root, check=True, capture_output=True, text=True)
    git('add', '--', *paths)
    dirty = subprocess.run(['git','diff','--cached','--quiet'], cwd=root).returncode
    if dirty:
        git('commit','-m','execution: LOCAL race-day claims/status [skip ci]')
    persist(cwd=root, branch='main')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root', default=str(ROOT))
    p.add_argument('--venue', required=True, choices=sorted(LOCAL_BABA_CODES))
    p.add_argument('--date', required=True)
    p.add_argument('--cutoff-seconds', required=True, type=int)
    p.add_argument('--execute', action='store_true')
    args = p.parse_args()
    root, now = Path(args.repo_root).resolve(), datetime.now(timezone.utc)
    name = args.date+'-'+args.venue
    folder = root/'runtime/local_race_day_plan'
    plan_path, state_path = folder/(name+'.json'), folder/(name+'.state.json')
    approval_path = root/'profiles/local_autonomous_approvals'/(name+'.json')
    if args.execute and (os.environ.get('KM_LOCAL_AUTONOMOUS_ENABLED') != 'true' or not approval_path.exists()):
        raise ValueError('OWNER_ACTIVATION_AND_DATED_APPROVAL_REQUIRED')
    plan = json.loads(plan_path.read_text()) if plan_path.exists() else discover(args.venue,args.date,args.cutoff_seconds,now=now)
    if (plan['venue_id'],plan['race_date']) != (args.venue,args.date):
        raise ValueError('DAY_PLAN_IDENTITY_MISMATCH')
    write(plan_path, plan)
    if not args.execute:
        print(json.dumps({'status': 'PREREGISTRATION_ONLY', 'races': len(plan['races']), 'plan_sha256': plan['plan_sha256']}))
        return
    approval = json.loads(approval_path.read_text())
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    paths = [str(plan_path.relative_to(root)), str(state_path.relative_to(root)), 'runtime/race_key_requests']
    # Only each approved race's derived delivery folder; no unrelated race writes.
    def publish():
        write(state_path, state)
        delivery_paths=[str(p.relative_to(root)) for r in plan['races']
                        if (p:=root/'runtime/execution_reports'/r['execution_id']/'delivery').exists()]
        publish_state(root, paths+delivery_paths)
    tick(root,plan,approval,state,now=now,execute=True,publish=publish,clock=lambda:datetime.now(timezone.utc))
    publish()


if __name__ == '__main__':
    main()
