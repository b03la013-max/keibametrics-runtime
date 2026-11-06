"""Offline OHI SOURCE handoff candidate, never an acquisition/signing route.

General personal-use terms are evidence for that use only. A technical SOURCE
snapshot does not enact provider, cloud, Owner or Consumer authorization.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from runtime.urw_nankan_reference_source import DOM, decode, sha, TERMS
from runtime.ohi_single_race_research import verify_observation, check_source_time, write, private_root
from runtime.ohi_nankan_private_source_v2 import SOURCE_PROFILE as INPUT_PROFILE
from runtime.local_physical.source_acquisition import (
    SOURCE_SCHEMA, SOURCE_PROFILE, snapshot_from_bytes, _merge_evidence,
    sha_obj, verify_source_artifact,
)

PROFILE = 'OHI-PERSONAL-SOURCE-ADMISSION-CANDIDATE-v1-20261026'
PURPOSE = 'PERSONAL_PRIVATE_NONCOMMERCIAL_RESEARCH_AND_PREDICTION'


def _reviewed_terms_text_sha256():
    profile = Path(__file__).resolve().parents[1] / 'profiles/ohi_personal_source_admission_candidate_20261026.json'
    return json.loads(profile.read_text())['terms_legal_text_sha256']


def _policy(receipt):
    policy = receipt.get('source_policy') or {}
    rule = policy.get('classification', '')
    allowed = ((policy.get('status') == 404 and rule == 'ROBOTS_ABSENT_HTTP_404_NOT_DENIAL')
               or (policy.get('status') == 200 and rule.startswith('Allow: ')
                   and isinstance(policy.get('robots_sha256'), str) and len(policy['robots_sha256']) == 64))
    if (not allowed or policy.get('robots_url') != 'https://www.nankankeiba.com/robots.txt'
            or policy.get('terms_url') != TERMS
            or policy.get('usage_scope') != 'USER_PERSONAL_NONCOMMERCIAL_PRIVATE_ONLY_NOT_PUBLIC_REDISTRIBUTION'):
        raise ValueError('OHI_CANDIDATE_SOURCE_POLICY_UNKNOWN_OR_DENIED')
    checked = datetime.fromisoformat(policy['checked_at'])
    fetched = datetime.fromisoformat(receipt['fetched_at'])
    if checked.tzinfo is None or fetched.tzinfo is None or checked > fetched:
        raise ValueError('OHI_CANDIDATE_POLICY_TIME')
    return policy


def review_terms(raw, receipt, *, now=None):
    """Bind the actual observed copyright paragraph; silence grants nothing."""
    now = now or datetime.now(timezone.utc)
    if (receipt.get('url') != TERMS or receipt.get('http_status') != 200
            or hashlib.sha256(raw).hexdigest() != receipt.get('raw_sha256')):
        raise ValueError('OHI_TERMS_RAW_RECEIPT_IDENTITY')
    stamp = datetime.fromisoformat(receipt['fetched_at'])
    if stamp.tzinfo is None or now.tzinfo is None or stamp > now:
        raise ValueError('OHI_TERMS_TIME_INVALID')
    _policy(receipt)
    dom = DOM(decode(raw)).root
    legal = [n for n in dom.all('div') if n.attrs.get('id') == 'contents730']
    if len(legal) != 1 or hashlib.sha256(legal[0].text().encode()).hexdigest() != _reviewed_terms_text_sha256():
        raise ValueError('OHI_TERMS_REQUIRES_FRESH_REVIEW')
    paragraphs = [p.text() for p in legal[0].all('p')
                  if '南関東4競馬場WWWサーバ' in p.text()]
    if len(paragraphs) != 1:
        raise ValueError('OHI_TERMS_COPYRIGHT_SCOPE_UNKNOWN')
    text = paragraphs[0]
    for clause in ('非営利の目的でかつユーザー自身で利用する場合に限り',
                   '文書を複製、使用、ダウンロードすることができます',
                   '個別に利用条件が付されている場合', '配布、転載は認められません'):
        if clause not in text:
            raise ValueError('OHI_TERMS_REQUIRES_FRESH_REVIEW')
    return {
        'url': TERMS, 'fetched_at': receipt['fetched_at'],
        'raw_sha256': receipt['raw_sha256'],
        'legal_text_sha256': _reviewed_terms_text_sha256(),
        'copyright_paragraph_sha256': hashlib.sha256(text.encode()).hexdigest(),
        'personal_document_copy_use_download': 'GENERAL_TERMS_EXPRESS_BASIS',
        'page_specific_conditions': 'MUST_BE_REVIEWED_AND_OBEYED',
        'redistribution': 'NOT_GRANTED_BY_GENERAL_TERMS',
        'automated_acquisition': 'NOT_EXPRESSLY_DETERMINED_BY_THIS_PARAGRAPH',
        'ai_analysis': 'NOT_EXPRESSLY_DETERMINED_BY_THIS_PARAGRAPH',
        'cloud_processing_storage': 'NOT_EXPRESSLY_DETERMINED_BY_THIS_PARAGRAPH',
        'provider_privacy_outsourcing_clause_is_user_cloud_permission': False,
        'commercial_contract_required_for_personal_document_use': False,
        'blanket_license_granted': False,
    }


def build_candidate(observation, source_dir, terms_raw, terms_receipt, *, diagnostic=False):
    """Reparse genuine Raw using the existing contract, then serialize unsigned.

    No network, source allowlist edit, provider registration, private ledger,
    model calculation, signing key or Runtime POST occurs here.
    """
    o = copy.deepcopy(observation)
    if (o.get('source_profile') != INPUT_PROFILE
            or o.get('race', {}).get('venue_id') != 'OHI'
            or o.get('sha256') != sha({k: v for k, v in o.items() if k != 'sha256'})
            or any(o.get(k) is not False for k in
                   ('active_verified', 'formal_source_claim', 'signed_source_claim', 'production_authority'))):
        raise ValueError('OHI_CANDIDATE_INPUT_CONTRACT_OR_AUTHORITY')
    clock = check_source_time(o, 'SOURCE_ADMISSION_CANDIDATE', diagnostic=diagnostic)
    verify_observation(o, source_dir)
    terms = review_terms(terms_raw, terms_receipt)
    root = Path(source_dir)
    snapshots, specs = [], []
    names = ['calendar', 'program', 'card', 'changes']
    if o['market'].get('source'):
        names.append('odds')
    for name in names:
        raw = (root / (name + '.raw.html')).read_bytes()
        meta = json.loads((root / (name + '.receipt.json')).read_text())
        policy = _policy(meta)
        if (meta.get('http_status') != 200
                or hashlib.sha256(raw).hexdigest() != meta.get('raw_sha256')):
            raise ValueError('OHI_CANDIDATE_SOURCE_POLICY_OR_RAW:' + name)
        # Retain evidence. A robots result is not a copyright/AI/cloud licence.
        source_id = 'NANKAN-' + name.upper() + ':' + o['race']['provider_race_id']
        spec = {'source_id': source_id, 'url': meta['url'],
                'source_class': 'OFFICIAL_RACE_FACTS_CANDIDATE',
                'authority': 'NANKAN_OFFICIAL', 'priority': 100, 'official': True,
                'required': True,
                'extract': [{'field': name + '_raw_sha256', 'type': 'meta',
                             'name': 'raw_sha256', 'required': True}]}
        snap, errors = snapshot_from_bytes(spec, raw, final_url=meta['url'],
            status_code=meta['http_status'], fetched_at=meta['fetched_at'],
            headers={'content-type': 'text/html'}, prediction_cutoff=o['race']['prediction_cutoff'])
        if errors:
            raise ValueError('OHI_CANDIDATE_SNAPSHOT:' + repr(errors))
        snap['source_access_policy'] = copy.deepcopy(policy)
        snap['snapshot_sha256'] = sha_obj({k: v for k, v in snap.items() if k != 'snapshot_sha256'})
        snapshots.append(snap)
        specs.append(spec)
    normalized, conflicts, errors = _merge_evidence(snapshots)
    if errors or conflicts:
        raise ValueError('OHI_CANDIDATE_SOURCE_CONFLICT')
    artifact = {
        'schema': SOURCE_SCHEMA, 'profile': SOURCE_PROFILE,
        'candidate_profile': PROFILE, 'provider': 'NANKAN_OFFICIAL',
        'race_id': 'OHI-' + o['race']['provider_race_id'],
        'source_race_context': copy.deepcopy(o['race']),
        'prediction_cutoff': o['race']['prediction_cutoff'],
        'source_freeze_at': clock['observed_at'],
        'required_source_manifest': specs, 'required_source_manifest_sha256': sha_obj(specs),
        'sources': snapshots,
        'raw_source_bundle_sha256': sha_obj([{k: s[k] for k in
            ('source_id', 'raw_sha256', 'snapshot_sha256', 'fetched_at', 'final_url')} for s in snapshots]),
        'normalized_evidence': normalized, 'normalized_evidence_sha256': sha_obj(normalized),
        'parsed_nankan_facts': o['facts'], 'declared_runner_universe': o['declared_facts'],
        'runner_universe_basis': o['runner_universe_basis'],
        'changes_observation': o['changes'], 'market_observation': o['market'],
        'input_observation_sha256': o['sha256'],
        'classification': 'ARCHIVED_SOURCE_ADMISSION_DIAGNOSTIC' if diagnostic else 'PRESTART_SOURCE_ADMISSION_CANDIDATE',
        'purpose_declaration': PURPOSE, 'terms_review': terms,
        'owner_reported_permission': 'ACQUIRED_AUTOMATED_AI_CLOUD_EVIDENCE_NOT_CONNECTED',
        'scope_review': {'A_personal_document_use': 'GENERAL_TERMS_EXPRESS_BASIS',
            'B_automated_method': 'TRANSPORT_CHECKED_PERMISSION_SCOPE_NOT_CONNECTED',
            'C_ai_cloud': 'OWNER_REPORTED_EVIDENCE_NOT_CONNECTED',
            'D_source_integrity': 'RAW_REPARSED_DECLARED_UNIVERSE_NOT_FORMAL_ACTIVE'},
        'conflicts': [], 'missing_required_sources': [], 'stale_sources': [],
        'post_cutoff_sources': [], 'errors': [],
        'formal_ready': False, 'active_verified': False, 'signed_source': False,
        'production_authority': False, 'consumer_authorization': False,
        'runtime_post_allowed': False, 'public_redistribution_authorized': False,
        'registered_oos_credit': 0,
    }
    artifact['source_snapshot_sha256'] = sha_obj(artifact)
    valid, errors = verify_source_artifact(artifact)
    if valid or errors != ['SOURCE_NOT_FORMAL_READY']:
        raise ValueError('OHI_CANDIDATE_FORMAL_REJECTION_OR_INTEGRITY:' + repr(errors))
    return artifact


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-dir', required=True)
    p.add_argument('--terms-dir', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--diagnostic', action='store_true')
    a = p.parse_args()
    output = private_root(a.output)
    src, terms = private_root(a.source_dir), private_root(a.terms_dir)
    result = build_candidate(json.loads((src/'observation.json').read_text()), src,
        (terms/'terms.raw.html').read_bytes(), json.loads((terms/'terms.receipt.json').read_text()),
        diagnostic=a.diagnostic)
    write(output, result)
    print(json.dumps({'candidate_sha256': result['source_snapshot_sha256'],
        'formal_ready': False, 'signed_source': False, 'scope_review': result['scope_review']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
