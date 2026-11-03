"""Private multi-provider evidence frontend; no SOURCE/Owner authority grant.

Only separately admitted, pinned private transports may acquire bytes. This
module does not discover an API, scrape an unqualified site, sign SOURCE, infer
permanent IDs from names, or import vendor indices into LOCAL numeric rules.
R20 receives an unchanged official packet through its existing source callback.
"""
from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import urlsplit

from runtime.urw_nankan_reference_source import private_directory, immutable

PROFILE = 'KM-FNB-MULTISOURCE-PRIVATE-FRONTEND-v0.1-20261103'
REFERENCE_CLASS = 'PRIVATE_USER_REFERENCE / NOT_FORMAL_SOURCE / NOT_SIGNED / NOT_REGISTERED_OOS / NO_TICKET'
TIERS = ('FORMAL_OFFICIAL_SOURCE', 'AUTHORIZED_SUPPLEMENTAL_EVIDENCE', 'PRIVATE_REFERENCE_SHADOW')
PROVIDERS = {
    'NAR_OFFICIAL': ('www.keiba.go.jp', 'OFFICIAL'),
    'NANKAN_OFFICIAL': ('www.nankankeiba.com', 'OFFICIAL'),
    'FKEIBA_OFFICIAL': ('www.f-keiba.com', 'OFFICIAL'),
    'RAKUTEN_KEIBA': ('keiba.rakuten.co.jp', 'NON_OFFICIAL'),
    'SPAIA_KEIBA': ('spaia-keiba.com', 'NON_OFFICIAL'),
    'SBO_NAR': ('nar.k-ba.net', 'NON_OFFICIAL'),
    'KICHIUMA': ('kichiuma-chiho.net', 'NON_OFFICIAL'),
    'STATS_KEIBA': ('stats-keiba.com', 'NON_OFFICIAL'),
}
_SHA = re.compile('[0-9a-f]{64}')


class MultisourceHold(ValueError):
    pass


def sha_bytes(data): return hashlib.sha256(data).hexdigest()
def sha(value): return sha_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                           separators=(',', ':'), allow_nan=False).encode())
def stamp(value):
    out = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    if out.tzinfo is None: raise MultisourceHold('MULTISOURCE_AWARE_TIME_REQUIRED')
    return out.astimezone(timezone.utc)
def norm(value): return re.sub(r'\s+', '', unicodedata.normalize('NFKC', str(value)))


def validate_url(provider, url):
    expected = PROVIDERS.get(provider)
    p = urlsplit(str(url))
    if (not expected or p.scheme != 'https' or p.netloc != expected[0]
            or p.username or p.password or p.fragment or p.port not in (None, 443)):
        raise MultisourceHold('MULTISOURCE_PROVIDER_URL_SCOPE')
    return p


def race_identity(value):
    day = str(value.get('race_date', ''))
    number = value.get('race_no')
    if (value.get('venue_id') != 'FNB' or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', day)
            or type(number) is not int or not 1 <= number <= 12):
        raise MultisourceHold('MULTISOURCE_FNB_RACE_IDENTITY_REQUIRED')
    datetime.fromisoformat(day)
    return ('FNB', day, number)


def race_condition_conflicts(expected, observed):
    """Compare observed headers; URLs and bare Race ID aliases are not proof."""
    if race_identity(expected) != race_identity(observed):
        raise MultisourceHold('MULTISOURCE_PROVIDER_RACE_MISMATCH')
    def conditions(value):
        post=value.get('scheduled_post_at') or value.get('scheduled_post_jst')
        distance=value.get('distance_m')
        surface=value.get('surface')
        if post is not None: post=stamp(post)
        if distance is not None:
            if type(distance) is not int or distance<=0:
                raise MultisourceHold('MULTISOURCE_DISTANCE_INVALID')
        if surface is not None:
            surface={'ダート':'DIRT','芝':'TURF'}.get(norm(surface),norm(surface).upper())
        return {'scheduled_post_at':post,'distance_m':distance,'surface':surface}
    left,right=conditions(expected),conditions(observed)
    return [k for k in left if left[k] is not None and right[k] is not None and left[k]!=right[k]]


