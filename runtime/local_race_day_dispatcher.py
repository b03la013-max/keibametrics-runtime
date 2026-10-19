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
import time
from urllib.parse import parse_qs, urljoin, urlparse

from runtime.local_race_key_intake import FIELDS, JST, build
from runtime.local_physical.nar_source_manifest import LOCAL_BABA_CODES, VENUE_NAMES, _url, _race_card_source, _odds_source
from runtime.local_physical.source_acquisition import fetch_source, _decode, _html_text
from runtime.local_physical.nar_runner_universe import enrich_source_artifact

WORKFLOW = 'km-local-race-key-entry.yml'
ROOT = Path(__file__).resolve().parents[1]
SOUTH_KANTO = ('FNB', 'OHI', 'URW', 'KAW')


class MeetingLinks(HTMLParser):
    """Official same-day navigation, excluding unrelated dates and hosts."""
    def __init__(self, day):
        super().__init__()
        self.day, self.codes, self.card_codes = day.replace('-', '/'), set(), set()

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return
        p = urlparse(urljoin('https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/', dict(attrs).get('href', '')))
        if (p.scheme, p.netloc) != ('https', 'www.keiba.go.jp'):
            return
        q = parse_qs(p.query)
        if q.get('k_raceDate') != [self.day] or len(q.get('k_babaCode', [])) != 1:
            return
        code = q['k_babaCode'][0]
        if not re.fullmatch(r'\d{1,2}', code):
            raise ValueError('OFFICIAL_VENUE_CODE_INVALID')
        code = code.zfill(2)  # Official top emits BAN=3, registry stores 03.
        if p.path == '/KeibaWeb/TodayRaceInfo/RaceList':
            self.codes.add(code)
        elif p.path == '/KeibaWeb/TodayRaceInfo/DebaTable':
            self.card_codes.add(code)


def read_official(spec, *, fetch, reads, read_observer=None, sleeper=time.sleep):
    # Official GET only. Do not apply this retry to signed SOURCE/FORMAL
    # submissions, receipt validation, or an ambiguous Actions handoff.
    from urllib.error import URLError, HTTPError
    from runtime.execution_gateway import RETRYABLE_HTTP_STATUS
    for attempt in range(1,4):
        event = {'source_id':spec['source_id'], 'url':spec['url'],
                 'attempt':attempt, 'observed_at':datetime.now(timezone.utc).isoformat()}
        try:
            snapshot, errors = fetch(spec, '')
            retryable = snapshot.get('http_status') in RETRYABLE_HTTP_STATUS
            event.update(http_status=snapshot.get('http_status'), errors=errors,
                         snapshot_sha256=snapshot.get('snapshot_sha256'))
            if retryable:
                event['failed_snapshot'] = snapshot
            if not retryable or attempt == 3:
                return snapshot, errors
        except (OSError, ValueError) as exc:
            event.update(error=str(exc),error_type=type(exc).__name__)
            retryable = (isinstance(exc,(TimeoutError,ConnectionError,URLError))
                and (not isinstance(exc,HTTPError) or exc.code in RETRYABLE_HTTP_STATUS))
            retryable |= str(exc).startswith('SOURCE_DNS_RESOLUTION_FAILED:')
            if not retryable or attempt == 3:
                raise
        finally:
            reads.append(event)
            if read_observer:
                read_observer(event)
        sleeper(attempt)


def discover_meetings(day, *, now, fetch=fetch_source, read_observer=None, sleeper=time.sleep):
    """Read the actual official daily menu. Fetch failure never means no meeting.

    Use the official all-venue day index, not RaceList without a venue (which
    redirects to a message page). Same-day official RaceList links are positive
    meeting evidence. An empty/unrecognized page remains HOLD, even on a holiday.
    """
    if date.fromisoformat(day).isoformat() != day or now.tzinfo is None:
        raise ValueError('LOCAL_DAY_IDENTITY_INVALID')
    spec = {'source_id':f'NAR-{day}-SOUTH-KANTO-MEETINGS', 'source_class':'OFFICIAL_DAY_MENU',
            'authority':'NAR_OFFICIAL', 'official':True, 'required':True, 'max_bytes':900000,
            'url':'https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/TodayRaceInfoTop?k_raceDate='+day.replace('-', '%2F')}
    reads = []
    snapshot, errors = read_official(spec, fetch=fetch, reads=reads, read_observer=read_observer, sleeper=sleeper)
    if read_observer:
        read_observer({'official_snapshot':snapshot})
    if errors:
        raise ValueError('OFFICIAL_MEETINGS_HOLD:'+';'.join(errors))
    html = raw_html(snapshot)
    links = MeetingLinks(day)
    links.feed(html)
    # BAN can be present in the official menu without joining LOCAL dispatch.
    codes = {**LOCAL_BABA_CODES, 'BAN':'03'}
    if not links.codes or not links.codes <= set(codes.values()):
        raise ValueError('OFFICIAL_DAY_MEETINGS_NOT_PROVEN')
    held = links.codes
    venues = [v for v in SOUTH_KANTO if LOCAL_BABA_CODES[v] in held]
    result = {'family_id':'LOCAL', 'race_date':day, 'observed_at':now.isoformat(),
              'allowed_venues':list(SOUTH_KANTO), 'venues':venues,
              'status':'OFFICIAL_MEETINGS_DISCOVERED' if venues else 'NO_SOUTH_KANTO_MEETING',
              'official_snapshot':snapshot, 'discovery_read_attempts':reads, 'prediction_freeze':False,
              'formal_registration_proven':False, 'new_live_send':False}
    result['sha256'] = sha(result)
    return result


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


