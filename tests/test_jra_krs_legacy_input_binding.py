"""Bind original signed KRS inputs without modifying or signing an artifact."""
import base64
import copy
import hashlib
import json
from pathlib import Path
import sys
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'runtime'), str(ROOT / 'scripts')]
from jra_production_krs_contract import production_krs_payload
from jra_krs_legacy_input_binding import check_input_binding, assert_input_race_identity, KRSInputBindingError, CONTRACT
from unpack_jra_day_review import unpack


@pytest.fixture(scope='module')
def originals():
    unpack()
    records = json.loads((ROOT / 'runtime/daily_reviews/JRA-2026-10-17/audit_ledger.json').read_text())['races']
    return [(production_krs_payload(json.loads((ROOT / r['artifact_refs']['request']).read_text())),
             json.loads((ROOT / r['krs']['raw_output_ref']).read_text()))
            for r in records if r['artifact_refs']['final']]


def test_all_twenty_three_original_signed_inputs_match_normalization(originals):
    assert len(originals) == 23
    key = Ed25519PublicKey.from_public_bytes(base64.b64decode('UhjfD9zFt+e77/9JUB19R6/XFC3SG4pM5twHBqfUSzI='))
    for payload, response in originals:
        before = copy.deepcopy((payload, response))
        envelope = response['run_receipt']
        receipt = json.dumps(envelope['receipt'], ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
        assert hashlib.sha256(receipt).hexdigest() == envelope['receipt_sha256']
        key.verify(base64.b64decode(envelope['signature']), receipt)
        record = check_input_binding(payload, response)
        assert record['contract'] == CONTRACT
        assert not record['wire_request_modified']
        assert (payload, response) == before


@pytest.mark.parametrize('fault', ['horse', 'environment', 'identity', 'version', 'schema', 'hash'])
def test_changed_content_identity_or_unknown_contract_fails_closed(originals, fault):
    payload, response = copy.deepcopy(originals[0])
    receipt = response['run_receipt']['receipt']
    if fault == 'horse': payload['input_data']['horses'][0]['name'] += ' tampered'
    if fault == 'environment': payload['input_data']['environment']['source_cutoff'] = 'CHANGED'
    if fault == 'identity': payload['input_data']['race']['prediction_id'] = 'OTHER-RACE'
    if fault == 'version': receipt['runtime_revision'] = 'UNKNOWN'
    if fault == 'schema': receipt['schema'] = 'UNKNOWN'
    if fault == 'hash': receipt['input_sha256'] = '0' * 64
    with pytest.raises(KRSInputBindingError):
        check_input_binding(payload, response)


def test_json_field_order_does_not_change_canonical_content_binding(originals):
    payload, response = originals[0]
    reordered = copy.deepcopy(payload)
    reordered['input_data'] = dict(reversed(list(reordered['input_data'].items())))
    assert check_input_binding(reordered, response) == check_input_binding(payload, response)


def test_wrong_inner_race_is_rejected_before_transport(originals):
    payload = copy.deepcopy(originals[0][0])
    payload['input_data']['race']['race_id'] = 'OTHER'
    with pytest.raises(KRSInputBindingError, match='RACE_ID_MISMATCH'):
        assert_input_race_identity(payload)