@dataclass(frozen=True)
class ProviderBinding:
    """Trusted private configuration, not a licence derived from public content.

    The existing provider admission owner must supply permission/admission
    evidence and exact URLs. Runtime requests cannot create this configuration.
    These input records are preserved, never independently asserted genuine by
    this interface. Effective Provider rights remain an external prerequisite.
    """
    provider: str
    exact_urls: tuple
    code_sha256: str
    permission_ref: str
    permission_sha256: str
    effective_from: str
    effective_until: str
    actor_id: str
    automated_get_admitted: bool
    private_retention_admitted: bool
    cloud_processing_admitted: bool
    qualified_field_rules: dict
    fetch: object
    parse: object


def _binding(binding, url, actor_id, now):
    if not isinstance(binding, ProviderBinding):
        raise MultisourceHold('MULTISOURCE_PROVIDER_BINDING_NOT_CONNECTED')
    validate_url(binding.provider, url)
    if (url not in binding.exact_urls or not _SHA.fullmatch(binding.code_sha256)
            or not _SHA.fullmatch(binding.permission_sha256) or not binding.permission_ref
            or binding.actor_id != actor_id or not all((binding.automated_get_admitted,
                binding.private_retention_admitted, binding.cloud_processing_admitted))
            or not callable(binding.fetch) or not callable(binding.parse)
            or not stamp(binding.effective_from) <= now < stamp(binding.effective_until)):
        raise MultisourceHold('MULTISOURCE_PROVIDER_QUALIFICATION_REQUIRED')