def discover(venue, day, cutoff_seconds, *, now, fetch=fetch_source, authority_resolver=None,
             read_observer=None, sleeper=time.sleep):
    """Use official menu links, then each individual official card; never guess N."""
    if venue not in LOCAL_BABA_CODES or date.fromisoformat(day).isoformat() != day:
        raise ValueError('LOCAL_DAY_IDENTITY_INVALID')
    if type(cutoff_seconds) is not int or not 120 <= cutoff_seconds <= 3600:
        raise ValueError('EXPLICIT_CUTOFF_SECONDS_REQUIRED')
    from runtime.family_authority_guard import resolve_current_authority
    authority = (authority_resolver or resolve_current_authority)(now=now)
    reads = []
    def read(spec):
        return read_official(spec, fetch=fetch, reads=reads, read_observer=read_observer, sleeper=sleeper)
    menu_url = _url('RaceList', LOCAL_BABA_CODES[venue], day.replace('-', '/'), 1)
    spec = {'source_id': f'NAR-{venue}-{day}-DAY-MENU', 'source_class': 'OFFICIAL_DAY_MENU',
            'authority': 'NAR_OFFICIAL', 'official': True, 'required': True,
            'url': menu_url, 'max_bytes': 900000}
    menu, errors = read(spec)
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
        card, errors = read(spec)
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
        normalized = {'race_card_tables': {'value': tables, 'source_id': card['source_id'],
                                           'snapshot_sha256': card['snapshot_sha256']}}
        odds_error = None
        try:
            odds, odds_errors = read(_odds_source(venue, LOCAL_BABA_CODES[venue],day.replace('-','/'),number))
            raw_html(odds)
            if odds_errors:
                raise ValueError(';'.join(odds_errors))
            normalized['odds_tables']={'value':odds.get('extracted_evidence',{}).get('odds_tables'),
                                      'source_id':odds['source_id'],'snapshot_sha256':odds['snapshot_sha256']}
            snapshots.append(odds)
        except Exception as exc:
            odds_error=str(exc)
        universe = enrich_source_artifact({'normalized_evidence': normalized})
        if not universe['declared_runner_universe']['runners']:
            raise ValueError('OFFICIAL_RUNNER_UNIVERSE_EMPTY')
        active_proven = not any(s['status']=='ACTIVE_DECLARED' for s in universe['runner_status_registry'])
        records.append({'race_key': f'{venue}-{d:%Y%m%d}-R{number:02d}-LIVE-R1',
                        'execution_id': request['execution_id'], 'fields': fields,
                        'current_authority_at_observation': request['current_authority_manifest'],
                        'required_numerical_manifest':authority[1]['common_family_components'].get('local_production_numerical_authority'),
                        'numerical_execution_status':'NOT_EXECUTED_REQUIRES_FRESH_SIGNED_SOURCE',
                        'request_intent_draft':request,
                        'intent_status':'DRAFT_NOT_FORMAL_STATIC_NOT_DISPATCHED',
                        'planned_dispatch_window':'DATED_OWNER_LEAD_AND_LOCAL_TIMING_EVIDENCE_REQUIRED',
                        'registration_status':'NOT_REGISTERED',
                        'declared_runner_universe': universe['declared_runner_universe'],
                        'observed_active_runner_universe': universe['active_runner_universe'] if active_proven else None,
                        'active_universe_status':'OFFICIAL_OBSERVATION_REQUIRES_DISPATCH_RECHECK' if active_proven else 'UNKNOWN_PENDING_FRESH_SIGNED_SOURCE',
                        'odds_observation_error':odds_error,
                        'runner_status_registry': universe['runner_status_registry'],
                        'source_basis_sha256': card['snapshot_sha256'],
                        'freeze': False, 'dispatch_requires_fresh_signed_source': True})
        snapshots.append(card)
    plan = {'family_id': 'LOCAL', 'venue_id': venue, 'race_date': day,
            'observed_at': now.isoformat(), 'races': records, 'official_snapshots': snapshots,
            'discovery_read_attempts':reads,
            'status': 'DISCOVERY_ONLY_NOT_REGISTERED_NOT_SIGNED_SOURCE', 'prediction_freeze': False}
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
            or not owner.get('enabled') or plan['venue_id'] not in owner.get('venues', [])
            or owner.get('family_authority_basis') != current['manifest_id']):
        raise ValueError('OWNER_SCOPE_SCHEDULE_OR_COST_APPROVAL_REQUIRED')
    selected = approval.get('race_numbers', [])
    available = {r['fields']['race_no'] for r in plan['races']}
    if (not selected or any(type(n) is not int for n in selected)
            or len(set(selected)) != len(selected) or not set(selected) <= available):
        raise ValueError('EXPLICIT_RACE_SUBSET_REQUIRED')
    phase = approval.get('activation_phase')
    if phase not in {'B', 'C', 'D'}:
        raise ValueError('EXPLICIT_ACTIVATION_PHASE_REQUIRED')
    if phase == 'B' and len(selected) != 1:
        raise ValueError('PHASE_B_SINGLE_RACE_REQUIRED')
    if phase == 'C' and not 2 <= len(selected) < len(available):
        raise ValueError('PHASE_C_LIMITED_MULTIPLE_RACES_REQUIRED')
    if phase in {'C', 'D'} and not approval.get('phase_b_acceptance_ref'):
        raise ValueError('PHASE_B_ACCEPTANCE_REQUIRED')
    if phase == 'D' and (set(selected) != available or not approval.get('phase_c_acceptance_ref')
                         or not approval.get('human_review_ref') or not approval.get('full_day_activation_ref')):
        raise ValueError('FULL_DAY_PROMOTION_APPROVAL_REQUIRED')
    cap = approval.get('max_dispatches')
    if type(cap) is not int or not 1 <= cap <= len(selected):
        raise ValueError('BOUNDED_DISPATCH_BUDGET_REQUIRED')
    # A dispatch count is not a monetary cap. Require a separately reviewed cost
    # control reference; this client cannot infer provider prices or free usage.
    if not approval.get('cost_control_ref'):
        raise ValueError('REVIEWED_PROVIDER_COST_CONTROL_REQUIRED')
    lead, margin = approval.get('start_lead_seconds'), approval.get('minimum_remaining_seconds')
    if type(lead) is not int or type(margin) is not int or not 1800 <= lead <= 7200 or not 300 <= margin < lead:
        raise ValueError('OWNER_DISPATCH_WINDOW_REQUIRED')
    if approval.get('preregister_authorized_races') is True and not approval.get('preregistration_approval_ref'):
        raise ValueError('PREREGISTRATION_OWNER_APPROVAL_REQUIRED')
    worker = approval.get('worker_seconds', 0)
    if (type(worker) is not int or not 0 <= worker <= 21000
            or worker and (approval.get('preregister_authorized_races') is not True
                           or not approval.get('worker_duration_approval_ref'))):
        raise ValueError('BOUNDED_WORKER_DURATION_APPROVAL_REQUIRED')
    return current['manifest_id']


