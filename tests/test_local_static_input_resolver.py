import json
import pytest
from runtime.local_static_input_resolver import resolve, input_packet


def request():
    return {'family_id': 'LOCAL', 'execution_id': 'race', 'race_id': 'race',
            'venue_id': 'KAW', 'race_date': '2099-01-01', 'race_no': 8,
            'prediction_cutoff': '2099-01-01T12:00:00+09:00',
            'scheduled_post_at': '2099-01-01T12:10:00+09:00'}


def source():
    return {'receipt_sha256': 'signed', 'artifact': {'source_snapshot_sha256': 'snapshot',
            'official_runner_universe': {'runners': [{'runner_id': '1'}, {'runner_id': '2'}]}}}


def frozen():
    return {**request(), 'static_prediction_frozen': True,
            'static_prediction': {'status': 'FROZEN', 'ranking': ['1', '2'],
                                  'roles': {'1': ['W'], '2': ['P2', 'P3']}}}


def put(root, q):
    p=root/'runtime/formal_intents/race.json';p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(q))


def test_locates_exact_canonical_frozen_input_without_asking_user(tmp_path):
    put(tmp_path, frozen())
    q, status = resolve(request(), source(), root=tmp_path)
    assert q['static_prediction_frozen'] is True
    assert status['input_mode'] == 'CANONICAL_FORMAL_INTENT'
    assert status['c2_owner_required'] is False


@pytest.mark.parametrize('change, code', [
    ({'family_id': 'JRA'}, 'FAMILY_MISMATCH'),
    ({'race_no': 9}, 'IDENTITY_MISMATCH'),
    ({'prediction_cutoff': '2099-01-01T11:59:00+09:00'}, 'TIME_BASIS_MISMATCH'),
    ({'source_receipt_sha256': 'other'}, 'SIGNED_SOURCE_MISMATCH'),
    ({'static_prediction': {'status': 'FROZEN', 'ranking': ['1'], 'roles': {'1': ['W']}}}, 'FULL_RUNNER_UNIVERSE_MISMATCH'),
    ({'static_prediction': {'status': 'FROZEN', 'ranking': ['1', '1'], 'roles': {'1': ['W']}}}, 'FULL_RUNNER_UNIVERSE_MISMATCH'),
])
def test_never_borrows_wrong_race_source_or_incomplete_static(tmp_path, change, code):
    put(tmp_path, {**frozen(), **change})
    with pytest.raises(ValueError, match=code):
        resolve(request(), source(), root=tmp_path)


def test_missing_static_is_handoff_not_new_owner_promotion(tmp_path):
    q, status = resolve(request(), source(), root=tmp_path)
    assert q is None and status['status'] == 'MISSING_RACE_STATIC'
    packet = input_packet(request(), source(), status, generation_allowed=False)
    assert packet['static_generation_allowed'] is False
    assert packet['prediction_consumption_authorized'] is False
    assert packet['source_receipt_sha256'] == 'signed'


def test_lookup_rejects_traversal(tmp_path):
    with pytest.raises(ValueError, match='EXECUTION_ID_INVALID'):
        resolve({**request(), 'execution_id': '../../other'}, source(), root=tmp_path)