def acquire(binding, *, url, intent, actor_id, now, private_root, consumer_verifier=None, clock=None):
    """One qualified callback, immutable original, and explicitly unsigned fields.

    Fetch must be the separately admitted transport enforcing actual robots,
    rate limits and redirects; no generic requests/alternate host fallback here.
    Its response returns actual HTTP bytes, a policy receipt, and capture time.
    A supplied search excerpt or DOM snapshot is never accepted as HTTP Raw.
    """
    now = stamp(now); _binding(binding, url, actor_id, now); identity = race_identity(intent)
    root = private_directory(private_root)
    # A failed earlier origin must not leave this attempt using its old clock.
    start = stamp((clock or (lambda: datetime.now(timezone.utc)))())
    if start < now: raise MultisourceHold('MULTISOURCE_CLOCK_REGRESSION')
    _binding(binding, url, actor_id, start)
    if intent.get('prediction_cutoff') and start >= stamp(intent['prediction_cutoff']):
        raise MultisourceHold('MULTISOURCE_CUTOFF_EXPIRED_DIAGNOSTIC_REQUIRED')
    response = binding.fetch(url=url, intent=deepcopy(intent), now=now)
    raw = response.get('raw')
    if (not isinstance(raw, bytes) or not raw or len(raw) > 4_000_000
            or response.get('retrieval_method') != 'HTTPS_GET_ORIGINAL_RESPONSE'
            or response.get('http_status') != 200 or response.get('final_url') != url
            or (response.get('access_policy') or {}).get('decision') != 'ALLOW'):
        raise MultisourceHold('MULTISOURCE_ORIGINAL_RESPONSE_UNVERIFIED')
    captured = stamp(response['captured_at'])
    after = stamp((clock or (lambda: datetime.now(timezone.utc)))())
    if after < now: raise MultisourceHold('MULTISOURCE_CLOCK_REGRESSION')
    _binding(binding, url, actor_id, after)
    if captured < now: raise MultisourceHold('MULTISOURCE_CAPTURE_BEFORE_ACQUISITION_START')
    if captured > after: raise MultisourceHold('MULTISOURCE_CAPTURE_IN_FUTURE')
    if intent.get('prediction_cutoff') and after >= stamp(intent['prediction_cutoff']):
        raise MultisourceHold('MULTISOURCE_CUTOFF_EXPIRED_DIAGNOSTIC_REQUIRED')
    # Preserve a valid original even when that Provider's format parser fails.
    # Saving its bytes does not admit its fields or declare an Active universe.
    digest = sha_bytes(raw)
    immutable(root/(digest+'.raw'), raw)
    capture = {'profile':PROFILE, 'provider':binding.provider, 'source_url':url,
        'http_status':200, 'retrieval_method':response['retrieval_method'],
        'captured_at':response['captured_at'], 'raw_sha256':digest, 'raw_bytes':len(raw),
        'transport_code_sha256':binding.code_sha256, 'permission_ref':binding.permission_ref,
        'permission_sha256':binding.permission_sha256, 'access_policy':deepcopy(response['access_policy']),
        'status':'RAW_CAPTURED_FORMAT_AND_ADMISSION_NOT_VERIFIED',
        'format_verified':False, 'formal_source_admitted':False, 'registered_oos_increment':0}
    capture['sha256'] = sha(capture)
    immutable(root/(capture['sha256']+'.capture.json'),
              (json.dumps(capture,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode())
    parsed = binding.parse(raw=raw, url=url, content_type=response.get('content_type'))
    if (not isinstance(parsed, dict) or not isinstance(parsed.get('identity'), dict)
            or not isinstance(parsed.get('fields'), list)):
        raise MultisourceHold('MULTISOURCE_PARSED_FORMAT_UNVERIFIED')
    if race_identity(parsed['identity']) != identity:
        raise MultisourceHold('MULTISOURCE_PROVIDER_RACE_MISMATCH')
    if race_condition_conflicts(intent,parsed['identity']):
        raise MultisourceHold('MULTISOURCE_RACE_CONDITION_CONFLICT')
    observations = []
    for field in parsed.get('fields', []):
        if not isinstance(field.get('field'), str) or not field['field']:
            raise MultisourceHold('MULTISOURCE_FIELD_PROVENANCE_REQUIRED')
        effective = stamp(field['effective_at'])
        if effective > captured: raise MultisourceHold('MULTISOURCE_POST_CAPTURE_FACT')
        rule = binding.qualified_field_rules.get(field['field'])
        external = field['field'].startswith('external_')
        consumer = (consumer_verifier(provider=binding.provider, field=deepcopy(field),
                      rule_id=rule, raw_sha256=digest, identity=deepcopy(parsed['identity']))
                    if rule and not external and callable(consumer_verifier) else {})
        # Provider permission is distinct from the current Registry/Consumer
        # permission. A matching rule name in a private binding is insufficient.
        usable = (isinstance(consumer,dict) and consumer.get('passed') is True
                  and consumer.get('rule_id') == rule
                  and consumer.get('raw_sha256') == digest)
        tier = TIERS[1] if usable else TIERS[2]
        # A parser cannot create permanent Identity from a displayed name.
        if field['field'].endswith('_id') and field.get('identity_kind') != 'PROVIDER_PERMANENT_ID':
            raise MultisourceHold('MULTISOURCE_PERMANENT_ID_NOT_OBSERVED')
        observations.append({**deepcopy(field), 'provider': binding.provider,
            'provider_authority': PROVIDERS[binding.provider][1], 'source_url': url,
            'raw_sha256': digest, 'captured_at': response['captured_at'],
            'tier': tier, 'rule_id': rule if tier == TIERS[1] else None,
            'formal_source_admitted': False})
    # Parsing and an external Consumer verifier may themselves take time.
    final = stamp((clock or (lambda: datetime.now(timezone.utc)))())
    if final < after: raise MultisourceHold('MULTISOURCE_CLOCK_REGRESSION')
    _binding(binding, url, actor_id, final)
    if intent.get('prediction_cutoff') and final >= stamp(intent['prediction_cutoff']):
        raise MultisourceHold('MULTISOURCE_CUTOFF_EXPIRED_DIAGNOSTIC_REQUIRED')
    packet = {'profile': PROFILE, 'provider': binding.provider,
        'provider_authority': PROVIDERS[binding.provider][1], 'source_url': url,
        'retrieval_method': response['retrieval_method'], 'http_status': 200,
        'raw_bytes': len(raw), 'raw_sha256': digest, 'captured_at': response['captured_at'],
        'acquisition_started_at': now.isoformat(), 'acquisition_verified_at': final.isoformat(),
        'identity': deepcopy(parsed['identity']), 'encoding': parsed.get('encoding'),
        'permission_ref': binding.permission_ref, 'permission_sha256': binding.permission_sha256,
        'raw_capture_receipt_sha256':capture['sha256'],
        'usage_qualification': 'EXTERNAL_TRUSTED_BINDING_REQUIRED_NOT_GRANTED_HERE',
        'transport_code_sha256': binding.code_sha256, 'access_policy': deepcopy(response['access_policy']),
        'observations': observations, 'formal_source_admitted': False,
        'active_universe_verified': False, 'signed_source_claim': False,
        'registered_oos_increment': 0}
    packet['sha256'] = sha(packet)
    immutable(root/(packet['sha256']+'.receipt.json'), (json.dumps(packet,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode())
    return packet



def acquire_available(targets, bindings, *, intent, actor_id, now, private_root, clock=None):
    """Attempt independent qualified bindings once each, preserving every HOLD.

    A failed origin does not manufacture authority for another. No duplicate
    target, hidden alternate-host retry or unqualified default GET is executed.
    """
    packets, receipts, seen = [], [], set()
    original_now = stamp(now)
    for target in targets:
        provider = target.get('provider') if isinstance(target, dict) else None
        url = target.get('url') if isinstance(target, dict) else None
        if not isinstance(provider, str) or not isinstance(url, str):
            receipts.append({'provider':None, 'url':None, 'status':'HOLD',
                'reason':'MULTISOURCE_EXPLICIT_TARGET_REQUIRED', 'formal_SOURCE':False, 'raw_sha256':None})
            continue
        key = (provider, url)
        if key in seen: continue
        seen.add(key)
        try:
            observed = stamp(clock()) if clock else datetime.now(timezone.utc)
            if observed < original_now: raise MultisourceHold('MULTISOURCE_CLOCK_REGRESSION')
            p = acquire(bindings.get(provider), url=url,
                        intent=intent, actor_id=actor_id, now=observed, private_root=private_root, clock=clock)
            packets.append(p)
            receipts.append({'provider':target['provider'],'url':target['url'],
                'status':'RAW_CAPTURED_NOT_FORMAL_ADMISSION','raw_sha256':p['raw_sha256']})
        except Exception as exc:
            # Each explicitly installed Provider owns its independent parser
            # and transport. Their ordinary failures cannot abort later ones.
            # Process interruption/SystemExit are deliberately not swallowed.
            if isinstance(exc,OSError):
                code='MULTISOURCE_TRANSPORT_OS_ERROR'
            else:
                code = str(exc).partition(':')[0]
            if not re.fullmatch('[A-Z][A-Z0-9_]{0,119}', code): code='MULTISOURCE_PRIVATE_TRANSPORT_FAILED'
            receipts.append({'provider':target['provider'],'url':target['url'],'status':'HOLD',
                'reason':code,'formal_SOURCE':False,'raw_sha256':None})
    result = {'packets':packets,'provider_receipts':receipts,'formal_source_admitted':False,
              'automatic_fallback_authority_granted':False,'registered_oos_increment':0}
    receipt = {'profile':PROFILE, 'identity':deepcopy(intent), 'provider_receipts':receipts,
               'formal_source_admitted':False, 'registered_oos_increment':0}
    receipt['sha256'] = sha(receipt)
    root = private_directory(private_root)
    immutable(root/('MULTISOURCE_ATTEMPTS_'+receipt['sha256']+'.json'),
              (json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode())
    result['attempt_receipt_sha256'] = receipt['sha256']
    return result


def import_user_reference(raw, *, expected_sha256):
    """Consume supplied JSON as reference bytes; never claim Provider HTTP Raw."""
    if sha_bytes(raw) != expected_sha256: raise MultisourceHold('MULTISOURCE_USER_REFERENCE_SHA_MISMATCH')
    original = json.loads(raw)
    if original.get('classification') != REFERENCE_CLASS:
        raise MultisourceHold('MULTISOURCE_REFERENCE_CLASSIFICATION_MISMATCH')
    race_identity(original['identity'])
    sources = original.get('provider_observations') or []
    for source in sources: validate_url(source['provider'], source['url'])
    observations = []
    for row in original.get('runners', []):
        for name in ('name','jockey_secondary','weight_carried_kg_secondary','trainer_secondary','sbo_external_average_reference'):
            observations.append({'runner_number': row['number'], 'field': name, 'value': row.get(name),
                'provider': 'USER_REFERENCE_COMPOSITE', 'provider_original_raw_sha256': None,
                'reference_file_sha256': expected_sha256, 'captured_at': original['observed_at_jst'],
                'tier': TIERS[2], 'rule_id': None, 'observed_via': 'public_web_search',
                'current_official_verified': False})
    return {'profile': PROFILE, 'classification': REFERENCE_CLASS, 'identity': original['identity'],
        'observations': observations, 'reference_file_sha256': expected_sha256,
        'provider_urls': sources, 'actual_provider_raw_count': 0, 'formal_source_admitted': False,
        'active_universe_verified': False, 'registered_oos_increment': 0}


def reconcile(packets, *, identity):
    """Report agreement/conflict; no voting, no newest-vendor Active decision."""
    key = race_identity(identity); grouped = {}; ids = set(); seen_identities=[]
    for packet in packets:
        if race_identity(packet['identity']) != key: raise MultisourceHold('MULTISOURCE_CROSS_RACE_JOIN')
        if race_condition_conflicts(identity,packet['identity']):
            raise MultisourceHold('MULTISOURCE_RACE_CONDITION_CONFLICT')
        for earlier in seen_identities:
            if race_condition_conflicts(earlier,packet['identity']):
                raise MultisourceHold('MULTISOURCE_RACE_CONDITION_CONFLICT')
        seen_identities.append(packet['identity'])
        for item in packet.get('observations', []):
            rid = item.get('runner_number')
            if type(rid) is not int or rid < 1: raise MultisourceHold('MULTISOURCE_RUNNER_NUMBER_REQUIRED')
            ids.add(rid); grouped.setdefault((rid,item['field']),[]).append(deepcopy(item))
    out = []; coverage = {rid:{'reference':0,'supplemental':0,'missing':0,'conflict':0} for rid in sorted(ids)}
    for (rid,field), values in sorted(grouped.items()):
        distinct = {norm(v['value']) for v in values if v.get('value') is not None}
        conflict = len(distinct)>1
        if conflict: coverage[rid]['conflict'] += 1
        if all(v.get('value') is None for v in values): coverage[rid]['missing'] += 1
        elif any(v.get('tier')==TIERS[1] for v in values): coverage[rid]['supplemental'] += 1
        else: coverage[rid]['reference'] += 1
        out.append({'runner_number':rid,'field':field,'conflict_status':'CONFLICT_REQUIRES_AUTHORITY' if conflict else 'NO_OBSERVED_CONFLICT',
                    'observations':values,'resolved_official_value':None})
    return {'profile':PROFILE,'identity':deepcopy(identity),'fields':out,'runner_coverage':coverage,
        'formal_active_universe_verified':False,'formal_source_admitted':False,
        'independent_provider_agreement_claimed':False,'numeric_consumer_changes':0}


def r20_source_frontend(official_producer, *, official_verifier, supplemental_producers=(),
                        official_fallbacks=(), official_provider=None, clock=None):
    """Plug into existing FNB_PRODUCERS.py ['source'] without changing R20 gates.

    The existing admitted official producer/cryptographic verifier are explicit
    dependencies, never inferred from matching reference sites. Supplementary
    packets are preserved privately and cannot rewrite official SOURCE fields.
    """
    def produce(*, intent, private_root, now):
        root = private_directory(private_root)
        routes = []
        if callable(official_producer) and callable(official_verifier):
            routes.append({'provider':official_provider or 'EXISTING_PRIMARY',
                           'produce':official_producer, 'verify':official_verifier})
        primary_count = len(routes)
        routes.extend(official_fallbacks)
        if not routes: raise MultisourceHold('MULTISOURCE_FORMAL_PRODUCER_NOT_CONNECTED')
        attempts = []
        seen = set()
        captured = decision = None
        last_code = 'MULTISOURCE_FORMAL_PRODUCER_NOT_CONNECTED'
        def current():
            observed = stamp(clock()) if clock else datetime.now(timezone.utc)
            if observed < stamp(now): raise MultisourceHold('MULTISOURCE_CLOCK_REGRESSION')
            if intent.get('prediction_cutoff') and observed >= stamp(intent['prediction_cutoff']):
                raise MultisourceHold('MULTISOURCE_CUTOFF_EXPIRED_DIAGNOSTIC_REQUIRED')
            return observed
        for index, route in enumerate(routes):
            provider = route.get('provider') if isinstance(route,dict) else None
            if isinstance(provider,str) and provider in seen: continue
            if isinstance(provider,str): seen.add(provider)
            try:
                if (not (provider == 'EXISTING_PRIMARY' and index < primary_count) and
                        (provider not in PROVIDERS or PROVIDERS[provider][1] != 'OFFICIAL')):
                    raise MultisourceHold('MULTISOURCE_EXPLICIT_OFFICIAL_BINDING_REQUIRED')
                if not callable(route.get('produce')) or not callable(route.get('verify')):
                    raise MultisourceHold('MULTISOURCE_FORMAL_PRODUCER_NOT_CONNECTED')
                candidate = route['produce'](intent=deepcopy(intent),private_root=root,now=current())
                if not isinstance(candidate,dict) or set(('request','source'))-candidate.keys():
                    raise MultisourceHold('MULTISOURCE_OFFICIAL_CAPTURE_REQUIRED')
                if race_condition_conflicts(intent,candidate['request']):
                    raise MultisourceHold('MULTISOURCE_RACE_CONDITION_CONFLICT')
                before = sha(candidate['source']); captured_before = sha(candidate)
                verified = route['verify'](captured=deepcopy(candidate),intent=deepcopy(intent),now=current())
                current()
                if (not isinstance(verified,dict) or verified.get('passed') is not True
                        or verified.get('source_artifact_sha256') != before):
                    raise MultisourceHold('MULTISOURCE_OFFICIAL_ADMISSION_UNVERIFIED')
                if sha(candidate) != captured_before:
                    raise MultisourceHold('MULTISOURCE_OFFICIAL_SOURCE_MUTATED')
                captured, decision = candidate, verified
                attempts.append({'provider':provider, 'status':'EXISTING_OFFICIAL_VERIFIER_PASSED',
                                 'source_artifact_sha256':before})
                break
            except Exception as error:
                last_code = 'MULTISOURCE_TRANSPORT_OS_ERROR' if isinstance(error,OSError) else str(error).partition(':')[0]
                if not re.fullmatch('[A-Z][A-Z0-9_]{0,119}',last_code):
                    last_code = 'MULTISOURCE_PRIVATE_TRANSPORT_FAILED'
                attempts.append({'provider':provider if isinstance(provider,str) else None,
                                 'status':'HOLD','reason':last_code})
        if captured is None:
            receipt = {'profile':PROFILE,'identity':deepcopy(intent),'official_attempts':attempts,
                       'formal_source_admitted':False,'registered_oos_increment':0}
            receipt['sha256'] = sha(receipt)
            immutable(root/('MULTISOURCE_'+receipt['sha256']+'.json'),
                      (json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode())
            raise MultisourceHold(last_code)
        extras, supplemental_attempts = [], []
        for producer in supplemental_producers:
            try:
                if not callable(producer): raise MultisourceHold('MULTISOURCE_SUPPLEMENTAL_BINDING_REQUIRED')
                item = producer(intent=deepcopy(intent),private_root=root,now=current())
                if race_identity(item['identity']) != race_identity(intent):
                    raise MultisourceHold('MULTISOURCE_CROSS_RACE_JOIN')
                extras.append(item)
            except Exception as error:
                code = str(error).partition(':')[0]
                if not re.fullmatch('[A-Z][A-Z0-9_]{0,119}',code): code='MULTISOURCE_PRIVATE_TRANSPORT_FAILED'
                supplemental_attempts.append({'status':'HOLD','reason':code})
        if sha(captured) != captured_before: raise MultisourceHold('MULTISOURCE_OFFICIAL_SOURCE_MUTATED')
        current()
        receipt = {'profile':PROFILE,'identity':deepcopy(intent),'official_artifact_sha256':before,
            'official_admission':decision,'supplemental_packets':extras,
            'official_attempts':attempts,'supplemental_attempts':supplemental_attempts,
            'source_bytes_rewritten':False,'formal_scope_granted_here':False,
            'supplemental_numeric_consumption':False,'registered_oos_increment':0}
        receipt['sha256'] = sha(receipt)
        immutable(root/('MULTISOURCE_'+receipt['sha256']+'.json'),
                  (json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode())
        return captured
    return produce