def checkpoint_status(root, eid):
    """Observe existing stage storage without rerunning prediction or settlement."""
    from runtime.execution_store import resolve_phase
    latest = {}
    for phase in ('SOURCE', 'FORMAL', 'RESULT'):
        saved = resolve_phase(eid, phase, root=root/'runtime/executions')
        if saved is not None:
            latest[phase] = saved['latest']
    delivery = root/'runtime/execution_reports'/eid/'delivery/canonical_tree.txt'
    reports=[]
    from runtime.formal_failure_diagnostics import failure_class_for, resume_hint_for
    for path in sorted((root/'runtime/execution_reports'/eid).glob('*.json')):
        report=json.loads(path.read_text())
        if not isinstance(report, dict):
            raise ValueError('RACE_DIAGNOSTIC_OBJECT_REQUIRED:' + str(path.relative_to(root)))
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


def inspect_plan(root, plan, now):
    """Phase A: observe every race without authorization, dispatch, or verification POST."""
    if sha({k:v for k,v in plan.items() if k != 'plan_sha256'}) != plan.get('plan_sha256'):
        raise ValueError('DAY_PLAN_SHA_MISMATCH')
    from runtime.family_authority_guard import resolve_current_authority
    current = resolve_current_authority(root=root, now=now)[1]['manifest_id']
    rows = []
    for race in plan['races']:
        fields, eid = race['fields'], race['execution_id']
        try:
            existing = existing_race_refs(root, race)
            checkpoints = checkpoint_status(root, eid)
            error = None
        except (OSError, ValueError, KeyError, TypeError) as exc:
            existing, checkpoints, error = [], {}, str(exc)
        rows.append({'execution_id':eid, 'fields':fields,
                     'existing_refs':sorted(str(p.relative_to(root)) for p in existing),
                     'remaining_seconds':(datetime.fromisoformat(fields['prediction_cutoff'])-now).total_seconds(),
                     'observed_active_runner_universe':race.get('observed_active_runner_universe'),
                     'checkpoints':checkpoints, 'observation_error':error,
                     'live_eligibility':'NOT_EVALUATED_NO_AUTHORIZATION'})
    return {'phase':'A', 'status':'READ_ONLY_NO_LIVE_SEND', 'current_authority_manifest':current,
            'observed_at':now.isoformat(), 'plan_sha256':plan['plan_sha256'], 'target_races':len(rows),
            'races':rows, 'dispatch_count':0, 'new_signed_artifacts':0}


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


def existing_race_refs(root, race):
    """All revisions and aliases, including an owned preregistration key."""
    prefix = race['execution_id'].rsplit('-R1', 1)[0]
    refs = list((root/'runtime/executions').glob(prefix+'-R*'))
    refs += list((root/'runtime/formal_intents').glob(prefix+'-R*.json'))
    for key in (root/'runtime/race_key_requests').glob('*.json'):
        try:
            candidate = json.loads(key.read_text())
            if not isinstance(candidate, dict):
                raise ValueError('RACE_KEY_OBJECT_REQUIRED')
        except (ValueError, OSError):
            identity = re.fullmatch(r'([A-Z]{3})-(\d{8})-R(\d{2})-LIVE-R\d+', key.stem)
            expected = (race['fields']['venue_id'], race['fields']['race_date'].replace('-',''),
                        f"{int(race['fields']['race_no']):02d}")
            # A malformed identifiable sibling cannot be an accepted key. Hold
            # that sibling only; unidentified aliases remain conservatively HOLD.
            if identity and identity.groups() != expected:
                continue
            raise
        if all(str(candidate.get(k)) == str(race['fields'][k]) for k in ('venue_id','race_date','race_no')):
            refs.append(key)
    return refs


