"""Existing SOURCE signature -> exact private CSV replay, never a new signer.

Dormant until an exact private CSV Profile and processing-scope decision are
actually adopted. A genuine generic SOURCE envelope signs original HTTP
captures. This adapter verifies that signature, reparses both original ZIPs,
and links the derived candidate by hash; it never claims a signature was
issued for the newly normalized candidate or grants a Provider licence.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import base64
import gzip
import hashlib
import io
import json
from pathlib import Path
import re

from runtime import local_fnb_csv_source_admission as admission
from runtime import local_fnb_csv_current_universe as universe
from runtime.local_nar_csv_download import DAILY_URL, DAILY_ODDS_URL, verify_usage_record

SCOPE = 'SINGLE_RACE_PRESTART_NONPRODUCTION_NOT_REGISTERED_OOS'
CONTRACT = 'PRIVATE_OFFERED_CSV_PROCESSING_SCOPE_ONLY'
CAPTURE_MANIFEST = 'KM-FNB-OFFERED-CSV-ORIGINAL-CAPTURE-NONPRODUCTION-v1'
SIGNATURE_CONTRACT = 'EXISTING_GENERIC_SOURCE_RAW_SIGNATURE_WITH_DETERMINISTIC_CSV_REPLAY'
PROCESSING_SCOPE = 'WHOLLY_PRIVATE_NONCOMMERCIAL_OFFERED_CSV_ANALYSIS'
SIGNER = 'KM-LOCAL-RUNTIME-ED25519-20260922'
RUNTIME_HASH_ALIASES = {'runtime_app_sha256':'runtime_wrapper_sha256',
                       'sbo_public_shadow_sha256':'sbo_public_shadow_evidence_sha256'}
CODE_PATHS = ('runtime/local_fnb_csv_source_admission.py',
              'runtime/local_nar_csv_reference.py',
              'runtime/local_fnb_csv_current_universe.py',
              'runtime/local_fnb_csv_signed_capture.py')


@dataclass(frozen=True)
class SignedCsvBinding:
    """Pinned private installation; never populated from a Race request."""
    profile_path: str
    profile_sha256: str
    owner_adoption_path: str
    owner_adoption_sha256: str
    usage_record_path: str
    usage_record_sha256: str
    trust_path: str
    trust_sha256: str
    actor_id: str
    expected_runtime_hashes: dict
    code_sha256: dict


def _load(path, expected):
    path = Path(path)
    if path.is_symlink() or not re.fullmatch('[0-9a-f]{64}', str(expected)):
        raise admission.CsvAdmissionHold('CSV_SIGNED_PINNED_INPUT_REQUIRED')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise admission.CsvAdmissionHold('CSV_SIGNED_PINNED_INPUT_SHA_MISMATCH')
    return json.loads(raw)


def _stamp(value):
    return admission._dt(value)


def _approved(binding, request, now, root):
    if not isinstance(binding, SignedCsvBinding):
        raise admission.CsvAdmissionHold('CSV_SIGNED_PRIVATE_BINDING_REQUIRED')
    profile = _load(binding.profile_path, binding.profile_sha256)
    if (profile.get('profile_id') != admission.PROFILE or profile.get('enabled') is not True
            or profile.get('status') != 'APPROVED_PRIVATE_NONPRODUCTION_CSV_PROFILE'
            or profile.get('qualification_contract') != CONTRACT
            or profile.get('signature_contract') != SIGNATURE_CONTRACT):
        raise admission.CsvAdmissionHold('CSV_SIGNED_PROFILE_NOT_ADOPTED')
    actual_codes = {name: hashlib.sha256((root/name).read_bytes()).hexdigest() for name in CODE_PATHS}
    if binding.code_sha256 != actual_codes:
        raise admission.CsvAdmissionHold('CSV_SIGNED_ADAPTER_CODE_PIN_MISMATCH')
    owner = _load(binding.owner_adoption_path, binding.owner_adoption_sha256)
    if (owner.get('decision') != 'APPROVE_EXACT_PRIVATE_CSV_ADOPTION'
            or owner.get('scope') != SCOPE or owner.get('processing_scope') != PROCESSING_SCOPE
            or owner.get('profile_sha256') != binding.profile_sha256
            or owner.get('trust_sha256') != binding.trust_sha256
            or owner.get('code_sha256') != actual_codes or owner.get('actor_id') != binding.actor_id
            or owner.get('receipt_signer_key_id') != SIGNER
            or owner.get('expected_runtime_hashes') != binding.expected_runtime_hashes
            or not owner.get('approval_ref') or owner.get('provider_licence_granted') is not False
            or request.get('venue_id') != 'FNB'
            or request.get('race_date') not in owner.get('race_dates', [])
            or request.get('race_no') not in owner.get('race_numbers', [])
            or not _stamp(owner['effective_from']) <= now < _stamp(owner['effective_until'])):
        raise admission.CsvAdmissionHold('CSV_SIGNED_EXACT_OWNER_ADOPTION_UNVERIFIED')
    if (set(binding.expected_runtime_hashes) == set()
            or not re.fullmatch('[0-9a-f]{64}', str(binding.expected_runtime_hashes.get('source_acquisition_sha256')))):
        raise admission.CsvAdmissionHold('CSV_SIGNED_SOURCE_RUNTIME_PIN_REQUIRED')
    for url in (DAILY_URL, DAILY_ODDS_URL):
        verify_usage_record(binding.usage_record_path, binding.usage_record_sha256, url)
    usage = _load(binding.usage_record_path, binding.usage_record_sha256)
    cap = usage.get('capability', {})
    if (cap.get('method') != 'GET' or request['race_date'] not in cap.get('target_race_dates', [])
            or cap.get('target_venue') != 'FNB'
            or not _stamp(cap['valid_from']) <= now < _stamp(cap['valid_until'])):
        raise admission.CsvAdmissionHold('CSV_SIGNED_PRIVATE_OFFERED_SCOPE_NOT_EFFECTIVE')
    trust = _load(binding.trust_path, binding.trust_sha256)
    canonical_path = root/'evidence/family_audit_20261016/runtime_health.json'
    canonical = _load(canonical_path, owner.get('canonical_trust_sha256'))
    gateway = json.loads((root/'profiles/current_execution_gateway.json').read_bytes())['families']['LOCAL']
    canonical_runtime = {RUNTIME_HASH_ALIASES.get(k,k):v
        for k,v in gateway.get('active_bundle_sha256',{}).items()}
    if (trust.get('receipt_signer_key_id') != SIGNER
            or any(trust.get(k) != canonical.get(k) for k in (
                'receipt_signer_key_id','receipt_public_key_b64','engine_sha256','parameter_map_sha256'))
            or any(trust.get(k) != gateway.get(k) for k in (
                'receipt_signer_key_id','engine_sha256','parameter_map_sha256'))
            or canonical_runtime != binding.expected_runtime_hashes):
        raise admission.CsvAdmissionHold('CSV_SIGNED_EXISTING_TRUST_KEY_MISMATCH')
    return profile, owner, trust


def verify_capture_envelope(envelope, request, *, trust, expected_runtime_hashes, now):
    """Verify actual existing signature and retain its exact raw-capture scope."""
    from runtime.local_fnb_r12_historical_krs_witness import verify_envelope
    source = verify_envelope(envelope, race_id=request['race_id'], phase='SOURCE',
        status='SOURCE_FROZEN', public=base64.b64decode(trust['receipt_public_key_b64'], validate=True), cfg=trust)
    receipt = envelope['receipt']
    if (envelope.get('signer_key_id') != SIGNER or trust.get('receipt_signer_key_id') != SIGNER
            or any(receipt.get('runtime_hashes', {}).get(k) != v for k,v in expected_runtime_hashes.items())
            or not expected_runtime_hashes.get('source_acquisition_sha256')
            or source.get('source_manifest_profile') != CAPTURE_MANIFEST
            or source.get('source_race_context') != {k:request[k] for k in ('venue_id','race_date','race_no')}
            or source.get('prediction_cutoff') != request['prediction_cutoff']
            or not _stamp(source['source_freeze_at']) <= _stamp(receipt['timestamp']) <= now
            or _stamp(receipt['timestamp']) >= _stamp(request['prediction_cutoff'])):
        raise admission.CsvAdmissionHold('CSV_SIGNED_CAPTURE_SCOPE_CODE_OR_CLOCK_MISMATCH')
    captures = {}
    for snapshot in source.get('sources', []):
        url = snapshot.get('requested_url')
        if url not in (DAILY_URL, DAILY_ODDS_URL) or url in captures:
            raise admission.CsvAdmissionHold('CSV_SIGNED_EXACT_TWO_SOURCE_MANIFEST_REQUIRED')
        if (snapshot.get('final_url') != url or snapshot.get('http_status') != 200
                or snapshot.get('source_class') != 'OFFICIAL_NAR_CSV_ZIP_CAPTURE'
                or snapshot.get('authority') != 'NAR_OFFICIAL' or snapshot.get('official') is not True
                or snapshot.get('raw_encoding') != 'gzip+base64'
                or snapshot.get('source_access_policy', {}).get('automatic_access_allowed') is not True
                or snapshot.get('content_type', '').split(';')[0].strip() != 'application/zip'
                or snapshot.get('snapshot_sha256') != admission.sha({k:v for k,v in snapshot.items() if k != 'snapshot_sha256'})):
            raise admission.CsvAdmissionHold('CSV_SIGNED_ORIGINAL_SNAPSHOT_UNVERIFIED')
        with gzip.GzipFile(fileobj=io.BytesIO(base64.b64decode(snapshot['raw_gzip_b64'], validate=True))) as file:
            raw = file.read(4_000_001)
        if (not 0 < len(raw) <= 4_000_000 or len(raw) != snapshot.get('byte_count')
                or hashlib.sha256(raw).hexdigest() != snapshot.get('raw_sha256')
                or not _stamp(snapshot['fetched_at']) <= _stamp(snapshot['archive_capture_completed_at'])
                    <= _stamp(source['source_freeze_at'])):
            raise admission.CsvAdmissionHold('CSV_SIGNED_ORIGINAL_RAW_SHA_OR_TIME_MISMATCH')
        captures[url] = {'raw':raw,'receipt':{'provider':'NAR_OFFICIAL_CSV',
            'http_status':200,'source_url':url,'final_url':url,'raw_sha256':snapshot['raw_sha256'],
            'captured_at':snapshot['archive_capture_completed_at'],'retrieval_method':'AUTHORIZED_HTTP_GET',
            'content_disposition':snapshot.get('archive_content_disposition')}}
    if set(captures) != {DAILY_URL, DAILY_ODDS_URL}:
        raise admission.CsvAdmissionHold('CSV_SIGNED_EXACT_TWO_SOURCE_MANIFEST_REQUIRED')
    return source, captures


def prepare_qualified_csv(envelope, request, *, binding, freeze_at, now=None, repo_root=None, clock=None):
    """Ready-to-call post-adoption seam for run_qualified; makes no signature.

    Returns the actual full original envelope unchanged and a consumer binding
    whose verifiers recheck the pinned Owner decision and original signature.
    An absent real adoption or live signed capture fails, rather than creating
    placeholder true values. No callback code must be invented after approval.
    """
    envelope, request = deepcopy(envelope), deepcopy(request)
    current_clock = (lambda:_stamp(clock())) if clock is not None else (
        lambda:_stamp(datetime.now(timezone.utc)))
    # A supplied observation timestamp may control initial assessment only.
    # Live verifier callbacks always advance with the real/trusted clock.
    checked = _stamp(now) if now is not None else current_clock()
    freeze = _stamp(freeze_at)
    root = Path(repo_root or Path(__file__).resolve().parents[1])
    # Same dated private single-Owner Cutoff already enforced by its runtime;
    # a generic SOURCE request cannot redefine that approved 300-second gap.
    if (_stamp(request['scheduled_post_at']) - _stamp(request['prediction_cutoff'])).total_seconds() != 300:
        raise admission.CsvAdmissionHold('CSV_SIGNED_EXISTING_PRIVATE_CUTOFF_300_SECONDS_REQUIRED')
    profile, owner, trust = _approved(binding, request, checked, root)
    source, captures = verify_capture_envelope(envelope,request,trust=trust,
        expected_runtime_hashes=binding.expected_runtime_hashes,now=checked)
    if not _stamp(envelope['receipt']['timestamp']) <= freeze <= checked < _stamp(request['prediction_cutoff']):
        raise admission.CsvAdmissionHold('CSV_SIGNED_CAPTURE_FREEZE_NOW_CUTOFF_ORDER')
    race, odds = captures[DAILY_URL], captures[DAILY_ODDS_URL]
    current = universe.assess_current_universe(race_raw=race['raw'],race_receipt=race['receipt'],
        odds_raw=odds['raw'],odds_receipt=odds['receipt'],request=request,freeze_at=freeze_at,
        freshness_limits=profile.get('current_snapshot_freshness_limits'))
    if not current['complete_current_universe_candidate']:
        raise admission.CsvAdmissionHold('CSV_SIGNED_CURRENT_UNIVERSE_NOT_COMPLETE_OR_FRESH')
    rows = current['rows']
    active = [{'runner_id':r['runner_id'],'name':r['name']} for r in rows if r['status']=='ACTIVE']
    request = deepcopy(request)
    # Canonical physical units and class come from the protected original ZIP,
    # never missing/defaulted or contradictory caller aliases.
    reference = admission.inspect_zip(race['raw'],capture={**race['receipt'],
        'usage_qualification':{'contract':CONTRACT,'usage_record_sha256':binding.usage_record_sha256,
                               'provider_licence_granted':False}},
        race=current['race_identity'],encoding='utf-8-sig',header_mode='present',now=checked)
    request = admission.bind_csv_race_context(reference,request)
    if request.get('runners') is None:
        request['runners'] = active
    if {(str(r['runner_id']),r['name']) for r in request['runners']} != {(r['runner_id'],r['name']) for r in active}:
        raise admission.CsvAdmissionHold('CSV_SIGNED_REQUEST_VERIFIED_ACTIVE_MISMATCH')
    capture = {**race['receipt'],'usage_qualification':{'contract':CONTRACT,
        'usage_record_sha256':binding.usage_record_sha256,'provider_licence_granted':False}}
    def recheck():
        observed = current_clock()
        _approved(binding,request,observed,root)
        verify_capture_envelope(envelope,request,trust=trust,
            expected_runtime_hashes=binding.expected_runtime_hashes,now=observed)
        latest = universe.assess_current_universe(race_raw=race['raw'],race_receipt=race['receipt'],
            odds_raw=odds['raw'],odds_receipt=odds['receipt'],request=request,freeze_at=observed.isoformat(),
            freshness_limits=profile.get('current_snapshot_freshness_limits'))
        if not latest['complete_current_universe_candidate']:
            raise admission.CsvAdmissionHold('CSV_SIGNED_CURRENT_UNIVERSE_EXPIRED')
        return observed
    def approval(**kwargs):
        recheck()
        return {'passed':True,'profile_sha256':binding.profile_sha256,'scope':SCOPE,
            'approval_ref':owner['approval_ref'],'approval_sha256':binding.owner_adoption_sha256,
            'effective_from':owner['effective_from'],'effective_until':owner['effective_until']}
    def rights(**kwargs):
        approval()
        return {'passed':True,'provider_id':'NAR_OFFICIAL_CSV','raw_sha256':capture['raw_sha256'],
            'source_url':DAILY_URL,'retrieval_method':'AUTHORIZED_HTTP_GET','actor_id':binding.actor_id,
            'permission_ref':binding.usage_record_path,'permission_sha256':binding.usage_record_sha256,
            'qualification_contract':CONTRACT,'scope':SCOPE,'exact_profile_adoption_verified':True,
            'private_processing_scope_verified':True,'provider_licence_granted':False,
            'adopted_profile_sha256':binding.profile_sha256,'owner_adoption_sha256':binding.owner_adoption_sha256,
            'effective_from':owner['effective_from'],'effective_until':owner['effective_until']}
    def changes(**kwargs):
        verify_capture_envelope(envelope,request,trust=trust,expected_runtime_hashes=binding.expected_runtime_hashes,now=recheck())
        return {'passed':True,'raw_sha256':odds['receipt']['raw_sha256'],'csv_raw_sha256':capture['raw_sha256'],
            'request_race_id':request['race_id'],'freeze_at':freeze_at,'cutoff_at':request['prediction_cutoff'],
            'csv_captured_at':capture['captured_at'],'authority':'NAR_OFFICIAL','original_raw_reparsed':True,
            'external_receipt_verified':True,'receipt_sha256':envelope['receipt_sha256'],
            'race_identity':current['race_identity'],
            'official_race_id':'NAR-CSV:'+':'.join(map(str,current['race_identity']['source_composite_key'])),
            'official_race_identity_kind':'OBSERVED_OFFICIAL_COMPOSITE_NOT_PERMANENT_PROVIDER_ID',
            'complete_declared_universe':True,'latest_changes_verified':True,
            'current_state_verification_mode':'FRESH_OFFICIAL_CARD_AND_COMPLETE_POSITIVE_WIN_SET_AS_OF_SNAPSHOT',
            'no_future_change_guarantee':True,'official_event_log_supplied':False,
            'observed_at':source['source_freeze_at'],'source_updated_at':current['snapshots'][1]['archive_filename_at'],
            'runners':rows,'events':[]}
    def signature(*, receipt, source_candidate, **kwargs):
        approval()
        _, replay = verify_capture_envelope(receipt,request,trust=trust,
            expected_runtime_hashes=binding.expected_runtime_hashes,now=recheck())
        if (not source_candidate or source_candidate.get('sha256') != admission.sha({k:v for k,v in source_candidate.items() if k!='sha256'})
                or base64.b64decode(source_candidate['sources'][0]['raw_b64'],validate=True) != replay[DAILY_URL]['raw']
                or base64.b64decode(source_candidate['official_change_evidence']['raw_b64'],validate=True) != replay[DAILY_ODDS_URL]['raw']
                or source_candidate.get('race_id') != request['race_id']
                or source_candidate.get('source_freeze_at') != freeze_at
                or {r['runner_id'] for r in source_candidate['active_runner_universe']['runners']} != {r['runner_id'] for r in active}):
            raise admission.CsvAdmissionHold('CSV_SIGNED_DETERMINISTIC_CANDIDATE_RAW_LINK_MISMATCH')
        # Rebuild every normalized value from the same signed original bytes.
        # Hashing a caller's modified candidate is not deterministic replay.
        replayed = admission.assess(raw=replay[DAILY_URL]['raw'],capture=capture,request=request,
            encoding='utf-8-sig',header_mode='present',freeze_at=freeze_at,actor_id=binding.actor_id,
            qualification_verifier=rights,official_change_packet={'raw':replay[DAILY_ODDS_URL]['raw']},
            official_change_verifier=changes,now=checked)
        if replayed.get('source_candidate') != source_candidate:
            raise admission.CsvAdmissionHold('CSV_SIGNED_NORMALIZED_REPLAY_MISMATCH')
        return {'passed':True,'signature_verified':True,'receipt_sha256':receipt['receipt_sha256'],
            'source_candidate_sha256':source_candidate['sha256'],'raw_sha256':capture['raw_sha256'],
            'profile_id':admission.PROFILE,'scope':SCOPE,'race_id':request['race_id'],
            'cutoff_at':request['prediction_cutoff'],'freeze_at':freeze_at,
            'signature_scope':'EXISTING_GENERIC_ORIGINAL_CAPTURE_WITH_CSV_REPLAY_LINK',
            'normalized_candidate_signature_issued':False}
    assessment = admission.assess(raw=race['raw'],capture=capture,request=request,
        encoding='utf-8-sig',header_mode='present',freeze_at=freeze_at,actor_id=binding.actor_id,
        qualification_verifier=rights,official_change_packet={'raw':odds['raw']},
        official_change_verifier=changes,source_receipt=envelope,source_receipt_verifier=signature,now=checked)
    if assessment.get('source_candidate') is None or assessment.get('external_signature_verified_by_supplied_gate') is not True:
        raise admission.CsvAdmissionHold('CSV_SIGNED_ASSESSMENT_NOT_READY:'+','.join(assessment['terminals']))
    consumer = admission.CsvConsumerBinding(binding.profile_sha256,binding.code_sha256[CODE_PATHS[0]],
        SCOPE,approval,signature,binding.actor_id,binding.profile_path)
    return {'assessment':assessment,'request':deepcopy(request),'consumer_binding':consumer,
        'source_receipt':deepcopy(envelope),'current_status':deepcopy(current),
        'existing_raw_signature_verified':True,'normalized_candidate_signature_issued':False,
        'production_source_or_consumers_enabled':False}
