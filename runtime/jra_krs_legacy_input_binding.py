"""Content binding for the observed JRA Runtime v1.3.1 input normalization.

The immutable request remains the exact sent bytes. The legacy runtime adds
race.prediction_id before hashing input_data. All 23 Oct17 signed originals
match this transformation. Unknown runtime/schema or conflicting identity is
rejected; no alternative hashes are tried. Signature verification remains a
separate mandatory gate at the caller.
"""
from copy import deepcopy
import hashlib
import json

REVISION = 'KM-EXEC-RUNTIME-v1.3.1-BASE44-RECEIPT-LOG-20260917'
SCHEMA = 'KM-KRS-RUN-RECEIPT-v1'
CONTRACT = 'OBSERVED-JRA-V131-RACE-PREDICTION-ID-SORTED-UTF8-v1'


class KRSInputBindingError(ValueError):
    pass


def assert_input_race_identity(payload):
    race = (payload.get('input_data') or {}).get('race')
    rid = payload.get('race_id')
    if not isinstance(race, dict) or not rid or race.get('race_id') != rid:
        raise KRSInputBindingError('KRS_INPUT_RACE_ID_MISMATCH')
    if 'prediction_id' in race and race['prediction_id'] != rid:
        raise KRSInputBindingError('KRS_INPUT_PREDICTION_ID_CONFLICT')


def check_input_binding(payload, response):
    assert_input_race_identity(payload)
    receipt = (response.get('run_receipt') or {}).get('receipt') or {}
    if receipt.get('race_id') != payload['race_id']:
        raise KRSInputBindingError('KRS_INPUT_RECEIPT_RACE_ID_MISMATCH')
    if receipt.get('runtime_revision') != REVISION or receipt.get('schema') != SCHEMA:
        raise KRSInputBindingError('KRS_INPUT_LEGACY_RUNTIME_UNSUPPORTED')
    declared = receipt.get('input_hash_contract')
    value = deepcopy(payload['input_data'])
    if declared is not None:
        if declared != 'KM-KRS-INPUT-DATA-SORTED-UTF8-v1':
            raise KRSInputBindingError('KRS_INPUT_DECLARED_CONTRACT_UNSUPPORTED')
        contract = declared
    else:
        race = value.get('race')
        race['prediction_id'] = payload['race_id']
        contract = CONTRACT
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')
    observed = hashlib.sha256(raw).hexdigest()
    if observed != receipt.get('input_sha256'):
        raise KRSInputBindingError('KRS_INPUT_CONTENT_HASH_MISMATCH')
    return {'race_id': payload['race_id'], 'contract': contract,
            'normalized_input_sha256': observed, 'input_content_binding': 'MATCH',
            'normalization': 'race.prediction_id = race_id' if declared is None else 'NONE',
            'wire_request_modified': False, 'historical_receipt_modified': False,
            'signature_verification': 'SEPARATE_REQUIRED_GATE'}