def canonical_day_index(root, plan, *, now, health=None, state=None):
    """Read-only LOCAL FINAL readback, with independent publication/arrival fields.

    The optional health must come from the canonical Gateway GET. Its current
    fingerprint is assessed here; keys embedded in envelopes are never trusted.
    No /verify POST, signing, notification or learning injection is performed.
    """
    if sha({k:v for k,v in plan.items() if k != 'plan_sha256'}) != plan.get('plan_sha256'):
        raise ValueError('DAY_PLAN_SHA_MISMATCH')
    from runtime.execution_gateway import assess_runtime_health
    from runtime.jra_ticket_tree_renderer import render_ticket_tree
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    trusted = health is not None and assess_runtime_health(health, 'LOCAL')['status'] == 'PASS'
    rows = []
    for race in plan['races']:
        eid, fields = race['execution_id'], race['fields']
        cell = ((state or {}).get('races') or {}).get(eid, {})
        row = {'execution_id':eid, **fields, 'discovered':True,
               'registration_status':cell.get('registration', {}).get('status', 'NOT_PROVEN'),
               'execution_status':cell.get('status', 'DISCOVERED'),
               'first_failure_observation':cell.get('first_failure_observation'),
               'final_generated':None, 'final_signed':False, 'final_signed_before_cutoff':False,
               'final_published_at':None, 'delivery_sent_at':None, 'delivery_acknowledged_at':None,
               'delivery_verified':False, 'recommendation_pfs':'N/A_NO_VERIFIED_FINAL',
               'actual_purchase_pfs':'UNKNOWN', 'next_race_consumption':'UNVERIFIED'}
        try:
            observation = checkpoint_status(root, eid)
            row['checkpoints'] = observation
            ref = observation['stages']['FINAL'].get('artifact_ref')
            if ref and trusted:
                envelope = json.loads((root/ref).read_text())
                receipt, artifact = envelope['receipt'], envelope['artifact']
                if (receipt.get('family') != 'LOCAL' or receipt.get('phase') != 'FINAL'
                        or receipt.get('status') != 'PASS' or receipt.get('errors')
                        or receipt.get('race_id') != eid or envelope.get('signature_alg') != 'Ed25519'
                        or envelope.get('signer_key_id') != health['receipt_signer_key_id']
                        or receipt.get('engine_sha256') != health['engine_sha256']
                        or receipt.get('parameter_map_sha256') != health['parameter_map_sha256']
                        or sha(receipt) != envelope['receipt_sha256']
                        or sha(artifact) != receipt['artifact_sha256']):
                    raise ValueError('CANONICAL_FINAL_IDENTITY_OR_HASH_MISMATCH')
                Ed25519PublicKey.from_public_bytes(base64.b64decode(health['receipt_public_key_b64'], validate=True)).verify(
                    base64.b64decode(envelope['signature'], validate=True),
                    json.dumps(receipt, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())
                signed = datetime.fromisoformat(receipt['timestamp'].replace('Z','+00:00'))
                frozen = datetime.fromisoformat(artifact['final_freeze_timestamp'].replace('Z','+00:00'))
                cutoff = datetime.fromisoformat(fields['prediction_cutoff'])
                if signed.tzinfo is None or frozen.tzinfo is None or not frozen <= signed <= now:
                    raise ValueError('CANONICAL_FINAL_CLOCK_INVALID')
                if signed >= cutoff or frozen >= cutoff:
                    row.update(final_generated=True, final_signed=True, final_signed_at=receipt['timestamp'])
                    raise ValueError('CANONICAL_FINAL_AFTER_CUTOFF_NOT_FORMAL_PRESTART')
                tree = render_ticket_tree(artifact)
                row.update(final_generated=True, final_signed=True, final_signed_at=receipt['timestamp'],
                           final_signed_before_cutoff=frozen < cutoff and signed < cutoff,
                           final_artifact_sha256=receipt['artifact_sha256'], final_receipt_sha256=envelope['receipt_sha256'],
                           canonical_tree=tree['text'], ticket_count=tree['ticket_count'],
                           total_investment=tree['total_investment'],
                           capital_decision=artifact.get('capital_policy_decision'),
                           recommendation_pfs='UNKNOWN_PENDING_VERIFIED_SETTLEMENT')
            elif ref:
                row['verification_status'] = 'HOLD_CANONICAL_HEALTH_REQUIRED'
        except Exception as exc:
            # InvalidSignature has an empty message; preserve the error type.
            row.update(verification_status='HOLD_READBACK', observation_error=f'{type(exc).__name__}:{exc}')
        rows.append(row)
    return {'family_id':'LOCAL', 'venue_id':plan['venue_id'], 'race_date':plan['race_date'],
            'observed_at':now.isoformat(), 'plan_sha256':plan['plan_sha256'],
            'target_races':len(rows), 'races':rows,
            'signed_final_before_cutoff_count':sum(r['final_signed_before_cutoff'] for r in rows),
            'delivery_verified_count':0, 'new_live_send':False,
            'publication_status':'LOCAL_INDEX_RENDER_ONLY_REMOTE_AVAILABILITY_UNVERIFIED'}


def owned_registration(root, race, cell, plan, current):
    registration = cell.get('registration', {})
    key = root/'runtime/race_key_requests'/(race['race_key']+'.json')
    return (registration.get('status') == 'REGISTERED_REQUEST_INTENT_NOT_FROZEN_STATIC'
            and registration.get('official_plan_sha256') == plan['plan_sha256']
            and registration.get('current_authority_manifest') == current
            and registration.get('fields_sha256') == sha(race['fields'])
            and registration.get('request_intent_sha256') == sha(registration.get('request_intent'))
            and key.exists() and json.loads(key.read_text()) == race['fields'])


def preregister_intakes(root, plan, approval, *, now):
    """JRA-style future intake, outside every live push-trigger directory.

    Reuse LOCAL authority, phase/subset, cost and canonical request guards.
    Registration does not dispatch SOURCE or freeze Static. The dated worker
    still claims/publishes through the existing race-day path at its own window.
    """
    root=Path(root)
    if (plan.get('family_id')!='LOCAL' or plan.get('venue_id')!='URW'
            or plan.get('plan_sha256')!=sha({k:v for k,v in plan.items() if k!='plan_sha256'})
            or now.tzinfo is None or now.astimezone(JST).date().isoformat()>plan['race_date']):
        raise ValueError('URW_PREREGISTRATION_PLAN_OR_DATE_INVALID')
    current=authorization(approval,plan,root,now)
    if (approval.get('preregister_authorized_races') is not True
            or not approval.get('preregistration_approval_ref')):
        raise ValueError('PREREGISTRATION_OWNER_APPROVAL_REQUIRED')
    selected=sorted(approval['race_numbers'])
    cohort={'family_id':'LOCAL','venue_id':'URW','race_date':plan['race_date'],
        'plan_sha256':plan['plan_sha256'],'race_numbers':selected,
        'current_authority_manifest':current,'approval_sha256':sha(approval)}
    cohort_sha=sha(cohort);pending=[];records=[]
    for race in plan['races']:
        fields=race['fields'];eid=race['execution_id']
        if fields['race_no'] not in selected:
            continue
        intent=build(fields,now=now)
        if intent['execution_id']!=eid or intent['current_authority_manifest']!=current:
            raise ValueError('PREREGISTRATION_IDENTITY_OR_AUTHORITY_MISMATCH')
        path=root/'runtime/local_race_registrations'/plan['race_date']/(eid+'.json')
        expected={'family_id':'LOCAL','venue_id':'URW','race_date':plan['race_date'],
            'race_no':fields['race_no'],'execution_id':eid,'plan_sha256':plan['plan_sha256'],
            'cohort_sha256':cohort_sha,'current_authority_manifest':current,
            'approval_sha256':sha(approval),'intake_intent':intent,
            'formal_status':'REGISTERED_AUTHORIZED_INTAKE_ONLY'}
        if path.exists():
            record=json.loads(path.read_text())
            if (record.get('sha256')!=sha({k:v for k,v in record.items() if k!='sha256'})
                    or any(record.get(k)!=v for k,v in expected.items())):
                raise ValueError('LOCAL_INTAKE_IMMUTABLE_BINDING_CONFLICT')
        else:
            if existing_race_refs(root,race):
                raise ValueError('EXISTING_RACE_REQUIRES_READBACK')
            record={**expected,'registered_at':now.isoformat(),
                'required_index_count':29,'planned_required_cells':29*len(race['declared_runner_universe']['runners']),
                'executed_cells':0,'fresh_signed_source_required':True,
                'active_runner_authority':'FRESH_SIGNED_RACE_DAY_SOURCE_REQUIRED',
                'source_executed':False,'static_frozen':False,'dispatch_acknowledged':False,
                'user_delivery_verified':False}
            record['sha256']=sha(record);pending.append((path,record))
        records.append(record)
    # Validate the complete approved cohort before writing any record.
    if len(records)!=len(selected):
        raise ValueError('LOCAL_INTAKE_APPROVED_COHORT_INCOMPLETE')
    for path,record in pending:
        write(path,record)
    return {'cohort':cohort,'cohort_sha256':cohort_sha,'discovered_count':len(plan['races']),
        'approved_target_count':len(selected),'registered_count':len(records),
        'registered_execution_ids':[r['execution_id'] for r in records],
        'runtime_posts':0,'dispatch_count':0,'source_executed':False}


def preregister(root, plan, approval, state, *, now, current, publish):
    """Persist approved request intents; never pretend they are frozen Static."""
    target = {'official_plan_sha256':plan['plan_sha256'],
              'approved_race_numbers':sorted(approval['race_numbers']),
              'current_authority_manifest':current}
    if state.get('registered_target') not in (None, target):
        raise ValueError('REGISTERED_TARGET_CHANGED_RECONCILIATION_REQUIRED')
    state['registered_target'] = target
    changed = False
    registered, missing = [], []
    for race in plan['races']:
        fields, eid = race['fields'], race['execution_id']
        if fields['race_no'] not in approval['race_numbers']:
            continue
        cell = state['races'].setdefault(eid, {})
        key = root/'runtime/race_key_requests'/(race['race_key']+'.json')
        try:
            intake=root/'runtime/local_race_registrations'/plan['race_date']/(eid+'.json')
            if intake.exists():
                record=json.loads(intake.read_text())
                if (record.get('sha256')!=sha({k:v for k,v in record.items() if k!='sha256'})
                        or record.get('execution_id')!=eid or record.get('plan_sha256')!=plan['plan_sha256']
                        or record.get('current_authority_manifest')!=current
                        or record.get('approval_sha256')!=sha(approval)
                        or record.get('intake_intent')!=build(fields,now=now)):
                    raise ValueError('LOCAL_INTAKE_IMMUTABLE_BINDING_CONFLICT')
            if not owned_registration(root,race,cell,plan,current):
                if cell.get('registration') or cell.get('claimed_at') or existing_race_refs(root,race) or key.exists():
                    raise ValueError('EXISTING_RACE_OR_REGISTRATION_REQUIRES_READBACK')
                request = build(fields, now=now)
                if request['execution_id'] != eid or request['current_authority_manifest'] != current:
                    raise ValueError('RACE_OR_AUTHORITY_BINDING_MISMATCH')
                cell['registration'] = {
                    'status':'REGISTERED_REQUEST_INTENT_NOT_FROZEN_STATIC',
                    'registered_at':now.isoformat(), 'official_plan_sha256':plan['plan_sha256'],
                    'current_authority_manifest':current, 'fields_sha256':sha(fields),
                    'request_intent':request, 'request_intent_sha256':sha(request),
                    'active_runner_status':'UNKNOWN_UNTIL_FRESH_SIGNED_SOURCE',
                    'owner_approval_ref':approval['preregistration_approval_ref']}
                write(key, fields)
                changed = True
            registered.append(eid)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            missing.append(eid)
            cell['registration_error'] = str(exc)
            cell.setdefault('first_failure_observation', {
                'stage':'PREREGISTRATION', 'code':str(exc), 'observed_at':now.isoformat()})
    state['registration_coverage'] = {
        **target, 'discovered_count':len(plan['races']),
        'approved_target_count':len(approval['race_numbers']),
        'registered_count':len(registered), 'registered_execution_ids':registered,
        'missing_execution_ids':missing, 'observed_at':now.isoformat(),
        'frozen_formal_intent_proven':False, 'signed_source_proven':False}
    if changed:
        publish()  # All owned keys + request intents, BEFORE any runtime handoff.


def tick(root, plan, approval, state, *, now, execute=False, authorize=authorization,
         health=runtime_ready, send=dispatch, publish=None, reconcile=reconcile_run, clock=None,
         only_execution_id=None):
    if sha({k:v for k,v in plan.items() if k != 'plan_sha256'}) != plan.get('plan_sha256'):
        raise ValueError('DAY_PLAN_SHA_MISMATCH')
    if now.tzinfo is None or now.astimezone(JST).date().isoformat() != plan['race_date']:
        raise ValueError('DISPATCH_REQUIRES_CURRENT_LOCAL_DAY')
    current = authorize(approval, plan, root, now)
    if only_execution_id is not None and (plan.get('venue_id') != 'URW' or
            only_execution_id not in {r['execution_id'] for r in plan['races']
                if r['fields']['race_no'] in approval['race_numbers']}):
        raise ValueError('CHAT_APPROVED_URW_EXECUTION_REQUIRED')
    if execute and publish is None:
        raise ValueError('DURABLE_CLAIM_PUBLISH_REQUIRED')
    state.setdefault('races', {})
    if execute and only_execution_id is None and approval.get('preregister_authorized_races') is True:
        preregister(root,plan,approval,state,now=now,current=current,publish=publish)
    for race in plan['races']:
        eid, fields = race['execution_id'], race['fields']
        if only_execution_id is not None and eid != only_execution_id:
            continue
        cell = state['races'].setdefault(eid, {})
        try:
            cell.update(checkpoint_status(root, eid))
        except (OSError, ValueError, KeyError, TypeError) as exc:
            # A corrupt race remains held; unrelated approved races keep their
            # own deadline. Never accept the broken pointer or reset its claim.
            cell.update(status='HOLD_CHECKPOINT_INTEGRITY', error=str(exc))
            cell.setdefault('first_failure_observation', {
                'stage':'CHECKPOINT_READBACK', 'code':str(exc), 'observed_at':now.isoformat()})
            continue
        if fields['race_no'] not in approval['race_numbers']:
            cell['status'] = 'NOT_AUTHORIZED_FOR_THIS_PHASE'
            continue
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
            if cell['stages']['FINAL']['status']=='NOT_OBSERVED' and now >= cutoff:
                cell['status']='FINAL_DEADLINE_EXPIRED'
                cell.setdefault('first_failure_observation', {
                    'stage':'SIGNED_FINAL_DEADLINE', 'code':'FINAL_NOT_OBSERVED_AT_OR_AFTER_CUTOFF',
                    'observed_at':now.isoformat(), 'cutoff':cutoff.isoformat()})
            continue
        # Check ALL same-race execution revisions, not only the expected R1.
        key = root/'runtime/race_key_requests'/f"{race['race_key']}.json"
        try:
            owned = owned_registration(root,race,cell,plan,current)
            existing = [ref for ref in existing_race_refs(root,race) if not (owned and ref == key)]
        except (OSError,ValueError,KeyError,TypeError) as exc:
            cell.update(status='HOLD_RACE_KEY_INTEGRITY', error=str(exc))
            cell.setdefault('first_failure_observation', {
                'stage':'RACE_KEY_READBACK', 'code':str(exc), 'observed_at':now.isoformat()})
            continue
        if existing or (key.exists() and not owned) or cell.get('registration_error'):
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
            cell.setdefault('first_failure_observation', {
                'stage':'DISPATCH_DEADLINE', 'code':'INSUFFICIENT_APPROVED_EXECUTION_WINDOW',
                'observed_at':now.isoformat(), 'cutoff':cutoff.isoformat()})
            continue
        if now < post-timedelta(seconds=approval['start_lead_seconds']):
            cell['status'] = 'WAIT_DISPATCH_WINDOW'
            continue
        if cell.get('preflight_attempts',0) >= 3:
            cell['status']='HOLD_PREFLIGHT_RETRY_LIMIT_OWNER_RECOVERY_REQUIRED'
            continue
        if cell.get('manual_recovery_required'):
            cell['status']='HOLD_GUARD_OWNER_RECOVERY_REQUIRED'
            continue
        if sum(bool(c.get('claimed_at')) for c in state['races'].values()) >= approval['max_dispatches']:
            cell['status'] = 'HOLD_DISPATCH_BUDGET_EXHAUSTED'
            continue
        try:
            request = build(fields, now=now)
            if request['execution_id'] != eid or request['current_authority_manifest'] != current:
                raise ValueError('RACE_OR_AUTHORITY_BINDING_MISMATCH')
            if owned and request != cell['registration']['request_intent']:
                raise ValueError('PREREGISTERED_INTENT_CHANGED_REVIEW_REQUIRED')
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
            # Only pre-send transport failures get bounded retry. A fingerprint,
            # authority or input mismatch is not a temporary unavailable server.
            from urllib.error import URLError, HTTPError
            retryable = (isinstance(exc,(TimeoutError,ConnectionError,URLError))
                         and (not isinstance(exc,HTTPError) or exc.code in {408,425,429,500,502,503,504}))
            from runtime.execution_gateway import ExecutionGatewayError, RETRYABLE_HTTP_STATUS
            match = re.match(r'^RUNTIME_HEALTH_HTTP_FAILED:(\d{3}):',str(exc))
            retryable |= isinstance(exc,ExecutionGatewayError) and bool(match) and int(match[1]) in RETRYABLE_HTTP_STATUS
            if not cell.get('claimed_at') and not retryable:
                cell['manual_recovery_required'] = True
            cell['retry_class'] = 'BOUNDED_PRE_SEND_TRANSPORT_ONLY' if retryable else 'HOLD_RECONCILE_OR_OWNER_REPAIR'
            cell.update(status='HOLD_AMBIGUOUS_DISPATCH_NO_AUTOMATIC_RETRY' if cell.get('claimed_at') else 'HOLD_PRE_DISPATCH',
                        error=str(exc), first_failure='ACTIONS_HANDOFF' if cell.get('claimed_at') else 'PRE_DISPATCH_GUARD')
            cell.setdefault('first_failure_observation', {
                'stage':cell['first_failure'], 'code':str(exc), 'observed_at':now.isoformat()})
            # Other races remain independent; no RESULT waiting in this driver.
    state.update(observed_at=now.isoformat(), plan_sha256=plan['plan_sha256'],
                 production_prediction_changed=False, chat_delivery_verified=False)
    return state


def run_worker(approval, step, *, clock=lambda:datetime.now(timezone.utc), sleep=time.sleep):
    """One existing dispatcher, bounded lease; no RESULT waits or self dispatch."""
    seconds = approval.get('worker_seconds', 0)
    if (type(seconds) is not int or not 0 <= seconds <= 21000
            or seconds and not approval.get('worker_duration_approval_ref')):
        raise ValueError('BOUNDED_WORKER_DURATION_APPROVAL_REQUIRED')
    end = clock() + timedelta(seconds=seconds)
    while True:
        state = step()
        pending = [c for c in state.get('races',{}).values()
                   if c.get('status') in {'WAIT_DISPATCH_WINDOW','HOLD_PRE_DISPATCH'}
                   and not c.get('manual_recovery_required') and not c.get('claimed_at')]
        remaining = (end-clock()).total_seconds()
        if not pending or remaining <= 0:
            return state
        sleep(min(60,remaining))


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


def south_kanto_day(root, day, cutoff_seconds, *, now, execute=False, fetch=fetch_source):
    """Resolve once, plan every held venue, then use existing dated workers.

    Planning never implies approval. Workers share one loop and strict Git
    publisher, rather than blocking behind a sibling's long lease or RESULT.
    """
    folder = root/'runtime/local_race_day_plan'
    index_path = root/'runtime/execution_reports'/('LOCAL-'+day)/'canonical_index.json'
    report = {'race_date':day, 'observed_at':now.isoformat(), 'venues':{},
              'live_execution_requested':execute, 'new_live_send':None if execute else False,
              'target_races':0, 'target_races_complete':False}
    if execute and os.environ.get('KM_LOCAL_AUTONOMOUS_ENABLED') != 'true':
        raise ValueError('OWNER_ACTIVATION_AND_DATED_APPROVAL_REQUIRED')
    meeting_reads = []
    try:
        meeting = discover_meetings(day, now=now, fetch=fetch, read_observer=meeting_reads.append)
        report['meeting'] = meeting
    except Exception as exc:
        report.update(status='HOLD_OFFICIAL_DISCOVERY', original_error=f'{type(exc).__name__}:{exc}', discovery_reads=meeting_reads)
        write(index_path, report)
        return report
    contexts = []
    for venue in meeting['venues']:
        name = day+'-'+venue
        plan_path, state_path = folder/(name+'.json'), folder/(name+'.state.json')
        approval_path = root/'profiles/local_autonomous_approvals'/(name+'.json')
        first_stop_stage = 'OFFICIAL_RACE_DISCOVERY_OR_PLAN_RECONCILIATION'
        try:
            approval = json.loads(approval_path.read_text()) if execute and approval_path.exists() else None
            fresh = discover(venue, day, approval.get('cutoff_seconds', cutoff_seconds) if approval else cutoff_seconds,
                             now=now, fetch=fetch)
            if plan_path.exists():
                plan = json.loads(plan_path.read_text())
                # Current official identity/time/universe drift requires review;
                # do not silently rewrite the plan SHA an Owner already approved.
                # A verified new GET has a new snapshot hash even when every
                # declared runner is unchanged. Compare declared CONTENT, not
                # those two derived provenance hashes. Both plans retain their
                # original hashes/raw evidence; only fresh signed SOURCE can
                # establish current ACTIVE runners and prestart evidence.
                def identity(r):
                    declared = {k:v for k,v in r['declared_runner_universe'].items()
                                if k not in {'source_snapshot_sha256', 'runner_universe_sha256'}}
                    return r['fields'], r['execution_id'], r['race_key'], declared
                if ((plan['venue_id'], plan['race_date']) != (venue, day)
                        or [identity(r) for r in plan['races']] != [identity(r) for r in fresh['races']]):
                    raise ValueError('OFFICIAL_DAY_PLAN_DRIFT_REVIEW_REQUIRED')
            else:
                plan = fresh
                write(plan_path, plan)
            state = json.loads(state_path.read_text()) if state_path.exists() else {}
            report['venues'][venue] = canonical_day_index(root, plan, now=now, state=state,
                                                         health=readback_health(root, plan))
            report['target_races'] += len(plan['races'])
            if execute:
                first_stop_stage = 'DATED_OWNER_AUTHORIZATION'
                if approval is None:
                    raise ValueError('DATED_OWNER_APPROVAL_REQUIRED')
                authorization(approval, plan, root, now)
                _, step = prepare_worker(root, plan, plan_path, state_path, approval_path)
                contexts.append((venue, approval, step, time.monotonic()))
        except Exception as exc:
            report['venues'].setdefault(venue, {}).update(status='HOLD',
                first_stop_stage=first_stop_stage,
                original_error=f'{type(exc).__name__}:{exc}', formal_registration_proven=False)
    report['target_races_complete'] = all('races' in v for v in report['venues'].values())
    report['status'] = 'READ_ONLY_DISCOVERY' if not execute else 'GATED_EXECUTION_OBSERVATION'
    write(index_path, report)
    while contexts:
        pending = []
        for venue, approval, step, started in contexts:
            try:
                state = step()
                venue_index = root/'runtime/execution_reports'/('LOCAL-'+day)/(venue+'.json')
                report['venues'][venue] = json.loads(venue_index.read_text())
                report['venues'][venue]['worker_state'] = state
                # Each venue retains its OWN reviewed duration and race budget.
                if (time.monotonic()-started < approval.get('worker_seconds', 0)
                        and any(c.get('status') in {'WAIT_DISPATCH_WINDOW','HOLD_PRE_DISPATCH'}
                            and not c.get('manual_recovery_required') and not c.get('claimed_at')
                            for c in state.get('races',{}).values())):
                    pending.append((venue, approval, step, started))
            except Exception as exc:
                report['venues'][venue].update(status='HOLD_WORKER', original_error=f'{type(exc).__name__}:{exc}')
        write(index_path, report)
        contexts = pending
        if contexts:
            time.sleep(min(60, max(0, min(a.get('worker_seconds',0)-(time.monotonic()-s) for _,a,_,s in contexts))))
    return report


def readback_health(root, plan):
    if any((root/'runtime/executions'/r['execution_id']/'FORMAL/LATEST.json').exists() for r in plan['races']):
        try:
            from runtime.execution_gateway import family_config, fetch_health
            return fetch_health(family_config('LOCAL')['external_endpoint'])
        except Exception:
            pass
    return None


def prepare_worker(root, plan, plan_path, state_path, approval_path, *, only_execution_id=None):
    approval = json.loads(approval_path.read_text())
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    paths = [str(plan_path.relative_to(root)), str(state_path.relative_to(root)), 'runtime/race_key_requests']
    index_path = root/'runtime/execution_reports'/('LOCAL-'+plan['race_date'])/(plan['venue_id']+'.json')
    def publish():
        write(state_path, state)
        health = readback_health(root, plan)
        write(index_path, canonical_day_index(root, plan, now=datetime.now(timezone.utc), health=health, state=state))
        delivery_paths=[str(p.relative_to(root)) for r in plan['races']
                        if (p:=root/'runtime/execution_reports'/r['execution_id']/'delivery').exists()]
        publish_state(root, paths+delivery_paths+[str(index_path.relative_to(root))])
        if sha(json.loads(approval_path.read_text())) != sha(approval):
            raise ValueError('OWNER_APPROVAL_CHANGED_DURING_WORKER')
        if json.loads(plan_path.read_text()) != plan:
            raise ValueError('DAY_PLAN_CHANGED_DURING_WORKER')
    def step():
        current_approval = json.loads(approval_path.read_text())
        if sha(current_approval) != sha(approval):
            raise ValueError('OWNER_APPROVAL_CHANGED_DURING_WORKER')
        tick(root,plan,current_approval,state,now=datetime.now(timezone.utc),execute=True,
             publish=publish,clock=lambda:datetime.now(timezone.utc),only_execution_id=only_execution_id)
        publish()
        return state
    return approval, step


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root', default=str(ROOT))
    scope = p.add_mutually_exclusive_group(required=True)
    scope.add_argument('--venue', choices=sorted(LOCAL_BABA_CODES))
    scope.add_argument('--south-kanto', action='store_true')
    p.add_argument('--date', required=True)
    p.add_argument('--cutoff-seconds', required=True, type=int)
    p.add_argument('--execute', action='store_true')
    p.add_argument('--preregister-only', action='store_true',help='URW authorized future intake only; never dispatch')
    args = p.parse_args()
    root, now = Path(args.repo_root).resolve(), datetime.now(timezone.utc)
    if args.preregister_only and (args.execute or args.south_kanto or args.venue!='URW'):
        raise ValueError('PREREGISTER_ONLY_ONE_URW_PLAN_NO_DISPATCH')
    if args.south_kanto:
        report = south_kanto_day(root,args.date,args.cutoff_seconds,now=now,execute=args.execute)
        print(json.dumps(report))
        # An Actions green exit is not FINAL proof; explicit discovery/worker
        # HOLD must nevertheless alert the caller after preserving its evidence.
        return int(not report['target_races_complete'] or any(
            v.get('status','').startswith('HOLD') for v in report['venues'].values()))
    name = args.date+'-'+args.venue
    folder = root/'runtime/local_race_day_plan'
    plan_path, state_path = folder/(name+'.json'), folder/(name+'.state.json')
    approval_path = root/'profiles/local_autonomous_approvals'/(name+'.json')
    if (args.execute or args.preregister_only) and (os.environ.get('KM_LOCAL_AUTONOMOUS_ENABLED') != 'true' or not approval_path.exists()):
        raise ValueError('OWNER_ACTIVATION_AND_DATED_APPROVAL_REQUIRED')
    discovery_reads = []
    try:
        plan = json.loads(plan_path.read_text()) if plan_path.exists() else discover(
            args.venue,args.date,args.cutoff_seconds,now=now,read_observer=discovery_reads.append)
    except (OSError,ValueError,KeyError,TypeError) as exc:
        failure_path = folder/(name+'.discovery-failure.json')
        write(failure_path, {
            'status':'HOLD_OFFICIAL_DISCOVERY', 'first_stop_stage':'OFFICIAL_DISCOVERY',
            'observed_at':datetime.now(timezone.utc).isoformat(), 'original_error':str(exc),
            'attempts':discovery_reads, 'race_registration_proven':False, 'dispatch_count':0})
        if args.execute:
            try:
                publish_state(root,[str(failure_path.relative_to(root))])
            except Exception as persistence_error:
                # The original failure remains available to the workflow's
                # always-uploaded artifact even if Git persistence also fails.
                print('DISCOVERY_FAILURE_PERSISTENCE_HOLD:'+str(persistence_error))
        raise
    if (plan['venue_id'],plan['race_date']) != (args.venue,args.date):
        raise ValueError('DAY_PLAN_IDENTITY_MISMATCH')
    write(plan_path, plan)
    if args.preregister_only:
        report=preregister_intakes(root,plan,json.loads(approval_path.read_text()),now=now)
        write(folder/(name+'.intake-registration.json'),report)
        print(json.dumps(report))
        return 0
    if not args.execute:
        report = inspect_plan(root, plan, now)
        write(folder/(name+'.dry-run.json'), report)
        print(json.dumps(report))
        return
    approval, step = prepare_worker(root, plan, plan_path, state_path, approval_path)
    run_worker(approval,step)


if __name__ == '__main__':
    raise SystemExit(main())
