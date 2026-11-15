"""Bounded private NAR CSV capture; no Provider licence or SOURCE authority grant.

The pinned private binding supplies a ProviderBinding and a rights verifier.
This module supplies the transport: existing robots enforcement, one original
GET, no redirect/retry, and unchanged reference parsing. No default binding,
credential discovery, signature, numeric Consumer or model is installed.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import fcntl
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import signal
import threading
import urllib.error
import urllib.request
import zipfile

from runtime import local_fnb_multisource as multisource
from runtime.local_nar_csv_reference import inspect_zip
from runtime.local_physical.source_acquisition import (
    SOURCE_USER_AGENT, _source_access_policy, validate_public_url,
)
from runtime.urw_nankan_reference_source import immutable, private_directory, private_lock

PROFILE = 'KM-FNB-NAR-CSV-ONEOFF-REFERENCE-ACTOR-v0.1-20261103'
DAILY_URL = 'https://www.keiba.go.jp/KeibaWeb/DataDownload/RaceDataDownload?type=daily'
MAX_BYTES = 4_000_000  # Preserve the existing multisource admission limit.
MAX_SECONDS = 120
MAX_UNCOMPRESSED = 32_000_000
MAX_MEMBER = 16_000_000


class CaptureHold(ValueError):
    pass


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()


def _now():
    return datetime.now(timezone.utc)


@contextmanager
def _wall_budget():
    # Railway/Work Linux CLI: bound even a slow body stream or a private
    # callback. A Python thread timeout would leave a downloading thread alive.
    if threading.current_thread() is not threading.main_thread() or not hasattr(signal, 'setitimer'):
        raise CaptureHold('CSV_CAPTURE_MAIN_THREAD_TIMER_REQUIRED')
    if signal.getitimer(signal.ITIMER_REAL)[0]:
        raise CaptureHold('CSV_CAPTURE_EXISTING_TIMER_CONFLICT')
    previous = signal.getsignal(signal.SIGALRM)
    def expired(signum, frame):
        raise CaptureHold('CSV_CAPTURE_WALL_TIME_LIMIT')
    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, MAX_SECONDS)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def _load_binding(path, expected):
    path = Path(path)
    private_directory(path.parent)
    if (path.is_symlink() or not path.is_file() or path.stat().st_mode & 0o077
            or not re.fullmatch('[0-9a-f]{64}', str(expected))):
        raise CaptureHold('CSV_CAPTURE_PRIVATE_PINNED_BINDING_REQUIRED')
    raw = path.read_bytes()
    if _sha(raw) != expected:
        raise CaptureHold('CSV_CAPTURE_BINDING_SHA_MISMATCH')
    scope = {'__name__': '_km_csv_capture_' + expected, '__file__': str(path)}
    # This is expressly trusted private code, like FNB_PRODUCERS.py, not a
    # sandbox for an untrusted page or an intent-supplied Python expression.
    exec(compile(raw, str(path), 'exec'), scope)
    factory = scope.get('get_capture_binding')
    if not callable(factory):
        raise CaptureHold('CSV_CAPTURE_BINDING_FACTORY_REQUIRED')
    result = factory()
    if (not isinstance(result, dict) or not isinstance(result.get('provider'), multisource.ProviderBinding)
            or not callable(result.get('verify_rights'))):
        raise CaptureHold('CSV_CAPTURE_PROVIDER_AND_RIGHTS_VERIFIER_REQUIRED')
    if result.get('encoding') not in {'utf-8', 'utf-8-sig', 'cp932'} or result.get('header_mode') not in {'present', 'absent'}:
        raise CaptureHold('CSV_CAPTURE_EXPLICIT_ENCODING_HEADER_REQUIRED')
    return result


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise CaptureHold('CSV_CAPTURE_REDIRECT_NOT_ALLOWED')


def _archive_facts(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        members = archive.infolist()
        if (not 1 <= len(members) <= 4 or sum(x.file_size for x in members) > MAX_UNCOMPRESSED
                or any(x.file_size > MAX_MEMBER or x.flag_bits & 1 for x in members)):
            raise CaptureHold('CSV_CAPTURE_ARCHIVE_RESOURCE_LIMIT')
        if archive.testzip() is not None:
            raise CaptureHold('CSV_CAPTURE_ZIP_CRC_FAILURE')
        return [{'name': x.filename, 'bytes': x.file_size, 'compressed_bytes': x.compress_size,
                 'crc32': format(x.CRC, '08x')} for x in members]


def capture(*, binding_path, binding_sha256, actor_id, intent, private_root, execution_id, clock=_now):
    """Execute one explicitly qualified reference capture; retain private originals.

    Rights-verifier output is evidence from the separately trusted binding,
    never approval invented by this CLI. Provider/scope/period checks run again
    through acquire() after transport. Failures retain a consumed claim and
    cannot silently retry the same execution ID.
    """
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        raise CaptureHold('CSV_CAPTURE_PUBLIC_CI_DISABLED')
    with _wall_budget():
        return _capture(binding_path=binding_path, binding_sha256=binding_sha256,
                        actor_id=actor_id, intent=intent, private_root=private_root,
                        execution_id=execution_id, clock=clock)


def _capture(*, binding_path, binding_sha256, actor_id, intent, private_root, execution_id, clock):
    if not re.fullmatch('[A-Za-z0-9_-]{1,100}', str(execution_id)):
        raise CaptureHold('CSV_CAPTURE_EXECUTION_ID_REQUIRED')
    multisource.race_identity(intent)
    if intent.get('source_url', DAILY_URL) != DAILY_URL:
        raise CaptureHold('CSV_CAPTURE_OBSERVED_DAILY_URL_REQUIRED')
    root = private_directory(private_root)
    bound = _load_binding(binding_path, binding_sha256)
    provider = bound['provider']
    if provider.provider != 'NAR_OFFICIAL' or provider.exact_urls != (DAILY_URL,):
        raise CaptureHold('CSV_CAPTURE_EXACT_PROVIDER_URL_REQUIRED')
    code_sha = _sha(Path(__file__).read_bytes())
    if provider.code_sha256 != code_sha:
        raise CaptureHold('CSV_CAPTURE_TRANSPORT_CODE_PIN_REQUIRED')
    start = multisource.stamp(clock())
    if intent.get('prediction_cutoff') and start >= multisource.stamp(intent['prediction_cutoff']):
        raise CaptureHold('CSV_CAPTURE_CUTOFF_EXPIRED')
    holder = {}
    effective = replace(provider, fetch=lambda **_: None, parse=lambda **_: None, qualified_field_rules={})
    expected = {'passed': True, 'provider': provider.provider, 'source_url': DAILY_URL,
        'method': 'GET', 'actor_id': actor_id, 'permission_ref': provider.permission_ref,
        'permission_sha256': provider.permission_sha256, 'transport_code_sha256': code_sha,
        'automated_get_admitted': True, 'private_retention_admitted': True,
        'cloud_processing_admitted': True}
    def qualify(at):
        multisource._binding(effective, DAILY_URL, actor_id, at)
        if intent.get('prediction_cutoff') and at >= multisource.stamp(intent['prediction_cutoff']):
            raise CaptureHold('CSV_CAPTURE_CUTOFF_EXPIRED')
        rights = bound['verify_rights'](provider=provider.provider, source_url=DAILY_URL,
            method='GET', actor_id=actor_id, permission_ref=provider.permission_ref,
            permission_sha256=provider.permission_sha256, transport_code_sha256=code_sha, now=at)
        if (not isinstance(rights, dict) or any(rights.get(k) != v for k, v in expected.items())
                or any(rights.get(k) is not True for k in ('passed', 'automated_get_admitted',
                    'private_retention_admitted', 'cloud_processing_admitted'))):
            raise CaptureHold('CSV_CAPTURE_PROVIDER_RIGHTS_NOT_VERIFIED')
        # The verifier itself may take time. Do not rely on its earlier clock.
        checked = multisource.stamp(clock())
        multisource._binding(effective, DAILY_URL, actor_id, checked)
        if intent.get('prediction_cutoff') and checked >= multisource.stamp(intent['prediction_cutoff']):
            raise CaptureHold('CSV_CAPTURE_CUTOFF_EXPIRED')
        return checked
    qualify(start)
    lock = private_lock(root/'NAR_CSV_CAPTURE.lock')
    try:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        claim = root/(execution_id + '.claim.json')
        try:
            fd = os.open(claim, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        except FileExistsError as exc:
            raise CaptureHold('CSV_CAPTURE_EXECUTION_ALREADY_CLAIMED') from exc
        with os.fdopen(fd, 'wb') as stream:
            stream.write(_encoded({'execution_id': execution_id, 'binding_sha256': binding_sha256,
                'actor_id': actor_id, 'started_at': start.isoformat(), 'source_url': DAILY_URL}))

        def transport(*, url, intent, now):
            holder['stage'] = 'ACCESS_POLICY'
            validate_public_url(url)
            state_path = root/'NAR_CSV_LAST_TARGET.json'
            if state_path.is_symlink():
                raise CaptureHold('CSV_CAPTURE_RATE_STATE_SYMLINK')
            if state_path.exists():
                state = json.loads(state_path.read_text())
                if state.get('server_backoff_requires_review'):
                    raise CaptureHold('CSV_CAPTURE_SERVER_BACKOFF_REVIEW_REQUIRED')
                last = multisource.stamp(state['target_attempt_at'])
                eligible = max(last + timedelta(seconds=120),
                    multisource.stamp(state.get('next_eligible_at', (last + timedelta(seconds=120)).isoformat())))
                if multisource.stamp(clock()) < eligible:
                    raise CaptureHold('CSV_CAPTURE_DAILY_RATE_LIMIT')
            policy = _source_access_policy(url, timeout=30)
            if policy.get('automatic_access_allowed') is not True:
                raise CaptureHold('CSV_CAPTURE_ROBOTS_ALLOW_REQUIRED')
            # Policy/DNS/rate waiting may have crossed a rights/cutoff boundary.
            holder['stage'] = 'PRE_GET_QUALIFICATION'
            qualify(multisource.stamp(clock()))
            attempted = multisource.stamp(clock())
            def rate_state(backoff_seconds=0, response_at=None):
                until = attempted + timedelta(seconds=120)
                review = not math.isfinite(backoff_seconds) or backoff_seconds > 31_536_000
                if response_at is not None and not review:
                    until = max(until, response_at + timedelta(seconds=max(0, backoff_seconds)))
                state_raw = _encoded({'target_attempt_at': attempted.isoformat(),
                    'next_eligible_at': until.isoformat(), 'server_backoff_requires_review': review})
                temp = root/(execution_id + '.rate-state.tmp')
                immutable(temp, state_raw)
                os.replace(temp, state_path)
            rate_state()
            req = urllib.request.Request(url, headers={'User-Agent': SOURCE_USER_AGENT,
                'Accept': 'application/zip', 'Accept-Encoding': 'identity'}, method='GET')
            # File persistence above must not turn a just-expired right into
            # a network attempt. No blocking callback follows this boundary.
            final_at = multisource.stamp(clock())
            multisource._binding(effective, url, actor_id, final_at)
            if intent.get('prediction_cutoff') and final_at >= multisource.stamp(intent['prediction_cutoff']):
                raise CaptureHold('CSV_CAPTURE_CUTOFF_EXPIRED')
            holder['stage'] = 'TARGET_GET'
            try:
                response = urllib.request.build_opener(_NoRedirect()).open(req, timeout=30)
            except urllib.error.HTTPError as exc:
                from runtime.local_physical.source_acquisition import _http_backoff_seconds
                holder['http_status'] = exc.code
                # Persist server backoff across manually named executions.
                rate_state(_http_backoff_seconds({k.lower(): v for k, v in (exc.headers or {}).items()}), multisource.stamp(clock()))
                raise
            with response:
                holder['http_status'] = response.status
                holder['received_bytes'] = 0
                if (response.status != 200 or response.geturl() != url
                        or str(response.headers.get('content-type', '')).split(';', 1)[0].strip().lower() != 'application/zip'
                        or str(response.headers.get('content-encoding', 'identity')).lower() not in {'', 'identity'}):
                    raise CaptureHold('CSV_CAPTURE_ORIGINAL_ZIP_HTTP_REQUIRED')
                holder['stage'] = 'TARGET_BODY_READ'
                holder['received_bytes'] = None  # A failed read may have consumed an unknown prefix.
                raw = response.read(MAX_BYTES + 1)
                holder.update(received_bytes=len(raw), body_read_completed=True,
                              raw_truncated=len(raw) > MAX_BYTES)
                if not raw or len(raw) > MAX_BYTES:
                    raise CaptureHold('CSV_CAPTURE_RAW_BYTE_LIMIT')
                captured = multisource.stamp(clock()).isoformat()
                holder.update(raw=raw, captured_at=captured)
                # Retain actual HTTP bytes even when CRC/schema inspection
                # fails. This is a private forensic original, not admission.
                immutable(root/(_sha(raw) + '.raw'), raw)
                holder['raw_saved'] = True
                holder['stage'] = 'ZIP_CRC'
                holder.update(raw=raw, captured_at=captured, archive=_archive_facts(raw),
                    headers={k: response.headers.get(k) for k in ('content-type', 'last-modified', 'etag', 'date')})
                return {'raw': raw, 'http_status': 200, 'final_url': url,
                    'retrieval_method': 'HTTPS_GET_ORIGINAL_RESPONSE', 'captured_at': captured,
                    'content_type': 'application/zip', 'access_policy': {**policy, 'decision': 'ALLOW'}}

        def parse(*, raw, url, content_type):
            holder['stage'] = 'CSV_PARSE'
            meta = {'provider': 'NAR_OFFICIAL_CSV', 'http_status': 200, 'source_url': url,
                'retrieval_method': 'AUTHORIZED_HTTP_GET', 'captured_at': holder['captured_at'],
                'raw_sha256': _sha(raw), 'usage_qualification': expected}
            parsed = inspect_zip(raw, capture=meta, race=intent, encoding=bound['encoding'],
                                 header_mode=bound['header_mode'], now=clock())
            holder['parsed'] = parsed
            fields = [{'runner_number': row['runner_number'], 'field': 'csv.' + field,
                'value': value, 'effective_at': holder['captured_at'],
                'effective_time_kind': 'CAPTURE_TIME_NOT_OFFICIAL_EVENT_TIME',
                'provenance': row['field_provenance'][field]}
                for row in parsed['runners'] for field, value in row['prestart_reference_fields'].items()]
            return {'identity': parsed['race_identity'], 'encoding': bound['encoding'], 'fields': fields}

        effective = replace(effective, fetch=transport, parse=parse)
        try:
            packet = multisource.acquire(effective, url=DAILY_URL, intent=intent,
                actor_id=actor_id, now=start, private_root=root, clock=clock)
            parsed_bytes = _encoded(holder['parsed'])
            parsed_path = root/(_sha(parsed_bytes) + '.parsed.json')
            immutable(parsed_path, parsed_bytes)
            receipt = {'profile': PROFILE, 'status': 'PRIVATE_REFERENCE_CAPTURED_AND_PARSED',
                'execution_id': execution_id, 'actor_id': actor_id,
                'binding_sha256': binding_sha256, 'transport_code_sha256': code_sha,
                'provider_rights_verification': expected, 'raw_sha256': packet['raw_sha256'],
                'raw_bytes': packet['raw_bytes'], 'captured_at': packet['captured_at'],
                'source_url': DAILY_URL, 'archive_crc_verified': True, 'archive': holder['archive'],
                'response_headers': holder['headers'], 'parsed_reference_sha256': _sha(parsed_bytes),
                'multisource_receipt_sha256': packet['sha256'],
                'race_identity': holder['parsed']['race_identity'],
                'horse_count': holder['parsed']['parsed_horse_rows'],
                'formal_source_admitted': False, 'signed_source_claim': False,
                'active_universe_verified': False, 'numerical_consumption_authorized': False,
                'registered_oos_increment': 0, 'external_store_get_verified': False,
                'local_raw_readback_sha_verified':
                    _sha((root/(packet['raw_sha256'] + '.raw')).read_bytes()) == packet['raw_sha256']}
            receipt['sha256'] = multisource.sha(receipt)
            immutable(root/(execution_id + '.capture.json'), _encoded(receipt))
            return receipt
        except Exception as exc:
            code = str(exc).partition(':')[0]
            if not re.fullmatch('[A-Z][A-Z0-9_]{0,119}', code):
                code = 'CSV_CAPTURE_PRIVATE_EXECUTION_FAILED'
            immutable(root/(execution_id + '.hold.json'), _encoded({'profile': PROFILE,
                'execution_id': execution_id, 'status': 'HOLD', 'reason': code,
                'first_failed_stage': holder.get('stage', 'ACQUISITION_VERIFICATION'),
                'raw_sha256': _sha(holder['raw']) if holder.get('raw') else None,
                'raw_bytes': len(holder.get('raw', b'')),
                'original_raw_bytes_saved': len(holder['raw']) if holder.get('raw_saved') else 0,
                'received_bytes': holder.get('received_bytes'),
                'raw_truncated': holder.get('raw_truncated'),
                'body_read_completed': holder.get('body_read_completed', False),
                'http_status': holder.get('http_status'),
                'captured_at': holder.get('captured_at'),
                'formal_source_admitted': False, 'registered_oos_increment': 0}))
            raise
    finally:
        lock.close()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binding', required=True)
    p.add_argument('--binding-sha256', required=True)
    p.add_argument('--actor-id', required=True)
    p.add_argument('--intent', required=True)
    p.add_argument('--private-root', required=True)
    p.add_argument('--execution-id', required=True)
    args = p.parse_args(argv)
    try:
        result = capture(binding_path=args.binding, binding_sha256=args.binding_sha256,
            actor_id=args.actor_id, intent=json.loads(Path(args.intent).read_text()),
            private_root=args.private_root, execution_id=args.execution_id)
        print(json.dumps({'status': result['status'], 'receipt_sha256': result['sha256'],
                          'formal_source_admitted': False}))
        return 0
    except Exception as exc:
        code = str(exc).partition(':')[0]
        if not re.fullmatch('[A-Z][A-Z0-9_]{0,119}', code):
            code = 'CSV_CAPTURE_PRIVATE_EXECUTION_FAILED'
        print(json.dumps({'status': 'HOLD', 'reason': code, 'formal_source_admitted': False}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
