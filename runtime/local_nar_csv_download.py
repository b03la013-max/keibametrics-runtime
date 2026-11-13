"""Download the specifically offered official CSV archive for private research.

This capability records an actual limited-use basis; it does not issue a licence,
SOURCE signature, Consumer grant, final Active set or cloud-permission claim.
Only exact offered URLs pinned by the private usage record are accepted. It
never requests forbidden HTML paths, changes hosts/UAs, redirects or retries.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import io
import json
import os
from pathlib import Path
import re
import signal
import threading
import urllib.request
import zipfile

DAILY_URL = 'https://www.keiba.go.jp/KeibaWeb/DataDownload/RaceDataDownload?type=daily'
MONTHLY_URL = 'https://www.keiba.go.jp/KeibaWeb/DataDownload/RaceDataDownload?k_month=11&k_year=2026&type=monthly'
DAILY_ODDS_URL = 'https://www.keiba.go.jp/KeibaWeb/DataDownload/OddsDataDownload?type=daily'
LIMITS = {'daily': 120, 'monthly': 86400, 'daily_odds': 120}
MAX_BYTES = 4_000_000
MAX_UNCOMPRESSED = 32_000_000
MAX_SECONDS = 45
PROFILE = 'KM-NAR-OFFERED-CSV-PRIVATE-DOWNLOAD-v1'
SUSPENSION_FILENAME = 'OFFERED_CSV_SOURCE_SUSPENSION_CURRENT.json'


class DownloadHold(ValueError):
    pass


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _now():
    return datetime.now(timezone.utc)


def _stamp(value):
    dt = value if isinstance(value, datetime) else datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise DownloadHold('OFFERED_CSV_AWARE_TIME_REQUIRED')
    return dt.astimezone(timezone.utc)


def _bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()


def _private(root):
    root = Path(root)
    if root.is_symlink():
        raise DownloadHold('OFFERED_CSV_PRIVATE_ROOT_REQUIRED')
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    if root.stat().st_mode & 0o077:
        raise DownloadHold('OFFERED_CSV_PRIVATE_ROOT_REQUIRED')
    return root


def _immutable(path, raw):
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        if path.is_symlink() or path.read_bytes() != raw:
            raise DownloadHold('OFFERED_CSV_IMMUTABLE_CONFLICT')
    else:
        with os.fdopen(fd, 'wb') as file:
            file.write(raw)
            file.flush()
            os.fsync(file.fileno())


def _assert_not_suspended(*directories):
    """A current private stop record overrides older limited-use evidence.

    Any record presence is fail-closed, including a broken symlink or malformed
    record. It cannot expire or be waived by caller flags/clock manipulation.
    Originals and old captures remain available through ordinary file readback.
    """
    for directory in directories:
        marker = Path(directory) / SUSPENSION_FILENAME
        if marker.exists() or marker.is_symlink():
            raise DownloadHold('OFFERED_CSV_SOURCE_SUSPENDED:' + str(marker))


def verify_usage_record(path, expected_sha256, url):
    """Verify pinned evidence and exact capability, without broader rights flags."""
    path = Path(path)
    _assert_not_suspended(path.parent)
    if path.is_symlink() or not re.fullmatch('[0-9a-f]{64}', str(expected_sha256)):
        raise DownloadHold('OFFERED_CSV_USAGE_PIN_REQUIRED')
    raw = path.read_bytes()
    if _sha(raw) != expected_sha256:
        raise DownloadHold('OFFERED_CSV_USAGE_SHA_MISMATCH')
    record = json.loads(raw)
    if (record.get('schema') != 'KM-NAR-OFFERED-CSV-PRIVATE-USE-EVIDENCE-v1'
            or record.get('provider') != 'NAR_OFFICIAL'
            or url not in record.get('observed_endpoints', {}).values()
            or not record.get('owner_instruction_ref')
            or record.get('scope_assessment', {}).get('third_party_redistribution') is not False
            or record.get('scope_assessment', {}).get('formal_source_signing') is not False):
        raise DownloadHold('OFFERED_CSV_USAGE_SCOPE_MISMATCH')
    evidence = record.get('published_basis', [])
    for item in evidence:
        name = item.get('path', '')
        if not name or Path(name).name != name:
            raise DownloadHold('OFFERED_CSV_EVIDENCE_PATH_REQUIRED')
        original = path.parent / name
        if original.is_symlink() or _sha(original.read_bytes()) != item.get('sha256'):
            raise DownloadHold('OFFERED_CSV_EVIDENCE_SHA_MISMATCH')
    if {x.get('url') for x in evidence} != {
            'https://www.keiba.go.jp/pdf/manual/data_pdf_manual.pdf',
            'https://www.keiba.go.jp/terms.html'}:
        raise DownloadHold('OFFERED_CSV_MANUAL_AND_TERMS_REQUIRED')
    return record


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise DownloadHold('OFFERED_CSV_REDIRECT_NOT_ALLOWED')


@contextmanager
def _wall_budget():
    if threading.current_thread() is not threading.main_thread() or signal.getitimer(signal.ITIMER_REAL)[0]:
        raise DownloadHold('OFFERED_CSV_MAIN_THREAD_UNOCCUPIED_TIMER_REQUIRED')
    previous = signal.getsignal(signal.SIGALRM)
    def expire(*_):
        raise DownloadHold('OFFERED_CSV_TOTAL_TIME_LIMIT')
    signal.signal(signal.SIGALRM, expire)
    signal.setitimer(signal.ITIMER_REAL, MAX_SECONDS)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def download_csv(*, period, private_root, usage_path, usage_sha256, clock=_now, opener=None):
    """One original GET or exact cache readback under a durable cadence ledger.

    Failed requests consume the period reservation too. Cache reuse preserves
    original capture/update time and cannot masquerade as a fresh capture.
    Shared private_root is required across all Races and processes.
    """
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        raise DownloadHold('OFFERED_CSV_PUBLIC_CI_DISABLED')
    if period not in LIMITS:
        raise DownloadHold('OFFERED_CSV_PERIOD_REQUIRED')
    _assert_not_suspended(private_root, Path(usage_path).parent)
    url = {'daily': DAILY_URL, 'monthly': MONTHLY_URL, 'daily_odds': DAILY_ODDS_URL}[period]
    usage = verify_usage_record(usage_path, usage_sha256, url)
    root = _private(private_root)
    lock_path = root / 'offered_csv.lock'
    if lock_path.is_symlink():
        raise DownloadHold('OFFERED_CSV_PRIVATE_LOCK_REQUIRED')
    with open(lock_path, 'a+b') as lock:
        os.chmod(lock_path, 0o600)
        fcntl.flock(lock, fcntl.LOCK_EX)
        state_path = root / 'offered_csv_ledger.json'
        if state_path.is_symlink():
            raise DownloadHold('OFFERED_CSV_PRIVATE_LEDGER_REQUIRED')
        state = json.loads(state_path.read_text()) if state_path.exists() else {}
        now = _stamp(clock())
        capability = usage.get('capability', {})
        if (capability.get('method') != 'GET'
                or not _stamp(capability.get('valid_from')) <= now < _stamp(capability.get('valid_until'))):
            raise DownloadHold('OFFERED_CSV_DATED_PRIVATE_SCOPE_REQUIRED')
        prior = state.get(period)
        if prior:
            elapsed = (now - _stamp(prior['started_at'])).total_seconds()
            if elapsed < 0:
                raise DownloadHold('OFFERED_CSV_CLOCK_REGRESSION')
            if elapsed < LIMITS[period]:
                receipt_name = prior.get('receipt_file', '')
                if not re.fullmatch('[0-9a-f]{64}\\.receipt\\.json', receipt_name):
                    raise DownloadHold('OFFERED_CSV_RATE_LIMIT_AFTER_INCOMPLETE_REQUEST')
                receipt_path = root / receipt_name
                if not receipt_path.is_file() or receipt_path.is_symlink():
                    raise DownloadHold('OFFERED_CSV_RATE_LIMIT_AFTER_INCOMPLETE_REQUEST')
                receipt_bytes = receipt_path.read_bytes()
                if _sha(receipt_bytes) != receipt_name[:64]:
                    raise DownloadHold('OFFERED_CSV_CACHED_RECEIPT_SHA_MISMATCH')
                receipt = json.loads(receipt_bytes)
                if (receipt.get('profile') != PROFILE or receipt.get('provider') != 'NAR_OFFICIAL_CSV'
                        or receipt.get('source_url') != url or receipt.get('period') != period
                        or receipt.get('started_at') != prior.get('started_at')
                        or receipt.get('usage_record_sha256') != usage_sha256):
                    raise DownloadHold('OFFERED_CSV_CACHED_RECEIPT_SCOPE_MISMATCH')
                if receipt.get('status') != 'ORIGINAL_ZIP_CAPTURED':
                    raise DownloadHold('OFFERED_CSV_RATE_LIMIT_AFTER_FAILED_REQUEST')
                if (not re.fullmatch('[0-9a-f]{64}', str(receipt.get('raw_sha256')))
                        or receipt.get('raw_file') != receipt['raw_sha256'] + '.zip'):
                    raise DownloadHold('OFFERED_CSV_CACHED_RECEIPT_SCOPE_MISMATCH')
                if not _stamp(prior['started_at']) <= _stamp(receipt.get('captured_at')) <= now:
                    raise DownloadHold('OFFERED_CSV_CACHED_CAPTURE_TIME_MISMATCH')
                original = root / receipt.get('raw_file', 'NO_RAW')
                if receipt.get('status') != 'ORIGINAL_ZIP_CAPTURED' or original.is_symlink() or not original.is_file():
                    raise DownloadHold('OFFERED_CSV_RATE_LIMIT_AFTER_FAILED_REQUEST')
                raw = original.read_bytes()
                if _sha(raw) != receipt.get('raw_sha256'):
                    raise DownloadHold('OFFERED_CSV_CACHED_RAW_SHA_MISMATCH')
                return {'receipt': receipt, 'raw': raw, 'cache_reused': True, 'new_http_requests': 0}
        attempt = {'started_at': now.isoformat(), 'url': url}
        state[period] = attempt
        temporary = root / 'offered_csv_ledger.tmp'
        if temporary.is_symlink():
            raise DownloadHold('OFFERED_CSV_PRIVATE_LEDGER_REQUIRED')
        with open(temporary, 'w') as file:
            os.chmod(temporary, 0o600)
            json.dump(state, file, ensure_ascii=False, sort_keys=True)
            file.flush(); os.fsync(file.fileno())
        os.replace(temporary, state_path)
        receipt = {'profile': PROFILE, 'provider': 'NAR_OFFICIAL_CSV', 'source_url': url,
                   'period': period, 'started_at': now.isoformat(), 'method': 'GET',
                   'usage_record_sha256': usage_sha256, 'formal_source_admitted': False,
                   'active_universe_verified': False, 'signature_issued': False,
                   'new_numerical_policy': False, 'new_http_requests': 1}
        try:
            with _wall_budget():
                client = opener or urllib.request.build_opener(_NoRedirect())
                # No UA override, proxy substitution, cookie reuse or retry.
                with client.open(urllib.request.Request(url, method='GET'), timeout=MAX_SECONDS) as response:
                    if response.status != 200 or response.geturl() != url:
                        raise DownloadHold('OFFERED_CSV_EXACT_HTTP200_REQUIRED')
                    content_type = response.headers.get('content-type', '').split(';')[0].strip().lower()
                    if content_type != 'application/zip':
                        raise DownloadHold('OFFERED_CSV_ZIP_RESPONSE_REQUIRED')
                    raw = response.read(MAX_BYTES + 1)
                    disposition = response.headers.get('content-disposition', '')
                if not 0 < len(raw) <= MAX_BYTES:
                    raise DownloadHold('OFFERED_CSV_COMPRESSED_LIMIT')
                # Even a ZIP/schema failure retains the actual bounded response.
                digest = _sha(raw)
                filename = digest + '.zip'
                _immutable(root / filename, raw)
                receipt.update(http_status=200, final_url=url, raw_sha256=digest,
                               raw_bytes=len(raw), raw_file=filename,
                               captured_at=_stamp(clock()).isoformat(),
                               content_type=content_type, content_disposition=disposition)
                with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                    members = archive.infolist()
                    if (not 1 <= len(members) <= 4 or sum(x.file_size for x in members) > MAX_UNCOMPRESSED
                            or any(x.file_size > 16_000_000 or x.flag_bits & 1 for x in members)
                            or archive.testzip() is not None):
                        raise DownloadHold('OFFERED_CSV_ZIP_INTEGRITY_OR_RESOURCE_LIMIT')
                captured = _stamp(clock())
                if captured < now:
                    raise DownloadHold('OFFERED_CSV_CLOCK_REGRESSION')
                receipt.update(status='ORIGINAL_ZIP_CAPTURED', http_status=200, final_url=url,
                               raw_sha256=digest, raw_bytes=len(raw), raw_file=filename,
                               captured_at=captured.isoformat(), content_type=content_type,
                               content_disposition=disposition, zip_crc_verified=True,
                               retrieval_method='AUTHORIZED_HTTP_GET')
        except Exception as error:
            receipt.update(status='ACQUISITION_FAILED_NOT_NO_BET', failed_at=_stamp(clock()).isoformat(),
                           error=type(error).__name__ + ':' + str(error))
        receipt_raw = _bytes(receipt)
        receipt_file = _sha(receipt_raw) + '.receipt.json'
        _immutable(root / receipt_file, receipt_raw)
        attempt['receipt_file'] = receipt_file
        with open(temporary, 'w') as file:
            os.chmod(temporary, 0o600)
            json.dump(state, file, ensure_ascii=False, sort_keys=True)
            file.flush(); os.fsync(file.fileno())
        os.replace(temporary, state_path)
        if receipt['status'] != 'ORIGINAL_ZIP_CAPTURED':
            raise DownloadHold(receipt['error'])
        return {'receipt': receipt, 'raw': raw, 'cache_reused': False, 'new_http_requests': 1}
